"""Per-country and per-region configuration used by every pipeline step.
City lat/lon are fetched from GeoNames.
Each region dict maps a short region code to {name, region, lat, lon, is_capital}.
COUNTRIES is the single source of truth that every other script imports.

One point per administrative region, always at that region's administrative
center, never at its largest city where the two differ.

Where a region is administered from the national capital and that capital is a
separate unit, the capital itself is used rather than a substitute inside the
region. That applies to CZ Central Bohemia, HU Pest, BG Sofia Province and
NO Akershus, so Prague, Budapest, Sofia and Oslo are each sampled twice within
their country. Regions with a shared or split seat are flagged on the entry.

Romania is the one market with no administrative center to use: its 8 units are
NUTS-2 statistical regions with no legal seat, so each point is the region's
principal city.

Every country block covers the full partition; the source for each country's
division is the Wikipedia link above it.
"""

# https://en.wikipedia.org/wiki/Voivodeships_of_Poland
POLAND_VOIVODESHIP = {
    "waw": {"name": "Warsaw",              "region": "Masovian Voivodeship",            "lat":  52.2298, "lon":   21.0118, "is_capital": True},
    "wro": {"name": "Wrocław",             "region": "Lower Silesian Voivodeship",      "lat":  51.1029, "lon":   17.0301, "is_capital": False},
    "ldz": {"name": "Łódź",                "region": "Łódź Voivodeship",                "lat":  51.7706, "lon":   19.4739, "is_capital": False},
    "krk": {"name": "Kraków",              "region": "Lesser Poland Voivodeship",       "lat":  50.0614, "lon":   19.9366, "is_capital": False},
    "ktw": {"name": "Katowice",            "region": "Silesian Voivodeship",            "lat":  50.2597, "lon":   19.0217, "is_capital": False},
    "gdn": {"name": "Gdańsk",              "region": "Pomeranian Voivodeship",          "lat":  54.3523, "lon":   18.6491, "is_capital": False},
    "poz": {"name": "Poznań",              "region": "Greater Poland Voivodeship",      "lat":  52.4069, "lon":   16.9299, "is_capital": False},
    "szz": {"name": "Szczecin",            "region": "West Pomeranian Voivodeship",     "lat":  53.4289, "lon":   14.5530, "is_capital": False},
    "lub": {"name": "Lublin",              "region": "Lublin Voivodeship",              "lat":  51.2506, "lon":   22.5701, "is_capital": False},
    "rzs": {"name": "Rzeszów",             "region": "Subcarpathian Voivodeship",       "lat":  50.0413, "lon":   21.9990, "is_capital": False},
    "klc": {"name": "Kielce",              "region": "Świętokrzyskie Voivodeship",      "lat":  50.8703, "lon":   20.6275, "is_capital": False},
    "bst": {"name": "Białystok",           "region": "Podlaskie Voivodeship",           "lat":  53.1333, "lon":   23.1643, "is_capital": False},
    "ols": {"name": "Olsztyn",             "region": "Warmian-Masurian Voivodeship",    "lat":  53.7838, "lon":   20.4927, "is_capital": False},
    "bgz": {"name": "Bydgoszcz",           "region": "Kuyavian-Pomeranian Voivodeship", "lat":  53.1235, "lon":   18.0076, "is_capital": False},   # seat of the voivode; Toruń seats the sejmik
    "zgo": {"name": "Gorzów Wielkopolski", "region": "Lubusz Voivodeship",              "lat":  52.7337, "lon":   15.2250, "is_capital": False},   # seat of the voivode; Zielona Góra seats the sejmik
    "opo": {"name": "Opole",               "region": "Opole Voivodeship",               "lat":  50.6712, "lon":   17.9260, "is_capital": False},
}

# https://en.wikipedia.org/wiki/States_of_Germany
GERMANY_LAENDER = {
    "bw": {"name": "Stuttgart",   "region": "Baden-Württemberg",      "lat":  48.7823, "lon":    9.1770, "is_capital": False},
    "by": {"name": "Munich",      "region": "Bavaria",                "lat":  48.1374, "lon":   11.5755, "is_capital": False},
    "be": {"name": "Berlin",      "region": "Berlin",                 "lat":  52.5244, "lon":   13.4105, "is_capital": True},
    "bb": {"name": "Potsdam",     "region": "Brandenburg",            "lat":  52.3989, "lon":   13.0657, "is_capital": False},
    "hb": {"name": "Bremen",      "region": "Bremen",                 "lat":  53.0758, "lon":    8.8072, "is_capital": False},
    "hh": {"name": "Hamburg",     "region": "Hamburg",                "lat":  53.5507, "lon":    9.9930, "is_capital": False},
    "he": {"name": "Wiesbaden",   "region": "Hesse",                  "lat":  50.0860, "lon":    8.2444, "is_capital": False},
    "ni": {"name": "Hanover",     "region": "Lower Saxony",           "lat":  52.3705, "lon":    9.7332, "is_capital": False},
    "mv": {"name": "Schwerin",    "region": "Mecklenburg-Vorpommern", "lat":  53.6294, "lon":   11.4132, "is_capital": False},
    "nw": {"name": "Düsseldorf",  "region": "North Rhine-Westphalia", "lat":  51.2217, "lon":    6.7762, "is_capital": False},
    "rp": {"name": "Mainz",       "region": "Rhineland-Palatinate",   "lat":  49.9819, "lon":    8.2801, "is_capital": False},
    "sl": {"name": "Saarbrücken", "region": "Saarland",               "lat":  49.2326, "lon":    7.0098, "is_capital": False},
    "sn": {"name": "Dresden",     "region": "Saxony",                 "lat":  51.0509, "lon":   13.7383, "is_capital": False},
    "st": {"name": "Magdeburg",   "region": "Saxony-Anhalt",          "lat":  52.1313, "lon":   11.6319, "is_capital": False},
    "sh": {"name": "Kiel",        "region": "Schleswig-Holstein",     "lat":  54.3213, "lon":   10.1349, "is_capital": False},
    "th": {"name": "Erfurt",      "region": "Thuringia",              "lat":  50.9773, "lon":   11.0354, "is_capital": False},
}

