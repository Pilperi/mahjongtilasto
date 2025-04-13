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
    return INP_ARGS.parse_args()
