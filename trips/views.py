from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
    TemplateView
)
from django.contrib import messages
from django.utils import timezone

from trips.models import Trip
from trips.forms import TripForm
from weather.services import get_weather_for_location, get_forecast_from_weather_data


class TripListView(ListView):
    """
    Display a list of all trips.
    """
    model = Trip
    template_name = 'trips/trip_list.html'
    context_object_name = 'trips'
    paginate_by = 10


class TripDetailView(DetailView):
    """
    Display details of a specific trip.
    """
    model = Trip
    template_name = 'trips/trip_detail.html'
    context_object_name = 'trip'
    
    def get_context_data(self, **kwargs):
        """
        Add activities and weather data to context.
        """
        context = super().get_context_data(**kwargs)
        trip = self.object
        
        # Get weather data for the trip destination
        try:
            weather_data = get_weather_for_location(trip.destination)
            context['weather'] = weather_data
            
            if weather_data:
                # Extract forecast data from the weather object
                context['forecast'] = get_forecast_from_weather_data(weather_data)
        except Exception as e:
            # Log the error but don't break the page
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error getting weather for {trip.destination}: {str(e)}")
            
            # Set empty values for templates to safely check
            context['weather'] = None
            context['forecast'] = []
            context['weather_error'] = True
        
        # Activities are accessible via the related_name 'activities' defined in the model
        # Trip activities are already included in trip object via related_name
        return context


class TripCreateView(CreateView):
    """
    Create a new trip.
    """
    model = Trip
    form_class = TripForm
    template_name = 'trips/trip_form.html'
    success_url = reverse_lazy('trip-list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create New Trip'
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'Trip created successfully!')
        return super().form_valid(form)


class TripUpdateView(UpdateView):
    """
    Update an existing trip.
    """
    model = Trip
    form_class = TripForm
    template_name = 'trips/trip_form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Trip'
        return context
    
    def get_success_url(self):
        return reverse_lazy('trip-detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, 'Trip updated successfully!')
        return super().form_valid(form)


class TripDeleteView(DeleteView):
    """
    Delete an existing trip.
    """
    model = Trip
    template_name = 'trips/trip_confirm_delete.html'
    success_url = reverse_lazy('trip-list')
    context_object_name = 'trip'
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Trip deleted successfully!')
        return super().delete(request, *args, **kwargs)


class DashboardView(TemplateView):
    """
    Display the main dashboard with upcoming trips and weather information.
    """
    template_name = 'trips/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()
        
        # Get upcoming trips (start date >= today)
        upcoming_trips = Trip.objects.filter(start_date__gte=today).order_by('start_date')[:5]
        context['upcoming_trips'] = upcoming_trips
        
        # Get ongoing trips (start date <= today <= end date)
        ongoing_trips = Trip.objects.filter(
            start_date__lte=today,
            end_date__gte=today
        ).order_by('end_date')
        context['ongoing_trips'] = ongoing_trips
        
        # Get weather data for upcoming destinations
        context['destinations_weather'] = []
        
        # Collect unique destinations from upcoming and ongoing trips
        destinations = set()
        for trip in list(upcoming_trips) + list(ongoing_trips):
            if trip.destination not in destinations and len(destinations) < 3:
                destinations.add(trip.destination)
                
                try:
                    weather_data = get_weather_for_location(trip.destination)
                    if weather_data:
                        forecast = get_forecast_from_weather_data(weather_data)
                        context['destinations_weather'].append({
                            'destination': trip.destination,
                            'weather': weather_data,
                            'forecast': forecast
                        })
                except Exception as e:
                    # Log the error but don't break the dashboard
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"Error getting weather for {trip.destination}: {str(e)}")
        
        return context