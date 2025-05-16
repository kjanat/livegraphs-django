# dashboard/forms.py

from django import forms

from .models import Dashboard, DataSource


class DataSourceUploadForm(forms.ModelForm):
    """Form for uploading CSV files"""

    class Meta:
        model = DataSource
        fields = ["name", "description", "file"]

    def __init__(self, *args, **kwargs):
        self.company = kwargs.pop("company", None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.company:
            instance.company = self.company
        if commit:
            instance.save()
        return instance


class DashboardForm(forms.ModelForm):
    """Form for creating and editing dashboards"""

    class Meta:
        model = Dashboard
        fields = ["name", "description", "data_sources"]

    def __init__(self, *args, **kwargs):
        self.company = kwargs.pop("company", None)
        super().__init__(*args, **kwargs)

        if self.company:
            self.fields["data_sources"].queryset = DataSource.objects.filter(company=self.company)

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.company:
            instance.company = self.company
        if commit:
            instance.save()
            self.save_m2m()
        return instance
