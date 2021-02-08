"""Defines ToDoList, which consists of an inbox (a Prj), a root Folder, and a
list of Contexts.

An end user thinks of the totality of their data as a ToDoList.
"""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

from dateutil import tz
from typing import Callable, Dict, Iterator, List, Optional, Set, Tuple, Type, TypeVar, Union, cast
import datetime
import heapq
import six
import time

from absl import flags  # type: ignore

from google.protobuf.pyext._message import SetAllowOversizeProtos  # type: ignore

from . import action
from . import common
from . import container
from . import ctx
from . import errors
from . import folder
from . import note
from . import prj
from . import pyatdl_pb2
from . import uid

flags.DEFINE_string('inbox_project_name', 'inbox',
                    'Name of the top-level "inbox" project')
flags.DEFINE_bool(
    'pyatdl_break_glass_and_skip_wellformedness_check', False,
    'This is very dangerous! We skip checks that make sure everything is '
    'well-formed. If you serialize (i.e., save) your to-do list without '
    'such checks, you may not be able to deserialize (i.e., load) it later.')
flags.DEFINE_bool(
    'pyatdl_allow_infinite_memory_for_protobuf', False,
    'There is a 64MiB memory limit otherwise.')
flags.DEFINE_string('pyatdl_separator', '/',
                    'In Folder names, which character separates parent from child?')

FLAGS = flags.FLAGS


class Error(Exception):
  """Base class for this module's exceptions."""


class NoSuchNameError(Error):
  """Bad name given; no such Action/Project/Context/Folder/Note exists."""


class NoSuchParentFolderError(Error):
  """No parent folder by that name exists."""


class DuplicateContextError(Error):
  """A Context by that name already exists."""


T = TypeVar('T', bound='ToDoList')


