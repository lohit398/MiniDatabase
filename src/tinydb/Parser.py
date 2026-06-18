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
                self.consume(t.type)
                return Identifier(t.lexeme,t.line,t.column)
            case TokenType.STRING:
                self.consume(TokenType.STRING)
                return Literal(t.literal,t.line,t.column)
            case TokenType.NUMBER:
                self.consume(TokenType.NUMBER)
                return Literal(t.literal,t.line,t.column)
            case _:
                raise ParseError(f"Unexpected Type: {t.type}")
    
    def parse_operator(self):
        t = self.peek()
        
        match t.type:
            case TokenType.EQ:
                self.consume(TokenType.EQ)
            case TokenType.GT:
                self.consume(TokenType.GT)
            case TokenType.LT:
                self.consume(TokenType.LT)
            case TokenType.GTE:
                self.consume(TokenType.GTE)
            case TokenType.LTE:
                self.consume(TokenType.LTE)
            case TokenType.NEQ:
                self.consume(TokenType.NEQ)
            case _:
                raise ParseError(f"Unexpected Type: {t.type}, expecting an operator")
        return t.lexeme
    

    def isEnd(self):
        if(self.peek().type == TokenType.EOF):
            return True
        return False
    
    def previous(self):
        if(self.pos - 1 >= 0):
            return self.tokens[self.pos-1]
        return None

    def matchTypes(self,types:list):
        for i in types:
            if(self.peek().type == i):
                return True
        return False
    

    def parse_equality(self):
        left  = self.parseOperand()
        opr = self.parse_operator()
        right = self.parseOperand()
        br = BinaryExpr(opr,left,right)
        return br


    def parse_logical_and(self):
        expr = self.parse_equality()

        while self.matchTypes([TokenType.KW_AND]):
            #opr = self.peek().lexeme
            self.consume(self.peek().type)
            r = self.parse_equality()
            expr = BinaryExpr("and",expr,r)
        return expr
    
    def parse_logical_or(self):
        expr = self.parse_logical_and()

        while self.matchTypes([TokenType.KW_OR]):
            #opr = self.peek().lexeme
            self.consume(self.peek().type)
            r = self.parse_logical_and()
            expr = BinaryExpr("or",expr,r)
        return expr


    def parse_where_clause(self):
        return self.parse_logical_or()

        
    
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
        

                

