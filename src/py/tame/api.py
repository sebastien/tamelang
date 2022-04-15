from dataclasses import dataclass
from typing import TypeVar, Generic, Optional

T = TypeVar("T")


class Structure:
    def __init__(self, size: int):
        assert size % 8 == 0, f"Exepected size multiple of 8, got: {size}"
        self.size: int = size

    def __str__(self):
        return f"#{self.size}"


B8 = Structure(8)
B16 = Structure(16)
B32 = Structure(32)
B64 = Structure(64)
B128 = Structure(128)


class Type:
    def __init__(self, name: str):
        self.name: str = name

    def __str__(self):
        return f":{self.name}"


Number = Type("Number")
NaturalNumber = Type("NaturalNumber")
DecimalNumber = Type("DecimalNumber")


class Value(Generic[T]):
    def __init__(self, type: Type, structure: Structure, value: T):
        self.type = type
        self.structure = structure
        self.value = value

    def __add__(self, other: "Value"):
        assert isinstance(
            other, Value
        ), "Can only accept a Value subclass, got: {other}"
        return Operation(Operation.ADD, self, other)

    def __str__(self):
        return f"({self.__class__.__name__}{self.type}{self.structure} {self.value})"


class Operation:
    ADD = ":add"

    def __init__(self, name: str, lvalue: Value, rvalue: Optional[Value]):
        self.name = name
        self.lvalue = lvalue
        self.rvalue = rvalue

    def __str__(self):
        return f"({self.name} {self.lvalue} {self.rvalue})"


class Int32(Value[int]):
    def __init__(self, value: int):
        super().__init__(type=NaturalNumber, structure=B32, value=value)


class T:
    def int(value: int) -> Int32:
        return Int32(value=value)
