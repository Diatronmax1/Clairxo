#!/usr/bin/env python3
#Author Chris Lambert
from PyQt5.QtCore import Qt, QMimeData, pyqtSignal, QObject, QThreadPool, QRunnable
from PyQt5.QtWidgets import (QMainWindow, QAction, QApplication, qApp, QLabel, QFileDialog,
                             QTabWidget, QWidget, QMessageBox, QVBoxLayout, QListWidget, QDialog, QPushButton)
import sys
from client import Client
from lib.gamemodel import GameModel
from tabs.gametab import GameTab
from tabs.panel import HomeScreen
import time
import pickle

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

class Clairxo(QMainWindow):
    
    def __init__(self, size):
        super().__init__()
        self.threadpool = QThreadPool()
        self.client = Client()
        #Set up remaining animations
        self.createHomePanel()
        self.setCentralWidget(self.mainwindow)
        self.setWindowTitle('CLAIRXO')
        self.setGeometry(625, 100, 750, 750)
        self.startMonitor()
        #Set up action bar
        tutorialAct = QAction('Tutorial', self)
        tutorialAct.setStatusTip('Launch Tutorial Mode for this program')
        tutorialAct.setShortcut('Ctrl+t')
        tutorialAct.triggered.connect(self.launchTutorial)
        menubar = self.menuBar()
        helpMenu = menubar.addMenu('Help')
        helpMenu.addAction(tutorialAct)
        self.show()

    def createHomePanel(self):
        self.mainwindow = HomeScreen(self.client, self.statusBar())
        self.mainwindow.signals.newGame.connect(self.newGame)
        self.mainwindow.signals.loadGame.connect(self.loadGame)

    def startMonitor(self):
        #Start threading
        self.monitor = ClientMonitor(self.client)
        self.monitor.signals.notify.connect(self.refresh)
        self.threadpool.start(self.monitor)

    def refresh(self):
        if self.mainwindow:
            self.mainwindow.refresh()

    def launchTutorial(self):
        msgWidget = QMessageBox()
        msgWidget.setIcon(QMessageBox.Information)
        msg = 'Welcome to Quixo!\n'
        msg += 'You can pick up any red edge block by right clicking and dragging\n'
        msg += 'You are only allowed to pick up a blank, or your own block\n'
        msg += 'Move the block to any of the outer blocks that are now highlighted green\n'
        msg += 'Release to drop your block onto the outer square. This will ready the block to be moved\n'
        msg += 'If you are happy with your move, press accept and pass turn to move it to the next turn\n'
        msg += 'After placing a block it can be picked up again and put in any other green space\n'
        msg += 'Move the block back to the starting block to cancel that move\n'
        msg += 'Goal is to get 5 in a row in either a row, column or diaganol\n'
        msgWidget.setText(msg)
        msgWidget.setWindowTitle('Tutorial')
        msgWidget.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        msgWidget.exec_()

    def newGame(self, player):
        '''Queries the client if there is already a current game in 
        progress, if not generates a new game model and a game
        widget to hold it.
        '''
        self.monitor.end()
        print('Starting a game with ' + player)
        self.gamemodel = GameModel(self.client, self.client.getUserName(), player)
        self.client.createInvite(self.gamemodel.getSaveFile())
        self.gameWidget = GameTab(self.client, self.gamemodel, self.statusBar())
        self.gameWidget.signals.finished.connect(self.returnToMain)
        self.setCentralWidget(self.gameWidget)
        #Now that the main widget has been reset all panel items
        #Should be discarded
        self.mainwindow = None
        
    def loadGame(self):
        currentGame = self.client.getCurrentGame()
        with open(currentGame, 'rb') as gfile:
            self.gamemodel = pickle.load(gfile)
            self.gameWidget = GameTab(self.client, self.gamemodel, self.statusBar())
            self.gameWidget.signals.finished.connect(self.returnToMain)
            self.setCentralWidget(self.gameWidget)
            self.mainwindow = None
            self.monitor.end()

    def returnToMain(self):
        #Create all the panel widgets again and reconnect the signals
        self.createHomePanel()
        self.setCentralWidget(self.mainwindow)
        self.startMonitor()
        #Delete all the old game information
        self.gamemodel = None
        self.gameWidget.signals.finished.disconnect()
        self.statusBar().showMessage('Main Menu')
  
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