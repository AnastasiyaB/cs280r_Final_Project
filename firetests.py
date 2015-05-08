import numpy as np
import matplotlib.pyplot as plt
import firesim

# DEFINE FUNCTIONS

# Helper dist function
def sqDistFromCenter(point, center):
	pX, pY = point
	cX, cY = center
	return float((pX-cX)**2 + (pY-cY)**2)

# Point Firefighters
# point = top, right, bottom, left
def generatePointFFs(center, radius, point = 'top', numFFs = 8):
	# How many FFs to left of center
	leftFFs = numFFs/2
	rightFFs = numFFs - leftFFs
	ffs = []

	if point == 'top':
		# Lineup numFFs across top of fire
		for ffPosX in range(center[0] - numFFs/2, center[0] + rightFFs):
			ffPosY = center[1] + radius + 1
			ffs.append((ffPosX, ffPosY))

	elif point == 'right':
		# Lineup numFFs along right side of fire
		for ffPosY in range(center[1] - numFFs/2, center[1] + rightFFs):
			ffPosX = center[0] + radius + 1
			ffs.append((ffPosX, ffPosY))

	elif point == 'bottom':
		# Lineup numFFs across bottom of fire
		for ffPosX in range(center[0] - numFFs/2, center[0] + rightFFs):
			ffPosY = center[1] - radius - 1
			ffs.append((ffPosX, ffPosY))

	elif point == 'left':
		# Lineup numFFs along left side of fire
		for ffPosY in range(center[1] - numFFs/2, center[1] + rightFFs):
			ffPosX = center[0] - radius - 1
			ffs.append((ffPosX, ffPosY))

	return ffs

# Surround Firefighters
def generateSurroundFFs(center, radius, numFFs = 8):
	ffs = []
	# indices: top - 0, right - 1, bottom - 2, left - 3
	ind = ['top', 'right', 'bottom', 'left']
	# Distribution of how many FFs per side
	ffDist = [0 for i in range(4)]
	for i in range(numFFs):
		ffDist[i%4] += 1

	# Iterate through the 4 locations and generate a point allocation
	# based on num FFs assigned to each location
	for i in range(len(ffDist)):
		ffs += generatePointFFs(center, radius, point = ind[i], numFFs = ffDist[i])

	return ffs

# Optimal Firefighters
def generateOptimalFFs(center, radius, numFFs = 8):
	# TODO using Anastasiya's code
	return False

def generateRoundFire(center, radius, minInten = 0.1):
	fire = [(center[0], center[1], 1)]
	for dx in range(-radius, radius+1):
		for dy in range(-radius, radius+1):
			# Generate new point
			newFirePt = (center[0] + dx, center[1] + dy)
			# Get intensity proportional to sq distance from center (1 at center, minInten on outside)
			# ie on the outside: sqDist = 16, radius = 16, minInten = .25
			# We then have 1-((16*(1-.25)))/16) = 1 - 12/16 = 1-.75 = .25, which is the desired result
			fireInten = 1. - (sqDistFromCenter(newFirePt, center) * (1-minInten))/(2*(radius**2))
			newFireCell = (newFirePt[0], newFirePt[1], fireInten)
			if not (newFireCell in fire):
				fire.append(newFireCell)
	return fire

def generateEllipseFire(center, xRadius, yRadius, minInten = 0.1):
	fire = [(center[0], center[1], 1)]
	for dx in range(-xRadius, xRadius+1):
		for dy in range(-yRadius, yRadius+1):
			# Generate new point
			newFirePt = (center[0] + dx, center[1] + dy)
			# Get intensity proportional to sq distance from center (1 at center, minInten on outside)
			# ie on the outside: sqDist = 16, radius = 16, minInten = .25
			# We then have 1-((16*(1-.25)))/16) = 1 - 12/16 = 1-.75 = .25, which is the desired result
			fireInten = 1. - (sqDistFromCenter(newFirePt, center) * (1-minInten))/(2*(xRadius**2))
			newFireCell = (newFirePt[0], newFirePt[1], fireInten)
			if not (newFireCell in fire):
				fire.append(newFireCell)
	return fire

def generateOddFire(center, radius, minInten = 0.1):
	fire = [(center[0], center[1], 1)]
	for dx in range(-radius, radius+1):
		for dy in range(-radius, radius+1):
			# Generate new point
			newFirePt = (center[0] + dx, center[1] + dy)
			# Get intensity proportional to sq distance from center (1 at center, minInten on outside)
			# ie on the outside: sqDist = 16, radius = 16, minInten = .25
			# We then have 1-((16*(1-.25)))/16) = 1 - 12/16 = 1-.75 = .25, which is the desired result
			fireInten = 1. - (sqDistFromCenter(newFirePt, center) * (1-minInten))/(2*(radius**2))
			newFireCell = (newFirePt[0], newFirePt[1], fireInten)
			if abs(dx-dy) < radius/2 and not (newFireCell in fire):
				fire.append(newFireCell)
	return fire

################################################################
# BUILD FIRES

testSize = 10
totalNumFFs = 8
fires = []

# Round fire
center = (testSize/2, testSize/2)

## Small
smallRadius = 1
smallFireR = generateRoundFire(center, smallRadius)
fires.append(("Small Round Fire", center, smallRadius, smallFireR))

## Medium
medRadius = 2
medFireR = generateRoundFire(center, medRadius)
fires.append(("Med Round Fire", center, medRadius, medFireR))

## Large
largeRadius = 3
largeFireR = generateRoundFire(center, largeRadius)
fires.append(("Med Round Fire", center, largeRadius, largeFireR))

