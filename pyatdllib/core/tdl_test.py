"""Unittests for module 'tdl'."""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import gflags as flags

from google.protobuf import text_format

from pyatdllib.core import pyatdl_pb2
from pyatdllib.core import errors
from pyatdllib.core import tdl
from pyatdllib.core import uid
from pyatdllib.core import unitjest

FLAGS = flags.FLAGS


# pylint: disable=missing-docstring,too-many-public-methods
class TdlTestCase(unitjest.TestCase):

  def setUp(self):
    super().setUp()
    FLAGS.pyatdl_randomize_uids = False
    uid.ResetNotesOfExistingUIDs()

  def testStr(self):
    FLAGS.pyatdl_show_uid = False
    FLAGS.pyatdl_separator = '/'
    lst = tdl.ToDoList()
    self.assertEqual(lst.inbox.name, 'inbox')
    self.assertEqual(lst.root.name, '')
    self.assertEqual(lst.root.items, [])
    # pylint: disable=trailing-whitespace
    self._AssertEqualWithDiff(
      """
<todolist>
    <inbox>
        <project is_deleted="False" is_complete="False" is_active="True" name="inbox">
       \x20
        </project>
    </inbox>
    <folder is_deleted="False" name="">
   \x20
    </folder>
    <contexts>
        <context_list is_deleted="False" name="Contexts">
       \x20
        </context_list>
    </contexts>
</todolist>
""".strip().split('\n'),
      str(lst).split('\n'))

  def testSanityChecks(self):
    pb = pyatdl_pb2.ToDoList()
    text = r"""
inbox {
  common {
    is_deleted: false
    timestamp {
      ctime: 1558072527255417
      dtime: -1
      mtime: 1558072614727605
    }
    metadata {
      name: "inbox"
    }
    uid: 1
  }
  is_complete: false
  is_active: true
  actions {
    common {
      is_deleted: false
      timestamp {
    ctime: 1558072535462194
    dtime: -1
    mtime: 1558073894997626
      }
      metadata {
    name: "an action in the inbox"
      }
      uid: 16
    }
    is_complete: false
  }
  actions {
    common {
      is_deleted: true
      timestamp {
    ctime: 1558072539973506
    dtime: 1558072543767712
    mtime: 1558073894997669
      }
      metadata {
    name: "a deleted action"
      }
      uid: 17
    }
    is_complete: false
  }
  actions {
    common {
      is_deleted: false
      timestamp {
    ctime: 1558072614727515
    dtime: -1
    mtime: 1558073894997744
      }
      metadata {
    name: "an aciton in @another context"
      }
      uid: 24
    }
    is_complete: false
    ctx_uid: -13
  }
}
root {
  common {
    is_deleted: false
    timestamp {
      ctime: 1558072527255533
      dtime: -1
      mtime: 1558072645434085
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
    ctime: 1558072527260128
    dtime: -1
    mtime: 1558072527260279
      }
      metadata {
    name: "miscellaneous"
      }
      uid: 11
    }
    is_complete: false
    is_active: true
    default_context_uid: 23
  }
  projects {
    common {
      is_deleted: false
      timestamp {
    ctime: 1558072527260526
    dtime: -1
    mtime: 1558072527261958
      }
      metadata {
    name: "learn how to use this to-do list"
      }
      uid: 12
    }
    is_complete: false
    is_active: true
    actions {
      common {
    is_deleted: false
    timestamp {
      ctime: 1558072527261003
      dtime: -1
      mtime: 1558073894998007
    }
        metadata {
      name: "Watch the video on the \"Help\" page -- find it on the top navigation bar"
    }
    uid: 13
      }
      is_complete: false
    }
    actions {
      common {
    is_deleted: false
    timestamp {
      ctime: 1558072527261439
      dtime: -1
      mtime: 1558073894998047
    }
    metadata {
      name: "Read the book \"Getting Things Done\" by David Allen"
    }
    uid: 14
      }
      is_complete: false
    }
    actions {
      common {
    is_deleted: false
    timestamp {
      ctime: 1558072527261880
      dtime: -1
      mtime: 1558073894998086
    }
    metadata {
      name: "After reading the book, try out a Weekly Review -- on the top navigation bar, find it underneath the \"Other\" drop-down"
    }
    uid: 15
      }
      is_complete: false
    }
  }
  projects {
    common {
      is_deleted: false
      timestamp {
    ctime: 1558072543768081
    dtime: -1
    mtime: 1558072579717302
      }
      metadata {
    name: "prj1"
      }
      uid: 18
    }
    is_complete: false
    is_active: true
    actions {
      common {
    is_deleted: false
    timestamp {
      ctime: 1558072557082147
      dtime: -1
      mtime: 1558073894998192
    }
    metadata {
      name: "prj1act1"
    }
    uid: 19
      }
      is_complete: false
    }
    actions {
      common {
    is_deleted: false
    timestamp {
      ctime: 1558072560258077
      dtime: -1
      mtime: 1558073894998231
    }
    metadata {
      name: "prj1act2"
    }
    uid: 20
      }
      is_complete: false
    }
    actions {
      common {
    is_deleted: false
    timestamp {
      ctime: 1558072567269887
      dtime: -1
      mtime: 1558073894998268
    }
    metadata {
      name: "prj1completed"
    }
    uid: 21
      }
      is_complete: true
    }
    actions {
      common {
    is_deleted: true
    timestamp {
      ctime: 1558072579717215
      dtime: 1558072582505034
      mtime: 1558073894998306
    }
    metadata {
      name: "prj1deleted"
    }
    uid: 22
      }
      is_complete: false
    }
  }
  projects {
    common {
      is_deleted: false
      timestamp {
    ctime: 1558072641431618
    dtime: -1
    mtime: 1558072641431714
      }
      metadata {
    name: "Goal/Milestone1"
      }
      uid: 25
    }
    is_complete: false
    is_active: true
  }
  projects {
    common {
      is_deleted: false
      timestamp {
    ctime: 1558072645433970
    dtime: -1
    mtime: 1558072651631986
      }
      metadata {
    name: "Goal/Milestone2"
      }
      uid: 26
    }
    is_complete: false
    is_active: true
    actions {
      common {
    is_deleted: false
    timestamp {
      ctime: 1558072651631806
      dtime: -1
      mtime: 1558073894998484
    }
    metadata {
      name: "do it @home"
    }
    uid: 27
      }
      is_complete: false
      ctx_uid: 6
    }
  }
}
ctx_list {
  common {
    is_deleted: false
    timestamp {
      ctime: 1558073894998551
      dtime: -1
      mtime: 1558073894998567
    }
    metadata {
      name: "Contexts"
    }
    uid: 3
  }
  contexts {
    common {
      is_deleted: false
      timestamp {
    ctime: 1558072527256254
    dtime: -1
    mtime: 1558072527256359
      }
      metadata {
    name: "@computer"
      }
      uid: 4
    }
    is_active: true
  }
  contexts {
    common {
      is_deleted: false
      timestamp {
    ctime: 1558072527256755
    dtime: -1
    mtime: 1558072527256907
      }
      metadata {
    name: "@phone"
      }
      uid: 5
    }
    is_active: true
  }
  contexts {
    common {
      is_deleted: false
      timestamp {
    ctime: 1558072527257268
    dtime: -1
    mtime: 1558072527257379
      }
      metadata {
    name: "@home"
      }
      uid: 6
    }
    is_active: true
  }
  contexts {
    common {
      is_deleted: false
      timestamp {
    ctime: 1558072527257745
    dtime: -1
    mtime: 1558072527257860
      }
      metadata {
    name: "@work"
      }
      uid: 7
    }
    is_active: true
  }
  contexts {
    common {
      is_deleted: false
      timestamp {
    ctime: 1558072527258221
    dtime: -1
    mtime: 1558072527258340
      }
      metadata {
    name: "@the store"
      }
      uid: 8
    }
    is_active: true
  }
  contexts {
    common {
      is_deleted: false
      timestamp {
    ctime: 1558072527258736
    dtime: -1
    mtime: 1558072527259623
      }
      metadata {
    name: "@someday/maybe"
      }
      uid: 9
    }
    is_active: false
  }
  contexts {
    common {
      is_deleted: false
      timestamp {
    ctime: 1558072527259235
    dtime: -1
    mtime: 1558072527259745
      }
      metadata {
    name: "@waiting for"
      }
      uid: 10
    }
    is_active: false
  }
  contexts {
    common {
      is_deleted: false
      timestamp {
    ctime: 1558072603561901
    dtime: -1
    mtime: 1558072603561988
      }
      metadata {
    name: "@another context"
      }
      uid: 23
    }
    is_active: true
  }
}
note_list {
  notes {
    name: ":__home"
    note: "this is the note on the home page (capture your thoughts)\\nit has many lines\\nlike\\nthis"
  }
}
""".strip()
    text_format.Merge(text, pb)
    self._AssertEqualWithDiff(
      [x.strip() for x in text_format.MessageToString(pb).split('\n')],
      [x.strip() for x in text.split('\n')] + [''])
    raised = False
    try:
      tdl.ToDoList.DeserializedProtobuf(pb.SerializeToString())
    except errors.DataError as e:
      self.assertEqual("UID -13 is an action's context UID but that context does not exist.", str(e))
      raised = True
    self.assertTrue(raised)

    self.setUp()
    text = text.replace("uid: -13\n", "uid: 23\n")
    pb = pyatdl_pb2.ToDoList()
    text_format.Merge(text, pb)
    tdl.ToDoList.DeserializedProtobuf(pb.SerializeToString())

    self.setUp()
    text = text.replace("default_context_uid: 23\n", "default_context_uid: -14\n")
    pb = pyatdl_pb2.ToDoList()
    text_format.Merge(text, pb)
    try:
      tdl.ToDoList.DeserializedProtobuf(pb.SerializeToString())
    except errors.DataError as e:
      self.assertEqual("UID -14 is a default_context_uid but that UID does not exist.", str(e))
      raised = True


if __name__ == '__main__':
  unitjest.main()
