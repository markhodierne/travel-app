from django import forms
from django.core.exceptions import ValidationError

from itineraries.models import Activity


class ActivityForm(forms.ModelForm):
    """
    Form for creating and updating Activity records.
    """
    
    class Meta:
        model = Activity
        fields = [
            'name',
            'date_time',
            'location',
            'description',
            'activity_type',
        ]
        widgets = {
            'date_time': forms.DateTimeInput(
                attrs={'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M'
            ),
            'description': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        """
        Initialize the form with custom parameters.
        
        If trip_id is provided, hide the trip field which will be set in the view.
        """
        self.trip = kwargs.pop('trip', None)
        super().__init__(*args, **kwargs)
        
        # Apply Bootstrap classes to form fields
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
    
    def clean_date_time(self):
        """
        Validate that the date_time is within the trip's date range.
        """
        date_time = self.cleaned_data.get('date_time')
        
        if self.trip and date_time:
            trip_start = self.trip.start_date
            trip_end = self.trip.end_date
            
            # Convert date_time to date for comparison
            activity_date = date_time.date()
            
            if activity_date < trip_start or activity_date > trip_end:
                raise ValidationError(
                    "Activity date must be within the trip's date range "
                    f"({trip_start} to {trip_end})."
                )
        
        return date_time
    
    def save(self, commit=True):
        """
        Save the form, setting the trip if provided.
        """
        instance = super().save(commit=False)
        
        if self.trip:
            instance.trip = self.trip
            
        if commit:
            instance.save()
            
        return instance