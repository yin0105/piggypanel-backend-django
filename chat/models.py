from django.db import models
# from django.contrib.auth.models import User
from user.models import User
from channels.db import database_sync_to_async
from django.contrib.auth.models import Group


class Chat(models.Model):
    name = models.CharField(max_length=64, default='')
    users = models.ManyToManyField(User, blank=True)
    receivers = models.TextField(blank=True, null=True)

    def __str__(self):
        description = ''
        for user in self.users.all():
            description += user.username
        return "users: " + description

    @property
    def group_name(self):
        return "chatting_room"
        # return "chat-%s" % self.id

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
    user = models.IntegerField()
    status = models.TextField(default="off")
    date_sent = models.DateTimeField(auto_now_add=True)


class GroupMessagePermission(models.Model):
    sender_group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True, related_name='sender')
    receiver_group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True, related_name='receiver')
    enabled = models.BooleanField(default=False, verbose_name="Can Send Messages?", choices=(
            (True, 'Yes'),
            (False, 'No'),
        ))

    def __str__(self):
        return self.sender_group.name + " -> " + self.receiver_group.name + " : " + str(self.enabled)

    class Meta:
        ordering = ['sender_group']