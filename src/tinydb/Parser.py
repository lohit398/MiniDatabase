from tinydb.TokenType import Token
from tinydb.TokenType import TokenType
from tinydb.ast import SelectStmt
from tinydb.ast import Column
from tinydb.ast import Table


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
        
        
    def parseSelectStmt(self):
        sst = self.consume(TokenType.KW_SELECT)
        cols = self.matchColumn()
        self.consume(TokenType.KW_FROM)
        table = self.consume(TokenType.IDENTIFIER)
        self.consume(TokenType.EOF)
        tt = Table(table.lexeme,table.line,table.column,None)
        selectStatement = SelectStmt(cols,tt,sst.line,sst.column)
        return selectStatement

        
    def parse(self):
        if(self.peek().type == TokenType.KW_SELECT):
            return self.parseSelectStmt()
        

                

