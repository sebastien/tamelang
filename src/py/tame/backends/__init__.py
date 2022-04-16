from ..model import Value, Application, Operator
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
    def on(self, value: Union[Value, Application]) -> TOutput:
        if isinstance(value, Application):
            return self.application(value)
        elif isinstance(value, Value):
            return self.value(value)
        else:
            raise ValueError(f"Expected Value or Application, got: {value}")

    def value(self, value: Value) -> TOutput:
        raise NotImplemented

    def application(self, application: Application) -> TOutput:
        name = application.name
        if name is Operator.Add:
            return self.add(application[0], application[1])
        elif name is Operator.Index:
            return self.index(application[0], application[1])
        else:
            raise RuntimeError("Operation '{name}' not implemented in backend: {self}")

    def add(self, value: Value, rvalue: Value) -> TOutput:
        raise NotImplemented

    def index(self, value: Value, rvalue: Value) -> TOutput:
        raise NotImplemented

    def __call__(self, value: Union[Value, Application]) -> Output:
        return Output(self.on(value))


# EOF
