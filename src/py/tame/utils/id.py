from typing import Iterator


# TODO: Identifiers that are long, monotonic and node-safe


def integers() -> Iterator[int]:
    counter: int = 0
    while True:
        yield counter
        counter += 1


IntegerID = integers()

# EOF
