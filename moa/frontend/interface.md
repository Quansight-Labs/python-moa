# Abstract Syntax Tree (AST) Interface

Inspired by lisp all the AST is a simple tuples of tuples

## Arrays

`(type, shape, name, data)`

 - type: int
 - shape: tuple[int]
 - name: None, str
 - data: None, tuple[float], tuple[int]
 
# Unary Operations

`(type, shape, right_node)`

 - type: int
 - shape: tuple[int]
 - right_node: tuple

## Binary Operations

`(type, shape, left_node, right_node)`

 - type: int
 - shape: tuple[int]
 - left_node: tuple
 - right_node: tuple

