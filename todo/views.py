# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import base64
import binascii
import codecs
import datetime
import hashlib
import json
import jwt as pyjwt
import io
import os
import pipes
import re
import six

import gflags as flags  # https://code.google.com/p/python-gflags/

from third_party.django_pjax import djpjax
from pyatdllib.ui import immaculater
from pyatdllib.ui import serialization
from pyatdllib.ui import uicmd
from pyatdllib.core import pyatdl_pb2
from pyatdllib.core import tdl
from pyatdllib.core import uid
from pyatdllib.core import view_filter
from pyatdllib.core.mergeprotobufs import Merge
from django.contrib.auth import authenticate
from django.contrib.auth import logout
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth import views
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.http import Http404
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.http import JsonResponse
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.encoding import escape_uri_path
from django.utils.html import escape
from django.views.decorators.cache import never_cache
from django.views.decorators.clickjacking import xframe_options_sameorigin
from django.views.decorators.csrf import csrf_exempt
from cryptography.fernet import Fernet, InvalidToken
from google.protobuf import message
from allauth.socialaccount import models as allauth_models
from jwt_auth import settings as jwt_auth_settings
from immaculater import jwt

from . import models

import sys
if not hasattr(sys.stdout, 'isatty'):
  # TODO(chandler): Add isatty to class Tee. gflags uses sys.stdout.isatty().
  sys.stdout.isatty = lambda: False

immaculater.RegisterUICmds(cloud_only=True)

FLAGS = flags.FLAGS
FLAGS.pyatdl_show_uid = True
FLAGS.database_filename = None
FLAGS.seed_upon_creation = True
FLAGS.no_context_display_string = 'Actions Without Context'

_COOKIE_NAME = 'VISITOR_INFO0'
_SANITY_CHECK = 37
MERGETODOLISTREQUEST_CONTENT_TYPE = 'application/x-protobuf; messageType="pyatdl.MergeToDoListRequest"'
MERGETODOLISTREQUEST_SANITY_CHECK = 18369614221190020847


# TODO(chandler37): Support redo/undo. Put the commands in the protobuf. Be aware of the mergeprotobufs API if you do
# this. But probably don't do this; do it on the client in such a way that you cannot undo the action done on another
# device.


def _encrypted_todolist_protobuf(some_bytes):
  return _protobuf_fernet().encrypt(some_bytes).decode('utf-8')


def _decrypted_todolist_protobuf(pb):
  """Args: pb: bytes; Returns the serialized bytes of a pyatdl_pb2.ChecksumAndData."""
  # We should never see InvalidToken. If we see it, let it become a 500.
  try:
    return _protobuf_fernet().decrypt(pb)
  except InvalidToken:
    _debug_log('Invalid encrypted pb')
    raise


class SerializationWriter(object):
  def __init__(self, mode, user, place_to_save_read):
    """Init.

    Regarding `mode`, 'write' is typical but 'write only if nothing is
    yet written' is useful for read-only commands, e.g. 'lsctx'.

    This avoids the race condition where we read, someone else writes, and we then
    overwrite stale data. TODO(chandler): Eliminate the race condition.

    Args:
      mode: 'write only if nothing is yet written' | 'write'
      user: models.User
      place_to_save_read: None|dict that will have 'saved_read' filled in with
                          the result of the write
    """
    if mode not in ('write', 'write only if nothing is yet written'):
      raise ValueError('bad mode')
    self._mode = mode
    self._user = user
    if place_to_save_read is None:
      self._place_to_save_read = {}
    else:
      self._place_to_save_read = place_to_save_read
      self._place_to_save_read['saved_read'] = None

  def write(self, b):
    user_id = self._user.id
    email = self._user.email
    assert user_id, 'FAILwhale email=%s' % (email,)
    x = models.ToDoList.objects.filter(user__id=user_id)
    encrypted_contents = _encrypted_todolist_protobuf(b)
    if len(x):
      if self._mode == 'write':
        x[0].encrypted_contents2 = encrypted_contents
        x[0].contents = b''
        x[0].save()
    else:
      new_model = models.ToDoList(user=self._user,
                                  contents=b'',
                                  encrypted_contents=None,
                                  encrypted_contents2=None)
      # HACK why can't we set encrypted_contents2 to encrypted_contents above?
      # If we do, we get a TypeError:
      # :   File "/app/todo/views.py", line 108, in write
      # :     new_model.save()
      # :   File "/app/.heroku/python/lib/python2.7/site-packages/django/db/models/base.py", line 806, in save
      # :     force_update=force_update, update_fields=update_fields)
      # :   File "/app/.heroku/python/lib/python2.7/site-packages/django/db/models/base.py", line 836, in save_base
      # :     updated = self._save_table(raw, cls, force_insert, force_update, using, update_fields)
      # :   File "/app/.heroku/python/lib/python2.7/site-packages/django/db/models/base.py", line 903, in _save_table
      # :     forced_update)
      # :   File "/app/.heroku/python/lib/python2.7/site-packages/django/db/models/base.py", line 953, in _do_update
      # :     return filtered._update(values) > 0
      # :   File "/app/.heroku/python/lib/python2.7/site-packages/django/db/models/query.py", line 662, in _update
      # :     return query.get_compiler(self.db).execute_sql(CURSOR)
      # :   File "/app/.heroku/python/lib/python2.7/site-packages/django/db/models/sql/compiler.py", line 1191, in execute_sql
      # :     cursor = super(SQLUpdateCompiler, self).execute_sql(result_type)
      # :   File "/app/.heroku/python/lib/python2.7/site-packages/django/db/models/sql/compiler.py", line 886, in execute_sql
      # :     raise original_exception
      # : TypeError: can't escape unicode to binary
      new_model.save()
      new_model.encrypted_contents2 = encrypted_contents
      new_model.contents = b''
      new_model.save()
      x = models.ToDoList.objects.filter(user__id=user_id)
      assert len(x) == 1, user_id
    self._place_to_save_read['saved_read'] = b


class SerializationReader(object):
  def __init__(self, user, place_to_save_read=None):
    """Init.

    Args:
      user: models.User
      place_to_save_read: None|dict that will have 'saved_read' filled in with
        the result of the read
    """
    self._user = user
    if place_to_save_read is None:
      self._place_to_save_read = {}
    else:
      self._place_to_save_read = place_to_save_read
      self._place_to_save_read['saved_read'] = None
    self.name = 'DB entity for %s' % user.email

  def read(self):
    user_id = self._user.id
    x = models.ToDoList.objects.filter(user__id=user_id)
    if len(x) > 0:
      if x[0].encrypted_contents2:
        decrypted_contents = _decrypted_todolist_protobuf(
          bytes(x[0].encrypted_contents2, 'utf-8') if six.PY3 else bytes(x[0].encrypted_contents2))
      else:
        _debug_log('reading old decrypted contents')
        decrypted_contents = x[0].contents
      self._place_to_save_read['saved_read'] = decrypted_contents
      return decrypted_contents
    else:
      self._place_to_save_read['saved_read'] = None
      return ''


class SavedSerializationReader(object):
  """Skips expensive deserialization from the DB and reuses a previous read."""
  def __init__(self, saved_read):
    self._saved_read = saved_read
    assert saved_read is not None
    self.name = 'Previous DB read'

  def read(self):
    return self._saved_read


class LogoutView(views.LogoutView):
  """Clears _COOKIE_NAME cookie upon sign out.

  TODO(chandler37): when USE_ALLAUTH is True, now we must set ADAPTER =
  todo.allauth_adapter.CookieClearingAdapter which will be a subclass of
  allauth.account.adapter.DefaultAccountAdapter. But it's probably
  better just to stop using our cookie and use the django session
  instead.

  django.contrib.auth.signals.user_logged_out has no
  access to the response so we have to subclass
  django.contrib.auth.views.LogoutView.
  """
  @method_decorator(never_cache)
  def dispatch(self, request, *args, **kwargs):
    response = super().dispatch(request, *args, **kwargs)
    response.delete_cookie(_COOKIE_NAME)
    request.session.flush()
    return response


def _debug_log(the_string):
  """Writes to a debug log bad cookies etc."""
  # Standard output is written to Heroku logs; see
  # https://devcenter.heroku.com/articles/logging and consider installing the
  # Heroku app 'papertrail'.
  print(the_string)


def _get_uid(request, param_name):
  uid = request.POST.get(param_name, '')
  if uid:
    try:
      uid = int(uid, 10)
      return uid
    except ValueError:
      pass
  return None


def _nickname(user):
  if len(user.email):
    return '%s (%s)' % (user.username, user.email)
  else:
    if re.match(r'^T.*:U.*', user.username):
        return 'Slacker'
    return user.username


def _render(request, template_name, options=None):
  d = {"Nickname": _nickname(request.user)}
  if options:
    d.update(options)
  return TemplateResponse(request, template_name, d)


def _error_page(request, txt):
  return _render(
    request, "error.html",
    {"ErrorText": txt,
     "Title": "Error"})


