from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.contrib import messages
from .models import Site, ConsumptionData
import requests
import csv
from datetime import datetime

# ======================
# Registration (Simple + Success Message)
# ======================
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "✅ Account created successfully! Welcome to EnerShift.")
            return redirect('dashboard_home')
    else:
        form = UserCreationForm()
    
    return render(request, 'registration/login.html', {
        'form': form,
        'register_form': form,
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
    total_estimated_earnings = len(sites) * 350
    return render(request, 'dashboard/all_sites.html', {
        'sites': sites,
        'total_estimated_earnings': total_estimated_earnings
    })


@login_required
def add_site(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        postcode = request.POST.get('postcode')
        industry_type = request.POST.get('industry_type', 'Other')
        if name and postcode:
            Site.objects.create(
                user=request.user,
                name=name,
                postcode=postcode,
                industry_type=industry_type
            )
            messages.success(request, f"Site '{name}' added successfully!")
            return redirect('dashboard_home')
    return render(request, 'dashboard/add_site.html')


@login_required
def site_detail(request, site_id):
    site = get_object_or_404(Site, id=site_id, user=request.user)
    consumption = ConsumptionData.objects.filter(site=site).order_by('timestamp')

    # Wind forecast + recommendations
    forecast_data = None
    recommendations = []
    try:
        pc_response = requests.get(f"https://api.postcodes.io/postcodes/{site.postcode.replace(' ', '')}")
        if pc_response.status_code == 200:
            data = pc_response.json()
            lat = data['result']['latitude']
            lon = data['result']['longitude']
            
            weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=wind_speed_10m"
            weather_response = requests.get(weather_url)
            if weather_response.status_code == 200:
                forecast_data = weather_response.json()
                
                # Simple recommendations
                for i, wind in enumerate(forecast_data['hourly']['wind_speed_10m'][:24]):
                    if wind > 10:
                        recommendations.append({
                            'time': forecast_data['hourly']['time'][i],
                            'action': 'Shift chillers, compressors or pumps',
                            'reason': f'High wind ({wind:.1f} m/s) → likely cheaper power'
                        })
    except:
        pass

    return render(request, 'dashboard/site_detail.html', {
        'site': site,
        'consumption': consumption,
        'forecast_data': forecast_data,
        'recommendations': recommendations[:6]
    })


@login_required
def upload_consumption(request, site_id):
    site = get_object_or_404(Site, id=site_id, user=request.user)
    
    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']
        
        if not csv_file.name.endswith('.csv'):
            messages.error(request, "Please upload a CSV file")
            return redirect('site_detail', site_id=site_id)
        
        try:
            file_content = csv_file.read().decode('utf-8').splitlines()
            reader = csv.DictReader(file_content)
            count = 0
            for row in reader:
                try:
                    timestamp = datetime.strptime(row['timestamp'], '%Y-%m-%d %H:%M:%S')
                    kwh = float(row['kwh'])
                    price = float(row.get('price_p_per_kwh', 0)) if row.get('price_p_per_kwh') else None
                    
                    ConsumptionData.objects.update_or_create(
                        site=site,
                        timestamp=timestamp,
                        defaults={'kwh': kwh, 'price_p_per_kwh': price}
                    )
                    count += 1
                except:
                    continue
            messages.success(request, f"✅ Imported {count} consumption records for {site.name}")
        except Exception as e:
            messages.error(request, f"Error processing file: {str(e)}")
    
    return redirect('site_detail', site_id=site_id)


@login_required
def delete_site(request, site_id):
    site = get_object_or_404(Site, id=site_id, user=request.user)
    if request.method == 'POST':
        site.delete()
        messages.success(request, "Site deleted successfully")
        return redirect('dashboard_home')
    return redirect('site_detail', site_id=site_id)
