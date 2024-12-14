'''Parserifunktioiden yksikkötestit'''
from mahjongtilasto import parseri


def test_parse_id_pass():
    '''Testaa että validit ID-rivit parsitaan oikein'''
    testr = "2024-12-09-21-29-45"
    parsetulos = parseri.parse_id(testr)
    assert isinstance(parsetulos, str)
    assert len(parsetulos) == len(testr)
    # Rivinvaihdolla
    testr = "2024-12-09-21-29-45\n"
    parsetulos = parseri.parse_id(testr)
    assert testr == "2024-12-09-21-29-45\n"
    assert isinstance(parsetulos, str)
    assert len(parsetulos) == len(testr)-1


def test_parse_id_fail():
    '''Testaa että huonot ID:t hylätään.'''
    # Lyhyt aikaleima
    testr = "2024-12-09-21-29\n"
    parsetulos = parseri.parse_id(testr)
    assert parsetulos is None
    # Pitkä aikaleima
    testr = "2024-12-09-21-29-29-29-29"
    parsetulos = parseri.parse_id(testr)
    assert parsetulos is None
    # Ei-numeroita
    testr = "2024-1w2-09-21-29-29-29-29"
    parsetulos = parseri.parse_id(testr)
    assert parsetulos is None
    # Vääriä numeroita
    testr = "2024-123-09-21-29-45\n"
    parsetulos = parseri.parse_id(testr)
    assert parsetulos is None
    testr = "2024-12-9-21-29-45\n"
    parsetulos = parseri.parse_id(testr)
    assert parsetulos is None
    testr = "202-12-09-21-29-45\n"
    parsetulos = parseri.parse_id(testr)
    assert parsetulos is None
    testr = "20244-12-09-21-29-45\n"
    parsetulos = parseri.parse_id(testr)
    assert parsetulos is None
    # None sisäänmenona
    testr = None
    parsetulos = parseri.parse_id(testr)
    assert parsetulos is None


def test_parse_pelaajatulos_pass():
    '''Testaa että validit pelaajatulosrivit saadaan luettua'''
    # Yksinkertainen tapaus
    testr = "Pelaaja 21300\n"
    parsetulos = parseri.parse_pelaajatulos(testr)
    assert parsetulos[0] == "Pelaaja"
    assert parsetulos[1] == 21300
    testr = "Pelaaja 21.3\n"
    parsetulos = parseri.parse_pelaajatulos(testr)
    assert parsetulos[0] == "Pelaaja"
    assert parsetulos[1] == 21300
    testr = "Pelaaja -21.3\n"
    parsetulos = parseri.parse_pelaajatulos(testr)
    assert parsetulos[0] == "Pelaaja"
    assert parsetulos[1] == -21300
    testr = "Pelaaja -21300\n"
    parsetulos = parseri.parse_pelaajatulos(testr)
    assert parsetulos[0] == "Pelaaja"
    assert parsetulos[1] == -21300
    # Kolmeosainen nimi
    testr = "Pelaaja jolla pitkä nimi 21300\n"
    parsetulos = parseri.parse_pelaajatulos(testr)
    assert parsetulos[0] == "Pelaaja jolla pitkä nimi"
    assert parsetulos[1] == 21300
    testr = "Pelaaja jolla pitkä nimi 21.3\n"
    parsetulos = parseri.parse_pelaajatulos(testr)
    assert parsetulos[0] == "Pelaaja jolla pitkä nimi"
    assert parsetulos[1] == 21300
