import os

strFilename = "1310039401_databaseLoadingData.txt"

nYear = 0
nCause = 5
nNumber = 6
nCount = 13
setExclude = {"2020", "2021"}
mapAvg = {}
with open(strFilename) as inFile:
    strHeader = inFile.readline()
    for strLine in inFile:
        strLine = strLine.strip()
        lstLine = strLine.split('","')
        if len(lstLine) < nCount: continue
        strYear = lstLine[nYear].replace('"', '').strip()
        if strYear in setExclude:
            continue
        strCause = lstLine[nCause].split("[")[0].strip()
        strNumber = lstLine[nNumber]
        strCount = lstLine[nCount]
        if "Number of deaths" in strNumber:
            strFilename = strCause.replace("(","").replace(")", "").replace(",",""
                                                ).replace(" ", "_").replace("'","").lower()+".csv"
            if strFilename not in mapAvg:
                mapAvg[strFilename] = []
            if not len(strCount):
                strCount = "0"
            mapAvg[strFilename].append(int(strCount))
            with open(strFilename, "a") as outFile:
                outFile.write(strYear+" "+strCount+"\n")
        
for strFilename in mapAvg:
    fAvg = sum(mapAvg[strFilename])/len(mapAvg[strFilename])
    if fAvg < 100:
        os.unlink(strFilename)

"""
Cases where there is a likely effect:

accidents_unintentional_injuries.csv
anaemias.csv
cholelithiasis_and_other_disorders_of_gallbladder.csv
complications_of_medical_and_surgical_care.csv
diseases_of_heart.csv
essential_hypertension_and_hypertensive_renal_disease.csv
human_immunodeficiency_virus.csv
nutritional_deficiencies.csv
peptic_ulcer.csv
total_all_causes_of_death.csv
"""