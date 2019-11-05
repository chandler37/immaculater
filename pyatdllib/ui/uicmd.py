"""Defines the various commands you can perform via immaculater.py's tty-based
UI (CLI).

You must call RegisterAppcommands before using this module.
"""

# pylint: disable=super-on-old-class

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import base64
import datetime
import json
import pipes
import pytz
import random
import re
import six
from six.moves import xrange
import time  # pylint: disable=wrong-import-order

import gflags as flags  # https://github.com/gflags/python-gflags now called abseil-py

from third_party.google.apputils.google.apputils import app
from third_party.google.apputils.google.apputils import appcommands
from google.protobuf import text_format

from ..core import action
from ..core import auditable_object
from ..core import common
from ..core import container
from ..core import ctx
from ..core import folder
from ..core import prj
from ..core import tdl
from ..core import uid
from ..core import view_filter
from . import appcommandsutil
from . import lexer
from . import serialization
from . import state as state_module


FLAGS = flags.FLAGS

flags.DEFINE_string('no_context_display_string', '<none>',
                    'Text to indicate the lack of a context')
flags.DEFINE_string('timezone', 'UTC',
                    'Time zone in pytz format, e.g. "US/Eastern", "UTC", "US/Pacific"')
flags.DEFINE_string('time_format', '%Y/%m/%d-%H:%M:%S',
                    'Format string for timestamps, used in, e.g., "ls"')
flags.DEFINE_bool('pyatdl_allow_exceptions_in_batch_mode', False,
                  'In batch mode, allow exceptions? If so, they will be '
                  'printed but execution will continue. If not, execution will '
                  'be aborted.')
flags.DEFINE_bool('seed_upon_creation', False,
                  'Run the command "seed" after creation of a to-do list?')


class Error(Exception):
  """Base class for this module's exceptions."""


# Multiple inheritance:
class BadArgsError(Error, appcommandsutil.IncorrectUsageError):
  """Invalid arguments."""


class NothingToUndoSlashRedoError(BadArgsError):
  """Undo/redo is impossible because, e.g., no undoable commands have yet
  happened.

  TODO(chandler): This is a BadArgsError, but maybe it's worth it to
  separate these errors into 'bad args' vs. 'illegal state for the given
  cmd' vs. 'cannot undo/redo'.
  """


class NoSuchContainerError(Error):
  """The folder/project was not found."""


def _ProjectString(project, path):  # pylint:disable=missing-docstring
  ps = FLAGS.pyatdl_separator.join(
    state_module.State.SlashEscaped(x.name) for x in reversed(path))
  return FLAGS.pyatdl_separator.join([ps, project.name])


def _CompleteStr(is_complete):  # pylint:disable=missing-docstring
  return '---COMPLETE---' if is_complete else '--incomplete--'


def _ActiveStr(is_active):  # pylint:disable=missing-docstring
  return '---active---' if is_active else '--INACTIVE--'


def _ListingForContext(show_uid, show_timestamps, context):
  """Returns the human-readble, one-line string representation of context.

  Args:
    show_uid: bool
    show_timestamps: bool  # include ctime, dtime, mtime
    context: Context|None
  Returns:
    str
  """
  if context is None:
    uid_str = 'uid=0 ' if show_uid else ''
  else:
    uid_str = ('uid=%s ' % context.uid) if show_uid else ''
  return '--context-- %s%s%s%s %s' % (
      uid_str,
      _DeletedStr(context.is_deleted if context is not None else False),
      _ConcatenatedTimestampStr(context, show_timestamps),
      _ActiveStr(True if context is None else context.is_active),
      pipes.quote(context.name if context is not None
                  else FLAGS.no_context_display_string))


def _ListingForOneItem(show_uid, show_timestamps, item, to_do_list, name_override=None,
                       in_context_override=None):
  """Returns the human-readble, one-line string representation of item.

  Args:
    show_uid: bool
    show_timestamps: bool  # include ctime, dtime, mtime
    item: Folder|Prj|Action
    to_do_list: ToDoList
    name_override: str  # overrides item.name if not None
    in_context_override: str
  Returns:
    str
  """
  by_type = {folder.Folder: '--folder--- ',
             prj.Prj: '--project-- ',
             action.Action: '--action--- ',
             ctx.Ctx: '--context-- '}
  deleted_str = _DeletedStr(item.is_deleted)
  type_str = by_type[type(item)]
  lead = '%s%s%s' % (
    type_str, deleted_str, _ConcatenatedTimestampStr(item, show_timestamps))
  completed_str = ''
  if hasattr(item, 'is_complete'):
    completed_str = '%s ' % _CompleteStr(item.is_complete)
  active_str = ''
  if hasattr(item, 'is_active'):
    active_str = '%s ' % _ActiveStr(item.is_active)
  in_context = ''
  if hasattr(item, 'ctx_uid'):
    if item.ctx_uid is None:
      in_context = ' --in-context-- %s' % pipes.quote(
        FLAGS.no_context_display_string)
    else:
      context = to_do_list.ContextByUID(item.ctx_uid)
      if context is None:
        raise AssertionError(
          "The protobuf has a bad Context association with an Action. item.ctx_uid=%s item.uid=%s"
          % (item.ctx_uid, item.uid))
      in_context = ' --in-context-- %s' % pipes.quote(context.name)
  return '%s%s%s%s%s%s' % (
    lead,
    'uid=%s ' % item.uid if show_uid else '',
    completed_str,
    active_str,
    pipes.quote(name_override if name_override is not None else item.name),
    in_context_override if in_context_override is not None else in_context)


def _JsonForOneItem(item, to_do_list, number_of_items,
                    name_override=None, in_context_override=None,
                    path_leaf_first=None, in_prj=None):
  """Returns a JSON-friendly object representing the given item.

  Args:
    item: Folder|Prj|Action|Ctx|None  # None is 'Actions Without Context'
    name_override: str  # overrides item.name if not None
    in_context_override: str
    path_leaf_first: [str]
    in_prj: str
  Returns:
    dict  # not JSON, but ready to be
  """
  name = FLAGS.no_context_display_string if item is None else item.name
  rv = {
    'is_deleted': False if item is None else item.is_deleted,
    'ctime': 0 if item is None else item.ctime,
    'dtime': None if item is None or not item.is_deleted else item.dtime,
    'mtime': 0 if item is None else item.mtime,
    'is_complete': item.is_complete if hasattr(item, 'is_complete') else False,
    'uid': str(0 if item is None else item.uid),  # javascript cannot handle 64-bit integers
    'name': name_override if name_override is not None else name,
    'number_of_items': number_of_items
  }
  if in_prj is not None:
    rv['in_prj'] = in_prj
  if hasattr(item, 'NeedsReview'):
    rv['needsreview'] = bool(item.NeedsReview())
  if hasattr(item, 'default_context_uid'):
    # Why a string instead of an integer? JSON doesn't have 64-bit
    # integers. javascript has only one numeric type and it is floating point
    # and therefore unable to represent all UIDs in our range. See
    # https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Number/MAX_SAFE_INTEGER
    rv['default_context_uid'] = str(0 if item.default_context_uid is None else item.default_context_uid)
  if hasattr(item, 'ctx_uid'):
    if item.ctx_uid is None:
      in_context = FLAGS.no_context_display_string
    else:
      context = to_do_list.ContextByUID(item.ctx_uid)
      if context is not None:
        in_context = context.name
      else:
        raise AssertionError(
          "The protobuf has a bad Context association with an Action. item.ctx_uid=%s item.uid=%s"
          % (item.ctx_uid, item.uid))
    rv['in_context'] = in_context_override if in_context_override is not None else in_context
    rv['in_context_uid'] = str(item.ctx_uid) if item.ctx_uid is not None else None
  if item is None:
    rv['is_active'] = True
  if hasattr(item, 'is_active'):
    rv['is_active'] = item.is_active
  if hasattr(item, 'note'):
    rv['has_note'] = bool(item.note)
  if path_leaf_first is not None:
    rv['path'] = FLAGS.pyatdl_separator.join(
      state_module.State.SlashEscaped(x.name) for x in reversed(path_leaf_first))
    if not rv['path']:
      rv['path'] = FLAGS.pyatdl_separator
  return rv


def _TimestampStr(epoch_sec_or_none):  # pylint:disable=missing-docstring
  if epoch_sec_or_none is None:
    # not yet deleted.
    return ''
  tz = pytz.timezone(FLAGS.timezone)
  return datetime.datetime.fromtimestamp(epoch_sec_or_none, tz).strftime(
    FLAGS.time_format)


def _ConcatenatedTimestampStr(c, show_timestamps):
  """Returns a display string for creation time, modification time, and deletion time.

  If non-empty, this string ends with a trailing space.

  Args:
    c: ctx.Ctx
    show_timestamps: bool
  Returns:
    str
  """
  ctime_str = 'ctime=%s ' % _TimestampStr(0 if c is None else c.ctime) if show_timestamps else ''
  mtime_str = 'mtime=%s ' % _TimestampStr(0 if c is None else c.mtime) if show_timestamps else ''
  if show_timestamps and c is not None and c.dtime:
    dtime_str = 'dtime=%s ' % _TimestampStr(c.dtime)
  else:
    dtime_str = ''
  return '%s%s%s' % (mtime_str, ctime_str, dtime_str)


def _DeletedStr(is_deleted):  # pylint:disable=missing-docstring
  return '--DELETED-- ' if is_deleted else ''


def NewToDoList():
  """Instantiates a new to-do list.

  Returns:
    tdl.ToDoList
  """
  t = tdl.ToDoList()
  if FLAGS.seed_upon_creation:
    APP_NAMESPACE.FindCmdAndExecute(
      state_module.State(lambda _: None, t, APP_NAMESPACE),
      ['seed'])
  return t


def _RemovePrefix(prefix, text):
  match = re.match(prefix, text)
  if match is None:
    return text
  return text[len(match.group()):]


def _Inboxize(state, note):
  """Creates a new Action in the Inbox for every line in the note. Returns the new note.

  Args:
    state: State
    note: basestring
  Returns:
    basestring
  Raises:
    BadArgsError
  """
  def essence(line):
    return _RemovePrefix(r'@xfer\b', line.strip().lstrip(':-\u2013\u2014').lstrip()).lstrip()

  first_action = None
  note = note.replace(r'\n', '\n')
  beginning = 'You chose to process'
  for line in note.splitlines():
    action = essence(line).strip()
    if not action:
      continue
    # TODO(chandler37): preserve metadata, ctime anyway?
    if first_action is None:
      first_action = action
      if action.startswith(beginning):
        raise BadArgsError('You already turned this note into Actions in the Inbox.')
    APP_NAMESPACE.FindCmdAndExecute(
      state,
      ['do', action])
  if first_action is None:
    return ''
  return "\\n".join(
    [f'{beginning} the note that was here into',
     'a sequence of Actions in the Inbox.',
     '',
     'The first such action was the following:',
     f'\t- {first_action}',
     ])


def _LookupProject(state, argument):  # pylint: disable=too-many-branches
  """Returns the specified Project and its parent Container.

  Args:
    state: State
    argument: basestring
  Returns:
    (Prj, Folder|None)  # project '/inbox' has no parent, hence None
  Raises:
    BadArgsError
    NoSuchContainerError
  """
  try:
    the_uid = lexer.ParseSyntaxForUID(argument)
  except lexer.Error as e:
    raise BadArgsError(e)
  if the_uid is not None:
    x = state.ToDoList().ProjectByUID(the_uid)  # None if the_uid is invalid
    if x is None:
      raise NoSuchContainerError('No Project exists with UID %s' % the_uid)
    the_project, the_path = x
    if not the_path:
      return the_project, None
    return the_project, the_path[0]
  try:
    dirname = state.DirName(argument)
    basename = state.BaseName(argument)
    if not basename:
      # For Containers, it'd also be fine to ignore a trailing slash.
      raise BadArgsError('Unexpected trailing "%s"' % FLAGS.pyatdl_separator)
  except state_module.InvalidPathError as e:
    raise BadArgsError(e)
  if not dirname and basename == '.':
    return (state.CurrentWorkingContainer(),
            _FindParentOf(state, state.CurrentWorkingContainer()))
  containr = state.GetContainerFromPath(dirname)
  if containr is state.ToDoList().root and basename == FLAGS.inbox_project_name:
    return state.ToDoList().inbox, None
  project_names = []
  for item in containr.items:
    if isinstance(item, prj.Prj):
      if not item.is_deleted:
        project_names.append(item.name)
        if the_uid == item.uid or item.name == basename:
          return item, containr
  for item in containr.items:
    if isinstance(item, prj.Prj):
      if item.is_deleted and item.name == basename:
          return item, containr
  if project_names:
    raise BadArgsError(
      'No such Project "%s". Choices: %s'
      % (basename,
         ' '.join(sorted(project_names))))
  else:
    raise BadArgsError(
      'No such Project "%s". There are no Projects in the current Folder.'
      % basename)


def _LookupFolder(state, argument):
  """Returns the specified Folder and its parent Container.

  Args:
    state: State
    argument: basestring
  Returns:
    Folder
  Raises:
    BadArgsError
    NoSuchContainerError
  """
  try:
    the_uid = lexer.ParseSyntaxForUID(argument)
  except lexer.Error as e:
    raise BadArgsError(e)
  if the_uid is not None:
    x = state.ToDoList().FolderByUID(the_uid)
    if x is None:
      raise NoSuchContainerError('No Folder exists with UID %s' % the_uid)
    the_folder, unused_path = x
    return the_folder
  try:
    dirname = state.DirName(argument)
    basename = state.BaseName(argument)
    if not basename:
      # For Containers, it'd also be fine to ignore a trailing slash.
      raise BadArgsError('Unexpected trailing "%s"' % FLAGS.pyatdl_separator)
  except state_module.InvalidPathError as e:
    raise BadArgsError(e)
  containr = state.GetContainerFromPath(dirname)
  folder_names = []
  for item in containr.items:
    if isinstance(item, folder.Folder):
      folder_names.append(item.name)
      if item.name == basename:
        return item
  if folder_names:
    raise NoSuchContainerError(
      'No such Folder "%s". Choices: %s'
      % (basename,
         ' '.join(sorted(folder_names))))
  else:
    raise NoSuchContainerError(
      'No such Folder "%s". There are no Folders within the specified Folder.'
      % basename)


