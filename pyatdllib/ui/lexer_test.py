"""Unittests the 'lexer' module."""

from __future__ import unicode_literals

import gflags as flags  # https://code.google.com/p/python-gflags/

from pyatdllib.core import unitjest
from pyatdllib.ui import lexer

FLAGS = flags.FLAGS


# pylint: disable=missing-docstring,protected-access,too-many-public-methods
class LexerTestCase(unitjest.TestCase):

  def setUp(self):
    super().setUp()
    self.maxDiff = None  # pylint: disable=invalid-name
    FLAGS.pyatdl_allow_command_line_comments = False

  def testSplitCommandLineIntoArgv(self):
    FLAGS.pyatdl_allow_command_line_comments = False

    def nonposix_fut(x):
      return lexer.SplitCommandLineIntoArgv(x, posix=False)

    def fut(x):
      return lexer.SplitCommandLineIntoArgv(x)

    self.assertEqual(nonposix_fut('baz'),
                     ['baz'])
    self.assertEqual(nonposix_fut('baz  y'),
                     ['baz', 'y'])
    self.assertEqual(fut("'baz  y'"),
                     ['baz  y'])
    self.assertEqual(nonposix_fut("'baz  y'"),
                     ['\'baz  y\''])
    self.assertEqual(nonposix_fut('"baz  y"'),
                     ["\"baz  y\""])
    self.assertEqual(fut('"baz  y"'),
                     ["baz  y"])
    self.assertEqual(fut(r"""a --b 3 --c=4 -d5 -c 6"""),
                     ['a', '--b', '3', '--c=4', '-d5', '-c', '6'])
    self.assertEqual(nonposix_fut("""complete 'an action'"""),
                     ['complete', '\'an action\''])
    self.assertEqual(fut("""complete 'an action'"""),
                     ['complete', 'an action'])
    self.assertEqual(nonposix_fut('complete \'an action\' '),
                     ['complete', '\'an action\''])
    self.assertEqual(fut('complete \'an action\' '),
                     ['complete', 'an action'])
    self.assertEqual(fut('complete \'an action\' '),
                     ['complete', 'an action'])
    self.assertEqual(fut('complete "an action"'),
                     ['complete', 'an action'])
    FLAGS.pyatdl_allow_command_line_comments = True
    self.assertEqual(fut(r"""baz#y"""),
                     ['baz'])
    FLAGS.pyatdl_allow_command_line_comments = False
    self.assertEqual(fut(r"""baz#y"""),
                     ['baz#y'])
    self.assertEqual(nonposix_fut('\\\\'),
                     ['\\\\'])
    self.assertEqual(fut('\\\\'),
                     ['\\'])
    self.assertEqual(nonposix_fut('\\'),
                     ['\\'])
    try:
      nonposix_fut('\\')
    except lexer.ShlexSyntaxError as e:
      self.assertEqual(str(e),
                       'Cannot parse command line. No escaped character')
    self.assertEqual(fut('chctx -- -Ca -2'),
                     # We let gflags implement the '--' magic.
                     ['chctx', '--', '-Ca', '-2'])


if __name__ == '__main__':
  unitjest.main()
