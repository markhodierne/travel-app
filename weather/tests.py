import json
from unittest.mock import patch, Mock
from django.test import TestCase
from django.utils import timezone
from datetime import timedelta

from weather.models import WeatherData
from weather.services import (
    get_weather_for_location,
    fetch_weather_from_api,
    process_forecast_data,
    get_forecast_from_weather_data,
    WeatherAPIKeyMissingException,
    WeatherAPIException
)


class WeatherModelTest(TestCase):
    """Test cases for the WeatherData model."""
    
    def test_weather_data_creation(self):
        """Test creating a new WeatherData record."""
        weather = WeatherData.objects.create(
            location="London",
            temperature=20.5,
            conditions="Sunny",
            forecast=json.dumps([{"date": "2023-01-01", "temperature": 19.0, "condition": "Sunny"}])
        )
        
        self.assertEqual(weather.location, "London")
        self.assertEqual(weather.temperature, 20.5)
        self.assertEqual(weather.conditions, "Sunny")
        self.assertIn("Sunny", weather.forecast)
        self.assertIsNotNone(weather.retrieved_at)
    
    def test_weather_data_string_representation(self):
        """Test the string representation of a WeatherData record."""
        weather = WeatherData.objects.create(
            location="Berlin",
            temperature=15.0,
            conditions="Cloudy",
            forecast="{}"
        )
        
        self.assertIn("Berlin", str(weather))
        self.assertIn("Cloudy", str(weather))
        self.assertIn("15.0", str(weather))