def _execute_cmd(request, uid, template_dict, cookie_value=None):
  """Returns (saved_read|None, error_page|None).

  Mutates template_dict["Flash"] and cookie_value.
  """
  cmd = request.POST.get('cmd', '')
  if not cmd:
    return None, None
  saved_read = None  # We don't need to read the DB more than once.
  if cmd not in ('complete', 'completereview', 'uncomplete', 'rmact', 'rmctx',
                 'rmprj', 'chctx', 'mv', 'view', 'activatectx', 'chdefaultctx',
                 'deactivatectx', 'activateprj', 'deactivateprj', 'rename',
                 'clearreview', 'note', 'note_for_weekly_review',
                 'note_for_home', 'prjify', 'togglecomplete',
                 'toggleincomplete', 'inboxize', 'inboxize_home'):
    return None, _error_page(request, 'cmd must not be %s' % cmd)

  def ReplaceNote(destination):
    if destination == 'uid=0':
      destination = ':__actions_without_context'
    value = request.POST.get('noteText', '').replace('\r\n', '\n').replace('\n', '\\n')
    command_line = 'note --replace %s %s' % (destination, pipes.quote(value),)
    cmd_result = _apply_batch_of_commands(
        request.user,
        [command_line],
        read_only=False)
    template_dict["Flash"] = "<strong>Note saved.</strong>"
    return cmd_result

  def Inboxize(destination):
    if destination == 'uid=0':
      destination = ':__actions_without_context'
    command_line = 'note --inboxize ' + destination
    cmd_result = _apply_batch_of_commands(
        request.user,
        [command_line],
        read_only=False)
    template_dict["Flash"] = "<strong>Note transformed into Actions in the Inbox.</strong>"
    return cmd_result

  try:
    if cmd == 'undeleteandmarkincomplete':
        return None, _error_page(request, 'Cannot change a deleted Action')
    elif cmd in ('togglecomplete', 'toggleincomplete'):
      target_uid = _get_uid(request, 'target_uid')
      if target_uid is None:
        return None, _error_page(request, 'Needs integer POST arg "target_uid"')
      cmd_result = _apply_batch_of_commands(
          request.user,
          ['%s uid=%s'
           % ("complete" if cmd == "togglecomplete" else "uncomplete",
              target_uid)],
          read_only=False)
      template_dict["Flash"] = "<strong>Marked Action %s %s.</strong>" % (target_uid, "Complete" if cmd == "togglecomplete" else "Incomplete")
    elif cmd == 'chdefaultctx':
      new_default_uid = _get_uid(request, 'new_default_uid')
      if new_default_uid is None:
        return None, _error_page(request, 'Needs integer POST arg "new_default_uid"')
      cmd_result = _apply_batch_of_commands(
          request.user,
          ['%s uid=%s uid=%s' % (cmd, new_default_uid, uid)],
          read_only=False)
      if new_default_uid == 0:
        template_dict["Flash"] = "<strong>Default context removed; new actions will be without context.</strong>"
      else:
        template_dict["Flash"] = "<strong>Default context changed; new actions will be assigned your chosen context. All actions without context assigned the new context.</strong>"
    elif cmd in ('chctx', 'mv'):
      new_uid = _get_uid(request, 'new_uid')
      if new_uid is None:
        return None, _error_page(request, 'Needs integer POST arg "new_uid"')
      cmd_result = _apply_batch_of_commands(
          request.user,
          ['%s uid=%s uid=%s' % (cmd,
                                 new_uid if cmd == 'chctx' else uid,
                                 uid if cmd == 'chctx' else new_uid)],
          read_only=False)
      if cmd == 'chctx':
        template_dict["Flash"] = "<strong>Context changed.</strong>"
      elif cmd == 'mv':
        template_dict["Flash"] = "<strong>Project changed.</strong>"
    elif cmd == 'rename':
      new_name = request.POST.get('new_name', '')
      if not new_name:
        return None, _error_page(request, 'Cannot rename to the empty string')
      command_line = '%s --allow_slashes --autoctx uid=%s %s' % (cmd, uid, pipes.quote(new_name))
      cmd_result = _apply_batch_of_commands(
          request.user,
          [command_line],
          read_only=False)
      template_dict["Flash"] = "<strong>Renamed.</strong>"
    elif cmd == 'note':
      cmd_result = ReplaceNote('uid=%s' % uid)
    elif cmd == 'inboxize':
      cmd_result = Inboxize('uid=%s' % uid)
    elif cmd == 'inboxize_home':
      cmd_result = Inboxize(':__home')
    elif cmd == 'note_for_weekly_review':
      cmd_result = ReplaceNote(':__weekly_review')
    elif cmd == 'note_for_home':
      cmd_result = ReplaceNote(':__home')
    elif cmd == 'view':
      view_filter = request.POST.get('view_filter', '')
      assert view_filter in (
        'all', 'actionable', 'all_even_deleted', 'inactive_and_incomplete', 'incomplete', 'needing_review'), view_filter
      cmd_result = _apply_batch_of_commands(
          request.user,
          ['%s %s' % (cmd, view_filter)],
          read_only=False)
      assert cookie_value is not None
      cookie_value.view = view_filter
      template_dict["Flash"] = "<strong>View filter updated.</strong>"
    elif cmd == 'clearreview':
      prj = request.POST.get('prj', '')
      cmd_result = _apply_batch_of_commands(
          request.user,
          ['%s %s' % (cmd, pipes.quote(prj))] if prj else [cmd],
          read_only=False)
      if prj:
        template_dict["Flash"] = "<strong>Project marked unreviewed.</strong>"
      else:
        template_dict["Flash"] = "<strong>All projects marked unreviewed.</strong>"
    elif cmd in ('complete', 'rmprj'):
      cmd_result = _apply_batch_of_commands(
          request.user,
          ['%s -f uid=%s' % (cmd, uid)],
          read_only=False)
      if cmd == 'complete':
        template_dict["Flash"] = "<strong>Done!</strong>"
      elif cmd == 'rmprj':
        template_dict["Flash"] = "<strong>Deleted.</strong>"
    else:
      cmd_result = _apply_batch_of_commands(
          request.user,
          ['%s uid=%s' % (cmd, uid)],
          read_only=False)
      if cmd == 'completereview':
        template_dict["Flash"] = "<strong>Project marked reviewed.</strong>"
      elif cmd == 'uncomplete':
        template_dict["Flash"] = "<strong>Marked incomplete.</strong>"
      elif cmd == 'activatectx' or cmd == 'activateprj':
        template_dict["Flash"] = "<strong>Activated.</strong>"
      elif cmd == 'deactivatectx' or cmd == 'deactivateprj':
        template_dict["Flash"] = "<strong>Deactivated.</strong>"
      elif cmd == 'prjify':
        template_dict["Flash"] = '<strong><a href="/todo/project/%s">Converted to a new project. Projects contain actions.</a></strong>' % cmd_result['printed'][0]
    saved_read = cmd_result['saved_read']
    assert saved_read is not None
  except immaculater.Error as e:
    return None, _error_page(request, six.text_type(e))
  return saved_read, None


def _apply_batch_of_commands(user, batch, read_only, saved_read=None, cookie=None):
  """Apply a list of commands, reading from and writing to the DB.

  Args:
    user: models.User
    batch: [str]
    read_only: bool
    saved_read: object  # from previous call to this function
    cookie: pyatdl_pb2.VisitorInfo0
  Returns:
    {'pwd': str,  # current working directory afterwards, see 'help cd'
     'pwd_uid': int  # current working directory's UID
     'printed': [str],
     'saved_read': object,
     'view': str}  # see 'help view'
  Raises:
    immaculater.Error
  """
  f = io.BytesIO()
  codecinfo = codecs.lookup("utf8")
  wrapper = codecs.StreamReaderWriter(
    f, codecinfo.streamreader, codecinfo.streamwriter)
  if cookie is not None:
    # Swallow errors if we have a bad cookie.
    wrapper.write('cd --swallow_errors uid=%d\n' % cookie.cwc_uid)
    wrapper.write('view %s\n' % pipes.quote(cookie.view))
    wrapper.write('sort %s\n' % pipes.quote(cookie.sort))
  for b in batch:
    assert not b.endswith('\n'), b
    wrapper.write(b)
    wrapper.write('\n')
  wrapper.seek(0)
  printed = []

  def Print(s):
    printed.append(s)

  place_to_save_read = {'saved_read': saved_read}
  try:
    if saved_read is not None:
      reader = SavedSerializationReader(saved_read)
    else:
      reader = SerializationReader(user, place_to_save_read)
    writer = SerializationWriter(
      'write only if nothing is yet written' if read_only else 'write',
      user,
      place_to_save_read)
    result_dict = immaculater.ApplyBatchOfCommands(
      wrapper, Print, reader, writer, html_escaper=escape)
  finally:
    wrapper.close()
  return {'pwd': result_dict['cwc'],
          'pwd_uid': result_dict['cwc_uid'],
          'printed': printed,
          'saved_read': place_to_save_read['saved_read'],
          'view': result_dict['view']}


def _username_hash(username):
  """Returns bytes, a cryptographically safe one-way hash of the username.

  This way, if someone breaks the Fernet encryption, they still don't know the
  username.

  Args:
    username: unicode
  """
  return hashlib.sha256(username.encode('utf-8')).digest()


def _default_cookie_value(username):
  p = pyatdl_pb2.VisitorInfo0()
  p.sanity_check = _SANITY_CHECK
  p.cwc_uid = 1  # Inbox
  p.view = view_filter.ShowNotDeleted.ViewFilterUINames()[0]
  p.username_hash = _username_hash(username)
  # Let p.sort be the default value from the .proto file.
  return p
  # TODO(chandler): Add a unittest without a cookie (and several with).


def _deserialized_cookie_value(cookie_raw_value):
  """Returns the blob that the base64-encoded, Fernet-encrypted, raw value represents.

  Args:
    cookie_raw_value: str  # url-safe base64
  Returns:
     str|None  # None on error, else a blob
  """
  if not cookie_raw_value:
    return None
  x = None
  try:
    x = base64.urlsafe_b64decode(cookie_raw_value)
  except TypeError:
    _debug_log('bad cookie raw value %s' % cookie_raw_value)
    return None
  try:
    return _cookie_fernet().decrypt(x)
  except InvalidToken:
    _debug_log('Invalid token')
    return None


def _default_debug_encryption_key():
  if os.environ.get('DJANGO_DEBUG', '').lower() == 'true':
    # See Fernet.generate_key():
    return 'ZdT5H2hhrJY9sNdpzdXiGeRd7JMPprR4yrzp4nLzUVo='
  return None


def _cookie_fernet():
  key = os.environ.get('FERNET_COOKIE_KEY', _default_debug_encryption_key())
  assert key is not None, 'No value set for environment variable FERNET_COOKIE_KEY; see .env file'
  assert len(key) > 40, 'Bad value of env var FERNET_COOKIE_KEY; use Fernet.generate_key() and heroku config:set'
  return Fernet(key.encode('ascii'))


def _protobuf_fernet():
  key = os.environ.get('FERNET_PROTOBUF_KEY', _default_debug_encryption_key())
  assert key is not None, 'No value set for environment variable FERNET_PROTOBUF_KEY; see .env file'
  assert len(key) > 40, 'Bad value of env var FERNET_PROTOBUF_KEY; use Fernet.generate_key() and heroku config:set'
  return Fernet(key.encode('ascii'))


def _serialized_cookie_value(cookie_value):
  """Returns base64-encoded form of encrypted cookie_value.

  Args:
    cookie_value: pyatdl_pb2.VisitorInfo0
  Returns:
    str  # url-safe base64
  """
  # SerializeToString will not throw.
  encrypted_value = _cookie_fernet().encrypt(cookie_value.SerializeToString())
  return base64.urlsafe_b64encode(encrypted_value).decode('utf-8')