def _LookupAction(state, argument):
  """Returns the specified Action and its containing Prj.

  Args:
    state: State
    argument: basestring
  Returns:
    (Action, Prj)
  Raises:
    BadArgsError
    NoSuchContainerError  # TODO(chandler37): This is a misnomer; NoSuchItemError?
  """
  try:
    the_uid = lexer.ParseSyntaxForUID(argument)
  except lexer.Error as e:
    raise BadArgsError(e)
  if the_uid is not None:
    x = state.ToDoList().ActionByUID(the_uid)  # None if the_uid is invalid
    if x is None:
      raise NoSuchContainerError('No Action with UID %s exists.' % the_uid)
    return x
  try:
    dirname = state.DirName(argument)
    basename = state.BaseName(argument)
    if not basename:
      raise BadArgsError('Unexpected trailing "%s"' % FLAGS.pyatdl_separator)
  except state_module.Error as e:
    raise BadArgsError(e)
  try:
    containr = state.GetContainerFromPath(dirname)
  except state_module.Error as e:
    raise BadArgsError(e)
  if not isinstance(containr, prj.Prj):
    raise BadArgsError(
      'This command only makes sense inside a Project, not inside "%s". See "help pwd".'
      % (containr.name if containr.name else FLAGS.pyatdl_separator,))
  action_names = []
  for item in containr.items:
    assert isinstance(item, action.Action), str(item)
    action_names.append(item.name)
    if the_uid == item.uid or item.name == basename:
      return item, containr
  if action_names:
    raise BadArgsError(
      'No such Action "%s". Choices: %s'
      % (basename,
         ' '.join(sorted(action_names))))
  else:
    raise BadArgsError(
      'No such Action "%s". There are no Actions in the current Project.'
      % basename)


def _LookupContext(state, argument):
  """Returns the specified Ctx.

  Args:
    state: State
    argument: basestring
  Returns:
    None|Ctx
  Raises:
    BadArgsError
  """
  # The Django UI uses UID 0 to mean <none> a.k.a. "Actions Without Context"
  if argument == 'uid=0' or argument == FLAGS.no_context_display_string:
    return None
  try:
    the_uid = lexer.ParseSyntaxForUID(argument)
  except lexer.Error as e:
    raise BadArgsError(e)
  if the_uid is not None:
    return state.ToDoList().ContextByUID(the_uid)  # None if the_uid is invalid
  return state.ToDoList().ContextByName(argument)


def _ExecuteUICmd(the_state, argv, generate_undo_info=True):
  """Executes a UICmd. Assumes it will not have an error.

  Args:
    the_state: State
    argv: [str]
    generate_undo_info: bool
  Returns:
    None
  Raises:
    Error
  """
  try:
    try:
      APP_NAMESPACE.FindCmdAndExecute(
        the_state, argv, generate_undo_info=generate_undo_info)
    except AssertionError as e:
      raise AssertionError('argv=%s err=%s' % (argv, str(e)))
  except (appcommandsutil.CmdNotFoundError,
          appcommandsutil.InvalidUsageError,
          appcommandsutil.IncorrectUsageError) as e:
    raise AssertionError('argv=%s error=%s' % (argv, str(e)))


class UICmd(appcommands.Cmd):  # pylint: disable=too-few-public-methods
  """Superclass for all UI commands."""
  @staticmethod
  def RaiseUnlessNArgumentsGiven(n, args):
    """Raises an exception unless the correct number of arguments was given.

    Args:
      n: int
      args: [str]
    Raises:
      BadArgsError  # TODO(chandler): Why not app.UsageError which prints
                    # full help? Should we abandon BadArgsError entirely,
                    # printing full help always?
    """
    assert n >= 1
    if len(args) != n + 1:  # $0 isn't an argument
      if len(args) < 2:
        if n == 1:
          raise BadArgsError('Needs a single positional argument; found none')
        else:
          raise BadArgsError('Needs %d positional arguments; found none' % n)
      else:
        if n == 1:
          raise BadArgsError('Needs a single positional argument; found these: %s' % repr(args[1:]))
        else:
          raise BadArgsError('Needs %d positional arguments; found these: %s' % (n, repr(args[1:])))

  @staticmethod
  def RaiseIfAnyArgumentsGiven(args):
    """Raises an exception unless there are no positional args.

    Args:
      args: [str]
    Raises:
      BadArgsError
    """
    if len(args) != 1:  # $0 isn't an argument
      raise BadArgsError(
        'Takes no arguments; found these arguments: %s' % repr(args[1:]))

  def IsUndoable(self):  # pylint: disable=no-self-use
    """Returns True iff this command is a mutation.

    Returns:
      bool
    """
    return False

  # def Run(self, args):
  #   """Override."""


class UndoableUICmd(UICmd):  # pylint: disable=too-few-public-methods
  """A command that mutates the to-do list.

  It would confuse the User if we undid a read-only command like 'ls';
  nothing would happen.
  """
  def IsUndoable(self):
    return True


class UICmdEcho(UICmd):
  """Echoes the arguments and prints a newline as the unix command echo(1) does.

  This is helpful for documenting lists of commands.
  """
  def __init__(self, name, flag_values, **kargs):
    super().__init__(name, flag_values, **kargs)
    flags.DEFINE_bool('stdout', False,
                      'For debugging, output directly to stdout.',
                      flag_values=flag_values)

  def Run(self, args):  # pylint: disable=missing-docstring,no-self-use
    p = ' '.join(x for x in args[1:])
    state = FLAGS.pyatdl_internal_state
    if FLAGS.stdout:
      print(p)
    else:
      state.Print(p)


class UICmdEcholines(UICmd):
  """Echoes the arguments, printing a newline after each.

  This is helpful for testing argument processing.
  """
  def Run(self, args):  # pylint: disable=missing-docstring,no-self-use
    state = FLAGS.pyatdl_internal_state
    for x in args[1:]:
      state.Print(x)


class UICmdChclock(UICmd):
  """Sets the system clock. Useful for unittests.

  There are two forms:
    chclock 1409712847.989031  # Absolute. Clock stops incrementing.
    chclock +1  # Relative. Clock does not stop.
  """
  def Run(self, args):  # pylint: disable=missing-docstring,no-self-use
    self.RaiseUnlessNArgumentsGiven(1, args)
    arg = args[-1]
    relative_not_absolute = False
    if arg.startswith('+'):
      relative_not_absolute = True
      arg = arg[1:]
      if arg.startswith('+'):
        raise BadArgsError('A leading \'++\' makes no sense.')
    assert arg, arg
    try:
      a_float = float(arg)
    except ValueError:
      raise BadArgsError(
        'Needs a numeric argument, seconds since the epoch (1970 CE). To move '
        'the clock relative to the old clock, prepend the argument with \'+\'. The argument: %s' % (repr(arg),))
    if a_float < 0 and not relative_not_absolute:
      raise BadArgsError('Minimum value is 0, a.k.a. 1970 CE.')
    if relative_not_absolute:
      old_time = time.time

      def NewTime():  # pylint: disable=missing-docstring
        return old_time() + a_float
      time.time = NewTime
    else:

      def AbsoluteNewTime():  # pylint: disable=missing-docstring
        return a_float
      time.time = AbsoluteNewTime


class UICmdLs(UICmd):
  """Lists immediate contents of the current working Folder/Project (see "help pwd").

  The 'view' command (see 'help view') controls which items are visible. 'ls -a'
  ignores the view filter and shows all items, including '.', the working
  directory, and '..', its parent.

  The following timestamps are displayed when the '-l' argument is given:

  * ctime: Time of creation
  * mtime: Time of last modification
  * dtime: Time of deletion
  """
  def __init__(self, name, flag_values, **kargs):
    super().__init__(name, flag_values, **kargs)
    flags.DEFINE_bool('show_all', False,
                      'Additionally lists everything, even hidden objects, '
                      'overriding the view filter',
                      short_name='a', flag_values=flag_values)
    flags.DEFINE_bool('recursive', False,
                      'Additionally lists subdirectories/subprojects recursively',
                      short_name='R', flag_values=flag_values)
    flags.DEFINE_bool('show_timestamps', False,
                      'Additionally lists timestamps ctime, dtime, mtime',
                      short_name='l', flag_values=flag_values)
    flags.DEFINE_enum('view_filter', None, sorted(view_filter.CLS_BY_UI_NAME),
                      'Instead of using the global view filter (see "help '
                      'view"), override it and use this view filter. Note: '
                      'this is ignored in --show_all mode',
                      short_name='v', flag_values=flag_values)

  def Run(self, args):  # pylint: disable=missing-docstring,no-self-use
    state = FLAGS.pyatdl_internal_state
    override = None
    if FLAGS.view_filter:
      override = state.NewViewFilter(
        filter_cls=view_filter.CLS_BY_UI_NAME[FLAGS.view_filter])

    def DoIt(obj, location):  # pylint: disable=missing-docstring
      _PerformLs(obj, location, state,
                 recursive=FLAGS.recursive, show_uid=FLAGS.pyatdl_show_uid,
                 show_all=FLAGS.show_all, show_timestamps=FLAGS.show_timestamps,
                 view_filter_override=override)

    if len(args) == 1:
      DoIt(state.CurrentWorkingContainer(), '.')
    else:
      for i, name in enumerate(args[1:]):
        try:
          dirname = state.DirName(name)
          basename = state.BaseName(name)
          if not basename and name != FLAGS.pyatdl_separator:
            raise BadArgsError(
              'Unexpected trailing "%s"; dirname=%s and basename=%s'
              % (FLAGS.pyatdl_separator, dirname, basename))
          obj = state.GetObjectFromPath(name)
        except state_module.InvalidPathError as e:
          raise BadArgsError(e)
        if isinstance(obj, container.Container) and len(args) > 2:
          state.Print('%s:' % name)
        DoIt(obj, dirname)
        if i < len(args) - 2:
          state.Print('')


def _FindParentOf(state, obj):
  """Returns the Container that contains obj, or
  state.ToDoList().root if obj is '/' or a Context.

  Args:
    obj: AuditableObject
  Returns:
    Container
  """
  item = None
  if isinstance(obj, ctx.Ctx):
    return state.ToDoList().root
  for (c, path) in state.ToDoList().ContainersPreorder():
    if c.uid == obj.uid:
      if path:
        item = path[0]
      else:
        item = state.ToDoList().root
      break
    for subitem in c.items:
      if subitem.uid == obj.uid:
        item = c
        break
    if item is not None:
      break
  else:
    raise AssertionError(
      'Cannot happen.  %s %s %s'
      % (state.CurrentWorkingContainer().name, str(state.ToDoList().root),
         obj.uid))
  return item


def _PerformLs(current_obj, location, state, recursive, show_uid, show_all,  # pylint: disable=too-many-arguments
               show_timestamps, view_filter_override=None):
  """Performs 'ls'.

  Args:
    current_obj: AuditableObject
    location: basestring
    state: State
    recursive: bool
    show_uid: bool
    show_all: bool
    show_timestamps: bool
    view_filter_override: None|ViewFilter
  """
  if show_all and isinstance(current_obj, container.Container):
    state.Print(_ListingForOneItem(
        show_uid,
        show_timestamps,
        current_obj,
        state.ToDoList(),
        '.'))
    state.Print(_ListingForOneItem(
        show_uid,
        show_timestamps,
        _FindParentOf(state, current_obj),
        state.ToDoList(),
        '..'))

  if hasattr(current_obj, 'items'):
    items = list(current_obj.items)
    if current_obj is state.ToDoList().root:
      items.insert(0, state.ToDoList().inbox)
  else:
    items = [current_obj]
  if state.CurrentSorting() == 'alpha' and not isinstance(current_obj, prj.Prj):
    items.sort(key=lambda x: '' if x.uid == 1 else x.name)
  items.sort(key=lambda x: 0 if isinstance(x, folder.Folder) or x.uid == 1 else 1)
  to_recurse = []
  for item in items:
    the_view_filter = view_filter_override if view_filter_override is not None else state.ViewFilter()
    if show_all or the_view_filter.Show(item):
      q = _ListingForOneItem(show_uid, show_timestamps, item, state.ToDoList())
      state.Print(q)
      if recursive and isinstance(item, container.Container):
        to_recurse.append((item, location))
  for obj, loc in to_recurse:
    state.Print('')
    if loc:
      state.Print('%s%s%s:'
                  % (loc if loc != FLAGS.pyatdl_separator else '',
                     FLAGS.pyatdl_separator, obj.name))
    else:
      state.Print('%s:' % obj.name)
    _PerformLs(obj,
               '%s%s%s'
               % (loc if loc != FLAGS.pyatdl_separator else '',
                  FLAGS.pyatdl_separator, obj.name),
               state, recursive, show_uid, show_all, show_timestamps,
               view_filter_override)


