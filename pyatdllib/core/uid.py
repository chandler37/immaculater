"""Provides a factory for unique identifiers (UIDs). We use small positive integers."""

import threading

MIN_UID = 1


class Factory(object):
  """Generator of new UIDs."""
  def __init__(self):
    self._previous_uid = MIN_UID - 1
    self._lock = threading.RLock()

  def NextUID(self):
    """Creates and returns a new unique identifier.

    If you deserialize in the future, you invalidate this UID.

    Returns:
      int
    """
    with self._lock:
      self._previous_uid += 1
      return self._previous_uid

  def NoteExistingUID(self, existing_uid):
    """During deserialization, call this with each UID you encounter.

    Args:
      existing_uid: int
    """
    with self._lock:
      self._previous_uid = max(existing_uid, self._previous_uid)


singleton_factory = Factory()  # pylint: disable=invalid-name
