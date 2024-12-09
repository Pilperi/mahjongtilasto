import json
from src import parseri

def main():
    testipeli = [
        ("Pelaaja", 22.4),
        ("Toinen Pelaaja", 25.1),
        ("Kolmas Pelaaja", 24.9),
        ("Neljäs pelaaja", 27.6)
    ]
    parseri.lisaa_tulos_txt(testipeli, "./testitulos.txt")
    tulokset = parseri.parse_txt_dictiksi("./testitulos.txt")
    print(json.dumps(tulokset, indent=1))

if __name__ == "__main__":
    main()
