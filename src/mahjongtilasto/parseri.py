'''Pelitulosten parserifunktiot.'''
import os
# import time
import datetime
import logging
from mahjongtilasto import TUULET, VALIDIT_PISTESUMMAT_10K, VALIDIT_PISTESUMMAT_100

LOGGER = logging.getLogger(__name__)

def parse_id(rivi: str):
    '''ID-rivin parseri.

    ID-rivin rakenne on aikaleima, esim.
    2024-12-09-20-22-30
    (9. joulukuuta 2024, klo 22:30)

    Parametrit
    ----------
    rivi : str
        Rivi josta tarkoitus parsia

    Palauttaa
    ---------
    str tai None
        rstrip-siivottu rivi jos validi, muutoin None
    '''
    # Väärä datatyyppi
    if not isinstance(rivi, str):
        LOGGER.debug("Ei validi ID %s", rivi)
        return None
    rivi = rivi.rstrip()
    # Tyhjä rivi: älä laita logiin mitään
    if not len(rivi):
        return None
    splitattu = rivi.split("-")
    # Ei oikeaa määrää elementtejä
    if len(splitattu) < 4:
        LOGGER.debug("Ei validi ID %s", rivi)
        return None
    # Ei-numeroita seassa
    if not all(osa.isnumeric() for osa in splitattu):
        LOGGER.debug("Ei validi ID %s", rivi)
        return None
    # Joku osa väärän pituinen
    if len(splitattu[0]) != 4 or any(len(osa) != 2 for osa in splitattu[1:3]):
        LOGGER.debug("Ei validi ID %s", rivi)
        return None
    # Muutoin validi ID
    return rivi


def parse_pelaajatulos(rivi: str):
    '''Lue yksittäisen pelaajan tulosrivi.

    Tulkkaa rivi nimi + pistetulos -arvopariksi.

    Parametrit
    ----------
    rivi : str
        Rivi josta tulos tarkoitus parsia, muotoa
        Jaakko Jonkkaaja 21300
        tai
        Pilperi 56.8

    Palauttaa
    ---------
    tuple (str, float)
        Tulosrivi parsitussa muodossa, ensin pelaajan nimi
        ja sitten pistemäärä liukulukuna (ts. tuhannella kertominen
        tehtävä kun hanchanin kaikkien pelaajien pistemäärät luettu
        ja niiden summasta päätelmiä tehty)
    '''
    splitattu = rivi.rstrip().split(" ")
    if len(splitattu) < 2:
        LOGGER.error("Ei validi tulosrivi '%s'", rivi)
        raise ValueError(f"Ei validi tulosrivi '{rivi:s}'")
    pelaajanimi = " ".join(splitattu[:-1])
    try:
        pistetulos = float(splitattu[-1])
    except ValueError as err:
        LOGGER.error("Ei validi tulosrivi '%s' (%s)", rivi, err)
        raise ValueError from err
    return pelaajanimi, pistetulos

def skaalaa_hanchanin_pisteet(pelaajatulokset: list):
    '''Tee tarvittavat skaalailut pelaajien tuloksiin.

    Muunnetaan 12.3 ja 12300.0 muotoon 12300
    eli liukuluvusta kokonaisluvuksi ja tarpeen mukaan tuhannella kertoen.

    Parametrit
    ----------
    pelaajatulokset : list
        Pelaajien tulokset raa'asti luettuina, (nimi, pisteet) tuplearvoina.

    Palauttaa
    ---------
    skaalatut_tulokset : list
        Vastaava lista mutta jossa pisteitä tarpeen mukaan skaalailtu.
    '''
    pistesumma = round(sum(tulos[1] for tulos in pelaajatulokset), 1)
    LOGGER.debug("Pisteet %s summaa %f", pelaajatulokset, pistesumma)
    # 12.3
    if pistesumma in VALIDIT_PISTESUMMAT_10K:
       LOGGER.debug("Skaalataan pisteet tuhannella")
       skaalatut_tulokset = [
            (tulos[0], int(1000*tulos[1]))
            for tulos in pelaajatulokset
        ]
    # 12300
    elif pistesumma in VALIDIT_PISTESUMMAT_100:
        LOGGER.debug("Ei skaalata pisteitä")
        skaalatut_tulokset = [
            (tulos[0], int(tulos[1]))
            for tulos in pelaajatulokset
        ]
    elif pistesumma == 0.0:
        LOGGER.debug("Nollasumma, katsotaan kummalla formaatilla")
        if any((matsaava_tulos := tulos[1])%100 for tulos in pelaajatulokset):
            LOGGER.debug("%s sisältää alle satasia, skaalataan tuhannella")
            skaalatut_tulokset = [
                (tulos[0], int(1000*tulos[1]))
                for tulos in pelaajatulokset
            ]
        else:
            LOGGER.debug("Ei skaalata pisteitä")
            skaalatut_tulokset = [
                (tulos[0], int(tulos[1]))
                for tulos in pelaajatulokset
            ]
    else:
        LOGGER.debug("Ei skaalata pisteitä")
        skaalatut_tulokset = [
            (tulos[0], int(tulos[1]))
            for tulos in pelaajatulokset
        ]
    return skaalatut_tulokset


