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
from django.utils import timezone

@reversion.register()
class DBSync(models.Model):
    id=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    hostname = models.CharField(verbose_name="hostname",max_length=50, blank=True, null=True, db_index=True)
    username = models.CharField(verbose_name="username",max_length=50, blank=True, null=True, db_index=True)
    password = models.CharField(verbose_name="password",max_length=50, blank=True, null=True, db_index=True)
    enable_call_sync = models.BooleanField(verbose_name="enable call sync",db_index=True)
    database_name = models.CharField(verbose_name="database name",max_length=50, blank=True, null=True, db_index=True)

    class Meta:
        db_table = ''
        managed = True
        verbose_name = 'DB Sync'
        verbose_name_plural = 'DB Sync'


@reversion.register()
class Extensions(models.Model):
    id=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    extension = models.CharField(verbose_name="extension",max_length=50, blank=True, null=True, db_index=True)
    name = models.CharField(verbose_name="name",max_length=50, blank=True, null=True, db_index=True)
    outbound_CID = models.CharField(verbose_name="outbound cid",max_length=50, blank=True, null=True, db_index=True)

    class Meta:
        db_table = ''
        managed = True
        verbose_name = 'Extensions'
        verbose_name_plural = 'Extensions'

# from datetimeutc.fields import DateTimeUTCField

@reversion.register()
class wbcdr(models.Model):
    id=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    calldate = models.DateTimeField(auto_now_add=False,blank=True)
    cid = models.CharField(max_length=80,blank=True)
    src = models.CharField(max_length=80,blank=True)
    dst = models.CharField(max_length=80,blank=True)
    dcontext = models.CharField(max_length=80,blank=True)
    channel = models.CharField(max_length=80,blank=True)
    dstchannel = models.CharField(max_length=80,blank=True)
    lastapp = models.CharField(max_length=80,blank=True)
    lastdata = models.CharField(max_length=80,blank=True)
    duration = models.IntegerField(blank=True)
    billsec = models.IntegerField(blank=True)
    disposition = models.CharField(max_length=80,blank=True)
    amaflags = models.IntegerField(blank=True)
    accountcode = models.CharField(max_length=80,blank=True)
    uniqueid = models.CharField(max_length=80,blank=True)
    userfield = models.CharField(max_length=80,blank=True)
    did = models.CharField(max_length=80,blank=True)
    recordingfile = models.CharField(max_length=80,blank=True)
    cnum = models.CharField(max_length=80,blank=True)
    cnam = models.CharField(max_length=80,blank=True)
    outbound_cnum = models.CharField(max_length=80,blank=True)
    outbound_cnam = models.CharField(max_length=80,blank=True)
    dst_cnam = models.CharField(max_length=80,blank=True)
    linkedid = models.CharField(max_length=80,blank=True)
    peeraccount = models.CharField(max_length=80,blank=True)
    sequence = models.IntegerField(blank=True)
    process_field = models.IntegerField(default=0)

class stats_day(models.Model):
    id=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cdate = models.DateTimeField(blank=True,null=True)
    extension = models.CharField(max_length=80,blank=True,null=True)
    firstcall = models.DateTimeField(blank=True,null=True)
    lastcall = models.DateTimeField(blank=True,null=True)
    duration = models.IntegerField(blank=True,null=True)
    billsec = models.IntegerField(blank=True,null=True)
    callqty = models.IntegerField(blank=True,null=True)
    callminutes = models.CharField(max_length=80,blank=True,null=True)
    

class stats_week(models.Model):
    id=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    wcdate = models.DateTimeField(blank=True,null=True)
    extension = models.CharField(max_length=80,blank=True,null=True)
    duration = models.IntegerField(blank=True,null=True)
    billsec = models.IntegerField(blank=True,null=True)
    callqty = models.IntegerField(blank=True,null=True)
    callminutes = models.CharField(max_length=80,blank=True,null=True)


class stats_month(models.Model):
    id=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    mcdate = models.DateTimeField(blank=True,null=True)
    extension = models.CharField(max_length=80,blank=True,null=True)
    duration = models.IntegerField(blank=True,null=True)
    billsec = models.IntegerField(blank=True,null=True)
    callqty = models.IntegerField(blank=True,null=True)
    callminutes = models.CharField(max_length=80,blank=True,null=True)
    

class stats_year(models.Model):
    id=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ycdate = models.DateTimeField(blank=True,null=True)
    extension = models.CharField(max_length=80,blank=True,null=True)
    duration = models.IntegerField(blank=True,null=True)
    billsec = models.IntegerField(blank=True,null=True)
    callqty = models.IntegerField(blank=True,null=True)
    callminutes = models.CharField(max_length=80,blank=True,null=True)
