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
        self.alkupaiva = (
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
        self.loppupaiva = (
            AikaIkkuna.aikaleima(loppuaika)
            if isinstance(loppuaika, str)
            else loppuaika
            )
        # Jos rajat asetettiin, tarkista että ne käy järkeen
        if not self:
            raise ValueError("Alkupäivä ei voi olla loppupäivän jälkeen!")

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
