# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: utils/pb/book_database/book_database.proto
# Protobuf Python Version: 4.25.1
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n*utils/pb/book_database/book_database.proto\x12\rbook_database\"$\n\x0eGetBookRequest\x12\x12\n\nrequest_id\x18\x01 \x01(\t\"\x07\n\x05\x45mpty\"\x9d\x01\n\x04\x42ook\x12\n\n\x02id\x18\x01 \x01(\t\x12\r\n\x05title\x18\x02 \x01(\t\x12\x0e\n\x06\x61uthor\x18\x03 \x01(\t\x12\x13\n\x0b\x64\x65scription\x18\x04 \x01(\t\x12\x0e\n\x06\x63opies\x18\x05 \x01(\x05\x12\x17\n\x0f\x63opiesAvailable\x18\x06 \x01(\x05\x12\x10\n\x08\x63\x61tegory\x18\x07 \x01(\t\x12\x0b\n\x03img\x18\x08 \x01(\t\x12\r\n\x05price\x18\t \x01(\x02\".\n\x08\x42ookList\x12\"\n\x05\x62ooks\x18\x01 \x03(\x0b\x32\x13.book_database.Book2\xc0\x02\n\x13\x42ookDatabaseService\x12\x33\n\x07\x41\x64\x64\x42ook\x12\x13.book_database.Book\x1a\x13.book_database.Book\x12=\n\x07GetBook\x12\x1d.book_database.GetBookRequest\x1a\x13.book_database.Book\x12:\n\tListBooks\x12\x14.book_database.Empty\x1a\x17.book_database.BookList\x12\x36\n\nUpdateBook\x12\x13.book_database.Book\x1a\x13.book_database.Book\x12\x41\n\nDeleteBook\x12\x1d.book_database.GetBookRequest\x1a\x14.book_database.Emptyb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'utils.pb.book_database.book_database_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
  DESCRIPTOR._options = None
  _globals['_GETBOOKREQUEST']._serialized_start=61
  _globals['_GETBOOKREQUEST']._serialized_end=97
  _globals['_EMPTY']._serialized_start=99
  _globals['_EMPTY']._serialized_end=106
  _globals['_BOOK']._serialized_start=109
  _globals['_BOOK']._serialized_end=266
  _globals['_BOOKLIST']._serialized_start=268
  _globals['_BOOKLIST']._serialized_end=314
  _globals['_BOOKDATABASESERVICE']._serialized_start=317
  _globals['_BOOKDATABASESERVICE']._serialized_end=637
# @@protoc_insertion_point(module_scope)
