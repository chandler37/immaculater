"""
Django settings for immaculater project on Heroku. For more info, see:
https://github.com/heroku/heroku-django-template

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""

import datetime
import os
import dj_database_url
import sentry_sdk

from sentry_sdk.integrations.django import DjangoIntegration

from django.urls import reverse_lazy

from immaculater import jwt


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/ TODO(chandler)

# SECURITY WARNING: keep the secret key used in production secret!
# Create a line DJANGO_SECRET_KEY=mysecretkey in your ../.env file for 'heroku local web' to see this. Use 'heroku config:set DJANGO_SECRET_KEY=secretkey' to affect it in production.
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY',
                            "9!41(_jh5evq2br6^&w6rx+-8g((c-a!p%1s9uk_usu8nq&&a7")

# SECURITY WARNING: don't run with debug turned on in production!
# Using 'heroku local web'? Create a file ../.env with a line 'DJANGO_DEBUG="True"'.
DEBUG = os.environ.get('DJANGO_DEBUG') == "True"

# Application definition

INSTALLED_APPS = [
    'todo.apps.TodoConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.sites',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    # Disable Django's own staticfiles handling in favour of WhiteNoise, for
    # greater consistency between gunicorn and `./manage.py runserver`. See:
    # http://whitenoise.evans.io/en/stable/django.html#using-whitenoise-in-development
    'whitenoise.runserver_nostatic',
    'django.contrib.staticfiles',
    'django_slack_oauth',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
]
USE_ALLAUTH = os.environ.get("USE_ALLAUTH", "False") == "True"
if USE_ALLAUTH:
    INSTALLED_APPS += [
        # TODO(chandler37): remove the old slack auth? Update the slash command
        # to use the allauth socialaccount models to authenticate?
        'allauth.socialaccount.providers.amazon',
        'allauth.socialaccount.providers.discord',
        'allauth.socialaccount.providers.facebook',
        'allauth.socialaccount.providers.google',
        'allauth.socialaccount.providers.slack',
    ]

SITE_ID = 1

MIDDLEWARE = [
    'todo.middleware.exception_middleware.ExceptionMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'immaculater.urls'

AUTHENTICATION_BACKENDS = (
    # Needed to login by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',
)
if USE_ALLAUTH:
    AUTHENTICATION_BACKENDS += (
        # `allauth` specific authentication methods, such as login by e-mail
        'allauth.account.auth_backends.AuthenticationBackend',
    )

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'todo.context_processors.basics',
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'debug': DEBUG,
        },
    },
]

WSGI_APPLICATION = 'immaculater.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

# TODO(chandler37): Test that ATOMIC_REQUESTS is working.
#
# If you don't think you need transactions, run multiple django servers against the same database and run many clients
# in parallel all trying to add actions with unique Action.Common.Metadata.Name fields. Record which ones the django
# app said succeeded and then stop writing and read and make sure all the actions you added are there. Without txns,
# you'll see that some updates make it to the database but are then overwritten.
#
# TODO(chandler37): We further need row locking like select_for_update provides. Atomicity may not be sufficient if we
# read v1, someone else writes v2, and we write a delta of v1 as v3, removing the delta from v1 to v2.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        'ATOMIC_REQUESTS': True,
    }
}

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
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Update database configuration with $DATABASE_URL.
db_from_env = dj_database_url.config(conn_max_age=500)
DATABASES['default'].update(db_from_env)

# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = True
X_FRAME_OPTIONS = "DENY"

# Allow all host headers
ALLOWED_HOSTS = ['*']

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

STATIC_ROOT = os.path.join(PROJECT_ROOT, 'staticfiles')
STATIC_URL = '/static/'

# Extra places for collectstatic to find static files.
STATICFILES_DIRS = [
    os.path.join(PROJECT_ROOT, 'static'),
]

# Simplified static file serving.
# https://warehouse.python.org/project/whitenoise/
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

LOGOUT_REDIRECT_URL = '/todo'

SLACK_CLIENT_ID = os.environ.get('SLACK_CLIENT_ID')
SLACK_CLIENT_SECRET = os.environ.get('SLACK_CLIENT_SECRET')
SLACK_SCOPE = 'identify'
SLACK_SUCCESS_REDIRECT_URL = reverse_lazy('home')
SLACK_PIPELINES = [
    # 'todo.pipelines.debug_oauth_request',
    'todo.pipelines.register_user',
]

if USE_ALLAUTH:
    LOGIN_REDIRECT_URL = '/todo/'
else:
    LOGIN_URL = '/todo/login'


if os.environ.get('MEMCACHEDCLOUD_SERVERS'):
    CACHES = {
        'default': {
            'BACKEND': 'django_bmemcached.memcached.BMemcached',
            'LOCATION': os.environ.get('MEMCACHEDCLOUD_SERVERS').split(','),
            'OPTIONS': {
                'username': os.environ.get('MEMCACHEDCLOUD_USERNAME'),
                'password': os.environ.get('MEMCACHEDCLOUD_PASSWORD')
            }
        }
    }
else:
    if not DEBUG and SLACK_CLIENT_ID is not None:
        raise Exception('You must use memcached/redis or the Slack OAuth integration will break (deny sign ups/sign ins) because its state machine uses the django cache.')

if DEBUG:
    LOGGING = {
        'version': 1,
        'handlers': {
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
            },
        },
        'loggers': {
            'django.request': {
                'handlers': ['console'],
                'propagate': True,
                'level': 'DEBUG',
            }
        },
    }

if os.environ.get('SENDGRID_API_KEY'):
    EMAIL_BACKEND = 'sendgrid_backend.SendgridBackend'
    ACCOUNT_EMAIL_VERIFICATION = "optional"
    SENDGRID_API_KEY = os.environ['SENDGRID_API_KEY']
    SENDGRID_SANDBOX_MODE_IN_DEBUG = True
else:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
    ACCOUNT_EMAIL_VERIFICATION = 'none'  # hence our EMAIL_BACKEND is fine.
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@localhost')

JWT_PAYLOAD_HANDLER = jwt.jwt_payload_handler

JWT_EXPIRATION_DELTA = datetime.timedelta(seconds=60 * 60 * 24)

if os.environ.get("SENTRY_DSN"):
  sentry_sdk.init(
      dsn=os.environ.get("SENTRY_DSN"),
      integrations=[DjangoIntegration()]
  )
