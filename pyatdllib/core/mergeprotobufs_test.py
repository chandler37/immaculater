"""Unittests for module 'mergeprotobufs'."""

import os
import random
import time

from typing import Dict, List, Tuple, Union

from google.protobuf import text_format  # type: ignore

from pyatdllib.core import action
from pyatdllib.core import mergeprotobufs
from pyatdllib.core import pyatdl_pb2
from pyatdllib.core import prj
from pyatdllib.core import tdl
from pyatdllib.core import uid
from pyatdllib.core import unitjest

_MICROS = 10**6
year1970microsec = 10**6 * _MICROS  # 1970-01-12 05:46:40
year5454microsec = 109951162777 * _MICROS  # 5454-03-19 14:39:37 PST8PDT


_OLDPRJ = """
  projects {
    common {
      is_deleted: false
      timestamp {
        ctime: 38000000
        dtime: -1
        mtime: 39000000
      }
      metadata {
        name: "oldprj"
      }
      uid: -15
    }
    is_complete: false
    is_active: true
    actions {
      common {
        is_deleted: false
        timestamp {
          ctime: 39000000
          dtime: -1
          mtime: 39000000
        }
        metadata {
          name: "old_action_in_oldprj"
        }
        uid: -29
      }
      is_complete: false
    }
  }
"""

_OLDPRJ_IN_NEW_FOLDER = """
  common {
    is_deleted: false
    timestamp {
      ctime: 38000000
      dtime: -1
      mtime: 38000000
    }
    metadata {
      name: "newfolder"
    }
    uid: -6279119140261074202
  }""" + _OLDPRJ

text_formatted_protobuf_well_known = """
inbox {
  common {
    is_deleted: false
    timestamp {
      ctime: 1000000001000000
      dtime: -1
      mtime: 1000000001000000
    }
    metadata {
      name: "inbox"
    }
    uid: 1
  }
  is_complete: false
  is_active: true
  actions {
    common {
      is_deleted: false
      timestamp {
        ctime: 1000000000001
        dtime: -1
        mtime: 1000000001000000
      }
      metadata {
        name: "buy light bulbs"
        note: "60w"
      }
      uid: -5
    }
    is_complete: false
  }
}
root {
  common {
    is_deleted: false
    timestamp {
      ctime: 1000000001000000
      dtime: -1
      mtime: 1000000001000000
    }
    uid: 2
  }
  projects {
    common {
      is_deleted: false
      timestamp {
        ctime: 1000000000000
        dtime: -1
        mtime: 1000000001000000
      }
      metadata {
        name: "P1"
      }
      uid: -6
    }
    is_complete: false
    is_active: false
  }
}
ctx_list {
  contexts {
    common {
      is_deleted: false
      timestamp {
        ctime: 1558072527256254
        dtime: -1
        mtime: 1558072527256359
      }
      metadata {
        name: "@computer"
      }
      uid: -48
    }
    is_active: true
  }
}
note_list {
  notes {
    name: ":__home"
    note: "this is the note on the home page"
  }
}
"""

text_formatted_protobuf_1 = """
inbox {
  common {
    is_deleted: false
    timestamp {
      ctime: %(year5454microsec)d
      dtime: -1
      mtime: %(year5454microsec)d
    }
    metadata {
      name: "new name for what was once the inbox"
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
      ctime: 1000000001000000
      dtime: -1
      mtime: 1000000001000000
    }
    uid: 2
  }
}
""" % {'year5454microsec': year5454microsec}

text_formatted_protobuf_dicts: List[Tuple[str, Dict[str, Union[str, bool]]]] = []
with open(
  os.path.join(os.path.dirname(__file__), 'mergeprotobufs_test_data3.pbtxt'),
  mode='rt') as f:
  _REAL_WORLD_EXAMPLE_DB = f.read()
with open(
  os.path.join(os.path.dirname(__file__), 'mergeprotobufs_test_data3_remote.pbtxt'),
  mode='rt') as f:
  _REAL_WORLD_EXAMPLE_REMOTE = f.read()
text_formatted_protobuf_dicts.append(
  ('A project "z fyi" in root moves into a folder "zz back burner" that already has a prj "T27" in it (reproducing a '
   'real bug found in the field)',
   {
     'database': _REAL_WORLD_EXAMPLE_DB,
     'remote': _REAL_WORLD_EXAMPLE_REMOTE
   }))

text_formatted_protobuf_dicts.append(
  ('Moves a prj out of a folder -109 into the root folder',
   {
     'database': """
inbox {
  common {
    is_deleted: false
    timestamp {
      ctime: 1000000001000000
      dtime: -1
      mtime: 1000000001000000
    }
    metadata {
      name: "inbox"
    }
    uid: 1
  }
  is_complete: false
  is_active: true
  actions {
    common {
      is_deleted: false
      timestamp {
        ctime: 1000000000001
        dtime: -1
        mtime: 1000000001000000
      }
      metadata {
        name: "buy light bulbs"
        note: "60w"
      }
      uid: -5
    }
    is_complete: false
  }
}
root {
  common {
    is_deleted: false
    timestamp {
      ctime: 38000000
      dtime: -1
      mtime: 1000000001000000
    }
    uid: 2
  }
  folders {
    common {
      is_deleted: false
      timestamp {
        ctime: 38000000
        dtime: -1
        mtime: 1000000001000000
      }
      metadata {
        name: "folder9"
      }
      uid: -109
    }
    projects {
      common {
        is_deleted: false
        timestamp {
          ctime: 38000000
          dtime: -1
          mtime: 39000000
        }
        metadata {
          name: "prj9"
        }
        uid: -110
      }
      is_complete: false
      is_active: true
      actions {
        common {
          is_deleted: false
          timestamp {
            ctime: 39000000
            dtime: -1
            mtime: 39000000
          }
          metadata {
            name: "action_in_prj9"
          }
          uid: -111
        }
        is_complete: false
      }
    }
  }
  projects {
    common {
      is_deleted: false
      timestamp {
        ctime: 1000000000000
        dtime: -1
        mtime: 1000000001000000
      }
      metadata {
        name: "P1"
      }
      uid: -6
    }
    is_complete: false
    is_active: false
  }
}
ctx_list {
  contexts {
    common {
      is_deleted: false
      timestamp {
        ctime: 1558072527256254
        dtime: -1
        mtime: 1558072527256359
      }
      metadata {
        name: "@computer"
      }
      uid: -48
    }
    is_active: true
  }
}
note_list {
  notes {
    name: ":__home"
    note: "this is the note on the home page"
  }
}
""",
     'remote': """
inbox {
  common {
    is_deleted: false
    timestamp {
      ctime: 1000000001000000
      dtime: -1
      mtime: 1000000001000000
    }
    metadata {
      name: "inbox"
    }
    uid: 1
  }
  is_complete: false
  is_active: true
  actions {
    common {
      is_deleted: false
      timestamp {
        ctime: 1000000000001
        dtime: -1
        mtime: 1000000001000000
      }
      metadata {
        name: "buy light bulbs"
        note: "60w"
      }
      uid: -5
    }
    is_complete: false
  }
}
root {
  common {
    is_deleted: false
    timestamp {
      ctime: 38000000
      dtime: -1
      mtime: 1000000001000000
    }
    uid: 2
  }
  folders {
    common {
      is_deleted: false
      timestamp {
        ctime: 38000000
        dtime: -1
        mtime: 1000000001000000
      }
      metadata {
        name: "folder9"
      }
      uid: -109
    }
  }
  projects {
    common {
      is_deleted: false
      timestamp {
        ctime: 1000000000000
        dtime: -1
        mtime: 1000000001000000
      }
      metadata {
        name: "P1"
      }
      uid: -6
    }
    is_complete: false
    is_active: false
  }
  projects {
    common {
      is_deleted: false
      timestamp {
        ctime: 38000000
        dtime: -1
        mtime: 39000000
      }
      metadata {
        name: "prj9"
      }
      uid: -110
    }
    is_complete: false
    is_active: true
    actions {
      common {
        is_deleted: false
        timestamp {
          ctime: 39000000
          dtime: -1
          mtime: 39000000
        }
        metadata {
          name: "action_in_prj9"
        }
        uid: -111
      }
      is_complete: false
    }
  }
}
ctx_list {
  contexts {
    common {
      is_deleted: false
      timestamp {
        ctime: 1558072527256254
        dtime: -1
        mtime: 1558072527256359
      }
      metadata {
        name: "@computer"
      }
      uid: -48
    }
    is_active: true
  }
}
note_list {
  notes {
    name: ":__home"
    note: "this is the note on the home page"
  }
}
"""
   }))

