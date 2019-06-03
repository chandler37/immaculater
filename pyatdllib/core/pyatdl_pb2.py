# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: core/pyatdl.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='core/pyatdl.proto',
  package='pyatdl',
  syntax='proto2',
  serialized_options=None,
  serialized_pb=_b('\n\x11\x63ore/pyatdl.proto\x12\x06pyatdl\"\x7f\n\x0cVisitorInfo0\x12\x14\n\x0csanity_check\x18\x01 \x01(\x05\x12\x13\n\x07\x63wc_uid\x18\x07 \x01(\x03\x42\x02\x30\x01\x12\x0c\n\x04view\x18\x03 \x01(\t\x12\x13\n\x04sort\x18\x05 \x01(\t:\x05\x61lpha\x12\x15\n\rusername_hash\x18\x06 \x01(\x0c*\n\x08\xa0\x9c\x01\x10\x80\x80\x80\x80\x02\"\x86\x01\n\x0f\x43hecksumAndData\x12\x1a\n\x0epayload_length\x18\x01 \x02(\x03\x42\x02\x30\x01\x12\x15\n\rsha1_checksum\x18\x02 \x01(\t\x12\"\n\x1apayload_is_zlib_compressed\x18\x03 \x01(\x08\x12\x10\n\x07payload\x18\x8bO \x02(\x0c*\n\x08\xa0\x9c\x01\x10\x80\x80\x80\x80\x02\"D\n\tTimestamp\x12\x11\n\x05\x63time\x18\x01 \x01(\x03\x42\x02\x30\x01\x12\x11\n\x05\x64time\x18\x02 \x01(\x03\x42\x02\x30\x01\x12\x11\n\x05mtime\x18\x03 \x01(\x03\x42\x02\x30\x01\"2\n\x08Metadata\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x0c\n\x04note\x18\x02 \x01(\t*\n\x08\xa0\x9c\x01\x10\x80\x80\x80\x80\x02\"\x83\x01\n\x06\x43ommon\x12\x0f\n\x03uid\x18\x04 \x01(\x03\x42\x02\x30\x01\x12\x12\n\nis_deleted\x18\x01 \x01(\x08\x12$\n\ttimestamp\x18\x02 \x01(\x0b\x32\x11.pyatdl.Timestamp\x12\"\n\x08metadata\x18\x03 \x01(\x0b\x32\x10.pyatdl.Metadata*\n\x08\xa0\x9c\x01\x10\x80\x80\x80\x80\x02\"H\n\x07\x43ontext\x12\x1e\n\x06\x63ommon\x18\x01 \x01(\x0b\x32\x0e.pyatdl.Common\x12\x11\n\tis_active\x18\x02 \x01(\x08*\n\x08\xa0\x9c\x01\x10\x80\x80\x80\x80\x02\"g\n\x06\x41\x63tion\x12\x1e\n\x06\x63ommon\x18\x01 \x01(\x0b\x32\x0e.pyatdl.Common\x12\x13\n\x0bis_complete\x18\x03 \x01(\x08\x12\x1c\n\x03\x63tx\x18\x04 \x01(\x0b\x32\x0f.pyatdl.Context*\n\x08\xa0\x9c\x01\x10\x80\x80\x80\x80\x02\"\xe8\x01\n\x07Project\x12\x1e\n\x06\x63ommon\x18\x01 \x01(\x0b\x32\x0e.pyatdl.Common\x12\x13\n\x0bis_complete\x18\x02 \x01(\x08\x12\x11\n\tis_active\x18\x03 \x01(\x08\x12\x1f\n\x07\x61\x63tions\x18\x04 \x03(\x0b\x32\x0e.pyatdl.Action\x12!\n\x19max_seconds_before_review\x18\x05 \x01(\x02\x12!\n\x19last_review_epoch_seconds\x18\x06 \x01(\x02\x12\"\n\x13\x64\x65\x66\x61ult_context_uid\x18\x07 \x01(\x03:\x01\x30\x42\x02\x30\x01*\n\x08\xa0\x9c\x01\x10\x80\x80\x80\x80\x02\".\n\x04Note\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x0c\n\x04note\x18\x02 \x01(\t*\n\x08\xa0\x9c\x01\x10\x80\x80\x80\x80\x02\"3\n\x08NoteList\x12\x1b\n\x05notes\x18\x02 \x03(\x0b\x32\x0c.pyatdl.Note*\n\x08\xa0\x9c\x01\x10\x80\x80\x80\x80\x02\"\\\n\x0b\x43ontextList\x12\x1e\n\x06\x63ommon\x18\x01 \x01(\x0b\x32\x0e.pyatdl.Common\x12!\n\x08\x63ontexts\x18\x02 \x03(\x0b\x32\x0f.pyatdl.Context*\n\x08\xa0\x9c\x01\x10\x80\x80\x80\x80\x02\"x\n\x06\x46older\x12\x1e\n\x06\x63ommon\x18\x01 \x01(\x0b\x32\x0e.pyatdl.Common\x12\x1f\n\x07\x66olders\x18\x02 \x03(\x0b\x32\x0e.pyatdl.Folder\x12!\n\x08projects\x18\x03 \x03(\x0b\x32\x0f.pyatdl.Project*\n\x08\xa0\x9c\x01\x10\x80\x80\x80\x80\x02\"\xa6\x01\n\x08ToDoList\x12\x1e\n\x05inbox\x18\x01 \x01(\x0b\x32\x0f.pyatdl.Project\x12\x1c\n\x04root\x18\x02 \x01(\x0b\x32\x0e.pyatdl.Folder\x12%\n\x08\x63tx_list\x18\x03 \x01(\x0b\x32\x13.pyatdl.ContextList\x12#\n\tnote_list\x18\x05 \x01(\x0b\x32\x10.pyatdl.NoteList*\n\x08\xa0\x9c\x01\x10\x80\x80\x80\x80\x02J\x04\x08\x04\x10\x05')
)




