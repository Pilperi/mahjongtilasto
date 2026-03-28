'''Mahjong-tulosten tilastointikirjasto.

Yksinkertainen kirjasto mahjong-pelitulosten hallinnointiin.
'''
import os
import time
import datetime
import configparser

# Tuetut kielet
LANGUAGES = ("FI", "ENG")

# Koeta lukea versio versiotiedostosta.
# Jos sellaista ei ole, tehdään.
VERSIOFILU = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    "VERSION"
)
__version__ = datetime.datetime.now().strftime("%Y.%m.%d.0")
if os.path.isfile(VERSIOFILU):
    with open(VERSIOFILU, "r") as fopen:
        __version__ = fopen.readline().rstrip()
else:
    with open(VERSIOFILU, "w+") as fopen:
        fopen.write(__version__)


KOTIKANSIO = os.path.expanduser("~")
KANSIO_CFG = os.path.join(KOTIKANSIO, ".config", "mahjongtilasto")
if not os.path.isdir(KANSIO_CFG):
    os.makedirs(KANSIO_CFG)

# Oletus-uma (EMA 15/5)
UMA_DEFAULT = (15_000, 5000, -5000, -15_000)
ASETUKSET = {
    "LANG": "FI",
    "POINTS": (100, 100_000, 0),
    "UMA": UMA_DEFAULT,
}

# Tulostiedoston oletusarvo
OLETUS_TULOSTIEDOSTO = os.path.join(KOTIKANSIO, time.strftime("pelit_%Y.txt"))
# Asetustiedosto
TIEDOSTO_CFG = os.path.join(KANSIO_CFG, "settings.ini")
config = configparser.ConfigParser()
if not os.path.exists(TIEDOSTO_CFG):
    config['SETTINGS'] = ASETUKSET
    config['SETTINGS']["POINTS"] = "/".join([str(pnt) for pnt in ASETUKSET["POINTS"]])
    config['SETTINGS']["UMA"] = "/".join([str(uma) for uma in ASETUKSET["UMA"]])
    config['FIELDS'] = {
        "LANG": f"Language, options are {LANGUAGES}",
        "POINTS": "Valid sum of inserted points, e.g. for zero-sum: 0, for 100(k) + zero-sum: 100/100000/0",
        "UMA": "Uma value, for EMA defaults insert 15000/5000/-5000/-15000",
        "RESULTFILE": "Fixed result file location. If not set, uses year specific file.",
    }
    with open(TIEDOSTO_CFG, "w+") as fopen:
        config.write(fopen)
else:
    config.read(TIEDOSTO_CFG)
    ASETUKSET["LANG"] = config.get("SETTINGS", "LANG", fallback="FI")
    if ASETUKSET["LANG"] not in LANGUAGES:
        raise ValueError(
            f"Unsupported language '{ASETUKSET['LANG']}'!"
            f"Supported: {LANGUAGES}")
    points = config.get("SETTINGS", "POINTS", fallback="100/100000/0")
    ASETUKSET["POINTS"] = tuple(float(pnt) for pnt in points.split("/"))
    uma = config.get("SETTINGS", "UMA", fallback="15000/5000/-5000/-15000")
    ASETUKSET["UMA"] = tuple(float(umaval) for umaval in uma.split("/"))
    tulostiedosto = config.get("SETTINGS", "RESULTFILE", fallback=None)
    if tulostiedosto is not None:
        OLETUS_TULOSTIEDOSTO = tulostiedosto
    else:
        basename = "pelit" if ASETUKSET["LANG"] == "FI" else "games"
        OLETUS_TULOSTIEDOSTO = os.path.join(
            KOTIKANSIO,
            time.strftime(f"{basename}_%Y.txt"))
LANG = ASETUKSET["LANG"]


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
    ASETUKSET["POINTS"] if ASETUKSET["POINTS"]
    else (100, 100_000, 0)
)

# Tulosten rajoittamiseen, valitse vain pelit jotka vaaditun tuoreita
AIKADELTAT = {
    "Kaikki": None,
    "6 kk": datetime.timedelta(days=6*30),
    "3 kk": datetime.timedelta(days=3*30),
    "1 kk": datetime.timedelta(days=30),
}
