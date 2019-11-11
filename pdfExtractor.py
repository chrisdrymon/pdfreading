import pandas as pd
import numpy as np
import PyPDF2 as p2
import re

# create pandas dataframe
df = pd.DataFrame(np.random.randn(6, 6), index=[1, 2, 3, 4, 5, 6], columns=['Chart', 'Bead', 'Color', 'Count', 'Per1k',
                                                                            'Cost'])
#print(df)


# creating a pdf file object
pdfFileObj = open('Eagle Vision.pdf', 'rb')

# creating a pdf reader object
pdfReader = p2.PdfFileReader(pdfFileObj)

# creating a page object
pageObj = pdfReader.getPage(1)
page2Obj = pdfReader.getPage(2)

# extracting text from page
plainText = pageObj.extractText() + page2Obj.extractText()
# splitText = plainText.split()

# this returns the beginning of the string
charts = [m.start() for m in re.finditer('Chart ', plainText)]
chartLetter = []
beadName = []
i = 0
for num in charts:
    newStart = num + 8
    if i < 26:
        chartLetter.append(plainText[newStart])
            if 
        beadName.append()
    else:
        chartLetter.append(plainText[newStart:newStart+2])
    i += 1

charts = [m.start() for m in re.finditer('DB', plainText)]

print(chartLetter)

# for letter in plainText:
#     if letter == 'D' and plainText[i+1] == 'B':
#         print('\n')
#     print(letter)
#     i += 1
#

# closing the pdf file object
pdfFileObj.close()
