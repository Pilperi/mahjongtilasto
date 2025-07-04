'''Tilastointi-main. Ohjaa joko CLI- tai GUI-ympäristöön. Oletuksena GUI.
'''

import logging
from mahjongtilasto.argumentit import parse_sisaantuloargumentit
from mahjongtilasto.gui import gui_main
from mahjongtilasto.cli import cli_main

LOGGER = logging.getLogger(__name__)

def main():
    '''Pääfunktio, joka ohjaa oikeaan suuntaan (GUI tai CLI tai mitä ikinä)
    '''
    args = parse_sisaantuloargumentit()
    if args.verbose > 0:
        logger = logging.getLogger("mahjongtilasto")
        if not logger.hasHandlers():
            streamhandler = logging.StreamHandler()
            logger.addHandler(streamhandler)
        if args.loglevel:
            logger.setLevel(args.loglevel)
        else:
            logger.setLevel(args.verbose)
        LOGGER.info("Lisättiin verboosi loggeri")
    # GUI-moodi (oletus)
    if not args.cli:
        gui_main.main()
    # CLI-moodi
    else:
        cli_main.main(args)

if __name__ == "__main__":
    main()
