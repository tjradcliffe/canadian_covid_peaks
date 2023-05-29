import math

class LowerLogisticConstraint:
    """Forces parameter value to always be greater than level
    """
    def __init__(self, fLevel, fScale = 1):
        self.fLevel = fLevel # value to stay above
        self.fScale = fScale
        if fLevel != 0:
            self.fScale = abs(fLevel)
        self.fL = 4*self.fScale # leading factor
        self.fThreshold = fLevel+2*self.fScale # point where constraint kicks in
        print(self.fLevel, self.fScale, self.fThreshold)

    def __call__(self, fX):
        if fX < self.fThreshold:
            fX = (fX-self.fLevel)/self.fScale - 2
            try:
                fX = self.fLevel+self.fL/(1+math.exp(-fX))
            except OverflowError as e:
                fX = self.fLevel # overflow means we have maxed out
        return fX

class UpperLogisticConstraint:
    """Forces parameter value to always be lower than level
    """
    def __init__(self, fLevel, fScale = 1):
        self.fLevel = fLevel # value to stay above
        self.fScale = fScale
        if fLevel != 0:
            self.fScale = abs(fLevel)
        self.fL = 4*self.fScale # leading factor
        self.fThreshold = fLevel-2*self.fScale # point where constraint kicks in
        print(self.fLevel, self.fScale, self.fThreshold)

    def __call__(self, fX):
        if fX > self.fThreshold:
            fX = (fX-self.fLevel)/self.fScale + 2
            try:
                fX = self.fLevel-self.fL/(1+math.exp(fX))
            except OverflowError as e:
                fX = self.fLevel # overflow means we have maxed out
        return fX

if "__main__" == __name__:
    
    with open("upper_logistic.dat", "w") as outFile:
        fLevel = 0.001
        fScale = 0.001 #abs(fLevel)
        pConstraint = UpperLogisticConstraint(fLevel)
        for nI in range(0, 40):
            fX = fScale*(-4+nI*0.2)
            fY = pConstraint(fX)
            print(fX, fY)
            outFile.write(str(fX)+" "+str(fY)+"\n")
