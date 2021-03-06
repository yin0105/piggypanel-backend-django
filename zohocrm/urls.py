"""zohocrm URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include, re_path
from django.conf.urls.static import static
from django.conf.urls import url
from django.conf import settings
from .views import CustomObtainAuthToken
from allauth.account.views import ConfirmEmailView,PasswordResetView
from rest_auth.registration.views import VerifyEmailView
from rest_framework import routers
import superadmin
import admin

from chat import views

router = routers.SimpleRouter()
router.register(r'chats', views.ChatViewSet, basename='Chat')
router.register(r'users', views.UserViewSet, basename='User')

urlpatterns = [
    path('admin/', admin.site.urls),    
    path('superadmin/', superadmin.site.urls),
    url(r'^rest-auth/', include('rest_auth.urls')),
    url(r'^rest-auth/authenticate/$', CustomObtainAuthToken.as_view()),
    path('api/leads/', include('leads.urls')),
    path('api/contacts/', include('contacts.urls')),
    path('create-chat/', views.createChat, name='create'),
    path('get-messages/', views.getMessages, name='get_messages'),
    path('unread/', views.getUnread, name='get_unread'),
    path('remove_msg/', views.removeMsg, name='removeMsg'),
    path('', views.IndexView.as_view(), name='home'),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + router.urls

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)