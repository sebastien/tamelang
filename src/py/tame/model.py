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
    # A unique, stable identifier can be associtated with the value
    Identifable = auto()


class Operator(Enum):
    # Unary
    Not = ":not"
    # Binary
    Add = ":add"
    Sub = ":sub"
    Mul = ":mul"
    Div = ":div"
    Mod = ":mod"
    Pow = ":pow"
    Or = ":or"
    Eq = ":eq"
    Is = ":is"
    Gt = ":gt"
    Lt = ":gt"
    And = ":and"
    Index = ":index"
    Access = ":access"
    Slice = ":slice"
    # Ternary
    Cond = ":cond"


# TODO: The structure should create some kind of hash that is then
# easily comparable with others.
class Structure:
    def __init__(self, size: int):
        assert size % 8 == 0, f"Expected size multiple of 8, got: {size}"
        self.size: int = size

    def __repr__(self):
        return f"#{self.size}"


class Sequence(Structure):
    def __init__(self, size: int, length: int):
        super().__init__(size * length)
        assert size % 8 == 0, f"Expected size multiple of 8, got: {size}"
        assert length > 0, f"Expected length to be > 0, got: {length}"
        self.itemSize = size
        self.length = length

    def __repr__(self):
        return f"#[{self.length}*{self.itemSize}]={self.size}"


# TODO: Have a List structure that accepts a given sentinel. For instance
# null-terminated string.


class Type:
    """A generic class to represent a variety of types, from basic name
    types to type parameters."""

    Registry: DAG[int, "Type"] = DAG()
    Symbols: dict[str, "Type"] = {}

    def __init__(
        self,
        # Types need to be named
        name: str,
        # The scope is like the parent type (used for naming/qname)
        scope: Optional["Type"] = None,
        # Capabilities are the operations that are allowed on a value
        # of that type.
        capabilities: Optional[Iterable[Operability]] = None,
        # Types can have parameters
        **parameters: Optional[Union["Type"]],
        # TODO: Types can have constraints, like structure, bounds, etc.
    ):
        self.id: int = next(IntegerID)
        self.name: str = name
        self.scope: Optional[Type] = scope
        self.qname: str = f"{scope.name}.{name}" if scope else name
        self.parameters: dict[Union[Type]] = {
            k: v or Type(name=k, scope=self) for k, v in parameters.items()
        }
        # We define the type capabilities
        self.capabilities: int = 0
        for cap in capabilities or ():
            self.capabilities = self.capabilities | cap.value
        # We define if the type is abstract or not
        self.isAbstract: bool = False
        if self.parameters:
            for _ in self.parameters.values():
                if _.isAbstract:
                    self.isAbstract = True
                    break
        # We register the type in the registry
        Type.Symbols[self.key] = self

    @property
    def key(self) -> str:
        return self.derivedKey()

    def derivedKey(
        self, parameters: Optional[Union[list["Type"], dict[str, "Type"]]] = None
    ) -> str:
        """Returns the name of the type derived from this type, completed
        by the given type aprameters"""
        p = []
        if not parameters:
            p = [v for v in self.parameters.values()]
        elif isinstance(parameters, dict):
            p = [parameters.get(k, v) for k, v in self.parameters.items()]
        else:
            p = parameters
        return (
            self.qname
            if not p
            else f"{self.qname}[{','.join(_.key if _ else '_' for _ in p)}]"
        )

    def supports(self, *capability: Operability) -> bool:
        """Tells if the given capabilities are supported by the type"""
        for cap in capability:
            if self.capabilities & cap.value == 0:
                return False
        return True

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
            # NOTE: This is a bit awkward, and should be probably be
            # something that is very fast to compute. There is an opportunity
            # for a numerical representation of all of that.
            a = {k: i for i, k in enumerate(Type.Registry.ancestors(self.id))}
            b = {k: i for i, k in enumerate(Type.Registry.ancestors(other.id))}
            l = sorted([(k, i) for k, i in b.items() if k in a], key=lambda _: _[1])
            return Type.Registry.get(l[0]) if l else None

    def __lshift__(self, other: "Type"):
        assert isinstance(other, Type), f"Expected type, got: {other}"
        Type.Registry.addInput(self.id, other.id)
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
        key = self.derivedKey(parameters)
        # We return the type if it's already there. This ensures
        # unicity of type instances.
        if key in self.Symbols:
            return self.Symbols[key]
        else:
            derived = Type(name=self.name, scope=self.scope, **parameters)
            derived.capabilities = self.capabilities
            # The derived type is linked to this type
            return derived << self

    def __getitem__(self, key: str) -> Optional["Type"]:
        return self.parameters[key]

    def __repr__(self):
        return f":{self.key}"


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
        return Application(Operator.Add, self, other)

    def __getitem__(self, key: "Value"):
        assert isinstance(key, Value), "Can only accept a Value subclass, got: {other}"
        return Application(Operator.Index, self, key)

    def __repr__(self):
        return f"({self.__class__.__name__}{self.type}{self.structure})"


class Literal(Value, Generic[T]):
    def __init__(self, type: Type, structure: Structure, value: T):
        super().__init__(type, structure)
        self.value = value

    def __repr__(self):
        return f"({self.__class__.__name__}{self.type}{self.structure} {self.value})"


class Operation:
    Registry: dict[str, "Operation"] = {}

    @staticmethod
    def Key(name: Union[Operator, str], lvalue: Type, rvalue: Optional[Type]):
        return "{name.value if isinstance(name,Operator) else name}.{lvalue.key}{f'.{rvalue.key}' if rvalue else ''}"

    @staticmethod
    def Ensure(name: Union[Operator, str], lvalue: Type, rvalue: Optional[Type]):
        key = Operation.Key(name, lvalue, rvalue)
        if key in Operation.Registry:
            return Operation.Registry[key]
        else:
            return Operation(name, lvalue, rvalue)

    def __init__(
        self, name: Union[Operator, str], lvalue: Type, rvalue: Optional[Type]
    ):
        self.name = name
        self.lvalue = lvalue
        self.rvalue = rvalue
        # FIXME: This should be defined in the operation interface itself
        self.type: Optional[Type] = (
            lvalue if rvalue is None else lvalue.intersect(rvalue)
        )
        self.key = "{name.value if isinstance(name,Operator) else name}.{lvalue.key}{f'.{rvalue.key}' if rvalue else ''}"
        assert (
            self.key not in Operation.Registry
        ), "Operation already registered, use 'Operation.Ensure()' instead"
        Operation.Registry[self.key] = self

    def __repr__(self):
        return f"({self.name} {self.lvalue} {self.rvalue})"


class Application:
    """Represents the application of values to a symbol/operator. The actual
    operation represented by the symbol/operator will be resolved by the
    runtime."""

    def __init__(self, name: Union[Operator, str], *value: Value):
        self.name = name
        self.values = value
        self.arity = len(value)

    def __getitem__(self, index: int):
        assert index >= 0 and index < self.arity
        return self.values[index]

    def __repr__(self):
        return f"({self.name}[{','.join(str(_.type) for _ in self.values)}] {' '.join(str(_) for _ in self.values)})"


# EOF
