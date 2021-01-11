"""Unittests for module 'mergeprotobufs'."""

import random
import time

from google.protobuf import text_format  # type: ignore

from pyatdllib.core import action
from pyatdllib.core import mergeprotobufs
from pyatdllib.core import pyatdl_pb2
from pyatdllib.core import prj
from pyatdllib.core import tdl
from pyatdllib.core import uid
from pyatdllib.core import unitjest

_MICROS = 10**6
year1970microsec = 10**6 * _MICROS  # 1970-01-12 05:46:40
year5454microsec = 109951162777 * _MICROS  # 5454-03-19 14:39:37 PST8PDT


text_formatted_protobuf_well_known = """
inbox {
  common {
    is_deleted: false
    timestamp {
      ctime: 1000000001000000
      dtime: -1
      mtime: 1000000001000000
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
        ctime: 1000000000001
        dtime: -1
        mtime: 1000000001000000
      }
      metadata {
        name: "buy light bulbs"
        note: "60w"
      }
      uid: -5
    }
    is_complete: false
  }
}
root {
  common {
    is_deleted: false
    timestamp {
      ctime: 1000000001000000
      dtime: -1
      mtime: 1000000001000000
    }
    uid: 2
  }
  projects {
    common {
      is_deleted: false
      timestamp {
        ctime: 1000000000000
        dtime: -1
        mtime: 1000000001000000
      }
      metadata {
        name: "P1"
      }
      uid: -6
    }
    is_complete: false
    is_active: false
  }
}
ctx_list {
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
      uid: -48
    }
    is_active: true
  }
}
note_list {
  notes {
    name: ":__home"
    note: "this is the note on the home page"
  }
}
"""

text_formatted_protobuf_0 = """
inbox {
  common {
    is_deleted: false
    timestamp {
      ctime: 1000000001000000
      dtime: -1
      mtime: 1000000001000000
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
        ctime: 1000000000001
        dtime: -1
        mtime: 1000000000001
      }
      metadata {
        name: "buy light bulbs"
        note: "60w"
      }
      uid: -5
    }
    is_complete: false
  }
}
root {
  common {
    is_deleted: false
    timestamp {
      ctime: 1000000001000000
      dtime: -1
      mtime: 1000000001000000
    }
    uid: 2
  }
  projects {
    common {
      is_deleted: false
      timestamp {
        ctime: 1000000000000
        dtime: -1
        mtime: 1000000001000000
      }
      metadata {
        name: "P1"
      }
      uid: -6
    }
    is_complete: false
    is_active: false
  }
}
"""

text_formatted_protobuf_1 = """
inbox {
  common {
    is_deleted: false
    timestamp {
      ctime: %(year5454microsec)d
      dtime: -1
      mtime: %(year5454microsec)d
    }
    metadata {
      name: "new name for what was once the inbox"
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
      ctime: 1000000001000000
      dtime: -1
      mtime: 1000000001000000
    }
    uid: 2
  }
}
""" % {'year5454microsec': year5454microsec}

text_formatted_protobuf_2 = """
inbox {
  common {
    is_deleted: false
    timestamp {
      ctime: 1000000001000000
      dtime: -1
      mtime: 1000000001000000
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
      ctime: 1000000001000000
      dtime: -1
      mtime: 1000000001000000
    }
    uid: 2
  }
  projects {
    common {
      is_deleted: false
      timestamp {
        ctime: 1000000000001
        dtime: -1
        mtime: 1000000000001
      }
      metadata {
        name: "P1"
      }
      uid: -6
    }
    is_complete: false
    is_active: false
    actions {
      common {
        is_deleted: false
        timestamp {
          ctime: 1000000000001
          dtime: -1
          mtime: 1000000000001
        }
        metadata {
          name: "A1 was once the name"
        }
        uid: -5
      }
      is_complete: false
    }
  }
}
"""


def _well_known_tdl() -> pyatdl_pb2.ToDoList:
  return text_format.Merge(text_formatted_protobuf_well_known, pyatdl_pb2.ToDoList())


def _ProtobufToTdl(proto: pyatdl_pb2.ToDoList) -> tdl.ToDoList:
  assert isinstance(proto, pyatdl_pb2.ToDoList)
  return tdl.ToDoList.DeserializedProtobuf(proto.SerializeToString())


