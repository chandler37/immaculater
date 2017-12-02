"""Tools that help implement "undo"/"redo" UICmds."""

import copy


class Error(Exception):
  """Base class for this module's exceptions."""


class NothingToUndoSlashRedoError(Error):
  """No commands left to undo/redo."""


class UndoableCommand(object):
  """All UICmds are either undoable or not. All commands that mutate the
  list are undoable; no read-only commands are undoable. It would confuse
  the user to "undo" a non-undoable command like "ls" because nothing
  would happen.
  """
  def __init__(self, args):
    self._args = copy.copy(args)

  def CommandName(self):
    """Returns the command's name.

    Returns:
      str
    """
    return copy.copy(self._args[0])

  def CommandArgsIncludingName(self):
    """Returns the arguments including $0.

    Returns:
      [str]
    """
    return copy.copy(self._args)

  def __str__(self):
    return repr(self)

  def __repr__(self):
    return 'UndoableCommand%s' % str(self._args)


# TODO(chandler): Serialize all UICmds in pyatdl_pb2.ToDoList? Maybe the
# User actually wants 'undo' to work across saves, but probably that level of
# 'undo' is confusing. Could help in the case of recovering from a bug, though.
class UndoStack(object):
  """A stack of uicmd.UICmds supporting undo and redo.

  We could do this in one of two ways:

  1 When applying a UICmd, have it return an equal-but-opposite UICmd
    that will undo. To undo, execute the returned command.

  2 When applying a UICmd, if it is an undoable operation, have it return a
    UICmd that is equivalent to the original UICmd (could be the same,
    but could be canonicalized or do some late or early binding). To undo,
    repeat the latest deserialization and apply all UICmds except the last.

  We use option 2.
  """

  def __init__(self, state):
    """Init.

    In Java, we'd use an Interface RewindableSupportingReplay to describe
    the type of 'state'. Instead, we use duck typing.
    RewindableSupportingReplay is defined as "RewindableSupportingReplay
    has methods 'RewindForUndoRedo()' and 'ReplayCommandForUndoRedo(undoutil.UndoableCommand)'"

    Args:
      state: RewindableSupportingReplay
    """
    # If self._undo_index >= 0, self._undo_stack[:self._undo_index] is the list
    # of commands that we will replay from the beginning.
    self._undo_stack = []  # [UndoableCommand]
    self._undo_index = -1
    self._redo_index = -1
    self._state = state

  def RegisterUndoableCommand(self, cmd):
    """Makes note of the most recent undoable UICmd.

    Args:
      cmd: UndoableCommand
    """
    assert isinstance(cmd, UndoableCommand)
    if self._redo_index >= 0:
      del self._undo_stack[self._redo_index:]
    self._undo_stack.append(cmd)
    self._undo_index += 1
    self._redo_index = -1

  def Undo(self):
    """Undoes a single command.

    Raises:
      NothingToUndoSlashRedoError
    """
    if self._undo_index < 0:
      raise NothingToUndoSlashRedoError('There are no more operations to undo')
    self._state.RewindForUndoRedo()
    for cmd in self._undo_stack[:self._undo_index]:
      self._state.ReplayCommandForUndoRedo(cmd)
    self._redo_index = self._undo_index
    self._undo_index -= 1

  def Redo(self):
    """Redoes a single command.

    Raises:
      NothingToUndoSlashRedoError
    """
    if self._redo_index < 0:
      raise NothingToUndoSlashRedoError('Nothing left to redo')
    cmds_to_replay = self._undo_stack[self._redo_index:]
    if not cmds_to_replay:
      raise NothingToUndoSlashRedoError('Nothing left to redo')
    self._state.ReplayCommandForUndoRedo(cmds_to_replay[0])
    self._undo_index += 1
    self._redo_index += 1
