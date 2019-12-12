from VMTranslator.Parser import Parser

class CodeWriter:
    SEGMENTS = {'local': 'LCL', 'argument': 'ARG', 'that': 'THAT', 'this': 'THIS'}
    POINTERS = {'0': 'THIS', '1': 'THAT'}
    
    def __init__ (self, filename):
        self.filename = filename
        self.out = str()

    def writePushPop (self, command, segment, index):
        if command.__eq__('push'):
            if segment in self.SEGMENTS:
                with open('VMTranslator/commands/pushSegment') as f:
                    self.out += f.read().format(segment=self.SEGMENTS[segment], index=index)
            elif segment.__eq__('constant'):
                with open('VMTranslator/commands/pushConstant') as f:
                    self.out += f.read().format(value=index)
            elif segment.__eq__('static'):
                with open('VMTranslator/commands/pushFrom') as f:
                    self.out += f.read().format(reference='%s.%s' % (self.filename, index))
            elif segment.__eq__('temp'):
                with open('VMTranslator/commands/pushFrom') as f:
                    self.out += f.read().format(reference='R%s' % (5+int(index)))
            elif segment.__eq__('pointer'):
                with open('VMTranslator/commands/pushPointer') as f:
                    self.out += f.read().format(pointer=self.POINTERS[index])
            else:
                raise Exception("Invalid segment: %s" % segment)
        elif command.__eq__('pop'):
            if segment in self.SEGMENTS:
                with open('VMTranslator/commands/popSegment') as f:
                    self.out += f.read().format(segment=self.SEGMENTS[segment], index=index)
            elif segment.__eq__('static'):
                with open('VMTranslator/commands/popTo') as f:
                    self.out += f.read().format(reference='%s.%s' % (self.filename, index))
            elif segment.__eq__('temp'):
                with open('VMTranslator/commands/popTo') as f:
                    self.out += f.read().format(reference='R%s' % (5+int(index)))
            elif segment.__eq__('pointer'):
                with open('VMTranslator/commands/popPointer') as f:
                    self.out += f.read().format(pointer=self.POINTERS[index])
            else:
                raise Exception("Invalid segment: %s" % segment)
        else:
            raise Exception("Invalid command: %s" % command)
        # WARNING: Assembly command files should end with '\n'
        # for any issue related to this requirement, uncomment following line:
        #self.out += '\n'

    def writeArithmetic (self, arithmetic):
        try:
            with open('VMTranslator/commands/' + arithmetic) as f:
                self.out += f.read()
        except FileNotFoundError:
            raise Exception("Invalid command: %s" % arithmetic)
