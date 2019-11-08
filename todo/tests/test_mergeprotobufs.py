# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import base64
import random
import time

import pytest

from google.protobuf import text_format
from django.test import TestCase, modify_settings
from django.test.client import Client
from django.contrib.auth.models import User
from pyatdllib.core import pyatdl_pb2
from pyatdllib.ui import serialization
from todo import models
from todo import views

# TODO(chandler37): test admin_client, client, invalid password, unknown user, ...


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

    def tearDown(self):
        time.time = self._saved_time

    def _populate_todolist(self):
        self.tdl_model = models.ToDoList(user=self.user,
                                         contents=b'',
                                         encrypted_contents=None,
                                         encrypted_contents2=None)
        self.tdl_model.save()
        self.tdl_model.encrypted_contents2 = self._encrypted_contents_of_known_existing_protobuf()
        self.tdl_model.contents = b''
        self.tdl_model.save()

    def _existing_todolist_protobuf(self):
        pb = pyatdl_pb2.ToDoList()
        pb.ctx_list.common.uid = -1
        pb.ctx_list.common.metadata.name = "We ❤ Contexts"
        pb.ctx_list.common.timestamp.ctime = 1500000000000000
        pb.ctx_list.common.timestamp.dtime = -1
        pb.ctx_list.common.timestamp.mtime = 1500000000000000
        pb.root.common.uid = 2
        pb.inbox.common.uid = 1
        a = pb.inbox.actions.add()
        a.common.metadata.name = "increase the tests' branch coverage"
        a.common.uid = -42
        assert text_format.MessageToString(pb) == r"""
inbox {
  common {
    uid: 1
  }
  actions {
    common {
      metadata {
        name: "increase the tests\' branch coverage"
      }
      uid: -42
    }
  }
}
root {
  common {
    uid: 2
  }
}
ctx_list {
  common {
    timestamp {
      ctime: 1500000000000000
      dtime: -1
      mtime: 1500000000000000
    }
    metadata {
      name: "We \342\235\244 Contexts"
    }
    uid: -1
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
        assert response.content == b'<h1>403 Forbidden</h1>\n\n'
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

    def test_post_existing_user_but_inactive(self):
        self._populate_todolist()
        self.user.is_active = False
        self.user.save()
        response = self.client.post('/todo/mergeprotobufs', **self.auth_headers)
        assert response.status_code == 403

    def test_post_existing_user_bad_contenttype(self):
        self._populate_todolist()
        response = self.client.post('/todo/mergeprotobufs', **self.auth_headers)
        assert response.content == rb'''{"error": "Content type provided is multipart/form-data instead of application/x-protobuf; messageType=\"pyatdl.MergeToDoListRequest\""}'''
        assert response.status_code == 415

    def test_post_existing_user_insane(self):
        self._populate_todolist()
        response = self._happy_post(b'insane value')
        assert response.content == b'{"error": "Got a valid MergeToDoListRequest but sanity_check was 0"}'
        assert response.status_code == 422

    def test_post_existing_user(self):
        self._populate_todolist()
        req = pyatdl_pb2.MergeToDoListRequest()
        req.sanity_check = views.MERGETODOLISTREQUEST_SANITY_CHECK
        response = self._happy_post(req.SerializeToString())
        assert response.status_code == 200
        pbresp = pyatdl_pb2.MergeToDoListResponse.FromString(response.content)
        assert not pbresp.starter_template
        assert text_format.MessageToString(pbresp) == r"""
sha1_checksum: "32d20be5b6e144d5b665e5690310a0e92ddd70e3"
to_do_list {
  inbox {
    common {
      is_deleted: false
      timestamp {
        ctime: 0
        dtime: 0
        mtime: 0
      }
      metadata {
        name: ""
      }
      uid: 1
    }
    is_complete: false
    is_active: false
    actions {
      common {
        is_deleted: false
        timestamp {
          ctime: 0
          dtime: 0
          mtime: 0
        }
        metadata {
          name: "increase the tests\' branch coverage"
        }
        uid: -42
      }
      is_complete: false
    }
  }
  root {
    common {
      is_deleted: false
      timestamp {
        ctime: 0
        dtime: 0
        mtime: 0
      }
      metadata {
        name: ""
      }
      uid: 2
    }
  }
  ctx_list {
    common {
      is_deleted: false
      timestamp {
        ctime: 1500000000000000
        dtime: -1
        mtime: 1500000000000000
      }
      metadata {
        name: "We \342\235\244 Contexts"
      }
      uid: -1
    }
  }
}
sanity_check: 18369614221190021342
""".lstrip()

    def test_post_existing_user_but_requires_merge(self):
        self._populate_todolist()
        req = pyatdl_pb2.MergeToDoListRequest()
        req.sanity_check = views.MERGETODOLISTREQUEST_SANITY_CHECK
        pb = self._existing_todolist_protobuf()
        a = pb.inbox.actions.add()
        a.common.metadata.name = "testing10013"
        a.common.uid = 373737
        req.latest.CopyFrom(self._cksum(pb))
        req.previous_sha1_checksum = "37" * 20
        response = self._happy_post(req.SerializeToString())
        assert response.status_code == 500
        assert response.content == b'{"error": "The server does not yet implement merging, but merging is required because the sha1_checksum of the todolist prior to your input is \'3737373737373737373737373737373737373737\' and the sha1_checksum of the database is \'32d20be5b6e144d5b665e5690310a0e92ddd70e3\'"}'

    @modify_settings(MIDDLEWARE={
        'prepend': 'todo.middleware.exception_middleware.ExceptionMiddleware',
    })
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
        assert response.content == b'{"error": "The given to-do list is ill-formed: A UID is missing from or explicitly zero in the protocol buffer!"}'

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
        assert response.content == b'{"error": "This backend has no to-do list. You passed one in but did not set the \'new_data\' boolean to true. We are aborting out of an abundance of caution. You might wish to call this API once with different arguments to trigger the creation of the default to-do list for new users."}'

    def test_post_new_user_setting_new_data(self):
        # The database has no to-do list yet.
        req = pyatdl_pb2.MergeToDoListRequest()
        req.sanity_check = views.MERGETODOLISTREQUEST_SANITY_CHECK
        response = self._happy_post(req.SerializeToString())
        assert response.status_code == 200, 'response.content is %s' % response.content
        pbresp = pyatdl_pb2.MergeToDoListResponse.FromString(response.content)
        assert text_format.MessageToString(pbresp) == r"""
