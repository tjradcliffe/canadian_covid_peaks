from datetime import date

lstCities = ["halifax", "halifax_halifax", "north_battleford",
"regina", "saskatoon", "toronto", "winnipeg"]

# these are urban populations, not metro area populations
lstPopulations = [228280, 156141, 13836, 226404, 266141, 2794356,  749607]  

for nI, strCity in enumerate(lstCities):
    print(strCity, lstPopulations[nI])
    
# start at 2023-07-01 and consider three peaks at 2024-01-01, 2024-10-01, and
# 2025-11-01 (starting points) with standard deviations of 90 days.

# use the usual "fit to a gaussian and extract the parameters" approach

pPeak1Date = date.fromisoformat("2024-01-01")
pPeak2Date = date.fromisoformat("2024-10-01")
pPeak3Date = date.fromisoformat("2025-11-01")

pStartDate = date.fromisoformat("2023-07-01")

nPeak1Days = (pPeak1Date-pStartDate).days
print(nPeak1Days)
nPeak2Days = (pPeak2Date-pStartDate).days
print(nPeak2Days)
nPeak3Days = (pPeak3Date-pStartDate).days
print(nPeak3Days)
