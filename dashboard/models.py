from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Site(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sites')
    name = models.CharField(max_length=200)
    postcode = models.CharField(max_length=10)
    industry_type = models.CharField(max_length=100, default='Other')
    
    # Expanded fields
    address = models.TextField(blank=True, null=True)
    annual_kwh_estimate = models.FloatField(null=True, blank=True, help_text="Estimated annual consumption in kWh")
    meter_type = models.CharField(max_length=50, choices=[
        ('smart', 'Smart Meter'),
        ('traditional', 'Traditional'),
        ('half_hourly', 'Half-Hourly'),
    ], default='traditional')
    notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.postcode})"

    class Meta:
        ordering = ['name']
        unique_together = ('user', 'name')


class SavingsLog(models.Model):
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name='savings_logs')
    date = models.DateField()
    baseline_kwh = models.FloatField(help_text="Expected / previous period consumption")
    actual_kwh = models.FloatField(help_text="Actual measured consumption")
    savings_kwh = models.FloatField(blank=True, null=True, help_text="Auto-calculated")
    savings_notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.baseline_kwh is not None and self.actual_kwh is not None:
            self.savings_kwh = self.baseline_kwh - self.actual_kwh
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.site.name} - {self.date} ({self.savings_kwh} kWh saved)"

    class Meta:
        ordering = ['-date']


class ConsumptionData(models.Model):
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name='consumption')
    timestamp = models.DateTimeField()
    kwh = models.FloatField()
    price_p_per_kwh = models.FloatField(null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('site', 'timestamp')
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.site.name} - {self.timestamp}"
