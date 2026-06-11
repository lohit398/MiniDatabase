import sys
from tinydb.TokenType import TokenType, KEYWORDS, Token

class Tokenizer:
    def __init__(self):
        self.tokens = []
        self.input = ""
        self.line = 0
        self.column = 0
        self.errors = []
        self.index = 0

    def readQuery(self):
        print("Enter CTRL + D to finish")
        self.input = sys.stdin.read()
        #self.input = self.input.lower()
        print("QUERY to be parsed: "+self.input)
    
    def addToken(self,t):
        self.tokens.append(t)
    

    def checkKeywordsAndIdentifiers(self,curr,cc):
        if(curr in KEYWORDS):
            self.addToken(Token(KEYWORDS[curr],f"{cc}",f"{curr}",self.line,self.column))
        else:
            self.addToken(Token(TokenType.IDENTIFIER,f"{cc}",f"{curr}",self.line,self.column))
        
    
    def number(self): 
        curr = ""
        dotCount = 0
        l = self.line
        col = self.column
        for i in range(self.index,len(self.input) + 1):

            if(self.peek().isdigit()):
                curr+=self.input[i]
            elif (self.peek() == "." and dotCount == 0):
                curr+="."
                dotCount = 1
            elif (self.peek() == "." and dotCount == 1):
                self.errors.append(f"Invalid Number at: Line {l}, Column {col}")
                return True
            else:
                if(dotCount == 0):
                    self.addToken(Token(TokenType.NUMBER,f"{curr}",int(curr),l,col))
                else:
                    self.addToken(Token(TokenType.NUMBER,f"{curr}",float(curr),l,col))
                break
            
            if(i == len(self.input)):
                if(dotCount == 0):
                    self.addToken(Token(TokenType.NUMBER,f"{curr}",int(curr),l,col))
                else:
                    self.addToken(Token(TokenType.NUMBER,f"{curr}",float(curr),l,col))
                break
            self.advance()

        return False
            
    def string(self):
        curr = ""
        l = self.line
        col = self.column
        for i in range(self.index+1,len(self.input) + 1):
            
            if(self.peek() == "'"):
                self.addToken(Token(TokenType.STRING,"'"+curr+"'",f"{curr}",l,col))
                self.advance()
                break
            if(i == len(self.input)):
                self.errors.append(f"Unterminated String: Line {self.line} Column {self.column}")
                return True
                break
            curr+=self.peek()
            self.advance()
        return False
    
    def advance(self):
        if(self.index >= len(self.input)):
            return
        
        char = self.input[self.index]
        self.index+=1
        if(char == "\n"): #advance line number
            self.line+=1
            self.column = 0
        else:
            self.column+=1
        return char
    
    def peek(self):
        if self.index >= len(self.input):
            return "\0"
        return self.input[self.index]
        
        
    def scan(self):
        if(self.input == ""):
            return
        
        # [a-zA-Z0-9_] -> continue the string else it is the next lexeme that we need to move to
        # or if it is a white space, we will need to skip it and start the next lexeme

        curr = ""
        cc = ""
        self.line = 1
        self.column = 0
        self.index = 0
        while(self.index < len(self.input) + 1):
            # check for spaces and change of shapes and pass curr to check
            if(self.index == len(self.input)):
                if(curr != ""):
                    res = self.checkKeywordsAndIdentifiers(curr,cc)
                    curr = ""
                    cc = ""
                self.index+=1
                continue

            char = self.peek()

            if((ord(char.lower()) >= 97 and ord(char.lower()) <= 122) or (ord(char) >= 48 and ord(char) <= 57 and len(curr) != 0) or ord(char) == 95):
                cc+=char
                curr+=char.lower()
                self.advance()
                continue
            elif(char == " "):
                if(curr != ""):
                    res = self.checkKeywordsAndIdentifiers(curr,cc)
                cc = ""
                curr = ""
                self.advance()
                continue

            if(curr != ""): # change of lexeme type
                res = self.checkKeywordsAndIdentifiers(curr,cc)
                curr = ""
                cc = ""


            if(char == "'"):
                self.advance()
                hasError = self.string()
                if(hasError):
                    break
                continue

            elif(char.isdigit()):
                hasError = self.number()
                if(hasError):
                    break
                continue

            match char:
                case "(": 
                    self.addToken(Token(TokenType.LPAREN,"(",None,self.line,self.column))
                case ")": 
                    self.addToken(Token(TokenType.RPAREN,")",None,self.line,self.column))
                case ",": 
                    self.addToken(Token(TokenType.COMMA,",",None,self.line,self.column))
                case ";": 
                    self.addToken(Token(TokenType.SEMICOLON,";",None,self.line,self.column))
                case ".": 
                    self.addToken(Token(TokenType.DOT,".",None,self.line,self.column))
                case "+": 
                    self.addToken(Token(TokenType.PLUS,"+",None,self.line,self.column))
                case "-": 
                    self.addToken(Token(TokenType.MINUS,"-",None,self.line,self.column))
                case "*": 
                    self.addToken(Token(TokenType.STAR,"*", None, self.line,self.column))
                case "/": 
                    self.addToken(Token(TokenType.SLASH,"/",None,self.line,self.column))
                case "|": 
                    self.advance()
                    if(self.peek() == "|"):
                        self.addToken(Token(TokenType.CONCAT,"||",None,self.line,self.column))
                    else:
                        #print("Invalid Character at ")
                        self.errors.append(f"Invalid Character: Line {self.line} at column {self.column}")
                        break
                case "=": 
                    self.addToken(Token(TokenType.EQ,"=",None,self.line,self.column))
                case ">":
                    self.advance()
                    if(self.peek() == "="):
                        self.addToken(Token(TokenType.GTE,">=",None,self.line,self.column))
                    else:
                        self.addToken(Token(TokenType.GT,">",None,self.line,self.column))
                case "<":
                    self.advance()
                    if(self.peek() == ">"):
                        self.addToken(Token(TokenType.NEQ,"<>",None,self.line,self.column))
                    elif(self.peek() == "="):
                        self.addToken(Token(TokenType.LTE,"<=",None,self.line,self.column))
                    else:
                        self.addToken(Token(TokenType.LT,"<",None,self.line,self.column))
            self.advance()
        self.tokens.append(Token(TokenType.EOF,"EOF",None,self.line,self.column))
            
            

# Remove this
# t = Tokenizer()
# t.readQuery()
# t.scan()