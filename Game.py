"""Game.py - Contains the Game object that holds all objects in the game - players, cities, 
   dredges, and the game world."""
# Model 
import os, random, datetime
import pygame
from City import City
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



class Dredge(object):
    """A dredge to do the work"""
    def __init__(self, name="Dredge No. 42", owner=None, production=1000, sail_speed=3, loc=(0,0)):
        self.name = name
        self.owner = owner
        self.production = float(production)          # m3/wrkhr
        self.sail_speed = float(sail_speed)          # units/hr
        
        self.workingCosts =  production *(2.0) * 24  # $/day
        self.fixedCosts = production * (0.70) * 24    # $/day
        
        self.location = loc
        self.assigned_project = None
        self.destination = None
        
        self.dimensions = {'dredge_length':        300.,#Dredge width/length includes horn tanks
                           'dredge_width':         60., 
                           'horn_length':          75., #Horn tanks on Bow
                           'horn_width':           10.,
                           'ladder_upper_length':  80., #Ladder upper box section
                           'ladder_upper_width':   38.,
                           'ladder_lower_length':  60., #Ladder lower taper
                           'ladder_lower_width':   18., #this is the end width
                           'cutter_length':        10., #cutter
                           'cutter_width':          4., #This is the tip width
                           }
        
        self.image_loc = os.path.join('graphics', 'ship_sea_ocean_64x64_b.png')
        self.image_size = (24,24)
        image = pygame.image.load(self.image_loc).convert()
        self.image = pygame.transform.scale(image, self.image_size)
        self.plane=None
        
    def TimeStep(self, steptimesize, game):
        """update the dredge position if not in place"""
        ts_messages = []
        if self.assigned_project and not self.destination:
            self.destination = self.assigned_project.parentCity.location
        if self.destination:
            D = float((self.destination[1]-self.location[1])**2+(self.destination[0]-self.location[0])**2)**0.5
            move_dist = min(steptimesize*days_to_hours*self.sail_speed,D)
            if D>move_dist:
                #Get closer
                Dx = (self.destination[0]-self.location[0])/D
                Dy = (self.destination[1]-self.location[1])/D
                self.location = [self.location[0]+move_dist*Dx, self.location[1]+move_dist*Dy]
            elif D<.001:
                self.destination = None
            else:
                self.location = self.destination
                ts_messages.append((self,"%s arrived at destination"%self.name))
        if self.plane:
            self.plane.rect.topleft=self.location #Ugly bit of display code crept in here
        return ts_messages
            
    def in_city(self, city):
        """Return true if the dredge is in the given city."""
        if self.destination:
            #Not in a city if sailing
            return False
        dist = float((self.location[1]-city.location[1])**2+(self.location[0]-city.location[0])**2)**0.5
        radius = (city.image_size[0]**2 + city.image_size[1]**2)**0.5
        return dist <= radius
        
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
