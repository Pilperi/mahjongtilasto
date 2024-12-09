import random
import json
from src import parseri

def generoi_pelitulos(nimet):
    tulos = [None for i in range(4)]
    pisteita = 4*25_000
    for pind,pelaaja in enumerate(nimet):
        if pind != 3:
            pisteet = 100*random.randint(-120, 687)
            pisteita -= pisteet
        else:
            pisteet = pisteita
        tulos[pind] = (pelaaja, pisteet)
    assert sum(tls[1] for tls in tulos) == 4*25_000
    return tulos

def main():
    nimet = [f"Pelaaja {ind+1:d}" for ind in range(10)]
    peleja = 37
    for i in range(peleja):
        aikaleima = f"2024-12-10-00-42-{i:02d}"
        pelaajat = random.sample(nimet, 4)
        testipeli = generoi_pelitulos(pelaajat)
        parseri.lisaa_tulos_txt(testipeli, "./testitulos.txt", aikaleima)
    tulokset = parseri.parse_txt_dictiksi("./testitulos.txt")
    print(json.dumps(tulokset, indent=1))

if __name__ == "__main__":
    main()
