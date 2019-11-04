"""Routines for serializing and deserializing a tdl.ToDoList."""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

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


class TooBigToSaveError(Error):
  """Failed to save to-do list because it is too large. You can delete
  completed actions (should still fit...) and then purge deleted
  actions. Or you can export to TaskPaper format and see if it or
  OmniFocus can deal with your extra-large to-do list.
  """


def Sha1Checksum(payload):
  """Returns the SHA1 checksum of the given byte sequence.

  Args:
    payload: bytes
  Returns:
    str
  """
  m = hashlib.sha1()
  m.update(payload)
  return m.hexdigest()


def _GetPayloadAfterVerifyingChecksum(file_contents, path, sha1_checksum_list=None):
  """Verifies the checksum of the payload; returns the payload.

  Args:
    file_contents: bytes  # serialized form of ChecksumAndData
    path: str  # save file location used only in error messages
    sha1_checksum_list: None|list to which we append the SHA1 checksum of the uncompressed pyatdl_pb2.ToDoList serialization
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
  if Sha1Checksum(pb.payload) != pb.sha1_checksum:
    raise DeserializationError(
      'Invalid save file %s: Checksum mismatch' % (path,))
  if pb.payload_is_zlib_compressed:
    uncompressed_payload = zlib.decompress(pb.payload)
    if sha1_checksum_list is not None:
      # TODO(chandler37): As a performance optimization, store this sha1_checksum inside ChecksumAndData in addition to
      # the current payload checksum. But for mergeprotobufs to be fastest, we'll need to also/instead store it outside
      # of todo_todolist.encrypted_contents2.
      sha1_checksum_list.append(Sha1Checksum(uncompressed_payload))
  else:
    uncompressed_payload = pb.payload
    if sha1_checksum_list is not None:
      sha1_checksum_list.append(pb.sha1_checksum)
  return uncompressed_payload


def SerializedWithChecksum(payload):
  """Returns a serialized ChecksumAndData wrapping the given byte sequence.

  Args:
    payload: bytes  # from pyatdl_pb2.ToDoList().SerializeToString()
  Returns:
    bytes  # from pyatdl_pb2.ChecksumAndData().SerializeToString()
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
  cksum = Sha1Checksum(payload)
  pb.sha1_checksum = cksum
  assert payload
  result = pb.SerializeToString()
  _TestDeserializationOfChecksumWithData(result, cksum)
  return result


def _TestDeserializationOfChecksumWithData(bytestring, cksum):
  """Makes sure we don't save to the database something so large we cannot read it back.

  Args:
    bytestring: str
    cksum: str
  Raises:
    TooBigToSaveError
    AssertionError (for checksum mismatch)
  """
  pb = pyatdl_pb2.ChecksumAndData.FromString(bytestring)
  assert len(cksum) > 0
  if cksum != pb.sha1_checksum:
    raise AssertionError(
        'this should never happen even if the to-do list is too big. '
        'cksum=%s and pb.sha1_checksum=%s'
        % (cksum, pb.sha1_checksum))
  if pb.payload_length != len(pb.payload):
    raise AssertionError(
        'this should never happen even if the to-do list is too big. '
        'pb.payload_length=%s and pb.payload actual length=%s'
        % (pb.payload_length, len(pb.payload)))
  real_sum = Sha1Checksum(pb.payload)  # TODO(chandler37): this is expensive, make it optional?
  if real_sum != cksum:
    raise AssertionError(
        'this should never happen even if the to-do list is too big. '
        'SHA1(pb.payload)=%s and pb.sha1_checksum=%s'
        % (real_sum, pb.sha1_checksum))
  uncompressed_payload = pb.payload
  if pb.payload_is_zlib_compressed:
    uncompressed_payload = zlib.decompress(pb.payload)
  try:
    pyatdl_pb2.ToDoList.FromString(uncompressed_payload)
  except message.DecodeError:
    raise TooBigToSaveError


def SerializeToDoList2(todolist, writer):
  """Saves a serialized copy of todolist to the named file.

  Args:
    todolist: tdl.ToDoList
    writer: object with write(self, bytes) method
  Returns:
    None
  """
  todolist.CheckIsWellFormed()
  writer.write(SerializedWithChecksum(todolist.AsProto().SerializeToString()))


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
  with open(tmp_path, 'wb') as tmp_file:
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


def DeserializeToDoList2(reader, tdl_factory, sha1_checksum_list=None):
  """Deserializes a to-do list from the given file.

  Args:
    reader: object with 'read(self)' method and 'name' attribute
    tdl_factory: None|callable function ()->tdl.ToDoList
    sha1_checksum_list: None|list to which we append the SHA1 checksum of the uncompressed pyatdl_pb2.ToDoList serialization
  Returns:
    None|tdl.ToDoList  # None only if tdl_factory is None and would have been used
  Raises:
    DeserializationError
  """
  uid.ResetNotesOfExistingUIDs()
  try:
    file_contents = reader.read()
    if not file_contents:
      if tdl_factory is None:
        return None
      todolist = tdl_factory()
    else:
      todolist = tdl.ToDoList.DeserializedProtobuf(
        _GetPayloadAfterVerifyingChecksum(file_contents, reader.name, sha1_checksum_list=sha1_checksum_list))
  except IOError as e:
    raise DeserializationError(
      'Cannot deserialize to-do list from %s. See the "reset_database" command '
      'regarding beginning anew. Error: %s'
      % (reader.name, repr(e)))
  except EOFError:
    if tdl_factory is None:
      return None
    todolist = tdl_factory()
  try:
    # TODO(chandler37): make this optional based on a FLAG for performance reasons.
    str(todolist)  # calls todolist.__unicode__
    str(todolist.AsProto())
    todolist.CheckIsWellFormed()
  except:  # noqa: E722
    print('Serialization error?  Reset by rerunning with the "reset_database" '
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
  uid.ResetNotesOfExistingUIDs()
  if not os.path.exists(path):
    todolist = tdl_factory()
  else:
    try:
      with open(path, 'rb') as save_file:
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
  except:  # noqa: E722
    print('Serialization error?  Reset by rerunning with the "reset_database" '
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
  with open(path, 'rb') as save_file:
    file_contents = save_file.read()
    payload = _GetPayloadAfterVerifyingChecksum(file_contents, path)
    return pyatdl_pb2.ToDoList.FromString(payload)  # pylint: disable=no-member
