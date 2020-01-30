from PyQt5.QtCore import Qt, QMimeData, pyqtSignal, QObject, QThreadPool, QRunnable
from PyQt5.QtGui import QDrag, QPixmap, QPalette, QBrush
from PyQt5.QtWidgets import (QFileDialog, QGridLayout, QGroupBox, QHBoxLayout, QInputDialog, 
                             QLabel, QListWidget, QListWidgetItem, QLineEdit, QPushButton, QProgressBar, 
                             QRadioButton, QTextEdit, QVBoxLayout, QDialog, QWidget)
import time
import numpy as np

class WorkerSignals(QObject):
    newGame = pyqtSignal(str)
    loadGame = pyqtSignal()

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
            self.msgBar.setText('Select an first!')

class InviteQuery(QDialog):
    def __init__(self, client):
        super().__init__()
        self.client = client
        self.acceptBut = QPushButton('Accept')
        self.acceptBut.clicked.connect(self.testAccept)
        self.cancelBut = QPushButton('Cancel')
        self.cancelBut.clicked.connect(self.reject)
        self.inviteList = QListWidget()
        self.msgBar = QLabel('')
        invites = self.client.getInvites()
        for invite in invites:
            self.inviteList.addItem(invite[:-1])
        self.inviteList.itemClicked.connect(self.setInviteTarget)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel('Select an invite'))
        layout.addWidget(self.inviteList)
        layout.addWidget(self.acceptBut)
        layout.addWidget(self.cancelBut)
        layout.addWidget(self.msgBar)
        self.invite = ''

    def setInviteTarget(self, state):
        self.invite = state.text()

    def testAccept(self):
        if self.invite:
            self.client.acceptInvite(invite)
            self.accept()
        else:
            self.msgBar.setText('Select a invite first!')

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
            self.statusbar.showMessage('Set User in the Options')
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
        layout.addWidget(startNewBut,                   2, 1)
        layout.addWidget(resumeBut,                     3, 1)
        layout.addWidget(self.inviteBut,                4, 1)
        layout.addWidget(optionsBut,                    5, 1)
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
        if self.client.getUserName():
            if self.client.getInvites():
                self.inviteSelect = InviteQuery(self.client)
                self.inviteSelect.exec_()

    def startNewGame(self):
        if self.client.getUserName():
            if self.client.getOnlinePlayers():
                self.client.setPlayerTarget('')
                self.playerSelect = PlayerQuery(self.client)
                self.playerSelect.exec_()
                #Check if the client has a selected player
                player = self.client.getPlayerTarget()
                if player:
                    self.statusbar.showMessage('Starting new game!')
                    self.signals.newGame.emit(player)
            else:
                self.statusbar.showMessage('No online players to play with :(')
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


