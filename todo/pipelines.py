# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

from django.contrib.auth.models import User
from django.contrib.auth import login

from django_slack_oauth.models import SlackUser


def debug_oauth_request(request, api_data):
    print(api_data)
    return request, api_data


def register_user(request, api_data):
    if api_data['ok']:
        user, _ = User.objects.get_or_create(
            # TODO(chandler): Share this code with views.py:
            username=api_data['team_id'] + ':' + api_data['user_id']
        )
        if user.is_active:
            slacker, _ = SlackUser.objects.get_or_create(slacker=user)
            slacker.access_token = api_data.pop('access_token')
            slacker.extras = api_data
            slacker.save()
            login(request, user)
    return request, api_data
