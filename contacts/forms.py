from django.contrib import admin
from django import forms
from .models import contacts

class ContactsLayoutFieldForm(forms.ModelForm):
    class Media:
        js = ('js/contactslayout-field-admin.js',)
