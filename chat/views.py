import json

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http.response import HttpResponse
# from django.contrib.auth.models import User
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
    # chat_name_flip = "_{}_{}_".format(sender.id, receiver.id)

    chat = models.Chat.objects.filter(Q(name=chat_name)) # | Q(name=chat_name_flip)
    if not chat:
        chat = models.Chat.objects.create(name=chat_name)
        chat.save()
        chat.users.add(sender)
        chat.receivers = "_{}_".format(sender.id)

        if data['receiver'].find("@") > -1 :
            group_name = data['receiver'][1:]
            receivers = User.objects.get(Q(group=group_name) & Q(id!=int(data['sender'])))
            for receiver in receivers:
                print("== receiver id: ", receiver.id)
                chat.users.add(receiver)
                chat.receivers += str(receiver.id) + "_"
            chat.save()        
        else:
            receiver = User.objects.get(pk=int(data['receiver']))
            chat.users.add(receiver)
            chat.receivers += str(receiver.id) + "_"
            chat.save()

            chat_clone = serializers.ChatSerializer(chat).data.copy()
            messages = [serializers.MessageSerializer(msg).data for msg in models.Message.objects.select_related('chat').filter(Q(Q(chat__receivers__startswith="_{}_".format(receiver.id)) & Q(chat__receivers__contains="_{}_".format(sender.id))) | Q(Q(chat__receivers__startswith="_{}_".format(sender.id)) & Q(chat__receivers__contains="_{}_".format(receiver.id))) ).order_by('date_sent')]
            chat_clone["messages"] = messages
            return JsonResponse(data=chat_clone)
    else:
        chat = chat[0]

        if data['receiver'].find("@") == -1 :
            receiver = User.objects.get(pk=int(data['receiver']))
            chat_clone = serializers.ChatSerializer(chat).data.copy()
            messages = [serializers.MessageSerializer(msg).data for msg in models.Message.objects.select_related('chat').filter(Q(Q(chat__receivers__startswith="_{}_".format(receiver.id)) & Q(chat__receivers__contains="_{}_".format(sender.id))) | Q(Q(chat__receivers__startswith="_{}_".format(sender.id)) & Q(chat__receivers__contains="_{}_".format(receiver.id))) ).order_by('date_sent')]
            chat_clone["messages"] = messages
            return JsonResponse(data=chat_clone)
    
    # if not chat.users.all():
    #     chat.users.add(receiver, sender)
    #     chat.save()
        
    return JsonResponse(data=serializers.ChatSerializer(chat).data)


# @api_view(['POST'])
def getMessages(request):
    data = request.GET
    sender = int(data['sender'])
    receiver = int(data['receiver'])
    # messages = core.serializers.serialize("json", models.Message.objects.filter(sender_id__in=[sender, receiver]).order_by('date_sent'))
    # return JsonResponse({"data": messages})
    # models.Message.objects.select_related('chat').filter(Q(Q(chat__receivers__startswith="_{}_".format(receiver)) & Q(chat__receivers__contains="_{}_".format(sender))) | Q(Q(chat__receivers__startswith="_{}_".format(sender)) & Q(chat__receivers__contains="_{}_".format(receiver))) )

    messages = [serializers.MessageSerializer(msg).data for msg in models.Message.objects.select_related('chat').filter(Q(Q(chat__receivers__startswith="_{}_".format(receiver)) & Q(chat__receivers__contains="_{}_".format(sender))) | Q(Q(chat__receivers__startswith="_{}_".format(sender)) & Q(chat__receivers__contains="_{}_".format(receiver))) ).order_by('date_sent')]

    return JsonResponse(data={"messages": messages})

    return HttpResponse(messages)


class ChatViewSet(ModelViewSet):    
    serializer_class = serializers.ChatSerializer

    # posts = ""
    # if "name" in request.GET :
    #     posts = Schedule.objects.filter(name = request.GET["name"])
    # else:
    # def get_queryset(self):
    #     queryset = models.Chat.objects.all()
    #     print("== queryset = ", queryset)
    #     serializer = serializers.ChatSerializer(queryset, many=True)

    #     return Response(serializer.data)

    def list(self, request):
        queryset = models.Chat.objects.filter(name__contains="_{}_".format(self.request.user.id))
        # queryset = models.Chat.objects.all()
        serializer = serializers.ChatSerializer(queryset, many=True)
        return Response(serializer.data)
    # def get_queryset(self):
    #     print("======= new user = ", self.request.user)
    #     # user = User.objects.filter(id=self.request.GET.get("user_id")).first()
    #     user = self.request.user
    #     # return user.chat_set.all().order_by('-pk')
    #     # return self.request.user.chat_set.all().order_by('-pk')

    #     queryset = self.filter_queryset(self.get_queryset().exclude(username=self.request.user.username))
    #     serializer = self.get_serializer(queryset, many=True)
    #     return Response(serializer.data)

        
        


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer

    def list(self, request, *args, **kwargs):
        print("=== self.request.user.username = ", self.request.user.username)
        queryset = self.filter_queryset(self.get_queryset().exclude(username=self.request.user.username))

        # if page is not None:
        #     serializer = self.get_serializer(page, many=True)
        #     return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    # queryset = User.objects.all()
    # serializer_class = serializers.UserSerializer

    # def list(self, request, *args, **kwargs):
    #     print("== UserViewSet : ", self.request.GET.get("user_id"))
    #     if self.request.GET.get("user_id") == None:
    #         queryset = self.filter_queryset(self.get_queryset())
    #     else:    
    #         user = User.objects.filter(id=self.request.GET.get("user_id")).first()
    #         queryset = self.filter_queryset(self.get_queryset().exclude(username=user.username))

    #     # page = self.paginate_queryset(queryset)
    #     # print("== page ", page)
    #     # if page is not None:
    #     #     serializer = self.get_serializer(page, many=True)
    #     #     print("== serializer ", serializer)
    #     #     self.get_paginated_response(serializer.data)
    #     #     return self.get_paginated_response(serializer.data)

    #     serializer = self.get_serializer(queryset, many=True)
    #     return Response(serializer.data)


class UserView(CreateView):
    form_class = UserCreationForm
    template_name = 'registration/form.html'
    success_url = reverse_lazy('home')