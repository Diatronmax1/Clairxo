import pickle
import os
from shutil import copy2

class CFGFile():
    def __init__(self, path):
        self.name = ''
        self.path = path
        self.serverFolder = '//azmain/data/Transfer/LambertC/QuixoServer/'
        self.userPath = self.serverFolder + 'users.txt'
        self.transferPath = self.serverFolder + 'transfer.txt'
        self.gamePath = self.serverFolder + 'games/'
        self.currentGame = None
        self.games = {}
        self.save()

    def integrityCheck(self):
        '''Tests the attributes defined in the config file, if there have been updates'''
        if not hasattr(self, 'path'):
            self.path = 'lib/cfg/cfg.tp'
        if not hasattr(self, 'serverFolder'):
            self.serverFolder = '//azmain/data/Transfer/LambertC/QuixoServer/'
        if not hasattr(self, 'userPath'):
            self.userPath = self.serverFolder + 'users.txt'
        if not hasattr(self, 'transferPath'):
            self.transferPath = self.serverFolder + 'transfer.txt'
        if not hasattr(self, 'gamePath'):
            self.gamepath = self.serverFolder + 'games/'
        if not hasattr(self, 'currentGame'):
            self.currentGame = None
        if not hasattr(self, 'games'):
            self.games = {}
        self.save()

    def setServerPath(self, newPath):
        #Check if you ahve connection to your old server to copy game info over
        oldFolder = None
        self.currentGame = None
        if os.path.exists(self.serverFolder):
            print('Current Server Link exists')
            oldFolder = self.serverFolder
        if os.path.exists(newPath):
            print('New Path is valid')
            self.serverFolder = newPath
            self.userPath = self.serverFolder + 'users.txt'
            self.transferPath = self.serverFolder + 'transfer.txt'
            self.gamePath = self.serverFolder + 'games/'
            if not os.path.exists(self.userPath):
                print('Server missing user file')
                open(self.userPath, 'w+').close()
            if not os.path.exists(self.transferPath):
                print('Server missing transfer file')
                open(self.transferPath, 'w+').close()
            if not os.path.exists(self.gamePath, 'w+'):
                print('Server missing game folder')
                os.mkdir(self.gamePath)
            if oldFolder:
                print('Copying old data')
                #Copy all your old games to this new location
                for gamename, path in self.games.items():
                    newpath = os.path.join(self.serverFolder, os.path.basename(path))
                    #Check another user hasn't copied your game over already
                    if not os.path.exists(newpath):
                        copy2(path, newpath)
                        self.games[gamename] = newpath
            #If you couldn't connect to your old game server 
            #delete your games :( tough luck buddy
            else:
                self.games = {}

    def setName(self, newname):
        if newname[-1] != '\n':
            newname += '\n'
        self.name = newname
        self.save()

    def setCurrentGame(self, filename, gamepath):
        self.currentGame = gamepath
        print('setting current game ' + filename)
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

    def getUserPath(self):
        return self.userPath

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