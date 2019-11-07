"""Defines ToDoList, which consists of an inbox (a Prj), a root Folder, and a
list of Contexts.

An end user thinks of the totality of their data as a ToDoList.
"""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import six
import time

import gflags as flags  # https://code.google.com/p/python-gflags/

from google.protobuf.pyext._message import SetAllowOversizeProtos

from . import action
from . import common
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


class ToDoList(object):
  """The totality of one end user's data, their projects and actions.

  Fields:
    root: Folder
    inbox: Prj
    ctx_list: CtxList
    note_list: NoteList  # every auditable object has its own note; these are global
  """

  def __init__(self, inbox=None, root=None, ctx_list=None, note_list=None):
    self.inbox = inbox if inbox is not None else prj.Prj(name=FLAGS.inbox_project_name, the_uid=uid.INBOX_UID)
    if self.inbox.uid != uid.INBOX_UID:
      raise errors.DataError(f"Inbox UID is not {uid.INBOX_UID}, it is {self.inbox.uid}")
    self.root = root if root is not None else folder.Folder(name='', the_uid=uid.ROOT_FOLDER_UID)
    if self.root.uid != uid.ROOT_FOLDER_UID:
      raise errors.DataError(f"Root folder UID is not {uid.ROOT_FOLDER_UID}, it is {self.root.uid}")
    self.ctx_list = ctx_list if ctx_list is not None else ctx.CtxList(name='Contexts')
    self.note_list = note_list if note_list is not None else note.NoteList()

  def __str__(self):
    return self.__unicode__().encode('utf-8') if six.PY2 else self.__unicode__()

  def __unicode__(self):
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

  def AsTaskPaper(self, lines, show_project=lambda _: True, show_action=lambda _: True, show_note=lambda _: True,
                  hypertext_prefix=None, html_escaper=None):
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
    def ContextName(context_uid):
      for i in self.ctx_list.items:
        if i.uid == context_uid:
          return six.text_type(i.name)
      return 'impossible error so file a bug report please'

    pairs = []
    for p, path in self.Projects():
      if show_project(p):
        pairs.append((p, path))

    def Key(pair):
      p, path = pair
      if p.uid == 1:  # inbox
        return ""
      prefix = six.text_type(FLAGS.pyatdl_separator).join(f.name for f in reversed(path))
      return FLAGS.pyatdl_separator.join([prefix, p.name])

    pairs.sort(key=Key)
    # TODO(chandler): make it possible to sort chronologically as well as what we do now, which is sorting
    # alphabetically.
    for p, path in pairs:
      prefix = six.text_type(FLAGS.pyatdl_separator).join(f.name for f in reversed(path))
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

  def PurgeDeleted(self):
    self.inbox.PurgeDeleted()
    self.root.PurgeDeleted()
    self.ctx_list.PurgeDeleted()

  def DeleteCompleted(self):
    self.inbox.DeleteCompleted()
    self.root.DeleteCompleted()
    self.ctx_list.DeleteCompleted()  # a nop for now; contexts cannot be completed

  def Projects(self):
    """Returns all projects, including the /inbox project.

    The /inbox project is distinguished by an empty path (i.e., [Folder] is []).

    Yields:
      (prj.Prj, [Folder]).  # The path is leaf first.
    """
    for p, path in self.ContainersPreorder():
      if not isinstance(p, prj.Prj):
        continue
      yield (p, path)

  def ProjectsToReview(self):
    """Yields: (prj.Prj, [Container])."""
    now = time.time()
    for p, path in self.Projects():
      if p.NeedsReview(now):
        yield (p, path)

  def Folders(self):
    """Returns all Folders and their paths.

    The root Folder is distinguished by an empty path (i.e., [Folder] is []).

    Yields:
      (prj.Prj, [Folder]).  # The path is leaf first.
    """
    for f, path in self.ContainersPreorder():
      if not isinstance(f, folder.Folder):
        continue
      yield (f, path)

  def Actions(self):
    """Iterates over all Actions and their enclosing projects.

    Yields:
      (Action, Prj)
    """
    for p, unused_path in self.Projects():
      for a in p.items:
        assert isinstance(a, action.Action), 'p=%s item=%s' % (str(p), str(a))
        yield (a, p)

  def ActionsInContext(self, ctx_uid):
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

  def ActionsInProject(self, prj_uid):
    """Iterates over all Actions in the specified Prj.

    Args:
      prj_uid: int
    Yields:
      Action
    """
    for a, _ in self.Actions():
      if a.project.uid == prj_uid:
        yield a

  def Items(self):
    """Iterates through all CtxLists, Actions, Projects, Contexts, and Folders.

    Yields:
      Action/Ctx/Folder/Prj
    """
    yield self.ctx_list
    for i in self.ctx_list.items:
      yield i
    for i, unused_path in self.ContainersPreorder():
      yield i
    for i, unused_prj in self.Actions():
      yield i

  def RemoveReferencesToContext(self, ctx_uid):
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

  def ContainersPreorder(self):
    """Yields all containers, /inbox first, then the others in /."""
    yield (self.inbox, [])
    for f, path in self.root.ContainersPreorder():
      yield (f, path)

  def ContextByName(self, ctx_name):
    """Returns the named Context if it exists, else None.

    Args:
      ctx_name: str
    Returns:
      None|Ctx
    """
    for c in self.ctx_list.items:
      if c.name == ctx_name:
        return c
    return None

  def ContextByUID(self, ctx_uid):
    """Returns the specified Context if it exists, else None.

    Args:
      ctx_uid: int
    Returns:
      None|Ctx
    """
    for c in self.ctx_list.items:
      if c.uid == ctx_uid:
        return c
    return None

  def ActionByUID(self, the_uid):
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

  def ProjectByUID(self, project_uid):
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

  def FolderByUID(self, folder_uid):
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

  def ParentContainerOf(self, item):
    """Returns the Container that contains the given Action/Ctx/Container.

    Returns:
      Container
    Raises:
      NoSuchParentFolderError
    """
    if isinstance(item, ctx.Ctx):
      return self.ctx_list
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

  def AddContext(self, context_name):
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
    self.ctx_list.NoteModification()
    return new_ctx.uid

  def AddProjectOrFolder(self, project_or_folder, parent_folder_uid=None):
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

  def CheckIsWellFormed(self):
    """A noop unless the programmer made an error.

    I.e., checks invariants.  We could do this better if we stopped
    using python's built-in lists and instead wrote types that
    enforced the invariants, but those lists don't know about the
    other lists in the ToDoList, so it's probably very hard to avoid
    this method.

    Raises:
      errors.DataError: A "foreign key" does not exists; a UID is missing/duplicated; etc.
    """
    if FLAGS.pyatdl_break_glass_and_skip_wellformedness_check:
      return

    def SelfStr():  # pylint: disable=missing-docstring
      saved_value = FLAGS.pyatdl_show_uid
      FLAGS.pyatdl_show_uid = True
      self_str = str(self)
      FLAGS.pyatdl_show_uid = saved_value
      return self_str

    self.ctx_list.CheckIsWellFormed()
    for f, unused_path in self.root.ContainersPreorder():
      f.CheckIsWellFormed()
    # Verify that UIDs are unique globally (not just within Actions or Contexts):
    uids = set()
    for item in self.Items():
      if not item.uid:
        raise errors.DataError(
          'Missing UID for item "%s". self=%s' % (str(item), SelfStr()))
      if item.uid in uids:
        raise errors.DataError(
          'UID %s was used for two different objects' % item.uid)
      uids.add(item.uid)
    for item in self.Items():
      if hasattr(item, 'default_context_uid'):
        if item.default_context_uid is not None and item.default_context_uid not in uids:
          raise errors.DataError(
            'UID %s is a default_context_uid but that UID does not exist.' % item.default_context_uid)
      if hasattr(item, 'ctx_uid'):
        if item.ctx_uid is not None and item.ctx_uid not in uids:
          raise errors.DataError(
            "UID %s is an action's context UID but that context does not exist." % item.ctx_uid)

  def AsProto(self, pb=None):
    """Serializes this object to a protocol buffer.

    Args:
      pb: None|pyatdl_pb2.ToDoList  # If not None, pb will be mutated and returned.
    Returns:
      pyatdl_pb2.ToDoList
    """
    if pb is None:
      pb = pyatdl_pb2.ToDoList()
    # pylint: disable=maybe-no-member
    self.inbox.AsProto(pb.inbox)
    self.root.AsProto(pb.root)
    self.ctx_list.AsProto(pb.ctx_list)
    self.note_list.AsProto(pb.note_list)
    assert self.ctx_list.uid == pb.ctx_list.common.uid
    assert pb.ctx_list.common.metadata.name, 'X23 %s' % str(pb.ctx_list)
    return pb

  @classmethod
  def DeserializedProtobuf(cls, bytestring):
    """Deserializes a ToDoList from the given protocol buffer.

    Args:
      bytestring: str
    Returns:
      ToDoList
    """
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
    # gflags.exceptions.DuplicateFlagError: The flag 'json' is defined twice. First from <unknown>, Second from pyatdllib.ui.appcommandsutil.  Description from first occurrence: Output JSON

    pb = pyatdl_pb2.ToDoList.FromString(bytestring)  # pylint: disable=no-member
    if not pb.HasField('inbox'):
      raise errors.DataError(f"protocol buffer error: the Inbox project, with UID={uid.INBOX_UID}, is required")
    if not pb.HasField('root'):
      raise errors.DataError(f"protocol buffer error: the root folder, with UID={uid.ROOT_FOLDER_UID}, is required")
    if not pb.HasField('ctx_list'):
      raise errors.DataError(f"protocol buffer error: the ctx_list is required")
    inbox = prj.Prj.DeserializedProtobuf(
      pb.inbox.SerializeToString())
    root = folder.Folder.DeserializedProtobuf(
      pb.root.SerializeToString())
    serialized_ctx_list = pb.ctx_list.SerializeToString()
    ctx_list = ctx.CtxList.DeserializedProtobuf(
      serialized_ctx_list)
    serialized_note_list = pb.note_list.SerializeToString()
    note_list = note.NoteList.DeserializedProtobuf(
      serialized_note_list)
    rv = cls(inbox=inbox, root=root, ctx_list=ctx_list, note_list=note_list)
    rv.CheckIsWellFormed()
    return rv
