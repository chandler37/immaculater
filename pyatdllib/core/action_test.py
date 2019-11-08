"""Unittests for module 'action'."""

import time

import gflags as flags  # https://code.google.com/p/python-gflags/

from pyatdllib.core import action
from pyatdllib.core import uid
from pyatdllib.core import unitjest


FLAGS = flags.FLAGS


class ActionTestCase(unitjest.TestCase):  # pylint: disable=missing-docstring,too-many-public-methods

  def setUp(self):
    super().setUp()
    FLAGS.pyatdl_randomize_uids = False
    uid.ResetNotesOfExistingUIDs()

  def testToAndFromProto(self):  # pylint: disable=missing-docstring

    def MockTime():  # pylint: disable=missing-docstring
      return 373737373

    def MockLater():  # pylint: disable=missing-docstring
      return MockTime() + 100 * 1000 * 1000

    saved_time = time.time
    time.time = MockTime
    try:
      project = unitjest.FullPrj()
      pb = project.items[0].AsProto()
      pb1 = project.items[1].AsProto()
      self.assertEqual(pb.common.metadata.name, 'Buy milk')
      # pylint: disable=line-too-long
      self.assertEqual(
        str(pb),
        r"""common {
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
""")
      self.assertEqual(
        str(pb1),
        r"""common {
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
""")

      time.time = MockLater
      uid.ResetNotesOfExistingUIDs()
      a = action.Action.DeserializedProtobuf(pb1.SerializeToString())
      self.assertEqual(
        a.mtime * 1000 * 1000.0,
        373737373000000.0)

    finally:
      time.time = saved_time


if __name__ == '__main__':
  unitjest.main()
