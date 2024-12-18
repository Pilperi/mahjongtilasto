'''Pääikkuna tulosten hallinnointiin.
'''
import sys
import logging
from PyQt5 import QtCore,QtWidgets
from mahjongtilasto import TUULET
from mahjongtilasto.gui import STYLESHEET_NORMAL, STYLESHEET_ERROR, STYLESHEET_OK

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
        # Asiat paikoilleen
        self.grid.addWidget(self.text_ita, 0,0,1,1)
        self.grid.addWidget(self.text_etela, 1,0,1,1)
        self.grid.addWidget(self.text_lansi, 2,0,1,1)
        self.grid.addWidget(self.text_pohjoinen, 3,0,1,1)
        self.grid.addWidget(self.pelaaja_ita, 0,1,1,10)
        self.grid.addWidget(self.pelaaja_etela, 1,1,1,10)
        self.grid.addWidget(self.pelaaja_lansi, 2,1,1,10)
        self.grid.addWidget(self.pelaaja_pohjoinen, 3,1,1,10)
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
        for pelaajaindex, pelaaja in enumerate(self.pelaajavalikot):
            pelaaja_nimi = pelaaja.currentText()
            # (init-rutiini)
            if pelaaja_nimi == '':
                continue
            valinta = pelaajavalinnat[pelaajaindex]
            n_eri_paikalla = pelaajavalinnat.count(valinta)
            # Useammassa läsnä (eikä paikan nimi)
            if valinta and n_eri_paikalla > 1:
                LOGGER.warning("'%s' on %d eri paikalla", pelaaja_nimi, n_eri_paikalla)
                pelaaja.setStyleSheet(STYLESHEET_ERROR)
            # OK
            elif valinta:
                pelaaja.setStyleSheet(STYLESHEET_OK)
            # Pelaajapaikka
            else:
                pelaaja.setStyleSheet(STYLESHEET_NORMAL)

    def lisaa_pelaaja(self, tuuli=None):
        '''Lisää uusi pelaaja pelaajalistaan.
        Jos tapahtui pelaajavalinnan kautta, aseta valituksi.
        '''
        return # TODO

def main():
    '''Käynnistää Paaikkunan.
    '''
    app = QtWidgets.QApplication([])
    ikkuna = Paaikkuna(pelaajalista=["Kalle", "Mari", "Jouni", "Helmi", "jouko"])
    sys.exit(app.exec_())
