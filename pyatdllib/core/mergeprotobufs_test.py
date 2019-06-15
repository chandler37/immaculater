"""Unittests for module 'mergeprotobufs'."""

import unittest

from pyatdllib.core import mergeprotobufs
from pyatdllib.core import pyatdl_pb2
from pyatdllib.core import prj
from pyatdllib.core import tdl
from pyatdllib.core import uid
from pyatdllib.core import unitjest


class MergeprotobufsTestCase(unitjest.TestCase):
  def setUp(self):
    super().setUp()
    uid.ResetNotesOfExistingUIDs()

  # TODO(chandler37): more test cases
  def testMergeNoneNone(self):
    with self.assertRaisesRegex(TypeError, "both of the arguments must be present"):
      mergeprotobufs.Merge(None, None)

  def testMergeNoneSomething(self):
    something = pyatdl_pb2.ToDoList()
    with self.assertRaisesRegex(TypeError, "both of the arguments must be present"):
      mergeprotobufs.Merge(None, something)
    with self.assertRaisesRegex(TypeError, "both of the arguments must be present"):
      mergeprotobufs.Merge(tdl.ToDoList(), None)

  @unittest.expectedFailure  # TODO(chandler37): fix this
  def testMerge0(self):
    thing1, thing2 = tdl.ToDoList(), pyatdl_pb2.ToDoList()
    self.assertProtosEqual(mergeprotobufs.Merge(thing1, thing2), thing1)

  @unittest.expectedFailure  # TODO(chandler37): fix this
  def testMerge1left(self):
    thing1, thing2 = tdl.ToDoList(), pyatdl_pb2.ToDoList()
    thing1.inbox.CopyFrom(prj.Prj(name="xyz").AsProto())
    self.assertProtosEqual(mergeprotobufs.Merge(thing1, thing2), thing1)

  @unittest.expectedFailure  # TODO(chandler37): fix this
  def testMerge1right(self):
    thing1, thing2 = tdl.ToDoList(), pyatdl_pb2.ToDoList()
    thing2.inbox.CopyFrom(prj.Prj(name="xyz").AsProto())
    self.assertProtosEqual(mergeprotobufs.Merge(thing1, thing2), thing2)

  @unittest.expectedFailure  # TODO(chandler37): fix this
  def testMergeInboxNameChangedWithoutTimestampDifference(self):
    prj1 = prj.Prj(the_uid=uid.INBOX_UID, name="my password is hunter2")
    uid.ResetNotesOfExistingUIDs()
    thing1 = tdl.ToDoList(
      inbox=prj.Prj.DeserializedProtobuf(prj1.AsProto().SerializeToString()))
    thing2 = pyatdl_pb2.ToDoList()
    thing2.CopyFrom(thing1.AsProto())
    thing2.inbox.common.metadata.name = "my password is *******"
    merged = pyatdl_pb2.ToDoList()
    merged.CopyFrom(thing1.AsProto())
    merged.MergeFrom(thing2)
    self.assertProtosEqual(mergeprotobufs.Merge(thing1, thing2), merged)

  @unittest.expectedFailure  # TODO(chandler37): fix this
  def testMergeInboxNameChangedWithTimestampDifferenceRight(self):
    thing1 = pyatdl_pb2.ToDoList()
    thing1.inbox.CopyFrom(prj.Prj(name="my password is hunter2").AsProto())
    thing2 = pyatdl_pb2.ToDoList()
    thing2.CopyFrom(thing1)
    thing2.inbox.common.metadata.name = "my password is *******"
    thing2.inbox.common.timestamp.mtime += 1000
    self.assertProtosEqual(mergeprotobufs.Merge(thing1, thing2), thing2)

  @unittest.expectedFailure  # TODO(chandler37): fix this
  def testMergeInboxNameChangedWithTimestampDifferenceLeft(self):
    thing1 = pyatdl_pb2.ToDoList()
    thing1.inbox.CopyFrom(prj.Prj(name="my password is hunter2").AsProto())
    thing2 = pyatdl_pb2.ToDoList()
    thing2.CopyFrom(thing1)
    thing2.inbox.common.metadata.name = "my password is *******"
    thing2.inbox.common.timestamp.mtime -= 1000
    self.assertProtosEqual(mergeprotobufs.Merge(thing1, thing2), thing1)

  def testMergeNewPrj(self):
    self.assertTrue("TODO(chandler37): add this test")

  def testMergeMarkCompletedBothAnActionAndAProject(self):
    self.assertTrue("TODO(chandler37): add this test")

  def testMergeNewCtx(self):
    self.assertTrue("TODO(chandler37): add this test")

  def testMergeNewFolder(self):
    self.assertTrue("TODO(chandler37): add this test")

  def testMergeNewNoteOnAnItem(self):
    self.assertTrue("TODO(chandler37): add this test")

  def testMergeNewGlobalNote(self):
    self.assertTrue("TODO(chandler37): add this test")

  def testMergeNewAction(self):
    self.assertTrue("TODO(chandler37): add this test")

  def testMergeUIDCollision(self):
    """Let's say the smartphone app has added Action 123
    "buy soymilk" and the django app has added Project 123 "replace wifi
    router". Do we handle it with grace?

    TODO(chandler37): think hard about UX: current webapp displays
    UIDs in URLs; they can be shared. So changing one is very very
    bad. We should instead generate a random 64-bit number and use that.

    TODO(chandler37): add a  test case for the very unlikely collision.
    """
    self.assertTrue("TODO(chandler37): add this test")

  def testMergeDeletions(self):
    """Deletions are trickier. The non-django app must preserve the
    object's UID (but it can optionally delete the metadata like "buy
    soymilk") and indicate that it was deleted so that we can delete the
    data.

    TODO(chandler37): let's be wise about truly deleting even the UID
    and is_deleted bit and their containing
    Action/Context/Project/Folder/Note/etc.
    """
    self.assertTrue("TODO(chandler37): add this test")

  def testMergeTrueDeletion(self):
    """Let us say that the non-django app sends us a new thing but also
    the complete (a.k.a. "true") deletion of an old thing. What do we
    do? We assume that the old thing is to be preserved, because if it
    were intended to be deleted then the item would remain, with much of
    its metadata gutted but the deletion noted and UID intact.

    TODO(chandler37): Add an API that truly deletes deleted items, to be
    used only when all devices are known to be in sync.
    """
    self.assertTrue("TODO(chandler37): add this test")

  # TODO(chandler37): start at text format of proto and change evertyhing you see -- ctime, mtime, ...

  # TODO(chandler37): overriding completions, contexts folders notes actions projects


if __name__ == '__main__':
  unitjest.main()
