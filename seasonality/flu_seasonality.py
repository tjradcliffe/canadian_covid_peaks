lstSum = [0 for nI in range(52)]

with open("adult_seasonality_2018_2019.dat") as inFile:
    inFile.readline() # discard header
    for strLine in inFile:
        lstLine = list(map(int, strLine.strip().split()))
        nWeek = lstLine.pop(0)
        lstSum[nWeek-1] += sum(lstLine)
        
with open("pediatric_seasonality_2018_2019.dat") as inFile:
    inFile.readline() # discard header
    for strLine in inFile:
        lstLine = list(map(int, strLine.strip().split()))
        nWeek = lstLine.pop(0)
        lstSum[nWeek-1] += sum(lstLine)

lstMonthSum = [0 for nI in range(12)]
for nI, nCount in enumerate(lstSum):
    lstMonthSum[int(nI/4.33)] += nCount

for nI, nCount in enumerate(lstMonthSum):
    print(nI+1, nCount)
