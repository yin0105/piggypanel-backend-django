from copy import deepcopy
from django.db import models
import django_filters
import rest_framework_filters as filters
from django_filters import filterset
from django_filters.rest_framework import DjangoFilterBackend
from django_filters.rest_framework.filters import CharFilter
from .models import contacts
from django.contrib.postgres.fields import JSONField

class CustomFilterSet(filters.FilterSet):
    FILTER_DEFAULTS = deepcopy(filterset.FILTER_FOR_DBFIELD_DEFAULTS)
    FILTER_DEFAULTS.update({
        JSONField: {
            'filter_class': CharFilter,
            'extra': lambda f: {'lookup_expr': ['icontains']},
        },
    })

    def filter_queryset(self, queryset):
        # print(self.request.query_params)
        for param in self.request.query_params:
            if param.find('data__') != -1:
                val = self.request.query_params[param]
                queryset = queryset.filter(**{param:val})

        if('allocated_to' in self.request.query_params):
            queryset = queryset.filter(allocated_to=self.request.query_params['allocated_to'])
        if('zoho_ref' in self.request.query_params):
            queryset = queryset.filter(zoho_ref=self.request.query_params['zoho_ref'])

        for param in self.request.query_params:
            if param.find('ordering') != -1:
                val = self.request.query_params[param]
                queryset = queryset.order_by(val)

        return queryset

    class Meta:
        model = contacts
        fields = {
                    'zoho_ref':['exact','icontains'],   
                    'allocated_to':['exact'],
                    'data':['icontains'] 
                }
        filter_overrides = {
            models.JSONField: {
                'filter_class': CharFilter,
                'extra': lambda f: {
                    'lookup_expr': 'icontains',
                },
            },
        }

# class CustomDjangoFilterBackend(DjangoFilterBackend):
#     default_filter_set = CustomFilterSet


# class ContactsFilterSet(filters.FilterSet):
#     class Meta:
#         model = contacts
#         fields = ['zoho_ref','data']
#         filter_overrides = {
#             models.JSONField: {
#                 'filter_class': CharFilter,
#                 'extra': lambda f: {
#                     'lookup_expr': 'icontains',
#                 },
#             },
#         }

    # FILTER_DEFAULTS= deepcopy(filterset.FILTER_FOR_DBFIELD_DEFAULTS)
    # FILTER_DEFAULTS.update({
    #     models.JSONField: {
    #         'filter_class': filters.CharFilter,
    #         'extra': lambda f: {'lookup_expr': 'icontains'},
    #     },
    # })

    # class Meta:
    #     model = contacts
    #     fields = ['data']
    #     filter_overrides = {
    #         models.CharField: {
    #             'filter_class': django_filters.CharFilter,
    #             'extra': lambda f: {
    #                 'lookup_expr': 'icontains',
    #             },
    #         },
    #     }
        
# class ContactsFilterSet(filters.FilterSet):
#     FILTER_DEFAULTS = deepcopy(filterset.FILTER_FOR_DBFIELD_DEFAULTS)
#     FILTER_DEFAULTS.update({
#         contacts: {
#             'filter_class': CharFilter,
#             'extra': lambda f: {'lookup_expr': ['icontains']},
#         },
#     })

# class CustomContactsFilterBackend(DjangoFilterBackend):
#     default_filter_set = ContactsFilterSet