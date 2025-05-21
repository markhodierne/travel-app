import logging
import os
import json
from datetime import timedelta
from django.utils import timezone

import requests
from django.conf import settings
from requests.exceptions import RequestException, Timeout, ConnectionError, HTTPError, TooManyRedirects

from weather.models import WeatherData

logger = logging.getLogger(__name__)

# Get API key and URL from settings or environment variables
WEATHER_API_KEY = getattr(settings, 'WEATHER_API_KEY', os.environ.get('WEATHER_API_KEY', ''))
WEATHER_API_URL = getattr(settings, 'WEATHER_API_URL', os.environ.get('WEATHER_API_URL', 'https://api.openweathermap.org/data/2.5'))

# Cache duration (in hours)
CACHE_DURATION = 3

# Request timeout in seconds
REQUEST_TIMEOUT = 5

# Whether to use mock data when API key is missing or API is unreachable
USE_MOCK_DATA = getattr(settings, 'WEATHER_USE_MOCK_DATA', True)

class WeatherServiceException(Exception):
    """Base exception for weather service errors"""
    pass

class WeatherAPIKeyMissingException(WeatherServiceException):
    """Exception raised when API key is missing"""
    pass

class WeatherAPIException(WeatherServiceException):
    """Exception raised for API errors"""
    pass


def get_weather_for_location(location):
    """
    Get weather data for a specific location.
    First, tries to retrieve from cache (database), if recent enough.
    If not available or outdated, fetches from the API.
    
    Args:
        location (str): The location to get weather for
        
    Returns:
        WeatherData: The weather data object or None if unsuccessful
    """
    if not location:
        logger.error("No location provided for weather data")
        return None
    
    try:
        # Check for cached data first
        cached_weather = WeatherData.objects.filter(
            location=location,
            retrieved_at__gte=timezone.now() - timedelta(hours=CACHE_DURATION)
        ).order_by('-retrieved_at').first()
        
        if cached_weather:
            logger.info(f"Retrieved cached weather data for {location}")
            return cached_weather
        
        # If no recent data, fetch from API
        try:
            return fetch_weather_from_api(location)
        except WeatherAPIKeyMissingException as e:
            logger.error(f"API key missing: {str(e)}")
            return None
        except WeatherAPIException as e:
            logger.error(f"API error: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching weather: {str(e)}")
            return None
    
    except Exception as e:
        logger.error(f"Error getting weather for {location}: {str(e)}")
        return None


def fetch_weather_from_api(location):
    """
    Fetch weather data from OpenWeatherMap API.
    
    Args:
        location (str): The location to get weather for
        
    Returns:
        WeatherData: The newly created weather data object
        
    Raises:
        WeatherAPIKeyMissingException: If the API key is not configured
        WeatherAPIException: If there's an error with the API request
        Exception: For any other unexpected errors
    """
    if not WEATHER_API_KEY or WEATHER_API_KEY == 'your_weather_api_key':
        logger.error("Weather API key is not configured")
        if USE_MOCK_DATA:
            logger.info(f"Using mock data for location: {location}")
            return create_mock_weather_data(location)
        raise WeatherAPIKeyMissingException("Weather API key is not configured")
    
    try:
        # OpenWeatherMap current weather endpoint
        current_url = f"{WEATHER_API_URL}/weather"
        
        # Make API request for current weather
        current_params = {
            'q': location,
            'appid': WEATHER_API_KEY,
            'units': 'metric'  # Get temperature in Celsius
        }
        
        try:
            # Set timeout to avoid hanging the application
            current_response = requests.get(current_url, params=current_params, timeout=REQUEST_TIMEOUT)
            current_response.raise_for_status()  # Raise exception for HTTP errors
            current_data = current_response.json()
        except (Timeout, ConnectionError) as e:
            logger.error(f"Connection error or timeout for current weather API: {str(e)}")
            if USE_MOCK_DATA:
                logger.info(f"Using mock data for location: {location}")
                return create_mock_weather_data(location)
            raise WeatherAPIException(f"Connection error: {str(e)}")
        except HTTPError as e:
            # Check for specific error codes
            if current_response.status_code == 401:
                logger.error("Unauthorized: Invalid API key")
                raise WeatherAPIException("Invalid API key")
            elif current_response.status_code == 404:
                logger.error(f"Location not found: {location}")
                raise WeatherAPIException(f"Location not found: {location}")
            elif current_response.status_code == 429:
                logger.error("Rate limit exceeded")
                raise WeatherAPIException("Rate limit exceeded")
            else:
                logger.error(f"HTTP error: {str(e)}")
                raise WeatherAPIException(f"HTTP error: {str(e)}")
        except ValueError as e:
            logger.error(f"Invalid JSON response: {str(e)}")
            raise WeatherAPIException(f"Invalid API response format: {str(e)}")
        
        # Extract current weather information
        temperature = current_data.get('main', {}).get('temp', 0.0)
        conditions = current_data.get('weather', [{}])[0].get('main', 'Unknown')
        description = current_data.get('weather', [{}])[0].get('description', '')
        
        # Fetch 5-day forecast
        forecast_url = f"{WEATHER_API_URL}/forecast"
        forecast_params = {
            'q': location,
            'appid': WEATHER_API_KEY,
            'units': 'metric',
            'cnt': 5  # Limit to 5 days data
        }
        
        try:
            forecast_response = requests.get(forecast_url, params=forecast_params, timeout=REQUEST_TIMEOUT)
            forecast_response.raise_for_status()
            forecast_data = forecast_response.json()
        except (RequestException, ValueError) as e:
            logger.error(f"Error fetching forecast data: {str(e)}")
            # If we can't get forecast data but have current weather, continue with empty forecast
            forecast_data = {'list': []}
        
        # Process forecast data (take the daily average from 3-hour forecasts)
        daily_forecasts = process_forecast_data(forecast_data)
        
        # Store forecast as JSON string
        forecast_json = json.dumps(daily_forecasts)
        
        # Create new WeatherData object from API response
        weather_data = WeatherData.objects.create(
            location=location,
            temperature=temperature,
            conditions=conditions,
            forecast=forecast_json
        )
        
        logger.info(f"Successfully fetched new weather data for {location}")
        return weather_data
        
    except (WeatherAPIKeyMissingException, WeatherAPIException):
        # Re-raise these specific exceptions for better error handling
        raise
    except Exception as e:
        logger.error(f"Unexpected error processing weather data: {str(e)}")
        if USE_MOCK_DATA:
            logger.info(f"Using mock data for location: {location}")
            return create_mock_weather_data(location)
        raise


