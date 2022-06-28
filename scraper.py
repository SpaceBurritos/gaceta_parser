import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass, field


@dataclass()
class Scraper:
    parse: dict = field(default_factory=dict)

    def get_text(self):
        """ Gets the text and adds it into a dictionary dividing it between the sub-sections"""
        url = 'https://www.imprentanacional.go.cr/gaceta/'
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        para = soup.find(id="ctl00_MainContentPlaceHolder_ContenidoGacetaDiv")

        for p in para:
            if p.name == "h1":
                name = p.get_text()
                print(name)
            elif p.name == "div":
                self.parse[name] = p.get_text()


if __name__ == "__main__":
    s = Scraper()
    s.get_text()
