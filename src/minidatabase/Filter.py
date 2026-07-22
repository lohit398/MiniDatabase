from minidatabase.Operator import Operator
from minidatabase.SeqScan import SeqScan
from minidatabase.ast import Expr
from minidatabase.ast import BinaryExpr
from minidatabase.ast import Literal
from minidatabase.ast import Identifier

class ParseError(Exception):
    pass

class ExpressionCantBeParsed(Exception):
    pass

class InvalidOperation(Exception):
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
    
    def typeCast(self,val,eVal):
        try:
            if(eVal == int):
                return int(val)
            elif(eVal == float):
                return float(val)
            elif(eVal == str):
                return val
            else:
                raise ParseError(f"Unknown Type!")
        except ParseError:
            raise ParseError(f"Unknown Type {eVal}")
        except:
            raise ParseError(f"Value {val} can not be typecasted to {eVal}")
            

        
    def compare(self,a,b,opr):
        if(self.isOperator(opr)):
            if(a['type'] == 'UNKNOWN' and b['type'] == 'UNKNOWN'):
                raise ExpressionCantBeParsed(f"Expression can not be parsed right now: {a}{opr}{b}")
            
            eVal = a['type'] if a['type'] != 'UNKNOWN' else b['type'] #expected values from cols
            
            match opr:
                case '>':
                    return self.typeCast(a['val'],eVal) > self.typeCast(b['val'],eVal)
                case '>=':
                    return self.typeCast(a['val'],eVal) >= self.typeCast(b['val'],eVal)
                case '=':
                    return self.typeCast(a['val'],eVal) == self.typeCast(b['val'],eVal)
                case '<':
                    return self.typeCast(a['val'],eVal) < self.typeCast(b['val'],eVal)
                case '<=':
                    return self.typeCast(a['val'],eVal) <= self.typeCast(b['val'],eVal)
                case '<>':
                    return self.typeCast(a['val'],eVal) != self.typeCast(b['val'],eVal)
                case "!=":
                    return self.typeCast(a['val'],eVal) != self.typeCast(b['val'],eVal)
                case _:
                    raise InvalidOperation(f'Invalid Operation on :{a['val']}{opr}{b['val']}')
        else:
            raise ParseError(f"Unidentified Operator: {opr}")

    def logicalOperator(self,a,b,opr):
        if(not(opr == 'and' or opr == 'or')):
            raise InvalidOperation(f'Invalid Operation on :{a['val']}{opr}{b['val']}')
        elif(not(type(a) is bool and type(b) is bool)):
            raise ExpressionCantBeParsed(f'Logical Operator can not be applied on these values {a}{b}')

        match opr:
            case "and":
                return a and b
            case 'or':
                return a or b            

    def walkExprTree(self,node,row):
        if(isinstance(node,BinaryExpr)):
            leftVal = self.walkExprTree(node.left,row)
            rightVal = self.walkExprTree(node.right,row)
            if(node.opr == 'and' or node.opr == 'or'):
                return self.logicalOperator(leftVal,rightVal,node.opr)  
            return self.compare(leftVal,rightVal,node.opr)
        elif (isinstance(node,Literal)):
            if(type(node.value) == float):
                return {'val' : node.value,'type': float}
            elif(type(node.value) == str):
                return {'val' : node.value,'type': str}
            elif(type(node.value) == int):
                return {'val' : node.value,'type': int}
            else:
                raise ParseError(f"Unexpected Literal: {node.value}")
            
        elif (isinstance(node,Identifier)):
            if(node.name in row):
                return {'val':row[node.name], 'type':'UNKNOWN'}
            else:
                raise ParseError(f"Unexpected Identifier")
        else:
            raise ParseError(f"Unexpected Identifier")
            


    def open(self):
        pass