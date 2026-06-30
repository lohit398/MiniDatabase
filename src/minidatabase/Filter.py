from minidatabase.Operator import Operator
from minidatabase.SeqScan import SeqScan
from minidatabase.ast import Expr
from minidatabase.ast import BinaryExpr
from minidatabase.ast import Literal
from minidatabase.ast import Identifier

class ParseError:
    pass

class Filter(Operator):
    def __init__(self,expr:Expr,file_path):
        self.Expr = expr

    def isOperator(self,val:str):
        if(">" == val or ">=" == val or "<" == val or  "<=" == val or "=" == val or "!=" == val or "<>" == val):
            return True
        elif("+" == val or "*" == val or "/" == val or "-" == val):
            return True
        elif("and" == val or "or" == val):
            return True 
        else:
            return False

    def walkExprTree(self,node,row):
        if(isinstance(node,BinaryExpr)):
            leftVal = self.walkExprTree(node.left,row)
            rightVal = self.walkExprTree(node.right,row)
            return eval(f"{leftVal}{node.opr}{rightVal}")
        elif (isinstance(node,Literal)):
            return node.literal
        elif (isinstance(node,Identifier)):
            if(node.name in row):
                return row[node.name]
            else:
                raise ParseError(f"Unexpected Identifier")
        else:
            raise ParseError(f"Unexpected Identifier")
            


    def open(self):
        pass