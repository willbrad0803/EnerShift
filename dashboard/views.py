from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from .models import Site
import requests

# ======================
# User Registration
# ======================
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)                    # Automatically log the user in after registration
            return redirect('dashboard_home')
    else:
        form = UserCreationForm()
    
    return render(request, 'registration/login.html', {
        'form': form,
        'register_form': form,   # Used by the combined login/register template
    })

# ======================
# Dashboard Views
# ======================
@login_required
def dashboard_home(request):
    sites = Site.objects.filter(user=request.user)
    return render(request, 'dashboard/home.html', {'sites': sites})

@login_required
def all_sites_overview(request):
    sites = Site.objects.filter(user=request.user)
    total_estimated_earnings = len(sites) * 350  # Rough average monthly estimate
    return render(request, 'dashboard/all_sites.html', {
        'sites': sites,
        'total_estimated_earnings': total_estimated_earnings
    })

@login_required
def add_site(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        postcode = request.POST.get('postcode')
        industry_type = request.POST.get('industry_type')
        
        if name and postcode:
            Site.objects.create(
                user=request.user,
                name=name,
                postcode=postcode,
                industry_type=industry_type or 'Other'
            )
            return redirect('dashboard_home')
    
    return render(request, 'dashboard/add_site.html')

@login_required
def site_detail(request, site_id):
    site = get_object_or_404(Site, id=site_id, user=request.user)
    
    # Example API calls for forecast (you can expand this)
    try:
        pc_response = requests.get(f"https://api.postcodes.io/postcodes/{site.postcode.replace(' ', '')}")
        if pc_response.status_code == 200:
            data = pc_response.json()
            lat = data['result']['latitude']
            lon = data['result']['longitude']
            
            weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=wind_speed_10m"
            weather_response = requests.get(weather_url)
            forecast_data = weather_response.json() if weather_response.status_code == 200 else None
        else:
            forecast_data = None
    except:
        forecast_data = None

    return render(request, 'dashboard/site_detail.html', {
        'site': site,
        'forecast_data': forecast_data
    })

@login_required
def delete_site(request, site_id):
    site = get_object_or_404(Site, id=site_id, user=request.user)
    if request.method == 'POST':
        site.delete()
        return redirect('dashboard_home')
    return redirect('site_detail', site_id=site_id)

# Optional: Simple help view
@login_required
def help_view(request):
    return render(request, 'dashboard/help.html')