def create_mock_weather_data(location):
    """
    Create mock weather data when the API is unavailable.
    
    Args:
        location (str): The location to create mock data for
        
    Returns:
        WeatherData: A new WeatherData object with mock data
    """
    import random
    
    # Mock conditions
    conditions_list = ['Clear', 'Clouds', 'Rain', 'Sunny', 'Partly Cloudy']
    condition = random.choice(conditions_list)
    
    # Mock temperature between 10-30°C
    temperature = round(random.uniform(10.0, 30.0), 1)
    
    # Create mock forecast for next 5 days
    mock_forecast = []
    for i in range(5):
        # Generate date string (YYYY-MM-DD) for today + i days
        from datetime import datetime, timedelta
        date_str = (datetime.now() + timedelta(days=i)).strftime('%Y-%m-%d')
        
        # Random temperature variation of ±5°C from current temperature
        temp_variation = round(random.uniform(-5.0, 5.0), 1)
        forecast_temp = round(temperature + temp_variation, 1)
        
        # Random condition
        forecast_condition = random.choice(conditions_list)
        
        mock_forecast.append({
            'date': date_str,
            'temperature': forecast_temp,
            'condition': forecast_condition,
            'description': forecast_condition.lower()
        })
    
    # Store forecast as JSON string
    forecast_json = json.dumps(mock_forecast)
    
    # Create mock WeatherData object
    weather_data = WeatherData.objects.create(
        location=location,
        temperature=temperature,
        conditions=condition,
        forecast=forecast_json
    )
    
    logger.info(f"Created mock weather data for {location}")
    return weather_data


def process_forecast_data(forecast_data):
    """
    Process the 5-day/3-hour forecast data into daily forecasts.
    
    Args:
        forecast_data (dict): The raw forecast data from the API
        
    Returns:
        list: A list of daily forecast dictionaries
    """
    # The returned data is in 3-hour intervals, group by day
    daily_forecasts = {}
    
    try:
        for item in forecast_data.get('list', []):
            # Get the date part of the timestamp
            date = item['dt_txt'].split(' ')[0]
            
            if date not in daily_forecasts:
                daily_forecasts[date] = {
                    'date': date,
                    'temps': [],
                    'conditions': [],
                    'descriptions': []
                }
            
            # Collect temperatures and conditions
            daily_forecasts[date]['temps'].append(item['main']['temp'])
            daily_forecasts[date]['conditions'].append(item['weather'][0]['main'])
            daily_forecasts[date]['descriptions'].append(item['weather'][0]['description'])
        
        # Calculate averages and most common conditions for each day
        result = []
        for date, data in daily_forecasts.items():
            # Average temperature
            avg_temp = sum(data['temps']) / len(data['temps']) if data['temps'] else 0
            
            # Most common condition
            conditions_count = {}
            for condition in data['conditions']:
                conditions_count[condition] = conditions_count.get(condition, 0) + 1
            most_common_condition = max(conditions_count.items(), key=lambda x: x[1])[0] if conditions_count else "Unknown"
            
            # Most common description
            desc_count = {}
            for desc in data['descriptions']:
                desc_count[desc] = desc_count.get(desc, 0) + 1
            most_common_desc = max(desc_count.items(), key=lambda x: x[1])[0] if desc_count else ""
            
            result.append({
                'date': date,
                'temperature': round(avg_temp, 1),
                'condition': most_common_condition,
                'description': most_common_desc
            })
        
        return result
    except (KeyError, IndexError) as e:
        logger.error(f"Error processing forecast data: {str(e)}")
        return []


def get_forecast_from_weather_data(weather_data):
    """
    Parse the forecast JSON from a WeatherData object.
    
    Args:
        weather_data (WeatherData): The weather data object
        
    Returns:
        list: A list of daily forecast dictionaries
    """
    if not weather_data or not weather_data.forecast:
        return []
    
    try:
        return json.loads(weather_data.forecast)
    except json.JSONDecodeError:
        logger.error(f"Error decoding forecast JSON for {weather_data.location}")
        return []


def refresh_weather_data():
    """
    Utility function to refresh weather data for all known locations.
    This could be called by a periodic task/cron job.
    
    Returns:
        int: The number of locations successfully refreshed
    """
    # Get distinct locations we have stored
    locations = WeatherData.objects.values_list('location', flat=True).distinct()
    
    success_count = 0
    for location in locations:
        if fetch_weather_from_api(location):
            success_count += 1
    
    return success_count