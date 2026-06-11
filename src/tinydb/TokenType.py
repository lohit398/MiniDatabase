"""
Token type definitions for the MiniDatabase SQL tokenizer.

Import in the scanner as:
    from .TokenType import TokenType, KEYWORDS
"""

from enum import Enum, auto

class Token:
    def __init__(self,type,lexeme,literal,line,column):
        self.type = type
        self.lexeme = lexeme
        self.literal = literal
        self.line = line
        self.column = column
    def __repr__(self):
        return f"Type: {self.type.name}, lexeme: {self.lexeme} at Line#{self.line},column: {self.column}"



class TokenType(Enum):
    # ── Punctuation ─────────────────────────────
    LPAREN = auto()      # (
    RPAREN = auto()      # )
    COMMA = auto()       # ,
    SEMICOLON = auto()   # ;
    DOT = auto()         # .  (e.g. users.name)

    # ── Arithmetic / Concat ─────────────────────
    PLUS = auto()        # +
    MINUS = auto()       # -
    STAR = auto()        # *   (also serves as SELECT *)
    SLASH = auto()       # /
    CONCAT = auto()      # ||  (SQL string concatenation)

    # ── Comparison ──────────────────────────────
    EQ = auto()          # =       (SQL equality, single =)
    NEQ = auto()         # !=  or  <>
    LT = auto()          # <
    LTE = auto()         # <=
    GT = auto()          # >
    GTE = auto()         # >=

    # ── Literals & identifiers ──────────────────
    IDENTIFIER = auto()  # column names, table names, aliases
    STRING = auto()      # 'hello world'
    NUMBER = auto()      # 42, 3.14

    # ── Keywords (case-insensitive — see KEYWORDS map below) ──
    KW_SELECT = auto()
    KW_FROM = auto()
    KW_WHERE = auto()
    KW_AND = auto()
    KW_OR = auto()
    KW_NOT = auto()
    KW_AS = auto()
    KW_JOIN = auto()
    KW_ON = auto()
    KW_INNER = auto()
    KW_LEFT = auto()
    KW_RIGHT = auto()
    KW_NULL = auto()
    KW_TRUE = auto()
    KW_FALSE = auto()
    KW_IN = auto()
    KW_IS = auto()

    # ── Sentinel ────────────────────────────────
    EOF = auto()


# Lowercased keyword text → TokenType.
# In the scanner: after consuming an identifier-shaped lexeme, lowercase it
# and look it up here. If found → emit that keyword token. If not → IDENTIFIER.
KEYWORDS = {
    "select": TokenType.KW_SELECT,
    "from":   TokenType.KW_FROM,
    "where":  TokenType.KW_WHERE,
    "and":    TokenType.KW_AND,
    "or":     TokenType.KW_OR,
    "not":    TokenType.KW_NOT,
    "as":     TokenType.KW_AS,
    "join":   TokenType.KW_JOIN,
    "on":     TokenType.KW_ON,
    "inner":  TokenType.KW_INNER,
    "left":   TokenType.KW_LEFT,
    "right":  TokenType.KW_RIGHT,
    "null":   TokenType.KW_NULL,
    "true":   TokenType.KW_TRUE,
    "false":  TokenType.KW_FALSE,
    "in":     TokenType.KW_IN,
    "is":     TokenType.KW_IS,
}
