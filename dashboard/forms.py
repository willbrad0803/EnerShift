# dashboard/forms.py (update for constraints)
from django import forms
from .models import Site

class SiteForm(forms.ModelForm):
    class Meta:
        model = Site
        fields = ['name', 'postcode', 'industry_type', 'address', 'flexible_loads', 'temp_min_c', 'temp_max_c', 'shift_notice_hours', 'max_shift_duration_hours']
