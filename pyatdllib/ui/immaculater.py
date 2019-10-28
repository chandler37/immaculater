#!/usr/bin/python

"""A command-line interface to pyatdl, yet another to-do list.

The most important command is 'help'.

The key notions are Action, Context, Folder, and Project. The commands use the
filesystem idiom. Actions and Contexts are like regular files. Projects and
Folders are like directories.

This was the first UI used in development. Having a command line makes for
readable functional tests. Instead of a bunch of python, you can specify lines
of commands at the 'immaculater>' prompt.

All future user interfaces are expected to translate things into this
command-line interface, adding new commands if necessary.

After importing this file, you must call RegisterUICmds.
"""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import base64
import hashlib
import os
import random
import six
from six.moves import input
from six.moves import xrange
import tempfile

import gflags as flags  # https://code.google.com/p/python-gflags/ now called abseil-py

from third_party.google.apputils.google.apputils import app
from third_party.google.apputils.google.apputils import appcommands
from google.protobuf import text_format

from . import serialization
from . import state
from . import uicmd

FLAGS = flags.FLAGS


def _SingletonDatabasePath():  # pylint: disable=missing-docstring
  # If there are two versions of pyatdl installed, this must vary between the two:
  pyatld_installation_path = os.path.dirname(os.path.abspath(__file__))
  try:
    return os.path.join(
      tempfile.gettempdir(),
      hashlib.md5(pyatld_installation_path.encode('utf-8')).hexdigest(),
      'saves',
      'pyatdl_ToDoList_singleton.protobuf')
  except NotImplementedError:  # google_appengine only provides TemporaryFile
    return None


flags.DEFINE_string(
    'database_filename',
    _SingletonDatabasePath(),
    'Path of the save file, currently a serialized protobuf (see '
    'https://developers.google.com/protocol-buffers/docs/overview) '
    'of type pyatdl.ToDoList. If this file\'s '
    'directory does not exist, it will be created. If the file does not exist, '
    'it will be created.')
flags.DEFINE_string(
    'pyatdl_prompt',
    'immaculater> ',
    'During interactive use, what text do you want to appear as the command line prompt (like bash\'s $PS1)?')
flags.ADOPT_module_key_flags(state)
flags.ADOPT_module_key_flags(uicmd)


class Error(Exception):
  """Base class for this module's exceptions."""


class NoCommandByThatNameExistsError(Error):
  """No such command found."""


class BadArgsForCommandError(Error):
  """Invalid arguments given."""


def _Print(s):
  """For easy mocking in the unittest."""
  if six.PY2:
    print(str(s))
  else:
    print(s)


def _Input(prompt):
  """For easy mocking in the unittest."""
  return input(prompt)


