from django.urls import path
from django.conf.urls import include
from django.conf.urls import url
from rest_framework import routers
from rest_framework.urlpatterns import format_suffix_patterns
from .views import LeadsViewSet, LeadsFieldsMetaViewSet, LeadsBrowseLayoutMetaViewSet, LeadsAddEditLayoutMetaViewSet

router = routers.DefaultRouter()

router.register('leadsfields', LeadsFieldsMetaViewSet)
router.register('leadsbrowselayout', LeadsBrowseLayoutMetaViewSet)
router.register('leadsaddeditlayout', LeadsAddEditLayoutMetaViewSet)
router.register('', LeadsViewSet)

urlpatterns = [
    path('', include(router.urls)),
]