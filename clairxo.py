#!/usr/bin/env python3
#Author Chris Lambert
from PyQt5.QtCore import Qt, QMimeData, pyqtSignal, QObject, QThreadPool, QRunnable
from PyQt5.QtWidgets import (QMainWindow, QAction, QApplication, qApp, QLabel, QFileDialog,
                             QTabWidget, QWidget)
import sys
from panel import HomeScreen
from client import Client
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
        while self.working:
            time.sleep(1)
            #players = self.client.getOnlinePlayers()
            self.signals.notify.emit()

class Clairxo(QMainWindow):
    
    def __init__(self, size):
        super().__init__()
        self.threadpool = QThreadPool()
        self.client = Client()
        self.mainwindow = HomeScreen(self.client, self.statusBar(), self)
        self.client.connect()
        #Start threading
        self.monitor = ClientMonitor(self.client)
        self.monitor.signals.notify.connect(self.refresh)
        self.threadpool.start(self.monitor)
        #Set up remaining animations
        self.setCentralWidget(self.mainwindow)
        self.setWindowTitle('CLAIRXO')
        self.setGeometry(650, 200, 600, 600)
        self.show()

    def refresh(self):
        self.mainwindow.refresh()
        
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