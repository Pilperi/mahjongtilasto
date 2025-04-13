'''Tulostilastojen katselutoiminnallisuudet.

Simppeli näin alkuun, paranee nyt.
'''
import os
import datetime
import logging
from PyQt5 import QtCore,QtWidgets
from mahjongtilasto import UMA_DEFAULT, AIKADELTAT
from mahjongtilasto import parseri
from mahjongtilasto.gui import STYLESHEET_NORMAL, STYLESHEET_TABLEHEADER
from mahjongtilasto.aikaikkuna import AikaIkkuna, KvartaaliIkkuna

LOGGER = logging.getLogger(__name__)


class TulosTilastot(QtWidgets.QDialog):
    '''Ikkuna kaikkien pelaajien tilastojen katseluun.
    '''
    def __init__(self, tulostiedosto, pelaajat=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle("Pelistatistiikat")
        self.setStyleSheet(STYLESHEET_NORMAL)
        # self.resize(800, 400)  # Pikkusen isompi alkuikkuna

        self.centralwidget = QtWidgets.QWidget(self)
        self.layout = QtWidgets.QVBoxLayout(self)

        # Valinta aikaikkunalle (mitkä pelit otetaan mukaan)
        self.aikaikkuna = AikaIkkuna()
        self.aikadelta = None # kaikki
        self.valinta_aika = QtWidgets.QComboBox(self)
        self.valinta_aika.addItems(["Kaikki", "6 kk", "3 kk", "1 kk"])
        self.valinta_aika.currentIndexChanged.connect(self.vaihda_aikaikkunaa)

        # Taulukko statistiikalle
        self.taulukko = QtWidgets.QTableWidget(self)
        self.taulukko.verticalHeader().setStyleSheet(STYLESHEET_TABLEHEADER)
        self.taulukko.horizontalHeader().setStyleSheet(STYLESHEET_TABLEHEADER)
        self.taulukko.setColumnCount(6)
        self.taulukko.setHorizontalHeaderLabels(["Nimi", "Pisteet", "Uma", "Yht.", "Pelejä", "Per peli"])
        self.taulukko.setSortingEnabled(True)
        self.taulukko.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
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
        self.aikaikkuna.alkupaiva = None if self.aikadelta is None else nykyhetki - self.aikadelta
        # Lue pelaajakohtaiset tulokset
        LOGGER.debug("Lue pelaajakohtaiset tulokset")
        kaikki_pelaajatulokset = parseri.pelaajadeltat(
            self.tulostiedosto,
            self.aikaikkuna
            )
        for pelaajan_nimi,pelaajan_tulokset in kaikki_pelaajatulokset.items():
            self.pelaajastats.append({
                "nimi": pelaajan_nimi,
                **pelaajan_tulokset
                })
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
            self.taulukko.setItem(row, 0, QtWidgets.QTableWidgetItem(pelaaja['nimi']))  # Nimi perus string

            # DisplayRole ja setData niin saa numerot oikein
            delta = QtWidgets.QTableWidgetItem()
            delta.setData(QtCore.Qt.DisplayRole, pelaaja['delta'])
            self.taulukko.setItem(row, 1, delta)

            uma_tot = QtWidgets.QTableWidgetItem()
            uma_tot.setData(QtCore.Qt.DisplayRole, pelaaja['uma_tot'])
            self.taulukko.setItem(row, 2, uma_tot)

            pistesumma = pelaaja['delta'] + pelaaja['uma_tot']
            delta_plus_uma = QtWidgets.QTableWidgetItem()
            delta_plus_uma.setData(QtCore.Qt.DisplayRole, pistesumma)
            self.taulukko.setItem(row, 3, delta_plus_uma)

            peleja = QtWidgets.QTableWidgetItem()
            peleja.setData(QtCore.Qt.DisplayRole, pelaaja['peleja'])
            self.taulukko.setItem(row, 4, peleja)

            keskimaarin = round(pistesumma/pelaaja['peleja']) if pelaaja['peleja'] else float('nan')
            per_peli = QtWidgets.QTableWidgetItem()
            per_peli.setData(QtCore.Qt.DisplayRole, keskimaarin)
            self.taulukko.setItem(row, 5, per_peli)

        # Säädä ikkunan koko sopivaksi
        taulukon_leveys = self.taulukko.verticalHeader().width() + 4
        for colind in range(self.taulukko.columnCount()):
            taulukon_leveys += self.taulukko.columnWidth(colind)
        LOGGER.debug("Taulukon leveys %s", taulukon_leveys)
        taulukon_korkeus = self.taulukko.horizontalHeader().height() + 24
        for rowind in range(self.taulukko.rowCount()):
            taulukon_korkeus += self.taulukko.rowHeight(rowind)
        LOGGER.debug("Taulukon korkeus %s", taulukon_korkeus)
        self.resize(min(800, taulukon_leveys), min(800, taulukon_korkeus))

    def vaihda_aikaikkunaa(self):
        '''Vaihda aikaikkunan pituutta.
        '''
        # Katso mikä aikaikkuna valittuna
        self.aikadelta = AIKADELTAT.get(self.valinta_aika.currentText())
        # Aikadelta muuttunut, täytä tulokset uudestaan (note: jalkeen_ajan)
        self.tayta_tulokset()