# The following test case, when 'remote' and 'database' are swapped, revealed a bug. The diff between database and
# remote is as follows:
#
# *** /tmp/db	2021-02-06 13:29:36.000000000 -0500
# --- /tmp/remote	2021-02-06 13:29:39.000000000 -0500
# ***************
# *** 49,101 ****
#           mtime: 1000000001000000
#         }
#         metadata {
# !         name: "folder10"
#         }
# !       uid: -209
#       }
# !     folders {
#         common {
#           is_deleted: false
#           timestamp {
#             ctime: 38000000
#             dtime: -1
# !           mtime: 1000000001000000
#           }
#           metadata {
# !           name: "folder9"
#           }
# !         uid: -109
#         }
# !       projects {
#           common {
#             is_deleted: false
#             timestamp {
# !             ctime: 38000000
#               dtime: -1
#               mtime: 39000000
#             }
#             metadata {
# !             name: "prj9"
#             }
# !           uid: -110
#           }
#           is_complete: false
# -         is_active: true
# -         actions {
# -           common {
# -             is_deleted: false
# -             timestamp {
# -               ctime: 39000000
# -               dtime: -1
# -               mtime: 39000000
# -             }
# -             metadata {
# -               name: "action_in_prj9"
# -             }
# -             uid: -111
# -           }
# -           is_complete: false
# -         }
#         }
#       }
#     }
# --- 49,87 ----
#           mtime: 1000000001000000
#         }
#         metadata {
# !         name: "folder9"
#         }
# !       uid: -109
#       }
# !     projects {
#         common {
#           is_deleted: false
#           timestamp {
#             ctime: 38000000
#             dtime: -1
# !           mtime: 39000000
#           }
#           metadata {
# !           name: "prj9"
#           }
# !         uid: -110
#         }
# !       is_complete: false
# !       is_active: true
# !       actions {
#           common {
#             is_deleted: false
#             timestamp {
# !             ctime: 39000000
#               dtime: -1
#               mtime: 39000000
#             }
#             metadata {
# !             name: "action_in_prj9"
#             }
# !           uid: -111
#           }
#           is_complete: false
#         }
#       }
#     }
#
#     In words, what has happened is that folder10 has disappeared. This is unrealistic behavior on the part of an
#     application because the correct merged form "resurrects" folder10. But the merged form should have an empty
#     folder10 with folder9 having parent Folder 'root'. prj9 remains underneath folder9 (which means that it too moves).
text_formatted_protobuf_dicts.append(
  ('folder10 disappears in a way that it would not in a well-written app',
   {
     'database': """
inbox {
  common {
    is_deleted: false
    timestamp {
      ctime: 1000000001000000
      dtime: -1
      mtime: 1000000001000000
    }
    metadata {
      name: "inbox"
    }
    uid: 1
  }
  is_complete: false
  is_active: true
  actions {
    common {
      is_deleted: false
      timestamp {
        ctime: 1000000000001
        dtime: -1
        mtime: 1000000001000000
      }
      metadata {
        name: "buy light bulbs"
        note: "60w"
      }
      uid: -5
    }
    is_complete: false
  }
}
root {
  common {
    is_deleted: false
    timestamp {
      ctime: 38000000
      dtime: -1
      mtime: 1000000001000000
    }
    uid: 2
  }
  folders {
    common {
      is_deleted: false
      timestamp {
        ctime: 38000000
        dtime: -1
        mtime: 1000000001000000
      }
      metadata {
        name: "folder9"
      }
      uid: -109
    }
    projects {
      common {
        is_deleted: false
        timestamp {
          ctime: 38000000
          dtime: -1
          mtime: 39000000
        }
        metadata {
          name: "prj9"
        }
        uid: -110
      }
      is_complete: false
      is_active: true
      actions {
        common {
          is_deleted: false
          timestamp {
            ctime: 39000000
            dtime: -1
            mtime: 39000000
          }
          metadata {
            name: "action_in_prj9"
          }
          uid: -111
        }
        is_complete: false
      }
    }
  }
  projects {
    common {
      is_deleted: false
      timestamp {
        ctime: 1000000000000
        dtime: -1
        mtime: 1000000001000000
      }
      metadata {
        name: "P1"
      }
      uid: -6
    }
    is_complete: false
    is_active: false
  }
}
ctx_list {
  contexts {
    common {
      is_deleted: false
      timestamp {
        ctime: 1558072527256254
        dtime: -1
        mtime: 1558072527256359
      }
      metadata {
        name: "@computer"
      }
      uid: -48
    }
    is_active: true
  }
}
note_list {
  notes {
    name: ":__home"
    note: "this is the note on the home page"
  }
}
""",
     'remote': """
inbox {
  common {
    is_deleted: false
    timestamp {
      ctime: 1000000001000000
      dtime: -1
      mtime: 1000000001000000
    }
    metadata {
      name: "inbox"
    }
    uid: 1
  }
  is_complete: false
  is_active: true
  actions {
    common {
      is_deleted: false
      timestamp {
        ctime: 1000000000001
        dtime: -1
        mtime: 1000000001000000
      }
      metadata {
        name: "buy light bulbs"
        note: "60w"
      }
      uid: -5
    }
    is_complete: false
  }
}
root {
  common {
    is_deleted: false
    timestamp {
      ctime: 38000000
      dtime: -1
      mtime: 1000000001000000
    }
    uid: 2
  }
  folders {
    common {
      is_deleted: false
      timestamp {
        ctime: 38000000
        dtime: -1
        mtime: 1000000001000000
      }
      metadata {
        name: "folder10"
      }
      uid: -209
    }
    folders {
      common {
        is_deleted: false
        timestamp {
          ctime: 38000000
          dtime: -1
          mtime: 1000000001000000
        }
        metadata {
          name: "folder9"
        }
        uid: -109
      }
      projects {
        common {
          is_deleted: false
          timestamp {
            ctime: 38000000
            dtime: -1
            mtime: 39000000
          }
          metadata {
            name: "prj9"
          }
          uid: -110
        }
        is_complete: false
        is_active: true
        actions {
          common {
            is_deleted: false
            timestamp {
              ctime: 39000000
              dtime: -1
              mtime: 39000000
            }
            metadata {
              name: "action_in_prj9"
            }
            uid: -111
          }
          is_complete: false
        }
      }
    }
  }
  projects {
    common {
      is_deleted: false
      timestamp {
        ctime: 1000000000000
        dtime: -1
        mtime: 1000000001000000
      }
      metadata {
        name: "P1"
      }
      uid: -6
    }
    is_complete: false
    is_active: false
  }
}
ctx_list {
  contexts {
    common {
      is_deleted: false
      timestamp {
        ctime: 1558072527256254
        dtime: -1
        mtime: 1558072527256359
      }
      metadata {
        name: "@computer"
      }
      uid: -48
    }
    is_active: true
  }
}
note_list {
  notes {
    name: ":__home"
    note: "this is the note on the home page"
  }
}
"""
   }))

text_formatted_protobuf_dicts.append(
  ('Move action -111 from prj -110 to prj -6',
   {
     'unidirectional': True,
     'database': """
inbox {
  common {
    is_deleted: false
    timestamp {
      ctime: 1000000001000000
      dtime: -1
      mtime: 1000000001000000
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
      ctime: 38000000
      dtime: -1
      mtime: 1000000001000000
    }
    uid: 2
  }
  folders {
    common {
      is_deleted: false
      timestamp {
        ctime: 38000000
        dtime: -1
        mtime: 1000000001000000
      }
      metadata {
        name: "folder9"
      }
      uid: -109
    }
    projects {
      common {
        is_deleted: false
        timestamp {
          ctime: 38000000
          dtime: -1
          mtime: 39000000
        }
        metadata {
          name: "prj9"
        }
        uid: -110
      }
      is_complete: false
      is_active: true
      actions {
        common {
          is_deleted: false
          timestamp {
            ctime: 39000000
            dtime: -1
            mtime: 39000000
          }
          metadata {
            name: "action_in_prj9"
          }
          uid: -111
        }
        is_complete: false
      }
    }
  }
  projects {
    common {
      is_deleted: false
      timestamp {
        ctime: 1000000000000
        dtime: -1
        mtime: 1000000001000000
      }
      metadata {
        name: "P1"
      }
      uid: -6
    }
    is_complete: false
    is_active: false
  }
}
""",
     'remote': """
inbox {
  common {
    is_deleted: false
    timestamp {
      ctime: 1000000001000000
      dtime: -1
      mtime: 1000000001000000
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
      ctime: 38000000
      dtime: -1
      mtime: 1000000001000000
    }
    uid: 2
  }
  folders {
    common {
      is_deleted: false
      timestamp {
        ctime: 38000000
        dtime: -1
        mtime: 1000000001000000
      }
      metadata {
        name: "folder9"
      }
      uid: -109
    }
    projects {
      common {
        is_deleted: false
        timestamp {
          ctime: 38000000
          dtime: -1
          mtime: 39000000
        }
        metadata {
          name: "prj9"
        }
        uid: -110
      }
      is_complete: false
      is_active: true
    }
  }
  projects {
    common {
      is_deleted: false
      timestamp {
        ctime: 1000000000000
        dtime: -1
        mtime: 1000000001000000
      }
      metadata {
        name: "P1"
      }
      uid: -6
    }
    is_complete: false
    is_active: false
    actions {
      common {
        is_deleted: false
        timestamp {
          ctime: 39000000
          dtime: -1
          mtime: 39000001
        }
        metadata {
          name: "action_in_prj9 but with a new name"
        }
        uid: -111
      }
      is_complete: false
    }
  }
}
"""
   }))
