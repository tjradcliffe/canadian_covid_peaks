from get_html import *

from random import random
from time import sleep

pGetter = GetHTML(GetHTML.knWebkit)

strBaseURL = "https://itsairborne.com"
strMainPage = "index.html"

strURL = "https://itsairborne.com/ashrae-241-control-of-infectious-aerosols-534a5ec33c38"
pSoup = pGetter.getHTML(strBaseURL)
with open("index.html", "w") as outFile:
    outFile.write(pSoup.prettify())
