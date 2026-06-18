import pytest

from tinydb.Tokenizer import Tokenizer
from tinydb.TokenType import TokenType
from tinydb.Parser import ParseError, Parser
from tinydb.ast import BinaryExpr, Identifier,Literal

def test_parser_star():
    t = Tokenizer()
    t.input = "SELECT* FROM users"
    t.scan()
    tokens = t.tokens
    p = Parser(tokens)
    sst = p.parse()

    assert sst.columns[0].token.type == TokenType.STAR
    assert sst.table.name == "users"

def test_parser_star_where():
    t = Tokenizer()
    t.input = "SELECT* FROM users where x = 5"
    t.scan()
    tokens = t.tokens
    p = Parser(tokens)
    sst = p.parse()

    assert sst.where != None

def test_parser_star_where_rev():
    t = Tokenizer()
    t.input = "SELECT* FROM users where 5 = x"
    t.scan()
    tokens = t.tokens
    p = Parser(tokens)
    sst = p.parse()
    l = Literal(5,1,25)
    i = Identifier("x",1,29)
    assert sst.where.opr == "="
    assert sst.where.left == l


def test_parser_star_where_GT():
    t = Tokenizer()
    t.input = "SELECT* FROM users where x > 5"
    t.scan()
    tokens = t.tokens
    p = Parser(tokens)
    sst = p.parse()

    assert sst.where != None
    assert sst.where.opr == ">";


def test_parser_star_where_AND():
    t = Tokenizer()
    t.input = "SELECT* FROM users where x <> 5 and x = 10"
    t.scan()
    tokens = t.tokens
    p = Parser(tokens)
    sst = p.parse()

    assert sst.where != None
    assert sst.where.opr == "and"
    assert sst.where.left != None
    assert sst.where.left.left.name == "x"
    assert sst.where.left.right.value == 5
    assert sst.where.left.opr == "<>"
    assert sst.where.right.left.name == "x"
    assert sst.where.right.right.value == 10
    assert sst.where.right.opr == "="


def test_parser_star_where_AND_OR():
    t = Tokenizer()
    t.input = "SELECT* FROM users where x <> 5 AND x <> 10 or x > 15"
    t.scan()
    tokens = t.tokens
    p = Parser(tokens)
    sst = p.parse()

    assert sst.where != None
    assert sst.where.opr == "or"
    assert sst.where.left != None
    assert sst.where.left.opr == "and"
    assert sst.where.left.left.left.name == "x"
    assert sst.where.left.left.right.value == 5
    assert sst.where.left.left.opr == "<>"
    

def test_parser_star_where_NEQ():
    t = Tokenizer()
    t.input = "SELECT* FROM users where x <> 5"
    t.scan()
    tokens = t.tokens
    p = Parser(tokens)
    sst = p.parse()

    assert sst.where != None
    assert sst.where.opr == "<>";


def test_parser_star_where_NEQ1():
    t = Tokenizer()
    t.input = "SELECT* FROM users where x != 5"
    t.scan()
    tokens = t.tokens
    p = Parser(tokens)
    sst = p.parse()

    assert sst.where != None
    assert sst.where.opr == "!=";



def test_parser_col_list():
    t = Tokenizer()
    t.input = "SELECT id,name,dob,Username FROM users"
    t.scan()
    tokens = t.tokens
    p = Parser(tokens)
    sst = p.parse()

    assert sst.columns[0].token.type == TokenType.IDENTIFIER
    assert sst.columns[0].token.lexeme == "id"
    assert sst.columns[1].token.type == TokenType.IDENTIFIER
    assert sst.columns[1].token.lexeme == "name"
    assert sst.columns[3].token.type == TokenType.IDENTIFIER
    assert sst.columns[3].token.lexeme == "Username"
    assert sst.table.name == "users"

def test_parser_error_no_col():
    t = Tokenizer()
    t.input = "SELECT FROM Users"
    t.scan()
    tokens = t.tokens
    p = Parser(tokens)
    #sst = p.parse()
    with pytest.raises(ParseError, match="Unexpected TokenType.KW_FROM"):
        p.parse()


def test_parser_error_star_cold():
    t = Tokenizer()
    t.input = "SELECT *,id FROM Users"
    t.scan()
    tokens = t.tokens
    p = Parser(tokens)
    #sst = p.parse()
    with pytest.raises(ParseError, match="Expected KW_FROM*"):
        p.parse()
   
    




