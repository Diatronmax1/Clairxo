import os
from lib.cfg import CFGFile
import pickle

class Point():
    def __init__(self, x, y):
        self.x = x
        self.y = y
        print(str(x) + ', ' + str(y)) 

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def getIndex(self):
        print(self.x)
        print(self.y)
        return (self.x*7) + self.y

class Client():
    def __init__(self):
        self.cfgfile = 'lib/cfg/cfg.tp'
        self.config = None
        self.serverLink = '//azmain/data/Transfer/LambertC/QuixoServer/users.txt'
        self.gameFolder = '//azmain/data/Transfer/LambertC/QuixoServer/games/'
        self.user = ''
        self.states = ['X', 'Y']
        self.currentState = self.states[0]
        self.dropPoints = []
        self.turns = 0

    def load(self):
        self.user = ''
        if not os.path.exists(self.cfgfile):
            self.config = CFGFile(self.cfgfile)
            with open(self.cfgfile, 'wb') as cfile:
                pickle.dump(self.config, cfile)
        else:
            with open(self.cfgfile, 'rb') as cfile:
                self.config = pickle.load(cfile)
                self.user = self.config.getName()
        return self.user

    def startNewGame(self):
        pass

    def checkUserName(self):
        return self.user

    def setUserName(self, newname):
        self.goOffline()
        self.config.setName(newname)
        self.user = self.config.getName()
        self.connect()

    def getOnlinePlayers(self):
        print('Scanning for online players')
        players = []
        if os.path.exists(self.serverLink):
            with open(self.serverLink, 'r') as slink:
                for line in slink:
                    if line != self.user:
                        players.append(line)
        else:
            print('Didnt\'t connect to server to find players')
        return players


    def goOffline(self):
        print('Going offline')
        if os.path.exists(self.serverLink):
            players = []
            with open(self.serverLink, 'r') as slink:
                for line in slink:
                    if line != self.user:
                        players.append(line)
            with open(self.serverLink, 'w') as slink:
                for player in players:
                    slink.write(player)
        else:
            print('Didn\'t connect to server to close')

    def connect(self):
        if os.path.exists(self.serverLink):
            print('Connected to server')
            players = []
            online = False
            with open(self.serverLink, 'r') as slink:
                for line in slink:
                    print('Online Player ' + line)
                    players.append(line)
                    if line == self.user:
                        online = True
            if not online:
                print('Setting status to online')
                players += self.user
                with open(self.serverLink, 'w') as slink:
                    for player in players:
                        slink.write(player)
        else:
            print('Did not connect to server!')

    def reset(self):
        self.currentState = self.states[0]
        self.turns = 0

    def changeTurn(self):
        self.turns += 1
        self.currentState = self.states[self.turns%2]
        return self.currentState

    def getState(self):
        return self.currentState

    def validDrop(self, x, y):
        newPoint = Point(x, y)
        found = False
        for point in self.dropPoints:
            if point == newPoint:
                found = True
        return found

    def updateDrops(self, x, y):
        """Selects the valid points on a 7x7 grid that are valid entries based on
        and x y coordinate. If point (1, 1) is picked up, valid entries are due east
        and south. (7, 1) and (1, 7). If (1, 2) is picked up, valid entries are west
        south and east (1, 0), (7, 2), (1, 7)

        Parameters:
            -x (int): x coordinate (rows) of the point
            -y (int): y coordingate (cols) of the point
        """
        self.dropPoints.clear()
        north = 0
        south = 6
        east = 6
        west = 0
        print(str(x) + ', ' + str(y))
        if x == 1:
            #On a northern edge
            self.dropPoints.append(Point(south, y))
            if y == 1:
                #North West Corner
                self.dropPoints.append(Point(x, east))
            elif y == 5:
                #North East Corner
                self.dropPoints.append(Point(x, west))
            else:
                #Northern Edge
                self.dropPoints.append(Point(x, west))
                self.dropPoints.append(Point(x, east))
        elif x == 5:
            #On a southern edge
            self.dropPoints.append(Point(north, y))
            if y == 1:
                #South West Corner
                self.dropPoints.append(Point(x, east))
            elif y == 5:
                #South East Corner
                self.dropPoints.append(Point(x, west))
            else:
                self.dropPoints.append(Point(x, west))
                self.dropPoints.append(Point(x, east))
        else:
            #Western or Eastern Front
            if y == 1:
                self.dropPoints.append(Point(x, east))
                self.dropPoints.append(Point(north, y))
                self.dropPoints.append(Point(south, y))
            elif y == 5:
                self.dropPoints.append(Point(x, west))
                self.dropPoints.append(Point(north, y))
                self.dropPoints.append(Point(south, y))
        return self.dropPoints