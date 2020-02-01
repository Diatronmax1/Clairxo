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
    def __init__(self, gamepath, player1, player2):
        self.players = [player1, player2]
        self.currentPlayer = self.players[0]
        self.gamePath = gamepath
        time = dt.datetime.now()
        self.filename = time.strftime("%d%m%Y") + self.players[0][:-1] + self.players[1][:-1]
        self.maxwidth = 5
        self.cubes = np.ndarray(shape=(self.maxwidth+2,self.maxwidth+2), dtype=object)
        for row in range(1, self.maxwidth+1):
            for col in range(1, self.maxwidth+1):
                edge = False
                if row==1 or row==self.maxwidth or col==1 or col==self.maxwidth:
                    edge = True
                self.cubes[row][col] = Cube(row, col, edge)
        self.states = ['X', 'O']
        self.state = self.states[0]
        self.turnCount = 0
        self.dropPoints = []
        self.droppedPoint = None
        self.pickedUpCube = None
        self.gameover = False
        self.chatText = ''
        self.save()

    def addMessage(self, player, newmessage):
        msg = '-'+ player
        msg += newmessage + '\n\n'
        self.chatText += msg
        self.save()

    def setChat(self, chat):
        self.chatText = chat
        self.save()

    def getChat(self):
        return self.chatText

    def getFileName(self):
        return self.filename

    def getCubes(self):
        return self.cubes

    def getSaveFile(self):
        return os.path.join(self.gamePath, self.filename + '.gtp')

    def getPlayerOne(self):
        return self.players[0]

    def getPlayerTwo(self):
        return self.players[1]

    def gameOver(self):
        return self.gameover

    def getCurrentPlayer(self):
        return self.currentPlayer

    def getState(self):
        return self.state

    def getDropPoints(self):
        return self.dropPoints

    def removeCurrentGame(self):
        self.config.removeCurrentGame()

    def getDroppedPoint(self):
        return self.droppedPoint

    def setDroppedPoint(self, x, y):
        self.droppedPoint = (x, y)

    def getPickedUpCube(self):
        return self.pickedUpCube

    def cancelPickedUp(self):
        self.pickedUpCube.revertState()
        self.pickedUpCube = None
        self.droppedPoint = None

    def save(self):
        '''Saves in the game folder'''
        savefile = os.path.join(self.gamePath, self.filename)
        with open(savefile + '.gtp', 'wb') as gfile:
            pickle.dump(self, gfile)

    def passTurn(self):
        #Move the dropped block into the grid shifting all of the cubes.
        #Determine whether the shift is a row or column shift
        startRow, startCol = self.droppedPoint
        puc = self.getPickedUpCube()
        pRow, pCol = puc.getPos()
        if startRow == 0:
            #Top Row, shift down a column
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
        elif startRow == self.maxwidth+1:
            #Bottom row, shift up
            #Start with right below the picked up cubes location
            #and move that state into where the picked up cube was
            #cascade down to the bottom.
            for row in range(pRow+1, self.maxwidth+1):
                cube = self.cubes[row][startCol]
                self.cubes[row-1][startCol].setState(cube.getState())
            #Then row 6 needs the new game state added to its cube
            self.cubes[self.maxwidth][startCol].setState(self.state)
        elif startCol == 0:
            #Left row shift right
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
        elif startCol == self.maxwidth+1:
            #Right row shift left
            #Start with the one to the right of the picked up cube
            #and move its value to the picked up cube
            #cascade to the right
            for col in range(pCol+1, self.maxwidth+1):
                cube = self.cubes[startRow][col]
                self.cubes[startRow][col-1].setState(cube.getState())
            #Finally put the cube on the right to the game state
            self.cubes[startRow][self.maxwidth].setState(self.state)
        self.turnCount += 1
        self.pickedUpCube = None
        self.droppedPoint = None
        self.state = self.states[self.turnCount%2]
        self.currentPlayer = self.players[self.turnCount%2]
        self.gameover = self.checkIfWon()
        self.save()
        return self.gameover

    def checkIfWon(self):
        '''Checks for rows, cols, or diaganols full of X's or O's'''
        xwon = False
        ywon = False
        #Check from row 1 to maxwidth
        for row in range(1, self.maxwidth+1):
            #Grab the first cube in the row's state
            state = self.cubes[row][1].getState()
            #If its none don't check the row, its not full yet
            if state:
                #Go through each cube in the row not including the first
                #and see if its the same
                #2 to maxwidth
                for col in range(2, self.maxwidth+1):
                    #Get the state of that cube
                    colstate = self.cubes[row][col].getState()
                    if state != colstate:
                        #Dont continue this row doesnt have all of the 
                        #same sate
                        break
                #If we reached the end and didnt break it was a full
                #row of the same
                else:
                    #Won on a row!
                    if state == 'X':
                        xwon = True
                    else:
                        ywon = True
        #Check from column 1 through maxwidth
        for col in range(1, self.maxwidth+1):
            #Grab the first cube in the rows state
            state = self.cubes[1][col].getState()
            #Verify the state is not None
            if state:
                #Go through each column not including the first
                #and see if tis the same
                for row in range(2, self.maxwidth+1):
                    rowstate = self.cubes[row][col].getState()
                    if state != rowstate:
                        break
                #If you reach the end of a column and they're all the 
                #same you won on a column
                else:
                    #Won on a column!
                    if state == 'X':
                        xwon = True
                    else:
                        ywon = True
        #Diagonol Check
        state = self.cubes[1][1].getState()
        #Check it isn't none
        if state:
            for diag in range(2, self.maxwidth+1):
                diagstate = self.cubes[diag][diag].getState()
                if state != diagstate:
                    break
            #If you reach the end of the diaganol and 
            #they the same you won on a diaganol
            else:
                #Won a diaganol
                if state == 'X':
                    xwon = True
                else:
                    ywon = True
        #Start from bottom left
        state = self.cubes[self.maxwidth][1].getState()
        if state:
            for diag in range(2, self.maxwidth+1):
                diagstate = self.cubes[self.maxwidth+1-diag][diag].getState()
                if state != diagstate:
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
                return self.players[0]
        else:
            if ywon:
                return self.players[1]
            else:
                return None

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
        south = self.maxwidth+1
        east = self.maxwidth+1
        west = 0
        row, col = gamecube.getPos()
        if row == 1:
            #On a northern edge
            self.dropPoints.append((south, col))
            if col == 1:
                #North West Corner
                self.dropPoints.append((row, east))
            elif col == self.maxwidth:
                #North East Corner
                self.dropPoints.append((row, west))
            else:
                #Northern Edge
                self.dropPoints.append((row, west))
                self.dropPoints.append((row, east))
        elif row == self.maxwidth:
            #On a southern edge
            self.dropPoints.append((north, col))
            if col == 1:
                #South West Corner
                self.dropPoints.append((row, east))
            elif col == self.maxwidth:
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
            elif col == self.maxwidth:
                #Eastern Edge
                self.dropPoints.append((row, west))
                self.dropPoints.append((north, col))
                self.dropPoints.append((south, col))
        return self.dropPoints
