"""Defines the state needed to perform the various commands in module 'uicmd'.

Specifically, this keeps track of the tdl.ToDoList, the current working
Folder/Prj, and the desired view filter (e.g., 'all_even_deleted').
"""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import six

import gflags as flags  # https://code.google.com/p/python-gflags/

from ..core import common
from ..core import container
from ..core import uid
from ..core import view_filter
from . import lexer
from . import undoutil

FLAGS = flags.FLAGS


class Error(Exception):
  """Base class for this module's exceptions."""


class InvalidPathError(Error):
  """A path specifying a Container is invalid syntax or not found."""


class NothingToUndoSlashRedoError(Error):
  """See undoutil.NothingToUndoSlashRedoError."""


class State(object):  # pylint: disable=too-many-instance-attributes,too-many-public-methods
  """Where in the to-do list's Folder hierarchcy are we? What is the to-do list?
  What is the current ViewFilter?
  """

  def __init__(self, printer, todolist, app_namespace, html_escaper=None):
    """Initializer.

    Args:
      printer: (str,)->None
      todolist: tdl.ToDoList
      app_namespace: appcommandsutil.Namespace
      html_escaper: lambda unicode: unicode
    """
    # TODO(chandler): change default sorting to alpha but in such a way that
    # immaculater_test doesn't have to change drastically:
    self.SetSorting('chrono')
    self._app_namespace = app_namespace
    self.SetPrinter(printer)
    self._current_working_container = None
    self._todolist = None
    self._view_filter = None
    self._class_to_deserialize_into = None
    self._serialized_tdl_we_rewind_to = None
    self._undo_helper = None
    self._html_escaper = html_escaper
    self.SetToDoList(todolist)
    self.ResetUndoStack()

  def HTMLEscaper(self):
    return self._html_escaper

  def SetPrinter(self, printer):
    """Sets the printer.

    Args:
      printer: (str,)->None
    """
    self._printer = printer

  def Printer(self):
    """Gets the printer.

    Returns:
      (str,)->None
    """
    return self._printer

  def SetToDoList(self, td):
    """Sets the to-do list.

    You must discard the results of previous calls to CurrentWorkingContainer()
    and ViewFilter() because they point to the previous to-do list.

    After this call, self.ViewFilter() will return a default view filter and
    self.CurrentWorkingContainer() will point to td's root folder.

    Args:
      td: tdl.ToDoList
    """
    self._todolist = td
    self._current_working_container = self._todolist.root
    self._view_filter = self.NewViewFilter(view_filter.CLS_BY_UI_NAME['default'])
    # TODO(chandler37): Perhaps we need to raise TooBigToSaveError if this is
    # too big? But really it'd be better to just delete the original undo/redo
    # code (see RewindForUndoRedo e.g.) which only worked in the command-line
    # interface before the django webapp and certainly doesn't work for mobile
    # apps, single-page webapps, or desktop apps. To undo/redo we must alter
    # pyatdl.proto itself.
    self._serialized_tdl_we_rewind_to = td.AsProto().SerializeToString()
    self._class_to_deserialize_into = td.__class__

  def ResetUndoStack(self):
    """After calling SetToDoList, call this to clear out the info used during
    undo/redo.
    """
    self._undo_helper = undoutil.UndoStack(self)

  def ToDoList(self):
    """Returns the to-do list.

    Returns:
      ToDoList
    """
    return self._todolist

  @staticmethod
  def AllSortingOptions():
    return frozenset(['alpha', 'chrono'])

  def CurrentSorting(self):
    return self._sorting_ui_name

  def SetSorting(self, ui_name):
    assert ui_name in State.AllSortingOptions(), ui_name
    self._sorting_ui_name = ui_name

  def _ActionToProject(self, an_action):
    a = self.ToDoList().ActionByUID(an_action.uid)
    if a is None:
      raise ValueError('No action with uid "%s" exists.' % an_action.uid)
    found_action, project = a
    assert found_action is an_action, 'Is it a deep copy?'
    return project

  def _ActionToContext(self, an_action):
    if an_action.ctx_uid is None:
      return None
    for c in self.ToDoList().ctx_list.items:
      if c.uid == an_action.ctx_uid:
        return c
    raise ValueError(
      'No Context found for action "%s" even though that action has a context UID of "%s"'
      % (an_action.uid, an_action.ctx_uid))

  def NewViewFilter(self, filter_cls):
    """Returns a view filter that holds an internal reference to the given todolist.

    Args:
      filter_cls: view_filter.ViewFilter
    Returns:
      view_filter.ViewFilter
    """
    return filter_cls(
      lambda a: self._ActionToProject(a),
      lambda a: self._ActionToContext(a))

  def CurrentWorkingContainer(self):
    """Returns the Folder/Prj operations are relative to.

    Returns:
      Container
    """
    return self._current_working_container

  def SetCurrentWorkingContainer(self, the_container):
    """Sets the current CurrentWorkingContainer.

    Args:
      the_container: Container
    """
    self._current_working_container = the_container

  def ContainerAbsolutePath(self, containr, display=False):
    """Prettyprinted absolute path to the given Container.

    If display is true, we omit the leading directory separator and do not
    escape directory separators.

    Args:
      containr: Container
      display: bool
    Returns:
      unicode
    """
    def Escaped(x):
      if display:
        return x
      else:
        return State.SlashEscaped(x)

    for f, path in self.ToDoList().ContainersPreorder():
      if f.uid == containr.uid:
        if f is self.ToDoList().root or f is self.ToDoList().inbox:
          return '%s%s' % ('' if display else FLAGS.pyatdl_separator,
                           Escaped(f.name))
        z = FLAGS.pyatdl_separator.join(Escaped(x.name) for x in reversed(path))
        r = '%s%s%s' % (z,
                        FLAGS.pyatdl_separator,
                        Escaped(f.name))
        return r.lstrip(FLAGS.pyatdl_separator) if display else r

  def CurrentWorkingContainerString(self):
    """Prettyprinted path to the current working Container.

    Returns:
      str
    """
    return self.ContainerAbsolutePath(self.CurrentWorkingContainer())

  @staticmethod
  def SlashEscaped(x):
    """In the pathological case where a directory separator appears in a
    Container|Action name, use this function to remove the directory separator.

    Args:
      x: str
    Returns:
      str
    """
    return x.replace(FLAGS.pyatdl_separator, '__FORWARD_SLASH__')

  @staticmethod
  def BaseName(path):
    """Returns the name of the deepest Container specified by path. Think os.path.basename.

    Args:
      path: basestring
    Returns:
      basestring
    Raises:
      InvalidPathError
    """
    path = State.CanonicalPath(path)
    if path.endswith(FLAGS.pyatdl_separator):
      return ''
    if FLAGS.pyatdl_separator in path:
      return path.split(FLAGS.pyatdl_separator)[-1]
    return path

  @staticmethod
  def CanonicalPath(path):
    """Returns the canonical representation of the given path.

    Args:
      path: basestring
    Returns:
      basestring
    """
    x = path.rfind('%s%s' % (FLAGS.pyatdl_separator, FLAGS.pyatdl_separator))
    if x >= 0:
      return State.CanonicalPath(path[x + 1:])
    return path

  @staticmethod
  def DirName(path):
    """Returns the path of the parent directory. Think os.path.dirname.

    Args:
      path: basestring
    Returns:
      basestring
    Raises:
      InvalidPathError
    """
    path = State.CanonicalPath(path)
    if path == FLAGS.pyatdl_separator:
      return path
    if not path:
      return ''
    x = FLAGS.pyatdl_separator.join(path.split(FLAGS.pyatdl_separator)[:-1])
    if x:
      return x
    if path.startswith(FLAGS.pyatdl_separator):
      return FLAGS.pyatdl_separator
    return ''

  def GetObjectFromPath(self, path, include_contexts=False):
    """Returns the AuditableObject specified by the path.

    If path is relative, it is relative to CurrentWorkingContainer().

    Args:
      path: basestring
      include_contexts: boolean
    Returns:
      AuditableObject
    Raises:
      InvalidPathError
    """
    # TODO(chandler): allow Perforce 'p4' style ".../*foo"
    try:
      the_uid = lexer.ParseSyntaxForUID(path)
    except lexer.Error as e:
      raise InvalidPathError(e)
    if the_uid:
      for context in self.ToDoList().ctx_list.items:
        if context.uid == the_uid:
          return context
      for f, unused_path in self.ToDoList().ContainersPreorder():
        if f.uid == the_uid:
          return f
        for item in f.items:
          if item.uid == the_uid:
            return item
      raise InvalidPathError('UID %s not found' % the_uid)
    if include_contexts:
      for context in self.ToDoList().ctx_list.items:
        if context.name == path:
          return context
    containr = self.CurrentWorkingContainer()
    if not path:
      return containr
    for name in path.rstrip(FLAGS.pyatdl_separator).split(FLAGS.pyatdl_separator):
      if not name:
        containr = self.ToDoList().root
      else:
        containr = self._ChildObject(name, containr)
    return containr

  def GetContainerFromPath(self, path):
    # TODO(chandler): Add more unit tests to test that all callers handle
    # Actions politely
    """Returns the Container specified by the path.

    If path is relative, it is relative to CurrentWorkingContainer().

    Args:
      path: basestring
    Returns:
      Container
    Raises:
      InvalidPathError
    """
    obj = self.GetObjectFromPath(path)
    if isinstance(obj, container.Container):
      return obj
    raise InvalidPathError(
      'The path "%s" exists but is not a Folder or Project.' % path)

  def _GetParentContainer(self, cwc):
    """Returns the parent Container ('..') of cwc.

    Args:
      cwc: Container
    Returns:
      Container
    Raises:
      InvalidPathError
    """
    if cwc.uid == 1:
      return self.ToDoList().root
    names_seen = set()
    for f, path in self.ToDoList().ContainersPreorder():
      names_seen.add(f.name)
      if f.uid == cwc.uid:
        if not path:
          raise InvalidPathError('Already at the root Folder; cannot ascend.')
        return path[0]
    raise InvalidPathError(
      'No such folder. All folders:\n%s'
      % (common.Indented('\n'.join(sorted(names_seen)))))

  def _ChildObject(self, name, cwc):
    """Searches for the specified immediate child and returns the AuditableObject for that child.

    Args:
      name: basestring
      cwc: Container  # current working container
    Returns:
      AuditableObject
    Raises:
      InvalidPathError
    """
    # TODO(chandler): Test with --allow_slashes though. How do you 'mv' an
    # action with slashes in it other than UID notation? mv a\/b /inbox does not
    # work; see testMv3.
    assert FLAGS.pyatdl_separator not in name, name
    try:
      the_uid = lexer.ParseSyntaxForUID(name)
    except lexer.Error as e:
      raise InvalidPathError(e)
    if name == '.':
      return cwc
    elif name == '..':
      return self._GetParentContainer(cwc)
    if cwc is self.ToDoList().root:
      if the_uid == self.ToDoList().root.uid:
        return cwc
      if name == FLAGS.inbox_project_name or the_uid == self.ToDoList().inbox.uid:
        return self.ToDoList().inbox
    # TODO(chandler): Does this mean we can stop renaming Contexts '%s-deleted-at-14999999999'?
    for item in cwc.items:
      if item.uid == the_uid or (not item.is_deleted and item.name == name):
        return item
    for item in cwc.items:
      if item.is_deleted and item.name == name:
        return item
    raise InvalidPathError(
      'With current working Folder/Project "%s", there is no such child "%s".  Choices:\n%s\n%s'
      % (self.CurrentWorkingContainerString(),
         name,
         common.Indented('..'),
         common.Indented('\n'.join(i.name for i in cwc.items if isinstance(i, container.Container)))))

  def SearchFilter(self, *, query, show_active, show_done):
    """Creates a ViewFilter that searches.

    Returns:
      ViewFilter
    """
    return view_filter.SearchFilter(
      lambda a: self._ActionToProject(a),
      lambda a: self._ActionToContext(a),
      query=query,
      show_active=show_active,
      show_done=show_done)

  def ViewFilter(self):
    """Returns the current ViewFilter.

    Returns:
      ViewFilter
    """
    return self._view_filter

  def SetViewFilter(self, vf):
    """Sets the current ViewFilter.

    Args:
      vf: ViewFilter
    """
    self._view_filter = vf

  def Print(self, s):  # pylint: disable=no-self-use
    """Shows the given string to the User.

    Args:
      s: basestring
    Returns:
      None
    """
    self._printer(six.text_type(s))

  def RegisterUndoableCommand(self, undoable_cmd):
    """Notes the successful execution of an undoable command.

    Args:
      undoable_cmd: undoutil.UndoableCommand
    """
    assert isinstance(undoable_cmd, undoutil.UndoableCommand), repr(undoable_cmd)
    self._undo_helper.RegisterUndoableCommand(undoable_cmd)

  def Undo(self):
    """Undoes the last undoable command.

    Raises:
      NothingToUndoSlashRedoError
    """
    try:
      self._undo_helper.Undo()
    except undoutil.NothingToUndoSlashRedoError as e:
      raise NothingToUndoSlashRedoError(e)

  def Redo(self):
    """Redoes the last undone command.

    Raises:
      NothingToUndoSlashRedoError
    """
    try:
      self._undo_helper.Redo()
    except undoutil.NothingToUndoSlashRedoError as e:
      raise NothingToUndoSlashRedoError(e)

  def RewindForUndoRedo(self):
    """UndoState calls this function as part of the RewindableSupportingReplay
    interface. It rewinds things so that we are in the same place we were
    when the to-do list was last deserialized/created.
    """
    uid.ResetNotesOfExistingUIDs()
    old_view_filter_name = None
    if self._view_filter is not None:
      old_view_filter_name = self._view_filter.ViewFilterUINames()[0]
    t = self._class_to_deserialize_into.DeserializedProtobuf(
      self._serialized_tdl_we_rewind_to)
    self._serialized_tdl_we_rewind_to = None
    self.SetToDoList(t)
    if old_view_filter_name is not None:
      self.SetViewFilter(self.NewViewFilter(
        view_filter.CLS_BY_UI_NAME[old_view_filter_name]))

  def ReplayCommandForUndoRedo(self, cmd):
    """UndoState calls this function as part of the RewindableSupportingReplay
    interface. It executes the given command.

    Args:
      cmd: undoutil.UndoableCommand
    """
    if cmd.CommandName() in self._app_namespace.CmdList():
      self._app_namespace.FindCmdAndExecute(
        self, cmd.CommandArgsIncludingName(), generate_undo_info=False)
    else:
      raise AssertionError('How did this command ever get registered? cmd=%s'
                           % cmd.CommandName())
