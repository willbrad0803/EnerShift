# dashboard/admin.py (update)
from django.contrib import admin
from .models import Site, MeterReading, EnergyPrice, WindForecast, GridEvent, OptimizationRecommendation

admin.site.register(Site)
admin.site.register(MeterReading)
admin.site.register(EnergyPrice)
admin.site.register(WindForecast)
admin.site.register(GridEvent)
admin.site.register(OptimizationRecommendation)
