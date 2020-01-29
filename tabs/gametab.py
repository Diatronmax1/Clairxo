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
    def __init__(self, x, y):
        super().__init__()
        self.setAcceptDrops(True)
        self.setFixedSize(75, 75)
        self.setStyleSheet('background-color:blue')
        self.x = x
        self.y = x
        self.validDrop = False

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
        return
        if self.edge and self.model.validDrop(self.x, self.y):
            self.model.changeTurn()
            self.setText(e.mimeData().text())

    def reset(self):
        self.setText('Empty')

class CubeWidget(QPushButton):
    def __init__(self, gamecube):
        super().__init__()
        if gamecube.state:
            self.setText(gamecube.state)
        self.setStyleSheet('background-color:brown')
        self.setFixedSize(75, 75)
        self.signals = ButtonSignals()
    
    def mouseMoveEvent(self, e):
        if e.buttons() != Qt.RightButton:
            return
        self.setText('Moving!')
        #self.signals.selected.emit(self.x, self.y)
        mimeData = QMimeData()
        mimeData.setText('X')
        drag = QDrag(self)
        drag.setMimeData(mimeData)
        drag.setHotSpot(e.pos())
        dropAction = drag.exec_(Qt.MoveAction)

    def mousePressEvent(self, e):
        super().mousePressEvent(e)

        if e.button() == Qt.LeftButton:
            print('press')

    def reset(self):
        self.setText('')

class GameTab(QWidget):
    def __init__(self, client, gamemodel, statusbar):
        super().__init__()
        self.client = client
        self.gamemodel = gamemodel
        self.statusbar = statusbar
        self.statusbar.showMessage('Your Turn!')
        self.signals = WorkerSignals()
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
                if gamecube is not None:
                    newCube = CubeWidget(gamecube)
                    layout.addWidget(newCube, gamecube.x, gamecube.y)
                else:
                    newSquare = SquareWidget(idx, idy)
                    layout.addWidget(newSquare, idx, idy)
        layout = QVBoxLayout(self)
        layout.addWidget(gameArea)
        layout.addWidget(self.endgamebut)
        # idx = 0
        # self.squares = {}
        # for x in range(7):
        #     for y in range(7):
        #         if x == 0 or x == 6 or y == 0 or y == 6:
        #             edge = True
        #         else:
        #             edge = False
        #         self.currentSquare = Square('Empty', self, self.gamemodel, x, y, edge)
        #         self.squares[str(idx)] = self.currentSquare
        #         idx += 1
        #         layout.addWidget(self.currentSquare, x, y)
        # idx = 0
        # self.cubes = {}
        # for x in range(1, 6):
        #     for y in range(1, 6):
        #         if x == 1 or x==5 or y==1 or y==5:
        #             edge = True
        #         else:
        #             edge = False
        #         self.currentCube = Cube(' ', self, self.gamemodel, x, y, edge)
        #         self.currentCube.signals.selected.connect(self.pickedUp)
        #         self.cubes[str(idx)] = self.currentCube
        #         idx += 1
        #         layout.addWidget(self.currentCube, x, y)
        # layout.addWidget(self.endgamebut, 7, 0, 1, 7)
        self.setAcceptDrops(True)

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
        print(e.mimeData().text())
        position = e.pos()
        #self.cube.move(position)
        e.setDropAction(Qt.MoveAction)
        e.accept()

    def endGame(self):
        self.signals.finished.emit()