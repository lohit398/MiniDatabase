from tinydb.TokenType import Token
from tinydb.TokenType import TokenType
from tinydb.ast import SelectStmt
from tinydb.ast import Column
from tinydb.ast import Table
from tinydb.ast import Identifier
from tinydb.ast import Literal
from tinydb.ast import BinaryExpr
from tinydb.ast import Expr


class ParseError(Exception):
    pass

class Parser:
    def __init__(self,tokens:list[Token]):
        self.tokens = tokens
        self.pos = 0

    def peek(self):
        if(self.pos >= len(self.tokens)):
            return
        return self.tokens[self.pos]

    def advance(self):
        if(self.pos >= len(self.tokens)):
            return
        t = self.tokens[self.pos]
        self.pos+=1
        return t
    
    def match(self,type):
        if(self.pos >= len(self.tokens)):
            return
        t= self.peek()
        if(t.type != type):
            return False
        self.advance()
        return True

    def consume(self,type):
        if(self.pos >= len(self.tokens)):
            return
        t = self.peek()
        if(not self.match(type)):
            raise ParseError(f"Expected {type.name}, got {t.type.name} at line {t.line}, col {t.column}")
        return t
    
    def parseColumnList(self):
        cols = []
        cols.append(Column(self.consume(TokenType.IDENTIFIER)))
        while self.match(TokenType.COMMA):
            cols.append(Column(self.consume(TokenType.IDENTIFIER)))
        return cols

    def matchColumn(self):
        t = self.peek()
        cols = []

        match t.type:
            case TokenType.STAR:
                self.consume(TokenType.STAR)
                cols.append(Column(t))
            case TokenType.IDENTIFIER:
                cols = self.parseColumnList()
            case _:
                raise ParseError(f"Unexpected {t.type}")

        return cols
        
    def where_clause(self):
        t = self.peek()
        match t.type:
            case TokenType.EOF:
                self.consume(TokenType.EOF)
                return None
            case TokenType.KW_WHERE:
                self.consume(TokenType.KW_WHERE)
                return self.parse_where_clause()
    
    def parseOperand(self):
        t = self.peek()
        match t.type:
            case TokenType.IDENTIFIER:
                return t.lexeme
            case TokenType.STRING | TokenType.NUMBER:
                return t.literal

    def parse_where_clause(self):
        left  = self.parseOperand()
        self.consume(TokenType.EQ)
        right = self.parseOperand()
        br = BinaryExpr("=",left,right)
        return br

        
    
    def parseSelectStmt(self):
        sst = self.consume(TokenType.KW_SELECT)
        cols = self.matchColumn()
        self.consume(TokenType.KW_FROM)
        table = self.consume(TokenType.IDENTIFIER)
       
        tt = Table(table.lexeme,table.line,table.column,None)
        where = self.where_clause()
        selectStatement = SelectStmt(cols,tt,sst.line,sst.column,where)
        return selectStatement

        
    def parse(self):
        if(self.peek().type == TokenType.KW_SELECT):
            return self.parseSelectStmt()
        

                

