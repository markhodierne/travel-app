from django.contrib import admin

from trips.models import Trip


@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ('name', 'destination', 'start_date', 'end_date')
    search_fields = ('name', 'destination', 'description')
    list_filter = ('start_date', 'end_date')
    date_hierarchy = 'start_date'
