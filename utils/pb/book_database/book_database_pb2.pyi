from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetBookRequest(_message.Message):
    __slots__ = ("request_id", "commitStatus")
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    COMMITSTATUS_FIELD_NUMBER: _ClassVar[int]
    request_id: str
    commitStatus: bool
    def __init__(self, request_id: _Optional[str] = ..., commitStatus: bool = ...) -> None: ...

class UpdateBookRequest(_message.Message):
    __slots__ = ("book", "commitStatus")
    BOOK_FIELD_NUMBER: _ClassVar[int]
    COMMITSTATUS_FIELD_NUMBER: _ClassVar[int]
    book: Book
    commitStatus: bool
    def __init__(self, book: _Optional[_Union[Book, _Mapping]] = ..., commitStatus: bool = ...) -> None: ...

class Empty(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class Book(_message.Message):
    __slots__ = ("id", "title", "author", "description", "copies", "copiesAvailable", "category", "img", "price")
    ID_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    AUTHOR_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    COPIES_FIELD_NUMBER: _ClassVar[int]
    COPIESAVAILABLE_FIELD_NUMBER: _ClassVar[int]
    CATEGORY_FIELD_NUMBER: _ClassVar[int]
    IMG_FIELD_NUMBER: _ClassVar[int]
    PRICE_FIELD_NUMBER: _ClassVar[int]
    id: str
    title: str
    author: str
    description: str
    copies: int
    copiesAvailable: int
    category: str
    img: str
    price: float
    def __init__(self, id: _Optional[str] = ..., title: _Optional[str] = ..., author: _Optional[str] = ..., description: _Optional[str] = ..., copies: _Optional[int] = ..., copiesAvailable: _Optional[int] = ..., category: _Optional[str] = ..., img: _Optional[str] = ..., price: _Optional[float] = ...) -> None: ...

class BookList(_message.Message):
    __slots__ = ("books",)
    BOOKS_FIELD_NUMBER: _ClassVar[int]
    books: _containers.RepeatedCompositeFieldContainer[Book]
    def __init__(self, books: _Optional[_Iterable[_Union[Book, _Mapping]]] = ...) -> None: ...

class Head2TailResponse(_message.Message):
    __slots__ = ("success",)
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    def __init__(self, success: bool = ...) -> None: ...

class VoteCommitRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class VoteCommitResponse(_message.Message):
    __slots__ = ("success",)
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    def __init__(self, success: bool = ...) -> None: ...

class GetBookFromTitleRequest(_message.Message):
    __slots__ = ("title",)
    TITLE_FIELD_NUMBER: _ClassVar[int]
    title: str
    def __init__(self, title: _Optional[str] = ...) -> None: ...
