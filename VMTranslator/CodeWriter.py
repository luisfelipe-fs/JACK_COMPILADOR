from VMTranslator.Parser import Parser

class CodeWriter:
    SEGMENTS = {'local': 'LCL', 'argument': 'ARG', 'that': 'THAT', 'this': 'THIS'}
    POINTERS = {'0': 'THIS', '1': 'THAT'}
    
    def __init__ (self, filename, counter = 1):
        self.filename = filename
        self.out = str()
        self.counter = counter

    def write (self, string):
        self.out += '%s\n' % string

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
                    self.out += f.read().format(reference='%s.%s'%(self.filename, index))
            elif segment.__eq__('temp'):
                with open('VMTranslator/commands/pushFrom') as f:
                    self.out += f.read().format(reference='R%s'%(5+int(index)))
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
                    self.out += f.read().format(reference='%s.%s'%(self.filename, index))
            elif segment.__eq__('temp'):
                with open('VMTranslator/commands/popTo') as f:
                    self.out += f.read().format(reference='R%s'%(5+int(index)))
            elif segment.__eq__('pointer'):
                with open('VMTranslator/commands/popPointer') as f:
                    self.out += f.read().format(pointer=self.POINTERS[index])
            else:
                raise Exception("Invalid segment: %s"%segment)
        else:
            raise Exception("Invalid command: %s"%command)
        # WARNING: Assembly arithmetic command files should end with '\n'
        # for any issue related to this requirement, uncomment following line:
        #self.out += '\n'

    def writeArithmetic (self, arithmetic):
        try:
            with open('VMTranslator/commands/' + arithmetic) as f:
                self.out += f.read().format(label='LABEL%d'%self.counter)
                self.counter += 1
        except FileNotFoundError:
            raise Exception("Invalid command: %s"%arithmetic)

    def writeLabel (self, label):
        self.write('({0}) // label {0}'.format(label))

    def writeGoto (self, label):
        self.write('@{0} // goto {0}'.format(label))
        self.write('0;JMP')
    
    def writeIf (self, label):
        self.write('@SP')
        self.write('M=M-1')
        self.write('A=M')
        self.write('D=M')
        self.write('@%s'%label)
        self.write('D;JNE')
        
    def writeCall (self, functionName, nArgs):
        self.writePushPop('push', 'constant', 'RETURN$%d'%self.counter)
        with open('VMTranslator/commands/pushFrom') as f:
            self.out += f.read().format(reference='LCL')
        with open('VMTranslator/commands/pushFrom') as f:
            self.out += f.read().format(reference='ARG')
        self.writePushPop('push', 'pointer', '0')
        self.writePushPop('push', 'pointer', '1')
        
        self.write('@SP')
        self.write('D=M')
        self.write('@%d'%(5+int(nArgs)))
        self.write('D=D-A')
        self.write('@ARG')
        self.write('M=D')

        self.write('@SP')
        self.write('D=M')
        self.write('@LCL')
        self.write('M=D')
        self.write('@%s'%functionName)
        self.write('0;JMP')
        self.write('(RETURN$%d)'%self.counter)
        self.counter += 1

    def writeFunction (self, functionName, nLocals):
        self.write('({0}) // function {0} {1}'.format(functionName, nLocals))
        self.write('@%s'%nLocals)
        self.write('D=A')
        self.write('@ZERO_LOCALS$%d'%self.counter)
        self.write('D;JEQ')
        self.write('@SP')
        self.write('D=D+M')
        self.write('@R13')
        self.write('M=D')
        self.write('(INIT$%d)'%self.counter)
        self.write('@SP')
        self.write('A=M')
        self.write('M=0')
        self.write('@SP')
        self.write('MD=M+1')
        self.write('@R13')
        self.write('D=M-D')
        self.write('@INIT$%d'%self.counter)
        self.write('D;JGT')
        self.write('(ZERO_LOCALS$%d)'%self.counter)
        self.counter += 1

    def writeReturn (self):
        self.write('@LCL')
        self.write('D=M')
        self.write('@R13')
        self.write('M=D')

        self.write('@5')
        self.write('D=D-A')
        self.write('A=D')
        self.write('D=M')
        self.write('@R14')
        self.write('M=D')

        self.write('@SP')
        self.write('A=M-1')
        self.write('D=M')
        self.write('@ARG')
        self.write('A=M')
        self.write('M=D')

        self.write('@ARG')
        self.write('D=M')
        self.write('@SP')
        self.write('M=D+1')

        self.write('@R13')
        self.write('D=M')
        self.write('A=D-1')
        self.write('D=M')
        self.write('@THAT')
        self.write('M=D')

        self.write('@2')
        self.write('D=A')
        self.write('@R13')
        self.write('D=M-D')
        self.write('A=D')
        self.write('D=M')
        self.write('@THIS')
        self.write('M=D')

        self.write('@3')
        self.write('D=A')
        self.write('@R13')
        self.write('D=M-D')
        self.write('A=D')
        self.write('D=M')
        self.write('@ARG')
        self.write('M=D')

        self.write('@4')
        self.write('D=A')
        self.write('@R13')
        self.write('D=M-D')
        self.write('A=D')
        self.write('D=M')
        self.write('@LCL')
        self.write('M=D')

        self.write('@R14')
        self.write('A=M')
        self.write('0;JMP')
