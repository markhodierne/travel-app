from django.urls import path

from itineraries.views import (
    ActivityListView,
    ActivityDetailView,
    ActivityCreateView,
    ActivityUpdateView,
    ActivityDeleteView
)

urlpatterns = [
    # List activities for a specific trip
    path('trip/<uuid:trip_id>/activities/', 
         ActivityListView.as_view(), 
         name='activity-list'),
    
    # Create new activity for a specific trip
    path('trip/<uuid:trip_id>/activities/create/', 
         ActivityCreateView.as_view(), 
         name='activity-create'),
    
    # View activity details
    path('activities/<uuid:pk>/', 
         ActivityDetailView.as_view(), 
         name='activity-detail'),
    
    # Update activity
    path('activities/<uuid:pk>/edit/', 
         ActivityUpdateView.as_view(), 
         name='activity-update'),
    
    # Delete activity
    path('activities/<uuid:pk>/delete/', 
         ActivityDeleteView.as_view(), 
         name='activity-delete'),
]