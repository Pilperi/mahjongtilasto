'''Tulostilastojen katselutoiminnallisuudet.

Simppeli näin alkuun, paranee nyt.
'''
import os
import datetime
import logging
from PyQt5 import QtCore,QtWidgets
from mahjongtilasto import UMA_DEFAULT, AIKADELTAT
from mahjongtilasto import parseri
from mahjongtilasto.gui import STYLESHEET_NORMAL

LOGGER = logging.getLogger(__name__)


class TulosTilastot(QtWidgets.QDialog):
    '''Ikkuna kaikkien pelaajien tilastojen katseluun.
    '''
    def __init__(self, tulostiedosto, pelaajat=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle("Pelistatistiikat")
        self.setStyleSheet(STYLESHEET_NORMAL)
        self.resize(800, 400)  # Pikkusen isompi alkuikkuna

        self.centralwidget = QtWidgets.QWidget(self)
        self.layout = QtWidgets.QVBoxLayout(self)

        # Valinta aikaikkunalle (mitkä pelit otetaan mukaan)
        self.aikadelta = None # kaikki
        self.valinta_aika = QtWidgets.QComboBox(self)
        self.valinta_aika.addItems(["Kaikki", "6 kk", "3 kk", "1 kk"])
        self.valinta_aika.currentIndexChanged.connect(self.vaihda_aikaikkunaa)

        # Taulukko statistiikalle
        self.taulukko = QtWidgets.QTableWidget(self)
        self.taulukko.setColumnCount(5)
        self.taulukko.setHorizontalHeaderLabels(["Nimi", "Pisteet", "Uma", "Yht.", "Pelejä"])

        # Widgetit layouttiin
        self.layout.addWidget(self.valinta_aika)
        self.layout.addWidget(self.taulukko)

        # Uman arvo
        self.uma_suuruus = UMA_DEFAULT

        # Lue tulokset tiedostosta ja täytä tekstikenttään
        assert os.path.isfile(tulostiedosto), f"Tulostiedosto '{tulostiedosto}' ei validi!"
        self.tulostiedosto = tulostiedosto
        self.pelaajat = pelaajat
        self.pelaajastats = []
        self.tayta_tulokset()
        self.show()

    def tayta_pelaajastats(self):
        '''Lue pelaajien tilastot tulostiedostosta.
        '''
        self.pelaajastats = [] # Nollaa
        if not isinstance(self.pelaajat, (list, tuple)):
            LOGGER.debug("Lue pelaajalista tulostiedostosta")
            kaikki_tulokset = parseri.parse_txt_dictiksi(self.tulostiedosto)
            self.pelaajat = []
            for pelin_paivays, pelitulos in kaikki_tulokset.items():
                LOGGER.debug("Peli %s", pelin_paivays)
                for tuulen_tulos in pelitulos:
                    if tuulen_tulos[0] not in self.pelaajat:
                        LOGGER.debug("Lisää pelaaja '%s'", tuulen_tulos[0])
                        self.pelaajat.append(tuulen_tulos[0])
        # Jos aikarajaus, katsotaan mikä aika nyt on
        nykyhetki = datetime.date.today()
        jalkeen_ajan = None if self.aikadelta is None else nykyhetki - self.aikadelta
        # Lue pelaajakohtaiset tulokset
        LOGGER.debug("Lue pelaajakohtaiset tulokset")
        for pelaajan_nimi in self.pelaajat:
            self.pelaajastats.append({
                "nimi": pelaajan_nimi,
                **parseri.pelaajadelta(
                    self.tulostiedosto,
                    pelaajan_nimi,
                    jalkeen_ajan=jalkeen_ajan,
                    )
                })
            LOGGER.debug("'%s' luettu, %d peliä",
                pelaajan_nimi, self.pelaajastats[-1]["peleja"])
            # Lisää umat
            umasumma = 0
            for pelisijoitus in self.pelaajastats[-1]["sijoitukset"]:
                # Hanchanin uman arvo on keskiarvo jaetuista sijoituksista,
                # jaetut sijat merkattu esim. [1, 2] ja ei-jaetut [1]
                # ja eka sija on 1
                uma_arvo = int(sum(
                    self.uma_suuruus[sijoitus-1]
                    for sijoitus in pelisijoitus)/len(pelisijoitus))
                LOGGER.debug("Sijoitukset %s, umaa %d", pelisijoitus, uma_arvo)
                umasumma += uma_arvo
            LOGGER.debug("Pelaajan '%s' umasumma %d", pelaajan_nimi, umasumma)
            self.pelaajastats[-1]["uma_tot"] = umasumma
        # Sorttaa kokonaisdeltan mukaan, uma mukaanlukien
        self.pelaajastats = sorted(
            self.pelaajastats,
            key=lambda t: t["delta"] + t["uma_tot"],
            reverse=True,)
        LOGGER.debug("Pelaajatilastot luettu tiedostosta")

    def tayta_tulokset(self):
        '''Täytä pelaajatilastot taulukkoon.
        '''
        self.tayta_pelaajastats()
        self.taulukko.setRowCount(len(self.pelaajastats))

        for row, pelaaja in enumerate(self.pelaajastats):
            self.taulukko.setItem(row, 0, QtWidgets.QTableWidgetItem(pelaaja['nimi']))
            self.taulukko.setItem(row, 1, QtWidgets.QTableWidgetItem(str(pelaaja['delta'])))
            self.taulukko.setItem(row, 2, QtWidgets.QTableWidgetItem(str(pelaaja['uma_tot'])))
            self.taulukko.setItem(row, 3, QtWidgets.QTableWidgetItem(str(pelaaja['delta'] + pelaaja['uma_tot'])))
            self.taulukko.setItem(row, 4, QtWidgets.QTableWidgetItem(str(pelaaja['peleja'])))

    def vaihda_aikaikkunaa(self):
        '''Vaihda aikaikkunan pituutta.
        '''
        # Katso mikä aikaikkuna valittuna
        self.aikadelta = AIKADELTAT.get(self.valinta_aika.currentText())
        # Aikadelta muuttunut, täytä tulokset uudestaan (note: jalkeen_ajan)
        self.tayta_tulokset()
