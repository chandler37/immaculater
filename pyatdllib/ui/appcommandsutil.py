"""Extensions to third_party.google.apputils.google.apputils.appcommands.

The authors of that code didn't expect we'd need various "namespaces"
for appcommands. We use appcommands in a plain vanilla fashion in
immaculater.py, but we also want to use them, in a separate namespace, in
uicmd.py.
"""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import six
import time

import gflags as flags

from third_party.google.apputils.google.apputils import app
from third_party.google.apputils.google.apputils import appcommands

from . import undoutil


flags.DEFINE_bool('pyatdl_paranoia',
                  True,  # Maybe they _are_ out to get us!
                  'Do more frequent checks for the well-formedness of internal '
                  'data structures?')
flags.DEFINE_bool('pyatdl_give_full_help_for_uicmd', True,
                  'Full or concise help when a UICmd is incorrectly used?')


FLAGS = flags.FLAGS


class Error(Exception):
  """Base class for this module's exceptions."""


class InvalidUsageError(Error):
  """Invalid usage. A usage message has already been printed."""


class CmdNotFoundError(Error):
  """No such command exists."""


class IncorrectUsageError(Exception):
  """If the appcommand detects invalid usage, it can raise app.UsageError
  directly or it can raise this. This is governed by
  FLAGS.pyatdl_give_full_help_for_uicmd.
  """


_UICMD_MODULE_NAME = 'ui.uicmd'


def _GenAppcommandsUsage(cmd, printer):
  """Returns a replacement for app.usage."""
  # pylint: disable=too-many-arguments,unused-argument
  def Usage(shorthelp=0, writeto_stdout=0, detailed_error=None,
            exitcode=None, show_cmd=None, show_global_flags=False):
    """A replacement for app.usage."""
    printer('%s: Incorrect usage; details below.' % show_cmd)
    printer('Correct usage is as follows:')
    printer('')
    for line in ('  ' + cmd.__doc__.rstrip()).splitlines():
      printer(line)
    # Print out str(FLAGS) for just the UICmd-specific flags.
    tmp_flags = flags.FlagValues()
    type(cmd)(show_cmd, tmp_flags)
    prefix = _UICMD_MODULE_NAME + ':\n'
    flag_str = tmp_flags.ModuleHelp(str(_UICMD_MODULE_NAME) if six.PY2 else _UICMD_MODULE_NAME)
    flag_str = flag_str.lstrip()
    if flag_str.startswith(prefix):
      flag_str = flag_str[len(prefix):]
    if flag_str:
      printer('')
      printer('flags:')
      for line in flag_str.splitlines():
        printer(line)
    if detailed_error is not None:
      printer('')
      printer('The incorrect usage is as follows:')
      printer('')
      for line in six.text_type(detailed_error).splitlines():
        printer('  ' + line)

  return Usage


def _DeleteSpecialFlagHelp(help_str):
  """Returns help_str minus the help for --flagfile etc."""
  rv = ''
  for line in help_str.splitlines():
    if line == 'ui.uicmd:':
      # Flags for ls:
      #
      # ui.uicmd:
      # -R,--[no]recursive: Additionally lists subdirectories recursively
      continue
    if line.strip() == 'gflags:':
      while rv.endswith('\n'):
        rv = rv[:-1]
      return rv
    rv += line
    rv += '\n'
  raise AssertionError('gflags help strings have changed. help=%s'
                       % help_str)


