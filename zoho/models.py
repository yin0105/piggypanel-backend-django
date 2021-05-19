from django.db import models
from zcrmsdk.OAuthClient import ZohoOAuthTokens

# Create your models here.
class ZohoOAuthHandler:
    @staticmethod
    def get_oauthtokens(email_address):
        oauth_model_instance = ZohoOAuth.objects.get(user_email=email_address)
        return ZohoOAuthTokens(oauth_model_instance.refresh_token,
                               oauth_model_instance.access_token,
                               oauth_model_instance.expiry_time,
                               user_email=oauth_model_instance.user_email)

    @staticmethod
    def save_oauthtokens(oauth_token):
        defaults = {
            'refresh_token': oauth_token.refreshToken,
            'access_token': oauth_token.accessToken,
            'expiry_time': oauth_token.expiryTime,
        }
        ZohoOAuth.objects.update_or_create(user_email=oauth_token.userEmail, defaults=defaults)


class ZohoOAuth(models.Model):

    refresh_token = models.CharField(max_length=250)
    access_token = models.CharField(max_length=250)
    expiry_time = models.BigIntegerField()
    user_email = models.EmailField()

class ZohoLeadsSyncSettings(models.Model):
    leads_incremental_sync_last_run = models.DateTimeField(verbose_name="Regular Sync Last Update", auto_now=False, auto_now_add=False, blank=True, null=True, editable=False)
    leads_incremental_sync_last_run_count = models.IntegerField(verbose_name="Regular Sync Last Update Count", blank=True, null=True, editable=False)    
    leads_delete_sync_last_run = models.DateTimeField(verbose_name="Delete Sync Last Update", auto_now=False, auto_now_add=False, blank=True, null=True, editable=False)
    leads_delete_sync_last_run_count = models.IntegerField(verbose_name="Delete Sync Last Update Count", blank=True, null=True, editable=False)
    leads_full_sync_last_run = models.DateTimeField(verbose_name="Full Sync Last Update", auto_now=False, auto_now_add=False, blank=True, null=True, editable=False)
    leads_full_sync_last_run_count = models.IntegerField(verbose_name="Full Sync Last Update", blank=True, null=True, editable=False)
    
    class Meta:
        db_table = ''
        managed = True
        verbose_name = 'Leads Sync Information'
        verbose_name_plural = 'Leads Sync Information'

class ZohoContactsSyncSettings(models.Model):
    contacts_incremental_sync_last_run = models.DateTimeField(verbose_name="Regular Sync Last Update", auto_now=False, auto_now_add=False, blank=True, null=True, editable=False)
    contacts_incremental_sync_last_run_count = models.IntegerField(verbose_name="Regular Sync Last Update Count", blank=True, null=True, editable=False)
    contacts_delete_sync_last_run = models.DateTimeField(verbose_name="Delete Sync Last Update", auto_now=False, auto_now_add=False, blank=True, null=True, editable=False)
    contacts_delete_sync_last_run_count = models.IntegerField(verbose_name="Delete Sync Last Update Count", blank=True, null=True, editable=False)
    contacts_full_sync_last_run = models.DateTimeField(verbose_name="Full Sync Last Update", auto_now=False, auto_now_add=False, blank=True, null=True, editable=False)
    contacts_full_sync_last_run_count = models.IntegerField(verbose_name="Full Sync Last Update", blank=True, null=True, editable=False)

    class Meta:
        db_table = ''
        managed = True
        verbose_name = 'Contacts Sync Information'
        verbose_name_plural = 'Contacts Sync Information'
    
class ZohoSyncErrorLogs(models.Model):
    id = models.AutoField(primary_key=True)
    module_type = models.CharField(verbose_name="Module", max_length = 150, blank=True, null=True, editable=False)
    added_on = models.DateTimeField(verbose_name="Date/Time", auto_now=False, auto_now_add=False, blank=True, null=True, editable=False)
    error_code = models.CharField(verbose_name="Error Code", max_length = 50, blank=True, null=True, editable=False)
    error_message = models.CharField(verbose_name="Error Message", max_length = 200, blank=True, null=True, editable=False)
    error_details = models.TextField(verbose_name="Error Details", blank=True, null=True, editable=False)
    error_content = models.TextField(verbose_name="Error Content", blank=True, null=True, editable=False)

    class Meta:
        db_table = ''
        managed = True
        verbose_name = 'Sync Error Log'
        verbose_name_plural = 'Sync Error Logs'
    
    
    

# Zoho Import Leads Fields
class ZohoImportLeadsFieldsModel(models.Model):
    class Meta:
        verbose_name_plural = 'Import Lead Fields'
        app_label = 'zoho'
        managed=False

# Zoho Import Leads
class ZohoImportLeadsModel(models.Model):
    class Meta:
        verbose_name_plural = 'Import Leads'
        app_label = 'zoho'
        managed = False

# Zoho Import Leads Fields
class ZohoImportContactsFieldsModel(models.Model):
    class Meta:
        verbose_name_plural = 'Import Contact Fields'
        app_label = 'zoho'
        managed=False

# Zoho Import Leads
class ZohoImportContactsModel(models.Model):
    class Meta:
        verbose_name_plural = 'Import Contacts'
        app_label = 'zoho'
        managed = False