from datetime import date
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
    strFirstDate = ""
    strLastDate = ""
    bHaveData = False
    strFilename = strLocation.lower().replace(" - ", "_").replace(".","").replace(" ", "_").replace("'","")+".dat"
    with open("wastewater_aggregate.csv") as inFile, open(os.path.join("cities", strFilename), "w") as outFile:
        lstHeader = inFile.readline().strip().split(",")
        for strLine in inFile:
            lstLine = strLine.strip().split(",")
            if len(lstLine) < 14: continue
            if lstLine[nLocation] != strLocation: 
                if bHaveData:
                    break
                else:
                    continue
            if lstLine[nVirus] != "covN2": continue
            bHaveData = True
            fError = float(lstLine[nMax])-float(lstLine[nMin])
#            print(lstLine[nWeekStart], lstLine[nWeeklyAvg])
            if strFirstDate == "":
                strFirstDate = lstLine[nWeekStart]
            strLastDate = lstLine[nWeekStart]
            outFile.write(lstLine[nWeekStart]+" "+lstLine[nWeeklyAvg]+"\n")
            
    pFirstDate = date.fromisoformat(strFirstDate)
    pLastDate = date.fromisoformat(strLastDate)
    if pFirstDate > date(2023, 1, 1) or pLastDate < date(2026, 5, 1):
        print("UNLINK:", strFilename, pFirstDate, pLastDate)
        os.unlink(os.path.join("cities", strFilename))
        