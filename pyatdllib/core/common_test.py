"""Unittests for module 'common'."""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

from pyatdllib.core import common
from pyatdllib.core import unitjest


# pylint: disable=missing-docstring,protected-access,too-many-public-methods
class CommonTestCase(unitjest.TestCase):

  def testFloatingPointTimestamp(self):
    self.assertEqual(
      common.FloatingPointTimestamp(-1), None)
    self.assertAlmostEqual(
      common.FloatingPointTimestamp(-1 * 10**6), -1)
    self.assertEqual(
      common.FloatingPointTimestamp(0), 0.0)
    self.assertEqual(
      common.FloatingPointTimestamp(1419989796918906),
      1419989796.918906)
    self.assertEqual(
      common.FloatingPointTimestamp(123456), 0.123456)


if __name__ == '__main__':
  unitjest.main()