class Namespace(object):
  """A container for appcommands.

  The command-line flags for these (the ones defined in __init__()) live
  in their own namespace, but during the execution of the command they
  appear to be global flags (in gflags.FLAGS). In addition, there is a
  special flag called FLAGS.pyatdl_internal_state that points to a
  state.State.
  """
  def __init__(self):
    """Init."""
    self._cmd_list = {}
    self._cmd_alias_list = {}
    self._flag_values_by_cmd = {}  # str: flags.FlagValues

  def AddCmd(self, command_name, cmd_factory, **kargs):
    """See appcommands.AddCmd.

    Raises:
      Error
    """
    try:
      assert command_name not in self._flag_values_by_cmd, command_name
      self._flag_values_by_cmd[command_name] = flags.FlagValues()
      cmd = cmd_factory(command_name,
                        self._flag_values_by_cmd[command_name],
                        **kargs)
      self._AddCmdInstance(command_name, cmd, **kargs)
    except appcommands.AppCommandsError as e:
      raise Error(e)

  def _AddCmdInstance(self, command_name, cmd, command_aliases=None):
    """Registers the command so that FindCmdAndExecute can find it."""
    for name in [command_name] + (command_aliases or []):
      self._cmd_alias_list[name] = command_name
    self._cmd_list[command_name] = cmd

  def _RunCommand(self, the_state, cmd, argv):
    """Executes the given command.

    Makes the right thing happen when the appcommand raises
    app.UsageError. Temporarily makes the appcommand-specific
    command-line flags appear to be global flags.

    Args:
      the_state: state.State
      cmd: uicmd.UICmd
      argv: [str]
    Returns:
      UndoableCommand|None
    Raises:
      InvalidUsageError
    """
    flag_values = self._flag_values_by_cmd[argv[0]]
    FLAGS.AppendFlagValues(flag_values)
    # Prepare flags parsing, to redirect help, to show help for command
    orig_app_usage = app.usage

    def ReplacementAppUsage(shorthelp=0, writeto_stdout=1,
                            detailed_error=None, exitcode=None):
      """Replaces app.usage."""
      func = _GenAppcommandsUsage(
        cmd,
        the_state.Print)
      func(show_cmd=None if not argv else argv[0],
           shorthelp=shorthelp,
           writeto_stdout=writeto_stdout,
           detailed_error=detailed_error,
           exitcode=exitcode)

    app.usage = ReplacementAppUsage
    # Parse flags and restore app.usage afterwards
    try:
      try:
        uc = None
        if cmd.IsUndoable():
          uc = undoutil.UndoableCommand(argv)  # unparsed argv
        try:
          argv = flag_values(argv)
        except flags.UnrecognizedFlagError as e:
          raise app.UsageError(
            'Cannot parse arguments. If you have a leading hyphen in one of '
            'your arguments, preface that argument with a \'--\' argument, '
            'the syntax that makes all following arguments positional. '
            'Detailed error: %s'
            % six.text_type(e))
        except flags.FlagsError as e:
          raise app.UsageError(
            'Cannot parse arguments. Note the \'--\' syntax which makes all '
            'following arguments positional. Detailed error: %s'
            % six.text_type(e))
        try:
          cmd.Run(argv)
        except IncorrectUsageError as e:
          if FLAGS.pyatdl_give_full_help_for_uicmd:
            raise app.UsageError(six.text_type(e))
          else:
            raise
        except Exception as e:
          msg = 'For the following error, note that argv=%s. Error: %s' % (argv, six.text_type(e))
          raise type(e)(msg) from e
        return uc
      except app.UsageError as error:
        app.usage(shorthelp=1, detailed_error=error, exitcode=error.exitcode)
        raise InvalidUsageError(six.text_type(error))
      finally:
        flag_values.Reset()
    finally:
      # Restore app.usage and remove this command's flags from the global flags.
      app.usage = orig_app_usage
      FLAGS.RemoveFlagValues(flag_values)

  def FindCmdAndExecute(self, the_state, argv, generate_undo_info=True):
    """Looks up the appropriate command and executes it.

    Args:
      the_state: state.State
      argv: [basestring]
      generate_undo_info: bool
    Raises:
      CmdNotFoundError
      InvalidUsageError
    """
    if argv[0] not in self._cmd_alias_list:
      raise CmdNotFoundError('Command "%s" not found; see "help"' % argv[0])
    cmd = self._cmd_list[self._cmd_alias_list[argv[0]]]
    if not hasattr(FLAGS, 'pyatdl_internal_state'):
      flags.DEFINE_string('pyatdl_internal_state',
                          'INTERNAL USE ONLY cmd=%s time=%s' % (argv[0], time.time()),
                          'FOR INTERNAL USE ONLY',
                          flag_values=FLAGS)
    # If the above flag already existed, it was first set when UICmdUndo or
    # UICmdRedo ran. Actually, that command is still running. The undo/redo
    # UICmd has already grabbed the value it needs, which will be a different
    # value because a new State is constructed as part of undo/redo. So we now
    # set the flag to point to the new rewound State, the one being replayed.
    FLAGS.pyatdl_internal_state = the_state
    saved_usage = appcommands.AppcommandsUsage
    appcommands.AppcommandsUsage = _GenAppcommandsUsage(cmd, the_state.Print)
    try:
      if FLAGS.pyatdl_paranoia:
        try:
          the_state.ToDoList().CheckIsWellFormed()
        except AssertionError as e:
          raise AssertionError('precheck: argv=%s error=%s' % (argv, six.text_type(e)))
      rv = self._RunCommand(the_state, cmd, argv)
      if rv is not None and generate_undo_info:
        the_state.RegisterUndoableCommand(rv)
      if FLAGS.pyatdl_paranoia:
        try:
          the_state.ToDoList().CheckIsWellFormed()
        except AssertionError as e:
          raise AssertionError('postcheck: %s' % six.text_type(e))
    finally:
      if hasattr(FLAGS, 'pyatdl_internal_state'):  # see above about undo/redo
        delattr(FLAGS, 'pyatdl_internal_state')
      appcommands.AppcommandsUsage = saved_usage

  def CmdList(self):
    """Returns the full list of command names, aliases included.

    Returns:
      [str]
    """
    return sorted(self._cmd_alias_list)

  def HelpForCmd(self, name):
    """Returns the help string for the named command.

    Args:
      name: str
    Returns:
      str
    """
    canonical_name = self._cmd_alias_list.get(name)
    if not canonical_name:
      raise CmdNotFoundError('Command not found: "%s"' % name)
    cmd = self._cmd_list[canonical_name]
    if cmd.__doc__.strip():
      flags_help = ''
      cmd_flags = self._flag_values_by_cmd[canonical_name]
      if cmd_flags.RegisteredFlags():
        prefix = '  '
        flags_help += '%s\nFlags for %s:\n' % (prefix, name)
        flags_help += cmd_flags.GetHelp(prefix + '  ')
        flags_help = _DeleteSpecialFlagHelp(flags_help)
        flags_help += '\n\n'
      return cmd.__doc__ + flags_help
    else:
      raise AssertionError('No class docstring found for command %s' % name)


"""TODO(chandler): .. should not appear here:

    InvalidUsageError: With current working Folder/Project "/", there is no such child "\u2014help".  Choices:
    ..
"""
