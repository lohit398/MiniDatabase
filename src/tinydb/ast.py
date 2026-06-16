from dataclasses import dataclass
from typing import Optional
from tinydb.TokenType import Token

@dataclass
class Expr:
    pass

@dataclass
class Column:
    token:Token

@dataclass
class Table:
    name:str
    line:int
    col:int
    alias: str

@dataclass
class SelectStmt:
    columns: list[Column]
    table: Table
    line:int
    col: int
    where: Optional[Expr]

@dataclass
class BinaryExpr(Expr):
    opr: str
    left: Expr
    right : Expr

@dataclass
class Identifier(Expr):
    name: str
    line: int
    col: int

@dataclass
class Literal(Expr):
    value: (str | int | float)
    line: int
    col: int