"""Defines Folder, an ordered list of projects or Folders -- i.e., [Prj|Folder]."""

from __future__ import absolute_import
from __future__ import annotations
from __future__ import unicode_literals
from __future__ import print_function

import six

from absl import flags  # type: ignore
from google.protobuf import message
from typing import Callable, Iterator, List, Optional, Tuple, Type, TypeVar, Union

from . import action
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

  def MergeFromProto(self,
                     other: pyatdl_pb2.Folder,
                     *,
                     truly_delete_by_uid,
                     find_existing_folder_by_uid: Callable[[int], Optional[Tuple[Folder, List[Folder]]]],
                     find_existing_project_by_uid: Callable[[int], Optional[Tuple[container.Container, List[Folder]]]],
                     find_existing_action_by_uid: Callable[[int], Optional[Tuple[action.Action, prj.Prj]]],
                     find_existing_project_by_uid_in_remote) -> None:
    if not isinstance(other, pyatdl_pb2.Folder):
      raise TypeError

    if common.MaxTimeOfPb(other) > common.MaxTime(self):
      self.MergeCommonFrom(other)

    def HandleFolders() -> None:
      for other_subfolder in other.folders:
        def AddOtherSubfolderHere():
          new_item = type(self).DeserializedProtobuf(
            other_subfolder.SerializeToString())
          for uu in new_item.ForEachUidRecursively():
            truly_delete_by_uid(uid=uu)
          self.items.append(new_item)
          self.NoteModification()

        existing_folder_and_path = find_existing_folder_by_uid(other_subfolder.common.uid)
        if existing_folder_and_path is None:
          AddOtherSubfolderHere()
        else:
          existing_folder, existing_path = existing_folder_and_path
          existing_folder.MergeFromProto(
            other_subfolder,
            truly_delete_by_uid=truly_delete_by_uid,
            find_existing_folder_by_uid=find_existing_folder_by_uid,
            find_existing_project_by_uid=find_existing_project_by_uid,
            find_existing_action_by_uid=find_existing_action_by_uid,
            find_existing_project_by_uid_in_remote=find_existing_project_by_uid_in_remote)
          parent_folder = existing_path[0]
          if parent_folder.uid != other.common.uid:
            for i, item in enumerate(parent_folder.items):
              if isinstance(item, Folder) and item.uid == existing_folder.uid:
                del parent_folder.items[i]  # TODO(chandler37): DRY up using truly_delete_by_uid?
                parent_folder.NoteModification()
                break
            else:
              raise AssertionError(f"Cannot find the folder to delete: existing_folder.uid={existing_folder.uid}")
            # OK, we deleted the copy that was in the wrong place. Now add it back inside the correct Folder:
            AddOtherSubfolderHere()
            # TODO(chandler37): make a test case where the folder is changed such as (1) by adding/deleting a prj and
            # (2) by adding/deleting a subfolder

    def HandleProjects() -> None:
      for other_project in other.projects:
        # If it is new, add it; if it is old, merge it.
        existing_project_and_path = find_existing_project_by_uid(other_project.common.uid)
        if existing_project_and_path is None:
          existing_project, path = None, None
        else:
          existing_project, path = existing_project_and_path
        if existing_project is None:
          new_prj_item = prj.Prj.DeserializedProtobuf(
            other_project.SerializeToString())
          for uu in new_prj_item.ForEachUidRecursively():
            truly_delete_by_uid(uid=uu)
          self.items.append(new_prj_item)
          self.NoteModification()
          continue
        assert isinstance(path, list)
        old_folder_in_db = path[0]  # The path is leaf first.
        old_folder_path = find_existing_project_by_uid_in_remote(other_project.common.uid)
        assert isinstance(old_folder_path, list)
        moved = old_folder_path and path and old_folder_path[0].common.uid != path[0]
        if not isinstance(existing_project, prj.Prj):
          raise AssertionError(
            "mergeprotobufs: Either there is a bug here on the server, or the client reused a project's UID for a folder")
        existing_project.MergeFromProto(
          other_project,
          find_existing_action_by_uid=find_existing_action_by_uid)
        if moved:
          # remove from the old folder: TODO(chandler): DRY up with a new method DeleteItemByUid() (or can we use
          # TrulyDeleteByUid?)
          for i, item in enumerate(old_folder_in_db.items):
            if isinstance(item, prj.Prj) and item.uid == other_project.common.uid:
              del old_folder_in_db.items[i]
              old_folder_in_db.NoteModification()
              break
          else:
            raise AssertionError(f"error moving a project(uid={other_project.common.uid}) during mergeprotobufs")
          # add here:
          self.items.append(
            prj.Prj.DeserializedProtobuf(
              other_project.SerializeToString()))
          self.NoteModification()

    # The order of these calls shouldn't matter:
    HandleFolders()
    HandleProjects()

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
