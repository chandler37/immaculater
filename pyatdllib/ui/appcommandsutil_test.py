"""Unittests for module 'appcommandsutil'."""

from pyatdllib.core import uid
from pyatdllib.core import unitjest
from pyatdllib.ui import appcommandsutil
from pyatdllib.ui import lexer
from pyatdllib.ui import state
from pyatdllib.ui import uicmd

from absl import flags  # type: ignore


uicmd.RegisterAppcommands(False, uicmd.APP_NAMESPACE)


FLAGS = flags.FLAGS


class AppcommandsutilTestCase(unitjest.TestCase):

  def setUp(self):
    super().setUp()
    FLAGS.pyatdl_randomize_uids = False
    uid.ResetNotesOfExistingUIDs()
    FLAGS.pyatdl_show_uid = True
    FLAGS.pyatdl_separator = '/'

  def _Exec(self, argv):
    """Args: argv: str"""
    uicmd.APP_NAMESPACE.FindCmdAndExecute(
      self._the_state, lexer.SplitCommandLineIntoArgv(argv))

  # TODO(chandler): This is the wrong place for this test. Move to
  # appcommandsutil_test.py:
  def testUnicodeCommandLines(self):
    printed = []

    def Print(x):
      printed.append(x)

    def NewStateInstance():
      del printed[:]
      uid.ResetNotesOfExistingUIDs()
      return state.State(Print, uicmd.NewToDoList(), uicmd.APP_NAMESPACE)

    self._the_state = NewStateInstance()
    try:
      self._Exec('ls \u2014help')
    except appcommandsutil.InvalidUsageError:
      pass
    except Exception:
      raise
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


if __name__ == '__main__':
  unitjest.main()
