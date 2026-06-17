from django import forms
from .models import Site

class SiteForm(forms.ModelForm):
    class Meta:
        model = Site
        fields = ['name', 'postcode', 'industry_type', 'address', 'flexible_loads']
