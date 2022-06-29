import requests
from bs4 import BeautifulSoup, NavigableString
from dataclasses import dataclass, field
from enum import Enum, auto


class Sections(str, Enum):
    portada = "PORTADA"
    poder_legislativo = "PODER LEGISLATIVO"
    poder_ejecutivo = "PODER EJECUTIVO"
    documentos_varios = "DOCUMENTOS\r\nVARIOS"
    tribunal_supremo_de_elecciones = "TRIBUNAL_SUPREMO_DE_ELECCIONES"
    contratacion_administrativa = "CONTRATACION ADMINISTRATIVA"
    reglamentos = "REGLAMENTOS"
    remates = "REMATES"
    instituciones_descentralizadas = "INSTITUCIONES DESCENTRALIZADAS"
    avisos = "AVISOS"
    notificaciones = "NOTIFICACIONES"


class Scraper:

    def __init__(self):
        self.parsed_text = dict()
        self.get_text()

    def get_text(self) -> {str: str}:
        """ Gets the text and adds it into a dictionary dividing it between the sub-sections"""
        url = 'https://www.imprentanacional.go.cr/gaceta/'
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        para = soup.find(id="ctl00_MainContentPlaceHolder_ContenidoGacetaDiv")
        name = ""

        for p in para:
            if p.name == "h1":
                name = p.get_text()
            elif p.name == "div" and name:
                self.parsed_text[name] = self._parse_text(name, p)
        return self.parsed_text

    def _parse_text(self, name: str, doc):
        if name == Sections.documentos_varios:
            return self._parse_industrial_requests(doc)
        else:
            return doc

    def _parse_industrial_requests(self, doc) -> [str]:
        """ Gets all the requests from the DOCUMENTSO VARIOS file """
        industrial_requests = []
        REGISTRO_PROPIEDAD_IND = "PROPIEDAD INDUSTRIAL"
        start = False
        add_next_para = False
        for p in doc:
            if isinstance(p, NavigableString):
                continue
            if not start and REGISTRO_PROPIEDAD_IND in p.get_text():
                start = True
            elif start and "Solicitud" in p.get_text():
                industrial_requests.append(p.get_text())
                add_next_para = True
            elif add_next_para:
                industrial_requests[-1] += p.get_text()
                add_next_para = False
        return industrial_requests

    def get_industrial_requests(self, nums: [str]) -> [str]:
        output = []
        print(nums)
        for num in nums:
            for r in self.parsed_text[Sections.documentos_varios]:
                if num in r:
                    output.append(r)
                    break
        return output


if __name__ == "__main__":
    s = Scraper()
    print(len(s.get_industrial_requests(["2022-0003586", "2022-0002820"])))
