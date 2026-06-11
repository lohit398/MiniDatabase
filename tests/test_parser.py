import pytest

from tinydb.Tokenizer import Tokenizer
from tinydb.TokenType import TokenType
from tinydb.Parser import ParseError, Parser

def test_parser_star():
    t = Tokenizer()
    t.input = "SELECT* FROM users"
    t.scan()
    tokens = t.tokens
    p = Parser(tokens)
    sst = p.parse()

    assert sst.columns[0].token.type == TokenType.STAR
    assert sst.table.name == "users"

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
   
    




