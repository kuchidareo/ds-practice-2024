from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class User(_message.Message):
    __slots__ = ("name", "contact")
    NAME_FIELD_NUMBER: _ClassVar[int]
    CONTACT_FIELD_NUMBER: _ClassVar[int]
    name: str
    contact: str
    def __init__(self, name: _Optional[str] = ..., contact: _Optional[str] = ...) -> None: ...

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

class Item(_message.Message):
    __slots__ = ("book", "quantity")
    BOOK_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    book: Book
    quantity: int
    def __init__(self, book: _Optional[_Union[Book, _Mapping]] = ..., quantity: _Optional[int] = ...) -> None: ...

class CreditCard(_message.Message):
    __slots__ = ("number", "expirationDate", "cvv")
    NUMBER_FIELD_NUMBER: _ClassVar[int]
    EXPIRATIONDATE_FIELD_NUMBER: _ClassVar[int]
    CVV_FIELD_NUMBER: _ClassVar[int]
    number: str
    expirationDate: str
    cvv: str
    def __init__(self, number: _Optional[str] = ..., expirationDate: _Optional[str] = ..., cvv: _Optional[str] = ...) -> None: ...

class Order(_message.Message):
    __slots__ = ("orderId", "user", "items", "creditCard", "address", "priority")
    ORDERID_FIELD_NUMBER: _ClassVar[int]
    USER_FIELD_NUMBER: _ClassVar[int]
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    CREDITCARD_FIELD_NUMBER: _ClassVar[int]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    PRIORITY_FIELD_NUMBER: _ClassVar[int]
    orderId: str
    user: User
    items: _containers.RepeatedCompositeFieldContainer[Item]
    creditCard: CreditCard
    address: BillingAddress
    priority: float
    def __init__(self, orderId: _Optional[str] = ..., user: _Optional[_Union[User, _Mapping]] = ..., items: _Optional[_Iterable[_Union[Item, _Mapping]]] = ..., creditCard: _Optional[_Union[CreditCard, _Mapping]] = ..., address: _Optional[_Union[BillingAddress, _Mapping]] = ..., priority: _Optional[float] = ...) -> None: ...

class BillingAddress(_message.Message):
    __slots__ = ("street", "city", "state", "zip", "country")
    STREET_FIELD_NUMBER: _ClassVar[int]
    CITY_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    ZIP_FIELD_NUMBER: _ClassVar[int]
    COUNTRY_FIELD_NUMBER: _ClassVar[int]
    street: str
    city: str
    state: str
    zip: str
    country: str
    def __init__(self, street: _Optional[str] = ..., city: _Optional[str] = ..., state: _Optional[str] = ..., zip: _Optional[str] = ..., country: _Optional[str] = ...) -> None: ...

class EnqueueRequest(_message.Message):
    __slots__ = ("order",)
    ORDER_FIELD_NUMBER: _ClassVar[int]
    order: Order
    def __init__(self, order: _Optional[_Union[Order, _Mapping]] = ...) -> None: ...

class EnqueueResponse(_message.Message):
    __slots__ = ("success",)
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    def __init__(self, success: bool = ...) -> None: ...

class DequeueRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class DequeueResponse(_message.Message):
    __slots__ = ("order", "success")
    ORDER_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    order: Order
    success: bool
    def __init__(self, order: _Optional[_Union[Order, _Mapping]] = ..., success: bool = ...) -> None: ...
