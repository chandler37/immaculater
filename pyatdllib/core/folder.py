"""Defines Folder, an ordered list of projects or Folders -- i.e., [Prj|Folder]."""

from __future__ import absolute_import
from __future__ import annotations
from __future__ import unicode_literals
from __future__ import print_function

import six

from absl import flags  # type: ignore
from google.protobuf import message
from typing import Iterator, List, Tuple, Type, TypeVar, Union

from . import common
from . import container
from . import errors
from . import prj
from . import pyatdl_pb2

FLAGS = flags.FLAGS


T = TypeVar('T', bound='Folder')


class Folder(container.Container):
  """An ordered list of items, each item being a Prj or itself a Folder.

  Fields:
    uid: int
    name: None|str|unicode
    note: str|unicode
    items: [Folder|Prj]
    is_deleted: bool
    ctime: float  # seconds since the epoch
    dtime: float|None  # seconds since the epoch, or None if not deleted.
    mtime: float  # seconds since the epoch

  If you touch a field, you touch this object.  Use copy.deepcopy if
  you do not want to mutate the project.
  """

  __pychecker__ = 'unusednames=cls'

  @classmethod
  def TypesContained(cls) -> Tuple[Type[object]]:
    return (container.Container,)

  def __init__(self, the_uid: int = None, name: str = None, note: str = '', items: List[Union[Folder, prj.Prj]] = None) -> None:
    super().__init__(the_uid=the_uid, items=items, name=name)
    self.note = note

  def __unicode__(self) -> str:
    uid_str = '' if not FLAGS.pyatdl_show_uid else ' uid=%s' % self.uid
    return """
<folder%s is_deleted="%s" name="%s">
%s
</folder>
""".strip() % (
      uid_str, self.is_deleted, self.name,
      common.Indented('\n'.join(six.text_type(a) for a in self.items)))

  def IsDone(self) -> bool:
    return self.is_deleted

  def Projects(self) -> Iterator[Tuple[prj.Prj, List[container.Container]]]:
    """Override."""
    for c, path in self.ContainersPreorder():
      if isinstance(c, prj.Prj):
        yield (c, path)

  def AsProto(self, pb: message.Message = None) -> message.Message:
    if pb is None:
      pb = pyatdl_pb2.Folder()
    if not isinstance(pb, pyatdl_pb2.Folder):
      raise TypeError
    super().AsProto(pb.common)
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
  def DeserializedProtobuf(cls: Type[T], bytestring: bytes) -> T:
    """Deserializes a Folder from the given protocol buffer."""
    if not bytestring:
      raise errors.DataError("empty folder in the protocol buffer -- not even a UID is present")
    pb = pyatdl_pb2.Folder.FromString(bytestring)  # pylint: disable=no-member
    p = cls(the_uid=pb.common.uid,
            name=pb.common.metadata.name,
            note=pb.common.metadata.note)
    for pb_folder in pb.folders:
      p.items.append(
        cls.DeserializedProtobuf(pb_folder.SerializeToString()))
    for pb_project in pb.projects:
      p.items.append(
        prj.Prj.DeserializedProtobuf(pb_project.SerializeToString()))
    p.SetFieldsBasedOnProtobuf(pb.common)  # must be last
    return p
