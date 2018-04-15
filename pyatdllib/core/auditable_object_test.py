"""Unittests for module 'auditable_object'."""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

from pyatdllib.core import auditable_object
from pyatdllib.core import unitjest


# pylint: disable=missing-docstring,protected-access,too-many-public-methods
class AuditableObjectTestCase(unitjest.TestCase):

  def testFloatingPointTimestamp(self):
    self.assertEqual(
      auditable_object._FloatingPointTimestamp(-1), None)
    self.assertAlmostEqual(
      auditable_object._FloatingPointTimestamp(-1 * 10**6), -1)
    self.assertEqual(
      auditable_object._FloatingPointTimestamp(0), 0.0)
    self.assertEqual(
      auditable_object._FloatingPointTimestamp(1419989796918906),
      1419989796.918906)
    self.assertEqual(
      auditable_object._FloatingPointTimestamp(123456), 0.123456)


if __name__ == '__main__':
  unitjest.main()
