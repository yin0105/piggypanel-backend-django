from django.contrib import admin
from django.http import HttpResponse
from django.urls import path
from .models import ZohoImportLeadsFieldsModel, ZohoImportLeadsModel, ZohoImportContactsFieldsModel, ZohoImportContactsModel, ZohoLeadsSyncSettings, ZohoContactsSyncSettings, ZohoSyncErrorLogs
from leads.models import leads, leads_fields
from contacts.models import contacts, contacts_fields
import zcrmsdk
from zcrmsdk import ZCRMRestClient
import json
from datetime import datetime, timezone
import superadmin

def importleadsfields_admin(request):
    try:
        module_ins = zcrmsdk.ZCRMModule.get_instance('Leads')# Module API Name
        resp = module_ins.get_all_fields()
        field_ins_arr = resp.data

        for field_ins in field_ins_arr:
            field_data = {}
            picklist_values = field_ins.picklist_values
            if picklist_values is not None:
                for picklist_value in picklist_values:
                   field_data[picklist_value.display_value] = picklist_value.actual_value

            lookup_field = field_ins.lookup_field
            if lookup_field is not None:                
                module_ins_lookup_data = zcrmsdk.ZCRMModule.get_instance(lookup_field.module)
                pointer = 0    
                total_records = 0    
                continue_loop = True
                while (continue_loop):
                    increment = 200
                    request_headers = dict()
                    pointer = pointer + 1
                    try:
                        resp_lookup = module_ins_lookup_data.get_records(None, None, None, pointer, increment)
                        if((resp_lookup.status_code == 'INVALID_DATA') or (resp_lookup.status_code == 'BAD REQUEST')):
                            continue_loop = False
                            break
                        else:
                            number_of_records = len(resp_lookup.data)
                            total_records += number_of_records
                            record_ins_arr_lookup = resp_lookup.data  # list of ZCRMRecord instance
                            for record_ins_lookup in record_ins_arr_lookup:
                                record_data = {}                       
                                if (record_ins_lookup.get_field_value("Name") == None):   
                                    field_display_value = None  
                                    field_actual_value = None   
                                else:
                                    field_display_value = str(record_ins_lookup.get_field_value("Name"))
                                    field_actual_value = record_ins_lookup.entity_id
                                field_data[field_display_value] = field_actual_value
                            if number_of_records < 200:
                                continue_loop = False
                    except zcrmsdk.ZCRMException as ex:
                        continue_loop = False
            if len(field_data) == 0:
                field_data_str = None
            else:
                field_data_str = field_data

            defaults = {
                'field_zoho_ref': field_ins.id,
                'field_api_name': field_ins.api_name,
                'field_label': field_ins.field_label,
                'field_type' : str(field_ins.data_type),
                'field_size' : int(field_ins.length),
                'field_iscustom' : field_ins.is_custom_field,
                'field_ismandatory' : field_ins.is_mandatory,
                'field_isreadonly' : field_ins.is_read_only,
                'field_isformulafield' : field_ins.is_formula_field,
                'field_iscurrencyfield' : field_ins.is_currency_field,
                'field_layout_permissions' : field_ins.field_layout_permissions,
                'field_data' : field_data_str,
            }
            leads_fields.objects.update_or_create(field_zoho_ref=field_ins.id, defaults=defaults)
            # print("\n\n")
    except zcrmsdk.ZCRMException as ex:
        ZohoSyncErrorLogs.objects.create(module_type='Leads Fields Sync', added_on=datetime.now(timezone.utc), error_code=ex.error_code, error_message=ex.error_message,error_details=ex.error_details,error_content=ex.error_content)
    
    return HttpResponse('Admin Custom View')

def importleads_admin(request):
    try:
        module_ins = zcrmsdk.ZCRMModule.get_instance('Leads')
        pointer = 0    
        total_records = 0    
        continue_loop = True
        while (continue_loop):
            increment = 200
            request_headers = dict()
            pointer = pointer + 1
            resp = module_ins.get_records(None, None, None, pointer, increment)  # Adding custom headers

            if((resp.status_code == 'INVALID_DATA') or (resp.status_code == 'BAD REQUEST')):
                continue_loop = False
                break
            else:
                number_of_records = len(resp.data)
                total_records += number_of_records
                fields = leads_fields.objects.values('field_api_name', 'field_type')       
                record_ins_arr = resp.data  # list of ZCRMRecord instance
                for record_ins in record_ins_arr:
                    record_data = {}
                    for field in fields:     
                        field_value = None   
                        if(field['field_type'] == "lookup"):
                            if (record_ins.get_field_value(field['field_api_name']) is not None):
                                lookup_data = record_ins.get_field_value(field['field_api_name'])
                                field_value = lookup_data.get('id')
                        else:    
                            if (record_ins.get_field_value(field['field_api_name']) == None):   
                                field_value = None     
                            else:
                                field_value = str(record_ins.get_field_value(field['field_api_name']))
                        
                        record_data[field['field_api_name']] = field_value
                
                    defaults = {
                        'zoho_ref': record_ins.entity_id,
                        'data': record_data
                    }
                    
                    leads.objects.update_or_create(zoho_ref=record_ins.entity_id, defaults=defaults) 
                    if number_of_records < 200:
                        continue_loop = False
               
    except zcrmsdk.ZCRMException as ex:
        if(ex.error_code != 'INVALID_DATA' and ex.error_code!='Not Modified'):
            ZohoSyncErrorLogs.objects.create(module_type='Leads - Full Sync', added_on=datetime.now(timezone.utc), error_code=ex.error_code, error_message=ex.error_message,error_details=ex.error_details,error_content=ex.error_content)
    return HttpResponse('Admin Custom View2')