def Base64RandomSlug(num_bits):
  """Returns a URL-safe slug encoding the given pseudorandom number.

  Args:
    num_bits: int  # divisible by 8
  Returns:
    str
  """
  if num_bits % 8:
    raise ValueError("The sole argument needs to be a multiple of 8")
  array = bytearray(random.getrandbits(8) for x in xrange(num_bits // 8))
  b = base64.urlsafe_b64encode(six.binary_type(array))
  return b.decode('utf-8').rstrip('=')


def MutateToDoListLoop(lst, printer=None, writer=None, html_escaper=None):
  """Loops forever (until EOFError) calling _Input for the User's input and mutating lst.

  Args:
    lst: tdl.ToDoList
    printer: lambda unicode: None
    writer: object with 'write(bytes)' method
    html_escaper: lambda unicode: unicode
  Returns:
    None
  """
  printer = printer if printer else _Print
  the_state = state.State(printer, lst, uicmd.APP_NAMESPACE, html_escaper)
  try:
    while True:
      ri = _Input(FLAGS.pyatdl_prompt)
      ri = ri.strip()
      if not ri:
        continue
      else:
        try:
          uicmd.ParsePyatdlPromptAndExecute(the_state, ri)
        except uicmd.BadArgsError as e:
          printer(six.text_type(e))
          continue
        try:
          if FLAGS.database_filename is None:
            serialization.SerializeToDoList2(the_state.ToDoList(), writer)
          else:
            serialization.SerializeToDoList(
              the_state.ToDoList(), FLAGS.database_filename)
        except AssertionError as e:
          raise AssertionError('With ri=%s, %s' % (ri, str(e)))
  except EOFError:
    pass


def LoopInteractively(reader=None, writer=None):
  """Loads the to-do list from the save file, loops indefinitely, saving the file periodically.
  """
  if FLAGS.database_filename is None:
    todolist = serialization.DeserializeToDoList2(
      reader, tdl_factory=uicmd.NewToDoList)
  else:
    todolist = serialization.DeserializeToDoList(
      FLAGS.database_filename, tdl_factory=uicmd.NewToDoList)
  _Print('Welcome to Immaculater!')
  _Print('')
  _Print('Autosave is ON.  File: %s' % FLAGS.database_filename)
  _Print('')
  _Print('Type "help" to get started.')
  MutateToDoListLoop(todolist, _Print, writer)
  if writer:
    _Print('')
    _Print('To-do list saved -- it is in fact saved after each command.')
  else:
    _Print('')
    _Print('File saved -- it is in fact saved after each command.')
    _Print('The file is %s' % FLAGS.database_filename)


class Cmd(appcommands.Cmd):  # pylint: disable=too-few-public-methods
  """Superclass for all our Cmds."""
  def Run(self, argv):
    """Override."""


class Interactive(Cmd):  # pylint: disable=too-few-public-methods
  """Run interactively, reading from stdin and printing to stdout."""
  def Run(self, argv):
    super().Run(argv)
    if len(argv) != 1:
      raise app.UsageError('Too many args: %s' % repr(argv))
    try:
      LoopInteractively()
    except serialization.DeserializationError as e:
      _Print(e)
      _Print('Aborting.')
      return 1


def ApplyBatchOfCommands(input_file, printer=None, reader=None, writer=None,
                         html_escaper=None):
  """Reads commands, one per line, from the named file, and performs them.

  Args:
    input_file: file
    writer: None|object with 'write(bytes)' method
    html_escaper: lambda unicode: unicode
  Returns:
    {'view': str,  # e.g., 'default'
     'cwc': str,  # current working Container
     'cwc_uid': int}  # current working Container's UID
  Raises:
    Error
  """
  if not printer:
    printer = _Print
  if FLAGS.database_filename is None:
    tdl = serialization.DeserializeToDoList2(reader,
                                             tdl_factory=uicmd.NewToDoList)
  else:
    tdl = serialization.DeserializeToDoList(FLAGS.database_filename,
                                            tdl_factory=uicmd.NewToDoList)
  the_state = state.State(
    printer,
    tdl,
    uicmd.APP_NAMESPACE,
    html_escaper)
  for line in input_file:
    line = line.strip()
    if not line:
      continue
    try:
      uicmd.ParsePyatdlPromptAndExecute(the_state, line)
    except uicmd.BadArgsError as e:
      printer(str(e))
      if not FLAGS.pyatdl_allow_exceptions_in_batch_mode:
        raise BadArgsForCommandError(str(e))
      continue
  the_state.ToDoList().CheckIsWellFormed()
  if FLAGS.database_filename is None:
    serialization.SerializeToDoList2(the_state.ToDoList(), writer)
  else:
    serialization.SerializeToDoList(
      the_state.ToDoList(), FLAGS.database_filename)
  return {'view': the_state.ViewFilter().ViewFilterUINames()[0],
          'cwc': the_state.CurrentWorkingContainerString(),
          'cwc_uid': the_state.CurrentWorkingContainer().uid}


class Batch(Cmd):  # pylint: disable=too-few-public-methods
  """Run in batch mode, reading lines of commands from a file and printing to stdout.

  The filename '-' is special; it means to read lines of commands from stdin.

  The database affected is specified by --database_filename, but the
  'load'/'save' commands are available to you.
  """
  def Run(self, argv):
    super().Run(argv)
    if len(argv) != 2:
      raise app.UsageError('Needs one argument, the filename of the file '
                           'where each line is a command.')
    if argv[-1] == '-':
      argv[-1] = '/dev/stdin'
    if not os.path.exists(argv[-1]):
      raise app.UsageError('File specified does not exist: %s' % argv[-1])
    try:
      with open(argv[-1]) as input_file:
        ApplyBatchOfCommands(input_file)
    except serialization.DeserializationError as e:
      _Print(e)
      _Print('Aborting.')
      return 1


class ResetDatabase(Cmd):  # pylint: disable=too-few-public-methods
  """Erase the current database and replace it with a brand-new one.

  Uses the flag --database_filename.

  This *should* be functionally the same thing as using the 'interactive' shell
  and giving it the 'reset' command.
  """
  def Run(self, argv):
    super().Run(argv)
    if len(argv) != 1:
      raise app.UsageError('Too many args: %s' % repr(argv))
    if os.path.exists(FLAGS.database_filename):
      os.remove(FLAGS.database_filename)
    print('Database successfully reset.')


class DumpRawProtobuf(Cmd):  # pylint: disable=too-few-public-methods
  """Partially deserializes the to-do list but stops as soon as a protobuf is
  available. Prints that protobuf.

  Uses the flag --database_filename.
  """
  def Run(self, argv):
    super().Run(argv)
    if len(argv) != 1:
      raise app.UsageError('Too many args: %s' % repr(argv))
    pb = serialization.GetRawProtobuf(FLAGS.database_filename)
    print(text_format.MessageToString(pb))


def main(_):
  """Register the commands."""
  appcommands.AddCmd('interactive', Interactive,
                     command_aliases=['shell', 'sh'])
  appcommands.AddCmd('batch', Batch)
  appcommands.AddCmd('reset_database', ResetDatabase)
  appcommands.AddCmd('dump_raw_protobuf', DumpRawProtobuf)


def RegisterUICmds(cloud_only):
  """Registers all UICmds unless cloud_only is True, in which case a subset are
  registered.

  Args:
    cloud_only: bool  # Registers only the subset making sense with a cloud
                        backend
  """
  uicmd.RegisterAppcommands(cloud_only, uicmd.APP_NAMESPACE)


def InitFlags():
  """If not running as __main__, use this to initialize the FLAGS module."""
  FLAGS([])


if __name__ == '__main__':
  RegisterUICmds(cloud_only=False)
  appcommands.Run()
