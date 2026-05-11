from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import login, logout
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django import forms
from .models import Site
import requests

# Custom Form
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


# Register
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

                subject = 'Activate your EnerShift account'
                message = f"""Hi {user.email},

Thank you for signing up to EnerShift!

Please click the link below to activate your account:

{activation_link}

This link expires in 48 hours.

Best regards,
The EnerShift Team"""

                send_mail(subject, message, DEFAULT_FROM_EMAIL, [user.email])
                print(f"✅ Activation email sent to {user.email}")

                return render(request, 'registration/account_activation_sent.html', {'email': user.email})

            except Exception as e:
                messages.error(request, "This email is already registered. Please log in.")
        else:
            messages.error(request, "Please check your inputs — passwords must match.")
    else:
        form = CustomUserCreationForm()

    return render(request, 'registration/login.html', {'form': form})


# Activate
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
        messages.success(request, "✅ Your account has been activated successfully!")
        return redirect('dashboard_home')
    else:
        return render(request, 'registration/activation_invalid.html')


# Dashboard
@login_required
def dashboard_home(request):
    sites = Site.objects.filter(user=request.user)
    return render(request, 'dashboard/home.html', {'sites': sites})


def custom_logout(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('home')
