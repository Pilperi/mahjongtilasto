'''Translations for UI elements
'''
TRANSLATIONS = {}

# Yleistason tiedot
TRANSLATIONS["Application"] = {
    "FI": {
        "application_name": "Pisteidensyöttäjä",
    },
    "ENG": {
        "application_name": "Score logger",
    },
}
# UusiPelaaja-luokan UI-käännökset
TRANSLATIONS["UusiPelaaja"] = {
    "FI": {
        "title": "Lisää uusi pelaaja",
        "player_name": "Pelaajan nimi",
    },
    "ENG": {
        "title": "Add new player",
        "player_name": "Player name",
    },
    
}
# Paaikkuna-luokan UI-käännökset
TRANSLATIONS["Paaikkuna"] = {
    "FI": {
        "title": "Pisteidensyöttäjä",
        "save": "Tallenna",
        "player_east": "Pelaaja itä",
        "player_south": "Pelaaja etelä",
        "player_west": "Pelaaja länsi",
        "player_north": "Pelaaja pohjoinen",
        "select_result_file": "Valitse tulostiedosto",
        "file_types": "Tekstitiedostot (*.txt)",
        "saved": "Tallennettu",
        "statistics": "stats",
        "statistics.pointsum": "Pistesumma",
    },
    "ENG": {
        "title": "Score logger",
        "save": "Save",
        "player_east": "Player east",
        "player_south": "Player south",
        "player_west": "Player west",
        "player_north": "Player north",
        "select_result_file": "Select result file",
        "file_types": "Text files (*.txt)",
        "saved": "Saved",
        "statistics": "stats",
        "statistics.pointsum": "Point sum",
    },
    
}
TRANSLATIONS["TulosTilastot"] = {
    "FI": {
        "title": "Pelistatistiikat",
        "time_selection": ["Kaikki", "6 kk", "3 kk", "1 kk"],
        "headers": ["Nimi", "Pisteet", "Uma", "Yht.", "Pelejä", "Per peli"],
    },
    "ENG": {
        "title": "Statistics",
        "time_selection": ["All", "6 months", "3 months", "1 month"],
        "headers": ["Name", "Points", "Uma", "Total", "Games", "Per game"],
    }
}