class VMWriter:
    ARITHMETIC = {'+': 'add', '-': 'sub', '=': 'eq', '>': 'gt', '<': 'lt', '&': 'and', '|': 'or', '~': 'not', '!': 'neg'}

    def __init__ (self, path):
        self.path = path
        self.buffer = str()

    def writePush (self, segment, index=''):
        self.buffer += 'push %s %s\n' % (segment, index)

    def writePop (self, segment, index=''):
        self.buffer += 'pop %s %s\n' % (segment, index)

    def writeArithmetic (self, command):
        self.buffer += '%s\n' % self.ARITHMETIC[command]

    def writeLabel (self, label):
        self.buffer += 'label %s\n' % label

    def writeGoto (self, label):
        self.buffer += 'goto %s\n' % label

    def writeIf (self, label):
        self.buffer += 'if-goto %s\n' % label

    def writeCall (self, name, nArgs):
        self.buffer += 'call %s %s\n' % (name, nArgs)

    def writeFunction (self, name, nLocals):
        self.buffer += 'function %s %s\n' % (name, nLocals)
    
    def writeReturn (self):
        self.buffer += 'return\n'

    def close (self):
        with open(self.path, 'w') as f: f.write(self.buffer)
            
