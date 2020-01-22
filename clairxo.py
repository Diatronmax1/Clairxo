#!/usr/bin/env python3
#Author Chris Lambert
from PyQt5.QtCore import QThread, QObject
from PyQt5.QtWidgets import (QMainWindow, QAction, QApplication, qApp, QLabel, QFileDialog,
                             QTabWidget, QWidget)
import sys
from panel import Panel
from gamemodel import GameModel

class Clairxo(QMainWindow):
    
    def __init__(self, size):
        super().__init__()
        self.gamemodel = GameModel()
        self.mainwindow = Panel(self.gamemodel, self.statusBar(), self)
        self.setCentralWidget(self.mainwindow)
        self.setWindowTitle('CLAIRXO')
        self.setGeometry(300, 300, 300, 150)
        self.show()
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    screen = app.primaryScreen()
    size = screen.size()
    ex = Clairxo(size)
    try:
        sys.exit(app.exec_())
    except:
        pass
    finally:
        ex.gamemodel.goOffline()