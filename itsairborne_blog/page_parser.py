
from bs4 import BeautifulSoup

pSoup = BeautifulSoup(open("ashrae_241_posts.html").read(), "html.parser")

lstA = pSoup.find_all("a")
for pA in lstA:
    if "href" in pA.attrs:
        if "par" in pA.attrs["href"]:
            print(pA.attrs["href"])
    