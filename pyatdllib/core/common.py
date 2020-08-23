"""Utilities used across multiple modules."""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

from . import pyatdl_pb2

from typing import Optional, Union, overload
from typing_extensions import Protocol


def Indented(txt: str, num_indents: int = 1, num_spaces: int = 4) -> str:
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


@overload
def FloatingPointTimestamp(microseconds_since_the_epoch: int, zero_value: float) -> float:
  ...


@overload
def FloatingPointTimestamp(microseconds_since_the_epoch: int, zero_value: None = None) -> Optional[float]:
  ...


def FloatingPointTimestamp(microseconds_since_the_epoch: int, zero_value: Optional[float] = None) -> Optional[float]:
  """Converts microseconds since the epoch to seconds since the epoch, or None for -1 or 0.

  Args:
    microseconds_since_the_epoch: int
  Returns:
    float|None
  """
  if microseconds_since_the_epoch in (-1, 0):
    return zero_value
  return (microseconds_since_the_epoch // 10**6) + ((microseconds_since_the_epoch % 10**6) / 1e6)


TypeHavingCommon = Union[
  pyatdl_pb2.Action,
  pyatdl_pb2.Context,
  pyatdl_pb2.ContextList,
  pyatdl_pb2.Folder,
  pyatdl_pb2.Project,
]


def MaxTimeOfPb(action_prj_etc: TypeHavingCommon) -> float:
  def ToFractionalEpochSeconds(x) -> float:
    return FloatingPointTimestamp(x, zero_value=0.0)

  ts = action_prj_etc.common.timestamp
  return max(
    ToFractionalEpochSeconds(ts.ctime),
    ToFractionalEpochSeconds(ts.mtime),
    ToFractionalEpochSeconds(ts.dtime))


class SupportsTimestamps(Protocol):
    ctime: float
    mtime: float
    dtime: Optional[float]
