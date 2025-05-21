import uuid

from django.db import models

from trips.models import Trip


class Activity(models.Model):
    ACTIVITY_TYPE_CHOICES = [
        ('transportation', 'Transportation'),
        ('accommodation', 'Accommodation'),
        ('sightseeing', 'Sightseeing'),
        ('food', 'Food & Dining'),
        ('entertainment', 'Entertainment'),
        ('other', 'Other'),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    trip = models.ForeignKey(
        Trip,
        on_delete=models.CASCADE,
        related_name='activities'
    )
    name = models.CharField(max_length=255)
    date_time = models.DateTimeField()
    location = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    activity_type = models.CharField(
        max_length=20,
        choices=ACTIVITY_TYPE_CHOICES,
        default='other',
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['date_time']
        verbose_name = "Activity"
        verbose_name_plural = "Activities"

    def __str__(self):
        return f"{self.name} - {self.date_time.strftime('%Y-%m-%d %H:%M')}"
