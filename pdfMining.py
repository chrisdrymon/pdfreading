import pandas as pd
import requests
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from pdfminer.layout import LAParams
from pdfminer.converter import PDFPageAggregator
from pdfminer.pdfinterp import PDFPageInterpreter, PDFResourceManager
from pdfminer.pdfpage import PDFPage
from pdfminer.layout import LTTextBoxHorizontal


def getcost(beadtype, driver):
    thecost = 'Not found'

    driver.get('https://www.fusionbeads.com/search?keywords={}'.format(beadtype))
    try:
        wait = WebDriverWait(driver, 10)
        wait.until(EC.visibility_of_element_located((By.XPATH, "//div[@class='facets-item-cell-grid']")))

    except TimeoutError:
        pass

    finally:
        html = driver.execute_script("return document.documentElement.outerHTML")
        selsoup = BeautifulSoup(html, 'lxml')
        webdress = selsoup.findAll('meta')
        for meta in webdress:
            if meta.has_attr('content'):
                contents = meta.get('content')
                if contents[:8] == '/Size-11' or contents[:8] == '/size-11':
                    pricesite = 'https://www.fusionbeads.com/' + contents
                    pricesource = requests.get(pricesite).text
                    pricesoup = BeautifulSoup(pricesource, 'lxml')
                    for spanthing in pricesoup.findAll('span'):
                        if spanthing.has_attr('data-rate'):
                            thecost = spanthing.get('data-rate')

    return thecost


theDriver = webdriver.Firefox()

document = open('Eagle Vision.pdf', 'rb')

# Create resource manager
rsrcmgr = PDFResourceManager()

# Set parameters for analysis.
laparams = LAParams()

# Create a PDF page aggregator object.

device = PDFPageAggregator(rsrcmgr, laparams=laparams)

interpreter = PDFPageInterpreter(rsrcmgr, device)

pdfPages = PDFPage.get_pages(document, pagenos=[1, 2])
chartList = []
beadList = []
colorList = []
countList = []
per1kList = []
costList = []
for page in pdfPages:
    interpreter.process_page(page)

    # receive the LTPage object for the page.
    layout = device.get_result()
    for tBox in layout:
        if isinstance(tBox, LTTextBoxHorizontal):
            i = 0
            for line in tBox.get_text().splitlines():
                if i == 0:
                    chartList.append(line[8:])
                    print(line[8:])
                if i == 1:
                    beadList.append(line)
                    print(line)
                    letterPart = line[:2]
                    numPart = int(line[3:])
                    newNum = '{:04}'.format(numPart)
                    newBead = letterPart + newNum
                    gotCost = getcost(newBead, theDriver)
                    try:
                        per1k = float(gotCost)
                    except ValueError:
                        per1k = gotCost
                        print('valueerror exception')
                    finally:
                        per1kList.append(per1k)
                    print(per1k)
                if i == 2:
                    colorList.append(line)
                    print(line)
                if i == 3:
                    countList.append(int(line[6:]))
                    print(line[6:])
                i += 1
j = 0
total = 0
while j < len(chartList):
    try:
        costList.append(countList[j]*per1kList[j]/1000)
        total = total + costList[j]
        j += 1
    except TypeError:
        costList.append('NA')
        j += 1

df = pd.DataFrame(list(zip(chartList, beadList, colorList, countList, per1kList, costList)), columns=['Chart', 'Bead',
                                                                                                      'Color', 'Count',
                                                                                                      'Per1K', 'Cost'])
theDriver.quit()
lastRow = [[' ', ' ', ' ', ' ', 'Total', total]]
dfLast = pd.DataFrame(lastRow, columns=['Chart', 'Bead', 'Color', 'Count', 'Per1K', 'Cost'])
dfFinal = df.append(dfLast)
print(dfFinal)
print("Total:", total)
savePath = os.path.join(os.environ['HOME'], 'desktop', 'newpattern.csv')
dfFinal.to_csv(savePath)
print('File output as:', savePath)