_VISITORINFO0 = _descriptor.Descriptor(
  name='VisitorInfo0',
  full_name='pyatdl.VisitorInfo0',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='sanity_check', full_name='pyatdl.VisitorInfo0.sanity_check', index=0,
      number=1, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='cwc_uid', full_name='pyatdl.VisitorInfo0.cwc_uid', index=1,
      number=7, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=_b('0\001'), file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='view', full_name='pyatdl.VisitorInfo0.view', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='sort', full_name='pyatdl.VisitorInfo0.sort', index=3,
      number=5, type=9, cpp_type=9, label=1,
      has_default_value=True, default_value=_b("alpha").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='username_hash', full_name='pyatdl.VisitorInfo0.username_hash', index=4,
      number=6, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=True,
  syntax='proto2',
  extension_ranges=[(20000, 536870912), ],
  oneofs=[
  ],
  serialized_start=29,
  serialized_end=156,
)


_CHECKSUMANDDATA = _descriptor.Descriptor(
  name='ChecksumAndData',
  full_name='pyatdl.ChecksumAndData',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='payload_length', full_name='pyatdl.ChecksumAndData.payload_length', index=0,
      number=1, type=3, cpp_type=2, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=_b('0\001'), file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='sha1_checksum', full_name='pyatdl.ChecksumAndData.sha1_checksum', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='payload_is_zlib_compressed', full_name='pyatdl.ChecksumAndData.payload_is_zlib_compressed', index=2,
      number=3, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='payload', full_name='pyatdl.ChecksumAndData.payload', index=3,
      number=10123, type=12, cpp_type=9, label=2,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=True,
  syntax='proto2',
  extension_ranges=[(20000, 536870912), ],
  oneofs=[
  ],
  serialized_start=159,
  serialized_end=293,
)


_TIMESTAMP = _descriptor.Descriptor(
  name='Timestamp',
  full_name='pyatdl.Timestamp',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='ctime', full_name='pyatdl.Timestamp.ctime', index=0,
      number=1, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=_b('0\001'), file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='dtime', full_name='pyatdl.Timestamp.dtime', index=1,
      number=2, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=_b('0\001'), file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='mtime', full_name='pyatdl.Timestamp.mtime', index=2,
      number=3, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=_b('0\001'), file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=295,
  serialized_end=363,
)


