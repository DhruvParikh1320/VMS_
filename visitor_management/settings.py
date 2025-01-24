"""
Django settings for visitor_management project.

Generated by 'django-admin startproject' using Django 5.0.7.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

from pathlib import Path
import os
from django.db import connection
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-p=j6kg6h*i2edfa6r(dnhvoa%@yf+ecm9j!p8p1@1y2*+-s-(v'

DOMAIN_URL ='https://192.168.1.137:7000/'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['192.168.1.137','*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'visitors_app',
    'gate_keeper_app',
    'employee_app',
    'admin_app',
    'api',
    'corsheaders',
    'rest_framework',
    'django_extensions',
]

MIDDLEWARE = [ 
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware'
]

ROOT_URLCONF = 'visitor_management.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'visitors_app.context_processors.my_constants',
            ],
        },
    },
]

WSGI_APPLICATION = 'visitor_management.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'vms_tanzania',
        'USER': 'root',
        'PASSWORD': 'root@123',
        'HOST':'localhost',
        'PORT':'3306',
    }
}

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Kolkata'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/'
# MEDIA_URL = ''
STATICFILES_DIRS = [BASE_DIR / "static"]

MEDIA_URL = '/'

MEDIA_ROOT = BASE_DIR
# MEDIA_ROOT = BASE_DIR
# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


ADMIN_STATIC_PATH = f'{DOMAIN_URL}/visitor_management/static/'

DOMAIN_NAME = 'VMS'

# DOMAIN_ICON = '/image/VMS.ico'/

# GET_PASS_IMAGE= '/image/logo.png'

# GET_PASS_IMAGE= '/image/Hexagon-infosoft.jpg'

BACKGROUND_IMAGE = '/image/bg-photo.jpg'

DATABASE_NAME = DATABASES['default']['NAME']

CORS_ORIGIN_ALLOW_ALL = True

CORS_ALLOWED_ORIGINS =['https://192.168.1.137:7000']

REST_FRAMEWORK = {
'DEFAULT_RENDERER_CLASSES': ('rest_framework.renderers.JSONRenderer',),

}

# DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_PORT =587
# EMAIL_HOST_USER='app.hexagon@gmail.com'
# EMAIL_HOST_PASSWORD='plrr qnyl gsdb gcjl'
# EMAIL_USE_TLS=True


DATABASE_TABLE = 'website_setting'
sql_query = f"SELECT * FROM {DATABASE_TABLE}"
with connection.cursor() as cursor:
    cursor.execute(sql_query)
    # Fetch all rows and column names
    database_all_data = cursor.fetchall()
    columns = [col[0] for col in cursor.description]

    # Create a list of dictionaries for each row
    all_coupon_dtl = [dict(zip(columns, row)) for row in database_all_data]

# def get_first_field_value(data_list, field, folder):
#     paths = [item[field] for item in data_list if field in item]
#     return f"{folder}/{paths[0]}" if paths else None


# Get the first 'image' and 'favicon' values, if they exist
# GET_PASS_IMAGE = get_first_field_value(all_coupon_dtl, 'image', 'website_setting/logo')
# DOMAIN_ICON = get_first_field_value(all_coupon_dtl, 'favicon', 'website_setting/favicon')

# image_paths = [user['image'] for user in all_coupon_dtl if 'image' in user]
# if image_paths:
#     GET_PASS_IMAGE = f"website_setting/logo/{image_paths[0]}"
# else:
#     GET_PASS_IMAGE = None

passwords = [user['smtp_password'] for user in all_coupon_dtl if 'smtp_password' in user]
host = [item['smtp_host'] for item in all_coupon_dtl if 'smtp_host' in item]
smtp_user = [item['smtp_user'] for item in all_coupon_dtl if 'smtp_user' in item]
from_names = [item['from_name'] for item in all_coupon_dtl if 'from_name' in item]
from_emails = [item['from_email'] for item in all_coupon_dtl if 'from_email' in item]



if host:
    smtp_host = host[0]
else:
    smtp_host = None

if smtp_user:
    smtp_user_name = smtp_user[0]
else:
    smtp_user_name = None

if passwords:
    smtp_password = passwords[0]
else:
    smtp_password = None
    
if from_names:
    from_name = from_names[0]
else:
    from_name = None

if from_emails:
    
    from_email = from_emails[0]
else:
    from_email = None


# domain_icon = [user['favicon'] for user in all_coupon_dtl if 'favicon' in user]

# DOMAIN_ICON = '/image/VMS.ico'/
# GET_PASS_IMAGE= '/image/Hexagon-infosoft.jpg'







DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = smtp_host
EMAIL_PORT =587
# EMAIL_HOST_USER='visit@easyvisit.in'
EMAIL_HOST_USER = smtp_user_name

# EMAIL_HOST_PASSWORD='Indian@1234'

EMAIL_HOST_PASSWORD= smtp_password
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL = f'{from_names} <{from_email}>'

# From_Email = 'app.hexagon@gmail.com'
From_Email = f'{from_names} <{from_email}>'
