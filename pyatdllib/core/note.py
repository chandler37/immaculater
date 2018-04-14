"""Defines NoteList, a global list of notes unattached to AuditableObjects.

For example, you can keep notes for your weekly review here.
"""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import six

import gflags as flags

from . import pyatdl_pb2

FLAGS = flags.FLAGS


class Error(Exception):
  """Base class for this module's exceptions."""


class NoSuchNameError(Error):
  """No Note by that name exists."""


class NoteList(object):
  """A dictionary of notes.

  Fields:
    notes: {unicode: unicode}
  """

  def __init__(self):
    self.notes = {}

  def __str__(self):
    return self.__unicode__().encode('utf-8') if six.PY2 else self.__unicode__()

  def __unicode__(self):
    return six.text_type(self.notes)

  def AsProto(self, pb=None):
    if pb is None:
      pb = pyatdl_pb2.NoteList()
    for name in sorted(self.notes):
      note = pb.notes.add()
      note.name = name
      note.note = self.notes[name]
    return pb

  @classmethod
  def DeserializedProtobuf(cls, bytestring):
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
