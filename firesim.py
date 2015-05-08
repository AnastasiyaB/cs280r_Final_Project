import random
from utils import *
import itertools
import sys
import ast

## class representation for each cell
class Cell:
    def __init__(self, x, y, time, veg_inten, wind_direc, wind_inten, fire_inten, firefighter, ff_info, exting):
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
        self.exting = exting

## code borrowed from: http://aima.cs.berkeley.edu/python/mdp.html
class MDP:
    """A Markov Decision Process, defined by an initial state, transition model,
    and reward function. We also keep track of a gamma value, for use by
    algorithms. The transition model is represented somewhat differently from
    the text.  Instead of T(s, a, s') being  probability number for each
    state/action/state triplet, we instead have T(s, a) return a list of (p, s')
    pairs.  We also keep track of the possible states, terminal states, and
    actions for each state. [page 615]"""

    def __init__(self, init, L, actlist, gamma=.9):
        self.L = L
        update(self, init=init, actlist=actlist,
               gamma=gamma, states=set(), reward={})

    def R(self, state):
        "Return a numeric reward for this state."
        return self.reward[state]

    def T(state, action):
        """Transition model.  From a state and an action, return a list
        of (result-state, probability) pairs."""
        abstract

    def actions(self, state):
        """Set of actions that can be performed in this state.  By default, a
        fixed list of actions, except for terminal states. Override this
        method if you need to specialize by state."""
        ### just return all the actions for now but would have to check whether in the boundaries
        possible_actions = []
        for dx, dy in self.actlist:
            if state[0] + dx >= 0 and state[0] + dx < self.L \
               and state[1] + dy >= 0 and state[1] + dy < self.L:
                    possible_actions.append((dx,dy))
        return possible_actions
        

class GridMDP(MDP):
    """A two-dimensional grid MDP, as in [Figure 17.1].  All you have to do is
    specify the grid as a list of lists of rewards; use None for an obstacle
    (unreachable state).  Also, you should specify the terminal states.
    An action is an (x, y) unit vector; e.g. (1, 0) means move east."""
    def __init__(self, grid, actions, init=(0, 0), gamma=.9): # eliminated terminals
        #grid.reverse() ## because we want row 0 on bottom, not on top
        L = len(grid)
        MDP.__init__(self, init, L, actlist=actions, gamma=gamma)
        update(self, grid=grid, rows=len(grid), cols=len(grid[0]))
        for x in range(self.cols):
            for y in range(self.rows):
                self.reward[x, y] = grid[y][x]
                if grid[y][x] is not None:
                    self.states.add((x, y))

    # think more about what our transition model here is
    def T(self, state, action):       
        if action == None:
            return [(0.0, state)]
        else:
            # deterministic
            return [(1., (state[0]+action[0], state[1]+action[1]))]

def value_iteration(mdp, epsilon=0.001):
    "Solving an MDP by value iteration. [Fig. 17.4]"
    U1 = dict([(s, 0) for s in mdp.states])
    R, T, gamma = mdp.R, mdp.T, mdp.gamma
    while True:
        U = U1.copy()
        delta = 0
        for s in mdp.states:
            U1[s] = R(s) + gamma * max([sum([p * U[s1] for (p, s1) in T(s, a)]) for a in mdp.actions(s)])
            delta = max(delta, abs(U1[s] - U[s]))
        if delta < epsilon * (1 - gamma) / gamma:
             return U

def best_policy(mdp, U):
    """Given an MDP and a utility function U, determine the best policy,
    as a mapping from state to action. (Equation 17.4)"""
    pi = {}
    for s in mdp.states:
        pi[s] = argmax(mdp.actions(s), lambda a:expected_utility(a, s, U, mdp))
    return pi

def expected_utility(a, s, U, mdp):
    "The expected utility of doing a in state s, according to the MDP and U."
    return sum([p * U[s1] for (p, s1) in mdp.T(s, a)])


