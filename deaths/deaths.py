from datetime import datetime

import numpy as np
import pandas as pd

# data downloaded from: 
# https://health-infobase.canada.ca/src/data/covidLive/covid19-download.csv

pFrame = pd.read_csv("covid19-download.csv")

pFrame = pFrame.loc[pFrame['prname'] == 'Canada']

pDate = pd.to_datetime(pFrame.loc[:, 'date'])
pCount = pFrame.loc[:, 'numdeaths_last7']

# massively brain-dead data handling because I suck at pandas
pDate2020 = datetime(2020, 1, 1)
pDate2021 = datetime(2021, 2, 1)
pDate2022 = datetime(2022, 2, 1)
pDate2023 = datetime(2023, 2, 1)
pDate2024 = datetime(2024, 2, 1)

lst2020 = []
lst2021 = []
lst2022 = []
lst2023 = []
for nIndex, date in pDate.items():
    if date >= pDate2020 and date < pDate2021:
        lst2020.append(pCount[nIndex])        
    elif date >= pDate2021 and date < pDate2022:
        lst2021.append(pCount[nIndex])    
    elif date >= pDate2022 and date < pDate2023:
        lst2022.append(pCount[nIndex])
    elif date >= pDate2023 and date < pDate2024:
        lst2023.append(pCount[nIndex])

nDeaths2020 = sum(map(int, lst2020))
nDeaths2021 = sum(map(int, lst2021))
nDeaths2022 = sum(map(int, lst2022))
nDeaths2023 = sum(map(int, lst2023))
print("Deaths")
print(2020, nDeaths2020)
print(2021, nDeaths2021)
print(2022, nDeaths2022)
print(2023, nDeaths2023)

# copypasta
pFrame = pd.read_csv("../seir_fit/can_hosp_patients.dat", sep=" ")
pDate = pd.to_datetime(pFrame.iloc[:, 0])
pCount = pFrame.iloc[:, 1]

pDate2020 = datetime(2020, 1, 1)
pDate2021 = datetime(2021, 1, 1)
pDate2022 = datetime(2022, 1, 1)
pDate2023 = datetime(2023, 1, 1)
pDate2024 = datetime(2024, 1, 1)

lst2020 = []
lst2021 = []
lst2022 = []
lst2023 = []
for nIndex, date in pDate.items():
    if date >= pDate2020 and date < pDate2021:
        lst2020.append(pCount[nIndex])        
    elif date >= pDate2021 and date < pDate2022:
        lst2021.append(pCount[nIndex])    
    elif date >= pDate2022 and date < pDate2023:
        lst2022.append(pCount[nIndex])
    elif date >= pDate2023 and date < pDate2024:
        lst2023.append(pCount[nIndex])

nHosp2020 = sum(map(int, lst2020))
nHosp2021 = sum(map(int, lst2021))
nHosp2022 = sum(map(int, lst2022))
nHosp2023 = sum(map(int, lst2023))
print("---")
print("Hospitalizations")
print(2020, nHosp2020)
print(2021, nHosp2021)
print(2022, nHosp2022)
print(2023, nHosp2023)
print("---")
print("Deaths/Hospitalization")
print(2020, nDeaths2020/nHosp2020)
print(2021, nDeaths2021/nHosp2021)
print(2022, nDeaths2022/nHosp2022)
print(2023, nDeaths2023/nHosp2023)
print(2023, 1.5*nDeaths2023/nHosp2023) # corrected for preliminary
