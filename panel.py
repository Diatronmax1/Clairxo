from PyQt5.QtCore import Qt, QMimeData, pyqtSignal, QObject
from PyQt5.QtGui import QDrag, QPixmap, QPalette, QBrush
from PyQt5.QtWidgets import (QFileDialog, QGridLayout, QGroupBox, QHBoxLayout, QInputDialog, 
                             QLabel, QListWidget, QListWidgetItem, QLineEdit, QPushButton, QProgressBar, 
                             QRadioButton, QTextEdit, QVBoxLayout, QWidget)
import time
import numpy as np

class HomeScreen(QWidget):
    def __init__(self, client, statusbar, parent):
        super().__init__(parent)
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
        userBox = QWidget()
        layout = QHBoxLayout(userBox)
        layout.addWidget(label)
        layout.addWidget(self.userName)
        startNewBut = QPushButton('Start New Game')
        startNewBut.clicked.connect(self.startNewGame)
        resumeBut = QPushButton('Resume Game')
        resumeBut.clicked.connect(self.loadGame)
        optionsBut = QPushButton('Options')
        optionsBut.clicked.connect(self.setOptions)
        self.playerList = QListWidget()
        layout = QGridLayout(self)
        layout.setRowStretch(0, 2)
        layout.setRowStretch(7, 2)
        layout.addWidget(QLabel('\t'),                  0, 0, 1, 2)
        layout.addWidget(userBox,                       1, 1)
        layout.addWidget(QLabel('\t'),                  2, 0)
        layout.addWidget(startNewBut,                   2, 1)
        layout.addWidget(QLabel('\t'),                  2, 2)
        layout.addWidget(QLabel('\t'),                  3, 0)
        layout.addWidget(resumeBut,                     3, 1)
        layout.addWidget(QLabel('\t'),                  3, 2)
        layout.addWidget(QLabel('\t'),                  4, 0)
        layout.addWidget(optionsBut,                    4, 1)
        layout.addWidget(QLabel('\t'),                  4, 2)
        label = QLabel('Online Players')
        label.setStyleSheet('background-color:white')
        layout.addWidget(label,                         5, 1)
        layout.addWidget(self.playerList,               6, 1)
        layout.addWidget(QLabel('\t'),                  7, 0, 1, 3)

    def initialize(self):
        print('Loading Client from Panel')
        username = self.client.load()
        if username:
            self.userName.setText(username)
            print('Connecting to Server')
            self.client.connect()
        else:
            print('No username set up yet')
            self.userName.setText('Unknown!')
            self.statusbar.showMessage('Set up user in options!')

    def refresh(self):
        self.playerList.clear()
        self.playerList.addItems(self.client.getOnlinePlayers())

    def resizeEvent(self, event):
        newmap = self.image.scaled(self.width(), self.height())
        p = self.palette()
        p.setBrush(self.backgroundRole(), QBrush(newmap))
        self.setPalette(p)

    def startNewGame(self):
        self.statusbar.showMessage('Starting new game!')

    def loadGame(self):
        self.statusbar.showMessage('Loading game from server')

    def setOptions(self):
        self.statusbar.showMessage('Setting Options!')
        text, _ok = QInputDialog.getText(self, "Set new User Name", "User name:", QLineEdit.Normal)
        if text and _ok:
            self.statusbar.showMessage('Set user name to: ' + text)
            self.userName.setText(text)
            self.client.setUserName(text)
            self.refresh()


