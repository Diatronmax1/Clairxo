from PyQt5.QtCore import Qt, QMimeData, pyqtSignal, QObject, QThreadPool, QRunnable
from PyQt5.QtGui import QDrag, QPixmap, QPalette, QBrush
from PyQt5.QtWidgets import (QFileDialog, QGridLayout, QGroupBox, QHBoxLayout, QInputDialog, 
                             QLabel, QListWidget, QListWidgetItem, QLineEdit, QPushButton, QProgressBar, 
                             QRadioButton, QTextEdit, QVBoxLayout, QWidget)
import time
import numpy as np

class WorkerSignals(QObject):
    newGame = pyqtSignal()
    loadGame = pyqtSignal()

class HomeScreen(QWidget):
    def __init__(self, client, statusbar):
        super().__init__()
        self.signals = WorkerSignals()
        #Client comes in loaded with a config
        self.client = client
        self.statusbar = statusbar
        background = 'lib/images/background.jpg'
        self.image = QPixmap(background)
        self.setAutoFillBackground(True)
        newmap = self.image.scaled(self.width(), self.height())
        p = self.palette()
        p.setBrush(self.backgroundRole(), QBrush(newmap))
        self.setPalette(p)
        label = QLabel('Current User: ')
        label.setStyleSheet('background-color:white')
        self.userName = QLabel()
        self.userName.setStyleSheet('background-color:white')
        name = self.client.getUserName()
        if name:
            self.userName.setText(name[:-1])
        else:
            self.statusbar.showMessage('Set User in the options')
        userBox = QWidget()
        layout = QHBoxLayout(userBox)
        layout.addWidget(label)
        layout.addWidget(self.userName)
        startNewBut = QPushButton('Start New Game')
        startNewBut.clicked.connect(self.startNewGame)
        resumeBut = QPushButton('Resume Game')
        resumeBut.clicked.connect(self.loadGame)
        invites = self.client.getInvites()
        if invites:
            self.inviteBut = QPushButton('Invites Available!')
        else:
            self.inviteBut = QPushButton('No invites :(')
        self.inviteBut.clicked.connect(self.viewInvites)
        optionsBut = QPushButton('Options')
        optionsBut.clicked.connect(self.setOptions)
        self.playerList = QListWidget()
        layout = QGridLayout(self)
        layout.setRowStretch(0, 2)
        layout.setRowStretch(8, 2)
        layout.setColumnStretch(0, 2)
        layout.setColumnStretch(2, 2)
        layout.addWidget(QLabel('\t'),                  0, 0, 1, 2)
        layout.addWidget(userBox,                       1, 1)
        #layout.addWidget(QLabel('\t'),                  2, 0)
        layout.addWidget(startNewBut,                   2, 1)
        #layout.addWidget(QLabel('\t'),                  2, 2)
        #layout.addWidget(QLabel('\t'),                  3, 0)
        layout.addWidget(resumeBut,                     3, 1)
        layout.addWidget(self.inviteBut,                4, 1)
        #layout.addWidget(QLabel('\t'),                  3, 2)
        #layout.addWidget(QLabel('\t'),                  4, 0)
        layout.addWidget(optionsBut,                    5, 1)
        #layout.addWidget(QLabel('\t'),                  4, 2)
        label = QLabel('Online Players')
        label.setStyleSheet('background-color:white')
        layout.addWidget(label,                         6, 1)
        layout.addWidget(self.playerList,               7, 1)
        layout.addWidget(QLabel('\t'),                  8, 0, 1, 3)
        
    def refresh(self):
        self.client.connect()
        self.playerList.clear()
        players = self.client.getOnlinePlayers()
        for player in players:
            self.playerList.addItem(player[:-1])
        invites = self.client.getInvites()
        if invites:
            self.inviteBut.setText('Invites Available!')
        else:
            self.inviteBut.setText('No invites :(')

    def resizeEvent(self, event):
        newmap = self.image.scaled(self.width(), self.height())
        p = self.palette()
        p.setBrush(self.backgroundRole(), QBrush(newmap))
        self.setPalette(p)

    def viewInvites(self):
        print(self.client.getInvites())

    def startNewGame(self):
        if self.client.getUserName():
            self.statusbar.showMessage('Starting new game!')
            self.signals.newGame.emit()
        else:
            self.statusbar.showMessage('Setup username first!')

    def loadGame(self):
        if self.client.getCurrentGame():
            self.statusbar.showMessage('Loading game from server')
            self.signals.loadGame.emit()
        else:
            self.statusbar.showMessage('No games currently in play, start a new one!')

    def setOptions(self):
        self.statusbar.showMessage('Setting Options!')
        text, _ok = QInputDialog.getText(self, "Set new User Name", "User name:", QLineEdit.Normal)
        if text and _ok:
            self.statusbar.showMessage('Set user name to: ' + text)
            self.userName.setText(text)
            self.client.setUserName(text)
            self.refresh()


