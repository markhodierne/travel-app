from django import forms
from django.core.exceptions import ValidationError

from trips.models import Trip


class TripForm(forms.ModelForm):
    """
    Form for creating and updating Trip records.
    """
    
    class Meta:
        model = Trip
        fields = [
            'name',
            'destination',
            'start_date',
            'end_date',
            'description',
            'cover_image',
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }
    
    def clean(self):
        """
        Validate that the end date is after or equal to the start date.
        """
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date and end_date < start_date:
            raise ValidationError("End date cannot be before start date.")
        
        return cleaned_data