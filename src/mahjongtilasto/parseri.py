'''Pelitulosten parserifunktiot.'''
import os
import time
import logging
from mahjongtilasto import TUULET

import logging
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
    splitattu = rivi.split("-")
    # Ei oikeaa määrää elementtejä
    if len(splitattu) != 6:
        LOGGER.debug("Ei validi ID %s", rivi)
        return None
    # Ei-numeroita seassa
    if not all(osa.isnumeric() for osa in splitattu):
        LOGGER.debug("Ei validi ID %s", rivi)
        return None
    # Joku osa väärän pituinen
    if len(splitattu[0]) != 4 or any(len(osa) != 2 for osa in splitattu[1:]):
        LOGGER.debug("Ei validi ID %s", rivi)
        return None
    # Muutoin validi ID
    return rivi.rstrip()


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
    tuple (str, int)
        Tulosrivi parsitussa muodossa, ensin pelaajan nimi
        ja sitten pistemäärä kokonaislukumuodossa (esim. 21300)
    '''
    splitattu = rivi.rstrip().split(" ")
    if len(splitattu) < 2:
        LOGGER.error("Ei validi tulosrivi '%s'", rivi)
        raise ValueError(f"Ei validi tulosrivi '{rivi:s}'")
    pelaajanimi = " ".join(splitattu[:-1])
    try:
        pistetulos = float(splitattu[-1])
        if "." in splitattu[-1]:
            pistetulos *= 1000
    except ValueError as err:
        LOGGER.error("Ei validi tulosrivi '%s' (%s)", rivi, err)
        raise ValueError from err
    return pelaajanimi, int(pistetulos)


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
                tulokset[aikaleima] = [None for i in TUULET]
                for tuuli_index,tuuli in enumerate(TUULET):
                    rivi = fopen.readline().rstrip()
                    tulokset[aikaleima][tuuli_index] = parse_pelaajatulos(rivi)
                    LOGGER.debug("%s tulos %s", tuuli, tulokset[aikaleima][tuuli_index])
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
        if not len(tulos[0]):
            return False
        if not isinstance(tulos[1], (int, float)):
            return False
        return True
    # Validoidaan data ennen kuin lähdetään kirjoittelemaan mitään
    for tuuli_index,tuuli in enumerate(TUULET):
        pelaajatulos = pelitulos[tuuli_index]
        if not validoi_pelaajatulos(pelaajatulos):
            LOGGER.error("Ei validi pelaajatulos %s", pelaajatulos)
            raise ValueError(f"Ei validi pelaajatulos {pelaajatulos}")
    if parse_id(aikaleima) is None:
        aikaleima = time.strftime("%Y-%m-%d-%H-%M-%S")
    with open(tiedostopolku, "a+") as fopen:
        LOGGER.debug(aikaleima)
        fopen.write(aikaleima+"\n")
        for tuuli_index,tuuli in enumerate(TUULET):
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


def pelaajadelta(tiedostopolku: str, pelaaja: str):
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
            - Pistedeltan varianssi
            - Kaikki delta-arvot listana
    '''
    if not os.path.isfile(tiedostopolku):
        LOGGER.error("Tiedostopolku '%s' ei ole validi!")
        raise ValueError(f"Tiedostopolku {tiedostopolku:s} ei ole validi!")
    tulokset = {
        "delta": 0.0,
        "var": 0.0,
        "delta_vals": [],
    }
    with open(tiedostopolku, "r", encoding="utf-8") as fopen:
        rivi = fopen.readline()
        # EOF asti
        while rivi:
            rivi = rivi.rstrip()
            # ID: lue yksittäinen pelitulos
            aikaleima = parse_id(rivi)
            if aikaleima is not None:
                LOGGER.debug("Lue tulos %s", aikaleima)
                tulos = [None for i in TUULET]
                for tuuli_index,tuuli in enumerate(TUULET):
                    rivi = fopen.readline().rstrip()
                    tulos[tuuli_index] = parse_pelaajatulos(rivi)
                    LOGGER.debug("%s tulos %s", tuuli, tulokset[aikaleima][tuuli_index])
                for nimi,piste in tulos:
                    if nimi == pelaaja:
                        aloituspisteet = sum(tls[1] for tls in tulos)/4
                        delta = piste - aloituspisteet
                        tulokset["delta"] += delta
                        tulokset["delta_vals"].append(delta)
                        break
                else:
                    LOGGER.debug("%s ei pelannut pelissä %s", pelaaja, aikaleima)
            rivi = fopen.readline()
    return tulokset
