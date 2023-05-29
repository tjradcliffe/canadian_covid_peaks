
from datetime import datetime, timedelta
import math
import sys

import simple_minimizer as sm
from peaks_objective import PeaksObjective

lstStarts = [110, 1000, 3000,
354, 2000, 5000,
460, 2000, 4700,
625, 2000, 2500,
735, 1000, 11000,
825, 1000, 7500,
925, 2000, 6000,
1005, 2000, 6500,
1075, 2000, 5500,
1150, 10000, 3000]
lstScales = [1 for nI in range(len(lstStarts))]

nDim = len(lstStarts)
pMinimizer = sm.SimpleMinimizer(nDim)
pObjective = PeaksObjective("can_hosp_patients.csv")
pMinimizer.setObjective(pObjective)
pMinimizer.setStarts(lstStarts)
pMinimizer.setScales(lstScales)

nCount, pResult, nReason = pMinimizer.minimize()
lstVertex = pResult.getVertex()
print(nCount, nReason)
print(pResult.getValue())
print(lstVertex)
print("")
nYear, nMonth, nDay = map(int, pObjective.strStartDate.split("-"))
pStartDate = datetime(nYear, nMonth, nDay)
nCount = 0
nPrevious = 0
with open("can_hosp_patients_parameters.csv", "w") as outFile:
    outFile.write("# Peak Date Height SDev Area Spacing\n")
    for nPeak in range(0, nDim, 3):
    #    print(lstVertex[nPeak:nPeak+3])
        fSDev = math.sqrt(lstVertex[nPeak+1]/2)
        fNorm = lstVertex[nPeak+2]*math.sqrt(2*math.pi)*fSDev
        pDate = pStartDate+timedelta(days=lstVertex[nPeak])
        nSpacing = lstVertex[nPeak]-nPrevious
        nPrevious = lstVertex[nPeak]
        outFile.write(" ".join(map(str, (nCount, pDate.date(), lstVertex[nPeak+2], fSDev, fNorm, nSpacing)))+"\n")
        nCount += 1
        
with open("can_hosp_patients_fit.csv", "w") as outFile:
    outFile.write("# "+" ".join(map(str, lstVertex))+"\n")
    outFile.write("# "+pObjective.strStartDate+"\n")
    for nDay in range(len(pObjective.lstData)):
        fFit = pObjective.fit(nDay, lstVertex)
        pDate = pStartDate + timedelta(days=nDay)
        outFile.write(" ".join(map(str, (nDay, pDate.date(), fFit)))+" ")
        lstComponents = pObjective.components(nDay, lstVertex)
        outFile.write(" ".join(map(str, lstComponents)))        
        outFile.write("\n")
        
    for nI in range(nDay+1, nDay+200):
        fFit = pObjective.fit(nI, lstVertex)
        pDate = pStartDate + timedelta(days=nI)
        outFile.write(" ".join(map(str, (nI, pDate.date(), fFit)))+" ")
        lstComponents = pObjective.components(nI, lstVertex)
        outFile.write(" ".join(map(str, lstComponents)))        
        outFile.write("\n")

with open("can_hosp_patients.dat", "w") as outFile:
    for nDay in range(len(pObjective.lstData)):
        pDate = pStartDate + timedelta(days=nDay)
        outFile.write(" ".join(map(str, (pDate.date(), pObjective.lstData[nDay])))+"\n")
