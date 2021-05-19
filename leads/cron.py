from leads.models import leads, leads_fields, leads_browse_layout, leads_addedit_layout
from zoho.models import ZohoLeadsSyncSettings, ZohoSyncErrorLogs
from datetime import datetime, timezone
import zcrmsdk

def leads_incremental_sync():
    try:
        leads_incremental_sync_last_run = ZohoLeadsSyncSettings.objects.values_list('leads_incremental_sync_last_run', flat = True).get(pk=1)
    except:
        leads_incremental_sync_last_run = None

    process_datetime = datetime.utcnow().replace(tzinfo=timezone.utc).astimezone().replace(microsecond=0).isoformat()  
    total_records = 0

    try:
        module_ins = zcrmsdk.ZCRMModule.get_instance('Leads')
        pointer = 0        
        continue_loop = True
        while (continue_loop):
            increment = 200
            request_headers = dict()
            additional_parameters = dict()
            records_to_delete = []
            additional_parameters['converted'] = 'both'
            pointer = pointer + 1
            
            if(leads_incremental_sync_last_run is not None):
                request_headers['If-Modified-Since'] = str(leads_incremental_sync_last_run.replace(tzinfo=timezone.utc).replace(microsecond=0).isoformat())
                resp = module_ins.get_records(None, None, None, pointer, increment, request_headers, additional_parameters)
            else:
                resp = module_ins.get_records(None, None, None, pointer, increment, None, additional_parameters)  # Adding custom headers

            if((resp.status_code == 'INVALID_DATA') or (resp.status_code == 'BAD REQUEST')):
                continue_loop = False
                break
            else:
                number_of_records = len(resp.data)
                total_records += number_of_records
                fields = leads_fields.objects.values('field_api_name', 'field_type')       
                record_ins_arr = resp.data  # list of ZCRMRecord instance
                for record_ins in record_ins_arr:
                    if(record_ins.properties['converted'] == True):
                        records_to_delete.append(record_ins.entity_id)
                    else:
                        record_data = {}
                        for field in fields:        
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
                
                if len(records_to_delete) > 0:
                    deleted_records = leads.objects.filter(zoho_ref__in = records_to_delete).delete()
                    total_deleted_records = deleted_records[0]
               
    except zcrmsdk.ZCRMException as ex:
        if(ex.error_code != 'INVALID_DATA' and ex.error_code!='Not Modified'):
            ZohoSyncErrorLogs.objects.create(module_type='Leads - Partial Sync', added_on=datetime.now(timezone.utc), error_code=ex.error_code, error_message=ex.error_message,error_details=ex.error_details,error_content=ex.error_content)
    
    leadsSyncSettings, created = ZohoLeadsSyncSettings.objects.update_or_create(id=1, defaults={'leads_incremental_sync_last_run':process_datetime, 'leads_incremental_sync_last_run_count':total_records})


def leads_delete_sync():
    try:
        leads_delete_sync_last_run = ZohoLeadsSyncSettings.objects.values_list('leads_delete_sync_last_run', flat = True).get(pk=1)
    except:
        leads_delete_sync_last_run = None
    
    total_deleted_records = 0
    process_datetime = datetime.utcnow().replace(tzinfo=timezone.utc).astimezone().replace(microsecond=0).isoformat()

    try:
        module_ins = zcrmsdk.ZCRMModule.get_instance('Leads') 
        
        pointer = 0
        continue_loop = True
        records_to_delete = []

        while (continue_loop):
            increment = 200
            request_headers = dict()
            pointer = pointer + 1
            if(leads_delete_sync_last_run is not None):
                request_headers['If-Modified-Since'] = str(leads_delete_sync_last_run.replace(tzinfo=timezone.utc).replace(microsecond=0).isoformat())
                resp = module_ins.get_all_deleted_records(pointer, increment, request_headers) 
            else:
                resp = module_ins.get_all_deleted_records(pointer, increment)
            
            trash_record_ins_arr = resp.data
            number_of_records = len(resp.data)
            resp_info = resp.info
            
            for record_ins in trash_record_ins_arr:
                records_to_delete.append(record_ins.id)

            if(resp_info.is_more_records):
                continue_loop = True
            else:
                continue_loop = False
        
        if len(records_to_delete) > 0:
            deleted_records = leads.objects.filter(zoho_ref__in = records_to_delete).delete()
            total_deleted_records = deleted_records[0]
    
    except zcrmsdk.ZCRMException as ex:
        if(ex.error_code != 'INVALID_DATA' and ex.error_code!='Not Modified'):
            ZohoSyncErrorLogs.objects.create(module_type='Leads - Delete', added_on=datetime.now(timezone.utc), error_code=ex.error_code, error_message=ex.error_message,error_details=ex.error_details,error_content=ex.error_content)
    
    leadsSyncSettings, created = ZohoLeadsSyncSettings.objects.update_or_create(id=1, defaults={'leads_delete_sync_last_run':process_datetime, 'leads_delete_sync_last_run_count':total_deleted_records})