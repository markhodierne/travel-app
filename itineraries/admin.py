from django.contrib import admin

from itineraries.models import Activity


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('name', 'trip', 'date_time', 'location', 'activity_type')
    list_filter = ('trip', 'date_time', 'activity_type')
    search_fields = ('name', 'location', 'description')
    date_hierarchy = 'date_time'
