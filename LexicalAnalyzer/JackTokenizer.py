import re
from Token import Token

TOKEN_REGEX = '[a-zA-Z_][a-zA-Z0-9_]*|[\{\}\(\)\[\]\.\,;\+\-\*/&|\<\>\=~]|[0-9]+|".*"'
NOCOMMENT_REGEX = '.*(?=//.*)|.*'

class JackTokenizer:
    def __init__ (self, path):
        self._tokens = list()
        self._current = -1
        with open(path) as f:
            lines = f.readlines()
            for index, line in enumerate(lines):
                start, end = re.match(NOCOMMENT_REGEX, line).span()
                if start != end:
                    rawTokens = re.findall(TOKEN_REGEX, line[start:end])
                    metaTokens = [Token(token, index) for token in rawTokens]
                    self._tokens.extend(metaTokens)
    
    def hasMoreTokens (self):
        return self._current+1 < len(self._tokens)

    def advance (self):
        if self.hasMoreTokens():
            self._current += 1
            return True
        return False

    def tokenType (self):
        return self._tokens[self._current].kind()

    def getToken (self):
        return self._tokens[self._current].token()
        
    
