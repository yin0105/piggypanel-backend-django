from django.conf import settings
from django.db import models
from user.models import User
from django.contrib.auth.models import Group
import reversion
from reversion.admin import VersionAdmin
from django.db.models import CharField, Value as V
from django.db.models.functions import Concat
from django.utils.text import slugify
from django.core.exceptions import ObjectDoesNotExist
from user.utils import generate_username
import unicodedata
import uuid
import zcrmsdk

# Create your models here.

@reversion.register()
class leads(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    zoho_ref = models.CharField(max_length=50, blank=True, null=True, db_index=True)
    allocated_to = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    data = models.JSONField(verbose_name="Data", blank=True, null=True)
    updated = models.DateTimeField(verbose_name="Last Updated", auto_now_add=True)

    class Meta:
        db_table = ''
        managed = True
        verbose_name = 'Lead'
        verbose_name_plural = 'Leads'
    
    def save(self, *args, **kwargs):         
        allocated = self.data[settings.ZCRM_LEADS_FIELD_MAP_ALLOCATED_TO_API_NAME]
        if(allocated is not None):            
            try:
                name = allocated.split(' ',1)
                if len(name) == 1:
                    firstname = name[0]
                    lastname = ''
                    user = User.objects.get(first_name=allocated)
                else:
                    lastname = name[-1]
                    firstname = name[0]
                    user = User.objects.annotate(name=Concat('first_name',V(' '),'last_name')).get(name=allocated)
                         
                self.allocated_to = user
            except ObjectDoesNotExist:
                username = generate_username(allocated)
                password = User.objects.make_random_password()
                
                user = User.objects.create_user(username=username, password=password, first_name=firstname, last_name=lastname, is_active=True)
                user.save()
                agent = Group.objects.get(name='Agent') 
                user.groups.add(agent) 

                self.allocated_to=user
            
        super(leads, self).save(*args, **kwargs) 


@reversion.register()
class leads_fields(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    field_zoho_ref = models.CharField(max_length=100, verbose_name="Field Zoho Ref", blank=True, null=True, editable=False)
    field_api_name = models.CharField(max_length=50, verbose_name="API Name")
    field_label = models.CharField(max_length=50, verbose_name="Label")
    field_type = models.CharField(max_length=50, verbose_name="Type", editable=False)
    field_layout_permissions = models.CharField(max_length=50, verbose_name="Layout Permissions", editable=False)
    field_size = models.IntegerField(verbose_name="Field Size", blank=True, null=True, editable=False)
    field_iscustom = models.BooleanField(verbose_name="Is Custom Field", blank=True, null=True, editable=False, db_index=True)
    field_ismandatory = models.BooleanField(verbose_name="Is Mandatory", blank=True, null=True, editable=False, db_index=True)
    field_isreadonly = models.BooleanField(verbose_name="Is Read Only", blank=True, null=True, editable=False, db_index=True)
    field_isformulafield = models.BooleanField(verbose_name="Is Formula Field", blank=True, null=True, editable=False)
    field_iscurrencyfield = models.BooleanField(verbose_name="Is Currency Field", blank=True, null=True, editable=False)
    field_data = models.JSONField(verbose_name="Default Data", blank=True, null=True)

    def __str__(self) :
        # return "{fname} {lname} ({car})".format(fname=self.user.first_name, lname=self.user.last_name, car=self.number)
        return self.field_label + " (" + self.field_api_name + ") "

    class Meta:
        db_table = ''
        managed = True
        verbose_name = 'Field'
        verbose_name_plural = 'Fields'

@reversion.register()
class leads_addedit_layout(models.Model):
    id=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    layout_row = models.IntegerField(verbose_name="Row Number")
    layout_col = models.IntegerField(verbose_name="Column Number")
    layout_col_size = models.IntegerField(verbose_name="Column Grid Size", help_text="Total grid size for a full row should be 12")
    layout_field = models.ForeignKey(leads_fields,on_delete=models.SET_NULL, blank=True, null=True)
    layout_field_display_add_screen = models.BooleanField(verbose_name="Show on 'Add' screen", default=False, db_index=True)
    layout_field_display_only = models.BooleanField(verbose_name="Column Data NOT editable", default=False, db_index=True)
    layout_nbsp = models.BooleanField(verbose_name="Column is a whitespace", default=False, db_index=True)
    layout_hr = models.BooleanField(verbose_name="Section separator", default=False, db_index=True)

    class Meta:
        db_table = ''
        managed = True
        verbose_name = 'Add/Edit Lead Layout'
        verbose_name_plural = 'Add/Edit Lead Layout'

@reversion.register()
class leads_browse_layout(models.Model):
    id=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    layout_col = models.IntegerField(verbose_name="Column Number")
    layout_col_width = models.IntegerField(verbose_name="Column Width")
    layout_field = models.ForeignKey(leads_fields,on_delete=models.CASCADE)
    layout_field_searchable = models.BooleanField(verbose_name="Column Searchable", db_index=True)
    layout_field_sortable = models.BooleanField(verbose_name="Column Sortable", db_index=True)

    class Meta:
        db_table = ''
        managed = True
        verbose_name = 'Browse Leads Layout'
        verbose_name_plural = 'Browse Leads Layout'