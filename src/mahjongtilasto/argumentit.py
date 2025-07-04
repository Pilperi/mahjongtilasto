'''Argumenttien tulkkaus.
'''
import argparse
import mahjongtilasto

INP_ARGS: argparse.ArgumentParser

def parse_sisaantuloargumentit():
    global INP_ARGS
    INP_ARGS = argparse.ArgumentParser(description="Mahjong-pelitulosten tilastointiohjelma")
    INP_ARGS.add_argument(
        "--version",
        action="version",
        version=mahjongtilasto.__version__,
        help="Tulosta versio ja poistu.",
        )
    INP_ARGS.add_argument(
        "--verbose", "-v",
        action="count",
        default=0,
        dest="verbose",
        help="Aja verboosina.",
        )
    INP_ARGS.add_argument(
        "--loglevel", "-l",
        action="store",
        default=0,
        dest="loglevel",
        help="Kuinka verboosilla tasolla ollaan",
        )
    INP_ARGS.add_argument(
        "--cli",
        action="store_true",
        dest="cli",
        help="Käytä CLI-moodia",
        )
    INP_ARGS.add_argument(
        "--toiminto",
        action="store",
        dest="toiminto",
        choices=["muunna"],
        default="muunna",
        help="CLI-moodin suoritettava toiminto",
        )
    INP_ARGS.add_argument(
        "--tulostiedosto", "-f",
        action="store",
        dest="tulostiedosto",
        default=mahjongtilasto.OLETUS_TULOSTIEDOSTO,
        help="Tekstitiedosto josta pelit luetaan",
        )
    INP_ARGS.add_argument(
        "--ulostulo", "-o",
        action="store",
        dest="ulostulo",
        default=mahjongtilasto.OLETUS_TULOSTIEDOSTO.replace(".txt", ".json"),
        help="Tiedosto johon pelitulokset kirjoitetaan JSON-muodossa",
        )
    return INP_ARGS.parse_args()
