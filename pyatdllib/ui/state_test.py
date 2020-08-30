"""Unittests for module 'state'."""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import time

from absl import flags  # type: ignore

from pyatdllib.core import uid
from pyatdllib.core import unitjest
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
      self._the_state, lexer.SplitCommandLineIntoArgv(argv))

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


if __name__ == '__main__':
  unitjest.main()