text_formatted_protobuf_dicts.append(
  ('Move action -111 from prj -110 to prj -6 (reversed)',
   {
     'unidirectional': True,
     'correct_winner': 'mix',
     # TODO(chandler37): For consistency, do this instead of _TXT_PB*:
     'database': text_formatted_protobuf_dicts[-1][1]['remote'],
     'remote': text_formatted_protobuf_dicts[-1][1]['database'],
     'mix': """
inbox {
  common {
    is_deleted: false
    timestamp {
      ctime: 1000000001000000
      dtime: -1
      mtime: 1000000001000000
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
      ctime: 38000000
      dtime: -1
      mtime: 1000000001000000
    }
    uid: 2
  }
  folders {
    common {
      is_deleted: false
      timestamp {
        ctime: 38000000
        dtime: -1
        mtime: 1000000001000000
      }
      metadata {
        name: "folder9"
      }
      uid: -109
    }
    projects {
      common {
        is_deleted: false
        timestamp {
          ctime: 38000000
          dtime: -1
          mtime: 39000000
        }
        metadata {
          name: "prj9"
        }
        uid: -110
      }
      is_complete: false
      is_active: true
    }
  }
  projects {
    common {
      is_deleted: false
      timestamp {
        ctime: 1000000000000
        dtime: -1
        mtime: 1000000001000000
      }
      metadata {
        name: "P1"
      }
      uid: -6
    }
    is_complete: false
    is_active: false
    actions {
      common {
        is_deleted: false
        timestamp {
          ctime: 39000000
          dtime: -1
          mtime: 39000001
        }
        metadata {
          name: "action_in_prj9 but with a new name"
        }
        uid: -111
      }
      is_complete: false
    }
  }
}
"""
   })
)

text_formatted_protobuf_dicts.append(
  ('Merge1RightMovedAction',
   {
     'unidirectional': True,
     'database': """
inbox {
  common {
    is_deleted: false
    timestamp {
      ctime: 1000000001000000
      dtime: -1
      mtime: 1000000001000000
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
      ctime: 1000000001000000
      dtime: -1
      mtime: 1000000001000000
    }
    uid: 2
  }
  projects {
    common {
      timestamp {
        ctime: 1000000000000
        mtime: 1000000000000
      }
      metadata {
        name: "P1"
      }
      uid: -6
    }
    actions {
      common {
        timestamp {
          ctime: 1000000000000
          mtime: 1000000000000
        }
        metadata {
          name: "A1 was once the name"
        }
        uid: -5
      }
    }
  }
}
""",
     'remote': """
inbox {
  common {
    is_deleted: false
    timestamp {
      ctime: 1000000001000000
      dtime: -1
      mtime: 1000000001000000
    }
    metadata {
      name: "inbox"
    }
    uid: 1
  }
  is_complete: false
  is_active: true
  actions {
    common {
      timestamp {
        ctime: 1000000000001
        mtime: 1000000000001
      }
      metadata {
        name: "buy light bulbs"
        note: "60w"
      }
      uid: -5
    }
  }
}
root {
  common {
    is_deleted: false
    timestamp {
      ctime: 1000000001000000
      dtime: -1
      mtime: 1000000001000000
    }
    uid: 2
  }
}
""",
     'mix': """
inbox {
  common {
    is_deleted: false
    timestamp {
      ctime: 1000000001000000
      dtime: -1
      mtime: 1000000001000000
    }
    metadata {
      name: "inbox"
    }
    uid: 1
  }
  is_complete: false
  is_active: true
  actions {
    common {
      is_deleted: false
      timestamp {
        ctime: 1000000000001
        dtime: -1
        mtime: 1000000000001
      }
      metadata {
        name: "buy light bulbs"
        note: "60w"
      }
      uid: -5
    }
    is_complete: false
  }
}
root {
  common {
    is_deleted: false
    timestamp {
      ctime: 1000000001000000
      dtime: -1
      mtime: 1000000001000000
    }
    uid: 2
  }
  projects {
    common {
      is_deleted: false
      timestamp {
        ctime: 1000000000000
        dtime: -1
        mtime: 1000000000000
      }
      metadata {
        name: "P1"
      }
      uid: -6
    }
    is_complete: false
    is_active: false
  }
}
""",
     'correct_winner': 'mix'
   })
)

text_formatted_protobuf_dicts.append(
  ('An action -5 changed metadata and project but mtime tells us the true project and metadata.',
   {
     'unidirectional': True,
     'database': """
inbox {
  common {
    is_deleted: false
    timestamp {
      ctime: 1000000001000000
      dtime: -1
      mtime: 1000000001000000
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
      ctime: 1000000001000000
      dtime: -1
      mtime: 1000000001000000
    }
    uid: 2
  }
  projects {
    common {
      timestamp {
        ctime: 1000000000001
        mtime: 1000000000001
      }
      metadata {
        name: "P1"
      }
      uid: -6
    }
    actions {
      common {
        timestamp {
          ctime: 1000000000001
          mtime: 1000000000001
        }
        metadata {
          name: "name associated with mtime 1000000000001"
        }
        uid: -5
      }
    }
  }
}
""",
     'remote': """
inbox {
  common {
    is_deleted: false
    timestamp {
      ctime: 1000000001000000
      dtime: -1
      mtime: 1000000001000000
    }
    metadata {
      name: "inbox"
    }
    uid: 1
  }
  is_complete: false
  is_active: true
  actions {
    common {
      timestamp {
        ctime: 1000000000000
        mtime: 1000000000000
      }
      metadata {
        name: "buy light bulbs"
        note: "60w"
      }
      uid: -5
    }
  }
}
root {
  common {
    is_deleted: false
    timestamp {
      ctime: 1000000001000000
      dtime: -1
      mtime: 1000000001000000
    }
    uid: 2
  }
}
""",
     'correct_winner': 'mix',
     'mix': """
inbox {
  common {
    is_deleted: false
    timestamp {
      ctime: 1000000001000000
      dtime: -1
      mtime: 1000000001000000
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
      ctime: 1000000001000000
      dtime: -1
      mtime: 1000000001000000
    }
    uid: 2
  }
  projects {
    common {
      is_deleted: false
      timestamp {
        ctime: 1000000000001
        dtime: -1
        mtime: 1000000000001
      }
      metadata {
        name: "P1"
      }
      uid: -6
    }
    is_complete: false
    is_active: false
    actions {
      common {
        is_deleted: false
        timestamp {
          ctime: 1000000000001
          dtime: -1
          mtime: 1000000000001
        }
        metadata {
          name: "name associated with mtime 1000000000001"
        }
        uid: -5
      }
      is_complete: false
    }
  }
}
"""
   })
)

text_formatted_protobuf_dicts.append(
  ('move an action into the inbox',
   {
     'database': """
inbox {
  common {
    is_deleted: false
    timestamp {
      ctime: 1000000001000000
      dtime: -1
      mtime: 1000000001000000
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
      ctime: 38000000
      dtime: -1
      mtime: 1000000001000000
    }
    uid: 2
  }
  folders {
    common {
      is_deleted: false
      timestamp {
        ctime: 38000000
        dtime: -1
        mtime: 1000000001000000
      }
      metadata {
        name: "folder9"
      }
      uid: -109
    }
    projects {
      common {
        is_deleted: false
        timestamp {
          ctime: 38000000
          dtime: -1
          mtime: 39000000
        }
        metadata {
          name: "prj9"
        }
        uid: -110
      }
      is_complete: false
      is_active: true
      actions {
        common {
          is_deleted: false
          timestamp {
            ctime: 39000000
            dtime: -1
            mtime: 39000000
          }
          metadata {
            name: "action_in_prj9"
          }
          uid: -111
        }
        is_complete: false
      }
    }
  }
  projects {
    common {
      is_deleted: false
      timestamp {
        ctime: 1000000000000
        dtime: -1
        mtime: 1000000001000000
      }
      metadata {
        name: "P1"
      }
      uid: -6
    }
    is_complete: false
    is_active: false
  }
}
ctx_list {
  contexts {
    common {
      is_deleted: false
      timestamp {
        ctime: 1558072527256254
        dtime: -1
        mtime: 1558072527256359
      }
      metadata {
        name: "@computer"
      }
      uid: -48
    }
    is_active: true
  }
}
note_list {
  notes {
    name: ":__home"
    note: "this is the note on the home page"
  }
}
""",
     'remote': """
inbox {
  common {
    is_deleted: false
    timestamp {
      ctime: 1000000001000000
      dtime: -1
      mtime: 1000000001000000
    }
    metadata {
      name: "inbox"
    }
    uid: 1
  }
  is_complete: false
  is_active: true
  actions {
    common {
      is_deleted: false
      timestamp {
        ctime: 39000000
        dtime: -1
        mtime: 39000000
      }
      metadata {
        name: "action_in_prj9"
      }
      uid: -111
    }
    is_complete: false
  }
}
root {
  common {
    is_deleted: false
    timestamp {
      ctime: 38000000
      dtime: -1
      mtime: 1000000001000000
    }
    uid: 2
  }
  folders {
    common {
      is_deleted: false
      timestamp {
        ctime: 38000000
        dtime: -1
        mtime: 1000000001000000
      }
      metadata {
        name: "folder9"
      }
      uid: -109
    }
    projects {
      common {
        is_deleted: false
        timestamp {
          ctime: 38000000
          dtime: -1
          mtime: 39000000
        }
        metadata {
          name: "prj9"
        }
        uid: -110
      }
      is_complete: false
      is_active: true
    }
  }
  projects {
    common {
      is_deleted: false
      timestamp {
        ctime: 1000000000000
        dtime: -1
        mtime: 1000000001000000
      }
      metadata {
        name: "P1"
      }
      uid: -6
    }
    is_complete: false
    is_active: false
  }
}
ctx_list {
  contexts {
    common {
      is_deleted: false
      timestamp {
        ctime: 1558072527256254
        dtime: -1
        mtime: 1558072527256359
      }
      metadata {
        name: "@computer"
      }
      uid: -48
    }
    is_active: true
  }
}
note_list {
  notes {
    name: ":__home"
    note: "this is the note on the home page"
  }
}
"""
   }))

