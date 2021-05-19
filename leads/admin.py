from django.contrib import admin
from django import forms
from .models import leads, leads_fields, leads_addedit_layout, leads_browse_layout
from .forms import LeadsLayoutFieldForm
import json
import pickle
from django.contrib.postgres.fields.jsonb import KeyTextTransform
from django.db import models
from django.db.models import Q, Count
from django.db.models.functions import Cast
from django.contrib.admin import widgets, ModelAdmin, SimpleListFilter
import zcrmsdk


class AdminLeadForm(forms.ModelForm):
    

    def __init__(self, *args, **kwargs):

        super(AdminLeadForm, self).__init__(*args,**kwargs)
        fields_properties = leads_fields.objects.all()
        
        for p in fields_properties:
            mandatory = False
            value_data = ''

            if self.instance.data is None:
                if 'CREATE' not in p.field_layout_permissions:
                    continue
                value_data = ''
            else:
                if 'EDIT' not in p.field_layout_permissions:
                    continue

                value_data = self.instance.data[p.field_api_name]

            if bool(p.field_ismandatory) == True:
                mandatory = True 

            if((p.field_type == "integer") and bool(p.field_isreadonly) != True): 
                self.base_fields[str(p.field_api_name)] = forms.IntegerField(label=str(p.field_label), initial=value_data, required=mandatory)
                self.fields[str(p.field_api_name)] = forms.IntegerField(label=str(p.field_label), initial=value_data, required=mandatory)

            if((p.field_type == "currency") and bool(p.field_isreadonly) != True): 
                self.base_fields[str(p.field_api_name)] = forms.DecimalField(label=str(p.field_label), initial=value_data, required=mandatory)
                self.fields[str(p.field_api_name)] = forms.DecimalField(label=str(p.field_label), initial=value_data, required=mandatory)

            if((p.field_type == "text") and bool(p.field_isreadonly) != True): 
                self.base_fields[str(p.field_api_name)] = forms.CharField(label=str(p.field_label), max_length=p.field_size, initial=value_data, required=mandatory)
                self.fields[str(p.field_api_name)] = forms.CharField(label=str(p.field_label), max_length=p.field_size, initial=value_data, required=mandatory)

            if((p.field_type == "picklist") and bool(p.field_isreadonly) != True): 
                choices = {}                
                for key, value in p.field_data.items():
                    choices[value] = key
                
                self.base_fields[str(p.field_api_name)] = forms.ChoiceField(label=str(p.field_label), initial=p.field_data, required=mandatory, choices=choices.items())
                self.fields[str(p.field_api_name)] = forms.ChoiceField(label=str(p.field_label), initial=p.field_data, required=mandatory, choices=choices.items())
            
            if(p.field_type == "boolean" and bool(p.field_isreadonly) != True):
                if(value_data=="True" or value_data=="on"):
                    checked = True
                else:
                    checked = False
                self.base_fields[str(p.field_api_name)] = forms.BooleanField(label=str(p.field_label), initial=checked, required=mandatory)
                self.fields[str(p.field_api_name)] = forms.BooleanField(label=str(p.field_label), initial=checked, required=mandatory)
            
            if(p.field_type == "textarea" and bool(p.field_isreadonly) != True):                
                self.base_fields[str(p.field_api_name)] = forms.CharField(widget=forms.Textarea,label=str(p.field_label), max_length=p.field_size, initial=value_data, required=mandatory)
                self.fields[str(p.field_api_name)] = forms.CharField(widget=forms.Textarea,label=str(p.field_label), max_length=p.field_size, initial=value_data, required=mandatory)
            
            if(p.field_type == "email" and bool(p.field_isreadonly) != True):                
                self.base_fields[str(p.field_api_name)] = forms.EmailField(label=str(p.field_label), max_length=p.field_size, initial=value_data, required=mandatory)
                self.fields[str(p.field_api_name)] = forms.EmailField(label=str(p.field_label), max_length=p.field_size, initial=value_data, required=mandatory)   

            if(p.field_type == "phone" and bool(p.field_isreadonly) != True):                
                self.base_fields[str(p.field_api_name)] = forms.ComboField(fields=[forms.CharField(max_length=p.field_size), forms.IntegerField()],initial=value_data, required=mandatory)
                self.fields[str(p.field_api_name)] = forms.ComboField(fields=[forms.CharField(max_length=p.field_size), forms.IntegerField()],initial=value_data, required=mandatory)      

            if((p.field_type == "datetime") and bool(p.field_isreadonly) != True):                
                self.base_fields[str(p.field_api_name)] = forms.DateTimeField(widget=widgets.AdminDateWidget(),label=str(p.field_label), initial=value_data, required=mandatory)
                self.fields[str(p.field_api_name)] = forms.DateTimeField(widget=widgets.AdminDateWidget(),label=str(p.field_label), initial=value_data, required=mandatory)  

            if((p.field_type == "date") and bool(p.field_isreadonly) != True):                
                self.base_fields[str(p.field_api_name)] = forms.DateTimeField(widget=widgets.AdminDateWidget(),label=str(p.field_label), initial=value_data, required=mandatory)
                self.fields[str(p.field_api_name)] = forms.DateTimeField(widget=widgets.AdminDateWidget(),label=str(p.field_label), initial=value_data, required=mandatory)

    class Meta:
        model = leads
        fields = ["allocated_to",]
       

