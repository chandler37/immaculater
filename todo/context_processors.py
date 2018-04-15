# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os


def _favicon_relative_path():
  return os.environ.get('IMMMACULATER_FAVICON', 'favicon.ico')


def _create_logout_url():
  return '/accounts/logout/?next=/todo'


def _support_email():
  return os.environ.get('IMMACULATER_SUPPORT_EMAIL', '???')


def _brand():
  return os.environ.get('IMMACULATER_BRAND', 'My To-Do List')


def _brand_url():
  return os.environ.get(
    'IMMACULATER_BRAND_URL',
    'please set the IMMACULATER_BRAND_URL environment variable')


def _logo():
  # Add your_logo.png to ../immaculater/static.
  return os.environ.get('BRAND_STATIC_FILE_LOGO_PATH', 'your_logo.png')


def basics(request):
  return {
    "Brand": _brand(),
    "BrandURL": _brand_url(),
    "Logo": _logo(),
    "SupportEmail": _support_email(),
    "Favicon": _favicon_relative_path(),
    "LogoutUrl": _create_logout_url(),
  }
