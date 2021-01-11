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

from absl import flags  # type: ignore
from typing import Set

from . import errors


FLAGS = flags.FLAGS

flags.DEFINE_bool('pyatdl_randomize_uids', False,
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

# pyatdl.proto can say 'int64 uid = 1 [default = 37]' but it is zero by default:
DEFAULT_PROTOBUF_VALUE_FOR_ABSENT_UID = 0

# _JsonForOneItem uses zero to represent the NULL UID:
UICMD_JSON_UID_VALUE_REPRESENTING_NONE = 0


class Factory(object):
  """Generator of new UIDs."""
  def __init__(self) -> None:
    self._uids: Set[int] = set()
    self._lock = threading.RLock()

  def NextUID(self, discarding: bool = False) -> int:
    """Creates and returns a new unique identifier.

    If FLAGS.pyatdl_randomize_uids is falsy and you deserialize in the future, you invalidate this UID.
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
      if n >= 2**63:
        raise errors.DataError("We ran out of UIDs at value 2**63")
      assert n not in self._uids, f'{n} is in self._uids'
      self._uids.add(n)
      return n

  def NoteExistingUID(self, existing_uid: int) -> None:
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
  def NextUID(self, discarding: bool = False) -> int:
    if not discarding:
      raise errors.DataError("A UID is missing!")
    return -42


class FactoryThatRaisesDataErrorUponNextUIDAndAllowsDuplication(FactoryThatRaisesDataErrorUponNextUID):
  def NoteExistingUID(self, existing_uid) -> None:
    pass


singleton_factory: Factory = FactoryThatRaisesDataErrorUponNextUID()


def ResetNotesOfExistingUIDs(raise_data_error_upon_next_uid: bool = False, allow_duplication: bool = False) -> None:
  global singleton_factory
  if raise_data_error_upon_next_uid:
    if allow_duplication:
      singleton_factory = FactoryThatRaisesDataErrorUponNextUIDAndAllowsDuplication()
    else:
      singleton_factory = FactoryThatRaisesDataErrorUponNextUID()
  else:
    singleton_factory = Factory()


ResetNotesOfExistingUIDs()
