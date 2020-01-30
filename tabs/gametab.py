from PyQt5.QtCore import Qt, QMimeData, pyqtSignal, QObject, QThreadPool, QRunnable
from PyQt5.QtGui import QDrag, QPixmap, QPalette, QBrush
from PyQt5.QtWidgets import (QFileDialog, QGridLayout, QGroupBox, QHBoxLayout, QInputDialog, 
                             QLabel, QListWidget, QListWidgetItem, QLineEdit, QPushButton, QProgressBar, 
                             QRadioButton, QTextEdit, QVBoxLayout, QMessageBox, QWidget)
import time
import numpy as np
import pickle

class WorkerSignals(QObject):
    finished = pyqtSignal()
    notify = pyqtSignal(object)

class ButtonSignals(QObject):
    pickedUp = pyqtSignal(object)
    receievedCube = pyqtSignal(int, int)
    cancelSelection = pyqtSignal()

class GameMonitor(QRunnable):
    def __init__(self, client, *args, **kwargs):
        super().__init__()
        self.signals = WorkerSignals()
        self.client = client
        self.working = True

    def run(self):
        self.working = True
        while self.working:
            try:
                with open(self.client.getCurrentGame(), 'rb') as gfile:
                    gamemodel = pickle.load(gfile)
                    if gamemodel.getCurrentPlayer() == self.client.getUserName():
                        self.signals.notify.emit(gamemodel)
                        self.working = False
            except:
                pass
            time.sleep(1)

    def end(self):
        self.working = False

class SquareWidget(QPushButton):
    '''Squares are initially blank but can receive cubes
    temporarily as a way to indicate the intent of moving a
    block from the square into the game
    They also are a visual indicator of the valid drop sites
    that a cube can be placed'''
    def __init__(self, client, gamemodel, x, y, maxX, maxY):
        super().__init__()
        self.client = client
        self.gamemodel = gamemodel
        self.gamecube = None
        self.signals = ButtonSignals()
        self.setAcceptDrops(True)
        self.setFixedSize(75, 75)
        self.validDrop = False
        self.x = x
        self.y = y
        self.maxX = maxX
        self.maxY = maxY
        self.style()

    def setGameModel(self, gamemodel):
        self.gamemodel = gamemodel

    def style(self, background='blue', font='16pt Times New Roman'):
        if self.gamecube:
            name = self.gamemodel.getState()
            if self.x == 0 and (self.y != 0 or self.y != self.maxY):
                #Top Row, arrow should point down
                self.setText(name + '\nv')
            elif self.x == self.maxX and (self.y != 0 and self.y != self.maxY):
                #Bottom Row, arrow should point up
                self.setText('^\n' + name)
            elif self.y == 0:
                #Left edge, arrow should point right
                self.setText(name + ' >')
            elif self.y == self.maxY:
                #Right edge arrow should point left
                self.setText('< ' + name)
        else:
            self.setText('')
        if self.validDrop and background=='blue':
            background='green'
        self.setStyleSheet("background-color:" + background + ";"
                           "font: " + font + ";")

    def mouseMoveEvent(self, e):
        '''Alerts the widget that a cube has been picked up'''
        if e.buttons() != Qt.RightButton or not self.gamecube:
            return
        if self.client.getUserName() != self.gamemodel.getCurrentPlayer():
            return
        self.signals.pickedUp.emit(self.gamecube)
        mimeData = QMimeData()
        mimeData.setText(str(self.gamecube))
        drag = QDrag(self)
        drag.setMimeData(mimeData)
        drag.setHotSpot(e.pos())
        dropAction = drag.exec_(Qt.MoveAction)
        self.gamecube = None
        self.style()

    def dragEnterEvent(self, e):
        '''If a drag object enters the square
        accept the drop regardless of what it is'''
        e.accept()
        self.style(background='white')

    def dragLeaveEvent(self, e):
        self.style()

    def dropEvent(self, e):
        '''If the drag object drops its payload, and the 
        square is receiving drops request the gamemodel to 
        provide a game cube matching the payload's string 
        parameter'''
        #print('Received Drop: ' + e.mimeData.text())
        if self.validDrop:
            self.gamecube = self.gamemodel.getPickedUpCube()
            self.signals.receievedCube.emit(self.x, self.y)
        else:
            self.gamemodel.cancelPickedUp()
        self.style()

    def setValidDrop(self, state):
        self.validDrop = state
        self.style()
          
    def reset(self):
        self.gamecube = None
        self.validDrop = False
        self.style()

    def refresh(self):
        self.style()

    def resizeEvent(self, event):
        self.resize(self.width(), self.height())

