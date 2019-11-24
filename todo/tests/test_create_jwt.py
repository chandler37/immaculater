# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import base64
import freezegun
import json
import pytest
import re
from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User
from jwt_auth import settings
from pyatdllib.ui import immaculater
from todo import models


# Maybe put the token generation in conftest.py or some other shared fixture
# place?
jwt_payload_handler = settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = settings.JWT_ENCODE_HANDLER
jwt_decode_handler = settings.JWT_DECODE_HANDLER


@pytest.mark.django_db
class CreateJwt(TestCase):
  def setUp(self):
    self.email = 'foo@example.com'
    self.username = 'fooabcdefghijklmnopqrstuvwxyz'
    self.password = 'password013245467789ABDCKJLSDFUIEWTYGHPHQA'
    self.user = User.objects.create_user(
      self.username, self.email, self.password)
    self.client = Client()
    b64 = base64.b64encode(bytes(f'{self.username}:{self.password}', 'utf-8'))
    bad_b64 = base64.b64encode(bytes(f'{self.username}:cat_videos', 'utf-8'))
    bad_username_b64 = base64.b64encode(bytes(f'{self.username+"a"}:{self.password}', 'utf-8'))
    assert len(b64) == 96
    self.auth_headers = {
      'HTTP_AUTHORIZATION': f'Basic {b64.decode("utf-8")}'
    }
    self.bad_password_auth_headers = {
      'HTTP_AUTHORIZATION': f'Basic {bad_b64.decode("utf-8")}'
    }
    self.bad_username_auth_headers = {
      'HTTP_AUTHORIZATION': f'Basic {bad_username_b64.decode("utf-8")}'
    }

  @freezegun.freeze_time("1988-02-14")
  def test_happy_path_post(self):
    slug = 'rLMA1Nj1XLo'
    saved = immaculater.Base64RandomSlug
    immaculater.Base64RandomSlug = lambda unused_bits: slug
    try:
      response = self.client.post(
        '/todo/v1/create_jwt', **self.auth_headers
      )
      response_content = json.loads(response.content)
      self.assertEqual(response.status_code, 201)
      self.assertEqual(list(response_content.keys()), ['token'])
      assert re.match(
        r'^eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9\.[^.]+\.[^.]+$',
        response_content['token'])
      assert jwt_decode_handler(response_content['token']) == {'slug': slug, 'expiry': '571881600'}
      response_content = json.loads(response.content)

      # Now see if the database has it...
      objs = models.JwtSession.objects.filter(pk=slug)
      assert len(objs) == 1
      assert objs[0].user_id == self.user.id
    finally:
      immaculater.Base64RandomSlug = saved

  @freezegun.freeze_time("1988-02-14")
  def test_403_bad_password(self):
    response = self.client.post(
      '/todo/v1/create_jwt', **self.bad_password_auth_headers
    )
    self.assertEqual(response.status_code, 403)
    assert response.content == b'<h1>403 Forbidden</h1>\n\n  <p>The properly formatted &quot;Authorization&quot; header has an invalid username or password.</p>\n\n'

  @freezegun.freeze_time("1988-02-14")
  def test_403_bad_username(self):
    response = self.client.post(
      '/todo/v1/create_jwt', **self.bad_username_auth_headers
    )
    self.assertEqual(response.status_code, 403)
    assert response.content == b'<h1>403 Forbidden</h1>\n\n  <p>The properly formatted &quot;Authorization&quot; header has an invalid username or password.</p>\n\n'

  @freezegun.freeze_time("1988-02-14")
  def test_403_inactive_user(self):
    did_it = False
    for model in User.objects.filter(pk=self.user.pk):
      model.is_active = False
      model.save()
      did_it = True
    assert did_it
    response = self.client.post(
      '/todo/v1/create_jwt', **self.auth_headers
    )
    self.assertEqual(response.status_code, 403)
    assert response.content == b'<h1>403 Forbidden</h1>\n\n  <p>The properly formatted &quot;Authorization&quot; header has an invalid username or password.</p>\n\n'
