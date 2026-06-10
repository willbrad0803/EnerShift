from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Site
from .forms import SiteForm


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
            messages.success(request, f"Site '{site.name}' added successfully!")
            return redirect('dashboard_home')
    else:
        form = SiteForm()
    return render(request, 'dashboard/add_site.html', {'form': form})


def custom_logout(request):
    from django.contrib.auth import logout
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('account_login')
