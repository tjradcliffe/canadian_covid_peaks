nWaves = 10

lstDate = []
lstData = []
lstWaves = [[] for nI in range(nWaves)]
lstPeaks = [0 for nI in range(nWaves)]
with open("can_hosp_patients_fit.csv") as inFile:
    for strLine in inFile:
        if strLine.strip().startswith("#"): continue
        lstDate.append(strLine.strip().split()[1])
        lstLine = list(map(float, strLine.strip().split()[3:]))
        for nI in range(nWaves):
            lstWaves[nI].append(lstLine[nI])
            if lstWaves[nI][-1] > lstPeaks[nI]:
                lstPeaks[nI] = lstWaves[nI][-1]

for nI in range(nWaves):
    fThreshold = lstPeaks[nI]/10
    for nJ, fValue in enumerate(lstWaves[nI]):
        if fValue > fThreshold:
            print(nJ-1, lstDate[nJ-1], 0)
            print(nJ, lstDate[nJ], 100)
            print(nJ+1, lstDate[nJ+1], 0)
            break
