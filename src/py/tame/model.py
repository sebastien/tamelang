from .utils.dag import DAG
from .utils.id import IntegerID
from typing import TypeVar, Generic, Optional, Iterator

T = TypeVar("T")


# TODO: The structure should create some kind of hash that is then
# easily comparable with others.
class Structure:
    def __init__(self, size: int):
        assert size % 8 == 0, f"Exepected size multiple of 8, got: {size}"
        self.size: int = size

    def __str__(self):
        return f"#{self.size}"


class Type:
    Registry: DAG[int, "Type"] = DAG()

    def __init__(self, name: str):
        self.id: int = next(IntegerID)
        self.name: str = name
        self.Registry.setNode(self.id, self)

    def isa(self, other: "Type"):
        assert isinstance(other, Type), f"Expected type, got: {other}"
        # TODO: Should look in the DAG for similarities
        if other is self:
            return True
        else:
            raise NotImplementedError

    def intersect(self, other: "Type") -> Optional["Type"]:
        """Returns the first common ancestors of both tyes"""
        assert isinstance(other, Type), f"Expected type, got: {other}"
        if other is self:
            return self
        else:
            raise NotImplementedError

    def __str__(self):
        return f":{self.name}"

    def __lshift__(self, other: "Type"):
        assert isinstance(other, Type), f"Expected type, got: {other}"
        self.Registry.addInput(self.id, other.id)
        return self


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
        # FIXME: This should be defined in the operation interface itself
        self.type = (
            lvalue.type if rvalue is None else lvalue.type.intersect(rvalue.type)
        )
        assert self.type

    def __str__(self):
        return f"({self.name} {self.lvalue} {self.rvalue})"


# EOF