class UICmdLsctx(UICmd):
  """Lists all Contexts, or, with one argument, details of a single context.

  The following timestamps are displayed when the '-l' argument is given:

  * ctime: Time of creation
  * mtime: Time of last modification
  * dtime: Time of deletion
  """
  def __init__(self, name, flag_values, **kargs):
    super().__init__(name, flag_values, **kargs)
    flags.DEFINE_bool('show_timestamps', False,
                      'Additionally lists timestamps ctime, dtime, mtime',
                      short_name='l', flag_values=flag_values)
    flags.DEFINE_bool('json', False, 'Output JSON', flag_values=flag_values)

  def Run(self, args):  # pylint: disable=missing-docstring,no-self-use
    state = FLAGS.pyatdl_internal_state
    to_be_json = []
    if len(args) == 2:
      context = _LookupContext(state, args[-1])
      if context is None:
        raise BadArgsError('No such Context "%s"' % args[-1])
      if FLAGS.json:
        to_be_json = _JsonForOneItem(  # pylint: disable=redefined-variable-type
          context,
          state.ToDoList(),
          sum(1 for a, _ in state.ToDoList().ActionsInContext(context.uid)
              if state.ViewFilter().ShowAction(a)))
      else:
        state.Print(
            _ListingForContext(FLAGS.pyatdl_show_uid, FLAGS.show_timestamps, context))
    else:
      if len(args) != 1:
        raise BadArgsError(
          'Takes zero or one arguments; found these arguments: %s' % repr(args[1:]))
      if FLAGS.json:
        to_be_json.append(_JsonForOneItem(
          None,
          state.ToDoList(),
          sum(1 for a, _ in state.ToDoList().ActionsInContext(None)
              if state.ViewFilter().ShowAction(a))))
      else:
        state.Print(
            _ListingForContext(FLAGS.pyatdl_show_uid, FLAGS.show_timestamps, None))
      sorted_contexts = list(state.ToDoList().ctx_list.items)
      if state.CurrentSorting() == 'alpha':
        sorted_contexts.sort(key=lambda c: c.name)
      for c in sorted_contexts:
        if state.ViewFilter().ShowContext(c):
          if FLAGS.json:
            to_be_json.append(_JsonForOneItem(
              c,
              state.ToDoList(),
              sum(1 for a, _ in state.ToDoList().ActionsInContext(c.uid)
                  if state.ViewFilter().ShowAction(a))))
          else:
            state.Print(
                _ListingForContext(FLAGS.pyatdl_show_uid, FLAGS.show_timestamps, c))
    if FLAGS.json:
      state.Print(json.dumps(to_be_json, sort_keys=True, separators=(',', ':')))


class UICmdLsprj(UICmd):
  """Without arguments, lists all Projects. Or takes one argument, a Project, and lists its details.

  See also command 'ls'.
  """
  def __init__(self, name, flag_values, **kargs):
    super().__init__(name, flag_values, **kargs)
    flags.DEFINE_bool('json', False, 'Output JSON', flag_values=flag_values)

  def Run(self, args):  # pylint: disable=missing-docstring,no-self-use
    state = FLAGS.pyatdl_internal_state
    if len(args) == 2:
      try:
        the_project, parent_container = _LookupProject(state, args[-1])
      except NoSuchContainerError as e:
        raise BadArgsError(e)
      to_be_json = _JsonForOneItem(
        the_project,
        state.ToDoList(),
        sum(1 for a in the_project.items if state.ViewFilter().ShowAction(a)))
      to_be_json['max_seconds_before_review'] = the_project.max_seconds_before_review
      if parent_container is None:
        # /inbox is weird:
        to_be_json['parent_path'] = state.ContainerAbsolutePath(state.ToDoList().root)
      else:
        to_be_json['parent_path'] = state.ContainerAbsolutePath(parent_container)
      if not FLAGS.json:
        raise BadArgsError('With an argument, --json is required')
      state.Print(json.dumps(to_be_json, sort_keys=True, separators=(',', ':')))
    else:
      if len(args) != 1:  # $0 isn't an argument
        raise BadArgsError(
          'Takes zero or one arguments; found these arguments: %s' % repr(args[1:]))
      to_be_json = []  # pylint: disable=redefined-variable-type
      sorted_projects = list(state.ToDoList().Projects())
      if state.CurrentSorting() == 'alpha':
        def AlphaKey(p_path):
          p, path = p_path
          return '' if p.uid == 1 else p.name

        sorted_projects.sort(key=AlphaKey)  # secondary key (stable sort)
      else:
        def ReverseChronoKey(p_path):
          p, path = p_path
          return float('-inf') if p.uid == 1 else -p.ctime

        sorted_projects.sort(key=ReverseChronoKey)  # secondary key (stable sort)

      def ActiveDoneKey(p_path):
        p, path = p_path
        return (
          1 if p.is_deleted else 0,
          1 if p.is_complete else 0,
          0 if p.is_active else 1)

      sorted_projects.sort(key=ActiveDoneKey)  # primary key
      for project, path_leaf_first in sorted_projects:
        if state.ViewFilter().ShowProject(project):
          if FLAGS.json:
            to_be_json.append(_JsonForOneItem(
                project,
                state.ToDoList(),
                sum(1 for a in project.items if state.ViewFilter().ShowAction(a)),
                path_leaf_first=path_leaf_first))
          else:
            state.Print(_ProjectString(project, path_leaf_first))
      if FLAGS.json:
        state.Print(json.dumps(to_be_json, sort_keys=True, separators=(',', ':')))


class UICmdLoadtest(UICmd):
  """Helps perform a load test, i.e. creates N Projects, N Actions, N Contexts,
  etc."""
  def __init__(self, name, flag_values, **kargs):
    super().__init__(name, flag_values, **kargs)
    flags.DEFINE_string('name', 'LoadTest', 'Name fragment',
                        flag_values=flag_values)
    flags.DEFINE_integer('n', None, 'Number of Actions and Projects etc.',
                         flag_values=flag_values)
    flags.DEFINE_bool('deep', True,
                      'Makes a deeply nested Folder containing one Project and'
                      ' one Action',
                      flag_values=flag_values)

  def Run(self, args):  # pylint: disable=missing-docstring,no-self-use
    state = FLAGS.pyatdl_internal_state
    self.RaiseIfAnyArgumentsGiven(args)
    if FLAGS.n is None or FLAGS.n < 0:
      raise BadArgsError('Argument --n is required and must be nonnegative')
    if not FLAGS.name:
      raise BadArgsError('Argument --name cannot be empty')

    def NoneShallPassPrinter(s):
      """A Printer that aborts if anything is printed."""
      raise AssertionError('Nothing should be printed but we see %s' % s)

    saved_cwd = state.CurrentWorkingContainer()
    saved_printer = state.Printer()
    state.SetPrinter(NoneShallPassPrinter)
    try:
      for i in xrange(FLAGS.n):
        _ExecuteUICmd(state, ['mkctx', '--ignore_existing',
                              'C%s%d' % (FLAGS.name, i)])
        fldr = '%sF%s%d' % (FLAGS.pyatdl_separator, FLAGS.name, i)
        _ExecuteUICmd(state, ['cd', FLAGS.pyatdl_separator])
        _ExecuteUICmd(state, ['mkdir', fldr])
        _ExecuteUICmd(state, ['cd', fldr])
        project = 'P%s%d' % (FLAGS.name, i)
        _ExecuteUICmd(state, ['mkprj', project])
        _ExecuteUICmd(state, ['cd', project])
        _ExecuteUICmd(state, ['mkact', 'A%s%d' % (FLAGS.name, i)])
      state.SetCurrentWorkingContainer(state.ToDoList().root)
      if FLAGS.deep:
        for i in xrange(FLAGS.n):
          deep_folder = 'DeepFolder%s%d' % (FLAGS.name, i)
          _ExecuteUICmd(state, ['mkdir', deep_folder])
          _ExecuteUICmd(state, ['cd', deep_folder])
        if FLAGS.n:
          _ExecuteUICmd(state, ['mkprj', 'DeepProject'])
          _ExecuteUICmd(state, ['cd', 'DeepProject'])
          _ExecuteUICmd(state, ['mkact', 'DeepAction'])
      _ExecuteUICmd(state, ['cd', '%s%s' % (FLAGS.pyatdl_separator,
                                            FLAGS.inbox_project_name)])
      long_action_name = 'ALongName'
      for i in xrange(FLAGS.n):
        long_action_name += FLAGS.name
        inbox_action = 'Ainbox%s%d' % (FLAGS.name, i)
        _ExecuteUICmd(state, ['mkact', inbox_action])
      if FLAGS.n:
        _ExecuteUICmd(state, ['mkact', long_action_name])
    finally:
      state.SetCurrentWorkingContainer(saved_cwd)
      state.SetPrinter(saved_printer)
    # TODO(chandler): Test undo. 'cd /inbox;mkctx a;mkctx b;loadtest;undo'


class UICmdConfigurereview(UndoableUICmd):
  """Changes how a Project is treated during a Review.

  Usage: configurereview --max_seconds_before_review=86400 ProjectName
  """
  def __init__(self, name, flag_values, **kargs):
    super().__init__(name, flag_values, **kargs)
    flags.DEFINE_float('max_seconds_before_review', None,
                       'How long can this project go without a review?',
                       flag_values=flag_values)
    # TODO(chandler): Add bounds checking via 'lower_bound'/'upper_bound'
    # TODO(chandler): Document how you say 'never needs review'; test case.

  def Run(self, args):  # pylint: disable=missing-docstring,no-self-use
    state = FLAGS.pyatdl_internal_state
    self.RaiseUnlessNArgumentsGiven(1, args)
    if FLAGS.max_seconds_before_review is None:
      raise BadArgsError('Must specify --max_seconds_before_review.')
    try:
      the_project, unused_parent_container = _LookupProject(state, args[-1])
    except NoSuchContainerError as e:
      raise BadArgsError(e)
    the_project.max_seconds_before_review = FLAGS.max_seconds_before_review


class UICmdDump(UICmd):
  """Prints pseudo-XML of the entire database regardless of view options.

  Beware escaping.  This is not real XML.  And no code yet exists to
  parse this representation back into a usable save file.

  This misses some things, e.g. the ctime/dtime/mtime timestamps.
  """
  def __init__(self, name, flag_values, **kargs):
    super().__init__(name, flag_values, **kargs)
    flags.DEFINE_bool('multi', False,
                      'For internal use only. Calls State.Print() once per line'
                      ' instead of once per string',
                      short_name='m', flag_values=flag_values)

  def Run(self, args):  # pylint: disable=missing-docstring,no-self-use
    state = FLAGS.pyatdl_internal_state
    self.RaiseIfAnyArgumentsGiven(args)
    text = str(state.ToDoList())
    if FLAGS.multi:
      for line in text.splitlines():
        state.Print(line)
    else:
      state.Print(text)


class UICmdDo(UICmd):  # TODO(chandler): UndoableUICmd, correct?
  """Creates an action in the Inbox, allowing forward slashes.

  If a context name appears in the action, that context will be assigned.

  This is conceptually a shortcut for '(cd /inbox && mkact --allow_slashes
  "$*")'; it does not leave you in the Inbox, though.

  Takes any number of arguments, concatenating them to make a single action.
  """
  def Run(self, args):  # pylint: disable=missing-docstring,no-self-use
    state = FLAGS.pyatdl_internal_state
    if len(args) == 1:  # $0 isn't an argument
      raise BadArgsError('Found no arguments.')
    if len(args) == 2:
      action_name = args[-1]
    else:
      action_name = ' '.join(pipes.quote(arg) for arg in args[1:])
    cwc = state.CurrentWorkingContainer()
    state.SetCurrentWorkingContainer(state.GetContainerFromPath('uid=1'))
    try:
      APP_NAMESPACE.FindCmdAndExecute(
        state,
        ['touch',  # mkact
         '--autoprj',
         '--allow_slashes',
         action_name])
    finally:
      state.SetCurrentWorkingContainer(cwc)


class UICmdMaybe(UICmd):  # aspire, maybe TODO(chandler): UndoableUICmd, correct?
  """Creates an action in the Inbox, allowing forward slashes, in the
  @someday/maybe context.

  This is conceptually a shortcut for '(cd /inbox && mkact -c @someday/maybe
  --allow_slashes "$*")'; it does not leave you in the Inbox, though.

  Takes any number of arguments, concatenating them to make a single action.
  """
  def Run(self, args):  # pylint: disable=missing-docstring,no-self-use
    state = FLAGS.pyatdl_internal_state
    if len(args) == 1:  # $0 isn't an argument
      raise BadArgsError('Found no arguments.')
    if len(args) == 2:
      action_name = args[-1]
    else:
      action_name = ' '.join(pipes.quote(arg) for arg in args[1:])
    cwc = state.CurrentWorkingContainer()
    state.SetCurrentWorkingContainer(state.GetContainerFromPath('uid=1'))
    try:
      APP_NAMESPACE.FindCmdAndExecute(
        state,
        ['touch',  # mkact
         '--autoprj',
         '-c',
         '@someday/maybe',
         '--allow_slashes',
         action_name])
    finally:
      state.SetCurrentWorkingContainer(cwc)


class UICmdAsTaskPaper(UICmd):  # astaskpaper a.k.a. txt
  """Exports the undeleted contents of your to-do list in TaskPaper format (text).

  See http://imissmymac.com/wp-content/uploads/2013/02/TaskPaper-Users-Guide.pdf
  and https://www.taskpaper.com/
  """
  def Run(self, args):  # pylint: disable=missing-docstring,no-self-use
    state = FLAGS.pyatdl_internal_state
    self.RaiseIfAnyArgumentsGiven(args)
    lines = []
    state.ToDoList().AsTaskPaper(lines,
                                 show_project=state.ViewFilter().ShowProject,
                                 show_action=state.ViewFilter().ShowAction)
    for i, line in enumerate(lines):
      if i != 0 or line:  # skips blank first line
        state.Print(line)


