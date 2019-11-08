"""Unittests for module 'uid'."""

import random

import gflags as flags  # https://code.google.com/p/python-gflags/

from pyatdllib.core import errors
from pyatdllib.core import uid
from pyatdllib.core import unitjest


FLAGS = flags.FLAGS


# TODO(chandler): Test thread-safety in at least two ways: NextUID._factory
# will be the same for all threads. Two threads can't step on each others toes
# in the critical sections.

# pylint: disable=missing-docstring,too-many-public-methods
class UIDTestCase(unitjest.TestCase):

  def setUp(self):
    super().setUp()
    FLAGS.pyatdl_randomize_uids = False
    uid.ResetNotesOfExistingUIDs()

  def testTestModeSequentialUIDs(self):
    self.assertEqual(uid.singleton_factory.NextUID(), 1)
    self.assertEqual(uid.singleton_factory.NextUID(), 2)
    self.assertEqual(uid.singleton_factory.NextUID(), 3)

    raised = False
    try:
      uid.singleton_factory.NoteExistingUID(2)
    except errors.DataError:
      raised = True
    self.assertTrue(raised)

    uid.singleton_factory.NoteExistingUID(5)
    self.assertEqual(uid.singleton_factory.NextUID(), 6)
    uid.singleton_factory.NoteExistingUID(12)
    uid.singleton_factory.NoteExistingUID(11)
    self.assertEqual(uid.singleton_factory.NextUID(), 13)
    uid.singleton_factory.NoteExistingUID(2**63 - 2)
    self.assertEqual(uid.singleton_factory.NextUID(), 2**63 - 1)

    raised = False
    try:
      uid.singleton_factory.NextUID()
    except errors.DataError:
      raised = True

  def testRaisingUponNextUID(self):
    FLAGS.pyatdl_randomize_uids = True
    random.seed(37)
    uid.ResetNotesOfExistingUIDs(True)
    raised = False
    try:
      uid.singleton_factory.NextUID()
    except errors.DataError:
      raised = True
    self.assertTrue(raised)
    uid.ResetNotesOfExistingUIDs(False)
    uid.singleton_factory.NextUID()

  def testRandomizedUIDs(self):
    FLAGS.pyatdl_randomize_uids = True
    random.seed(37)
    self.assertEqual(uid.singleton_factory.NextUID(), 1987761140110186971)
    self.assertEqual(uid.singleton_factory.NextUID(), 277028180750618930)
    self.assertEqual(uid.singleton_factory.NextUID(), 8923216991658685487)
    uid.singleton_factory.NoteExistingUID(1)
    self.assertEqual(uid.singleton_factory.NextUID(), 7844860928174339221)
    uid.singleton_factory.NoteExistingUID(11)
    uid.singleton_factory.NoteExistingUID(10)
    self.assertEqual(uid.singleton_factory.NextUID(), 4355858073736897916)
    raised = False
    try:
      uid.singleton_factory.NoteExistingUID(4355858073736897916)
    except errors.DataError:
      raised = True
    self.assertEqual(raised, True)
    raised = False
    try:
      uid.singleton_factory.NoteExistingUID(10)
    except errors.DataError:
      raised = True
    self.assertEqual(raised, True)


if __name__ == '__main__':
  unitjest.main()
