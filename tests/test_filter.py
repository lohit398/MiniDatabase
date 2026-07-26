from minidatabase.Filter import Filter
from minidatabase.ast import BinaryExpr
from minidatabase.ast import Identifier
from minidatabase.ast import Literal
from minidatabase.SeqScan import SeqScan

def test_comparision():
    expr = BinaryExpr('>',Identifier('age',-1,-1),Literal(30,-1,-1))
    sq = SeqScan('/home/lohit/Desktop/MiniDatabase/tests/fixtures/users.csv')
    f = Filter(expr,sq)
    f.open()
    count = 0
    while f.next() != None:
        count+=1

    assert count == 2


def test_comparision_or():
    
    expr1 = BinaryExpr('=',Identifier('name',-1,-1),Literal('Alice',-1,-1))
    expr2 = BinaryExpr('>',Identifier('age',-1,-1),Literal(30,-1,-1))
    parentExpr = BinaryExpr('or',expr2,expr1)
    sq = SeqScan('/home/lohit/Desktop/MiniDatabase/tests/fixtures/users.csv')
    f = Filter(parentExpr,sq)
    f.open()
    count = 0
    while f.next() != None:
        count+=1

    assert count == 4


def test_comparision_and():
    
    expr1 = BinaryExpr('=',Identifier('name',-1,-1),Literal('Alice',-1,-1))
    expr2 = BinaryExpr('>',Identifier('age',-1,-1),Literal(30,-1,-1))
    parentExpr = BinaryExpr('and',expr2,expr1)
    sq = SeqScan('/home/lohit/Desktop/MiniDatabase/tests/fixtures/users.csv')
    f = Filter(parentExpr,sq)
    f.open()
    count = 0
    while f.next() != None:
        count+=1

    assert count == 0


def test_comparision_or_rev():
    
    expr1 = BinaryExpr('=',Identifier('name',-1,-1),Literal('Alice',-1,-1))
    expr2 = BinaryExpr('>',Identifier('age',-1,-1),Literal(30,-1,-1))
    parentExpr = BinaryExpr('or',expr1,expr2)
    sq = SeqScan('/home/lohit/Desktop/MiniDatabase/tests/fixtures/users.csv')
    f = Filter(parentExpr,sq)
    f.open()
    count = 0
    while f.next() != None:
        count+=1

    assert count == 4