def policy_iteration(mdp):
    "Solve an MDP by policy iteration [Fig. 17.7]"
    U = dict([(s, 0) for s in mdp.states])
    pi = dict([(s, random.choice(mdp.actions(s))) for s in mdp.states])
    while True:
        U = policy_evaluation(pi, U, mdp)
        unchanged = True
        for s in mdp.states:
            a = argmax(mdp.actions(s), lambda a: expected_utility(a,s,U,mdp))
            if a != pi[s]:
                pi[s] = a
                unchanged = False
        if unchanged:
            return pi

def policy_evaluation(pi, U, mdp, k=20):
    """Return an updated utility mapping U from each state in the MDP to its
    utility, using an approximation (modified policy iteration)."""
    R, T, gamma = mdp.R, mdp.T, mdp.gamma
    for i in range(k):
        for s in mdp.states:
            U[s] = R(s) + gamma * sum([p * U[s] for (p, s1) in T(s, pi[s])])
    return U
  
## class representation for each firefighter
class FireFighter:
    def __init__(self, x, y, area, style = "random", efficacy = 1):
        self.x = x # The starting cell/cell we're currently in
        self.y = y
        self.area = area # The grid where the firefighter lives
        self.path = [] # The path we've traverse so far
        self.efficacy = efficacy # Perhaps make this model vary on fighter skill level
        self.style = style # random, greedy, optimal, teamOptimal
        self.actList = [(-1,-1), (-1,0), (-1,1), (0,-1), 
                   (0, 1), (1,-1),  (1,0),  (1,1)]
                 
    # FIX THIS!!
    def calculate_rewards(self,grid):
        # TODO: take into account safety more
        L = int(math.sqrt(len(grid)))
        reward_grid = []
        for y in range(L):
            reward_row = []
            for x in range(L):
                #if fire intensity > .8 reward for going there is 0
                # if grid[(x,y)].fire_inten > .8:
                #     reward_row.append(0.)
                # else if fire intensity between 0 and .8 reward for going there is fire.inten itself
                if grid[(x,y)].fire_inten > 0: # and grid[(x,y)].fire_inten <= .8
                    reward_row.append(grid[(x,y)].fire_inten)
                # else it depends of proximity to a the most intense fire divided by how far it is
                else:
                    reward_row.append(0.)
                    # max_neighbor = 0
                    # times = 0.
                    # while max_neighbor == 0 and times < L:
                    #     times +=1.
                    #     for dx,dy in self.actList:
                    #         if (x+dx*times,y+dy*times) in grid:
                    #             max_neighbor = max(max_neighbor, grid[(x+dx*times,y+dy*times)].fire_inten)
                    # reward_row.append(max_neighbor/times) ## need to discount somehow -- picked 1/2 arbitrarily -- removed
            reward_grid.append(reward_row)

        return reward_grid
    
    # Random
    def bestActionRandom(self, grid):
        act = None
        while not act:
            # Random
            act = random.choice(self.actList)
            dx, dy = act
            if self.x + dx >= 0 and self.x + dx < self.area.L \
               and self.y + dy >= 0 and self.y + dy < self.area.L:
                fft = grid[(self.x + dx, self.y + dy)].firefighter
                fft2 = self.area.firefighters[self.x + dx][self.y + dy]
                if (not fft) and (not fft2):
                    break
                else:
                    act = None
            else:
                act = None
        self.path.append(act)
        self.x += act[0]
        self.y += act[1]
        return act

    # Single agent Greedy
    def bestActionGreedy(self, grid):
        # Greedy
        max_inten = 0.
        max_move = None
        mult = 1
        while not max_move and mult < self.area.L:
            for dx, dy in self.actList:
                dx = mult*dx
                dy = mult*dy
                if self.x + dx >= 0 and self.x + dx < self.area.L \
                   and self.y + dy >= 0 and self.y + dy < self.area.L:
                    it = self.area.grid[(self.x + dx, self.y + dy)].fire_inten
                    fft = grid[(self.x + dx, self.y + dy)].firefighter
                    fft2 = self.area.firefighters[self.x + dx][self.y + dy]
                    fft3 = self.area.grid[(self.x + dx, self.y + dy)].firefighter
                    if it > max_inten and (not fft) and (not fft2) and (not fft3):
                        max_inten = it
                        max_move = (dx/mult, dy/mult)
            mult += 1
        if not max_move:
            print "No more fire left"
            max_move = self.bestActionRandom(grid)
        act = max_move
        self.path.append(act)
        self.x += act[0]
        self.y += act[1]
        return act

    # Single Agent Optimal MDP via VI/PI
    def bestActionSingleMDP(self, newgrid):
        reward_grid = self.calculate_rewards(self.area.grid)
        #print "reward grid", reward_grid
        my_grid = GridMDP(reward_grid, self.actList)
        values = value_iteration(my_grid)
        best_pol = best_policy(my_grid,values)
        return best_pol[(self.x,self.y)]

    # Sequential Optimal MDP
    def bestActionSeqMDP(self, newgrid):
        reward_grid = self.calculate_rewards(newgrid)
        #print "reward grid", reward_grid
        my_grid = GridMDP(reward_grid, self.actList)
        values = value_iteration(my_grid)
        best_pol = best_policy(my_grid,values)
        return best_pol[(self.x,self.y)]

    # Return best action based on type
    def bestAction(self, newgrid):
        if self.style == "random":
            return self.bestActionRandom(newgrid)

        if self.style == "greedy":
            return self.bestActionGreedy(newgrid)

        if self.style == "optimal":
            return self.bestActionSingleMDP(newgrid)

        if self.style == "teamOptimal":
            return self.bestActionSeqMDP(newgrid)
            
       
