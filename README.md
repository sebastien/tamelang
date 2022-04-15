```
 ______   ______     __    __     ______     __         ______     __   __     ______    
/\__  _\ /\  __ \   /\ "-./  \   /\  ___\   /\ \       /\  __ \   /\ "-.\ \   /\  ___\   
\/_/\ \/ \ \  __ \  \ \ \-./\ \  \ \  __\   \ \ \____  \ \  __ \  \ \ \-.  \  \ \ \__ \  
   \ \_\  \ \_\ \_\  \ \_\ \ \_\  \ \_____\  \ \_____\  \ \_\ \_\  \ \_\\"\_\  \ \_____\ 
    \/_/   \/_/\/_/   \/_/  \/_/   \/_____/   \/_____/   \/_/\/_/   \/_/ \/_/   \/_____/ 

```

*Tamelang* is an embedded DSL for Python to define programs in other programming language.
Tamelang is a metalanguage backed by a clean, typed API to define an object-oriented model
of a program, which can then be transpiled/compiled to a supported target language.

Tamelang is designed with the following goals in mind:

- Use Python as a host language to define programs and meta-programs. Similar to Lisp,
  or Zig's `comptime`, there is little difference between code and code-generating code.


## References

Tamelang is the spiritual successor to [λ-factory](https://github.com/sebastien/lambdafactory),
a toolkit to easily plug syntactic front-ends with transpiling backends.
