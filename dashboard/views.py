from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .models import Site
import requests
from datetime import datetime

@login_required
def dashboard_home(request):
    sites = Site.objects.filter(user=request.user)
    return render(request, 'dashboard/home.html', {'sites': sites})

@login_required
def all_sites_overview(request):
    sites = Site.objects.filter(user=request.user)
    total_sites = sites.count()
    
    # Simple aggregate estimate
    total_estimated_earnings = "£0 - £1,200"
    if total_sites > 0:
        total_estimated_earnings = f"£{total_sites * 180} - £{total_sites * 550}"
    
    return render(request, 'dashboard/all_sites.html', {
        'sites': sites,
        'total_sites': total_sites,
        'total_estimated_earnings': total_estimated_earnings
    })

@login_required
def add_site(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        postcode = request.POST.get('postcode', '').upper().replace(" ", "")
        industry_type = request.POST.get('industry_type')
        
        site = Site.objects.create(
            user=request.user,
            name=name,
            postcode=postcode,
            industry_type=industry_type
        )
        return redirect('dashboard_home')
    
    return render(request, 'dashboard/add_site.html')

@login_required
def site_detail(request, site_id):
    site = get_object_or_404(Site, id=site_id, user=request.user)
    
    forecast_data = None
    recommendation = "Could not fetch forecast right now."
    estimated_earnings = "£0 - £150"
    last_updated = datetime.now().strftime("%d %b %H:%M")
    
    try:
        clean_postcode = site.postcode.replace(" ", "")
        
        pc_url = f"https://api.postcodes.io/postcodes/{clean_postcode}"
        pc_response = requests.get(pc_url, timeout=5)
        
        if pc_response.status_code == 200:
            pc_data = pc_response.json()
            lat = pc_data['result']['latitude']
            lon = pc_data['result']['longitude']
            
            weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=wind_speed_10m&timezone=Europe/London"
            weather_response = requests.get(weather_url, timeout=10)
            
            if weather_response.status_code == 200:
                data = weather_response.json()
                hourly = data.get('hourly', {})
                times = hourly.get('time', [])
                speeds = hourly.get('wind_speed_10m', [])
                
                high_wind = []
                total_strong_wind_hours = 0
                
                for i in range(min(len(times), len(speeds))):
                    if speeds[i] > 8.0:
                        high_wind.append({
                            'time': times[i][11:16],
                            'wind_speed': round(speeds[i], 1)
                        })
                        total_strong_wind_hours += 1
                
                if high_wind:
                    forecast_data = high_wind[:8]
                    low = total_strong_wind_hours * 30
                    high = total_strong_wind_hours * 60
                    estimated_earnings = f"£{low}-£{high}"
                    recommendation = f"Shift load to high-wind periods tomorrow. Strong wind expected for {total_strong_wind_hours} hours."
                else:
                    recommendation = "No strong wind surplus expected in the next 48 hours."
    except Exception as e:
        recommendation = f"Error fetching forecast: {str(e)[:80]}"
    
    return render(request, 'dashboard/site_detail.html', {
        'site': site,
        'forecast_data': forecast_data,
        'recommendation': recommendation,
        'estimated_earnings': estimated_earnings,
        'last_updated': last_updated
    })

@login_required
@require_POST
def delete_site(request, site_id):
    site = get_object_or_404(Site, id=site_id, user=request.user)
    site.delete()
    return redirect('dashboard_home')