# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import base64
import random
import time

import pytest

from _pytest import monkeypatch as mp
from absl import flags  # type: ignore
from django.contrib.auth.models import User
from django.test import TestCase
from django.test.client import Client
from google.protobuf import text_format  # type: ignore
from pyatdllib.core import pyatdl_pb2
from pyatdllib.ui import serialization
from todo import models
from todo import views

FLAGS = flags.FLAGS

# TODO(chandler37): test admin_client, client, invalid password, unknown user, ...


@pytest.mark.usefixtures("golden_pbs")
@pytest.mark.django_db
class Mergeprotobufs(TestCase):
    def setUp(self):
        random.seed(37)
        self._saved_time = time.time
        time.time = lambda: 37.000037

        self.email = 'foo@example.com'
        self.username = 'foo'
        self.password = 'password'
        self.user = User.objects.create_user(
            self.username, self.email, self.password)
        self.client = Client()
        userpass = '%s:%s' % (self.username, self.password)
        b64 = base64.b64encode(bytes(userpass, 'utf-8'))
        self.auth_headers = {
            'HTTP_AUTHORIZATION': 'Basic %s' % b64.decode('utf-8')
        }

        # UIDs are easier to understand if they are 1,2,3,4,...
        self.mp = mp.MonkeyPatch()
        self.mp.setattr(FLAGS, 'pyatdl_randomize_uids', False)

    def tearDown(self):
        time.time = self._saved_time
        self.mp.undo()

    def _populate_todolist(self):
        self.tdl_model = models.ToDoList(user=self.user,
                                         contents=b'',
                                         encrypted_contents=None,
                                         encrypted_contents2=None)
        self.tdl_model.save()
        self.tdl_model.encrypted_contents2 = self._encrypted_contents_of_known_existing_protobuf()
        self.tdl_model.contents = b''
        self.tdl_model.save()

    def _fill_in_timestamps(self, obj) -> None:
      obj.common.timestamp.ctime = obj.common.timestamp.mtime = 1_500_000_000_000_000

    def _existing_todolist_protobuf(self):
        pb = pyatdl_pb2.ToDoList()
        pb.root.common.uid = 2
        self._fill_in_timestamps(pb.root)
        pb.inbox.common.uid = 1
        self._fill_in_timestamps(pb.inbox)
        a = pb.inbox.actions.add()
        a.common.metadata.name = "increase the tests' branch coverage"
        a.common.uid = -42
        self._fill_in_timestamps(a)
        assert text_format.MessageToString(pb) == r"""
inbox {
  common {
    timestamp {
      ctime: 1500000000000000
      mtime: 1500000000000000
    }
    uid: 1
  }
  actions {
    common {
      timestamp {
        ctime: 1500000000000000
        mtime: 1500000000000000
      }
      metadata {
        name: "increase the tests\' branch coverage"
      }
      uid: -42
    }
  }
}
root {
  common {
    timestamp {
      ctime: 1500000000000000
      mtime: 1500000000000000
    }
    uid: 2
  }
}
""".lstrip()
        return pb

    def _cksum(self, pb=None):
        if pb is None:
            pb = self._existing_todolist_protobuf()
        cksum = pyatdl_pb2.ChecksumAndData()
        cksum.payload = pb.SerializeToString()
        cksum.payload_length = len(cksum.payload)
        cksum.sha1_checksum = serialization.Sha1Checksum(cksum.payload)
        return cksum

    def _encrypted_contents_of_known_existing_protobuf(self):
        return views._encrypted_todolist_protobuf(self._cksum().SerializeToString())
        # TODO(chandler37): If we return 'ELC19191919', we should catch the
        # InvalidToken error and serve up a graceful 500.

    def _happy_post(self, data):
        return self.client.post(
            '/todo/mergeprotobufs',
            content_type=views.MERGETODOLISTREQUEST_CONTENT_TYPE,
            data=data,
            **self.auth_headers)

    def test_non_post_404s(self):
        for auth in [True, False]:
            for method in ["get", "patch", "put", "delete", "options", "trace", "head"]:
                response = getattr(self.client, method)('/todo/mergeprotobufs', **(self.auth_headers if auth else {}))
                if method == "head":
                    assert response.content == b''
                else:
                    assert response.content == b'<h1>Not Found</h1><p>The requested resource was not found on this server.</p>'
                assert response.status_code == 404

    def test_post_unauthenticated(self):
        response = self.client.post('/todo/mergeprotobufs')
        assert response.content == b'<h1>403 Forbidden</h1>\n\n  <p>missing &quot;Authorization&quot; header</p>\n\n'
        assert response.status_code == 403

    def test_post_misauthenticated(self):
        misauth_headers = {
            'HTTP_AUTHORIZATION': 'Basic oHg5SJYRHA0='  # just some YouTube video ID...
        }
        response = self.client.post('/todo/mergeprotobufs', **misauth_headers)
        assert response.content == b'<h1>403 Forbidden</h1>\n\n'
        assert response.status_code == 403

    def test_post_misauthenticated_not_base64(self):
        misauth_headers = {
            'HTTP_AUTHORIZATION': 'Basic %s:%s' % (self.username, self.password)
        }
        response = self.client.post('/todo/mergeprotobufs', **misauth_headers)
        assert response.content == b'<h1>403 Forbidden</h1>\n\n'
        assert response.status_code == 403

    def test_post_misauthenticated_terrible_jwt(self):
        misauth_headers = {
            'HTTP_AUTHORIZATION': 'Bearer x'
        }
        response = self.client.post('/todo/mergeprotobufs', **misauth_headers)
        assert response.content == b'<h1>403 Forbidden</h1>\n\n  <p>Cannot decode JSON Web Token</p>\n\n'
        assert response.status_code == 403

    def test_post_misauthenticated_sort_of_close_jwt(self):
        misauth_headers = {
            'HTTP_AUTHORIZATION': 'Bearer x.y.z'
        }
        response = self.client.post('/todo/mergeprotobufs', **misauth_headers)
        assert response.content == b'<h1>403 Forbidden</h1>\n\n  <p>Cannot decode JSON Web Token</p>\n\n'
        assert response.status_code == 403

    def test_post_existing_user_but_inactive(self):
        self._populate_todolist()
        self.user.is_active = False
        self.user.save()
        response = self.client.post('/todo/mergeprotobufs', **self.auth_headers)
        assert response.status_code == 403

    def test_post_existing_user_bad_contenttype(self):
        self._populate_todolist()
        response = self.client.post('/todo/mergeprotobufs', **self.auth_headers)
        x = (rb'{"error": "Content type provided is multipart/form-data instead of application/x-protobuf; '
             rb'messageType=\"pyatdl.MergeToDoListRequest\""}')
        assert response.content == x
        assert response.status_code == 415

    def test_post_existing_user_insane(self):
        self._populate_todolist()
        response = self._happy_post(b'insane value')
        assert response.content == b'{"error": "Got a valid MergeToDoListRequest but sanity_check was 0"}'
        assert response.status_code == 422

    def test_post_inactive_user(self):
        self._populate_todolist()
        did_it = False
        for model in User.objects.filter(pk=self.user.pk):
          model.is_active = False
          model.save()
          did_it = True
        assert did_it
        req = pyatdl_pb2.MergeToDoListRequest()
        req.sanity_check = views.MERGETODOLISTREQUEST_SANITY_CHECK
        response = self._happy_post(req.SerializeToString())
        assert response.status_code == 403
        x = (b'<h1>403 Forbidden</h1>\n\n  <p>The properly formatted &quot;Authorization&quot; header has an invalid '
             b'username or password.</p>\n\n')
        assert response.content == x

    def test_post_existing_user(self):
        self._populate_todolist()
        req = pyatdl_pb2.MergeToDoListRequest()
        req.sanity_check = views.MERGETODOLISTREQUEST_SANITY_CHECK
        response = self._happy_post(req.SerializeToString())
        assert response.status_code == 200
        pbresp = pyatdl_pb2.MergeToDoListResponse.FromString(response.content)
        assert not pbresp.starter_template
        assert text_format.MessageToString(pbresp) == type(self).golden_pb_b

    def test_post_existing_user_but_requires_merge(self):
        self._populate_todolist()
        req = pyatdl_pb2.MergeToDoListRequest()
        req.sanity_check = views.MERGETODOLISTREQUEST_SANITY_CHECK
        pb = self._existing_todolist_protobuf()
        a = pb.inbox.actions.add()
        a.common.metadata.name = "testing10013"
        a.common.timestamp.mtime = a.common.timestamp.ctime = 1_600_000_000_000_000
        time.time = lambda: a.common.timestamp.mtime / 1e6 + 42.0
        a.common.uid = 373737
        req.latest.CopyFrom(self._cksum(pb))
        req.previous_sha1_checksum = "37" * 20
        response = self._happy_post(req.SerializeToString())
        assert response.status_code == 200
        assert response.content == (b'\n(69aad0d4c9059f1bfdac46f639929cbc2d87e925\x12\xe7\x01\n\xbd\x01\n#\x08\x00'
                                    b'\x12\x1d\x08\x80\x80\xa7\xb9\xdf\x87\xd5\x02\x10\xff\xff\xff\xff'
                                    b'\xff\xff\xff\xff\xff\x01\x18\x80\x80\xa7\xb9\xdf\x87\xd5\x02 '
                                    b'\x01\x10\x00\x18\x00"W\nS\x08\x00\x12\x1d\x08\x80\x80\xa7\xb9\xdf\x87'
                                    b'\xd5\x02\x10\xff\xff\xff\xff\xff\xff\xff\xff\xff\x01\x18\x80\x80'
                                    b"\xa7\xb9\xdf\x87\xd5\x02\x1a%\n#increase the tests' branch coverage \xd6\xff"
                                    b'\xff\xff\xff\xff\xff\xff\xff\x01\x18\x00"9\n5\x08\x00\x12\x1d\x08\x80'
                                    b'\x80\x90\xbd\x90\xe6\xeb\x02\x10\xff\xff\xff\xff\xff\xff\xff\xff'
                                    b'\xff\x01\x18\x80\x80\x90\xbd\x90\xe6\xeb\x02\x1a\x0e\n\x0ctesting10013 '
                                    b'\xe9\xe7\x16\x18\x00\x12%\n#\x08\x00\x12\x1d\x08\x80\x80\xa7\xb9\xdf\x87'
                                    b'\xd5\x02\x10\xff\xff\xff\xff\xff\xff\xff\xff\xff\x01\x18\x80\x80'
                                    b'\xa7\xb9\xdf\x87\xd5\x02 \x02y\xde\xc0\xfe\xca\xce\xfa\xed\xfe')

    def test_ill_formed_input(self):
        self._populate_todolist()
        req = pyatdl_pb2.MergeToDoListRequest()
        req.sanity_check = views.MERGETODOLISTREQUEST_SANITY_CHECK
        pb = self._existing_todolist_protobuf()
        a = pb.inbox.actions.add()
        a.common.metadata.name = "testing10013"
        # SKIP a.common.uid = 373737
        req.latest.CopyFrom(self._cksum(pb))
        req.previous_sha1_checksum = self._cksum().sha1_checksum
        response = self._happy_post(req.SerializeToString())
        assert response.status_code == 422
        assert response.content == (
          b'{"error": "The given to-do list is ill-formed: A UID is missing from or explicitly zero in the protocol '
          b'buffer!"}')

    def test_post_previous_sha1_given_for_existing_user(self):
        self._populate_todolist()
        req = pyatdl_pb2.MergeToDoListRequest()
        req.sanity_check = views.MERGETODOLISTREQUEST_SANITY_CHECK
        pb = self._existing_todolist_protobuf()
        a = pb.inbox.actions.add()
        a.common.metadata.name = "testing10013"
        a.common.uid = 373737
        req.latest.CopyFrom(self._cksum(pb))
        req.previous_sha1_checksum = self._cksum().sha1_checksum
        response = self._happy_post(req.SerializeToString())
        assert response.status_code == 200
        pbresp = pyatdl_pb2.MergeToDoListResponse.FromString(response.content)
        assert not pbresp.starter_template
        assert text_format.MessageToString(pbresp) == r"""
sha1_checksum: "%s"
sanity_check: 18369614221190021342
""".lstrip() % req.latest.sha1_checksum

    def test_post_new_user_without_data_without_setting_new_data(self):
        # The database has no to-do list yet but it will create a starter template
        req = pyatdl_pb2.MergeToDoListRequest()
        req.sanity_check = views.MERGETODOLISTREQUEST_SANITY_CHECK
        response = self._happy_post(req.SerializeToString())
        assert response.status_code == 200
        pbresp = pyatdl_pb2.MergeToDoListResponse.FromString(response.content)
        assert pbresp.starter_template
        assert 'Read the book' in text_format.MessageToString(pbresp)

    def test_post_new_user_with_data_but_not_setting_new_data(self):
        # The database has no to-do list yet.
        req = pyatdl_pb2.MergeToDoListRequest()
        req.sanity_check = views.MERGETODOLISTREQUEST_SANITY_CHECK
        req.latest.CopyFrom(self._cksum())
        response = self._happy_post(req.SerializeToString())
        assert response.status_code == 409
        x = (b'{"error": "This backend has no to-do list. You passed one in but did not set the \'new_data\' boolean '
             b'to true. We are aborting out of an abundance of caution. You might wish to call this API once with different '
             b'arguments to trigger the creation of the default to-do list for new users."}')
        assert response.content == x

    def test_post_new_user_setting_new_data(self):
        # The database has no to-do list yet.
        req = pyatdl_pb2.MergeToDoListRequest()
        req.sanity_check = views.MERGETODOLISTREQUEST_SANITY_CHECK
        response = self._happy_post(req.SerializeToString())
        assert response.status_code == 200, 'response.content is %s' % response.content
        pbresp = pyatdl_pb2.MergeToDoListResponse.FromString(response.content)
        assert type(self).golden_pb_a == text_format.MessageToString(pbresp)
