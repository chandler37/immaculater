"""Defines AuditableObject, something deletable with a ctime and an mtime etc."""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import os
import six
import time

import gflags as flags

from . import errors
from . import uid

flags.DEFINE_bool('pyatdl_show_uid', True,
                  'When displaying objects, include unique identifiers?')


def _FloatingPointTimestamp(microseconds_since_the_epoch):
  """Converts microseconds since the epoch to seconds since the epoch, or None for -1.

  Args:
    microseconds_since_the_epoch: int
  Returns:
    float|None
  """
  if microseconds_since_the_epoch == -1:
    return None
  return (microseconds_since_the_epoch // 10**6) + ((microseconds_since_the_epoch % 10**6) / 1e6)


def _Int64Timestamp(float_time):
  """Returns microseconds since the epoch given seconds since the epoch.

  Args:
    float_time: None|float  # seconds since the epoch
  Returns:
    int  # -1 if float_time is None or a positive int otherwise
  """
  epsilon = 1e-5
  if float_time is None or -1.0 - epsilon <= float_time <= -1.0 + epsilon:
    return -1
  if float_time < 0.0:
    raise errors.DataError(f"A timestamp was negative: {float_time}")
  assert float_time >= 0.0, float_time
  return int(float_time * 1e6)


class Error(Exception):
  """Base class for this module's exceptions."""


class IllegalNameError(Error):
  """Cannot create a name that matches UID syntax."""


class AuditableObject(object):
  """An auditable object has timestamps tracking creation, modification, and deletion.

  Fields:
    uid: int  # No two AuditableObjects have the same unique identifier
    ctime: float  # seconds since the epoch
    dtime: float|None  # seconds since the epoch, or None if not deleted.
    mtime: float  # seconds since the epoch
    is_deleted: bool

  Invariants:
    ctime == min(ctime, mtime, dtime if dtime is not None else +infinity)
    2**63 > uid >= -(2**63)
  """

  def __init__(self, the_uid=None):  # the_uid only for deserialization
    self.ctime = time.time()
    self.mtime = self.ctime
    self.dtime = None
    self.is_deleted = False
    # If we are deserializing, we could call SetFieldsBasedOnProtobuf and overwrite this value. UIDs are inexpensive
    # and we don't care if we waste some during deserialization. But the DataError for mergeprotobufs' sake is
    # important, so we take care to set the_uid in the __init__ method when deserializing.
    if the_uid is None:
      try:
        self.uid = uid.singleton_factory.NextUID()
      except errors.DataError as e:
        raise errors.DataError(f"In the process of instantiating an object of type {type(e)}: {e}")
    else:
      uid.singleton_factory.NoteExistingUID(the_uid)
      self.uid = the_uid

  def NoteModification(self):
    """Updates mtime."""
    self.__dict__['mtime'] = time.time()
    if os.environ.get('DJANGO_DEBUG') == "True":
      assert self.__dict__['mtime'] >= self.__dict__['ctime'], str(self.__dict__)
    # The above assertion led to this: AssertionError:
    # {'max_seconds_before_review': 604800.0, 'is_deleted': False, 'uid': 62L,
    # 'items': [], 'dtime': None, 'is_active': False, 'name': u'inactive prj',
    # 'note': u'', '_last_review_epoch_sec': 0, 'mtime': 1512402677.768133,
    # 'default_context_uid': None, 'is_complete': False,
    # 'ctime': 1512402694.178005}
    #
    # which I got by creating a project and immediately clicking through to it and deactivating it. This was on
    # localhost. This is likely now impossible to reproduce because the culprit was probably calling NoteModification
    # after setting timestamps, which was fixed.

  # NOTE(chandler): __setattr__ attempts to enforce invariants, including the
  # mtime timestamp, but __setattr__ is flawed, so note: modification of a list
  # won't be caught. In such cases, we have to remember to change mtime
  # manually by calling:
  #
  #   NoteModification()
  #
  # (Or we could subclass 'list' and avoid use of bare lists.)
  #
  # E.g., if you add a project to self.items, you must call NoteModification.
  def __setattr__(self, name, value):
    if name == 'name':
      if value is not None and value.startswith('uid='):
        raise IllegalNameError('Names starting with "uid=" are prohibited.')
    self.__dict__[name] = value
    if name == 'is_deleted' and value:
      self.__dict__['dtime'] = time.time()
    if name != 'mtime':
      self.NoteModification()

  def AsProto(self, pb):
    """Serializes this object by mutating pb.

    Args:
      pb: pyatdl_pb2.Common
    Returns:
      pb
    Raises:
      errors.DataError
    """
    pb.is_deleted = self.is_deleted
    pb.timestamp.ctime = _Int64Timestamp(self.ctime)
    pb.timestamp.dtime = _Int64Timestamp(self.dtime)
    pb.timestamp.mtime = _Int64Timestamp(self.mtime)
    pb.uid = self.uid
    return pb

  def SetFieldsBasedOnProtobuf(self, pb):
    """Overwrites fields based on the given protobuf. You must call this at the very last.

    At the very last because any manipulation of this object afterwards will overwrite mtime.

    Args:
      pb: pyatdl_pb2.Common
    Returns:
      None

    """
    self.__dict__['is_deleted'] = pb.is_deleted
    self.__dict__['ctime'] = _FloatingPointTimestamp(pb.timestamp.ctime)
    self.__dict__['dtime'] = _FloatingPointTimestamp(pb.timestamp.dtime)
    # self.__dict__['mtime'] must be set last because setting anything else triggers NoteModification which overwrites
    # it based on time.time().
    if pb.uid == 0 or pb.uid < -2**63 or pb.uid >= 2**63:
      raise errors.DataError(f"Illegal UID value {pb.uid} from {pb}: not in range [-2**63, 0) or (0, 2**63)")
    if self.__dict__['uid'] != pb.uid:
      uid.singleton_factory.NoteExistingUID(pb.uid)
    self.__dict__['uid'] = pb.uid
    self.__dict__['mtime'] = _FloatingPointTimestamp(pb.timestamp.mtime)  # because __setattr__ tramples mtime, this comes last
    if os.environ.get('DJANGO_DEBUG') == "True":
      # See comment above for why we don't run this in production.
      assert self.__dict__['mtime'] >= self.__dict__['ctime'], str(self.__dict__)

  def __str__(self):
    return self.__unicode__().encode('utf-8') if six.PY2 else self.__unicode__()
