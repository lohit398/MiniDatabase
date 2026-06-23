from minidatabase.Tokenizer import Tokenizer
from minidatabase.TokenType import TokenType


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
    t2.input = "SELECT * FROM users WHERE (id <> 1AND name = 'Lohit')"
    t2.scan()
    types = [tok.type for tok in t2.tokens]
    assert types == [
        TokenType.KW_SELECT,
        TokenType.STAR,
        TokenType.KW_FROM,
        TokenType.IDENTIFIER,
        TokenType.KW_WHERE,
        TokenType.LPAREN,
        TokenType.IDENTIFIER,
        TokenType.NEQ,
        TokenType.NUMBER,
        TokenType.KW_AND,
        TokenType.IDENTIFIER,
        TokenType.EQ,
        TokenType.STRING,
        TokenType.RPAREN,
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
    t2.input = "SELECT * FROM users WHERE name = 'Lohit' AND id != 1"
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
        TokenType.NEQ,
        TokenType.NUMBER,
        TokenType.EOF
    ]

def test_select_floating_pt_number():
    t1 = Tokenizer()
    t1.input = "SELECT id,percentage FROM users where percentage >= 94.56123 AND id < 20 AND asd <= 21"
    t1.scan()
    types = [tok.type for tok in t1.tokens]
    assert types == [
        TokenType.KW_SELECT,
        TokenType.IDENTIFIER,
        TokenType.COMMA,
        TokenType.IDENTIFIER,
        TokenType.KW_FROM,
        TokenType.IDENTIFIER,
        TokenType.KW_WHERE,
        TokenType.IDENTIFIER,
        TokenType.GTE,
        TokenType.NUMBER,
        TokenType.KW_AND,
        TokenType.IDENTIFIER,
        TokenType.LT,
        TokenType.NUMBER,
        TokenType.KW_AND,
        TokenType.IDENTIFIER,
        TokenType.LTE,
        TokenType.NUMBER,
        TokenType.EOF
    ]

def test_select_floating_pt_number_error():
    t1 = Tokenizer()
    t1.input = "SELECT id,percentage FROM users where percentage > 4.56.1"
    t1.scan()
    types = [tok.type for tok in t1.tokens]
    assert len(t1.errors) > 0


def test_select_multi_line_query():
    t1 = Tokenizer()
    t1.input = """SELECT id,percentage FROM users
    where percentage > 65.78"""
    t1.scan()
    types = [tok.type for tok in t1.tokens]
    assert types == [
        TokenType.KW_SELECT,
        TokenType.IDENTIFIER,
        TokenType.COMMA,
        TokenType.IDENTIFIER,
        TokenType.KW_FROM,
        TokenType.IDENTIFIER,
        TokenType.KW_WHERE,
        TokenType.IDENTIFIER,
        TokenType.GT,
        TokenType.NUMBER,
        TokenType.EOF
    ]


def test_empty_query():
    t = Tokenizer()
    t.input = ""
    t.scan()
    types = [tok.type for tok in t.tokens]
    assert types == []

def test_concat():
    t = Tokenizer()
    t.input = "SELECT a_col||b_col from cols"
    t.scan()
    types = [tok.type for tok in t.tokens]
    assert types == [TokenType.KW_SELECT,TokenType.IDENTIFIER,TokenType.CONCAT,TokenType.IDENTIFIER,TokenType.KW_FROM,TokenType.IDENTIFIER,TokenType.EOF]

def test_concat_error():
    t = Tokenizer()
    t.input = "SELECT a_col|b_col from cols"
    t.scan()
    types = [tok.type for tok in t.tokens]
    assert len(t.errors) > 0

def test_NEQ_error():
    t = Tokenizer()
    t.input = "SELECT id from cols WHERE id ! 1"
    t.scan()
    types = [tok.type for tok in t.tokens]
    assert len(t.errors) > 0

def test_number_ending():
    t = Tokenizer()
    t.input = "SELECT * from cols WHERE id = 1"
    t.scan()
    types = [tok.type for tok in t.tokens]
    assert types == [
        TokenType.KW_SELECT,
        TokenType.STAR,
        TokenType.KW_FROM,
        TokenType.IDENTIFIER,
        TokenType.KW_WHERE,
        TokenType.IDENTIFIER,
        TokenType.EQ,
        TokenType.NUMBER,
        TokenType.EOF
    ]

def test_ft_ending():
    t = Tokenizer()
    t.input = "SELECT * from cols WHERE id > 52.90897"
    t.scan()
    types = [tok.type for tok in t.tokens]
    assert types == [
        TokenType.KW_SELECT,
        TokenType.STAR,
        TokenType.KW_FROM,
        TokenType.IDENTIFIER,
        TokenType.KW_WHERE,
        TokenType.IDENTIFIER,
        TokenType.GT,
        TokenType.NUMBER,
        TokenType.EOF
    ]

def test_pos():
    t = Tokenizer()
    t.input = "SELECT * from cols WHERE id > 52.90897"
    t.scan()
    types = [tok.type for tok in t.tokens]
    t.pos = 120
    assert t.advance() == None
    assert t.peek() == "\0"


def test_plus():
    t = Tokenizer()
    t.input = "SELECT * from cols WHERE id+x > 52.90897 OR id-x < 40.82"
    t.scan()
    types = [tok.type for tok in t.tokens]
    assert types == [
        TokenType.KW_SELECT,
        TokenType.STAR,
        TokenType.KW_FROM,
        TokenType.IDENTIFIER,
        TokenType.KW_WHERE,
        TokenType.IDENTIFIER,
        TokenType.PLUS,
        TokenType.IDENTIFIER,
        TokenType.GT,
        TokenType.NUMBER,
        TokenType.KW_OR,
        TokenType.IDENTIFIER,
        TokenType.MINUS,
        TokenType.IDENTIFIER,
        TokenType.LT,
        TokenType.NUMBER,
        TokenType.EOF
    ]