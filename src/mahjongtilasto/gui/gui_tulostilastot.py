'''Tulostilastojen katselutoiminnallisuudet.

Simppeli näin alkuun, paranee ajan kanssa.
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
        self.centralwidget = QtWidgets.QWidget(self)
        self.layout = QtWidgets.QVBoxLayout(self)
        # Valinta aikaikkunalle (mitkä pelit otetaan mukaan)
        self.aikadelta = None # kaikki
        self.valinta_aika = QtWidgets.QComboBox(self)
        self.valinta_aika.addItems(["Kaikki", "6 kk", "3 kk", "1 kk"])
        self.valinta_aika.currentIndexChanged.connect(self.vaihda_aikaikkunaa)
        # Tekstisarakkeet
        # TODO: nämä pitäisi tehdä jollain muulla kuin QLabel, koska
        # isolla pelaajamäärällä alkaa leikkautua. QTextEdit readonly olisi scrollattava,
        # mutta pitäisi saada kaikki sarakkeet scrollaamaan samaan tahtiin.
        self.layout_txt = QtWidgets.QHBoxLayout(self)
        # Nimimerkki
        self.sarake_pelaajanimet = QtWidgets.QLabel(self)
        self.sarake_pelaajanimet.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        # Raa'at pisteet
        self.sarake_pistesummat_raaka = QtWidgets.QLabel(self)
        self.sarake_pistesummat_raaka.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
        # Umasumma
        self.sarake_pistesummat_uma = QtWidgets.QLabel(self)
        self.sarake_pistesummat_uma.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
        # Kokonaispisteet
        self.sarake_pistesummat_tot = QtWidgets.QLabel(self)
        self.sarake_pistesummat_tot.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
        # Montako peliä takana
        self.sarake_pelimaara = QtWidgets.QLabel(self)
        self.sarake_pelimaara.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
        # Lisää ikkunaan
        # Sarakkeet tekstilayouttiin
        self.layout_txt.addWidget(self.sarake_pelaajanimet)
        self.layout_txt.addWidget(self.sarake_pistesummat_raaka)
        self.layout_txt.addWidget(self.sarake_pistesummat_uma)
        self.layout_txt.addWidget(self.sarake_pistesummat_tot)
        self.layout_txt.addWidget(self.sarake_pelimaara)
        # Aikaikkuna ikkunalayouttiin
        self.layout.addWidget(self.valinta_aika)
        # Tekstilayout ikkunalayouttiin
        self.layout.addLayout(self.layout_txt)
        # Uman arvo
        self.uma_suuruus = UMA_DEFAULT
        self.centralwidget.setLayout(self.layout)
        self.setModal(True)
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
        '''Täytä pelaajatilastot tekstiboksiin.
        '''
        self.tayta_pelaajastats()
        # Nimimerkit
        self.sarake_pelaajanimet.clear()
        st_pelaajanimet = "Nimi\n\n"
        # Raa'at pisteet
        self.sarake_pistesummat_raaka.clear()
        st_pistesummat_raaka = "Pisteet\n\n"
        # Umat
        self.sarake_pistesummat_uma.clear()
        st_pistesummat_uma = "Uma\n\n"
        # Kokonaispisteet
        self.sarake_pistesummat_tot.clear()
        st_pistesummat_tot = "Yht.\n\n"
        # Pelimäärä
        self.sarake_pelimaara.clear()
        st_pelimaara = "Pelejä\n\n"
        for pelaaja in self.pelaajastats:
            st_pelaajanimet += f"{pelaaja['nimi']:s}\n"
            st_pistesummat_raaka += f" {pelaaja['delta']:d}\n"
            st_pistesummat_uma += f" {pelaaja['uma_tot']:d}\n"
            st_pistesummat_tot += f" {pelaaja['delta']+pelaaja['uma_tot']:d}\n"
            st_pelimaara += f" {pelaaja['peleja']:d}\n"
        self.sarake_pelaajanimet.setText(st_pelaajanimet)
        self.sarake_pistesummat_raaka.setText(st_pistesummat_raaka)
        self.sarake_pistesummat_uma.setText(st_pistesummat_uma)
        self.sarake_pistesummat_tot.setText(st_pistesummat_tot)
        self.sarake_pelimaara.setText(st_pelimaara)

    def vaihda_aikaikkunaa(self):
        '''Vaihda aikaikkunan pituutta.
        '''
        # Katso mikä valittuna
        self.aikadelta = AIKADELTAT.get(self.valinta_aika.currentText())
        # Uudelleenpopuloi tulokset
        self.tayta_tulokset()
