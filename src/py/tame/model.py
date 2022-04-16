from .utils.dag import DAG
from .utils.id import IntegerID
from typing import TypeVar, Generic, Optional, Iterator, Iterable, Union
from enum import Enum, Flag, auto

T = TypeVar("T")


class Capability(Flag):
    """Defines the capabilities that are given to a reference."""

    # The value can be referenced
    Dereference = auto()
    # Transfers the reference to something else
    Transfer = auto()
    # The value can be accessed
    Access = auto()
    # The value can be updated
    Update = auto()
    # The value can be removed
    Remove = auto()


class Operability(Flag):
    """Defines the oeprations that can be performed on a type"""

    # The value can be evaluated
    Evaluate = auto()
    # The value can be decomposed
    Decompose = auto()
    # The value can be invoked
    Invoke = auto()
    # The value can be indexed
    Index = auto()
    # The value can be sliced
    Slice = auto()


# TODO: The structure should create some kind of hash that is then
# easily comparable with others.
class Structure:
    def __init__(self, size: int):
        assert size % 8 == 0, f"Expected size multiple of 8, got: {size}"
        self.size: int = size

    def __str__(self):
        return f"#{self.size}"


class Sequence(Structure):
    def __init__(self, size: int, length: int):
        super().__init__(size * length)
        assert size % 8 == 0, f"Expected size multiple of 8, got: {size}"
        assert length > 0, f"Expected length to be > 0, got: {length}"
        self.itemSize = size
        self.length = length

    def __str__(self):
        return f"#[{self.length}*{self.itemSize}]={self.size}"


# TODO: Have a List structure that accepts a given sentinel. For instance
# null-terminated string.


class Type:
    Registry: DAG[int, "Type"] = DAG()
    Symbols: dict[str, "Type"] = {}

    def __init__(
        self,
        name: str,
        capabilities: Optional[Iterable[Operability]] = None,
        **parameters: Optional["Type"],
    ):
        self.id: int = next(IntegerID)
        self.name: str = name
        self.parameters: Optional[Type] = parameters
        self._isAbstract: Optional[bool] = None
        self.capability: int = 0
        for cap in capabilities or ():
            self.capability = self.capability | cap.value
        self.Registry.setNode(self.id, self)
        if (qname := self.qname) not in self.Symbols:
            self.Symbols[qname] = self

    def supports(self, *capability: Operability) -> bool:
        """Tells if the given capabilities are supported by the type"""
        for cap in capability:
            if self.capability & cap == 0:
                return False
        return True

    @property
    def isAbstract(self) -> bool:
        if self._isAbstract is not None:
            return self._isAbstract
        if self.parameters:
            for _ in self.parameters.values():
                self._isAbstract = True
                return self._isAbstract
        self._isAbstract = False
        return self._isAbstract

    @property
    def qname(self) -> str:
        return self.derivedName()

    def derivedName(
        self, parameters: Optional[Union[list, dict[str, str]]] = None
    ) -> str:
        p = []
        if not parameters:
            p = [v for v in self.parameters.values()]
        elif isinstance(parameters, dict):
            p = [parameters.get(k, v) for k, v in self.parameters.items()]
        else:
            p = parameters
        return (
            self.name
            if not p
            else f"{self.name}[{','.join(_.qname if _ else '_' for _ in p)}]"
        )

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

    def __call__(self, *args: "Type", **kwargs: "Type"):
        """Returns the type that corresponds to the application of the given
        types to this type."""
        parameters = {k: v for k, v in self.parameters.items()}
        for i, k in enumerate(self.parameters.keys()):
            if i < len(args):
                parameters[k] = args[i]
            elif k in kwargs:
                parameters[k] = kwargs[k]
        dname = self.derivedName(parameters)
        # We return the type if it's already there. This ensures
        # unicity of type instances.
        if dname in self.Symbols:
            return self.Symbols[dname]
        else:
            derived = Type(self.name, **parameters)
            # The derived type is linked to this type
            return derived << self

        return self


class Value:
    def __init__(self, type: Type, structure: Structure):
        self.type = type
        self.structure = structure

    @property
    def size(self) -> Optional[int]:
        return self.structure.size

    def __add__(self, other: "Value"):
        assert isinstance(
            other, Value
        ), "Can only accept a Value subclass, got: {other}"
        return Operation(Operator.ADD, self, other)

    def __getitem__(self, key: "Value"):
        assert isinstance(key, Value), "Can only accept a Value subclass, got: {other}"
        return Operation(Operator.INDEX, self, key)

    def __str__(self):
        return f"({self.__class__.__name__}{self.type}{self.structure})"


class Literal(Value, Generic[T]):
    def __init__(self, type: Type, structure: Structure, value: T):
        super().__init__(type, structure)
        self.value = value

    def __str__(self):
        return f"({self.__class__.__name__}{self.type}{self.structure} {self.value})"


class Operator(Enum):
    ADD = ":add"
    INDEX = ":index"


class Operation:
    def __init__(
        self, name: Union[Operator, str], lvalue: Value, rvalue: Optional[Value]
    ):
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
