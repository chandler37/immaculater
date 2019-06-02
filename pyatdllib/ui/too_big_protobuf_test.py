"""Unittests for module 'immaculater' that cannot live peaceably with immaculater_test.

This unittest is separate because once you call SetAllowOversizeProtos(True)
you cannot change it.
"""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import pipes

import gflags as flags  # https://github.com/gflags/python-gflags

from pyatdllib.ui import serialization
from pyatdllib.ui import test_helper

FLAGS = flags.FLAGS


class TooBigProtobufTestCase(test_helper.TestHelper):
  def setUp(self):
    super().setUp()

    FLAGS.pyatdl_allow_infinite_memory_for_protobuf = True

  def testTooBigToSaveError(self):
    FLAGS.pyatdl_allow_infinite_memory_for_protobuf = False
    save_path = self._CreateTmpFile('')
    inputs = ['loadtest -n 100',
              'save %s' % pipes.quote(save_path)
              ]
    self.helpTest(inputs, serialization.TooBigToSaveError)


if __name__ == '__main__':
  test_helper.main()
