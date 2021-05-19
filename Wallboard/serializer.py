from rest_framework import serializers
from .models import *


class wbcdrInfoSerializer(serializers.ModelSerializer):
    class Meta():
        model  = wbcdr
        # fields = ('calldata')
        fields = ('calldate','cid','src','dst','dcontext','channel','dstchannel','lastapp','lastdata','duration','billsec','disposition','amaflags','accountcode','uniqueid','userfield','did','recordingfile','cnum','cnam','outbound_cnum','outbound_cnam','dst_cnam','linkedid','peeraccount','sequence')
        # fields = "__all__"

class DBSyncInfoSerializer(serializers.ModelSerializer):
    class Meta():
        model  = DBSync
        fields = "__all__"

class StatsDayInfoSerializer(serializers.ModelSerializer):
    class Meta():
        model  = stats_day
        fields = ('firstcall','lastcall','duration','billsec','callqty')

class statsWeekInfoSerializer(serializers.ModelSerializer):
    class Meta():
        model  = stats_week
        fields = ('wcdate','extension','duration','billsec','callqty','callminutes')