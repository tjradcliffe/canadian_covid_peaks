
from datetime import date, datetime, timedelta
import math
import os
import sys

import simple_minimizer as sm
from peaks_objective import PeaksObjective

mapConvergenceReasons = {-1: "Exceeded iteration limit", 1: "Closest points indistinguishable", 
                                                 2: "Met fractional tolerance", 3:"Minimum scale achieved"}

def runFitterPre(strFilename):

    # set up minimizer
    lstStarts = [350, 30, 20**2]
    lstScales = [50, 5, 100]
    pStartDate = date(2021, 12, 1)
    pEndDate = date(2022, 3, 1)    
    nParameters = len(lstStarts)
    pMinimizer = sm.SimpleMinimizer(nParameters)
    pObjective = PeaksObjective(strFilename, pStartDate, pEndDate)
    pMinimizer.setObjective(pObjective)
    pMinimizer.setMinimumScale(1E-6) # the minimum is pretty well defined

    pMinimizer.setStarts(lstStarts)
    pMinimizer.setScales(lstScales)

    print("Fitting... this may take a minute or two...")
    nCount, pResult, nReason = pMinimizer.minimize()
    lstVertex = pResult.getVertex()

    print("Iterations:", nCount)
    print("Reason for termination:", mapConvergenceReasons[nReason])
    print("Residual RMS Error: ",pResult.getValue())

    print("Peak Position Size Width")
    for nI in range(0, len(lstVertex[1:]), 3):
        pDate = pStartDate+timedelta(days=lstVertex[nI+2])
        print(int(nI/3)+1, pDate, lstVertex[nI+1], lstVertex[nI], math.sqrt(lstVertex[nI+2]))

    print("")
    strOutputFile = strFilename.replace(".dat", "_omicron_fit.dat").replace("cities", "omicron")
    strParameterFile = strFilename.replace(".dat", "_omicron_parameters.dat").replace("cities", "omicron")
    with open(strParameterFile, "w") as outFile:
        outFile.write("# slope: "+str(lstVertex[0])+"\n")
        outFile.write("# Peak Date Day SDev Area\n")
        nCount = 1
        for nPeak in range(0, nParameters, 3):
            print(lstVertex[nPeak:nPeak+3])
            fSDev = math.sqrt(lstVertex[nPeak+2]/2)
            fArea = lstVertex[nPeak]*math.sqrt(2*math.pi)*fSDev
            pDate = pStartDate+timedelta(days=lstVertex[nPeak+1])
            outFile.write(" ".join(map(str, (nCount, pDate, lstVertex[nPeak+1], fSDev, fArea)))+"\n")
            nCount += 1

    print("Writing fit and components to: ", strOutputFile)
    with open(strOutputFile, "w") as outFile:
        outFile.write("# "+" ".join(map(str, lstVertex))+"\n")
        outFile.write("# "+pStartDate.isoformat()+"\n")
        for nDay in pObjective.lstDays:
            pDate = pStartDate+timedelta(days=nDay)
            fFit = pObjective.fit(nDay, lstVertex)
            fValue = pObjective.mapData[nDay]
            lstComponents = pObjective.components(nDay, lstVertex)
            outFile.write(" ".join(map(str, [pDate, fValue, fFit]+lstComponents))+"\n")

    return fArea
            
def runFitterPost(strFilename):

    # set up minimizer
    lstStarts = [50, 184, 90**2, 50, 458, 90**2, 50, 854, 90**2]
    lstScales = [10, 10, 1000, 10, 10, 1000, 10, 10, 1000]
    nParameters = len(lstStarts)
    pMinimizer = sm.SimpleMinimizer(nParameters)
    pObjective = PeaksObjective(strFilename)
    pMinimizer.setObjective(pObjective)
    pMinimizer.setMinimumScale(1E-6) # the minimum is pretty well defined

    pMinimizer.setStarts(lstStarts)
    pMinimizer.setScales(lstScales)

    print("Fitting... this may take a minute or two...")
    nCount, pResult, nReason = pMinimizer.minimize()
    lstVertex = pResult.getVertex()

    print("Iterations:", nCount)
    print("Reason for termination:", mapConvergenceReasons[nReason])
    print("Residual RMS Error: ",pResult.getValue())

    print("Peak Position Size Width")
    pStartDate = date(2023, 7, 1)
    for nI in range(0, len(lstVertex[1:]), 3):
        pDate = pStartDate+timedelta(days=lstVertex[nI+2])
        print(int(nI/3)+1, pDate, lstVertex[nI+1], lstVertex[nI], math.sqrt(lstVertex[nI+2]))

    print("")
    strOutputFile = strFilename.replace(".dat", "_fit.dat")
    strDiffFile = strFilename.replace(".dat", "_diff.dat")
    strParameterFile = strFilename.replace(".dat", "_parameters.dat")
    with open(strParameterFile, "w") as outFile:
        outFile.write("# slope: "+str(lstVertex[0])+"\n")
        outFile.write("# Peak Date Day SDev Area\n")
        nCount = 1
        for nPeak in range(0, nParameters, 3):
            print(lstVertex[nPeak:nPeak+3])
            fSDev = math.sqrt(lstVertex[nPeak+2]/2)
            fArea = lstVertex[nPeak]*math.sqrt(2*math.pi)*fSDev
            pDate = pStartDate+timedelta(days=lstVertex[nPeak+1])
            outFile.write(" ".join(map(str, (nCount, pDate, lstVertex[nPeak+1], fSDev, fArea)))+"\n")
            nCount += 1

    print("Writing fit and components to: ", strOutputFile)
    with open(strOutputFile, "w") as outFile:
        outFile.write("# "+" ".join(map(str, lstVertex))+"\n")
        outFile.write("# "+pStartDate.isoformat()+"\n")
        for nDay in pObjective.lstDays:
            pDate = pStartDate+timedelta(days=nDay)
            fFit = pObjective.fit(nDay, lstVertex)
            lstComponents = pObjective.components(nDay, lstVertex)
            outFile.write(" ".join(map(str, [pDate, fFit]+lstComponents))+"\n")
            
    print("Writing diff to: ", strDiffFile)    
    with open(strDiffFile, "w") as outFile:
        for nDay  in pObjective.lstDays:
            fValue = pObjective.mapData[nDay]
            pDate = pStartDate+timedelta(days=nDay)
            fFit = pObjective.fit(nDay, lstVertex)
            outFile.write(" ".join(map(str, (pDate, 2*(fValue-fFit)/(fValue+fFit))))+"\n")

if __name__ == "__main__":

    # from Brown et al Omicron BA.1/1.1 SARS-CoV-2 Infection among Vaccinated Canadian Adults
    # N Engl J Med 2022;386:2337-2339
    # DOI: 10.1056/NEJMc2202879
    # VOL. 386 NO. 24
    fInfectedFraction = 0.303

    mapCities = {
"halifax.dat": 228280,
"metro_vancouver.dat": 2642825,
"north_battleford.dat": 13836,
"prince_albert.dat": 37756,
"regina.dat": 226404,
"saskatoon.dat": 266141,
"toronto.dat": 2794356,
"winnipeg.dat": 749607}
    
    with open(os.path.join("omicron", "city_ratios.dat"), "w") as outFile:
        outFile.write("# City nInfected/WasteWaterPeakArea\n")
        for strCity in mapCities.keys():
            fArea = runFitterPre(os.path.join("cities", strCity))
            nInfected = mapCities[strCity]*fInfectedFraction
            fRatio = nInfected/fArea
            outFile.write(strCity.replace(".dat","")+" "+str(fRatio)+"\n")
        
        
    