import numpy as np

class FireModel:
	def __init__(self, fireLayerTemp, fuelSupplyMass, thermDiffus, tempRise, propCoef, scaledCoef, fuelDispearRate, ambTemp, windSpeed):
		self.fireLayerTemp = fireLayerTemp
		self.fuelSupplyMass = fuelSupplyMass
		self.thermDiffus = thermDiffus
		self.tempRise = tempRise
		self.propCoef = propCoef
		self.scaledCoef = scaledCoef
		self.fuelDispearRate = fuelDispearRate
		self.ambTemp = ambTemp
		self.windSpeed = windSpeed

	def changeTemp():
		diffusion = np.gradient(self.thermDiffus * np.gradient(self.fireLayerTemp))
		heatAdvancedByWind = self.windSpeed * np.gradient(self.fireLayerTemp)
		rateFuelComsumedByBurning = self.fuelSupplyMass * np.exp(-self.propCoef/(self.fireLayerTemp - self.ambTemp))
		convectiveHeatLostAtmosphere = self.scaledCoef * (self.fireLayerTemp - self.ambTemp)
		return diffusion - heatAdvancedByWind + self.tempRise * (rateFuelComsumedByBurning - convectiveHeatLostAtmosphere)

	def changeFuelSupply():
		expTemp = np.exp(-self.propCoef/(self.fireLayerTemp - self.ambTemp))
		return -1 * self.fuelDispearRate * self.fuelSupplyMass * expTemp