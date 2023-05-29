from datetime import datetime, timedelta

pStart = datetime(2020, 1, 23) # start of OWID data, which I'm emulating

nOffset = 69 # all zeros before start

def extractHospitalized(strSource, strDest):
    with open(strDest, "w") as outFile:
        outFile.write("## 2020-01-23\n")
        for nI in range(nOffset):
            outFile.write(str(nI)+" "+"0\n")

        with open(strSource) as inFile:
            inFile.readline()
            for strLine in inFile:
                lstLine = strLine.strip().split(",")
                strDate = lstLine[0]
                strCount = lstLine[-1]

                if len(strCount):
                    pDate = datetime.strptime(strDate, "%Y-%m-%d")
                    nDays = (pDate-pStart).days
                    outFile.write(str(nDays)+" "+strCount+"\n")
    return pDate
    
if __name__ == "__main__":
    strSource = "canada-covid-data.csv"
    strDest = "can_hosp_patients.csv"
    extractHospitalized(strSource, strDest)
