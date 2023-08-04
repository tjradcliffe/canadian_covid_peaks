
"""Playing around with differences and derivatives to see
if I can set a better handle on deviations from the fit to
predict when a new wave is starting.

Thus far, this is a complete failure.
"""

nWaves = 10

lstDate = []
lstData = []
lstWaves = [[] for nI in range(nWaves)]
with open("can_hosp_patients.dat") as inFile:
    for strLine in inFile:
        lstDate.append(strLine.strip().split()[0])
        lstLine = list(map(float, strLine.strip().split()[1:]))
        lstData.append(lstLine[0])
        for nI in range(1, nWaves+1):
            lstWaves[nI-1].append(lstLine[nI])

lstDiffs = [[] for nI in range(nWaves)]
for nI, fValue in enumerate(lstData):
    for nJ in range(nWaves):
        lstDiffs[nJ].append(fValue-lstWaves[nJ][nI])
        
with open("diffs.dat", "w") as outFile:
    for nI in range(len(lstData)):
        strOut = lstDate[nI]+" "
        strOut += " ".join(map(str, [lstDiffs[nJ][nI] for nJ in range(nWaves)]))
        outFile.write(strOut+"\n")

lstDeriv = [[0] for nI in range(nWaves)]
lstDataDeriv = [0, 0, 0, 0, 0, 0, 0]
for nI, fValue in enumerate(lstData):
    if not nI: continue # skip first
    if nI > 6:
        lstDataDeriv.append(fValue-lstData[nI-7])
    for nJ in range(nWaves):
        lstDeriv[nJ].append(lstWaves[nJ][nI]-lstWaves[nJ][nI-1])
        
with open("deriv.dat", "w") as outFile:
    for nI in range(len(lstData)):
        strOut = lstDate[nI]+" "+str(lstDataDeriv[nI])+" "
        strOut += " ".join(map(str, [lstDeriv[nJ][nI] for nJ in range(nWaves)]))
        outFile.write(strOut+"\n")
        