'''Pääikkuna tulosten hallinnointiin.
'''
import sys
import os
import time
import logging
from PyQt5 import QtCore,QtWidgets,QtGui
from mahjongtilasto import KOTIKANSIO, TUULET, VALIDIT_PISTESUMMAT
from mahjongtilasto import parseri
from mahjongtilasto import PELAAJAT, PELAAJATIEDOSTO, OLETUS_TULOSTIEDOSTO
from mahjongtilasto.gui import STYLESHEET_NORMAL, STYLESHEET_ERROR, STYLESHEET_OK, STYLESHEET_NA, STYLESHEET_TOOLTIP
from mahjongtilasto.gui import gui_tulostilastot

LOGGER = logging.getLogger(__name__)


class UusiPelaaja(QtWidgets.QDialog):
    '''Ikkuna uuden pelaajan nickin syöttämiseen, rajoitetulla merkistöllä.
    '''
    nick_validator = QtGui.QRegExpValidator(
        QtCore.QRegExp("([A-Öa-ö0-9!,.\-;:_*/]*[ ]?[A-Öa-ö0-9!,.\-;:_*/]*)*"))
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle("Lisää uusi pelaaja")
        self.setStyleSheet(STYLESHEET_NORMAL)
        self.centralwidget = QtWidgets.QWidget(self)
        self.layout = QtWidgets.QVBoxLayout()
        self.centralwidget.setLayout(self.layout)
        self.layout.addWidget(QtWidgets.QLabel("Pelaajan nimi"))
        self.nimikentta = QtWidgets.QLineEdit(alignment=QtCore.Qt.AlignRight)
        self.nimikentta.setMaxLength(32)
        self.layout.addWidget(self.nimikentta)
        # Rajoitetaan nick
        self.nimikentta.setValidator(UusiPelaaja.nick_validator)
        # Ok Cancel
        self.napit = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        )
        self.napit.accepted.connect(self.accept)
        self.napit.rejected.connect(self.reject)
        self.layout.addWidget(self.napit)
        self.setLayout(self.layout)
        self.setModal(True)
        self.show()