class DuplicatePhoneRecordsFilter(SimpleListFilter):
    title = 'Duplicates' # a label for our filter
    parameter_name = 'duplicates' # you can put anything here

    def lookups(self, request, model_admin):
        # This is where you create filter options; we have two:
        return [
            ('phoneduplicates', 'Phone Only'),
            ('mobileduplicates', 'Mobile Only'),
            ('phonemobileduplicates', 'Mobile & Phone'),
            ('anyphonemobileduplicates', 'Any Mobile Or Phone'),
        ] 

    def queryset(self, request, queryset):
        # This is where you process parameters selected by use via filter options:
        if self.value() == 'phoneduplicates':
            
            dataset = leads.objects.values('data__Phone').exclude(data__Phone__exact='').exclude(data__Phone = None).annotate(group_phones = Count('data__Phone')).filter(group_phones__gte=2).values_list('data__Phone', flat=True)

            queryset = leads.objects.filter(data__Phone__in = dataset).order_by('data__Phone')

            return queryset
        if self.value() == 'mobileduplicates':
            
            dataset = leads.objects.values('data__Mobile').exclude(data__Mobile__exact='').exclude(data__Mobile = None).annotate(group_phones = Count('data__Mobile')).filter(group_phones__gte=2).values_list('data__Mobile', flat=True)

            queryset = leads.objects.filter(data__Mobile__in = dataset).order_by('data__Mobile')

            return queryset
        if self.value() == 'phonemobileduplicates':
            
            mobiledataset = leads.objects.values('data__Mobile').exclude(data__Mobile__exact='').exclude(data__Mobile = None).annotate(group_mobiles = Count('data__Mobile')).filter(group_mobiles__gte=2).values('data__Phone').exclude(data__Phone__exact='').exclude(data__Phone = None).annotate(group_phones = Count('data__Phone')).filter(group_phones__gte=2).values_list('data__Mobile', flat=True)

            queryset = leads.objects.filter(data__Mobile__in = mobiledataset).order_by('data__Mobile')

            return queryset
        if self.value() == 'anyphonemobileduplicates':
            
            mobiledataset = leads.objects.values('data__Mobile').exclude(data__Mobile__exact='').exclude(data__Mobile = None).values_list('data__Mobile', flat=True)

            phonedataset = leads.objects.values('data__Phone').exclude(data__Phone__exact='').exclude(data__Phone = None).values_list('data__Phone', flat=True)

            queryset = leads.objects.filter(Q(data__Phone__in = mobiledataset) | Q(data__Mobile__in = phonedataset)).order_by('data__Phone', 'data__Mobile')

            return queryset
        if self.value():
            # Get websites that don't have any pages.
            return queryset.distinct().filter(data__Phone__isnull=True)

