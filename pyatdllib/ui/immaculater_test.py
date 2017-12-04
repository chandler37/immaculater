"""Unittests for module 'immaculater'."""

import copy
import os
import pipes
import random
import tempfile
import time
import zlib

import gflags as flags  # https://github.com/gflags/python-gflags
from gflags import _helpers

from google.protobuf import message

from pyatdllib.ui import immaculater
from pyatdllib.core import tdl
from pyatdllib.core import uid
from pyatdllib.core import unitjest

immaculater.RegisterUICmds(cloud_only=False)

FLAGS = flags.FLAGS


def _CreateTmpFile(contents):
  """Creates a new temporary file (that will never be removed) and returns the
  name of that file.

  Args:
    contents: str
  Returns:
    str
  """
  with tempfile.NamedTemporaryFile(
    prefix='tmppyatdluiimmaculater_test', delete=False) as tf:
    tempfilename = tf.name
  with open(tempfilename, 'wb') as f:
    f.write(contents)
  return tempfilename


# pylint: disable=line-too-long,missing-docstring,too-many-public-methods
class ImmaculaterTestCase(unitjest.TestCase):
  # pylint: disable=trailing-whitespace

  def setUp(self):
    assert _helpers.GetHelpWidth
    _helpers.GetHelpWidth = lambda: 180
    uid.singleton_factory = uid.Factory()
    # There is a glags.TextWrap glitch re: the line '-a,--[no]show_all:
    # Additionally lists everything, even hidden objects, overriding the view
    # filter' so we replace TextWrap.
    def MyTextWrap(text, length=None, indent='', firstline_indent=None, tabs='    '):  # pylint: disable=unused-argument
      return text

    flags.TextWrap = MyTextWrap
    FLAGS.pyatdl_allow_exceptions_in_batch_mode = True
    FLAGS.pyatdl_separator = '/'
    FLAGS.pyatdl_break_glass_and_skip_wellformedness_check = False
    FLAGS.pyatdl_give_full_help_for_uicmd = False
    FLAGS.pyatdl_paranoia = True
    FLAGS.pyatdl_allow_command_line_comments = False
    FLAGS.pyatdl_zlib_compression_level = 6
    FLAGS.pyatdl_show_uid = False
    FLAGS.seed_upon_creation = False
    FLAGS.no_context_display_string = '<none>'
    FLAGS.time_format = '%Y/%m/%d-%H:%M:%S'
    FLAGS.timezone = 'US/Eastern'
    self.saved_time = time.time
    time.time = lambda: 36
    self.todolist = tdl.ToDoList()
    time.time = self.saved_time
    self.saved_input = immaculater._Input  # pylint: disable=protected-access
    self.saved_print = immaculater._Print  # pylint: disable=protected-access
    self.maxDiff = None  # pylint: disable=invalid-name
    tf = tempfile.NamedTemporaryFile(
      prefix='tmppyatdluiimmaculater_test', delete=False)
    FLAGS.database_filename = tf.name
    tf.close()
    self.saved_decompress = zlib.decompress

  def tearDown(self):
    zlib.decompress = self.saved_decompress
    time.time = self.saved_time
    immaculater._Input = self.saved_input  # pylint: disable=protected-access
    immaculater._Print = self.saved_print  # pylint: disable=protected-access
    try:
      os.remove(FLAGS.database_filename)
    except OSError:
      pass

  def helpTest(self, inputs, golden_outputs):
    """Feeds the inputs to the beast and verifies that the output
    matches the golden output.

    Args:
      inputs: [basestring]
      golden_outputs: [basestring]
    """
    inputs = copy.copy(inputs)

    def MyRawInput(unused_prompt=''):  # pylint: disable=unused-argument
      if not inputs:
        raise EOFError('immaculater_test1')
      return inputs.pop(0)

    printed = []

    def MyPrint(s):
      printed.append(unicode(s))

    immaculater._Input = MyRawInput  # pylint: disable=protected-access
    immaculater._Print = MyPrint  # pylint: disable=protected-access

    def HTMLEscaper(s):
      return s.replace('&nbsp;', '&amp;nbsp;')

    immaculater.MutateToDoListLoop(self.todolist, html_escaper=HTMLEscaper)
    self._AssertEqualWithDiff(golden_outputs, printed)

  def testBase64RandomSlug(self):
    random.seed(37)
    self.assertEqual(immaculater.Base64RandomSlug(64), "rpsX756q178")
    self.assertEqual(immaculater.Base64RandomSlug(64), "1aKDCaH7XnA")
    self.assertEqual(immaculater.Base64RandomSlug(64), "h8ob-650mcs")  # url-safe
    self.assertEqual(immaculater.Base64RandomSlug(8), "SA")

  def testBatchMode(self):
    FLAGS.pyatdl_show_uid = True
    printed = []

    def MyPrint(s):
      printed.append(str(s))

    FLAGS.pyatdl_paranoia = True
    FLAGS.pyatdl_allow_command_line_comments = False
    v0 = r"""
      reset --annihilate
      mkprj Pbatch0
      mkprj Pbatch1
      mkctx Cbatch0
      lsctx
      echo after lsctx before pwd:
      pwd
      echo after pwd; ls -a: # This is a POSIX-style comment
      ls -a"""
    immaculater.ApplyBatchOfCommands(open(_CreateTmpFile(v0)), MyPrint)
    self.assertEqual(
      ['Reset complete.',
       "--context-- uid=0 ---active--- '<none>'",
       '--context-- uid=6 ---active--- Cbatch0',
       'after lsctx before pwd:',
       '/',
       'after pwd; ls -a: # This is a POSIX-style comment',
       '--folder--- uid=2 .',
       '--folder--- uid=2 ..',
       '--project-- uid=1 --incomplete-- ---active--- inbox',
       '--project-- uid=4 --incomplete-- ---active--- Pbatch0',
       '--project-- uid=5 --incomplete-- ---active--- Pbatch1'],
      printed)
    del printed[:]
    FLAGS.pyatdl_allow_command_line_comments = True
    immaculater.ApplyBatchOfCommands(open(_CreateTmpFile(v0)), MyPrint)
    self.assertEqual(
      ['Reset complete.',
       "--context-- uid=0 ---active--- '<none>'",
       '--context-- uid=6 ---active--- Cbatch0',
       'after lsctx before pwd:',
       '/',
       'after pwd; ls -a:',
       '--folder--- uid=2 .',
       '--folder--- uid=2 ..',
       '--project-- uid=1 --incomplete-- ---active--- inbox',
       '--project-- uid=4 --incomplete-- ---active--- Pbatch0',
       '--project-- uid=5 --incomplete-- ---active--- Pbatch1'],
      printed)
    del printed[:]

    # Now apply a different batch without resetting the DB.
    assert not printed
    uid.singleton_factory = uid.Factory()
    immaculater.ApplyBatchOfCommands(open(_CreateTmpFile(r"""
      mkprj Pbatch2
      lsctx
      ls -a""")), MyPrint)
    self.assertEqual(
      ['--context-- uid=0 ---active--- \'<none>\'',
       '--context-- uid=6 ---active--- Cbatch0',
       '--folder--- uid=2 .',
       '--folder--- uid=2 ..',
       '--project-- uid=1 --incomplete-- ---active--- inbox',
       '--project-- uid=4 --incomplete-- ---active--- Pbatch0',
       '--project-- uid=5 --incomplete-- ---active--- Pbatch1',
       '--project-- uid=7 --incomplete-- ---active--- Pbatch2'],
      printed)
    del printed[:]

  def testSerializationAndDeserialization(self):
    printed = []

    def MyPrint(s):
      printed.append(str(s))

    immaculater._Print = MyPrint  # pylint: disable=protected-access

    immaculater.ApplyBatchOfCommands(open(_CreateTmpFile(r"""
reset --annihilate
mkdir F0
cd F0
mkdir F00
cd F00
mkprj PF00
cd PF00
touch actionF00
mkctx C0
chctx C0 actionF00
touch action2F00
cd /
mkdir F1
cd F1
mkprj PF1
cd PF1
cd /
mkprj Ptop0
cd Ptop0
touch action0Ptop0
touch action1Ptop0
mkctx C1
deactivatectx C1
chctx C1 action1Ptop0
cd /
mkprj Ptop1
configurereview --max_seconds_before_review=86401 Ptop1
dump""")))

    gold = r"""<todolist>
    <inbox>
        <project is_deleted="False" is_complete="False" is_active="True" name="inbox">
        
        </project>
    </inbox>
    <folder is_deleted="False" name="">
        <folder is_deleted="False" name="F0">
            <folder is_deleted="False" name="F00">
                <project is_deleted="False" is_complete="False" is_active="True" name="PF00">
                    <action is_deleted="False" is_complete="False" name="actionF00" ctx="uid=8"/>
                    <action is_deleted="False" is_complete="False" name="action2F00" ctx=""/>
                </project>
            </folder>
        </folder>
        <folder is_deleted="False" name="F1">
            <project is_deleted="False" is_complete="False" is_active="True" name="PF1">
            
            </project>
        </folder>
        <project is_deleted="False" is_complete="False" is_active="True" name="Ptop0">
            <action is_deleted="False" is_complete="False" name="action0Ptop0" ctx=""/>
            <action is_deleted="False" is_complete="False" name="action1Ptop0" ctx="uid=15"/>
        </project>
        <project is_deleted="False" is_complete="False" is_active="True" max_seconds_before_review="86401.0" name="Ptop1">
        
        </project>
    </folder>
    <contexts>
        <context_list is_deleted="False" name="Contexts">
            <context is_deleted="False" is_active="True" name="C0"/>
            <context is_deleted="False" is_active="False" name="C1"/>
        </context_list>
    </contexts>
</todolist>"""

    self._AssertEqualWithDiff(gold, printed[-1])

    self.assertEqual(
      ['Reset complete.', gold],
      printed)
    del printed[:]

    # Now apply a different batch without resetting the DB. Tests
    # deserialization.
    assert not printed
    immaculater.ApplyBatchOfCommands(open(_CreateTmpFile(r"""
      dump""")))
    self._AssertEqualWithDiff(
      [gold],
      printed)
    del printed[:]

    # Now poison decompression by making it a NOP. Tests
    # that deserialization was using decompression.
    #
    # pylint: disable=unused-argument
    def MyPoisonedDecompress(x, wbits=None, bufsize=None):
      return x

    zlib.decompress = MyPoisonedDecompress
    try:
      immaculater.ApplyBatchOfCommands(open(_CreateTmpFile(r"""
        dump""")))
    except message.DecodeError:
      pass
    else:
      raise AssertionError('Poisoning decompression did not cause a failure.')

    # Unpoison it.
    zlib.decompress = self.saved_decompress
    del printed[:]
    immaculater.ApplyBatchOfCommands(open(_CreateTmpFile(r"""
      dump""")))
    self._AssertEqualWithDiff(
      [gold],
      printed)

    # Now deserialize and then serialize without compression.
    FLAGS.pyatdl_zlib_compression_level = 0
    del printed[:]
    immaculater.ApplyBatchOfCommands(open(_CreateTmpFile(r"""
      dump""")))
    self._AssertEqualWithDiff(
      [gold],
      printed)
    # Now go back to compressing. Can we deserialize an uncompressed payload?
    FLAGS.pyatdl_zlib_compression_level = 6
    del printed[:]
    immaculater.ApplyBatchOfCommands(open(_CreateTmpFile(r"""
      dump""")))
    self._AssertEqualWithDiff(
      [gold],
      printed)

  def testEcholines(self):
    inputs = ['echo echoa,b,c',
              'echolines TT a,b,c',
              'echolines UU a, b, c',
              'echolines YY a b c',
              'echolines ZZa,b,c,,',
              'echolines QQa,b,c,, ',
              'echolines PPa,b,c,, ,',
              'echolines ,xx,yy',
              ]
    golden_printed = [
      'echoa,b,c',
      'TT',
      'a,b,c',
      'UU',
      'a,',
      'b,',
      'c',
      'YY',
      'a',
      'b',
      'c',
      'ZZa,b,c,,',
      'QQa,b,c,,',
      'PPa,b,c,,',
      ',',
      ',xx,yy',
      ]
    self.helpTest(inputs, golden_printed)

  def testLsContextOfActionAfterDeserialization(self):
    save_path = _CreateTmpFile('')
    inputs = ['mkctx @home',
              'mkact -c @home /inbox/a',
              'echo ls before save:',
              'ls -R',
              'save %s' % pipes.quote(save_path),
              'load %s' % pipes.quote(save_path),
              'echo ls after save:',
              'ls -R',
              ]
    golden_printed = [
      'ls before save:',
      '--project-- --incomplete-- ---active--- inbox',
      '',
      './inbox:',
      '--action--- --incomplete-- a --in-context-- @home',
      'Save complete.',
      'Load complete.',
      'ls after save:',
      '--project-- --incomplete-- ---active--- inbox',
      '',
      './inbox:',
      '--action--- --incomplete-- a --in-context-- @home',
      ]
    self.helpTest(inputs, golden_printed)

  def testSortingInctx(self):
    inputs = ['mkctx a',
              'mkact -c a /inbox/1',
              'mkprj /p',
              'mkact -c a /p/2',
              'mkact -c a /inbox/3',
              'echo sorting naturally:',
              'inctx a',  
              'echo sorting by uid:',
              'inctx --sort_by uid a',
              ]
    golden_printed = [
      "sorting naturally:",
      "--action--- --incomplete-- 1",
      "--action--- --incomplete-- 3",
      "--action--- --incomplete-- 2",
      "sorting by uid:",
      "--action--- --incomplete-- 1",
      "--action--- --incomplete-- 2",
      "--action--- --incomplete-- 3",
      ]
    self.helpTest(inputs, golden_printed)

  def testChctxRememberTheMilk(self):
    inputs = ['reset --annihilate',
              'cd /inbox',
              'mkctx 652',
              'touch "remember the milk"',
              'ls',
              "chctx 652 'remember the milk'",
              'ls',
              ]
    golden_printed = [
      'Reset complete.',
      "--action--- --incomplete-- 'remember the milk' --in-context-- '<none>'",
      "--action--- --incomplete-- 'remember the milk' --in-context-- 652",
      ]
    self.helpTest(inputs, golden_printed)

  def testLsctxJson(self):
    save_path = _CreateTmpFile('')
    inputs = ['chclock 1137',
              'reset --annihilate',
              'cd /inbox',
              'lsctx --json',
              'echo after len==0',
              'mkctx 653',
              'lsctx --json',
              'echo after len==1',
              'mkctx "at 654}]"',
              'save %s' % pipes.quote(save_path),
              'load %s' % pipes.quote(save_path),
              'lsctx --json',
              'echo after len==2',
              'lsctx --json 0 1',
              u'lsctx --json \u2019til 1',
              'echo after too many args',
              'lsctx --json 653',
              'echo after --json 653',
              'lsctx 653',
              'echo after 653',
              'lsctx --json <none>',
              'echo after --json <none>',
              ]
    golden_printed = [
      'Reset complete.',
      '[{"ctime":0,"dtime":null,"is_active":true,"is_complete":false,"is_deleted":false,"mtime":0,"name":"<none>","number_of_items":0,"uid":0}]',
      'after len==0',
      '[{"ctime":0,"dtime":null,"is_active":true,"is_complete":false,"is_deleted":false,"mtime":0,"name":"<none>","number_of_items":0,"uid":0},{"ctime":1137.0,"dtime":null,"is_active":true,"is_complete":false,"is_deleted":false,"mtime":1137.0,"name":"653","number_of_items":0,"uid":4}]',
      'after len==1',
      'Save complete.',
      'Load complete.',
      '[{"ctime":0,"dtime":null,"is_active":true,"is_complete":false,"is_deleted":false,"mtime":0,"name":"<none>","number_of_items":0,"uid":0},{"ctime":1137.0,"dtime":null,"is_active":true,"is_complete":false,"is_deleted":false,"mtime":1137.0,"name":"653","number_of_items":0,"uid":4},{"ctime":1137.0,"dtime":null,"is_active":true,"is_complete":false,"is_deleted":false,"mtime":1137.0,"name":"at 654}]","number_of_items":0,"uid":5}]',
      'after len==2',
      'Takes zero or one arguments; found these arguments: [u\'0\', u\'1\']',
      'Takes zero or one arguments; found these arguments: [u\'\u2019til\', u\'1\']',
      'after too many args',
      '{"ctime":1137.0,"dtime":null,"is_active":true,"is_complete":false,"is_deleted":false,"mtime":1137.0,"name":"653","number_of_items":0,"uid":4}',
      'after --json 653',
      '--context-- ---active--- 653',
      'after 653',
      'No such Context "<none>"',
      'after --json <none>',
      ]
    self.helpTest(inputs, golden_printed)

  def testBuyOatmealAtTheStore(self):
    inputs = ['chclock 1337',
              'seed',
              'mkact "/inbox/buy oatmeal @the store"',
              'echo ls:',
              'ls -R',
              ]
    golden_printed = [
      'ls:',
      '--project-- --incomplete-- ---active--- inbox',
      '--project-- --incomplete-- ---active--- miscellaneous',
      '--project-- --incomplete-- ---active--- \'learn how to use this to-do list\'',
      '',
      './inbox:',
      '--action--- --incomplete-- \'buy oatmeal @the store\' --in-context-- \'@the store\'',
      '',
      './miscellaneous:',
      '',
      './learn how to use this to-do list:',
      '--action--- --incomplete-- \'Watch the video on the "Help" page -- on the top navigation bar, find it underneath the "Other" drop-down\' --in-context-- \'<none>\'',
      '--action--- --incomplete-- \'Read the book "Getting Things Done" by David Allen\' --in-context-- \'<none>\'',
      '--action--- --incomplete-- \'After reading the book, try out a Weekly Review -- on the top navigation bar, find it underneath the "Other" drop-down\' --in-context-- \'<none>\'',
      ]
    self.helpTest(inputs, golden_printed)

  def testLsactJson(self):
    inputs = ['chclock 1137',
              'reset --annihilate',
              'cd /inbox',
              'lsact uid=1',
              'echo after --nojson not-an-action',
              'lsact --json uid=1',
              'echo after --json not-an-action',
              'lsact --json',
              'echo after no args',
              'mkact "a 0"',
              'lsact --json uid=4',
              'echo after --json uid=4',
              'lsact --json "/inbox/a 0"',
              'echo after --json /inbox/a 0',
              'mkctx c0',
              'chctx c0 uid=4',
              'lsact --json uid=4',
              'echo after --json uid=4 chctx c0',
              'mkdir /D0',
              'mkprj /D0/P0',
              'echo before mv uid=4',
              'mv uid=4 /D0/P0',
              'mv uid=4 uid=1',  # -> /inbox
              'echo after mv uid=4',
              'mv "/inbox/a 0" /D0/P0',
              'lsact --json uid=4',
              'echo after --json uid=4 chctx c0 /D0/P0',
              'cd /',
              'lsact --json uid=4',
              'echo after running from root',
              ]
    golden_printed = [
      'Reset complete.',
      '--json is required; see "help ls" and consider using "ls -a"',
      'after --nojson not-an-action',
      'No Action with UID 1 exists.',
      'after --json not-an-action',
      'Needs a single positional argument; found none',
      'after no args',
      '{"ctime":1137.0,"display_project_path":"inbox","dtime":null,"in_context":"<none>","in_context_uid":null,"is_complete":false,"is_deleted":false,"mtime":1137.0,"name":"a 0","number_of_items":1,"project_path":"/inbox","project_uid":1,"uid":4}',
      'after --json uid=4',
      '{"ctime":1137.0,"display_project_path":"inbox","dtime":null,"in_context":"<none>","in_context_uid":null,"is_complete":false,"is_deleted":false,"mtime":1137.0,"name":"a 0","number_of_items":1,"project_path":"/inbox","project_uid":1,"uid":4}',
      'after --json /inbox/a 0',
      '{"ctime":1137.0,"display_project_path":"inbox","dtime":null,"in_context":"c0","in_context_uid":5,"is_complete":false,"is_deleted":false,"mtime":1137.0,"name":"a 0","number_of_items":1,"project_path":"/inbox","project_uid":1,"uid":4}',
      'after --json uid=4 chctx c0',
      'before mv uid=4',
      'after mv uid=4',
      '{"ctime":1137.0,"display_project_path":"D0/P0","dtime":null,"in_context":"c0","in_context_uid":5,"is_complete":false,"is_deleted":false,"mtime":1137.0,"name":"a 0","number_of_items":1,"project_path":"/D0/P0","project_uid":7,"uid":4}',
      'after --json uid=4 chctx c0 /D0/P0',
      '{"ctime":1137.0,"display_project_path":"D0/P0","dtime":null,"in_context":"c0","in_context_uid":5,"is_complete":false,"is_deleted":false,"mtime":1137.0,"name":"a 0","number_of_items":1,"project_path":"/D0/P0","project_uid":7,"uid":4}',
      'after running from root',
      ]
    self.helpTest(inputs, golden_printed)

  def testMkactContext(self):
    FLAGS.pyatdl_show_uid = True
    inputs = ['chclock 1137',
              'reset --annihilate',
              'cd /inbox',
              'mkact --context uid=0 "buy the milk"',
              'echo ls',
              'ls',
              'mkctx c0',
              'echo lsctx',
              'lsctx',
              'mkact --context uid=999 "nonexistent context"',
              'mkact --context uid=5 "buy the milk"',
              'mkact -c c0 "buy eggs"',
              'echo ls',
              'ls',
              ]
    golden_printed = [
      'Reset complete.',
      'ls',
      '--action--- uid=4 --incomplete-- \'buy the milk\' --in-context-- \'<none>\'',
      'lsctx',
      "--context-- uid=0 ---active--- '<none>'",
      '--context-- uid=5 ---active--- c0',
      'No such Context "uid=999"',
      'ls',
      '--action--- uid=4 --incomplete-- \'buy the milk\' --in-context-- \'<none>\'',
      '--action--- uid=6 --incomplete-- \'buy the milk\' --in-context-- c0',
      '--action--- uid=7 --incomplete-- \'buy eggs\' --in-context-- c0',
      ]
    self.helpTest(inputs, golden_printed)

  def testInctxJson(self):
    inputs = ['chclock 1137',
              'reset --annihilate',
              'cd /inbox',
              'mkctx 655',
              'mkact -c uid=0 a0_655',
              'mkact -c uid=0 a1_655',
              'inctx --json 655',
              'echo after null',
              'inctx --json <none>',
              'echo after 2',
              'chctx 655 a0_655',
              'inctx --json 655',
              'echo after len==1',
              'chctx 655 a1_655',
              'inctx --json 655',
              'echo after len==2',
              ]
    golden_printed = [
      'Reset complete.',
      '[]',
      'after null',
      '[{"ctime":1137.0,"dtime":null,"in_context":"<none>","in_context_uid":null,"in_prj":"inbox","is_complete":false,"is_deleted":false,"mtime":1137.0,"name":"a0_655","number_of_items":1,"uid":5},{"ctime":1137.0,"dtime":null,"in_context":"<none>","in_context_uid":null,"in_prj":"inbox","is_complete":false,"is_deleted":false,"mtime":1137.0,"name":"a1_655","number_of_items":1,"uid":6}]',
      'after 2',
      '[{"ctime":1137.0,"dtime":null,"in_context":"655","in_context_uid":4,"in_prj":"inbox","is_complete":false,"is_deleted":false,"mtime":1137.0,"name":"a0_655","number_of_items":1,"uid":5}]',
      'after len==1',
      '[{"ctime":1137.0,"dtime":null,"in_context":"655","in_context_uid":4,"in_prj":"inbox","is_complete":false,"is_deleted":false,"mtime":1137.0,"name":"a0_655","number_of_items":1,"uid":5},{"ctime":1137.0,"dtime":null,"in_context":"655","in_context_uid":4,"in_prj":"inbox","is_complete":false,"is_deleted":false,"mtime":1137.0,"name":"a1_655","number_of_items":1,"uid":6}]',
      'after len==2',
      ]
    self.helpTest(inputs, golden_printed)

  def testLsprjJson(self):
    inputs = ['chclock 1137',
              'reset --annihilate',
              'lsprj',
              'echo after nothing but inbox default',
              'lsprj --json',
              'echo after nothing but inbox --json',
              'lsprj --nojson',
              'echo after nothing but inbox --nojson',
              'mkprj "p 0"',
              'mkprj "p1"',
              'mkdir dir0',
              'cd dir0',
              'mkprj p2_in_dir0',
              'lsprj --json',
              'echo after several --json',
              'lsprj',
              'echo after several --nojson',
              'lsprj a b',
              'echo after two args',
              'lsprj uid=1',
              'echo after uid=1',
              'lsprj --json uid=1',
              'echo after --json uid=1',
              'lsprj --json /inbox',
              'echo after --json /inbox',
              'cd /dir0',
              'lsprj --json p2_in_dir0',
              'echo after --json p2_in_dir0',
              ]
    golden_printed = [
      'Reset complete.',
      '/inbox',
      'after nothing but inbox default',
      '[{"ctime":1137.0,"default_context_uid":0,"dtime":null,"is_active":true,"is_complete":false,"is_deleted":false,"mtime":1137.0,"name":"inbox","needsreview":false,"number_of_items":0,"path":"/","uid":1}]',
      'after nothing but inbox --json',
      '/inbox',
      'after nothing but inbox --nojson',
      '[{"ctime":1137.0,"default_context_uid":0,"dtime":null,"is_active":true,"is_complete":false,"is_deleted":false,"mtime":1137.0,"name":"inbox","needsreview":false,"number_of_items":0,"path":"/","uid":1},{"ctime":1137.0,"default_context_uid":0,"dtime":null,"is_active":true,"is_complete":false,"is_deleted":false,"mtime":1137.0,"name":"p 0","needsreview":false,"number_of_items":0,"path":"/","uid":4},{"ctime":1137.0,"default_context_uid":0,"dtime":null,"is_active":true,"is_complete":false,"is_deleted":false,"mtime":1137.0,"name":"p1","needsreview":false,"number_of_items":0,"path":"/","uid":5},{"ctime":1137.0,"default_context_uid":0,"dtime":null,"is_active":true,"is_complete":false,"is_deleted":false,"mtime":1137.0,"name":"p2_in_dir0","needsreview":false,"number_of_items":0,"path":"/dir0","uid":7}]',
      'after several --json',
      '/inbox',
      '/p 0',
      '/p1',
      '/dir0/p2_in_dir0',
      'after several --nojson',
      'Takes zero or one arguments; found these arguments: [u\'a\', u\'b\']',
      'after two args',
      'With an argument, --json is required',
      'after uid=1',
      '{"ctime":1137.0,"default_context_uid":0,"dtime":null,"is_active":true,"is_complete":false,"is_deleted":false,"max_seconds_before_review":604800.0,"mtime":1137.0,"name":"inbox","needsreview":false,"number_of_items":0,"parent_path":"/","uid":1}',
      'after --json uid=1',
      '{"ctime":1137.0,"default_context_uid":0,"dtime":null,"is_active":true,"is_complete":false,"is_deleted":false,"max_seconds_before_review":604800.0,"mtime":1137.0,"name":"inbox","needsreview":false,"number_of_items":0,"parent_path":"/","uid":1}',
      'after --json /inbox',
      '{"ctime":1137.0,"default_context_uid":0,"dtime":null,"is_active":true,"is_complete":false,"is_deleted":false,"max_seconds_before_review":604800.0,"mtime":1137.0,"name":"p2_in_dir0","needsreview":false,"number_of_items":0,"parent_path":"/dir0","uid":7}',
      'after --json p2_in_dir0',
      ]
    self.helpTest(inputs, golden_printed)

  def testChctxUid0(self):
    inputs = ['mkctx @home',
              'mkact /inbox/a',
              'chctx @home /inbox/a',
              'echo ls',
              'ls /inbox',
              'chctx uid=0 /inbox/a',
              'echo ls now',
              'ls /inbox',
              ]
    golden_printed = [
      'ls',
      '--action--- --incomplete-- a --in-context-- @home',
      'ls now',
      '--action--- --incomplete-- a --in-context-- \'<none>\'',
      ]
    self.helpTest(inputs, golden_printed)

  def testInprjJson(self):
    FLAGS.pyatdl_show_uid = True
    inputs = ['chclock 1137',
              'reset --annihilate',
              'inprj',
              'echo after no args',
              'inprj --json',
              'echo after --json but no args',
              'inprj --json uid=1',
              'echo after --json inbox',
              'mkprj p0',
              'mkprj p1',
              'cd p1',
              'mkact a0_in_p1',
              'cd ..',
              'mkdir dir0',
              'cd dir0',
              'mkprj p2_in_dir0',
              'cd p2_in_dir0',
              'mkact a0_in_p2_in_dir0',
              'mkact a1_in_p2_in_dir0',
              'ls -R /',
              'echo after ls',
              'inprj --json uid=4',
              'echo after uid=4 p0',
              'inprj --json uid=5',
              'echo after uid=5 p1',
              'inprj --json /dir0/p2_in_dir0',
              'echo after uid=8 p2_in_dir0',
              'inprj /dir0/p2_in_dir0',
              'echo after uid=8 p2_in_dir0 --nojson',
              ]
    golden_printed = [
      'Reset complete.',
      'Needs a single positional argument; found none',
      'after no args',
      'Needs a single positional argument; found none',
      'after --json but no args',
      '[]',
      'after --json inbox',
      '--project-- uid=1 --incomplete-- ---active--- inbox',
      '--project-- uid=4 --incomplete-- ---active--- p0',
      '--project-- uid=5 --incomplete-- ---active--- p1',
      '--folder--- uid=7 dir0',
      '',
      '/inbox:',
      '',
      '/p0:',
      '',
      '/p1:',
      '--action--- uid=6 --incomplete-- a0_in_p1 --in-context-- \'<none>\'',
      '',
      '/dir0:',
      '--project-- uid=8 --incomplete-- ---active--- p2_in_dir0',
      '',
      '/dir0/p2_in_dir0:',
      '--action--- uid=9 --incomplete-- a0_in_p2_in_dir0 --in-context-- \'<none>\'',
      '--action--- uid=10 --incomplete-- a1_in_p2_in_dir0 --in-context-- \'<none>\'',
      'after ls',
      '[]',
      'after uid=4 p0',
      '[{"ctime":1137.0,"dtime":null,"in_context":"<none>","in_context_uid":null,"is_complete":false,"is_deleted":false,"mtime":1137.0,"name":"a0_in_p1","number_of_items":1,"uid":6}]',
      'after uid=5 p1',
      '[{"ctime":1137.0,"dtime":null,"in_context":"<none>","in_context_uid":null,"is_complete":false,"is_deleted":false,"mtime":1137.0,"name":"a0_in_p2_in_dir0","number_of_items":1,"uid":9},{"ctime":1137.0,"dtime":null,"in_context":"<none>","in_context_uid":null,"is_complete":false,"is_deleted":false,"mtime":1137.0,"name":"a1_in_p2_in_dir0","number_of_items":1,"uid":10}]',
      'after uid=8 p2_in_dir0',
      '--action--- uid=9 --incomplete-- a0_in_p2_in_dir0 --in-context-- \'<none>\'',
      '--action--- uid=10 --incomplete-- a1_in_p2_in_dir0 --in-context-- \'<none>\'',
      'after uid=8 p2_in_dir0 --nojson',
      ]
    self.helpTest(inputs, golden_printed)

  def testInprjViewFilters(self):
    inputs = ['chclock 1137',
              'inprj /inbox',
              'echo after empty',
              'mkact /inbox/normal',
              'mkact /inbox/completed',
              'complete /inbox/completed',
              'mkact /inbox/deleted',
              'rmact /inbox/deleted',
              'echo inprj default view',
              'inprj /inbox',
              'view all_even_deleted',
              'echo inprj all_even_deleted',
              'inprj /inbox',
              'view actionable',
              'echo inprj actionable',
              'inprj /inbox',
              ]
    golden_printed = [
      'after empty',
      'inprj default view',
      '--action--- --incomplete-- normal --in-context-- \'<none>\'',
      '--action--- ---COMPLETE--- completed --in-context-- \'<none>\'',
      'inprj all_even_deleted',
      '--action--- --incomplete-- normal --in-context-- \'<none>\'',
      '--action--- ---COMPLETE--- completed --in-context-- \'<none>\'',
      '--action--- --DELETED-- --incomplete-- deleted --in-context-- \'<none>\'',
      'inprj actionable',
      '--action--- --incomplete-- normal --in-context-- \'<none>\'',
      ]
    self.helpTest(inputs, golden_printed)

  def testMv(self):
    FLAGS.pyatdl_show_uid = True
    save_path = _CreateTmpFile('')
    inputs = ['chclock 1137',
              'reset --annihilate',
              'mv /inbox /',
              'echo after mv /inbox /, a NOP',
              'mv / /inbox',
              'echo after mv / /inbox',
              'mv / /',
              'echo after mv / /, an error',
              'mkprj p0',
              'mkprj p1',
              'cd p1',
              'mkact a0_in_p1',
              'cd ..',
              'mkdir dir0',
              'cd dir0',
              'mkprj p2_in_dir0',
              'cd p2_in_dir0',
              'mkact a0_in_p2_in_dir0',
              'mkact a1_in_p2_in_dir0',
              'ls -R /',
              'echo after ls',
              'mv /p0 /',
              'ls -R /',
              'echo after mv /p0 /, a NOP',
              'mv /dir0/p2_in_dir0 /',
              'ls -R /',
              'echo after mv /dir0/p2_in_dir0 /',
              'mv / /dir0',
              'echo after mv / /dir0, an error',
              'mv /p1/a0_in_p1 /',
              'echo after mv /p1/a0_in_p1 /, an error',
              'mv /p1/a0_in_p1 /dir0',
              'echo after mv /p1/a0_in_p1 /dir0, an error',
              'mv /p1/a0_in_p1 /p1/a0_in_p1',
              'echo after mv /p1/a0_in_p1 /p1/a0_in_p1, an error',
              'mv /p1/a0_in_p1 /inbox',
              'ls -R /',
              'echo after mv /p1/a0_in_p1 /inbox',
              'mv /p1/a0_in_p1 /inbox',
              'echo after mv /p1/a0_in_p1 /inbox second time, an error',
              'mv /inbox /',
              'ls /',
              'echo after mv /inbox /, a NOP',
              'mv /inbox /inbox',
              'echo after mv /inbox /inbox, an error',
              'mv /inbox /ThisIsMvNotRename',
              'echo after mv /inbox /ThisIsMvNotRename, an error',
              'mv /inbox /dir0',
              'echo after mv /inbox /dir0, an error',
              'mv /inbox/a0_in_p1 /p1',
              'ls -R /',
              'echo after mv /inbox/a0_in_p1 /p1',
              'cd /',
              'mkdir dir1',
              'mkdir dir2',
              'cd dir1',
              'mkdir dir3',
              'mv dir3 ../dir2',
              'ls -R /',
              'echo after mv dir3 ../dir2',
              'cd /dir2/dir3',
              'mv ../../dir2/dir3 /',
              'ls -R /',
              'echo after moving dir3 into /',
              'pwd',
              'echo after pwd inside /dir3 formerly /dir2/dir3',
              'mv /dir2 /p1',
              'mv /dir2 /p1/a0_in_p1',
              'echo after two errors',
              'mv /dir0 /dir0',
              'echo after /dir0 /dir0 err',
              'mv /p0 /p0',
              'echo after /p0 /p0 err',
              'cd /',
              'mv .. /',
              'echo after cd /&&mv .. /',
              'mv . /dir3',
              'echo after cd /&&mv . /dir3',
              'mv /p1/a0_in_p1 /dir3',
              'echo after mv /p1/a0_in_p1 /dir3',
              'mv /p1/a0_in_p1 /p1',
              'ls -R /p1',
              'echo /p1 after a0_in_p1 NOP',
              'mv /p1/a0_in_p1 /p2_in_dir0',
              'cd /',
              'rmprj p1',
              'ls -R /',
              'echo after mv a0_in_p1 /p2_in_dir0 and rmprj p1',
              'cd /p2_in_dir0',
              'mv ./a0_in_p1 ../p1',
              'ls /p1',
              'echo after ls /p1 after trying to move a0_in_p1 into it',
              'cd /dir3',
              'mv . /dir0',
              'pwd',
              'echo AFTER pwd /dir0/dir3',
              'cd /dir0/dir3',
              'mv ./.././../dir2 .',
              'save %s' % pipes.quote(save_path),
              'load %s' % pipes.quote(save_path),
              'cd /dir0/dir3',
              'ls -R /',
              'echo AFTER moving dir2 into dir3',
              'mkctx c0',
              'mv c0 /dir1',
              'echo AFTER mv c0 /dir1',
              ]
    golden_printed = [
      'Reset complete.',
      'after mv /inbox /, a NOP',
      'First argument is a Folder, but second argument is not a Folder',
      'after mv / /inbox',
      'Cannot move the root Folder \'/\'',
      'after mv / /, an error',
      '--project-- uid=1 --incomplete-- ---active--- inbox',
      '--project-- uid=4 --incomplete-- ---active--- p0',
      '--project-- uid=5 --incomplete-- ---active--- p1',
      '--folder--- uid=7 dir0',
      '',
      '/inbox:',
      '',
      '/p0:',
      '',
      '/p1:',
      '--action--- uid=6 --incomplete-- a0_in_p1 --in-context-- \'<none>\'',
      '',
      '/dir0:',
      '--project-- uid=8 --incomplete-- ---active--- p2_in_dir0',
      '',
      '/dir0/p2_in_dir0:',
      '--action--- uid=9 --incomplete-- a0_in_p2_in_dir0 --in-context-- \'<none>\'',
      '--action--- uid=10 --incomplete-- a1_in_p2_in_dir0 --in-context-- \'<none>\'',
      'after ls',
      '--project-- uid=1 --incomplete-- ---active--- inbox',
      '--project-- uid=4 --incomplete-- ---active--- p0',
      '--project-- uid=5 --incomplete-- ---active--- p1',
      '--folder--- uid=7 dir0',
      '',
      '/inbox:',
      '',
      '/p0:',
      '',
      '/p1:',
      '--action--- uid=6 --incomplete-- a0_in_p1 --in-context-- \'<none>\'',
      '',
      '/dir0:',
      '--project-- uid=8 --incomplete-- ---active--- p2_in_dir0',
      '',
      '/dir0/p2_in_dir0:',
      '--action--- uid=9 --incomplete-- a0_in_p2_in_dir0 --in-context-- \'<none>\'',
      '--action--- uid=10 --incomplete-- a1_in_p2_in_dir0 --in-context-- \'<none>\'',
      'after mv /p0 /, a NOP',
      '--project-- uid=1 --incomplete-- ---active--- inbox',
      '--project-- uid=4 --incomplete-- ---active--- p0',
      '--project-- uid=5 --incomplete-- ---active--- p1',
      '--folder--- uid=7 dir0',
      '--project-- uid=8 --incomplete-- ---active--- p2_in_dir0',
      '',
      '/inbox:',
      '',
      '/p0:',
      '',
      '/p1:',
      '--action--- uid=6 --incomplete-- a0_in_p1 --in-context-- \'<none>\'',
      '',
      '/dir0:',
      '',
      '/p2_in_dir0:',
      '--action--- uid=9 --incomplete-- a0_in_p2_in_dir0 --in-context-- \'<none>\'',
      '--action--- uid=10 --incomplete-- a1_in_p2_in_dir0 --in-context-- \'<none>\'',
      'after mv /dir0/p2_in_dir0 /',
      'Cannot move the root Folder \'/\'',
      'after mv / /dir0, an error',
      'First argument is an Action, but second argument is not a Project',
      'after mv /p1/a0_in_p1 /, an error',
      'First argument is an Action, but second argument is not a Project',
      'after mv /p1/a0_in_p1 /dir0, an error',
      'First argument is an Action, but second argument is not a Project',
      'after mv /p1/a0_in_p1 /p1/a0_in_p1, an error',
      '--project-- uid=1 --incomplete-- ---active--- inbox',
      '--project-- uid=4 --incomplete-- ---active--- p0',
      '--project-- uid=5 --incomplete-- ---active--- p1',
      '--folder--- uid=7 dir0',
      '--project-- uid=8 --incomplete-- ---active--- p2_in_dir0',
      '',
      '/inbox:',
      '--action--- uid=6 --incomplete-- a0_in_p1 --in-context-- \'<none>\'',
      '',
      '/p0:',
      '',
      '/p1:',
      '',
      '/dir0:',
      '',
      '/p2_in_dir0:',
      '--action--- uid=9 --incomplete-- a0_in_p2_in_dir0 --in-context-- \'<none>\'',
      '--action--- uid=10 --incomplete-- a1_in_p2_in_dir0 --in-context-- \'<none>\'',
      'after mv /p1/a0_in_p1 /inbox',
      """With current working Folder/Project "/p2_in_dir0", there is no such child "a0_in_p1".  Choices:
    ..
""",
      'after mv /p1/a0_in_p1 /inbox second time, an error',
      '--project-- uid=1 --incomplete-- ---active--- inbox',
      '--project-- uid=4 --incomplete-- ---active--- p0',
      '--project-- uid=5 --incomplete-- ---active--- p1',
      '--folder--- uid=7 dir0',
      '--project-- uid=8 --incomplete-- ---active--- p2_in_dir0',
      'after mv /inbox /, a NOP',
      'First argument is a Project, but second argument is not a Folder',
      'after mv /inbox /inbox, an error',
      """With current working Folder/Project "/p2_in_dir0", there is no such child "ThisIsMvNotRename".  Choices:
    ..
    p0
    p1
    dir0
    p2_in_dir0""",
      'after mv /inbox /ThisIsMvNotRename, an error',
      'Cannot move /inbox',
      'after mv /inbox /dir0, an error',
      '--project-- uid=1 --incomplete-- ---active--- inbox',
      '--project-- uid=4 --incomplete-- ---active--- p0',
      '--project-- uid=5 --incomplete-- ---active--- p1',
      '--folder--- uid=7 dir0',
      '--project-- uid=8 --incomplete-- ---active--- p2_in_dir0',
      '',
      '/inbox:',
      '',
      '/p0:',
      '',
      '/p1:',
      '--action--- uid=6 --incomplete-- a0_in_p1 --in-context-- \'<none>\'',
      '',
      '/dir0:',
      '',
      '/p2_in_dir0:',
      '--action--- uid=9 --incomplete-- a0_in_p2_in_dir0 --in-context-- \'<none>\'',
      '--action--- uid=10 --incomplete-- a1_in_p2_in_dir0 --in-context-- \'<none>\'',
      'after mv /inbox/a0_in_p1 /p1',
      '--project-- uid=1 --incomplete-- ---active--- inbox',
      '--project-- uid=4 --incomplete-- ---active--- p0',
      '--project-- uid=5 --incomplete-- ---active--- p1',
      '--folder--- uid=7 dir0',
      '--project-- uid=8 --incomplete-- ---active--- p2_in_dir0',
      '--folder--- uid=11 dir1',
      '--folder--- uid=12 dir2',
      '',
      '/inbox:',
      '',
      '/p0:',
      '',
      '/p1:',
      '--action--- uid=6 --incomplete-- a0_in_p1 --in-context-- \'<none>\'',
      '',
      '/dir0:',
      '',
      '/p2_in_dir0:',
      '--action--- uid=9 --incomplete-- a0_in_p2_in_dir0 --in-context-- \'<none>\'',
      '--action--- uid=10 --incomplete-- a1_in_p2_in_dir0 --in-context-- \'<none>\'',
      '',
      '/dir1:',
      '',
      '/dir2:',
      '--folder--- uid=13 dir3',
      '',
      '/dir2/dir3:',
      'after mv dir3 ../dir2',
      '--project-- uid=1 --incomplete-- ---active--- inbox',
      '--project-- uid=4 --incomplete-- ---active--- p0',
      '--project-- uid=5 --incomplete-- ---active--- p1',
      '--folder--- uid=7 dir0',
      '--project-- uid=8 --incomplete-- ---active--- p2_in_dir0',
      '--folder--- uid=11 dir1',
      '--folder--- uid=12 dir2',
      '--folder--- uid=13 dir3',
      '',
      '/inbox:',
      '',
      '/p0:',
      '',
      '/p1:',
      '--action--- uid=6 --incomplete-- a0_in_p1 --in-context-- \'<none>\'',
      '',
      '/dir0:',
      '',
      '/p2_in_dir0:',
      '--action--- uid=9 --incomplete-- a0_in_p2_in_dir0 --in-context-- \'<none>\'',
      '--action--- uid=10 --incomplete-- a1_in_p2_in_dir0 --in-context-- \'<none>\'',
      '',
      '/dir1:',
      '',
      '/dir2:',
      '',
      '/dir3:',
      'after moving dir3 into /',
      '/dir3',
      'after pwd inside /dir3 formerly /dir2/dir3',
      'First argument is a Folder, but second argument is not a Folder',
      'First argument is a Folder, but second argument is not a Folder',
      'after two errors',
      'Cannot move an item into itself.',
      'after /dir0 /dir0 err',
      'First argument is a Project, but second argument is not a Folder',
      'after /p0 /p0 err',
      'Already at the root Folder; cannot ascend.',
      'after cd /&&mv .. /',
      'Cannot move the root Folder \'/\'',
      'after cd /&&mv . /dir3',
      'First argument is an Action, but second argument is not a Project',
      'after mv /p1/a0_in_p1 /dir3',
      '--action--- uid=6 --incomplete-- a0_in_p1 --in-context-- \'<none>\'',
      '/p1 after a0_in_p1 NOP',
      '--project-- uid=1 --incomplete-- ---active--- inbox',
      '--project-- uid=4 --incomplete-- ---active--- p0',
      '--folder--- uid=7 dir0',
      '--project-- uid=8 --incomplete-- ---active--- p2_in_dir0',
      '--folder--- uid=11 dir1',
      '--folder--- uid=12 dir2',
      '--folder--- uid=13 dir3',
      '',
      '/inbox:',
      '',
      '/p0:',
      '',
      '/dir0:',
      '',
      '/p2_in_dir0:',
      '--action--- uid=9 --incomplete-- a0_in_p2_in_dir0 --in-context-- \'<none>\'',
      '--action--- uid=10 --incomplete-- a1_in_p2_in_dir0 --in-context-- \'<none>\'',
      '--action--- uid=6 --incomplete-- a0_in_p1 --in-context-- \'<none>\'',
      '',
      '/dir1:',
      '',
      '/dir2:',
      '',
      '/dir3:',
      'after mv a0_in_p1 /p2_in_dir0 and rmprj p1',
      'Cannot move an undeleted item into a deleted container.',
      'after ls /p1 after trying to move a0_in_p1 into it',
      '/dir0/dir3',
      'AFTER pwd /dir0/dir3',
      'Save complete.',
      'Load complete.',
      '--project-- uid=1 --incomplete-- ---active--- inbox',
      '--project-- uid=4 --incomplete-- ---active--- p0',
      '--folder--- uid=7 dir0',
      '--project-- uid=8 --incomplete-- ---active--- p2_in_dir0',
      '--folder--- uid=11 dir1',
      '',
      '/inbox:',
      '',
      '/p0:',
      '',
      '/dir0:',
      '--folder--- uid=13 dir3',
      '',
      '/dir0/dir3:',
      '--folder--- uid=12 dir2',
      '',
      '/dir0/dir3/dir2:',
      '',
      '/p2_in_dir0:',
      '--action--- uid=9 --incomplete-- a0_in_p2_in_dir0 --in-context-- \'<none>\'',
      '--action--- uid=10 --incomplete-- a1_in_p2_in_dir0 --in-context-- \'<none>\'',
      '--action--- uid=6 --incomplete-- a0_in_p1 --in-context-- \'<none>\'',
      '',
      '/dir1:',
      'AFTER moving dir2 into dir3',
      """With current working Folder/Project "/dir0/dir3", there is no such child "c0".  Choices:
    ..
    dir2""",
      'AFTER mv c0 /dir1',
      ]
    self.helpTest(inputs, golden_printed)

  def testMkprjInsideProjectNotFolder(self):
    inputs = ['chclock 1137',
              'reset --annihilate',
              'mkprj p0',
              'cd p0',
              'echo b4',
              'mkprj p00',
              ]
    golden_printed = [
      'Reset complete.',
      'b4',
      'The parent directory must be a Folder, not a Project.',
      ]
    self.helpTest(inputs, golden_printed)

  def testRm(self):  # 'rm' is a mere alias of 'rmact'. See also test cases
                     # using 'rmact'.
    inputs = ['chclock 11371137',
              'reset --annihilate',
              'cd /inbox',
              'touch foo',
              'touch bar',
              'view all_even_deleted',
              'echo [all_even_deleted] ls -R -l',
              'ls -R -l',
              'view all',
              'echo [all] ls -R -l',
              'ls -R -l',
              'chclock +1',
              'rm foo',
              'view all',
              'echo after rm foo [all] ls -R -l',
              'ls -R -l',
              'view all_even_deleted',
              'echo [all_even_deleted] ls -R -l',
              'ls -R -l',
              ]
    golden_printed = [
      'Reset complete.',
      '[all_even_deleted] ls -R -l',
      '--action--- mtime=1970/05/12-10:38:57 ctime=1970/05/12-10:38:57 --incomplete-- foo --in-context-- \'<none>\'',
      '--action--- mtime=1970/05/12-10:38:57 ctime=1970/05/12-10:38:57 --incomplete-- bar --in-context-- \'<none>\'',
      '[all] ls -R -l',
      '--action--- mtime=1970/05/12-10:38:57 ctime=1970/05/12-10:38:57 --incomplete-- foo --in-context-- \'<none>\'',
      '--action--- mtime=1970/05/12-10:38:57 ctime=1970/05/12-10:38:57 --incomplete-- bar --in-context-- \'<none>\'',
      'after rm foo [all] ls -R -l',
      '--action--- mtime=1970/05/12-10:38:57 ctime=1970/05/12-10:38:57 --incomplete-- bar --in-context-- \'<none>\'',
      '[all_even_deleted] ls -R -l',
      '--action--- --DELETED-- mtime=1970/05/12-10:38:58 ctime=1970/05/12-10:38:57 dtime=1970/05/12-10:38:58 --incomplete-- foo --in-context-- \'<none>\'',
      '--action--- mtime=1970/05/12-10:38:57 ctime=1970/05/12-10:38:57 --incomplete-- bar --in-context-- \'<none>\'',
      ]
    self.helpTest(inputs, golden_printed)

  def testDuplicateContextNames(self):
    inputs = ['chclock 988',
              'cd /inbox',

              'mkctx Ca',
              'mkact ACa',
              'chctx Ca ACa',
              'echo inctx Ca -1:',
              'inctx Ca',

              'mkact ANoContext',
              'echo inctx -0.8 is the same:',
              'inctx Ca',

              'chclock +1',
              'rmctx Ca',
              'echo inctx after rmctx:',
              'inctx Ca',
              'echo done',
              'chclock +1',
              'echo mkctx Ca:',
              'mkctx Ca',
              'view all_even_deleted',
              'echo lsctx -l:',
              'lsctx -l',
              'mkact ACa2',
              'chctx Ca ACa2',
              'echo inctx Ca 3.14:',
              'inctx Ca',
              'echo lsctx -l 2:',
              'lsctx -l',
              'echo done',

              'chclock +1',
              'rmctx Ca',
              'mkctx Ca',
              'deactivatectx Ca',
              'chctx Ca ACa2',
              'echo lsctx after rmctx mkctx:',
              'lsctx -l',
              'echo ls:',
              'ls',
              'rmctx Ca',
              'echo ls2 after rmctx:',
              'ls',
              ]
    golden_printed = [
      'inctx Ca -1:',
      '--action--- --incomplete-- ACa',
      'inctx -0.8 is the same:',
      '--action--- --incomplete-- ACa',
      'inctx after rmctx:',
      'No Context is named "Ca"',
      'done',
      'mkctx Ca:',
      'lsctx -l:',
      "--context-- mtime=1969/12/31-19:00:00 ctime=1969/12/31-19:00:00 ---active--- '<none>'",
      '--context-- --DELETED-- mtime=1969/12/31-19:16:29 ctime=1969/12/31-19:16:28 dtime=1969/12/31-19:16:29 ---active--- Ca-deleted-at-989.0',
      '--context-- mtime=1969/12/31-19:16:30 ctime=1969/12/31-19:16:30 ---active--- Ca',
      'inctx Ca 3.14:',
      '--action--- --incomplete-- ACa2',
      'lsctx -l 2:',
      "--context-- mtime=1969/12/31-19:00:00 ctime=1969/12/31-19:00:00 ---active--- '<none>'",
      '--context-- --DELETED-- mtime=1969/12/31-19:16:29 ctime=1969/12/31-19:16:28 dtime=1969/12/31-19:16:29 ---active--- Ca-deleted-at-989.0',
      '--context-- mtime=1969/12/31-19:16:30 ctime=1969/12/31-19:16:30 ---active--- Ca',
      'done',
      'lsctx after rmctx mkctx:',
      "--context-- mtime=1969/12/31-19:00:00 ctime=1969/12/31-19:00:00 ---active--- '<none>'",
      '--context-- --DELETED-- mtime=1969/12/31-19:16:29 ctime=1969/12/31-19:16:28 dtime=1969/12/31-19:16:29 ---active--- Ca-deleted-at-989.0',
      '--context-- --DELETED-- mtime=1969/12/31-19:16:31 ctime=1969/12/31-19:16:30 dtime=1969/12/31-19:16:31 ---active--- Ca-deleted-at-991.0',
      '--context-- mtime=1969/12/31-19:16:31 ctime=1969/12/31-19:16:31 --INACTIVE-- Ca',
      'ls:',
      '--action--- --incomplete-- ACa --in-context-- \'<none>\'',
      '--action--- --incomplete-- ANoContext --in-context-- \'<none>\'',
      '--action--- --incomplete-- ACa2 --in-context-- Ca',
      'ls2 after rmctx:',
      '--action--- --incomplete-- ACa --in-context-- \'<none>\'',
      '--action--- --incomplete-- ANoContext --in-context-- \'<none>\'',
      '--action--- --incomplete-- ACa2 --in-context-- \'<none>\'',
      ]
    self.helpTest(inputs, golden_printed)

  def testDumpprotobuf(self):
    inputs = ['chclock 988',
              'cd /inbox',
              'mkctx Ca',
              'mkact ACa',
              'chctx Ca ACa',
              'dumpprotobuf',
              ]
    golden_printed = ['inbox {\n'
                      '  common {\n'
                      '    is_deleted: false\n'
                      '    timestamp {\n'
                      '      ctime: 36000000\n'
                      '      dtime: -1\n'
                      '      mtime: 988000000\n'
                      '    }\n'
                      '    metadata {\n'
                      '      name: "inbox"\n'
                      '    }\n'
                      '    uid: 1\n'
                      '  }\n'
                      '  is_complete: false\n'
                      '  is_active: true\n'
                      '  actions {\n'
                      '    common {\n'
                      '      is_deleted: false\n'
                      '      timestamp {\n'
                      '        ctime: 988000000\n'
                      '        dtime: -1\n'
                      '        mtime: 988000000\n'
                      '      }\n'
                      '      metadata {\n'
                      '        name: "ACa"\n'
                      '      }\n'
                      '      uid: 5\n'
                      '    }\n'
                      '    is_complete: false\n'
                      '    ctx {\n'
                      '      common {\n'
                      '        uid: 4\n'
                      '      }\n'
                      '    }\n'
                      '  }\n'
                      '}\n'
                      'root {\n'
                      '  common {\n'
                      '    is_deleted: false\n'
                      '    timestamp {\n'
                      '      ctime: 36000000\n'
                      '      dtime: -1\n'
                      '      mtime: 36000000\n'
                      '    }\n'
                      '    metadata {\n'
                      '      name: ""\n'
                      '    }\n'
                      '    uid: 2\n'
                      '  }\n'
                      '}\n'
                      'ctx_list {\n'
                      '  common {\n'
                      '    is_deleted: false\n'
                      '    timestamp {\n'
                      '      ctime: 36000000\n'
                      '      dtime: -1\n'
                      '      mtime: 988000000\n'
                      '    }\n'
                      '    metadata {\n'
                      '      name: "Contexts"\n'
                      '    }\n'
                      '    uid: 3\n'
                      '  }\n'
                      '  contexts {\n'
                      '    common {\n'
                      '      is_deleted: false\n'
                      '      timestamp {\n'
                      '        ctime: 988000000\n'
                      '        dtime: -1\n'
                      '        mtime: 988000000\n'
                      '      }\n'
                      '      metadata {\n'
                      '        name: "Ca"\n'
                      '      }\n'
                      '      uid: 4\n'
                      '    }\n'
                      '    is_active: true\n'
                      '  }\n'
                      '}\n'
                      'has_never_purged_deleted: true\n'
      ]
    self.helpTest(inputs, golden_printed)

  def testCdinbox(self):
    time.time = lambda: 38
    inputs = ['cd /',
              'cd /inbox',
              'touch ZZ',
              'echo ls -l -a:',
              'ls -l -a',
              'cd /',
              'cd inbox',
              'echo ls:',
              'ls',
              ]
    golden_printed = [
      'ls -l -a:',
      '--project-- mtime=1969/12/31-19:00:38 ctime=1969/12/31-19:00:36 --incomplete-- ---active--- .',
      '--folder--- mtime=1969/12/31-19:00:36 ctime=1969/12/31-19:00:36 ..',
      '--action--- mtime=1969/12/31-19:00:38 ctime=1969/12/31-19:00:38 --incomplete-- ZZ --in-context-- \'<none>\'',
      'ls:',
      '--action--- --incomplete-- ZZ --in-context-- \'<none>\'',
      ]
    self.helpTest(inputs, golden_printed)

  def testLsWithArguments(self):
    time.time = lambda: 38
    inputs = ['mkdir /F0',
              'mkdir /F1',
              'mkdir /F0/F00',
              'mkdir F0/F01',

              'echo ls -R F0:',
              'ls -R F0',

              'echo ls / first time:',
              'ls /',

              'echo ls F0 F1:',
              'ls F0 F1',

              'echo ls /F0:',
              'ls /F0',

              'echo ls F0:',
              'ls F0',

              'mkprj /F0/F00/PinF00',
              'mkact /F0/F00/PinF00/AinPinF00',

              'echo ls Action:',
              'ls /F0/F00/PinF00/AinPinF00',

              'echo ls / second time:',
              'ls /',
              ]
    golden_printed = [
      'ls -R F0:',
      '--folder--- F00',
      '--folder--- F01',
      '',
      'F00:',
      '',
      'F01:',
      # TODO(chandler): Instead of the above 'F00:', print 'F0/F00:'. Here's how
      # GNU/Linux's "ls" does it:
      # $ ls -R -1 /l/F0
      # F00
      # F01
      # 
      # /l/F0/F00:
      # 
      # /l/F0/F01:

      'ls / first time:',
      '--project-- --incomplete-- ---active--- inbox',
      '--folder--- F0',
      '--folder--- F1',

      'ls F0 F1:',
      'F0:',
      '--folder--- F00',
      '--folder--- F01',
      '',
      'F1:',

      'ls /F0:',
      '--folder--- F00',
      '--folder--- F01',

      'ls F0:',
      '--folder--- F00',
      '--folder--- F01',

      'ls Action:',
      '--action--- --incomplete-- AinPinF00 --in-context-- \'<none>\'',
      # TODO(chandler): Mimic GNU/Linux's "ls" which would print this instead:
      # '--action--- --incomplete-- /F0/F00/PinF00/AinPinF00 --in-context-- \'<none>\'',

      'ls / second time:',
      '--project-- --incomplete-- ---active--- inbox',
      '--folder--- F0',
      '--folder--- F1',
      ]
    self.helpTest(inputs, golden_printed)

  def testMkdirPathsWithSlashes(self):
    time.time = lambda: 38
    inputs = ['mkdir /F0',
              'mkdir /F0/F00',
              'mkdir F0/F01',
              'cd /',
              'ls -R',
              'echo oof',
              'mkdir F9/',
              'echo oofoof',
              'mkdir F0/F02/',
              ]
    golden_printed = [
      '--project-- --incomplete-- ---active--- inbox',
      '--folder--- F0',
      '',
      './inbox:',
      '',
      './F0:',
      '--folder--- F00',
      '--folder--- F01',
      '',
      './F0/F00:',
      '',
      './F0/F01:',
      'oof',
      'Unexpected trailing "/"',
      'oofoof',
      'Unexpected trailing "/"',
      ]
    self.helpTest(inputs, golden_printed)

  def testPathsWithSlashes(self):
    FLAGS.pyatdl_show_uid = True
    time.time = lambda: 38
    inputs = ['cd /',
              'mkdir F0',
              'cd F0',
              'echo pwd F0:',
              'pwd',
              'mkdir F00',
              'mkdir F01',
              'cd F00',
              'mkdir F000',
              'cd /F0/F00',
              'echo /F0/F00:',
              'pwd',
              'echo ls:',
              'ls',
              'cd /F0',
              'echo /F0:',
              'pwd',
              'cd /',
              'cd F0/F00',
              'echo F0/F00:',
              'pwd',
              'cd /F0//F0/F01',
              'echo F0/F01:',
              'pwd',
              'cd /',
              'echo pwd at root:',
              'pwd',
              'cd //F0',
              'echo /F0:',
              'pwd',
              'cd //inbox',
              'echo /inbox:',
              'pwd',
              'cd /F0/F01///inbox',
              'echo /inbox:',
              'pwd',
              'cd /',
              'mkprj /F0/F01/P0',
              'mkact /F0/F01/P0/A0',
              'cd F0/F01',
              'mkact P0/A1',
              'cd /',
              'echo ls9:',
              'ls -R',
              'echo removals:',
              'rmact /F0/F01/P0/A0',
              'echo complete:',
              'complete /F0/F01/P0/A1',
              'echo configurereview:',
              'configurereview --max_seconds_before_review=9.0 F0/F01/P0',
              'configurereview --max_seconds_before_review=7.0 /F0/F01/P0',
              'echo configurereview error:',
              'configurereview --max_seconds_before_review=6.0 /F0/F01/P0/',
              'echo ls10:',
              'ls -R',
              'echo rmprj err:',
              'rmprj /F0/F01/P0/',
              'rmact /F0/F01/P0/A1',
              'activateprj /F0/F01/P0',
              'deactivateprj F0/F01/P0',
              'echo complete success:',
              'complete /F0/F01/P0',
              'echo ls showing completed P0:',
              'ls /F0/F01',
              'echo rmprj:',
              'rmprj /F0/F01/P0',
              'echo ls11:',
              'ls -R',
              'cd /',
              'rmdir F0/F00/F000',
              'rmdir F0/F00',
              'rmdir F0/F01',
              'rmdir /F0',
              'echo ls12:',
              'ls -R',
              ]
    golden_printed = [
      'pwd F0:',
      '/F0',
      '/F0/F00:',
      '/F0/F00',
      'ls:',
      '--folder--- uid=7 F000',
      '/F0:',
      '/F0',
      'F0/F00:',
      '/F0/F00',
      'F0/F01:',
      '/F0/F01',
      'pwd at root:',
      '/',
      '/F0:',
      '/F0',
      '/inbox:',
      '/inbox',
      '/inbox:',
      '/inbox',
      'ls9:',
      '--project-- uid=1 --incomplete-- ---active--- inbox',
      '--folder--- uid=4 F0',
      '',
      './inbox:',
      '',
      './F0:',
      '--folder--- uid=5 F00',
      '--folder--- uid=6 F01',
      '',
      './F0/F00:',
      '--folder--- uid=7 F000',
      '',
      './F0/F00/F000:',
      '',
      './F0/F01:',
      '--project-- uid=8 --incomplete-- ---active--- P0',
      '',
      './F0/F01/P0:',
      '--action--- uid=9 --incomplete-- A0 --in-context-- \'<none>\'',
      '--action--- uid=10 --incomplete-- A1 --in-context-- \'<none>\'',
      'removals:',
      'complete:',
      'configurereview:',
      'configurereview error:',
      'Unexpected trailing "/"',
      'ls10:',
      '--project-- uid=1 --incomplete-- ---active--- inbox',
      '--folder--- uid=4 F0',
      '',
      './inbox:',
      '',
      './F0:',
      '--folder--- uid=5 F00',
      '--folder--- uid=6 F01',
      '',
      './F0/F00:',
      '--folder--- uid=7 F000',
      '',
      './F0/F00/F000:',
      '',
      './F0/F01:',
      '--project-- uid=8 --incomplete-- ---active--- P0',
      '',
      './F0/F01/P0:',
      '--action--- uid=10 ---COMPLETE--- A1 --in-context-- \'<none>\'',
      'rmprj err:',
      'Unexpected trailing "/"',
      'complete success:',
      'ls showing completed P0:',
      '--project-- uid=8 ---COMPLETE--- --INACTIVE-- P0',
      'rmprj:',
      'ls11:',
      '--project-- uid=1 --incomplete-- ---active--- inbox',
      '--folder--- uid=4 F0',
      '',
      './inbox:',
      '',
      './F0:',
      '--folder--- uid=5 F00',
      '--folder--- uid=6 F01',
      '',
      './F0/F00:',
      '--folder--- uid=7 F000',
      '',
      './F0/F00/F000:',
      '',
      './F0/F01:',
      'ls12:',
      '--project-- uid=1 --incomplete-- ---active--- inbox',
      '',
      './inbox:',
      ]
    self.helpTest(inputs, golden_printed)

  def testRenameActionProjectsFolders(self):
    inputs = ['cd /inbox',
              'chclock 39',
              'touch ZZ',
              'echo ls -l -a:',
              'ls -l -a',
              'rename "ZZ TOP"',
              'echo ls:',
              'ls',
              'rename ZZ TOP',
              'echo ls2:',
              'ls -l',
              'chclock 40',
              'touch YY',
              'echo lsctx',
              'lsctx',
              'echo yep it is empty',
              'mkctx WAITY',
              'chctx WAITY YY',
              'rename YY TOY',
              'echo ls3:',
              'ls -l',
              'echo rename TOY TOP:',
              'rename TOY\tTOP',
              'echo err1:',
              'rename NONEXIST TOPPPP',
              'echo success renaming action:',
              'rename TOP wasTOYthenwasTOP',
              'echo ls:',
              'ls',
              'cd /',
              'mkdir aDir',
              'cd aDir',
              'mkprj aPrj',
              'cd ..',
              'rename aDir wasaDir',
              'echo ls wasaDir:',
              'ls',
              'cd wasaDir',
              'echo subdir ls:',
              'ls',
              ]
    golden_printed = [
      'ls -l -a:',
      '--project-- mtime=1969/12/31-19:00:39 ctime=1969/12/31-19:00:36 --incomplete-- ---active--- .',
      '--folder--- mtime=1969/12/31-19:00:36 ctime=1969/12/31-19:00:36 ..',
      '--action--- mtime=1969/12/31-19:00:39 ctime=1969/12/31-19:00:39 --incomplete-- ZZ --in-context-- \'<none>\'',
      'Needs 2 positional arguments; found these: [u\'ZZ TOP\']',
      'ls:',
      '--action--- --incomplete-- ZZ --in-context-- \'<none>\'',
      'ls2:',
      '--action--- mtime=1969/12/31-19:00:39 ctime=1969/12/31-19:00:39 --incomplete-- TOP --in-context-- \'<none>\'',
      'lsctx',
      "--context-- ---active--- '<none>'",
      'yep it is empty',
      'ls3:',
      '--action--- mtime=1969/12/31-19:00:39 ctime=1969/12/31-19:00:39 --incomplete-- TOP --in-context-- \'<none>\'',
      '--action--- mtime=1969/12/31-19:00:40 ctime=1969/12/31-19:00:40 --incomplete-- TOY --in-context-- WAITY',
      'rename TOY TOP:',
      'err1:',
      'No item named "NONEXIST" exists in the current working Folder/Project (see "help pwd").  Choices: TOP TOP',
      'success renaming action:',
      'ls:',
      '--action--- --incomplete-- wasTOYthenwasTOP --in-context-- \'<none>\'',
      '--action--- --incomplete-- TOP --in-context-- WAITY',
      'ls wasaDir:',
      '--project-- --incomplete-- ---active--- inbox',
      '--folder--- wasaDir',
      'subdir ls:',
      '--project-- --incomplete-- ---active--- aPrj',
      ]
    self.helpTest(inputs, golden_printed)

  def testRenameContext(self):
    inputs = ['chclock 1112',
              'view all_even_deleted',
              'mkctx C0',
              'echo No Context...',
              'renamectx C1 wasC1',
              'echo Now renamectx',
              'renamectx C0 wasC0',
              'mkctx C2',
              'cd /inbox',
              'touch A0',
              'touch A1',
              'chctx C2 A1',
              'cd /',
              'mkprj P0',
              'cd P0',
              'touch AP0',
              'chctx C2 AP0',
              'echo ls -l P0:',
              'ls -l',
              'cd /inbox',
              'echo ls -l /inbox:',
              'ls -l',
              'echo lsctx:',
              'lsctx',
              'renamectx C2 wasC2',
              'cd /',
              'cd P0',
              'echo ls -l P0 2:',
              'ls -l',
              'cd /inbox',
              'echo ls -l /inbox 2:',
              'ls -l',
              'echo lsctx 2:',
              'lsctx',
              'echo Err:',
              'renamectx wasC2 "wasC0"',
              'echo done Err',
              'rmctx wasC0',
              'echo lsctx -l after rmctx wasC0:',
              'lsctx -l',
              'echo mkctx wasC0:',
              'mkctx wasC0',
              'echo before renamectx:',
              'renamectx wasC0 waswasC0',
              'mkctx wasC0',
              'echo gist:',
              'dump -m',
              'echo FINrenamectx',
              ]
    golden_printed = [
      'No Context...',
      'No Context named "C1" found. Choices: C0',
      'Now renamectx',
      'ls -l P0:',
      '--action--- mtime=1969/12/31-19:18:32 ctime=1969/12/31-19:18:32 --incomplete-- AP0 --in-context-- C2',
      'ls -l /inbox:',
      '--action--- mtime=1969/12/31-19:18:32 ctime=1969/12/31-19:18:32 --incomplete-- A0 --in-context-- \'<none>\'',
      '--action--- mtime=1969/12/31-19:18:32 ctime=1969/12/31-19:18:32 --incomplete-- A1 --in-context-- C2',
      'lsctx:',
      "--context-- ---active--- '<none>'",
      '--context-- ---active--- wasC0',
      '--context-- ---active--- C2',
      'ls -l P0 2:',
      '--action--- mtime=1969/12/31-19:18:32 ctime=1969/12/31-19:18:32 --incomplete-- AP0 --in-context-- wasC2',
      'ls -l /inbox 2:',
      '--action--- mtime=1969/12/31-19:18:32 ctime=1969/12/31-19:18:32 --incomplete-- A0 --in-context-- \'<none>\'',
      '--action--- mtime=1969/12/31-19:18:32 ctime=1969/12/31-19:18:32 --incomplete-- A1 --in-context-- wasC2',
      'lsctx 2:',
      "--context-- ---active--- '<none>'",
      '--context-- ---active--- wasC0',
      '--context-- ---active--- wasC2',
      'Err:',
      'done Err',
      'lsctx -l after rmctx wasC0:',
      "--context-- mtime=1969/12/31-19:00:00 ctime=1969/12/31-19:00:00 ---active--- '<none>'",
      '--context-- --DELETED-- mtime=1969/12/31-19:18:32 ctime=1969/12/31-19:18:32 dtime=1969/12/31-19:18:32 ---active--- wasC0-deleted-at-1112.0',
      '--context-- mtime=1969/12/31-19:18:32 ctime=1969/12/31-19:18:32 ---active--- wasC0',
      'mkctx wasC0:',
      'A Context named "wasC0" already exists.',
      'before renamectx:',
      'gist:',
      '<todolist>',
      '    <inbox>',
      '        <project is_deleted="False" is_complete="False" is_active="True" name="inbox">',
      '            <action is_deleted="False" is_complete="False" name="A0" ctx=""/>',
      '            <action is_deleted="False" is_complete="False" name="A1" ctx="uid=5"/>',
      '        </project>',
      '    </inbox>',
      '    <folder is_deleted="False" name="">',
      '        <project is_deleted="False" is_complete="False" is_active="True" name="P0">',
      '            <action is_deleted="False" is_complete="False" name="AP0" ctx="uid=5"/>',
      '        </project>',
      '    </folder>',
      '    <contexts>',
      '        <context_list is_deleted="False" name="Contexts">',
      '            <context is_deleted="True" is_active="True" name="wasC0-deleted-at-1112.0"/>',
      '            <context is_deleted="False" is_active="True" name="waswasC0"/>',
      '            <context is_deleted="False" is_active="True" name="wasC0"/>',
      '        </context_list>',
      '    </contexts>',
      '</todolist>',
      'FINrenamectx',
      ]
    self.helpTest(inputs, golden_printed)

  def testArgProcessing(self):
    time.time = lambda: 49
    inputs = ['cd /inbox',
              'chclock -- +2',
              'chclock +1',
              'touch C',
              'chclock 1409712847.989031',
              'touch E',
              'echo ls -l 0:',
              'ls -l',
              'echo 199j',
              'chclock 199j',
              u'chclock \u0fff',
              'echo Before too-many-args error',
              'chclock 200j, 100j',
              'echo Before too-many-args error take 2',
              'chclock 200j 100j',
              'echo Before too-few-args error',
              'chclock',
              'echo before chclock -997 without --',
              'chclock -997',
              'echo before chclock -9 without --',
              'chclock -9',
              ]
    golden_printed = [
      'ls -l 0:',
      '--action--- mtime=1969/12/31-19:00:52 ctime=1969/12/31-19:00:52 --incomplete-- C --in-context-- \'<none>\'',
      '--action--- mtime=2014/09/02-22:54:07 ctime=2014/09/02-22:54:07 --incomplete-- E --in-context-- \'<none>\'',
      '199j',
      'Needs a numeric argument, seconds since the epoch (1970 CE). To move the clock relative to the old clock, prepend the argument with \'+\'. The argument: u\'199j\'',
      u'Needs a numeric argument, seconds since the epoch (1970 CE). To move the clock relative to the old clock, prepend the argument with \'+\'. The argument: u\'\\u0fff\'',
      'Before too-many-args error',
      'Needs a single positional argument; found these: [u\'200j,\', u\'100j\']',
      'Before too-many-args error take 2',
      'Needs a single positional argument; found these: [u\'200j\', u\'100j\']',
      'Before too-few-args error',
      'Needs a single positional argument; found none',
      'before chclock -997 without --',
      'chclock: Incorrect usage; details below.',
      'Correct usage is as follows:',
      '',
      '  Sets the system clock. Useful for unittests.',
      '',
      '  There are two forms:',
      '    chclock 1409712847.989031  # Absolute. Clock stops incrementing.',
      '    chclock +1  # Relative. Clock does not stop.',
      '',
      'The incorrect usage is as follows:',
      '',
      '  Cannot parse arguments. If you have a leading hyphen in one of your arguments, preface that argument with a \'--\' argument, the syntax that makes all following arguments positional. Detailed error: Unknown command line flag \'997\'',
      'before chclock -9 without --',
      'chclock: Incorrect usage; details below.',
      'Correct usage is as follows:',
      '',
      '  Sets the system clock. Useful for unittests.',
      '',
      '  There are two forms:',
      '    chclock 1409712847.989031  # Absolute. Clock stops incrementing.',
      '    chclock +1  # Relative. Clock does not stop.',
      '',
      'The incorrect usage is as follows:',
      '',
      '  Cannot parse arguments. If you have a leading hyphen in one of your arguments, preface that argument with a \'--\' argument, the syntax that makes all following arguments positional. Detailed error: Unknown command line flag \'9\'',
      ]
    self.helpTest(inputs, golden_printed)

  def testChclock(self):
    time.time = lambda: 40
    inputs = ['cd /inbox',
              'touch A',
              'echo ls -l:',
              'ls -l',
              'touch B',
              'echo ls -l 2:',
              'ls -l',
              'chclock +2',
              'touch C',
              'echo ls -l 3:',
              'ls -l',
              'chclock +3',
              'touch D',
              'chclock 1409712847.989031',
              'touch E',
              'echo ls -l 5:',
              'ls -l',
              ]
    golden_printed = [
      'ls -l:',
      '--action--- mtime=1969/12/31-19:00:40 ctime=1969/12/31-19:00:40 --incomplete-- A --in-context-- \'<none>\'',
      'ls -l 2:',
      '--action--- mtime=1969/12/31-19:00:40 ctime=1969/12/31-19:00:40 --incomplete-- A --in-context-- \'<none>\'',
      '--action--- mtime=1969/12/31-19:00:40 ctime=1969/12/31-19:00:40 --incomplete-- B --in-context-- \'<none>\'',
      'ls -l 3:',
      '--action--- mtime=1969/12/31-19:00:40 ctime=1969/12/31-19:00:40 --incomplete-- A --in-context-- \'<none>\'',
      '--action--- mtime=1969/12/31-19:00:40 ctime=1969/12/31-19:00:40 --incomplete-- B --in-context-- \'<none>\'',
      '--action--- mtime=1969/12/31-19:00:42 ctime=1969/12/31-19:00:42 --incomplete-- C --in-context-- \'<none>\'',
      'ls -l 5:',
      '--action--- mtime=1969/12/31-19:00:40 ctime=1969/12/31-19:00:40 --incomplete-- A --in-context-- \'<none>\'',
      '--action--- mtime=1969/12/31-19:00:40 ctime=1969/12/31-19:00:40 --incomplete-- B --in-context-- \'<none>\'',
      '--action--- mtime=1969/12/31-19:00:42 ctime=1969/12/31-19:00:42 --incomplete-- C --in-context-- \'<none>\'',
      '--action--- mtime=1969/12/31-19:00:45 ctime=1969/12/31-19:00:45 --incomplete-- D --in-context-- \'<none>\'',
      '--action--- mtime=2014/09/02-22:54:07 ctime=2014/09/02-22:54:07 --incomplete-- E --in-context-- \'<none>\'',
      ]
    self.helpTest(inputs, golden_printed)

  def testDeleteChildWithUndeletedGrandchildren(self):
    inputs = ['chclock 11333',
              'cd /',
              'mkdir F0',
              'cd F0',
              'mkprj P0',
              'cd P0',
              'touch A0',
              'touch A1',
              'rmact A0',
              'cd ..',
              'echo Expect an error re: A1 is not yet deleted',
              'rmprj P0',
              'cd P0',
              'rmact A1',
              'cd ..',
              'rmprj P0',
              'echo dump:',
              'dump',
              'cd /',
              'cd F0',
              'mkprj P1',
              'cd /',
              'echo Err re: rmdir F0',
              'rmdir F0',
              'cd F0',
              'rmprj P1',
              'cd ..',
              'rmdir F0',
              'echo dump2:',
              'dump',
              ]
    golden_printed = [
      'Expect an error re: A1 is not yet deleted',
      'Cannot delete because a descendant is not deleted.  descendant=\n<action is_deleted="False" is_complete="False" name="A1" ctx=""/>',
      'dump:',
r"""<todolist>
    <inbox>
        <project is_deleted="False" is_complete="False" is_active="True" name="inbox">
        
        </project>
    </inbox>
    <folder is_deleted="False" name="">
        <folder is_deleted="False" name="F0">
            <project is_deleted="True" is_complete="False" is_active="True" name="P0">
                <action is_deleted="True" is_complete="False" name="A0" ctx=""/>
                <action is_deleted="True" is_complete="False" name="A1" ctx=""/>
            </project>
        </folder>
    </folder>
    <contexts>
        <context_list is_deleted="False" name="Contexts">
        
        </context_list>
    </contexts>
</todolist>""",
      'Err re: rmdir F0',
      'Cannot delete because a descendant is not deleted.  descendant=\n<project is_deleted="False" is_complete="False" is_active="True" name="P1">\n\n</project>',
      'dump2:',
      r"""<todolist>
    <inbox>
        <project is_deleted="False" is_complete="False" is_active="True" name="inbox">
        
        </project>
    </inbox>
    <folder is_deleted="False" name="">
        <folder is_deleted="True" name="F0">
            <project is_deleted="True" is_complete="False" is_active="True" name="P0">
                <action is_deleted="True" is_complete="False" name="A0" ctx=""/>
                <action is_deleted="True" is_complete="False" name="A1" ctx=""/>
            </project>
            <project is_deleted="True" is_complete="False" is_active="True" name="P1">
            
            </project>
        </folder>
    </folder>
    <contexts>
        <context_list is_deleted="False" name="Contexts">
        
        </context_list>
    </contexts>
</todolist>""",
    ]
    self.helpTest(inputs, golden_printed)

  def testNamesAreNotUnique(self):
    inputs = ['chclock 7666',
              'cd /inbox',
              'mkact aa',
              'chclock +1',
              'echo second mkact aa:',
              'mkact aa',
              'echo ls -l:',
              'ls -l',
              ]
    golden_printed = [
        'second mkact aa:',
        'ls -l:',
        '--action--- mtime=1969/12/31-21:07:46 ctime=1969/12/31-21:07:46 --incomplete-- aa --in-context-- \'<none>\'',
        '--action--- mtime=1969/12/31-21:07:47 ctime=1969/12/31-21:07:47 --incomplete-- aa --in-context-- \'<none>\'',
      ]
    self.helpTest(inputs, golden_printed)

  def testRmdirThenMkdirOfSameDir(self):
    time.time = lambda: 37
    inputs = ['cd /',
              'mkdir D',
              'echo ls0:',
              'ls',
              'rmdir D',
              'echo ls1:',
              'ls',
              'view all_even_deleted',
              'echo ls2 all_even_deleted:',
              'ls -l',
              'echo mkdir D:',
              'mkdir D',
              ]
    golden_printed = [
      'ls0:',
      '--project-- --incomplete-- ---active--- inbox',
      '--folder--- D',
      'ls1:',
      '--project-- --incomplete-- ---active--- inbox',
      'ls2 all_even_deleted:',
      '--project-- mtime=1969/12/31-19:00:36 ctime=1969/12/31-19:00:36 --incomplete-- ---active--- inbox',
      '--folder--- --DELETED-- mtime=1969/12/31-19:00:37 ctime=1969/12/31-19:00:37 dtime=1969/12/31-19:00:37 D',
      'mkdir D:',
      ]
    self.helpTest(inputs, golden_printed)

  def testRmdirThenMkdirOfSameDir2(self):
    inputs = ['chclock 37',
              'cd /',
              'mkdir D',
              'rmdir D',
              'mkdir D',
              'mkprj D/prj',
              'touch D/prj/A',
              'echo ls all_even_deleted:',
              'ls -R -v all_even_deleted',
              'echo ls all:',
              'ls -R -v all',
              ]
    golden_printed = [
      'ls all_even_deleted:',
      '--project-- --incomplete-- ---active--- inbox',
      '--folder--- --DELETED-- D',
      '--folder--- D',
      '',
      './inbox:',
      '',
      './D:',
      '',
      './D:',
      '--project-- --incomplete-- ---active--- prj',
      '',
      './D/prj:',
      '--action--- --incomplete-- A --in-context-- \'<none>\'',
      'ls all:',
      '--project-- --incomplete-- ---active--- inbox',
      '--folder--- D',
      '',
      './inbox:',
      '',
      './D:',
      '--project-- --incomplete-- ---active--- prj',
      '',
      './D/prj:',
      '--action--- --incomplete-- A --in-context-- \'<none>\'',
      ]
    self.helpTest(inputs, golden_printed)

  def testRmdirThenMkdirOfSameDir3(self):
    inputs = ['chclock 37',
              'cd /',
              'mkdir D',
              'rmdir D',
              'mkprj D/prj',
              'mkdir D/subd',
              'ls -R -v all_even_deleted',
              ]
    golden_printed = [
      'Cannot create within a deleted Folder',
      'Cannot create within a deleted Folder',
      '--project-- --incomplete-- ---active--- inbox',
      '--folder--- --DELETED-- D',
      '',
      './inbox:',
      '',
      './D:',
      ]
    self.helpTest(inputs, golden_printed)

  def testContextRemovalAndViews(self):
    inputs = ['chclock 12345',
              'mkctx Ca',
              'mkctx Cb',
              'echo lsctx 0:',
              'lsctx',
              'chclock +1',
              'rmctx Ca',
              'echo lsctx after rmctx Ca:',
              'lsctx',
              'view all_even_deleted',
              'echo lsctx 2 all_even_deleted:',
              'lsctx',
              'echo lsctx -l all_even_deleted:',
              'lsctx -l',
              ]
    golden_printed = [
      'lsctx 0:',
      '--context-- ---active--- \'<none>\'',
      '--context-- ---active--- Ca',
      '--context-- ---active--- Cb',
      'lsctx after rmctx Ca:',
      '--context-- ---active--- \'<none>\'',
      '--context-- ---active--- Cb',
      'lsctx 2 all_even_deleted:',
      '--context-- ---active--- \'<none>\'',
      '--context-- --DELETED-- ---active--- Ca-deleted-at-12346.0',
      '--context-- ---active--- Cb',
      'lsctx -l all_even_deleted:',
      "--context-- mtime=1969/12/31-19:00:00 ctime=1969/12/31-19:00:00 ---active--- '<none>'",
      '--context-- --DELETED-- mtime=1969/12/31-22:25:46 ctime=1969/12/31-22:25:45 dtime=1969/12/31-22:25:46 ---active--- Ca-deleted-at-12346.0',
      '--context-- mtime=1969/12/31-22:25:45 ctime=1969/12/31-22:25:45 ---active--- Cb',
      ]
    self.helpTest(inputs, golden_printed)

  def testViews(self):
    inputs = ['chclock 123456',
              'view',
              'echo after view no args',
              'mkctx Cactive',
              'mkctx Cinactive',
              'deactivatectx Cinactive',
              'mkctx CactiveDeleted',
              'rmctx CactiveDeleted',
              'mkctx CinactiveDeleted',
              'deactivatectx CinactiveDeleted',
              'rmctx CinactiveDeleted',

              'cd /',
              'mkprj Pinactive',
              'deactivateprj Pinactive',
              'activateprj Pinactive',  # gets more code coverage
              'deactivateprj Pinactive',
              'cd Pinactive',

              'touch PinactiveAcompleteUndeleted',
              'complete PinactiveAcompleteUndeleted',

              'touch PinactiveAcompleteDeleted',
              'complete PinactiveAcompleteDeleted',
              'rmact PinactiveAcompleteDeleted',

              'touch PinactiveAincompleteUndeleted',

              'touch PinactiveAincompleteDeleted',
              'rmact PinactiveAincompleteDeleted',

              'cd /',
              'mkprj Pactive',
              'cd Pactive',

              'touch PactiveAcompleteUndeleted',
              'complete PactiveAcompleteUndeleted',

              'touch PactiveAcompleteDeleted',
              'complete PactiveAcompleteDeleted',
              'rmact PactiveAcompleteDeleted',

              'touch PactiveAincompleteUndeleted',

              'touch PactiveAincompleteDeleted',
              'rmact PactiveAincompleteDeleted',

              'view all_even_deleted',
              'echo ls Pactive all_even_deleted:',
              'ls',

              'view all',
              'echo ls Pactive all:',
              'ls',

              'view incomplete',
              'echo ls Pactive incomplete:',
              'ls',

              'view actionable',
              'echo ls Pactive actionable:',
              'ls',

              'cd /',
              'cd Pinactive',

              'view all_even_deleted',
              'echo ls Pinactive all_even_deleted:',
              'ls',
              'echo lsctx all_even_deleted:',
              'lsctx',

              'view all',
              'echo ls Pinactive all:',
              'ls',
              'echo lsctx all:',
              'lsctx',

              'view incomplete',
              'echo ls Pinactive incomplete:',
              'ls',
              'echo lsctx incomplete:',
              'lsctx',

              'view actionable',
              'echo ls Pinactive actionable:',
              'ls',
              'echo ls -v all_even_deleted:',
              'ls -v all_even_deleted',
              'echo ls -v all:',
              'ls -v all',
              'echo ls -a:',
              'ls -a',
              'echo ls:',
              'ls',
              'echo lsctx actionable:',
              'lsctx',
              'view',
              'echo after view no args again',
              'view default',
              'view',
              'echo after default is an alias',
              ]
    golden_printed = [
      'all',
      'after view no args',
      'ls Pactive all_even_deleted:',
      '--action--- ---COMPLETE--- PactiveAcompleteUndeleted --in-context-- \'<none>\'',
      '--action--- --DELETED-- ---COMPLETE--- PactiveAcompleteDeleted --in-context-- \'<none>\'',
      '--action--- --incomplete-- PactiveAincompleteUndeleted --in-context-- \'<none>\'',
      '--action--- --DELETED-- --incomplete-- PactiveAincompleteDeleted --in-context-- \'<none>\'',
      'ls Pactive all:',
      '--action--- ---COMPLETE--- PactiveAcompleteUndeleted --in-context-- \'<none>\'',
      '--action--- --incomplete-- PactiveAincompleteUndeleted --in-context-- \'<none>\'',
      'ls Pactive incomplete:',
      '--action--- --incomplete-- PactiveAincompleteUndeleted --in-context-- \'<none>\'',
      'ls Pactive actionable:',
      '--action--- --incomplete-- PactiveAincompleteUndeleted --in-context-- \'<none>\'',

      'ls Pinactive all_even_deleted:',
      '--action--- ---COMPLETE--- PinactiveAcompleteUndeleted --in-context-- \'<none>\'',
      '--action--- --DELETED-- ---COMPLETE--- PinactiveAcompleteDeleted --in-context-- \'<none>\'',
      '--action--- --incomplete-- PinactiveAincompleteUndeleted --in-context-- \'<none>\'',
      '--action--- --DELETED-- --incomplete-- PinactiveAincompleteDeleted --in-context-- \'<none>\'',

      'lsctx all_even_deleted:',
      "--context-- ---active--- '<none>'",
      '--context-- ---active--- Cactive',
      '--context-- --INACTIVE-- Cinactive',
      '--context-- --DELETED-- ---active--- CactiveDeleted-deleted-at-123456.0',
      '--context-- --DELETED-- --INACTIVE-- CinactiveDeleted-deleted-at-123456.0',

      'ls Pinactive all:',
      '--action--- ---COMPLETE--- PinactiveAcompleteUndeleted --in-context-- \'<none>\'',
      '--action--- --incomplete-- PinactiveAincompleteUndeleted --in-context-- \'<none>\'',

      'lsctx all:',
      "--context-- ---active--- '<none>'",
      '--context-- ---active--- Cactive',
      '--context-- --INACTIVE-- Cinactive',

      'ls Pinactive incomplete:',
      '--action--- --incomplete-- PinactiveAincompleteUndeleted --in-context-- \'<none>\'',

      'lsctx incomplete:',
      "--context-- ---active--- '<none>'",
      '--context-- ---active--- Cactive',
      '--context-- --INACTIVE-- Cinactive',

      'ls Pinactive actionable:',

      'ls -v all_even_deleted:',
      '--action--- ---COMPLETE--- PinactiveAcompleteUndeleted --in-context-- \'<none>\'',
      '--action--- --DELETED-- ---COMPLETE--- PinactiveAcompleteDeleted --in-context-- \'<none>\'',
      '--action--- --incomplete-- PinactiveAincompleteUndeleted --in-context-- \'<none>\'',
      '--action--- --DELETED-- --incomplete-- PinactiveAincompleteDeleted --in-context-- \'<none>\'',

      'ls -v all:',
      '--action--- ---COMPLETE--- PinactiveAcompleteUndeleted --in-context-- \'<none>\'',
      '--action--- --incomplete-- PinactiveAincompleteUndeleted --in-context-- \'<none>\'',
      'ls -a:',
      '--project-- --incomplete-- --INACTIVE-- .',
      '--folder--- ..',
      '--action--- ---COMPLETE--- PinactiveAcompleteUndeleted --in-context-- \'<none>\'',
      '--action--- --DELETED-- ---COMPLETE--- PinactiveAcompleteDeleted --in-context-- \'<none>\'',
      '--action--- --incomplete-- PinactiveAincompleteUndeleted --in-context-- \'<none>\'',
      '--action--- --DELETED-- --incomplete-- PinactiveAincompleteDeleted --in-context-- \'<none>\'',
      'ls:',
      'lsctx actionable:',
      "--context-- ---active--- '<none>'",
      '--context-- ---active--- Cactive',
      'actionable',
      'after view no args again',
      'all',
      'after default is an alias',
      ]
    self.helpTest(inputs, golden_printed)

  def testViewNeedingReview(self):
    inputs = ['chclock 123456',
              'mkprj /pDefault',
              'mkprj /pCompleted',
              'complete /pCompleted',
              'mkact /inbox/aCompleted',
              'complete /inbox/aCompleted',
              'mkact /inbox/aDeleted',
              'rmact /inbox/aDeleted',
              'mkact /inbox/aDefault',
              'mkprj /pInactive',
              'deactivateprj /pInactive',
              'mkprj /pReviewed',
              'chclock %d' % (123456 + 367*24*60*60),  # about a year later
              'completereview /pReviewed',
              'needsreview',
              'echo after needsreview',
              'view needing_review',
              'ls -R /',
              'echo after ls needing_review',
              'ls -v all_even_deleted -R /',
              'echo after ls all_even_deleted',
              'completereview /inbox',
              'ls -R /',
              'echo after inbox reviewed',
              'lsprj',
              'echo after lsprj',
              ]
    golden_printed = [
      '/inbox',
      '/pDefault',
      'after needsreview',
      '--project-- --incomplete-- ---active--- inbox',
      '--project-- --incomplete-- ---active--- pDefault',
      '',
      '/inbox:',
      '--action--- --incomplete-- aDefault --in-context-- \'<none>\'',
      '',
      '/pDefault:',
      'after ls needing_review',
      '--project-- --incomplete-- ---active--- inbox',
      '--project-- --incomplete-- ---active--- pDefault',
      '--project-- ---COMPLETE--- ---active--- pCompleted',
      '--project-- --incomplete-- --INACTIVE-- pInactive',
      '--project-- --incomplete-- ---active--- pReviewed',
      '',
      '/inbox:',
      '--action--- ---COMPLETE--- aCompleted --in-context-- \'<none>\'',
      '--action--- --DELETED-- --incomplete-- aDeleted --in-context-- \'<none>\'',
      '--action--- --incomplete-- aDefault --in-context-- \'<none>\'',
      '',
      '/pDefault:',
      '',
      '/pCompleted:',
      '',
      '/pInactive:',
      '',
      '/pReviewed:',
      'after ls all_even_deleted',
      '--project-- --incomplete-- ---active--- pDefault',
      '',
      '/pDefault:',
      'after inbox reviewed',
      '/pDefault',
      'after lsprj',
      ]
    self.helpTest(inputs, golden_printed)

  def testViewActionable(self):
    inputs = ['chclock 123456',
              'mkctx @someday',
              'deactivatectx @someday',
              'mkctx @home',
              'mkprj /p',
              'touch -c @someday "/p/blue sky idea"',
              'touch "/p/no context"',
              'touch -c @home "/p/kiss my spouse"',
              'echo ls -R -v all',
              'ls -R -v all',
              'echo ls -R -v actionable',
              'ls -R -v actionable',
              ]
    golden_printed = [
      'ls -R -v all',
      '--project-- --incomplete-- ---active--- inbox',
      '--project-- --incomplete-- ---active--- p',
      '',
      './inbox:',
      '',
      './p:',
      '--action--- --incomplete-- \'blue sky idea\' --in-context-- @someday',
      '--action--- --incomplete-- \'no context\' --in-context-- \'<none>\'',
      '--action--- --incomplete-- \'kiss my spouse\' --in-context-- @home',
      'ls -R -v actionable',
      '--project-- --incomplete-- ---active--- inbox',
      '--project-- --incomplete-- ---active--- p',
      '',
      './inbox:',
      '',
      './p:',
      '--action--- --incomplete-- \'no context\' --in-context-- \'<none>\'',
      '--action--- --incomplete-- \'kiss my spouse\' --in-context-- @home',
      ]
    self.helpTest(inputs, golden_printed)

  def testClearreview(self):
    inputs = ['chclock 1500192330',
              'mkprj /a',
              'mkprj /b',
              'completereview /a',
              'echo ls:',
              'ls -R -v needing_review /',
              'clearreview',
              'echo again ls:',
              'ls -R -v needing_review /',
              'completereview /a',
              'clearreview /a',
              'echo again again ls:',
              'ls -R -v needing_review /',
              ]
    golden_printed = [
      'ls:',
      '--project-- --incomplete-- ---active--- inbox',
      '--project-- --incomplete-- ---active--- b',
      '',
      '/inbox:',
      '',
      '/b:',
      'again ls:',
      '--project-- --incomplete-- ---active--- inbox',
      '--project-- --incomplete-- ---active--- a',
      '--project-- --incomplete-- ---active--- b',
      '',
      '/inbox:',
      '',
      '/a:',
      '',
      '/b:',
      'again again ls:',
      '--project-- --incomplete-- ---active--- inbox',
      '--project-- --incomplete-- ---active--- a',
      '--project-- --incomplete-- ---active--- b',
      '',
      '/inbox:',
      '',
      '/a:',
      '',
      '/b:',
      ]
    self.helpTest(inputs, golden_printed)

  def testComplete(self):
    inputs = ['chclock 1234567',
              'cd /',
              'mkprj P',
              'cd P',
              'touch Acomplete',
              'complete Acomplete',
              'touch Aincomplete',
              'cd /',
              'echo b4',
              'complete P',
              'echo after',
              'cd P',
              'complete Aincomplete',
              'cd /',
              'complete P',
              'echo dump:',
              'dump',
              ]
    golden_printed = [
      'b4',
      'Cannot mark complete (without --force flag) because a descendant action is incomplete: <action is_deleted="False" is_complete="False" name="Aincomplete" ctx=""/>',
      'after',
      'dump:',
      r"""<todolist>
    <inbox>
        <project is_deleted="False" is_complete="False" is_active="True" name="inbox">
        
        </project>
    </inbox>
    <folder is_deleted="False" name="">
        <project is_deleted="False" is_complete="True" is_active="True" name="P">
            <action is_deleted="False" is_complete="True" name="Acomplete" ctx=""/>
            <action is_deleted="False" is_complete="True" name="Aincomplete" ctx=""/>
        </project>
    </folder>
    <contexts>
        <context_list is_deleted="False" name="Contexts">
        
        </context_list>
    </contexts>
</todolist>""",
      ]
    self.helpTest(inputs, golden_printed)

  def testEcho2(self):
    inputs = ['echo -2',
              'echo --2',
              'echo -- 2',
              'echo -- -2',
              'echo -- --2',
              'echolines -- -2 --2',
              ]
    golden_printed = [
      'echo: Incorrect usage; details below.',
      'Correct usage is as follows:',
      '',
      '  Echoes the arguments and prints a newline as the unix command echo(1) does.',
      '',
      '  This is helpful for documenting lists of commands.',
      '',
      'The incorrect usage is as follows:',
      '',
      '  Cannot parse arguments. If you have a leading hyphen in one of your arguments, preface that argument with a \'--\' argument, the syntax that makes all following arguments positional. Detailed error: Unknown command line flag \'2\'',
      'echo: Incorrect usage; details below.',
      'Correct usage is as follows:',
      '',
      '  Echoes the arguments and prints a newline as the unix command echo(1) does.',
      '',
      '  This is helpful for documenting lists of commands.',
      '',
      'The incorrect usage is as follows:',
      '',
      '  Cannot parse arguments. If you have a leading hyphen in one of your arguments, preface that argument with a \'--\' argument, the syntax that makes all following arguments positional. Detailed error: Unknown command line flag \'2\'',
      '2',
      '-2',
      '--2',
      '-2',
      '--2',
      ]
    self.helpTest(inputs, golden_printed)

  def testMisc37(self):
    FLAGS.pyatdl_show_uid = True
    inputs = ['cd /inbox',
              'mkact "Remember the yogurt"',
              'mkctx "@Store"',
              "chctx @Store 'Remember the yogurt'",
              "inctx @Store",
              "mkctx X",
              "mkctx X",
              ]
    golden_printed = [
      '--action--- uid=4 --incomplete-- \'Remember the yogurt\'',
      'A Context named "X" already exists.',
      ]
    self.helpTest(inputs, golden_printed)

  def testBadArgs(self):
    inputs = ['chclock 1234567',
              'chclock ++2',
              'echo e0',
              'chclock -- -2',
              'echo e1',
              'ls $',
              'echo e2',
              'dump $',
              'echo e3.1',
              'dump -m $',
              'echo e3.2',
              'dumpprotobuf $',
              'echo e4',
              'chctx Z Y',
              'echo e5',
              'mkctx C0',
              'chctx C0 Y',
              'echo e5.5',
              'cd /inbox',
              'chctx C0 Y',
              'echo e6',
              'complete ZZ',
              'echo e7',
              'view ZZZ',
              'echo e8',
              'cd /',
              'cd ..',
              'echo e9',
              'cd -R QJ',
              'echo e10',
              'cd QK',
              'echo e11',
              'completereview AB',
              'echo e12',
              'needsreview $',
              'echo e13',
              'activatectx foo',
              'echo e14',
              'mkact A0',
              'echo e15',
              'mkprj Pn',
              'cd Pn',
              'echo e16',
              'mkact A0',
              'echo e18',
              'reset --annihilate $',
              'echo e19',
              'rmctx $',
              'echo e20',
              'cd /',
              'rmdir Pn',
              'echo e21',
              'mkdir F000',
              'rmprj F000',
              'echo e22',
              'rmprj Pnonexistent',
              'echo e23',
              'cd F000',
              'rmact $',
              'echo e24',
              'cd /',
              'cd Pn',
              'rmact $',
              'echo e25',
              'pwd $',
              'echo e27',
              'activateprj nonexistentProject',
              'echo e28',
              '',
              'echo e29',
              'nonexistentCommand $',
              'echo e30',
              'cd ..',
              'touch Pn/',
              'echo e31',
              'touch nonexist/',
              'echo e32',
              ]
    golden_printed = [
      'A leading \'++\' makes no sense.',
      'e0',
      'Minimum value is 0, a.k.a. 1970 CE.',
      'e1',
      r"""With current working Folder/Project "/", there is no such child "$".  Choices:
    ..
""",
      'e2',
      'Takes no arguments; found these arguments: [u\'$\']',
      'e3.1',
      'Takes no arguments; found these arguments: [u\'$\']',
      'e3.2',
      'Takes no arguments; found these arguments: [u\'$\']',
      'e4',
      'No such Context "Z"',
      'e5',
      'This command only makes sense inside a Project, not inside "/". See "help pwd".',
      'e5.5',
      'No such Action "Y". There are no Actions in the current Project.',
      'e6',
      'No such Project "ZZ". There are no Projects in the current Folder.',
      'e7',
      'No such view filter "ZZZ": See "help view".',
      'e8',
      'Already at the root Folder; cannot ascend.',
      'e9',
      r"""With current working Folder/Project "/", there is no such child "QJ".""",
      'e10',
      r"""With current working Folder/Project "/", there is no such child "QK".  Choices:
    ..
""",
      'e11',
      'No such Project "AB". There are no Projects in the current Folder.',
      'e12',
      'Takes no arguments; found these arguments: [u\'$\']',
      'e13',
      'No such context "foo"',
      'e14',
      'The "mkact" command only works within a Project, not a Folder.  The folder is "/".',
      'e15',
      'e16',
      'e18',
      'Takes no arguments; found these arguments: [u\'$\']',
      'e19',
      'No such context "$".  Your choices: C0',
      'e20',
      'No such Folder "Pn". There are no Folders within the specified Folder.',
      'e21',
      'No such Project "F000". Choices: Pn',
      'e22',
      'No such Project "Pnonexistent". Choices: Pn',
      'e23',
      'This command only makes sense inside a Project, not inside "F000". See "help pwd".',
      'e24',
      'No such Action "$". Choices: A0',
      'e25',
      'Takes no arguments; found these arguments: [u\'$\']',
      'e27',
      'No such Project "nonexistentProject". There are no Projects in the current Folder.',
      'e28',
      'e29',
      'Command "nonexistentCommand" not found; see "help"',
      'e30',
      'Unexpected trailing "/"',
      'e31',
      r"""With current working Folder/Project "/", there is no such child "nonexist".  Choices:
    ..
    Pn
    F000""",
      'e32',
      ]
    self.helpTest(inputs, golden_printed)

  def testRmctx(self):
    # Especially tests what happens when someone tries to remove a context that
    # is in use.
    inputs = ['chclock 122',
              'cd /inbox',
              'mkctx Eternal',
              'mkctx Ephemeral',
              'touch AnActionEternal',
              'chctx Eternal AnActionEternal',
              'touch AnActionEphemeral',
              'chctx Ephemeral AnActionEphemeral',
              'echo pwd:',
              'pwd',
              'echo Errors out:',
              'mkdir errF0',
              'echo Errors out 2:',
              'mkprj errP0',
              'echo Errors out 3:',
              'mkdir /inbox/errF1',
              'echo Errors out 4:',
              'mkprj /inbox/errP1',
              'cd /',
              'mkdir F0',
              'cd F0',
              'mkdir F1',
              'cd F1',
              'mkprj P0',
              'cd P0',
              'touch AnotherActionEphemeral',
              'chctx Ephemeral AnotherActionEphemeral',
              'mkctx Foo',
              'echo lsctx:',
              'lsctx',
              'echo rmctx Foo:',
              'rmctx Foo',
              'echo lsctx2:',
              'lsctx',
              'mkctx InactiveCtx',
              'deactivatectx InactiveCtx',
              'echo lsctx3:',
              'lsctx',
              'echo rmctx InactiveCtx',
              'rmctx InactiveCtx',
              'echo lsctx4:',
              'lsctx',
              'echo dump:',
              'dump',
              'echo rmctx Ephemeral:',
              'rmctx Ephemeral',
              'echo lsctx5:',
              'lsctx',
              'view all_even_deleted',
              'echo lsctx6 with deleted:',
              'lsctx',
              'echo dump after rmctx Ephemeral:',
              'dump',
              ]
    golden_printed = [
      'pwd:',
      '/inbox',
      'Errors out:',
      'Cannot make a project or folder beneath /inbox',
      'Errors out 2:',
      'Cannot make a project or folder beneath /inbox',
      'Errors out 3:',
      'Cannot make a project or folder beneath /inbox',
      'Errors out 4:',
      'Cannot make a project or folder beneath /inbox',
      'lsctx:',
      "--context-- ---active--- '<none>'",
      '--context-- ---active--- Eternal',
      '--context-- ---active--- Ephemeral',
      '--context-- ---active--- Foo',
      'rmctx Foo:',
      'lsctx2:',
      "--context-- ---active--- '<none>'",
      '--context-- ---active--- Eternal',
      '--context-- ---active--- Ephemeral',
      'lsctx3:',
      "--context-- ---active--- '<none>'",
      '--context-- ---active--- Eternal',
      '--context-- ---active--- Ephemeral',
      '--context-- --INACTIVE-- InactiveCtx',
      'rmctx InactiveCtx',
      'lsctx4:',
      "--context-- ---active--- '<none>'",
      '--context-- ---active--- Eternal',
      '--context-- ---active--- Ephemeral',
      'dump:',
      r"""<todolist>
    <inbox>
        <project is_deleted="False" is_complete="False" is_active="True" name="inbox">
            <action is_deleted="False" is_complete="False" name="AnActionEternal" ctx="uid=4"/>
            <action is_deleted="False" is_complete="False" name="AnActionEphemeral" ctx="uid=5"/>
        </project>
    </inbox>
    <folder is_deleted="False" name="">
        <folder is_deleted="False" name="F0">
            <folder is_deleted="False" name="F1">
                <project is_deleted="False" is_complete="False" is_active="True" name="P0">
                    <action is_deleted="False" is_complete="False" name="AnotherActionEphemeral" ctx="uid=5"/>
                </project>
            </folder>
        </folder>
    </folder>
    <contexts>
        <context_list is_deleted="False" name="Contexts">
            <context is_deleted="False" is_active="True" name="Eternal"/>
            <context is_deleted="False" is_active="True" name="Ephemeral"/>
            <context is_deleted="True" is_active="True" name="Foo-deleted-at-122.0"/>
            <context is_deleted="True" is_active="False" name="InactiveCtx-deleted-at-122.0"/>
        </context_list>
    </contexts>
</todolist>""",
      'rmctx Ephemeral:',
      'lsctx5:',
      "--context-- ---active--- '<none>'",
      '--context-- ---active--- Eternal',
      'lsctx6 with deleted:',
      "--context-- ---active--- '<none>'",
      '--context-- ---active--- Eternal',
      '--context-- --DELETED-- ---active--- Ephemeral-deleted-at-122.0',
      '--context-- --DELETED-- ---active--- Foo-deleted-at-122.0',
      '--context-- --DELETED-- --INACTIVE-- InactiveCtx-deleted-at-122.0',
      'dump after rmctx Ephemeral:',
      r"""<todolist>
    <inbox>
        <project is_deleted="False" is_complete="False" is_active="True" name="inbox">
            <action is_deleted="False" is_complete="False" name="AnActionEternal" ctx="uid=4"/>
            <action is_deleted="False" is_complete="False" name="AnActionEphemeral" ctx=""/>
        </project>
    </inbox>
    <folder is_deleted="False" name="">
        <folder is_deleted="False" name="F0">
            <folder is_deleted="False" name="F1">
                <project is_deleted="False" is_complete="False" is_active="True" name="P0">
                    <action is_deleted="False" is_complete="False" name="AnotherActionEphemeral" ctx=""/>
                </project>
            </folder>
        </folder>
    </folder>
    <contexts>
        <context_list is_deleted="False" name="Contexts">
            <context is_deleted="False" is_active="True" name="Eternal"/>
            <context is_deleted="True" is_active="True" name="Ephemeral-deleted-at-122.0"/>
            <context is_deleted="True" is_active="True" name="Foo-deleted-at-122.0"/>
            <context is_deleted="True" is_active="False" name="InactiveCtx-deleted-at-122.0"/>
        </context_list>
    </contexts>
</todolist>""",
      ]
    self.helpTest(inputs, golden_printed)

  def testRmprj(self):
    inputs = [
      'chclock 1137888',
      'mkprj P',
      'cd P',
      'rmprj .',
      'pwd',
      'ls -a /P',
      ]
    golden_printed = [
      '/P',
      '--project-- --DELETED-- --incomplete-- ---active--- .',
      '--folder--- ..',
      ]
    self.helpTest(inputs, golden_printed)

  def testRmdirAndViews(self):
    inputs = [
      'chclock 1137888',
      'mkdir foo',
      'echo ls -l 1:',
      'ls -l',
      'chclock +1',
      'rmdir foo',
      'view all_even_deleted',
      'echo ls -l 2 even deleted:',
      'ls -l',
      'view actionable',
      'echo ls -l 3 actionable:',
      'ls -l',
      ]
    golden_printed = [
      'ls -l 1:',
      '--project-- mtime=1969/12/31-19:00:36 ctime=1969/12/31-19:00:36 --incomplete-- ---active--- inbox',
      '--folder--- mtime=1970/01/13-23:04:48 ctime=1970/01/13-23:04:48 foo',
      'ls -l 2 even deleted:',
      '--project-- mtime=1969/12/31-19:00:36 ctime=1969/12/31-19:00:36 --incomplete-- ---active--- inbox',
      '--folder--- --DELETED-- mtime=1970/01/13-23:04:49 ctime=1970/01/13-23:04:48 dtime=1970/01/13-23:04:49 foo',
      'ls -l 3 actionable:',
      '--project-- mtime=1969/12/31-19:00:36 ctime=1969/12/31-19:00:36 --incomplete-- ---active--- inbox',
      ]
    self.helpTest(inputs, golden_printed)

  def testMvUid(self):
    FLAGS.pyatdl_show_uid = True
    inputs = [
      'chclock 1137008',
      'mkprj P0',  # uid=4
      'mkact /inbox/i1',
      'ls -R /',
      'echo after ls',
      'mv uid=5 uid=4',
      'ls -R /',
      'echo after ls 2',
      ]
    golden_printed = [
      '--project-- uid=1 --incomplete-- ---active--- inbox',
      '--project-- uid=4 --incomplete-- ---active--- P0',
      '',
      '/inbox:',
      '--action--- uid=5 --incomplete-- i1 --in-context-- \'<none>\'',
      '',
      '/P0:',
      'after ls',
      '--project-- uid=1 --incomplete-- ---active--- inbox',
      '--project-- uid=4 --incomplete-- ---active--- P0',
      '',
      '/inbox:',
      '',
      '/P0:',
      '--action--- uid=5 --incomplete-- i1 --in-context-- \'<none>\'',
      'after ls 2',
      ]
    self.helpTest(inputs, golden_printed)

  def testRenameUidInVariousDirectories(self):
    FLAGS.pyatdl_show_uid = True
    inputs = [
      'chclock 1137008',
      'cd /inbox',
      'mkact foo',
      'echo ls:',
      'ls',
      'cd /',
      'rename uid=4 foof',
      'echo ls2:',
      'ls -R',
      ]
    golden_printed = [
      'ls:',
      '--action--- uid=4 --incomplete-- foo --in-context-- \'<none>\'',
      'ls2:',
      '--project-- uid=1 --incomplete-- ---active--- inbox',
      '',
      './inbox:',
      '--action--- uid=4 --incomplete-- foof --in-context-- \'<none>\'',
      ]
    self.helpTest(inputs, golden_printed)

  def testRenameCtxThenLsact(self):
    FLAGS.pyatdl_show_uid = True
    inputs = [
      'chclock 1137008',
      'mkctx c',
      'mkact -c c /inbox/a',
      'echo ls -R:',
      'ls -R',
      'echo lsctx',
      'lsctx',
      'rename uid=4 C',
      'echo lsact:',
      'lsact --json uid=5',
      ]
    golden_printed = [
      'ls -R:',
      '--project-- uid=1 --incomplete-- ---active--- inbox',
      '',
      './inbox:',
      '--action--- uid=5 --incomplete-- a --in-context-- c',
      'lsctx',
      "--context-- uid=0 ---active--- '<none>'",
      '--context-- uid=4 ---active--- c',
      'lsact:',
      '{"ctime":1137008.0,"display_project_path":"inbox","dtime":null,"in_context":"C","in_context_uid":4,"is_complete":false,"is_deleted":false,"mtime":1137008.0,"name":"a","number_of_items":1,"project_path":"/inbox","project_uid":1,"uid":5}',
      ]
    self.helpTest(inputs, golden_printed)

  def testUidParsing(self):
    FLAGS.pyatdl_show_uid = True
    inputs = [
      'chclock 1137008',
      'mkctx Ca',  # uid=4
      'echo rmctx Error:',
      'rmctx uid=1',  # That's /inbox
      'mkctx Cb',  # uid=5
      'cd /inbox',
      'mkact Aa',  # uid=6
      'chctx Cb Aa',
      'echo Err chctx -1:',
      'chctx uid=-1 Aa',
      'echo Err chctx 999:',
      'chctx uid=999 Aa',
      'cd /',
      'mkdir Fa',
      'cd Fa',
      'mkdir Faa',
      'cd Faa',
      'mkprj PFaa',
      'deactivateprj uid=9',
      'echo gist1:',
      'dump -m',
      'echo end gist1',
      'echo inctx via uid:',
      'inctx uid=5',
      'echo inctx via name:',
      'inctx Cb',
      'echo [de]activatectx via UID:',
      'activatectx uid=4',
      'deactivatectx uid=5',
      'cd -R Faa',
      'completereview uid=9',
      'echo Err991:',
      'completereview uid=991',
      'cd /inbox',
      'complete uid=6',
      'uncomplete uid=6',
      'cd /',
      'echo root:',
      'pwd',
      'cd uid=2',
      'echo [x2] /:',
      'pwd',
      'cd -R uid=8',
      'echo Faa',
      'pwd',
      'cd /',
      'cd Fa',
      'echo Error undeleted descendant:',
      'rmdir Faa',
      'echo Err2:',
      'rmdir uid=998',
      'echo Success is an error:',
      'rmdir uid=8',
      'cd Faa',
      'rmprj uid=9',  # PFaa
      'mkprj Pdupename',
      'mkprj Pdupename',
      'rmprj Pdupename',
      'rmprj Pdupename',
      'echo ls600:',
      'ls',
      'configurereview --max_seconds_before_review=8.0 uid=11',
      'rmprj uid=11',
      'cd /inbox',
      'echo ls -l /inbox shows UIDs:',
      'ls -l',
      'echo ls shows UIDs:',
      'ls',
      'echo lsctx shows UIDs:',
      'lsctx',
      'echo rmctx uid=4',
      'rmctx uid=4',
      'echo lsctx 100:',
      'lsctx',
      'cd -R Faa',
      'activateprj uid=9',
      'echo rename error nosuchleft:',
      'rename uid=989 foo',
      'echo rename success:',
      'rename uid=9 wasPFaa',
      'echo rename error badsyntaxright:',
      'rename wasPFaa uid=990',
      'cd uid=1',
      'rmact uid=6',
      'echo gistEnd:',  # shows that rmprj worked
      'dump -m',
      'echo end gistEnd',
      'echo FIN',
      ]
    golden_printed = [
      'rmctx Error:',
      'No such context "uid=1".  Your choices: Ca',
      'Err chctx -1:',
      'Illegal "uid" syntax. Correct syntax: uid=N where N is a positive, decimal integer',
      'Err chctx 999:',
      'No such Context "uid=999"',
      'gist1:',
      '<todolist uid=2>',
      '    <inbox uid=1>',
      '        <project uid=1 is_deleted="False" is_complete="False" is_active="True" name="inbox">',
      '            <action uid=6 is_deleted="False" is_complete="False" name="Aa" ctx="uid=5"/>',
      '        </project>',
      '    </inbox>',
      '    <folder uid=2 is_deleted="False" name="">',
      '        <folder uid=7 is_deleted="False" name="Fa">',
      '            <folder uid=8 is_deleted="False" name="Faa">',
      '                <project uid=9 is_deleted="False" is_complete="False" is_active="False" name="PFaa">',
      '                ',
      '                </project>',
      '            </folder>',
      '        </folder>',
      '    </folder>',
      '    <contexts>',
      '        <context_list uid=3 is_deleted="False" name="Contexts">',
      '            <context uid=4 is_deleted="False" is_active="True" name="Ca"/>',
      '            <context uid=5 is_deleted="False" is_active="True" name="Cb"/>',
      '        </context_list>',
      '    </contexts>',
      '</todolist>',
      'end gist1',
      'inctx via uid:',
      '--action--- uid=6 --incomplete-- Aa',
      'inctx via name:',
      '--action--- uid=6 --incomplete-- Aa',
      '[de]activatectx via UID:',
      'Err991:',
      'No Project exists with UID 991',
      'root:',
      '/',
      '[x2] /:',
      '/',
      'Faa',
      '/Fa/Faa',
      'Error undeleted descendant:',
      'Cannot delete because a descendant is not deleted.  descendant=\n<project uid=9 is_deleted="False" is_complete="False" is_active="False" name="PFaa">\n\n</project>',
      'Err2:',
      'No Folder exists with UID 998',
      'Success is an error:',
      'Cannot delete because a descendant is not deleted.  descendant=\n<project uid=9 is_deleted="False" is_complete="False" is_active="False" name="PFaa">\n\n</project>',
      'ls600:',
      'ls -l /inbox shows UIDs:',
      '--action--- mtime=1970/01/13-22:50:08 ctime=1970/01/13-22:50:08 uid=6 --incomplete-- Aa --in-context-- Cb',
      'ls shows UIDs:',
      '--action--- uid=6 --incomplete-- Aa --in-context-- Cb',
      'lsctx shows UIDs:',
      '--context-- uid=0 ---active--- \'<none>\'',
      '--context-- uid=4 ---active--- Ca',
      '--context-- uid=5 --INACTIVE-- Cb',
      'rmctx uid=4',
      'lsctx 100:',
      '--context-- uid=0 ---active--- \'<none>\'',
      '--context-- uid=5 --INACTIVE-- Cb',
      'rename error nosuchleft:',
      'No item named "uid=989" exists in the current working Folder/Project (see "help pwd").  Choices: PFaa Pdupename Pdupename',
      'rename success:',
      'rename error badsyntaxright:',
      'Bad syntax for right-hand side: Names starting with "uid=" are prohibited.',
      'gistEnd:',
      '<todolist uid=2>',
      '    <inbox uid=1>',
      '        <project uid=1 is_deleted="False" is_complete="False" is_active="True" name="inbox">',
      '            <action uid=6 is_deleted="True" is_complete="False" name="Aa" ctx="uid=5"/>',
      '        </project>',
      '    </inbox>',
      '    <folder uid=2 is_deleted="False" name="">',
      '        <folder uid=7 is_deleted="False" name="Fa">',
      '            <folder uid=8 is_deleted="False" name="Faa">',
      '                <project uid=9 is_deleted="True" is_complete="False" is_active="True" name="wasPFaa">',
      '                ',
      '                </project>',
      '                <project uid=10 is_deleted="True" is_complete="False" is_active="True" name="Pdupename">',
      '                ',
      '                </project>',
      '                <project uid=11 is_deleted="True" is_complete="False" is_active="True" max_seconds_before_review="8.0" name="Pdupename">',
      '                ',
      '                </project>',
      '            </folder>',
      '        </folder>',
      '    </folder>',
      '    <contexts>',
      '        <context_list uid=3 is_deleted="False" name="Contexts">',
      '            <context uid=4 is_deleted="True" is_active="True" name="Ca-deleted-at-1137008.0"/>',
      '            <context uid=5 is_deleted="False" is_active="False" name="Cb"/>',
      '        </context_list>',
      '    </contexts>',
      '</todolist>',
      'end gistEnd',
      'FIN',
      ]
    self.helpTest(inputs, golden_printed)

  def testHelp(self):
    inputs = [
      'help',
      '? pwd',
      '? nonexistentcmd',
      'help ls',
      ]
    golden_printed = [
      'Welcome!',
      '',
      'To exit and save, use the "exit" command (alternatively,',
      'press Control-D to trigger end-of-file (EOF)).',
      '',
      'Some core concepts follow:',
      '* A Folder contains Folders and Projects.',
      '  It is like a directory in a file system.',
      '* A Project contains Actions.',
      '* An Action may have a Context.',
      '* A Context is designed to show you ONLY Actions you can perform right now.',
      '  An inactive Context (e.g., WaitingFor or SomedayMaybe) houses',
      '  Actions that need to be reviewed but cannot be acted on.',
      '  (E.g., reviewing WaitingFor items, you will find some that are old ',
      '  enough to require follow-up.)',
      '',
      r"""Commands:
  * ?
  * activatectx
  * activateprj
  * aspire
  * astaskpaper
  * cat
  * cd
  * chclock
  * chctx
  * chdefaultctx
  * clearreview
  * complete
  * completereview
  * configurereview
  * deactivatectx
  * deactivateprj
  * deletecompleted
  * do
  * dump
  * dumpprotobuf
  * echo
  * echolines
  * exit
  * help
  * hypertext
  * inctx
  * inprj
  * load
  * loadtest
  * ls
  * lsact
  * lsctx
  * lsprj
  * maybe
  * mkact
  * mkctx
  * mkdir
  * mkprj
  * mv
  * needsreview
  * note
  * prjify
  * purgedeleted
  * pwd
  * quit
  * redo
  * rename
  * renamectx
  * reset
  * rm
  * rmact
  * rmctx
  * rmdir
  * rmprj
  * roll
  * save
  * seed
  * sort
  * todo
  * touch
  * txt
  * uncomplete
  * undo
  * unicorn
  * view""",
      '',
      'For help on a specific command, type "help cmd".',
      'Prints the current working "directory" if you will, a Folder or a Project.',
      'No such command "nonexistentcmd"; try "help" for a list of all commands.',
      r"""Lists immediate contents of the current working Folder/Project (see "help pwd").

The 'view' command (see 'help view') controls which items are visible. 'ls -a'
ignores the view filter and shows all items, including '.', the working
directory, and '..', its parent.

The following timestamps are displayed when the '-l' argument is given:

* ctime: Time of creation
* mtime: Time of last modification
* dtime: Time of deletion

Flags for ls:

pyatdllib.ui.uicmd:
-R,--[no]recursive: Additionally lists subdirectories/subprojects recursively
(default: 'false')
-a,--[no]show_all: Additionally lists everything, even hidden objects, overriding the view filter
(default: 'false')
-l,--[no]show_timestamps: Additionally lists timestamps ctime, dtime, mtime
(default: 'false')
-v,--view_filter: <actionable|all|all_even_deleted|default|inactive_and_incomplete|incomplete|needing_review>: Instead of using the global view filter (see "help view"), override
it and use this view filter. Note: this is ignored in --show_all mode""",
      ]
    self.helpTest(inputs, golden_printed)

  def testLsDashR(self):
    inputs = [
      'cd /inbox',
      'touch inboxa',
      'cd /',
      'mkdir P0',
      'cd P0',
      'mkprj P0p',
      'mkdir P1',
      'cd P1',
      'mkprj P1p',
      'mkprj P2',
      'cd P2',
      'touch P2a',
      'cd ..',
      'mkdir fooInP1',
      'cd /',
      'mkdir D0',
      'cd D0',
      'mkprj D0p',
      'mkdir D1',
      'cd D1',
      'mkprj D1p',
      'cd ..',
      'mkprj PnexttoD1',
      'cd PnexttoD1',
      'touch PnexttoD1a',
      'echo ls:',
      'ls',
      'echo ls -R:',
      'ls -R',
      'cd /',
      'echo ls -R from /:',
      'ls -R',
      ]
    golden_printed = [
      'ls:',
      '--action--- --incomplete-- PnexttoD1a --in-context-- \'<none>\'',
      'ls -R:',
      '--action--- --incomplete-- PnexttoD1a --in-context-- \'<none>\'',
      'ls -R from /:',
      '--project-- --incomplete-- ---active--- inbox',
      '--folder--- P0',
      '--folder--- D0',
      '',
      './inbox:',
      '--action--- --incomplete-- inboxa --in-context-- \'<none>\'',
      '',
      './P0:',
      '--project-- --incomplete-- ---active--- P0p',
      '--folder--- P1',
      '',
      './P0/P0p:',
      '',
      './P0/P1:',
      '--project-- --incomplete-- ---active--- P1p',
      '--project-- --incomplete-- ---active--- P2',
      '--folder--- fooInP1',
      '',
      './P0/P1/P1p:',
      '',
      './P0/P1/P2:',
      '--action--- --incomplete-- P2a --in-context-- \'<none>\'',
      '',
      './P0/P1/fooInP1:',
      '',
      './D0:',
      '--project-- --incomplete-- ---active--- D0p',
      '--folder--- D1',
      '--project-- --incomplete-- ---active--- PnexttoD1',
      '',
      './D0/D0p:',
      '',
      './D0/D1:',
      '--project-- --incomplete-- ---active--- D1p',
      '',
      './D0/D1/D1p:',
      '',
      './D0/PnexttoD1:',
      '--action--- --incomplete-- PnexttoD1a --in-context-- \'<none>\'',
      ]
    self.helpTest(inputs, golden_printed)

  def testVarious2(self):
    inputs = [
      'chclock 1137999',
      'mkctx Ca',
      'cd /',
      'mkprj Pa',
      'mkdir Fb',
      'cd Fb',
      'mkdir Fbb',
      'cd Fbb',
      'mkprj Pbb',
      'mkdir oow',
      'cd Pbb',
      'touch "an action"',
      'touch foo',
      'complete "an action"',
      'cd /',
      'cd -R Pbb',
      'cd ..',
      'echo ls default view:',
      'ls',
      'view all_even_deleted',
      'echo ls all_even_deleted:',
      'ls',
      'rmdir oow',
      'echo pwd:',
      'pwd',
      'cd Pbb',
      'rmact \'an action\'',
      'rmact foo',
      'cd ..',
      'rmprj Pbb',
      'cd ..',
      'echo rmdir Fbb:',
      'rmdir Fbb',
      'echo ls2:',
      'ls',
      'echo pwd2:',
      'pwd',
      'cd ..',
      'echo ls3:',
      'ls',
      'echo ls default view2:',
      'view default',
      'ls',
      'rmdir Fb',
      'echo dump:',
      'dump',
      ]
    golden_printed = [
      'ls default view:',
      '--project-- --incomplete-- ---active--- Pbb',
      '--folder--- oow',
      'ls all_even_deleted:',
      '--project-- --incomplete-- ---active--- Pbb',
      '--folder--- oow',
      'pwd:',
      '/Fb/Fbb',
      'rmdir Fbb:',
      'ls2:',
      '--folder--- --DELETED-- Fbb',
      'pwd2:',
      '/Fb',
      'ls3:',
      '--project-- --incomplete-- ---active--- inbox',
      '--project-- --incomplete-- ---active--- Pa',
      '--folder--- Fb',
      'ls default view2:',
      '--project-- --incomplete-- ---active--- inbox',
      '--project-- --incomplete-- ---active--- Pa',
      '--folder--- Fb',
      'dump:',
r"""<todolist>
    <inbox>
        <project is_deleted="False" is_complete="False" is_active="True" name="inbox">
        
        </project>
    </inbox>
    <folder is_deleted="False" name="">
        <project is_deleted="False" is_complete="False" is_active="True" name="Pa">
        
        </project>
        <folder is_deleted="True" name="Fb">
            <folder is_deleted="True" name="Fbb">
                <project is_deleted="True" is_complete="False" is_active="True" name="Pbb">
                    <action is_deleted="True" is_complete="True" name="an action" ctx=""/>
                    <action is_deleted="True" is_complete="False" name="foo" ctx=""/>
                </project>
                <folder is_deleted="True" name="oow">
                
                </folder>
            </folder>
        </folder>
    </folder>
    <contexts>
        <context_list is_deleted="False" name="Contexts">
            <context is_deleted="False" is_active="True" name="Ca"/>
        </context_list>
    </contexts>
</todolist>"""
      ]
    self.helpTest(inputs, golden_printed)

  def testinboxProjectIsHandledWellByAllCommands(self):
    # TODO(chandler): Test all relevant commands, not just the ones tested below.
    inputs = ['cd /inbox',
              'touch AninboxAction',
              'echo First ls -a is as follows:',
              'ls -a',
              'mkctx C0',
              'chctx C0 AninboxAction',
              'echo Second ls -a:',
              'ls -a',
              'cd /',
              'echo rmdir inbox:',
              'rmdir inbox',
              'echo Third ls -a:',
              'ls -a',
              'rmprj inbox',
              'echo Fourth ls -a:',
              'ls -a',
              'echo Complete inbox:',
              'complete inbox',
              'echo Fifth ls -a:',
              'ls -a',
              'echo Uncomplete inbox:',
              'uncomplete inbox',
              'echo Sixth ls -a:',
              'ls -a',
              ]
    golden_printed = [
      'First ls -a is as follows:',
      '--project-- --incomplete-- ---active--- .',
      '--folder--- ..',
      '--action--- --incomplete-- AninboxAction --in-context-- \'<none>\'',
      'Second ls -a:',
      '--project-- --incomplete-- ---active--- .',
      '--folder--- ..',
      '--action--- --incomplete-- AninboxAction --in-context-- C0',
      'rmdir inbox:',
      'No such Folder "inbox". There are no Folders within the specified Folder.',
      'Third ls -a:',
      '--folder--- .',
      '--folder--- ..',
      '--project-- --incomplete-- ---active--- inbox',
      'The project /inbox is special; it cannot be removed.',
      'Fourth ls -a:',
      '--folder--- .',
      '--folder--- ..',
      '--project-- --incomplete-- ---active--- inbox',
      'Complete inbox:',
      'The project /inbox is special and cannot be marked complete.',
      'Fifth ls -a:',
      '--folder--- .',
      '--folder--- ..',
      '--project-- --incomplete-- ---active--- inbox',
      'Uncomplete inbox:',
      'Sixth ls -a:',
      '--folder--- .',
      '--folder--- ..',
      '--project-- --incomplete-- ---active--- inbox',
      ]
    self.helpTest(inputs, golden_printed)

  def testVarious(self):
    def HelpHelpTest(inputs, golden):
      self.helpTest(['chclock 111'] + inputs, golden)

    inputs = ['mkprj Pa',
              'ls -a',
              'cd Pa',
              'ls -a',
              'pwd',
              ]
    golden_printed = ['--folder--- .',
                      '--folder--- ..',
                      '--project-- --incomplete-- ---active--- inbox',
                      '--project-- --incomplete-- ---active--- Pa',
                      '--project-- --incomplete-- ---active--- .',
                      '--folder--- ..',
                      '/Pa',
                      ]
    HelpHelpTest(inputs, golden_printed)
    HelpHelpTest(['dump'], [r"""
<todolist>
    <inbox>
        <project is_deleted="False" is_complete="False" is_active="True" name="inbox">
        
        </project>
    </inbox>
    <folder is_deleted="False" name="">
        <project is_deleted="False" is_complete="False" is_active="True" name="Pa">
        
        </project>
    </folder>
    <contexts>
        <context_list is_deleted="False" name="Contexts">
        
        </context_list>
    </contexts>
</todolist>
""".strip()])
    HelpHelpTest(['cd .'], [])

    HelpHelpTest(
      ['mkctx Ca',
       'dump'],
      [r"""
<todolist>
    <inbox>
        <project is_deleted="False" is_complete="False" is_active="True" name="inbox">
        
        </project>
    </inbox>
    <folder is_deleted="False" name="">
        <project is_deleted="False" is_complete="False" is_active="True" name="Pa">
        
        </project>
    </folder>
    <contexts>
        <context_list is_deleted="False" name="Contexts">
            <context is_deleted="False" is_active="True" name="Ca"/>
        </context_list>
    </contexts>
</todolist>
""".strip()])

    HelpHelpTest(
      ['cd /',
       'mkdir Fb',
       'cd Fb',
       'mkdir Fbb',
       'cd Fbb',
       'mkprj Pbb',
       'cd Pbb',
       'touch "an action"',
       'dump'
       ],
      [r"""
<todolist>
    <inbox>
        <project is_deleted="False" is_complete="False" is_active="True" name="inbox">
        
        </project>
    </inbox>
    <folder is_deleted="False" name="">
        <project is_deleted="False" is_complete="False" is_active="True" name="Pa">
        
        </project>
        <folder is_deleted="False" name="Fb">
            <folder is_deleted="False" name="Fbb">
                <project is_deleted="False" is_complete="False" is_active="True" name="Pbb">
                    <action is_deleted="False" is_complete="False" name="an action" ctx=""/>
                </project>
            </folder>
        </folder>
    </folder>
    <contexts>
        <context_list is_deleted="False" name="Contexts">
            <context is_deleted="False" is_active="True" name="Ca"/>
        </context_list>
    </contexts>
</todolist>
""".strip()])

    HelpHelpTest(['lsctx'],
                 ['--context-- ---active--- \'<none>\'',
                  '--context-- ---active--- Ca'])
    HelpHelpTest(['activatectx Ca', 'lsctx'],
                 ['--context-- ---active--- \'<none>\'',
                  '--context-- ---active--- Ca'])
    HelpHelpTest(['deactivatectx Ca', 'lsctx'],
                 ['--context-- ---active--- \'<none>\'',
                  '--context-- --INACTIVE-- Ca'])
    HelpHelpTest(['activatectx Ca', 'lsctx'],
                 ['--context-- ---active--- \'<none>\'',
                  '--context-- ---active--- Ca'])
    HelpHelpTest(['chctx Ca "/Fb/Fbb/Pbb/an action"', 'cd Fb', 'cd Fbb', 'cd Pbb', 'ls'],
                  ['--action--- --incomplete-- \'an action\' --in-context-- Ca'])
    HelpHelpTest(['inctx <none>'],
                  [])
    HelpHelpTest(['inctx Ca'],
                  ['--action--- --incomplete-- \'an action\''])
    HelpHelpTest(['cd /', 'chctx <none> "Fb/Fbb/Pbb/an action"', 'cd Fb', 'cd Fbb', 'cd Pbb', 'ls'],
                  ['--action--- --incomplete-- \'an action\' --in-context-- \'<none>\''])
    HelpHelpTest(['cd /', 'cd Fb/Fbb', 'complete "Pbb/an action"', 'cd /Fb', 'cd Fbb', 'cd Pbb', 'ls'],
                  ['--action--- ---COMPLETE--- \'an action\' --in-context-- \'<none>\''])
    HelpHelpTest(['uncomplete "/Fb/Fbb/Pbb/an action"', 'cd -R Pbb', 'ls'],
                  ['--action--- --incomplete-- \'an action\' --in-context-- \'<none>\''])
    HelpHelpTest(['inctx <none>'],
                  ['--action--- --incomplete-- \'an action\''])
    HelpHelpTest(['inctx uid=0'],
                  ['--action--- --incomplete-- \'an action\''])
    HelpHelpTest(['chclock 999999999', 'needsreview'],
                  ['/inbox', '/Pa', '/Fb/Fbb/Pbb'])
    HelpHelpTest(['chclock 999999999', 'needsreview --json'],
                  ['[{"ctime":36,"default_context_uid":0,"dtime":null,"is_active":true,"is_complete":false,"is_deleted":false,"mtime":36,"name":"inbox","needsreview":true,"number_of_items":0,"uid":1},{"ctime":111.0,"default_context_uid":0,"dtime":null,"is_active":true,"is_complete":false,"is_deleted":false,"mtime":111.0,"name":"Pa","needsreview":true,"number_of_items":0,"uid":4},{"ctime":111.0,"default_context_uid":0,"dtime":null,"is_active":true,"is_complete":false,"is_deleted":false,"mtime":111.0,"name":"Pbb","needsreview":true,"number_of_items":1,"uid":8}]'])
    HelpHelpTest(['chclock 999999998', 'completereview /Fb/Fbb/Pbb'],
                  [])
    # TODO(chandler): Should we treat the review of the inbox specially? You
    # might argue that the review is not complete until the inbox is empty.
    HelpHelpTest(['chclock 999999998', 'completereview inbox'],
                  [])
    HelpHelpTest(['chclock 999999999', 'needsreview'],
                  ['/Pa'])
    HelpHelpTest(['completereview /Pa'],
                  [])
    HelpHelpTest(['needsreview'],
                  [])

  def testLoadtest(self):
    FLAGS.pyatdl_show_uid = True
    inputs = ['loadtest -n 0',
              'ls -R /',
              'echo after ls after NOP',
              'loadtest --name="N A M E" -n 2',
              'ls -R /',
              'echo after ls -R /',
              'lsctx',
              'loadtest --n 1',  # tests default args
              ]
    golden_printed = [
      '--project-- uid=1 --incomplete-- ---active--- inbox',
      '',
      '/inbox:',
      'after ls after NOP',
      '--project-- uid=1 --incomplete-- ---active--- inbox',
      '--folder--- uid=5 \'FN A M E0\'',
      '--folder--- uid=9 \'FN A M E1\'',
      '--folder--- uid=12 \'DeepFolderN A M E0\'',
      '',
      '/inbox:',
      '--action--- uid=16 --incomplete-- \'AinboxN A M E0\' --in-context-- \'<none>\'',
      '--action--- uid=17 --incomplete-- \'AinboxN A M E1\' --in-context-- \'<none>\'',
      '--action--- uid=18 --incomplete-- \'ALongNameN A M EN A M E\' --in-context-- \'<none>\'',
      '',
      '/FN A M E0:',
      '--project-- uid=6 --incomplete-- ---active--- \'PN A M E0\'',
      '',
      '/FN A M E0/PN A M E0:',
      '--action--- uid=7 --incomplete-- \'AN A M E0\' --in-context-- \'<none>\'',
      '',
      '/FN A M E1:',
      '--project-- uid=10 --incomplete-- ---active--- \'PN A M E1\'',
      '',
      '/FN A M E1/PN A M E1:',
      '--action--- uid=11 --incomplete-- \'AN A M E1\' --in-context-- \'<none>\'',
      '',
      '/DeepFolderN A M E0:',
      '--folder--- uid=13 \'DeepFolderN A M E1\'',
      '',
      '/DeepFolderN A M E0/DeepFolderN A M E1:',
      '--project-- uid=14 --incomplete-- ---active--- DeepProject',
      '',
      '/DeepFolderN A M E0/DeepFolderN A M E1/DeepProject:',
      '--action--- uid=15 --incomplete-- DeepAction --in-context-- \'<none>\'',
      'after ls -R /',
      "--context-- uid=0 ---active--- '<none>'",
      '--context-- uid=4 ---active--- \'CN A M E0\'',
      '--context-- uid=8 ---active--- \'CN A M E1\'',
      ]
    self.helpTest(inputs, golden_printed)

  def testRmctxTwice(self):
    FLAGS.pyatdl_show_uid = True
    inputs = ['chclock 1000',
              'mkctx c',
              'rmctx c',
              'view all_even_deleted',
              'echo lsctx:',
              'lsctx',
              'chclock 2000',
              'rmctx uid=4',
              'echo lsctx2:',
              'lsctx',
              ]
    golden_printed = [
      'lsctx:',
      '--context-- uid=0 ---active--- \'<none>\'',
      '--context-- uid=4 --DELETED-- ---active--- c-deleted-at-1000.0',
      'lsctx2:',
      '--context-- uid=0 ---active--- \'<none>\'',
      '--context-- uid=4 --DELETED-- ---active--- c-deleted-at-1000.0',
    ]
    self.helpTest(inputs, golden_printed)

  def testUndoRedo1(self):
    # See state_test.py for the majority of test cases. Here we just test that
    # the plumbing works.
    FLAGS.pyatdl_show_uid = True
    inputs = ['mkprj Pa',
              'undo',
              'mkprj Pa',
              'dump -m',
              'echo redo:',
              'redo',
              'reset --annihilate',
              'mkprj Pa',
              'undo',
              'echo undo fail:',
              'undo',
              ]
    golden_printed = [
      '<todolist uid=2>',
      '    <inbox uid=1>',
      '        <project uid=1 is_deleted="False" is_complete="False" is_active="True" name="inbox">',
      '        ',
      '        </project>',
      '    </inbox>',
      '    <folder uid=2 is_deleted="False" name="">',
      '        <project uid=4 is_deleted="False" is_complete="False" is_active="True" name="Pa">',
      '        ',
      '        </project>',
      '    </folder>',
      '    <contexts>',
      '        <context_list uid=3 is_deleted="False" name="Contexts">',
      '        ',
      '        </context_list>',
      '    </contexts>',
      '</todolist>',
      'redo:',
      'Nothing left to redo',
      'Reset complete.',
      'undo fail:',
      'There are no more operations to undo',
    ]
    self.helpTest(inputs, golden_printed)

  def testUndoRedo2(self):
    # Inspired by RemoveReferencesToContext, part of 'rmctx'. rmctx C touches
    # the actions in context C.
    FLAGS.pyatdl_show_uid = True
    inputs = ['chclock 77',
              'mkctx C',
              'mkprj P',
              'cd P',
              'touch -c uid=0 AwithoutContext',
              'touch -c uid=0 AinContextC',
              'chctx C AinContextC',
              'echo after construction',
              'dump -m',
              'echo before rmctx C',
              'rmctx C',
              'echo gist after rmctx:',
              'dump -m',
              'echo before undo',
              'undo',
              'echo after undo',
              'dump -m',
              'echo before successful redo:',
              'redo',
              'echo after that redo the gist is:',
              'dump -m',
              'echo failure:',
              'redo',
              ]
    final_gist = ['<todolist uid=2>',
      '    <inbox uid=1>',
      '        <project uid=1 is_deleted="False" is_complete="False" is_active="True" name="inbox">',
      '        ',
      '        </project>',
      '    </inbox>',
      '    <folder uid=2 is_deleted="False" name="">',
      '        <project uid=5 is_deleted="False" is_complete="False" is_active="True" name="P">',
      '            <action uid=6 is_deleted="False" is_complete="False" name="AwithoutContext" ctx=""/>',
      '            <action uid=7 is_deleted="False" is_complete="False" name="AinContextC" ctx=""/>',
      '        </project>',
      '    </folder>',
      '    <contexts>',
      '        <context_list uid=3 is_deleted="False" name="Contexts">',
      '            <context uid=4 is_deleted="True" is_active="True" name="C-deleted-at-77.0"/>',
      '        </context_list>',
      '    </contexts>',
      '</todolist>',
      ]
    golden_printed = [
      'after construction',
      '<todolist uid=2>',
      '    <inbox uid=1>',
      '        <project uid=1 is_deleted="False" is_complete="False" is_active="True" name="inbox">',
      '        ',
      '        </project>',
      '    </inbox>',
      '    <folder uid=2 is_deleted="False" name="">',
      '        <project uid=5 is_deleted="False" is_complete="False" is_active="True" name="P">',
      '            <action uid=6 is_deleted="False" is_complete="False" name="AwithoutContext" ctx=""/>',
      '            <action uid=7 is_deleted="False" is_complete="False" name="AinContextC" ctx="uid=4"/>',
      '        </project>',
      '    </folder>',
      '    <contexts>',
      '        <context_list uid=3 is_deleted="False" name="Contexts">',
      '            <context uid=4 is_deleted="False" is_active="True" name="C"/>',
      '        </context_list>',
      '    </contexts>',
      '</todolist>',
      'before rmctx C',
      'gist after rmctx:',
      ] + final_gist + [
      'before undo',
      'after undo',
      '<todolist uid=2>',
      '    <inbox uid=1>',
      '        <project uid=1 is_deleted="False" is_complete="False" is_active="True" name="inbox">',
      '        ',
      '        </project>',
      '    </inbox>',
      '    <folder uid=2 is_deleted="False" name="">',
      '        <project uid=5 is_deleted="False" is_complete="False" is_active="True" name="P">',
      '            <action uid=6 is_deleted="False" is_complete="False" name="AwithoutContext" ctx=""/>',
      '            <action uid=7 is_deleted="False" is_complete="False" name="AinContextC" ctx="uid=4"/>',
      '        </project>',
      '    </folder>',
      '    <contexts>',
      '        <context_list uid=3 is_deleted="False" name="Contexts">',
      '            <context uid=4 is_deleted="False" is_active="True" name="C"/>',
      '        </context_list>',
      '    </contexts>',
      '</todolist>',
      'before successful redo:',
      'after that redo the gist is:',
      ] + final_gist + [
      'failure:',
      'Nothing left to redo',
    ]
    self.helpTest(inputs, golden_printed)

  def testLsUid(self):
    FLAGS.pyatdl_show_uid = True
    inputs = ['chclock 37',
              'cd /inbox',
              'mkact "foo bar"',
              'echo ls',
              'ls',
              'echo ls "foo bar"',
              'ls "foo bar"',
              'echo ls "/inbox/foo bar"',
              'ls "/inbox/foo bar"',
              'echo ls uid=4',
              'ls uid=4',
              'mkctx C',
              'echo lsctx',
              'lsctx',
              'echo ls uid=5',
              'ls uid=5',
              'echo ls -l uid=5',
              'ls -l uid=5',
              'echo ls uid=0',
              'ls uid=0',
              ]
    golden_printed = [
      'ls',
      '--action--- uid=4 --incomplete-- \'foo bar\' --in-context-- \'<none>\'',
      'ls foo bar',
      '--action--- uid=4 --incomplete-- \'foo bar\' --in-context-- \'<none>\'',
      'ls /inbox/foo bar',
      '--action--- uid=4 --incomplete-- \'foo bar\' --in-context-- \'<none>\'',
      'ls uid=4',
      '--action--- uid=4 --incomplete-- \'foo bar\' --in-context-- \'<none>\'',
      'lsctx',
      '--context-- uid=0 ---active--- \'<none>\'',
      '--context-- uid=5 ---active--- C',
      'ls uid=5',
      '--context-- uid=5 ---active--- C',
      'ls -l uid=5',
      '--context-- mtime=1969/12/31-19:00:37 ctime=1969/12/31-19:00:37 uid=5 ---active--- C',
      'ls uid=0',
      'Illegal "uid" syntax. Correct syntax: uid=N where N is a positive, decimal integer',
      # TODO: Make it print out '--context-- uid=0 \'<none>\''
    ]
    self.helpTest(inputs, golden_printed)

  def testMkactAllowSlashes(self):
    FLAGS.pyatdl_show_uid = True
    inputs = ['chclock 77',
              'cd /inbox',
              'mkact --allow_slashes 07/13/2017',
              'mkact --allow_slashes /inbox/foo',
              'ls',
              ]
    golden_printed = [
      '--action--- uid=4 --incomplete-- 07/13/2017 --in-context-- \'<none>\'',
      '--action--- uid=5 --incomplete-- /inbox/foo --in-context-- \'<none>\'',
    ]
    self.helpTest(inputs, golden_printed)

  def testSeed(self):
    save_path = _CreateTmpFile('')
    inputs = ['chclock 77',
              'seed',
              'save %s' % pipes.quote(save_path),
              'load %s' % pipes.quote(save_path),
              'echo lsctx:',
              'lsctx',
              'echo ls:',
              'ls -R -v all_even_deleted',
              ]
    golden_printed = [
      'Save complete.',
      'Load complete.',
      'lsctx:',
      '--context-- ---active--- \'<none>\'',
      '--context-- ---active--- @computer',
      '--context-- ---active--- @phone',
      '--context-- ---active--- @home',
      '--context-- ---active--- @work',
      '--context-- ---active--- \'@the store\'',
      '--context-- --INACTIVE-- @someday/maybe',
      '--context-- --INACTIVE-- \'@waiting for\'',
      'ls:',
      '--project-- --incomplete-- ---active--- inbox',
      '--project-- --incomplete-- ---active--- miscellaneous',
      '--project-- --incomplete-- ---active--- \'learn how to use this to-do list\'',
      '',
      './inbox:',
      '',
      './miscellaneous:',
      '',
      './learn how to use this to-do list:',
      '--action--- --incomplete-- \'Watch the video on the "Help" page -- on the top navigation bar, find it underneath the "Other" drop-down\' --in-context-- \'<none>\'',
      '--action--- --incomplete-- \'Read the book "Getting Things Done" by David Allen\' --in-context-- \'<none>\'',
      '--action--- --incomplete-- \'After reading the book, try out a Weekly Review -- on the top navigation bar, find it underneath the "Other" drop-down\' --in-context-- \'<none>\'',
    ]
    self.helpTest(inputs, golden_printed)

  def testSeed2(self):
    FLAGS.seed_upon_creation = True
    inputs = ['chclock 77',
              'reset --annihilate',
              'echo lsctx:',
              'lsctx',
              'echo ls:',
              'ls -R -v all_even_deleted',
              ]
    golden_printed = [
      'Reset complete.',
      'lsctx:',
      '--context-- ---active--- \'<none>\'',
      '--context-- ---active--- @computer',
      '--context-- ---active--- @phone',
      '--context-- ---active--- @home',
      '--context-- ---active--- @work',
      '--context-- ---active--- \'@the store\'',
      '--context-- --INACTIVE-- @someday/maybe',
      '--context-- --INACTIVE-- \'@waiting for\'',
      'ls:',
      '--project-- --incomplete-- ---active--- inbox',
      '--project-- --incomplete-- ---active--- miscellaneous',
      '--project-- --incomplete-- ---active--- \'learn how to use this to-do list\'',
      '',
      './inbox:',
      '',
      './miscellaneous:',
      '',
      './learn how to use this to-do list:',
      '--action--- --incomplete-- \'Watch the video on the "Help" page -- on the top navigation bar, find it underneath the "Other" drop-down\' --in-context-- \'<none>\'',
      '--action--- --incomplete-- \'Read the book "Getting Things Done" by David Allen\' --in-context-- \'<none>\'',
      '--action--- --incomplete-- \'After reading the book, try out a Weekly Review -- on the top navigation bar, find it underneath the "Other" drop-down\' --in-context-- \'<none>\'',
    ]
    self.helpTest(inputs, golden_printed)

  def testPrecedenceOfUndeletedProjectNames(self):
    FLAGS.pyatdl_show_uid = True
    inputs = ['mkprj /P',
              'touch /P/inFirstP',
              'rm /P/inFirstP',
              'rmprj /P',
              'mkprj /P',
              'touch /P/inSecondP',
              'echo ls -R -v all_even_deleted',
              'ls -R -v all_even_deleted',
              'echo ls uid=4',
              'ls -v all_even_deleted uid=4',
              'echo ls uid=6',
              'ls -v all_even_deleted uid=6',
              'echo ls -a of an action',
              'ls -a /P/inSecondP',
              'rm /P/inSecondP',
              'rmprj /P',
              'echo ls /P',
              'ls -a -v all_even_deleted /P',
              'echo pwd',
              'pwd',
              'echo ls -a .',
              'ls -a .',
              ]
    golden_printed = [
      'ls -R -v all_even_deleted',
      '--project-- uid=1 --incomplete-- ---active--- inbox',
      '--project-- --DELETED-- uid=4 --incomplete-- ---active--- P',
      '--project-- uid=6 --incomplete-- ---active--- P',
      '',
      './inbox:',
      '',
      './P:',
      '--action--- --DELETED-- uid=5 --incomplete-- inFirstP --in-context-- \'<none>\'',
      '',
      './P:',
      '--action--- uid=7 --incomplete-- inSecondP --in-context-- \'<none>\'',
      'ls uid=4',
      '--action--- --DELETED-- uid=5 --incomplete-- inFirstP --in-context-- \'<none>\'',
      'ls uid=6',
      '--action--- uid=7 --incomplete-- inSecondP --in-context-- \'<none>\'',
      'ls -a of an action',
      '--action--- uid=7 --incomplete-- inSecondP --in-context-- \'<none>\'',
      'ls /P',
      '--project-- --DELETED-- uid=4 --incomplete-- ---active--- .',
      '--folder--- uid=2 ..',
      '--action--- --DELETED-- uid=5 --incomplete-- inFirstP --in-context-- \'<none>\'',
      'pwd',
      '/',
      'ls -a .',
      '--folder--- uid=2 .',
      '--folder--- uid=2 ..',
      '--project-- uid=1 --incomplete-- ---active--- inbox',
      '--project-- --DELETED-- uid=4 --incomplete-- ---active--- P',
      '--project-- --DELETED-- uid=6 --incomplete-- ---active--- P',
    ]
    self.helpTest(inputs, golden_printed)

  def testPrecedenceOfUndeletedObjectsUponRename(self):
    FLAGS.pyatdl_show_uid = True
    inputs = ['touch /inbox/a',
              'rm /inbox/a',
              'touch /inbox/a',
              'echo rename /inbox/a /c',
              'rename /inbox/a /c',
              'rename /inbox/a c',
              'rename /inbox/c /inbox/b',
              'echo ls',
              'ls -R -v all_even_deleted /',
              'echo rename error',
              'rename --allow_slashes /inbox/b /inbox/d',
              'cd /inbox',
              'rename --allow_slashes b /inbox/d',
              'echo ls /inbox',
              'ls /inbox',
              'rename --allow_slashes /inbox/d /inbox/e',
              'rename --allow_slashes uid=5 /inbox/e',
              'echo ls /inbox',
              'ls /inbox',
              'mkctx C',
              'lsctx',
              'rename uid=6 D',
              'echo again lsctx',
              'lsctx',
              'echo rename uid=0 foo',
              'rename uid=0 foo',
              ]
    golden_printed = [
      'rename /inbox/a /c',
      'Cannot use "rename" to move an item; see "mv"',
      'ls',
      '--project-- uid=1 --incomplete-- ---active--- inbox',
      '',
      '/inbox:',
      '--action--- --DELETED-- uid=4 --incomplete-- a --in-context-- \'<none>\'',
      '--action--- uid=5 --incomplete-- b --in-context-- \'<none>\'',
      'rename error',
      'No item named "/inbox/b" exists in the current working Folder/Project (see "help pwd").',
      'ls /inbox',
      '--action--- uid=5 --incomplete-- /inbox/d --in-context-- \'<none>\'',
      'ls /inbox',
      '--action--- uid=5 --incomplete-- /inbox/e --in-context-- \'<none>\'',
      '--context-- uid=0 ---active--- \'<none>\'',
      '--context-- uid=6 ---active--- C',
      'again lsctx',
      '--context-- uid=0 ---active--- \'<none>\'',
      '--context-- uid=6 ---active--- D',
      'rename uid=0 foo',
      'Illegal "uid" syntax. Correct syntax: uid=N where N is a positive, decimal integer',
    ]
    self.helpTest(inputs, golden_printed)

  def testCdWithMultipleChoices(self):
    FLAGS.pyatdl_show_uid = True
    inputs = ['mkprj /a',
              'mkprj /a',
              'echo ls to show UIDs',
              'ls',
              'cd a',
              'touch action',
              'echo ls -a from /a',
              'ls -a',
              'rmact /a/action',
              'rmprj /a',
              'cd /a',
              'echo ls -a after rmprj /a, cd /a:',
              'ls -a',
              'rmprj /a',  # gives undeleted projects precedence
              'cd /a',
              'echo ls -a from /a once both are deleted',
              'ls -a',
              ]
    golden_printed = [
      'ls to show UIDs',
      '--project-- uid=1 --incomplete-- ---active--- inbox',
      '--project-- uid=4 --incomplete-- ---active--- a',
      '--project-- uid=5 --incomplete-- ---active--- a',
      'ls -a from /a',
      '--project-- uid=4 --incomplete-- ---active--- .',
      '--folder--- uid=2 ..',
      '--action--- uid=6 --incomplete-- action --in-context-- \'<none>\'',
      'ls -a after rmprj /a, cd /a:',
      '--project-- uid=5 --incomplete-- ---active--- .',
      '--folder--- uid=2 ..',
      'ls -a from /a once both are deleted',
      '--project-- --DELETED-- uid=4 --incomplete-- ---active--- .',
      '--folder--- uid=2 ..',
      '--action--- --DELETED-- uid=6 --incomplete-- action --in-context-- \'<none>\'',
    ]
    self.helpTest(inputs, golden_printed)

  def testAtHomeDepotVsAtHome(self):
    inputs = ['mkctx "@home"',
              'mkctx "@home depot"',
              'cd /inbox',
              'mkact "buy nails @home depot"',
              'ls',
              ]
    golden_printed = [
      "--action--- --incomplete-- 'buy nails @home depot' --in-context-- '@home depot'",
    ]
    self.helpTest(inputs, golden_printed)

  def testAutoassigningPrj(self):
    inputs = ['mkprj "improve immaculater"',
              'cd /inbox',
              'mkact "improve immaculater with pretty colors"',
              'ls -R /',
              ]
    golden_printed = [
      "--project-- --incomplete-- ---active--- inbox",
      "--project-- --incomplete-- ---active--- 'improve immaculater'",
      "",
      "/inbox:",
      "--action--- --incomplete-- 'improve immaculater with pretty colors' --in-context-- '<none>'",
      "",
      "/improve immaculater:",
    ]
    # TODO(MiniMnM): Autoassign projects to actions:Basically same as
    # context.Just for Heroku app.
    self.helpTest(inputs, golden_printed)

  def testUnicode(self):
    save_path = _CreateTmpFile('')
    inputs = [u'mkact /inbox/\u02bctil',
              'ls -R /',
              'save %s' % pipes.quote(save_path),
              'load %s' % pipes.quote(save_path),
              'echo ls after save:',
              'ls -R /',
              ]
    golden_printed = [
      '--project-- --incomplete-- ---active--- inbox',
      '',
      '/inbox:',
      u'--action--- --incomplete-- \'\u02bctil\' --in-context-- \'<none>\'',
      'Save complete.',
      'Load complete.',
      'ls after save:',
      '--project-- --incomplete-- ---active--- inbox',
      '',
      '/inbox:',
      u'--action--- --incomplete-- \'\u02bctil\' --in-context-- \'<none>\'',
    ]
    self.helpTest(inputs, golden_printed)

  def testSort(self):
    inputs = ['chclock 1137',
              'reset --annihilate',
              'mkact /inbox/cfirst',
              'mkact /inbox/asecond',
              'mkact /inbox/bthird',
              'mkprj /cfirst',
              'mkprj /asecond',
              'mkprj /bthird',
              'mkdir /cDfirst',
              'mkdir /aDsecond',
              'mkdir /bDthird',
              'sort alpha',
              'echo sort alpha',
              'ls -R /',
              'sort chrono',
              'echo sort chrono',
              'ls -R /',
              'sort alpha',
              'echo lsprj:',
              'lsprj --json',
              'mkctx @cfirst',
              'mkctx @asecond',
              'echo lsctx alpha:',
              'lsctx --json',
              'echo lsctx chrono:',
              'sort chrono',
              'lsctx --json',
              ]
    golden_printed = [
      'Reset complete.',
      'sort alpha',
      '--project-- --incomplete-- ---active--- inbox',
      '--folder--- aDsecond',
      '--project-- --incomplete-- ---active--- asecond',
      '--folder--- bDthird',
      '--project-- --incomplete-- ---active--- bthird',
      '--folder--- cDfirst',
      '--project-- --incomplete-- ---active--- cfirst',
      '',
      '/inbox:',
      '--action--- --incomplete-- cfirst --in-context-- \'<none>\'',
      '--action--- --incomplete-- asecond --in-context-- \'<none>\'',
      '--action--- --incomplete-- bthird --in-context-- \'<none>\'',
      '',
      '/aDsecond:',
      '',
      '/asecond:',
      '',
      '/bDthird:',
      '',
      '/bthird:',
      '',
      '/cDfirst:',
      '',
      '/cfirst:',
      'sort chrono',
      '--project-- --incomplete-- ---active--- inbox',
      '--project-- --incomplete-- ---active--- cfirst',
      '--project-- --incomplete-- ---active--- asecond',
      '--project-- --incomplete-- ---active--- bthird',
      '--folder--- cDfirst',
      '--folder--- aDsecond',
      '--folder--- bDthird',
      '',
      '/inbox:',
      '--action--- --incomplete-- cfirst --in-context-- \'<none>\'',
      '--action--- --incomplete-- asecond --in-context-- \'<none>\'',
      '--action--- --incomplete-- bthird --in-context-- \'<none>\'',
      '',
      '/cfirst:',
      '',
      '/asecond:',
      '',
      '/bthird:',
      '',
      '/cDfirst:',
      '',
      '/aDsecond:',
      '',
      '/bDthird:',
      'lsprj:',
      # inbox always first:
      '[{"ctime":1137.0,"default_context_uid":0,"dtime":null,"is_active":true,"is_complete":false,"is_deleted":false,"mtime":1137.0,"name":"inbox","needsreview":false,"number_of_items":3,"path":"/","uid":1},{"ctime":1137.0,"default_context_uid":0,"dtime":null,"is_active":true,"is_complete":false,"is_deleted":false,"mtime":1137.0,"name":"asecond","needsreview":false,"number_of_items":0,"path":"/","uid":8},{"ctime":1137.0,"default_context_uid":0,"dtime":null,"is_active":true,"is_complete":false,"is_deleted":false,"mtime":1137.0,"name":"bthird","needsreview":false,"number_of_items":0,"path":"/","uid":9},{"ctime":1137.0,"default_context_uid":0,"dtime":null,"is_active":true,"is_complete":false,"is_deleted":false,"mtime":1137.0,"name":"cfirst","needsreview":false,"number_of_items":0,"path":"/","uid":7}]',
      'lsctx alpha:',
      '[{"ctime":0,"dtime":null,"is_active":true,"is_complete":false,"is_deleted":false,"mtime":0,"name":"<none>","number_of_items":3,"uid":0},{"ctime":1137.0,"dtime":null,"is_active":true,"is_complete":false,"is_deleted":false,"mtime":1137.0,"name":"@asecond","number_of_items":0,"uid":14},{"ctime":1137.0,"dtime":null,"is_active":true,"is_complete":false,"is_deleted":false,"mtime":1137.0,"name":"@cfirst","number_of_items":0,"uid":13}]',
      'lsctx chrono:',
      '[{"ctime":0,"dtime":null,"is_active":true,"is_complete":false,"is_deleted":false,"mtime":0,"name":"<none>","number_of_items":3,"uid":0},{"ctime":1137.0,"dtime":null,"is_active":true,"is_complete":false,"is_deleted":false,"mtime":1137.0,"name":"@cfirst","number_of_items":0,"uid":13},{"ctime":1137.0,"dtime":null,"is_active":true,"is_complete":false,"is_deleted":false,"mtime":1137.0,"name":"@asecond","number_of_items":0,"uid":14}]',
    ]
    self.helpTest(inputs, golden_printed)

  def testDoAndMaybe(self):
    inputs = ['chclock 1137',
              'reset --annihilate',
              'mkctx @grocerystore',
              'mkctx @someday/maybe',
              'mkprj /foo',
              'cd foo',
              'echo pwd:',
              'pwd',
              'do buy soy/cashew milk',
              'do "buy almond milk @grocerystore"',
              'maybe lose 10kg',
              'echo pwd:',
              'pwd',
              'echo ls:',
              'ls -R /',
              ]
    golden_printed = [
      'Reset complete.',
      'pwd:',
      '/foo',
      'pwd:',
      '/foo',
      'ls:',
      '--project-- --incomplete-- ---active--- inbox',
      '--project-- --incomplete-- ---active--- foo',
      '',
      '/inbox:',
      '--action--- --incomplete-- \'buy soy/cashew milk\' --in-context-- \'<none>\'',
      '--action--- --incomplete-- \'buy almond milk @grocerystore\' --in-context-- @grocerystore',
      '--action--- --incomplete-- \'lose 10kg\' --in-context-- @someday/maybe',
      '',
      '/foo:',
    ]
    self.helpTest(inputs, golden_printed)

  def testRoll(self):
    inputs = ['chclock 1137',
              'reset --annihilate',
              'roll 6',
              'roll 1d',
              'roll --seed 37 1d6',
              'echo 3d1:',
              'roll 3d1',
              'echo 2d2:',
              'roll --seed 38 2d2',
              'echo 1d1000:',
              'roll --seed 39 1d1000',
              ]
    golden_printed = [
      'Reset complete.',
      'Needs argument like "1d6" or "21d20"',
      'Needs argument like "1d6" or "21d20"',
      '5',
      '3d1:',
      '1',
      '1',
      '1',
      '2d2:',
      '2',
      '1',
      '1d1000:',
      '210',
    ]
    self.helpTest(inputs, golden_printed)

  def testMv2(self):
    inputs = ['chclock 1137',
              'reset --annihilate',
              'mkctx @home',
              'do clean the garage @home',
              'mkprj /housekeeping',
              'cd /inbox',
              "mv 'clean the garage @home' /housekeeping",
              'ls -R /',
              ]
    golden_printed = [
      'Reset complete.',
      '--project-- --incomplete-- ---active--- inbox',
      '--project-- --incomplete-- ---active--- housekeeping',
      '',
      '/inbox:',
      '',
      '/housekeeping:',
      '--action--- --incomplete-- \'clean the garage @home\' --in-context-- @home',
    ]
    self.helpTest(inputs, golden_printed)
    
  def testMv3(self):
    inputs = ['mkprj /p',
              'do a/b',
              'ls -R /',
              'mv a\\/b /p',
              ]
    golden_printed = [
      '--project-- --incomplete-- ---active--- inbox',
      '--project-- --incomplete-- ---active--- p',
      '',
      '/inbox:',
      '--action--- --incomplete-- a/b --in-context-- \'<none>\'',
      '',
      '/p:',
      """With current working Folder/Project "/", there is no such child "a".  Choices:
    ..
    p""",
    # TODO(chandler): How can we move an action with slashes in it other than
    # UID notation? See TODO in state._ChildObject.
    ]
    self.helpTest(inputs, golden_printed)
    
  def testAscension(self):
    inputs = ['mkprj /p',
              'cd /inbox',
              'ls ..',
              ]
    golden_printed = [
      '--project-- --incomplete-- ---active--- inbox',
      '--project-- --incomplete-- ---active--- p',
    ]
    self.helpTest(inputs, golden_printed)
    
  def testCat(self):
    inputs = ['echo nop:',
              'cat /inbox',
              'note /inbox foo',
              'echo foo:',
              'cat /inbox',
              'echo foo:',
              'cat uid=1',
              'echo foo:',
              'cat ./inbox',
              'echo foo:',
              'cat inbox',
              'mkact /inbox/a',
              'note /inbox/a "foo bar"',
              'echo foo bar:',
              'cat /inbox/a',
              'mkctx @home',
              'note @home baz',
              'echo baz:',
              'cat @home',
              'mkdir /d',
              'note /d deez',
              'echo deez:',
              'cat /d',
              'echo error 0:',
              'cat',
              'echo error 2:',
              'cat 0 1',
              ]
    golden_printed = [
      'nop:',
      'foo:',
      'foo',
      'foo:',
      'foo',
      'foo:',
      'foo',
      'foo:',
      'foo',
      'foo bar:',
      'foo bar',
      'baz:',
      'baz',
      'deez:',
      'deez',
      'error 0:',
      'Needs a single positional argument; found none',
      'error 2:',
      'Needs a single positional argument; found these: [u\'0\', u\'1\']',
    ]
    self.helpTest(inputs, golden_printed)
    
  def testNote(self):
    save_path = _CreateTmpFile('')
    inputs = ['echo wrong args:',
              'note',
              'note 0 1 2',
              'echo nop:',
              'note /inbox',
              'echo after nop',
              'note /inbox "i am an inbox"',
              'echo i am an inbox:',
              'note uid=1',
              'note --noreplace /inbox " and more notes"',
              'note /inbox " and even more notes"',
              'cd /',
              'echo i am an inbox and more notes and even more notes:',
              'note inbox',
              'note --replace inbox foo',
              'echo foo:',
              'note /inbox',
              'note -r inbox foobar',
              'echo foobar:',
              'note /inbox',
              'echo now testing actions ctxs and folders',
              'mkctx @c',
              'echo nop:',
              'note @c',
              'note @c foo',
              'note @c bar',
              'echo foobar:',
              'note -r @c', # -r does not matter in the one-arg case

              'echo error:',
              'note /dir dirbaz',
              'mkdir /dir',
              'note /dir dirbaz',
              'note / baz',
              'echo baz:',
              'note /',
              'echo dirbaz:',
              'note /dir',

              'mkact /inbox/action',
              'echo nop:',
              'note /inbox/action',
              'note /inbox/action wow',
              'echo error2:',
              'note /inbox/action -r wow2',
              'note --replace /inbox/action wow2',
              'echo wow2:',
              'note /inbox/action',

              'echo now serialization',
              'save %s' % pipes.quote(save_path),
              'load %s' % pipes.quote(save_path),
              'echo foobar:',
              'note /inbox',
              'echo foobar:',
              'note @c',
              'note @c x',
              'echo foobarx:',
              'note @c',
              'echo baz:',
              'note /',
              'echo dirbaz:',
              'note /dir',
              'cd /inbox',
              'echo wow2:',
              'note action',
              ]
    golden_printed = [
      'wrong args:',
      'Needs 2 positional arguments; found none',
      'Needs 2 positional arguments; found these: [u\'0\', u\'1\', u\'2\']',
      'nop:',
      'after nop',
      'i am an inbox:',
      'i am an inbox',
      'i am an inbox and more notes and even more notes:',
      'i am an inbox and more notes and even more notes',
      'foo:',
      'foo',
      'foobar:',
      'foobar',
      'now testing actions ctxs and folders',
      'nop:',
      'foobar:',
      'foobar',
      'error:',
       """With current working Folder/Project "/", there is no such child "dir".  Choices:
    ..
""",
      'baz:',
      'baz',
      'dirbaz:',
      'dirbaz',
      'nop:',
      'error2:',
      'Needs 2 positional arguments; found these: [u\'/inbox/action\', u\'-r\', u\'wow2\']',
      'wow2:',
      'wow2',
      'now serialization',
      'Save complete.',
      'Load complete.',
      'foobar:',
      'foobar',
      'foobar:',
      'foobar',
      'foobarx:',
      'foobarx',
      'baz:',
      'baz',
      'dirbaz:',
      'dirbaz',
      'wow2:',
      'wow2',
    ]
    self.helpTest(inputs, golden_printed)

  def testPurgeDeleted(self):
    FLAGS.pyatdl_show_uid = True
    save_path = _CreateTmpFile('')
    inputs = ['mkact /inbox/alive',
              'mkact /inbox/deleted',
              'mkact /inbox/alive2',
              'rmact /inbox/deleted',
              'mkprj /palive',
              'mkact /palive/alive3',
              'mkact /palive/deleted17',
              'rmact /palive/deleted17',
              'mkprj /pdeleted',
              'rmprj /pdeleted',
              'mkdir /dalive',
              'mkdir /ddeleted',
              'rmdir /ddeleted',
              'mkctx @home',
              'mkctx @deleted',
              'echo lsctx originally:',
              'lsctx',
              'rmctx @deleted',
              'echo now serialization',
              'save %s' % pipes.quote(save_path),
              'load %s' % pipes.quote(save_path),
              'echo ls before purgedeleted:',
              'ls -R -v all_even_deleted /',
              'echo lsctx before purgedeleted:',
              'lsctx',
              'purgedeleted',
              'echo ls after purgedeleted:',
              'ls -R -v all_even_deleted /',
              'echo serialization',
              'save %s' % pipes.quote(save_path),
              'load %s' % pipes.quote(save_path),
              'echo ls after load:',
              'ls -R -v all_even_deleted /',
              'echo lsctx after load:',
              'lsctx',
              'echo now make a new item and see its UID',
              'mkdir /dnew',
              'mkctx @new',
              'save %s' % pipes.quote(save_path),
              'load %s' % pipes.quote(save_path),
              'echo ls after load2:',
              'ls -R -v all_even_deleted /',
              'echo lsctx after load2:',
              'lsctx',
              ]
    golden_printed = [
      'lsctx originally:',
      '--context-- uid=0 ---active--- \'<none>\'',
      '--context-- uid=13 ---active--- @home',
      '--context-- uid=14 ---active--- @deleted',
      'now serialization',
      'Save complete.',
      'Load complete.',
      'ls before purgedeleted:',
      '--project-- uid=1 --incomplete-- ---active--- inbox',
      '--project-- uid=7 --incomplete-- ---active--- palive',
      '--project-- --DELETED-- uid=10 --incomplete-- ---active--- pdeleted',
      '--folder--- uid=11 dalive',
      '--folder--- --DELETED-- uid=12 ddeleted',
      '',
      '/inbox:',
      '--action--- uid=4 --incomplete-- alive --in-context-- \'<none>\'',
      '--action--- --DELETED-- uid=5 --incomplete-- deleted --in-context-- \'<none>\'',
      '--action--- uid=6 --incomplete-- alive2 --in-context-- \'<none>\'',
      '',
      '/palive:',
      '--action--- uid=8 --incomplete-- alive3 --in-context-- \'<none>\'',
      '--action--- --DELETED-- uid=9 --incomplete-- deleted17 --in-context-- \'<none>\'',
      '',
      '/pdeleted:',
      '',
      '/dalive:',
      '',
      '/ddeleted:',
      'lsctx before purgedeleted:',
      '--context-- uid=0 ---active--- \'<none>\'',
      '--context-- uid=13 ---active--- @home',
      'ls after purgedeleted:',
      '--project-- uid=1 --incomplete-- ---active--- inbox',
      '--project-- uid=7 --incomplete-- ---active--- palive',
      '--folder--- uid=11 dalive',
      '',
      '/inbox:',
      '--action--- uid=4 --incomplete-- alive --in-context-- \'<none>\'',
      '--action--- uid=6 --incomplete-- alive2 --in-context-- \'<none>\'',
      '',
      '/palive:',
      '--action--- uid=8 --incomplete-- alive3 --in-context-- \'<none>\'',
      '',
      '/dalive:',
      'serialization',
      'Save complete.',
      'Load complete.',
      'ls after load:',
      '--project-- uid=1 --incomplete-- ---active--- inbox',
      '--project-- uid=7 --incomplete-- ---active--- palive',
      '--folder--- uid=11 dalive',
      '',
      '/inbox:',
      '--action--- uid=4 --incomplete-- alive --in-context-- \'<none>\'',
      '--action--- uid=6 --incomplete-- alive2 --in-context-- \'<none>\'',
      '',
      '/palive:',
      '--action--- uid=8 --incomplete-- alive3 --in-context-- \'<none>\'',
      '',
      '/dalive:',
      'lsctx after load:',
      '--context-- uid=0 ---active--- \'<none>\'',
      '--context-- uid=13 ---active--- @home',
      'now make a new item and see its UID',
      'Save complete.',
      'Load complete.',
      'ls after load2:',
      '--project-- uid=1 --incomplete-- ---active--- inbox',
      '--project-- uid=7 --incomplete-- ---active--- palive',
      '--folder--- uid=11 dalive',
      '--folder--- uid=14 dnew',
      '',
      '/inbox:',
      '--action--- uid=4 --incomplete-- alive --in-context-- \'<none>\'',
      '--action--- uid=6 --incomplete-- alive2 --in-context-- \'<none>\'',
      '',
      '/palive:',
      '--action--- uid=8 --incomplete-- alive3 --in-context-- \'<none>\'',
      '',
      '/dalive:',
      '',
      '/dnew:',
      'lsctx after load2:',
      '--context-- uid=0 ---active--- \'<none>\'',
      '--context-- uid=13 ---active--- @home',
      '--context-- uid=15 ---active--- @new',
    ]
    self.helpTest(inputs, golden_printed)

  def testPurgeDeleted(self):
    FLAGS.pyatdl_show_uid = True
    save_path = _CreateTmpFile('')
    inputs = ['mkact /inbox/alive',
              'mkact /inbox/deleted',
              'mkact /inbox/alive2',
              'rmact /inbox/deleted',
              'mkprj /palive',
              'mkctx @c',
              'mkctx "my context"',
              'mkact -c @c /palive/alive3',
              'mkact /palive/aliveNoContext',
              'mkact -c "my context" /palive/aliveDone',
              'complete /palive/aliveDone',
              'mkprj /pdone',
              'complete /pdone',
              'renamectx @c @newc',
              'mkact /palive/deleted17',
              'rmact /palive/deleted17',
              'mkprj /pdeleted',
              'rmprj /pdeleted',
              'mkdir /dalive',
              'mkdir /ddeleted',
              'rmdir /ddeleted',
              'mkctx @home',
              'mkctx @deleted',
              'rmctx @deleted',
              'mkdir /dalive/subdir',
              'mkprj /dalive/subdir/deepprj',
              'note /dalive "missing note d"',
              'note /palive "a_note"',
              'note /palive "\n\nanother note\nwith lines\n"',
              'note /palive/aliveDone "done_note"',
              'note /palive/aliveDone "\n\nanother done note\nwith lines\n"',
              'echo originally:',
              'astaskpaper',
              'echo now serialization',
              'save %s' % pipes.quote(save_path),
              'load %s' % pipes.quote(save_path),
              'echo after save & load:',
              'astaskpaper',
              'view all_even_deleted',
              'echo with_deleted:',
              'astaskpaper',
              'view actionable',
              'echo actionable:',
              'astaskpaper',
              ]
    subgolden = [
      'inbox:',
      '	- alive',
      '	- alive2',
      '',
      'palive:',
      'a_note',
      '',
      'another note',
      'with lines',
      '',
      '	- alive3 @newc',
      '	- aliveNoContext',
      '	- aliveDone	note: done_note		another done note	with lines @my_context @done',
      '',
      '@done pdone:',
      '',
      '/dalive/subdir/deepprj:',
      ]
    golden_printed = ['originally:'] + subgolden + [
      'now serialization',
      'Save complete.',
      'Load complete.',
      'after save & load:',
    ] + subgolden + [
      'with_deleted:',
      'inbox:',
      '	- alive',
      '	- deleted @done @deleted',
      '	- alive2',
      '',
      'palive:',
      'a_note',
      '',
      'another note',
      'with lines',
      '',
      '	- alive3 @newc',
      '	- aliveNoContext',
      '	- aliveDone	note: done_note		another done note	with lines @my_context @done',
      '	- deleted17 @done @deleted',
      '',
      '@done pdone:',
      '',
      '@deleted pdeleted:',
      '',
      '/dalive/subdir/deepprj:',
      'actionable:',
      'inbox:',
      '	- alive',
      '	- alive2',
      '',
      'palive:',
      'a_note',
      '',
      'another note',
      'with lines',
      '',
      '	- alive3 @newc',
      '	- aliveNoContext',
      '',
      '/dalive/subdir/deepprj:',
    ]
    self.helpTest(inputs, golden_printed)

  def testWeeklyReviewNotes(self):
    FLAGS.pyatdl_show_uid = True
    save_path = _CreateTmpFile('')
    inputs = ['echo nop',
              'note :__weekly_review',
              'cat :__weekly_review',
              'note :__weekly_review foo',
              'note :__weekly_review bar',
              'echo foobar:',
              'note :__weekly_review',
              'echo same:',
              'cat :__weekly_review',
              'note :0- foo',
              'note -r :0- wow',
              'echo wow:',
              'cat :0-',
              u'note :0- \u2014',
              'echo with em dash unicode at the end:',
              'note :0-',
              'save %s' % pipes.quote(save_path),
              'load %s' % pipes.quote(save_path),
              'echo foobar:',
              'cat :__weekly_review',
              'echo wow-em-dash:',
              'cat :0-',
              'note --replace :0- ""',
              'echo nop:',
              'cat :0-',
              ]
    golden_printed = [
      'nop',
      'foobar:',
      'foobar',
      'same:',
      'foobar',
      'wow:',
      'wow',
      'with em dash unicode at the end:',
      u'wow\u2014',
      'Save complete.',
      'Load complete.',
      'foobar:',
      'foobar',
      'wow-em-dash:',
      u'wow\u2014',
      'nop:',
    ]
    self.helpTest(inputs, golden_printed)

  def testCaseInsensitivityOfAutoassignment(self):
    inputs = ['mkctx @waiting_For',
              'mkctx "@Home Depot"',
              u'mkact "/inbox/bake bread\u2014 @waiting_for"',
              u'mkact "/inbox/copy keys @Home Depot"',
              u'mkact "/inbox/copy keys2 @Home_Depot"',
              u'mkact "/inbox/copy keys3 @Home-Depot"',
              u'mkact "/inbox/copy keys4 @Homedepot"',
              'ls /inbox',
              ]
    golden_printed = [
      u"--action--- --incomplete-- 'bake bread\u2014 @waiting_for' --in-context-- @waiting_For",
      "--action--- --incomplete-- 'copy keys @Home Depot' --in-context-- '@Home Depot'",
      "--action--- --incomplete-- 'copy keys2 @Home_Depot' --in-context-- '@Home Depot'",
      "--action--- --incomplete-- 'copy keys3 @Home-Depot' --in-context-- '@Home Depot'",
      "--action--- --incomplete-- 'copy keys4 @Homedepot' --in-context-- '@Home Depot'",
      ]
    self.helpTest(inputs, golden_printed)

  def testMarkingAProjectIncompleteMarksActionsIncomplete(self):
    inputs = ['mkprj /p',
              'touch /p/a',
              'touch /p/b',
              'complete -f /p',
              'echo completed:',
              'ls -R /',
              'uncomplete /p',
              'echo newly incomplete:',
              'ls -R /',
              ]
    golden_printed = [
      "completed:",
      "--project-- --incomplete-- ---active--- inbox",
      "--project-- ---COMPLETE--- ---active--- p",
      "",
      "/inbox:",
      "",
      "/p:",
      "--action--- ---COMPLETE--- a --in-context-- '<none>'",
      "--action--- ---COMPLETE--- b --in-context-- '<none>'",
      "newly incomplete:",
      "--project-- --incomplete-- ---active--- inbox",
      "--project-- --incomplete-- ---active--- p",
      "",
      "/inbox:",
      "",
      "/p:",
      "--action--- --incomplete-- a --in-context-- '<none>'",
      "--action--- --incomplete-- b --in-context-- '<none>'",
    ]
    self.helpTest(inputs, golden_printed)

  def testAutoassigningProject(self):
    inputs = ['mkprj "/hang art"',
              'mkctx @home',
              'touch "/inbox/Hang art: find nails @home"',
              'ls -R /',
              'touch --autoprj "/inbox/Hang art: find nails @home"',
              'maybe hang art: someday',
              'mkctx @someday/maybe',
              'maybe hang art: some other day',
              'do hang art: foobar',
              'do baz +hangart',
              'do +HangArt baz2',
              'do baz3 +HangArt baz4',
              'echo now:',
              'ls -R /',
              'cd /inbox',
              'rmprj -f "/hang art"',
              'mkact --autoprj "hang art: after deletion"',
              'echo now after deletion:',
              'ls -R /',
              ]
    golden_printed = [
      "--project-- --incomplete-- ---active--- inbox",
      "--project-- --incomplete-- ---active--- 'hang art'",
      "",
      "/inbox:",
      "--action--- --incomplete-- 'Hang art: find nails @home' --in-context-- @home",
      "",
      "/hang art:",
      'No such Context "@someday/maybe"',

      "now:",
      "--project-- --incomplete-- ---active--- inbox",
      "--project-- --incomplete-- ---active--- 'hang art'",
      "",
      "/inbox:",
      "--action--- --incomplete-- 'Hang art: find nails @home' --in-context-- @home",
      "",
      "/hang art:",
      "--action--- --incomplete-- 'find nails @home' --in-context-- @home",
      "--action--- --incomplete-- 'some other day' --in-context-- @someday/maybe",
      "--action--- --incomplete-- foobar --in-context-- '<none>'",
      "--action--- --incomplete-- baz --in-context-- '<none>'",
      "--action--- --incomplete-- baz2 --in-context-- '<none>'",
      "--action--- --incomplete-- 'baz3 baz4' --in-context-- '<none>'",

      "now after deletion:",
      "--project-- --incomplete-- ---active--- inbox",
      "",
      "/inbox:",
      "--action--- --incomplete-- 'Hang art: find nails @home' --in-context-- @home",
      "--action--- --incomplete-- 'hang art: after deletion' --in-context-- '<none>'",
    ]
    self.helpTest(inputs, golden_printed)

  def testTodoCommand(self):
    inputs = ['mkprj "/hang art"',
              'mkprj /inactiveproject',
              'deactivateprj /inactiveproject',
              'do activeaction +inactiveproject',
              'mkctx @home',
              'touch --autoprj "/inbox/Hang art: find nails @home"',
              'mkctx @someday/maybe',
              'deactivatectx @someday/maybe',
              'cd /inbox',
              'touch --allow_slashes "@someday/maybe quuz"',
              'maybe hang art: some other day',
              'do hang art: buy brackets',
              'complete "/hang art/buy brackets"',
              'echo todo:',
              'todo',
              'echo',
              'echo todo now:',
              'todo now',
              'echo',
              'echo todo -v actionable:',
              'todo -v actionable',
              'echo',
              'echo error:',
              'todo -v actionable all',
              'echo view:',
              'view',
              'echo txt:',
              'txt',
              'do 1',
              'note /inbox/1 "line 1\n\nline 3"',
              'txt',
              ]
    golden_printed = [
      "todo:",
      "inbox:",
      "	- @someday/maybe quuz",
      "",
      "hang art:",
      "	- find nails @home",
      "	- some other day @someday/maybe",
      "",
      "inactiveproject:",
      "	- activeaction",
      "",
      "todo now:",
      "inbox:",
      "",
      "hang art:",
      "	- find nails @home",
      "",
      "todo -v actionable:",
      "inbox:",
      "",
      "hang art:",
      "	- find nails @home",
      "",
      "error:",
      "Conflicting view filters",
      "view:",
      "all",
      "txt:",
      "inbox:",
      "	- @someday/maybe quuz",
      "",
      "hang art:",
      "	- find nails @home",
      "	- some other day @someday/maybe",
      "	- buy brackets @done",
      "",
      "inactiveproject:",
      "	- activeaction",
      "inbox:",
      "	- @someday/maybe quuz",
      "	- 1	note: line 1		line 3",
      "",
      "hang art:",
      "	- find nails @home",
      "	- some other day @someday/maybe",
      "	- buy brackets @done",
      "",
      "inactiveproject:",
      "	- activeaction",
    ]
    self.helpTest(inputs, golden_printed)

  def testInactiveViewFilter(self):
    inputs = ['chclock 37',
              'mkprj "/hang art"',
              'mkprj /inactiveproject',
              'deactivateprj /inactiveproject',
              'do activeaction +inactiveproject',
              'do completedaction +inactiveproject',
              'complete /inactiveproject/completedaction',
              'mkctx @home',
              'touch --autoprj "/inbox/Hang art: find nails @home"',
              'mkctx @someday/maybe1y',
              'mkctx @someday/maybe',
              'deactivatectx @someday/maybe1y',
              'deactivatectx @someday/maybe',
              'rmctx @someday/maybe1y',
              'maybe hang art: some other day',
              'do hang art: buy brackets',
              'rmact "/hang art/buy brackets"',
              'do active_and_incomplete_in_inbox',
              'echo ls -v inactive_and_incomplete -R /:',
              'ls -v inactive_and_incomplete -R /',
              'echo ls -v inactive_and_incomplete "/hang art":',
              'ls -v inactive_and_incomplete -R "/hang art"',
              'view inactive_and_incomplete',
              'echo lsctx:',
              'lsctx',
              'echo inactive_and_incomplete inprj inbox:',
              'inprj --json uid=1',
              'echo all inprj inbox:',
              'view all',
              'inprj --json uid=1',
              ]
    golden_printed = [
      "ls -v inactive_and_incomplete -R /:",
      "--project-- --incomplete-- --INACTIVE-- inactiveproject",
      "",
      "/inactiveproject:",
      "--action--- --incomplete-- activeaction --in-context-- '<none>'",
      "ls -v inactive_and_incomplete /hang art:",
      "--action--- --incomplete-- 'some other day' --in-context-- @someday/maybe",
      "lsctx:",
      "--context-- ---active--- '<none>'",
      "--context-- --INACTIVE-- @someday/maybe",
      "inactive_and_incomplete inprj inbox:",
      "[]",
      "all inprj inbox:",
      '[{"ctime":37.0,"dtime":null,"in_context":"<none>","in_context_uid":null,"is_complete":false,"is_deleted":false,"mtime":37.0,"name":"active_and_incomplete_in_inbox","number_of_items":1,"uid":14}]',
    ]
    self.helpTest(inputs, golden_printed)

  def testInactiveItems(self):
    inputs = ['mkprj "/hang art"',
              'mkprj /inactiveproject',
              'deactivateprj /inactiveproject',
              'mkctx @home',
              'do activeaction @home +inactiveproject',
              'touch --autoprj "/inbox/Hang art: find nails @home"',
              'view incomplete',
              'echo incomplete inctx @home:',
              'inctx @home',
              'view actionable',
              'echo actionable inctx @home:',
              'inctx @home',
              ]
    golden_printed = [
      "incomplete inctx @home:",
      "--action--- --incomplete-- 'find nails @home'",
      "--action--- --incomplete-- 'activeaction @home'",
      "actionable inctx @home:",
      "--action--- --incomplete-- 'find nails @home'",
    ]
    self.helpTest(inputs, golden_printed)

  def testVerboseCreation(self):
    FLAGS.pyatdl_show_uid = True
    inputs = ['mkprj --verbose "/hang art"',
              'mkact --verbose /inbox/a',
              'mkctx --verbose @c',
              'ls -R -v all /',
              'echo lsctx:',
              'lsctx',
              ]
    golden_printed = [
      "4",
      "5",
      "6",
      "--project-- uid=1 --incomplete-- ---active--- inbox",
      "--project-- uid=4 --incomplete-- ---active--- 'hang art'",
      "",
      "/inbox:",
      "--action--- uid=5 --incomplete-- a --in-context-- '<none>'",
      "",
      "/hang art:",
      "lsctx:",
      "--context-- uid=0 ---active--- '<none>'",
      "--context-- uid=6 ---active--- @c",
    ]
    self.helpTest(inputs, golden_printed)

  def testChdefaultctxAndReusingUIDs(self):
    FLAGS.pyatdl_show_uid = True
    save_path = _CreateTmpFile('')
    inputs = ['chclock 1137.0',
              'mkprj /p',
              'chdefaultctx @unknown /p',
              'mkctx @home',
              'mkact /p/beforedefault',
              'chdefaultctx @home /p',
              'chdefaultctx @home /unknown',
              'chdefaultctx @home uid=1',
              'do buy soymilk',
              'mkact /p/afterdefault',
              'echo ls -R /:',
              'ls -R /',
              'save %s' % pipes.quote(save_path),
              'load %s' % pipes.quote(save_path),
              'mkact /p/afterdeserializiation',
              'echo ls -R /:',
              'ls -R /',
              'renamectx @home @newname',  
              'mkact /p/afternewname',
              'chdefaultctx uid=0 uid=1',
              'do buy almond milk',
              'echo ls -R /:',
              'ls -R /',
              'rmctx @newname',
              'mkact /p/afterrmctx',
              'do buy more soymilk',
              'echo ls -R /:',
              'ls -R /',
              'mkctx @foobar',
              'chdefaultctx @foobar uid=1',
              'echo lsprj --json uid=1',
              'lsprj --json uid=1',

              # And this could really be its own test case:
              'mkctx @highestuid',
              'echo uid=15 for @highestuid:',
              'lsctx -l',
              'rmctx @highestuid',
              'purgedeleted',
              'save %s' % pipes.quote(save_path),
              'load %s' % pipes.quote(save_path),
              'mkctx @higherstilluid',
              # TODO(chandler): Should we be reusing UIDs?
              'echo uid=15 reused for @higherstilluid:',
              'lsctx -l',
              ]
    golden_printed = [
      'No such Context "@unknown"',
      'No such Project "unknown". Choices: p',
      "ls -R /:",
      "--project-- uid=1 --incomplete-- ---active--- inbox",
      "--project-- uid=4 --incomplete-- ---active--- p",
      "",
      "/inbox:",
      "--action--- uid=7 --incomplete-- 'buy soymilk' --in-context-- @home",
      "",
      "/p:",
      "--action--- uid=6 --incomplete-- beforedefault --in-context-- @home",
      "--action--- uid=8 --incomplete-- afterdefault --in-context-- @home",
      "Save complete.",
      "Load complete.",
      "ls -R /:",
      "--project-- uid=1 --incomplete-- ---active--- inbox",
      "--project-- uid=4 --incomplete-- ---active--- p",
      "",
      "/inbox:",
      "--action--- uid=7 --incomplete-- 'buy soymilk' --in-context-- @home",
      "",
      "/p:",
      "--action--- uid=6 --incomplete-- beforedefault --in-context-- @home",
      "--action--- uid=8 --incomplete-- afterdefault --in-context-- @home",
      "--action--- uid=9 --incomplete-- afterdeserializiation --in-context-- @home",
      "ls -R /:",
      "--project-- uid=1 --incomplete-- ---active--- inbox",
      "--project-- uid=4 --incomplete-- ---active--- p",
      "",
      "/inbox:",
      "--action--- uid=7 --incomplete-- 'buy soymilk' --in-context-- @newname",
      "--action--- uid=11 --incomplete-- 'buy almond milk' --in-context-- '<none>'",
      "",
      "/p:",
      "--action--- uid=6 --incomplete-- beforedefault --in-context-- @newname",
      "--action--- uid=8 --incomplete-- afterdefault --in-context-- @newname",
      "--action--- uid=9 --incomplete-- afterdeserializiation --in-context-- @newname",
      "--action--- uid=10 --incomplete-- afternewname --in-context-- @newname",
      "ls -R /:",
      "--project-- uid=1 --incomplete-- ---active--- inbox",
      "--project-- uid=4 --incomplete-- ---active--- p",
      "",
      "/inbox:",
      "--action--- uid=7 --incomplete-- 'buy soymilk' --in-context-- '<none>'",
      "--action--- uid=11 --incomplete-- 'buy almond milk' --in-context-- '<none>'",
      "--action--- uid=13 --incomplete-- 'buy more soymilk' --in-context-- '<none>'",
      "",
      "/p:",
      "--action--- uid=6 --incomplete-- beforedefault --in-context-- '<none>'",
      "--action--- uid=8 --incomplete-- afterdefault --in-context-- '<none>'",
      "--action--- uid=9 --incomplete-- afterdeserializiation --in-context-- '<none>'",
      "--action--- uid=10 --incomplete-- afternewname --in-context-- '<none>'",
      "--action--- uid=12 --incomplete-- afterrmctx --in-context-- '<none>'",
      "lsprj --json uid=1",
      '{"ctime":36.0,"default_context_uid":14,"dtime":null,"is_active":true,"is_complete":false,"is_deleted":false,"max_seconds_before_review":604800.0,"mtime":1137.0,"name":"inbox","needsreview":false,"number_of_items":3,"parent_path":"/","uid":1}',
      "uid=15 for @highestuid:",
      "--context-- uid=0 mtime=1969/12/31-19:00:00 ctime=1969/12/31-19:00:00 ---active--- '<none>'",
      "--context-- uid=14 mtime=1969/12/31-19:18:57 ctime=1969/12/31-19:18:57 ---active--- @foobar",
      "--context-- uid=15 mtime=1969/12/31-19:18:57 ctime=1969/12/31-19:18:57 ---active--- @highestuid",
      "Save complete.",
      "Load complete.",
      "uid=15 reused for @higherstilluid:",
      "--context-- uid=0 mtime=1969/12/31-19:00:00 ctime=1969/12/31-19:00:00 ---active--- '<none>'",
      "--context-- uid=14 mtime=1969/12/31-19:18:57 ctime=1969/12/31-19:18:57 ---active--- @foobar",
      "--context-- uid=15 mtime=1969/12/31-19:18:57 ctime=1969/12/31-19:18:57 ---active--- @higherstilluid",
    ]
    self.helpTest(inputs, golden_printed)

  def testPrjify(self):
    # TODO(chandler): support uid=-1 referring to the last object created, the
    # max UID in the system.
    save_path = _CreateTmpFile('')
    inputs = ['do foo bar/baz',
              'prjify uid=4',
              'save %s' % pipes.quote(save_path),
              'load %s' % pipes.quote(save_path),
              'chclock 1337',
              'do quux',
              'chclock 1338',
              'prjify /inbox/quux',
              'ls -R -v all_even_deleted /',
              'ls -l -v all_even_deleted /inbox/quux',
              'do withanote',
              'note /inbox/withanote X',
              'prjify /inbox/withanote',
             ]
    golden_printed = [
      "5",
      "Save complete.",
      "Load complete.",
      "7",
      "--project-- --incomplete-- ---active--- inbox",
      "--project-- --incomplete-- ---active--- 'foo bar/baz'",
      "--project-- --incomplete-- ---active--- quux",
      "",
      "/inbox:",
      "--action--- --DELETED-- --incomplete-- 'foo bar/baz' --in-context-- '<none>'",
      "--action--- --DELETED-- --incomplete-- quux --in-context-- '<none>'",
      "",
      "/foo bar/baz:",
      "",
      "/quux:",
      "--action--- --DELETED-- mtime=1969/12/31-19:22:18 ctime=1969/12/31-19:22:17 dtime=1969/12/31-19:22:18 --incomplete-- quux --in-context-- '<none>'",
      "Action has a Note; can't automatically convert to a Project.",
    ]
    self.helpTest(inputs, golden_printed)

  def testHypertext(self):
    inputs = ['do foo bar/baz',
              'mkdir /a',
              'mkprj /a/b',
              'touch /a/b/c',
              'note /a/b/c "\\nline 1\\n\\nline 3\\n"',
              'touch /a/b/completed',
              'complete /a/b/completed',
              'touch /a/b/e&nbsp;f',
              'hypertext /todo',
              'echo and now incomplete:',
              'view incomplete',
              'hypertext ""',
             ]
    golden_printed = [
      '<a href="/todo/project/1">inbox:</a><br>',
      '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- <a href="/todo/action/4">foo bar/baz</a><br>',
      '<br>',
      '<a href="/todo/project/6">/a/b:</a><br>',
      '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- <a href="/todo/action/7">c<br>line 1<br><br>line 3</a><br>',
      '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- <a href="/todo/action/8">completed @done</a><br>',
      '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- <a href="/todo/action/9">e&amp;nbsp;f</a><br>',
      'and now incomplete:',
      '<a href="/project/1">inbox:</a><br>',
      '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- <a href="/action/4">foo bar/baz</a><br>',
      '<br>',
      '<a href="/project/6">/a/b:</a><br>',
      '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- <a href="/action/7">c<br>line 1<br><br>line 3</a><br>',
      '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- <a href="/action/9">e&amp;nbsp;f</a><br>',
    ]
    self.helpTest(inputs, golden_printed)

  def testDeletecompleted(self):
    save_path = _CreateTmpFile('')
    inputs = ['chclock 37',
              'do foo',
              'do bar',
              'complete /inbox/bar',
              'mkprj /p0',
              'complete /p0',
              'touch /p0/incompletedescendant',
              'mkprj /p1',
              'mkprj /pcompletewithnoincompletedescendants',
              'touch /pcompletewithnoincompletedescendants/deleted',
              'rmact /pcompletewithnoincompletedescendants/deleted',
              'touch /pcompletewithnoincompletedescendants/completed',
              'complete /pcompletewithnoincompletedescendants/completed',
              'complete /pcompletewithnoincompletedescendants',
              'complete /pcompletewithnoincompletedescendants/completed',
              'mkdir /a',
              'echo error: you cannot complete a directory',
              'complete /a',
              'mkprj /a/b',
              'touch /a/b/c',
              'touch /a/b/completed',
              'complete /a/b/completed',
              'chclock 38',
              'echo deletecompleted:',
              'deletecompleted',
              'echo ls after deletecompleted before save/load:',
              'ls -R -v all_even_deleted /',
              'save %s' % pipes.quote(save_path),
              'load %s' % pipes.quote(save_path),
              'echo ls after save/load:',
              'ls -R -v all_even_deleted /',
              'echo and is dtime set correctly?',
              'ls -l -v all_even_deleted uid=1',
             ]
    subgolden = [
      "--project-- --incomplete-- ---active--- inbox",
      "--project-- --incomplete-- ---active--- p0",
      "--project-- --incomplete-- ---active--- p1",
      "--project-- --DELETED-- ---COMPLETE--- ---active--- pcompletewithnoincompletedescendants",
      "--folder--- a",
      "",
      "/inbox:",
      "--action--- --incomplete-- foo --in-context-- '<none>'",
      "--action--- --DELETED-- ---COMPLETE--- bar --in-context-- '<none>'",
      "",
      "/p0:",
      "--action--- --incomplete-- incompletedescendant --in-context-- '<none>'",
      "",
      "/p1:",
      "",
      "/pcompletewithnoincompletedescendants:",
      "--action--- --DELETED-- --incomplete-- deleted --in-context-- '<none>'",
      "--action--- --DELETED-- ---COMPLETE--- completed --in-context-- '<none>'",
      "",
      "/a:",
      "--project-- --incomplete-- ---active--- b",
      "",
      "/a/b:",
      "--action--- --incomplete-- c --in-context-- '<none>'",
      "--action--- --DELETED-- ---COMPLETE--- completed --in-context-- '<none>'",
    ]
    golden_printed = [
      "error: you cannot complete a directory",
      "No such Project \"a\". Choices: p0 p1 pcompletewithnoincompletedescendants",
      "deletecompleted:",
      "ls after deletecompleted before save/load:"] + subgolden + [
      "Save complete.",
      "Load complete.",
      "ls after save/load:"] + subgolden + [
      "and is dtime set correctly?",
      "--action--- mtime=1969/12/31-19:00:38 ctime=1969/12/31-19:00:37 --incomplete-- foo --in-context-- '<none>'",
      "--action--- --DELETED-- mtime=1969/12/31-19:00:38 ctime=1969/12/31-19:00:37 dtime=1969/12/31-19:00:38 ---COMPLETE--- bar --in-context-- '<none>'",
    ]
    self.helpTest(inputs, golden_printed)

  def testUncompletingProjectUponArrivalOfIncompleteAction(self):
    inputs = ['do bar',
              'rmact /inbox/bar',
              'mkprj /p0',
              'complete /p0',
              'mv /inbox/bar /p0',
              'echo ls / should show completed p0:',  # TODO(chandler): support ls -d /inbox
              'ls /',
              'touch /p0/incompletedescendant',
              'mkprj /p1',
              'touch /p1/iamcomplete',
              'complete -f /p1',
              'do foo',
              'mv /inbox/foo /p1',
              'deletecompleted',
              'echo ls (iamcomplete still complete, p0 incomplete, p1 incomplete):',
              'ls -R -v all_even_deleted /',
              'purgedeleted',
              'echo ls after purgedeleted:',
              'ls -R -v all_even_deleted /',
             ]
    golden_printed = [
      'ls / should show completed p0:',
      '--project-- --incomplete-- ---active--- inbox',
      '--project-- ---COMPLETE--- ---active--- p0',
      'ls (iamcomplete still complete, p0 incomplete, p1 incomplete):',
      '--project-- --incomplete-- ---active--- inbox',
      '--project-- --incomplete-- ---active--- p0',
      '--project-- --incomplete-- ---active--- p1',
      '',
      '/inbox:',
      '',
      '/p0:',
      '--action--- --DELETED-- --incomplete-- bar --in-context-- \'<none>\'',
      '--action--- --incomplete-- incompletedescendant --in-context-- \'<none>\'',
      '',
      '/p1:',
      '--action--- --DELETED-- ---COMPLETE--- iamcomplete --in-context-- \'<none>\'',
      '--action--- --incomplete-- foo --in-context-- \'<none>\'',
      'ls after purgedeleted:',
      '--project-- --incomplete-- ---active--- inbox',
      '--project-- --incomplete-- ---active--- p0',
      '--project-- --incomplete-- ---active--- p1',
      '',
      '/inbox:',
      '',
      '/p0:',
      '--action--- --incomplete-- incompletedescendant --in-context-- \'<none>\'',
      '',
      '/p1:',
      '--action--- --incomplete-- foo --in-context-- \'<none>\'',
    ]
    self.helpTest(inputs, golden_printed)

  def testAddingUndeletedActionToDeletedProject(self):
    inputs = ['mkprj /p0',
              'complete /p0',
              'rmprj /p0',
              'touch /p0/incompletedescendant',
             ]
    golden_printed = [
      'Cannot add an Action to a deleted Project',
    ]
    self.helpTest(inputs, golden_printed)

  def testCompletingOrDeletingInbox(self):
    inputs = ['complete /inbox',
              'rmprj /inbox',
             ]
    golden_printed = [
      'The project /inbox is special and cannot be marked complete.',
      'The project /inbox is special; it cannot be removed.',
    ]
    self.helpTest(inputs, golden_printed)


if __name__ == '__main__':
  unitjest.main()


# TODO(chandler): Test working with future protobuf; verify that we pass along
# any uninterpreted data
