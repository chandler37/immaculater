# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

from . import views

def basics(request):
    return {
        "Brand": views._brand(),
        "BrandURL": views._brand_url(),
        "Logo": views._logo(),
        "SupportEmail": views._support_email(),
        "Favicon": views._favicon_relative_path(),
        }
