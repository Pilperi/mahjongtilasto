'''Luokka aikaikkunoiden hallintaan.
'''
import datetime

class AikaIkkuna:
    '''Luokka yleisille aikaikkunoille.'''
    def __init__(self, *args, **kwargs):
        '''Alusta luokka, oletuksena rajaton aikaikkuna'''
        # Aloituspäivä, None (rajoittamaton) tai datetime.date
        alkuaika = None
        if args:
            alkuaika = args[0]
        else:
            alkuaika = kwargs.get("alkupaiva", None)
        # Parse tarvittaessa
        self._alkupaiva = (
            AikaIkkuna.aikaleima(alkuaika)
            if isinstance(alkuaika, str)
            else alkuaika
            )
        # Vastaavasti ikkunan päätepäivä
        loppuaika = None
        if len(args) > 1:
            loppuaika = args[1]
        else:
            loppuaika = kwargs.get("loppupaiva", None)
        self._loppupaiva = (
            AikaIkkuna.aikaleima(loppuaika)
            if isinstance(loppuaika, str)
            else loppuaika
            )
        # Jos rajat asetettiin, tarkista että ne käy järkeen
        if not self:
            raise ValueError("Alkupäivä ei voi olla loppupäivän jälkeen!")

    @property
    def alkupaiva(self):
        '''Alkupäivän getteri'''
        return self._alkupaiva
    @alkupaiva.setter
    def alkupaiva(self, val):
        '''Alkupäivän setteri'''
        if isinstance(val, str):
            self._alkupaiva = AikaIkkuna.aikaleima(val)
        elif isinstance(val, datetime.date):
            self._alkupaiva = val
        elif val is None:
            self._alkupaiva = val
        else:
            raise ValueError(f"Ei validi aikaleima {val}")

    @property
    def loppupaiva(self):
        '''Loppupäivän getteri'''
        return self._loppupaiva
    @loppupaiva.setter
    def loppupaiva(self, val):
        '''Loppupäivän setteri'''
        if isinstance(val, str):
            self._loppupaiva = AikaIkkuna.aikaleima(val)
        elif isinstance(val, datetime.date):
            self._loppupaiva = val
        elif val is None:
            self._loppupaiva = val
        else:
            raise ValueError(f"Ei validi aikaleima {val}")

    def __bool__(self):
        '''Tarkista onko aikaikkuna validi (alkupäivä ennen loppupäivää)'''
        if None in (self.alkupaiva, self.loppupaiva):
            return True
        return self.alkupaiva <= self.loppupaiva

    def __gt__(self, other):
        '''Tarkista onko aikaikkuna jälkeen toisen aikaikkunan.'''
        return self.alkupaiva > other.alkupaiva

    def __lt__(self, other):
        '''Tarkista onko aikaikkuna ennen toista aikaikkunaa.'''
        return self.loppupaiva < other.alkupaiva

    def __str__(self):
        '''Tekstirepresentaatio'''
        # Alkupäivä
        alku = (
            "*" if self.alkupaiva is None
            else self.alkupaiva.strftime("%Y-%m-%d")
        )
        loppu = (
            "*" if self.loppupaiva is None
            else self.loppupaiva.strftime("%Y-%m-%d")
        )
        return f"{alku} - {loppu}"

    def __iadd__(self, val):
        '''Siirrä aikaikkunaa tulevaisuuteen'''
        # int: Päivien verran
        if isinstance(val, int):
            offset = datetime.timedelta(days=val)
        # Suoraan aikamäärä
        elif isinstance(val, datetime.timedelta):
            offset = val
        else:
            raise ValueError(f"Epäkelpo tyyppi {type(val)}")
        if self.alkupaiva is not None:
            self.alkupaiva += offset
        if self.loppupaiva is not None:
            self.loppupaiva += offset

    def __isub__(self, val):
        '''Siirrä aikaikkunaa menneisyyteen'''
        # int: Päivien verran
        if isinstance(val, int):
            offset = datetime.timedelta(days=val)
        # Suoraan aikamäärä
        elif isinstance(val, datetime.timedelta):
            offset = val
        else:
            raise ValueError(f"Epäkelpo tyyppi {type(val)}")
        if self.alkupaiva is not None:
            self.alkupaiva -= offset
        if self.loppupaiva is not None:
            self.loppupaiva -= offset

    @staticmethod
    def aikaleima(aika_str):
        '''Muunna YYYY-mm-dd datetime-olioksi'''
        splitattu_aika = aika_str.split("-")
        muunnettu_aika = datetime.date(
            year=int(splitattu_aika[0]),
            month=int(splitattu_aika[1]),
            day=int(splitattu_aika[2]),
            )
        return muunnettu_aika

    def paivays_rajoissa(self, paivays):
        '''Tarkista onko päiväys aikaikkunan sisällä.
        Jos päiväys ikkunan sisällä, palauttaa True. Muutoin False.
        '''
        if not isinstance(paivays, datetime.date):
            pvm = datetime.date(paivays)
        else:
            pvm = paivays
        valid = True
        # Onko liian vanha?
        if self.alkupaiva is not None:
            valid = valid and pvm >= self.alkupaiva
        # Onko liian tuore?
        if self.loppupaiva is not None:
            valid = valid and pvm <= self.loppupaiva
        return valid


