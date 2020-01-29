#!/usr/bin/env python3
#Author Chris Lambert
from PyQt5.QtCore import Qt, QMimeData, pyqtSignal, QObject, QThreadPool, QRunnable
from PyQt5.QtWidgets import (QMainWindow, QAction, QApplication, qApp, QLabel, QFileDialog,
                             QTabWidget, QWidget, QVBoxLayout, QListWidget, QDialog, QPushButton)
import sys

from client import Client
from lib.gamemodel import GameModel
from tabs.gametab import GameTab
from tabs.panel import HomeScreen
import time

class WorkerSignals(QObject):
    notify = pyqtSignal()

class ClientMonitor(QRunnable):
    def __init__(self, client, *args, **kwargs):
        super().__init__()
        self.signals = WorkerSignals()
        self.client = client
        self.working = True

    def run(self):
        self.working = True
        while self.working:
            time.sleep(1)
            self.signals.notify.emit()

    def end(self):
        self.working = False

class PlayerQuery(QDialog):
    def __init__(self, client):
        super().__init__()
        self.client = client
        self.acceptBut = QPushButton('Accept')
        self.acceptBut.clicked.connect(self.testAccept)
        self.cancelBut = QPushButton('Cancel')
        self.cancelBut.clicked.connect(self.reject)
        self.playerList = QListWidget()
        self.msgBar = QLabel('')
        players = self.client.getOnlinePlayers()
        for player in players:
            self.playerList.addItem(player[:-1])
        self.playerList.itemClicked.connect(self.setPlayerTarget)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel('Select a player'))
        layout.addWidget(self.playerList)
        layout.addWidget(self.acceptBut)
        layout.addWidget(self.cancelBut)
        layout.addWidget(self.msgBar)
        self.player = ''

    def setPlayerTarget(self, state):
        name = state.text() + '\n'
        self.player = name
        self.client.setPlayerTarget(name)

    def testAccept(self):
        if self.player:
            self.accept()
        else:
            self.msgBar.setText('Select a player first!')

class Clairxo(QMainWindow):
    
    def __init__(self, size):
        super().__init__()
        self.threadpool = QThreadPool()
        self.client = Client()
        #Set up remaining animations
        self.createHomePanel()
        self.setCentralWidget(self.mainwindow)
        self.setWindowTitle('CLAIRXO')
        self.setGeometry(650, 200, 600, 600)
        self.show()

    def createHomePanel(self):
        self.mainwindow = HomeScreen(self.client, self.statusBar())
        self.mainwindow.signals.newGame.connect(self.newGame)
        self.mainwindow.signals.loadGame.connect(self.loadGame)
        self.client.connect()
        #Start threading
        self.monitor = ClientMonitor(self.client)
        self.monitor.signals.notify.connect(self.refresh)
        self.threadpool.start(self.monitor)

    def refresh(self):
        if self.mainwindow:
            self.mainwindow.refresh()

    def newGame(self):
        '''Queries the client if there is already a current game in 
        progress, if not generates a new game model and a game
        widget to hold it.
        '''
        self.client.setPlayerTarget('')
        self.playerSelect = PlayerQuery(self.client)
        self.playerSelect.exec_()
        #Check if the client has a selected player
        player = self.client.getPlayerTarget()
        if player:
            #We can create a game.
            print('Starting a game with ' + player)
            self.gamemodel = GameModel(self.client)
            self.gameWidget = GameTab(self.client, self.gamemodel, self.statusBar())
            self.gameWidget.signals.finished.connect(self.returnToMain)
            self.setCentralWidget(self.gameWidget)
            #Now that the main widget has been reset all panel items
            #Should be discarded
            self.mainwindow = None
            self.monitor.end()

    def loadGame(self):
        print(self.client.getCurrentGame())

    def returnToMain(self):
        #Create all the panel widgets again and reconnect the signals
        self.createHomePanel()
        self.setCentralWidget(self.mainwindow)
        #Delete all the old game information
        self.gamemodel = None
        self.gameWidget = None

        
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