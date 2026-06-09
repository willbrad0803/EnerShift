from django import forms
from .models import Site

class SiteForm(forms.ModelForm):
    class Meta:
        model = Site
        fields = ['name', 'postcode', 'industry_type', 'address', 'flexible_loads']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full border border-gray-300 rounded-2xl px-5 py-4'}),
            'postcode': forms.TextInput(attrs={'class': 'w-full border border-gray-300 rounded-2xl px-5 py-4', 'placeholder': 'M1 1AA'}),
            'address': forms.Textarea(attrs={'class': 'w-full border border-gray-300 rounded-2xl px-5 py-4', 'rows': 3}),
            'flexible_loads': forms.Textarea(attrs={'class': 'w-full border border-gray-300 rounded-2xl px-5 py-4', 'rows': 3, 'placeholder': 'Refrigeration, HVAC, compressors, etc.'}),
        }