def _cookie_value(request):
  """Returns the deserialized form of the VISITOR_INFO0 cookie, or a default.

  Args:
    request: HTTPRequest
  Returns:
    pyatdl_pb2.VisitorInfo0
  """
  if _COOKIE_NAME in request.COOKIES:
    value = request.COOKIES[_COOKIE_NAME]
    blob = _deserialized_cookie_value(value)
    if blob is None:
      _debug_log('insane cookie value %s' % value)
      return _default_cookie_value(request.user.username)
    try:
      cookie_value = pyatdl_pb2.VisitorInfo0.FromString(blob)
    except message.Error as e:
      _debug_log('cookie message.Error %s' % six.text_type(e))
      return _default_cookie_value(request.user.username)
    if cookie_value.sanity_check == _SANITY_CHECK and cookie_value.username_hash == _username_hash(request.user.username):
      return cookie_value
    else:
      _debug_log('cookie sanity check %s' % cookie_value.sanity_check)
      return _default_cookie_value(request.user.username)
  return _default_cookie_value(request.user.username)


def _set_cookie(response, key, value, days_expire=365):
  max_age = days_expire * 24 * 60 * 60
  expires = datetime.datetime.strftime(
    datetime.datetime.utcnow() + datetime.timedelta(seconds=max_age),
    "%a, %d-%b-%Y %H:%M:%S GMT")
  # Insecure, please:
  response.set_cookie(key, value, max_age=max_age, expires=expires)


# Tests our Sentry integration and tests that we are not showing stack traces
# to users in production (a security no-no and a UX faux pas):
@never_cache
def five_hundred(request):
    division_by_zero = 1 / 0  # # noqa: F841


@xframe_options_sameorigin
@never_cache
@login_required
def as_text(request, the_view_filter):
  if request.method != 'GET':
    raise Http404()
  response = HttpResponse(content_type='text/plain;charset=utf-8')
  try:
    x = _apply_batch_of_commands(
      request.user,
      ["view %s" % ("all_even_deleted" if the_view_filter is None else the_view_filter,),
       "sort alpha",
       "astaskpaper"],
      read_only=True)
    response.write('\n'.join(x['printed']))
  except immaculater.Error as e:
    return _error_page(request, six.text_type(e))
  return response


@xframe_options_sameorigin
@never_cache
def privacy(request):
  if request.method != 'GET':
    raise Http404()
  return TemplateResponse(request, "privacy.html", {})


@djpjax.pjax()
@never_cache
@login_required
def as_text2(request):
  if request.method != 'GET' and request.method != 'POST':
    raise Http404()
  cookie_value = _cookie_value(request)
  template_dict = {"Flash": "",
                   "Title": "View Text"}
  saved_read, error_page = _execute_cmd(request, None, template_dict, cookie_value)
  template_dict["ViewFilter"] = cookie_value.view
  if error_page is not None:
    return error_page
  if saved_read is not None and not _using_pjax(request):  # https://en.wikipedia.org/wiki/Post/Redirect/Get
    response = redirect('text')
    _set_cookie(response, _COOKIE_NAME, _serialized_cookie_value(cookie_value))
    return response
  try:
    x = _apply_batch_of_commands(
      request.user,
      ["view %s" % ("all" if cookie_value.view is None else cookie_value.view,),
       "sort alpha",
       "hypertext /todo"],
      read_only=True)
    template_dict["Hypertext"] = '\n'.join(x['printed'])
  except immaculater.Error as e:
    return _error_page(request, six.text_type(e))
  response = _render(request, "as_text2.html", template_dict)
  _set_cookie(response, _COOKIE_NAME, _serialized_cookie_value(cookie_value))
  return response


@djpjax.pjax()
@never_cache
@login_required
def search(request):
  if request.method != 'GET' and request.method != 'POST':
    raise Http404()
  search_query = request.GET.get('q', '') or request.POST.get('q', '')
  template_dict = {"Flash": "", "Title": "Search"}
  try:
    x = _apply_batch_of_commands(
      request.user,
      ["view all_even_deleted",
       "sort alpha",
       "hypertext --search_query %s /todo" % pipes.quote(search_query) if search_query else "hypertext /todo"],
      read_only=True)
    template_dict["Hypertext"] = '\n'.join(x['printed'])
  except immaculater.Error as e:
    return _error_page(request, six.text_type(e))
  response = _render(request, "search.html", template_dict)
  return response


@djpjax.pjax()
@never_cache
@login_required
def update_todolist(request):  # /todo/cli
  cookie_value = _cookie_value(request)
  command = request.POST.get('command', '').replace('\u2014', '--')  # em dash
  batch = []
  batch.append('echo "<Beginning of command line output, if any>"')
  subcommand = None
  # We use the UNIX (e.g., bash) '&&' command separator. It means that the
  # failure of the former command forbids execution of the latter, and that is
  # true here.
  #
  # We support having '&&' in data (action names, prj names, etc.) via escaping
  # as in 'cd /x&&touch a\&\&b'.
  for subcommand in command.split('&&'):
    subcommand = subcommand.strip()
    batch.append(subcommand)
  batch.append('echo "<End of command line output, if any>"')
  if subcommand is None or (not subcommand.startswith('dump') and not subcommand.startswith('help') and not subcommand.startswith('ls') and not subcommand.startswith('astaskpaper') and not subcommand.startswith('todo')):
    batch.append('echo')
    batch.append('echo The result of running \\"todo\\" is as follows:')
    batch.append('echo')
    batch.append('todo')
  try:
    x = _apply_batch_of_commands(request.user, batch, read_only=False, cookie=cookie_value)
  except immaculater.Error as e:
    return _error_page(request, six.text_type(e))
  response = _render(
    request,
    "update_todolist.html",
    {"ToDoListPre": '\n'.join(x['printed']),
     "Cwd": x['pwd'],  # needs escapejs
     "View": x['view'],  # needs escapejs
     "Title": "Command-Line Interface"})
  cookie_value.cwc_uid = x['pwd_uid']
  cookie_value.view = x['view']
  _set_cookie(response, _COOKIE_NAME, _serialized_cookie_value(cookie_value))
  return response


@djpjax.pjax()
@never_cache
@login_required
def contexts(request):
  cookie_value = _cookie_value(request)
  template_dict = {"Flash": ""}
  saved_read, error_page = _execute_cmd(request, None, template_dict, cookie_value)
  if error_page is not None:
    return error_page
  new_ctx = request.POST.get('new_ctx', '').strip()
  if new_ctx:
    try:
      mkctx = _apply_batch_of_commands(
          request.user, ['mkctx --verbose %s' % pipes.quote(new_ctx)], read_only=False)
      saved_read = mkctx['saved_read']
      assert saved_read is not None
      assert len(mkctx['printed']) == 1, mkctx['printed']
      new_uid = mkctx['printed'][0]
      template_dict["Flash"] = '<strong><a href="/todo/context/%s">Context %s created.</a></strong>' % (new_uid, new_uid)
    except immaculater.Error as e:
      return _error_page(request, six.text_type(e))
  if saved_read is not None and not _using_pjax(request):  # https://en.wikipedia.org/wiki/Post/Redirect/Get
    response = redirect('contexts')
    _set_cookie(response, _COOKIE_NAME, _serialized_cookie_value(cookie_value))
    return response
  return _contexts_get(request, template_dict, cookie_value)


def _contexts_get(request, template_dict, cookie_value):  # mutates template_dict
  lsctx = _apply_batch_of_commands(request.user, ['lsctx --json'], read_only=True,
                                   saved_read=None, cookie=cookie_value)
  assert lsctx['saved_read'] is not None
  assert len(lsctx['printed']) == 1, lsctx['printed']
  template_dict.update({
    "ContextsJSON": lsctx['printed'][0],
    "NoContextDisplayString": FLAGS.no_context_display_string,
    "ViewFilter": cookie_value.view,
    "Title": "Contexts"})
  response = _render(
    request,
    "contexts.html",
    template_dict)
  _set_cookie(response, _COOKIE_NAME, _serialized_cookie_value(cookie_value))
  return response


@djpjax.pjax()
@never_cache
@login_required
def context(request, uid):
  cookie_value = _cookie_value(request)
  uid = int(uid, 10)
  template_dict = {"Flash": ""}
  saved_read, error_page = _execute_cmd(request, uid, template_dict, cookie_value)
  if error_page is not None:
    return error_page
  new_action = request.POST.get('new_action', '').strip()
  if new_action:
    try:
      batch = ['cd uid=1',
               'mkact --verbose --autoprj --allow_slashes --context uid=%d %s' % (
                 uid, pipes.quote(new_action))]
      mkact = _apply_batch_of_commands(request.user, batch, read_only=False)
      saved_read = mkact['saved_read']
      assert saved_read is not None
      assert len(mkact['printed']) == 1, mkact['printed']
      new_uid = mkact['printed'][0].strip()
      template_dict["Flash"] = '<strong><a href="/todo/action/%s">Action %s created.</a></strong> (Expecting to see it? Change your view filter.)' % (new_uid, new_uid)
    except immaculater.Error as e:
      return _error_page(request, six.text_type(e))
  if saved_read is not None and not _using_pjax(request):  # https://en.wikipedia.org/wiki/Post/Redirect/Get
    response = redirect('context', uid=uid)
    _set_cookie(response, _COOKIE_NAME, _serialized_cookie_value(cookie_value))
    return response
  return _context_get(request, uid, template_dict, cookie_value)


