from tame.api import T
from tame.backends.c import C

a = T.int(10)
b = T.int(20)

# We show that in C
print(C(a + b))

# TODO: Support casting. For instance, if we have int + float, then we get float

# --
# ### Arrays
array_a = T.array(T.int(0), 10)
print(array_a)
