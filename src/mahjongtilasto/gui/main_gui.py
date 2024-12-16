'''Pääikkuna tulosten hallinnointiin.
'''
import sys
import logging
from PyQt5 import QtCore,QtWidgets
from mahjongtilasto.gui import STYLESHEET_NORMAL, STYLESHEET_ERROR

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
        self.pelaaja_ita = QtWidgets.QComboBox()
        self.pelaaja_etela = QtWidgets.QComboBox()
        self.pelaaja_lansi = QtWidgets.QComboBox()
        self.pelaaja_pohjoinen = QtWidgets.QComboBox()
        # Signaalit pelaajanimiin
        self.pelaaja_ita.currentIndexChanged.connect(self.vaihda_itaa)
        self.pelaaja_ita.addItems(["Pelaaja itä"])
        self.pelaaja_ita.addItems([nimi for nimi in self.pelaajavaihtoehdot])
        self.pelaaja_etela.currentIndexChanged.connect(self.vaihda_etelaa)
        self.pelaaja_etela.addItems(["Pelaaja etelä"])
        self.pelaaja_etela.addItems([nimi for nimi in self.pelaajavaihtoehdot])
        self.pelaaja_lansi.currentIndexChanged.connect(self.vaihda_lantta)
        self.pelaaja_lansi.addItems(["Pelaaja länsi"])
        self.pelaaja_lansi.addItems([nimi for nimi in self.pelaajavaihtoehdot])
        self.pelaaja_pohjoinen.currentIndexChanged.connect(self.vaihda_pohjoista)
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

    # TODO: yksittäiseksi kutsuksi joka ottaa listan argumenttina
    # TODO: STYLESHEET_NORMAL pitää palauttaa pareittain
    def vaihda_itaa(self):
        sel_index = self.pelaaja_ita.currentIndex()
        if not sel_index:
            self.pelaaja_ita.setStyleSheet(STYLESHEET_NORMAL)
        elif sel_index == len(self.pelaajavaihtoehdot):
            self.lisaa_pelaaja(self.pelaaja_ita)
        else:
            muut_kentat = (
                self.pelaaja_etela,
                self.pelaaja_lansi,
                self.pelaaja_pohjoinen,
            )
            self.pelaaja_ita.setStyleSheet(STYLESHEET_NORMAL)
            for kentta in muut_kentat:
                if kentta.currentIndex() == sel_index:
                    kentta.setStyleSheet(STYLESHEET_ERROR)
                    self.pelaaja_ita.setStyleSheet(STYLESHEET_ERROR)

    def vaihda_etelaa(self):
        sel_index = self.pelaaja_etela.currentIndex()
        if not sel_index:
            self.pelaaja_etela.setStyleSheet(STYLESHEET_NORMAL)
        elif sel_index == len(self.pelaajavaihtoehdot):
            self.lisaa_pelaaja(self.pelaaja_etela)
        else:
            muut_kentat = (
                self.pelaaja_ita,
                self.pelaaja_lansi,
                self.pelaaja_pohjoinen,
            )
            self.pelaaja_etela.setStyleSheet(STYLESHEET_NORMAL)
            for kentta in muut_kentat:
                if kentta.currentIndex() == sel_index:
                    kentta.setStyleSheet(STYLESHEET_ERROR)
                    self.pelaaja_etela.setStyleSheet(STYLESHEET_ERROR)

    def vaihda_lantta(self):
        sel_index = self.pelaaja_lansi.currentIndex()
        if not sel_index:
            self.pelaaja_lansi.setStyleSheet(STYLESHEET_NORMAL)
        elif sel_index == len(self.pelaajavaihtoehdot):
            self.lisaa_pelaaja(self.pelaaja_lansi)
        else:
            muut_kentat = (
                self.pelaaja_ita,
                self.pelaaja_etela,
                self.pelaaja_pohjoinen,
            )
            self.pelaaja_lansi.setStyleSheet(STYLESHEET_NORMAL)
            for kentta in muut_kentat:
                if kentta.currentIndex() == sel_index:
                    kentta.setStyleSheet(STYLESHEET_ERROR)
                    self.pelaaja_lansi.setStyleSheet(STYLESHEET_ERROR)

    def vaihda_pohjoista(self):
        sel_index = self.pelaaja_pohjoinen.currentIndex()
        if not sel_index:
            self.pelaaja_pohjoinen.setStyleSheet(STYLESHEET_NORMAL)
        elif sel_index == len(self.pelaajavaihtoehdot):
            self.lisaa_pelaaja(self.pelaaja_pohjoinen)
        else:
            muut_kentat = (
                self.pelaaja_ita,
                self.pelaaja_etela,
                self.pelaaja_lansi,
            )
            self.pelaaja_pohjoinen.setStyleSheet(STYLESHEET_NORMAL)
            for kentta in muut_kentat:
                if kentta.currentIndex() == sel_index:
                    kentta.setStyleSheet(STYLESHEET_ERROR)
                    self.pelaaja_pohjoinen.setStyleSheet(STYLESHEET_ERROR)

    def lisaa_pelaaja(self, listaan=None):
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
