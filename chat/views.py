import json

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http.response import HttpResponse
from user.models import User
from django.db.models import Q
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView

from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from . import models, serializers
from rest_framework.decorators import api_view
from django import core
from datetime import datetime
import pytz
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import Group
from django.forms.models import model_to_dict
from collections import OrderedDict
from django.shortcuts import redirect


class IndexView(LoginRequiredMixin, TemplateView):
    login_url = reverse_lazy('login')
    redirect_field_name = 'redirect_to'
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        user = User.objects.filter(id=self.request.GET.get("user_id")).first()
        chat = user.chat_set.all()
        if not chat:
            context['chat'] = 0
        else:
            context['chat'] = chat[0].id
        return context


@api_view(['POST'])
def createChat(request):
    data = request.POST
    sender = User.objects.get(pk=int(data['sender']))
    chat_name = "_{}_{}_".format(sender.id, data['receiver'])

    chat = models.Chat.objects.filter(Q(name=chat_name)) # | Q(name=chat_name_flip)
    if not chat:
        chat = models.Chat.objects.create(name=chat_name)
        chat.save()
    else:
        chat = chat[0]
        chat.users.set([])

    chat.users.add(sender) 
    chat.receivers = "_{}_".format(sender.id)

    if data['receiver'].find("@") > -1 :
        group_name = data['receiver'][1:]
        if group_name.lower() == "admin":
            receivers = User.objects.filter(Q(is_superuser=True) , ~Q(id=int(data['sender']))) 
        else:
            receivers = User.objects.filter(Q(groups__name__iexact=group_name) , ~Q(id=int(data['sender'])))
        
        for receiver in receivers:
            chat.users.add(receiver)
            chat.receivers += str(receiver.id) + "_"
        chat.save()        
    else:
        receiver = User.objects.get(pk=int(data['receiver']))
        chat.users.add(receiver)
        chat.receivers += str(receiver.id) + "_"
        chat.save()

        models.Unread.objects.filter(sender=receiver.id, receiver=sender.id).update(unread=0)

        chat_clone = serializers.ChatSerializer(chat).data.copy()
        messages = [serializers.MessageSerializer(msg).data for msg in models.Message.objects.select_related('chat').filter(Q(Q(chat__receivers__startswith="_{}_".format(receiver.id)) & Q(chat__receivers__contains="_{}_".format(sender.id))) | Q(Q(chat__receivers__startswith="_{}_".format(sender.id)) & Q(chat__receivers__contains="_{}_".format(receiver.id))) ).order_by('date_sent')]
        chat_clone["messages"] = messages
        return JsonResponse(data=chat_clone)
    
    return JsonResponse(data=serializers.ChatSerializer(chat).data)


@api_view(['POST'])
def getMessages(request):
    data = request.GET
    sender = int(data['sender'])
    receiver = int(data['receiver'])
    messages = [serializers.MessageSerializer(msg).data for msg in models.Message.objects.select_related('chat').filter(Q(Q(chat__receivers__startswith="_{}_".format(receiver)) & Q(chat__receivers__contains="_{}_".format(sender))) | Q(Q(chat__receivers__startswith="_{}_".format(sender)) & Q(chat__receivers__contains="_{}_".format(receiver))) ).order_by('date_sent')]

    return JsonResponse(data={"messages": messages})


@api_view(['POST'])
def removeMsg(request):
    id = request.GET.get("id")
    msg = models.Message.objects.get(id=id)
    sender_id = msg.sender_id
    models.Message.objects.filter(id=id).delete()
    return JsonResponse(data={"data": "ok"})


