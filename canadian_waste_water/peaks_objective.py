from datetime import date
import math

pStartDate = date(2023, 7, 1)

class PeaksObjective:
    
    def __init__(self, strFilename, pStartDate=date(2023, 7, 1), pEndDate = None):

        self.mapData = {}
        with open(strFilename) as inFile:
            for strLine in inFile:
                pDate = date.fromisoformat(strLine.strip().split()[0])
                if  pDate >= pStartDate and (pEndDate == None or pDate <= pEndDate):
                    nDays = (pDate-pStartDate).days
                    self.mapData[nDays] = float(strLine.strip().split()[1])
        self.lstDays = list(self.mapData.keys())
        self.lstDays.sort()

    def __call__(self, lstX):
        
        # lstX has structure area1, pos1, width1, area2, ...

        fError = 0.0
        for nDay in self.lstDays:
            fValue = self.mapData[nDay]
            fError += (self.fit(nDay, lstX)-fValue)**2
        return math.sqrt(fError/nDay)

    def fit(self, nDay, lstX):
        fFit = 0.0
        for nPeak in range(0, len(lstX), 3): # add peaks
            fFit += self.peak(nDay, lstX[nPeak:nPeak+3])
        return fFit

    def components(self, nDay, lstX):
        lstComponents = [] # start with slope
        for nPeak in range(0, len(lstX), 3): # add peaks
            lstComponents.append(self.peak(nDay, lstX[nPeak:nPeak+3]))
        return lstComponents
        
    def peak(self, nDay, lstPeak):
        fValue = -1E8
        try:
            fPeak = lstPeak[0]
            fPosition = lstPeak[1]
            fWidth = lstPeak[2]
            fValue = fPeak*math.exp(-(nDay-fPosition)**2/fWidth)
        except OverflowError as e:
            print(lstPeak)
            sys.exit(-1)
        return fValue