# https://en.wikipedia.org/wiki/Regions_of_Finland
FINLAND_REGIONS = {
    "uu": {"name": "Helsinki",     "region": "Uusimaa",              "lat":  60.1695, "lon":   24.9354, "is_capital": True},
    "vs": {"name": "Turku",        "region": "Varsinais-Suomi",      "lat":  60.4515, "lon":   22.2687, "is_capital": False},
    "sk": {"name": "Pori",         "region": "Satakunta",            "lat":  61.4807, "lon":   21.7852, "is_capital": False},
    "kh": {"name": "Hämeenlinna",  "region": "Kanta-Häme",           "lat":  60.9960, "lon":   24.4643, "is_capital": False},
    "pm": {"name": "Tampere",      "region": "Pirkanmaa",            "lat":  61.4991, "lon":   23.7871, "is_capital": False},
    "ph": {"name": "Lahti",        "region": "Päijät-Häme",          "lat":  60.9827, "lon":   25.6615, "is_capital": False},
    "ky": {"name": "Kouvola",      "region": "Kymenlaakso",          "lat":  60.8667, "lon":   26.7000, "is_capital": False},   # administrative center; Kotka is the official regional center
    "ek": {"name": "Lappeenranta", "region": "South Karelia",        "lat":  61.0587, "lon":   28.1887, "is_capital": False},
    "es": {"name": "Mikkeli",      "region": "South Savo",           "lat":  61.6886, "lon":   27.2723, "is_capital": False},
    "ps": {"name": "Kuopio",       "region": "North Savo",           "lat":  62.8924, "lon":   27.6770, "is_capital": False},
    "pk": {"name": "Joensuu",      "region": "North Karelia",        "lat":  62.6012, "lon":   29.7632, "is_capital": False},
    "ks": {"name": "Jyväskylä",    "region": "Central Finland",      "lat":  62.2415, "lon":   25.7209, "is_capital": False},
    "ep": {"name": "Seinäjoki",    "region": "South Ostrobothnia",   "lat":  62.7945, "lon":   22.8282, "is_capital": False},
    "po": {"name": "Vaasa",        "region": "Ostrobothnia",         "lat":  63.0960, "lon":   21.6158, "is_capital": False},
    "kp": {"name": "Kokkola",      "region": "Central Ostrobothnia", "lat":  63.8385, "lon":   23.1307, "is_capital": False},
    "pp": {"name": "Oulu",         "region": "North Ostrobothnia",   "lat":  65.0124, "lon":   25.4682, "is_capital": False},
    "ka": {"name": "Kajaani",      "region": "Kainuu",               "lat":  64.2273, "lon":   27.7285, "is_capital": False},
    "la": {"name": "Rovaniemi",    "region": "Lapland",              "lat":  66.4990, "lon":   25.6887, "is_capital": False},
}

# https://en.wikipedia.org/wiki/Regions_of_Italy
ITALY_REGIONS = {
    "vda": {"name": "Aosta",      "region": "Valle d'Aosta",         "lat":  45.7376, "lon":    7.3172, "is_capital": False},
    "pie": {"name": "Turin",      "region": "Piedmont",              "lat":  45.0705, "lon":    7.6868, "is_capital": False},
    "lig": {"name": "Genoa",      "region": "Liguria",               "lat":  44.4048, "lon":    8.9444, "is_capital": False},
    "lom": {"name": "Milan",      "region": "Lombardy",              "lat":  45.4643, "lon":    9.1895, "is_capital": False},
    "taa": {"name": "Trento",     "region": "Trentino-Alto Adige",   "lat":  46.0679, "lon":   11.1211, "is_capital": False},
    "ven": {"name": "Venice",     "region": "Veneto",                "lat":  45.4371, "lon":   12.3326, "is_capital": False},
    "fvg": {"name": "Trieste",    "region": "Friuli-Venezia Giulia", "lat":  45.6495, "lon":   13.7768, "is_capital": False},
    "emr": {"name": "Bologna",    "region": "Emilia-Romagna",        "lat":  44.4938, "lon":   11.3387, "is_capital": False},
    "tos": {"name": "Florence",   "region": "Tuscany",               "lat":  43.7792, "lon":   11.2463, "is_capital": False},
    "mar": {"name": "Ancona",     "region": "Marche",                "lat":  43.6072, "lon":   13.5103, "is_capital": False},
    "umb": {"name": "Perugia",    "region": "Umbria",                "lat":  43.1122, "lon":   12.3888, "is_capital": False},
    "laz": {"name": "Rome",       "region": "Lazio",                 "lat":  41.8919, "lon":   12.5113, "is_capital": True},
    "abr": {"name": "L'Aquila",   "region": "Abruzzo",               "lat":  42.3505, "lon":   13.3995, "is_capital": False},
    "mol": {"name": "Campobasso", "region": "Molise",                "lat":  41.5595, "lon":   14.6674, "is_capital": False},
    "cam": {"name": "Naples",     "region": "Campania",              "lat":  40.8522, "lon":   14.2681, "is_capital": False},
    "bas": {"name": "Potenza",    "region": "Basilicata",            "lat":  40.6418, "lon":   15.8079, "is_capital": False},
    "pug": {"name": "Bari",       "region": "Puglia",                "lat":  41.1207, "lon":   16.8698, "is_capital": False},
    "cal": {"name": "Catanzaro",  "region": "Calabria",              "lat":  38.8825, "lon":   16.6009, "is_capital": False},
    "sic": {"name": "Palermo",    "region": "Sicily",                "lat":  38.1166, "lon":   13.3636, "is_capital": False},
    "sar": {"name": "Cagliari",   "region": "Sardinia",              "lat":  39.2305, "lon":    9.1192, "is_capital": False},
}

