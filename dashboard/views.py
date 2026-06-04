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
from .models import Site


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
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                token = default_token_generator.make_token(user)
                activation_link = f"https://www.enershift.energy/dashboard/activate/{uid}/{token}/"

                send_mail(
                    'Activate your EnerShift account',
                    f"Hi {user.email},\n\nPlease click here to activate your account:\n{activation_link}\n\nThis link expires in 48 hours.\n\nBest regards,\nThe EnerShift Team",
                    'noreply@enershift.energy',
                    [user.email]
                )
                return render(request, 'registration/account_activation_sent.html', {'email': user.email})
            except Exception:
                messages.error(request, "This email is already registered.")
        else:
            messages.error(request, "Passwords must match.")
    else:
        form = CustomUserCreationForm()

    return render(request, 'registration/login.html', {'form': form})


def activate(request, uidb64, token):
    print("Activation attempt - uidb64:", uidb64)
    print("Token:", token)
    
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
        print("User found:", user.email)
    except Exception as e:
        print("Decode/User error:", e)
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        messages.success(request, "✅ Account activated successfully!")
        return redirect('dashboard_home')
    else:
        print("❌ Token check failed")
        return render(request, 'registration/activation_invalid.html')

@login_required
def dashboard_home(request):
    sites = Site.objects.filter(user=request.user)
    return render(request, 'dashboard/home.html', {'sites': sites})


def custom_logout(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('home')
