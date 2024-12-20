'''Pääikkuna tulosten hallinnointiin.
'''
import sys
import logging
from PyQt5 import QtCore,QtWidgets,QtGui
from mahjongtilasto import TUULET, VALIDIT_PISTESUMMAT
from mahjongtilasto.gui import STYLESHEET_NORMAL, STYLESHEET_ERROR, STYLESHEET_OK, STYLESHEET_NA

LOGGER = logging.getLogger(__name__)

class Paaikkuna(QtWidgets.QMainWindow):
    def __init__(self, pelaajalista=None):
        super().__init__()
        wid = QtWidgets.QWidget(self)
        self.setCentralWidget(wid)
        self.grid = QtWidgets.QGridLayout()
        wid.setLayout(self.grid)
        self.setLayout(self.grid)
        self.grid.setSpacing(5)
        self.setStyleSheet(STYLESHEET_NORMAL)
        # Tuloksen validius
        self.validit_pelaajat = False
        self.validit_pisteet = False
        self.validi_kirjaus = False
        # Tallennus
        self.nappi_tallenna = QtWidgets.QPushButton()
        self.nappi_tallenna.setFocusPolicy(QtCore.Qt.NoFocus)
        self.nappi_tallenna.setText("Tallenna")
        self.nappi_tallenna.setEnabled(False)
        self.nappi_tallenna.clicked.connect(self.tallenna_tulos)
        # Kenttien nimet
        self.text_ita = QtWidgets.QLabel(
            "東", alignment=QtCore.Qt.AlignLeft)
        self.text_etela = QtWidgets.QLabel(
            "南", alignment=QtCore.Qt.AlignLeft)
        self.text_lansi = QtWidgets.QLabel(
            "西", alignment=QtCore.Qt.AlignLeft)
        self.text_pohjoinen = QtWidgets.QLabel(
            "北", alignment=QtCore.Qt.AlignLeft)
        # Pelaajien nimet
        if not isinstance(pelaajalista, list):
            pelaajalista = []
        self.pelaajavaihtoehdot = sorted(pelaajalista, key=lambda t: t.lower()).copy()
        self.pelaajavaihtoehdot.extend("+")
        self.pelaajavalikot = (
            QtWidgets.QComboBox(),
            QtWidgets.QComboBox(),
            QtWidgets.QComboBox(),
            QtWidgets.QComboBox(),
            )
        self.pelaajat = [None for _ in TUULET] # Pelaajien nimet
        self.pelaaja_ita = self.pelaajavalikot[0]
        self.pelaaja_etela = self.pelaajavalikot[1]
        self.pelaaja_lansi = self.pelaajavalikot[2]
        self.pelaaja_pohjoinen = self.pelaajavalikot[3]
        # Signaalit pelaajanimiin
        self.pelaaja_ita.currentIndexChanged.connect(
            lambda t: self.vaihda_pelaajaa(self.pelaaja_ita))
        self.pelaaja_ita.addItems(["Pelaaja itä"])
        self.pelaaja_ita.addItems([nimi for nimi in self.pelaajavaihtoehdot])
        self.pelaaja_etela.currentIndexChanged.connect(
            lambda t: self.vaihda_pelaajaa(self.pelaaja_etela))
        self.pelaaja_etela.addItems(["Pelaaja etelä"])
        self.pelaaja_etela.addItems([nimi for nimi in self.pelaajavaihtoehdot])
        self.pelaaja_lansi.currentIndexChanged.connect(
            lambda t: self.vaihda_pelaajaa(self.pelaaja_lansi))
        self.pelaaja_lansi.addItems(["Pelaaja länsi"])
        self.pelaaja_lansi.addItems([nimi for nimi in self.pelaajavaihtoehdot])
        self.pelaaja_pohjoinen.currentIndexChanged.connect(
            lambda t: self.vaihda_pelaajaa(self.pelaaja_pohjoinen))
        self.pelaaja_pohjoinen.addItems(["Pelaaja pohjoinen"])
        self.pelaaja_pohjoinen.addItems([nimi for nimi in self.pelaajavaihtoehdot])
        # Pisteiden syöttökentät
        validaattori_piste = QtGui.QRegExpValidator(
            QtCore.QRegExp("[-+]?[0-9]*[\\.\\,]?[0-9]?"))
        self.pisteet_ita = QtWidgets.QLineEdit(alignment=QtCore.Qt.AlignRight)
        self.pisteet_ita.setValidator(validaattori_piste)
        self.pisteet_ita.setToolTip("12.3 / -12,3 / 12300")
        self.pisteet_ita.textChanged.connect(self.tarkista_pisteet)

        self.pisteet_etela = QtWidgets.QLineEdit(alignment=QtCore.Qt.AlignRight)
        self.pisteet_etela.setValidator(validaattori_piste)
        self.pisteet_etela.setToolTip("12.3 / -12,3 / 12300")
        self.pisteet_etela.textChanged.connect(self.tarkista_pisteet)

        self.pisteet_lansi = QtWidgets.QLineEdit(alignment=QtCore.Qt.AlignRight)
        self.pisteet_lansi.setValidator(validaattori_piste)
        self.pisteet_lansi.setToolTip("12.3 / -12,3 / 12300")
        self.pisteet_lansi.textChanged.connect(self.tarkista_pisteet)

        self.pisteet_pohjoinen = QtWidgets.QLineEdit(alignment=QtCore.Qt.AlignRight)
        self.pisteet_pohjoinen.setValidator(validaattori_piste)
        self.pisteet_pohjoinen.setToolTip("12.3 / -12,3 / 12300")
        self.pisteet_pohjoinen.textChanged.connect(self.tarkista_pisteet)
        self.pistelaatikot = (
            self.pisteet_ita,
            self.pisteet_etela,
            self.pisteet_lansi,
            self.pisteet_pohjoinen,
        )
        self.pistesumma = QtWidgets.QLabel(
            "sum", alignment=QtCore.Qt.AlignRight)
        # Asiat paikoilleen
        # Gridipaikka y, x, korkeus, leveys
        # Paikkojen nimet
        self.grid.addWidget(self.text_ita, 0,0,1,1)
        self.grid.addWidget(self.text_etela, 1,0,1,1)
        self.grid.addWidget(self.text_lansi, 2,0,1,1)
        self.grid.addWidget(self.text_pohjoinen, 3,0,1,1)
        # Pelaajien nimet
        self.grid.addWidget(self.pelaaja_ita, 0,1,1,10)
        self.grid.addWidget(self.pelaaja_etela, 1,1,1,10)
        self.grid.addWidget(self.pelaaja_lansi, 2,1,1,10)
        self.grid.addWidget(self.pelaaja_pohjoinen, 3,1,1,10)
        # Pisteiden syöttö
        self.grid.addWidget(self.pisteet_ita, 0,11,1,10)
        self.grid.addWidget(self.pisteet_etela, 1,11,1,10)
        self.grid.addWidget(self.pisteet_lansi, 2,11,1,10)
        self.grid.addWidget(self.pisteet_pohjoinen, 3,11,1,10)
        self.grid.addWidget(self.pistesumma, 4,11,1,10)
        self.grid.addWidget(self.nappi_tallenna, 5,11,1,10)
        self.show()

    def vaihda_pelaajaa(self, tuuli):
        '''Vaihda valitun tuulen pelaajaa.

        Parametrit
        ----------
        tuuli : QtWidgets.QComboBox
            Referenssi pudotusvalikkoon josta tähän tultiin.
        '''
        sel_index = tuuli.currentIndex()
        # Tuulen nimi ekana
        if sel_index == 0:
            LOGGER.debug("Valittiin istuinpaikan nimi")
        # Uuden pelaajan lisääminen listan pohjalla
        elif sel_index == len(self.pelaajavalikot):
            LOGGER.debug("Lisää uusi pelaaja")
            self.lisaa_pelaaja(tuuli)
        # Tarkista onko sama pelaaja valittu kahteen paikkaan
        pelaajavalinnat = [
            pelaaja.currentIndex()
            for pelaaja in self.pelaajavalikot
            ]
        self.validit_pelaajat = True
        for pelaajaindex, pelaaja in enumerate(self.pelaajavalikot):
            pelaaja_nimi = pelaaja.currentText()
            # (init-rutiini)
            if pelaaja_nimi == '':
                self.validit_pelaajat = False
                continue
            valinta = pelaajavalinnat[pelaajaindex]
            n_eri_paikalla = pelaajavalinnat.count(valinta)
            # Useammassa läsnä (eikä paikan nimi)
            if valinta and n_eri_paikalla > 1:
                LOGGER.warning("'%s' on %d eri paikalla", pelaaja_nimi, n_eri_paikalla)
                pelaaja.setStyleSheet(STYLESHEET_ERROR)
                self.validit_pelaajat = False
            # OK
            elif valinta:
                pelaaja.setStyleSheet(STYLESHEET_OK)
            # Pelaajapaikka
            else:
                pelaaja.setStyleSheet(STYLESHEET_NORMAL)
                self.validit_pelaajat = False
        self.tarkista_validius()

    def lisaa_pelaaja(self, tuuli=None):
        '''Lisää uusi pelaaja pelaajalistaan.
        Jos tapahtui pelaajavalinnan kautta, aseta valituksi.
        '''
        return # TODO

    def tarkista_pisteet(self):
        '''Tarkista täsmääkö syötetyt pisteet
        '''
        pistesumma = 0.0
        joku_laittamatta = False
        self.validit_pisteet = True
        for pelaaja, pistetulos in enumerate(self.pistelaatikot):
            pisteet = pistetulos.text().replace(',', '.')
            try:
                pisteet = float(pisteet)
            except ValueError:
                # Ei validi: vielä asetettu tai ei-numeerinen
                joku_laittamatta = True
                continue
            LOGGER.debug("%s pisteet %.1f", TUULET[pelaaja], pisteet)
            pistesumma += pisteet
            LOGGER.debug("Pistesumma %.1f", pisteet)
        if pistesumma in VALIDIT_PISTESUMMAT:
            self.pistesumma.setStyleSheet(STYLESHEET_OK)
            self.pistesumma.setText(f"{pistesumma:.1f}")
            LOGGER.debug("Pistesumma OK")
        else:
            self.pistesumma.setStyleSheet(STYLESHEET_ERROR)
            LOGGER.debug("Pistesumma ei täsmää")
            self.validit_pisteet = False
            # Etsi lähin mätsäävä
            lahin_erotus = None
            for validi in VALIDIT_PISTESUMMAT:
                erotus = pistesumma - validi
                if lahin_erotus is None:
                    lahin_erotus = erotus
                elif abs(erotus) < abs(lahin_erotus):
                    lahin_erotus = erotus
            self.pistesumma.setText(f"{pistesumma:.1f} ({lahin_erotus:+.1f})")
        # Joku vielä laittamatta: ei korosteta millään värillä
        if joku_laittamatta:
            self.pistesumma.setStyleSheet(STYLESHEET_NORMAL)
            self.validit_pisteet = False
        self.tarkista_validius()

    def tarkista_validius(self):
        '''Tarkista onko sekä pisteet että pelaajien nimet OK.

        Jos kaikki on OK, voidaan tallentaa tulos.
        '''
        self.nappi_tallenna.setEnabled(False)
        self.nappi_tallenna.setStyleSheet(STYLESHEET_NA)
        if self.validit_pisteet and self.validit_pelaajat:
            self.nappi_tallenna.setStyleSheet(STYLESHEET_NORMAL)
            self.nappi_tallenna.setEnabled(True)

    def tallenna_tulos(self):
        '''Tallenna tulos tiedostoon.
        '''
        ...

def main():
    '''Käynnistää Paaikkunan.
    '''
    app = QtWidgets.QApplication([])
    ikkuna = Paaikkuna(pelaajalista=["Kalle", "Mari", "Jouni", "Helmi", "jouko"])
    sys.exit(app.exec_())
