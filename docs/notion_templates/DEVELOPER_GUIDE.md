# Travel Planning Application - Developer Guide

## Setting Up the Development Environment

### Prerequisites

- Python 3.8 or higher
- PostgreSQL
- pip (Python package manager)

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/markhodierne/travel-app.git
   cd travel-app
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**
   
   On Windows:
   ```bash
   venv\Scripts\activate
   ```
   
   On macOS/Linux:
   ```bash
   source venv/bin/activate
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Set up PostgreSQL database**
   
   Create a database for the project:
   ```bash
   createdb travelapp
   ```

6. **Configure environment variables**
   
   Create a `.env` file in the project root with:
   ```
   DATABASE_URL=postgresql://username:password@localhost:5432/travelapp
   SECRET_KEY=your_secret_key
   WEATHER_API_KEY=your_weather_api_key
   ```

7. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

8. **Create a superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

9. **Run the development server**
   ```bash
   python manage.py runserver
   ```

## Project Structure

```
travel-app/
├── manage.py
├── requirements.txt
├── travel_project/  # Project settings
├── trips/           # Trip management app
├── itineraries/     # Itinerary planning app
├── weather/         # Weather integration app
└── templates/       # Project-wide templates
```

## Key Components

### Models

#### Trip Model
The central model for storing trip information:
- Basic trip details (name, destination, dates)
- Optional fields (description, cover image)
- Related activities through foreign key relationship

#### Activity Model
Stores activities associated with trips:
- Activity details (name, datetime, location)
- Foreign key relationship to Trip
- Optional fields (description, activity type)

#### WeatherData Model
Caches weather information to minimize API calls:
- Weather details for locations
- Timestamp for data freshness

### Views

The application uses Django's class-based views where appropriate:
- List views for displaying collections of trips and activities
- Detail views for individual items
- Create, Update, and Delete views for data manipulation

### Templates

Templates follow Django's convention with a hierarchical structure:
- Base template with common elements
- App-specific templates extending the base
- Reusable components as includes

## Development Workflow

### Version Control

We follow the Feature Branch Workflow:
1. Create a new branch for each feature or fix
2. Make changes and commit using Conventional Commits format
3. Push to GitHub and create a pull request
4. Request code review
5. Merge after approval

### Testing

Run tests before submitting code:
```bash
python manage.py test
```

Tests should cover:
- Model validation
- View functionality
- Form processing
- API integration

### Code Style

We follow Django's coding style based on PEP 8. Key points:
- 4 spaces for indentation
- 79 character line limit
- Docstrings for all functions, classes, and methods
- Clear, descriptive variable names

## Common Tasks

### Creating a New App

```bash
python manage.py startapp app_name
```

Remember to:
1. Add the app to INSTALLED_APPS in settings.py
2. Create the necessary models, views, and templates
3. Add URL patterns to the app and project

### Database Changes

When changing models:
```bash
python manage.py makemigrations
python manage.py migrate
```

### Adding Static Files

Place static files in the app's static directory:
```
app_name/static/app_name/
```

### External API Integration

The weather feature uses a third-party API:
1. Store API key in environment variables
2. Use the Requests library for API calls
3. Implement error handling and caching
4. Create service classes to encapsulate API logic

## Troubleshooting

### Common Issues

1. **Database connection errors**
   - Check PostgreSQL is running
   - Verify DATABASE_URL environment variable
   - Ensure database exists

2. **Static files not loading**
   - Run `python manage.py collectstatic`
   - Check STATIC_URL and STATICFILES_DIRS settings

3. **Weather API errors**
   - Verify API key is correct
   - Check API service status
   - Review API call implementation

## Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Python Requests Library](https://docs.python-requests.org/)