_TXT_PB0 = """
inbox {
  common {
    is_deleted: false
    timestamp {
      ctime: 1000000001000000
      dtime: -1
      mtime: 1000000001000000
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
      ctime: 38000000
      dtime: -1
      mtime: 1000000001000000
    }
    uid: 2
  }
  folders {
    common {
      is_deleted: false
      timestamp {
        ctime: 38000000
        dtime: -1
        mtime: 1000000001000000
      }
      metadata {
        name: "folder9"
      }
      uid: -109
    }
    projects {
      common {
        is_deleted: false
        timestamp {
          ctime: 38000000
          dtime: -1
          mtime: 39000000
        }
        metadata {
          name: "prj9"
        }
        uid: -110
      }
      is_complete: false
      is_active: true
      actions {
        common {
          is_deleted: false
          timestamp {
            ctime: 39000000
            dtime: -1
            mtime: 39000000111
          }
          metadata {
            name: "action_in_prj9 that was changed on the web hence mtime here is higher"
          }
          uid: -111
        }
        is_complete: false
      }
    }
  }
  projects {
    common {
      is_deleted: false
      timestamp {
        ctime: 1000000000000
        dtime: -1
        mtime: 1000000001000000
      }
      metadata {
        name: "P1"
      }
      uid: -6
    }
    is_complete: false
    is_active: false
  }
}
"""

_TXT_PB1 = """
inbox {
  common {
    is_deleted: false
    timestamp {
      ctime: 1000000001000000
      dtime: -1
      mtime: 1000000001000000
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
      ctime: 38000000
      dtime: -1
      mtime: 1000000001000000
    }
    uid: 2
  }
  folders {
    common {
      is_deleted: false
      timestamp {
        ctime: 38000000
        dtime: -1
        mtime: 1000000001000000
      }
      metadata {
        name: "folder9"
      }
      uid: -109
    }
  }
  projects {
    common {
      is_deleted: false
      timestamp {
        ctime: 1000000000000
        dtime: -1
        mtime: 1000000001000000
      }
      metadata {
        name: "P1"
      }
      uid: -6
    }
    is_complete: false
    is_active: false
    actions {
      common {
        is_deleted: false
        timestamp {
          ctime: 39000000
          dtime: -1
          mtime: 39000000
        }
        metadata {
          name: "action_in_prj9 with an old name that should not survive the move"
        }
        uid: -111
      }
      is_complete: false
    }
  }
  projects {
    common {
      is_deleted: false
      timestamp {
        ctime: 38000000
        dtime: -1
        mtime: 39000000
      }
      metadata {
        name: "prj9"
      }
      uid: -110
    }
    is_complete: false
    is_active: true
  }
}
"""

text_formatted_protobuf_dicts.extend(
  [
    ('move an action -111 from prj -110 to -6 (not really: mtime negates the move) as its old prj (-110 initially '
     'inside -109) moves into a new folder 2 (_TXT_PB0=>_TXT_PB1)',
     {
       'unidirectional': True,
       'database': _TXT_PB0,
       'remote': _TXT_PB1,
       'correct_winner': 'mix',
       'mix': """
inbox {
  common {
    is_deleted: false
    timestamp {
      ctime: 1000000001000000
      dtime: -1
      mtime: 1000000001000000
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
      ctime: 38000000
      dtime: -1
      mtime: 1000000001000000
    }
    uid: 2
  }
  folders {
    common {
      is_deleted: false
      timestamp {
        ctime: 38000000
        dtime: -1
        mtime: 1000000001000000
      }
      metadata {
        name: "folder9"
      }
      uid: -109
    }
  }
  projects {
    common {
      is_deleted: false
      timestamp {
        ctime: 1000000000000
        dtime: -1
        mtime: 1000000001000000
      }
      metadata {
        name: "P1"
      }
      uid: -6
    }
    is_complete: false
    is_active: false
  }
  projects {
    common {
      is_deleted: false
      timestamp {
        ctime: 38000000
        dtime: -1
        mtime: 39000000
      }
      metadata {
        name: "prj9"
      }
      uid: -110
    }
    is_complete: false
    is_active: true
    actions {
      common {
        is_deleted: false
        timestamp {
          ctime: 39000000
          dtime: -1
          mtime: 39000000111
        }
        metadata {
          name: "action_in_prj9 that was changed on the web hence mtime here is higher"
        }
        uid: -111
      }
      is_complete: false
    }
  }
}
       """
     }),
    ('Careful not to move an action -111 from prj -110 to -6 (mtime dictates a non-move) as its old prj (-110 initially'
     ' inside -109) moves into a new folder 2 (_TXT_PB1=>_TXT_PB0)',
     {
       'unidirectional': True,
       'database': _TXT_PB1,
       'remote': _TXT_PB0,
       'correct_winner': 'mix',
       'mix': """
inbox {
  common {
    is_deleted: false
    timestamp {
      ctime: 1000000001000000
      dtime: -1
      mtime: 1000000001000000
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
      ctime: 38000000
      dtime: -1
      mtime: 1000000001000000
    }
    uid: 2
  }
  folders {
    common {
      is_deleted: false
      timestamp {
        ctime: 38000000
        dtime: -1
        mtime: 1000000001000000
      }
      metadata {
        name: "folder9"
      }
      uid: -109
    }
    projects {
      common {
        is_deleted: false
        timestamp {
          ctime: 38000000
          dtime: -1
          mtime: 39000000
        }
        metadata {
          name: "prj9"
        }
        uid: -110
      }
      is_complete: false
      is_active: true
      actions {
        common {
          is_deleted: false
          timestamp {
            ctime: 39000000
            dtime: -1
            mtime: 39000000111
          }
          metadata {
            name: "action_in_prj9 that was changed on the web hence mtime here is higher"
          }
          uid: -111
        }
        is_complete: false
      }
    }
  }
  projects {
    common {
      is_deleted: false
      timestamp {
        ctime: 1000000000000
        dtime: -1
        mtime: 1000000001000000
      }
      metadata {
        name: "P1"
      }
      uid: -6
    }
    is_complete: false
    is_active: false
  }
}
       """
     })
  ]
)

