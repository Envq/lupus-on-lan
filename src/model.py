#!/usr/bin/python3
import random
from enum import Enum

from data_manager import DataManager


class GamePhase(Enum):
    init = 0
    waitForPeoples = 1
    start = 2
    finish = 3


class Game:
    def __init__(self):
        self.phase = GamePhase.init
        self.dataManager = DataManager()
        self.rolesSelected = self.dataManager.getRolesAvailables()
        self.playerCounter = 0
        self.players = dict()
        self.allPlayersAreAssigned = False
        self.master = None
        self.masterIsAssigned = False
        self.phase = GamePhase.waitForPeoples

    # DataManager Wrappers
    def getDescriptions(self, role):
        return self.dataManager.getDescriptions(role)


    def getRoleNameOf(self, role):
        return self.dataManager.getRoleNameOf(role)


    def getRaceOf(self, role):
        return self.dataManager.getRaceOf(role)


    def getTeamOf(self, role):
        return self.dataManager.getTeamOf(role)


    def isVisibleForSimilars(self, role):
        return self.dataManager.getIsVisibleForSimilars(role)


    def getPlayerDescriptionOf(self, role):
        return self.dataManager.getPlayerDescriptionOf(role)


    def getImagePathOf(self, role):
        return self.dataManager.getImagePathOf(role)


    # Init to Start phase
    def isAlreadyLogged(self, id):
        return (id in self.players) or (self.masterIsAssigned and id == self.master)

    
    def getNameOf(self, id):
        if self.masterIsAssigned and id == self.master:
            return 'master'
        if id in self.players:
            return self.players[id]['name']
        return 'UnkownName'


    def addPlayer(self, id, name):
        """Returns True if the addition of the player was successful"""
        # check if the phase is valid
        if self.phase != GamePhase.waitForPeoples:
            return False
        # check if the user is alredy register
        if (id in self.players) or (id == self.master):
            return False
        # check if the name is valid
        if name == None or name == '' or name.lower() in [p.lower() for p in self.players.keys()]:
            return False
        # check if all roles are just assigned
        if self.playerCounter == len(self.rolesSelected):
            self.allPlayersAreAssigned = True
        # check if master
        if name.lower() == 'master':
            self.master = id
            self.masterIsAssigned = True
            # Check if game can start
            if self.allPlayersAreAssigned:
                self.newGame()
            return True
        # check if add player
        if self.allPlayersAreAssigned:
            return False
        # add player
        self.players[id] = dict()
        self.players[id]['name'] = name
        self.players[id]['death'] = False
        self.players[id]['role'] = self.rolesSelected[self.playerCounter]
        self.playerCounter += 1
        # check if all roles are assigned
        if self.playerCounter == len(self.rolesSelected):
            self.allPlayersAreAssigned = True
        # Check if the game can start
        if self.allPlayersAreAssigned and self.masterIsAssigned:
            self.newGame()
        return True


    def getPlayersName(self):
        names = [v['name'] for k, v in self.players.items()]
        if self.masterIsAssigned:
            return names + ['master']
        return names
    

    def getProgressLobbyStr(self):
        return f'{int(len(self.getPlayersName())/(len(self.rolesSelected)+1)*100)}%'


    def isStart(self):
        return self.phase == GamePhase.start


    # Player phase
    def getPlayersSimilarTo(self, id):
        playersSimilar = list()
        playerRole = self.players[id]['role']
        if self.isVisibleForSimilars(playerRole):
            for p, info in self.players.items():
                if info['role'] == playerRole and p != id:
                    playersSimilar.append(p)
        return playersSimilar


    def getRoleOf(self, id):
        return self.players[id]['role']

    
    def getPlayers(self):
        return self.players


    # Finish
    def isFinish(self):
        return self.phase == GamePhase.finish


    def newGame(self):
        self.phase = GamePhase.init
        tmp = list(self.players.items())
        random.shuffle(tmp)
        self.players = dict(tmp)
        self.phase = GamePhase.start



# TESTS
if __name__ == "__main__":
    g = Game()

    id_a = '192.168.1.130'
    id_b = '192.168.1.120'
    id_master = '192.168.1.110'
    role = 'werewolf'

    assert not g.isAlreadyLogged(id_master)
    assert not g.isAlreadyLogged(id_a)
    assert g.getNameOf(id_master) =='UnkownName'
    assert g.getNameOf(id_a) == 'UnkownName'

    assert not g.isStart()
    assert g.phase == GamePhase.waitForPeoples
    assert g.rolesSelected == [role, role]
    assert g.players == {}
    assert not g.masterIsAssigned
    assert not g.allPlayersAreAssigned

    res = g.addPlayer(id_a, 'a')
    assert res
    assert g.phase == GamePhase.waitForPeoples
    assert g.players == {id_a: {'name':'a', 'death':False, 'role':role}}
    assert not g.masterIsAssigned
    assert not g.allPlayersAreAssigned

    res = g.addPlayer(id_a, 'a')
    assert not res
    assert g.phase == GamePhase.waitForPeoples
    assert g.players == {id_a: {'name':'a', 'death':False, 'role':role}}
    assert not g.masterIsAssigned
    assert not g.allPlayersAreAssigned

    res = g.addPlayer(id_b, 'b')
    assert res
    assert g.phase == GamePhase.waitForPeoples
    assert g.players == {id_a: {'name':'a', 'death':False, 'role':role}, \
                         id_b: {'name':'b', 'death':False, 'role':role}}
    assert not g.masterIsAssigned
    assert g.allPlayersAreAssigned
    assert len(g.getPlayersName()) == 2
    assert 'a' in g.getPlayersName()
    assert 'b' in g.getPlayersName()

    res = g.addPlayer('192.168.1.140', 'c')
    assert not res
    assert g.phase == GamePhase.waitForPeoples
    assert g.players == {id_a: {'name':'a', 'death':False, 'role':role}, \
                         id_b: {'name':'b', 'death':False, 'role':role}}
    assert not g.masterIsAssigned
    assert g.allPlayersAreAssigned

    assert g.master == None
    res = g.addPlayer(id_master, 'master')
    assert res
    assert g.phase == GamePhase.start
    assert g.players == {id_a: {'name':'a', 'death':False, 'role':role}, \
                         id_b: {'name':'b', 'death':False, 'role':role}}
    assert g.master == id_master
    assert g.masterIsAssigned
    assert g.allPlayersAreAssigned
    assert g.isStart()
    assert len(g.getPlayersName()) == 3
    assert 'a' in g.getPlayersName()
    assert 'b' in g.getPlayersName()
    assert 'master' in g.getPlayersName()


    assert g.getPlayersSimilarTo(id_a) == [id_b]
    assert g.getPlayersSimilarTo(id_b) == [id_a]
    assert g.getRoleOf(id_a) == 'werewolf'
    assert g.isAlreadyLogged(id_master)
    assert g.isAlreadyLogged(id_a)
    assert g.getNameOf(id_master) =='master'
    assert g.getNameOf(id_a) == 'a'


    print("OK all is correct")
