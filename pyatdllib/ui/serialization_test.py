"""Unittests for module 'serialization'."""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import gflags as flags  # https://code.google.com/p/python-gflags/

from google.protobuf import text_format

from pyatdllib.core import unitjest
from pyatdllib.ui import serialization
from pyatdllib.ui import uicmd
uicmd.RegisterAppcommands(False, uicmd.APP_NAMESPACE)

FLAGS = flags.FLAGS


class MockReader(object):
  def __init__(self, saved_read):
    self._saved_read = saved_read
    assert saved_read is not None
    self.name = 'MockReader'

  def read(self):
    return self._saved_read


# pylint: disable=missing-docstring,too-many-public-methods
class SerializationTestCase(unitjest.TestCase):

  def setUp(self):
    super().setUp()
    self.maxDiff = None

  def testSha1Checksum(self):
    # echo "testing SHA1" > /tmp/sum_me && shasum /tmp/sum_me
    self.assertEqual(
      serialization.Sha1Checksum(b"testing SHA1\n"),
      "041c35b35c8c1c0fa18925b1c18e965c7efee06f")

  def testDeserializeToDoList2_corruption(self):
    reader = MockReader(b'abc\xad123')
    sha1_checksum_list = []
    here = False
    try:
      serialization.DeserializeToDoList2(
        reader,
        tdl_factory=None,
        sha1_checksum_list=sha1_checksum_list)
    except serialization.DeserializationError as e:
      here = True
      self.assertEqual('corruption' in str(e), True)
    self.assertTrue(here)

  def testDeserializeToDoList2_compression_saving_uncompressed_sha1(self):
    reader = MockReader(b'\x08\xd6\x05\x12(24337f7c77dc855ba47ac18c2cc4398fd8af776f\x18\x01\xda\xf8\x04\xd6\x05x^m\x93]H\x14Q\x14\xc7w\xb4\x8f\xedf\xba\xec\xd32\x10\x1c\xe6\xa5\x17%\x10\x0b\x95\x94\x15\x05\xf3\xa9\x90\xc0\xe7Y\xf7\xeaN\xce\xce]f\xee\xee\xba\xf4")\x82\n)\x98\x1f\x05\x92\x1f\x99\xb8l\xda\x17\x99T\xd2K\x08\x96\xe4J\xb4"a\x18\xe9\x1a\xe1\x07\x92Y\xf4a3\xd7\xd9\x10\xa6y\x18\xe6\x9e\xb9\xbf\xff\xff\x9cs\xcfE\xb9(\xdbns\x9e\xb47\xae&\x07o\xce\xae\xa49\xf6R\x0f\xe7\xfaf\xc6\xf8\xa3\xe8\xb0\xa4xH=p\x0e\x9b\x8bs.\x1cB\xa7\x18\xd4\x9a\xb4B/\x1a\xd7\x98\x10\x9f\x86l\x90\xc6\x97\xa2"\xb6us\xcf\xba5\xd1`n\xcdB\'\xfc\x92V\x8deYT0\tj03\xdc32\xb7\xdd;\xbf\xc8\x0c\xf9d:\xba\xc8T\x9e]\xdd\'\x0ef\xb9~\xcdT\x11\x10\xc8XT\x15\xf0\x910P\x02A\r\x03\xf5I\x9a\xfe\x9d\xe3% K\x1a\x85\xa1\x87\xbb}\xdd\x0f:\xa7G\x99\xb0p\x05\x85\x99no\xb3U\xf7\xa3\x19\xe3+Py\x95H\xab}\xba\x18\x86\x90\xe4\xc5\x04\x88\xc2\x16\xc2y,\x07\x04\x08\x88\xb5\x18rr\xa0FR\xbc \xd1\xd4_J\x02\xa0\x88!\xa9V\xa4\x92\x0exD\x15\x12\x8b\x03\xd1W}\xabK1\xcee\x130\x12\x99\xf9\xa7\x16\xab\xf9X\xabYT\x1e\xca\xad\xc4\xa2\x97\xd9y\x08\xa9\x03\xa1\x1cS*)\xb5p\xc9\xa7\xbf5(#\n\x16\xc0\x13\x812\xdd\xca\x0b%\xb2\x8c\x15\x88u\xdf\x88\xc7c;S\x97u\x9b(\x87\x869f\xd4nv\xea`\xf7VR\xdd\xabG\xa1\x92\x1a\x8aUPu;C?\xe5\x98\rT\x8d\x00\tR\x10\xa1\n\xe3:9\x02\x958$\xe1\xb0Q\xb2\xd9\x08k\xa9\xd9\xff\xba\x11T\xbcXU\xb0H\xf7\x1b(\\\xd0\x85U\x01\xbc*\t\xe8\xc7\x12V\xe0^t\xf4\xd1\xfd\xb6\x89\xf1\n\x97\x8d\xdfLG\xf9,\xd7\x9d\xff\x8c\xd6\xd4\xaf\xfd\x19\xe2\x11\xb2\x97\x12\x85\xe2z\xaa\xc1\xf0rs\x7fo\xe2\xeb\xcc*\xe7,B\x05\x8c\x8d\xaf[g\xadg\xc3d\x8f\xa3c\xeej\xe2\x0f\x04\x8dZ\xc7\x9a\x13o\x17\xdfu\xb4\xdd\xe5\x1c\x9c\xb3\x10\x9de\xf8\xc0\x96\x15O\x9a1\xde\x8e\x8e\xb8\x03>\xbd\xe7\x10\x9bm\x7f9\xd2\xb5\xdc\xf0\xc5`\xf3Q\x1ecoo[\xd953f\\#\xb7\x8f\xf81\x8cn/\xdci\x8c\x0e\xb6e\xe9d\x01:\xc3\xc8\x8e\x1d+\xf9\xde\x8c12L\xd4:x\xdd7\xd7\x14]\x9a\xbc\xfe\xd80-F\x85\x0c\xfd\xb0kE\x07\xbf\x9b\xf5f \xe46\x8eR\xa3D\xc5\xb0\xd74\x1f\xff\xfcdb\xbc\xcb\xe0K\xcc\xbb\x99\xf8a\xe5\x9f\xfe6y\x07\xcatkz\xd2^1r\xda/F<\x18Z\x9a\xc6\'\x17\xde\xac=/v\xd8\x9cnt\x8e\xa50\xfd\xd3*q\xeb\x8f)\x91\x892\xdcaQbS[CT\x98\xd9\xd8\xda\x1d\xea\xef\x1c\xda\xd0/\xe1_\xf2\xaa\x17v')
    sha1_checksum_list = []
    a_tdl = serialization.DeserializeToDoList2(
        reader,
        tdl_factory=None,
        sha1_checksum_list=sha1_checksum_list)
    self.assertEqual(sha1_checksum_list, ["015bf1f05eb048f4afbaa2cc1862bba667b0c51a"])
    a_tdl.CheckIsWellFormed()
    expected = r"""
inbox {
  common {
    is_deleted: false
    timestamp {
      ctime: 1572755356644099
      dtime: -1
      mtime: 1572755356644214
    }
    metadata {
      name: "inbox"
    }
    uid: 1
  }
  is_complete: false
  is_active: true
}
root {
  common {
    is_deleted: false
    timestamp {
      ctime: 1572755356644234
      dtime: -1
      mtime: 1572755356647872
    }
    metadata {
      name: ""
    }
    uid: 2
  }
  projects {
    common {
      is_deleted: false
      timestamp {
        ctime: 1572755356647407
        dtime: -1
        mtime: 1572755356647511
      }
      metadata {
        name: "miscellaneous"
      }
      uid: -2691917185577266486
    }
    is_complete: false
    is_active: true
  }
  projects {
    common {
      is_deleted: false
      timestamp {
        ctime: 1572755356647740
        dtime: -1
        mtime: 1572755356649325
      }
      metadata {
        name: "learn how to use this to-do list"
      }
      uid: -6228955947767834205
    }
    is_complete: false
    is_active: true
    actions {
      common {
        is_deleted: false
        timestamp {
          ctime: 1572755356648216
          dtime: -1
          mtime: 1572755356648290
        }
        metadata {
          name: "Watch the video on the \"Help\" page -- find it on the top navigation bar"
        }
        uid: -5999470986166506153
      }
      is_complete: false
    }
    actions {
      common {
        is_deleted: false
        timestamp {
          ctime: 1572755356648676
          dtime: -1
          mtime: 1572755356648750
        }
        metadata {
          name: "Read the book \"Getting Things Done\" by David Allen"
        }
        uid: 7673523970316323628
      }
      is_complete: false
    }
    actions {
      common {
        is_deleted: false
        timestamp {
          ctime: 1572755356649231
          dtime: -1
          mtime: 1572755356649317
        }
        metadata {
          name: "After reading the book, try out a Weekly Review -- on the top navigation bar, find it underneath the \"Other\" drop-down"
        }
        uid: 5286905296357840176
      }
      is_complete: false
    }
  }
}
ctx_list {
  common {
    is_deleted: false
    timestamp {
      ctime: 1572755356644341
      dtime: -1
      mtime: 1572755356646974
    }
    metadata {
      name: "Contexts"
    }
    uid: -1831325979230752603
  }
  contexts {
    common {
      is_deleted: false
      timestamp {
        ctime: 1572755356645073
        dtime: -1
        mtime: 1572755356645143
      }
      metadata {
        name: "@computer"
      }
      uid: -5974514507641928914
    }
    is_active: true
  }
  contexts {
    common {
      is_deleted: false
      timestamp {
        ctime: 1572755356645409
        dtime: -1
        mtime: 1572755356645479
      }
      metadata {
        name: "@phone"
      }
      uid: -1512782132116461908
    }
    is_active: true
  }
  contexts {
    common {
      is_deleted: false
      timestamp {
        ctime: 1572755356645668
        dtime: -1
        mtime: 1572755356645736
      }
      metadata {
        name: "@home"
      }
      uid: 1087207337633397033
    }
    is_active: true
  }
  contexts {
    common {
      is_deleted: false
      timestamp {
        ctime: 1572755356646032
        dtime: -1
        mtime: 1572755356646108
      }
      metadata {
        name: "@work"
      }
      uid: -5320749029987709236
    }
    is_active: true
  }
  contexts {
    common {
      is_deleted: false
      timestamp {
        ctime: 1572755356646367
        dtime: -1
        mtime: 1572755356646434
      }
      metadata {
        name: "@the store"
      }
      uid: -7683460069187091841
    }
    is_active: true
  }
  contexts {
    common {
      is_deleted: false
      timestamp {
        ctime: 1572755356646615
        dtime: -1
        mtime: 1572755356647099
      }
      metadata {
        name: "@someday/maybe"
      }
      uid: 4502370912509346313
    }
    is_active: false
  }
  contexts {
    common {
      is_deleted: false
      timestamp {
        ctime: 1572755356646855
        dtime: -1
        mtime: 1572755356647199
      }
      metadata {
        name: "@waiting for"
      }
      uid: -1277248772270966966
    }
    is_active: false
  }
}
""".lstrip()
    self.assertEqual(text_format.MessageToString(a_tdl.AsProto()), expected)


if __name__ == '__main__':
  unitjest.main()
