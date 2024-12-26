'''Mahjong-tulosten tilastointikirjasto.

Yksinkertainen kirjasto mahjong-pelitulosten hallinnointiin.
'''
import os

__version__ = "2024.12.27.0"

KOTIKANSIO = os.path.expanduser("~")
KANSIO_CFG = os.path.join(KOTIKANSIO, ".config", "mahjongtilasto")
if not os.path.isdir(KANSIO_CFG):
    os.makedirs(KANSIO_CFG)

# Lue pelaajat tiedostosta
PELAAJAT = set()
PELAAJATIEDOSTO = os.path.join(KANSIO_CFG, "pelaajat.txt")
if not os.path.isfile(PELAAJATIEDOSTO):
    fopen = open(PELAAJATIEDOSTO, "w+", encoding="UTF-8")
    fopen.write("# Pelaajanimet rivinvaihdolla eroteltuna, # kommentointimerkkinä\n")
    fopen.close()
with open(PELAAJATIEDOSTO, "r", encoding="UTF-8") as fopen:
    while rivi := fopen.readline():
        rivi = rivi.rstrip()
        if not rivi.startswith("#") and len(rivi) > 0:
            PELAAJAT.add(rivi)

TUULET = ("ITÄ", "ETELÄ", "LÄNSI", "POHJOINEN")
VALIDIT_PISTESUMMAT = (
    4*25_000,
    4*25.0,
    0,
    4*30_000,
    4*30.0,
)
