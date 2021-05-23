from django.conf import settings
from rest_framework import serializers
from .models import contacts, contacts_fields, contacts_browse_layout, contacts_addedit_layout
from zoho.models import ZohoSyncErrorLogs
from datetime import datetime, timezone
import zcrmsdk

class ContactsFieldsSerializer(serializers.ModelSerializer):
    class Meta:
        model = contacts_fields
        fields = '__all__'

class ContactsBrowseLayoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = contacts_browse_layout
        fields = '__all__'
        depth = 1

class ContactsAddEditLayoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = contacts_addedit_layout
        fields = '__all__'
        depth = 2
        
class ContactsSerializer(serializers.ModelSerializer):
    lookups = serializers.SerializerMethodField()
    class Meta:
        model = contacts
        fields = ['id','zoho_ref','data','lookups']
    
    def get_lookups(self,obj):
        fields = contacts_fields.objects.filter(field_type='lookup').values('field_api_name','field_data')
        return_data = {}
        return_data = obj.data
        for field in fields:
            if field['field_data'] is not None:
                for (key,data) in field['field_data'].items():
                    if(data == obj.data[field['field_api_name']]):
                        return_data[field['field_api_name']] = key
            
        return ''

    def update(self, instance, validated_data):
        fields = contacts_addedit_layout.objects.filter(layout_field__isnull=False, layout_field_display_only=False).values_list('layout_field', flat=True)        
        fields_api_names = contacts_fields.objects.filter(pk__in=fields).values_list('field_api_name', flat=True)
        
        try:
            record_ins_list = list()
            record = zcrmsdk.ZCRMRecord.get_instance('Contacts')
            record.set_field_value('id', instance.zoho_ref) # record id
            for field in fields_api_names:
                record.set_field_value(str(field), validated_data['data'][field]) # record id
            if(settings.ZCRM_CONTACTS_FIELD_MAP_PANEL_UPDATE_DATE_TO_API_NAME):
                panel_update_date = settings.ZCRM_CONTACTS_FIELD_MAP_PANEL_UPDATE_DATE_TO_API_NAME
                field_type_update_date = contacts_fields.objects.values_list('field_type', flat=True).get(field_api_name=panel_update_date)
                if(field_type_update_date == "date"):
                    date_val = datetime.utcnow().strftime("%Y-%m-%d")
                if(field_type_update_date == "datetime"):
                    date_val = datetime.utcnow().isoformat("T", "seconds")
                record.set_field_value(panel_update_date, date_val)

                validated_data['data'][panel_update_date] = date_val
                
            record_ins_list.append(record)
            resp = zcrmsdk.ZCRMModule.get_instance('Contacts').update_records(record_ins_list)
            if(resp.status_code == 200):
                instance = super(ContactsSerializer,self).update(instance, validated_data)
                return instance
            else:
                entity_responses = resp.bulk_entity_response
                for entity_response in entity_responses:
                    error_details = entity_response.details
                    error_status = entity_response.status
                    error_message = entity_response.message
                ZohoSyncErrorLogs.objects.create(module_type='Contact Record Update From Panel', added_on=datetime.now(timezone.utc), error_code=error_status, error_message=error_message,error_details=error_details,error_content='Zoho Ref: '+instance.zoho_ref)
                error = {'error':'true','message':error_message,'detail': error_details}
                raise serializers.ValidationError(error)
        except zcrmsdk.ZCRMException as ex:
            ZohoSyncErrorLogs.objects.create(module_type='Contact Record Update From Panel', added_on=datetime.now(timezone.utc), error_code=ex.error_code, error_message=ex.error_message,error_details=ex.error_details,error_content=ex.error_content)
        
        
        
