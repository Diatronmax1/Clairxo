import pickle
import os

class CFGFile():
    def __init__(self, path):
        self.name = ''
        self.path = path
        self.serverPath = '//azmain/data/Transfer/LambertC/QuixoServer/users.txt'
        self.transferPath = '//azmain/data/Transfer/LambertC/QuixoServer/transfer.txt'
        self.gamePath = '//azmain/data/Transfer/LambertC/QuixoServer/games/'
        self.currentGame = None
        self.games = {}
        self.save()

    def integrityCheck(self):
        '''Tests the attributes defined in the config file, if there have been updates'''
        if not hasattr(self, 'path'):
            self.path = 'lib/cfg/cfg.tp'
        if not hasattr(self, 'serverPath'):
            self.serverPath = '//azmain/data/Transfer/LambertC/QuixoServer/users.txt'
        if not hasattr(self, 'transferPath'):
            self.transferPath = '//azmain/data/Transfer/LambertC/QuixoServer/transfer.txt'
        if not hasattr(self, 'gamePath'):
            self.gamepath = '//azmain/data/Transfer/LambertC/QuixoServer/games/'
        if not hasattr(self, 'currentGame'):
            self.currentGame = None
        if not hasattr(self, 'games'):
            self.games = {}
        self.save()

    def setName(self, newname):
        if newname[-1] != '\n':
            newname += '\n'
        self.name = newname
        self.save()

    def setCurrentGame(self, filename, gamepath):
        self.currentGame = gamepath
        self.games[filename] = self.currentGame
        self.save()

    def removeCurrentGame(self):
        '''Either called to delete the game in the folder
        or to remove the game from this client'''
        if self.currentGame:
            if os.path.exists(self.currentGame):
                try:
                    os.remove(self.currentGame)
                except:
                    pass
            mark = None
            for game, path in self.games.items():
                if path == self.currentGame:
                    mark = game
            if mark:
                self.games.pop(mark)
            self.currentGame = None

    def getGames(self):
        return self.games

    def getGame(self, gamename):
        self.currentGame = None
        if gamename in self.games:
            self.currentGame = self.games[gamename]
        return self.currentGame

    def getCurrentGame(self):
        return self.currentGame

    def getName(self):
        return self.name

    def setServerPath(self, newpath):
        self.serverPath = newpath
        self.save()

    def getServerPath(self):
        return self.serverPath

    def setGamePath(self, newPath):
        self.gamePath = newPath
        self.save()

    def getGamePath(self):
        return self.gamePath

    def setTransferPath(self, newPath):
        self.transferPath = newPath
        self.save()

    def getTransferPath(self):
        return self.transferPath

    def save(self):
        with open(self.path, 'wb') as cfile:
            pickle.dump(self, cfile)