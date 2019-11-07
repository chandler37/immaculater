"""Defines Container, the superclass of Folder and Prj.

Folders contain Containers (but not CtxLists).  Prj contains Actions.
"""

from . import auditable_object
from . import errors


class Error(Exception):
  """Base class for this module's exceptions."""


class IllegalOperationError(Error):
  """The semantics don't allow what you're asking. Similar in spirit to ValueError."""


def YieldDescendantsThatAreNotDeleted(root):
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
    items: [object]
  """

  @classmethod
  def TypesContained(cls):
    """Returns [type].  self.items will be restricted to items of the
    types in this list.
    """
    raise NotImplementedError

  def __init__(self, the_uid=None, items=None):  # items=[] is a python foible
    super().__init__(the_uid=the_uid)
    if items is None:
      self.items = []
    else:
      self.items = items

  @classmethod
  def HasLiveDescendant(cls, item):
    if hasattr(item, 'items'):
      for subitem in item.items:
        if not subitem.is_deleted:
          return True
    return False

  def PurgeDeleted(self):
    self.items = [item for item in self.items
                  if not item.is_deleted or self.HasLiveDescendant(item)]
    for item in self.items:
      if hasattr(item, 'PurgeDeleted'):
        item.PurgeDeleted()

  def DeleteCompleted(self):
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

  def ContainersPreorder(self):
    """Yields all containers, including itself, in a preorder traversal (itself first).

    Yields:
      (Container, [Container])  # the first element in the list is the leaf
    """
    yield (self, [])
    for item in self.items:
      if isinstance(item, Container):
        for f, path in item.ContainersPreorder():
          yield (f, list(path) + [self])

  def Projects(self):
    """Iterates recursively over all projects contained herein.

    Each Prj is yeilded with its path (leaf first). If this container is itself
    a project, it will be the only Prj yielded.

    Yields:
      (Prj, [Folder|Prj])
    """
    raise NotImplementedError(
      'Projects() is not yet implemented in the subclass.')

  def DeleteChild(self, child):
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

  def CheckIsWellFormed(self):
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

  def AsProto(self, pb):
    """Args: pb: pyatdl_pb2.Common.  Returns: pb."""
    super().AsProto(pb)
    assert self.uid == pb.uid
    return pb