text_formatted_protobuf_dicts.append(
  ('move an action -111 from prj -110=>-6 as its old prj -110 moves into a new folder (-109=>2) -- but this time, '
   'modification time (mtime) demands that we use different metadata than above',
   {
     'unidirectional': True,
     'database': """
inbox {
  common {
    is_deleted: false
    timestamp {
      ctime: 1000000001000000
      dtime: -1
      mtime: 1000000001000000
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
      ctime: 38000000
      dtime: -1
      mtime: 1000000001000000
    }
    uid: 2
  }
  folders {
    common {
      is_deleted: false
      timestamp {
        ctime: 38000000
        dtime: -1
        mtime: 1000000001000000
      }
      metadata {
        name: "folder9"
      }
      uid: -109
    }
    projects {
      common {
        is_deleted: false
        timestamp {
          ctime: 38000000
          dtime: -1
          mtime: 39000000
        }
        metadata {
          name: "prj9"
        }
        uid: -110
      }
      is_complete: false
      is_active: true
      actions {
        common {
          is_deleted: false
          timestamp {
            ctime: 39000000
            dtime: -1
            mtime: 39000000
          }
          metadata {
            name: "action_in_prj9"
          }
          uid: -111
        }
        is_complete: false
      }
    }
  }
  projects {
    common {
      is_deleted: false
      timestamp {
        ctime: 1000000000000
        dtime: -1
        mtime: 1000000001000000
      }
      metadata {
        name: "P1"
      }
      uid: -6
    }
    is_complete: false
    is_active: false
  }
}
""",
     'remote': """
inbox {
  common {
    is_deleted: false
    timestamp {
      ctime: 1000000001000000
      dtime: -1
      mtime: 1000000001000000
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
      ctime: 38000000
      dtime: -1
      mtime: 1000000001000000
    }
    uid: 2
  }
  folders {
    common {
      is_deleted: false
      timestamp {
        ctime: 38000000
        dtime: -1
        mtime: 1000000001000000
      }
      metadata {
        name: "folder9"
      }
      uid: -109
    }
  }
  projects {
    common {
      is_deleted: false
      timestamp {
        ctime: 1000000000000
        dtime: -1
        mtime: 1000000001000000
      }
      metadata {
        name: "P1"
      }
      uid: -6
    }
    is_complete: false
    is_active: false
    actions {
      common {
        is_deleted: false
        timestamp {
          ctime: 37000000
          dtime: -1
          mtime: 38000000
        }
        metadata {
          name: "This will not be used because the higher mtime is 39000000."
        }
        uid: -111
      }
      is_complete: false
    }
  }
  projects {
    common {
      is_deleted: false
      timestamp {
        ctime: 38000000
        dtime: -1
        mtime: 39000000
      }
      metadata {
        name: "prj9"
      }
      uid: -110
    }
    is_complete: false
    is_active: true
  }
}
""",
     'correct_winner': 'mix',
     'mix': """
inbox {
  common {
    is_deleted: false
    timestamp {
      ctime: 1000000001000000
      dtime: -1
      mtime: 1000000001000000
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
      ctime: 38000000
      dtime: -1
      mtime: 1000000001000000
    }
    uid: 2
  }
  folders {
    common {
      is_deleted: false
      timestamp {
        ctime: 38000000
        dtime: -1
        mtime: 1000000001000000
      }
      metadata {
        name: "folder9"
      }
      uid: -109
    }
  }
  projects {
    common {
      is_deleted: false
      timestamp {
        ctime: 1000000000000
        dtime: -1
        mtime: 1000000001000000
      }
      metadata {
        name: "P1"
      }
      uid: -6
    }
    is_complete: false
    is_active: false
  }
  projects {
    common {
      is_deleted: false
      timestamp {
        ctime: 38000000
        dtime: -1
        mtime: 39000000
      }
      metadata {
        name: "prj9"
      }
      uid: -110
    }
    is_complete: false
    is_active: true
    actions {
      common {
        is_deleted: false
        timestamp {
          ctime: 39000000
          dtime: -1
          mtime: 39000000
        }
        metadata {
          name: "action_in_prj9"
        }
        uid: -111
      }
      is_complete: false
    }
  }
}
"""
   }))

_TXT_PB2 = """
inbox {
  common {
    is_deleted: false
    timestamp {
      ctime: 1000000001000000
      dtime: -1
      mtime: 1000000001000000
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
      ctime: 38000000
      dtime: -1
      mtime: 1000000001000000
    }
    uid: 2
  }
  folders {
    common {
      is_deleted: false
      timestamp {
        ctime: 38000000
        dtime: -1
        mtime: 1000000001000000
      }
      metadata {
        name: "folder9"
      }
      uid: -109
    }
    projects {
      common {
        is_deleted: false
        timestamp {
          ctime: 38000000
          dtime: -1
          mtime: 39000000
        }
        metadata {
          name: "prj9"
        }
        uid: -110
      }
      is_complete: false
      is_active: true
      actions {
        common {
          is_deleted: false
          timestamp {
            ctime: 39000000
            dtime: -1
            mtime: 39000000
          }
          metadata {
            name: "action_in_prj9"
          }
          uid: -111
        }
        is_complete: false
      }
    }
  }
  projects {
    common {
      is_deleted: false
      timestamp {
        ctime: 1000000000000
        dtime: -1
        mtime: 1000000001000000
      }
      metadata {
        name: "P1"
      }
      uid: -6
    }
    is_complete: false
    is_active: false
  }
}
"""

_TXT_PB3 = """
inbox {
  common {
    is_deleted: false
    timestamp {
      ctime: 1000000001000000
      dtime: -1
      mtime: 1000000001000000
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
      ctime: 38000000
      dtime: -1
      mtime: 1000000001000000
    }
    uid: 2
  }
  folders {
    common {
      is_deleted: false
      timestamp {
        ctime: 38000000
        dtime: -1
        mtime: 1000000001000000
      }
      metadata {
        name: "folder9"
      }
      uid: -109
    }
    projects {
      common {
        is_deleted: false
        timestamp {
          ctime: 38000000
          dtime: -1
          mtime: 39000000
        }
        metadata {
          name: "prj9"
        }
        uid: -110
      }
      is_complete: false
      is_active: true
    }
  }
  projects {
    common {
      is_deleted: false
      timestamp {
        ctime: 1000000000000
        dtime: -1
        mtime: 1000000001000000
      }
      metadata {
        name: "P1"
      }
      uid: -6
    }
    is_complete: false
    is_active: false
    actions {
      common {
        is_deleted: false
        timestamp {
          ctime: 39000000
          dtime: -1
          mtime: 39000001
        }
        metadata {
          name: "action_in_prj9 but renamed (with mtime incremented) to make sure we capture the renaming (and completed)"
        }
        uid: -111
      }
      is_complete: true
    }
  }
}
"""

text_formatted_protobuf_dicts.extend(
  [
    ('move an action from one prj (that itself is not moved into a new folder) into another prj (_TXT_PB2=>_TXT_PB3)',
     {
       'unidirectional': True,
       'database': _TXT_PB2,
       'remote': _TXT_PB3
     }),
    ('move an action from one prj (that itself is not moved into a new folder) into another prj (_TXT_PB3=>_TXT_PB2)',
     {
       'unidirectional': True,
       'database': _TXT_PB3,
       'remote': _TXT_PB2,
       'correct_winner': 'mix',
       'mix': """
inbox {
  common {
    is_deleted: false
    timestamp {
      ctime: 1000000001000000
      dtime: -1
      mtime: 1000000001000000
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
      ctime: 38000000
      dtime: -1
      mtime: 1000000001000000
    }
    uid: 2
  }
  folders {
    common {
      is_deleted: false
      timestamp {
        ctime: 38000000
        dtime: -1
        mtime: 1000000001000000
      }
      metadata {
        name: "folder9"
      }
      uid: -109
    }
    projects {
      common {
        is_deleted: false
        timestamp {
          ctime: 38000000
          dtime: -1
          mtime: 39000000
        }
        metadata {
          name: "prj9"
        }
        uid: -110
      }
      is_complete: false
      is_active: true
    }
  }
  projects {
    common {
      is_deleted: false
      timestamp {
        ctime: 1000000000000
        dtime: -1
        mtime: 1000000001000000
      }
      metadata {
        name: "P1"
      }
      uid: -6
    }
    is_complete: false
    is_active: false
    actions {
      common {
        is_deleted: false
        timestamp {
          ctime: 39000000
          dtime: -1
          mtime: 39000001
        }
        metadata {
          name: "action_in_prj9 but renamed (with mtime incremented) to make sure we capture the renaming (and completed)"
        }
        uid: -111
      }
      is_complete: true
    }
  }
}
"""
     })
  ]
)

text_formatted_protobuf_dicts.append(
  ('moves an action -111 from one prj -110 into another prj -6 (white-box test of prj.Prj.MergeFromProto)',
   {
     'database': """
inbox {
  common {
    is_deleted: false
    timestamp {
      ctime: 1000000001000000
      dtime: -1
      mtime: 1000000001000000
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
      ctime: 38000000
      dtime: -1
      mtime: 1000000001000000
    }
    uid: 2
  }
  folders {
    common {
      is_deleted: false
      timestamp {
        ctime: 38000000
        dtime: -1
        mtime: 1000000001000000
      }
      metadata {
        name: "folder9"
      }
      uid: -109
    }
    projects {
      common {
        is_deleted: false
        timestamp {
          ctime: 38000000
          dtime: -1
          mtime: 39000000
        }
        metadata {
          name: "prj9"
        }
        uid: -110
      }
      is_complete: false
      is_active: true
      actions {
        common {
          is_deleted: false
          timestamp {
            ctime: 39000000
            dtime: -1
            mtime: 39000000
          }
          metadata {
            name: "action_in_prj9"
          }
          uid: -111
        }
        is_complete: false
      }
    }
  }
  projects {
    common {
      is_deleted: false
      timestamp {
        ctime: 1000000000000
        dtime: -1
        mtime: 1000000001000000
      }
      metadata {
        name: "P1"
      }
      uid: -6
    }
    is_complete: false
    is_active: false
  }
}
""",
     'remote': """
inbox {
  common {
    is_deleted: false
    timestamp {
      ctime: 1000000001000000
      dtime: -1
      mtime: 1000000001000000
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
      ctime: 38000000
      dtime: -1
      mtime: 1000000001000000
    }
    uid: 2
  }
  folders {
    common {
      is_deleted: false
      timestamp {
        ctime: 38000000
        dtime: -1
        mtime: 1000000001000000
      }
      metadata {
        name: "folder9"
      }
      uid: -109
    }
    projects {
      common {
        is_deleted: false
        timestamp {
          ctime: 38000000
          dtime: -1
          mtime: 39000000
        }
        metadata {
          name: "prj9"
        }
        uid: -110
      }
      is_complete: false
      is_active: true
    }
  }
  projects {
    common {
      is_deleted: false
      timestamp {
        ctime: 1000000000000
        dtime: -1
        mtime: 1000000001000000
      }
      metadata {
        name: "P1"
      }
      uid: -6
    }
    is_complete: false
    is_active: false
    actions {
      common {
        is_deleted: false
        timestamp {
          ctime: 39000000
          dtime: -1
          mtime: 39000000
        }
        metadata {
          name: "action_in_prj9"
        }
        uid: -111
      }
      is_complete: false
    }
  }
}
"""
   }))

