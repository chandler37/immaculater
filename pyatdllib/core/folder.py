"""Defines Folder, an ordered list of projects or Folders -- i.e., [Prj|Folder]."""

import gflags as flags

from . import common
from . import container
from . import prj
from . import pyatdl_pb2

FLAGS = flags.FLAGS


class Folder(container.Container):
  """An ordered list of items, each item being a Prj or itself a Folder.

  Fields:
    uid: int
    name: None|str|unicode
    note: str|unicode
    items: [Folder|Prj]
    is_deleted: bool
    ctime: int  # seconds since the epoch
    dtime: int|None  # seconds since the epoch, or None if not deleted.
    mtime: int  # seconds since the epoch

  If you touch a field, you touch this object.  Use copy.deepcopy if
  you do not want to mutate the project.
  """

  __pychecker__ = 'unusednames=cls'
  @classmethod
  def TypesContained(cls):
    return (container.Container,)

  # items=[] is a python foible but strings are immutable:
  def __init__(self, the_uid=None, name=None, note='', items=None):
    super(Folder, self).__init__(the_uid=the_uid, items=items)
    self.name = name
    self.note = note

  def __str__(self):
    return unicode(self).encode('utf-8')

  def __unicode__(self):
    uid_str = u'' if not FLAGS.pyatdl_show_uid else u' uid=%s' % self.uid
    return u"""
<folder%s is_deleted="%s" name="%s">
%s
</folder>
""".strip() % (
      uid_str, self.is_deleted, self.name,
      common.Indented(u'\n'.join(unicode(a) for a in self.items)))

  def Projects(self):
    """Override."""
    for c, path in self.ContainersPreorder():
      if isinstance(c, prj.Prj):
        yield (c, path)

  def AsProto(self, pb=None):
    if pb is None:
      pb = pyatdl_pb2.Folder()
    # pylint: disable=maybe-no-member
    super(Folder, self).AsProto(pb.common)
    pb.common.metadata.name = self.name
    if self.note:
      pb.common.metadata.note = self.note
    for i in self.items:
      if isinstance(i, prj.Prj):
        i.AsProto(pb.projects.add())
      else:
        assert isinstance(i, Folder), (type(i), str(i))
        i.AsProto(pb.folders.add())
    return pb

  @classmethod
  def DeserializedProtobuf(cls, bytestring):
    """Deserializes a Folder from the given protocol buffer.

    Args:
      bytestring: str
    Returns:
      Folder
    """
    assert bytestring
    pb = pyatdl_pb2.Folder.FromString(bytestring)  # pylint: disable=no-member
    p = cls(the_uid=pb.common.uid,
            name=pb.common.metadata.name,
            note=pb.common.metadata.note)
    p.SetFieldsBasedOnProtobuf(pb.common)
    for pb_folder in pb.folders:
      p.items.append(
        cls.DeserializedProtobuf(pb_folder.SerializeToString()))
    for pb_project in pb.projects:
      p.items.append(
        prj.Prj.DeserializedProtobuf(pb_project.SerializeToString()))
    p.items.sort(key=lambda i: i.uid)
    return p