# https://en.wikipedia.org/wiki/Districts_of_Portugal
# https://en.wikipedia.org/wiki/Autonomous_regions_of_Portugal
# 18 mainland districts sampled. The 2 autonomous regions are commented out at
# the end of this block: they are isolated microgrids run by EEM and EDA under
# the Regional Governments, so their demand is not in REN's control area and
# not in the ENTSO-E PT load we forecast. They also sat outside the ECMWF
# download box, so they were sampling open ocean rather than the islands.
PORTUGAL_DISTRICTS = {
    "lsb": {"name": "Lisbon",           "region": "Lisboa",           "lat":  38.7251, "lon":   -9.1498, "is_capital": True},
    "prt": {"name": "Porto",            "region": "Porto",            "lat":  41.1485, "lon":   -8.6110, "is_capital": False},
    "brg": {"name": "Braga",            "region": "Braga",            "lat":  41.5514, "lon":   -8.4231, "is_capital": False},
    "set": {"name": "Setúbal",          "region": "Setúbal",          "lat":  38.5244, "lon":   -8.8882, "is_capital": False},
    "cmb": {"name": "Coimbra",          "region": "Coimbra",          "lat":  40.2069, "lon":   -8.4200, "is_capital": False},
    "avr": {"name": "Aveiro",           "region": "Aveiro",           "lat":  40.6457, "lon":   -8.6464, "is_capital": False},
    "lei": {"name": "Leiria",           "region": "Leiria",           "lat":  39.7436, "lon":   -8.8071, "is_capital": False},
    "san": {"name": "Santarém",         "region": "Santarém",         "lat":  39.2338, "lon":   -8.6862, "is_capital": False},
    "evr": {"name": "Évora",            "region": "Évora",            "lat":  38.5659, "lon":   -7.9040, "is_capital": False},
    "bja": {"name": "Beja",             "region": "Beja",             "lat":  38.0147, "lon":   -7.8628, "is_capital": False},
    "fro": {"name": "Faro",             "region": "Faro",             "lat":  37.0187, "lon":   -7.9272, "is_capital": False},
    "via": {"name": "Viana do Castelo", "region": "Viana do Castelo", "lat":  41.6932, "lon":   -8.8329, "is_capital": False},
    "vlr": {"name": "Vila Real",        "region": "Vila Real",        "lat":  41.3001, "lon":   -7.7432, "is_capital": False},
    "vis": {"name": "Viseu",            "region": "Viseu",            "lat":  40.6617, "lon":   -7.9090, "is_capital": False},
    "ctb": {"name": "Castelo Branco",   "region": "Castelo Branco",   "lat":  39.8236, "lon":   -7.4910, "is_capital": False},
    "gua": {"name": "Guarda",           "region": "Guarda",           "lat":  40.5375, "lon":   -7.2663, "is_capital": False},
    "ptl": {"name": "Portalegre",       "region": "Portalegre",       "lat":  39.2938, "lon":   -7.4312, "is_capital": False},
    "bgc": {"name": "Bragança",         "region": "Bragança",         "lat":  41.8072, "lon":   -6.7590, "is_capital": False},
    # Disabled 2026-07-27. Outside REN's control area (EEM / EDA isolated
    # microgrids) AND outside the 1a AREA box, so 1b bound them to open-ocean
    # cells 180 km and 938 km away: mean diurnal 2t range 0.79 K and 0.88 K vs
    # 6-9 K at every mainland point. Removing them also improves the
    # temperature-load correlation (+2.5% on the daily max). See
    # region_grid_coverage.md.
    # "fnc": {"name": "Funchal",          "region": "Madeira",           "lat":  32.6657, "lon":  -16.9255, "is_capital": False},
    # "pdl": {"name": "Ponta Delgada",    "region": "Azores",            "lat":  37.7395, "lon":  -25.6687, "is_capital": False},
}

# https://en.wikipedia.org/wiki/Regions_of_France
FRANCE_REGIONS = {
    "idf": {"name": "Paris",      "region": "Île-de-France",              "lat":  48.8534, "lon":    2.3488, "is_capital": True},
    "ara": {"name": "Lyon",       "region": "Auvergne-Rhône-Alpes",       "lat":  45.7491, "lon":    4.8479, "is_capital": False},
    "pac": {"name": "Marseille",  "region": "Provence-Alpes-Côte d'Azur", "lat":  43.2970, "lon":    5.3811, "is_capital": False},
    "occ": {"name": "Toulouse",   "region": "Occitanie",                  "lat":  43.6043, "lon":    1.4437, "is_capital": False},
    "naq": {"name": "Bordeaux",   "region": "Nouvelle-Aquitaine",         "lat":  44.8412, "lon":   -0.5805, "is_capital": False},
    "hdf": {"name": "Lille",      "region": "Hauts-de-France",            "lat":  50.6339, "lon":    3.0551, "is_capital": False},
    "ges": {"name": "Strasbourg", "region": "Grand Est",                  "lat":  48.5839, "lon":    7.7455, "is_capital": False},
    "pdl": {"name": "Nantes",     "region": "Pays de la Loire",           "lat":  47.2172, "lon":   -1.5534, "is_capital": False},
    "nor": {"name": "Rouen",      "region": "Normandy",                   "lat":  49.4431, "lon":    1.0993, "is_capital": False},   # two prefectures: Caen and Rouen
    "bre": {"name": "Rennes",     "region": "Brittany",                   "lat":  48.1111, "lon":   -1.6743, "is_capital": False},
    "bfc": {"name": "Dijon",      "region": "Bourgogne-Franche-Comté",    "lat":  47.3134, "lon":    5.0139, "is_capital": False},   # two prefectures: Besançon and Dijon
    "cvl": {"name": "Orléans",    "region": "Centre-Val de Loire",        "lat":  47.9025, "lon":    1.9041, "is_capital": False},
    "cor": {"name": "Ajaccio",    "region": "Corsica",                    "lat":  41.9189, "lon":    8.7381, "is_capital": False},
}

# https://en.wikipedia.org/wiki/Autonomous_communities_of_Spain
SPAIN_COMMUNITIES = {
    "mad": {"name": "Madrid",                 "region": "Community of Madrid", "lat":  40.4165, "lon":   -3.7026, "is_capital": True},
    "cat": {"name": "Barcelona",              "region": "Catalonia",           "lat":  41.3888, "lon":    2.1590, "is_capital": False},
    "and": {"name": "Seville",                "region": "Andalusia",           "lat":  37.3828, "lon":   -5.9732, "is_capital": False},
    "val": {"name": "Valencia",               "region": "Valencian Community", "lat":  39.4739, "lon":   -0.3797, "is_capital": False},
    "gal": {"name": "Santiago de Compostela", "region": "Galicia",             "lat":  42.8805, "lon":   -8.5457, "is_capital": False},
    "cle": {"name": "Valladolid",             "region": "Castile and León",    "lat":  41.6554, "lon":   -4.7235, "is_capital": False},
    "pvb": {"name": "Vitoria-Gasteiz",        "region": "Basque Country",      "lat":  42.8500, "lon":   -2.6727, "is_capital": False},
    "clm": {"name": "Toledo",                 "region": "Castilla-La Mancha",  "lat":  39.8581, "lon":   -4.0226, "is_capital": False},
    "can": {"name": "Las Palmas",             "region": "Canary Islands",      "lat":  28.1018, "lon":  -15.4157, "is_capital": False},   # two co-capitals: Las Palmas and Santa Cruz de Tenerife
    "arn": {"name": "Zaragoza",               "region": "Aragon",              "lat":  41.6561, "lon":   -0.8773, "is_capital": False},
    "mur": {"name": "Murcia",                 "region": "Region of Murcia",    "lat":  37.9870, "lon":   -1.1300, "is_capital": False},
    "ast": {"name": "Oviedo",                 "region": "Asturias",            "lat":  43.3603, "lon":   -5.8448, "is_capital": False},
    "nav": {"name": "Pamplona",               "region": "Navarre",             "lat":  42.8169, "lon":   -1.6432, "is_capital": False},
    "ext": {"name": "Mérida",                 "region": "Extremadura",         "lat":  38.9180, "lon":   -6.3429, "is_capital": False},
    "cnt": {"name": "Santander",              "region": "Cantabria",           "lat":  43.4659, "lon":   -3.8049, "is_capital": False},
    "rio": {"name": "Logroño",                "region": "La Rioja",            "lat":  42.4661, "lon":   -2.4512, "is_capital": False},
    "bal": {"name": "Palma",                  "region": "Balearic Islands",    "lat":  39.5694, "lon":    2.6502, "is_capital": False},
}

