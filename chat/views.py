import json

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
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
    print("== createChat => ", data)
    receiver = User.objects.get(pk=int(data['receiver']))
    sender = User.objects.get(pk=int(data['sender']))
    chat_name = receiver.username + sender.username
    chat_name_flip = sender.username + receiver.username

    chat = models.Chat.objects.filter(Q(name=chat_name) | Q(name=chat_name_flip))
    if not chat:
        chat = models.Chat.objects.create(name=chat_name)
        chat.save()
        chat.users.add(receiver, sender)
        chat.save()
    else:
        chat = chat[0]
        
    if not chat.users.all():
        chat.users.add(receiver, sender)
        chat.save()
        
    return JsonResponse(data=serializers.ChatSerializer(chat).data)


class ChatViewSet(ModelViewSet):    
    serializer_class = serializers.ChatSerializer

    # posts = ""
    # if "name" in request.GET :
    #     posts = Schedule.objects.filter(name = request.GET["name"])
    # else:
    def list(self, request):
        queryset = models.Chat.objects.all()
        print("== queryset = ", queryset)
        serializer = serializers.ChatSerializer(queryset, many=True)

        return Response(serializer.data)

    # def list(self, request):
    #     queryset = models.Chat.objects.all()
    #     serializer = serializers.ChatSerializer(queryset, many=True)
    #     return Response(serializer.data)
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

        # page = self.paginate_queryset(queryset)
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