# Elliptical fire - right facing
center = (testSize/2, testSize/2)

## Small
smallRadius = 1
smallFireE = generateEllipseFire(center, smallRadius*2, smallRadius)
fires.append(("Small Ellipse Fire", center, smallRadius, smallFireE))

## Medium
medRadius = 2
medFireE = generateEllipseFire(center, medRadius*2, medRadius)
fires.append(("Med Ellipse Fire", center, medRadius, medFireE))

## Large
largeRadius = 3
largeFireE = generateEllipseFire(center, largeRadius*2, largeRadius)
fires.append(("Large Ellipse Fire", center, largeRadius, largeFireE))

# Odd-shaped fire
center = (testSize/2, testSize/2)

## Small
smallRadius = 1
smallFireO = generateRoundFire(center, smallRadius)
fires.append(("Small Odd Fire", center, smallRadius, smallFireO))

## Medium
medRadius = 3
medFireO = generateRoundFire(center, medRadius)
fires.append(("Med Odd Fire", center, medRadius, medFireO))

## Large
largeRadius = 3
largeFireO = generateRoundFire(center, largeRadius)
fires.append(("Large Odd Fire", center, largeRadius, largeFireO))

###################################################################
## RUN TESTS
# figIdx = 1
# styles = ["Point Configuration - ", "Surround Configuration - ", "Optimal Configuration - "]
# strats = ["random", "greedy"]
# strats2 = ["random", "greedy", "optimal", "teamOptimal"]
# for name, center, radius, cells in fires:
# 	for configStyle in range(2): # 0 - point, 1 - surround, 2 - optimal
# 		for strat in strats:
# 			trials = 10
# 			stepsToExtinguish = []

# 			# Initialize figure
# 			fig = plt.figure(figIdx)
# 			fig.suptitle(styles[configStyle] + name + " (" + strat+ ")")
# 			plt.xlabel('Iterations')
# 			plt.ylabel('Turns to Extinguish')

# 			# Run through trials, save outputs, and plot		
# 			for tri in range(trials):
# 				# Init
# 				sim = firesim.AreaSimulation(testSize)
# 				sim.initialize()

# 				# Light the fire and count the num fires lit
# 				c = 0
# 				for x, y, inten in cells:
# 					sim.grid[(x, y)].fire_inten = inten
# 					c += 1
# 				# sim.num_fires = c

# 				if configStyle == 0:
# 					ff_config = generatePointFFs(center, radius, point = 'top', numFFs = totalNumFFs)

# 				elif configStyle == 1:
# 					ff_config = generateSurroundFFs(center, radius, numFFs = totalNumFFs)

# 				else:
# 					ff_config = sim.best_ff_config(totalNumFFs)

# 				for ff in ff_config:
# 					ff2 = firesim.FireFighter(ff[0], ff[1], sim, style = strat, efficacy = 1)
# 			    	sim.fight_fire(ff2)

# 				# sim.gprint()
# 			    # Run simulation
# 				steps = 0
# 				iters = 50

# 				for itr in range(iters):
# 					sim.gnew()
# 					steps += 1
# 					print sim.num_fires
# 					if sim.num_fires == 0:
# 						break
# 				stepsToExtinguish.append(steps)
# 				print "Done Trial with", steps, "steps"
# 				# sim.gprint()	    	

# 			print "Done. Plotting", styles[configStyle], name, strat
# 			plt.plot(stepsToExtinguish)
# 			fig.savefig(styles[configStyle] + name + strat + '.jpg')
# 			figIdx += 1




# Init
figIdx = 1
name, center, radius, cells = ("Small Round Fire", center, smallRadius, smallFireR)
styles = ["Point Configuration - ", "Surround Configuration - ", "Optimal Configuration - "]
strats = ["random", "greedy"]
strats2 = ["random", "greedy", "optimal", "teamOptimal"]
# print name, center, radius, cells
# print "###"
for name, center, radius, cells in fires:
	for configStyle in range(2): # 0 - point, 1 - surround, 2 - optimal
		for strat in strats2:
			trials = 10
			stepsToExtinguish = []

			# Initialize figure
			fig = plt.figure(figIdx)
			fig.suptitle(name)
			plt.xlabel('Iterations')
			plt.ylabel('Turns to Extinguish')
			for t in range(trials):
				sim = firesim.AreaSimulation(testSize)
				sim.initialize()
			
				# Light the fire and count the num fires lit
				c = 0
				for x, y, inten in cells:
					sim.grid[(x, y)].fire_inten = inten
					c += 1
				# sim.num_fires = c

				if configStyle == 0:
					ff_config = generatePointFFs(center, radius, point = 'top', numFFs = totalNumFFs)

				elif configStyle == 1:
					ff_config = generateSurroundFFs(center, radius, numFFs = totalNumFFs)

				else:
					ff_config = sim.best_ff_config(totalNumFFs)

				for ff in ff_config:
					ff2 = firesim.FireFighter(ff[0], ff[1], sim, style = strat, efficacy = 1)
					sim.fight_fire(ff2)

				# sim.gprint()
				# Run simulation
				steps = 0
				iters = 50
				for itr in range(iters):
					sim.gnew()
					steps += 1
					#print sim.num_fires
					if sim.num_fires == 0:
						break
				stepsToExtinguish.append(steps)
				print "Done Trial with", steps, "steps"


			print "Done. Plotting", styles[configStyle], name, strat
			plt.plot(stepsToExtinguish, label = styles[configStyle] + " (" + strat + ")")
	plt.legend()
	fig.savefig(name + '.jpg')
	figIdx += 1