def _FreshToDoListProto() -> pyatdl_pb2.ToDoList:
  """Returns a semantically empty, well-formed protobuf."""
  return pyatdl_pb2.ToDoList.FromString(
    tdl.ToDoList().AsProto().SerializeToString())


class MergeprotobufsTestCase(unitjest.TestCase):
  def setUp(self) -> None:
    super().setUp()
    uid.ResetNotesOfExistingUIDs()
    self.maxDiff = None
    self.saved_time = time.time
    time.time = lambda: 1000000001  # 2001-09-08 18:46:41 PST8PDT, which is 1000000001000000 in microseconds since the epoch
    random.seed(3737123)
    uid.ResetNotesOfExistingUIDs(raise_data_error_upon_next_uid=True, allow_duplication=True)

  def tearDown(self) -> None:
    time.time = self.saved_time

  # TODO(chandler37): more test cases
  def testMergeNoneNone(self) -> None:
    with self.assertRaisesRegex(TypeError, "both of the arguments must be present"):
      mergeprotobufs.Merge(None, None)  # type: ignore

  def testMergeNoneSomething(self) -> None:
    something = pyatdl_pb2.ToDoList()
    with self.assertRaisesRegex(TypeError, "both of the arguments must be present"):
      mergeprotobufs.Merge(None, something)  # type: ignore
    with self.assertRaisesRegex(TypeError, "both of the arguments must be present"):
      mergeprotobufs.Merge(tdl.ToDoList(), None)  # type: ignore

  def testMerge0(self) -> None:
    todos_in_db, remote_pb = tdl.ToDoList(), pyatdl_pb2.ToDoList()
    self.assertProtosEqual(mergeprotobufs.Merge(todos_in_db, remote_pb), todos_in_db.AsProto())

  def testMerge1left(self) -> None:
    todos_in_db, remote_pb = tdl.ToDoList(), pyatdl_pb2.ToDoList()
    todos_in_db.inbox = prj.Prj(the_uid=uid.INBOX_UID, name="xyz")
    self.assertProtosEqual(mergeprotobufs.Merge(todos_in_db, remote_pb), todos_in_db.AsProto())

  def testMerge1Right(self) -> None:
    todos_in_db, remote_pb = tdl.ToDoList(), pyatdl_pb2.ToDoList()
    p = prj.Prj(name="new name for what was once the inbox", the_uid=uid.INBOX_UID).AsProto()
    p.common.timestamp.ctime = year5454microsec
    p.common.timestamp.mtime = year5454microsec
    remote_pb.inbox.CopyFrom(p)
    self.assertProtoTextuallyEquals(
      mergeprotobufs.Merge(todos_in_db, remote_pb),
      text_formatted_protobuf_1)

  def testMerge1RightNewAction(self) -> None:
    todos_in_db, remote_pb = tdl.ToDoList(), pyatdl_pb2.ToDoList()
    p = prj.Prj(name="old name (as dictated by ctime and mtime) for what was once the inbox", the_uid=uid.INBOX_UID)
    p.mtime = p.ctime = 9.0
    a = action.Action(name="buy light bulbs", note="60w", the_uid=5)
    p.items.append(a)
    remote_pb.inbox.CopyFrom(p.AsProto())
    self.assertProtoTextuallyEquals(mergeprotobufs.Merge(todos_in_db, remote_pb), """
inbox {
  common {
    is_deleted: false
    timestamp {
      ctime: 1000000001000000
      dtime: -1
      mtime: 1000000001000000
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
        ctime: 1000000001000000
        dtime: -1
        mtime: 1000000001000000
      }
      metadata {
        name: "buy light bulbs"
        note: "60w"
      }
      uid: 5
    }
    is_complete: false
  }
}
root {
  common {
    is_deleted: false
    timestamp {
      ctime: 1000000001000000
      dtime: -1
      mtime: 1000000001000000
    }
    uid: 2
  }
}
""")

  def testMerge1RightMovedAction(self) -> None:
    self.helpTestMovedActionToInbox(
      microseconds_since_the_epoch_in_db=year1970microsec,
      microseconds_since_the_epoch_in_remote=year1970microsec + 1,
      index=0)

  def testMerge1RightWeMovedTheActionLastTime(self) -> None:
    # The "golden" text_formatted_protobuf_2 has the action with UID -5 inside project P1 because of recency:
    self.helpTestMovedActionToInbox(
      microseconds_since_the_epoch_in_db=year1970microsec + 1,
      microseconds_since_the_epoch_in_remote=year1970microsec,
      index=2)

  def helpTestMovedActionToInbox(
    self,
    microseconds_since_the_epoch_in_db: int,
    microseconds_since_the_epoch_in_remote: int,
    index: int
  ) -> None:
    """An action was in a project P1 but has moved to the inbox."""
    a1_uid = -5

    def DatabaseToDoList() -> pyatdl_pb2.ToDoList:
      tdlpb = _FreshToDoListProto()

      p1 = tdlpb.root.projects.add()
      p1.common.uid = -6
      p1.common.metadata.name = "P1"
      p1.common.timestamp.ctime = microseconds_since_the_epoch_in_db
      p1.common.timestamp.mtime = p1.common.timestamp.ctime

      a1 = p1.actions.add()
      a1.common.metadata.name = "A1 was once the name"
      a1.common.uid = a1_uid
      a1.common.timestamp.ctime = microseconds_since_the_epoch_in_db
      a1.common.timestamp.mtime = a1.common.timestamp.ctime
      return tdlpb

    def RemoteToDoList() -> pyatdl_pb2.ToDoList:
      tdlpb = _FreshToDoListProto()
      a = tdlpb.inbox.actions.add()
      a.common.metadata.name = "buy light bulbs"
      a.common.metadata.note = "60w"
      a.common.timestamp.ctime = microseconds_since_the_epoch_in_remote
      a.common.timestamp.mtime = a.common.timestamp.ctime
      a.common.uid = a1_uid
      return tdlpb

    tdl1_in_db = _ProtobufToTdl(DatabaseToDoList())
    if index == 0:
      golden = text_formatted_protobuf_0
    elif index == 2:
      golden = text_formatted_protobuf_2
    else:
      assert False, "bad index"
    self.assertProtoTextuallyEquals(
      mergeprotobufs.Merge(tdl1_in_db, RemoteToDoList()),
      golden)

  def testMergeInboxNameChangedWithoutTimestampDifference(self) -> None:
    # TODO(chandler37): also, add an action to the inbox and make sure that it appears even though the metadata should
    # not change.
    prj1 = prj.Prj(the_uid=uid.INBOX_UID, name="my password is hunter2")
    uid.ResetNotesOfExistingUIDs()
    todos_in_db = tdl.ToDoList(
      inbox=prj.Prj.DeserializedProtobuf(prj1.AsProto().SerializeToString()))
    remote_pb = pyatdl_pb2.ToDoList()
    remote_pb.CopyFrom(todos_in_db.AsProto())
    remote_pb.inbox.common.metadata.name = "my password is *******"
    merged = pyatdl_pb2.ToDoList()
    merged.CopyFrom(todos_in_db.AsProto())
    merged.MergeFrom(remote_pb)
    self.assertProtosEqual(mergeprotobufs.Merge(todos_in_db, remote_pb), todos_in_db.AsProto())

  def testMergeInboxNameChangedWithTimestampDifferenceRight(self) -> None:
    def DatabaseToDoList() -> pyatdl_pb2.ToDoList:
      tdlpb = _FreshToDoListProto()
      tdlpb.inbox.CopyFrom(
        prj.Prj(the_uid=uid.INBOX_UID, name="my password is hunter2").AsProto())
      return tdlpb

    def RemoteToDoList() -> pyatdl_pb2.ToDoList:
      tdlpb = _FreshToDoListProto()
      tdlpb.CopyFrom(DatabaseToDoList())
      tdlpb.inbox.common.metadata.name = "my password is *******"
      tdlpb.inbox.common.timestamp.mtime += 1000
      return tdlpb

    remote = RemoteToDoList()
    self.assertProtosEqual(
      mergeprotobufs.Merge(
        _ProtobufToTdl(DatabaseToDoList()),
        remote),
      remote)

  def testMergeInboxNameChangedWithTimestampDifferenceLeft(self) -> None:
    todos_in_db = tdl.ToDoList(
      inbox=prj.Prj(the_uid=uid.INBOX_UID, name="my password is hunter2"))
    remote_pb = pyatdl_pb2.ToDoList()
    remote_pb.CopyFrom(todos_in_db.AsProto())
    remote_pb.inbox.common.metadata.name = "my password is *******"
    remote_pb.inbox.common.timestamp.mtime -= 1000
    self.assertProtosEqual(
      mergeprotobufs.Merge(
        todos_in_db,
        remote_pb),
      todos_in_db.AsProto())

  def testMergeNewPrj(self) -> None:
    self.assertTrue("TODO(chandler37): add this test")

  def testMergeMarkCompletedBothAnActionAndAProject(self) -> None:
    self.assertTrue("TODO(chandler37): add this test")

  def testMergeNewCtx(self) -> None:
    self.assertTrue("TODO(chandler37): add this test")

  def testMergeNewFolder(self) -> None:
    self.assertTrue("TODO(chandler37): add this test")

  def testMergeNewNoteOnAnItem(self) -> None:
    self.assertTrue("TODO(chandler37): add this test")

  def testMergeNewGlobalNote(self) -> None:
    self.assertTrue("TODO(chandler37): add this test")

  def testMergeNewActionInInbox(self) -> None:
    self.assertTrue("TODO(chandler37): add this test")

  def testMergeNewActionOutsideInbox(self) -> None:
    self.assertTrue("TODO(chandler37): add this test")

  def testMergeUIDCollision(self) -> None:
    """Let's say the smartphone app has added Action 123
    "buy soymilk" and the django app has added Project 123 "replace wifi
    router". Do we handle it with grace?

    TODO(chandler37): think hard about UX: current webapp displays
    UIDs in URLs; they can be shared. So changing one is very very
    bad. We should instead generate a random 64-bit number and use that.

    TODO(chandler37): add a test case for the very unlikely collision.
    """
    self.assertTrue("TODO(chandler37): add this test")

  def testMergeDeletions(self) -> None:
    """Deletions are trickier. The non-django app must preserve the
    object's UID (but it can optionally delete the metadata like "buy
    soymilk") and indicate that it was deleted so that we can delete the
    data.

    TODO(chandler37): let's be wise about truly deleting even the UID
    and is_deleted bit and their containing
    Action/Context/Project/Folder/Note/etc.
    """
    self.assertTrue("TODO(chandler37): add this test")

  def testMergeTrueDeletion(self) -> None:
    """Let us say that the non-django app sends us a new thing but also
    the complete (a.k.a. "true") deletion of an old thing. What do we
    do? We assume that the old thing is to be preserved, because if it
    were intended to be deleted then the item would remain, with much of
    its metadata gutted but the deletion noted and UID intact.

    TODO(chandler37): Add an API that truly deletes deleted items, to be
    used only when all devices are known to be in sync.
    """
    self.assertTrue("TODO(chandler37): add this test")

  def testFolderChanges(self) -> None:
    """A folder has a new prj inside, and a new folder inside. We grab all three changes.

    TODO(chandler37): test a subfolder that has updated metadata.
    """
    def RemoteToDoList(start: pyatdl_pb2.ToDoList) -> pyatdl_pb2.ToDoList:
      remote_pb = pyatdl_pb2.ToDoList()
      remote_pb.CopyFrom(start)
      remote_pb.ctx_list.contexts[0].common.timestamp.mtime = year5454microsec
      remote_pb.ctx_list.contexts[0].common.metadata.name = remote_pb.ctx_list.contexts[0].common.metadata.name.upper()
      remote_pb.note_list.notes[0].note = "this is the UPDATED note on the home page"
      new_note = remote_pb.note_list.notes.add()
      # TODO(chandler37): test deletion of a note, perhaps just setting the note to the empty string.
      new_note.name = "new note"
      new_note.note = "the corresponding new note"
      new_folder = remote_pb.root.folders.add()
      text_format.Merge("""
  common {
    is_deleted: false
    timestamp {
      ctime: 38000000
      dtime: -1
      mtime: 38000000
    }
    metadata {
      name: "newfolder"
    }
    uid: -6279119140261074202
  }
  projects {
    common {
      is_deleted: false
      timestamp {
        ctime: 38000000
        dtime: -1
        mtime: 39000000
      }
      metadata {
        name: "newprj"
      }
      uid: -15
    }
    is_complete: false
    is_active: true
    actions {
      common {
        is_deleted: false
        timestamp {
          ctime: 39000000
          dtime: -1
          mtime: 39000000
        }
        metadata {
          name: "action_in_newprj"
        }
        uid: -29
      }
      is_complete: false
    }
  }
""", new_folder)
      return remote_pb

    golden = """
inbox {
  common {
    is_deleted: false
    timestamp {
      ctime: 1000000001000000
      dtime: -1
      mtime: 1000000001000000
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
        ctime: 1000000000001
        dtime: -1
        mtime: 1000000001000000
      }
      metadata {
        name: "buy light bulbs"
        note: "60w"
      }
      uid: -5
    }
    is_complete: false
  }
}
root {
  common {
    is_deleted: false
    timestamp {
      ctime: 1000000001000000
      dtime: -1
      mtime: 1000000001000000
    }
    uid: 2
  }
  folders {
    common {
      is_deleted: false
      timestamp {
        ctime: 38000000
        dtime: -1
        mtime: 38000000
      }
      metadata {
        name: "newfolder"
      }
      uid: -6279119140261074202
    }
    projects {
      common {
        is_deleted: false
        timestamp {
          ctime: 38000000
          dtime: -1
          mtime: 39000000
        }
        metadata {
          name: "newprj"
        }
        uid: -15
      }
      is_complete: false
      is_active: true
      actions {
        common {
          is_deleted: false
          timestamp {
            ctime: 39000000
            dtime: -1
            mtime: 39000000
          }
          metadata {
            name: "action_in_newprj"
          }
          uid: -29
        }
        is_complete: false
      }
    }
  }
  projects {
    common {
      is_deleted: false
      timestamp {
        ctime: 1000000000000
        dtime: -1
        mtime: 1000000001000000
      }
      metadata {
        name: "P1"
      }
      uid: -6
    }
    is_complete: false
    is_active: false
  }
}
ctx_list {
  contexts {
    common {
      is_deleted: false
      timestamp {
        ctime: 1558072527256254
        dtime: -1
        mtime: 109951162777000000
      }
      metadata {
        name: "@COMPUTER"
      }
      uid: -48
    }
    is_active: true
  }
}
note_list {
  notes {
    name: ":__home"
    note: "<<<<<<< DB\\\\nthis is the note on the home page\\\\n=======\\\\nthis is the UPDATED note on the home \
page\\\\n>>>>>>> device\\\\n"
  }
  notes {
    name: "new note"
    note: "the corresponding new note"
  }
}
"""
    # TODO(chandler37): test with a well known TDL with an existing folder under root.
    self.assertProtoTextuallyEquals(
      mergeprotobufs.Merge(
        _ProtobufToTdl(_well_known_tdl()),
        RemoteToDoList(_well_known_tdl())),
      golden)