# https://en.wikipedia.org/wiki/Provinces_of_the_Netherlands
NETHERLANDS_PROVINCES = {
    "nh": {"name": "Amsterdam",        "region": "North Holland", "lat":  52.3740, "lon":    4.8897, "is_capital": True},   # provincial capital is Haarlem, but the national capital lies in this province
    "zh": {"name": "The Hague",        "region": "South Holland", "lat":  52.0767, "lon":    4.2986, "is_capital": False},
    "ut": {"name": "Utrecht",          "region": "Utrecht",       "lat":  52.0908, "lon":    5.1222, "is_capital": False},
    "nb": {"name": "'s-Hertogenbosch", "region": "North Brabant", "lat":  51.6992, "lon":    5.3042, "is_capital": False},
    "ge": {"name": "Arnhem",           "region": "Gelderland",    "lat":  51.9800, "lon":    5.9111, "is_capital": False},
    "ov": {"name": "Zwolle",           "region": "Overijssel",    "lat":  52.5125, "lon":    6.0944, "is_capital": False},
    "li": {"name": "Maastricht",       "region": "Limburg",       "lat":  50.8483, "lon":    5.6889, "is_capital": False},
    "fr": {"name": "Leeuwarden",       "region": "Friesland",     "lat":  53.2027, "lon":    5.8097, "is_capital": False},
    "gr": {"name": "Groningen",        "region": "Groningen",     "lat":  53.2192, "lon":    6.5667, "is_capital": False},
    "dr": {"name": "Assen",            "region": "Drenthe",       "lat":  52.9967, "lon":    6.5625, "is_capital": False},
    "fl": {"name": "Lelystad",         "region": "Flevoland",     "lat":  52.5083, "lon":    5.4750, "is_capital": False},
    "ze": {"name": "Middelburg",       "region": "Zeeland",       "lat":  51.5000, "lon":    3.6139, "is_capital": False},
}

# https://en.wikipedia.org/wiki/Provinces_of_Belgium
BELGIUM_PROVINCES = {
    "bru": {"name": "Brussels", "region": "Brussels-Capital", "lat":  50.8505, "lon":    4.3488, "is_capital": True},
    "ant": {"name": "Antwerp",  "region": "Antwerp",          "lat":  51.2205, "lon":    4.4003, "is_capital": False},
    "ovl": {"name": "Ghent",    "region": "East Flanders",    "lat":  51.0500, "lon":    3.7167, "is_capital": False},
    "wvl": {"name": "Bruges",   "region": "West Flanders",    "lat":  51.2089, "lon":    3.2242, "is_capital": False},
    "vbr": {"name": "Leuven",   "region": "Flemish Brabant",  "lat":  50.8796, "lon":    4.7009, "is_capital": False},
    "lim": {"name": "Hasselt",  "region": "Limburg (BE)",     "lat":  50.9311, "lon":    5.3378, "is_capital": False},
    "hai": {"name": "Mons",     "region": "Hainaut",          "lat":  50.4541, "lon":    3.9523, "is_capital": False},
    "lie": {"name": "Liège",    "region": "Liège",            "lat":  50.6337, "lon":    5.5675, "is_capital": False},
    "nam": {"name": "Namur",    "region": "Namur",            "lat":  50.4669, "lon":    4.8675, "is_capital": False},
    "lux": {"name": "Arlon",    "region": "Luxembourg (BE)",  "lat":  49.6833, "lon":    5.8167, "is_capital": False},
    "wbr": {"name": "Wavre",    "region": "Walloon Brabant",  "lat":  50.7172, "lon":    4.6014, "is_capital": False},
}

# https://en.wikipedia.org/wiki/States_of_Austria
AUSTRIA_STATES = {
    "w":  {"name": "Vienna",     "region": "Vienna",        "lat":  48.2085, "lon":   16.3721, "is_capital": True},
    "no": {"name": "St. Pölten", "region": "Lower Austria", "lat":  48.2076, "lon":   15.6372, "is_capital": False},
    "oo": {"name": "Linz",       "region": "Upper Austria", "lat":  48.3064, "lon":   14.2861, "is_capital": False},
    "st": {"name": "Graz",       "region": "Styria",        "lat":  47.0673, "lon":   15.4420, "is_capital": False},
    "t":  {"name": "Innsbruck",  "region": "Tyrol",         "lat":  47.2627, "lon":   11.3945, "is_capital": False},
    "k":  {"name": "Klagenfurt", "region": "Carinthia",     "lat":  46.6247, "lon":   14.3053, "is_capital": False},
    "s":  {"name": "Salzburg",   "region": "Salzburg",      "lat":  47.7994, "lon":   13.0440, "is_capital": False},
    "v":  {"name": "Bregenz",    "region": "Vorarlberg",    "lat":  47.5031, "lon":    9.7471, "is_capital": False},
    "b":  {"name": "Eisenstadt", "region": "Burgenland",    "lat":  47.8456, "lon":   16.5233, "is_capital": False},
}

