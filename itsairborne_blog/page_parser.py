from get_html import *

from bs4 import BeautifulSoup

import os
from random import random
from time import sleep

nMinDelaySeconds = 10
nHalfDelaySeconds = nMinDelaySeconds/2

pGetter = GetHTML()

pSoup = BeautifulSoup(open("ashrae_241_posts.html").read(), "html.parser")
strBaseURL = "https://itsairborne.com"
strBaseDir = "ashrae_241"

lstA = pSoup.find_all("a")
lstURLs = []
lstDirs = []
for pA in lstA:
    if "href" in pA.attrs:
        if "par" in pA.attrs["href"]:
            strHref=pA.attrs["href"].split("?")[0]
            if "ashrae" in strHref:
                lstURLs.append(strBaseURL+strHref)
                strDir = "_".join(strHref.split("-")[0:-1])
                lstDirs.append(strBaseDir+strDir)
    
lstURLs.append(strBaseURL+"/ashrae-241-always-applies-part-10-16548e85b17c")
lstDirs.append(strBaseDir+"/ashrae-241-always-applies-part-10")

for nI, strURL in enumerate(lstURLs):
    strDir = lstDirs[nI]
    print(strURL, strDir)
    if not os.path.exists(strDir):
        os.mkdir(strDir)
    open(os.path.join(strDir, "index.html"), "w")
    continue
    pSoup = pGetter.getHTML(strURL)
    with open(os.path.join(strDir, "index.html"), "w") as outFile:
        outFile.write(pSoup.prettify())
        
    sleep(nMinDelaySeconds+nHalfDelaySeconds*random()+nHalfDelaySeconds*random())