class UICmdHypertext(UICmd):
  """Prints a hypertext version of your to-do list."""
  def __init__(self, name, flag_values, **kargs):
    super().__init__(name, flag_values, **kargs)
    flags.DEFINE_string('search_query', None,
                        'Search query, case-insensitive',
                        short_name='q', flag_values=flag_values)

  def Run(self, args):  # pylint: disable=missing-docstring,no-self-use
    lines = []

    def DoIt(*, show_active, show_done):
      the_view_filter = state.ViewFilter()
      if FLAGS.search_query:
        the_view_filter = state.SearchFilter(
          query=FLAGS.search_query, show_active=show_active, show_done=show_done)

      def ShowProject(p):
        if not the_view_filter.ShowProject(p):
          return False
        if FLAGS.search_query:
          return True
        if bool(p.is_active) is not bool(show_active):
          return False
        if bool(p.is_complete or p.is_deleted) is not bool(show_done):
          return False
        return True

      def ShowNote(n):
        if not FLAGS.search_query:
          return True
        if not n:
          return False
        return FLAGS.search_query.lower() in n.lower()

      state.ToDoList().AsTaskPaper(lines,
                                   show_project=ShowProject,
                                   show_action=the_view_filter.ShowAction,
                                   show_note=ShowNote,
                                   hypertext_prefix=args[-1],
                                   html_escaper=state.HTMLEscaper())

    state = FLAGS.pyatdl_internal_state
    self.RaiseUnlessNArgumentsGiven(1, args)

    def Header(s):
      lines.append(f'<h2>{s}</h2>')

    Header('Active and not yet done items:')
    DoIt(show_active=True, show_done=False)
    Header('Inactive and not yet done items:')
    DoIt(show_active=False, show_done=False)
    Header('Active, already done items:')
    DoIt(show_active=True, show_done=True)
    Header('Inactive, already done items:')
    DoIt(show_active=False, show_done=True)
    for i, line in enumerate(lines):
      if i != 0 or line:  # skips blank first line
        state.Print('%s<br>' % line)


class UICmdDumpprotobuf(UICmd):
  """Prints the text form of the protocol message (a.k.a. protocol buffer,
  protobuf) that is the entire database (regardless of view options).
  """
  def Run(self, args):  # pylint: disable=missing-docstring,no-self-use
    state = FLAGS.pyatdl_internal_state
    self.RaiseIfAnyArgumentsGiven(args)
    state.Print(text_format.MessageToString(state.ToDoList().AsProto()))


class UICmdChctx(UndoableUICmd):
  """Given a context's name and an action's name, changes the action's context.

  E.g., chctx @home /inbox/play

  The string FLAGS.no_context_display_string (default="<none>") is special
  -- it means to delete the context. You may also use the notation 'uid=0' to
  delete the context.
  """
  def __init__(self, name, flag_values, **kargs):
    super().__init__(name, flag_values, **kargs)
    flags.DEFINE_bool('autorename', True, 'Change Action name to match the new context?', flag_values=flag_values)

  def Run(self, args):  # pylint: disable=missing-docstring,no-self-use
    state = FLAGS.pyatdl_internal_state
    self.RaiseUnlessNArgumentsGiven(2, args)
    ctx_name, action_name = args[-2:]
    delete_ctx = ctx_name == FLAGS.no_context_display_string or ctx_name == 'uid=0'
    context = _LookupContext(state, ctx_name)
    if context is None and not delete_ctx:
      raise BadArgsError('No such Context "%s"' % ctx_name)
    try:
      an_action, unused_project = _LookupAction(state, action_name)
    except NoSuchContainerError as e:
      raise BadArgsError(e)
    assert delete_ctx or context.uid != 0, ctx_name
    old_ctx_uid = an_action.ctx_uid
    an_action.ctx_uid = None if delete_ctx else context.uid
    if FLAGS.autorename and old_ctx_uid is not None:
      old_ctx = _LookupContext(state, f'uid={old_ctx_uid}')
      an_action.name = re.sub(
        re.escape(old_ctx.name) + r'\b',
        old_ctx.name.replace('@', 'at ', 1) if context is None else context.name,
        an_action.name)


class UICmdChdefaultctx(UndoableUICmd):
  """Given a context's name and an action's name, changes the action's context.

  E.g., chdefaultctx @home /packingchecklist

  The string FLAGS.no_context_display_string (default="<none>") is special
  -- it means to delete the default context. You may also use the notation
  'uid=0' to delete the context.
  """
  def Run(self, args):  # pylint: disable=missing-docstring,no-self-use
    state = FLAGS.pyatdl_internal_state
    self.RaiseUnlessNArgumentsGiven(2, args)
    ctx_name, project_name = args[-2:]
    delete_ctx = ctx_name == FLAGS.no_context_display_string or ctx_name == 'uid=0'
    context = _LookupContext(state, ctx_name)
    if context is None and not delete_ctx:
      raise BadArgsError('No such Context "%s"' % ctx_name)
    try:
      project, unused_parent_container = _LookupProject(state, project_name)
    except NoSuchContainerError as e:
      raise BadArgsError(e)
    project.default_context_uid = None if context is None else context.uid
    for item in project.items:
      if item.ctx_uid is None:
        item.ctx_uid = context.uid


class UICmdLsact(UndoableUICmd):
  """Displays all data regarding an Action.

  Ignores the view filter.
  """
  def __init__(self, name, flag_values, **kargs):
    super().__init__(name, flag_values, **kargs)
    flags.DEFINE_bool('json', False, 'Output JSON', flag_values=flag_values)

  def Run(self, args):  # pylint: disable=missing-docstring,no-self-use
    state = FLAGS.pyatdl_internal_state
    if not FLAGS.json:
      # TODO(chandler): Make it not so:
      raise BadArgsError(
          '--json is required; see "help ls" and consider using "ls -a"')
    self.RaiseUnlessNArgumentsGiven(1, args)
    action_name = args[-1]
    try:
      an_action, a_project = _LookupAction(state, action_name)
    except NoSuchContainerError as e:
      raise BadArgsError(e)
    to_be_json = _JsonForOneItem(an_action, state.ToDoList(), 1)
    # javascript cannot handle 64-bit integers:
    to_be_json['project_uid'] = None if a_project.uid is None else str(a_project.uid)
    to_be_json['project_path'] = state.ContainerAbsolutePath(a_project)
    to_be_json['display_project_path'] = state.ContainerAbsolutePath(
      a_project, display=True)
    if FLAGS.json:
      state.Print(json.dumps(to_be_json, sort_keys=True, separators=(',', ':')))


def _PerformComplete(state, item_name, mark_complete, force):
  """Performs 'complete'/'uncomplete'.

  If force is True and mark_complete is True, all descendants are marked
  complete first. Without force an error is raised if mark_complete is
  True and any descendant is incomplete.

  To ease the creation of checklists, uncompleting a non-Inbox project
  uncompletes all its undeleted actions.
  """
  item = None
  containing_prj = None
  try:
    item, containing_prj = _LookupAction(state, item_name)
  except (BadArgsError, NoSuchContainerError):
    pass
  if item is None:
    try:
      item, unused_parent_container = _LookupProject(state, item_name)
    except NoSuchContainerError as e:
      raise BadArgsError(e)
  if item is state.ToDoList().inbox:
    if mark_complete:
      raise BadArgsError(
        'The project /%s is special and cannot be marked complete.'
        % FLAGS.inbox_project_name)
  if not mark_complete and isinstance(item, container.Container):
    for c, unused_path in item.ContainersPreorder():
      for a in c.items:
        if isinstance(a, action.Action):
          a.is_complete = False
  if mark_complete and isinstance(item, container.Container):
    for c, unused_path in item.ContainersPreorder():
      for a in c.items:
        if isinstance(a, action.Action) and not a.is_complete:
          if force:
            a.is_complete = True
          else:
            if not a.is_deleted:
              raise BadArgsError(
                'Cannot mark complete (without --force flag) because a descendant action is incomplete: %s'
                % str(a))
  if not mark_complete and containing_prj is not None:
    containing_prj.is_complete = False
  item.is_complete = mark_complete


class UICmdComplete(UndoableUICmd):
  """Marks as "complete" an Action or Prj."""
  def __init__(self, name, flag_values, **kargs):
    super().__init__(name, flag_values, **kargs)
    flags.DEFINE_bool('force',
                      False,
                      'First marks all descendant actions complete',
                      short_name='f',
                      flag_values=flag_values)

  def Run(self, args):  # pylint: disable=missing-docstring,no-self-use
    state = FLAGS.pyatdl_internal_state
    self.RaiseUnlessNArgumentsGiven(1, args)
    _PerformComplete(state, args[-1], mark_complete=True, force=FLAGS.force)


class UICmdUncomplete(UndoableUICmd):
  """Marks as "incomplete" an Action or Prj."""
  def Run(self, args):  # pylint: disable=missing-docstring,no-self-use
    state = FLAGS.pyatdl_internal_state
    self.RaiseUnlessNArgumentsGiven(1, args)
    _PerformComplete(state, args[-1], mark_complete=False, force=False)


class UICmdSort(UICmd):
  """Displays or changes how folders, projects, and contexts are sorted.

  Actions within a project are always sorted chronologically because so often they are entered in sequence. They are
  sorted reverse chronologically because the most recently entered item is often the one you want, so we save you from
  scrolling down.

  Your choices are:

  * alpha: Sorts alphabetically, case-sensitively.
  * chrono: Sorts reverse chronologically.

  Without arguments, prints the current setting. With a single argument, changes
  the setting.

  """
  def Run(self, args):  # pylint: disable=missing-docstring,no-self-use
    state = FLAGS.pyatdl_internal_state
    if len(args) == 1:
      state.Print(state.CurrentSorting())
      return
    self.RaiseUnlessNArgumentsGiven(1, args)
    setting_name = args[-1]
    if setting_name not in state.AllSortingOptions():
      raise BadArgsError(
        'No such sort setting "%s": See "help sort".' % setting_name)
    state.SetSorting(setting_name)


def _SetViewFilterByName(filter_name, state):
  the_view_filter = view_filter.CLS_BY_UI_NAME.get(filter_name, None)
  if the_view_filter is None:
    raise BadArgsError(
      'No such view filter "%s": See "help view".' % filter_name)
  state.SetViewFilter(state.NewViewFilter(the_view_filter))


class UICmdTodo(UICmd):
  """Displays incomplete items.

  Without arguments, uses the incomplete view filter. With the sole argument
  'now', uses the 'actionable' view filter. With any other argument, uses the
  named view filter. See 'help view'.

  Alternatively, to match the behavior of 'ls -v', you can pass in a view
  filter using the '-v' flag.
  """
  def __init__(self, name, flag_values, **kargs):
    super().__init__(name, flag_values, **kargs)
    flags.DEFINE_enum('view_filter', None, sorted(view_filter.CLS_BY_UI_NAME),
                      'View filter',
                      short_name='v', flag_values=flag_values)

  def Run(self, args):  # pylint: disable=missing-docstring,no-self-use
    state = FLAGS.pyatdl_internal_state
    if len(args) == 1:
      filter_name = 'incomplete'
    else:
      self.RaiseUnlessNArgumentsGiven(1, args)
      filter_name = args[-1]
      if filter_name == 'now':
        filter_name = 'actionable'
    if FLAGS.view_filter:
      if len(args) == 2 and args[-1] != FLAGS.view_filter:
        raise BadArgsError('Conflicting view filters')
      filter_name = FLAGS.view_filter
    old_view_filter = state.ViewFilter().ViewFilterUINames()[0]
    _SetViewFilterByName(filter_name, state)
    try:
      lines = []
      state.ToDoList().AsTaskPaper(lines,
                                   show_project=state.ViewFilter().ShowProject,
                                   show_action=state.ViewFilter().ShowAction)
      for i, line in enumerate(lines):
        if i != 0 or line:  # skips blank first line
          state.Print(line)
    finally:
      _SetViewFilterByName(old_view_filter, state)


class UICmdView(UICmd):
  """Displays or changes which folders, projects, actions, and contexts to display.

  Your choices are:

  * all_even_deleted: Shows absolutely everything.
  * all: Shows everything but deleted items.
  * default: Resets.
  * incomplete: Shows all not-deleted, incomplete items, even if inactive.
  * actionable: Shows only not-deleted, incomplete, active items.
  * needing_review: Shows only not-deleted, incomplete items needing review.
  * inactive_and_incomplete: Shows not-deleted, incomplete items in inactive projects or contexts.

  Without arguments, prints the current filter. Note that 'default' is an alias.
  With a single argument, sets the filter.
  """
  def Run(self, args):  # pylint: disable=missing-docstring,no-self-use
    state = FLAGS.pyatdl_internal_state
    if len(args) == 1:
      state.Print(state.ViewFilter().ViewFilterUINames()[0])
      return
    self.RaiseUnlessNArgumentsGiven(1, args)
    _SetViewFilterByName(args[-1], state)


