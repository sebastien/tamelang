from ..model import Value
from ..api import NaturalNumber
from . import Backend, TOutput

T = None


class CBackend(Backend):
    def value(self, value: Value) -> TOutput:
        return f"{value.value}"

    def add(self, lvalue: Value, rvalue: Value):
        return f"{self.value(lvalue)} + {self.value(rvalue)}"

    def index(self, lvalue: Value, rvalue: Value):
        if isinstance(lvalue.structure, Sequence):
            if rvalue.type.isa(NaturalNumber):
                return f"OK"
            else:
                raise ValueError(f"Unsupported indexing value: {rvalue}")
        else:
            raise ValueError(f"Unsupported indexed value: {rvalue}")


C = CBackend()
# EOF