class CubeWidget(QPushButton):
    '''Cubes widgets store their gamecubes and show the states
    they also alert the model that they have been picked up'''
    def __init__(self, client, gamemodel, gamecube):
        super().__init__()
        self.setAcceptDrops(True)
        self.client = client
        self.gamemodel = gamemodel
        self.gamecube = gamecube
        self.selected = False
        self.signals = ButtonSignals()
        self.setFixedSize(75, 75)
        self.style()

    def setGameCube(self, gamemodel, gamecube):
        self.gamemodel = gamemodel
        self.gamecube = gamecube
    
    def style(self, background='brown', font='28pt Times New Roman'):
        if self.gamecube:
            state = self.gamecube.getState()
            if state:
                self.setText(state)
            else:
                self.setText('')
        if self.selected:
            self.setText('| |')
            background = 'pink'
        self.setStyleSheet("background-color:" + background + ";"
                           "font: " + font + ";")
    
    def mouseMoveEvent(self, e):
        '''If the cubes is not an edge cube it cannot be picked up
        additionally, it cannot be picked up if there is already a cube
        picked up
        '''
        if e.buttons() != Qt.RightButton or not self.gamecube.edge:
            #print('Edge Cube?: ' + str(self.gamecube.edge))
            return
        #Make sure there arent picked up cubes already on the board
        pc = self.gamemodel.getPickedUpCube()
        if pc:
            if self.gamecube != pc:
                #print('still a picked up cube on the board')
                return
        #Make sure there arent cubes waiting in drop zones
        dp = self.gamemodel.getDroppedPoint()
        if dp:
            #print('still a dropped cube in waiting zone')
            return
        #Make sure you are allowed to pick up this cube type
        state = self.gamecube.getState()
        if state:
            if state != self.gamemodel.getState():
                return
        #Ensure you can be playing right now
        if self.client.getUserName() != self.gamemodel.getCurrentPlayer():
            return
        self.signals.pickedUp.emit(self.gamecube)
        self.selected = True
        mimeData = QMimeData()
        mimeData.setText(str(self.gamecube))
        drag = QDrag(self)
        drag.setMimeData(mimeData)
        drag.setHotSpot(e.pos())
        dropAction = drag.exec_(Qt.MoveAction)
        self.style()

    def deSelect(self):
        self.selected = False

    def dragEnterEvent(self, e):
        e.accept()

    def dragLeaveEvent(self, e):
        self.style()

    def dropEvent(self, e):
        '''Intent of dropping on a cube must be to cancel the move'''
        self.selected = False
        self.signals.cancelSelection.emit()
        self.style()

    def reset(self):
        self.selected = False
        self.style()

    def refresh(self):
        self.style()

