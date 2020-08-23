"""Defines NoteList, a global list of notes unattached to AuditableObjects.

For example, you can keep notes for your weekly review here.
"""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import six

from absl import flags  # type: ignore
from google.protobuf import message
from typing import Dict, Type, TypeVar

from . import pyatdl_pb2

FLAGS = flags.FLAGS


class Error(Exception):
  """Base class for this module's exceptions."""


class NoSuchNameError(Error):
  """No Note by that name exists."""


T = TypeVar('T', bound='NoteList')


class NoteList(object):
  """A dictionary of notes.

  Fields:
    notes: {unicode: unicode}
  """

  def __init__(self) -> None:
    self.notes: Dict[str, str] = {}

  def __str__(self):
    return self.__unicode__().encode('utf-8') if six.PY2 else self.__unicode__()

  def __unicode__(self) -> str:
    return six.text_type(self.notes)

  def AsProto(self, pb: message.Message = None) -> message.Message:
    if pb is None:
      pb = pyatdl_pb2.NoteList()
    if not isinstance(pb, pyatdl_pb2.NoteList):
      raise TypeError
    for name in sorted(self.notes):
      note = pb.notes.add()
      note.name = name
      note.note = self.notes[name]
    return pb

  @classmethod
  def DeserializedProtobuf(cls: Type[T], bytestring: bytes) -> T:
    """Deserializes a NoteList from the given protocol buffer.

    Args:
      bytestring: str
    Returns:
      NoteList
    """
    pb = pyatdl_pb2.NoteList.FromString(bytestring)  # pylint: disable=no-member
    nl = cls()
    for pbn in pb.notes:
      nl.notes[pbn.name] = pbn.note
    return nl
