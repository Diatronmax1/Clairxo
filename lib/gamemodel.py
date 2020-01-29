import datetime as dt
import os
import pickle
import numpy as np

class Cube():
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.state = None

    def claimX(self):
        self.state = 'X'

    def claimY(self):
        self.state = 'Y'

    def clear(self):
        self.state = None

    def __str__(self):
        return str(self.x) + ' :' + str(self.y) + ' State: ' +  str(self.state)

class GameModel():
    def __init__(self, client):
        self.client = client
        time = dt.datetime.now()
        self.filename = time.strftime("%d%m%Y") + self.client.getUserName()[:-1] + self.client.getPlayerTarget()[:-1]
        self.save()
        self.cubes = np.ndarray(shape=(8,8), dtype=object)
        #Starting configuration is a 5x5 grid of cubes all incremented by 1
        #so that top left is (1, 1), top right is (1, 6), bot left is (6, 1)
        #and bot right is (6, 6)
        for x in range(1, 7):
            for y in range(1, 7):
                self.cubes[x][y] = Cube(x, y)

    def getCubes(self):
        return self.cubes

    def save(self):
        '''Saves in the game folder'''
        gamefolder = self.client.getGamePath()
        savefile = os.path.join(gamefolder, self.filename)
        count = 0
        savefile = savefile + str(count)
        while os.path.exists(savefile + '.gtp'):
            count += 1
            savefile = savefile[:-1] + str(count)
        with open(savefile + '.gtp', 'wb') as gfile:
            pickle.dump(self, gfile)
