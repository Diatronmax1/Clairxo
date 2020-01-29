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
    selected = pyqtSignal(int, int)
    targeted = pyqtSignal(int, int)

class SquareWidget(QPushButton):
    def __init__(self, gamemodel, x, y):
        super().__init__()
        self.gamemodel = gamemodel
        self.setAcceptDrops(True)
        self.setFixedSize(75, 75)
        self.setStyleSheet('background-color:blue')
        self.x = x
        self.y = x

    def resizeEvent(self, event):
        self.resize(self.width(), self.height())

    def dragEnterEvent(self, e):
        self.setStyleSheet('background-color:white')
        if e.mimeData().hasFormat('text/plain'):
            self.setText(e.mimeData().text())
            e.accept()
        else:
            e.ignore()

    def dragLeaveEvent(self, e):
        self.setStyleSheet('background-color:blue')
        self.setText('')

    def dropEvent(self, e):
        self.gamemodel.acceptDrop(self.x, self.y)
        self.setText(e.mimeData().text())

    def reset(self):
        self.setText('')
        self.setStyleSheet('background-color:blue')

class CubeWidget(QPushButton):
    def __init__(self, gamecube):
        super().__init__()
        self.gamecube = gamecube
        if gamecube.state:
            self.setText(gamecube.state)
        self.style()
        self.setFixedSize(75, 75)
        self.signals = ButtonSignals()
    
    def mouseMoveEvent(self, e):
        if e.buttons() != Qt.RightButton:
            return
        self.style(background='green')
        mimeData = QMimeData()
        mimeData.setText('X')
        drag = QDrag(self)
        drag.setMimeData(mimeData)
        drag.setHotSpot(e.pos())
        dropAction = drag.exec_(Qt.MoveAction)

    def style(self, background='brown', font='30pt Comic Sans MS'):
        self.setStyleSheet("background-color:" + background + ";"
                           "font: " + font + ";"
                           )

    def mousePressEvent(self, e):
        super().mousePressEvent(e)

        if e.button() == Qt.LeftButton:
            print('press')

    def reset(self):
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
        self.passTurnBut.clicked.connect(self.passTurn)
        self.endgamebut = QPushButton('End Game')
        self.endgamebut.clicked.connect(self.endGame)
        self.refreshBut = QPushButton('Refresh')
        self.refreshBut.clicked.connect(self.refresh)
        gameArea = QWidget()
        layout = QGridLayout(gameArea)
        #Make the outer layer of Squares
        cubes = self.gamemodel.getCubes()
        for idx, row in enumerate(cubes):
            for idy, gamecube in enumerate(row):
                if idx == 0 and idy == 0:
                    continue
                elif idx == 7 and idy == 0:
                    continue
                elif idx == 0 and idy == 7:
                    continue
                elif idx == 7 and idy == 7:
                    continue
                elif gamecube is not None:
                    newCube = CubeWidget(gamecube)
                    layout.addWidget(newCube, gamecube.x, gamecube.y)
                else:
                    newSquare = SquareWidget(self.gamemodel, idx, idy)
                    layout.addWidget(newSquare, idx, idy)
        layout = QVBoxLayout(self)
        layout.addWidget(gameArea)
        layout.addWidget(self.passTurnBut)
        layout.addWidget(self.endgamebut)
        self.setAcceptDrops(True)

    def passTurn(self):
        turn = self.gamemodel.passTurn()
        self.statusbar.showMessage('Current Turn Count: ' + str(turn))
        #self.client.passTurn()

    def refresh(self):
        print('refreshing')

    def pickedUp(self, x, y):
        dropPoints = self.gamemodel.updateDrops(x, y)
        for point in dropPoints:
            index = point.getIndex()
            self.squares[str(index)].setText('Marked')

    def reset(self):
        self.gamemodel.reset()
        for square in self.squares.values():
            square.reset()
        for cube in self.cubes.values():
            cube.reset()

    def currentState(self):
        return self.currentState
        
    def dragEnterEvent(self, e):
        e.accept()

    def dropEvent(self, e):
        #Handles the drop information for 
        #The dropped cube
        print(e.mimeData().text())
        position = e.pos()
        #self.cube.move(position)
        e.setDropAction(Qt.MoveAction)
        e.accept()

    def endGame(self):
        self.signals.finished.emit()

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