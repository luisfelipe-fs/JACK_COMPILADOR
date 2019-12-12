from CodeWriter import CodeWriter
from Parser import Parser

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
        for token in self.parser.tokens:
            if token.getToken() in ['push', 'pop']:
                self.cw.writePushPop(token.getToken(), token.getArg(0), token.getArg(1))
            elif token.getToken() in self.parser.ARITHMETIC:
                self.cw.writeArithmetic(token.getToken())
        with open(self.path[:-3] + '.asm', 'w') as f:
            f.write(self.cw.out)
        print("Done.")
