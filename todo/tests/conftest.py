import pytest


@pytest.fixture(scope="class")
def golden_pbs(request):
    request.cls.golden_pb_a = r"""
sha1_checksum: "4f1e05daf57904a5a133993e6f19890e36c746ed"
to_do_list {
  inbox {
    common {
      is_deleted: false
      timestamp {
        ctime: 37000037
        dtime: -1
        mtime: 37000037
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
        ctime: 37000037
        dtime: -1
        mtime: 37000037
      }
      uid: 2
    }
    projects {
      common {
        is_deleted: false
        timestamp {
          ctime: 37000037
          dtime: -1
          mtime: 37000037
        }
        metadata {
          name: "miscellaneous"
        }
        uid: 11
      }
      is_complete: false
      is_active: true
    }
    projects {
      common {
        is_deleted: false
        timestamp {
          ctime: 37000037
          dtime: -1
          mtime: 37000037
        }
        metadata {
          name: "learn how to use this to-do list"
        }
        uid: 12
      }
      is_complete: false
      is_active: true
      actions {
        common {
          is_deleted: false
          timestamp {
            ctime: 37000037
            dtime: -1
            mtime: 37000037
          }
          metadata {
            name: "Watch the video on the \"Help\" page -- find it on the top navigation bar"
          }
          uid: 13
        }
        is_complete: false
      }
      actions {
        common {
          is_deleted: false
          timestamp {
            ctime: 37000037
            dtime: -1
            mtime: 37000037
          }
          metadata {
            name: "Read the book \"Getting Things Done\" by David Allen"
          }
          uid: 14
        }
        is_complete: false
      }
      actions {
        common {
          is_deleted: false
          timestamp {
            ctime: 37000037
            dtime: -1
            mtime: 37000037
          }
          metadata {
            name: "After reading the book, try out a Weekly Review -- on the top navigation bar, find it underneath the \"Other\" drop-down"
          }
          uid: 15
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
          ctime: 37000037
          dtime: -1
          mtime: 37000037
        }
        metadata {
          name: "@computer"
        }
        uid: 4
      }
      is_active: true
    }
    contexts {
      common {
        is_deleted: false
        timestamp {
          ctime: 37000037
          dtime: -1
          mtime: 37000037
        }
        metadata {
          name: "@phone"
        }
        uid: 5
      }
      is_active: true
    }
    contexts {
      common {
        is_deleted: false
        timestamp {
          ctime: 37000037
          dtime: -1
          mtime: 37000037
        }
        metadata {
          name: "@home"
        }
        uid: 6
      }
      is_active: true
    }
    contexts {
      common {
        is_deleted: false
        timestamp {
          ctime: 37000037
          dtime: -1
          mtime: 37000037
        }
        metadata {
          name: "@work"
        }
        uid: 7
      }
      is_active: true
    }
    contexts {
      common {
        is_deleted: false
        timestamp {
          ctime: 37000037
          dtime: -1
          mtime: 37000037
        }
        metadata {
          name: "@the store"
        }
        uid: 8
      }
      is_active: true
    }
    contexts {
      common {
        is_deleted: false
        timestamp {
          ctime: 37000037
          dtime: -1
          mtime: 37000037
        }
        metadata {
          name: "@someday/maybe"
        }
        uid: 9
      }
      is_active: false
    }
    contexts {
      common {
        is_deleted: false
        timestamp {
          ctime: 37000037
          dtime: -1
          mtime: 37000037
        }
        metadata {
          name: "@waiting for"
        }
        uid: 10
      }
      is_active: false
    }
  }
}
starter_template: true
sanity_check: 18369614221190021342
""".lstrip()

    request.cls.golden_pb_b = r"""
sha1_checksum: "c40dea147c4373089fd00c37558afc2e9c7ce011"
to_do_list {
  inbox {
    common {
      is_deleted: false
      timestamp {
        ctime: 1500000000000000
        dtime: -1
        mtime: 1500000000000000
      }
      uid: 1
    }
    is_complete: false
    is_active: false
    actions {
      common {
        is_deleted: false
        timestamp {
          ctime: 1500000000000000
          dtime: -1
          mtime: 1500000000000000
        }
        metadata {
          name: "increase the tests\' branch coverage"
        }
        uid: -42
      }
      is_complete: false
    }
  }
  root {
    common {
      is_deleted: false
      timestamp {
        ctime: 1500000000000000
        dtime: -1
        mtime: 1500000000000000
      }
      uid: 2
    }
  }
}
sanity_check: 18369614221190021342
""".lstrip()
