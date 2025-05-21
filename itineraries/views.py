from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)
from django.contrib import messages

from itineraries.models import Activity
from itineraries.forms import ActivityForm
from trips.models import Trip


class ActivityListView(ListView):
    """
    Display a list of activities for a specific trip.
    """
    model = Activity
    template_name = 'itineraries/activity_list.html'
    context_object_name = 'activities'
    
    def get_queryset(self):
        """
        Filter activities by trip_id from URL.
        """
        self.trip = get_object_or_404(Trip, pk=self.kwargs['trip_id'])
        return Activity.objects.filter(trip=self.trip)
    
    def get_context_data(self, **kwargs):
        """
        Add trip to context.
        """
        context = super().get_context_data(**kwargs)
        context['trip'] = self.trip
        return context


class ActivityDetailView(DetailView):
    """
    Display details of a specific activity.
    """
    model = Activity
    template_name = 'itineraries/activity_detail.html'
    context_object_name = 'activity'
    
    def get_context_data(self, **kwargs):
        """
        Add trip to context.
        """
        context = super().get_context_data(**kwargs)
        context['trip'] = self.object.trip
        return context


class ActivityCreateView(CreateView):
    """
    Create a new activity for a specific trip.
    """
    model = Activity
    form_class = ActivityForm
    template_name = 'itineraries/activity_form.html'
    
    def get_trip(self):
        """
        Get the trip object from URL.
        """
        return get_object_or_404(Trip, pk=self.kwargs['trip_id'])
    
    def get_form_kwargs(self):
        """
        Pass trip to form for validation.
        """
        kwargs = super().get_form_kwargs()
        kwargs['trip'] = self.get_trip()
        return kwargs
    
    def get_context_data(self, **kwargs):
        """
        Add trip and title to context.
        """
        context = super().get_context_data(**kwargs)
        context['trip'] = self.get_trip()
        context['title'] = 'Add Activity'
        return context
    
    def get_success_url(self):
        """
        Redirect to trip detail page after successful creation.
        """
        return reverse('trip-detail', kwargs={'pk': self.kwargs['trip_id']})
    
    def form_valid(self, form):
        """
        Set trip and display success message.
        """
        form.instance.trip = self.get_trip()
        messages.success(self.request, 'Activity added successfully!')
        return super().form_valid(form)


class ActivityUpdateView(UpdateView):
    """
    Update an existing activity.
    """
    model = Activity
    form_class = ActivityForm
    template_name = 'itineraries/activity_form.html'
    
    def get_form_kwargs(self):
        """
        Pass trip to form for validation.
        """
        kwargs = super().get_form_kwargs()
        kwargs['trip'] = self.object.trip
        return kwargs
    
    def get_context_data(self, **kwargs):
        """
        Add trip and title to context.
        """
        context = super().get_context_data(**kwargs)
        context['trip'] = self.object.trip
        context['title'] = 'Edit Activity'
        return context
    
    def get_success_url(self):
        """
        Redirect to trip detail page after successful update.
        """
        return reverse('trip-detail', kwargs={'pk': self.object.trip.pk})
    
    def form_valid(self, form):
        """
        Display success message.
        """
        messages.success(self.request, 'Activity updated successfully!')
        return super().form_valid(form)


class ActivityDeleteView(DeleteView):
    """
    Delete an existing activity.
    """
    model = Activity
    template_name = 'itineraries/activity_confirm_delete.html'
    context_object_name = 'activity'
    
    def get_context_data(self, **kwargs):
        """
        Add trip to context.
        """
        context = super().get_context_data(**kwargs)
        context['trip'] = self.object.trip
        return context
    
    def get_success_url(self):
        """
        Redirect to trip detail page after successful deletion.
        """
        return reverse('trip-detail', kwargs={'pk': self.object.trip.pk})
    
    def delete(self, request, *args, **kwargs):
        """
        Display success message.
        """
        messages.success(request, 'Activity deleted successfully!')
        return super().delete(request, *args, **kwargs)