def _context_get(request, uid, template_dict, cookie_value):  # mutates template_dict
  inctx = _apply_batch_of_commands(
    request.user, ['inctx --sort_by ctime --json %s' % ('uid=%d' % uid)],
    read_only=True,
    saved_read=None, cookie=cookie_value)
  assert len(inctx['printed']) == 1, inctx['printed']
  saved_read = inctx['saved_read']
  if uid == 0:
    lsctx = {'printed':
             ['{"ctime":null,"dtime":null,"is_active":true,"is_complete":false,"is_deleted":false,"mtime":null,"name":"%s","uid":0}'
              % FLAGS.no_context_display_string]}
  else:
    lsctx = _apply_batch_of_commands(
      request.user, ['lsctx --json uid=%d' % uid],
      read_only=True,
      saved_read=saved_read, cookie=cookie_value)
    assert len(lsctx['printed']) == 1, lsctx['printed']
  if uid == 0:
    note = _apply_batch_of_commands(request.user, ['note :__actions_without_context'],
                                    read_only=True, saved_read=saved_read)
  else:
    note = _apply_batch_of_commands(request.user, ['note uid=%d' % uid],
                                    read_only=True, saved_read=saved_read)
  template_dict.update(
    {"InctxJSON": inctx['printed'][0],
     "LsctxJSON": lsctx['printed'][0],
     "UID": six.text_type(uid),
     "ViewFilter": cookie_value.view,
     "Note": '\n'.join(note['printed']),
     "Title": "Context"})
  response = _render(
    request,
    "context.html",
    template_dict)
  _set_cookie(response, _COOKIE_NAME, _serialized_cookie_value(cookie_value))
  return response


@djpjax.pjax()
@never_cache
@login_required
def projects(request):
  cookie_value = _cookie_value(request)
  template_dict = {"Flash": ""}
  saved_read, error_page = _execute_cmd(request, None, template_dict, cookie_value)
  if error_page is not None:
    return error_page
  new_prj = request.POST.get('new_prj', '')
  new_folder = request.POST.get('new_folder', '')
  if new_prj and new_folder:
      return _error_page(
        request,
        'Cannot create a new project and a new folder simultaneously.')
  if new_prj:
    try:
      mkprj = _apply_batch_of_commands(
          request.user,
          ['cd /',
           'mkprj --verbose --allow_slashes %s' % pipes.quote(new_prj)],
          read_only=False)
      saved_read = mkprj['saved_read']
      assert saved_read is not None
      assert len(mkprj['printed']) == 1, mkprj['printed']
      new_uid = mkprj['printed'][0]
      template_dict["Flash"] = '<strong><a href="/todo/project/%s">Project %s created.</a></strong>' % (new_uid, new_uid)
    except immaculater.Error as e:
      return _error_page(request, six.text_type(e))
  if new_folder:
    if not os.path.isabs(new_folder):
      return _error_page(
        request,
        'Path must be absolute, e.g. "/Folder51" or "/Folder0/Folder1"')
    try:
      mkdir = _apply_batch_of_commands(
          request.user,
          ['cd %s' % pipes.quote(os.path.dirname(new_folder)),
           'mkdir %s' % pipes.quote(os.path.basename(new_folder))],
          read_only=False)
      saved_read = mkdir['saved_read']
      assert saved_read is not None
      template_dict["Flash"] = "<strong>Folder created.</strong>"
    except immaculater.Error as e:
      return _error_page(
        request, six.text_type(e))
  if saved_read is not None and not _using_pjax(request):  # https://en.wikipedia.org/wiki/Post/Redirect/Get
    response = redirect('projects')
    _set_cookie(response, _COOKIE_NAME, _serialized_cookie_value(cookie_value))
    return response
  return _projects_get(request, template_dict, cookie_value)


def _projects_get(request, template_dict, cookie_value):  # mutates template_dict
  lsprj = _apply_batch_of_commands(request.user, ['lsprj --json'],
                                   read_only=True, saved_read=None,
                                   cookie=cookie_value)
  saved_read = lsprj['saved_read']
  assert saved_read is not None
  assert len(lsprj['printed']) == 1, lsprj['printed']
  needsreview = _apply_batch_of_commands(request.user, ['needsreview --json'],
                                         read_only=True, saved_read=saved_read,
                                         cookie=cookie_value)
  assert len(needsreview['printed']) == 1, needsreview['printed']
  template_dict.update(
    {"ProjectsJSON": lsprj['printed'][0],
     "NeedsreviewJSON": needsreview['printed'][0],
     "ViewFilter": cookie_value.view,
     "Title": "Projects"})
  response = _render(
    request,
    "projects.html",
    template_dict)
  _set_cookie(response, _COOKIE_NAME, _serialized_cookie_value(cookie_value))
  return response


@djpjax.pjax()
@never_cache
@login_required
def project(request, uid):
  cookie_value = _cookie_value(request)
  uid = int(uid, 10)
  template_dict = {"Flash": ""}
  saved_read, error_page = _execute_cmd(request, uid, template_dict, cookie_value)
  if error_page is not None:
    return error_page
  new_action = request.POST.get('new_action', '').strip()
  if new_action:
    try:
      mkact = _apply_batch_of_commands(
          request.user,
          ['cd uid=%d' % uid,
           'mkact --verbose --noautoprj --allow_slashes %s' % pipes.quote(new_action)],
          read_only=False)
      saved_read = mkact['saved_read']
      assert saved_read is not None
      assert len(mkact['printed']) == 1, mkact['printed']
      new_uid = mkact['printed'][0]
      template_dict["Flash"] = '<strong><a href="/todo/action/%s">Action %s created.</a></strong> (Expecting to see it? Change your view filter.)' % (new_uid, new_uid)
    except immaculater.Error as e:
      return _error_page(request, six.text_type(e))
  if saved_read is not None and not _using_pjax(request):  # https://en.wikipedia.org/wiki/Post/Redirect/Get
    response = redirect('project', uid=uid)
    _set_cookie(response, _COOKIE_NAME, _serialized_cookie_value(cookie_value))
    return response
  return _project_get(request, uid, template_dict, cookie_value)


def _project_get(request, uid, template_dict, cookie_value):
  inprj = _apply_batch_of_commands(request.user, ['inprj --json uid=%s' % uid],
                                   read_only=True, saved_read=None,
                                   cookie=cookie_value)
  saved_read = inprj['saved_read']
  assert saved_read is not None
  assert len(inprj['printed']) == 1, inprj['printed']
  needsreview = _apply_batch_of_commands(request.user, ['needsreview --json'],
                                         read_only=True, saved_read=saved_read,
                                         cookie=cookie_value)
  assert len(needsreview['printed']) == 1, needsreview['printed']
  lsprj = _apply_batch_of_commands(request.user, ['lsprj --json uid=%s' % uid],
                                   read_only=True, saved_read=saved_read,
                                   cookie=cookie_value)
  assert len(lsprj['printed']) == 1, lsprj['printed']
  note = _apply_batch_of_commands(request.user, ['note uid=%d' % uid],
                                  read_only=True, saved_read=saved_read)
  lsctx = _apply_batch_of_commands(request.user,
                                   ['view incomplete', 'sort alpha', 'lsctx --json'],
                                   read_only=True, saved_read=saved_read)
  assert len(lsctx['printed']) == 1, lsctx['printed']
  template_dict.update(
    {"InprjJSON": inprj['printed'][0],
     "NeedsreviewJSON": needsreview['printed'][0],
     "LsprjJSON": lsprj['printed'][0],
     "UndeletedLsctxJSON": lsctx['printed'][0],
     "UID": six.text_type(uid),
     "ViewFilter": cookie_value.view,
     "Title": "Project",
     "Note": '\n'.join(note['printed'])})
  response = _render(
    request,
    "project.html",
    template_dict)
  _set_cookie(response, _COOKIE_NAME, _serialized_cookie_value(cookie_value))
  return response


def _using_pjax(request):
  return request.META.get('HTTP_X_PJAX', False)


# no login required to view a shared to-do list:
@never_cache
def view(request, slug):
  if request.method != 'GET':
    raise Http404()
  x = models.Share.objects.filter(slug=slug)
  if not x or not x[0].is_active or not x[0].user.is_active:
    raise PermissionDenied()
  response = HttpResponse(content_type='text/plain;charset=utf-8')
  try:
    xx = _apply_batch_of_commands(
      x[0].user,
      ["view all", "sort alpha", "astaskpaper"],
      read_only=True)
    response.write('\n'.join(xx['printed']))
  except immaculater.Error as e:
    return _error_page(request, six.text_type(e))
  return response


def _deactivate_all_shares_for_user(user):
  for model in models.Share.objects.filter(user=user):
    model.is_active = False
    model.save()


@transaction.atomic  # These nest with ATOMIC_REQUESTS. I'm just being explicit.
def _create_share(user, slug):
  _deactivate_all_shares_for_user(user)
  new_model = models.Share(user=user, is_active=True, slug=slug)
  new_model.save()
  return new_model


@djpjax.pjax()
@never_cache
@login_required
def action(request, uid):
  uid = int(uid, 10)
  template_dict = {"Flash": ""}
  saved_read, error_page = _execute_cmd(request, uid, template_dict)
  if error_page is not None:
    return error_page
  if saved_read is not None and not _using_pjax(request):  # https://en.wikipedia.org/wiki/Post/Redirect/Get unless it's an AJAX form submission
    return redirect('action', uid=uid)
  return _action_get(request, uid, template_dict)


def _action_get(request, uid, template_dict):  # mutates template_dict
  try:
    lsact = _apply_batch_of_commands(
        request.user,
        ['lsact --json uid=%d' % uid],
        read_only=True, saved_read=None)
  except immaculater.Error as e:
    return _error_page(request, six.text_type(e))
  assert len(lsact['printed']) == 1, lsact['printed']
  saved_read = lsact['saved_read']
  lsctx = _apply_batch_of_commands(request.user,
                                   ['view incomplete', 'sort alpha', 'lsctx --json'],
                                   read_only=True, saved_read=saved_read)
  assert len(lsctx['printed']) == 1, lsctx['printed']
  lsprj = _apply_batch_of_commands(request.user,
                                   ['view incomplete', 'sort alpha', 'lsprj --json'],
                                   read_only=True, saved_read=saved_read)
  assert len(lsprj['printed']) == 1, lsprj['printed']
  note = _apply_batch_of_commands(request.user, ['note uid=%d' % uid],
                                  read_only=True, saved_read=saved_read)
  template_dict.update(
    {"LsactJSON": lsact['printed'][0],
     "UndeletedLsctxJSON": lsctx['printed'][0],
     "UndeletedLsprjJSON": lsprj['printed'][0],
     "Note": '\n'.join(note['printed']),
     "Title": "Action",
     "UID": six.text_type(uid)})
  return _render(
    request,
    "action.html",
    template_dict)


