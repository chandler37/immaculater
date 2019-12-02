"""Utilities used across multiple modules."""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function


def Indented(txt, num_indents=1, num_spaces=4):
  """Returns txt indented across multiple lines.

  Args:
    txt: basestring
    num_indents: int
    num_spaces: int
  Returns:
    basestring
  """
  if not txt.strip():
    return ''
  lines = txt.splitlines()
  indent = ' ' * num_spaces * num_indents
  return '\n'.join(indent + line for line in lines)


def FloatingPointTimestamp(microseconds_since_the_epoch, zero_value=None):
  """Converts microseconds since the epoch to seconds since the epoch, or None for -1 or 0.

  Args:
    microseconds_since_the_epoch: int
  Returns:
    float|None
  """
  if microseconds_since_the_epoch == -1:
    return zero_value
  return (microseconds_since_the_epoch // 10**6) + ((microseconds_since_the_epoch % 10**6) / 1e6)


def MaxTimeOfPb(action_prj_etc):
  def ToFractionalEpochSeconds(x):
    return FloatingPointTimestamp(x, zero_value=0.0)

  ts = action_prj_etc.common.timestamp
  return max(
    ToFractionalEpochSeconds(ts.ctime),
    ToFractionalEpochSeconds(ts.mtime),
    ToFractionalEpochSeconds(ts.dtime))