_METADATA = _descriptor.Descriptor(
  name='Metadata',
  full_name='pyatdl.Metadata',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='name', full_name='pyatdl.Metadata.name', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='note', full_name='pyatdl.Metadata.note', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=True,
  syntax='proto2',
  extension_ranges=[(20000, 536870912), ],
  oneofs=[
  ],
  serialized_start=365,
  serialized_end=415,
)


_COMMON = _descriptor.Descriptor(
  name='Common',
  full_name='pyatdl.Common',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='uid', full_name='pyatdl.Common.uid', index=0,
      number=4, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=_b('0\001'), file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='is_deleted', full_name='pyatdl.Common.is_deleted', index=1,
      number=1, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='timestamp', full_name='pyatdl.Common.timestamp', index=2,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='metadata', full_name='pyatdl.Common.metadata', index=3,
      number=3, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=True,
  syntax='proto2',
  extension_ranges=[(20000, 536870912), ],
  oneofs=[
  ],
  serialized_start=418,
  serialized_end=549,
)


_CONTEXT = _descriptor.Descriptor(
  name='Context',
  full_name='pyatdl.Context',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='common', full_name='pyatdl.Context.common', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='is_active', full_name='pyatdl.Context.is_active', index=1,
      number=2, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=True,
  syntax='proto2',
  extension_ranges=[(20000, 536870912), ],
  oneofs=[
  ],
  serialized_start=551,
  serialized_end=623,
)


_ACTION = _descriptor.Descriptor(
  name='Action',
  full_name='pyatdl.Action',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='common', full_name='pyatdl.Action.common', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='is_complete', full_name='pyatdl.Action.is_complete', index=1,
      number=3, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='ctx', full_name='pyatdl.Action.ctx', index=2,
      number=4, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=True,
  syntax='proto2',
  extension_ranges=[(20000, 536870912), ],
  oneofs=[
  ],
  serialized_start=625,
  serialized_end=728,
)


_PROJECT = _descriptor.Descriptor(
  name='Project',
  full_name='pyatdl.Project',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='common', full_name='pyatdl.Project.common', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='is_complete', full_name='pyatdl.Project.is_complete', index=1,
      number=2, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='is_active', full_name='pyatdl.Project.is_active', index=2,
      number=3, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='actions', full_name='pyatdl.Project.actions', index=3,
      number=4, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='max_seconds_before_review', full_name='pyatdl.Project.max_seconds_before_review', index=4,
      number=5, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='last_review_epoch_seconds', full_name='pyatdl.Project.last_review_epoch_seconds', index=5,
      number=6, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='default_context_uid', full_name='pyatdl.Project.default_context_uid', index=6,
      number=7, type=3, cpp_type=2, label=1,
      has_default_value=True, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=_b('0\001'), file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=True,
  syntax='proto2',
  extension_ranges=[(20000, 536870912), ],
  oneofs=[
  ],
  serialized_start=731,
  serialized_end=963,
)


_NOTE = _descriptor.Descriptor(
  name='Note',
  full_name='pyatdl.Note',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='name', full_name='pyatdl.Note.name', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='note', full_name='pyatdl.Note.note', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=True,
  syntax='proto2',
  extension_ranges=[(20000, 536870912), ],
  oneofs=[
  ],
  serialized_start=965,
  serialized_end=1011,
)


_NOTELIST = _descriptor.Descriptor(
  name='NoteList',
  full_name='pyatdl.NoteList',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='notes', full_name='pyatdl.NoteList.notes', index=0,
      number=2, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=True,
  syntax='proto2',
  extension_ranges=[(20000, 536870912), ],
  oneofs=[
  ],
  serialized_start=1013,
  serialized_end=1064,
)


_CONTEXTLIST = _descriptor.Descriptor(
  name='ContextList',
  full_name='pyatdl.ContextList',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='common', full_name='pyatdl.ContextList.common', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='contexts', full_name='pyatdl.ContextList.contexts', index=1,
      number=2, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=True,
  syntax='proto2',
  extension_ranges=[(20000, 536870912), ],
  oneofs=[
  ],
  serialized_start=1066,
  serialized_end=1158,
)


