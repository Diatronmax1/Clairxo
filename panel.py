from PyQt5.QtCore import Qt, QMimeData, pyqtSignal, QObject
from PyQt5.QtGui import QDrag
from PyQt5.QtWidgets import (QFileDialog, QGridLayout, QGroupBox, QHBoxLayout, QInputDialog, 
                             QLabel, QListWidget, QListWidgetItem, QPushButton, QProgressBar, 
                             QRadioButton, QTextEdit, QVBoxLayout, QWidget)
import time
import numpy as np

class ButtonSignals(QObject):
    selected = pyqtSignal(int, int)
    targeted = pyqtSignal(int, int)

class Square(QPushButton):
    def __init__(self, name, parent, model, x, y, edge=False):
        super().__init__(name, parent)
        self.parent = parent
        self.setAcceptDrops(True)
        self.setFixedSize(75, 75)
        self.model = model
        self.edge = edge
        self.x = x
        self.y = x
        self.validDrop = False

    def resizeEvent(self, event):
        self.resize(self.width(), self.height())

    def dragEnterEvent(self, e):
        if e.mimeData().hasFormat('text/plain'):
            e.accept()
        else:
            e.ignore()

    def dropEvent(self, e):
        if self.edge and self.model.validDrop(self.x, self.y):
            self.model.changeTurn()
            self.setText(e.mimeData().text())

    def reset(self):
        self.setText('Empty')

class Cube(QPushButton):
    def __init__(self, name, parent, model, x, y, edge = False):
        super().__init__(name, parent)
        self.setFixedSize(75, 75)
        self.parent = parent
        self.model = model
        self.edge = edge
        self.x = x
        self.y = y
        self.signals = ButtonSignals()
    
    def mouseMoveEvent(self, e):
        if e.buttons() != Qt.RightButton or not self.edge:
            return
        self.setText('Moving!')
        self.signals.selected.emit(self.x, self.y)
        mimeData = QMimeData()
        mimeData.setText(self.model.getState())
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


class Panel(QWidget):
    def __init__(self, gamemodel, statusbar, parent):
        super().__init__(parent)
        self.gamemodel = gamemodel
        name = self.gamemodel.checkUserName()
        if not name:
            txt, okpressed = QInputDialog.getText(self, 'User Name', '')
            if okpressed and txt:
                self.gamemodel.setUserName(txt)
        self.statusbar = statusbar
        self.resetBut = QPushButton('Reset')
        self.resetBut.clicked.connect(self.reset)
        #Main View
        layout = QGridLayout(self)
        #Make the outer layer of Squares
        idx = 0
        self.squares = {}
        for x in range(7):
            for y in range(7):
                if x == 0 or x == 6 or y == 0 or y == 6:
                    edge = True
                else:
                    edge = False
                self.currentSquare = Square('Empty', self, self.gamemodel, x, y, edge)
                self.squares[str(idx)] = self.currentSquare
                idx += 1
                layout.addWidget(self.currentSquare, x, y)
        idx = 0
        self.cubes = {}
        for x in range(1, 6):
            for y in range(1, 6):
                if x == 1 or x==5 or y==1 or y==5:
                    edge = True
                else:
                    edge = False
                self.currentCube = Cube(' ', self, self.gamemodel, x, y, edge)
                self.currentCube.signals.selected.connect(self.pickedUp)
                self.cubes[str(idx)] = self.currentCube
                idx += 1
                layout.addWidget(self.currentCube, x, y)
        layout.addWidget(self.resetBut, 7, 0, 1, 7)
        self.setAcceptDrops(True)

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