def _create_new_action(request, template_dict, var_name='new_action'):
  new_action = request.POST.get(var_name, '').strip()
  if new_action:
    try:
       result = _apply_batch_of_commands(
           request.user,
           ['cd uid=1',
            'mkact --verbose --autoprj --allow_slashes %s' % (pipes.quote(new_action),)],  # a.k.a. touch
           read_only=False)
       assert len(result['printed']) == 1, result['printed']
       uid = result['printed'][0].strip()
       template_dict['Flash'] = '<a href="/todo/action/%s"><strong>Action %s created.</strong></a> (Expecting to see it? Refresh this page or change the view filter.)' % (uid, uid)
       return True, None
    except immaculater.Error as e:
      return False, _error_page(request, six.text_type(e))
  return False, None


def _create_new_project(request, template_dict):
  new_project = request.POST.get('new_project', '').strip()
  if new_project:
    try:
       result = _apply_batch_of_commands(
           request.user,
           ['cd %s' % (pipes.quote(FLAGS.pyatdl_separator),),
            'mkprj --verbose --allow_slashes %s' % (pipes.quote(new_project),)],
           read_only=False)
       assert len(result['printed']) == 1, result['printed']
       uid = result['printed'][0].strip()
       template_dict['Flash'] = '<strong><a href="/todo/project/%s">Project %s created.</a></strong>' % (uid, uid)
    except immaculater.Error as e:
      return _error_page(request, six.text_type(e))
  return None


@djpjax.pjax()
@never_cache
@login_required
def home(request):
  template_dict = {"Flash": ""}
  quick_capture = request.POST.get('quick_capture', '').strip()
  if quick_capture and quick_capture[0] == '/':
    # a search query. TODO(chandler): create a separate search box in the
    # navigation bar that actually navigates you to the /todo/search?q=query
    # page. Or do some javascript magic to make the one-true-navbar-box able to
    # navigate to the /todo/search page.
    template_dict["Flash"] = '<a href="/todo/search?q=%s">Click here to search.</a>' % escape_uri_path(quick_capture[1:])
    return _render(request,
                   "flash.html",
                   template_dict)
  created, error_page = _create_new_action(request, template_dict, 'quick_capture')
  if error_page is not None:
    # TODO(chandler): show the error in the flash message? Test by quick
    # capturing "uid=1".
    return error_page
  if created:
    if not _using_pjax(request):  # https://en.wikipedia.org/wiki/Post/Redirect/Get
      return redirect('home')
    else:
      assert template_dict["Flash"]
      return _render(request,
                     "flash.html",
                     template_dict)
  _, error_page = _create_new_action(request, template_dict)  # new_action var name
  if error_page is not None:
    return error_page
  error_page = _create_new_project(request, template_dict)
  if error_page is not None:
    return error_page
  cookie_value = _cookie_value(request)
  saved_read, error_page = _execute_cmd(request, None, template_dict, cookie_value)
  if error_page is not None:
    return error_page
  if request.method == 'POST' and not _using_pjax(request):  # https://en.wikipedia.org/wiki/Post/Redirect/Get
    return redirect('home')
  note = _apply_batch_of_commands(request.user, ['note :__home'],
                                  read_only=True, saved_read=saved_read)
  template_dict.update({"Title": "Home",
                        "Note": '\n'.join(note['printed'])})
  return _render(request,
                 "home.html",
                 template_dict)


@djpjax.pjax()  # but we don't always use pjax forms for this one
@never_cache
@login_required
def dl(request):
  flash = ""
  if request.method == 'POST':
    if request.POST.get('command') == 'dl':
      assert not _using_pjax(request)
      response = HttpResponse(content_type='application/octet-stream')
      response['Content-Disposition'] = 'attachment; filename="immaculater.dat"'
      response.write(SerializationReader(request.user).read())
      return response
    elif request.POST.get('command') == 'purgedeleted':
      _apply_batch_of_commands(  # will not throw an exception
          request.user,
          ['purgedeleted'],
          read_only=False)
      if not _using_pjax(request):  # https://en.wikipedia.org/wiki/Post/Redirect/Get
        return redirect('/todo/dl')  # TODO(chandler): Don't hard-code the link
      flash = "<strong>Are you sure?</strong> Just kidding! Already obliterated everything that was deleted, including contexts, actions, and projects."  # and folders.
    elif request.POST.get('command') == 'deletecompleted':
      _apply_batch_of_commands(  # will not throw an exception
          request.user,
          ['deletecompleted'],
          read_only=False)
      if not _using_pjax(request):  # https://en.wikipedia.org/wiki/Post/Redirect/Get
        return redirect('/todo/dl')  # TODO(chandler): Don't hard-code the link
      flash = "Deleted everything that was completed. You may now use the &quot;<strong>Purge Deleted</strong>&quot; command to remove deleted items. You can see deleted items using the &quot;<strong>Truly all, even deleted</strong>&quot; view filter."
    else:
      return _error_page(request, 'invalid command')
  return _render(request, "dl.html",
                 {"Title": "Download Your Data",
                  "Flash": flash})


@djpjax.pjax()
@never_cache
@login_required
def share(request):
  flash = ""
  current_link = None
  for model in models.Share.objects.filter(user=request.user):
    if model.is_active:
      current_link = "/todo/view/%s" % model.slug  # TODO(chandler): don't hard-code /todo
      break
  if request.POST.get('csrfmiddlewaretoken'):
    # They pressed the button.
    if current_link:
      # Atomicity doesn't matter.
      _deactivate_all_shares_for_user(request.user)
      current_link = ""
      flash = "Sharing disabled. Existing links no longer work."
    else:
      slug = immaculater.Base64RandomSlug(64)
      _create_share(request.user, slug)  # this is atomic
      current_link = "/todo/view/%s" % slug  # TODO(chandler): don't hard-code the path
      flash = "Read-only sharing enabled. Copy the link below and share it."
    if not _using_pjax(request):  # https://en.wikipedia.org/wiki/Post/Redirect/Get
      return redirect('/todo/share')  # TODO(chandler): Don't hard-code the link
  return _render(request, "share.html",
                 {"Title": "Share Your Data",
                  "CurrentLink": request.build_absolute_uri(current_link) if current_link else "",
                  "Flash": flash})


@never_cache
@login_required
def account(request):
  if request.POST.get('csrfmiddlewaretoken'):
    if request.POST.get('password1') != request.POST.get('password2'):
      return HttpResponseBadRequest("Passwords do not match.")
    if request.POST.get('password1') == request.user.username:
      return HttpResponseBadRequest("Password cannot match username.")
    if len(request.POST.get('password1')) < 8:
      return HttpResponseBadRequest("Password too short.")
    if request.POST.get('password1').lower() in ('password', 'immaculater'):
      return HttpResponseBadRequest("Password insufficiently clever.")
    request.user.set_password(request.POST.get('password1'))
    request.user.save()
    update_session_auth_hash(request, request.user)
    return redirect('home')
    # TODO(chandler): redirect to 'account' with a flash message.
  return _render(request,
                 "account.html",
                 {"Title": "Your Account"})


@djpjax.pjax()
@never_cache
@login_required
def weekly_review(request):
  template_dict = {"Flash": ""}
  _, error_page = _create_new_action(request, template_dict)
  if error_page is not None:
    return error_page
  error_page = _create_new_project(request, template_dict)
  if error_page is not None:
    return error_page
  cookie_value = _cookie_value(request)
  saved_read, error_page = _execute_cmd(request, None, template_dict, cookie_value)
  if error_page is not None:
    return error_page
  if request.method == 'POST' and not _using_pjax(request):  # https://en.wikipedia.org/wiki/Post/Redirect/Get
    response = redirect('weekly_review')
    _set_cookie(response, _COOKIE_NAME, _serialized_cookie_value(cookie_value))
    return response
  note = _apply_batch_of_commands(request.user, ['note :__weekly_review'],
                                  read_only=True, saved_read=saved_read)
  template_dict.update({"ViewFilter": cookie_value.view,
                        "Title": "Weekly Review",
                        "Note": '\n'.join(note['printed'])})
  response = _render(request, "weekly_review.html", template_dict)
  _set_cookie(response, _COOKIE_NAME, _serialized_cookie_value(cookie_value))
  return response


@djpjax.pjax()
@never_cache
@login_required
def about(request):
  return _render(request, "about.html",
                 {"Title": "About"})


@never_cache
def login(request):
  logout(request)
  d = {"Title": "Login"}
  return TemplateResponse(request, "login_with_slack.html", d)


@djpjax.pjax()
@never_cache
@login_required
def shortcuts(request):
  return _render(request, "shortcuts.html",
                 {"Title": "Keyboard Shortcuts"})


@djpjax.pjax()
@never_cache
@login_required
def help(request):
  return _render(request, "help.html",
                 {"Title": "Help",
                  "Screencast": os.environ.get("IMMACULATER_SCREENCAST", '/todo/help'),
                  "Screencast2": os.environ.get("IMMACULATER_SCREENCAST2", '/todo/help')})


def _authenticated_user_via_discord_bot_custom_auth(request):
  auth = request.META.get('HTTP_AUTHORIZATION', '').split()
  if not auth or auth[0].lower() != 'basic' or len(auth) != 2:
    raise PermissionDenied()
  try:
    userid, password = base64.b64decode(auth[1]).decode('iso-8859-1').split(':', 1)
  except (ValueError, TypeError, UnicodeDecodeError, binascii.Error):
    raise PermissionDenied()
  if userid != os.environ['IMMACULATER_DISCORD_BOT_ID']:
    raise PermissionDenied()
  if password != os.environ['IMMACULATER_DISCORD_BOT_SECRET']:
    raise PermissionDenied()
  try:
    json_data = json.loads(request.body)
  except ValueError:
    raise PermissionDenied()
  if not isinstance(json_data, dict) or 'discord_user' not in json_data:
    raise PermissionDenied()
  # Now we have discord_user=123 which had better match a SocialAccount.uid
  # value for a User that is_active.
  try:
    sa = allauth_models.SocialAccount.objects.get(
        uid=six.text_type(json_data['discord_user']),
        provider='discord')
    if not sa.user.is_active:
      raise PermissionDenied()
    return sa.user
  except ObjectDoesNotExist:
    raise PermissionDenied("FirstLoginRequired")
  raise PermissionDenied()


