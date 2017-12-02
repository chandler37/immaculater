"""Routines common to all unittests.

All our unittests inherit from this module's TestCase instead of
unittest.TestCase directly.
"""

import difflib
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

  def _AssertEqualWithDiff(self, gold, actual):
    """Calls assertEqual() with intelligible diffs so that you can easily
    understand and update the unittest.

    Args:
      gold: str  # expected output
      actual: str
    """
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
        u'Diff with left=golden, right=actually-printed is as follows (len left=%s,'
        u' len right=%s):\n%s'
        % (len(gold), len(actual), unicode(diffstr)))
      

def main():
  """Serves the same purpose as unittest.main."""
  # Let's avoid "RuntimeWarning: Trying to access flag pyatdl_show_uid before
  # flags were parsed. This will raise an exception in the future.":
  FLAGS([])
  unittest.main()
