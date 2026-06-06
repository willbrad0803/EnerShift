from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import login, logout
from django.contrib import messages
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django import forms
from .models import Site, SavingsLog

# === FORMS ===
class CustomUserCreationForm(forms.ModelForm):
    email = forms.EmailField(required=True)
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


class SiteForm(forms.ModelForm):
    class Meta:
        model = Site
        fields = ['name', 'postcode', 'address', 'industry_type', 'annual_kwh_estimate', 'meter_type', 'notes']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }


class SavingsLogForm(forms.ModelForm):
    class Meta:
        model = SavingsLog
        fields = ['date', 'baseline_kwh', 'actual_kwh', 'savings_notes']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }


# === VIEWS ===
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                user.is_active = False
                user.save()

                current_site = get_current_site(request)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                token = default_token_generator.make_token(user)
                activation_link = f"https://{current_site.domain}/dashboard/activate/{uid}/{token}/"

                send_mail(
                    'Activate your EnerShift account',
                    f"""Hi,\n\nPlease click the link below to activate your account:\n\n{activation_link}\n\nThis link expires in 7 days.""",
                    'noreply@enershift.energy',
                    [user.email],
                    fail_silently=False,
                )
                return render(request, 'registration/account_activation_sent.html', {'email': user.email})
            except Exception as e:
                messages.error(request, "This email is already registered.")
        else:
            messages.error(request, "Form error. Please check passwords match.")
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/login.html', {'form': form})


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
        messages.success(request, "✅ Account activated successfully! Welcome to EnerShift.")
        return redirect('dashboard_home')
    else:
        return render(request, 'registration/activation_invalid.html')


@login_required
def dashboard_home(request):
    sites = Site.objects.filter(user=request.user)
    recent_logs = SavingsLog.objects.filter(site__user=request.user)[:5]
    return render(request, 'dashboard/home.html', {
        'sites': sites,
        'recent_logs': recent_logs
    })


@login_required
def add_site(request):
    if request.method == 'POST':
        form = SiteForm(request.POST)
        if form.is_valid():
            site = form.save(commit=False)
            site.user = request.user
            site.save()
            messages.success(request, f"Site '{site.name}' added successfully!")
            return redirect('dashboard_home')
    else:
        form = SiteForm()
    return render(request, 'dashboard/add_site.html', {'form': form})


@login_required
def add_savings_log(request, site_id):
    site = get_object_or_404(Site, id=site_id, user=request.user)
    if request.method == 'POST':
        form = SavingsLogForm(request.POST)
        if form.is_valid():
            log = form.save(commit=False)
            log.site = site
            log.save()
            messages.success(request, "Savings log added!")
            return redirect('dashboard_home')
    else:
        form = SavingsLogForm(initial={'date': timezone.now().date()})
    return render(request, 'dashboard/add_savings_log.html', {'form': form, 'site': site})


def custom_logout(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect('home')
