"""Projecy.py - Contains the Project object."""

import random
import Game

class Project(object):
    """A project to be performed"""

    def __init__(self, city, player=None, qty=1000000, unit=4.5):
        self.parentCity = city
        self.player = player
        self.quantity = qty
        self.quantityRemain = qty
        self.quantityThisPeriod = 0
        self.unitcost = unit
        self.TotalValue = qty * self.unitcost
        self.dredges = []
        Locations = ["Harbor", "Inlet", "Maintenance", "Beach"]
        self.name = self.parentCity.name + " %s" % (Locations[random.randint(0, 3)])

    def progress(self):
        """ return the fraction of the project progress """
        return (float(self.quantity) - self.quantityRemain) / self.quantity

    def progressThisPeriod(self):
        """ return the fraction of the project completed this step period """
        return (self.quantityThisPeriod / self.quantity)

    def time_step(self, steptimesize, G):
        """ adjust the project to reflect moving forward in time
            steptimesize is the timestep in days
            G is the game object
            Call order this before the player TimeStep """
        ts_messages = []
        self.quantityThisPeriod = 0
        if not self.player:
            # have not been assigned to a player
            for d in G.dredges:
                if not d.assigned_project and d.in_city(self.parentCity):
                    # assign this project
                    d.assigned_project = self
                    self.player = d.owner
                    self.player.projects.append(self)
                    d.assigned_project = self
                    self.dredges.append(d)
                    ts_messages.append((d, "%s awarded to %s" % (self.name, self.player.name)))
        elif self.quantityRemain > 0 and self.dredges:
            # have dredges, update
            for mydredge in [d for d in self.dredges if d.in_city(self.parentCity)]:
                # can only contribute if on-site
                self.quantityThisPeriod += (mydredge.production * steptimesize * Game.days_to_hours)
            self.quantityRemain = self.quantityRemain - self.quantityThisPeriod
        elif self.quantityRemain <= 0:
            # finished
            for d in self.dredges:
                d.assigned_project = None
            self.player.projects.remove(self)
            self.parentCity.projects.remove(self)
            ts_messages.append((self.parentCity, "%s completed" % self.name))
        else:
            # still qty, but no dredges assigned
            pass
        return ts_messages