class Paaikkuna(QtWidgets.QMainWindow):
    def __init__(self, pelaajalista=None):
        super().__init__()
        self.tulostiedosto = None
        self.centralwidget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.centralwidget)
        self.setWindowTitle("Pisteidensyöttäjä")
        self.grid = QtWidgets.QGridLayout()
        self.centralwidget.setLayout(self.grid)
        self.grid.setSpacing(5)
        self.setStyleSheet(STYLESHEET_NORMAL)
        # Tuloksen validius
        self.validit_pelaajat = False
        self.validit_pisteet = False
        # Tallennus
        self.nappi_tallenna = QtWidgets.QPushButton()
        # self.nappi_tallenna.setFocusPolicy(QtCore.Qt.NoFocus)
        self.nappi_tallenna.setText("Tallenna")
        self.nappi_tallenna.clicked.connect(self.tallenna_tulos)
        self.nappi_tallenna.setEnabled(False)
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
        self.pelaajavaihtoehdot = pelaajalista
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
        self.tayta_pelaajanimet()
        # Signaalit pelaajanimiin
        self.pelaaja_ita.currentIndexChanged.connect(
            lambda t: self.vaihda_pelaajaa(self.pelaaja_ita))
        self.pelaaja_etela.currentIndexChanged.connect(
            lambda t: self.vaihda_pelaajaa(self.pelaaja_etela))
        self.pelaaja_lansi.currentIndexChanged.connect(
            lambda t: self.vaihda_pelaajaa(self.pelaaja_lansi))
        self.pelaaja_pohjoinen.currentIndexChanged.connect(
            lambda t: self.vaihda_pelaajaa(self.pelaaja_pohjoinen))
        # Pisteiden syöttökentät
        validaattori_piste = QtGui.QRegExpValidator(
            QtCore.QRegExp("[-+]?[0-9]*[\\.\\,]?[0-9]?"))
        self.pisteet_ita = QtWidgets.QLineEdit(alignment=QtCore.Qt.AlignRight)
        self.pisteet_ita.setValidator(validaattori_piste)
        self.pisteet_ita.setToolTip("12.3 / -12,3 / 12300")
        self.pisteet_ita.textChanged.connect(self.tarkista_pisteet)
        self.pisteet_ita.setStyleSheet(STYLESHEET_TOOLTIP)

        self.pisteet_etela = QtWidgets.QLineEdit(alignment=QtCore.Qt.AlignRight)
        self.pisteet_etela.setValidator(validaattori_piste)
        self.pisteet_etela.setToolTip("12.3 / -12,3 / 12300")
        self.pisteet_etela.textChanged.connect(self.tarkista_pisteet)
        self.pisteet_etela.setStyleSheet(STYLESHEET_TOOLTIP)

        self.pisteet_lansi = QtWidgets.QLineEdit(alignment=QtCore.Qt.AlignRight)
        self.pisteet_lansi.setValidator(validaattori_piste)
        self.pisteet_lansi.setToolTip("12.3 / -12,3 / 12300")
        self.pisteet_lansi.textChanged.connect(self.tarkista_pisteet)
        self.pisteet_lansi.setStyleSheet(STYLESHEET_TOOLTIP)

        self.pisteet_pohjoinen = QtWidgets.QLineEdit(alignment=QtCore.Qt.AlignRight)
        self.pisteet_pohjoinen.setValidator(validaattori_piste)
        self.pisteet_pohjoinen.setToolTip("12.3 / -12,3 / 12300")
        self.pisteet_pohjoinen.textChanged.connect(self.tarkista_pisteet)
        self.pisteet_pohjoinen.setStyleSheet(STYLESHEET_TOOLTIP)
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
        # Tab-järjestys kohdilleen: pudotusvalikko -> pistelaari
        self.centralwidget.setTabOrder(self.pelaaja_ita, self.pisteet_ita)
        self.centralwidget.setTabOrder(self.pisteet_ita, self.pelaaja_etela)
        self.centralwidget.setTabOrder(self.pelaaja_etela, self.pisteet_etela)
        self.centralwidget.setTabOrder(self.pisteet_etela, self.pelaaja_lansi)
        self.centralwidget.setTabOrder(self.pelaaja_lansi, self.pisteet_lansi)
        self.centralwidget.setTabOrder(self.pisteet_lansi, self.pelaaja_pohjoinen)
        self.centralwidget.setTabOrder(self.pelaaja_pohjoinen, self.pisteet_pohjoinen)
        self.centralwidget.setTabOrder(self.pisteet_pohjoinen, self.nappi_tallenna)
        # Menubar
        self._lisaa_menubar()
        self.show()

    def _lisaa_menubar(self):
        '''Lisää ikkunaan menubar'''
        menu = QtWidgets.QMenuBar(self)
        stats_menu = QtWidgets.QMenu("&Stats", self)
        self.action_nayta_pisteet = QtWidgets.QAction("Pistesumma", self)
        self.action_nayta_pisteet.triggered.connect(self.nayta_pistesummat)
        stats_menu.addAction(self.action_nayta_pisteet)
        menu.addMenu(stats_menu)
        self.setMenuBar(menu)

    def nayta_pistesummat(self):
        '''Näytä pistesummaikkuna.'''
        LOGGER.debug("Näytä pistesummat pelaajille")
        # Tarkistetaan että tulostiedosto on validi
        if self.tulostiedosto is None:
            if not self.avaa_tulostiedosto():
                return
        # Näytetään tulokset
        tulosikkuna = gui_tulostilastot.TulosTilastot(self.tulostiedosto)
        tulosikkuna.exec()

    def keyPressEvent(self, event):
        '''Rekisteröi näppäimistöpainallukset.

        Lähinnä: enter menee Tallenna-nappiin
        '''
        if event.key() in (QtCore.Qt.Key_Enter, QtCore.Qt.Key_Return):
            self.tarkista_validius()
            if self.nappi_tallenna.isEnabled():
                self.tallenna_tulos()

    def tayta_pelaajanimet(self):
        '''Täytä pelaajanimet pudotusvalikoihin, aakkosjärjestyksessä.
        '''
        # Blokkaa signaalit operaatioiden ajaksi
        self.pelaaja_ita.blockSignals(True)
        self.pelaaja_etela.blockSignals(True)
        self.pelaaja_lansi.blockSignals(True)
        self.pelaaja_pohjoinen.blockSignals(True)
        # Tyhjennä vanhat arvot
        self.pelaaja_ita.clear()
        self.pelaaja_etela.clear()
        self.pelaaja_lansi.clear()
        self.pelaaja_pohjoinen.clear()
        # Sorttaa kaikki paitsi lopun '+'
        LOGGER.debug("Pelaajavaihtoehdot ennen sorttia: %s", self.pelaajavaihtoehdot)
        self.pelaajavaihtoehdot[:-1] = sorted(self.pelaajavaihtoehdot[:-1], key=lambda t: t.lower())
        LOGGER.debug("Pelaajavaihtoehdot sortattuna: %s", self.pelaajavaihtoehdot)
        # aseta pudotusvalikoihin
        self.pelaaja_ita.addItems(["Pelaaja itä"])
        self.pelaaja_ita.addItems([nimi for nimi in self.pelaajavaihtoehdot])
        self.pelaaja_etela.addItems(["Pelaaja etelä"])
        self.pelaaja_etela.addItems([nimi for nimi in self.pelaajavaihtoehdot])
        self.pelaaja_lansi.addItems(["Pelaaja länsi"])
        self.pelaaja_lansi.addItems([nimi for nimi in self.pelaajavaihtoehdot])
        self.pelaaja_pohjoinen.addItems(["Pelaaja pohjoinen"])
        self.pelaaja_pohjoinen.addItems([nimi for nimi in self.pelaajavaihtoehdot])
        # Värit kohdilleen
        self.pelaaja_ita.setStyleSheet(STYLESHEET_NORMAL)
        self.pelaaja_etela.setStyleSheet(STYLESHEET_NORMAL)
        self.pelaaja_lansi.setStyleSheet(STYLESHEET_NORMAL)
        self.pelaaja_pohjoinen.setStyleSheet(STYLESHEET_NORMAL)
        # Signaalit takas päälle
        self.pelaaja_ita.blockSignals(False)
        self.pelaaja_etela.blockSignals(False)
        self.pelaaja_lansi.blockSignals(False)
        self.pelaaja_pohjoinen.blockSignals(False)

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
        elif sel_index == tuuli.count()-1:
            LOGGER.debug("Lisää uusi pelaaja")
            self.lisaa_pelaaja(tuuli)
        # Tarkista onko sama pelaaja valittu kahteen paikkaan
        pelaajavalinnat = [
            pelaajavalikko.currentIndex()
            for pelaajavalikko in self.pelaajavalikot
            ]
        self.validit_pelaajat = True
        for pelaajaindex, pelaajavalikko in enumerate(self.pelaajavalikot):
            pelaaja_nimi = pelaajavalikko.currentText()
            # (init-rutiini)
            if pelaaja_nimi == '':
                self.validit_pelaajat = False
                continue
            pelaajan_tuuli = TUULET[pelaajaindex]
            valinta = pelaajavalinnat[pelaajaindex]
            n_eri_paikalla = pelaajavalinnat.count(valinta)
            # Useammassa läsnä (eikä paikan nimi)
            if valinta and n_eri_paikalla > 1:
                LOGGER.debug("%s: '%s' on %d eri paikalla",
                    pelaajan_tuuli, pelaaja_nimi, n_eri_paikalla)
                pelaajavalikko.setStyleSheet(STYLESHEET_ERROR)
                self.validit_pelaajat = False
            # OK
            elif valinta:
                pelaajavalikko.setStyleSheet(STYLESHEET_OK)
            # Pelaajapaikka
            else:
                pelaajavalikko.setStyleSheet(STYLESHEET_NORMAL)
                self.validit_pelaajat = False
        self.tarkista_validius()

    def lisaa_pelaaja(self, tuuli):
        '''Lisää uusi pelaaja pelaajalistaan.
        Aseta valituksi kenttään josta lisäys tapahtui, muissa tokavikaksi.
        '''
        kyselyikkuna = UusiPelaaja(self.centralwidget)
        ok_painettu = kyselyikkuna.exec()
        # Luetaan pelaajan nimi, mahdollinen loppuvälilyönti veks
        pelaajan_nimi = kyselyikkuna.nimikentta.text().rstrip()
        if ok_painettu and len(pelaajan_nimi):
            LOGGER.debug("Pelaajalisäys OK")
            # Tarkistetaan onko pelaaja jo pelaajalistassa
            on_jo_listassa = any(
                vanha_pelaaja.casefold() == pelaajan_nimi.casefold()
                for vanha_pelaaja in self.pelaajavaihtoehdot[:-1]
            )
            if not on_jo_listassa:
                LOGGER.debug("%s ei pelaajalistassa, valid", pelaajan_nimi)
                with open(PELAAJATIEDOSTO, "a+", encoding="UTF-8") as fopen:
                    LOGGER.debug("Tallenna '%s' pelaajatiedostoon", pelaajan_nimi)
                    fopen.write(f"{pelaajan_nimi}\n")
                paikka = len(self.pelaajavaihtoehdot)
                self.pelaajavaihtoehdot.insert(paikka-1, pelaajan_nimi)
                for pelaaja in self.pelaajavalikot:
                    # Muutoin tunnistaa currentIndexChanged
                    # ja jää looppaamaan
                    pelaaja.blockSignals(True)
                    pelaaja.insertItem(paikka, pelaajan_nimi)
                    pelaaja.blockSignals(False)
                tuuli.setCurrentIndex(paikka)
            else:
                # Voisi myös olla: valkkaa listasta jos se siellä jo on
                LOGGER.error("'%s' on jo pelaajalistassa", pelaajan_nimi)
                tuuli.setCurrentIndex(0)
        else:
            LOGGER.debug("Pelaajalisäys CANCEL")
            tuuli.setCurrentIndex(0)

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
        pistesumma = round(pistesumma, 1) # fp-pyöristykset veks
        # Etsi lähin mätsäävä
        nollaraja = 1E-3
        lahin_erotus = None
        lahin_validi = None
        for validi in VALIDIT_PISTESUMMAT:
            erotus = pistesumma - validi
            if lahin_erotus is None:
                lahin_erotus = erotus
                lahin_validi = validi
            elif abs(erotus) < abs(lahin_erotus):
                lahin_erotus = erotus
                lahin_validi = validi
                # Täydellinen mätsi, lopetetaan
                if abs(lahin_erotus) < nollaraja:
                    break
        # Katso onko nolla tai "nolla"
        if abs(lahin_erotus) < nollaraja:
            self.pistesumma.setStyleSheet(STYLESHEET_OK)
            self.pistesumma.setText(f"{pistesumma:.1f}")
            LOGGER.debug("Pistesumma OK. Pistesumma: %.1f, lähin: %s erotuksella %f",
                pistesumma, lahin_validi, lahin_erotus)
        else:
            self.pistesumma.setStyleSheet(STYLESHEET_ERROR)
            LOGGER.debug("Pistesumma ei täsmää. Pistesumma: %.1f, lähin: %s erotuksella %f",
                pistesumma, lahin_validi, lahin_erotus)
            self.validit_pisteet = False
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

    def valitse_tulostiedosto(self):
        '''Valitse tulostiedoston sijainti.

        Palauttaa
        ---------
        bool
            True jos valittiin tiedosto, False muutoin.
        '''
        LOGGER.debug("Valitse tulostiedosto")
        oletuspolku = OLETUS_TULOSTIEDOSTO
        tiedostopolku, ok_cancel = QtWidgets.QFileDialog.getSaveFileName(
            self.centralwidget,
            "Valitse tulostiedosto",
            oletuspolku,
            "Tekstitiedostot (*.txt)",
            options=QtWidgets.QFileDialog.DontConfirmOverwrite,
        )
        if ok_cancel:
            self.tulostiedosto = tiedostopolku
            return True
        return False

    def avaa_tulostiedosto(self):
        '''avaa tulostiedoston sijainti.

        Palauttaa
        ---------
        bool
            True jos valittiin tiedosto, False muutoin.
        '''
        LOGGER.debug("Valitse tulostiedosto")
        oletuspolku = OLETUS_TULOSTIEDOSTO
        tiedostopolku, ok_cancel = QtWidgets.QFileDialog.getOpenFileName(
            self.centralwidget,
            "Valitse tulostiedosto",
            oletuspolku,
            "Tekstitiedostot (*.txt)",
            options=QtWidgets.QFileDialog.DontConfirmOverwrite,
        )
        if ok_cancel:
            self.tulostiedosto = tiedostopolku
            return True
        return False

    def tallenna_tulos(self):
        '''Tallenna tulos tiedostoon.
        '''
        if self.tulostiedosto is None:
            if not self.valitse_tulostiedosto():
                return
        LOGGER.debug("Tallenna tiedostoon '%s'", self.tulostiedosto)
        aikaleima = time.strftime("%Y-%m-%d-%H-%M-%S")
        LOGGER.debug("Tallennetaan tiedostoon '%s' aikaleimalla %s",
            self.tulostiedosto, aikaleima)
        pelitulos = []
        for pelaaja_ind, pistetulos in enumerate(self.pistelaatikot):
            pelaajan_nimi = self.pelaajavalikot[pelaaja_ind].currentText()
            pelaajan_pisteet = float(pistetulos.text().replace(',', '.'))
            LOGGER.debug("%s: %s pisteillä %.1f",
                TUULET[pelaaja_ind], pelaajan_nimi, pelaajan_pisteet)
            pelitulos.append((pelaajan_nimi, pelaajan_pisteet))
        parseri.lisaa_tulos_txt(
            pelitulos=pelitulos,
            tiedostopolku=self.tulostiedosto,
            aikaleima=aikaleima,
            )
        infobox = QtWidgets.QMessageBox(self.centralwidget)
        infobox.setWindowTitle("Tallennettu")
        infobox.setText(f"{self.tulostiedosto}\n{aikaleima}")
        infobox.exec()
        self.reset()

    def reset(self):
        '''Aseta kentät takaisin alkuarvoihin
        '''
        # Pelaajanimet järkkään
        self.tayta_pelaajanimet()
        # Pistelootat tyhjiksi
        for pelaaja_ind, pistetulos in enumerate(self.pistelaatikot):
            self.pelaajavalikot[pelaaja_ind].setCurrentIndex(0)
            pistetulos.clear()

def main():
    '''Käynnistää Paaikkunan.
    '''
    app = QtWidgets.QApplication([])
    app.setApplicationName("Pisteidensyöttäjä")
    app.setApplicationDisplayName("Pisteidensyöttäjä")
    Paaikkuna(
        pelaajalista=sorted(list(PELAAJAT))
        )
    sys.exit(app.exec_())
