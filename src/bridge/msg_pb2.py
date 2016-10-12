# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: msg.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='msg.proto',
  package='message_factory',
  syntax='proto3',
  serialized_pb=_b('\n\tmsg.proto\x12\x0fmessage_factory\"r\n\x08InputMsg\x12\x0f\n\x07\x62ot_hid\x18\x01 \x01(\t\x12\x14\n\x0cscraper_name\x18\x02 \x01(\t\x12\x13\n\x0bsource_name\x18\x03 \x01(\t\x12\x14\n\x0c\x66\x65tch_kwargs\x18\x04 \x01(\t\x12\x14\n\x0cquery_kwargs\x18\x05 \x01(\t\")\n\tOutputMsg\x12\x0f\n\x07\x62ot_hid\x18\x01 \x01(\t\x12\x0b\n\x03msg\x18\x02 \x01(\tb\x06proto3')
)
_sym_db.RegisterFileDescriptor(DESCRIPTOR)




_INPUTMSG = _descriptor.Descriptor(
  name='InputMsg',
  full_name='message_factory.InputMsg',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='bot_hid', full_name='message_factory.InputMsg.bot_hid', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='scraper_name', full_name='message_factory.InputMsg.scraper_name', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='source_name', full_name='message_factory.InputMsg.source_name', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='fetch_kwargs', full_name='message_factory.InputMsg.fetch_kwargs', index=3,
      number=4, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='query_kwargs', full_name='message_factory.InputMsg.query_kwargs', index=4,
      number=5, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=30,
  serialized_end=144,
)


_OUTPUTMSG = _descriptor.Descriptor(
  name='OutputMsg',
  full_name='message_factory.OutputMsg',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='bot_hid', full_name='message_factory.OutputMsg.bot_hid', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='msg', full_name='message_factory.OutputMsg.msg', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=146,
  serialized_end=187,
)

DESCRIPTOR.message_types_by_name['InputMsg'] = _INPUTMSG
DESCRIPTOR.message_types_by_name['OutputMsg'] = _OUTPUTMSG

InputMsg = _reflection.GeneratedProtocolMessageType('InputMsg', (_message.Message,), dict(
  DESCRIPTOR = _INPUTMSG,
  __module__ = 'msg_pb2'
  # @@protoc_insertion_point(class_scope:message_factory.InputMsg)
  ))
_sym_db.RegisterMessage(InputMsg)

OutputMsg = _reflection.GeneratedProtocolMessageType('OutputMsg', (_message.Message,), dict(
  DESCRIPTOR = _OUTPUTMSG,
  __module__ = 'msg_pb2'
  # @@protoc_insertion_point(class_scope:message_factory.OutputMsg)
  ))
_sym_db.RegisterMessage(OutputMsg)


# @@protoc_insertion_point(module_scope)
