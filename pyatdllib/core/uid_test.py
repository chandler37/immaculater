"""Unittests for module 'uid'."""

from pyatdllib.core import uid
from pyatdllib.core import unitjest


# TODO(chandler): Test thread-safety in at least two ways: NextUID._factory
# will be the same for all threads. Two threads can't step on each others toes
# in the critical sections.

# pylint: disable=missing-docstring,too-many-public-methods
class UIDTestCase(unitjest.TestCase):
  def testUIDs(self):
    self.assertEqual(uid.singleton_factory.NextUID(), 1)
    self.assertEqual(uid.singleton_factory.NextUID(), 2)
    self.assertEqual(uid.singleton_factory.NextUID(), 3)
    uid.singleton_factory.NoteExistingUID(1)
    self.assertEqual(uid.singleton_factory.NextUID(), 4)
    uid.singleton_factory.NoteExistingUID(11)
    uid.singleton_factory.NoteExistingUID(10)
    self.assertEqual(uid.singleton_factory.NextUID(), 12)


if __name__ == '__main__':
  unitjest.main()
