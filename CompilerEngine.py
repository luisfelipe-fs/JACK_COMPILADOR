from JackTokenizer import JackTokenizer
from Token import Token
from CompilerException import CompilerException
from EOFException import EOFException
from SymbolTable import SymbolTable
from SymbolTable import SymbolTable as st
from VMWriter import VMWriter
from VMWriter import VMWriter as vm
import sys

class CompilerEngine (JackTokenizer):
    B_OPERATOR = ['+', '-', '*', '/', '&', '|', '<', '>', '=']
    U_OPERATOR = ['-', '~']
    KEYWORD_CONSTANT = ['true', 'false', 'null', 'this']
    STATEMENTS = ['let', 'if', 'while', 'do', 'return']
    KEYWORD_TYPE = ['int', 'char', 'boolean']
    KEYWORD_SUBROUTINE = ['constructor', 'function', 'method']
    KEYWORD_CLASS_VAR_TYPE = ['static', 'field']
    TERM_TYPE = [Token.TK_INT, Token.TK_STRING, Token.TK_IDENTIFIER]
    REPLACEMENTS = {'<': '&lt;', '>': '&gt;', '"': '&quot;', '&': '&amp;'}
    
    def __init__ (self, path):
        super().__init__(path)
        self.xml = str()
        self.advance()
        self.st = SymbolTable()
        self.vm = VMWriter(self.path[:-5]+'.vm')
        self.className = str()
        self.labelCounter = 0
        self.currentFunctionName = str()
        self.currentSubroutineType = str()

    def xmlContent (self):
        tokenClass = self.tokenType()
        currentToken = self.getToken()
        if tokenClass != Token.TK_STRING:
            try:
                currentToken = self.REPLACEMENTS[currentToken]
            except KeyError:
                pass
            return currentToken
        else:
            return currentToken[1:-1]

    def generateXML (self):
        with open(self.path+'.xml', 'w+') as f:
            f.write(self.xml)

    def error (self, expected):
        print("\n# On file '%s', got following error:" % self.path, file=sys.stderr)
        fancyExpected = ' or '.join([repr(x) for x in expected]) if isinstance(expected, (tuple, list)) else expected
        print("# Line %s: Expected %s, got '%s'." % (self.getLine()+1, fancyExpected, self.getToken()), file=sys.stderr)
        raise CompilerException("Get out.")

    def eat (self, *types):
        if self.tokenType() not in types:
            self.error(types)
        self.xml += '<%s>%s</%s>\n'%(self.tokenType(), self.xmlContent(), self.tokenType())
        self.advance()

    def cEat (self, token): # Conditional Eat
        if self.getToken().__eq__(token):
            self.eat(self.tokenType())
        else:
            self.error(token)

    def compileTerm (self):
        self.xml += '<term>\n'
        if self.tokenType().__eq__(Token.TK_IDENTIFIER):
            try:
                nextToken = self._tokens[1].token()
            except:
                nextToken = str()
            if nextToken.__eq__('['):
                self.vm.writePush(self.st.kindOf(self.getToken()), self.st.indexOf(self.getToken()))
                self.eat(Token.TK_IDENTIFIER)
                self.cEat('[')
                self.compileExpression()
                self.cEat(']')
                self.vm.writeArithmetic('+')
                self.vm.writePop('pointer', 1)
                self.vm.writePush('that', 0)
            elif nextToken in ['(', '.']:
                self.compileSubroutineCall()
            else:
                self.vm.writePush(self.st.kindOf(self.getToken()), self.st.indexOf(self.getToken()))
                self.eat(Token.TK_IDENTIFIER)
        elif self.getToken().__eq__('('):
            self.cEat('(')
            self.compileExpression()
            self.cEat(')')
        elif self.getToken() in self.U_OPERATOR:
            operator = self.getToken()
            self.eat(Token.TK_SYMBOL)
            self.compileTerm()
            if operator.__eq__('-'):
                self.vm.writeArithmetic('!')
            else:
                self.vm.writeArithmetic(operator)
        elif self.getToken() in self.KEYWORD_CONSTANT:
            if self.getToken().__eq__('this'):
                self.vm.writePush('pointer', 0)
            elif self.getToken().__eq__('true'):
                self.vm.writePush('constant', 0)
                self.vm.writeArithmetic('~')
            else:
                self.vm.writePush('constant', 0)
            self.eat(Token.TK_KEYWORD)
        else:
            if self.tokenType().__eq__(Token.TK_INT):
                self.vm.writePush('constant', self.getToken())
            else:
                self.vm.writePush('constant', len(self.getToken()))
                self.vm.writeCall('String.new', 1)
                for char in self.getToken():
                    self.vm.writePush('constant', ord(char))
                    self.vm.writeCall('String.appendChar', 2)
            self.eat(Token.TK_INT, Token.TK_STRING)
        self.xml += '</term>\n'

    def compileExpression (self):
        self.xml += '<expression>\n'
        self.compileTerm()
        while self.getToken() in self.B_OPERATOR:
            operator = self.getToken()
            self.eat(Token.TK_SYMBOL)
            self.compileTerm()
            if operator in vm.ARITHMETIC:
                self.vm.writeArithmetic(operator)
            elif operator.__eq__('*'):
                self.vm.writeCall('Math.multiply', 2)
            elif operator.__eq__(r'/'):
                self.vm.writeCall('Math.divide', 2)
        self.xml += '</expression>\n'

    def compileExpressionList (self):
        self.xml += '<expressionList>\n'
        nArgs = 0
        if self.tokenType() in self.TERM_TYPE or self.getToken() in self.KEYWORD_CONSTANT or self.getToken().__eq__('('):
            nArgs += 1
            self.compileExpression()
            while self.getToken().__eq__(','):
                nArgs += 1
                self.eat(Token.TK_SYMBOL)
                self.compileExpression()
        self.xml += '</expressionList>\n'
        return nArgs

    def compileSubroutineCall (self):
        owner = self.getToken()
        self.eat(Token.TK_IDENTIFIER)
        if self.getToken().__eq__('.'):
            self.eat(Token.TK_SYMBOL)
            method = self.getToken()
            try:
                ownerIndex = self.st.indexOf(owner)
            except CompilerException:
                ownerIndex = -1
            if ownerIndex != -1:
                nArgs = 1
                self.vm.writePush(self.st.kindOf(owner), ownerIndex)
            else:
                nArgs = 0
            self.eat(Token.TK_IDENTIFIER)
            self.cEat('(')
            nArgs += self.compileExpressionList()
            self.cEat(')')
            if ownerIndex != -1:
                self.vm.writeCall('%s.%s' % (self.st.typeOf(owner), method), nArgs)
            else:
                self.vm.writeCall('%s.%s' % (owner, method), nArgs)
        elif self.getToken().__eq__('('):
            self.cEat('(')
            self.vm.writePush('pointer', 0)
            nArgs = self.compileExpressionList()
            self.cEat(')')
            self.vm.writeCall('%s.%s' % (self.className, owner), nArgs+1)

    def compileStatements (self):
        self.xml += '<statements>\n'
        while self.getToken() in self.STATEMENTS:
            if self.getToken().__eq__('let'):
                self.compileLet()
            elif self.getToken().__eq__('if'):
                self.compileIf()
            elif self.getToken().__eq__('while'):
                self.compileWhile()
            elif self.getToken().__eq__('do'):
                self.compileDo()
            elif self.getToken().__eq__('return'):
                self.compileReturn()
        self.xml += '</statements>\n'

    def compileLet (self):
        self.xml += '<letStatement>\n'
        self.cEat('let')
        variable = self.getToken()
        self.eat(Token.TK_IDENTIFIER)
        hasLeftArray = False
        hasRightArray = False
        if self.getToken().__eq__('['):
            hasLeftArray = True
            self.eat(Token.TK_SYMBOL)
            self.vm.writePush(self.st.kindOf(variable), self.st.indexOf(variable))
            self.compileExpression()
            self.vm.writeArithmetic('+')
            self.cEat(']')
            for token in self._tokens:
                if token.token().__eq__('['):
                    hasRightArray = True
                    break
                if token.token().__eq__(';'):
                    break
            if not hasRightArray:
                self.vm.writePop('pointer', 1)
        
        self.cEat('=')
        self.compileExpression()
        if hasRightArray and hasLeftArray:
            self.vm.writePop('temp', 0)
            self.vm.writePop('pointer', 1)
            self.vm.writePush('temp', 0)
            self.vm.writePop('that', 0)
        elif hasLeftArray:
            self.vm.writePop('that', 0)
        else:
            self.vm.writePop(self.st.kindOf(variable), self.st.indexOf(variable))
        self.cEat(';')
        self.xml += '</letStatement>\n'

    def compileIf (self):
        self.xml += '<ifStatement>\n'
        self.cEat('if')
        self.cEat('(')
        self.compileExpression()
        self.vm.writeArithmetic('~')
        self.labelCounter += 2
        thisLabel = self.labelCounter
        self.vm.writeIf('%s.L%d' % (self.className, thisLabel-1))
        self.cEat(')')
        self.cEat('{')
        self.compileStatements()
        self.vm.writeGoto('%s.L%d' % (self.className, thisLabel))
        self.vm.writeLabel('%s.L%d' % (self.className, thisLabel-1))
        self.cEat('}')
        try:
            if self.getToken().__eq__('else'):
                self.eat(Token.TK_KEYWORD)
                self.cEat('{')
                self.compileStatements()
                self.cEat('}')
        except EOFException:
            pass
        self.vm.writeLabel('%s.L%d' % (self.className, thisLabel))
        self.xml += '</ifStatement>\n'

    def compileWhile (self):
        self.xml += '<whileStatement>\n'
        self.cEat('while')
        self.cEat('(')
        self.labelCounter += 2
        thisLabel = self.labelCounter
        self.vm.writeLabel('%s.L%d' % (self.className, thisLabel-1))
        self.compileExpression()
        self.vm.writeArithmetic('~')
        self.vm.writeIf('%s.L%d' % (self.className, thisLabel))
        self.cEat(')')
        self.cEat('{')
        self.compileStatements()
        self.vm.writeGoto('%s.L%d' % (self.className, thisLabel-1))
        self.vm.writeLabel('%s.L%d' % (self.className, thisLabel))
        self.cEat('}')
        self.xml += '</whileStatement>\n'

    def compileDo (self):
        self.xml += '<doStatement>\n'
        self.cEat('do')
        self.compileSubroutineCall()
        self.vm.writePop('temp', 0)
        self.cEat(';')
        self.xml += '</doStatement>\n'

    def compileReturn (self):
        self.xml += '<returnStatement>\n'
        self.cEat('return')
        if self.getToken().__eq__(';'):
            self.vm.writePush('constant', 0)
            self.vm.writeReturn()
            self.eat(Token.TK_SYMBOL)
            self.xml += '</returnStatement>\n'
            return
        self.compileExpression()
        self.vm.writeReturn()
        self.cEat(';')
        self.xml += '</returnStatement>\n'

    def compileType (self):
        if self.getToken() in self.KEYWORD_TYPE:
            self.eat(Token.TK_KEYWORD)
        elif self.tokenType().__eq__(Token.TK_IDENTIFIER):
            self.eat(Token.TK_IDENTIFIER)
        else:
            self.error(self.KEYWORD_TYPE+[Token.TK_IDENTIFIER])

    def compileVarDec (self):
        self.xml += '<varDec>\n'
        self.cEat('var')
        
        if len(self._tokens) >= 2:
            tokenType, tokenIdent = [x.token() for x in self._tokens[0:2]]
        self.compileType()
        self.eat(Token.TK_IDENTIFIER)
        self.st.define(tokenIdent, tokenType, 'local')
        
        while self.getToken().__eq__(','):
            self.eat(Token.TK_SYMBOL)

            tokenIdent = self.getToken()
            self.st.define(tokenIdent, tokenType, 'local')
            self.eat(Token.TK_IDENTIFIER)
        
        self.cEat(';')
        self.xml += '</varDec>\n'

    def compileSubroutineBody (self):
        self.xml += '<subroutineBody>\n'
        self.cEat('{')
        while self.getToken().__eq__('var'):
            self.compileVarDec()
        self.vm.writeFunction('%s.%s' % (self.className, self.currentFunctionName), self.st.varCount('local'))
        if self.currentSubroutineType.__eq__('method'):
            self.vm.writePush('argument', 0)
            self.vm.writePop('pointer', 0)
        elif self.currentSubroutineType.__eq__('constructor'):
            self.vm.writePush('constant', self.st.varCount(st.FIELD))
            self.vm.writeCall('Memory.alloc', 1)
            self.vm.writePop('pointer', 0)
        self.compileStatements()
        self.cEat('}')
        self.xml += '</subroutineBody>\n'

    def compileParameterList (self):
        self.xml += '<parameterList>\n'
        promiseTable = list()
        if self.getToken() in self.KEYWORD_TYPE or self.tokenType().__eq__(Token.TK_IDENTIFIER):
            if len(self._tokens) >= 2:
                tokenType, tokenIdent = [x.token() for x in self._tokens[0:2]]
            self.compileType()
            self.eat(Token.TK_IDENTIFIER)
            self.st.define(tokenIdent, tokenType, 'argument')
            
            while self.getToken().__eq__(','):
                self.eat(Token.TK_SYMBOL)

                if len(self._tokens) >= 2:
                    tokenType, tokenIdent = [x.token() for x in self._tokens[0:2]]
                self.compileType()
                self.eat(Token.TK_IDENTIFIER)
                self.st.define(tokenIdent, tokenType, 'argument')
        self.xml += '</parameterList>\n'

    def compileSubroutineDec (self):
        self.xml += '<subroutineDec>\n'
        if self.getToken() in self.KEYWORD_SUBROUTINE:
            if self.getToken().__eq__('method'):
                self.st.define('this', self.className, 'argument')
            self.currentSubroutineType = self.getToken()
            self.eat(Token.TK_KEYWORD)
        else:
            self.error(self.KEYWORD_SUBROUTINE)
        if self.getToken() in self.KEYWORD_TYPE+['void']:
            self.eat(Token.TK_KEYWORD)
        elif self.tokenType().__eq__(Token.TK_IDENTIFIER):
            self.eat(Token.TK_IDENTIFIER)
        else:
            self.error(self.KEYWORD_TYPE+['void']+Token.TK_IDENTIFIER)
        self.currentFunctionName = self.getToken()
        self.eat(Token.TK_IDENTIFIER)
        self.cEat('(')
        self.compileParameterList()
        self.cEat(')')
        self.compileSubroutineBody()
        self.xml += '</subroutineDec>\n'
    
    def compileClassVarDec (self):
        self.xml += '<classVarDec>\n'

        if self.getToken().__eq__('static'):
            tokenKind = st.STATIC
        elif self.getToken().__eq__('field'):
            tokenKind = st.FIELD
        else:
            self.error(self.KEYWORD_CLASS_VAR_TYPE)
        self.eat(Token.TK_KEYWORD)
        if len(self._tokens) >= 2:
            tokenType, tokenIdent = [x.token() for x in self._tokens[0:2]]
        self.compileType()
        self.eat(Token.TK_IDENTIFIER)
        self.st.define(tokenIdent, tokenType, tokenKind)
        
        while self.getToken().__eq__(','):
            self.eat(Token.TK_SYMBOL)
            
            tokenIdent = self.getToken()
            self.st.define(tokenIdent, tokenType, tokenKind)
            self.eat(Token.TK_IDENTIFIER)
        
        self.cEat(';')
        self.xml += '</classVarDec>\n'

    def compileClass (self):
        self.xml += '<class>\n'
        self.cEat('class')
        self.className = self.getToken()
        self.eat(Token.TK_IDENTIFIER)
        self.cEat('{')
        while self.getToken() in self.KEYWORD_CLASS_VAR_TYPE:
            self.compileClassVarDec()
        while self.getToken() in self.KEYWORD_SUBROUTINE:
            self.compileSubroutineDec()
            self.st.startSubroutine()
            
        self.cEat('}')
        self.xml += '</class>\n'

    def compile (self):
        try:
            self.compileClass()
        except CompilerException as e:
            print("# Compilation failed.\n", file=sys.stderr)
            return
        self.generateXML()
        self.vm.close()
        print('Successful compiling of "%s"' % self.path)

if __name__ == '__main__':
    import os, sys
    if len(sys.argv) > 1:
        if os.path.isfile(sys.argv[1]):
            CompilerEngine(sys.argv[1]).compile()
        elif os.path.isdir(sys.argv[1]):
            for file in os.listdir(sys.argv[1]):
                if file.endswith(".jack"):
                    CompilerEngine(os.path.join(sys.argv[1], file)).compile()
        else:
            print("Not supported file type.")
    else:
        CompilerEngine('Main.jack').compile()
