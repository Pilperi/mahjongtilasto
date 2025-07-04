'''Mahjong-tulosten tilastointikirjasto.

Yksinkertainen kirjasto mahjong-pelitulosten hallinnointiin.
'''
import os
import time
import datetime

__version__ = "2025.07.04.1"

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
# Tulostiedoston oletusarvo
OLETUS_TULOSTIEDOSTO = os.path.join(KOTIKANSIO, time.strftime("pelit_%Y.txt"))

TUULET = ("ITÄ", "ETELÄ", "LÄNSI", "POHJOINEN")

# Pistemääritelmät
# Validit aloituspisteet
VALIDIT_PISTESUMMAT_10K = (
    4*25.0,
    4*30.0,
)
VALIDIT_PISTESUMMAT_100 = (
    4*25_000,
    4*30_000,
)
VALIDIT_PISTESUMMAT = (
    *VALIDIT_PISTESUMMAT_10K,
    0,
    *VALIDIT_PISTESUMMAT_100,
)
# Oletus-uma (EMA 15/5)
UMA_DEFAULT = (15_000, 5000, -5000, -15_000)

# Tulosten rajoittamiseen, valitse vain pelit jotka vaaditun tuoreita
AIKADELTAT = {
    "Kaikki": None,
    "6 kk": datetime.timedelta(days=6*30),
    "3 kk": datetime.timedelta(days=3*30),
    "1 kk": datetime.timedelta(days=30),
}
