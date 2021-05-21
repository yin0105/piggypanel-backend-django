# from django.contrib.auth.models import User
from typing import OrderedDict
from user.models import User
from rest_framework.fields import SerializerMethodField

from . import models

from rest_framework import serializers
from datetime import date, datetime
import pytz
from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async



class MessageSerializer(serializers.ModelSerializer):
    # date_sent = serializers.DateTimeField()
    diff_time = SerializerMethodField
    class Meta:
        model = models.Message
        
        fields = '__all__'
        depth = 1

    def to_representation(self, instance):
        # representation = super(MessageSerializer, self).to_representation(instance)
        if instance.date_sent != None:
            diff = (datetime.utcnow().replace(tzinfo=pytz.UTC) - instance.date_sent).total_seconds()
            if diff < 1:
                instance.diff_time = "just now"
            elif diff < 60:
                instance.diff_time = "{} seconds ago".format(int(diff))
            elif diff < 3600:
                instance.diff_time = "{} minutes ago".format(int(diff // 60))
            elif diff < 86400:
                instance.diff_time = "{} hours ago".format(int(diff // 3600))
            elif diff < 86400 * 30:
                instance.diff_time = "{} days ago".format(int(diff // 86400))
            elif diff < 86400 * 365:
                instance.diff_time = "{} months ago".format(int(diff // (86400 * 30)))
            else:
                instance.diff_time = "{} years ago".format(int(diff // (86400 * 365)))
        representation = super(MessageSerializer, self).to_representation(instance)
        return representation


class MessageSerializerWS(serializers.ModelSerializer):
    # date_sent = serializers.DateTimeField()
    diff_time = SerializerMethodField
    class Meta:
        model = models.Message
        
        fields = '__all__'
        depth = 1

    @database_sync_to_async
    def to_representation(self, instance):
        # representation = super(MessageSerializer, self).to_representation(instance)
        if instance.date_sent != None:
            diff = (datetime.utcnow().replace(tzinfo=pytz.UTC) - instance.date_sent).total_seconds()
            if diff < 1:
                instance.diff_time = "just now"
            elif diff < 60:
                instance.diff_time = "{} seconds ago".format(int(diff))
            elif diff < 3600:
                instance.diff_time = "{} minutes ago".format(int(diff // 60))
            elif diff < 86400:
                instance.diff_time = "{} hours ago".format(int(diff // 3600))
            elif diff < 86400 * 30:
                instance.diff_time = "{} days ago".format(int(diff // 86400))
            elif diff < 86400 * 365:
                instance.diff_time = "{} months ago".format(int(diff // (86400 * 30)))
            else:
                instance.diff_time = "{} years ago".format(int(diff // (86400 * 365)))
        representation = super(MessageSerializer, self).to_representation(instance)
        return representation




class ChatSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = models.Chat
        fields = ('users', 'name', 'messages', 'id')
        depth = 1


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'