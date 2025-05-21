import uuid
from django.db import models


class WeatherData(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    location = models.CharField(max_length=255)
    temperature = models.FloatField()
    conditions = models.CharField(max_length=100)
    forecast = models.TextField()
    retrieved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-retrieved_at']
        verbose_name = "Weather Data"
        verbose_name_plural = "Weather Data"
        # Add a unique constraint for the location and time to prevent duplicate entries
        # This allows getting the latest weather data for a location easily
        constraints = [
            models.UniqueConstraint(
                fields=['location', 'retrieved_at'],
                name='unique_location_time'
            )
        ]

    def __str__(self):
        return f"{self.location} - {self.conditions} ({self.temperature}°C) at {self.retrieved_at.strftime('%Y-%m-%d %H:%M')}"
