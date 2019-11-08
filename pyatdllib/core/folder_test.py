"""Unittests for module 'folder'."""

import gflags as flags

from pyatdllib.core import folder
from pyatdllib.core import uid
from pyatdllib.core import unitjest

FLAGS = flags.FLAGS


# pylint: disable=missing-docstring,too-many-public-methods
class FolderTestCase(unitjest.TestCase):

  def setUp(self):
    super().setUp()
    FLAGS.pyatdl_randomize_uids = False
    uid.ResetNotesOfExistingUIDs()

  def testStr(self):
    f = folder.Folder()
    self.assertTrue(f.name is None)
    self.assertEqual(f.items, [])
    f = folder.Folder(name='F0')
    self.assertEqual(f.name, 'F0')
    self.assertEqual(f.items, [])
    outer = folder.Folder(name='outer', items=[f, unitjest.FullPrj()])
    # pylint: disable=trailing-whitespace
    FLAGS.pyatdl_show_uid = False
    self._AssertEqualWithDiff(
      [str(outer)],
      ["""
<folder is_deleted="False" name="outer">
    <folder is_deleted="False" name="F0">
   \x20
    </folder>
    <project is_deleted="False" is_complete="False" is_active="True" name="myname">
        <action is_deleted="False" is_complete="False" name="Buy milk" ctx=""/>
        <action is_deleted="False" is_complete="False" name="Oranges" ctx="uid=-9223372036854775808"/>
    </project>
</folder>
""".strip()])
    FLAGS.pyatdl_show_uid = True
    self._AssertEqualWithDiff(
      [str(outer)],
      ["""
<folder uid=6 is_deleted="False" name="outer">
    <folder uid=2 is_deleted="False" name="F0">
   \x20
    </folder>
    <project uid=5 is_deleted="False" is_complete="False" is_active="True" name="myname">
        <action uid=3 is_deleted="False" is_complete="False" name="Buy milk" ctx=""/>
        <action uid=4 is_deleted="False" is_complete="False" name="Oranges" ctx="uid=-9223372036854775808"/>
    </project>
</folder>
""".strip()])


if __name__ == '__main__':
  unitjest.main()
