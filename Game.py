"""Game.py - Contains the Game object that holds all objects in the game - players, cities, 
   dredges, and the game world."""
# Model 
import os, random, datetime
import pygame
from City import City
from Dredge import Dredge
Demo=True
days_to_hours = 24.


def comprehension_flatten(iter_lst):
    return list(item for iter_ in iter_lst for item in iter_)


class Player(object):
    """Player with dredges"""
    def __init__(self, name="First Player"):
        self.name = name
        self.dredges = []
        self.value=1000000
        self.projects = [] # a list of Projects
        if Demo:
            self.dredges.append(Dredge(name="Treasure Island", owner=self, production=2000, loc=(5+16,425+16)))
            self.dredges.append(Dredge(owner=self,loc=(400,400)))
    
    def generateDredge(self, name=None):
        # add a dredge to a player
        #What purpose does this function serve?
        self.dredges.append(Dredge())  
    
    def TimeStep(self, steptimesize, game):
        """Adjust the player to reflect moving forward in time.
           steptimesize in the time step in days.
           game is the game I am part of."""
        ts_messages=[]
        revenue = 0
        for myproject in self.projects:
            # For Profit - expect projects to be updated before players
            revenue += myproject.quantityThisPeriod * myproject.unitcost
        fixed_costs = 0
        working_costs = 0
        for mydredge in self.dredges:
            # For Payroll! wait Boo!
            fixed_costs -= mydredge.fixedCosts*steptimesize
            mydredge.TimeStep(steptimesize, game)
            city_its_in = [c for c in game.cities if mydredge.in_city(c)]
            if mydredge.assigned_project and city_its_in:
                working_costs -= mydredge.workingCosts*steptimesize
            elif city_its_in:
                projects = [p for p in city_its_in[0].projects if p.player == self]
                if projects:
                    mydredge.assigned_project = projects[0]
                    mydredge.assigned_project.dredges.append(mydredge)
                    ts_messages.append((mydredge,"%s assigned to %s"%(mydredge.name, mydredge.assigned_project)))
        self.value += (revenue + fixed_costs + working_costs)
        return ts_messages




        
class Game(object):
    """Holds the various game objects"""
    def __init__(self):
        self.cities = [City("Boston", (375,20)),
                       City("New York", (400,80)),
                       City("Jacksonville", (5,425)),
                       ]
        self.players = [Player()]    
        self.date = datetime.datetime(1920,1,1)
    
    @property
    def dredges(self):
        """return a list of all dredges"""
        return comprehension_flatten([p.dredges for p in self.players]) # this returns a flat list of all dredges
    
    @property
    def projects(self):
        """return a list of projects"""
        return comprehension_flatten([c.projects for c in self.cities]) # this returns a flat list of projects underway