def parse_txt_dictiksi(tiedostopolku: str):
    '''Lue pelitulokset tekstitiedostosta.

    Parametrit
    ----------
    tiedostopolku : str
        Tekstitiedoston polku josta tulokset luetaan.

    Palauttaa
    ---------
    dict
        Kaikki tiedoston pelitulokset yhdessä dictissä.
        Pelipäivämäärät (ID) avaimena, tulokset arvoina.
    '''
    if not os.path.isfile(tiedostopolku):
        LOGGER.error("Tiedostopolku '%s' ei ole validi!")
        raise ValueError(f"Tiedostopolku {tiedostopolku:s} ei ole validi!")
    tulokset = {}
    with open(tiedostopolku, "r", encoding="utf-8") as fopen:
        rivi = fopen.readline()
        # EOF
        while rivi:
            rivi = rivi.rstrip()
            # ID: lue yksittäinen pelitulos
            aikaleima = parse_id(rivi)
            if aikaleima is not None:
                LOGGER.debug("Lue tulos %s", aikaleima)
                # Pistelukemat jotenkin vaan inee
                raakatulos = [None for i in TUULET]
                for tuuli_index, tuuli in enumerate(TUULET):
                    rivi = fopen.readline().rstrip()
                    raakatulos[tuuli_index] = parse_pelaajatulos(rivi)
                    LOGGER.debug("%s tulos %s", tuuli, raakatulos[tuuli_index])
                # Katsotaan summaako pisteet 100 000 vai 100.0 vai mihin
                tulokset[aikaleima] = skaalaa_hanchanin_pisteet(raakatulos)
            rivi = fopen.readline()
    return tulokset


def lisaa_tulos_txt(pelitulos: list, tiedostopolku: str, aikaleima=None):
    '''Kirjaa pelitulos tekstitiedoston pohjalle.

    Kirjoita pelitulos tekstitiedostoon.
    Tulos lisätään pohjalle aikaleiman arvosta riippumatta.

    Parametrit
    ----------
    pelitulos : list
        Pelaajatulokset tuulijärjestyksessä itä-etelä-länsi-pohjoinen
        (pelaajan nimi, pelaajan pisteet) -arvopareja neljä kappaletta.
    tiedostopolku : str
        Tiedosto johon tulokset tarkoitus kirjata.
        Luodaan jos ei ollut olemassa.
    aikaleima : str tai None, vapaaehtoinen
        Aikaleima jolla tulos kirjataan.
        Jos ei tarjottu (None), käytetään kutsuhetkeä.
    '''
    def validoi_pelaajatulos(tulos):
        if not isinstance(tulos[0], str):
            return False
        if len(tulos[0]) == 0:
            return False
        if not isinstance(tulos[1], (int, float)):
            return False
        return True
    # Validoidaan data ennen kuin lähdetään kirjoittelemaan mitään
    for tuuli_index, tuuli in enumerate(TUULET):
        pelaajatulos = pelitulos[tuuli_index]
        if not validoi_pelaajatulos(pelaajatulos):
            LOGGER.error("Ei validi pelaajatulos %s", pelaajatulos)
            raise ValueError(f"Ei validi pelaajatulos {pelaajatulos}")
    if parse_id(aikaleima) is None:
        aikaleima = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    with open(tiedostopolku, "a+") as fopen:
        LOGGER.debug(aikaleima)
        fopen.write(aikaleima+"\n")
        for tuuli_index, tuuli in enumerate(TUULET):
            pelaaja = pelitulos[tuuli_index][0]
            pisteet = pelitulos[tuuli_index][1]
            if isinstance(pisteet, float):
                LOGGER.debug("%s %s %.1f", tuuli, pelaaja, pisteet)
                fopen.write(f"{pelaaja:s} {pisteet:.1f}\n")
            else:
                LOGGER.debug("%s %s %d", tuuli, pelaaja, pisteet)
                fopen.write(f"{pelaaja:s} {pisteet:d}\n")
        fopen.write("\n")
    LOGGER.debug("Kirjoitettu")

