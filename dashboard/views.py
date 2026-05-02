from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django import forms
from .models import Site, ConsumptionData
import requests
import csv
from datetime import datetime

# ======================
# Custom Form
# ======================
class CustomUserCreationForm(forms.ModelForm):
    email = forms.EmailField(required=True, label="Email Address")
    password1 = forms.CharField(widget=forms.PasswordInput, label="Password")
    password2 = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")

    class Meta:
        model = User
        fields = ['email']

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("password1") != cleaned_data.get("password2"):
            self.add_error('password2', "Passwords do not match")
        return cleaned_data

    def save(self, commit=True):
        user = User.objects.create_user(
            username=self.cleaned_data['email'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password1']
        )
        return user

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                user.is_active = False
                user.save()

                current_site = get_current_site(request)
                subject = 'Activate your EnerShift account'
                message = render_to_string('registration/account_activation_email.html', {
                    'user': user,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': default_token_generator.make_token(user),
                })
                send_mail(subject, message, 'noreply@enershift.energy', [user.email])

                return render(request, 'registration/account_activation_sent.html')
            except Exception as e:
                # Catch duplicate email/username
                messages.error(request, "This email address is already registered. Please login or use a different email.")
                form = CustomUserCreationForm()  # Reset form
        else:
            messages.error(request, "Please check your inputs. Passwords must match.")
    else:
        form = CustomUserCreationForm()

    return render(request, 'registration/login.html', {
        'form': form,
        'register_form': form,
    })


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except:
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        messages.success(request, "✅ Email verified! You are now logged in.")
        return redirect('dashboard_home')
    else:
        return render(request, 'registration/activation_invalid.html')


# Dashboard views...
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
                for i, wind in enumerate(forecast_data['hourly']['wind_speed_10m'][:24]):
                    if wind > 10:
                        recommendations.append({
                            'time': forecast_data['hourly']['time'][i],
                            'action': 'Shift chillers/compressors/pumps',
                            'reason': f'High wind ({wind:.1f} m/s)'
                        })
    except:
        pass

    return render(request, 'dashboard/site_detail.html', {
        'site': site,
        'consumption': consumption,
        'recommendations': recommendations
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
            messages.success(request, f"✅ Imported {count} records for {site.name}")
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
    return redirect('site_detail', site_id=site_id)


@login_required
def delete_site(request, site_id):
    site = get_object_or_404(Site, id=site_id, user=request.user)
    if request.method == 'POST':
        site.delete()
        messages.success(request, "Site deleted successfully")
        return redirect('dashboard_home')
    return redirect('site_detail', site_id=site_id)
