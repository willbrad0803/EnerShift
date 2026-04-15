from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from .models import Site
import requests

# ======================
# Custom Registration Form with Email
# ======================
class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

# ======================
# Registration View (with email verification)
# ======================
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Require email verification
            user.save()

            # Send verification email
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
    else:
        form = CustomUserCreationForm()

    return render(request, 'registration/login.html', {
        'form': form,
        'register_form': form,
    })

# ======================
# Email Activation View
# ======================
def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return redirect('dashboard_home')
    else:
        return render(request, 'registration/activation_invalid.html')

# ======================
# Dashboard Views (protected)
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
            return redirect('dashboard_home')
    
    return render(request, 'dashboard/add_site.html')

@login_required
def site_detail(request, site_id):
    site = get_object_or_404(Site, id=site_id, user=request.user)
    
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

@login_required
def help_view(request):
    return render(request, 'dashboard/help.html')
