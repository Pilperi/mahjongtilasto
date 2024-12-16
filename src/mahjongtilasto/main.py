'''Tilastointi-main.
TODO.
'''

import logging
from mahjongtilasto.gui import main_gui

LOGGER = logging.getLogger(__name__)

def main():
    '''Pääfunktio, joka ohjaa oikeaan suuntaan (GUI tai CLI tai mitä ikinä)
    '''
    main_gui.main()

if __name__ == "__main__":
    main()