def laske_sijoitukset(pisteet: list):
    '''Laske pistesijoitusten sijoitukset.

    Isoin pistenumero on 1. sija.
    Jaetuilla sijoilla annetaan pelaajan kaikki sijoitukset, koska siitä helpompi
    laskea uman arvo (keskiarvo sijoituksista).

    Parametrit
    ----------
    pisteet : list
        Pelaajien loppupisteet. Kullekin pelaajalle kaikki tämän sijoitukset,
        ts. pelaajan uma on sijoitusumien keskiarvo.

    Palauttaa
    ---------
    sijoitukset : list
        Pelaajien sijoitukset, esim [[1] [2], [3], [4]]
        tai [[1,2], [1,2], [3], [4]]
    '''
    sijoitukset = [[] for _ in pisteet]
    sijoitus = 1
    LOGGER.debug("Pisteet %s", pisteet)
    for piste_ind, piste in enumerate(sorted(pisteet, reverse=True)):
        LOGGER.debug("Piste %s %d suurin", piste, sijoitus)
        for pelaaja_ind, pelaaja_piste in enumerate(pisteet):
            # Asetetaan sijoitus
            if pelaaja_piste == piste:
                sijoitukset[pelaaja_ind].append(sijoitus)
                LOGGER.debug("Piste on pelaajalla %s, sijoitukset %s",
                    TUULET[pelaaja_ind], sijoitukset[pelaaja_ind])
        sijoitus += 1
    return sijoitukset

def pelaajadelta(tiedostopolku: str, pelaaja: str, jalkeen_ajan=None):
    '''Etsi tuloslistasta tietyn pelaajan pistedelta.

    Parametrit
    ----------
    tiedostopolku : str
        Tiedosto jossa pelitulokset.
    pelaaja : str
        Pelaajan nimi.

    Palauttaa
    ---------
    dict
        Pelaajan pistetilastot:
            - Pistesumma
            - Pelikohtaiset pistedeltat
            - Pelikohtaiset sijoitukset
    '''
    if not os.path.isfile(tiedostopolku):
        LOGGER.error("Tiedostopolku '%s' ei ole validi!")
        raise ValueError(f"Tiedostopolku {tiedostopolku:s} ei ole validi!")
    tulokset = {
        "delta": 0,
        "delta_vals": [],
        "sijoitukset": [],
        "peleja": 0,
    }
    with open(tiedostopolku, "r", encoding="utf-8") as fopen:
        rivi = fopen.readline()
        # EOF asti
        while rivi:
            rivi = rivi.rstrip()
            # ID: lue yksittäinen pelitulos
            aikaleima = parse_id(rivi)
            if aikaleima is None:
                rivi = fopen.readline()
                continue
            # Kerta oli validi ID, katsotaan onko tarpeeksi tuore peli
            mukaan_tuloksiin = True
            if isinstance(jalkeen_ajan, datetime.date):
                splitattu_aika = aikaleima.split("-")
                pelin_aika = datetime.date(
                    year=int(splitattu_aika[0]),
                    month=int(splitattu_aika[1]),
                    day=int(splitattu_aika[2]),
                    )
                if pelin_aika >= jalkeen_ajan:
                    LOGGER.debug("'%s' on jälkeen '%s'",
                        aikaleima, jalkeen_ajan.strftime("%Y-%m-%d"))
                    mukaan_tuloksiin = True
                else:
                    LOGGER.debug("'%s' on ennen '%s', skip",
                        aikaleima, jalkeen_ajan.strftime("%Y-%m-%d"))
                    mukaan_tuloksiin = False
            # Vain jos aikaleima täsmää
            if mukaan_tuloksiin:
                LOGGER.debug("Lue tulos %s", aikaleima)
                tulos = [None for i in TUULET]
                for tuuli_index, tuuli in enumerate(TUULET):
                    rivi = fopen.readline().rstrip()
                    tulos[tuuli_index] = parse_pelaajatulos(rivi)
                    LOGGER.debug("%s tulos %s", tuuli, tulos[tuuli_index])
                tulos = skaalaa_hanchanin_pisteet(tulos)
                sijoitukset = laske_sijoitukset([t[1] for t in tulos])
                for pelipaikka, (nimi, piste) in enumerate(tulos):
                    if nimi == pelaaja:
                        aloituspisteet = sum(tls[1] for tls in tulos)/4
                        delta = piste - aloituspisteet
                        tulokset["delta"] += int(delta)
                        tulokset["delta_vals"].append(delta)
                        tulokset["sijoitukset"].append(sijoitukset[pelipaikka])
                        tulokset["peleja"] += 1
                        break
                else:
                    LOGGER.debug("%s ei pelannut pelissä %s", pelaaja, aikaleima)
            rivi = fopen.readline()
    return tulokset