def importcontactsfields_admin(request):
    try:
        module_ins = zcrmsdk.ZCRMModule.get_instance('Contacts')# Module API Name     
        resp = module_ins.get_all_fields()
        field_ins_arr = resp.data 
        for field_ins in field_ins_arr:
            print(field_ins.api_name)
            field_data = {}
            picklist_values = field_ins.picklist_values
            if picklist_values is not None:
                for picklist_value in picklist_values:
                   field_data[picklist_value.display_value] = picklist_value.actual_value

            lookup_field = field_ins.lookup_field
            if lookup_field is not None:  
                module_ins_lookup_data = zcrmsdk.ZCRMModule.get_instance(lookup_field.module)
                pointer = 0    
                total_records = 0    
                continue_loop = True
                while (continue_loop):
                    increment = 200
                    request_headers = dict()
                    pointer = pointer + 1
                    try:
                        resp_lookup = module_ins_lookup_data.get_records(None, None, None, pointer, increment)
                        if((resp_lookup.status_code == 'INVALID_DATA') or (resp_lookup.status_code == 'BAD REQUEST')):
                            continue_loop = False
                            # break
                        else:
                            number_of_records = len(resp_lookup.data)
                            total_records += number_of_records
                            record_ins_arr_lookup = resp_lookup.data  # list of ZCRMRecord instance
                            for record_ins_lookup in record_ins_arr_lookup:
                                record_data = {}                       
                                if (record_ins_lookup.get_field_value("Name") == None):   
                                    field_display_value = None  
                                    field_actual_value = None   
                                else:
                                    field_display_value = str(record_ins_lookup.get_field_value("Name"))
                                    field_actual_value = record_ins_lookup.entity_id
                                field_data[field_display_value] = field_actual_value
                            if number_of_records < 200:
                                continue_loop = False
                    except zcrmsdk.ZCRMException as ex:
                        continue_loop = False
            if len(field_data) == 0:
                field_data_str = None
            else:
                field_data_str = field_data

            defaults = {
                'field_zoho_ref': field_ins.id,
                'field_api_name': field_ins.api_name,
                'field_label': field_ins.field_label,
                'field_type' : str(field_ins.data_type),
                'field_size' : int(field_ins.length),
                'field_iscustom' : field_ins.is_custom_field,
                'field_ismandatory' : field_ins.is_mandatory,
                'field_isreadonly' : field_ins.is_read_only,
                'field_isformulafield' : field_ins.is_formula_field,
                'field_iscurrencyfield' : field_ins.is_currency_field,
                'field_layout_permissions' : field_ins.field_layout_permissions,
                'field_data' : field_data_str,
            }
            contacts_fields.objects.update_or_create(field_zoho_ref=field_ins.id, defaults=defaults)
    except zcrmsdk.ZCRMException as ex:
        ZohoSyncErrorLogs.objects.create(module_type='Contacts Fields Sync', added_on=datetime.now(timezone.utc), error_code=ex.error_code, error_message=ex.error_message,error_details=ex.error_details,error_content=ex.error_content)
    
    return HttpResponse('Admin Custom View')

def importcontacts_admin(request):
    try:
        module_ins = zcrmsdk.ZCRMModule.get_instance('Contacts')
        pointer = 0    
        total_records = 0    
        continue_loop = True
        while (continue_loop):
            increment = 200
            request_headers = dict()
            pointer = pointer + 1
            resp = module_ins.get_records(None, None, None, pointer, increment)  # Adding custom headers

            if((resp.status_code == 'INVALID_DATA') or (resp.status_code == 'BAD REQUEST')):
                continue_loop = False
                break
            else:
                number_of_records = len(resp.data)
                total_records += number_of_records
                fields = contacts_fields.objects.values('field_api_name', 'field_type')       
                record_ins_arr = resp.data  # list of ZCRMRecord instance
                for record_ins in record_ins_arr:
                    record_data = {}
                    for field in fields:  
                        field_value = None      
                        if(field['field_type'] == "lookup"):
                            if (record_ins.get_field_value(field['field_api_name']) is not None):
                                lookup_data = record_ins.get_field_value(field['field_api_name'])
                                field_value = lookup_data.get('id')
                        else:    
                            if (record_ins.get_field_value(field['field_api_name']) == None):   
                                field_value = None     
                            else:
                                field_value = str(record_ins.get_field_value(field['field_api_name']))
                        
                        record_data[field['field_api_name']] = field_value
                
                    defaults = {
                        'zoho_ref': record_ins.entity_id,
                        'data': record_data
                    }
                    
                    contacts.objects.update_or_create(zoho_ref=record_ins.entity_id, defaults=defaults) 
                    if number_of_records < 200:
                        continue_loop = False
               
    except zcrmsdk.ZCRMException as ex:
        if(ex.error_code != 'INVALID_DATA' and ex.error_code!='Not Modified'):
            ZohoSyncErrorLogs.objects.create(module_type='Contacts - Full Sync', added_on=datetime.now(timezone.utc), error_code=ex.error_code, error_message=ex.error_message,error_details=ex.error_details,error_content=ex.error_content)
    return HttpResponse('Admin Custom View2')

