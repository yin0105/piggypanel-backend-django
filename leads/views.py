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

class LeadsViewSet(viewsets.ModelViewSet):
    queryset = leads.objects.all()
    serializer_class = LeadsSerializer
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated,)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, RestFrameworkFilterBackend]
    # filter_backends = [DjangoFilterBackend]
    # filter_class = CustomLeadsFilterBackend
    # filter_backends = [CustomDjangoFilterBackend]
    filterset_class = CustomFilterSet
    filterset_fields = ['id','allocated_to','zoho_ref','data']
    search_fields = ['data']

    @action(detail=False, methods=['delete'], url_path='delete-leads')
    def delete_multiple(self, request):
        body_unicode = request.body.decode('utf-8')
        leads_data = json.loads(body_unicode)
        zoho_list = leads.objects.filter(id__in=leads_data).values_list('zoho_ref',flat=True)
        try:
            # entityid_list = [347706100000031, 3477061000000311] # record id
            resp = zcrmsdk.ZCRMModule.get_instance('Leads').delete_records(zoho_list) #To call the delete record method
            # print(resp.status_code)
            # entity_responses = resp.bulk_entity_response
            # for entity_response in entity_responses:
            #     print(entity_response.details)
            #     print(entity_response.status)
            #     print(entity_response.message)
            #     print(entity_response.code)
            #     print(entity_response.data.entity_id)
            #     print("\n\n")
            records = leads.objects.filter(id__in=leads_data).delete()
            return Response(records)
        except zcrmsdk.ZCRMException as ex:
            print(ex.status_code)  
            print(ex.error_message) 
            print(ex.error_code) 
            print(ex.error_details) 
            print(ex.error_content) 


class LeadsFieldsMetaViewSet(viewsets.ModelViewSet):    
    queryset = leads_fields.objects.all()
    serializer_class = LeadsFieldsSerializer
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated,)
    filter_backends = [filters.SearchFilter, RestFrameworkFilterBackend]
    filterset_fields = ['field_api_name','field_type']
    search_fields = ['field_api_name']

class LeadsBrowseLayoutMetaViewSet(viewsets.ModelViewSet):
    queryset = leads_browse_layout.objects.all()
    serializer_class = LeadsBrowseLayoutSerializer
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated,)
    filter_backends = [filters.SearchFilter, RestFrameworkFilterBackend, filters.OrderingFilter]
    ordering = ['layout_col']


class LeadsAddEditLayoutMetaViewSet(viewsets.ModelViewSet):
    queryset = leads_addedit_layout.objects.all()
    serializer_class = LeadsAddEditLayoutSerializer
    filter_backends = [filters.SearchFilter, RestFrameworkFilterBackend, filters.OrderingFilter]
    filterset_fields = ['layout_row']
    search_fields = ['layout_row']
    ordering = ['layout_row','layout_col']