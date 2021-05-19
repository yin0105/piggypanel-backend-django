from django.http import HttpResponse
from django.shortcuts import render
import json
import requests
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response

class CustomObtainAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        response = super(CustomObtainAuthToken, self).post(request, *args, **kwargs)
        token = Token.objects.get(key=response.data['token'])
        group = token.user.groups.values_list('name',flat = True) # QuerySet Object
        return Response({'key': token.key, 'id': token.user_id, 'group':group, 'authName':token.user.first_name+' '+token.user.last_name,'is_active':token.user.is_active, 'is_superuser':token.user.is_superuser,'last_login':token.user.last_login})