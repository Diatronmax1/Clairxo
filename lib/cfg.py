import pickle

class CFGFile():
    def __init__(self, path):
        self.name = ''
        self.path = path

    def setName(self, newname):
        if newname[-1] != '\n':
            newname += '\n'
        self.name = newname
        self.save()

    def getName(self):
        return self.name

    def save(self):
        with open(self.path, 'wb') as cfile:
            pickle.dump(self, cfile)