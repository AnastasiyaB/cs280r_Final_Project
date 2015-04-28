import random

## class representation for each cell
class Cell:
    def __init__(self, x, y, time, veg_inten, wind_direc, wind_inten, fire_inten, firefighter, ff_info):
        self.x = x
        self.y = y
        self.time = time
        self.veg_inten = veg_inten # vegetation intensity (assuming the most intense, the more flammable; 0 means it can no longer catch on fire)
        #self.veg_vol = veg_vol #vegetation volume
        self.wind_direc = wind_direc # wind direction
        self.wind_inten = wind_inten # wind intensity
        self.fire_inten = fire_inten # if there is a fire in the cell, how intensly is it burning
        self.firefighter = firefighter
        self.ff_info = ff_info ## but will be class firefighter
        
## class representation for each firefighter
class FireFighter:
    def __init__(self, x, y, area, efficacy = 1):
        self.x = x # The starting cell/cell we're currently in
        self.y = y
        self.area = area # The grid where the firefighter lives
        self.path = [] # The path we've traverse so far
        self.efficacy = efficacy # Perhaps make this model vary on fighter skill level
        self.actList = range(8) # 0 = up left, ... 7 = left

    def bestAction(self, newgrid):
        #actList = [(-1,0),(0,-1),(0,1),(1,0)]
        actList = [(-1,-1), (-1,0), (-1,1), (0,-1), \
                   (0, 1), (1,-1),  (1,0),  (1,1)]
        # Greedy
        max_inten = 0.
        max_move = None
        for dx, dy in actList:
            if self.x + dx >= 0 and self.x + dx < self.area.L \
               and self.y + dy >= 0 and self.y + dy < self.area.L:
                it = self.area.grid[(self.x + dx, self.y + dy)].fire_inten
                fft = newgrid[(self.x + dx, self.y + dy)].firefighter
                if it > max_inten and not fft:
                    max_inten = it
                    max_move = (dx, dy)
        act = max_move
        while not act:
            # Random
            act = random.choice(actList)
            dx, dy = act
            if self.x + dx >= 0 and self.x + dx < self.area.L \
               and self.y + dy >= 0 and self.y + dy < self.area.L \
               and not newgrid[(self.x + dx, self.y + dy)].firefighter:
                break
            else:
                act = None
        self.path.append(act)
        self.x += act[0]
        self.y += act[1]
        return act
       
class AreaSimulation:
    def __init__(self, L):
        self.grid = {}
        self.hood = ((-1,-1), (-1,0), (-1,1),
                (0,-1),          (0, 1),
                (1,-1),  (1,0),  (1,1))
        
        self.L = L
        self.time = 0
        self.firefighters = [[False for i in range(L)] for j in range(L)]
        
    def fight_fire(self, ff_info):
        self.grid[(ff_info.x, ff_info.y)].firefighter = True
        self.grid[(ff_info.x, ff_info.y)].ff_info = ff_info
        self.firefighters[ff_info.x][ff_info.y] = True
        return
        
    ## rewrite this
    def initialize(self):
        for x in range(self.L):
            for y in range(self.L):
                self.grid[(x,y)] = Cell(
                    x= x,
                    y= y,
                    time= 0,
                    veg_inten= random.random(),
                    #veg_vol = random.random()*10,
                    wind_direc= "right", ### not using this for now
                    wind_inten= random.random(),
                    fire_inten= 0.00,
                    firefighter = False,
                    ff_info = None 
                )
        
        return self.grid
    
    def gnew(self):
        newgrid = {}
        new_ff_coord = []
        self.time += 1
        # iterate through all the cells
        for x in range(self.L):
            for y in range(self.L): 
#                 if self.grid[(x,y)].veg_inten == 0: # no fire is possible here
#                     newgrid[(x,y)] = self.grid[(x,y)] ## need to update time
#                     newgrid[(x,y)].time +=1
#                     newgrid[(x,y)].fire_inten = 0
                ## TO DO: indicate here which cell the firefigher will go to next
                if self.grid[(x,y)].fire_inten > 0: # cell is burning
                    new_fire_inten = min(self.grid[(x,y)].fire_inten * (self.grid[(x,y)].veg_inten) * 3, 1) ### take into account vegetation
                    newgrid[(x,y)] = Cell(
                        x= x,
                        y= y,
                        time = self.time if not self.grid[(x,y)].time else self.grid[(x,y)].time,
                        veg_inten = max(0, self.grid[(x,y)].veg_inten - .005),
                        #veg_vol = max(0.,self.grid[(x,y)].veg_vol - (new_fire_inten/4.)),
                        wind_direc= self.grid[(x,y)].wind_direc,
                        wind_inten= self.grid[(x,y)].wind_inten,
                        # some previous intensity and a combination of surrounding intensities 
                        fire_inten= round(new_fire_inten,2),
                        firefighter = False,
                        ff_info = None 
                   )
                elif self.grid[(x,y)].fire_inten == 0: # cell is not burning but can catch (assuming cells don't randomly catch fire)
                    ## need to take into account the conditions of surrounding cells
                    total_inten = 0.
                    for dx,dy in self.hood:
                        if (x+dx,y+dy) in self.grid:
                            total_inten += self.grid[(x+dx,y+dy)].fire_inten # will somehow need to handle the surrounding fire  
                    new_fire_inten = (total_inten * self.grid[(x,y)].veg_inten)/8. # to do: take into account wind somehow
                    if not self.grid[(x,y)].veg_inten and new_fire_inten:
                        print x, y, new_fire_inten
                    newgrid[(x,y)] = Cell(
                        x= x,
                        y= y,
                        time= self.grid[(x,y)].time,
                        veg_inten = self.grid[(x,y)].veg_inten,
                        #veg_vol = max(0.,self.grid[(x,y)].veg_vol - new_fire_inten),
                        wind_direc= self.grid[(x,y)].wind_direc,
                        wind_inten= self.grid[(x,y)].wind_inten,
                        fire_inten= round(new_fire_inten,2),
                        firefighter = False,
                        ff_info = None 
                   )
                if self.firefighters[x][y]: ## there is a firefighter in that cell
                    new_ff_coord.append((x, y))
                    
        for x, y in new_ff_coord:
            dx, dy = self.grid[(x,y)].ff_info.bestAction(newgrid) ## somewhere here need to check if it's a legal action
            newgrid[(x+dx, y+dy)].firefighter = True
            newgrid[(x+dx, y+dy)].ff_info = self.grid[(x,y)].ff_info
            newgrid[(x+dx, y+dy)].fire_inten = 0.
            newgrid[(x+dx, y+dy)].veg_inten = 0.
            self.firefighters[x+dx][y+dy] = True
            self.firefighters[x][y] = False
                    
        self.grid = newgrid
        return newgrid

    ## printing functions
    def gprint(self):
        txt = '\n'.join(' * '.join(str(self.grid[(x,y)].fire_inten) for x in range(L))
                         for y in range(L))
        print(txt)

#     def quickprint(self,grid):
#         t = b = 0
#         ll = L * L
#         for x in range(L):
#             for y in range(L):
#                 if grid[(x,y)] in (tree, burning):
#                     t += 1
#                     if grid[(x,y)] == burning:
#                         b += 1
#         print(('Of %6i cells, %6i are trees of which %6i are currently burning.'
#               + ' (%6.3f%%, %6.3f%%)')
#               % (ll, t, b, 100. * t / ll, 100. * b / ll))