text_formatted_protobuf_dicts.append(
  ('moves an action -111 from one prj -6 into another prj -7 that is a sibling',
   {
     'database': """
inbox {
  common {
    is_deleted: false
    timestamp {
      ctime: 1000000001000000
      dtime: -1
      mtime: 1000000001000000
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
      ctime: 38000000
      dtime: -1
      mtime: 1000000001000000
    }
    uid: 2
  }
  projects {
    common {
      is_deleted: false
      timestamp {
        ctime: 1000000000000
        dtime: -1
        mtime: 1000000001000000
      }
      metadata {
        name: "P-6"
      }
      uid: -6
    }
    is_complete: false
    is_active: true
    actions {
      common {
        is_deleted: false
        timestamp {
          ctime: 39000000
          dtime: -1
          mtime: 39000000
        }
        metadata {
          name: "action_in_prj9"
        }
        uid: -111
      }
      is_complete: false
    }
  }
  projects {
    common {
      is_deleted: false
      timestamp {
        ctime: 1000000000000
        dtime: -1
        mtime: 1000000001000000
      }
      metadata {
        name: "P-7"
      }
      uid: -7
    }
    is_complete: false
    is_active: true
  }
}
""",
     'remote': """
inbox {
  common {
    is_deleted: false
    timestamp {
      ctime: 1000000001000000
      dtime: -1
      mtime: 1000000001000000
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
      ctime: 38000000
      dtime: -1
      mtime: 1000000001000000
    }
    uid: 2
  }
  projects {
    common {
      is_deleted: false
      timestamp {
        ctime: 1000000000000
        dtime: -1
        mtime: 1000000001000000
      }
      metadata {
        name: "P-6"
      }
      uid: -6
    }
    is_complete: false
    is_active: true
  }
  projects {
    common {
      is_deleted: false
      timestamp {
        ctime: 1000000000000
        dtime: -1
        mtime: 1000000001000000
      }
      metadata {
        name: "P-7"
      }
      uid: -7
    }
    is_complete: false
    is_active: true
    actions {
      common {
        is_deleted: false
        timestamp {
          ctime: 39000000
          dtime: -1
          mtime: 39000000
        }
        metadata {
          name: "action_in_prj9"
        }
        uid: -111
      }
      is_complete: false
    }
  }
}
"""
   }))

text_formatted_protobuf_dicts.append(
  ('completes an action on the web and finds it completed on the device',
   {
     'correct_winner': 'database',
     'database': """
inbox {
  common {
    is_deleted: false
    timestamp {
      ctime: 1000000001000000
      dtime: -1
      mtime: 1000000001000000
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
      ctime: 38000000
      dtime: -1
      mtime: 1000000001000000
    }
    uid: 2
  }
  projects {
    common {
      is_deleted: false
      timestamp {
        ctime: 1000000000000
        dtime: -1
        mtime: 1000000001000000
      }
      metadata {
        name: "P1"
      }
      uid: -6
    }
    is_complete: false
    is_active: false
    actions {
      common {
        is_deleted: false
        timestamp {
          ctime: 39000000
          dtime: -1
          mtime: 39500000
        }
        metadata {
          name: "action_in_prj9"
        }
        uid: -111
      }
      is_complete: true
    }
  }
}
""",
     'remote': """
inbox {
  common {
    is_deleted: false
    timestamp {
      ctime: 1000000001000000
      dtime: -1
      mtime: 1000000001000000
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
      ctime: 38000000
      dtime: -1
      mtime: 1000000001000000
    }
    uid: 2
  }
  projects {
    common {
      is_deleted: false
      timestamp {
        ctime: 1000000000000
        dtime: -1
        mtime: 1000000001000000
      }
      metadata {
        name: "P1"
      }
      uid: -6
    }
    is_complete: false
    is_active: false
    actions {
      common {
        is_deleted: false
        timestamp {
          ctime: 39000000
          dtime: -1
          mtime: 39000000
        }
        metadata {
          name: "action_in_prj9"
        }
        uid: -111
      }
      is_complete: false
    }
  }
}
"""
   }))


def _pb2str(pb):
  return text_format.MessageToString(pb)


def _well_known_tdl() -> pyatdl_pb2.ToDoList:
  return text_format.Merge(text_formatted_protobuf_well_known, pyatdl_pb2.ToDoList())


def _ProtobufToTdl(proto: pyatdl_pb2.ToDoList) -> tdl.ToDoList:
  assert isinstance(proto, pyatdl_pb2.ToDoList)
  return tdl.ToDoList.DeserializedProtobuf(proto.SerializeToString())


def _FreshToDoListProto() -> pyatdl_pb2.ToDoList:
  """Returns a semantically empty, well-formed protobuf."""
  uid.ResetNotesOfExistingUIDs(raise_data_error_upon_next_uid=True, allow_duplication=True)
  return pyatdl_pb2.ToDoList.FromString(
    tdl.ToDoList().AsProto().SerializeToString())


