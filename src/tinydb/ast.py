from dataclasses import dataclass
from tinydb.TokenType import Token

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


