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
    # Lyhyt aikaleima
    testr = "2024-12-09-21"
    parsetulos = parseri.parse_id(testr)
    assert isinstance(parsetulos, str)
    # Pitkä aikaleima
    testr = "2024-12-09-21-29-29-29-29"
    parsetulos = parseri.parse_id(testr)
    assert isinstance(parsetulos, str)


def test_parse_id_fail():
    '''Testaa että huonot ID:t hylätään.'''
    # Lyhyt aikaleima
    testr = "2024-12-09"
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
    assert parsetulos[1] == 21.3
    testr = "Pelaaja -21.3\n"
    parsetulos = parseri.parse_pelaajatulos(testr)
    assert parsetulos[0] == "Pelaaja"
    assert parsetulos[1] == -21.3
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
    assert parsetulos[1] == 21.3
    # 21.0 tiivistetty muotoon 21
    testr = "Pelaaja 21"
    parsetulos = parseri.parse_pelaajatulos(testr)
    assert parsetulos[0] == "Pelaaja"
    assert parsetulos[1] == 21.0
    testr = "Pelaaja -21"
    parsetulos = parseri.parse_pelaajatulos(testr)
    assert parsetulos[0] == "Pelaaja"
    assert parsetulos[1] == -21.0
    # 20.0 tiivistetty muotoon 20
    testr = "Pelaaja 20"
    parsetulos = parseri.parse_pelaajatulos(testr)
    assert parsetulos[0] == "Pelaaja"
    assert parsetulos[1] == 20.0
    testr = "Pelaaja -20"
    parsetulos = parseri.parse_pelaajatulos(testr)
    assert parsetulos[0] == "Pelaaja"
    assert parsetulos[1] == -20.0
    # 100.0 ei voi tiivistää muotoon 100
    testr = "Pelaaja 100"
    parsetulos = parseri.parse_pelaajatulos(testr)
    assert parsetulos[0] == "Pelaaja"
    assert parsetulos[1] == 100
    testr = "Pelaaja -100"
    parsetulos = parseri.parse_pelaajatulos(testr)
    assert parsetulos[0] == "Pelaaja"
    assert parsetulos[1] == -100

def test_sijoitukset_helppo():
    '''Testaa että sijoitusten lasku toimii helpossa tapauksessa.
    '''
    pisteet = [-1.3, 3.8, 15.3, 82.2]
    assert sum(pisteet) == 100.0
    sijoitukset = parseri.laske_sijoitukset(pisteet)
    assert sijoitukset == [[4], [3], [2], [1]]
    pisteet.reverse()
    assert parseri.laske_sijoitukset(pisteet) == [[1], [2], [3], [4]]
    pisteet = [3.8, -1.3, 82.2, 15.3]
    assert parseri.laske_sijoitukset(pisteet) == [[3], [4], [1], [2]]


def test_sijoitukset_jaetut_sijat():
    '''Testaa että sijoitusten lasku toimii jaetuilla sijoituksilla.
    '''
    # Jaettu ykkönen
    pisteet = [28.0, 21.0, 28.0, 23.0]
    sijoitukset = parseri.laske_sijoitukset(pisteet)
    assert sijoitukset == [[1, 2], [4], [1, 2], [3]]
    # Jaettu nelonen
    pisteet = [29.0, 21.5, 28.0, 21.5]
    sijoitukset = parseri.laske_sijoitukset(pisteet)
    assert sijoitukset == [[1], [3, 4], [2], [3, 4]]
    # Kaikki tasoissa
    pisteet = [25.0, 25.0, 25.0, 25.0]
    sijoitukset = parseri.laske_sijoitukset(pisteet)
    assert sijoitukset == [[1, 2, 3, 4] for _ in range(len(pisteet))]
    # Kaks ja kaks
    pisteet = [28.0, 22.0, 28.0, 22.0]
    sijoitukset = parseri.laske_sijoitukset(pisteet)
    assert sijoitukset == [[1, 2], [3, 4], [1, 2], [3, 4]]