class UICmdInctx(UICmd):
  """Prints Actions in the given Context."""
  def __init__(self, name, flag_values, **kargs):
    super().__init__(name, flag_values, **kargs)
    flags.DEFINE_bool('json', False, 'Output JSON', flag_values=flag_values)
    flags.DEFINE_enum('sort_by', 'natural', ['natural', 'ctime'],
                      'Sort by what? Sorting by ctime (creation time) sorts '
                      'intuitively. Sorting naturally gives an arbitrary but '
                      'deterministic order.',
                      short_name='s', flag_values=flag_values)

  def Run(self, args):  # pylint: disable=missing-docstring,no-self-use
    state = FLAGS.pyatdl_internal_state
    self.RaiseUnlessNArgumentsGiven(1, args)
    ctx_name = args[-1]
    ctx_uid = None
    # UIDs start at 1, but we say UID 0 refers to the Context that contains
    # Actions without any Context.
    if ctx_name != FLAGS.no_context_display_string and ctx_name != 'uid=0':
      try:
        ctx_uid = lexer.ParseSyntaxForUID(ctx_name)
      except lexer.Error as e:
        raise BadArgsError(e)
      if ctx_uid is None:
        try:
          ctx_uid = state.ToDoList().ctx_list.ContextUIDFromName(ctx_name)
        except ctx.NoSuchNameError as e:
          raise BadArgsError(e)
    action_prj_tuples = list(state.ToDoList().ActionsInContext(ctx_uid))
    if FLAGS.sort_by == 'ctime':
      action_prj_tuples.sort(reverse=True, key=lambda a_p: a_p[0].ctime)
    to_be_json = []
    for a, p in action_prj_tuples:
      if state.ViewFilter().ShowAction(a):
        if FLAGS.json:
          to_be_json.append(_JsonForOneItem(
            a, state.ToDoList(), 1, in_prj=p.name))
        else:
          state.Print(_ListingForOneItem(
            show_uid=FLAGS.pyatdl_show_uid, show_timestamps=False, item=a,
            to_do_list=state.ToDoList(), in_context_override=''))
    if FLAGS.json:
      state.Print(json.dumps(to_be_json, sort_keys=True, separators=(',', ':')))


class UICmdInprj(UICmd):
  """Prints Actions in the given Project."""
  def __init__(self, name, flag_values, **kargs):
    super().__init__(name, flag_values, **kargs)
    flags.DEFINE_bool('json', False, 'Output JSON', flag_values=flag_values)

  def Run(self, args):  # pylint: disable=missing-docstring,no-self-use
    state = FLAGS.pyatdl_internal_state
    self.RaiseUnlessNArgumentsGiven(1, args)
    try:
      the_project, unused_parent_container = _LookupProject(state, args[-1])
    except NoSuchContainerError as e:
      raise BadArgsError(e)
    to_be_json = []

    def ActionToContext(an_action):
      if an_action.ctx_uid is None:
        return None
      for c in state.ToDoList().ctx_list.items:
        if c.uid == an_action.ctx_uid:
          return c
      raise ValueError(
        'No Context found for action "%s" even though that action has a context UID of "%s"'
        % (an_action.uid, an_action.ctx_uid))

    def SecondaryKey(an_action):
      return -an_action.ctime  # reverse chronological

    def PrimaryKey(an_action):
      if an_action.is_deleted:
        return 100
      if an_action.is_complete:
        return 90
      if the_project.uid != 1:  # the inbox is special because primary=done, secondary=chrono is more intuitive there
        c = ActionToContext(an_action)
        if c is None:
          return 0
        if c.is_deleted or not c.is_active:
          return 80
      return 10

    s = sorted(the_project.items, key=SecondaryKey)  # Python's sorting is stable
    for a in sorted(s, key=PrimaryKey):
      if state.ViewFilter().ShowAction(a):
        if FLAGS.json:
          to_be_json.append(_JsonForOneItem(a, state.ToDoList(), 1))
        else:
          state.Print(_ListingForOneItem(
            show_uid=FLAGS.pyatdl_show_uid, show_timestamps=False, item=a,
            to_do_list=state.ToDoList()))
    if FLAGS.json:
      state.Print(json.dumps(to_be_json, sort_keys=True, separators=(',', ':')))


class UICmdCd(UndoableUICmd):  # undoable because 'mkact A' must know its CWD
  """Changes current working directory to the named directory. See cd(1).
  Special locations include ".." (parent directory), "/" (root directory).

  Projects and Folders are treated alike.

  Because projects and folders are often named uniquely, it is possible to
  change working directory regardless of the current working
  directory. The argument '-R' (a.k.a. --recursive) does so. E.g., 'cd -R Px'
  will change to the folder or project named "Px".
  """
  def __init__(self, name, flag_values, **kargs):
    super().__init__(name, flag_values, **kargs)
    flags.DEFINE_bool('recursive', False,
                      'Instead of looking only in the current working directory'
                      ' (see "help pwd"), look at all directories',
                      short_name='R', flag_values=flag_values)
    flags.DEFINE_bool('swallow_errors', False,
                      'Fail silently',
                      flag_values=flag_values)

  def Run(self, args):  # pylint: disable=missing-docstring,no-self-use
    state = FLAGS.pyatdl_internal_state
    self.RaiseUnlessNArgumentsGiven(1, args)
    self._PerformCd(state, args[-1], FLAGS.recursive)

  def _PerformCdDashR(self, state, name):  # pylint: disable=no-self-use
    """Performs 'cd -R'.

    Args:
      state: State
      name: basestring
    """
    try:
      the_uid = lexer.ParseSyntaxForUID(name)
    except lexer.Error as e:
      raise BadArgsError(e)
    for (c, unused_path) in state.ToDoList().root.ContainersPreorder():
      if the_uid == c.uid or c.name == name:
        state.SetCurrentWorkingContainer(c)
        break
    else:
      if not FLAGS.swallow_errors:
        names = [i.name for (i, _) in state.ToDoList().root.ContainersPreorder()
                 if i.name]
        if names:
          choices = '  Choices:\n%s' % common.Indented('\n'.join(names))
        else:
          choices = ''
        raise BadArgsError(
          'With current working Folder/Project "%s", there is no such child "%s".%s'
          % (state.CurrentWorkingContainerString(), name, choices))

  def _PerformCd(self, state, name, recurse=False):  # pylint: disable=too-many-branches
    """Performs UICmd 'cd'."""
    if recurse:
      self._PerformCdDashR(state, name)
    else:
      try:
        dirname = state.DirName(name)
        if dirname:
          state.SetCurrentWorkingContainer(state.GetContainerFromPath(dirname))
        basename = state.BaseName(name)
        if basename:
          state.SetCurrentWorkingContainer(state.GetContainerFromPath(basename))
      except state_module.InvalidPathError as e:
        if not FLAGS.swallow_errors:
          raise BadArgsError(e)


class UICmdCompletereview(UndoableUICmd):
  """Marks the sole named project as having completed its review."""
  def Run(self, args):  # pylint: disable=missing-docstring,no-self-use
    state = FLAGS.pyatdl_internal_state
    self.RaiseUnlessNArgumentsGiven(1, args)
    try:
      the_project, unused_parent_container = _LookupProject(state, args[-1])
    except NoSuchContainerError as e:
      raise BadArgsError(e)
    the_project.MarkAsReviewed()


class UICmdClearreview(UndoableUICmd):
  """Without arguments, marks all projects as needing review.

  With a sole argument, marks the named project as requiring review.
  """
  def Run(self, args):  # pylint: disable=missing-docstring,no-self-use
    state = FLAGS.pyatdl_internal_state
    if len(args) != 1:
      self.RaiseUnlessNArgumentsGiven(1, args)
      try:
        the_project, unused_parent_container = _LookupProject(state, args[-1])
      except NoSuchContainerError as e:
        raise BadArgsError(e)
      the_project.MarkAsNeedingReview()
    else:
      for project, unused_path in state.ToDoList().Projects():
        project.MarkAsNeedingReview()


def _PerformMkprjOrMkdir(prj_or_folder, state, name, allow_slashes, verbose):
  """Performs 'mkprj'/'mkdir'."""
  if allow_slashes:
    dirname = ''
    basename = name
  else:
    try:
      dirname = state.DirName(name)
      basename = state.BaseName(name)
      if not basename:
        raise BadArgsError('Unexpected trailing "%s"' % FLAGS.pyatdl_separator)
    except state_module.InvalidPathError as e:
      raise BadArgsError(e)
  try:
    containr = state.GetContainerFromPath(dirname)
    if containr is state.ToDoList().inbox:
      raise BadArgsError(
        'Cannot make a project or folder beneath %s%s' % (
          FLAGS.pyatdl_separator, FLAGS.inbox_project_name))
    if containr.is_deleted:
      raise BadArgsError('Cannot create within a deleted Folder')
    new_item = prj_or_folder(name=basename)
    state.ToDoList().AddProjectOrFolder(
      new_item,
      containr.uid)
    if verbose:
      state.Print(new_item.uid)
  except tdl.NoSuchParentFolderError:
    raise BadArgsError('The parent directory must be a Folder, not a Project.')
  except state_module.InvalidPathError as e:
    raise BadArgsError(e)
  except auditable_object.IllegalNameError as e:
    raise BadArgsError(e)


class UICmdMkdir(UndoableUICmd):
  """Makes a Folder with the given name."""
  def Run(self, args):  # pylint: disable=missing-docstring,no-self-use
    state = FLAGS.pyatdl_internal_state
    self.RaiseUnlessNArgumentsGiven(1, args)
    _PerformMkprjOrMkdir(folder.Folder, state, args[-1], False, False)


class UICmdMkprj(UndoableUICmd):
  """Makes a Project with the given name."""
  def __init__(self, name, flag_values, **kargs):
    super().__init__(name, flag_values, **kargs)
    flags.DEFINE_boolean('allow_slashes', False,
                         'Do not treat directory separators as directory separators',
                         flag_values=flag_values)
    flags.DEFINE_bool('verbose', False, 'Output UID created', flag_values=flag_values)

  def Run(self, args):  # pylint: disable=missing-docstring,no-self-use
    state = FLAGS.pyatdl_internal_state
    self.RaiseUnlessNArgumentsGiven(1, args)
    _PerformMkprjOrMkdir(prj.Prj, state, args[-1], FLAGS.allow_slashes, FLAGS.verbose)


class UICmdMkctx(UndoableUICmd):
  """Makes a Context with the given name."""
  def __init__(self, name, flag_values, **kargs):
    super().__init__(name, flag_values, **kargs)
    flags.DEFINE_bool('ignore_existing', False,
                      'Ignore trying to create an existing Context',
                      flag_values=flag_values)
    flags.DEFINE_bool('verbose', False, 'Output UID created', flag_values=flag_values)

  def Run(self, args):  # pylint: disable=missing-docstring,no-self-use
    self.RaiseUnlessNArgumentsGiven(1, args)
    state = FLAGS.pyatdl_internal_state
    try:
      new_uid = state.ToDoList().AddContext(args[-1])
      if FLAGS.verbose:
        state.Print(new_uid)
    except tdl.DuplicateContextError as e:
      if not FLAGS.ignore_existing:
        raise BadArgsError(e)
    except auditable_object.IllegalNameError as e:
      raise BadArgsError(e)


class UICmdNeedsreview(UICmd):
  """Prints all Projects in need of review. Takes no arguments."""
  def __init__(self, name, flag_values, **kargs):
    super().__init__(name, flag_values, **kargs)
    flags.DEFINE_bool('json', False, 'Output JSON', flag_values=flag_values)

  def Run(self, args):  # pylint: disable=missing-docstring,no-self-use
    state = FLAGS.pyatdl_internal_state
    self.RaiseIfAnyArgumentsGiven(args)
    vfilter = state.NewViewFilter(view_filter.ShowNeedingReview)
    to_be_json = []
    for project, path in state.ToDoList().ProjectsToReview():
      if vfilter.ShowProject(project):
        if FLAGS.json:
          to_be_json.append(_JsonForOneItem(
            project, state.ToDoList(), len(project.items)))
        else:
          state.Print(_ProjectString(project, path))
    if FLAGS.json:
      state.Print(json.dumps(to_be_json, sort_keys=True, separators=(',', ':')))


class UICmdNote(UICmd):
  """Creates or edits or prints a note on a Folder/Prj/Ctx/Action.

  With a single positional argument, prints the note for the given object, or, if --inboxize is true, replaces the note
  for the given object with a small note indicating that each line of the note has been transformed into a new Action
  in the Inbox.

  With two positional arguments, the second argument is a note to either
  replace the note or extend the existing note based on --replace.

  """
  def __init__(self, name, flag_values, **kargs):
    super().__init__(name, flag_values, **kargs)
    flags.DEFINE_bool('replace',
                      False,
                      'Replace instead of append',
                      short_name='r',
                      flag_values=flag_values)
    flags.DEFINE_bool('inboxize',
                      False,
                      'Turn each line of the note into its own Action in the Inbox and clear the note.',
                      short_name='z',
                      flag_values=flag_values)

  def Run(self, args):  # pylint: disable=missing-docstring,no-self-use
    state = FLAGS.pyatdl_internal_state
    if len(args) == 2:
      if re.match(r'^:[a-zA-Z0-9_-]+$', args[-1]) is not None:
        notes = state.ToDoList().note_list.notes
        x = notes.get(args[-1], '')
        if x:
          if FLAGS.inboxize:
            notes[args[-1]] = _Inboxize(state, x)
          else:
            state.Print(x)
        return
      try:
        auditable_object = state.GetObjectFromPath(args[-1], include_contexts=True)
      except state_module.Error as e:
        raise BadArgsError(six.text_type(e))
      if auditable_object.note:
        if FLAGS.inboxize:
          auditable_object.note = _Inboxize(state, auditable_object.note)
        else:
          state.Print(auditable_object.note)
      return
    if FLAGS.inboxize:
      raise BadArgsError('--inboxize only works with the single-positional-argument form.')
    self.RaiseUnlessNArgumentsGiven(2, args)
    if re.match(r'^:[a-zA-Z0-9_-]+$', args[-2]) is not None:
      notes = state.ToDoList().note_list.notes
      if FLAGS.replace:
        notes[args[-2]] = args[-1]
      else:
        notes[args[-2]] = notes.get(args[-2], '') + args[-1]
      return
    try:
      auditable_object = state.GetObjectFromPath(args[-2], include_contexts=True)
    except state_module.Error as e:
      raise BadArgsError(six.text_type(e))
    if FLAGS.replace:
      auditable_object.note = args[-1]
    else:
      auditable_object.note += args[-1]


