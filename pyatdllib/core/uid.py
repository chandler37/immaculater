"""Provides a factory for signed 64-bit unique identifiers (UIDs).

We use a pseudorandom number generator to generate UIDs. With 2**64 total
choices, you would expect to generate about 2**64**0.5 (4 billion) objects
before a collision occurs. We check for collisions anyway and keep generating
random numbers until we find one that's not yet used.

Historians: We used to use small positive integers like 1,2,3. Then we thought
about supporting multiple devices, some of them offline. The 'mergeprotobufs'
API to merge together two ToDoLists becomes ugly if it has to say 'I see a new
action 123 from one device and a new action 123 from another device -- what do
I do?' (We probably should generate a new UID in the very unlikely case of a
collision.)
"""

import random
import threading

import gflags as flags

from . import errors


FLAGS = flags.FLAGS

flags.DEFINE_bool('pyatdl_randomize_uids', True,
                  'Randomize the UIDs (unique identifiers) of objects (e.g., '
                  'Actions) in the protobuf? (This is only for easier testing. '
                  'The tests make more sense with UIDs 1,2,3,... than huge '
                  'signed random numbers.)')

# The inbox has unique identifier 1 because tests depend on it. Also it might
# be easier to write your app if you can rely on this.
INBOX_UID = 1
# Similarly with the root Folder:
ROOT_FOLDER_UID = INBOX_UID + 1
assert ROOT_FOLDER_UID == 2
# TODO(chandler37): Change pyatdl.proto so that ContextList has no 'common' field.

# pyatdl.proto can say 'int64 uid = 1 [default = 37]' but it is zero by default:
DEFAULT_PROTOBUF_VALUE_FOR_ABSENT_UID = 0

# _JsonForOneItem uses zero to represent the NULL UID:
UICMD_JSON_UID_VALUE_REPRESENTING_NONE = 0


class Factory(object):
  """Generator of new UIDs."""
  def __init__(self):
    self._uids = set()
    self._lock = threading.RLock()

  def NextUID(self):
    """Creates and returns a new unique identifier.

    If you deserialize in the future, you invalidate this UID.

    Returns:
      int
    """
    with self._lock:
      if FLAGS.pyatdl_randomize_uids:
        reserved = (
          INBOX_UID,
          ROOT_FOLDER_UID,
          DEFAULT_PROTOBUF_VALUE_FOR_ABSENT_UID,
          UICMD_JSON_UID_VALUE_REPRESENTING_NONE)
        while True:
          # The following is (inclusive, exclusive):
          n = random.randrange(-2**63, 2**63)
          if n not in reserved and n not in self._uids:
            self._uids.add(n)
            return n

      # Else: Emulate legacy behavior for easy testing.
      if self._uids:
        n = max(self._uids) + 1
      else:
        n = INBOX_UID
      # TODO(chandler37): https://github.com/grantjenks/python-sortedcontainers
      # might be faster than doing this O(N) operation each time. But if it's
      # only for tests then we don't care, so let's switch the classic django
      # webapp to randomization.
      if n >= 2**63:
        raise errors.DataError("We ran out of UIDs at value 2**63")
      assert n not in self._uids, f'{n} is in self._uids'
      self._uids.add(n)
      return n

  def NoteExistingUID(self, existing_uid):
    """During deserialization, call this with each UID you encounter.

    Args:
      existing_uid: int
    """
    with self._lock:
      if existing_uid == DEFAULT_PROTOBUF_VALUE_FOR_ABSENT_UID:
        raise errors.DataError("A UID is missing from or explicitly zero in the protocol buffer!")
      if existing_uid in self._uids:
        raise errors.DataError("A UID %s is duplicated!" % existing_uid)
      self._uids.add(existing_uid)


class FactoryThatRaisesDataErrorUponNextUID(Factory):
  def NextUID(self):
    raise errors.DataError("A UID is missing!")


def ResetNotesOfExistingUIDs(raise_data_error_upon_next_uid=False):
  global singleton_factory
  singleton_factory = FactoryThatRaisesDataErrorUponNextUID() if raise_data_error_upon_next_uid else Factory()


ResetNotesOfExistingUIDs()
