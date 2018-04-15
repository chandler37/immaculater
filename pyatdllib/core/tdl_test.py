"""Unittests for module 'tdl'."""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import gflags as flags

from pyatdllib.core import tdl
from pyatdllib.core import unitjest

FLAGS = flags.FLAGS


# pylint: disable=missing-docstring,too-many-public-methods
class TdlTestCase(unitjest.TestCase):

  def testStr(self):
    FLAGS.pyatdl_show_uid = False
    FLAGS.pyatdl_separator = '/'
    lst = tdl.ToDoList()
    self.assertEqual(lst.inbox.name, 'inbox')
    self.assertEqual(lst.root.name, '')
    self.assertEqual(lst.root.items, [])
    # pylint: disable=trailing-whitespace
    self._AssertEqualWithDiff(
      r"""
<todolist>
    <inbox>
        <project is_deleted="False" is_complete="False" is_active="True" name="inbox">
        
        </project>
    </inbox>
    <folder is_deleted="False" name="">
    
    </folder>
    <contexts>
        <context_list is_deleted="False" name="Contexts">
        
        </context_list>
    </contexts>
</todolist>
""".strip().split('\n'),
      str(lst).split('\n'))


if __name__ == '__main__':
  unitjest.main()
