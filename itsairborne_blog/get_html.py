from bs4 import BeautifulSoup

from playwright.sync_api import sync_playwright
from playwright._impl._errors import TimeoutError

from pypdf import PdfReader

import requests

class GetHTMLTimeout(Exception):
    """Timeout in the HTML processing"""
    pass

class GetHTML:

    knFirefox = 0
    knWebkit = 1
    knChromium = 2
    
    def __init__(self, nBrowser = knFirefox):
        self.pPlaywright = sync_playwright().start()
        if nBrowser == GetHTML.knFirefox:
            self.pBrowser = self.pPlaywright.firefox.launch()
        elif nBrowser == GetHTML.knWebkit:
            self.pBrowser = self.pPlaywright.webkit.launch()
        elif nBrowser == GetHTML.knChromium:
            self.pBrowser = self.pPlaywright.chromium.launch()
        self.pPage = self.pBrowser.new_page()
        
    def __del__(self):
        self.pPlaywright.stop()
        
    def getHTML(self, strURL):
        try:
            self.pPage.goto(strURL)
        except TimeoutError:
            raise GetHTMLTimeout("Timeout processing: "+strURL)
            
        return BeautifulSoup(self.pPage.content(), 'html.parser')

def getBinary(strURL, strFilename):
    pResponse = requests.get(strURL)
    if pResponse.status_code == 200:
        with open(strFilename, 'wb') as outFile:
            outFile.write(pResponse.content)
    return pResponse.status_code

def getPDF(strURL, strFilename = None):

    if not strFilename:
        strFilename = "download.pdf"

    strText = ""
    if getBinary(strURL, strFilename) == 200:
        pReader = PdfReader(strFilename)
        for pPage in pReader.pages:
            strText += pPage.extract_text() + "\n"
    return strText

if __name__ == "__main__":
    pGetter = GetHTML()
    
    strURL = "http://www.bccdc.ca/health-info/diseases-conditions/measles"

    pSoup = pGetter.getHTML(strURL)
    with open("main_page.html", "w") as outFile:
        outFile.write(pSoup.prettify())
        

    strURL = "http://www.bccdc.ca/Health-Info-Site/Documents/Measles/Epi/Measles-update_2025-08-21.pdf"
    strText = getPDF(strURL, "test.pdf")
    
    print(strText)