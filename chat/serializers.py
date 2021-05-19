from django.contrib.auth.models import User
from rest_framework.fields import SerializerMethodField

from . import models

from rest_framework import serializers
from datetime import date, datetime
import pytz


class MessageSerializer(serializers.ModelSerializer):
    # date_sent = serializers.DateTimeField()
    diff_time = SerializerMethodField
    class Meta:
        model = models.Message
        
        fields = '__all__'
        depth = 1

    def to_representation(self, instance):
        representation = super(MessageSerializer, self).to_representation(instance)
        print("instance = ", instance)
        print("date_sent = ", instance.date_sent)
        print("date_sent = ", representation['date_sent'])
        if instance.date_sent != None:
            diff = (datetime.utcnow().replace(tzinfo=pytz.UTC) - instance.date_sent).total_seconds()
            if diff < 1:
                representation['diff_time'] = "just now"
            elif diff < 60:
                representation['diff_time'] = "{} seconds ago".format(int(diff))
            elif diff < 3600:
                representation['diff_time'] = "{} minutes ago".format(int(diff // 60))
            elif diff < 86400:
                representation['diff_time'] = "{} hours ago".format(int(diff // 3600))
            elif diff < 86400 * 30:
                representation['diff_time'] = "{} days ago".format(int(diff // 86400))
            elif diff < 86400 * 365:
                representation['diff_time'] = "{} months ago".format(int(diff // (86400 * 30)))
            else:
                representation['diff_time'] = "{} years ago".format(int(diff // (86400 * 365)))
            print(representation['diff_time'])
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