class ToDoList(object):
  """The totality of one end user's data, their projects and actions.

  Fields:
    root: Folder
    inbox: Prj
    ctx_list: CtxList
    note_list: NoteList  # every auditable object has its own note; these are global
  """

  def __init__(self,
               inbox: prj.Prj = None,
               root: folder.Folder = None,
               ctx_list: ctx.CtxList = None,
               note_list: note.NoteList = None) -> None:
    self.inbox = inbox if inbox is not None else prj.Prj(name=FLAGS.inbox_project_name, the_uid=uid.INBOX_UID)
    if self.inbox.ctime is None or self.inbox.mtime is None:
      raise errors.DataError("ctime and mtime are required")
    if self.inbox.uid != uid.INBOX_UID:
      raise errors.DataError(f"Inbox UID is not {uid.INBOX_UID}, it is {self.inbox.uid}")
    self.root = root if root is not None else folder.Folder(name='', the_uid=uid.ROOT_FOLDER_UID)
    if self.root.uid != uid.ROOT_FOLDER_UID:
      raise errors.DataError(f"Root folder UID is not {uid.ROOT_FOLDER_UID}, it is {self.root.uid}")
    if self.inbox.ctime is None or self.inbox.mtime is None:
      raise errors.DataError("ctime and mtime are required")
    self.ctx_list = ctx_list if ctx_list is not None else ctx.CtxList()
    self.note_list = note_list if note_list is not None else note.NoteList()

  def __str__(self):
    return self.__unicode__().encode('utf-8') if six.PY2 else self.__unicode__()

  def __unicode__(self) -> str:
    inbox_uid_str = '' if not FLAGS.pyatdl_show_uid else ' uid=%s' % self.inbox.uid
    todos_uid_str = '' if not FLAGS.pyatdl_show_uid else ' uid=%s' % self.root.uid
    t = """
<todolist%s>
    <inbox%s>
%s
    </inbox>
%s
    <contexts>
%s
    </contexts>
</todolist>
""" % (todos_uid_str,
       inbox_uid_str,
       common.Indented(six.text_type(self.inbox), 2),
       common.Indented(six.text_type(self.root), 1),
       common.Indented(six.text_type(self.ctx_list), 2))
    return t.strip()

  def AsTaskPaper(self,
                  lines: List[str],
                  show_project: Callable[[prj.Prj], bool] = lambda _: True,
                  show_action: Callable[[action.Action], bool] = lambda _: True,
                  show_note: Callable[[str], bool] = lambda _: True,
                  hypertext_prefix: str = None,
                  html_escaper: Callable[[str], str] = None) -> None:
    """Appends lines of text to lines in TaskPaper format.

    Args:
      lines: [unicode]
      show_project: lambda Prj: bool
      show_action: lambda Action: bool
      show_note: lambda str: bool
      hypertext_prefix: None|unicode  # URL fragment e.g. "/todo". if None,
                                      # output plain text
      html_escaper: lambda unicode: unicode
    Returns:
      None
    """
    def ContextName(context_uid: int) -> str:
      for i in self.ctx_list.items:
        if i.uid == context_uid:
          return six.text_type(i.name)
      return 'impossible error so file a bug report please'

    pairs = []
    for p, path in self.Projects():
      if show_project(p):
        pairs.append((p, path))

    def Key(pair: Tuple[prj.Prj, List[folder.Folder]]) -> str:
      p, path = pair
      if p.uid == 1:  # inbox
        return ""
      prefix = FLAGS.pyatdl_separator.join(f.name for f in reversed(path))
      return FLAGS.pyatdl_separator.join([prefix, p.name])

    pairs.sort(key=Key)
    # TODO(chandler): make it possible to sort chronologically as well as what we do now, which is sorting
    # alphabetically.
    for p, path in pairs:
      prefix = FLAGS.pyatdl_separator.join(f.name for f in reversed(path))
      if prefix and not prefix.endswith(FLAGS.pyatdl_separator):
        prefix += six.text_type(FLAGS.pyatdl_separator)
      if p.is_deleted:
        prefix = '@deleted ' + prefix
      if p.is_complete:
        prefix = '@done ' + prefix
      if not p.is_active:
        prefix = '@inactive ' + prefix
      p.AsTaskPaper(lines,
                    context_name=ContextName,
                    project_name_prefix=prefix,
                    show_action=show_action,
                    show_note=show_note,
                    hypertext_prefix=hypertext_prefix,
                    html_escaper=html_escaper)

  def PurgeDeleted(self) -> None:
    self.inbox.PurgeDeleted()
    self.root.PurgeDeleted()
    self.ctx_list.PurgeDeleted()

  def DeleteCompleted(self) -> None:
    self.inbox.DeleteCompleted()
    self.root.DeleteCompleted()

  def Projects(self) -> Iterator[Tuple[prj.Prj, List[folder.Folder]]]:
    """Returns all projects, including the /inbox project.

    The /inbox project is distinguished by an empty path (i.e., [Folder] is []).

    Yields:
      (prj.Prj, [Folder]).  # The path is leaf first.
    """
    for p, path in self.ContainersPreorder():
      if not isinstance(p, prj.Prj):
        continue
      for element in path:
        if not isinstance(element, folder.Folder):
          raise TypeError
      yield (p, cast(List[folder.Folder], path))

  def ProjectsToReview(self) -> Iterator[Tuple[prj.Prj, List[folder.Folder]]]:
    """Yields: (prj.Prj, [Container])."""
    now = time.time()
    for p, path in self.Projects():
      if p.NeedsReview(now):
        yield (p, path)

  def Folders(self) -> Iterator[Tuple[folder.Folder, List[folder.Folder]]]:
    """Returns all Folders and their paths.

    The root Folder is distinguished by an empty path (i.e., [Folder] is []).

    Yields:
      (Folder, [Folder]).  # The path is leaf first.
    """
    for f, path in self.ContainersPreorder():
      if not isinstance(f, folder.Folder):
        continue
      for element in path:
        if not isinstance(element, folder.Folder):
          raise TypeError
      yield (f, cast(List[folder.Folder], path))

  def Actions(self) -> Iterator[Tuple[action.Action, prj.Prj]]:
    """Iterates over all Actions and their enclosing projects.

    Yields:
      (Action, Prj)
    """
    for p, unused_path in self.Projects():
      for a in p.items:
        assert isinstance(a, action.Action), 'p=%s item=%s' % (str(p), str(a))
        yield (a, p)

  def ActionsInContext(self, ctx_uid: Optional[int]) -> Iterator[Tuple[action.Action, prj.Prj]]:
    """Iterates over all Actions in the specified Ctx.

    Args:
      ctx_uid: int|None  # For None, we return actions without a context.
    Yields:
      (Action, Prj)
    """
    for a, p in self.Actions():
      if ctx_uid is None:
        if a.ctx_uid is None:
          yield a, p
      else:
        if a.ctx_uid is not None and a.ctx_uid == ctx_uid:
          yield a, p

  def Items(self) -> Iterator[Union[action.Action, container.Container, ctx.Ctx]]:
    """Iterates through all Actions, Projects, Contexts, and Folders."""
    for c in self.ctx_list.items:
      yield c
    for co, unused_path in self.ContainersPreorder():
      yield co
    for a, unused_prj in self.Actions():
      yield a

  def RemoveReferencesToContext(self, ctx_uid: int) -> None:
    """Ensures that nothing references the specified context.

    Args:
      ctx_uid: int
    """
    for a, unused_prj in self.ActionsInContext(ctx_uid):
      assert a.ctx_uid == ctx_uid, str(a)
      a.ctx_uid = None
    for p, unused_path in self.Projects():
      if p.default_context_uid == ctx_uid:
        p.default_context_uid = None

  def ContainersPreorder(self) -> Iterator[Tuple[container.Container, List[container.Container]]]:
    """Yields all containers, /inbox first, then the others in /."""
    yield (self.inbox, [])
    for f, path in self.root.ContainersPreorder():
      yield (f, path)

  def ContextByName(self, ctx_name: str) -> Optional[ctx.Ctx]:
    """Returns the named Context if it exists, else None."""
    for c in self.ctx_list.items:
      if c.name == ctx_name:
        return c
    return None

  def ContextByUID(self, ctx_uid: int) -> Optional[ctx.Ctx]:
    """Returns the specified Context if it exists, else None."""
    for c in self.ctx_list.items:
      if c.uid == ctx_uid:
        return c
    return None

  def ActionByUID(self, the_uid: int) -> Optional[Tuple[action.Action, prj.Prj]]:
    """Returns the specified Action (with its corresponding Prj) if it exists, else None.

    Args:
      the_uid: integer
    Returns:
      None|(Action, Prj)
    """
    for a, project in self.Actions():
      if a.uid == the_uid:
        return (a, project)
    return None

  def ProjectByUID(self, project_uid: int) -> Optional[Tuple[prj.Prj, List[folder.Folder]]]:
    """Returns the specified Prj (with its corresponding path) if it exists, else None.

    Args:
      project_uid: int
    Returns:
      None|(Prj, [Folder])
    """
    for p, path in self.Projects():
      if p.uid == project_uid:
        return (p, path)
    return None

  def FolderByUID(self, folder_uid: int) -> Optional[Tuple[folder.Folder, List[folder.Folder]]]:
    """Returns the specified Folder (with its corresponding path) if it exists, else None.

    Args:
      folder_uid: int
    Returns:
      None|(Folder, [Folder])
    """
    for f, path in self.Folders():
      if f.uid == folder_uid:
        return (f, path)
    return None

  def ParentContainerOf(self, item: Union[action.Action, container.Container]) -> container.Container:
    """Returns the Container that contains the given Action/Container.

    Raises:
      NoSuchParentFolderError
    """
    if item is self.root:
      raise NoSuchParentFolderError('The root Folder has no parent Folder.')
    if item is self.inbox:
      # TODO(chandler): Should inbox be in self.root.items?
      return self.root
    for f, unused_path in self.ContainersPreorder():
      for child in f.items:
        if child is item:
          return f
    # This is very probably a bug. Could be 'x is y' vs. 'x == y'; could be a
    # stale reference.
    raise NoSuchParentFolderError('The given item has no parent Container.')

  def AddContext(self, context_name: str) -> int:
    """Adds a Ctx with the given name to our list of contexts.

    Args:
      context_name: basestring
    Returns:
      int  # UID
    Raises:
      DuplicateContextError
    """
    if context_name in [c.name for c in self.ctx_list.items]:
      raise DuplicateContextError(
        'A Context named "%s" already exists.' % context_name)
    new_ctx = ctx.Ctx(name=context_name)
    self.ctx_list.items.append(new_ctx)
    return new_ctx.uid

  def AddProjectOrFolder(self, project_or_folder: Union[prj.Prj, folder.Folder], parent_folder_uid: int = None) -> None:
    """Adds a Project/Folder with the given parent (default=root).

    Args:
      project_or_folder: Folder|Prj
      parent_folder_uid: None|int
    Raises:
      NoSuchParentFolderError
    """
    if parent_folder_uid is None:
      parent_folder_uid = self.root.uid
    for f, unused_path in self.ContainersPreorder():
      if isinstance(f, prj.Prj):
        continue
      if f.uid == parent_folder_uid:
        f.items.append(project_or_folder)
        f.NoteModification()
        break
    else:
      raise NoSuchParentFolderError(
        'No such parent folder with UID %s. project_or_folder=%s'
        % (parent_folder_uid, str(project_or_folder)))

  def RecentActivity(self, num_items: int = 5, max_name_length: int = 79) -> List[Dict[str, Union[float, str]]]:
    # TODO(chandler37): This sorts the whole list; it's slower than necessary.
    def Key(item: common.SupportsTimestamps) -> float:
      return max(item.mtime, item.ctime, 0.0 if item.dtime is None else item.dtime)

    def Val(number: float, name: str) -> Dict[str, Union[float, str]]:
      return {
        "timestamp": number,
        "pretty_timestamp_in_utc": str(datetime.datetime.fromtimestamp(number, tz.tzutc())),
        "pretty_timestamp_in_pst8pdt": str(datetime.datetime.fromtimestamp(number, tz.gettz('America/Los_Angeles'))),
        "name": name
      }

    vals = [Val(Key(item), (item.name or '')[:max_name_length])
            for item in heapq.nlargest(num_items, self.Items(), key=Key)]
    return [Val(time.time(), "current time")] + vals

  def CheckIsWellFormed(self) -> Set[int]:
    """A noop unless the programmer made an error.

    I.e., checks invariants.  We could do this better if we stopped
    using python's built-in lists and instead wrote types that
    enforced the invariants, but those lists don't know about the
    other lists in the ToDoList, so it's probably very hard to avoid
    this method.

    Raises:
      errors.DataError: A "foreign key" does not exists; a UID is missing/duplicated; etc.
    Returns:
      a set of all UIDs
    """
    if FLAGS.pyatdl_break_glass_and_skip_wellformedness_check:
      uu: Set[int] = set()
      for item in self.Items():
        if not item.uid:
          continue
        uu.add(item.uid)
      return uu

    def SelfStr() -> str:  # pylint: disable=missing-docstring
      saved_value = FLAGS.pyatdl_show_uid
      FLAGS.pyatdl_show_uid = True
      try:
        return str(self)
      finally:
        FLAGS.pyatdl_show_uid = saved_value

    for f, unused_path in self.root.ContainersPreorder():
      f.CheckIsWellFormed()
    # Verify that UIDs are unique globally (not just within Actions or Contexts):
    uids: Set[int] = set()
    for item in self.Items():
      if not item.uid:
        raise errors.DataError(
          'Missing UID for item "%s". self=%s' % (str(item), SelfStr()))
      if item.uid in uids:
        raise errors.DataError(
          'UID %s was used for two different objects' % item.uid)
      uids.add(item.uid)
    for item in self.Items():
      if isinstance(item, prj.Prj):
        if item.default_context_uid is not None and item.default_context_uid not in uids:
          raise errors.DataError(
            'UID %s is a default_context_uid but that UID does not exist.' % item.default_context_uid)
      if isinstance(item, action.Action):
        if item.ctx_uid is not None and item.ctx_uid not in uids:
          raise errors.DataError(
            "UID %s is an action's context UID but that context does not exist." % item.ctx_uid)
    return uids

  def MergeNoteList(self, other: pyatdl_pb2.NoteList) -> None:
    """repeated Note notes = 2;

    message Note {
      optional string name = 1;
      optional string note = 2;
    }
    """
    if not isinstance(other, pyatdl_pb2.NoteList):
      raise TypeError
    for other_name_and_note in other.notes:
      our_note = self.note_list.notes.get(other_name_and_note.name)
      if our_note is not None and our_note != other_name_and_note.note and other_name_and_note.note not in our_note:
        # TODO(chandler): put ctime and mtime on these notes in pyatdl.proto so that we can merge intelligently.
        self.note_list.notes[other_name_and_note.name] = f"""
<<<<<<< DB
{our_note}
=======
{other_name_and_note.note}
>>>>>>> device
""".lstrip().replace('\n', '\\n')
      else:
        self.note_list.notes[other_name_and_note.name] = other_name_and_note.note

  def MergeCtxList(self, other: pyatdl_pb2.ContextList) -> None:
    if not isinstance(other, pyatdl_pb2.ContextList):
      raise TypeError
    for context in other.contexts:
      for existing_context in self.ctx_list.items:
        assert existing_context.uid
        if existing_context.uid == context.common.uid:
          existing_context.MergeFromProto(context)
          break
      else:
        # TODO(chandler): check if the UID is in use by some non-Context entity. Duplicate if you must, but then the
        # duplication will happen again each time the mergeprotobufs API is used.
        self.ctx_list.items.append(
          ctx.Ctx.DeserializedProtobuf(
            context.SerializeToString()))

  @staticmethod
  def _FindExistingProjectByUidInRemote(*, root: pyatdl_pb2.Folder, uid: int, path: List[pyatdl_pb2.Folder]) -> List[pyatdl_pb2.Folder]:
    new_path = [root] + path
    for p in root.projects:
      if uid == p.common.uid:
        return new_path
    for f in root.folders:
      return ToDoList._FindExistingProjectByUidInRemote(root=f, uid=uid, path=new_path)
    return []

  def TrulyDeleteByUid(self, *, uid: int) -> bool:
    """Returns True iff the true deletion happened."""
    for cc in [self.inbox, self.root]:
      result = getattr(cc, 'TrulyDeleteByUid')(uid=uid)
      if not isinstance(result, bool):
        raise TypeError
      if result:
        return True
    return False

  def MergeRoot(self, other: pyatdl_pb2.Folder) -> None:
    if other.common.uid != uid.ROOT_FOLDER_UID:
      raise ValueError("needs a root Folder")
    self.root.MergeFromProto(
      other,
      find_existing_folder_by_uid=self.FolderByUID,
      find_existing_project_by_uid=self.ProjectByUID,
      find_existing_action_by_uid=self.ActionByUID,
      find_existing_project_by_uid_in_remote=lambda uid: self._FindExistingProjectByUidInRemote(root=other, uid=uid, path=[]),
      truly_delete_by_uid=self.TrulyDeleteByUid)

  def MergeInbox(self, other: pyatdl_pb2.Project, *, all_uids_in_remote_to_do_list: Set[int]) -> None:
    """Add things in other but not in self (anywhere, not just self.inbox) to self.inbox.

    Change things in self to match what are in other for existing things that are more recent according to
    max(ctime,mtime,dtime).

    (TODO(chandler): Make the flutter app (a client of the mergeprotobufs API) look at max(ctime,mtime,dtime) to
    determine a floor for its timestamps.)

    Existing things may not be in self.inbox and one must move them there if they are more recent in other. (Existence
    is determined by UID.)
    """
    assert isinstance(other, pyatdl_pb2.Project)
    assert other.common.uid == uid.INBOX_UID
    if common.MaxTimeOfPb(other) > common.MaxTime(self.inbox):
      self.inbox.MergeCommonFrom(other)
    other_uids = set()
    for an_action in other.actions:
      if an_action.common.uid in (uid.DEFAULT_PROTOBUF_VALUE_FOR_ABSENT_UID, uid.ROOT_FOLDER_UID, uid.INBOX_UID):
        raise AssertionError("merge error: illegal or missing UID")  # TODO(chandler37): do this in more places, too
      other_uids.add(an_action.common.uid)
      tup = self.ActionByUID(an_action.common.uid)
      if tup is None:
        # You might wonder, what if this used to exist here and the most recent thing we did was purge it? You are not
        # supposed to purge without syncing 100% of devices.
        self.inbox.items.append(
          action.Action.DeserializedProtobuf(
            an_action.SerializeToString()))
      else:
        existing_action, existing_project = tup
        they_are_authority = common.MaxTimeOfPb(an_action) >= common.MaxTime(existing_action)
        # TODO(chandler37): we need a test case where they moved an action into the inbox but we renamed it so both
        # actions need to exist (one with a new UID, either one...)
        if they_are_authority:
          existing_action.MergeFromProto(an_action)
          if existing_project.uid != self.inbox.uid:
            self.inbox.items.append(
              action.Action.DeserializedProtobuf(
                existing_action.AsProto().SerializeToString()))
            existing_project.DeleteItemByUid(an_action.common.uid)
    uids_to_delete = set()
    for our_action in self.inbox.items:
      if our_action.uid in other_uids:
        continue
      if our_action.uid in all_uids_in_remote_to_do_list:
        uids_to_delete.add(our_action.uid)
    if uids_to_delete:
      self.inbox.items = [i for i in self.inbox.items if i.uid not in uids_to_delete]
      self.inbox.NoteModification()

  def AsProto(self, pb: Optional[pyatdl_pb2.ToDoList] = None) -> pyatdl_pb2.ToDoList:
    """Serializes this object to a protocol buffer.

    Args:
      pb: None|pyatdl_pb2.ToDoList  # If not None, pb will be mutated and returned.
    Returns:
      pyatdl_pb2.ToDoList
    """
    if pb is None:
      pb = pyatdl_pb2.ToDoList()
    self.inbox.AsProto(pb.inbox)
    self.root.AsProto(pb.root)
    self.ctx_list.AsProto(pb.ctx_list)
    self.note_list.AsProto(pb.note_list)
    return pb

  @classmethod
  def DeserializedProtobuf(cls: Type[T], bytestring: six.binary_type) -> T:
    """Deserializes a ToDoList from the given protocol buffer."""
    assert bytestring
    assert type(bytestring) == six.binary_type, type(bytestring)
    SetAllowOversizeProtos(FLAGS.pyatdl_allow_infinite_memory_for_protobuf)
    # TODO(chandler37): after `loadtest -n 100` with
    # FLAGS.pyatdl_allow_infinite_memory_for_protobuf==True (on localhost;
    # heroku will time out), navigating to the Action page for 'DeepAction'
    # gives bizarre errors from appcommands about the following:
    #
    # Internal Server Error: /todo/action/7812977415892969734
    # AttributeError: pyatdl_internal_state
    #
    # gflags.exceptions.DuplicateFlagError: The flag 'json' is defined twice. First from <unknown>, Second from
    # pyatdllib.ui.appcommandsutil.  Description from first occurrence: Output JSON
    pb = pyatdl_pb2.ToDoList.FromString(bytestring)  # pylint: disable=no-member
    if not pb.HasField('inbox'):
      raise errors.DataError(f"protocol buffer error: the Inbox project, with UID={uid.INBOX_UID}, is required")
    if not pb.HasField('root'):
      raise errors.DataError(f"protocol buffer error: the root folder, with UID={uid.ROOT_FOLDER_UID}, is required")
    inbox = prj.Prj.DeserializedProtobuf(pb.inbox.SerializeToString())
    root = folder.Folder.DeserializedProtobuf(pb.root.SerializeToString())
    serialized_ctx_list = pb.ctx_list.SerializeToString()
    if len(pb.ctx_list.contexts) > 0:
      ctx_list = ctx.CtxList.DeserializedProtobuf(serialized_ctx_list)
    else:
      ctx_list = ctx.CtxList(deserializing=True)
    serialized_note_list = pb.note_list.SerializeToString()
    note_list = note.NoteList.DeserializedProtobuf(serialized_note_list)
    rv = cls(inbox=inbox, root=root, ctx_list=ctx_list, note_list=note_list)
    rv.CheckIsWellFormed()
    return rv
