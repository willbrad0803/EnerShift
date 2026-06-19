# dashboard/models.py (full replacement - backward compatible)
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import uuid
from decimal import Decimal

class UserProfile(models.Model):
    ROLE_CHOICES = [('CUSTOMER', 'Customer'), ('STAFF', 'Staff')]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='CUSTOMER')
    company_name = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return f"{self.user.email} - {self.role}"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


class Site(models.Model):
    INDUSTRY_CHOICES = [
        ('MANUFACTURING', 'Manufacturing'), ('FOOD_PROCESSING', 'Food Processing'),
        ('RETAIL', 'Retail / Supermarket'), ('WAREHOUSE', 'Warehouse / Logistics'), ('OTHER', 'Other')
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sites')
    name = models.CharField(max_length=200)
    postcode = models.CharField(max_length=20)
    industry_type = models.CharField(max_length=50, choices=INDUSTRY_CHOICES, default='OTHER')
    address = models.TextField(blank=True, null=True)
    flexible_loads = models.TextField(blank=True, null=True)
    
    # New constraints for optimization
    temp_min_c = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(-20)])
    temp_max_c = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, validators=[MaxValueValidator(50)])
    shift_notice_hours = models.PositiveIntegerField(default=2)
    max_shift_duration_hours = models.PositiveIntegerField(default=4)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('user', 'name')

    def __str__(self):
        return f"{self.name} ({self.postcode})"


class MeterReading(models.Model):
    """Half-hourly data layer."""
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name='meter_readings')
    timestamp = models.DateTimeField(db_index=True)
    consumption_kwh = models.DecimalField(max_digits=10, decimal_places=4, validators=[MinValueValidator(0)])
    export_kwh = models.DecimalField(max_digits=10, decimal_places=4, default=0, validators=[MinValueValidator(0)])
    meter_id = models.CharField(max_length=100, blank=True, null=True)
    data_source = models.CharField(max_length=50, default='manual', choices=[('manual', 'Manual'), ('csv', 'CSV'), ('api', 'API')])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('site', 'timestamp')
        indexes = [models.Index(fields=['site', 'timestamp']), models.Index(fields=['timestamp'])]
        ordering = ['-timestamp']


class EnergyPrice(models.Model):
    timestamp = models.DateTimeField(db_index=True)
    price_gbp_per_mwh = models.DecimalField(max_digits=12, decimal_places=4)
    price_type = models.CharField(max_length=50, choices=[('wholesale', 'Wholesale'), ('day_ahead', 'Day-Ahead')])

    class Meta:
        unique_together = ('timestamp', 'price_type')


class WindForecast(models.Model):
    timestamp = models.DateTimeField(db_index=True)
    forecast_mw = models.DecimalField(max_digits=12, decimal_places=2)


class GridEvent(models.Model):
    EVENT_TYPE_CHOICES = [('DFS', 'Demand Flexibility Service'), ('ENWL', 'ENWL')]
    event_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    title = models.CharField(max_length=255)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPE_CHOICES)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(max_length=20, default='upcoming')
    reward_gbp_per_mwh = models.DecimalField(max_digits=10, decimal_places=2, null=True)


class OptimizationRecommendation(models.Model):
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name='recommendations')
    timestamp = models.DateTimeField(db_index=True)
    action_type = models.CharField(max_length=100)
    recommended_kwh_shift = models.DecimalField(max_digits=10, decimal_places=2)
    expected_savings_gbp = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50, default='pending')
    reasoning = models.TextField(blank=True)

    class Meta:
        ordering = ['-timestamp']
