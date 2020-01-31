import os
from lib.cfg import CFGFile
import pickle

class Client():
    '''Loads the players default settings which include
    username and games as well as stats
    '''
    def __init__(self):
        self.cfgfile = 'lib/cfg/cfg.tp'
        self.config = None
        self.playerTarget = None
        self.invites = {}
        self.load()

    def load(self):
        '''Verifies integrity of server connection and loads user
        settings
        '''
        #Check if cfg directory has ever been created
        if not os.path.exists(os.path.dirname(self.cfgfile)):
            os.mkdir(os.path.dirname(self.cfgfile))
        #Check if there is already a config saved
        if os.path.exists(self.cfgfile):
            #Try to load the config. If there have been
            #changes this might fail.
            try:
                with open(self.cfgfile, 'rb') as cfile:
                    self.config = pickle.load(cfile)
                    self.config.integrityCheck()
            except:
                #If this failes make a new config file
                #Config saves automatically on creation
                self.config = CFGFile(self.cfgfile) 
        else:
            #Create a new config, saves automatically
            self.config = CFGFile(self.cfgfile)
        #Now that the config file has been loaded in the 
        #remaining functions are guranteed to have a self.config
        #available.
        self.connect()

    def getInvites(self):
        return self.invites

    def getGames(self):
        return self.config.getGames()

    def setCurrentGame(self, gamename):
        self.config.getGame(gamename)

    def acceptInvite(self, invite):
        newgamepath = self.invites.pop(invite)
        self.config.setCurrentGame(invite, newgamepath[:-1])
        #Check invites
        ip = self.config.getTransferPath()
        invites = []
        if os.path.exists(ip):
            with open(ip, 'r') as tfile:
                for line in tfile:
                    if not line.endswith(newgamepath):
                        invites.append(line)
        with open(ip, 'w') as tfile:
            for invite in invites:
                tfile.write(invite)

    def createInvite(self, filename, savefile):
        tp = self.config.getTransferPath()
        self.config.setCurrentGame(filename, savefile)
        with open(tp, 'a+') as tfile:
            tfile.write(self.playerTarget[:-1] + '-' + savefile + '\n')

    def getCurrentGame(self):
        return self.config.getCurrentGame()

    def checkUserName(self):
        return self.user

    def setServerPath(self, newpath):
        self.config.setServerPath(newpath)

    def removeCurrentGame(self):
        self.config.removeCurrentGame()

    def setUserName(self, newname):
        self.goOffline()
        self.config.setName(newname)
        self.user = self.config.getName()
        self.connect()

    def getUserName(self):
        return self.config.getName()

    def getGamePath(self):
        return self.config.getGamePath()

    def getOnlinePlayers(self):
        players = []
        sp = self.config.getUserPath()
        name = self.config.getName()
        if os.path.exists(sp):
            with open(sp, 'r') as slink:
                for line in slink:
                    if line != name:
                        players.append(line)
        else:
            print('Didnt\'t connect to server to find players')
        return players

    def setPlayerTarget(self, playerName):
        self.playerTarget = playerName

    def getPlayerTarget(self):
        return self.playerTarget

    def goOffline(self):
        print('Going offline')
        sp = self.config.getUserPath()
        name = self.config.getName()
        if name == '':
            print('No username so dont disconnect')
            return
        if os.path.exists(sp):
            players = []
            with open(sp, 'r') as slink:
                for line in slink:
                    if line != name:
                        players.append(line)
            with open(sp, 'w') as slink:
                for player in players:
                    slink.write(player)
        else:
            print('Didn\'t connect to server to close')

    def connect(self):
        sp = self.config.getUserPath()
        name = self.config.getName()
        if name == '':
            return
        if os.path.exists(sp):
            players = []
            online = False
            with open(sp, 'r') as slink:
                for line in slink:
                    players.append(line)
                    if line == name:
                        online = True
            if not online:
                print('Setting status to online')
                players += name
                with open(sp, 'w') as slink:
                    for player in players:
                        slink.write(player)
        else:
            print('Did not connect to server!')
        #Check invites
        ip = self.config.getTransferPath()
        self.invites = {}
        if os.path.exists(ip):
            with open(ip, 'r') as tfile:
                for line in tfile:
                    if line.startswith(name[:-1]):
                        #Game invite exits
                        name, gamepath = line.split('-')
                        self.invites[os.path.basename(gamepath).split('.')[0]] = gamepath
        #Check the current game is accesible
        cg = self.config.getCurrentGame()
        if cg:
            if not os.path.exists(cg):
                self.config.removeCurrentGame()
