from VMTranslator.CodeWriter import CodeWriter
from VMTranslator.Parser import Parser

class VMTranslator:
    def __init__ (self, path):
        self.path = path.replace('\\', '/')
        try:
            self.filename = self.path[len(self.path)-self.path[::-1].index('/'):-3]
        except ValueError:
            self.filename = self.path[:-3]
        self.cw = CodeWriter(self.filename)
        self.parser = Parser(path)

    def translate (self):
        self.parser.advance()
        currentFunction = 'Sys.init'
        for token in self.parser.tokens:
            if token.getToken() in ['push', 'pop']:
                self.cw.writePushPop(token.getToken(), token.getArg(0), token.getArg(1))
            elif token.getToken() in self.parser.ARITHMETIC:
                self.cw.writeArithmetic(token.getToken())
            elif token.getToken().__eq__('label'):
                self.cw.writeLabel('%s$%s'%(currentFunction, token.getArg(0)))
            elif token.getToken().__eq__('goto'):
                self.cw.writeGoto('%s$%s'%(currentFunction, token.getArg(0)))
            elif token.getToken().__eq__('if-goto'):
                self.cw.writeIf('%s$%s'%(currentFunction, token.getArg(0)))
            elif token.getToken().__eq__('call'):
                self.cw.writeCall(token.getArg(0), token.getArg(1))
            elif token.getToken().__eq__('function'):
                currentFunction = token.getArg(0)
                self.cw.writeFunction(token.getArg(0), token.getArg(1))
            elif token.getToken().__eq__('return'):
                self.cw.writeReturn()
                
        with open(self.path[:-3] + '.asm', 'w') as f:
            f.write(self.cw.out)
        print("Translate of '%s' done." % self.path)

if __name__ == '__main__':
    import os, sys
    if len(sys.argv) > 1:
        if os.path.isfile(sys.argv[1]):
            VMTranslator(sys.argv[1]).translate()
        elif os.path.isdir(sys.argv[1]):
            counter = 1
            out = '@256 // bootstrap\n'
            out += 'D=A\n'
            out += '@SP\n'
            out += 'M=D\n'
            cw = CodeWriter(str(), counter=0)
            cw.writeCall('Sys.init', '0')
            out += cw.out
            for file in os.listdir(sys.argv[1]):
                if file.endswith(".vm"):
                    vmt = VMTranslator(os.path.join(sys.argv[1], file))
                    vmt.cw.counter = counter
                    vmt.translate()
                    counter = vmt.cw.counter
                    out += '// begin %s\n' % file
                    out += vmt.cw.out
                    out += '// end %s\n' % file
            osPath = sys.argv[1].replace('\\', '/')
            folderName = osPath[len(osPath)-osPath[::-1].index('/'):]
            with open(osPath+'/'+folderName+'.asm', 'w') as f:
                print("Generated: '%s'" % (osPath+'/'+folderName+'.asm'))
                f.write(out)
        else:
            print("Not supported file type.")
    else:
        VMTranslator('Main.vm').translate()
