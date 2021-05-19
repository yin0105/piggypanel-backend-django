from django.urls import path
from django.conf.urls import include
from django.conf.urls import url
from rest_framework import routers
from rest_framework.urlpatterns import format_suffix_patterns
from .views import ContactsViewSet, ContactsFieldsMetaViewSet, ContactsBrowseLayoutMetaViewSet, ContactsAddEditLayoutMetaViewSet

router = routers.DefaultRouter()

router.register('contactsfields', ContactsFieldsMetaViewSet)
router.register('contactsbrowselayout', ContactsBrowseLayoutMetaViewSet)
router.register('contactsaddeditlayout', ContactsAddEditLayoutMetaViewSet)
router.register('', ContactsViewSet)

urlpatterns = [
    path('', include(router.urls)),
]