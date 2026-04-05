from django.db import models
from django.contrib.auth.models import User

class Site(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sites')
    name = models.CharField(max_length=200)
    postcode = models.CharField(max_length=10)
    lat = models.FloatField(null=True, blank=True)
    lon = models.FloatField(null=True, blank=True)
    industry_type = models.CharField(max_length=100, choices=[
        ('warehouse', 'Warehouse / Distribution'),
        ('supermarket', 'Supermarket / Retail'),
        ('industrial', 'Industrial / Manufacturing'),
        ('data_centre', 'Data Centre'),
        ('community', 'Community Energy'),
        ('other', 'Other'),
    ], default='warehouse')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.postcode})"

    class Meta:
        ordering = ['-created_at']