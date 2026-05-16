import os

nLocation = 0
nSite = 1
nCity = 2
nProv = 3
nCountry = 4
nEpiYear = 5
nEpiWeek = 6
nWeekStart = 7
nVirus = 8
nWeeklyAvg = 9
nMin = 10
nMax = 11
nPopulationCoverage = 12
nPruID = 13
strLastLocation = ""
lstLocations = []
with open("wastewater_aggregate.csv") as inFile:
    lstHeader = inFile.readline().strip().split(",")
    for nI, strWord in enumerate(lstHeader):
        print(nI, strWord)
    for strLine in inFile:
        lstLine = strLine.strip().split(",")
        if len(lstLine) < 14: continue
        if lstLine[nLocation] != strLastLocation:
            strLastLocation = lstLine[nLocation]
            lstLocations.append(strLastLocation)

for strLocation in lstLocations:
    print(strLocation)
    with open("wastewater_aggregate.csv") as inFile, open(strLocation.lower().replace(".","").replace(" ", "_").replace("'","")+".dat", "w") as outFile:
        lstHeader = inFile.readline().strip().split(",")
        for strLine in inFile:
            lstLine = strLine.strip().split(",")
            if len(lstLine) < 14: continue
            if lstLine[nLocation] != strLocation: continue
            if lstLine[nVirus] != "covN2": continue
            fError = float(lstLine[nMax])-float(lstLine[nMin])
#            print(lstLine[nWeekStart], lstLine[nWeeklyAvg])
            outFile.write(lstLine[nWeekStart]+" "+lstLine[nWeeklyAvg]+"\n")