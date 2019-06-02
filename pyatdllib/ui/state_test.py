"""Unittests for module 'state'."""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import time

import gflags as flags  # https://code.google.com/p/python-gflags/

from pyatdllib.core import uid
from pyatdllib.core import unitjest
from pyatdllib.ui import appcommandsutil
from pyatdllib.ui import lexer
from pyatdllib.ui import state
from pyatdllib.ui import uicmd
uicmd.RegisterAppcommands(False, uicmd.APP_NAMESPACE)

FLAGS = flags.FLAGS


# pylint: disable=missing-docstring,too-many-public-methods
class StateTestCase(unitjest.TestCase):

  def setUp(self):
    super().setUp()
    FLAGS.pyatdl_randomize_uids = False
    time.time = lambda: 1337
    uid.ResetNotesOfExistingUIDs()
    FLAGS.pyatdl_show_uid = True
    FLAGS.pyatdl_separator = '/'
    self._the_state = None

  def tearDown(self):
    super().tearDown()
    del self._the_state

  def _Exec(self, argv):
    """Args: argv: str"""
    uicmd.APP_NAMESPACE.FindCmdAndExecute(
      self._the_state, lexer.SplitCommandLineIntoArgv(argv),
      generate_undo_info=True)

  def testCanonicalPath(self):
    self.assertEqual(state.State.CanonicalPath('//a'), '/a')
    self.assertEqual(state.State.CanonicalPath('Todos'), 'Todos')
    self.assertEqual(state.State.CanonicalPath('Todos/a'), 'Todos/a')
    self.assertEqual(state.State.CanonicalPath('Todos/a/'), 'Todos/a/')

  def testDirnameAndBasename(self):
    self.assertEqual(state.State.DirName('/'), '/')
    self.assertEqual(state.State.DirName('/a'), '/')
    self.assertEqual(state.State.DirName('/a/'), '/a')
    self.assertEqual(state.State.DirName('/a/b'), '/a')
    self.assertEqual(state.State.DirName('/a/b/c'), '/a/b')
    self.assertEqual(state.State.DirName('/a/b/c//'), '/')
    self.assertEqual(state.State.DirName('/a//b/c/'), '/b/c')

    self.assertEqual(state.State.DirName(''), '')
    self.assertEqual(state.State.DirName('a'), '')
    self.assertEqual(state.State.DirName('a/'), 'a')
    self.assertEqual(state.State.DirName('a/b'), 'a')
    self.assertEqual(state.State.DirName('a/b/c'), 'a/b')
    self.assertEqual(state.State.DirName('a/b/c//'), '/')
    self.assertEqual(state.State.DirName('a//b/c/'), '/b/c')

    self.assertEqual(state.State.BaseName(''), '')
    self.assertEqual(state.State.BaseName('/'), '')
    self.assertEqual(state.State.BaseName('/a'), 'a')
    self.assertEqual(state.State.BaseName('/x//a'), 'a')
    self.assertEqual(state.State.BaseName('/x//a/'), '')
    self.assertEqual(state.State.BaseName('/a/'), '')
    self.assertEqual(state.State.BaseName('/a//b/c'), 'c')
    self.assertEqual(state.State.BaseName('/a//b/c/'), '')

    self.assertEqual(state.State.BaseName('a'), 'a')
    self.assertEqual(state.State.BaseName('a/'), '')
    self.assertEqual(state.State.BaseName('b/c'), 'c')
    self.assertEqual(state.State.BaseName('b/c/'), '')

  def testUndo(self):
    # pylint: disable=too-many-locals,too-many-branches
    printed = []

    def Print(x):
      printed.append(x)

    def NewStateInstance():
      del printed[:]
      uid.ResetNotesOfExistingUIDs()
      return state.State(Print, uicmd.NewToDoList(), uicmd.APP_NAMESPACE)

    def TestNothingToRedo():
      try:
        self._the_state.Redo()
      except state.NothingToUndoSlashRedoError:
        pass
      else:
        del printed[:]
        self._Exec('dump -m')
        self.fail('Nothing raised; gist now=%s' % '\n'.join(printed))

    def TestNothingToUndo():
      try:
        self._the_state.Undo()
      except state.NothingToUndoSlashRedoError:
        pass
      else:
        self.fail('Nothing raised')

    def ExecuteUndoableCommand(the_index):
      self._Exec('mkctx Context%d' % the_index)
      TestNothingToRedo()

    def GenGist(gist_of_the_gist):
      return [
        '<todolist uid=2>',
        '    <inbox uid=1>',
        '        <project uid=1 is_deleted="False" is_complete="False" is_active="True" name="inbox">',
        '        ',
        '        </project>',
        '    </inbox>',
        '    <folder uid=2 is_deleted="False" name="">',
        '    ',
        '    </folder>',
        '    <contexts>',
        '        <context_list uid=3 is_deleted="False" name="Contexts">',
      ] + gist_of_the_gist + [
        '        </context_list>',
        '    </contexts>',
        '</todolist>',
      ]

    def AssertGistIs(expected_gist):
      assert not printed
      self._Exec('dump -m')
      self._AssertEqualWithDiff(
        expected_gist,
        printed)
      del printed[:]

    gist_no_contexts = GenGist([
      '        ',
    ])

    self._the_state = NewStateInstance()
    AssertGistIs(gist_no_contexts)
    TestNothingToUndo()
    TestNothingToRedo()

    self._the_state = NewStateInstance()
    TestNothingToRedo()

    self._the_state = NewStateInstance()
    ExecuteUndoableCommand(0)
    TestNothingToRedo()
    gist0 = GenGist([
      '            <context uid=4 is_deleted="False" is_active="True" name="Context0"/>',
    ])
    AssertGistIs(gist0)
    self._the_state.Undo()
    AssertGistIs(gist_no_contexts)
    # Now redo will work.
    self._the_state.Redo()
    AssertGistIs(gist0)
    TestNothingToRedo()

    # Undo now works.
    self._the_state.Undo()
    AssertGistIs(gist_no_contexts)
    TestNothingToUndo()

    # After a new mutation, redo will not work.
    ExecuteUndoableCommand(1)
    gist1 = GenGist([
      '            <context uid=4 is_deleted="False" is_active="True" name="Context1"/>',
    ])
    AssertGistIs(gist1)
    TestNothingToRedo()

    # Now we can undo once.
    self._the_state.Undo()
    AssertGistIs(gist_no_contexts)
    TestNothingToUndo()

    def TestUndoThenSomethingNewProhibitsRedoButNotUndo():
      """Tests that 'undo + do something new' makes Redo impossible but
      makes undo of something new possible.
      """
      ExecuteUndoableCommand(0)
      ExecuteUndoableCommand(1)
      gist01 = GenGist([
        '            <context uid=4 is_deleted="False" is_active="True" name="Context0"/>',
        '            <context uid=5 is_deleted="False" is_active="True" name="Context1"/>',
      ])
      AssertGistIs(gist01)
      self._the_state.Undo()
      AssertGistIs(gist0)
      ExecuteUndoableCommand(2)
      gist02 = GenGist([
        '            <context uid=4 is_deleted="False" is_active="True" name="Context0"/>',
        '            <context uid=5 is_deleted="False" is_active="True" name="Context2"/>',
      ])
      AssertGistIs(gist02)
      self._the_state.Undo()
      AssertGistIs(gist0)
      self._the_state.Undo()
      AssertGistIs(gist_no_contexts)
      TestNothingToUndo()
      self._the_state.Redo()
      AssertGistIs(gist0)
      self._the_state.Redo()
      AssertGistIs(gist02)
      self._the_state.Undo()
      AssertGistIs(gist0)
      self._the_state.Undo()
      AssertGistIs(gist_no_contexts)
      self.assertEqual(printed, [])

    TestUndoThenSomethingNewProhibitsRedoButNotUndo()

    def TestView():
      """Test case: The view filter is preserved across undo/redo."""
      del printed[:]
      self._the_state = NewStateInstance()
      self._Exec('mkctx ContextDeleted')
      self._Exec('rmctx ContextDeleted')
      self._Exec('lsctx')
      self.assertEqual(
          printed,
          ["--context-- uid=0 ---active--- '<none>'"])
      del printed[:]
      self._Exec('view all_even_deleted')
      self._Exec('lsctx')
      self.assertEqual(
        printed,
        ["--context-- uid=0 ---active--- '<none>'",
         '--context-- uid=4 --DELETED-- ---active--- ContextDeleted-deleted-at-1337'])
      time.time = lambda: 1338
      self._the_state.Undo()
      self._Exec('rmctx ContextDeleted')
      del printed[:]
      self._Exec('lsctx')
      self.assertEqual(
        printed,
        ['--context-- uid=0 ---active--- \'<none>\'',
         '--context-- uid=4 --DELETED-- ---active--- ContextDeleted-deleted-at-1338'])
      del printed[:]

    TestView()

    def TestCommandsSpecifyingUID():
      """Test case: Commands like 'rmctx uid=13' should work after being
      undone and then redone.
      """
      del printed[:]
      self._the_state = NewStateInstance()
      ExecuteUndoableCommand(0)  # uid=4
      ExecuteUndoableCommand(1)  # uid=5
      self._Exec('rmctx uid=4')
      gist01with0deleted = [
        '<todolist uid=2>',
        '    <inbox uid=1>',
        '        <project uid=1 is_deleted="False" is_complete="False" is_active="True" name="inbox">',
        '        ',
        '        </project>',
        '    </inbox>',
        '    <folder uid=2 is_deleted="False" name="">',
        '    ',
        '    </folder>',
        '    <contexts>',
        '        <context_list uid=3 is_deleted="False" name="Contexts">',
        '            <context uid=4 is_deleted="True" is_active="True" name="Context0-deleted-at-1338"/>',
        '            <context uid=5 is_deleted="False" is_active="True" name="Context1"/>',
        '        </context_list>',
        '    </contexts>',
        '</todolist>',
      ]
      AssertGistIs(gist01with0deleted)
      self._the_state.Undo()
      gist01 = GenGist([
        '            <context uid=4 is_deleted="False" is_active="True" name="Context0"/>',
        '            <context uid=5 is_deleted="False" is_active="True" name="Context1"/>',
      ])
      AssertGistIs(gist01)
      self._the_state.Redo()
      AssertGistIs(gist01with0deleted)

    TestCommandsSpecifyingUID()

    def TestResetCommand():
      """Test case: we have an undo stack but call 'reset'. There should be an
      empty undo stack.
      """
      del printed[:]
      self._the_state = NewStateInstance()
      ExecuteUndoableCommand(0)
      self._Exec('reset --annihilate')
      TestNothingToUndo()
      TestNothingToRedo()

    TestResetCommand()

    # TODO(chandler): This is the wrong place for this test. Move to
    # appcommandsutil_test.py:
    def TestUnicodeCommandLines():
      del printed[:]
      self._the_state = NewStateInstance()
      try:
        self._Exec('ls \u2014help')
      except appcommandsutil.InvalidUsageError:
        pass
      else:
        assert False
      try:
        self._Exec('reset --\u2014annihilate')
      except appcommandsutil.InvalidUsageError:
        pass
      else:
        assert False
      try:
        self._Exec('\u2014')
      except appcommandsutil.CmdNotFoundError:
        pass
      else:
        assert False

    TestUnicodeCommandLines()


if __name__ == '__main__':
  unitjest.main()

# TODO(chandler): A test case that proves that all UICmds correctly
# return UndoableCommand iff they are mutations.
