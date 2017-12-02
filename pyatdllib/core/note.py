"""Defines NoteList, a global list of notes unattached to AuditableObjects.

For example, you can keep notes for your weekly review here.
"""

import gflags as flags

from . import auditable_object
from . import common
from . import container
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
    return unicode(self).encode('utf-8')

  def __unicode__(self):
    return unicode(self.notes)

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
