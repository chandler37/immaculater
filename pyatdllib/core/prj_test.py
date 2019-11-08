"""Unittests for module 'prj'."""

import time

import gflags as flags  # https://code.google.com/p/python-gflags/

from pyatdllib.core import prj
from pyatdllib.core import uid
from pyatdllib.core import unitjest


FLAGS = flags.FLAGS


# pylint: disable=missing-docstring,too-many-public-methods
class PrjTestCase(unitjest.TestCase):

  def setUp(self):
    super().setUp()
    FLAGS.pyatdl_randomize_uids = False
    uid.ResetNotesOfExistingUIDs()

  def testEmptyPrj(self):
    project = prj.Prj()
    self.assertTrue(project.name is None)
    self.assertEqual(project.items, [])

  def testNamedPrj(self):
    project = prj.Prj(name='myname', items=[])
    self.assertEqual(project.name, 'myname')
    self.assertEqual(project.items, [])

  def testFullPrj(self):
    project = unitjest.FullPrj()
    self.assertEqual(project.name, 'myname')
    self.assertEqual(project.items[0].name, 'Buy milk')
    self.assertEqual(project.items[1].ctx_uid, -2**63)
    project.items[1] = project.items[0]
    self.assertEqual(project.items, [project.items[0], project.items[0]])

  def testAsProto(self):
    def MockTime():
      return 373737373

    saved_time = time.time
    time.time = MockTime
    try:
      project = unitjest.FullPrj()
      pb = project.AsProto()
      # pylint: disable=maybe-no-member
      self.assertEqual(pb.common.metadata.name, 'myname')
      # pylint: disable=line-too-long
      self._AssertEqualWithDiff(
        [str(pb)],
        [r"""common {
  is_deleted: false
  timestamp {
    ctime: 373737373000000
    dtime: -1
    mtime: 373737373000000
  }
  metadata {
    name: "myname"
  }
  uid: 3
}
is_complete: false
is_active: true
actions {
  common {
    is_deleted: false
    timestamp {
      ctime: 373737373000000
      dtime: -1
      mtime: 373737373000000
    }
    metadata {
      name: "Buy milk"
    }
    uid: 1
  }
  is_complete: false
}
actions {
  common {
    is_deleted: false
    timestamp {
      ctime: 373737373000000
      dtime: -1
      mtime: 373737373000000
    }
    metadata {
      name: "Oranges"
    }
    uid: 2
  }
  is_complete: false
  ctx_uid: -9223372036854775808
}
"""])
    finally:
      time.time = saved_time


if __name__ == '__main__':
  unitjest.main()
