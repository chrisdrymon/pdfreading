from pdfminer.layout import LAParams
from pdfminer.converter import PDFPageAggregator
from pdfminer.pdfinterp import PDFPageInterpreter, PDFResourceManager
from pdfminer.pdfpage import PDFPage
from pdfminer.layout import LTTextBoxHorizontal
import pandas

document = open('ETS Program.pdf', 'rb')

# Create resource manager
rsrcmgr = PDFResourceManager()

# Set parameters for analysis.
laparams = LAParams()

# Create a PDF page aggregator object.

device = PDFPageAggregator(rsrcmgr, laparams=laparams)

interpreter = PDFPageInterpreter(rsrcmgr, device)

pdfPages = PDFPage.get_pages(document)

schoolList = []

for page in pdfPages:
    interpreter.process_page(page)

    # receive the LTPage object for the page.
    layout = device.get_result()
    for tBox in layout:
        if isinstance(tBox, LTTextBoxHorizontal):
            theText = tBox.get_text()
            if '(' in theText and ')' in theText:
                beginIndex = theText.index('(') + 1
                endIndex = theText.index(')')
                school = theText[beginIndex:endIndex]
                if school[:3] == 'cid':
                    pass
                else:
                    if school in schoolList:
                        pass
                    else:
                        schoolList.append(school)
                    print(school)
df = pandas.DataFrame(schoolList)
df.to_csv('schoollist.csv')
