from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Site(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sites')
    name = models.CharField(max_length=200)
    postcode = models.CharField(max_length=10)
    industry_type = models.CharField(max_length=100, default='Other')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.postcode})"

    class Meta:
        ordering = ['name']


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
        return f"{self.site.name} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"