def _active_authenticated_user_via_jwt(request):
  if not request.is_secure() and os.environ.get('DJANGO_DEBUG') != "True":
    # We do this at a higher level with SECURE_SSL_REDIRECT, but enforce it
    # here too, just in case.
    raise PermissionDenied()  # really a 426 would be best
  auth = request.META.get('HTTP_AUTHORIZATION', '').split()
  if not auth or auth[0].lower() != 'bearer':
    return None
  if len(auth) != 2:
    raise PermissionDenied()
  try:
    auth_payload = jwt_auth_settings.JWT_DECODE_HANDLER(auth[-1])
  except pyjwt.PyJWTError:
    raise PermissionDenied()
  if not auth_payload['expiry']:
    raise PermissionDenied()
  epoch_seconds = int(auth_payload['expiry'], 10)
  if int(datetime.datetime.utcnow().strftime('%s'), 10) >= epoch_seconds:
    raise PermissionDenied()
  if not auth_payload['slug']:
    raise PermissionDenied()
  sessions = models.JwtSession.objects.filter(pk=auth_payload['slug'])
  assert len(sessions) in (0, 1)
  if not sessions:
    raise PermissionDenied()
  if sessions[0].expires_at < timezone.now():
    # TODO(chandler37): Keep statsd statistics of the number of occurrences of each of these rejection criteria.
    raise PermissionDenied()
  user_id = sessions[0].user_id
  users = User.objects.filter(pk=user_id)
  assert len(users) in (0, 1)
  if not users:
    assert not 'TODO(chandler37): here 100'
    raise PermissionDenied()
  if not users[0].is_active:
    assert not 'TODO(chandler37): here 200'
    raise PermissionDenied()
  return users[0]


def _active_authenticated_user_via_basic_auth(request):
  auth = request.META.get('HTTP_AUTHORIZATION', '').split()
  if not auth or auth[0].lower() != 'basic' or len(auth) != 2:
    raise PermissionDenied()
  try:
    userid, password = base64.b64decode(auth[1]).decode('iso-8859-1').split(':', 1)
  except (ValueError, TypeError, UnicodeDecodeError, binascii.Error):
    raise PermissionDenied()
  credentials = {
    User.USERNAME_FIELD: userid,
    'password': password
  }
  user = authenticate(request=request, **credentials)
  if user is None:  # which may be because user.is_active is False in the case of the ModelBackend
    raise PermissionDenied()
  if not user.is_active:  # but you can't be too careful...
    raise PermissionDenied()
  return user


def _username_via_slack_creds(user_id, team_id):
  # TODO(chandler): Share this code with pipelines.py:
  return team_id + ':' + user_id


# This assumes you've checked 'token' already.
def _authenticated_user_via_slack_user_and_team(user_id, team_id):
  assert user_id
  assert team_id
  our_username = _username_via_slack_creds(user_id=user_id, team_id=team_id)
  try:
    user = User.objects.get(username=our_username)
    if not user.is_active:
      raise PermissionDenied()
    return user, None
  except User.DoesNotExist:
    return None, 'To sign up, visit %s' % os.environ.get('OUR_SLACK_SIGNUP_URL', '???')


# TODO(chandler): Are we checking User.is_active everywhere?


@never_cache
@csrf_exempt
def overload_phasers(request):
  """Raises an exception to test the Sentry integration"""
  if request.method == 'POST':
    raise Exception("testing Exception")
  if request.method == 'DELETE':
    raise BaseException("testing BaseException which we will never raise...")
  try:
    raise TypeError("testing TypeError")
  except TypeError as e:
    raise IndexError("testing IndexError from TypeError") from e


@never_cache
@csrf_exempt
def api(request):
  """Because we have a CLI, our API simply accepts a list of strings.

  Example usage:

  curl -H 'Content-Type: application/json' -X POST -d '{"commands": ["sort alpha", "lsprj"]}' -u foo:bar http://127.0.0.1:5000/todo/api

  curl -X POST -d 'cmd=view needing_review' -d 'cmd=ls' -u foo:bar http://127.0.0.1:5000/todo/api

  curl -X POST -d 'cmdro=cd /inbox' -d 'cmdro=ls' -H 'Authorization:Bearer my.json.web.token' http://127.0.0.1:5000/todo/api
  """
  if request.method != 'POST':
    raise Http404()
  user = _active_authenticated_user_via_jwt(request)
  if user is None:
    user = _active_authenticated_user_via_basic_auth(request)
  assert user is not None
  read_only = False
  cmd_list = request.POST.getlist('cmdro', [])
  if cmd_list:
    read_only = True
    if request.POST.getlist('cmd', []):
      return JsonResponse({"error": "Takes one or the other but not both of cmd/cmdro"},
                          status=422)
  if not cmd_list:
    cmd_list = request.POST.getlist('cmd', [])
  if not cmd_list:
    try:
      json_data = json.loads(request.body)
    except ValueError:
      return HttpResponseBadRequest("Invalid JSON")
    if not isinstance(json_data, dict) or 'commands' not in json_data:
      return JsonResponse({"error": "Needed a dict containing the key 'commands'"},
                          status=422)
    if not isinstance(json_data['commands'], list):
      return JsonResponse({"error": "commands must be an array of strings"},
                          status=422)
    for c in json_data['commands']:
      if not isinstance(c, six.string_types):
        return JsonResponse({"error": "commands must be an array of strings"},
                            status=422)
    cmd_list = json_data['commands']
    if 'read_only' in json_data:
      if json_data['read_only'] in (True, False):
        read_only = json_data['read_only']
      else:
        if isinstance(json_data['read_only'], six.string_types):
          read_only = json_data['read_only'].lower() == 'true'
        else:
          return JsonResponse({"error": "read_only must be True/False/'true'/'false'"},
                              status=422)
  try:
    results = _apply_batch_of_commands(user, cmd_list, read_only=read_only)
    return JsonResponse({'pwd': results['pwd'],
                         'printed': results['printed'],
                         'view': results['view']})
  except immaculater.Error as error:
    return JsonResponse({'immaculater_error': six.text_type(error)}, status=422)


@never_cache
@csrf_exempt
def create_jwt(request):
  """`create_jwt` is how you trade a username and password for a JSON Web Token (JWT)."""
  if request.method != 'POST':
    raise Http404()
  if not request.is_secure() and os.environ.get('DJANGO_DEBUG') != "True":
    # We do this at a higher level with SECURE_SSL_REDIRECT, but enforce it here too, just in case. TODO(chandler37):
    # DRY this up with mergeprotobufs via a decorator.
    return JsonResponse({"error": "Use https, not http"},
                        status=426)
  user = _active_authenticated_user_via_basic_auth(request)
  # Now create the row in jwt_session:
  encoder = jwt_auth_settings.JWT_ENCODE_HANDLER
  token = encoder(jwt.jwt_payload_handler(user))
  return JsonResponse({"token": token}, status=201)


def _is_valid_sha1_checksum(s):
  return re.match(r'^[0-9a-f]{40}$', s)


def _parse_mergeprotobufs_request(request):
  """mergeprotobufs helper returning a 2-tuple (None|pyatdl_pb2.MergeToDoListRequest, None|HttpResponse)."""
  if request.content_type != MERGETODOLISTREQUEST_CONTENT_TYPE and request.content_type != MERGETODOLISTREQUEST_CONTENT_TYPE.split(';', 1)[0]:
    msg = "Content type provided is %s instead of %s" % (
        request.content_type,
        MERGETODOLISTREQUEST_CONTENT_TYPE)
    return None, JsonResponse({"error": msg}, status=415)  # Unsupported Media Type
  try:
    req = pyatdl_pb2.MergeToDoListRequest.FromString(request.body)
  except message.Error as e:
    _debug_log('MergeToDoListRequest message.Error %s' % six.text_type(e))
    return None, JsonResponse({"error": "Could not parse pyatdl.MergeToDoListRequest"},
                              status=400)
  if req.sanity_check != MERGETODOLISTREQUEST_SANITY_CHECK:
    return None, JsonResponse({"error": "Got a valid MergeToDoListRequest but sanity_check was %s" % req.sanity_check},
                              status=422)
  if req.previous_sha1_checksum and req.new_data:
    return None, JsonResponse({"error": "new data should not be based on a previous checksum %s" % req.previous_sha1_checksum},
                              status=422)
  if req.new_data and not req.latest.sha1_checksum:
    return None, JsonResponse({"error": "new data should come with req.latest.sha1_checksum"},
                              status=422)
  if req.previous_sha1_checksum and req.previous_sha1_checksum == req.latest.sha1_checksum:
    return None, JsonResponse({"error": "req.previous_sha1_checksum equals req.latest.sha1_checksum which means you are just asking for changes from other devices, I presume, since nothing changed on your end. The only way to ask for that is to omit the 'latest' field which saves network bandwidth."},
                              status=409)
  if req.latest.payload_is_zlib_compressed:
    return None, JsonResponse({"error": "req.latest.payload_is_zlib_compressed is true which is unsupported because we have HTTP compression available to us."},
                              status=409)
  sha1_format_error = "is the wrong length or not hexadecimal"
  if req.previous_sha1_checksum and not _is_valid_sha1_checksum(req.previous_sha1_checksum):
    return None, JsonResponse({"error": "previous_sha1 %s" % sha1_format_error},
                              status=422)
  if req.latest.sha1_checksum and not _is_valid_sha1_checksum(req.latest.sha1_checksum):
    return None, JsonResponse({"error": "latest.sha1_checksum %s" % sha1_format_error},
                              status=422)
  if req.latest.payload and not req.latest.sha1_checksum:
    return None, JsonResponse({"error": "latest.payload given but latest.sha1_checksum absent"},
                              status=422)
  if len(req.latest.payload) != req.latest.payload_length:
    return None, JsonResponse({"error": "len(latest.payload)=%s but latest.payload_length=%s" % (len(req.latest.payload), req.latest.payload_length)},
                              status=422)
  if req.latest.sha1_checksum:
    if not req.latest.payload:
      return None, JsonResponse({"error": "req.latest.sha1_checksum given but req.latest.payload is missing"},
                                status=422)
    # TODO(chandler37): verify req.latest.sha1_checksum optionally to save a few CPU cycles?
    real_sum = serialization.Sha1Checksum(req.latest.payload)
    if real_sum != req.latest.sha1_checksum:
      return None, JsonResponse({"error": "SHA1(latest.payload)=%s mismatches with latest.sha1_checksum=%s" % (real_sum, req.latest.sha1_checksum)},
                                status=422)
  return req, None