class MergeprotobufsTestCase(unitjest.TestCase):
  def helpSetUp(self) -> None:
    random.seed(3737123)
    uid.ResetNotesOfExistingUIDs(raise_data_error_upon_next_uid=True, allow_duplication=True)

  def setUp(self) -> None:
    super().setUp()
    self.maxDiff = None
    self.saved_time = time.time
    time.time = lambda: 1000000001  # 2001-09-08 18:46:41 PST8PDT, which is 1000000001000000 in microseconds since the epoch
    self.helpSetUp()

  def tearDown(self) -> None:
    time.time = self.saved_time

  # TODO(chandler37): more test cases
  def testMergeNoneNone(self) -> None:
    with self.assertRaisesRegex(TypeError, "both of the arguments must be present"):
      mergeprotobufs.Merge(None, None)  # type: ignore

  def testMergeNoneSomething(self) -> None:
    something = pyatdl_pb2.ToDoList()
    with self.assertRaisesRegex(TypeError, "both of the arguments must be present"):
      mergeprotobufs.Merge(None, something)  # type: ignore
    with self.assertRaisesRegex(TypeError, "both of the arguments must be present"):
      mergeprotobufs.Merge(tdl.ToDoList(), None)  # type: ignore

  def testMerge0(self) -> None:
    todos_in_db, remote_pb = tdl.ToDoList(), pyatdl_pb2.ToDoList()
    self.assertProtosEqual(mergeprotobufs.Merge(todos_in_db, remote_pb), todos_in_db.AsProto())

  def testMerge1left(self) -> None:
    todos_in_db, remote_pb = tdl.ToDoList(), pyatdl_pb2.ToDoList()
    todos_in_db.inbox = prj.Prj(the_uid=uid.INBOX_UID, name="xyz")
    self.assertProtosEqual(mergeprotobufs.Merge(todos_in_db, remote_pb), todos_in_db.AsProto())

  def testMerge1Right(self) -> None:
    todos_in_db, remote_pb = tdl.ToDoList(), _FreshToDoListProto()
    p = prj.Prj(name="new name for what was once the inbox", the_uid=uid.INBOX_UID).AsProto()
    p.common.timestamp.ctime = year5454microsec
    p.common.timestamp.mtime = year5454microsec
    remote_pb.inbox.CopyFrom(p)
    self.assertProtoTextuallyEquals(
      mergeprotobufs.Merge(todos_in_db, remote_pb),
      text_formatted_protobuf_1)

  def testMerge1RightNewAction(self) -> None:
    todos_in_db, remote_pb = tdl.ToDoList(), _FreshToDoListProto()
    p = prj.Prj(name="old name (as dictated by ctime and mtime) for what was once the inbox", the_uid=uid.INBOX_UID)
    p.mtime = p.ctime = 9.0
    a = action.Action(name="buy light bulbs", note="60w", the_uid=5)
    p.items.append(a)
    remote_pb.inbox.CopyFrom(p.AsProto())
    self.assertProtoTextuallyEquals(mergeprotobufs.Merge(todos_in_db, remote_pb), """
inbox {
  common {
    is_deleted: false
    timestamp {
      ctime: 1000000001000000
      dtime: -1
      mtime: 1000000001000000
    }
    metadata {
      name: "inbox"
    }
    uid: 1
  }
  is_complete: false
  is_active: true
  actions {
    common {
      is_deleted: false
      timestamp {
        ctime: 1000000001000000
        dtime: -1
        mtime: 1000000001000000
      }
      metadata {
        name: "buy light bulbs"
        note: "60w"
      }
      uid: 5
    }
    is_complete: false
  }
}
root {
  common {
    is_deleted: false
    timestamp {
      ctime: 1000000001000000
      dtime: -1
      mtime: 1000000001000000
    }
    uid: 2
  }
}
""")

  def testMergeInboxNameChangedWithoutTimestampDifference(self) -> None:
    # TODO(chandler37): also, add an action to the inbox and make sure that it appears even though the metadata should
    # not change.
    prj1 = prj.Prj(the_uid=uid.INBOX_UID, name="my password is hunter2")
    uid.ResetNotesOfExistingUIDs()
    todos_in_db = tdl.ToDoList(
      inbox=prj.Prj.DeserializedProtobuf(prj1.AsProto().SerializeToString()))
    remote_pb = pyatdl_pb2.ToDoList()
    remote_pb.CopyFrom(todos_in_db.AsProto())
    remote_pb.inbox.common.metadata.name = "my password is *******"
    merged = pyatdl_pb2.ToDoList()
    merged.CopyFrom(todos_in_db.AsProto())
    merged.MergeFrom(remote_pb)
    self.assertProtosEqual(mergeprotobufs.Merge(todos_in_db, remote_pb), todos_in_db.AsProto())

  def testMergeInboxNameChangedWithTimestampDifferenceRight(self) -> None:
    def DatabaseToDoList() -> pyatdl_pb2.ToDoList:
      tdlpb = _FreshToDoListProto()
      tdlpb.inbox.CopyFrom(
        prj.Prj(the_uid=uid.INBOX_UID, name="my password is hunter2").AsProto())
      return tdlpb

    def RemoteToDoList() -> pyatdl_pb2.ToDoList:
      tdlpb = _FreshToDoListProto()
      tdlpb.CopyFrom(DatabaseToDoList())
      tdlpb.inbox.common.metadata.name = "my password is *******"
      tdlpb.inbox.common.timestamp.mtime += 1000
      return tdlpb

    remote = RemoteToDoList()
    self.assertProtosEqual(
      mergeprotobufs.Merge(
        _ProtobufToTdl(DatabaseToDoList()),
        remote),
      remote)

  def testMergeInboxNameChangedWithTimestampDifferenceLeft(self) -> None:
    todos_in_db = tdl.ToDoList(
      inbox=prj.Prj(the_uid=uid.INBOX_UID, name="my password is hunter2"))
    remote_pb = _FreshToDoListProto()
    remote_pb.CopyFrom(todos_in_db.AsProto())
    remote_pb.inbox.common.metadata.name = "my password is *******"
    remote_pb.inbox.common.timestamp.mtime -= 1000
    remote_pb.inbox.common.timestamp.ctime -= 1000
    self.assertProtosEqual(
      mergeprotobufs.Merge(
        todos_in_db,
        remote_pb),
      todos_in_db.AsProto())

  def testMergeNewPrj(self) -> None:
    self.assertTrue("TODO(chandler37): add this test")

  def testMergeMarkCompletedBothAnActionAndAProject(self) -> None:
    self.assertTrue("TODO(chandler37): add this test")

  def testMergeNewCtx(self) -> None:
    self.assertTrue("TODO(chandler37): add this test")

  def testMergeNewFolder(self) -> None:
    self.assertTrue("TODO(chandler37): add this test")

  def testMergeNewNoteOnAnItem(self) -> None:
    self.assertTrue("TODO(chandler37): add this test")

  def testMergeNewGlobalNote(self) -> None:
    self.assertTrue("TODO(chandler37): add this test")

  def testMergeNewActionInInbox(self) -> None:
    self.assertTrue("TODO(chandler37): add this test")

  def testMergeNewActionOutsideInbox(self) -> None:
    self.assertTrue("TODO(chandler37): add this test")

  def testMergeUIDCollision(self) -> None:
    """Let's say the smartphone app has added Action 123
    "buy soymilk" and the django app has added Project 123 "replace wifi
    router". Do we handle it with grace?

    TODO(chandler37): think hard about UX: current webapp displays
    UIDs in URLs; they can be shared. So changing one is very very
    bad. We should instead generate a random 64-bit number and use that.

    TODO(chandler37): add a test case for the very unlikely collision.
    """
    self.assertTrue("TODO(chandler37): add this test")

  def testMergeDeletions(self) -> None:
    """Deletions are trickier. The non-django app must preserve the
    object's UID (but it can optionally delete the metadata like "buy
    soymilk") and indicate that it was deleted so that we can delete the
    data.

    TODO(chandler37): let's be wise about truly deleting even the UID
    and is_deleted bit and their containing
    Action/Context/Project/Folder/Note/etc.
    """
    self.assertTrue("TODO(chandler37): add this test")

  def testMergeTrueDeletion(self) -> None:
    """Let us say that the non-django app sends us a new thing but also
    the complete (a.k.a. "true") deletion of an old thing. What do we
    do? We assume that the old thing is to be preserved, because if it
    were intended to be deleted then the item would remain, with much of
    its metadata gutted but the deletion noted and UID intact.

    TODO(chandler37): Add an API that truly deletes deleted items, to be
    used only when all devices are known to be in sync.
    """
    self.assertTrue("TODO(chandler37): add this test")

  def testFolderChanges(self) -> None:
    """A folder has a new prj inside, and a new folder inside. We grab all three changes.

    TODO(chandler37): test a subfolder that has updated metadata.
    """
    def RemoteToDoList(start: pyatdl_pb2.ToDoList) -> pyatdl_pb2.ToDoList:
      remote_pb = pyatdl_pb2.ToDoList()
      remote_pb.CopyFrom(start)
      remote_pb.ctx_list.contexts[0].common.timestamp.mtime = year5454microsec
      remote_pb.ctx_list.contexts[0].common.metadata.name = remote_pb.ctx_list.contexts[0].common.metadata.name.upper()
      remote_pb.note_list.notes[0].note = "this is the UPDATED note on the home page"
      new_note = remote_pb.note_list.notes.add()
      # TODO(chandler37): test deletion of a note, perhaps just setting the note to the empty string.
      new_note.name = "new note"
      new_note.note = "the corresponding new note"
      new_folder = remote_pb.root.folders.add()
      text_format.Merge("""
  common {
    is_deleted: false
    timestamp {
      ctime: 38000000
      dtime: -1
      mtime: 38000000
    }
    metadata {
      name: "newfolder"
    }
    uid: -6279119140261074202
  }
  projects {
    common {
      is_deleted: false
      timestamp {
        ctime: 38000000
        dtime: -1
        mtime: 39000000
      }
      metadata {
        name: "newprj"
      }
      uid: -15
    }
    is_complete: false
    is_active: true
    actions {
      common {
        is_deleted: false
        timestamp {
          ctime: 39000000
          dtime: -1
          mtime: 39000000
        }
        metadata {
          name: "action_in_newprj"
        }
        uid: -29
      }
      is_complete: false
    }
  }
""", new_folder)
      return remote_pb

    golden = """
inbox {
  common {
    is_deleted: false
    timestamp {
      ctime: 1000000001000000
      dtime: -1
      mtime: 1000000001000000
    }
    metadata {
      name: "inbox"
    }
    uid: 1
  }
  is_complete: false
  is_active: true
  actions {
    common {
      is_deleted: false
      timestamp {
        ctime: 1000000000001
        dtime: -1
        mtime: 1000000001000000
      }
      metadata {
        name: "buy light bulbs"
        note: "60w"
      }
      uid: -5
    }
    is_complete: false
  }
}
root {
  common {
    is_deleted: false
    timestamp {
      ctime: 1000000001000000
      dtime: -1
      mtime: 1000000001000000
    }
    uid: 2
  }
  folders {
    common {
      is_deleted: false
      timestamp {
        ctime: 38000000
        dtime: -1
        mtime: 38000000
      }
      metadata {
        name: "newfolder"
      }
      uid: -6279119140261074202
    }
    projects {
      common {
        is_deleted: false
        timestamp {
          ctime: 38000000
          dtime: -1
          mtime: 39000000
        }
        metadata {
          name: "newprj"
        }
        uid: -15
      }
      is_complete: false
      is_active: true
      actions {
        common {
          is_deleted: false
          timestamp {
            ctime: 39000000
            dtime: -1
            mtime: 39000000
          }
          metadata {
            name: "action_in_newprj"
          }
          uid: -29
        }
        is_complete: false
      }
    }
  }
  projects {
    common {
      is_deleted: false
      timestamp {
        ctime: 1000000000000
        dtime: -1
        mtime: 1000000001000000
      }
      metadata {
        name: "P1"
      }
      uid: -6
    }
    is_complete: false
    is_active: false
  }
}
ctx_list {
  contexts {
    common {
      is_deleted: false
      timestamp {
        ctime: 1558072527256254
        dtime: -1
        mtime: 109951162777000000
      }
      metadata {
        name: "@COMPUTER"
      }
      uid: -48
    }
    is_active: true
  }
}
note_list {
  notes {
    name: ":__home"
    note: "<<<<<<< DB\\\\nthis is the note on the home page\\\\n=======\\\\nthis is the UPDATED note on the home \
page\\\\n>>>>>>> device\\\\n"
  }
  notes {
    name: "new note"
    note: "the corresponding new note"
  }
}
"""
    # TODO(chandler37): test with a well known TDL with an existing folder under root.
    self.assertProtoTextuallyEquals(
      mergeprotobufs.Merge(
        _ProtobufToTdl(_well_known_tdl()),
        RemoteToDoList(_well_known_tdl())),
      golden)

  def testMultitudesOfScenarios(self) -> None:
    for xx, yy in [('database', 'remote'), ('remote', 'database')]:
      i_seen = set()
      for i, dd in text_formatted_protobuf_dicts:
        assert i not in i_seen
        i_seen.add(i)
        if dd.get('unidirectional', False) and xx != 'database':
          continue
        self.helpSetUp()
        todos_in_db_pb = text_format.Merge(dd[xx], pyatdl_pb2.ToDoList())
        todos_in_db = _ProtobufToTdl(todos_in_db_pb)
        self.helpSetUp()
        remote_pb = text_format.Merge(dd[yy], pyatdl_pb2.ToDoList())
        try:
          merged = mergeprotobufs.Merge(todos_in_db, remote_pb)
        except AssertionError as e:
          raise AssertionError(f"hint={(i, xx, yy)} for {e}") from e
        winner = dd.get('correct_winner', 'remote' if xx == 'database' else 'database')
        assert isinstance(winner, str)
        expected = text_format.Merge(dd[winner], pyatdl_pb2.ToDoList())
        if (i, xx, yy) != ('folder10 disappears in a way that it would not in a well-written app', 'remote', 'database'):
          self.assertProtosEqual(actual=merged, expected=expected, hint=(i, xx, yy))
          continue
        assert winner != ('database' if xx == 'database' else 'remote'), (xx, yy, i, dd)
        tt = pyatdl_pb2.ToDoList()
        text_format.Merge(r"""
        root {
          folders {
            common {
              is_deleted: false
              timestamp {
                ctime: 38000000
                dtime: -1
                mtime: 1000000001000000
              }
              metadata {
                name: "folder10"
              }
              uid: -209
            }
          }
        }
        """, tt)
        tt.MergeFrom(remote_pb)
        self.assertProtosEqual(actual=merged, expected=tt, hint=(i, xx, yy))

  def testChangeFolderOfProjectAlsoKnownAsMovingTheProject2(self) -> None:
    # TODO(chandler37): test moving to root, from root, from non-root to non-root, and also into a new folder

    def DatabaseToDoList(start: pyatdl_pb2.ToDoList) -> pyatdl_pb2.ToDoList:
      db_pb = pyatdl_pb2.ToDoList()
      db_pb.CopyFrom(start)
      text_format.Merge(_OLDPRJ, db_pb.root)
      return db_pb

    def RemoteToDoList(start: pyatdl_pb2.ToDoList) -> pyatdl_pb2.ToDoList:
      remote_pb = pyatdl_pb2.ToDoList()
      remote_pb.CopyFrom(start)
      new_folder = remote_pb.root.folders.add()
      text_format.Merge(_OLDPRJ_IN_NEW_FOLDER, new_folder)
      return remote_pb

    base_tdl = text_format.Merge(text_formatted_protobuf_well_known, pyatdl_pb2.ToDoList())
    todos_in_db = _ProtobufToTdl(DatabaseToDoList(base_tdl))
    remote_pb = RemoteToDoList(base_tdl)
    self.assertProtosEqual(
      mergeprotobufs.Merge(
        todos_in_db,
        remote_pb),
      remote_pb)


