"""
Django settings for AdrileBoutique project.

Generated by 'django-admin startproject' using Django 4.2.5.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from pathlib import Path
from datetime import timedelta
import os
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-et=ei4^s@2h3w(zdem(m!b3f-415&ec9l7spd8fsrq&^+*i&g)'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # custom
    'appTiendaInventario',
    'corsheaders',
    'rest_framework',
    'rest_framework_jwt',
    'rest_framework.authtoken',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'AdrileBoutique.urls'

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
            ],
        },
    },
]

WSGI_APPLICATION = 'AdrileBoutique.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES_SQlite = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'inventario',
            'USER': 'root',
            'PASSWORD': '',
            'HOST': 'localhost',
            'PORT': '3306',
        }
    }


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'es-CO'

TIME_ZONE = 'America/Bogota'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR,'static')

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Para guardar archivos de multimedia. 

MEDIA_URL = '/media/'
MEDIA_ROOT= os.path.join(BASE_DIR,'media')


# Tiempo de sesión en segundos (desactivado para qu e funcione en el login)
# SESSION_COOKIE_AGE = 4 * 60 * 60 # 4 horas


# 
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES':(
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
       'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
    ),
}


# permitir solicitudes solo desde un origen específico
# permitir todas las solicitudes de origen cruzado
CORS_ORIGIN_ALLOW_ALL = True

CORS_ALLOWED_ORIGINS = [
    "http://*",
    "https://*",
]

# Configuración para enviar correos utilizando SMTP (Simple Mail Transfer Protocol)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
load_dotenv()

EMAIL_HOST = 'smtp.gmail.com'  # Ejemplo para Gmail
EMAIL_PORT = 587  # Puerto para Gmail
EMAIL_USE_TLS = True  # Usar TLS (True para Gmail)
EMAIL_USE_SSL = False  # No usar SSL (False para Gmail)
EMAIL_HOST_USER = os.getenv('EMAIL_SENDER')  # Dirección de correo
EMAIL_HOST_PASSWORD = os.getenv('PASSWORD_SENDER')  # Contraseña de correo

# # Opcional: Configuración para manejar correos en el entorno de desarrollo
# if DEBUG:
#     EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # Muestra los correos en la consola en lugar de enviarlos

# ruta a la cual sera redirigido cuando termine su sesion
LOGOUT_REDIRECT_URL = '/'

# Redireccion a la pagina de inicio.
LOGIN_REDIRECT_URL = '/dashboard/'

# ruta la cual sera redirigido cuando caduque la sesion
LOGIN_URL = '/dashboard/'

# AUTH_USER_MODEL = 'auth.User'

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    # ...
]
