from django.contrib import admin
from django import forms
from .models import leads

class LeadsLayoutFieldForm(forms.ModelForm):
    class Media:
        js = ('js/leadslayout-field-admin.js',)
