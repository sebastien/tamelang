from dataclasses import dataclass
from .model import Type, Structure, Value


B8 = Structure(8)
B16 = Structure(16)
B32 = Structure(32)
B64 = Structure(64)
B128 = Structure(128)


Number = Type("Number")
NaturalNumber = Type("NaturalNumber") << Number
DecimalNumber = Type("DecimalNumber") << Number


class Int32(Value[int]):
    def __init__(self, value: int):
        super().__init__(type=NaturalNumber, structure=B32, value=value)


class T:
    def int(value: int) -> Int32:
        return Int32(value=value)


# EOF
