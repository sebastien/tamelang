from dataclasses import dataclass
from typing import TypeVar
from .model import Type, Structure, Value, Literal, Sequence, Operation, Operator

A = TypeVar("A")

B8 = Structure(8)
B16 = Structure(16)
B32 = Structure(32)
B64 = Structure(64)
B128 = Structure(128)


Any = Type("Any")
Number = Type("Number") << Any
NaturalNumber = Type("NaturalNumber") << Number
DecimalNumber = Type("DecimalNumber") << Number
Array = Type("Array", T=Any)


def int32(value: int) -> Literal[int]:
    return Literal[int](NaturalNumber, structure=B32, value=value)


class T:
    @staticmethod
    def int(value: int) -> Literal[int]:
        return int32(value)

    @staticmethod
    def array(value: Literal[A], count: int) -> Value:
        return Value(type=Array(value.type), structure=Sequence(value.size, count))


# EOF
