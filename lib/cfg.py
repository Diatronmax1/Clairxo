import pickle

class CFGFile():
    def __init__(self, path):
        self.name = ''
        self.path = path
        self.serverPath = '//azmain/data/Transfer/LambertC/QuixoServer/users.txt'
        self.gamePath = '//azmain/data/Transfer/LambertC/QuixoServer/games/'
        self.save()

    def setName(self, newname):
        if newname[-1] != '\n':
            newname += '\n'
        self.name = newname
        self.save()

    def getName(self):
        return self.name

    def newGame(self, gamename):
        self.game = gamename

    def loadGame(self):
        return self.game

    def setServerPath(self, newpath):
        self.serverPath = newpath

    def getServerPath(self):
        return self.serverPath

    def save(self):
        with open(self.path, 'wb') as cfile:
            pickle.dump(self, cfile)