class UICmdCat(UICmd):
  """Displays a note on a Folder/Prj/Ctx/Action, the sole positional argument."""
  def Run(self, args):  # pylint: disable=missing-docstring,no-self-use
    state = FLAGS.pyatdl_internal_state
    self.RaiseUnlessNArgumentsGiven(1, args)
    if re.match(r'^:[a-zA-Z0-9_-]+$', args[-1]) is not None:
      x = state.ToDoList().note_list.notes.get(args[-1], '')
      if x:
        state.Print(x)
      return
    try:
      auditable_object = state.GetObjectFromPath(args[-1],
                                                 include_contexts=True)
    except state_module.Error as e:
      raise BadArgsError(six.text_type(e))
    if auditable_object.note:
      state.Print(auditable_object.note)


class UICmdAlmostPurgeAllActionsInContext(UICmd):
  """For each Action associated with the given Context, truly delete (i.e., purge) the Action.

  Afterwards the Context will still exist but will be empty.
  """
  def Run(self, args):  # pylint: disable=missing-docstring,no-self-use
    state = FLAGS.pyatdl_internal_state
    self.RaiseUnlessNArgumentsGiven(1, args)
    ctx_name = args[-1]
    ctx_uid = None
    # UIDs start at 1, but we say UID 0 refers to the Context that contains
    # Actions without any Context.
    errmsg = "Purging actions without context is weird and, well, how dare you."
    if ctx_name == FLAGS.no_context_display_string or ctx_name == 'uid=0':
      raise BadArgsError(errmsg)
    try:
      ctx_uid = lexer.ParseSyntaxForUID(ctx_name)
    except lexer.Error as e:
      raise BadArgsError(e)
    if ctx_uid is None:
      try:
        ctx_uid = state.ToDoList().ctx_list.ContextUIDFromName(ctx_name)
      except ctx.NoSuchNameError as e:
        raise BadArgsError(e)
    if ctx_uid is None:
      raise BadArgsError(errmsg)
    for a, p in state.ToDoList().ActionsInContext(ctx_uid):
      a.AlmostPurge()


def _PerformActivatectx(state, ctx_name, is_active):
  """Performs 'activatectx'/'deactivatectx'."""
  context = _LookupContext(state, ctx_name)
  if context is None:
    raise BadArgsError('No such context "%s"' % ctx_name)
  context.is_active = is_active


class UICmdActivatectx(UndoableUICmd):
  """Makes the sole named Context active, which affects view filters."""
  def Run(self, args):  # pylint: disable=missing-docstring,no-self-use
    state = FLAGS.pyatdl_internal_state
    self.RaiseUnlessNArgumentsGiven(1, args)
    _PerformActivatectx(state, args[-1], is_active=True)


class UICmdDeactivatectx(UndoableUICmd):
  """Makes the sole named Context inactive, which affects view filters."""
  def Run(self, args):  # pylint: disable=missing-docstring,no-self-use
    state = FLAGS.pyatdl_internal_state
    self.RaiseUnlessNArgumentsGiven(1, args)
    _PerformActivatectx(state, args[-1], is_active=False)


def _PerformActivateprj(state, prj_name, is_active):
  """Performs 'activateprj'/'deactivateprj'."""
  try:
    the_project, unused_parent_container = _LookupProject(state, prj_name)
  except NoSuchContainerError as e:
    raise BadArgsError(e)
  the_project.is_active = is_active


class UICmdActivateprj(UndoableUICmd):
  """Makes the sole named Project active, which affects view filters.

  An inactive project does not appear (e.g., with "ls") under the "actionable"
  view filter. You'd need to use "all_even_deleted" or "all" or "inactive". An
  inactive project is, in layman's terms, "on hold".
  """
  def Run(self, args):  # pylint: disable=missing-docstring,no-self-use
    state = FLAGS.pyatdl_internal_state
    self.RaiseUnlessNArgumentsGiven(1, args)
    _PerformActivateprj(state, args[-1], is_active=True)


class UICmdDeactivateprj(UndoableUICmd):
  """Makes the sole named Project inactive, which affects view filters and
  'needsreview'. See also the opposite command 'activateprj'.
  """
  def Run(self, args):  # pylint: disable=missing-docstring,no-self-use
    state = FLAGS.pyatdl_internal_state
    self.RaiseUnlessNArgumentsGiven(1, args)
    _PerformActivateprj(state, args[-1], is_active=False)


def _ContextFromActionName(state, action_name):
  def ModifiedString(s):
    return s.replace(' ', '').replace('_', '').replace('-', '').lower()

  contexts = state.ToDoList().ctx_list.items
  contexts_longest_name_first = sorted(
      contexts,
      key=lambda c: (len(c.name), c.name),
      reverse=True)
  for candidate_context in contexts_longest_name_first:
    if not candidate_context.is_deleted:
      if ModifiedString(candidate_context.name) in ModifiedString(action_name):
        return candidate_context
  return None


class UICmdUnicorn(UndoableUICmd):
  """Takes no arguments."""
  def Run(self, args):  # pylint: disable=missing-docstring,no-self-use
    self.RaiseIfAnyArgumentsGiven(args)
    state = FLAGS.pyatdl_internal_state
    data = """
CiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIC8KICAg
ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAuNwogICAgICAg
ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICBcICAgICAgICwgLy8KICAgICAgICAgICAg
ICAgICAgICAgICAgICAgICAgICAgICAgICAgfFwuLS0uXy98Ly8KICAgICAgICAgICAgICAgICAg
ICAgICAgICAgICAgICAgICAgICAvXCApICkgKS4nLwogICAgICAgICAgICAgICAgICAgICAgICAg
ICAgICAgICAgICAgLyggIFwgIC8vIC8KICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAg
ICAgLyggICBKYCgoXy8gXAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIC8gKSB8
IF9cICAgICAvCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAvfCkgIFwgIGVKICAg
IEwKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgfCAgXCBMIFwgICBMICAgTAogICAg
ICAgICAgICAgICAgICAgICAgICAgICAgICAgIC8gIFwgIEogIGAuIEogICBMCiAgICAgICAgICAg
ICAgICAgICAgICAgICAgICAgICAgfCAgKSAgIEwgICBcLyAgIFwKICAgICAgICAgICAgICAgICAg
ICAgICAgICAgICAgIC8gIFwgICAgSiAgIChcICAgLwogICAgICAgICAgICAgXy4uLi5fX18gICAg
ICAgICB8ICBcICAgICAgXCAgIFxgYGAKICAgICAgLC4uXy4tJyAgICAgICAgJycnLS0uLi4tfHxc
ICAgICAtLiBcICAgXAogICAgLicuPS4nICAgICAgICAgICAgICAgICAgICBgICAgICAgICAgYC5c
IFsgWQogICAvICAgLyAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICBcXSAgSgogIFkg
LyBZICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgWSAgIEwKICB8IHwgfCAgICAg
ICAgICBcICAgICAgICAgICAgICAgICAgICAgICAgIHwgICBMCiAgfCB8IHwgICAgICAgICAgIFkg
ICAgICAgICAgICAgICAgICAgICAgICBBICBKCiAgfCAgIEkgICAgICAgICAgIHwgICAgICAgICAg
ICAgICAgICAgICAgIC9JXCAvCiAgfCAgICBcICAgICAgICAgIEkgICAgICAgICAgICAgXCAgICAg
ICAgKCB8XS98CiAgSiAgICAgXCAgICAgICAgIC8uXyAgICAgICAgICAgLyAgICAgICAgLXRJLyB8
CiAgIEwgICAgICkgICAgICAgLyAgIC8nLS0tLS0tLSdKICAgICAgICAgICBgJy06LgogICBKICAg
LicgICAgICAsJyAgLCcgLCAgICAgXCAgIGAnLS5fXyAgICAgICAgICBcCiAgICBcIFQgICAgICAs
JyAgLCcgICApXCAgICAvfCAgICAgICAgJzsnLS0tNyAgIC8KICAgICBcfCAgICAsJ0wgIFkuLi4t
JyAvIF8uJyAvICAgICAgICAgXCAgIC8gICAvCiAgICAgIEogICBZICB8ICBKICAgIC4nLScgICAv
ICAgICAgICAgLC0tLiggICAvCiAgICAgICBMICB8ICBKICAgTCAtJyAgICAgLicgICAgICAgICAv
ICB8ICAgIC9cCiAgICAgICB8ICBKLiAgTCAgSiAgICAgLi07Li0vICAgICAgIHwgICAgXCAuJyAv
CiAgICAgICBKICAgTGAtSiAgIExfX19fLC4tJ2AgICAgICAgIHwgIF8uLScgICB8CiAgICAgICAg
TCAgSiAgIEwgIEogICAgICAgICAgICAgICAgICBgYCAgSiAgICB8ZgogICAgICAgIEogICBMICB8
ICAgTCAgICAgICAgICAgICAgICAgICAgIEogICAgfAogICAgICAgICBMICBKICBMICAgIFwgICAg
ICAgICAgICAgICAgICAgIEwgICAgXAogICAgICAgICB8ICAgTCAgKSBfLidcICAgICAgICAgICAg
ICAgICAgICApIF8uJ1wKICAgICAgICAgTCAgICBcKCdgICAgIFwgICAgICAgICAgICAgICAgICAo
J2AgICAgXAogICAgICAgICAgKSBfLidcYC0uLi4uJyAgICAgICAgICAgICAgICAgICBgLS4uLi4n
CiAgICAgICAgICgnYCAgICBcCiAgICAgICAgICBgLS5fX18vCg=="""

    for line in base64.decodestring(bytes(data.strip(), 'utf-8')).splitlines():
      state.Print(str(line, 'utf-8'))


def _ContainerFromActionName(state, basename):
  """Handles +ProjectName and r'^Project Name:.*'"""
  basename_lower = basename.lower()
  split_basename_lower = basename_lower.split(' ')
  split_basename = basename.split(' ')
  for project, _ in state.ToDoList().Projects():
    if project.is_deleted or not project.name:
      continue
    if basename_lower.startswith(project.name.lower() + ':'):
      return project, basename[len(project.name) + 1:].strip()
    plus_form = '+' + ''.join(project.name.strip().split(' '))
    for i, split in enumerate(split_basename_lower):
      if split == plus_form:
        del split_basename[i]
        return project, ' '.join(split_basename)
  return None, basename


class UICmdTouch(UndoableUICmd):  # 'mkact', 'touch'
  """Creates an Action.  Only works inside of a Project.

  Takes one argument, the name of the Action.
  """
  def __init__(self, name, flag_values, **kargs):
    super().__init__(name, flag_values, **kargs)
    flags.DEFINE_string('context', '', 'Optional Context',
                        short_name='c',
                        flag_values=flag_values)
    flags.DEFINE_boolean('allow_slashes', False,
                         'Do not treat directory separators as directory separators',
                         flag_values=flag_values)
    flags.DEFINE_boolean('autoprj', False,
                         'Automatically assign a project based on conventions',
                         flag_values=flag_values)
    flags.DEFINE_bool('verbose', False, 'Output UID created', flag_values=flag_values)

  def Run(self, args):  # pylint: disable=missing-docstring,no-self-use
    state = FLAGS.pyatdl_internal_state
    self.RaiseUnlessNArgumentsGiven(1, args)
    name = args[-1]
    containr = state.CurrentWorkingContainer()
    if FLAGS.allow_slashes:
      basename = name
    else:
      try:
        dirname = state.DirName(name)
        if dirname:
          containr = state.GetContainerFromPath(dirname)
        basename = state.BaseName(name)
        if not basename:
          raise BadArgsError('Unexpected trailing "%s"' % FLAGS.pyatdl_separator)
      except state_module.InvalidPathError as e:
        raise BadArgsError(e)
    if not isinstance(containr, prj.Prj):
      raise BadArgsError(
        'The "%s" command only works within a Project, not a Folder.'
        '  The folder is "%s".'
        % (args[0],
           containr.name if containr.name else FLAGS.pyatdl_separator))
    context = None
    if FLAGS.context and FLAGS.context != 'uid=0':
      context = _LookupContext(state, FLAGS.context)
      if context is None:
        raise BadArgsError('No such Context "%s"' % FLAGS.context)
    if context is None and FLAGS.context != 'uid=0':
      context = _ContextFromActionName(state, basename)
    if FLAGS.autoprj:
      c, basename = _ContainerFromActionName(state, basename)
      if c is not None and not c.is_deleted:
        containr = c
    if containr.is_deleted:
      raise BadArgsError('Cannot add an Action to a deleted Project')
    try:
      a = action.Action(name=basename)
    except auditable_object.IllegalNameError as e:
      raise BadArgsError(e)
    if context is not None:
      a.ctx_uid = context.uid
    if context is None and containr.default_context_uid is not None:
      # default_context_uid may no longer exist:
      default_context = state.ToDoList().ContextByUID(containr.default_context_uid)
      if default_context is not None:
        a.ctx_uid = default_context.uid
    containr.items.append(a)
    containr.NoteModification()
    if containr.is_complete:
      containr.is_complete = False
    if FLAGS.verbose:
      state.Print(a.uid)


