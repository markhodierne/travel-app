import json
from django import template
from django.utils.safestring import mark_safe

from weather.services import get_weather_for_location, get_forecast_from_weather_data

register = template.Library()


@register.simple_tag
def get_weather(location):
    """
    Template tag to fetch weather data for a location.
    
    Usage:
    {% load weather_tags %}
    {% get_weather location as weather %}
    
    Args:
        location (str): The location to get weather for
        
    Returns:
        WeatherData: The weather data object or None if unsuccessful
    """
    return get_weather_for_location(location)


@register.filter
def get_forecast(weather_data):
    """
    Template filter to extract forecast data from a WeatherData object.
    
    Usage:
    {{ weather|get_forecast }}
    
    Args:
        weather_data (WeatherData): The weather data object
        
    Returns:
        list: A list of daily forecast dictionaries
    """
    return get_forecast_from_weather_data(weather_data)


@register.filter
def weather_icon(condition):
    """
    Template filter to get the appropriate Bootstrap Icon for a weather condition.
    
    Usage:
    {{ weather.conditions|weather_icon }}
    
    Args:
        condition (str): The weather condition string
        
    Returns:
        str: The Bootstrap Icon class for the condition
    """
    condition = condition.lower() if condition else ""
    
    # Map condition to Bootstrap Icons
    icons = {
        'clear': 'bi-sun',
        'clouds': 'bi-cloud',
        'rain': 'bi-cloud-rain',
        'drizzle': 'bi-cloud-drizzle',
        'thunderstorm': 'bi-cloud-lightning',
        'snow': 'bi-snow',
        'mist': 'bi-cloud-fog',
        'smoke': 'bi-cloud-haze',
        'haze': 'bi-cloud-haze',
        'dust': 'bi-cloud-haze',
        'fog': 'bi-cloud-fog',
        'sand': 'bi-cloud-haze',
        'ash': 'bi-cloud-haze',
        'squall': 'bi-cloud-lightning-rain',
        'tornado': 'bi-tornado'
    }
    
    # Check for partial matches
    for key, icon in icons.items():
        if key in condition:
            return icon
    
    # Default icon if no match found
    return 'bi-cloud'


@register.filter
def weather_color(condition):
    """
    Template filter to get the appropriate text color for a weather condition.
    
    Usage:
    {{ weather.conditions|weather_color }}
    
    Args:
        condition (str): The weather condition string
        
    Returns:
        str: The text color class for the condition
    """
    condition = condition.lower() if condition else ""
    
    # Map condition to Bootstrap text colors
    colors = {
        'clear': 'text-warning',
        'clouds': 'text-secondary',
        'rain': 'text-primary',
        'drizzle': 'text-info',
        'thunderstorm': 'text-danger',
        'snow': 'text-info',
        'mist': 'text-secondary',
        'smoke': 'text-secondary',
        'haze': 'text-secondary',
        'dust': 'text-secondary',
        'fog': 'text-secondary',
        'sand': 'text-warning',
        'ash': 'text-secondary',
        'squall': 'text-primary',
        'tornado': 'text-danger'
    }
    
    # Check for partial matches
    for key, color in colors.items():
        if key in condition:
            return color
    
    # Default color if no match found
    return 'text-secondary'