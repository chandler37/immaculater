"""Defines Container, the superclass of Folder and Prj.

Folders contain Containers.  Prj contains Actions.
"""

from __future__ import annotations

from . import auditable_object
from . import common
from . import errors
from . import pyatdl_pb2

from google.protobuf import message
from typing import Any, Iterator, List, Tuple, Type
from typing_extensions import Protocol


class _SupportsDeletion(Protocol):
    is_deleted: bool


class Error(Exception):
  """Base class for this module's exceptions."""


class IllegalOperationError(Error):
  """The semantics don't allow what you're asking. Similar in spirit to ValueError."""


def YieldDescendantsThatAreNotDeleted(root: Any) -> Iterator[object]:
  """Yields undeleted descendants.

  Args:
    root: object
  Yields:
    object  # only if root is a Container
  """
  if hasattr(root, 'items'):
    for item in root.items:
      if not getattr(item, 'is_deleted', True):
        yield item
      YieldDescendantsThatAreNotDeleted(item)


class Container(auditable_object.AuditableObject):
  """A Container contains either Containers or Actions, but not every
  Container may contain Actions and not every Contain may contain Containers.

  Fields:
    uid: int
    ctime: float  # seconds since the epoch
    dtime: float|None  # seconds since the epoch, or None if not deleted.
    mtime: float  # seconds since the epoch
    is_deleted: bool
    name: str|None
    note: str|None
    items: [object]
  """

  @classmethod
  def TypesContained(cls) -> Tuple[Type[object]]:
    """Returns [type].  self.items will be restricted to items of the
    types in this list.
    """
    raise NotImplementedError

  def __init__(self, *, the_uid: int = None, items: list = None, name: str = None, note: str = '') -> None:
    super().__init__(the_uid=the_uid)
    self.items = list() if items is None else list(items)
    self.name = name
    self.note = note

  def MergeCommonFrom(self, pb: common.TypeHavingCommon) -> None:
    if not hasattr(self, 'name') and hasattr(self, 'note'):
      raise AssertionError("All Containers have a name and note.")
    self.__dict__['name'] = pb.common.metadata.name
    self.__dict__['note'] = pb.common.metadata.note
    super().MergeCommonFrom(pb)  # comes last to preserve mtime

  @classmethod
  def HasLiveDescendant(cls, item: Any) -> bool:
    if hasattr(item, 'items'):
      for subitem in item.items:
        if not subitem.is_deleted:
          return True
    return False

  def DeleteItemByUid(self, the_uid: int) -> None:
    old_length = len(self.items)
    self.items = [item for item in self.items if item.uid != the_uid]
    if old_length - 1 != len(self.items):
      raise AssertionError(f"Cannot find the item with UID {the_uid} to delete.")

  def PurgeDeleted(self) -> None:
    self.items[:] = [item for item in self.items if not item.is_deleted or self.HasLiveDescendant(item)]
    for item in self.items:
      if hasattr(item, 'PurgeDeleted'):
        item.PurgeDeleted()

  def DeleteCompleted(self) -> None:
    for item in self.items:
      if hasattr(item, 'is_complete') and item.is_complete:
        incomplete_descendant = False
        if hasattr(item, 'items'):
          for subitem in item.items:
            if hasattr(subitem, 'is_complete') and not subitem.is_complete and not subitem.is_deleted:
              incomplete_descendant = True
              break
        if not incomplete_descendant:
          item.is_deleted = True
      if hasattr(item, 'DeleteCompleted'):
        item.DeleteCompleted()

  def ContainersPreorder(self) -> Iterator[Tuple[Container, List[Container]]]:
    """Yields all containers, including itself, in a preorder traversal (itself first).

    Yields:
      (Container, [Container])  # the first element in the list is the leaf
    """
    yield (self, [])
    for item in self.items:
      if isinstance(item, Container):
        for f, path in item.ContainersPreorder():
          yield (f, list(path) + [self])

  def TrulyDeleteByUid(self, *, uid: int) -> bool:
    for i, item in enumerate(self.items):
      if item.uid != uid:
        if hasattr(item, 'TrulyDeleteByUid'):
          if getattr(item, 'TrulyDeleteByUid')(uid=uid):
            return True
        continue
      del self.items[i]
      return True
    return False

  def ForEachUidRecursively(self) -> Iterator[int]:
    for cc, _ in self.ContainersPreorder():
      yield cc.uid
      if cc is self:
        continue
      func = getattr(cc, 'ForEachUidRecursively', None)
      if func is not None:
        yield from func()

  def Projects(self) -> Iterator[Tuple[Container, List[Container]]]:
    """Iterates recursively over all projects contained herein.

    Each Prj is yielded with its path (leaf first). If this container is itself
    a project, it will be the only Prj yielded.

    Yields:
      (Prj, [Folder|Prj])
    """
    raise NotImplementedError(
      'Projects() is not yet implemented in the subclass.')

  def DeleteChild(self, child: _SupportsDeletion) -> None:
    """Iff the child has no undeleted descendants, deletes the child.

    Deletion just means changing the 'is_deleted' bit. TODO(chandler): Update dtime?

    Args:
      child: object
    Raises:
      IllegalOperationError: An undeleted descendant exists
      errors.DataError: child is not really a child
    """
    for item in self.items:
      if child is item:
        break
    else:
      raise errors.DataError(
        'The suppposed "child" is not really a child of this container.'
        ' self=%s child=%s'
        % (str(self), str(child)))
    for descendant in YieldDescendantsThatAreNotDeleted(child):
      raise IllegalOperationError(
        'Cannot delete because a descendant is not deleted.  descendant=\n%s'
        % str(descendant))
    child.is_deleted = True

  def CheckIsWellFormed(self) -> None:
    """A noop unless the programmer made an error.

    I.e., checks invariants.

    Raises:
      AssertionError: Find a new programmer.
    """
    for item in self.items:
      if True not in [isinstance(item, t) for t in self.TypesContained()]:
        raise AssertionError(
          'An item is of type %s which is not an acceptable type (%s)'
          % (str(type(item)), ', '.join(str(t) for t in self.TypesContained())))

  def AsProto(self, pb: message.Message) -> message.Message:
    """Returns: pb."""
    if not isinstance(pb, pyatdl_pb2.Common):
      raise TypeError
    super().AsProto(pb)
    assert self.uid == pb.uid
    if self.name:
      pb.metadata.name = self.name
    return pb
