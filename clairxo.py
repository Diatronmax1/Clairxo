#!/usr/bin/env python3
#Author Chris Lambert
from PyQt5.QtCore import QThread, QObject
from PyQt5.QtWidgets import (QMainWindow, QAction, QApplication, qApp, QLabel, QFileDialog,
                             QTabWidget, QWidget)
import sys
from panel import HomeScreen
from client import Client

class Clairxo(QMainWindow):
    
    def __init__(self, size):
        super().__init__()
        self.client = Client()
        self.mainwindow = HomeScreen(self.client, self.statusBar(), self)
        self.mainwindow.initialize()
        self.setCentralWidget(self.mainwindow)
        self.setWindowTitle('CLAIRXO')
        self.setGeometry(650, 200, 600, 600)
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
        ex.client.goOffline()