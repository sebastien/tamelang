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
print(array_a.type.qname)

print(array_a[T.int(5)])

# --
# The question is basically: can the runtime perform the operations on the
# given arguments.
# EOF
