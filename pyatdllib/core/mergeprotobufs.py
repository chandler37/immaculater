"""Logic for merging together two ToDoList protobufs that share a common ancestor.

If you update your ToDoList on a smartphone and simultaneously update it
through the Django classic webapp, this will unite those changes into a single
result.
"""


from . import pyatdl_pb2
from . import tdl


def Merge(db: tdl.ToDoList, remote: pyatdl_pb2.ToDoList) -> pyatdl_pb2.ToDoList:
  """Merges two pyatdl.ToDoList protobufs, one from our database and one from another device or application.

  db and remote have different types, but only trivially so. The question then is whether it matters which one is
  which. The answer is yes. db must be the one from django's database and remote must be the one from the other
  device/app. The reason is because we do not trust other devices/apps to preserve unknown fields in the protobuf (the
  official Google javascript implementation, for example, fails in this regard). If we add a new field, there will be a
  window where the django app fills it in but other devices read it, drop it on the floor, and return to us a protobuf
  without the new field. (We assume that you add new fields to this django app first.) [TODO(chandler37): The `uid`
  module (`from . import uid`) has a singleton, too, `singleton_factory`, so manipulating two TDLs at once might be
  tricky.]

  We merge global notes (i.e., those in the NoteList), contexts, projects, folders, actions, and their notes. Deletion
  is accomplished by leaving a context, project, folder, or action in place with UID intact and common.is_deleted set
  to True. If you try to delete an action by removing the pyatdl.Action message, it will be resurrected.

  pyatdl.Timestamp values are used to determine the winner of a modification of an item. We don't want to rely upon the
  various applications' clocks to be in sync in a perfect world, but that's what you've got for now. (A paranoid
  application might wish to take into account time on the server.)

  Args:
    db: tdl.ToDoList | None
    remote: pyatdl_pb2.ToDoList | None
  Returns:
    pyatdl_pb2.ToDoList
  Raises:
    TypeError: one or both args is None

  """
  if db is None or remote is None:
    raise TypeError('both of the arguments must be present')
  if not isinstance(db, tdl.ToDoList):
    raise TypeError('db must be tdl.ToDoList')
  if not isinstance(remote, pyatdl_pb2.ToDoList):
    raise TypeError('arguments must be None|pyatdl_pb2.ToDoList')
  if remote.HasField('inbox'):
    db.MergeInbox(remote.inbox)
  if remote.HasField('root'):
    db.MergeRoot(remote.root)
  if remote.HasField('ctx_list'):
    db.MergeCtxList(remote.ctx_list)
  if remote.HasField('note_list'):
    db.MergeNoteList(remote.note_list)
  return db.AsProto()