# https://en.wikipedia.org/wiki/Cantons_of_Switzerland
SWITZERLAND_CANTONS = {
    "be": {"name": "Bern",         "region": "Bern",                   "lat":  46.9481, "lon":    7.4474, "is_capital": True},
    "zh": {"name": "Zurich",       "region": "Zürich",                 "lat":  47.3667, "lon":    8.5500, "is_capital": False},
    "ge": {"name": "Geneva",       "region": "Geneva",                 "lat":  46.2022, "lon":    6.1457, "is_capital": False},
    "vd": {"name": "Lausanne",     "region": "Vaud",                   "lat":  46.5160, "lon":    6.6328, "is_capital": False},
    "bs": {"name": "Basel",        "region": "Basel-Stadt",            "lat":  47.5584, "lon":    7.5733, "is_capital": False},
    "lu": {"name": "Lucerne",      "region": "Lucerne",                "lat":  47.0505, "lon":    8.3064, "is_capital": False},
    "sg": {"name": "St. Gallen",   "region": "St. Gallen",             "lat":  47.4239, "lon":    9.3748, "is_capital": False},
    "ti": {"name": "Bellinzona",   "region": "Ticino",                 "lat":  46.1928, "lon":    9.0170, "is_capital": False},
    "vs": {"name": "Sion",         "region": "Valais",                 "lat":  46.2274, "lon":    7.3556, "is_capital": False},
    "gr": {"name": "Chur",         "region": "Graubünden",             "lat":  46.8499, "lon":    9.5329, "is_capital": False},
    "ag": {"name": "Aarau",        "region": "Aargau",                 "lat":  47.3925, "lon":    8.0442, "is_capital": False},
    "tg": {"name": "Frauenfeld",   "region": "Thurgau",                "lat":  47.5578, "lon":    8.8989, "is_capital": False},
    "ne": {"name": "Neuchâtel",    "region": "Neuchâtel",              "lat":  46.9918, "lon":    6.9310, "is_capital": False},
    "fr": {"name": "Fribourg",     "region": "Fribourg",               "lat":  46.8024, "lon":    7.1513, "is_capital": False},
    "so": {"name": "Solothurn",    "region": "Solothurn",              "lat":  47.2079, "lon":    7.5371, "is_capital": False},
    "sh": {"name": "Schaffhausen", "region": "Schaffhausen",           "lat":  47.6973, "lon":    8.6349, "is_capital": False},
    "ur": {"name": "Altdorf",      "region": "Uri",                    "lat":  46.8804, "lon":    8.6444, "is_capital": False},
    "sz": {"name": "Schwyz",       "region": "Schwyz",                 "lat":  47.0208, "lon":    8.6541, "is_capital": False},
    "ow": {"name": "Sarnen",       "region": "Obwalden",               "lat":  46.8961, "lon":    8.2453, "is_capital": False},
    "nw": {"name": "Stans",        "region": "Nidwalden",              "lat":  46.9581, "lon":    8.3661, "is_capital": False},
    "gl": {"name": "Glarus",       "region": "Glarus",                 "lat":  47.0406, "lon":    9.0680, "is_capital": False},
    "zg": {"name": "Zug",          "region": "Zug",                    "lat":  47.1724, "lon":    8.5175, "is_capital": False},
    "bl": {"name": "Liestal",      "region": "Basel-Landschaft",       "lat":  47.4845, "lon":    7.7345, "is_capital": False},
    "ar": {"name": "Herisau",      "region": "Appenzell Ausserrhoden", "lat":  47.3862, "lon":    9.2792, "is_capital": False},   # Herisau is the seat of government; Trogen is the judicial seat
    "ai": {"name": "Appenzell",    "region": "Appenzell Innerrhoden",  "lat":  47.3310, "lon":    9.4100, "is_capital": False},
    "ju": {"name": "Delémont",     "region": "Jura",                   "lat":  47.3649, "lon":    7.3445, "is_capital": False},
}

# https://en.wikipedia.org/wiki/Regions_of_the_Czech_Republic
CZECHIA_REGIONS = {
    "pr": {"name": "Prague",           "region": "Prague",            "lat":  50.0880, "lon":   14.4208, "is_capital": True},
    "st": {"name": "Prague",           "region": "Central Bohemia",   "lat":  50.0880, "lon":   14.4208, "is_capital": False},   # seated in Prague, which lies outside the region
    "jc": {"name": "České Budějovice", "region": "South Bohemia",     "lat":  48.9745, "lon":   14.4743, "is_capital": False},
    "pl": {"name": "Plzeň",            "region": "Plzeň",             "lat":  49.7475, "lon":   13.3776, "is_capital": False},
    "ka": {"name": "Karlovy Vary",     "region": "Karlovy Vary",      "lat":  50.2327, "lon":   12.8712, "is_capital": False},
    "us": {"name": "Ústí nad Labem",   "region": "Ústí nad Labem",    "lat":  50.6607, "lon":   14.0323, "is_capital": False},
    "li": {"name": "Liberec",          "region": "Liberec",           "lat":  50.7671, "lon":   15.0562, "is_capital": False},
    "hk": {"name": "Hradec Králové",   "region": "Hradec Králové",    "lat":  50.2092, "lon":   15.8328, "is_capital": False},
    "pa": {"name": "Pardubice",        "region": "Pardubice",         "lat":  50.0408, "lon":   15.7766, "is_capital": False},
    "vy": {"name": "Jihlava",          "region": "Vysočina",          "lat":  49.3961, "lon":   15.5912, "is_capital": False},
    "jm": {"name": "Brno",             "region": "South Moravia",     "lat":  49.1952, "lon":   16.6080, "is_capital": False},
    "ol": {"name": "Olomouc",          "region": "Olomouc",           "lat":  49.5955, "lon":   17.2518, "is_capital": False},
    "zl": {"name": "Zlín",             "region": "Zlín",              "lat":  49.2264, "lon":   17.6706, "is_capital": False},
    "ms": {"name": "Ostrava",          "region": "Moravian-Silesian", "lat":  49.8347, "lon":   18.2820, "is_capital": False},
}

# https://en.wikipedia.org/wiki/Regions_of_Slovakia
SLOVAKIA_REGIONS = {
    "ba": {"name": "Bratislava",      "region": "Bratislava",      "lat":  48.1482, "lon":   17.1067, "is_capital": True},
    "tt": {"name": "Trnava",          "region": "Trnava",          "lat":  48.3777, "lon":   17.5860, "is_capital": False},
    "tn": {"name": "Trenčín",         "region": "Trenčín",         "lat":  48.8945, "lon":   18.0444, "is_capital": False},
    "nr": {"name": "Nitra",           "region": "Nitra",           "lat":  48.3076, "lon":   18.0845, "is_capital": False},
    "za": {"name": "Žilina",          "region": "Žilina",          "lat":  49.2231, "lon":   18.7394, "is_capital": False},
    "bb": {"name": "Banská Bystrica", "region": "Banská Bystrica", "lat":  48.7395, "lon":   19.1493, "is_capital": False},
    "po": {"name": "Prešov",          "region": "Prešov",          "lat":  48.9992, "lon":   21.2355, "is_capital": False},
    "ke": {"name": "Košice",          "region": "Košice",          "lat":  48.7144, "lon":   21.2580, "is_capital": False},
}

