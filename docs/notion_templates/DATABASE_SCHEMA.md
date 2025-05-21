# Travel Planning Application - Database Schema

## Overview

The Travel Planning Application uses PostgreSQL as its database, with Django's Object-Relational Mapping (ORM) handling database interactions. This document outlines the database schema, relationships between models, and key fields.

## Database Models

### Trip

The central model that stores information about travel plans.

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| name | CharField | Name of the trip |
| destination | CharField | Destination location |
| start_date | DateField | Trip start date |
| end_date | DateField | Trip end date |
| description | TextField | Optional description of the trip |
| cover_image | ImageField | Optional image for the trip |
| created_at | DateTimeField | When the trip was created |
| updated_at | DateTimeField | When the trip was last updated |

```python
class Trip(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    destination = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()
    description = models.TextField(blank=True, null=True)
    cover_image = models.ImageField(upload_to='trip_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
```

### Activity

Stores activities associated with trips, such as sightseeing, dining, or transportation.

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| trip | ForeignKey(Trip) | Reference to the associated trip |
| name | CharField | Name of the activity |
| date_time | DateTimeField | When the activity takes place |
| location | CharField | Where the activity takes place |
| description | TextField | Optional description of the activity |
| activity_type | CharField | Optional category/type of activity |
| created_at | DateTimeField | When the activity was created |
| updated_at | DateTimeField | When the activity was last updated |

```python
class Activity(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='activities')
    name = models.CharField(max_length=255)
    date_time = models.DateTimeField()
    location = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    activity_type = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - {self.trip.name}"
    
    class Meta:
        ordering = ['date_time']
        verbose_name_plural = 'Activities'
```

### WeatherData

Caches weather information to avoid excessive API calls.

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| location | CharField | Location for the weather data |
| temperature | FloatField | Current temperature |
| conditions | CharField | Weather conditions (e.g., "Sunny", "Rainy") |
| forecast | TextField | Brief forecast information |
| retrieved_at | DateTimeField | When the weather data was fetched |

```python
class WeatherData(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    location = models.CharField(max_length=255)
    temperature = models.FloatField()
    conditions = models.CharField(max_length=100)
    forecast = models.TextField()
    retrieved_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Weather for {self.location} at {self.retrieved_at}"
    
    class Meta:
        verbose_name_plural = 'Weather Data'
```

## Relationships

- **One-to-Many**: A Trip can have multiple Activities (one trip to many activities)
- Activities belong to exactly one Trip

## Indexes

For performance optimization, the following indexes are recommended:

- Trip.destination (for weather lookups)
- Activity.trip_id and Activity.date_time (for retrieving activities by trip and date)
- WeatherData.location and WeatherData.retrieved_at (for finding recent weather for a location)

## Migrations

Django handles database migrations automatically when you run:

```bash
python manage.py makemigrations
python manage.py migrate
```

## Data Integrity

Foreign key constraints ensure:

- When a Trip is deleted, all related Activities are automatically deleted (CASCADE)
- Activities cannot reference non-existent Trips

## Query Examples

### Get all activities for a trip, ordered by date and time:

```python
activities = Activity.objects.filter(trip=trip_instance).order_by('date_time')
```

### Get trips with activities in a date range:

```python
trips = Trip.objects.filter(activities__date_time__range=[start_date, end_date]).distinct()
```

### Get the most recent weather data for a location:

```python
weather = WeatherData.objects.filter(location=location).order_by('-retrieved_at').first()
```

## Data Validation

Django models include field-level validation:

- `start_date` should be before or equal to `end_date` in Trip model
- Required fields (name, destination, dates) cannot be empty
- Proper date formats are enforced

```python
# Example custom validation in Trip model
def clean(self):
    if self.start_date and self.end_date and self.start_date > self.end_date:
        raise ValidationError('Start date must be before or equal to end date')
```