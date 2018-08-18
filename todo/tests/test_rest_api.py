# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import pytest
from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User
from jwt_auth import settings


# Maybe put the token generation in conftest.py or some other shared fixture
# place?
jwt_payload_handler = settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = settings.JWT_ENCODE_HANDLER


@pytest.mark.django_db
class V1Projects(TestCase):
    def setUp(self):
        self.email = 'foo@example.com'
        self.username = 'foo'
        self.password = 'password'
        self.user = User.objects.create_user(
            self.username, self.email, self.password)
        self.client = Client()

        payload = jwt_payload_handler(self.user)
        self.token = jwt_encode_handler(payload)
        self.auth_headers = {
            'HTTP_AUTHORIZATION': 'Bearer ' + self.token
        }

    def test_get(self):
        response = self.client.get(
            '/todo/v1/projects', **self.auth_headers
        )

        response_content = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response_content.keys()), ['result'])
        self.assertEqual(response_content['result'][0]['name'], 'inbox')
