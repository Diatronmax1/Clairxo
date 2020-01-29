from PyQt5.QtCore import Qt, QMimeData, pyqtSignal, QObject, QThreadPool, QRunnable
from PyQt5.QtGui import QDrag, QPixmap, QPalette, QBrush
from PyQt5.QtWidgets import (QFileDialog, QGridLayout, QGroupBox, QHBoxLayout, QInputDialog, 
                             QLabel, QListWidget, QListWidgetItem, QLineEdit, QPushButton, QProgressBar, 
                             QRadioButton, QTextEdit, QVBoxLayout, QWidget)
import time
import numpy as np

class WorkerSignals(QObject):
    finished = pyqtSignal()

class ButtonSignals(QObject):
    pickedUp = pyqtSignal(int, int)
    cancelMove = pyqtSignal()
    droppedOn = pyqtSignal()
    targeted = pyqtSignal(int, int)

class SquareWidget(QPushButton):
    def __init__(self, gamemodel, x, y):
        super().__init__()
        self.gamemodel = gamemodel
        self.signals = ButtonSignals()
        self.setAcceptDrops(True)
        self.setFixedSize(75, 75)
        self.validDrop = False
        self.isblocked = False
        self.squareText = ''
        self.x = x
        self.y = y
        self.style()

    def block(self, state=True):
        '''Prevents all interactions unless it is a valid drop'''
        if state:
            if not self.validDrop:
                self.isblocked = state
        else:
            self.isblocked = state
        self.style()

    def mouseMoveEvent(self, e):
        if e.buttons() != Qt.RightButton or not self.squareText:
            return
        mimeData = QMimeData()
        mimeData.setText(self.squareText)
        self.squareText = ''
        self.style()
        drag = QDrag(self)
        drag.setMimeData(mimeData)
        drag.setHotSpot(e.pos())
        dropAction = drag.exec_(Qt.MoveAction)

    def style(self, background='blue', font='22pt Comic Sans MS'):
        if self.validDrop:
            background='green'
        self.setStyleSheet("background-color:" + background + ";"
                           "font: " + font + ";"
                           )

    def setValidDrop(self, state):
        if not self.isblocked:
            self.validDrop = state
            self.style()

    def resizeEvent(self, event):
        self.resize(self.width(), self.height())

    def dragEnterEvent(self, e):
        if not self.isblocked:
            self.style(background = 'white')
            if e.mimeData().hasFormat('text/plain'):
                e.accept()
            else:
                e.ignore()

    def dragLeaveEvent(self, e):
        self.style()
        self.setText('')

    def dropEvent(self, e):
        if self.validDrop:
            self.gamemodel.acceptDrop(self.x, self.y)
            self.squareText = e.mimeData().text()
            if len(self.squareText) > 1:
                if self.squareText.find('X') > -1:
                    self.squareText = 'X'
                else:
                    self.squareText = 'Y'
            if self.x == 0 and (self.y != 0 or self.y != 7):
                #Top Row, arrow should point down
                self.squareText += '\nv'
            elif self.x == 7 and (self.y != 0 and self.y != 7):
                #Bottom Row, arrow should point up
                self.squareText = '^\n' + self.squareText
            elif self.y == 0:
                #Left edge, arrow should point right
                self.squareText = self.squareText + '>'
            elif self.y == 7:
                self.squareText = '<' + self.squareText
            self.setText(self.squareText)
        else:
            self.gamemodel.rejectDrop()
        self.style()
        self.signals.droppedOn.emit()
        
    def reset(self):
        self.setText('')
        self.validDrop = False
        self.style()

