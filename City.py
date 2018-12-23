"""City.py - Contains the City object"""

import os, random, datetime
import pygame
from Project import Project

class City(object):
    """The cities with projects to let"""

    def __init__(self, date, name="sometown", xy=(0, 0)):
        self.name = name
        self.location = xy
        self.projects = []

        # project characteristics - below should net to 1,000,000 cm/year in 4 projects
        self.project_probability = 8. / 365.  # probability of a project per day (i.e. 8/year avg)
        self.project_size = 550000.  # average project size
        self.project_growth = 500  # projects grow (shoal) at this rate on average
        self.project_unit = 4.5  # projects start at this unit rate

        self.image_loc = os.path.join('graphics', 'city_256x256.png')
        image = pygame.image.load(self.image_loc).convert()
        self.image_size = (32, 32)
        self.image = pygame.transform.scale(image, self.image_size)
        self.plane = None

        self.generate_project(date)

    def generate_project(self, date, probability=1):
        """generateProject - Add a project to the city
           probability is the probability of a project.
        """
        if random.random() <= probability:
            size = random.normalvariate(self.project_size, self.project_size * 0.25)
            size = int(size / 1000.) * 1000
            unit = random.normalvariate(self.project_unit, self.project_unit * 0.2)
            proj = Project(self, date, qty=size, unit=unit)
            self.projects.append(proj)
            return [(self, "Project %s advertised for tender in %s" % (proj.name, self.name))]
        else:
            return []

    def time_step(self, steptimesize, game):
        """update the city as time passes"""
        # eventually generate new projects here
        ts_messages = []
        # Check my projects
        for p in self.projects:
            ts_messages.extend(p.time_step(steptimesize, game))
        # generate any new projects
        ts_messages.extend(self.generate_project(game.date, self.project_probability * steptimesize))
        return ts_messages
