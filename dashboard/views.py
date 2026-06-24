# dashboard/views.py (full replacement)
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from django.http import JsonResponse
from .models import Site, MeterReading, OptimizationRecommendation
from .forms import SiteForm
import csv
from decimal import Decimal
from io import TextIOWrapper
from django.utils import timezone

@login_required
def dashboard_home(request):
    sites = Site.objects.filter(user=request.user)
    return render(request, 'dashboard/home.html', {'sites': sites})


@login_required
def add_site(request):
    if request.method == 'POST':
        form = SiteForm(request.POST)
        if form.is_valid():
            site = form.save(commit=False)
            site.user = request.user
            site.save()
            messages.success(request, f"Site '{site.name}' added!")
            return redirect('dashboard_home')
    else:
        form = SiteForm()
    return render(request, 'dashboard/add_site.html', {'form': form})


@login_required
def upload_meter_data(request):
    """Initial manual CSV ingestion for half-hourly data."""
    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']
        site_id = request.POST.get('site_id')
        site = get_object_or_404(Site, id=site_id, user=request.user)
        
        try:
            decoded = TextIOWrapper(csv_file, encoding='utf-8')
            reader = csv.DictReader(decoded)
            count = 0
            for row in reader:
                try:
                    ts = timezone.datetime.fromisoformat(row['timestamp'].replace('Z', '+00:00'))
                    MeterReading.objects.update_or_create(
                        site=site, timestamp=ts,
                        defaults={
                            'consumption_kwh': Decimal(row.get('consumption_kwh', 0)),
                            'export_kwh': Decimal(row.get('export_kwh', 0)),
                            'data_source': 'csv'
                        }
                    )
                    count += 1
                except Exception as e:  # Explicit per-row
                    print(f"Row error: {e}")  # TODO: structured logging
                    continue
            messages.success(request, f"Imported {count} readings for {site.name}.")
            return redirect('dashboard_home')
        except Exception as e:
            messages.error(request, f"Upload error: {str(e)}")
            raise  # Never swallow
    sites = Site.objects.filter(user=request.user)
    return render(request, 'dashboard/upload_meter.html', {'sites': sites})


@login_required
def get_recommendations(request, site_id=None):
    site = get_object_or_404(Site, id=site_id, user=request.user) if site_id else None
    recs = OptimizationRecommendation.objects.filter(site=site).order_by('-timestamp')[:10] if site else []
    data = [{'ts': r.timestamp.isoformat(), 'action': r.action_type, 'savings': float(r.expected_savings_gbp)} for r in recs]
    return JsonResponse({'recommendations': data})


def custom_logout(request):
    from django.contrib.auth import logout
    logout(request)
    return redirect('account_login')
