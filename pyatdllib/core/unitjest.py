"""Routines common to all unittests.

All our unittests inherit from this module's TestCase instead of
unittest.TestCase directly.
"""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import difflib
import os
import six
import tempfile
import unittest

from absl import flags  # type: ignore

from google.protobuf import message
from google.protobuf import text_format  # type: ignore

from typing import IO, List

from . import action
from . import prj

FLAGS = flags.FLAGS


def FullPrj() -> prj.Prj:
  """Returns a Prj with two Actions, one in a Ctx."""
  store_ctx_uid = -2**63
  a0 = action.Action(name='Buy milk')
  a1 = action.Action(name='Oranges', ctx_uid=store_ctx_uid)
  rv = prj.Prj(name='myname', items=[a0, a1])
  return rv


# pylint: disable=too-few-public-methods
class TestCase(unittest.TestCase):
  """Even better than unittest.TestCase."""

  def setUp(self) -> None:
    FLAGS(['required_program_name_arg'])
    FLAGS.set_gnu_getopt(False)
    self._tempfilenames: List[str] = []

  def tearDown(self) -> None:
    for name in self._tempfilenames:
      try:
        os.remove(name)
      except OSError:
        pass

  def _NamedTempFile(self) -> IO[bytes]:
    tf = tempfile.NamedTemporaryFile(
      prefix='tmppyatdlunitjest',
      delete=False)
    self._tempfilenames.append(tf.name)
    self._tempfilenames.append(tf.name + '.bak')
    return tf

  def _CreateTmpFile(self, contents: str) -> str:
    """Creates a new temporary file (that will never be removed) and returns the
    name of that file.

    Args:
      contents: str
    Returns:
      str
    """
    with tempfile.NamedTemporaryFile(prefix='tmppyatdlunitjest', delete=False) as tf:
      tempfilename = tf.name
      self._tempfilenames.append(tf.name)
      self._tempfilenames.append(tf.name + '.bak')
    with open(tempfilename, 'wb') as f:
      f.write(contents.encode('utf-8'))
    return tempfilename

  def assertProtosEqual(self, pb1: message.Message, pb2: message.Message) -> None:
    if pb1.SerializeToString() != pb2.SerializeToString():
      self.assertEqual(
        text_format.MessageToString(pb1),
        text_format.MessageToString(pb2))

  def assertProtoTextuallyEquals(self, pb: message.Message, text: str) -> None:
    self.assertEqual(text.strip(), text_format.MessageToString(pb).strip())

  def _Python3Munging(self, list_of_strings: List[str]) -> List[str]:
    def Munge(string: str) -> str:
      if six.PY3:
        return string.replace("u'", "'")
      return string
    test_str = 'u\'\u2019til\', u\'1\''
    assert len(test_str) == len('u\'.til\', u\'1\'')
    if six.PY3:
      assert Munge(test_str) == "'\u2019til', '1'", Munge(test_str)
    else:
      assert Munge(test_str) == test_str
    return [Munge(s) for s in list_of_strings]

  def _AssertEqualWithDiff(self, gold: List[str], actual: str) -> None:
    """Calls assertEqual() with intelligible diffs so that you can easily
    understand and update the unittest.

    Args:
      gold: [str]  # expected output
      actual: str
    """
    gold = self._Python3Munging(gold)
    diffstr = '\n'.join(difflib.context_diff(gold, actual, n=5))
    try:
      self.assertEqual(
        gold, actual,
        'Diff with left=golden, right=actually-printed is as follows (len left=%s,'
        ' len right=%s):\n%s'
        % (len(gold), len(actual), str(diffstr)))
    except UnicodeEncodeError:
      self.assertEqual(
        gold, actual,
        'Diff with left=golden, right=actually-printed is as follows (len left=%s,'
        ' len right=%s):\n%s'
        % (len(gold), len(actual), six.text_type(diffstr)))


def main() -> None:
  """Serves the same purpose as unittest.main."""
  unittest.main()
