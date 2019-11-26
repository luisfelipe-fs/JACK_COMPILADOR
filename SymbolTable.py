from CompilerException import CompilerException

class SymbolTable:
    STATIC = 'static'
    FIELD = 'this'
    ARGUMENT = 'argument'
    LOCAL = 'local'
    LOCAL_SCOPE = [ARGUMENT, LOCAL]
    NONLOCAL_SCOPE = [STATIC, FIELD]
    TABLE_INDEX = 0
    TABLE_TYPE = 1
    TABLE_KIND = 2
    
    def __init__ (self):
        self.currentIndex = {self.STATIC: -1, self.FIELD: -1, self.ARGUMENT: -1, self.LOCAL: -1}
        self.classTable = dict()
        self.subRoutineTable = dict()

    def startSubroutine (self):
        self.currentIndex[self.ARGUMENT] = -1
        self.currentIndex[self.LOCAL] = -1
        self.subRoutineTable = dict()
    
    def getTableByKind (self, entryKind):
        return self.subRoutineTable if entryKind in self.LOCAL_SCOPE else self.classTable if entryKind in self.NONLOCAL_SCOPE else None
    
    def define (self, entryName, entryType, entryKind):
        self.currentIndex[entryKind] += 1
        self.getTableByKind(entryKind)[entryName] = [self.currentIndex[entryKind], entryType, entryKind]
    
    def varCount (self, entryKind):
        table = self.getTableByKind(entryKind)
        return self.currentIndex[entryKind]+1
    
    def kindOf (self, entryName):
        if entryName in self.subRoutineTable:
            return self.subRoutineTable[entryName][self.TABLE_KIND]
        elif entryName in self.classTable:
            return self.classTable[entryName][self.TABLE_KIND]
        else:
            raise CompilerException("ENTRY NOT FOUND: %s" % entryName)
    
    def typeOf (self, entryName):
        if entryName in self.subRoutineTable:
            return self.subRoutineTable[entryName][self.TABLE_TYPE]
        elif entryName in self.classTable:
            return self.classTable[entryName][self.TABLE_TYPE]
        else:
            raise CompilerException("ENTRY NOT FOUND: %s" % entryName)
    
    def indexOf (self, entryName):
        if entryName in self.subRoutineTable:
            return self.subRoutineTable[entryName][self.TABLE_INDEX]
        elif entryName in self.classTable:
            return self.classTable[entryName][self.TABLE_INDEX]
        else:
            raise CompilerException("ENTRY NOT FOUND: %s" % entryName)
