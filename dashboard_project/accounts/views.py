# accounts/views.py

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import CompanyForm, CustomUserCreationForm
from .models import Company, CustomUser


def register_view(request):
    """View for user registration"""
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful.")
            return redirect("dashboard")
        else:
            messages.error(request, "Registration failed. Please correct the errors.")
    else:
        form = CustomUserCreationForm()

    return render(request, "accounts/register.html", {"form": form})


@login_required
def profile_view(request):
    """View for user profile"""
    user = request.user
    company = user.company

    context = {
        "user": user,
        "company": company,
    }

    return render(request, "accounts/profile.html", context)


@staff_member_required
def company_create_view(request):
    """View for creating companies (admin only)"""
    if request.method == "POST":
        form = CompanyForm(request.POST)
        if form.is_valid():
            company = form.save()
            messages.success(request, f"Company '{company.name}' created successfully.")
            return redirect("admin:accounts_company_changelist")
        else:
            messages.error(request, "Failed to create company. Please correct the errors.")
    else:
        form = CompanyForm()

    return render(request, "admin/accounts/company/create.html", {"form": form})


@staff_member_required
def company_users_view(request, company_id):
    """View for managing users in a company (admin only)"""
    company = Company.objects.get(pk=company_id)
    users = CustomUser.objects.filter(company=company)

    context = {
        "company": company,
        "users": users,
    }

    return render(request, "admin/accounts/company/users.html", context)