if __name__ == '__main__':
  unitjest.main()


r"""
// TODO(chandler37): start at text format of proto and change evertyhing you see -- ctime, mtime, ...

// TODO(chandler37): overriding completions, contexts folders notes actions projects

// TODO(chandler37): test Action for obliterated. for deleted. for completed.

// TODO(chandler37): More test cases follow:

//
// immaculater> ls
// --project-- uid=1 --incomplete-- ---active--- inbox
// immaculater> cd inbox
// immaculater> ls
// immaculater> touch "give the cat a bath"
// immaculater> ls
// --action--- uid=4940145534978221493 --incomplete-- 'give the cat a bath' --in-context-- '<none>'
// immaculater> touch "give the cat a bath"
// immaculater> ls
// --action--- uid=4940145534978221493 --incomplete-- 'give the cat a bath' --in-context-- '<none>'
// --action--- uid=-5492528092754581212 --incomplete-- 'give the cat a bath' --in-context-- '<none>'

// TEST that if we delete 4940145534978221493 on device0 and change it to 'give the dog a bath' on device1, then we end
// up with, UNDELETED, 'give the dog a bath', i.e.,
//
// immaculater> ls
// --action--- uid=4940145534978221493 --incomplete-- 'give the dog a bath' --in-context-- '<none>'
// --action--- uid=-5492528092754581212 --incomplete-- 'give the cat a bath' --in-context-- '<none>'
// TODO(chandler37):  also test the same thing with a note changing:
//      if, on device1 the note changes on 4940145534978221493 from NULL to 'must do
// this!' (or vice versa) but on device0 again 4940145534978221493 is deleted,
// then discard the deletion.
// also test the same thing with context changing:
//      if, on device1 the context changes (from NULL to something, or vice versa, or from @a to @b) but on device0 again
//      4940145534978221493 is deleted,
// then POLD (Principle of Least Disappearances) requires that we discard the deletion, but of course we keep the change to the context.

// before:
// immaculater> ls
// --action--- uid=4940145534978221493 --incomplete-- 'give the dog a bath' --in-context-- '<none>'
// --action--- uid=-5492528092754581212 --incomplete-- 'give the cat a bath' --in-context-- '<none>'
//
// after on device0:
// immaculater> ls
// <DELETED>--action--- uid=4940145534978221493 --incomplete-- 'give the dog a bath' --in-context-- '<none>'</DELETED>
// --action--- uid=-5492528092754581212 --incomplete-- 'give the cat a bath' --in-context-- '<none>'

// after on device1:
// immaculater> ls
// --action--- uid=4940145534978221493 --incomplete-- 'give the dog a bath' --in-context-- @home
// --action--- uid=-5492528092754581212 --incomplete-- 'give the cat a bath' --in-context-- '<none>'

// merged:
// immaculater> ls
// <DELETED>--action--- uid=4940145534978221493 --incomplete-- 'give the dog a bath' --in-context-- @home</DELETED>
// --action--- uid=-5492528092754581212 --incomplete-- 'give the cat a bath' --in-context-- '<none>'


// also test the same thing with context changing differently on both devices (TODO(chandler37):  w/ and w/o deletion too):
//      if, on device1 the context changes from NULL to @a but on device0 from NULL to @b, (TODO(chandler37): Note that this
//      is the same as a note or name change in conflict)
// then....
//
// before:
// immaculater> ls
// --action--- uid=4940145534978221493 --incomplete-- 'give the dog a bath' --in-context-- '<none>'
//
// on device0:
// immaculater> ls
// --action--- uid=4940145534978221493 --incomplete-- 'eat cucumber' --in-context-- '<none>'

// on device1:
// immaculater> ls
// --action--- uid=4940145534978221493 --incomplete-- 'buy a prius' --in-context-- '<none>'

// merged:
// immaculater> ls
// --action--- uid=4940145534978221493 --incomplete-- 'buy a prius' --in-context-- '<none>'
// --action--- uid=123                 --incomplete-- 'eat cucumber' --in-context-- '<none>'

// SAME AS ABOVE but with CONTEXT:
//
// before:
// immaculater> ls
// --action--- uid=4940145534978221493 --incomplete-- 'give the dog a bath' --in-context-- '<none>'
//
// on device0:
// immaculater> ls
// --action--- uid=4940145534978221493 --incomplete-- 'give the dog a bath' --in-context-- @home
//
// on device1:
// immaculater> ls
// --action--- uid=4940145534978221493 --incomplete-- 'give the dog a bath' --in-context-- @someday/maybe
//
// merged:
// immaculater> ls
// --action--- uid=4940145534978221493 --incomplete-- 'give the dog a bath' --in-context-- @someday/maybe
// --action--- uid=123                 --incomplete-- 'give the dog a bath' --in-context-- @home

// TODO(chandler37):  test case: a note is changed in such a way that it would produce a git conflict should the note be a file in a
git repository. what we do is to leave git conflict markers like so:
//
// immaculater> touch pontificate
// immaculater> note --noreplace pontificate "Note follows:\nNote from device0\nEnd note."
// immaculater> note pontificate
// Note follows:\nNote from device0\nEnd note.
// immaculater> save ~/tmp/device0.note
// immaculater> note --replace pontificate "Note follows:\nNote from device1\nEnd note."
// immaculater> note pontificate
// Note follows:\nNote from device1\nEnd note.
// immaculater> save ~/tmp/device1.note
// immaculater> ls
// --action--- uid=3367828127791869605 --incomplete-- pontificate --in-context-- '<none>'
//
// merged:
// immaculater> note pontificate
// Note follows:\n<<<<<<< FROM NETWORK\nNote from device1\n=======\nNote from device0\n>>>>>>> IN DATABASE\nEnd note.

// TODO(chandler37): a test case where the database is non-empty but semantically empty so that we make sure we can add every single
// thing in the ToDoList message (and Action et al.)
"""
