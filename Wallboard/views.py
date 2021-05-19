from django.shortcuts import render
from django.http import HttpResponse
from .serializers import LeadsSerializer, LeadsFieldsSerializer, LeadsBrowseLayoutSerializer, LeadsAddEditLayoutSerializer
from .models import leads, leads_fields, leads_browse_layout, leads_addedit_layout
from rest_framework.generics import get_object_or_404
from rest_framework import viewsets
from rest_framework import filters, status, generics
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework_filters.backends import RestFrameworkFilterBackend
# import rest_framework_filters as filters
from rest_framework.views import APIView
from .filters import CustomFilterSet
import json
import zcrmsdk
import pymysql

db = pymysql.connect("localhost","admin1","UbMF&eFVQ%MTw*hs","trialetics")


