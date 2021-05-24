from django.db import models
# from django.contrib.auth.models import User
from user.models import User
from channels.db import database_sync_to_async


class Chat(models.Model):
    name = models.CharField(max_length=64, default='')
    users = models.ManyToManyField(User, blank=True)
    receivers = models.TextField(blank=True, null=True)
    # receiver = models.TextField(blank=True, null=True)

    def __str__(self):
        description = ''
        for user in self.users.all():
            description += user.username
        return "users: " + description

    @property
    def group_name(self):
        return "chatting_room"
        # return "chat-%s" % self.id

    # @property
    # @database_sync_to_async
    # def receivers(self):
    #     rec = '_'
    #     for user in self.users.all():
    #         rec += user.id + '_'
    #     return rec

class Message(models.Model):
    text = models.TextField()
    date_sent = models.DateTimeField(auto_now_add=True)
    diff_time = models.TextField(blank=True, null=True)
    chat = models.ForeignKey(Chat, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)


class Unread(models.Model):    
    sender = models.IntegerField()
    receiver = models.IntegerField()
    unread = models.IntegerField(default=0)


class UserStatus(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    status = models.TextField()
    date_sent = models.DateTimeField(auto_now_add=True)