class CubeWidget(QPushButton):
    def __init__(self, gamecube):
        super().__init__()
        self.setAcceptDrops(True)
        self.gamecube = gamecube
        self.pickedUp = False
        self.isblocked = False
        if gamecube.state:
            self.setText(gamecube.state)
        self.style()
        self.setFixedSize(75, 75)
        self.signals = ButtonSignals()
    
    def mouseMoveEvent(self, e):
        if e.buttons() != Qt.RightButton or not self.gamecube.edge or self.isblocked:
            return
        self.pickedUp = True
        self.style()
        self.signals.pickedUp.emit(self.gamecube.x, self.gamecube.y)
        mimeData = QMimeData()
        mimeData.setText('X')
        drag = QDrag(self)
        drag.setMimeData(mimeData)
        drag.setHotSpot(e.pos())
        dropAction = drag.exec_(Qt.MoveAction)

    def style(self, background='brown', font='30pt Comic Sans MS'):
        if self.pickedUp:
            background = 'pink'
            self.setText('')
        self.setStyleSheet("background-color:" + background + ";"
                           "font: " + font + ";"
                           )

    def mousePressEvent(self, e):
        super().mousePressEvent(e)
        if e.button() == Qt.LeftButton:
            print('press')

    def dragEnterEvent(self, e):
        e.accept()

    def dropEvent(self, e):
        #Intent must be to cancel the move, so remove the 
        #valid drops and refresh the model
        self.pickedUp = False
        self.signals.cancelMove.emit()
        self.setText(self.gamecube.state)
        self.style()

    def block(self, state=True):
        '''Should only block cubes that arent the active cube'''
        if not self.pickedUp:
            self.isblocked = state

    def reset(self):
        self.isblocked = False
        self.pickedUp = False
        if self.gamecube.state:
            self.setText(self.gamecube.state)
        else:
            self.setText('')
        self.style()

class GameTab(QWidget):
    def __init__(self, client, gamemodel, statusbar):
        super().__init__()
        self.client = client
        self.gamemodel = gamemodel
        self.statusbar = statusbar
        self.statusbar.showMessage('Your Turn!')
        self.signals = WorkerSignals()
        self.passTurnBut = QPushButton('Accept and Pass Turn')
        self.passTurnBut.setEnabled(False)
        self.passTurnBut.clicked.connect(self.passTurn)
        self.endgamebut = QPushButton('End Game')
        self.endgamebut.clicked.connect(self.endGame)
        #Development
        self.resetBut = QPushButton('Reset Game')
        self.resetBut.clicked.connect(self.reset)
        gameArea = QWidget()
        layout = QGridLayout(gameArea)
        #Make the outer layer of Squares
        gamecubes = self.gamemodel.getCubes()
        self.squares = []
        self.cubes = []
        for idx, row in enumerate(gamecubes):
            for idy, gamecube in enumerate(row):
                if gamecube is not None:
                    newCube = CubeWidget(gamecube)
                    newCube.signals.pickedUp.connect(self.pickedUp)
                    newCube.signals.cancelMove.connect(self.cancelMove)
                    self.cubes.append(newCube)
                    layout.addWidget(newCube, gamecube.x, gamecube.y)
                else:
                    if idx == 0 and idy == 0:
                        continue
                    elif idx == 7 and idy == 0:
                        continue
                    elif idx == 0 and idy == 7:
                        continue
                    elif idx == 7 and idy == 7:
                        continue
                    else:
                        newSquare = SquareWidget(self.gamemodel, idx, idy)
                        newSquare.signals.droppedOn.connect(self.blockCubes)
                        self.squares.append(newSquare)
                        layout.addWidget(newSquare, idx, idy)
        layout = QVBoxLayout(self)
        layout.addWidget(gameArea)
        layout.addWidget(self.passTurnBut)
        layout.addWidget(self.endgamebut)
        layout.addWidget(self.resetBut)
        self.setAcceptDrops(True)

    def passTurn(self):
        turn = self.gamemodel.passTurn()
        self.statusbar.showMessage('Current Turn Count: ' + str(turn))
        #self.client.passTurn()

    def refresh(self):
        print('refreshing')

    def pickedUp(self, x, y):
        print('Picked Up: ' + str(x) + ', ' + str(y))
        dropPoints = self.gamemodel.updateDrops(x, y)
        for point in dropPoints:
            print(point)
            for square in self.squares:
                if point[0] == square.x and point[1] == square.y:
                    square.setValidDrop(True)

    def cancelMove(self):
        self.passTurnBut.setEnabled(False)
        print('Canceling move')
        dropPoints = self.gamemodel.getDropPoints()
        for point in dropPoints:
            for square in self.squares:
                if point[0] == square.x and point[1] == square.y:
                    square.setValidDrop(False)
        for cube in self.cubes:
            cube.block(False)

    def reset(self):
        self.gamemodel.reset()
        for square in self.squares:
            square.reset()
        for cube in self.cubes:
            cube.reset()

    def currentState(self):
        return self.currentState
        
    def dragEnterEvent(self, e):
        e.accept()

    def blockCubes(self):
        print('Blocking all cubes')
        if self.gamemodel.getDroppedPoint():
            self.passTurnBut.setEnabled(True)
        else:
            self.passTurnBut.setEnabled(False)
        #Block all remaining pick ups
        for cube in self.cubes:
            cube.block()

    def endGame(self):
        self.signals.finished.emit()