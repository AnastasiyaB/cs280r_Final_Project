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