def _write_database(user, some_bytes, sha1_checksum):
  # TODO(chandler37): As a huge performance optimization, we must write the
  # sha1 checksum too. Let's write it to a separate column and query not the
  # entire row but just that column. A separate table would work too if django
  # is hard to convince to read just part of a row because we use transactions.
  SerializationWriter('write', user, None).write(some_bytes)


def _read_database(user, sha1_checksum):
  """Returns {"tdl":None|tdl.ToDoList, "sha1":None|str, "they_have_the_latest":bool}; raises serialization.DeserializationError"""
  # TODO(chandler37): After making the "huge performance optimization" in
  # _write_database, change this function too. Stop reading the ToDoList data
  # from the database if sha1_checksum is present and matches the database.
  reader = SerializationReader(user)
  sha1_checksum_list = []
  a_tdl = serialization.DeserializeToDoList2(
      reader,
      tdl_factory=None,
      sha1_checksum_list=sha1_checksum_list)
  assert len(sha1_checksum_list) <= 1, sha1_checksum_list
  result = {
    "tdl": a_tdl,
    "sha1": sha1_checksum_list[0] if sha1_checksum_list else None,
    "they_have_the_latest": bool(sha1_checksum_list and sha1_checksum_list[0] == sha1_checksum)
  }
  return result


@never_cache
@csrf_exempt
def mergeprotobufs(request):
  """`mergeprotobufs` (which can merely read or merely write as well) receives
  an octet-stream that is a pyatdl.MergeToDoListRequest and returns various
  HTML and JSON errors or an HTTP 200 with an octet-stream that is a
  pyatdl.MergeToDoListResponse which will contain a wrapped pyatdl.ToDoList
  when and only when the to-do list has been modified since your app last saw
  it by another app (probably on another device).

  This API is the heart of how a desktop app, smartphone app or a
  single-page web application (SPA) (e.g., using React+Redux,
  https://webdev.dartlang.org/angular, https://angular.io/, or Vue.js)
  interacts with the database.

  This API accepts an optional ToDoList and the SHA1 hash of the starting point
  and merges it with the latest ToDoList in the database. It returns the merged
  data if there were changes on other devices (no reason to send back the
  identical data otherwise) along with an SHA1 hash that becomes part of your
  request the next time you call this API. It always returns HTTP 200 upon
  success, returning a binary protobuf of type pyatdl.ChecksumAndData.

  The SHA1 checksum serves two purposes:

  1) It makes certain that the transport layer didn't fail us -- we compute the
  same checksum server-side and abort if your checksum does not match our
  checksum of your "payload" which is a serialized (binary) protobuf of type
  pyatdl.ToDoList that is optionally gzip-compressed if
  pyatdl.ChecksumAndData.payload_is_zlib_compressed is true (defaults to
  false). We do not recommend such compression at this level because
  compression, if valuable, is possible at the level of HTTP (via RFC 2616's
  'gzip', 'deflate', 'compress', etc.). This paranoia about data corruption
  comes at a cost, and you may wish to disable it. But there's still value in
  this hash because of the following: (TODO(chandler37): make it configurable
  that we skip verifying the hash as a performance win.)

  2) It allows us to avoid merging in the common case that no merge is required
  because only your app has made any changes. When combined with the length,
  hash collisions are so unlikely (and, thanks to the use of a cryptographic
  hash, very expensive to create artifically by attackers) that we can use a
  SHA1 checksum as a unique identifier for a pyatdl.ToDoList and thus can tell
  that you are trying to save changes to version V and are the only one who has
  made changes since V because V is the most recent version in our database. We
  then short circuit the merge and simply accept your changes as version V+1
  and write them to the database along with the SHA1 checksum.

  TODO(chandler37): check length too and even check byte by byte in paranoid
  mode.

  TODO(chandler37): talk about SHA1's brokenness -- soon it won't be that
  expensive to construct artificial collisions (even with the same length, I
  assume). Then explain how our threat model means that we don't care (because
  only you, authenticated by username and password or a JWT that came from
  username and password, can modify your data). Since we don't care, we should
  be using something faster.  TODO(chandler37): Use a cheaper hash/PRF
  e.g. SipHash or HighwayHash (https://arxiv.org/abs/1612.06257) or crc32 or
  md5 or ...

  Imagine you write a Flutter smartphone app. Flutter uses Dart. Dart has
  protocol messages a.k.a. protocol buffers a.k.a. protobufs. See here:
  https://pub.dartlang.org/packages/protobuf. So you can use pyatdl.ToDoList to
  represent the data on the smartphone app and then use pyatdl.ChecksumAndData
  to transmit it to this API. You disallow any updates as you wait for this
  API's result (or you might write them to a side log you can replay against
  the result obtained from this API). You then replace your data structure with
  the merged data structure (or the merged data structure plus any replayed
  events from your side log).

  In this way a user can interact via the Discord and Slack APIs, via SPAs, via
  this django classic-web-architecture web app, via a desktop app, and via your
  new smartphone app, all simultaneously. Changes will be merged. Additions are
  straightforward except in the exceptionally rare case that two devices picked
  the same 64-bit pseudorandom number for a UID (you'd expect your first such
  collision after roughly the square root of 2**64 (a few billion) items were
  created) (e.g., the smartphone app has added Action 3145957813018432511 "buy
  soymilk" and the django app has added Project 3145957813018432511 "replace
  wifi router").

  TODO(chandler37): return max mtime/ctime or current server time so that the
  client can make sure their clock isn't terribly off.

  TODO(chandler37): verify that incoming timestamps are sane.

  Deletions are trickier because we must preserve the object's UID (but we can
  delete the data like "buy soymilk") and indicate that it was deleted so this
  server can delete the data. TODO(chandler37): Add an API that truly deletes
  deleted items, to be used only when all devices are known to be in sync.

  You might wonder why one would need an SPA. This django app is a web
  application, after all. It uses PJAX (pushState+AJAX), but it's still classic
  web architecture. Any operation the user performs waits on the AJAX request
  to finish and the browser to replace part of the page and render the
  change. If the server is slow, that could mean waiting two seconds to see the
  checkbox appear to be checked. And if you press that checkbox or alter that
  drop-down with text inside the 'capture new action' box, that text will be
  lost when the browser renders. An SPA is a much better UX especially if the
  server is slow (perhaps because you're running Immaculater in only one
  datacenter and the user is far away).

  You might also wonder why the app would want to use this type of API instead
  of a full REST API for Actions, Projects, Contexts, Folders, etc. That's
  simple: Use the right tool for the job. Since a human being's personal to-do
  list fits nicely in a single HTTP request, just make one request. Then you
  don't have to worry about doing additions, deletions, etc. in a piecemeal
  fashion. This merge is all-or-nothing.

  TODO(chandler37): Allow specifying whether the output should be
  zlib-compressed (which level? 2? 7? 9?). Perhaps have an 'auto' level that
  compresses only when the data is large enough that it might save a packet.

  Example usage:

  curl -X POST --data-binary @localfile.MergeToDoListRequest.binaryproto -u foo:bar http://127.0.0.1:5000/todo/mergeprotobufs

  TODO(chandler37): Preserve unknown protobuf tags (future data). [For now you
  have to change this django server first (and not just to see your tag, but to
  copy it over) because we reserve the right to pluck out only the tags we know
  about, discarding your extensions.]

  TODO(chandler37): test when we return no protobuf, indicating that what you
  sent us is fully up to date (no merging was done). Test this with a
  pyatdl.ToDoList as input and without (which is a request a frontend might
  make to stay in sync with other devices' changes).
  """
  # TODO(chandler37): create an audit log so the user can see "oh i synced an
  # hour ago from Device D", perhaps with a summary of changes.
  if request.method != 'POST':
    raise Http404()
  if not request.is_secure() and os.environ.get('DJANGO_DEBUG') != "True":
    # We do this at a higher level with SECURE_SSL_REDIRECT, but enforce it
    # here too, just in case.
    return JsonResponse({"error": "Use https, not http"},
                        status=426)
  user = _active_authenticated_user_via_jwt(request)
  if user is None:
    user = _active_authenticated_user_via_basic_auth(request)

  pbreq, error_response = _parse_mergeprotobufs_request(request)
  assert pbreq is None or error_response is None
  assert pbreq is not None or error_response is not None
  if error_response:
    return error_response

  if pbreq.HasField('latest'):
    actual_cksum = serialization.Sha1Checksum(pbreq.latest.payload)
    if actual_cksum != pbreq.latest.sha1_checksum:
      return JsonResponse({"error": f"request.latest.sha1_checksum={pbreq.latest.sha1_checksum} mismatches with {actual_cksum}"},
                          status=422)

  try:
    read_result = _read_database(user, pbreq.latest.sha1_checksum)
  except serialization.DeserializationError:
    return JsonResponse(
        {"error": "Cannot read existing to-do list from the database!"},
        status=500)

  if read_result["they_have_the_latest"]:
    return HttpResponse(status=204)  # you are in sync

  if read_result["tdl"] is not None and pbreq.new_data:
    return JsonResponse(
        {"error": "You set the new_data bit, but there is already a to-do list in the database. Maybe we should overwrite it? Maybe we should do a potentially ugly merge (ugly because two or more applications are competing to get the user started)? For now we abort and await your pull request."},
        status=409)  # CONFLICT

  pbresponse = pyatdl_pb2.MergeToDoListResponse()
  pbresponse.sanity_check = 18369614221190021342

  def protobuf_response():
    serialized_result = pbresponse.SerializeToString()
    hr = HttpResponse(serialized_result)
    # The following seems better than application/octet-stream and is supported
    # by some debugging proxies:
    hr['Content-Type'] = 'application/x-protobuf; messageType="pyatdl.MergeToDoListResponse"'
    hr['Content-Length'] = len(serialized_result)  # TODO(chandler37): needed?
    hr['Content-Transfer-Encoding'] = 'binary'
    return hr

  def write_db(bytes_of_pyatdl_todolist):
    """Returns sha1_checksum of (uncompressed) pyatdl.ToDoList. Raises ReserializationError."""
    # First, make sure it's valid input and not so large that we run out of memory (MemoryError).
    # NOTE: exception_middleware deals with any pyatdllib.core.errors.DataError gracefully. This is *not* dead code:
    uid.ResetNotesOfExistingUIDs(raise_data_error_upon_next_uid=True)  # let the error propagate
    deserialized_tdl = tdl.ToDoList.DeserializedProtobuf(bytes_of_pyatdl_todolist)
    deserialized_tdl.CheckIsWellFormed()
    deserialized_tdl.AsProto().SerializeToString()

    # No exception was raised, so let's proceed:
    cksum = serialization.Sha1Checksum(bytes_of_pyatdl_todolist)
    _write_database(
      user,
      serialization.SerializedWithChecksum(bytes_of_pyatdl_todolist),
      cksum)
    return cksum

  if read_result["tdl"] is None:
    if pbreq.HasField('latest'):  # We must merge with nothing. We write latest to the DB.
      if pbreq.new_data:
        cksum = write_db(pbreq.latest.payload)
        assert pbreq.latest.sha1_checksum == cksum, f'Checksum mismatch after writing to the database; this is not terrible thanks to ATOMIC_REQUESTS which will roll back the so-called write: req.sha1={pbreq.latest.sha1_checksum} db={cksum}'
        pbresponse.sha1_checksum = pbreq.latest.sha1_checksum
        # Leave pbresponse.to_do_list unset for performance reasons. (If this
        # complicates some apps, then we can add a boolean to
        # MergeToDoListRequest to be verbose.)
        return protobuf_response()
      return JsonResponse({"error": "This backend has no to-do list. You passed one in but did not set the 'new_data' boolean to true. We are aborting out of an abundance of caution. You might wish to call this API once with different arguments to trigger the creation of the default to-do list for new users."},
                          status=409)
    assert not pbreq.new_data
    new_tdl = uicmd.NewToDoList()
    new_tdl.CheckIsWellFormed()
    pbresponse.starter_template = True
    serialized_tdl = new_tdl.AsProto(pb=pbresponse.to_do_list).SerializeToString()  # AsProto returns its argument
    uid.ResetNotesOfExistingUIDs(raise_data_error_upon_next_uid=True)
    deserialized_tdl = tdl.ToDoList.DeserializedProtobuf(serialized_tdl)
    deserialized_tdl.CheckIsWellFormed()
    reserialized_tdl = deserialized_tdl.AsProto().SerializeToString()
    if serialized_tdl != reserialized_tdl:
      raise AssertionError(
        'Cannot round trip starter template. This is not a key constraint but clients will find it easier if they can '
        'get back the same thing with the same sha1_checksum the next time they read.')
    pbresponse.sha1_checksum = write_db(serialized_tdl)
    return protobuf_response()

  if pbreq.HasField('latest'):
    try:
      deserialized_latest = pyatdl_pb2.ToDoList.FromString(pbreq.latest.payload)
    except message.Error as e:
      return JsonResponse({"error": "The given to-do list did not serialize. Hint: %s" % str(e)},  # TODO(chandler37): test
                          status=409)
    if pbreq.previous_sha1_checksum or pbreq.overwrite_instead_of_merge:
      # TODO(chandler37): See comments in _write_database regarding performance optimizations from storing SHA1
      # checksums in the database.
      if pbreq.overwrite_instead_of_merge or pbreq.previous_sha1_checksum == read_result["sha1"]:  # yes, read_result["sha1"] is for the uncompressed pyatdl.ToDoList
        cksum = write_db(pbreq.latest.payload)
        pbresponse.sha1_checksum = pbreq.latest.sha1_checksum
        assert pbreq.latest.sha1_checksum == cksum, f'Checksum mismatch after writing to the database; this is not terrible thanks to ATOMIC_REQUESTS which will roll back the so-called write: req.sha1={pbreq.latest.sha1_checksum} db={cksum}'
        assert not pbresponse.HasField('to_do_list')
        assert not pbresponse.HasField('starter_template')
        return protobuf_response()
      else:
        pass  # we must merge, fall through...
    # It does not match what is in the db; we must merge. If a client has a very old to-do list, merging could
    # resurrect anything that has been purged. TODO(chandler37): Think about Lamport clocks and vector clocks and design a truly paranoid system, perhaps one that worked like 'git rebase'.
    if pbreq.abort_if_merge_is_required:
      errmsg = ''.join(f"""
The server needs to merge, but you set abort_if_merge_is_required to true, so we are aborting.
 Merging is required because the sha1_checksum of the todolist prior to your input is
 {pbreq.previous_sha1_checksum!r} and the sha1_checksum of the database is
 {read_result["sha1"]!r}
""".split('\n')).strip()
      return JsonResponse({"error": errmsg}, status=409)
    error_quickly = True
    if error_quickly:
      errmsg = ''.join(f"""
The server does not yet implement merging, but merging is
 required because the sha1_checksum of the todolist prior to your input is
 {pbreq.previous_sha1_checksum!r} and the sha1_checksum of the database is
 {read_result["sha1"]!r}
""".split('\n')).strip()
      return JsonResponse({"error": errmsg}, status=500)
    # DEAD CODE... until we implement Merge:
    merged_tdl_pb = Merge(read_result["tdl"], deserialized_latest)
    pbresponse.sha1_checksum = write_db(merged_tdl_pb.SerializeToString())
    assert pbresponse.sha1_checksum and len(pbresponse.sha1_checksum) == 40, f'pbresponse.sha1_checksum={pbresponse.sha1_checksum}'
    assert len(pbresponse.sha1_checksum) == 40, pbresponse.sha1_checksum
    pbresponse.to_do_list.CopyFrom(merged_tdl_pb)
    return protobuf_response()
  assert len(read_result["sha1"]) == 40, read_result["sha1"]
  pbresponse.sha1_checksum = read_result["sha1"]
  read_result["tdl"].AsProto(pb=pbresponse.to_do_list)
  return protobuf_response()


