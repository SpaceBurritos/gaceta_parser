import requests
from bs4 import BeautifulSoup
import PyPDF2

class Scraper:

    def __init__(self):
        self.file = None

    def downloadFile(self):
        url = 'https://www.imprentanacional.go.cr/gaceta/'
        base_url = "https://www.imprentanacional.go.cr"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        file_url = base_url + soup.findAll(attrs={'class': 'LinkNavBar'})[2]["href"]
        name = file_url.split("/")[-1]
        with requests.get(file_url, stream=True) as r:
            r.raise_for_status()
            with open("pdfs/"+name, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):

                    f.write(chunk)
                self.file = f
        return name

    def getPDF(self, filename):
        file = open("pdfs/"+filename, 'rb')
        return PyPDF2.PdfFileReader(file)

if __name__ == "__main__":
    s = Scraper()
    name2 = s.downloadFile()
    pdf = s.getPDF(name2)
    page_one = pdf.getPage(1)
    print(page_one.extractText())
