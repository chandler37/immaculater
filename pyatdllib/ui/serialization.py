"""Routines for serializing and deserializing a tdl.ToDoList."""

import hashlib
import os
import zlib

import gflags as flags  # https://code.google.com/p/python-gflags/
from google.protobuf import message

from ..core import pyatdl_pb2
from ..core import tdl
from ..core import uid

FLAGS = flags.FLAGS

flags.DEFINE_integer(
  'pyatdl_zlib_compression_level',
  2,  # CPU usage matters more than how many packets go across the wire
      # when we serialize.
  'Regarding compression of the to-do list: If zero, zlib compression is'
  ' not used. If 1-9, that level of zlib compression is used. 1'
  ' decompresses quickly; 6 is zlib\'s default; 9 compresses most'
  ' thoroughly and most slowly.',
  lower_bound=0,
  upper_bound=9)


class Error(Exception):
  """Base class for this module's exceptions."""


class DeserializationError(Error):
  """Failed to load to-do list."""


def _Sha1Checksum(payload):
  """Returns the SHA1 checksum of the given byte sequence.

  Args:
    payload: bytes
  Returns:
    str
  """
  m = hashlib.sha1()
  m.update(payload)
  return m.hexdigest()


def _GetPayloadAfterVerifyingChecksum(file_contents, path):
  """Verifies the checksum of the payload; returns the payload.

  Args:
    file_contents: bytes  # serialized form of ChecksumAndData
    path: str  # save file location used only in error messages
  Returns:
    bytes
  Raises:
    DeserializationError
  """
  try:
    pb = pyatdl_pb2.ChecksumAndData.FromString(file_contents)  # pylint: disable=no-member
  except message.DecodeError:
    raise DeserializationError('Data corruption: Cannot load from %s' % path)
  if pb.payload_length < 1:
    raise DeserializationError(
      'Invalid save file %s: payload_length=%s' % (path, pb.payload_length))
  if pb.payload_length != len(pb.payload):
    raise DeserializationError(
      'Invalid save file %s: payload_length=%s but len(payload)=%s'
      % (path, pb.payload_length, len(pb.payload)))
  if _Sha1Checksum(pb.payload) != pb.sha1_checksum:
    raise DeserializationError(
      'Invalid save file %s: Checksum mismatch' % (path,))
  if pb.payload_is_zlib_compressed:
    return zlib.decompress(pb.payload)
  return pb.payload


def _SerializedWithChecksum(payload):
  """Returns a serialized ChecksumAndData wrapping the given byte sequence.

  Args:
    payload: bytes
  Returns:
    bytes
  """
  pb = pyatdl_pb2.ChecksumAndData()
  pb.payload_is_zlib_compressed = False
  assert 0 <= FLAGS.pyatdl_zlib_compression_level <= 9
  if FLAGS.pyatdl_zlib_compression_level:
    pb.payload_is_zlib_compressed = True
    payload = zlib.compress(
      payload, FLAGS.pyatdl_zlib_compression_level)
  pb.payload = payload
  pb.payload_length = len(payload)
  pb.sha1_checksum = _Sha1Checksum(payload)
  assert payload
  return pb.SerializeToString()  # pylint: disable=no-member


def SerializeToDoList2(todolist, writer):
  """Saves a serialized copy of todolist to the named file.

  Args:
    todolist: tdl.ToDoList
    writer: object with write(self, bytes) method
  Returns:
    None
  """
  todolist.CheckIsWellFormed()
  writer.write(_SerializedWithChecksum(todolist.AsProto().SerializeToString()))


def SerializeToDoList(todolist, path):
  """Saves a serialized copy of todolist to the named file.

  Args:
    todolist: tdl.ToDoList
    path: str
  Returns:
    None
  """
  tmp_path = path + '.tmp'
  dirname = os.path.dirname(tmp_path)
  if dirname and not os.path.exists(dirname):
    os.makedirs(os.path.dirname(tmp_path))
  with open(tmp_path, 'w') as tmp_file:
    SerializeToDoList2(todolist, tmp_file)
  try:
    os.remove(path + '.bak')
  except OSError:
    pass
  try:
    os.rename(path, path + '.bak')
  except OSError:
    pass
  try:
    os.remove(path)
  except OSError:
    pass
  os.rename(tmp_path, path)


def DeserializeToDoList2(reader, tdl_factory):
  """Deserializes a to-do list from the given file.

  Args:
    reader: object with 'read(self)' method and 'name' attribute
    tdl_factory: callable function ()->tdl.ToDoList
  Returns:
    tdl.ToDoList
  Raises:
    DeserializationError
  """
  uid.singleton_factory = uid.Factory()
  try:
    file_contents = reader.read()
    if not file_contents:
      todolist = tdl_factory()
    else:
      todolist = tdl.ToDoList.DeserializedProtobuf(
        _GetPayloadAfterVerifyingChecksum(file_contents, reader.name))
  except IOError as e:
    raise DeserializationError(
      'Cannot deserialize to-do list from %s. See the "reset_database" command '
      'regarding beginning anew. Error: %s'
      % (reader.name, repr(e)))
  except EOFError:
    todolist = tdl_factory()
  try:
    str(todolist)  # calls unicode(todolist)
    str(todolist.AsProto())
    todolist.CheckIsWellFormed()
  except:
    print ('Serialization error?  Reset by rerunning with the "reset_database" '
           'command.\nHere is the exception:\n')
    raise
  return todolist


def DeserializeToDoList(path, tdl_factory):
  """Deserializes a to-do list from the named file.

  Args:
    path: str
    tdl_factory: callable function ()->tdl.ToDoList
  Returns:
    tdl.ToDoList
  Raises:
    DeserializationError
  """
  uid.singleton_factory = uid.Factory()
  if not os.path.exists(path):
    todolist = tdl_factory()
  else:
    try:
      with open(path) as save_file:
        file_contents = save_file.read()
        if not file_contents:
          todolist = tdl_factory()
        else:
          todolist = tdl.ToDoList.DeserializedProtobuf(
            _GetPayloadAfterVerifyingChecksum(file_contents, path))
    except IOError as e:
      raise DeserializationError(
        'Cannot deserialize to-do list from %s. See the "reset_database" command '
        'regarding beginning anew. Error: %s'
        % (path, repr(e)))
    except EOFError:
      todolist = tdl_factory()
  try:
    str(todolist)
    str(todolist.AsProto())
    todolist.CheckIsWellFormed()
  except:
    print ('Serialization error?  Reset by rerunning with the "reset_database" '
           'command, i.e. deleting\n  %s\nHere is the exception:\n'
           % FLAGS.database_filename)
    raise
  return todolist


def GetRawProtobuf(path):
  """Partially deserializes the to-do list but stops as soon as a protobuf is
  available. Returns that protobuf.

  Returns:
    pyatdl_pb2.ToDoList
  Raises:
    Error
    IOError
  """
  with open(path) as save_file:
    file_contents = save_file.read()
    payload = _GetPayloadAfterVerifyingChecksum(file_contents, path)
    return pyatdl_pb2.ToDoList.FromString(payload)  # pylint: disable=no-member
