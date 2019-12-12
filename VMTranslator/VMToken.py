class VMToken:
    def __init__ (self, token, args, line):
        self.token = token
        self.args = args
        self.line = line

    def __getitem__ (self, i):
        return args[i]

    def getToken (self):
        return self.token

    def getArg (self, i):
        return self.args[i]

    def getLine (self):
        return line
