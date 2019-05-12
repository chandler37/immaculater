"""Unittests for module 'serialization'."""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import gflags as flags  # https://code.google.com/p/python-gflags/

from pyatdllib.core import unitjest
from pyatdllib.ui import serialization
from pyatdllib.ui import uicmd
uicmd.RegisterAppcommands(False, uicmd.APP_NAMESPACE)

FLAGS = flags.FLAGS


# pylint: disable=missing-docstring,too-many-public-methods
class SerializationTestCase(unitjest.TestCase):

  def testSha1Checksum(self):
    # echo "testing SHA1" > /tmp/sum_me && shasum /tmp/sum_me
    self.assertEqual(
      serialization.Sha1Checksum(b"testing SHA1\n"),
      "041c35b35c8c1c0fa18925b1c18e965c7efee06f")


if __name__ == '__main__':
  unitjest.main()
