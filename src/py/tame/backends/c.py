from ..model import Value
from . import Backend, TOutput

T = None


class CBackend(Backend):
    def value(self, value: Value) -> TOutput:
        return f"{value.value}"

    def add(self, lvalue: Value, rvalue: Value):
        return f"{self.value(lvalue)} + {self.value(rvalue)}"


C = CBackend()
# EOF