_FOLDER = _descriptor.Descriptor(
  name='Folder',
  full_name='pyatdl.Folder',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='common', full_name='pyatdl.Folder.common', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='folders', full_name='pyatdl.Folder.folders', index=1,
      number=2, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='projects', full_name='pyatdl.Folder.projects', index=2,
      number=3, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=True,
  syntax='proto2',
  extension_ranges=[(20000, 536870912), ],
  oneofs=[
  ],
  serialized_start=1160,
  serialized_end=1280,
)


_TODOLIST = _descriptor.Descriptor(
  name='ToDoList',
  full_name='pyatdl.ToDoList',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='inbox', full_name='pyatdl.ToDoList.inbox', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='root', full_name='pyatdl.ToDoList.root', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='ctx_list', full_name='pyatdl.ToDoList.ctx_list', index=2,
      number=3, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='note_list', full_name='pyatdl.ToDoList.note_list', index=3,
      number=5, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=True,
  syntax='proto2',
  extension_ranges=[(20000, 536870912), ],
  oneofs=[
  ],
  serialized_start=1283,
  serialized_end=1449,
)

_COMMON.fields_by_name['timestamp'].message_type = _TIMESTAMP
_COMMON.fields_by_name['metadata'].message_type = _METADATA
_CONTEXT.fields_by_name['common'].message_type = _COMMON
_ACTION.fields_by_name['common'].message_type = _COMMON
_ACTION.fields_by_name['ctx'].message_type = _CONTEXT
_PROJECT.fields_by_name['common'].message_type = _COMMON
_PROJECT.fields_by_name['actions'].message_type = _ACTION
_NOTELIST.fields_by_name['notes'].message_type = _NOTE
_CONTEXTLIST.fields_by_name['common'].message_type = _COMMON
_CONTEXTLIST.fields_by_name['contexts'].message_type = _CONTEXT
_FOLDER.fields_by_name['common'].message_type = _COMMON
_FOLDER.fields_by_name['folders'].message_type = _FOLDER
_FOLDER.fields_by_name['projects'].message_type = _PROJECT
_TODOLIST.fields_by_name['inbox'].message_type = _PROJECT
_TODOLIST.fields_by_name['root'].message_type = _FOLDER
_TODOLIST.fields_by_name['ctx_list'].message_type = _CONTEXTLIST
_TODOLIST.fields_by_name['note_list'].message_type = _NOTELIST
DESCRIPTOR.message_types_by_name['VisitorInfo0'] = _VISITORINFO0
DESCRIPTOR.message_types_by_name['ChecksumAndData'] = _CHECKSUMANDDATA
DESCRIPTOR.message_types_by_name['Timestamp'] = _TIMESTAMP
DESCRIPTOR.message_types_by_name['Metadata'] = _METADATA
DESCRIPTOR.message_types_by_name['Common'] = _COMMON
DESCRIPTOR.message_types_by_name['Context'] = _CONTEXT
DESCRIPTOR.message_types_by_name['Action'] = _ACTION
DESCRIPTOR.message_types_by_name['Project'] = _PROJECT
DESCRIPTOR.message_types_by_name['Note'] = _NOTE
DESCRIPTOR.message_types_by_name['NoteList'] = _NOTELIST
DESCRIPTOR.message_types_by_name['ContextList'] = _CONTEXTLIST
DESCRIPTOR.message_types_by_name['Folder'] = _FOLDER
DESCRIPTOR.message_types_by_name['ToDoList'] = _TODOLIST
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

VisitorInfo0 = _reflection.GeneratedProtocolMessageType('VisitorInfo0', (_message.Message,), {
  'DESCRIPTOR' : _VISITORINFO0,
  '__module__' : 'core.pyatdl_pb2'
  # @@protoc_insertion_point(class_scope:pyatdl.VisitorInfo0)
  })
_sym_db.RegisterMessage(VisitorInfo0)

ChecksumAndData = _reflection.GeneratedProtocolMessageType('ChecksumAndData', (_message.Message,), {
  'DESCRIPTOR' : _CHECKSUMANDDATA,
  '__module__' : 'core.pyatdl_pb2'
  # @@protoc_insertion_point(class_scope:pyatdl.ChecksumAndData)
  })
_sym_db.RegisterMessage(ChecksumAndData)

