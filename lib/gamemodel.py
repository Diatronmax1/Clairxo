import datetime as dt
import os
import pickle
import numpy as np

class Cube():
    def __init__(self, x, y, edge=False):
        self.x = x
        self.y = y
        self.state = None
        self.oldstate = None
        self.edge = edge

    def setState(self, state):
        self.oldstate = self.state
        self.state = state

    def getState(self):
        return self.state

    def revertState(self):
        self.state = self.oldstate

    def getPos(self):
        return self.x, self.y

    def clear(self):
        self.state = None

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y and self.state == other.state

    def __str__(self):
        return str(self.x) + ', ' + str(self.y) + ' State: ' +  str(self.state)

class GameModel():
    def __init__(self, client, player1, player2):
        self.players = [player1, player2]
        self.currentPlayer = self.players[0]
        self.client = client
        time = dt.datetime.now()
        self.filename = time.strftime("%d%m%Y") + self.players[0][:-1] + self.players[1][:-1]
        self.cubes = np.ndarray(shape=(8,8), dtype=object)
        #Starting configuration is a 5x5 grid of cubes all incremented by 1
        #so that top left is (1, 1), top right is (1, 6), bot left is (6, 1)
        #and bot right is (6, 6)
        for x in range(1, 7):
            for y in range(1, 7):
                edge = False
                if x == 1 or x==6 or y==1 or y==6:
                    edge = True
                self.cubes[x][y] = Cube(x, y, edge)
        self.states = ['X', 'Y']
        self.state = self.states[0]
        self.turnCount = 0
        self.dropPoints = []
        self.droppedPoint = None
        self.pickedUpCube = None
        self.save()

    def getCurrentPlayer(self):
        return self.currentPlayer

    def getState(self):
        return self.state

    def getDropPoints(self):
        return self.dropPoints

    def reset(self):
        #Clear the cubes
        for row in self.cubes:
            for cube in row:
                if cube:
                    cube.clear()
        self.state = self.states[0]
        self.droppedPoint = None
        self.pickedUpCube = None
        self.turnCount = 0
        self.save()

    def setQueueDrop(self, x, y):
        self.droppedPoint = (x, y)

    def rejectDrop(self):
        self.droppedPoint = None

    def getDroppedPoint(self):
        return self.droppedPoint

    def getCube(self, x, y):
        for row in self.cubes:
            for cube in row:
                if cube:
                    if x == cube.x and y == cube.y:
                        return cube

    def passTurn(self):
        #Move the dropped block into the grid shifting all of the cubes.
        print('Shifting ' + str(self.droppedPoint) + ' into grid')
        #Determine whether the shift is a row or column shift
        row, col = self.droppedPoint
        if row == 0:
            #Top Row, shift down a column
            print('Down shift')
            #For all cubes starting with the one right
            #above the bottom, take its state and move it down
            #one
            for row in range(1, 6):
                #Starts with 6-1 row 5.
                #Ends with 6-5 row 1.
                cube = self.cubes[6-row][col]
                self.cubes[7-row][col].setState(cube.getState())
            #Then row 1 needs the new game state added to its cube
            self.cubes[1][col].setState(self.state)
        elif row == 7:
            #Bottom row, shift up
            print('Up Shift')
            #For all cubes starting with the one just below
            #the top, take its state and move it up one
            for row in range(2, 7):
                cube = self.cubes[row][col]
                self.cubes[row-1][col].setState(cube.getState())
            #Then row 6 needs the new game state added to its cube
            self.cubes[6][col].setState(self.state)
        elif col == 0:
            #Left row shift right
            print('Right Shift')
            #For all cubes starting with the one right
            #before the right edge, take its state and move to the right
            for col in range(1, 6):
                #Starts with col 5
                #ends with col 1
                cube = self.cubes[row][6-col]
                self.cubes[row][7-col].setState(cube.getState())
            #Finally put the cube on the left edge to the game state
            self.cubes[row][1].setState(self.state)
        elif col == 7:
            #Right row shift left
            print('Left Shift')
            #For all cubes starting with the one right before the
            #left edge, take its state and move it to the left
            for col in range(2, 7):
                cube = self.cubes[row][col]
                self.cubes[row][col-1].setState(cube.getState())
            #Finally put the cube on the right to the game state
            self.cubes[row][6].setState(self.state)
        self.turnCount += 1
        self.state = self.states[self.turnCount%2]
        self.pickedUpCube = None
        self.droppedPoint = None
        self.currentPlayer = self.players[self.turnCount%2]
        self.save()
        return self.checkIfWon()

    def checkIfWon(self):
        '''Checks for rows, cols, or diaganols full of X's or Y's'''
        print('Checking Win')
        for row in range(1, 7):
            startCube = self.cubes[row][1]
            if startCube:
                for col in range(1, 7):
                    cube = self.cubes[row][col]
                    if cube != startCube:
                        break
                else:
                    #Won on a row!
                    return True
        for col in range(1, 7):
            startCube = self.cubes[1][col]
            if startCube:
                for row in range(1, 7):
                    cube = self.cubes[row][col]
                    if cube != startCube:
                        break
                else:
                    #Won on a column!
                    return True

    def getCubes(self):
        return self.cubes

    def save(self):
        '''Saves in the game folder'''
        gamefolder = self.client.getGamePath()
        savefile = os.path.join(gamefolder, self.filename)
        self.client.alertPlayer(savefile + '.gtp')
        with open(savefile + '.gtp', 'wb') as gfile:
            pickle.dump(self, gfile)

    def cancelPickedUp(self):
        self.pickedUpCube.revertState()
        self.pickedUpCube = None
        self.droppedPoint = None

    def getPickedUpCube(self):
        return self.pickedUpCube

    def updateDrops(self, gamecube):
        """Selects the valid points on a 7x7 grid that are valid entries based on
        and x y coordinate. If point (1, 1) is picked up, valid entries are due east
        and south. (7, 1) and (1, 7). If (1, 2) is picked up, valid entries are west
        south and east (1, 0), (7, 2), (1, 7)

        Parameters:
            gamecube (obj): Cube object with cooridnates
        """
        self.pickedUpCube = gamecube
        if self.pickedUpCube.getState() is None:
            self.pickedUpCube.setState(self.state)
        self.dropPoints.clear()
        north = 0
        south = 7
        east = 7
        west = 0
        x, y = gamecube.getPos()
        if x == 1:
            #On a northern edge
            self.dropPoints.append((south, y))
            if y == 1:
                #North West Corner
                self.dropPoints.append((x, east))
            elif y == 6:
                #North East Corner
                self.dropPoints.append((x, west))
            else:
                #Northern Edge
                self.dropPoints.append((x, west))
                self.dropPoints.append((x, east))
        elif x == 6:
            #On a southern edge
            self.dropPoints.append((north, y))
            if y == 1:
                #South West Corner
                self.dropPoints.append((x, east))
            elif y == 6:
                #South East Corner
                self.dropPoints.append((x, west))
            else:
                self.dropPoints.append((x, west))
                self.dropPoints.append((x, east))
        else:
            #Western or Eastern Front
            if y == 1:
                #Western Edge
                self.dropPoints.append((x, east))
                self.dropPoints.append((north, y))
                self.dropPoints.append((south, y))
            elif y == 6:
                #Eastern Edge
                self.dropPoints.append((x, west))
                self.dropPoints.append((north, y))
                self.dropPoints.append((south, y))
        return self.dropPoints
