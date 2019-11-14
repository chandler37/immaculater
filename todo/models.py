# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models


class ToDoList(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    contents = models.BinaryField()
    encrypted_contents = models.BinaryField(null=True)
    encrypted_contents2 = models.TextField(editable=False, null=True, blank=True)
    created_at = models.DateTimeField('date created', auto_now_add=True)
    updated_at = models.DateTimeField('date updated', auto_now=True)


class Share(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    slug = models.CharField(
      max_length=11, null=False, blank=False, unique=True, primary_key=True)
    created_at = models.DateTimeField('date created', auto_now_add=True)
    updated_at = models.DateTimeField('date updated', auto_now=True)


class JwtSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    slug = models.CharField(
      max_length=11, null=False, blank=False, unique=True, primary_key=True)
    created_at = models.DateTimeField('date created', auto_now_add=True)
    updated_at = models.DateTimeField('date updated', auto_now=True)
    expires_at = models.DateTimeField('date created', null=False, blank=False)