def getUnread(request):
    data = request.GET
    
    receiver = int(data['receiver'])

    if data['sender'].find("@") == -1:
        sender = int(data['sender'])    

        user_status, created = models.UserStatus.objects.update_or_create(
            user=receiver,
            defaults={'date_sent': datetime.now()},
        )
        if user_status.status == 'off':
            user_status.status = 'on'
        user_status.save()

        models.Unread.objects.filter(sender=sender, receiver=receiver).update(unread=0)
    
    unread_list = []
    unreads = models.Unread.objects.filter(receiver=receiver)
    for row in unreads:
        unread_list.append({"user": row.sender, "unread": row.unread})

    user_status_list = []
    user_statuses = models.UserStatus.objects.all()
    for row in user_statuses:
        if (datetime.utcnow().replace(tzinfo=pytz.UTC) - row.date_sent).total_seconds() > 300:
            row.status = 'off'
            row.save()
        user_status_list.append({"user": row.user, "status": row.status})

    return JsonResponse(data={"unread": unread_list, "user_status": user_status_list})
    

class ChatViewSet(ModelViewSet):    
    serializer_class = serializers.ChatSerializer

    def list(self, request):
        queryset = models.Chat.objects.filter(name__contains="_{}_".format(self.request.user.id))
        serializer = serializers.ChatSerializer(queryset, many=True)
        return Response(serializer.data)


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer

    def list(self, request, *args, **kwargs):
        user = User.objects.get(id=request.GET.get("user"))
        user_group = user.groups.values_list()[0]
        
        # Get Receiver Group (Sender Group including user)
        queryset = models.GroupMessagePermission.objects.select_related("sender_group").filter(Q(sender_group_id=user_group[0]), Q(enabled=True))
        receiver_group_list = [row.receiver_group_id for row in queryset]

        queryset = User.objects.select_related("auth_token").filter(Q(groups__id__in=receiver_group_list), ~Q(id=user.id))        
        serializer = self.get_serializer(queryset, many=True)
        receiver_user_list = serializer.data

        for row in receiver_user_list:
            row["transmissible"] = True

        # Get Sender Group (Receiver Group including user)
        queryset = models.GroupMessagePermission.objects.select_related("receiver_group").filter(Q(receiver_group_id=user_group[0]), Q(enabled=True))
        # sender_group_list = [row.sender_group_id for row in queryset if not row.sender_group_id in receiver_group_list]
        sender_group_list = [row.sender_group_id for row in queryset]
        
        queryset = User.objects.select_related("auth_token").filter(Q(groups__id__in=sender_group_list), ~Q(id=user.id))
        serializer = self.get_serializer(queryset, many=True)
        sender_user_list = serializer.data

        queryset = Group.objects.filter(id__in=receiver_group_list)
        
        data = []
        for row in queryset:
            group_name = "@" + row.name
            data.append(OrderedDict([("id", group_name), ("first_name", group_name), ("last_name", ""),  ("last_login", ""), ("unread", 0), ("status", "on"), ("transmissible", True)]))
        
        for row in receiver_user_list:
            if "chat" in request.GET:
                try:
                    msgs = models.Message.objects.select_related("chat").filter(Q(sender_id=user.id) & Q(chat__receivers__contains="_" + str(row["id"]) + "_") | Q(sender_id=row["id"]), Q(chat__receivers__contains="_" + str(user.id) + "_"))

                    if not msgs:
                        continue
                except:
                    continue
                
            try:
                user_status = models.UserStatus.objects.get(user=row["id"])
                if user_status.status != "on": continue
            except:
                continue

            data.append(row)
        for row in sender_user_list:
            if "chat" in request.GET:
                try:
                    msgs = models.Message.objects.select_related("chat").filter(Q(sender_id=user.id) & Q(chat__receivers__contains="_" + str(row["id"]) + "_") | Q(sender_id=row["id"]), Q(chat__receivers__contains="_" + str(user.id) + "_"))                    
                    if not msgs:
                        continue
                except:
                    continue

            try:
                user_status = models.UserStatus.objects.get(user=row["id"])
                if user_status.status != "on": continue
            except:
                continue

            for elem in data:
                if elem["id"] == row["id"]:
                    break
            else:
                data.append(row)

        return Response(data)


class UserView(CreateView):
    form_class = UserCreationForm
    template_name = 'registration/form.html'
    success_url = reverse_lazy('home')