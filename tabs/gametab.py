from PyQt5.QtCore import Qt, QMimeData, pyqtSignal, QObject, QThreadPool, QRunnable
from PyQt5.QtGui import QDrag, QPixmap, QPalette, QBrush
from PyQt5.QtWidgets import (QFileDialog, QGridLayout, QGroupBox, QHBoxLayout, QInputDialog, 
                             QLabel, QListWidget, QListWidgetItem, QLineEdit, QPushButton, QProgressBar, 
                             QRadioButton, QTextEdit, QVBoxLayout, QWidget)
import time
import numpy as np

class WorkerSignals(QObject):
    finished = pyqtSignal()

class GameTab(QWidget):
	def __init__(self, client, gamemodel):
		super().__init__()
		self.client = client
		self.gamemodel = gamemodel
		self.signals = WorkerSignals()
		self.endgamebut = QPushButton('End Game')
		self.endgamebut.clicked.connect(self.endGame)
		layout = QHBoxLayout(self)
		layout.addWidget(self.endgamebut)

	def endGame(self):
		self.signals.finished.emit()