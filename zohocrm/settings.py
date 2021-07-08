"""
Django settings for zohocrm project.

Generated by 'django-admin startproject' using Django 3.1.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""
import os
import re
import zcrmsdk
from django.urls import reverse_lazy
from pathlib import Path
from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve(strict=True).parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='9iygl=yw9++%73g(j-_x8@dru&dmxh5h0k+$(q+jo&0rol*f+c')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)

# ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=lambda v: [s.strip() for s in v.split(',')])
ALLOWED_HOSTS = ['*']



# Application definition

INSTALLED_APPS = [
    'admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'corsheaders',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'rest_framework',
    'rest_auth',
    'rest_auth.registration',
    'rest_framework.authtoken',
    'django_filters',
    'rest_framework_filters',
    'django_crontab',
    'user',
    'leads',
    'contacts',
    'zoho',
    'reversion',
    'zcrmsdk',
    'Wallboard',
    'menu',

    'channels',
    'chat',
    'zohocrm',
    'superadmin',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
        # 'rest_framework_datatables.renderers.DatatablesRenderer',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'rest_framework_filters.backends.RestFrameworkFilterBackend',
        #'rest_framework_datatables.filters.DatatablesFilterBackend',
        # 'django_filters.rest_framework.DjangoFilterBackend',
    ),
    'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.coreapi.AutoSchema',
    #'DEFAULT_PAGINATION_CLASS': 'rest_framework_datatables.pagination.DatatablesPageNumberPagination',
    'DEFAULT_PAGINATION_CLASS': 'zohocrm.pagination.CustomPagination',
    'PAGE_SIZE': 10,
}

CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_ALLOW_ALL = True

# CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', cast=lambda v: [s.strip() for s in v.split(',')])
# CORS_ALLOWED_ORIGINS = [
#     "https://example.com",
#     "https://sub.example.com",
#     "http://localhost:4000",
#     "http://127.0.0.1:9000",
#     "https://demo.piggypanel.com",
# ]

ROOT_URLCONF = 'zohocrm.urls'
AUTH_USER_MODEL = 'user.User'

AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
)

SITE_ID = 1

ACCOUNT_EMAIL_REQUIRED = False
ACCOUNT_USERNAME_REQUIRED = True
# ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_AUTHENTICATION_METHOD = "username_email"
ACCOUNT_CONFIRM_EMAIL_ON_GET = True
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = False
ACCOUNT_EMAIL_CONFIRMATION_ANONYMOUS_REDIRECT_URL = reverse_lazy('account_confirmed')

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, "templates"), os.path.join(BASE_DIR, "zohocrm/templates")],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


WSGI_APPLICATION = 'zohocrm.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': config('DB_NAME', default='zohocrm'),
        'USER': config('DB_USER', default='postgres'),
        'PASSWORD': config('DB_PASS', default='postgres'),
        # 'PASSWORD': config('DB_PASS', default='dipankar'),
        'HOST': config('HOST', default='localhost'),
        'PORT': '5432',
    }
}

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql_psycopg2',
#         'NAME': 'zohocrm',
#         'USER':'postgres' ,
#         'PASSWORD': 'postgres',
#         'HOST': 'localhost',
#         'PORT': '5432',
#     }
# }

# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Europe/London'

USE_I18N = True

USE_L10N = True

USE_TZ = True

configuration_dictionary = {
    'apiBaseUrl': 'https://www.zohoapis.eu',
    'apiVersion': 'v2',
    'currentUserEmail': config('ZOHO_CURRENT_USER_EMAIL',default='info@bvm.legal'),
    'sandbox': 'False',
    'applicationLogFilePath': os.path.join(BASE_DIR, "Log"),
    'client_id': config('ZOHO_CLIENT_ID',default='1000.76FKQGMEUQQZWQ13B40XKWQ6PK6I2E'),
    'client_secret': config('ZOHO_CLIENT_SECRET',default='5b86037185d63faff832e73a10412bab23303e4999'),
    'redirect_uri': config('ZOHO_REDIRECT_URI',default='http://localhost:7000/'),
    'accounts_url': 'https://accounts.zoho.eu',
    'access_type': 'offline',
    'persistence_handler_class': 'ZohoOAuthHandler',
    'persistence_handler_path': 'zoho.models',
}
zcrmsdk.ZCRMRestClient.initialize(configuration_dictionary)

ZCRM_LEADS_FIELD_MAP_ALLOCATED_TO_API_NAME =  config('ZCRM_LEADS_FIELD_MAP_ALLOCATED_TO_API_NAME', default='allocated_to')
ZCRM_CONTACTS_FIELD_MAP_ALLOCATED_TO_API_NAME =  config('ZCRM_CONTACTS_FIELD_MAP_ALLOCATED_TO_API_NAME', default='allocated_to')
ZCRM_LEADS_FIELD_MAP_PANEL_UPDATE_DATE_TO_API_NAME =  config('ZCRM_LEADS_FIELD_MAP_PANEL_UPDATE_DATE_TO_API_NAME', default='Last_Updated')
ZCRM_CONTACTS_FIELD_MAP_PANEL_UPDATE_DATE_TO_API_NAME =  config('ZCRM_CONTACTS_FIELD_MAP_PANEL_UPDATE_DATE_TO_API_NAME', default='Last_Updated')

CRONTAB_LOCK_JOBS = True
# CRONJOBS = config('CRONJOBS', cast=lambda v: [s.strip() for s in v.replace('),', ')//').split('//')])

CRONTAB_DJANGO_PROJECT_NAME = config('CRONTAB_DJANGO_PROJECT_NAME')

CRONJOBS = [
    ('*/5 * * * *', 'leads.cron.leads_incremental_sync','>> ' + config('CRONJOBS_LOG_DIR') + 'leads_scheduled_job.log 2>&1'),
    ('*/5 * * * *', 'leads.cron.leads_delete_sync','>> ' + config('CRONJOBS_LOG_DIR') + 'leads_scheduled_job_delete.log 2>&1'),
    ('*/5 * * * *', 'contacts.cron.contacts_incremental_sync','>> ' + config('CRONJOBS_LOG_DIR') + 'contacts_scheduled_job.log 2>&1'),
    ('*/5 * * * *', 'contacts.cron.contacts_delete_sync','>> ' + config('CRONJOBS_LOG_DIR') + 'contacts_scheduled_job_delete.log 2>&1'),
    ('*/5 * * * *', 'Wallboard.cron.extensions_sync','>> ' + config('CRONJOBS_LOG_DIR') + 'wallboard_extensions_sync.log 2>&1'),
    ('3-58/5 * * * *', 'Wallboard.cron.call_status','>> ' + config('CRONJOBS_LOG_DIR') + 'wallboard_call_status.log 2>&1')      
]


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_URL = '/static/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

#################
# CORS_ALLOWED_ORIGINS = ["http://localhost:4000", "https://demo.piggypanel.com", "https://aegis.piggypanel.com", "https://chilli.piggypanel.com", "https://tcn.piggypanel.com", "https://viking.piggypanel.com"]
CHANNEL_LAYERS = {
    "default": {
        # This example app uses the Redis channel layer implementation channels_redis
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [('localhost', 6379)],
            # "hosts": [('my-redis-1-001.di0a43.0001.sae1.cache.amazonaws.com', 6379)],
        },
    },
}

ASGI_APPLICATION = 'zohocrm.asgi.application'

# TEMPLATE_CONTEXT_PROCESSORS = ['django.core.context_processors.request', ]

TEMPLATE_CONTEXT_PROCESSORS = [
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.request",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
]