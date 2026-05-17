import argparse
from datetime import datetime, timedelta
import math
import sys

import simple_minimizer as sm

mapConvergenceReasons = {-1: "Exceeded iteration limit", 1: "Closest points indistinguishable", 
                                                 2: "Met fractional tolerance", 3:"Minimum scale achieved"}

class SeirsModelObjective:
    
    def __init__(self, strDataFile, strModelFile):
        
        self.pFitStart = datetime(2023, 7, 1) # low point
        
        self.lstData = []
        self.pDate = None
        nCount = 0
        self.nStart = -1
        with open(strDataFile) as inFile:
            for strLine in inFile:
                if self.pDate is None:
                    if strLine.strip().startswith("#"):
                        self.pDate = datetime.strptime(strLine.strip().split()[1], "%Y-%m-%d")
                        continue
                else:
                    if self.pDate > self.pFitStart:
                        if self.nStart < 0:
                            self.nStart = nCount
                            print("Starting point: ", self.nStart)
                        self.lstData.append(float(strLine.strip().split()[1]))
                    self.pDate += timedelta(days=1)
                    nCount += 1
                
        self.lstSeirsModel = []
        with open(strModelFile) as inFile:
            for strLine in inFile:
                lstLine = strLine.strip().split()
                self.lstSeirsModel.append(int(lstLine[1]))

    def __call__(self, lstX):
        
        # lstX = [offset, multiplier]
        fOffset, fMultiplier = lstX
        
        fError = 0.0
        nCount = 0
        for nDay, fValue in enumerate(self.lstData):
            nMatchDay = int(nDay + fOffset)
            if nMatchDay >= 0 and nMatchDay < len(self.lstSeirsModel):
                fError += (fValue-fMultiplier*self.lstSeirsModel[nMatchDay])**2
                nCount += 1
        return math.sqrt(fError/nCount)

def fitSeirsModel(strFilename):

    nParameters = 2
    pMinimizer = sm.SimpleMinimizer(nParameters)
    pObjective = SeirsModelObjective(strFilename, "seirs_model.csv")
    pMinimizer.setObjective(pObjective)
    pMinimizer.setStarts([0, 0.3])
    pMinimizer.setScales([25, 0.05])
    pMinimizer.setMinimumScale(1E-6) # the minimum is pretty well defined

    print("Fitting... this may take a minute or two...")
    nCount, pResult, nReason = pMinimizer.minimize()
    lstVertex = pResult.getVertex()

    print("Iterations:", nCount)
    print("Reason for termination:", mapConvergenceReasons[nReason])
    print("Residual RMS Error: ",pResult.getValue())
    print("Offset, multiplier: ", lstVertex[0], lstVertex[1])
    nOffset = int(lstVertex[0])
    fMultiplier = lstVertex[1]
    lstModel = pObjective.lstSeirsModel
    with open(strFilename.replace(".csv", "_model.csv"), "w") as outFile:
        for nI, fValue in enumerate(lstModel):
            outFile.write(str(nI+pObjective.nStart-nOffset)+" "+str(fMultiplier*fValue)+"\n")

if __name__ == "__main__":
    fitSeirsModel("can_hosp_patients.csv")