# https://en.wikipedia.org/wiki/Counties_of_Hungary
HUNGARY_COUNTIES = {
    "bu": {"name": "Budapest",       "region": "Budapest",               "lat":  47.4984, "lon":   19.0404, "is_capital": True},
    "de": {"name": "Debrecen",       "region": "Hajdú-Bihar",            "lat":  47.5317, "lon":   21.6244, "is_capital": False},
    "sz": {"name": "Szeged",         "region": "Csongrád-Csanád",        "lat":  46.2530, "lon":   20.1482, "is_capital": False},
    "mi": {"name": "Miskolc",        "region": "Borsod-Abaúj-Zemplén",   "lat":  48.1033, "lon":   20.7781, "is_capital": False},
    "pe": {"name": "Pécs",           "region": "Baranya",                "lat":  46.0762, "lon":   18.2281, "is_capital": False},
    "gy": {"name": "Győr",           "region": "Győr-Moson-Sopron",      "lat":  47.6833, "lon":   17.6351, "is_capital": False},
    "ny": {"name": "Nyíregyháza",    "region": "Szabolcs-Szatmár-Bereg", "lat":  47.9554, "lon":   21.7167, "is_capital": False},
    "ke": {"name": "Kecskemét",      "region": "Bács-Kiskun",            "lat":  46.9062, "lon":   19.6913, "is_capital": False},
    "sf": {"name": "Székesfehérvár", "region": "Fejér",                  "lat":  47.1900, "lon":   18.4103, "is_capital": False},
    "sb": {"name": "Szombathely",    "region": "Vas",                    "lat":  47.2309, "lon":   16.6215, "is_capital": False},
    "ka": {"name": "Kaposvár",       "region": "Somogy",                 "lat":  46.3667, "lon":   17.8000, "is_capital": False},
    "eg": {"name": "Eger",           "region": "Heves",                  "lat":  47.9027, "lon":   20.3733, "is_capital": False},
    "ta": {"name": "Tatabánya",      "region": "Komárom-Esztergom",      "lat":  47.5925, "lon":   18.3810, "is_capital": False},
    "za": {"name": "Zalaegerszeg",   "region": "Zala",                   "lat":  46.8370, "lon":   16.8440, "is_capital": False},
    "pt": {"name": "Budapest",       "region": "Pest",                   "lat":  47.4984, "lon":   19.0404, "is_capital": False},   # seated in Budapest, a separate unit
    "no": {"name": "Salgótarján",    "region": "Nógrád",                 "lat":  48.0987, "lon":   19.8030, "is_capital": False},
    "js": {"name": "Szolnok",        "region": "Jász-Nagykun-Szolnok",   "lat":  47.1807, "lon":   20.1984, "is_capital": False},
    "bk": {"name": "Békéscsaba",     "region": "Békés",                  "lat":  46.6833, "lon":   21.1000, "is_capital": False},
    "to": {"name": "Szekszárd",      "region": "Tolna",                  "lat":  46.3472, "lon":   18.7119, "is_capital": False},
    "ve": {"name": "Veszprém",       "region": "Veszprém",               "lat":  47.0933, "lon":   17.9115, "is_capital": False},
}

# https://en.wikipedia.org/wiki/Development_regions_of_Romania
# NUTS-2 statistical regions with no legal seat; each point is the region's principal city
ROMANIA_REGIONS = {
    "b":  {"name": "Bucharest",   "region": "Bucharest-Ilfov",  "lat":  44.4323, "lon":   26.1063, "is_capital": True},
    "cj": {"name": "Cluj-Napoca", "region": "Nord-Vest",        "lat":  46.7667, "lon":   23.6000, "is_capital": False},
    "ti": {"name": "Timișoara",   "region": "Vest",             "lat":  45.7537, "lon":   21.2257, "is_capital": False},
    "is": {"name": "Iași",        "region": "Nord-Est",         "lat":  47.1667, "lon":   27.6000, "is_capital": False},
    "ct": {"name": "Constanța",   "region": "Sud-Est",          "lat":  44.1807, "lon":   28.6343, "is_capital": False},
    "cv": {"name": "Craiova",     "region": "Sud-Vest Oltenia", "lat":  44.3167, "lon":   23.8000, "is_capital": False},
    "bv": {"name": "Brașov",      "region": "Centru",           "lat":  45.6486, "lon":   25.6061, "is_capital": False},
    "pl": {"name": "Ploiești",    "region": "Sud-Muntenia",     "lat":  44.9500, "lon":   26.0167, "is_capital": False},
}

# https://en.wikipedia.org/wiki/Provinces_of_Bulgaria
BULGARIA_PROVINCES = {
    "so": {"name": "Sofia",          "region": "Sofia-grad",     "lat":  42.6975, "lon":   23.3241, "is_capital": True},
    "pd": {"name": "Plovdiv",        "region": "Plovdiv",        "lat":  42.1539, "lon":   24.7500, "is_capital": False},
    "vn": {"name": "Varna",          "region": "Varna",          "lat":  43.2191, "lon":   27.9102, "is_capital": False},
    "bs": {"name": "Burgas",         "region": "Burgas",         "lat":  42.5065, "lon":   27.4689, "is_capital": False},
    "ru": {"name": "Ruse",           "region": "Ruse",           "lat":  43.8487, "lon":   25.9534, "is_capital": False},
    "sz": {"name": "Stara Zagora",   "region": "Stara Zagora",   "lat":  42.4320, "lon":   25.6426, "is_capital": False},
    "pl": {"name": "Pleven",         "region": "Pleven",         "lat":  43.4179, "lon":   24.6167, "is_capital": False},
    "bl": {"name": "Blagoevgrad",    "region": "Blagoevgrad",    "lat":  42.0146, "lon":   23.0980, "is_capital": False},
    "vt": {"name": "Veliko Tarnovo", "region": "Veliko Tarnovo", "lat":  43.0812, "lon":   25.6290, "is_capital": False},
    "db": {"name": "Dobrich",        "region": "Dobrich",        "lat":  43.5649, "lon":   27.8314, "is_capital": False},
    "gb": {"name": "Gabrovo",        "region": "Gabrovo",        "lat":  42.8742, "lon":   25.3182, "is_capital": False},
    "hs": {"name": "Haskovo",        "region": "Haskovo",        "lat":  41.9342, "lon":   25.5556, "is_capital": False},
    "kj": {"name": "Kardzhali",      "region": "Kardzhali",      "lat":  41.6450, "lon":   25.3658, "is_capital": False},
    "kn": {"name": "Kyustendil",     "region": "Kyustendil",     "lat":  42.2831, "lon":   22.6922, "is_capital": False},
    "lv": {"name": "Lovech",         "region": "Lovech",         "lat":  43.1323, "lon":   24.7176, "is_capital": False},
    "mn": {"name": "Montana",        "region": "Montana",        "lat":  43.4128, "lon":   23.2217, "is_capital": False},
    "pz": {"name": "Pazardzhik",     "region": "Pazardzhik",     "lat":  42.1993, "lon":   24.3332, "is_capital": False},
    "pk": {"name": "Pernik",         "region": "Pernik",         "lat":  42.5967, "lon":   23.0332, "is_capital": False},
    "rz": {"name": "Razgrad",        "region": "Razgrad",        "lat":  43.5333, "lon":   26.5185, "is_capital": False},
    "sh": {"name": "Shumen",         "region": "Shumen",         "lat":  43.2706, "lon":   26.9229, "is_capital": False},
    "ss": {"name": "Silistra",       "region": "Silistra",       "lat":  44.1171, "lon":   27.2606, "is_capital": False},
    "sl": {"name": "Sliven",         "region": "Sliven",         "lat":  42.6861, "lon":   26.3256, "is_capital": False},
    "sm": {"name": "Smolyan",        "region": "Smolyan",        "lat":  41.5744, "lon":   24.7120, "is_capital": False},
    "sq": {"name": "Sofia",          "region": "Sofia Province", "lat":  42.6975, "lon":   23.3241, "is_capital": False},   # seated in Sofia city, a separate province
    "tg": {"name": "Targovishte",    "region": "Targovishte",    "lat":  43.2512, "lon":   26.5722, "is_capital": False},
    "vd": {"name": "Vidin",          "region": "Vidin",          "lat":  43.9916, "lon":   22.8824, "is_capital": False},
    "vr": {"name": "Vratsa",         "region": "Vratsa",         "lat":  43.2105, "lon":   23.5631, "is_capital": False},
    "ya": {"name": "Yambol",         "region": "Yambol",         "lat":  42.4824, "lon":   26.5001, "is_capital": False},
}