class AreaSimulation:
    def __init__(self, L):
        self.grid = {}
        self.hood = ((-1,-1), (-1,0), (-1,1),
                (0,-1),          (0, 1),
                (1,-1),  (1,0),  (1,1))
        
        self.L = L
        self.time = 0
        self.firefighters = [[False for i in range(L)] for j in range(L)]
        self.num_fires = 0
        self.burning = 0  
        
    def fight_fire(self, ff_info):
        self.grid[(ff_info.x, ff_info.y)].firefighter = True
        self.grid[(ff_info.x, ff_info.y)].ff_info = ff_info
        self.firefighters[ff_info.x][ff_info.y] = True
        return
        
    def initialize(self):
        for x in range(self.L):
            for y in range(self.L):
                self.grid[(x,y)] = Cell(
                    x= x,
                    y= y,
                    time= 0,
                    veg_inten= random.random(),
                    #veg_vol = random.random()*10,
                    wind_direc= random.choice(["n", "nw", "w", "s", "sw", "e", "ne", "se"]),
                    wind_inten= random.random(),
                    fire_inten= 0.00,
                    firefighter = False,
                    ff_info = None,
                    exting = False
                )            
        return self.grid
    
    def wind_influence(self,x,y):
        wind_inf = 0.
        for dx,dy in self.hood:
            if (x+dx,y+dy) in self.grid:
                if ((dx == -1 and dy == -1 and self.grid[(x+dx,y+dy)].wind_direc == "se") or 
                (dx == -1 and dy == 0 and self.grid[(x+dx,y+dy)].wind_direc == "s") or 
                (dx == -1 and dy == 1 and self.grid[(x+dx,y+dy)].wind_direc == "sw") or
                (dx == 0 and dy == -1 and self.grid[(x+dx,y+dy)].wind_direc == "e") or
                (dx == 0 and dy == 1 and self.grid[(x+dx,y+dy)].wind_direc == "w") or
                (dx == 1 and dy == -1 and self.grid[(x+dx,y+dy)].wind_direc == "ne") or
                (dx == 1 and dy == 0 and self.grid[(x+dx,y+dy)].wind_direc == "n") or
                (dx == 1 and dy == 1 and self.grid[(x+dx,y+dy)].wind_direc == "nw")):
                    wind_inf += self.grid[(x+dx,y+dy)].wind_inten * self.grid[(x+dx,y+dy)].fire_inten
        return wind_inf
    
    def gnew(self):
        newgrid = {}
        new_ff_coord = []
        self.time += 1
        # iterate through all the cells
        for x in range(self.L):
            for y in range(self.L): 
                
                print "current number of fires", self.num_fires
               
                if self.firefighters[x][y]: ## there is a firefighter in that cell
                    #print "firefighter in this cell", x,y
                    print "there is a firefighter in this cell",x,y
                    new_ff_coord.append((x, y))
                    print "num fires before ff", self.num_fires
                    if self.num_fires > 0:
                        # otherwise there's nothing to extinguish
                        self.num_fires-=1
                    print "num fires after", self.num_fires

                    
                    ## extinguish fire in this cell
                    newgrid[(x,y)] = Cell(
                        x= x,
                        y= y,
                        time = self.time if not self.grid[(x,y)].time else self.grid[(x,y)].time,
                        veg_inten = 0., # so it can't light on fire again
                        #veg_vol = max(0.,self.grid[(x,y)].veg_vol - (new_fire_inten/4.)),
                        wind_direc= self.grid[(x,y)].wind_direc,
                        wind_inten= self.grid[(x,y)].wind_inten,
                        # some previous intensity and a combination of surrounding intensities 
                        fire_inten= 0.,
                        firefighter = False,
                        ff_info = None,
                        exting = True
                   )

                elif self.grid[(x,y)].fire_inten > 0: # cell is burning
                    print "cell is burning",x,y
                    # if we multiply by 1 means just stays the same
                    wind_inf = 1 if self.wind_influence(x,y) == 0 else self.wind_influence(x,y)*10
                                     
                    ### revise this fire intensity func
                    print "num fires beofre", self.num_fires
                    new_fire_inten = min(self.grid[(x,y)].fire_inten * (self.grid[(x,y)].veg_inten) * wind_inf * 3, 1) 
                    if new_fire_inten == 0:                       
                        self.num_fires-=1

                    print "num fires after", self.num_fires

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
                        ff_info = None,
                        exting = self.grid[(x,y)].exting
                   )
                elif self.grid[(x,y)].fire_inten == 0: # cell is not burning but can catch (assuming cells don't randomly catch fire)
                    print "cell can catch",x,y
                    ## need to take into account the conditions of surrounding cells
                    wind_inf = 1 if self.wind_influence(x,y) == 0 else self.wind_influence(x,y)*10
                    
                    total_inten = 0.
                    for dx,dy in self.hood:
                        if (x+dx,y+dy) in self.grid:
                            total_inten += self.grid[(x+dx,y+dy)].fire_inten # will somehow need to handle the surrounding fire  
                    new_fire_inten = (total_inten * self.grid[(x,y)].veg_inten)/8. * wind_inf
                    
                    new_fire_inten = round(new_fire_inten,2)

                    print "num of fires before", self.num_fires
                    if new_fire_inten > 0:
                        if not self.grid[(x,y)].exting:
                            self.num_fires+=1
                    print "num of fires after", self.num_fires
                            
                    #if not self.grid[(x,y)].veg_inten and new_fire_inten: 
                    newgrid[(x,y)] = Cell(
                        x= x,
                        y= y,
                        time= self.grid[(x,y)].time,
                        veg_inten = self.grid[(x,y)].veg_inten,
                        #veg_vol = max(0.,self.grid[(x,y)].veg_vol - new_fire_inten),
                        wind_direc= self.grid[(x,y)].wind_direc,
                        wind_inten= self.grid[(x,y)].wind_inten,
                        fire_inten= new_fire_inten,
                        firefighter = False,
                        ff_info = None,
                        exting = self.grid[(x,y)].exting
                   )
                else:
                    print "Negative fire intensity"
                    
        for x, y in new_ff_coord:
            ## put the firefighter in the next cell
            # should we pass grid or newgrid here?
            dx, dy = self.grid[(x,y)].ff_info.bestAction(newgrid) ## somewhere here need to check if it's a legal action
            newgrid[(x+dx, y+dy)].firefighter = True
            newgrid[(x+dx, y+dy)].ff_info = self.grid[(x,y)].ff_info
            ## will need to change actual coordinates here
            newgrid[(x+dx, y+dy)].ff_info.x = x+dx
            newgrid[(x+dx, y+dy)].ff_info.y = y+dy                
            
            ## I don't see why we need this but ok
            self.firefighters[x+dx][y+dy] = True
            self.firefighters[x][y] = False

        self.grid = newgrid
        return newgrid

    ## printing function
    def gprint(self):
        txt = '\n'.join('|'.join(str(self.grid[(x,y)].fire_inten) for x in range(self.L))
                         for y in range(self.L))
        print(txt)

    # need to evaluate how well of a job the firefighters did
    # for now: the faster that the fire gets put out
    def best_ff_config(self, number_ffs=8, iters=50): # standard crew is 8 people
        # find all the cells where fire_inten > 0
        fires = []
        for x in range(self.L):
            for y in range(self.L):
                if self.grid[(x,y)].fire_inten:
                    fires.append((x,y))
                    
        # find all the possible places we could place the firefighters
        # (for now assuming we can't place them anywhere that's burning)
        ff_placement_poss = []
        for fire in fires:
            for dx, dy in self.hood:
                    # if it's within the boundaries
                    if fire[0] + dx >= 0 and fire[0] + dx < self.L \
                       and fire[1] + dy >= 0 and fire[1] + dy < self.L:
                            # and it's not already in our list
                            if (fire[0] + dx,fire[1] + dy) not in ff_placement_poss :
                              #  and (fire[0] + dx,fire[1] + dy) not in fires:
                                ff_placement_poss.append((fire[0] + dx,fire[1] + dy))
                                
        best_placement = None
        best_time = float('inf')
        
        possible_initial_placements = list(itertools.combinations(ff_placement_poss, number_ffs))
        for placement in possible_initial_placements:
            # place all the firefighters
            for pos in placement:
                sim = copy.deepcopy(self)
                ff = FireFighter(pos[0],pos[1],sim)
                sim.fight_fire(ff)
            # run the simulation until all the fire is eliminated
            for i in range(iters):
                sim.gnew()
                if sim.num_fires == 0: # all have been extinguished
                    #print "DONE"
                    #print best_placement
                    if i < best_time: # log the best time
                        best_time = i
                        best_placement = placement
                        break
        print "best time", best_time
        print "best placement", best_placement
        return best_placement
       

def main(argv):
    # assumes all the inputs are well defined
    area, iters, fire_coords, fire_inten, ff_coords = argv

    # initialize the simulation
    sim = AreaSimulation(int(area))
    sim.initialize()

    # start the fire
    fire_coords = ast.literal_eval(fire_coords)
   
    fire_inten = ast.literal_eval(fire_inten)

    ff_coords =  ast.literal_eval(ff_coords)

    
    for i in range(len(fire_inten)):
        sim.grid[(int(fire_coords[i*2]), int(fire_coords[i*2+1]))].fire_inten = float(fire_inten[i])
    
    sim.num_fires = len(fire_inten)

    for i in range(len(ff_coords)/2):
        ff = FireFighter(int(ff_coords[i*2]), int(ff_coords[i*2+1]),sim)
        sim.fight_fire(ff)

    for i in range(int(iters)):
        print "iteration",i
        sim.gprint()
        sim.gnew()
        print 
   
    # you could also find best config
    # sim.best_ff_config(2)


if __name__ == '__main__':
    main(sys.argv[1:])
