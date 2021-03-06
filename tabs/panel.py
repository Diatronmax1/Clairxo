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
        self.inviteList.addItems(self.client.getInvites())
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
            self.client.acceptInvite(self.invite)
            self.accept()
        else:
            self.msgBar.setText('Select a invite first!')

class GameQuery(QDialog):
    def __init__(self, client):
        super().__init__()
        self.client = client
        self.acceptBut = QPushButton('Accept')
        self.acceptBut.clicked.connect(self.testAccept)
        self.cancelBut = QPushButton('Cancel')
        self.cancelBut.clicked.connect(self.reject)
        self.gameList = QListWidget()
        self.msgBar = QLabel('')
        self.gameList.addItems(self.client.getGames())
        self.gameList.itemClicked.connect(self.setInviteTarget)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel('Select a game'))
        layout.addWidget(self.gameList)
        layout.addWidget(self.acceptBut)
        layout.addWidget(self.cancelBut)
        layout.addWidget(self.msgBar)
        self.game = ''

    def setInviteTarget(self, state):
        self.game = state.text()

    def testAccept(self):
        if self.game:
            self.client.setCurrentGame(self.game)
            self.accept()
        else:
            self.msgBar.setText('Select a game first!')

class HomeScreen(QWidget):
    def __init__(self, client, statusbar):
        super().__init__()
        self.signals = WorkerSignals()
        self.client = client
        self.statusbar = statusbar
        self.setBackground()
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
        resumeBut.clicked.connect(self.resumeGame)
        loadGameBut = QPushButton('Load Game')
        loadGameBut.clicked.connect(self.loadGame)
        invites = self.client.getInvites()
        self.inviteBut = QPushButton('No invites :(')
        self.inviteBut.clicked.connect(self.viewInvites)
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
        layout.addWidget(loadGameBut,                   4, 1)
        layout.addWidget(self.inviteBut,                5, 1)
        label = QLabel('Online Players')
        label.setStyleSheet('background-color:white')
        layout.addWidget(label,                         6, 1)
        layout.addWidget(self.playerList,               7, 1)
        layout.addWidget(QLabel('\t'),                  8, 0, 1, 3)

    def setBackground(self):
        background = 'lib/images/background.jpg'
        self.image = QPixmap(background)
        self.setAutoFillBackground(True)
        newmap = self.image.scaled(self.width(), self.height())
        p = self.palette()
        p.setBrush(self.backgroundRole(), QBrush(newmap))
        self.setPalette(p)
        
    def refresh(self):
        self.client.connect()
        self.playerList.clear()
        self.userName.setText(self.client.getUserName()[:-1])
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
                self.resumeGame()

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

    def resumeGame(self):
        if self.client.getCurrentGame():
            self.statusbar.showMessage('Loading game from server')
            self.signals.loadGame.emit()
        else:
            self.statusbar.showMessage('No games currently in play, start a new one!')

    def loadGame(self):
        self.statusbar.showMessage('Loading games ')
        if self.client.getUserName():
            self.gameSelect = GameQuery(self.client)
            if self.gameSelect.exec_():
                game = self.client.getCurrentGame()
                if game:
                    self.statusbar.showMessage('Current game: ' + game)
                    self.resumeGame()
                else:
                    self.statusbar.showMessage('No current games')
        else:
            self.statusbar.showMessage('Set up username first!')