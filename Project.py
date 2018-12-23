"""Projecy.py - Contains the Project object."""

import random
import Game

class Project(object):
    """A project to be performed"""

    def __init__(self, city, start_date, player=None, qty=1000000, unit=4.5):
        self.parent_city = city
        self.start_date = start_date
        self.player = player
        self.quantity = qty
        self.quantity_remain = qty
        self.quantity_this_period = 0
        self.orig_unit = unit
        self.unit_cost = unit
        self.total_value = qty * self.unit_cost
        self.dredges = []
        locations = ["Harbor", "Inlet", "Maintenance", "Beach"]
        self.name = self.parent_city.name + " %s" % (locations[random.randint(0, 3)])

    def progress(self):
        """ return the fraction of the project progress """
        return (float(self.quantity) - self.quantity_remain) / self.quantity

    def progress_this_period(self):
        """ return the fraction of the project completed this step period """
        return (self.quantity_this_period / self.quantity)

    def time_step(self, steptimesize, G):
        """ adjust the project to reflect moving forward in time
            steptimesize is the timestep in days
            G is the game object
            Call order this before the player TimeStep """
        ts_messages = []
        self.quantity_this_period = 0
        if not self.player:
            # have not been assigned to a player
            for d in G.dredges:
                if not d.assigned_project and d.in_city(self.parent_city):
                    # assign this project
                    d.assigned_project = self
                    self.player = d.owner
                    self.player.projects.append(self)
                    d.assigned_project = self
                    self.dredges.append(d)
                    ts_messages.append((d, "%s awarded to %s" % (self.name, self.player.name)))
            if not self.player:
                #reduce the value
                days_advertised = (G.date - self.start_date).days
                a = -0.5/(60.**2-2*30.**2)
                b = -60.*a
                c = 1
                self.unit_cost = self.orig_unit*(a*days_advertised**2 + b*days_advertised + c)
                self.total_value = self.quantity * self.unit_cost
        elif self.quantity_remain > 0 and self.dredges:
            # have dredges, update
            for mydredge in [d for d in self.dredges if d.in_city(self.parent_city)]:
                # can only contribute if on-site
                self.quantity_this_period += (mydredge.production * steptimesize * Game.days_to_hours)
            self.quantity_remain = self.quantity_remain - self.quantity_this_period
        elif self.quantity_remain <= 0:
            # finished
            for d in self.dredges:
                d.assigned_project = None
            self.player.projects.remove(self)
            self.parent_city.projects.remove(self)
            ts_messages.append((self.parent_city, "%s completed" % self.name))
        else:
            # still qty, but no dredges assigned
            pass
        return ts_messages
