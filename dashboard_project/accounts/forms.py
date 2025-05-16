# accounts/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Company, CustomUser


class CustomUserCreationForm(UserCreationForm):
    """Form for creating new users"""

    class Meta:
        model = CustomUser
        fields = ("username", "email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add help text for fields
        self.fields["email"].required = True
        self.fields["email"].help_text = "Required. Enter a valid email address."


class CustomUserChangeForm(forms.ModelForm):
    """Form for updating users"""

    class Meta:
        model = CustomUser
        fields = ("username", "email", "company", "is_company_admin")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only staff members can change company and admin status
        if not kwargs.get("instance") or not kwargs.get("instance").is_staff:
            if "company" in self.fields:
                self.fields["company"].disabled = True
            if "is_company_admin" in self.fields:
                self.fields["is_company_admin"].disabled = True


class CompanyForm(forms.ModelForm):
    """Form for creating and updating companies"""

    class Meta:
        model = Company
        fields = ("name", "description")
