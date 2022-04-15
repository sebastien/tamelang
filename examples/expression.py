from tame.api import T
from tame.backends.c import C

a = T.int(10)
b = T.int(20)
print(a, b)
print(a + b)
print(C(a + b))
