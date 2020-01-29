import pickle

class CFGFile():
    def __init__(self, path):
        self.name = ''
        self.path = path
        self.serverPath = '//azmain/data/Transfer/LambertC/QuixoServer/users.txt'
        self.transferPath = '//azmain/data/Transfer/LambertC/QuixoServer/transfer.txt'
        self.gamePath = '//azmain/data/Transfer/LambertC/QuixoServer/games/'
        self.save()

    def setName(self, newname):
        if newname[-1] != '\n':
            newname += '\n'
        self.name = newname
        self.save()

    def getName(self):
        return self.name

    def setServerPath(self, newpath):
        self.serverPath = newpath

    def getServerPath(self):
        return self.serverPath

    def setGamePath(self, newPath):
        self.gamePath = newPath

    def getGamePath(self):
        return self.gamePath

    def setTransferPath(self, newPath):
        self.transferPath = newPath

    def getTransferPath(self):
        return self.transferPath

    def save(self):
        with open(self.path, 'wb') as cfile:
            pickle.dump(self, cfile)