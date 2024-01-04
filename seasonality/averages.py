from datetime import datetime
import math

nStartYear = 2020
nYears = 4
p2022Start = datetime(2022, 1, 1)
p2022End = datetime(2022, 12, 31)
nSum = 0
nCount = 0
lstMonthSums = [[0 for nI in range(12)] for nJ in range(nYears)]
lstMonthDays = [[0 for nI in range(12)] for nJ in range(nYears)]
with open("../seir_fit/can_hosp_patients.dat") as inFile:
    for strLine in inFile:
        if strLine.strip().startswith("#"): continue
        
        lstLine = strLine.strip().split()
        pDate = datetime.strptime(lstLine[0], "%Y-%m-%d")
        fCases = float(lstLine[1])
        if pDate >= p2022Start and pDate <= p2022End:
            nSum += fCases
            nCount += 1
        if ((pDate.month == 1 or pDate.month == 2) and pDate.year == 2022) or (pDate.month == 12 and pDate.year == 2021):
            continue
        lstMonthSums[pDate.year-nStartYear][pDate.month-1] += fCases
        lstMonthDays[pDate.year-nStartYear][pDate.month-1] += 1

print("2022 Average: ", nSum/nCount)
lstMonthAverage = [0 for nI in range(12)]
for nYear in range(nYears):
    for nMonth, fCount in enumerate(lstMonthSums[nYear]):
        if fCount > 0:
            lstMonthAverage[nMonth] += fCount/lstMonthDays[nYear][nMonth]

lstMonthAverage = [fValue/nYears for fValue in lstMonthAverage]
lstMonthSdev = [0 for nI in range(12)]
for nMonth, fMean in enumerate(lstMonthAverage):
    for nYear in range(nYears):
        if lstMonthDays[nYear][nMonth] > 0:
            lstMonthSdev[nMonth] += (fMean-lstMonthSums[nYear][nMonth]/lstMonthDays[nYear][nMonth])**2
lstMonthSdev = [math.sqrt(fValue)/(nYears-1) for fValue in lstMonthSdev]

for nI in range(12):
    print(nI+1, lstMonthAverage[nI], lstMonthSdev[nI])
