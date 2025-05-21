from django.urls import path

from trips.views import (
    TripListView,
    TripDetailView,
    TripCreateView,
    TripUpdateView,
    TripDeleteView,
    DashboardView
)

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path('trips/', TripListView.as_view(), name='trip-list'),
    path('trips/create/', TripCreateView.as_view(), name='trip-create'),
    path('trips/<uuid:pk>/', TripDetailView.as_view(), name='trip-detail'),
    path('trips/<uuid:pk>/edit/', TripUpdateView.as_view(), name='trip-update'),
    path('trips/<uuid:pk>/delete/', TripDeleteView.as_view(), name='trip-delete'),
]