class LeadsAdmin(admin.ModelAdmin):
    list_display = ['zoho_ref','full_name','phone','mobile','email']
    search_fields = ['zoho_ref', 'data__Full_Name', 'data__Phone', 'data__Mobile', 'data__Email']
    list_filter = (DuplicatePhoneRecordsFilter, )
    readonly_fields = ["zoho_ref",]

    def full_name(self, instance):
        return instance.data["Full_Name"]
    full_name.admin_order_field = "data__Full_Name"

    def phone(self, instance):
        return instance.data["Phone"]
    phone.admin_order_field = "data__Phone"

    def mobile(self, instance):
        return instance.data["Mobile"]
    mobile.admin_order_field = "data__Mobile"

    def email(self, instance):
        return instance.data["Email"]
    email.admin_order_field = "data__Email"

    def get_form(self, instance, request, obj=None, change=False, **kwargs):
        return AdminLeadForm
    
    def save_model(self, request, obj, form, change):
        lead_fields = leads_fields.objects.all()
        for field in lead_fields:
            layout_permissions = field.field_layout_permissions
            if 'EDIT' in layout_permissions:
                if field.field_type == 'boolean':
                    if field.field_api_name not in request.POST:
                        obj.data[field.field_api_name] = False
                        # field_api_names_boolean.append(field.field_api_name)

        for key,value in obj.data.items():
            if key in request.POST:
                if request.POST.get(key) == '-None-':
                    obj.data[key] = ''
                else:
                    if obj.data[key] != request.POST[key]:
                        obj.data[key] = request.POST[key]
        
        super().save_model(request, obj, form, change)
        

        
        field_api_names = []
        field_api_names_boolean = []
        field_api_names_integer = []
        field_api_names_currency = []
        for field in lead_fields:
            layout_permissions = field.field_layout_permissions
            if 'EDIT' in layout_permissions:
                if field.field_type == 'boolean':
                    field_api_names_boolean.append(field.field_api_name)
                elif field.field_type == 'integer':
                    field_api_names_integer.append(field.field_api_name)
                elif field.field_type == 'currency':
                    field_api_names_currency.append(field.field_api_name)
                elif field.field_type == 'ownerlookup':
                    continue
                else:    
                    field_api_names.append(field.field_api_name)
        try:
            record_ins_list = list()
            record = zcrmsdk.ZCRMRecord.get_instance('Leads')
            record.set_field_value('id', obj.zoho_ref) # record id
            for field_api_name in field_api_names:
                record.set_field_value(field_api_name, str(obj.data[field_api_name]))
            for field_api_name in field_api_names_boolean:
                
                if(obj.data[field_api_name] == '' or obj.data[field_api_name] is None):
                    record.set_field_value(field_api_name, False)
                else:
                    record.set_field_value(field_api_name, bool(obj.data[field_api_name]))
            for field_api_name in field_api_names_integer:
                if(obj.data[field_api_name] == '' or obj.data[field_api_name] is None):
                    record.set_field_value(field_api_name, None)
                else:
                    record.set_field_value(field_api_name, int(obj.data[field_api_name]))
            for field_api_name in field_api_names_currency:
                if(obj.data[field_api_name] == '' or obj.data[field_api_name] is None):
                    record.set_field_value(field_api_name, None)
                else:
                    record.set_field_value(field_api_name, float(obj.data[field_api_name]))
            record_ins_list.append(record)
            resp = zcrmsdk.ZCRMModule.get_instance('Leads').update_records(record_ins_list)
            print(resp.status_code)
            entity_responses = resp.bulk_entity_response
            for entity_response in entity_responses:
                print(entity_response.details)
                print(entity_response.status)
                print(entity_response.message)
                print(entity_response.data.entity_id)
                print(entity_response.data.created_by.id)
                print(entity_response.data.created_time)
                print(entity_response.data.modified_by.id)
                print("\n\n")
        except zcrmsdk.ZCRMException as ex:
            print(ex.status_code)  
            print(ex.error_message) 
            print(ex.error_code) 
            print(ex.error_details) 
            print(ex.error_content) 

class LeadFieldsAdmin(admin.ModelAdmin):
    list_display = ['field_api_name', 'field_label', 'field_type', 'field_iscustom']
    ordering = ['field_api_name']
    exclude=("field_api_name ",)
    readonly_fields=['field_api_name', 'field_type', 'field_size', 'field_data', 'field_zoho_ref', 'field_iscustom', 'field_ismandatory', 'field_isreadonly']

class LeadsLayoutAdmin(admin.ModelAdmin):
    form = LeadsLayoutFieldForm
    list_display = ['layout_row', 'layout_col', 'layout_col_size', 'layout_field', 'layout_field_display_only', 'layout_nbsp', 'layout_hr']
    ordering = ['layout_row', 'layout_col']

class LeadsBrowseLayoutAdmin(admin.ModelAdmin):
    list_display = ['layout_col', 'layout_col_width', 'layout_field', 'layout_field_searchable', 'layout_field_sortable']
    ordering = ['layout_col']

admin.site.register(leads, LeadsAdmin)
admin.site.register(leads_fields, LeadFieldsAdmin)
admin.site.register(leads_addedit_layout, LeadsLayoutAdmin)
admin.site.register(leads_browse_layout, LeadsBrowseLayoutAdmin)