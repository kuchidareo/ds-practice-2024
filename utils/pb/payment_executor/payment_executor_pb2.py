# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: utils/pb/payment_executor/payment_executor.proto
# Protobuf Python Version: 4.25.1
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n0utils/pb/payment_executor/payment_executor.proto\x12\x10payment_executor\"/\n\x17PaymentExecutionRequest\x12\x14\n\x0c\x63ommitStatus\x18\x01 \x01(\x08\"+\n\x18PaymentExecutionResponse\x12\x0f\n\x07success\x18\x01 \x01(\x08\"\x13\n\x11VoteCommitRequest\"%\n\x12VoteCommitResponse\x12\x0f\n\x07success\x18\x01 \x01(\x08\x32\xe5\x01\n\x16PaymentExecutorService\x12g\n\x0e\x45xecutePayment\x12).payment_executor.PaymentExecutionRequest\x1a*.payment_executor.PaymentExecutionResponse\x12\x62\n\x15SendVoteToCoordinator\x12#.payment_executor.VoteCommitRequest\x1a$.payment_executor.VoteCommitResponseb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'utils.pb.payment_executor.payment_executor_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
  DESCRIPTOR._options = None
  _globals['_PAYMENTEXECUTIONREQUEST']._serialized_start=70
  _globals['_PAYMENTEXECUTIONREQUEST']._serialized_end=117
  _globals['_PAYMENTEXECUTIONRESPONSE']._serialized_start=119
  _globals['_PAYMENTEXECUTIONRESPONSE']._serialized_end=162
  _globals['_VOTECOMMITREQUEST']._serialized_start=164
  _globals['_VOTECOMMITREQUEST']._serialized_end=183
  _globals['_VOTECOMMITRESPONSE']._serialized_start=185
  _globals['_VOTECOMMITRESPONSE']._serialized_end=222
  _globals['_PAYMENTEXECUTORSERVICE']._serialized_start=225
  _globals['_PAYMENTEXECUTORSERVICE']._serialized_end=454
# @@protoc_insertion_point(module_scope)