def _Reparent(moving_item, new_container, todolist):
  """Moves moving_item from its parent Container to new_container.

  Args:
    moving_item: Action|Prj|Folder
    new_container: Container
    todolist: ToDoList
  Returns:
    None
  Raises:
    BadArgsError
  """
  if moving_item is todolist.inbox:
    if new_container is todolist.root or new_container is todolist.inbox:
      return  # NOP
    else:
      raise BadArgsError('Cannot move %s%s' % (
        FLAGS.pyatdl_separator, FLAGS.inbox_project_name))
  try:
    old_parent = todolist.ParentContainerOf(moving_item)
  except tdl.NoSuchParentFolderError:
    raise BadArgsError('Cannot move the root Folder \'%s\''
                       % FLAGS.pyatdl_separator)
  if moving_item.uid == new_container.uid:
    raise BadArgsError('Cannot move an item into itself.')
  if not moving_item.is_deleted and new_container.is_deleted:
    raise BadArgsError('Cannot move an undeleted item into a deleted container.')
  if old_parent.uid != new_container.uid:  # Don't change the order of items
    for i, item in enumerate(old_parent.items):
      if item.uid == moving_item.uid:
        del old_parent.items[i]
        old_parent.NoteModification()
        break
    else:
      raise AssertionError('Cannot find the first arg within its old '
                           'parent Container. arg=%s' % moving_item)
    if not moving_item.is_deleted and hasattr(moving_item, 'is_complete') and not moving_item.is_complete:
      new_container.is_complete = False
    new_container.items.append(moving_item)
    new_container.NoteModification()


class UICmdMv(UndoableUICmd):
  """Moves an Action to a different Project (relative to the current working
  Folder/Project, or absolute), or a Project to a different Folder, or a Folder
  to a different Folder. See also 'rename'.

  Usage: mv action project
         mv project folder
         mv folder folder
  """
  def Run(self, args):  # pylint: disable=missing-docstring,no-self-use
    self.RaiseUnlessNArgumentsGiven(2, args)
    state = FLAGS.pyatdl_internal_state
    old, new = args[-2], args[-1]
    try:
      old_item = state.GetObjectFromPath(old)
      new_item = state.GetObjectFromPath(new)
    except state_module.Error as e:
      raise BadArgsError(e)
    if isinstance(old_item, action.Action):
      if not isinstance(new_item, prj.Prj):
        raise BadArgsError('First argument is an Action, but second argument is'
                           ' not a Project')
    elif isinstance(old_item, (prj.Prj, folder.Folder)):
      if not isinstance(new_item, folder.Folder):
        raise BadArgsError(
            'First argument is a %s, but second argument is'
            ' not a Folder' % (
                'Folder' if isinstance(old_item, folder.Folder) else 'Project',))
    else:
      raise BadArgsError('First argument must be an Action, Project, or Folder')
    _Reparent(old_item, new_item, state.ToDoList())
    state.ToDoList().CheckIsWellFormed()


class UICmdRename(UndoableUICmd):
  """Renames a Project/Folder/Action in the current working Folder/Project.

  Usage: rename "old name" "new name"
  """
  def __init__(self, name, flag_values, **kargs):
    super().__init__(name, flag_values, **kargs)
    flags.DEFINE_boolean('allow_slashes', False,
                         'Do not treat directory separators as directory separators',
                         flag_values=flag_values)
    flags.DEFINE_boolean('autoctx', False,
                         'Change context if a context\'s name is found',
                         flag_values=flag_values,
                         short_name='a')

  def Run(self, args):  # pylint: disable=missing-docstring,no-self-use
    def Rename(state, container_of_item, item, new):
      if not FLAGS.allow_slashes:
        if container_of_item is None:
          container_of_item = _FindParentOf(state, item)
        new_dirname = state.DirName(new)
        if new_dirname:
          new_basename = state.BaseName(new)
          new_container = state.GetContainerFromPath(new_dirname)
          if container_of_item is not new_container:
            raise BadArgsError(
                'Cannot use "rename" to move an item; see "mv"')
          new = new_basename
      try:
        item.name = new
      except auditable_object.IllegalNameError as e:
        raise BadArgsError('Bad syntax for right-hand side: %s' % str(e))
      try:
        state.ToDoList().CheckIsWellFormed()
      except AssertionError:
        item.name = old
        raise BadArgsError('The new name, "%s", is not well-formed.' % new)
      if isinstance(item, action.Action) and FLAGS.autoctx:
        context = _ContextFromActionName(state, new)
        if context is not None:
          item.ctx_uid = context.uid

    def ContainerOfOld(state, old):
      dirname = state.DirName(old)
      if not dirname:
        return state.CurrentWorkingContainer()
      return state.GetContainerFromPath(dirname)

    self.RaiseUnlessNArgumentsGiven(2, args)
    state = FLAGS.pyatdl_internal_state
    old, new = args[-2], args[-1]
    try:
      old_uid = lexer.ParseSyntaxForUID(old)
    except lexer.Error as e:
      raise BadArgsError(e)
    container_of_old = None
    if old_uid is not None:
      items = state.ToDoList().Items()
    else:
      if FLAGS.allow_slashes:
        container_of_old = state.CurrentWorkingContainer()
      else:
        container_of_old = ContainerOfOld(state, old)
      items = container_of_old.items
    old = old if FLAGS.allow_slashes else state.BaseName(old)
    # Give undeleted items precedence.
    for item in items:
      if old_uid == item.uid or (item.name == old and not item.is_deleted):
        Rename(state, container_of_old, item, new)
        break
    else:
      for item in items:
        if old_uid is None and item.name == old:
          Rename(state, container_of_old, item, new)
          break
      else:
        names = [i.name for i in state.CurrentWorkingContainer().items]
        if names:
          choices = '  Choices: %s' % ' '.join(names)
        else:
          choices = ''
        raise BadArgsError(
          'No item named "%s" exists in the current working Folder/Project '
          '(see "help pwd").%s'
          % (old, choices))


class UICmdRenamectx(UndoableUICmd):
  """Renames a Context.

  Usage: renamectx "old name" "new name"
  """
  def Run(self, args):  # pylint: disable=missing-docstring,no-self-use
    self.RaiseUnlessNArgumentsGiven(2, args)
    state = FLAGS.pyatdl_internal_state
    old, new = args[-2], args[-1]
    c = _LookupContext(state, old)
    if c is None:
      raise BadArgsError(
        'No Context named "%s" found. Choices: %s'
        % (old, ' '.join(i.name for i in state.ToDoList().ctx_list.items)))
    c.name = new
    try:
      state.ToDoList().CheckIsWellFormed()
    except AssertionError:
      c.name = old
      raise BadArgsError(
        'The new name, "%s", is not well-formed.  See "help lsctx".'
        % new)


class UICmdReset(UICmd):
  """Discards the current to-do list and associated state, i.e. current
  working directory. Starts over. Obliterates all your precious data! Cannot
  be undone (all information about undo/redo is obliterated).

  Usage: Takes no arguments.
  """
  def __init__(self, name, flag_values, **kargs):
    super().__init__(name, flag_values, **kargs)
    flags.DEFINE_bool('annihilate', False,
                      'Yes, really destroy all my hard work.',
                      flag_values=flag_values)

  def Run(self, args):  # pylint: disable=missing-docstring,no-self-use
    state = FLAGS.pyatdl_internal_state
    self.RaiseIfAnyArgumentsGiven(args)
    if not FLAGS.annihilate:
      raise BadArgsError(
          'You did not pass in the flag --annihilate to confirm that you really'
          ' want to lose all your data.')
    uid.ResetNotesOfExistingUIDs()
    state.SetToDoList(NewToDoList())
    state.ResetUndoStack()
    state.Print('Reset complete.')


class UICmdLoad(UICmd):
  """Discards the current to-do list -- obliterates all your precious data!

  Cannot be undone (all information about undo/redo is obliterated).

  The next autosave will save the newly loaded data to the file specified
  by --database_filename.

  Usage: A single argument, a path to a file
  """
  def Run(self, args):  # pylint: disable=missing-docstring,no-self-use
    state = FLAGS.pyatdl_internal_state
    self.RaiseUnlessNArgumentsGiven(1, args)
    filename = args[-1]
    uid.ResetNotesOfExistingUIDs()
    try:
      todolist = serialization.DeserializeToDoList(filename, NewToDoList)
    except serialization.DeserializationError as e:
      raise app.UsageError(str(e))
    state.SetToDoList(todolist)
    state.ResetUndoStack()
    state.Print('Load complete.')


class UICmdSave(UICmd):
  """Saves a copy of the current to-do list to a file.

  This is a one-time thing; the next autosave will still be to the file
  specified by --database_filename.

  Usage: A single argument, a path to a file
  """
  def Run(self, args):  # pylint: disable=missing-docstring,no-self-use
    state = FLAGS.pyatdl_internal_state
    self.RaiseUnlessNArgumentsGiven(1, args)
    filename = args[-1]
    serialization.SerializeToDoList(state.ToDoList(), filename)
    state.Print('Save complete.')


def _RunCmd(cmd, args):
  """Only works because FLAGS.pyatdl_internal_state is already defined. See
  also APP_NAMESPACE.FindCmdAndExecute.
  """
  cmd(None, flags.FlagValues()).CommandRun([None] + args)


class UICmdSeed(UICmd):
  """Creates some contexts, actions, and projects to use as a starting point."""
  def Run(self, args):  # pylint: disable=missing-docstring,no-self-use
    self.RaiseIfAnyArgumentsGiven(args)
    _RunCmd(UICmdMkctx, ['@computer'])
    _RunCmd(UICmdMkctx, ['@phone'])
    _RunCmd(UICmdMkctx, ['@home'])
    _RunCmd(UICmdMkctx, ['@work'])
    _RunCmd(UICmdMkctx, ['@the store'])
    _RunCmd(UICmdMkctx, ['@someday/maybe'])
    _RunCmd(UICmdMkctx, ['@waiting for'])
    _RunCmd(UICmdDeactivatectx, ['@someday/maybe'])
    _RunCmd(UICmdDeactivatectx, ['@waiting for'])
    _RunCmd(UICmdMkprj, [FLAGS.pyatdl_separator + 'miscellaneous'])
    _RunCmd(UICmdMkprj, [FLAGS.pyatdl_separator + 'learn how to use this to-do list'])
    _RunCmd(UICmdTouch, [FLAGS.pyatdl_separator + 'learn how to use this to-do list'
                         + FLAGS.pyatdl_separator
                         + 'Watch the video on the "Help" page -- find it on the top '
                         + 'navigation bar'])
    _RunCmd(UICmdTouch, [FLAGS.pyatdl_separator + 'learn how to use this to-do list'
                         + FLAGS.pyatdl_separator
                         + 'Read the book "Getting Things Done" by David Allen'])
    _RunCmd(UICmdTouch, [FLAGS.pyatdl_separator + 'learn how to use this to-do list'
                         + FLAGS.pyatdl_separator
                         + 'After reading the book, try out a Weekly Review -- on'
                         + ' the top navigation bar, find it underneath the'
                         + ' "Other" drop-down'])


class UICmdRmctx(UndoableUICmd):
  """Deletes the given Context after doctoring all associated Actions.
  See also "view all_even_deleted".
  """
  def Run(self, args):  # pylint: disable=missing-docstring,no-self-use
    self.RaiseUnlessNArgumentsGiven(1, args)
    state = FLAGS.pyatdl_internal_state
    name = args[-1]
    context = _LookupContext(state, name)
    if context is None:
      raise BadArgsError(
        'No such context "%s".  Your choices: %s'
        % (name, ' '.join(sorted(c.name for c in state.ToDoList().ctx_list.items))))
    state.ToDoList().RemoveReferencesToContext(context.uid)
    if not context.is_deleted:
      context.is_deleted = True
      context.name += '-deleted-at-%s' % time.time()


class UICmdRmdir(UndoableUICmd):
  """Deletes the given Folder.  See also "view all_even_deleted"."""
  def Run(self, args):  # pylint: disable=missing-docstring,no-self-use
    state = FLAGS.pyatdl_internal_state
    self.RaiseUnlessNArgumentsGiven(1, args)
    try:
      the_folder = _LookupFolder(state, args[-1])
    except NoSuchContainerError as e:
      raise BadArgsError(e)
    try:
      state.ToDoList().ParentContainerOf(the_folder).DeleteChild(the_folder)
    except container.IllegalOperationError as e:
      raise BadArgsError(str(e))


class UICmdRmprj(UndoableUICmd):
  """Deletes the given Project.  See also "view all_even_deleted"."""
  def __init__(self, name, flag_values, **kargs):
    super().__init__(name, flag_values, **kargs)
    flags.DEFINE_bool('force',
                      False,
                      'First deletes all descendant actions',
                      short_name='f',
                      flag_values=flag_values)

  def Run(self, args):  # pylint: disable=missing-docstring,no-self-use
    state = FLAGS.pyatdl_internal_state
    self.RaiseUnlessNArgumentsGiven(1, args)
    name = args[-1]
    try:
      the_project, parent_container = _LookupProject(state, name)
    except NoSuchContainerError as e:
      raise BadArgsError(e)
    if parent_container is None:
      assert the_project.uid == 1, name
      raise BadArgsError('The project %s%s is special; it cannot be removed.'
                         % (FLAGS.pyatdl_separator, FLAGS.inbox_project_name))
    if FLAGS.force:
      for d in container.YieldDescendantsThatAreNotDeleted(the_project):
        # TODO(chandler): Update dtime?
        d.is_deleted = True
    try:
      parent_container.DeleteChild(the_project)
    except container.IllegalOperationError as e:
      raise BadArgsError(str(e))


class UICmdRmact(UndoableUICmd):  # 'rm', 'rmact'
  """Deletes the given Action.  See also "complete" and
  "view all_even_deleted".
  """
  def Run(self, args):  # pylint: disable=missing-docstring,no-self-use
    state = FLAGS.pyatdl_internal_state
    self.RaiseUnlessNArgumentsGiven(1, args)
    name = args[-1]
    try:
      the_action, the_project = _LookupAction(state, name)
    except NoSuchContainerError:
      raise BadArgsError('Action "%s" not found.' % name)
    try:
      the_project.DeleteChild(the_action)
    except container.IllegalOperationError as e:
      raise AssertionError(
        'Impossible because an Action has no descendants: %s' % str(e))


