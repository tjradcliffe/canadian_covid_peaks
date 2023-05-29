import math
from simple_minimizer import LowerLogisticConstraint

class PeaksObjective:
    
    def __init__(self, strFilename, nMaxDay = -1, nMInDay = 0):
        
        self.lstData = []
        self.strStartDate = ""
        self.pConstraint = LowerLogisticConstraint(0) # force all parameters > 0
        with open(strFilename) as inFile:
            nCount = 0
            for strLine in inFile:
                if strLine.strip().startswith("#"):
                    self.strStartDate = strLine.strip().split()[1]
                    continue
                nCount += 1
                if nCount < nMInDay:
                    continue
                self.lstData.append(float(strLine.strip().split()[1]))
                if nMaxDay >= 0 and len(self.lstData) > nMaxDay:
                    break

    def __call__(self, lstX):
        
        # lstX has structure pos1, width1, area1, pos2 ...

        fError = 0.0
        for nDay, fValue in enumerate(self.lstData):
            fError += (self.fit(nDay, lstX)-fValue)**2
        return math.sqrt(fError/nDay)

    def fit(self, nDay, lstX):
        fFit = 0.0
        for nPeak in range(0, len(lstX), 3): # add peaks
            fFit += self.peak(nDay, lstX[nPeak:nPeak+3])
        return fFit

    def components(self, nDay, lstX):
        lstComponents = []
        for nPeak in range(0, len(lstX), 3): # add peaks
            lstComponents.append(self.peak(nDay, lstX[nPeak:nPeak+3]))
        return lstComponents
        
    def peak(self, nDay, lstPeak):
        fValue = -1E8
        try:
            fPosition = self.pConstraint(lstPeak[0])
            fWidth = self.pConstraint(lstPeak[1])
            fArea = self.pConstraint(lstPeak[2])
            fValue = fArea*math.exp(-(nDay-fPosition)**2/fWidth)
        except OverflowError as e:
            print(lstPeak)
            sys.exit(-1)
        return fValue
