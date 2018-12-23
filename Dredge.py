""""Dredge.py - contains the Dredge object"""

import pygame
import os
import Game

class Dredge(object):
    """A dredge to do the work"""

    def __init__(self, name="Dredge No. 42", owner=None, production=750, sail_speed=3, loc=(0, 0)):
        self.name = name
        self.owner = owner
        self.production = float(production)  # m3/wrkhr
        self.sail_speed = float(sail_speed)  # units/hr

        self.working_costs = production * (2.0) * 24  # $/day
        self.fixed_costs = production * (0.70) * 24  # $/day

        self.location = loc
        self.assigned_project = None
        self.destination = None

        self.dimensions = {'dredge_length': 300.,  # Dredge width/length includes horn tanks
                           'dredge_width': 60.,
                           'horn_length': 75.,  # Horn tanks on Bow
                           'horn_width': 10.,
                           'ladder_upper_length': 80.,  # Ladder upper box section
                           'ladder_upper_width': 38.,
                           'ladder_lower_length': 60.,  # Ladder lower taper
                           'ladder_lower_width': 18.,  # this is the end width
                           'cutter_length': 10.,  # cutter
                           'cutter_width': 4.,  # This is the tip width
                           }

        self.image_loc = os.path.join('graphics', 'ship_sea_ocean_64x64_b.png')
        self.image_size = (24, 24)
        image = pygame.image.load(self.image_loc).convert()
        self.image = pygame.transform.scale(image, self.image_size)
        self.plane = None

    def time_step(self, steptimesize, game):
        """update the dredge position if not in place"""
        ts_messages = []
        if self.assigned_project and not self.destination:
            self.destination = self.assigned_project.parent_city.location
        if self.destination:
            D = float(
                (self.destination[1] - self.location[1]) ** 2 + (self.destination[0] - self.location[0]) ** 2) ** 0.5
            move_dist = min(steptimesize * Game.days_to_hours * self.sail_speed, D)
            if D > move_dist:
                # Get closer
                Dx = (self.destination[0] - self.location[0]) / D
                Dy = (self.destination[1] - self.location[1]) / D
                self.location = [self.location[0] + move_dist * Dx, self.location[1] + move_dist * Dy]
            elif D < .001:
                self.destination = None
            else:
                self.location = self.destination
                ts_messages.append((self, "%s arrived at destination" % self.name))
        if self.plane:
            self.plane.rect.topleft = self.location  # Ugly bit of display code crept in here
        return ts_messages

    def in_city(self, city):
        """Return true if the dredge is in the given city."""
        if self.destination:
            # Not in a city if sailing
            return False
        dist = float((self.location[1] - city.location[1]) ** 2 + (self.location[0] - city.location[0]) ** 2) ** 0.5
        radius = (city.image_size[0] ** 2 + city.image_size[1] ** 2) ** 0.5
        return dist <= radius