# https://en.wikipedia.org/wiki/Administrative_regions_of_Greece
GREECE_REGIONS = {
    "att":  {"name": "Athens",       "region": "Attica",                    "lat":  37.9838, "lon":   23.7278, "is_capital": True},
    "cmac": {"name": "Thessaloniki", "region": "Central Macedonia",         "lat":  40.6407, "lon":   22.9349, "is_capital": False},
    "wgr":  {"name": "Patras",       "region": "Western Greece",            "lat":  38.2462, "lon":   21.7351, "is_capital": False},
    "cre":  {"name": "Heraklion",    "region": "Crete",                     "lat":  35.3279, "lon":   25.1434, "is_capital": False},   # Peloponnese AC link 2021, Attica HVDC only from mid-2025
    "the":  {"name": "Larissa",      "region": "Thessaly",                  "lat":  39.6285, "lon":   22.4211, "is_capital": False},
    "emac": {"name": "Komotini",     "region": "East Macedonia and Thrace", "lat":  41.1176, "lon":   25.4059, "is_capital": False},
    "epi":  {"name": "Ioannina",     "region": "Epirus",                    "lat":  39.6634, "lon":   20.8519, "is_capital": False},
    "wmac": {"name": "Kozani",       "region": "West Macedonia",            "lat":  40.2993, "lon":   21.7898, "is_capital": False},
    "cgr":  {"name": "Lamia",        "region": "Central Greece",            "lat":  38.8995, "lon":   22.4335, "is_capital": False},
    "pel":  {"name": "Tripoli",      "region": "Peloponnese",               "lat":  37.5096, "lon":   22.3788, "is_capital": False},
    "nae":  {"name": "Mytilene",     "region": "North Aegean",              "lat":  39.1077, "lon":   26.5553, "is_capital": False},   # Lesbos is a HEDNO non-interconnected island; link due 2030
    "sae":  {"name": "Ermoupoli",    "region": "South Aegean",              "lat":  37.4447, "lon":   24.9429, "is_capital": False},   # Syros interconnected since 2018 (Cyclades phase A)
    "ion":  {"name": "Corfu",        "region": "Ionian Islands",            "lat":  39.6244, "lon":   19.9202, "is_capital": False},   # interconnected to the mainland via Igoumenitsa
}

# https://en.wikipedia.org/wiki/Regions_of_Denmark
DENMARK_REGIONS = {
    "h":  {"name": "Copenhagen", "region": "Hovedstaden",      "lat":  55.6759, "lon":   12.5655, "is_capital": True},   # regional seat is Hillerød, but the national capital lies in this region
    "m":  {"name": "Viborg",     "region": "Central Denmark",  "lat":  56.4532, "lon":    9.4020, "is_capital": False},
    "sd": {"name": "Vejle",      "region": "Southern Denmark", "lat":  55.7093, "lon":    9.5357, "is_capital": False},
    "n":  {"name": "Aalborg",    "region": "North Denmark",    "lat":  57.0480, "lon":    9.9187, "is_capital": False},
    "sj": {"name": "Sorø",       "region": "Zealand",          "lat":  55.4318, "lon":   11.5555, "is_capital": False},
}

# https://en.wikipedia.org/wiki/Counties_of_Norway
NORWAY_COUNTIES = {
    "os": {"name": "Oslo",         "region": "Oslo",            "lat":  59.9127, "lon":   10.7461, "is_capital": True},
    "vl": {"name": "Bergen",       "region": "Vestland",        "lat":  60.3930, "lon":    5.3242, "is_capital": False},
    "tr": {"name": "Steinkjer",    "region": "Trøndelag",       "lat":  64.0149, "lon":   11.4954, "is_capital": False},
    "ro": {"name": "Stavanger",    "region": "Rogaland",        "lat":  58.9701, "lon":    5.7333, "is_capital": False},
    "tf": {"name": "Tromsø",       "region": "Troms",           "lat":  69.6489, "lon":   18.9551, "is_capital": False},
    "ag": {"name": "Kristiansand", "region": "Agder",           "lat":  58.1467, "lon":    7.9956, "is_capital": False},
    "mr": {"name": "Molde",        "region": "Møre og Romsdal", "lat":  62.7375, "lon":    7.1591, "is_capital": False},
    "nl": {"name": "Bodø",         "region": "Nordland",        "lat":  67.2827, "lon":   14.3751, "is_capital": False},
    "in": {"name": "Hamar",        "region": "Innlandet",       "lat":  60.7945, "lon":   11.0680, "is_capital": False},
    "vt": {"name": "Tønsberg",     "region": "Vestfold",        "lat":  59.2675, "lon":   10.4076, "is_capital": False},
    "vk": {"name": "Drammen",      "region": "Buskerud",        "lat":  59.7439, "lon":   10.2045, "is_capital": False},
    "of": {"name": "Sarpsborg",    "region": "Østfold",         "lat":  59.2839, "lon":   11.1096, "is_capital": False},
    "ak": {"name": "Oslo",         "region": "Akershus",        "lat":  59.9127, "lon":   10.7461, "is_capital": False},   # seated in Oslo, a separate county
    "te": {"name": "Skien",        "region": "Telemark",        "lat":  59.2096, "lon":    9.6090, "is_capital": False},
    "fm": {"name": "Vadsø",        "region": "Finnmark",        "lat":  70.0735, "lon":   29.7494, "is_capital": False},
}