class KvartaaliIkkuna(AikaIkkuna):
    '''Erillinen luokka kvartaalien pyörittelyyn.'''
    def __init__(self, *args, **kwargs):
        '''Alustusfunktio
        Parametrit
        ----------
        kvartaali : int
            Kvartaalin numero (1,2,3,4)
        vuosi : int
            Minkä vuoden kvartaalista kyse.
        '''
        super().__init__()
        self._vuosi = None
        self._kvartaali = None
        # Kvartaalinumero, oletuksena nykyinen
        kvartaali = None
        if args:
            kvartaali = int(args[0])
        else:
            kvartaali = kwargs.get("kvartaali", None)
        self.kvartaali = (
            kvartaali
            if isinstance(kvartaali, int)
            else 1+(datetime.date.today().month//3)
            )
        # Minkä vuoden kvartaali, oletuksena nykyvuosi
        if len(args) > 1:
            vuosi = args[1]
        else:
            vuosi = kwargs.get("vuosi", None)
        self.vuosi = (
            vuosi
            if isinstance(vuosi, int)
            else datetime.date.today().year
            )

    @property
    def kvartaali(self):
        '''Kvartaalinumeron getteri'''
        return self._kvartaali
    @kvartaali.setter
    def kvartaali(self, val):
        '''Kvartaalinumeron setteri. Säätää samalla alku- ja loppupäivät jos mahdollista'''
        kvartaali = int(val)
        assert kvartaali in range(1,5), "Kvartaalinumeron oltava väliltä 1-4!"
        self._kvartaali = kvartaali
        # Aseta aikaikkuna kohdilleen
        self._alkupaiva = KvartaaliIkkuna.hae_alkupaiva(self._kvartaali, self._vuosi)
        self._loppupaiva = KvartaaliIkkuna.hae_loppupaiva(self._kvartaali, self._vuosi)
    
    @property
    def vuosi(self):
        '''Kvartaalinumeron getteri'''
        return self._kvartaali
    @vuosi.setter
    def vuosi(self, val):
        '''Kvartaalinumeron setteri. Säätää samalla alku- ja loppupäivät jos mahdollista'''
        self._kvartaali = int(val)
        # Aseta aikaikkuna kohdilleen
        self._alkupaiva = KvartaaliIkkuna.hae_alkupaiva(self._kvartaali, self._vuosi)
        self._loppupaiva = KvartaaliIkkuna.hae_loppupaiva(self._kvartaali, self._vuosi)

    @property
    def alkupaiva(self):
        '''Alkupäivän getteri'''
        return self._alkupaiva
    @alkupaiva.setter
    def alkupaiva(self, val):
        '''Alkupäivän setteri (kielletty)'''
        raise ValueError(f"Ei sallittu, säädetään kvartaalinumeroiden kautta")

    @property
    def loppupaiva(self):
        '''Loppupäivän getteri'''
        return self._loppupaiva
    @loppupaiva.setter
    def loppupaiva(self, val):
        '''Loppupäivän setteri (kielletty)'''
        raise ValueError(f"Ei sallittu, säädetään kvartaalinumeroiden kautta")

    @staticmethod
    def hae_alkupaiva(kvartaali, vuosi):
        if not isinstance(kvartaali, int):
            return None
        if not isinstance(vuosi, int):
            return None
        assert kvartaali in range(1,5), "Kvartaalinumeron oltava väliltä 1-4!"
        paivays = datetime.date(day=1, month=(kvartaali-1)*3+1, year=vuosi)
        return paivays
    @staticmethod
    def hae_loppupaiva(kvartaali, vuosi):
        if not isinstance(kvartaali, int):
            return None
        if not isinstance(vuosi, int):
            return None
        assert kvartaali in range(1,5), "Kvartaalinumeron oltava väliltä 1-4!"
        paivays = (
            datetime.date(day=1, month=((kvartaali-1)*3+4)%12, year=vuosi+(kvartaali==4))
            - datetime.timedelta(days=1)
        )
        return paivays