class UICmdRoll(UICmd):
  """Rolls dice.

  This is a crucial antiprocrastination measure when, e.g., you cannot pick
  between actionable actions inside a context.
  """
  def __init__(self, name, flag_values, **kargs):
    super().__init__(name, flag_values, **kargs)
    # TODO(chandler):
    # flags.DEFINE_bool('advantaged', False,
    #                   'Roll with advantage.',
    #                   short_name='a',
    #                   flag_values=flag_values)
    # flags.DEFINE_bool('disadvantaged', False,
    #                   'Roll with disadvantage.',
    #                   short_name='d',
    #                   flag_values=flag_values)
    flags.DEFINE_integer('seed', None,
                         'Random seed',
                         flag_values=flag_values)

  def Run(self, args):  # pylint: disable=missing-docstring
    state = FLAGS.pyatdl_internal_state
    self.RaiseUnlessNArgumentsGiven(1, args)
    m = re.compile(r'^(?P<num>\d+)[dD](?P<sides>\d+)$').match(args[-1])
    if not m:
      raise BadArgsError('Needs argument like "1d6" or "21d20"')
    num, sides = int(m.group('num')), int(m.group('sides'))
    if FLAGS.seed is not None:
      random.seed(FLAGS.seed)
    for k in xrange(num):
      state.Print(six.text_type(random.randrange(1, sides + 1)))


class UICmdExit(UICmd):
  """Saves and exits.  Control-D does the same."""
  def Run(self, args):  # pylint: disable=missing-docstring,no-self-use
    self.RaiseIfAnyArgumentsGiven(args)
    raise EOFError('exiting')


class UICmdHelp(UICmd):
  """Gives interactive help."""
  def Run(self, args):  # pylint: disable=missing-docstring,no-self-use
    def Pretty(p):  # pylint:disable=missing-docstring
      return '\n'.join(x.strip() for x in p.strip().splitlines())

    state = FLAGS.pyatdl_internal_state
    if len(args) != 1:
      self.RaiseUnlessNArgumentsGiven(1, args)
      cmd_name = args[-1]
      try:
        the_help_str = APP_NAMESPACE.HelpForCmd(cmd_name)
      except appcommandsutil.CmdNotFoundError:
        the_help_str = ('No such command "%s"; try "help" for a list of '
                        'all commands.' % cmd_name)
      if not the_help_str:
        state.Print(Pretty(r"""I have a brilliant help string written for this command,
            but it is too large to fit in the margins of this book,
            which are cluttered with proofs of Fermat's last theorem :-("""))
      else:
        state.Print(Pretty(the_help_str))
    else:
      state.Print('Welcome!')
      state.Print('')
      if 'exit' in APP_NAMESPACE.CmdList():
        state.Print('To exit and save, use the "exit" command (alternatively,')
        state.Print('press Control-D to trigger end-of-file (EOF)).')
        state.Print('')
      state.Print('Some core concepts follow:')
      state.Print('* A Folder contains Folders and Projects.')
      state.Print('  It is like a directory in a file system.')
      state.Print('* A Project contains Actions.')
      state.Print('* An Action may have a Context.')
      state.Print('* A Context is designed to show you ONLY Actions you can perform right now.')
      state.Print('  An inactive Context (e.g., WaitingFor or SomedayMaybe) houses')
      state.Print('  Actions that need to be reviewed but cannot be acted on.')
      state.Print('  (E.g., reviewing WaitingFor items, you will find some that are old ')
      state.Print('  enough to require follow-up.)')
      state.Print('')
      state.Print('Commands:\n  * %s' % '\n  * '.join(APP_NAMESPACE.CmdList()))
      state.Print('')
      state.Print('For help on a specific command, type "help cmd".')


class UICmdPurgedeleted(UICmd):
  """Purges deleted items. That is, empties the trash.

  See also deletecompleted.
  """
  def Run(self, args):  # pylint: disable=missing-docstring,no-self-use
    state = FLAGS.pyatdl_internal_state
    self.RaiseIfAnyArgumentsGiven(args)
    state.ToDoList().PurgeDeleted()


class UICmdDeletecompleted(UICmd):
  """Deletes completed items. That is, moves them to the trash.

  See also purgedeleted.
  """
  def Run(self, args):  # pylint: disable=missing-docstring,no-self-use
    state = FLAGS.pyatdl_internal_state
    self.RaiseIfAnyArgumentsGiven(args)
    state.ToDoList().DeleteCompleted()


class UICmdPrjify(UICmd):
  """Converts an Action to a Project under the root Folder, deleting the Action."""
  def Run(self, args):  # pylint: disable=missing-docstring,no-self-use
    state = FLAGS.pyatdl_internal_state
    self.RaiseUnlessNArgumentsGiven(1, args)
    try:
      the_action, unused_project = _LookupAction(state, args[-1])
    except NoSuchContainerError:
      raise BadArgsError('Action "%s" not found.' % args[-1])
    if the_action.note:
      # TODO(chandler): support this case.
      raise BadArgsError(
          'Action has a Note; can\'t automatically convert to a Project.')
    the_action.is_deleted = True  # sets dtime
    _RunCmd(UICmdMkprj,
            ['--verbose', '--allow_slashes', the_action.name])
    # Set default context to whatever the action's context is? Judgment call.


class UICmdPwd(UICmd):
  """Prints the current working "directory" if you will, a Folder or a Project."""
  def Run(self, args):  # pylint: disable=missing-docstring,no-self-use
    state = FLAGS.pyatdl_internal_state
    self.RaiseIfAnyArgumentsGiven(args)
    q = state.CurrentWorkingContainerString()
    state.Print(q)


class UICmdUndo(UICmd):
  """Undoes the last undoable command. All mutations are undoable; read-only
  commands like 'ls' aren't.

  Takes no arguments.
  """
  def Run(self, args):  # pylint: disable=missing-docstring,no-self-use
    state = FLAGS.pyatdl_internal_state
    self.RaiseIfAnyArgumentsGiven(args)
    try:
      state.Undo()
    except state_module.NothingToUndoSlashRedoError as e:
      raise NothingToUndoSlashRedoError(e)


class UICmdRedo(UICmd):
  """Undoes the last 'undo' operation so long as no undoable commands have
  been executed since the last 'undo'.

  Takes no arguments.
  """
  def Run(self, args):  # pylint: disable=missing-docstring,no-self-use
    state = FLAGS.pyatdl_internal_state
    self.RaiseIfAnyArgumentsGiven(args)
    try:
      state.Redo()
    except state_module.NothingToUndoSlashRedoError as e:
      raise NothingToUndoSlashRedoError(e)


def RegisterAppcommands(cloud_only, appcommands_namespace):  # pylint: disable=too-many-statements
  """Calls appcommandsutil.Namespace.AddCmd() for all UICmd subclasses.

  Args:
    cloud_only: bool  # Register only commands that make sense with a cloud
                        backend
    appcommands_namespace: appcommandsutil.Namespace  # see APP_NAMESPACE
  """
  appcommands_namespace.AddCmd('?', UICmdHelp)
  appcommands_namespace.AddCmd('activatectx', UICmdActivatectx)
  appcommands_namespace.AddCmd('activateprj', UICmdActivateprj)
  appcommands_namespace.AddCmd('aspire', UICmdMaybe)
  appcommands_namespace.AddCmd('astaskpaper', UICmdAsTaskPaper)
  appcommands_namespace.AddCmd('cat', UICmdCat)
  appcommands_namespace.AddCmd('cd', UICmdCd)
  if not cloud_only:
    appcommands_namespace.AddCmd('chclock', UICmdChclock)
  appcommands_namespace.AddCmd('chctx', UICmdChctx)
  appcommands_namespace.AddCmd('chdefaultctx', UICmdChdefaultctx)
  appcommands_namespace.AddCmd('clearreview', UICmdClearreview)
  appcommands_namespace.AddCmd('complete', UICmdComplete)
  appcommands_namespace.AddCmd('completereview', UICmdCompletereview)
  appcommands_namespace.AddCmd('configurereview', UICmdConfigurereview)
  appcommands_namespace.AddCmd('deactivatectx', UICmdDeactivatectx)
  appcommands_namespace.AddCmd('deactivateprj', UICmdDeactivateprj)
  appcommands_namespace.AddCmd('deletecompleted', UICmdDeletecompleted)
  appcommands_namespace.AddCmd('do', UICmdDo)
  appcommands_namespace.AddCmd('dump', UICmdDump)
  appcommands_namespace.AddCmd('dumpprotobuf', UICmdDumpprotobuf)
  appcommands_namespace.AddCmd('echo', UICmdEcho)
  appcommands_namespace.AddCmd('echolines', UICmdEcholines)
  if not cloud_only:
    appcommands_namespace.AddCmd('exit', UICmdExit)
  appcommands_namespace.AddCmd('help', UICmdHelp)
  appcommands_namespace.AddCmd('hypertext', UICmdHypertext)
  appcommands_namespace.AddCmd('inctx', UICmdInctx)
  appcommands_namespace.AddCmd('inprj', UICmdInprj)
  if not cloud_only:
    appcommands_namespace.AddCmd('load', UICmdLoad)
  appcommands_namespace.AddCmd('loadtest', UICmdLoadtest)
  appcommands_namespace.AddCmd('ls', UICmdLs)
  appcommands_namespace.AddCmd('lsact', UICmdLsact)
  appcommands_namespace.AddCmd('lsctx', UICmdLsctx)
  appcommands_namespace.AddCmd('lsprj', UICmdLsprj)
  appcommands_namespace.AddCmd('maybe', UICmdMaybe)
  appcommands_namespace.AddCmd('mkact', UICmdTouch)
  appcommands_namespace.AddCmd('mkctx', UICmdMkctx)
  appcommands_namespace.AddCmd('mkdir', UICmdMkdir)
  appcommands_namespace.AddCmd('mkprj', UICmdMkprj)
  appcommands_namespace.AddCmd('mv', UICmdMv)
  appcommands_namespace.AddCmd('needsreview', UICmdNeedsreview)
  appcommands_namespace.AddCmd('note', UICmdNote)
  appcommands_namespace.AddCmd('prjify', UICmdPrjify)
  appcommands_namespace.AddCmd('purgedeleted', UICmdPurgedeleted)
  appcommands_namespace.AddCmd('almostpurgeallactionsincontext', UICmdAlmostPurgeAllActionsInContext)
  appcommands_namespace.AddCmd('pwd', UICmdPwd)
  if not cloud_only:
    appcommands_namespace.AddCmd('quit', UICmdExit)
  if not cloud_only:
    appcommands_namespace.AddCmd('redo', UICmdRedo)
  appcommands_namespace.AddCmd('rename', UICmdRename)
  appcommands_namespace.AddCmd('renamectx', UICmdRenamectx)
  appcommands_namespace.AddCmd('reset', UICmdReset)
  appcommands_namespace.AddCmd('roll', UICmdRoll)
  appcommands_namespace.AddCmd('rm', UICmdRmact)
  appcommands_namespace.AddCmd('rmact', UICmdRmact)
  appcommands_namespace.AddCmd('rmctx', UICmdRmctx)
  appcommands_namespace.AddCmd('rmdir', UICmdRmdir)
  appcommands_namespace.AddCmd('rmprj', UICmdRmprj)
  if not cloud_only:
    appcommands_namespace.AddCmd('save', UICmdSave)
  appcommands_namespace.AddCmd('seed', UICmdSeed)
  appcommands_namespace.AddCmd('sort', UICmdSort)
  appcommands_namespace.AddCmd('todo', UICmdTodo)
  appcommands_namespace.AddCmd('touch', UICmdTouch)
  appcommands_namespace.AddCmd('txt', UICmdAsTaskPaper)
  appcommands_namespace.AddCmd('uncomplete', UICmdUncomplete)
  if not cloud_only:
    appcommands_namespace.AddCmd('undo', UICmdUndo)
  appcommands_namespace.AddCmd('unicorn', UICmdUnicorn)
  appcommands_namespace.AddCmd('view', UICmdView)


APP_NAMESPACE = appcommandsutil.Namespace()


def ParsePyatdlPromptAndExecute(the_state, space_delimited_argv):
  """Finds the appropriate UICmd and executes it.

  A leading '+' will cause two commands, one an echo of the command, and the next the command itself (everything but
  the '+').

  Args:
    the_state: state.State
    space_delimited_argv: str
  Raises:
    Error

  """
  try:
    argv = lexer.SplitCommandLineIntoArgv(space_delimited_argv)
  except lexer.Error as e:
    raise BadArgsError(e)
  cmds = []
  if argv and argv[0] and argv[0][0] == '+':
    argv[0] = argv[0][1:]
    cmds.append(['echo', *(pipes.quote(x) for x in argv[:-1]), f'{pipes.quote(argv[-1])}:'])
  cmds.append(argv)
  try:
    for cmd in cmds:
      APP_NAMESPACE.FindCmdAndExecute(the_state, cmd)
  except appcommandsutil.CmdNotFoundError as e:
    raise BadArgsError(e)
  except appcommandsutil.InvalidUsageError as e:
    if not FLAGS.pyatdl_allow_exceptions_in_batch_mode:
      raise BadArgsError(e)
  except appcommandsutil.Error as e:
    raise Error(e)


# TODO(chandler): A test case where a Tibetan Unicode string [U+0F00, U+0FFF]
# is the value of --no_context_display_string. Another where we change the name
# of /inbox to something Tibetan via --inbox_project_name. Even better, emoji
# support (utf8mb4).

# TODO(chandler): Support cloning a project/folder/action. You can then have
# template items for processes that recur again and again, e.g. a packing list
# so you don't forget your toothbrush.

# TODO(chandler): "mkprj /Health; mkctx @Store; mkact "buy vitamins @store
# #health" should assign both a context and project (case insensitively).