class ZohoImportLeadsFieldsModelAdmin(admin.ModelAdmin):
    model = ZohoImportLeadsFieldsModel

    def get_urls(self):
        view_name = '{}_{}_changelist'.format(
            self.model._meta.app_label, self.model._meta.model_name)
        return [
            path('importleadsfields', self.admin_site.admin_view(importleadsfields_admin), name=view_name),
        ]

superadmin.site.register(ZohoImportLeadsFieldsModel, ZohoImportLeadsFieldsModelAdmin)

class ZohoImportLeadsAdmin(admin.ModelAdmin):
    model = ZohoImportLeadsModel

    def get_urls(self):
        view_name = '{}_{}_changelist'.format(
            self.model._meta.app_label, self.model._meta.model_name)
        return [
            path('importleads', self.admin_site.admin_view(importleads_admin), name=view_name),
        ]

superadmin.site.register(ZohoImportLeadsModel, ZohoImportLeadsAdmin)

class ZohoImportContactsFieldsModelAdmin(admin.ModelAdmin):
    model = ZohoImportContactsFieldsModel

    def get_urls(self):
        view_name = '{}_{}_changelist'.format(
            self.model._meta.app_label, self.model._meta.model_name)
        return [
            path('importcontactsfields', self.admin_site.admin_view(importcontactsfields_admin), name=view_name),
        ]

# admin.site.register(ZohoImportContactsFieldsModel, ZohoImportContactsFieldsModelAdmin)

class ZohoImportContactsAdmin(admin.ModelAdmin):
    model = ZohoImportContactsModel

    def get_urls(self):
        view_name = '{}_{}_changelist'.format(
            self.model._meta.app_label, self.model._meta.model_name)
        return [
            path('importcontacts', self.admin_site.admin_view(importcontacts_admin), name=view_name),
        ]

# admin.site.register(ZohoImportContactsModel, ZohoImportContactsAdmin)

class ZohoLeadsSyncSettingsAdmin(admin.ModelAdmin):
    actions = None
    list_display_links = None
    list_display = ['leads_incremental_sync_last_run', 'leads_incremental_sync_last_run_count', 'leads_delete_sync_last_run', 'leads_delete_sync_last_run_count', 'leads_full_sync_last_run', 'leads_full_sync_last_run_count']
    readonly_fields=['leads_incremental_sync_last_run', 'leads_incremental_sync_last_run_count', 'leads_delete_sync_last_run', 'leads_delete_sync_last_run_count', 'leads_full_sync_last_run', 'leads_full_sync_last_run_count']

    def has_add_permission(self, request):
        return False
    def has_edit_permission(self, request):
        return False
    def has_delete_permission(self, request, obj=None):
        return False
    

class ZohoContactsSyncSettingsAdmin(admin.ModelAdmin):
    actions = None
    list_display_links = None
    list_display = ['contacts_incremental_sync_last_run', 'contacts_incremental_sync_last_run_count', 'contacts_delete_sync_last_run', 'contacts_delete_sync_last_run_count', 'contacts_full_sync_last_run', 'contacts_full_sync_last_run_count']
    readonly_fields=['contacts_incremental_sync_last_run', 'contacts_incremental_sync_last_run_count', 'contacts_delete_sync_last_run', 'contacts_delete_sync_last_run_count', 'contacts_full_sync_last_run', 'contacts_full_sync_last_run_count']

    def has_add_permission(self, request):
        return False
    def has_edit_permission(self, request):
        return False
    def has_delete_permission(self, request, obj=None):
        return False
    
class ZohoSyncErrorLogsAdmin(admin.ModelAdmin):
    list_display = ['module_type', 'added_on', 'error_code', 'error_message', 'error_content']
    ordering = ['-added_on']
    exclude=("field_api_name ",)
    readonly_fields=['module_type', 'added_on', 'error_code', 'error_message', 'error_details', 'error_content']

    def has_add_permission(self, request):
        return False
    def has_edit_permission(self, request):
        return False

admin.site.register(ZohoLeadsSyncSettings, ZohoLeadsSyncSettingsAdmin)
admin.site.register(ZohoContactsSyncSettings, ZohoContactsSyncSettingsAdmin)
admin.site.register(ZohoSyncErrorLogs, ZohoSyncErrorLogsAdmin)