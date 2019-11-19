import re

KEYWORDS = ['class', 'constructor', 'function', 'method', 'field', 'static', 'var', 'int', 'char', 'boolean', 'void', 'true', 'false', 'null', 'this', 'let', 'do', 'if', 'else', 'while', 'return']
SYMBOLS = ['{', '}', '(', ')', '[', ']', '.', ',', ';', '+', '-', '*', '/', '&', '|', '<', '>', '=', '~']
TYPES = ['int', 'char', 'boolean']
INTEGER_REGEX = '[0-9]+'
STRING_REGEX = '".*"'

class Token:
    TK_KEYWORD = 'keyword'
    TK_SYMBOL = 'symbol'
    TK_INT = 'intConst'
    TK_STRING = 'stringConst'
    TK_IDENTIFIER = 'identifier'
    
    def __init__ (self, token, line):
        self._token = token
        self._line = line
        if token in KEYWORDS:
            self._type = self.TK_KEYWORD
        elif token in SYMBOLS:
            self._type = self.TK_SYMBOL
        elif re.match(INTEGER_REGEX, token):
            self._type = self.TK_INT
        elif re.match(STRING_REGEX, token):
            self._type = self.TK_STRING
        else:
            self._type = self.TK_IDENTIFIER

    def __repr__ (self):
        return repr(self._token)

    def __eq__ (self, other):
        if type(other).__eq__(str):
            return self._token == other
        elif type(other).__eq__(Token):
            return self._token == other._token
        else:
            return self == other

    def token (self):
        return self._token

    def line (self):
        return self._line

    def kind (self):
        return self._type
