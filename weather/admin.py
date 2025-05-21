from django.contrib import admin

from weather.models import WeatherData


@admin.register(WeatherData)
class WeatherDataAdmin(admin.ModelAdmin):
    list_display = ('location', 'temperature', 'conditions', 'retrieved_at')
    list_filter = ('location', 'conditions', 'retrieved_at')
    search_fields = ('location', 'conditions', 'forecast')
    date_hierarchy = 'retrieved_at'
    readonly_fields = ('id', 'retrieved_at')
