from ..model import Value, Operation, Operator
from typing import Iterable, Union
from io import StringIO
from enum import Enum


class Control(Enum):
    START = "{"
    END = "}"
    EOL = "\n"


START = Control.START
END = Control.END
EOL = Control.EOL
TOutput = Iterable[Union[str, Control]]


class Output:
    def __init__(self, stream: TOutput):
        self.stream = stream

    def write(self, output: StringIO):
        for atom in self:
            output.write(atom)
        return output

    def __iter__(self):
        for atom in self.stream:
            if atom is EOL:
                yield atom.value
            elif isinstance(atom, Control):
                pass
            else:
                yield atom

    def __str__(self) -> str:
        res = StringIO()
        self.write(res)
        res.seek(0)
        return res.read()


class Backend:
    def value(self, value: Value) -> TOutput:
        raise NotImplemented

    def operation(self, operation: Operation) -> TOutput:
        name, lv, rv = operation.name, operation.lvalue, operation.rvalue
        if name is Operator.ADD:
            return self.add(lv, rv)
        elif name is Operator.INDEX:
            return self.index(lv, rv)
        else:
            raise RuntimeError("Operation '{name}' not implemented in backend: {self}")

    def add(self, value: Value, rvalue: Value) -> TOutput:
        raise NotImplemented

    def index(self, value: Value, rvalue: Value) -> TOutput:
        raise NotImplemented

    def on(self, value: Union[Value, Operation]) -> TOutput:
        return (
            self.operation(value) if isinstance(value, Operation) else self.value(value)
        )

    def __call__(self, value: Union[Value, Operation]) -> Output:
        return Output(self.on(value))


# EOF
