from tinydb.Tokenizer import Tokenizer
from tinydb.TokenType import TokenType


def test_select_star():
    t = Tokenizer()
    t.input = "SELECT * FROM users"
    t.scan()
    types = [tok.type for tok in t.tokens]
    assert types == [
        TokenType.KW_SELECT,
        TokenType.STAR,
        TokenType.KW_FROM,
        TokenType.IDENTIFIER,
        TokenType.EOF
    ]

def test_select_star_no_space():
    t1 = Tokenizer()
    t1.input = "SELECT* FROM users"
    t1.scan()
    types = [tok.type for tok in t1.tokens]
    assert types == [
        TokenType.KW_SELECT,
        TokenType.STAR,
        TokenType.KW_FROM,
        TokenType.IDENTIFIER,
        TokenType.EOF
    ]

def test_select_star_filters():
    t2 = Tokenizer()
    t2.input = "SELECT * FROM users WHERE id = 1AND name = 'Lohit'"
    t2.scan()
    types = [tok.type for tok in t2.tokens]
    assert types == [
        TokenType.KW_SELECT,
        TokenType.STAR,
        TokenType.KW_FROM,
        TokenType.IDENTIFIER,
        TokenType.KW_WHERE,
        TokenType.IDENTIFIER,
        TokenType.EQ,
        TokenType.NUMBER,
        TokenType.KW_AND,
        TokenType.IDENTIFIER,
        TokenType.EQ,
        TokenType.STRING,
        TokenType.EOF
    ]


def test_unterminated_string_error():
    t2 = Tokenizer()
    t2.input = "SELECT * FROM users WHERE id = 1AND name = 'Lohit"
    t2.scan()
    errors = [tok for tok in t2.errors]
    assert len(errors)>0

def test_string():
    t2 = Tokenizer()
    t2.input = "SELECT * FROM users WHERE name = 'Lohit' AND id = 1"
    t2.scan()
    types = [tok.type for tok in t2.tokens]
    assert types == [
        TokenType.KW_SELECT,
        TokenType.STAR,
        TokenType.KW_FROM,
        TokenType.IDENTIFIER,
        TokenType.KW_WHERE,
        TokenType.IDENTIFIER,
        TokenType.EQ,
        TokenType.STRING,
        TokenType.KW_AND,
        TokenType.IDENTIFIER,
        TokenType.EQ,
        TokenType.NUMBER,
        TokenType.EOF
    ]