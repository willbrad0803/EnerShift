from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django import forms
from .models import Site

# Custom Registration Form
class CustomUserCreationForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)

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
                activation_link = f"https://www.enershift.energy/dashboard/activate/{uid}/{token}/"

                subject = 'Activate your EnerShift account'
                message = f"""Hi {user.email},

Thank you for signing up!

Please click here to activate: {activation_link}

Best,
EnerShift Team"""

                send_mail(subject, message, 'noreply@enershift.energy', [user.email])
                return render(request, 'registration/account_activation_sent.html', {'email': user.email})

            except Exception:
                messages.error(request, "This email is already registered.")
        else:
            messages.error(request, "Passwords must match.")
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

    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        messages.success(request, "✅ Account activated! Welcome.")
        return redirect('dashboard_home')
    else:
        return render(request, 'registration/activation_invalid.html')


# Login (using Django's built-in)
from django.contrib.auth.views import LoginView

class CustomLoginView(LoginView):
    template_name = 'registration/login.html'
    redirect_authenticated_user = True


# Logout
def custom_logout(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect('home')


# Dashboard Views
@login_required
def dashboard_home(request):
    sites = Site.objects.filter(user=request.user)
    return render(request, 'dashboard/home.html', {'sites': sites})

@login_required
def add_site(request):
    if request.method == 'POST':
        name = request.POST.get('name', 'New Site')
        postcode = request.POST.get('postcode', '')
        site = Site.objects.create(user=request.user, name=name, postcode=postcode)
        messages.success(request, f"Site '{name}' created.")
        return redirect('site_detail', site_id=site.id)
    return render(request, 'dashboard/add_site.html')

@login_required
def site_detail(request, site_id):
    site = get_object_or_404(Site, id=site_id, user=request.user)
    return render(request, 'dashboard/site_detail.html', {'site': site})

@login_required
def delete_site(request, site_id):
    site = get_object_or_404(Site, id=site_id, user=request.user)
    site.delete()
    messages.success(request, "Site deleted.")
    return redirect('dashboard_home')