Timestamp = _reflection.GeneratedProtocolMessageType('Timestamp', (_message.Message,), {
  'DESCRIPTOR' : _TIMESTAMP,
  '__module__' : 'core.pyatdl_pb2'
  # @@protoc_insertion_point(class_scope:pyatdl.Timestamp)
  })
_sym_db.RegisterMessage(Timestamp)

Metadata = _reflection.GeneratedProtocolMessageType('Metadata', (_message.Message,), {
  'DESCRIPTOR' : _METADATA,
  '__module__' : 'core.pyatdl_pb2'
  # @@protoc_insertion_point(class_scope:pyatdl.Metadata)
  })
_sym_db.RegisterMessage(Metadata)

Common = _reflection.GeneratedProtocolMessageType('Common', (_message.Message,), {
  'DESCRIPTOR' : _COMMON,
  '__module__' : 'core.pyatdl_pb2'
  # @@protoc_insertion_point(class_scope:pyatdl.Common)
  })
_sym_db.RegisterMessage(Common)

Context = _reflection.GeneratedProtocolMessageType('Context', (_message.Message,), {
  'DESCRIPTOR' : _CONTEXT,
  '__module__' : 'core.pyatdl_pb2'
  # @@protoc_insertion_point(class_scope:pyatdl.Context)
  })
_sym_db.RegisterMessage(Context)

Action = _reflection.GeneratedProtocolMessageType('Action', (_message.Message,), {
  'DESCRIPTOR' : _ACTION,
  '__module__' : 'core.pyatdl_pb2'
  # @@protoc_insertion_point(class_scope:pyatdl.Action)
  })
_sym_db.RegisterMessage(Action)

Project = _reflection.GeneratedProtocolMessageType('Project', (_message.Message,), {
  'DESCRIPTOR' : _PROJECT,
  '__module__' : 'core.pyatdl_pb2'
  # @@protoc_insertion_point(class_scope:pyatdl.Project)
  })
_sym_db.RegisterMessage(Project)

Note = _reflection.GeneratedProtocolMessageType('Note', (_message.Message,), {
  'DESCRIPTOR' : _NOTE,
  '__module__' : 'core.pyatdl_pb2'
  # @@protoc_insertion_point(class_scope:pyatdl.Note)
  })
_sym_db.RegisterMessage(Note)

NoteList = _reflection.GeneratedProtocolMessageType('NoteList', (_message.Message,), {
  'DESCRIPTOR' : _NOTELIST,
  '__module__' : 'core.pyatdl_pb2'
  # @@protoc_insertion_point(class_scope:pyatdl.NoteList)
  })
_sym_db.RegisterMessage(NoteList)

ContextList = _reflection.GeneratedProtocolMessageType('ContextList', (_message.Message,), {
  'DESCRIPTOR' : _CONTEXTLIST,
  '__module__' : 'core.pyatdl_pb2'
  # @@protoc_insertion_point(class_scope:pyatdl.ContextList)
  })
_sym_db.RegisterMessage(ContextList)

Folder = _reflection.GeneratedProtocolMessageType('Folder', (_message.Message,), {
  'DESCRIPTOR' : _FOLDER,
  '__module__' : 'core.pyatdl_pb2'
  # @@protoc_insertion_point(class_scope:pyatdl.Folder)
  })
_sym_db.RegisterMessage(Folder)

ToDoList = _reflection.GeneratedProtocolMessageType('ToDoList', (_message.Message,), {
  'DESCRIPTOR' : _TODOLIST,
  '__module__' : 'core.pyatdl_pb2'
  # @@protoc_insertion_point(class_scope:pyatdl.ToDoList)
  })
_sym_db.RegisterMessage(ToDoList)


_VISITORINFO0.fields_by_name['cwc_uid']._options = None
_CHECKSUMANDDATA.fields_by_name['payload_length']._options = None
_TIMESTAMP.fields_by_name['ctime']._options = None
_TIMESTAMP.fields_by_name['dtime']._options = None
_TIMESTAMP.fields_by_name['mtime']._options = None
_COMMON.fields_by_name['uid']._options = None
_PROJECT.fields_by_name['default_context_uid']._options = None
# @@protoc_insertion_point(module_scope)
