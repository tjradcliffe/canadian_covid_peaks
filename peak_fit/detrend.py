
from datetime import datetime, timedelta
import math
import sys

import simple_minimizer as sm
from peaks_objective import PeaksObjective

# cycle through these to see the effect of different numbers of peaks in the current wave
lstStarts = [110.08030684934468, 1299.3806525595394, 3103.7808699590696, 
349.11961175974403, 3321.99249104081, 4317.933868645453, 
464.6758503724063, 1722.5421323268513, 4220.304935125256, 
627.0459484963019, 2901.9094385497583, 2482.2819382847756, 
734.9950423643446, 816.0831262990868, 10297.499496377788, 
823.819061236064, 2162.2754682092577, 6882.834975997942, 
925.1001449952886, 1646.792982364046, 5300.682589529171, 
998.9066601818656, 1369.292524014261, 4875.776505594954, 
1063.3540440569411, 1917.7203151486415, 3389.7927566803623, 
1125, 1783, 2000, # 1783 is the average squared peak width to this point
1175, 1783, 2000]

lstStarts = [110.08030684934468, 1299.3806525595394, 3103.7808699590696, 
349.11961175974403, 3321.99249104081, 4317.933868645453, 
464.6758503724063, 1722.5421323268513, 4220.304935125256, 
627.0459484963019, 2901.9094385497583, 2482.2819382847756, 
734.9950423643446, 816.0831262990868, 10297.499496377788, 
823.819061236064, 2162.2754682092577, 6882.834975997942, 
925.1001449952886, 1646.792982364046, 5300.682589529171, 
998.9066601818656, 1369.292524014261, 4875.776505594954, 
1063.3540440569411, 1917.7203151486415, 3389.7927566803623, 
1100, 1783, 2000,
1150, 1783, 2000,
1200, 1783, 2000]

lstStarts = [110.08030684934468, 1299.3806525595394, 3103.7808699590696, 
349.11961175974403, 3321.99249104081, 4317.933868645453, 
464.6758503724063, 1722.5421323268513, 4220.304935125256, 
627.0459484963019, 2901.9094385497583, 2482.2819382847756, 
734.9950423643446, 816.0831262990868, 10297.499496377788, 
823.819061236064, 2162.2754682092577, 6882.834975997942, 
925.1001449952886, 1646.792982364046, 5300.682589529171, 
998.9066601818656, 1369.292524014261, 4875.776505594954, 
1063.3540440569411, 1917.7203151486415, 3389.7927566803623, 
1100, 1783, 2000,
1125, 1783, 2000,
1175, 1783, 2000,
1200, 1783, 2000]

lstStarts = [110.08030684934468, 1299.3806525595394, 3103.7808699590696, 
349.11961175974403, 3321.99249104081, 4317.933868645453, 
464.6758503724063, 1722.5421323268513, 4220.304935125256, 
627.0459484963019, 2901.9094385497583, 2482.2819382847756, 
734.9950423643446, 816.0831262990868, 10297.499496377788, 
823.819061236064, 2162.2754682092577, 6882.834975997942, 
925.1001449952886, 1646.792982364046, 5300.682589529171, 
998.9066601818656, 1369.292524014261, 4875.776505594954, 
1063.3540440569411, 1917.7203151486415, 3389.7927566803623, 
1100, 1783, 2000,
1125, 1783, 2000,
1150, 1783, 2000,
1175, 1783, 2000,
1200, 1783, 2000]

# best estimate values
lstStarts = [110.08030684934468, 1299.3806525595394, 3103.7808699590696, 
349.11961175974403, 3321.99249104081, 4317.933868645453, 
464.6758503724063, 1722.5421323268513, 4220.304935125256, 
627.0459484963019, 2901.9094385497583, 2482.2819382847756, 
734.9950423643446, 816.0831262990868, 10297.499496377788, 
823.819061236064, 2162.2754682092577, 6882.834975997942, 
925.1001449952886, 1646.792982364046, 5300.682589529171, 
998.9066601818656, 1369.292524014261, 4875.776505594954, 
1063.3540440569411, 1917.7203151486415, 3389.7927566803623, 
1152.1487891448894, 15695.61214457163, 3351.9063429893113]

nFinal = len(lstStarts)//3-8 # location of final unambiguous
print(nFinal)

print("Peaks:", len(lstStarts)//3)
lstScales = [1 for nI in range(len(lstStarts))]

nDim = len(lstStarts)
pMinimizer = sm.SimpleMinimizer(nDim)
pObjective = PeaksObjective("can_hosp_patients.csv", 1255) # 2023-07-01, 1225 for 2023-06-01
pMinimizer.setObjective(pObjective)
pMinimizer.setStarts(lstStarts)
pMinimizer.setScales(lstScales)

if False: # turn to True if you want to fix the widths of the sub-peaks
    for nI, fValue in enumerate(lstStarts):
        if fValue == 1783:
            pMinimizer.lstOrder[nI] = -1 # cut out minor peak widths as variable

nCount, pResult, nReason = pMinimizer.minimize()
lstVertex = pResult.getVertex()
print(nCount, nReason)
nCut = 953 # Sept 1 2022
print("Tail RMS:", pObjective(lstVertex, nCut))
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
        fFit = pObjective.fit(nDay, lstVertex)
        lstComponents = pObjective.components(nDay, lstVertex)
        lstPartialSums = [sum(lstComponents[0:nI]) for nI in range(1, len(lstComponents)+1)]
        lstOutput = [pDate.date(), pObjective.lstData[nDay]]
        lstOutput.extend(lstPartialSums)
        outFile.write(" ".join(map(str, lstOutput))+"\n")