class WeatherServiceTest(TestCase):
    """Test cases for weather service functions."""
    
    def setUp(self):
        """Set up test data."""
        # Create a test weather record for caching tests
        self.test_weather = WeatherData.objects.create(
            location="Paris",
            temperature=22.0,
            conditions="Clear",
            forecast=json.dumps([{"date": "2023-01-01", "temperature": 21.0, "condition": "Clear"}]),
            retrieved_at=timezone.now()
        )
    
    @patch('weather.services.fetch_weather_from_api')
    def test_get_weather_for_location_cache_hit(self, mock_fetch):
        """Test retrieving weather from cache."""
        # This should retrieve from cache without calling the API
        result = get_weather_for_location("Paris")
        
        self.assertEqual(result.id, self.test_weather.id)
        mock_fetch.assert_not_called()
    
    @patch('weather.services.fetch_weather_from_api')
    def test_get_weather_for_location_cache_miss(self, mock_fetch):
        """Test retrieving weather when not in cache."""
        # Create a mock return value
        mock_weather = WeatherData(
            location="Rome",
            temperature=25.0,
            conditions="Sunny",
            forecast="{}"
        )
        mock_fetch.return_value = mock_weather
        
        # This should call the API function
        result = get_weather_for_location("Rome")
        
        mock_fetch.assert_called_once_with("Rome")
        self.assertEqual(result, mock_weather)
    
    @patch('weather.services.fetch_weather_from_api')
    def test_get_weather_for_location_cache_expired(self, mock_fetch):
        """Test retrieving weather when cache is expired."""
        # Create an expired weather record
        expired_weather = WeatherData.objects.create(
            location="Madrid",
            temperature=30.0,
            conditions="Hot",
            forecast="{}",
            retrieved_at=timezone.now() - timedelta(hours=4)  # Expired (> 3 hours old)
        )
        
        # Create a mock return value for the API call
        mock_weather = WeatherData(
            location="Madrid",
            temperature=28.0,
            conditions="Warm",
            forecast="{}"
        )
        mock_fetch.return_value = mock_weather
        
        # This should call the API function due to expired cache
        result = get_weather_for_location("Madrid")
        
        mock_fetch.assert_called_once_with("Madrid")
        self.assertEqual(result, mock_weather)
    
    @patch('weather.services.requests.get')
    def test_fetch_weather_from_api_success(self, mock_get):
        """Test successful API fetch."""
        # Mock the API responses
        mock_current_response = Mock()
        mock_current_response.json.return_value = {
            'main': {'temp': 18.5},
            'weather': [{'main': 'Clouds', 'description': 'scattered clouds'}]
        }
        
        mock_forecast_response = Mock()
        mock_forecast_response.json.return_value = {
            'list': [
                {
                    'dt_txt': '2023-01-01 12:00:00',
                    'main': {'temp': 19.0},
                    'weather': [{'main': 'Clouds', 'description': 'scattered clouds'}]
                }
            ]
        }
        
        # Configure the mock to return different responses for different URLs
        def side_effect(*args, **kwargs):
            url = args[0] if args else kwargs.get('url')
            if '/weather' in url:
                return mock_current_response
            elif '/forecast' in url:
                return mock_forecast_response
            return Mock()
        
        mock_get.side_effect = side_effect
        
        # Override settings for the test
        with patch('weather.services.WEATHER_API_KEY', 'test_key'):
            with patch('weather.services.WEATHER_API_URL', 'https://test.com'):
                result = fetch_weather_from_api("London")
        
        self.assertEqual(result.location, "London")
        self.assertEqual(result.temperature, 18.5)
        self.assertEqual(result.conditions, "Clouds")
        self.assertIsNotNone(result.forecast)
    
    def test_process_forecast_data(self):
        """Test processing forecast data."""
        forecast_data = {
            'list': [
                {
                    'dt_txt': '2023-01-01 00:00:00',
                    'main': {'temp': 20.0},
                    'weather': [{'main': 'Clear', 'description': 'clear sky'}]
                },
                {
                    'dt_txt': '2023-01-01 03:00:00',
                    'main': {'temp': 18.0},
                    'weather': [{'main': 'Clear', 'description': 'clear sky'}]
                },
                {
                    'dt_txt': '2023-01-02 00:00:00',
                    'main': {'temp': 22.0},
                    'weather': [{'main': 'Clouds', 'description': 'scattered clouds'}]
                }
            ]
        }
        
        result = process_forecast_data(forecast_data)
        
        self.assertEqual(len(result), 2)  # Two unique dates
        
        # Check first day
        self.assertEqual(result[0]['date'], '2023-01-01')
        self.assertEqual(result[0]['temperature'], 19.0)  # Average of 20.0 and 18.0
        self.assertEqual(result[0]['condition'], 'Clear')
        
        # Check second day
        self.assertEqual(result[1]['date'], '2023-01-02')
        self.assertEqual(result[1]['temperature'], 22.0)
        self.assertEqual(result[1]['condition'], 'Clouds')
    
    def test_get_forecast_from_weather_data(self):
        """Test parsing forecast JSON from WeatherData."""
        forecast_data = [
            {'date': '2023-01-01', 'temperature': 20.0, 'condition': 'Clear', 'description': 'clear sky'},
            {'date': '2023-01-02', 'temperature': 22.0, 'condition': 'Clouds', 'description': 'scattered clouds'}
        ]
        
        weather = WeatherData.objects.create(
            location="Berlin",
            temperature=20.0,
            conditions="Clear",
            forecast=json.dumps(forecast_data)
        )
        
        result = get_forecast_from_weather_data(weather)
        
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['date'], '2023-01-01')
        self.assertEqual(result[1]['date'], '2023-01-02')
        self.assertEqual(result[0]['temperature'], 20.0)
        self.assertEqual(result[1]['condition'], 'Clouds')
    
    def test_get_forecast_from_weather_data_empty(self):
        """Test parsing forecast with empty or invalid data."""
        # Test with None
        self.assertEqual(get_forecast_from_weather_data(None), [])
        
        # Test with empty forecast
        weather = WeatherData.objects.create(
            location="Empty",
            temperature=0.0,
            conditions="Unknown",
            forecast=""
        )
        self.assertEqual(get_forecast_from_weather_data(weather), [])
        
        # Test with invalid JSON
        weather = WeatherData.objects.create(
            location="Invalid",
            temperature=0.0,
            conditions="Unknown",
            forecast="not-valid-json"
        )
        self.assertEqual(get_forecast_from_weather_data(weather), [])