@never_cache
@csrf_exempt
def discordapi(request):
  """Like /api but only for use by the immaculater-discord-bot Discord bot."""
  if request.method != 'POST':
    raise Http404()
  user = _authenticated_user_via_discord_bot_custom_auth(request)
  assert user is not None
  try:
    json_data = json.loads(request.body)
  except ValueError:
    return HttpResponseBadRequest("Invalid JSON")
  if not isinstance(json_data, dict) or 'commands' not in json_data:
    return JsonResponse({"error": "Needed a dict containing the key 'commands'"},
                        status=422)
  if not isinstance(json_data['commands'], list):
    return JsonResponse({"error": "commands must be an array of strings"},
                        status=422)
  for c in json_data['commands']:
    if not isinstance(c, six.string_types):
      return JsonResponse({"error": "commands must be an array of strings"},
                          status=422)
  cmd_list = json_data['commands']
  read_only = False
  if 'read_only' in json_data:
    if json_data['read_only'] in (True, False):
      read_only = json_data['read_only']
    else:
      if isinstance(json_data['read_only'], six.string_types):
        read_only = json_data['read_only'].lower() == 'true'
      else:
        return JsonResponse({"error": "read_only must be True/False/'true'/'false'"},
                            status=422)
  try:
    results = _apply_batch_of_commands(user, cmd_list, read_only=read_only)
    return JsonResponse({'pwd': results['pwd'],
                         'printed': results['printed'],
                         'view': results['view']})
  except immaculater.Error as error:
    return JsonResponse({'immaculater_error': six.text_type(error)}, status=422)


def _slackapi(request):
  _debug_log('POST is %s' % six.text_type(request.POST))
  user, sign_up_message = _authenticated_user_via_slack_user_and_team(
    user_id=request.POST.get('user_id'),
    team_id=request.POST.get('team_id'))
  if user is not None:
    _debug_log('we have a user')
  else:
    return HttpResponse(sign_up_message, content_type="text/plain")
  cmd = request.POST.get('text')
  if not cmd:
    cmd = 'help'
  try:
    results = _apply_batch_of_commands(user, [cmd], read_only=False)
    _debug_log('we have a batch')
    return HttpResponse("\n".join(results['printed']) if results['printed'] else 'Command succeeded.',
                        content_type="text/plain")
  except immaculater.Error as error:
    _debug_log('we have an error')
    return HttpResponse(six.text_type(error), content_type="text/plain")


@never_cache
@csrf_exempt
def slackapi(request):
  """Slack integration experimentation."""
  if request.method != 'POST':
    raise Http404()
  assert os.environ['SLACK_VERIFICATION_TOKEN']
  if os.environ['SLACK_VERIFICATION_TOKEN'] != request.POST.get('token', ''):
    raise PermissionDenied()
  if request.POST.get('ssl_check', '') == '1':
    return HttpResponse("")
  if 'SLACK_TEAMS_ALLOWED' in os.environ:
    allowed_teams = os.environ['SLACK_TEAMS_ALLOWED'].split(',')
    if request.POST.get('team_id', '') not in allowed_teams:
      raise PermissionDenied()
  return _slackapi(request)


immaculater.InitFlags()


# TODO(chandler): unittest csrf protection. The token is present in the source? And
# are we making sure it's present in the input? To test manually, in Chrome's
# developer tools edit the HTML to have a bad or missing token.

# TODO(chandler): the error page says 'refresh to proceed' but consider using a
# flash message instead.

# TODO(chandler): Consider
# https://github.com/brightinteractive/django-encrypted-cookie-session for
# encrypting the session cookie (it is signed but not encrypted) and use JSON,
# not Pickle, serialization for better security. I don't think we need this
# because the session cookie's value is just a single large integer used as a
# key in our database, but make sure.

# TOOD(chandler): Write a cron job that calls django's clearsessions.

# TODO(chandler): Logging out gives the following error:
# Internal Server Error: /todo/
# Traceback (most recent call last):
#   File "immaculater/venv/lib/python2.7/site-packages/django/core/handlers/exception.py", line 41, in inner
#     response = get_response(request)
#   File "immaculater/venv/lib/python2.7/site-packages/django/core/handlers/base.py", line 187, in _get_response
#     response = self.process_exception_by_middleware(e, request)
#   File "immaculater/venv/lib/python2.7/site-packages/django/core/handlers/base.py", line 185, in _get_response
#     response = wrapped_callback(request, *callback_args, **callback_kwargs)
#   File "immaculater/third_party/django_pjax/djpjax.py", line 39, in _view
#     resp.template_name = _pjaxify_template_var(resp.template_name)
# AttributeError: 'HttpResponseRedirect' object has no attribute 'template_name'

# TODO(chandler37): https://github.com/chandler37/immaculater/issues/55: The
# notes fields can become large, so let's store only the first, say, 256 bytes
# of the note in pyatdl.proto and store links to the complete larger items
# which will live in a new database table.
