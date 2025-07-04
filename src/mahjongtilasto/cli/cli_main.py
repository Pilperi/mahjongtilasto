'''CLI-moodi yksinkertaisia dataoperaatioita varten: JSON-ulostulo tilastodatasta tmv.
'''
import os
import json
import logging
from mahjongtilasto import parseri
LOGGER = logging.getLogger(__name__)

def main(args):
    '''Suorittaa toimenpiteet komentoriviargumenttien perusteella.
    '''
    # Muunna tekstitiedosto JSON-muotoon jota helpompi käpistellä:
    if args.toiminto == "muunna":
        LOGGER.info("Käännetään TXT-tiedosto JSON-muotoon")
        # Data sisään
        if not os.path.isfile(args.tulostiedosto):
            LOGGER.error("Ei tulostiedostoa '%s'!", args.tulostiedosto)
            raise ValueError(f"Ei tulostiedostoa '{args.tulostiedosto:s}'!")
        LOGGER.info("Luetaan data tiedostosta '%s'", args.tulostiedosto)
        data = parseri.parse_txt_dictiksi(args.tulostiedosto)
        # Data ulos
        # Ihan siltä varalta että joku joskus yrittäisi kirjoittaa alkuperäisen tiedoston päälle
        # (todennäköisempää kuin luulisikaan)
        if os.path.isfile(args.ulostulo) and os.path.samefile(args.tulostiedosto, args.ulostulo):
            LOGGER.error("Yritetään kirjoittaa parsintatulosta alkuperäisen tulostiedoston päälle!")
            raise ValueError(f"Tulostiedoston päälle ei saa kirjoittaa! {args.tulostiedosto:s} -> {args.ulostulo:s}")
        LOGGER.info("Kirjoitetaan luettu data tiedostoon '%s'", args.ulostulo)
        with open(args.ulostulo, "w+") as fopen:
            json.dump(data, fopen, indent=4)
    LOGGER.info("Valmis")
