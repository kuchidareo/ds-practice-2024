# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: utils/pb/order_executor/order_executor.proto
# Protobuf Python Version: 4.25.1
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n,utils/pb/order_executor/order_executor.proto\x12\x0eorder_executor\"\x16\n\x05Token\x12\r\n\x05token\x18\x01 \x01(\t\" \n\rTokenResponse\x12\x0f\n\x07success\x18\x01 \x01(\x08\"\r\n\x0bVoteRequest\"\x1f\n\x0cVoteResponse\x12\x0f\n\x07success\x18\x01 \x01(\x08\"\x14\n\x12HealthCheckRequest\"$\n\x13HealthCheckResponse\x12\r\n\x05\x61live\x18\x01 \x01(\x08\x32\x86\x02\n\x14OrderExecutorService\x12\x41\n\tPassToken\x12\x15.order_executor.Token\x1a\x1d.order_executor.TokenResponse\x12V\n\x0b\x43heckHealth\x12\".order_executor.HealthCheckRequest\x1a#.order_executor.HealthCheckResponse\x12S\n\x16SendVoteToParticipants\x12\x1b.order_executor.VoteRequest\x1a\x1c.order_executor.VoteResponseb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'utils.pb.order_executor.order_executor_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
  DESCRIPTOR._options = None
  _globals['_TOKEN']._serialized_start=64
  _globals['_TOKEN']._serialized_end=86
  _globals['_TOKENRESPONSE']._serialized_start=88
  _globals['_TOKENRESPONSE']._serialized_end=120
  _globals['_VOTEREQUEST']._serialized_start=122
  _globals['_VOTEREQUEST']._serialized_end=135
  _globals['_VOTERESPONSE']._serialized_start=137
  _globals['_VOTERESPONSE']._serialized_end=168
  _globals['_HEALTHCHECKREQUEST']._serialized_start=170
  _globals['_HEALTHCHECKREQUEST']._serialized_end=190
  _globals['_HEALTHCHECKRESPONSE']._serialized_start=192
  _globals['_HEALTHCHECKRESPONSE']._serialized_end=228
  _globals['_ORDEREXECUTORSERVICE']._serialized_start=231
  _globals['_ORDEREXECUTORSERVICE']._serialized_end=493
# @@protoc_insertion_point(module_scope)
