"""Routines common to all unittests.

All our unittests inherit from this module's TestCase instead of
unittest.TestCase directly.
"""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import difflib
import six
import unittest

import gflags as flags

from . import action
from . import ctx
from . import prj

FLAGS = flags.FLAGS


def FullPrj():
  """Returns a Prj with two Actions, one in a Ctx.

  Returns:
    Prj
  """
  store_ctx = ctx.Ctx(name='the store')
  a0 = action.Action(name='Buy milk')
  a1 = action.Action(name='Oranges', context=store_ctx)
  rv = prj.Prj(name='myname', items=[a0, a1])
  return rv


# pylint: disable=too-few-public-methods
class TestCase(unittest.TestCase):
  """Even better than unittest.TestCase."""

  def _Python3Munging(self, list_of_strings):
    def Munge(string):
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

  def _AssertEqualWithDiff(self, gold, actual):
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
      

def main():
  """Serves the same purpose as unittest.main."""
  # Let's avoid "RuntimeWarning: Trying to access flag pyatdl_show_uid before
  # flags were parsed. This will raise an exception in the future.":
  FLAGS([])
  unittest.main()