if __name__ == '__main__':
  unitjest.main()


r"""
// TODO(chandler37): start at text format of proto and change evertyhing you see -- ctime, mtime, ...

// TODO(chandler37): overriding completions, contexts folders notes actions projects

// TODO(chandler37): test Action for obliterated. for deleted. for completed.

// TODO(chandler37): More test cases follow:

//
// immaculater> ls
// --project-- uid=1 --incomplete-- ---active--- inbox
// immaculater> cd inbox
// immaculater> ls
// immaculater> touch "give the cat a bath"
// immaculater> ls
// --action--- uid=4940145534978221493 --incomplete-- 'give the cat a bath' --in-context-- '<none>'
// immaculater> touch "give the cat a bath"
// immaculater> ls
// --action--- uid=4940145534978221493 --incomplete-- 'give the cat a bath' --in-context-- '<none>'
// --action--- uid=-5492528092754581212 --incomplete-- 'give the cat a bath' --in-context-- '<none>'

// TEST that if we delete 4940145534978221493 on device0 and change it to 'give the dog a bath' on device1, then we end
// up with, UNDELETED, 'give the dog a bath', i.e.,
//
// immaculater> ls
// --action--- uid=4940145534978221493 --incomplete-- 'give the dog a bath' --in-context-- '<none>'
// --action--- uid=-5492528092754581212 --incomplete-- 'give the cat a bath' --in-context-- '<none>'
// TODO(chandler37):  also test the same thing with a note changing:
//      if, on device1 the note changes on 4940145534978221493 from NULL to 'must do
// this!' (or vice versa) but on device0 again 4940145534978221493 is deleted,
// then discard the deletion.
// also test the same thing with context changing:
//      if, on device1 the context changes (from NULL to something, or vice versa, or from @a to @b) but on device0 again
//      4940145534978221493 is deleted,
// then POLD (Principle of Least Disappearances) requires that we discard the deletion, but of course we keep the change to the context.

// before:
// immaculater> ls
// --action--- uid=4940145534978221493 --incomplete-- 'give the dog a bath' --in-context-- '<none>'
// --action--- uid=-5492528092754581212 --incomplete-- 'give the cat a bath' --in-context-- '<none>'
//
// after on device0:
// immaculater> ls
// <DELETED>--action--- uid=4940145534978221493 --incomplete-- 'give the dog a bath' --in-context-- '<none>'</DELETED>
// --action--- uid=-5492528092754581212 --incomplete-- 'give the cat a bath' --in-context-- '<none>'

// after on device1:
// immaculater> ls
// --action--- uid=4940145534978221493 --incomplete-- 'give the dog a bath' --in-context-- @home
// --action--- uid=-5492528092754581212 --incomplete-- 'give the cat a bath' --in-context-- '<none>'

// merged:
// immaculater> ls
// <DELETED>--action--- uid=4940145534978221493 --incomplete-- 'give the dog a bath' --in-context-- @home</DELETED>
// --action--- uid=-5492528092754581212 --incomplete-- 'give the cat a bath' --in-context-- '<none>'


// also test the same thing with context changing differently on both devices (TODO(chandler37):  w/ and w/o deletion too):
//      if, on device1 the context changes from NULL to @a but on device0 from NULL to @b, (TODO(chandler37): Note that this
//      is the same as a note or name change in conflict)
// then....
//
// before:
// immaculater> ls
// --action--- uid=4940145534978221493 --incomplete-- 'give the dog a bath' --in-context-- '<none>'
//
// on device0:
// immaculater> ls
// --action--- uid=4940145534978221493 --incomplete-- 'eat cucumber' --in-context-- '<none>'

// on device1:
// immaculater> ls
// --action--- uid=4940145534978221493 --incomplete-- 'buy a prius' --in-context-- '<none>'

// merged:
// immaculater> ls
// --action--- uid=4940145534978221493 --incomplete-- 'buy a prius' --in-context-- '<none>'
// --action--- uid=123                 --incomplete-- 'eat cucumber' --in-context-- '<none>'

// SAME AS ABOVE but with CONTEXT:
//
// before:
// immaculater> ls
// --action--- uid=4940145534978221493 --incomplete-- 'give the dog a bath' --in-context-- '<none>'
//
// on device0:
// immaculater> ls
// --action--- uid=4940145534978221493 --incomplete-- 'give the dog a bath' --in-context-- @home
//
// on device1:
// immaculater> ls
// --action--- uid=4940145534978221493 --incomplete-- 'give the dog a bath' --in-context-- @someday/maybe
//
// merged:
// immaculater> ls
// --action--- uid=4940145534978221493 --incomplete-- 'give the dog a bath' --in-context-- @someday/maybe
// --action--- uid=123                 --incomplete-- 'give the dog a bath' --in-context-- @home

// TODO(chandler37):  test case: a note is changed in such a way that it would produce a git conflict should the note be a file in a
git repository. what we do is to leave git conflict markers like so:
//
// immaculater> touch pontificate
// immaculater> note --noreplace pontificate "Note follows:\nNote from device0\nEnd note."
// immaculater> note pontificate
// Note follows:\nNote from device0\nEnd note.
// immaculater> save ~/tmp/device0.note
// immaculater> note --replace pontificate "Note follows:\nNote from device1\nEnd note."
// immaculater> note pontificate
// Note follows:\nNote from device1\nEnd note.
// immaculater> save ~/tmp/device1.note
// immaculater> ls
// --action--- uid=3367828127791869605 --incomplete-- pontificate --in-context-- '<none>'
//
// merged:
// immaculater> note pontificate
// Note follows:\n<<<<<<< FROM NETWORK\nNote from device1\n=======\nNote from device0\n>>>>>>> IN DATABASE\nEnd note.

// TODO(chandler37): a test case where the database is non-empty but semantically empty so that we make sure we can add every single
// thing in the ToDoList message (and Action et al.)

TODO(chandler37): test moving a prj from one subfolder to another subfolder (parametrized by a destination subfolder
that is {earlier, later} in the protobuf)

TODO(chandler37): test that we actually 'obliterate' and that a sync with the same remote again would not resurrect any
objects.
"""
