from collections import defaultdict

import requests
from bs4 import BeautifulSoup, NavigableString
from enum import Enum


class Sections(str, Enum):
    portada = "PORTADA"
    poder_legislativo = "PODER LEGISLATIVO"
    poder_ejecutivo = "PODER EJECUTIVO"
    documentos_varios = "DOCUMENTOS VARIOS"  # "DOCUMENTOS\r\nVARIOS"
    tribunal_supremo_de_elecciones = "TRIBUNAL_SUPREMO_DE_ELECCIONES"
    contratacion_administrativa = "CONTRATACION ADMINISTRATIVA"
    reglamentos = "REGLAMENTOS"
    remates = "REMATES"
    instituciones_descentralizadas = "INSTITUCIONES DESCENTRALIZADAS"
    avisos = "AVISOS"
    notificaciones = "NOTIFICACIONES"


class Scraper:

    def __init__(self):
        self.parsed_text = defaultdict(lambda : "")
        self.get_text()

    def get_text(self) -> {str: str}:
        """ Gets the text and adds it into a dictionary dividing it between the sections"""
        url = 'https://www.imprentanacional.go.cr/gaceta/'
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        para = soup.find(id="ctl00_MainContentPlaceHolder_ContenidoGacetaDiv")
        name = ""

        # The text is divided between the titles - h1 and the main content - div
        # Only the last part has two consecutive div, and that last div is just the
        # bibliographic references, so it can be ignored
        for i, p in enumerate(para):
            if p.name == "h1":
                name = p.get_text()
            elif p.name == "div" and name and i < len(para)-1:
                self.parsed_text[name] = self._parse_text(name, p)
        return self.parsed_text

    def _parse_text(self, name: str, doc: "bs4.element.Tag"):
        """ Makes the dictionaries with the parsed information for each of the sections of the file """

        if name == Sections.documentos_varios:
            return self._parse_industrial_requests(doc)
        elif name == Sections.notificaciones:
            return self._parse_notifications(doc)
        else:
            return doc

    def _parse_industrial_requests(self, doc) -> {str: str}:
        """ Gets all the requests from the DOCUMENTSO VARIOS section """

        REGISTRO_PROPIEDAD_IND = "PROPIEDAD INDUSTRIAL"
        request_str = "Solicitud Nº "
        request_num_len = 12
        start = False
        add_next_para = False
        name = ""
        request_dict = defaultdict(lambda : "")
        for p in doc:
            if isinstance(p, NavigableString):
                continue
            if not start and REGISTRO_PROPIEDAD_IND in p.get_text():
                start = True
            elif start and request_str in p.get_text():
                name = p.get_text()[len(request_str):len(request_str)+request_num_len]
                request_dict[name] += p.get_text()[len(request_str)+request_num_len+1:]
                add_next_para = True
            elif add_next_para:
                request_dict[name] += p.get_text()
                add_next_para = False
        return request_dict

    def _parse_notifications(self, doc: str) -> {str: str}:
        """ Gets all the information from the different entities inside the AVISOS section """

        name = ""
        notification_dict = defaultdict(lambda : "")
        for p in doc:
            if p.name == "h3":
                name = p.get_text()
            elif name:
                notification_dict[name] += p.get_text()
        return notification_dict

    def get_info(self, section: Sections, words: [str]) -> [str]:
        """ Checks and returns the searched info exists if it exists """

        output = []
        for word in words:
            if self.parsed_text[section][word]:
                output.append(word + " " + self.parsed_text[section][word])
        return output


if __name__ == "__main__":
    s = Scraper()
    print(s.get_info(Sections.documentos_varios, ["2022-0004953", "2022-0001780"]))
    print(s.get_info(Sections.notificaciones, ["AVISOS"]))
