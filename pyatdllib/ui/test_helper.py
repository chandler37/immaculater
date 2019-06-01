"""Common code for immaculater_test and too_big_protobuf_test inheriting from unitjest.TestCase."""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import copy
import random
import six
import time
import zlib

import gflags as flags  # https://github.com/gflags/python-gflags
from gflags import _helpers

from pyatdllib.ui import immaculater
from pyatdllib.core import tdl
from pyatdllib.core import uid
from pyatdllib.core import unitjest

immaculater.RegisterUICmds(cloud_only=False)

FLAGS = flags.FLAGS


class TestHelper(unitjest.TestCase):
  def setUp(self):
    super().setUp()

    random.seed(3737123)

    FLAGS.pyatdl_randomize_uids = False

    assert _helpers.GetHelpWidth
    _helpers.GetHelpWidth = lambda: 180
    uid.ResetNotesOfExistingUIDs()

    # There is a gflags.TextWrap glitch re: the line '-a,--[no]show_all:
    # Additionally lists everything, even hidden objects, overriding the view
    # filter' so we replace TextWrap.
    def MyTextWrap(text, length=None, indent='', firstline_indent=None, tabs='    '):  # pylint: disable=unused-argument
      return text

    flags.TextWrap = MyTextWrap
    FLAGS.pyatdl_allow_exceptions_in_batch_mode = True
    FLAGS.pyatdl_separator = '/'
    FLAGS.pyatdl_break_glass_and_skip_wellformedness_check = False
    FLAGS.pyatdl_give_full_help_for_uicmd = False
    FLAGS.pyatdl_paranoia = True
    FLAGS.pyatdl_allow_command_line_comments = False
    FLAGS.pyatdl_zlib_compression_level = 6
    FLAGS.pyatdl_show_uid = False
    FLAGS.seed_upon_creation = False
    FLAGS.no_context_display_string = '<none>'
    FLAGS.time_format = '%Y/%m/%d-%H:%M:%S'
    FLAGS.timezone = 'US/Eastern'
    self.saved_time = time.time
    time.time = lambda: 36
    self.todolist = tdl.ToDoList()
    time.time = self.saved_time
    self.saved_input = immaculater._Input  # pylint: disable=protected-access
    self.saved_print = immaculater._Print  # pylint: disable=protected-access
    self.maxDiff = None  # pylint: disable=invalid-name
    tf = self._NamedTempFile()
    FLAGS.database_filename = tf.name
    tf.close()
    self.saved_decompress = zlib.decompress

  def tearDown(self):
    super().tearDown()
    zlib.decompress = self.saved_decompress
    time.time = self.saved_time
    immaculater._Input = self.saved_input  # pylint: disable=protected-access
    immaculater._Print = self.saved_print  # pylint: disable=protected-access

  def helpTest(self, inputs, golden_outputs_or_exception):
    """Feeds the inputs to the beast and verifies that the output
    matches the golden output.

    Args:
      inputs: [basestring]
      golden_outputs_or_exception: Class|[basestring]  # a subclass of Exception will make us assert that it is raised
    """
    inputs = copy.copy(inputs)

    def MyRawInput(unused_prompt=''):  # pylint: disable=unused-argument
      if not inputs:
        raise EOFError('immaculater_test1')
      return inputs.pop(0)

    printed = []

    def MyPrint(s):
      printed.append(six.text_type(s))

    immaculater._Input = MyRawInput  # pylint: disable=protected-access
    immaculater._Print = MyPrint  # pylint: disable=protected-access

    def HTMLEscaper(s):
      return s.replace('&nbsp;', '&amp;nbsp;')

    def Run():
      immaculater.MutateToDoListLoop(self.todolist, html_escaper=HTMLEscaper)

    if isinstance(golden_outputs_or_exception, list):
      Run()
      self._AssertEqualWithDiff(golden_outputs_or_exception, printed)
    else:
      with self.assertRaises(golden_outputs_or_exception):
        Run()


def main():
  unitjest.main()