# https://en.wikipedia.org/wiki/Counties_of_Ireland
IRELAND_COUNTIES = {
    "d":  {"name": "Dublin",             "region": "Dublin",    "lat":  53.3331, "lon":   -6.2489, "is_capital": True},
    "c":  {"name": "Cork",               "region": "Cork",      "lat":  51.8980, "lon":   -8.4706, "is_capital": False},
    "g":  {"name": "Galway",             "region": "Galway",    "lat":  53.2724, "lon":   -9.0510, "is_capital": False},
    "l":  {"name": "Limerick",           "region": "Limerick",  "lat":  52.6647, "lon":   -8.6231, "is_capital": False},
    "w":  {"name": "Waterford",          "region": "Waterford", "lat":  52.2583, "lon":   -7.1119, "is_capital": False},
    "k":  {"name": "Kilkenny",           "region": "Kilkenny",  "lat":  52.6542, "lon":   -7.2522, "is_capital": False},
    "s":  {"name": "Sligo",              "region": "Sligo",     "lat":  54.2697, "lon":   -8.4694, "is_capital": False},
    "a":  {"name": "Mullingar",          "region": "Westmeath", "lat":  53.5247, "lon":   -7.3385, "is_capital": False},
    "t":  {"name": "Tralee",             "region": "Kerry",     "lat":  52.2704, "lon":   -9.7026, "is_capital": False},
    "dl": {"name": "Lifford",            "region": "Donegal",   "lat":  54.8319, "lon":   -7.4836, "is_capital": False},
    "cw": {"name": "Carlow",             "region": "Carlow",    "lat":  52.8408, "lon":   -6.9261, "is_capital": False},
    "cn": {"name": "Cavan",              "region": "Cavan",     "lat":  53.9908, "lon":   -7.3606, "is_capital": False},
    "cl": {"name": "Ennis",              "region": "Clare",     "lat":  52.8436, "lon":   -8.9864, "is_capital": False},
    "kd": {"name": "Naas",               "region": "Kildare",   "lat":  53.2158, "lon":   -6.6669, "is_capital": False},
    "ls": {"name": "Portlaoise",         "region": "Laois",     "lat":  53.0344, "lon":   -7.2998, "is_capital": False},
    "lm": {"name": "Carrick-on-Shannon", "region": "Leitrim",   "lat":  53.9469, "lon":   -8.0900, "is_capital": False},
    "lf": {"name": "Longford",           "region": "Longford",  "lat":  53.7254, "lon":   -7.7982, "is_capital": False},
    "lh": {"name": "Dundalk",            "region": "Louth",     "lat":  54.0000, "lon":   -6.4167, "is_capital": False},
    "mo": {"name": "Castlebar",          "region": "Mayo",      "lat":  53.8500, "lon":   -9.3000, "is_capital": False},
    "mh": {"name": "Navan",              "region": "Meath",     "lat":  53.6528, "lon":   -6.6814, "is_capital": False},
    "mn": {"name": "Monaghan",           "region": "Monaghan",  "lat":  54.2459, "lon":   -6.9710, "is_capital": False},
    "oy": {"name": "Tullamore",          "region": "Offaly",    "lat":  53.2739, "lon":   -7.4889, "is_capital": False},
    "rn": {"name": "Roscommon",          "region": "Roscommon", "lat":  53.6333, "lon":   -8.1833, "is_capital": False},
    "tp": {"name": "Nenagh",             "region": "Tipperary", "lat":  52.8628, "lon":   -8.1995, "is_capital": False},
    "wx": {"name": "Wexford",            "region": "Wexford",   "lat":  52.3342, "lon":   -6.4575, "is_capital": False},
    "ww": {"name": "Wicklow",            "region": "Wicklow",   "lat":  52.9750, "lon":   -6.0494, "is_capital": False},
}

COUNTRIES = {
    "PL": {"name": "poland",   "tz": "Europe/Warsaw",   "calendar": "PL", "regions": POLAND_VOIVODESHIP},
    "IT": {"name": "italy",    "tz": "Europe/Rome",     "calendar": "IT", "regions": ITALY_REGIONS},
    "FI": {"name": "finland",  "tz": "Europe/Helsinki", "calendar": "FI", "regions": FINLAND_REGIONS},
    "DE": {"name": "germany",  "tz": "Europe/Berlin",   "calendar": "DE", "regions": GERMANY_LAENDER},
    "PT": {"name": "portugal", "tz": "Europe/Lisbon",   "calendar": "PT", "regions": PORTUGAL_DISTRICTS},
    "FR": {"name": "france",      "tz": "Europe/Paris",      "calendar": "FR", "regions": FRANCE_REGIONS},
    "ES": {"name": "spain",       "tz": "Europe/Madrid",     "calendar": "ES", "regions": SPAIN_COMMUNITIES},
    "NL": {"name": "netherlands", "tz": "Europe/Amsterdam",  "calendar": "NL", "regions": NETHERLANDS_PROVINCES},
    "BE": {"name": "belgium",     "tz": "Europe/Brussels",   "calendar": "BE", "regions": BELGIUM_PROVINCES},
    "AT": {"name": "austria",     "tz": "Europe/Vienna",     "calendar": "AT", "regions": AUSTRIA_STATES},
    "CH": {"name": "switzerland", "tz": "Europe/Zurich",     "calendar": "CH", "regions": SWITZERLAND_CANTONS},
    "CZ": {"name": "czechia",     "tz": "Europe/Prague",     "calendar": "CZ", "regions": CZECHIA_REGIONS},
    "SK": {"name": "slovakia",    "tz": "Europe/Bratislava", "calendar": "SK", "regions": SLOVAKIA_REGIONS},
    "HU": {"name": "hungary",     "tz": "Europe/Budapest",   "calendar": "HU", "regions": HUNGARY_COUNTIES},
    "RO": {"name": "romania",     "tz": "Europe/Bucharest",  "calendar": "RO", "regions": ROMANIA_REGIONS},
    "BG": {"name": "bulgaria",    "tz": "Europe/Sofia",      "calendar": "BG", "regions": BULGARIA_PROVINCES},
    "GR": {"name": "greece",      "tz": "Europe/Athens",     "calendar": "GR", "regions": GREECE_REGIONS},
    "DK": {"name": "denmark",     "tz": "Europe/Copenhagen", "calendar": "DK", "regions": DENMARK_REGIONS},
    "NO": {"name": "norway",      "tz": "Europe/Oslo",       "calendar": "NO", "regions": NORWAY_COUNTIES},
    "IE": {"name": "ireland",     "tz": "Europe/Dublin",     "calendar": "IE", "regions": IRELAND_COUNTIES},
    #     SE/GB are omitted (no ENTSO-E load / no A31 forecast). ---
}


def capital_code(info: dict) -> str:
    """Region code of the country's capital."""
    for code, region in info["regions"].items():
        if region.get("is_capital"):
            return code
    raise ValueError(f"no capital region defined for {info['name']}")


def capital_latlon(info: dict) -> tuple[float, float]:
    """(lat, lon) of the country's capital region."""
    region = info["regions"][capital_code(info)]
    return region["lat"], region["lon"]
