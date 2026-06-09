from django.db import models
from django.contrib.auth.models import User

class Site(models.Model):
    INDUSTRY_CHOICES = [
        ('MANUFACTURING', 'Manufacturing'),
        ('FOOD_PROCESSING', 'Food Processing'),
        ('RETAIL', 'Retail / Supermarket'),
        ('WAREHOUSE', 'Warehouse / Logistics'),
        ('OTHER', 'Other'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sites')
    name = models.CharField(max_length=200)
    postcode = models.CharField(max_length=20)
    industry_type = models.CharField(max_length=50, choices=INDUSTRY_CHOICES, default='OTHER')
    address = models.TextField(blank=True, null=True)
    flexible_loads = models.TextField(blank=True, null=True, help_text="e.g. refrigeration, HVAC, compressors")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.postcode})"

    class Meta:
        ordering = ['-created_at']
