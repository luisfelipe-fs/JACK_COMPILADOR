from VMTranslator.VMToken import VMToken
import re

class Parser:
    ARITHMETIC = ['add', 'sub', 'eq', 'gt', 'lt', 'and', 'or', 'not', 'neg']
    def __init__ (self, path):
        self.path = path
        self.tokens = [None]
        with open(path) as f:
            lines = f.readlines()
            cFlag = 0
            for index, line in enumerate(lines):
                line = line[:-1]
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
                    rawTokens = re.findall('[A-Za-z0-9\-\$\.\_]+', line)
                    self.tokens.append(VMToken(rawTokens[0], rawTokens[1:], index))

    def hasMoreTokens (self):
        return bool(self.tokens[1:])

    def advance (self):
        self.tokens.pop(0)

    def token (self):
        return self.tokens[0]

    def commandType (self):
        if self.token[0].getToken() in ARITHMETIC:
            return 'arithmetic'
        else:
            return self.token[0].getToken()

    def arg1 (self):
        return self.token[0].getArg[0]

    def arg2 (self):
        return self.token[0].getArg[1]
