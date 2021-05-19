from django.contrib import admin
from django import forms
from .models import DBSync,Extensions
import json
import pickle
import zcrmsdk
from django.db import models
from django.db.models import Q, Count
from django.db.models.functions import Cast
# Register your models here.

class DBSyncAdmin(admin.ModelAdmin):
    list_display = ['hostname', 'username', 'password', 'enable_call_sync','database_name']
    ordering = ['hostname']

class ExtensionsAdmin(admin.ModelAdmin):
    list_display = ['extension', 'name', 'outbound_CID']
    ordering = ['extension']

admin.site.register(DBSync, DBSyncAdmin)
admin.site.register(Extensions, ExtensionsAdmin)