sha1_checksum: "b2f2761dc24359cace7809eaf7cb0e1cf9c3f05e"
to_do_list {
  inbox {
    common {
      is_deleted: false
      timestamp {
        ctime: 37000037
        dtime: -1
        mtime: 37000037
      }
      metadata {
        name: "inbox"
      }
      uid: 1
    }
    is_complete: false
    is_active: true
  }
  root {
    common {
      is_deleted: false
      timestamp {
        ctime: 37000037
        dtime: -1
        mtime: 37000037
      }
      metadata {
        name: ""
      }
      uid: 2
    }
    projects {
      common {
        is_deleted: false
        timestamp {
          ctime: 37000037
          dtime: -1
          mtime: 37000037
        }
        metadata {
          name: "miscellaneous"
        }
        uid: 8677894846078606063
      }
      is_complete: false
      is_active: true
    }
    projects {
      common {
        is_deleted: false
        timestamp {
          ctime: 37000037
          dtime: -1
          mtime: 37000037
        }
        metadata {
          name: "learn how to use this to-do list"
        }
        uid: 95864267963049347
      }
      is_complete: false
      is_active: true
      actions {
        common {
          is_deleted: false
          timestamp {
            ctime: 37000037
            dtime: -1
            mtime: 37000037
          }
          metadata {
            name: "Watch the video on the \"Help\" page -- find it on the top navigation bar"
          }
          uid: -9061335006543989703
        }
        is_complete: false
      }
      actions {
        common {
          is_deleted: false
          timestamp {
            ctime: 37000037
            dtime: -1
            mtime: 37000037
          }
          metadata {
            name: "Read the book \"Getting Things Done\" by David Allen"
          }
          uid: -5075438498450816768
        }
        is_complete: false
      }
      actions {
        common {
          is_deleted: false
          timestamp {
            ctime: 37000037
            dtime: -1
            mtime: 37000037
          }
          metadata {
            name: "After reading the book, try out a Weekly Review -- on the top navigation bar, find it underneath the \"Other\" drop-down"
          }
          uid: 4206351632466587494
        }
        is_complete: false
      }
    }
  }
  ctx_list {
    common {
      is_deleted: false
      timestamp {
        ctime: 37000037
        dtime: -1
        mtime: 37000037
      }
      metadata {
        name: "Contexts"
      }
      uid: 1987761140110186971
    }
    contexts {
      common {
        is_deleted: false
        timestamp {
          ctime: 37000037
          dtime: -1
          mtime: 37000037
        }
        metadata {
          name: "@computer"
        }
        uid: 277028180750618930
      }
      is_active: true
    }
    contexts {
      common {
        is_deleted: false
        timestamp {
          ctime: 37000037
          dtime: -1
          mtime: 37000037
        }
        metadata {
          name: "@phone"
        }
        uid: 8923216991658685487
      }
      is_active: true
    }
    contexts {
      common {
        is_deleted: false
        timestamp {
          ctime: 37000037
          dtime: -1
          mtime: 37000037
        }
        metadata {
          name: "@home"
        }
        uid: 7844860928174339221
      }
      is_active: true
    }
    contexts {
      common {
        is_deleted: false
        timestamp {
          ctime: 37000037
          dtime: -1
          mtime: 37000037
        }
        metadata {
          name: "@work"
        }
        uid: 4355858073736897916
      }
      is_active: true
    }
    contexts {
      common {
        is_deleted: false
        timestamp {
          ctime: 37000037
          dtime: -1
          mtime: 37000037
        }
        metadata {
          name: "@the store"
        }
        uid: -8310047117500551536
      }
      is_active: true
    }
    contexts {
      common {
        is_deleted: false
        timestamp {
          ctime: 37000037
          dtime: -1
          mtime: 37000037
        }
        metadata {
          name: "@someday/maybe"
        }
        uid: 7926615695106819409
      }
      is_active: false
    }
    contexts {
      common {
        is_deleted: false
        timestamp {
          ctime: 37000037
          dtime: -1
          mtime: 37000037
        }
        metadata {
          name: "@waiting for"
        }
        uid: 3780713555715847339
      }
      is_active: false
    }
  }
}
starter_template: true
sanity_check: 18369614221190021342
""".lstrip()
