import re
from Token import Token
from CompilerException import CompilerException
from EOFException import EOFException

TOKEN_REGEX = '[a-zA-Z_][a-zA-Z0-9_]*|[\{\}\(\)\[\]\.\,;\+\-\*/&|\<\>\=~]|[0-9]+|".*"'

class JackTokenizer:
    def __init__ (self, path):
        self.path = path
        self._tokens = [None]
        with open(path) as f:
            lines = f.readlines()
            cFlag = 0 # comment flag
            for index, line in enumerate(lines):
                if cFlag.__eq__(0):
                    match = re.search('//', line)
                    if match:
                        line = line[0:match.start()]
                    else:
                        cFlag = 1
                if cFlag.__eq__(1):
                    match = re.search('/\*', line)
                    if match:
                        line = line[match.end():]
                        cFlag = 2
                    else:
                        cFlag = 0
                if cFlag.__eq__(2):
                    match = re.search('\*/', line)
                    if match:
                        line = line[match.end():]
                        cFlag = 0
                    else:
                        continue
                if line != str():
                    rawTokens = re.findall(TOKEN_REGEX, line)
                    metaTokens = [Token(token, index) for token in rawTokens]
                    self._tokens.extend(metaTokens)
                
    
    def hasMoreTokens (self):
        return bool(self._tokens[1:])

    def advance (self):
        self._tokens.pop(0)

    def tokenType (self):
        if self._tokens:
            return self._tokens[0].kind()
        else:
            raise EOFException("%s: Unexpected EOF" % self.path)

    def getToken (self):
        if self._tokens:
            return self._tokens[0].token()
        else:
            raise EOFException("%s: Unexpected EOF" % self.path)

    def getLine (self):
        if self._tokens:
            return self._tokens[0].line()
        else:
            raise EOFException("%s: Unexpected EOF" % self.path)

    def getTokenObject (self):
        if self._tokens:
            return self._tokens[0]
        else:
            raise EOFException("%s: Unexpected EOF" % self.path)
