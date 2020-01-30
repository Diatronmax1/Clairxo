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

    def compareState(self, other):
        return self.state == other.state

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
        self.states = ['X', 'O']
        self.state = self.states[0]
        self.turnCount = 0
        self.dropPoints = []
        self.droppedPoint = None
        self.pickedUpCube = None
        self.gameover = False
        self.save()

    def getPlayerOne(self):
        return self.players[0]

    def gameOver(self):
        return self.gameover

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
        startRow, startCol = self.droppedPoint
        puc = self.getPickedUpCube()
        pRow, pCol = puc.getPos()
        if startRow == 0:
            #Top Row, shift down a column
            print('Down shift')
            #Depending on where the cube was removed, not all the blocks
            #may need to be moved down. Take where the cube was picked
            #up and move all others above it down.
            for row in range(pRow-1, 0, -1):
                #Start with right above the picked up cubes location
                #and move that state down into the cube. Cascade to the 
                #top.
                cube = self.cubes[row][startCol]
                self.cubes[row+1][startCol].setState(cube.getState())
            #Then row 1 needs the new game state added to its cube
            self.cubes[1][startCol].setState(self.state)
        elif startRow == self.maxrows+1:
            #Bottom row, shift up
            print('Up Shift')
            #Start with right below the picked up cubes location
            #and move that state into where the picked up cube was
            #cascade down to the bottom.
            for row in range(pRow+1, self.maxrows+1):
                cube = self.cubes[row][startCol]
                self.cubes[row-1][startCol].setState(cube.getState())
            #Then row 6 needs the new game state added to its cube
            self.cubes[self.maxrows][startCol].setState(self.state)
        elif startCol == 0:
            #Left row shift right
            print('Right Shift')
            #Start with the one the left of the picked up cube
            #and move its value to the picked up cube
            #cascade to the left
            for col in range(pCol-1, 0, -1):
                #Starts with max column
                #ends with col 1
                cube = self.cubes[startRow][col]
                self.cubes[startRow][col+1].setState(cube.getState())
            #Finally put the cube on the left edge to the game state
            self.cubes[startRow][1].setState(self.state)
        elif startCol == self.maxcols+1:
            #Right row shift left
            print('Left Shift')
            #Start with the one to the right of the picked up cube
            #and move its value to the picked up cube
            #cascade to the right
            for col in range(pCol+1, self.maxcols+1):
                cube = self.cubes[startRow][col]
                self.cubes[startRow][col-1].setState(cube.getState())
            #Finally put the cube on the right to the game state
            self.cubes[startRow][self.maxcols].setState(self.state)
        self.turnCount += 1
        self.state = self.states[self.turnCount%2]
        self.pickedUpCube = None
        self.droppedPoint = None
        self.currentPlayer = self.players[self.turnCount%2]
        #self.gameover = self.checkIfWon()
        self.save()
        return self.gameover

    def checkIfWon(self):
        '''Checks for rows, cols, or diaganols full of X's or O's'''
        print('Checking Win')
        xwon = False
        ywon = False
        for row in range(1, self.maxrows+1):
            startCube = self.cubes[row][1]
            if startCube:
                state = startCube.getState()
                if state:
                    for col in range(1, self.maxcols+1):
                        cube = self.cubes[row][col]
                        if not cube.compareState(startCube):
                            break
                    else:
                        #Won on a row!
                        if state == 'X':
                            xwon = True
                        else:
                            ywon = True
        for col in range(1, self.maxcols+1):
            startCube = self.cubes[1][col]
            if startCube:
                state = startCube.getState()
                if state:
                    for row in range(1, self.maxrows+1):
                        cube = self.cubes[row][col]
                        if not cube.compareState(startCube):
                            break
                    else:
                        #Won on a column!
                        if state == 'X':
                            xwon = True
                        else:
                            ywon = True
        #Diaganol Check
        startcube = self.cubes[1][1]
        if startcube:
            state = startCube.getState()
            if state:
                for diag in range(1, self.maxrows+1):
                    cube = self.cubes[diag][diag]
                    if not cube.compareState(startcube):
                        break
                else:
                    #Won a diaganol
                    if state == 'X':
                        xwon = True
                    else:
                        ywon = True
        startcube = self.cubes[self.maxrows][1]
        if startcube:
            state = startCube.getState()
            if state:
                for diag in range(1, self.maxrows+1):
                    cube = self.cubes[self.maxrows+1-diag][diag]
                    if not cube.compareState(startcube):
                        break
                else:
                    #Won a diagaonl
                    if state == 'X':
                        xwon = True
                    else:
                        ywon = True
        #Now that we have who may have won we need to set the winner or not
        if xwon:
            if ywon:
                return 'Tie!'
            else:
                return 'X'
        else:
            if ywon:
                return 'O'


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
