# accounts/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserChangeForm, CustomUserCreationForm
from .models import Company, CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ("username", "email", "company", "is_company_admin", "is_staff")
    list_filter = ("is_staff", "is_active", "company", "is_company_admin")
    fieldsets = (
        (None, {"fields": ("username", "email", "password")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Company", {"fields": ("company", "is_company_admin")}),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "email",
                    "password1",
                    "password2",
                    "company",
                    "is_company_admin",
                    "is_staff",
                    "is_active",
                ),
            },
        ),
    )
    search_fields = ("username", "email", "company__name")
    ordering = ("username",)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if obj.is_superuser and not obj.company:
            default_company, created = Company.objects.get_or_create(
                name="Default Organization",
                defaults={"description": "Default company for new superusers."},
            )
            obj.company = default_company
            obj.is_company_admin = True  # Optionally make the superuser an admin of this default company
            obj.save()


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at", "get_employee_count")
    search_fields = ("name", "description")

    @admin.display(description="Employees")
    def get_employee_count(self, obj):
        return obj.employees.count()
