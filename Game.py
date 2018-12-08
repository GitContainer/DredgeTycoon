"""Game.py - Contains the Game object that holds all objects in the game - players, cities, 
   dredges, and the game world."""
# Model 
import os, random, datetime
import pygame
Demo=True
days_to_hours = 24.

def comprehension_flatten(iter_lst):
    return list(item for iter_ in iter_lst for item in iter_)

class City(object):
    """The cities with projects to let"""
    def __init__(self, name="sometown", xy=(0,0)):
        self.name = name
        self.location = xy
        self.projects = []
        
        #project characteristics - below should net to 1,000,000 cm/year in 4 projects
        self.project_probability = 8./365.  #probability of a project per day (i.e. 8/year avg)
        self.project_size = 550000.         #average project size
        self.project_growth = 500           #projects grow (shoal) at this rate on average
        self.project_unit = 4.5             #projects start at this unit rate
        
        self.image_loc = os.path.join('graphics', 'city_256x256.png')
        image = pygame.image.load(self.image_loc).convert()
        self.image_size = (32, 32)
        self.image = pygame.transform.scale(image, self.image_size)
        self.plane = None
        
        self.generateProject()
            
    def generateProject(self, probability=1):
        """generateProject - Add a project to the city
           probability is the probability of a project.
        """
        if random.random() <= probability:
            size = random.normalvariate(self.project_size, self.project_size*0.25)
            size = int(size/1000.)*1000
            unit = random.normalvariate(self.project_unit, self.project_unit*0.2)
            proj = Project(self, qty=size, unit=unit)
            self.projects.append(proj)
            return[(self, "Project %s advertised for tender in %s"%(proj.name, self.name))]
        else:
            return []
        
    def TimeStep(self, steptimesize, game):
        """update the city as time passes"""
        #eventually generate new projects here
        ts_messages = []
        #Check my projects
        for p in self.projects:
            ts_messages.extend(p.TimeStep(steptimesize, game))
        #generate any new projects
        ts_messages.extend(self.generateProject(self.project_probability*steptimesize))
        return ts_messages

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

class Project(object):
    """A project to be performed"""
    def __init__(self, city, player=None, qty=1000000, unit=4.5):
        self.parentCity = city
        self.player = player
        self.quantity = qty
        self.quantityRemain = qty
        self.quantityThisPeriod = 0 
        self.unitcost = unit        
        self.TotalValue = qty*self.unitcost
        self.dredges =[]
        Locations = ["Harbor", "Inlet", "Maintenance", "Beach"]
        self.name=self.parentCity.name+" %s"%(Locations[random.randint(0,3)])
    
    def progress(self):
        """ return the fraction of the project progress """
        return (float(self.quantity)-self.quantityRemain)/self.quantity
    
    def progressThisPeriod(self):
        """ return the fraction of the project completed this step period """
        return (self.quantityThisPeriod/self.quantity)
    
    def TimeStep(self, steptimesize, G):
        """ adjust the project to reflect moving forward in time
            steptimesize is the timestep in days
            G is the game object
            Call order this before the player TimeStep """
        ts_messages = []
        self.quantityThisPeriod=0
        if not self.player:
            #have not been assigned to a player
            for d in G.dredges:
                if not d.assigned_project and d.in_city(self.parentCity):
                    #assign this project
                    d.assigned_project = self
                    self.player = d.owner
                    self.player.projects.append(self)
                    d.assigned_project = self
                    self.dredges.append(d)
                    ts_messages.append((d,"%s awarded to %s"%(self.name, self.player.name)))
        elif self.quantityRemain > 0 and self.dredges:
            #have dredges, update 
            for mydredge in [d for d in self.dredges if d.in_city(self.parentCity)]:
                #can only contribute if on-site
                self.quantityThisPeriod += (mydredge.production * steptimesize * days_to_hours)
            self.quantityRemain = self.quantityRemain-self.quantityThisPeriod
        elif self.quantityRemain <= 0:
            #finished
            for d in self.dredges:
                d.assigned_project = None
            self.player.projects.remove(self)
            self.parentCity.projects.remove(self)
            ts_messages.append((self.parentCity, "%s completed"%self.name))
        else:
            #still qty, but no dredges assigned
            pass
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
    