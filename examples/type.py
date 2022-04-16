from tame.api import Type, Operation, Operator

# --
# We define a generic array type
Array = Type("Array", T=None)
print(Array)
print(Array["T"])

# --
# We define an abstract access operation on the array
Array_access = Operation(Operator.Access, Array, Array["T"])
print(Array_access)

# EOF
