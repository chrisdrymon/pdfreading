import pandas as pd
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
from tkinter import filedialog
from tkinter import *


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
        finddict = {'data-track-productlist-position': '0'}
        firstwindow = selsoup.find('div', attrs=finddict)
        costspot = firstwindow.find('span', class_='item-views-price-lead ng-binding')
        thecost = costspot.get('data-rate')

    return thecost


root = Tk()
root.filename = filedialog.askopenfilename(initialdir="/", title="Select file", filetypes=(("PDF", "*.pdf"),
                                                                                           ("All Files", "*.*")))
print(root.filename)
theDriver = webdriver.Firefox()
filename = root.filename
document = open(filename, 'rb')

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
per1kTotal = 0
countTotal = 0

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
                    try:
                        numPart = int(line[3:])
                        newNum = '{:04}'.format(numPart)
                        newBead = letterPart + newNum
                    except ValueError:
                        numPart = int(line[3:-1])
                        newNum = '{:04}'.format(numPart)
                        newBead = letterPart + newNum + line[-1:]
                    gotCost = getcost(newBead, theDriver)
                    try:
                        per1k = float(gotCost)
                    except ValueError:
                        per1k = gotCost
                        print('valueerror exception')
                    finally:
                        per1kList.append(per1k)
                    print(per1k)
                    per1kTotal = per1kTotal + float(per1k)
                if i == 2:
                    colorList.append(line)
                    print(line)
                if i == 3:
                    countList.append(int(line[6:]))
                    countTotal = countTotal + int(line[6:])
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
                                                                                                      'PerBag', 'Cost'])
theDriver.quit()
lastRow = [[' ', ' ', 'Totals', countTotal, per1kTotal, total]]
dfLast = pd.DataFrame(lastRow, columns=['Chart', 'Bead', 'Color', 'Count', 'PerBag', 'Cost'])
dfFinal = df.append(dfLast)
dfFinal['Per1K'] = dfFinal['Per1K'].map('${:,.2f}'.format)
dfFinal['Cost'] = dfFinal['Cost'].map('${:,.2f}'.format)
print(dfFinal)
print("Total:", total)
savePath = filename[:-4] + '.csv'
dfFinal.to_csv(savePath)
print('File output as:', savePath)
