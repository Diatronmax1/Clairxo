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
        print('State Set!')
        self.oldstate = self.state
        self.state = state

    def setEdge(self, state=True):
        self.edge = state

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
        #Starting configuration is a 5x5 grid of cubes all incremented by 1
        #so that top left is (1, 1), top right is (1, 6), bot left is (6, 1)
        #and bot right is (6, 6)
        self.maxrows = 5
        self.maxcols = 5
        self.cubes = np.ndarray(shape=(self.maxrows+2,self.maxcols+2), dtype=object)
        for row in range(1, self.maxrows+1):
            for col in range(1, self.maxcols+1):
                edge = False
                if row==1 or row==self.maxrows or col==1 or col==self.maxcols:
                    edge = True
                self.cubes[row][col] = Cube(row, col, edge)
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
            for row in range(1, self.maxrows):
                #Starts with 6-1 row 5.
                #Ends with 6-5 row 1.
                cube = self.cubes[self.maxrows-row][col]
                self.cubes[self.maxrows+1-row][col].setState(cube.getState())
            #Then row 1 needs the new game state added to its cube
            self.cubes[1][col].setState(self.state)
        elif row == self.maxrows+1:
            #Bottom row, shift up
            print('Up Shift')
            #For all cubes starting with the one just below
            #the top, take its state and move it up one
            for row in range(2, self.maxrows+1):
                cube = self.cubes[row][col]
                self.cubes[row-1][col].setState(cube.getState())
            #Then row 6 needs the new game state added to its cube
            self.cubes[self.maxrows+1][col].setState(self.state)
        elif col == 0:
            #Left row shift right
            print('Right Shift')
            #For all cubes starting with the one right
            #before the right edge, take its state and move to the right
            for col in range(1, self.maxcols):
                #Starts with col 5
                #ends with col 1
                cube = self.cubes[row][self.maxcols-col]
                self.cubes[row][self.maxcols+1-col].setState(cube.getState())
            #Finally put the cube on the left edge to the game state
            self.cubes[row][1].setState(self.state)
        elif col == self.maxcols+1:
            #Right row shift left
            print('Left Shift')
            #For all cubes starting with the one right before the
            #left edge, take its state and move it to the left
            for col in range(2, self.maxcols+1):
                cube = self.cubes[row][col]
                self.cubes[row][col-1].setState(cube.getState())
            #Finally put the cube on the right to the game state
            self.cubes[row][self.maxcols].setState(self.state)
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
        for row in range(1, self.maxrows+1):
            startCube = self.cubes[row][1]
            if startCube:
                for col in range(1, self.maxcols+1):
                    cube = self.cubes[row][col]
                    if cube != startCube:
                        break
                else:
                    #Won on a row!
                    return True
        for col in range(1, self.maxcols+1):
            startCube = self.cubes[1][col]
            if startCube:
                for row in range(1, self.maxrows+1):
                    cube = self.cubes[row][col]
                    if cube != startCube:
                        break
                else:
                    #Won on a column!
                    return True

    def getCubes(self):
        return self.cubes

    def getSaveFile(self):
        return os.path.join(self.client.getGamePath(), self.filename + '.gtp')

    def save(self):
        '''Saves in the game folder'''
        gamefolder = self.client.getGamePath()
        savefile = os.path.join(gamefolder, self.filename)
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
        self.dropPoints.clear()
        north = 0
        south = self.maxrows+1
        east = self.maxcols+1
        west = 0
        row, col = gamecube.getPos()
        if row == 1:
            #On a northern edge
            self.dropPoints.append((south, col))
            if col == 1:
                #North West Corner
                self.dropPoints.append((row, east))
            elif col == self.maxcols:
                #North East Corner
                self.dropPoints.append((row, west))
            else:
                #Northern Edge
                self.dropPoints.append((row, west))
                self.dropPoints.append((row, east))
        elif row == self.maxrows:
            #On a southern edge
            self.dropPoints.append((north, col))
            if col == 1:
                #South West Corner
                self.dropPoints.append((row, east))
            elif col == self.maxcols:
                #South East Corner
                self.dropPoints.append((row, west))
            else:
                self.dropPoints.append((row, west))
                self.dropPoints.append((row, east))
        else:
            #Western or Eastern Front
            if col == 1:
                #Western Edge
                self.dropPoints.append((row, east))
                self.dropPoints.append((north, col))
                self.dropPoints.append((south, col))
            elif col == self.maxcols:
                #Eastern Edge
                self.dropPoints.append((row, west))
                self.dropPoints.append((north, col))
                self.dropPoints.append((south, col))
        return self.dropPoints