class GameTab(QWidget):
    def __init__(self, client, gamemodel, statusbar):
        super().__init__()
        self.threadpool = QThreadPool()
        self.client = client
        self.gamemodel = gamemodel
        self.statusbar = statusbar
        self.gameMonitor = None
        if self.client.getUserName() == self.gamemodel.getCurrentPlayer():
            self.statusbar.showMessage('Your Turn!')
        else:
            self.statusbar.showMessage(self.gamemodel.getCurrentPlayer() + '\'s turn')
            self.gameMonitor = GameMonitor(self.client)
            self.gameMonitor.signals.notify.connect(self.reloadGame)
            self.threadpool.start(self.gameMonitor)
        self.signals = WorkerSignals()
        self.passTurnBut = QPushButton('Accept and Pass Turn')
        self.passTurnBut.setEnabled(False)
        self.passTurnBut.clicked.connect(self.passTurn)
        self.endgamebut = QPushButton('End Game')
        self.endgamebut.clicked.connect(self.endGame)
        #Development
        gameArea = QWidget()
        layout = QGridLayout(gameArea)
        #Make the outer layer of Squares
        self.squares = []
        self.cubes = np.ndarray(shape=(8,8), dtype=object)
        maxrows = self.gamemodel.maxrows
        maxcols = self.gamemodel.maxcols
        for idx, row in enumerate(self.gamemodel.getCubes()):
            for idy, gamecube in enumerate(row):
                if gamecube is not None:
                    newCube = CubeWidget(self.client, self.gamemodel, gamecube)
                    newCube.signals.pickedUp.connect(self.pickedUp)
                    newCube.signals.cancelSelection.connect(self.cancelMove)
                    self.cubes[idx][idy] = newCube
                    layout.addWidget(newCube, gamecube.x, gamecube.y)
                else:
                    if idx == 0 and idy == 0:
                        continue
                    elif idx == maxrows+1 and idy == 0:
                        continue
                    elif idx == 0 and idy == maxcols+1:
                        continue
                    elif idx == maxrows+1 and idy == maxcols+1:
                        continue
                    else:
                        newSquare = SquareWidget(self.client, self.gamemodel, idx, idy, maxrows+1, maxcols+1)
                        newSquare.signals.receievedCube.connect(self.queueDrop)
                        newSquare.signals.pickedUp.connect(self.pickedUp)
                        self.squares.append(newSquare)
                        layout.addWidget(newSquare, idx, idy)
        layout = QVBoxLayout(self)
        layout.addWidget(gameArea)
        layout.addWidget(self.passTurnBut)
        layout.addWidget(self.endgamebut)
        self.setAcceptDrops(True)

    def reloadGame(self, newgamemodel):
        self.gamemodel = newgamemodel
        for idx, row in enumerate(self.gamemodel.getCubes()):
            for idy, gamecube in enumerate(row):
                if gamecube is not None:
                    self.cubes[idx][idy].setGameCube(self.gamemodel, gamecube)
                    self.cubes[idx][idy].reset()
        for square in self.squares:
            square.setGameModel(self.gamemodel)
            square.reset()
        #self.pingUser()
        self.refresh()

    def pingUser(self):
        msgWidget = QMessageBox()
        msgWidget.setIcon(QMessageBox.Critical)
        msg = 'Your move!'
        msgWidget.setText(msg)
        msgWidget.setWindowTitle('Alert')
        msgWidget.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        msgWidget.exec_()

    def reset(self):
        self.gamemodel.reset()
        for square in self.squares:
            square.reset()
        for row in self.cubes:
            for cube in row:
                if cube:
                    cube.reset()

    def refresh(self):
        #If its your turn we can turn off the game monitor
        if self.client.getUserName() == self.gamemodel.getCurrentPlayer():
            if self.gamemodel.gameOver():
                self.winCondition(False)
                return
            else:
                self.statusbar.showMessage('Your Turn!')
        else:
            self.statusbar.showMessage(self.gamemodel.getCurrentPlayer() + '\'s turn')
        for row in self.cubes:
            for cube in row:
                if cube:
                    cube.refresh()
        for square in self.squares:
            square.refresh()

    def passTurn(self):
        '''Should clear the squares of their cubes and move the turn'''
        self.passTurnBut.setEnabled(False)
        won = self.gamemodel.passTurn()
        #Spawn the monitor
        for square in self.squares:
            square.reset()
        for row in self.cubes:
            for cube in row:
                if cube:
                    cube.reset()
        if won:
            self.statusbar.showMessage('You Win!')
            self.winCondition()
            return
        self.refresh()
        self.gameMonitor = GameMonitor(self.client)
        self.gameMonitor.signals.notify.connect(self.reloadGame)
        self.threadpool.start(self.gameMonitor)
        
    def pickedUp(self, gamecube):
        print('Picked Up: ' + str(gamecube))
        dropPoints = self.gamemodel.updateDrops(gamecube)
        for point in dropPoints:
            for square in self.squares:
                if point[0] == square.x and point[1] == square.y:
                    square.setValidDrop(True)

    def cancelMove(self):
        print('Canceling move')
        self.passTurnBut.setEnabled(False)
        self.gamemodel.cancelPickedUp()
        dropPoints = self.gamemodel.getDropPoints()
        for point in dropPoints:
            for square in self.squares:
                if point[0] == square.x and point[1] == square.y:
                    square.setValidDrop(False)
        for row in self.cubes:
            for cube in row:
                if cube:
                    cube.deSelect()
        self.refresh()
        
    def queueDrop(self, x, y):
        '''Alert the game model that a square now has a valid
        dropped cube'''
        self.gamemodel.setQueueDrop(x, y)
        self.passTurnBut.setEnabled(True)

    def winCondition(self, won=True):
        msgWidget = QMessageBox()
        msgWidget.setIcon(QMessageBox.Critical)
        if won:
            msg = 'You Won!'
        else:
            msg = 'You Lost!'
        msgWidget.setText(msg)
        msgWidget.setWindowTitle('Alert')
        msgWidget.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        msgWidget.exec_()
        self.endGame()

    def endGame(self):
        if self.gameMonitor:
            self.gameMonitor.end()
        self.signals.finished.emit()