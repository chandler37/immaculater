"""Unittests for module 'mergeprotobufs'."""

from pyatdllib.core import mergeprotobufs
from pyatdllib.core import pyatdl_pb2
from pyatdllib.core import prj
from pyatdllib.core import unitjest


class MergeprotobufsTestCase(unitjest.TestCase):
  # DLC more test cases
  def testMergeNoneNone(self):
    raised = False
    try:
      mergeprotobufs.Merge(None, None)
    except TypeError as e:
      self.assertEqual(str(e), 'one or both of the arguments must be present')
      raised = True
    self.assertTrue(raised)

  def testMergeNoneSomething(self):
    something = pyatdl_pb2.ToDoList()
    self.assertIs(mergeprotobufs.Merge(None, something), something)
    self.assertIs(mergeprotobufs.Merge(something, None), something)

  def testMergeTwo0(self):
    thing1, thing2 = pyatdl_pb2.ToDoList(), pyatdl_pb2.ToDoList()
    self.assertProtosEqual(mergeprotobufs.Merge(thing1, thing2), thing1)

  def testMergeTwo1left(self):
    thing1, thing2 = pyatdl_pb2.ToDoList(), pyatdl_pb2.ToDoList()
    thing1.inbox.CopyFrom(prj.Prj(name="xyz").AsProto())
    self.assertProtosEqual(mergeprotobufs.Merge(thing1, thing2), thing1)

  def testMergeTwo1right(self):
    thing1, thing2 = pyatdl_pb2.ToDoList(), pyatdl_pb2.ToDoList()
    thing2.inbox.CopyFrom(prj.Prj(name="xyz").AsProto())
    self.assertProtosEqual(mergeprotobufs.Merge(thing1, thing2), thing2)

  def testMergeTwoInboxNameChangedWithoutTimestampDifference(self):
    thing1 = pyatdl_pb2.ToDoList()
    thing1.inbox.CopyFrom(prj.Prj(name="my password is hunter2").AsProto())
    thing2 = pyatdl_pb2.ToDoList()
    thing2.CopyFrom(thing1)
    thing2.inbox.common.metadata.name = "my password is *******"
    merged = pyatdl_pb2.ToDoList()
    merged.CopyFrom(thing2)
    merged.inbox.common.metadata.name = "my password is either hunter2 or *******"  # DLC?
    self.assertProtosEqual(mergeprotobufs.Merge(thing1, thing2), merged)

  def testMergeTwoInboxNameChangedWithTimestampDifferenceRight(self):
    thing1 = pyatdl_pb2.ToDoList()
    thing1.inbox.CopyFrom(prj.Prj(name="my password is hunter2").AsProto())
    thing2 = pyatdl_pb2.ToDoList()
    thing2.CopyFrom(thing1)
    thing2.inbox.common.metadata.name = "my password is *******"
    thing2.inbox.common.timestamp.mtime += 1000
    self.assertProtosEqual(mergeprotobufs.Merge(thing1, thing2), thing2)

  def testMergeTwoInboxNameChangedWithTimestampDifferenceLeft(self):
    thing1 = pyatdl_pb2.ToDoList()
    thing1.inbox.CopyFrom(prj.Prj(name="my password is hunter2").AsProto())
    thing2 = pyatdl_pb2.ToDoList()
    thing2.CopyFrom(thing1)
    thing2.inbox.common.metadata.name = "my password is *******"
    thing2.inbox.common.timestamp.mtime -= 1000
    self.assertProtosEqual(mergeprotobufs.Merge(thing1, thing2), thing1)

  def testMergeTwoNewPrj(self):  # DLC left, right, and both
    self.assertEqual("DLC", "foo")

  def testMergeTwoNewCtx(self):  # DLC left, right, and both
    self.assertEqual("DLC", "foo")

  def testMergeTwoNewFolder(self):  # DLC left, right, and both
    self.assertEqual("DLC", "foo")

  def testMergeTwoNewNote(self):  # DLC left, right, and both
    self.assertEqual("DLC", "foo")

  def testMergeTwoNewAction(self):  # DLC left, right, and both, inbox vs. otherwise
    self.assertEqual("DLC", "foo")

  def testMergeTwoUIDCollision(self):  # DLC left, right, and both
    """DLC think hard about UX: current webapp displays UIDs in URLs; they can be shared. So changing one is very very bad. We should instead generate a random 64-bit number and use that.

DLC test case for the very unlikely collision
    """
    self.assertEqual("DLC", "foo")

  def testMergeTwoDeletions(self):  # DLC left, right, and both, overriding completions, contexts folders notes actions projects
    self.assertEqual("DLC", "foo")

  def testMergeTwoTrueDeletion(self):
    self.assertEqual("DLC", "foo")

  # DLC completion

  # DLC start at text format of proto and change evertyhing you see -- ctime, mtime, ...


"""DLC Additions are
  straightforward but you must handle UID collisions (e.g., the smartphone app
  has added Action 123 "buy soymilk" and the django app has added Project 123
  "replace wifi router"). Deletions are trickier because we must preserve the
  object's UID (but we can delete the data like "buy soymilk") and indicate
  that it was deleted so this server can delete the data. TODO(chandler37): Add
  an API that truly deletes deleted items, to be used only when all devices are
  known to be in sync.
  """

if __name__ == '__main__':
  unitjest.main()
