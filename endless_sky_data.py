# Data tables for Endless Sky system generation

# Planetary zones table
planetary_zones = {
    "inner_rocky_zone": {
        "description": "Hot zone where only rock and metal can condense",
        "distance_range_au": (0.3, 0.7),
        "temperature_range_k": (600, 1000),
        "dominant_materials": ["silicon", "iron", "nickel"],
        "max_terrestrial_planets": 6,
        "max_gas_giants": 0,
        "max_ice_giants": 0,
        "typical_planet_radius_km": (2400, 6052),
        "processing_order": 7,
        "average_major_moons": 0,
    },
    "goldilocks_zone": {
        "description": "Habitable zone where liquid water can exist",
        "distance_range_au": (0.7, 1.5),
        "temperature_range_k": (200, 300),
        "dominant_materials": ["silicon", "iron", "water"],
        "max_terrestrial_planets": 4,
        "max_gas_giants": 0,
        "max_ice_giants": 0,
        "typical_planet_radius_km": (3400, 7000),
        "processing_order": 6,
        "average_major_moons": 1.2,
        "notes": "Optimal zone for life; moons provide tidal stability"
    },
    "asteroid_belt_zone": {
        "description": "Disrupted formation zone due to gravitational influence",
        "distance_range_au": (1.5, 4.0),
        "temperature_range_k": (150, 250),
        "dominant_materials": ["silicon", "iron"],
        "max_terrestrial_planets": 0,
        "max_gas_giants": 0,
        "max_ice_giants": 0,
        "typical_planet_radius_km": (0, 0),
        "processing_order": 8,
        "average_major_moons": 0,
    },
    "snow_line_zone": {
        "description": "Critical boundary where water ice can form",
        "distance_range_au": (3.0, 5.0),
        "temperature_range_k": (150, 200),
        "dominant_materials": ["silicon", "water"],
        "max_terrestrial_planets": 1,
        "max_gas_giants": 1,
        "max_ice_giants": 0,
        "typical_planet_radius_km": (69911, 71492),
        "processing_order": 1,
        "average_major_moons": 6,
        "notes": "Enhanced solid material allows rapid core growth"
    },
    "outer_gas_giant_zone": {
        "description": "Cold zone optimal for gas giant formation",
        "distance_range_au": (5.0, 15.0),
        "temperature_range_k": (80, 150),
        "dominant_materials": ["metal", "ice"],
        "max_terrestrial_planets": 0,
        "max_gas_giants": 2,
        "max_ice_giants": 1,
        "typical_planet_radius_km": (58232, 69911),
        "processing_order": 2,
        "average_major_moons": 5,
        "notes": "Multiple gas giants possible with 3:2 resonances"
    },
    "ice_giant_zone": {
        "description": "Region where ice giants form efficiently",
        "distance_range_au": (15.0, 35.0),
        "temperature_range_k": (40, 80),
        "dominant_materials": ["water", "metal"],
        "max_terrestrial_planets": 0,
        "max_gas_giants": 0,
        "max_ice_giants": 3,
        "typical_planet_radius_km": (24622, 25362),
        "processing_order": 3,
        "average_major_moons": 4,
        "notes": "Lower gas density limits gas giant formation"
    },
    "kuiper_belt_zone": {
        "description": "Scattered disk and small body formation region",
        "distance_range_au": (35.0, 100.0),
        "temperature_range_k": (20, 40),
        "dominant_materials": ["ice", "tungsten"],
        "max_terrestrial_planets": 0,
        "max_gas_giants": 0,
        "max_ice_giants": 1,
        "typical_planet_radius_km": (1200, 25000),
        "processing_order": 4,
        "average_major_moons": 3,
        "notes": "Very long formation timescales"
    }
}

# Planet classes
planet_classes = {
    'A': {
        'name': 'Proto-Earth',
        'description': 'A scorching, molten world with glowing lava seas...',
        'mass_range': (0.5, 1.0),
        'orbital_range': (0.1, 0.7),
        'planet_sprites': ['planet/lava0', 'planet/lava1', 'planet/lava2'],
        'land_sprites': ['land/lava0', 'land/lava1', 'land/lava2'],
        'adjectives': ['scorching', 'molten', 'fiery', 'radiant'],
        'base_habitability': 500,
        'moon_range': (0, 1),
        'dominant_materials': ['silicon', 'iron', 'aluminum']
    },
    'B': {
        'name': 'Unstable Planet',
        'description': 'A volatile, rocky planet riven by quakes...',
        'mass_range': (0.5, 1.0),
        'orbital_range': (0.1, 0.7),
        'planet_sprites': ['planet/lava3'],
        'land_sprites': ['land/lava3'],
        'adjectives': ['volatile', 'rocky', 'trembling', 'rugged'],
        'base_habitability': 500,
        'moon_range': (0, 1),
        'dominant_materials': ['silicon', 'iron', 'titanium']
    },
    'C': {
        'name': 'Carbon-Rich Planet',
        'description': 'A dark, crystalline world with a carbon-rich crust...',
        'mass_range': (0.5, 5.0),
        'orbital_range': (0.8, 1.5),
        'planet_sprites': ['planet/rock12', 'planet/rock13', 'planet/rock14'],
        'land_sprites': ['land/rock12', 'land/rock13', 'land/rock14'],
        'adjectives': ['dark', 'crystalline', 'carbonaceous', 'gleaming'],
        'base_habitability': 1000,
        'moon_range': (0, 1),
        'dominant_materials': ['gold', 'platinum', 'neodymium']
    },
    'D': {
        'name': 'Barren Rock',
        'description': 'A desolate, barren world with no atmosphere...',
        'mass_range': (0.01, 0.2),
        'orbital_range': (0.7, 4.0),
        'planet_sprites': ['planet/rock0', 'planet/rock1', 'planet/rock2', 'planet/dust0'],
        'land_sprites': ['land/rock0', 'land/rock1', 'land/rock2', 'land/dust0'],
        'adjectives': ['barren', 'cratered', 'desolate', 'dusty'],
        'base_habitability': 600,
        'moon_range': (0, 0),
        'dominant_materials': ['silicon', 'iron', 'aluminum']
    },
    'E': {
        'name': 'Exotic Energy World',
        'description': 'A radiant, anomalous sphere pulsing with energy...',
        'mass_range': (0.1, 100.0),
        'orbital_range': (5.0, 100.0),
        'planet_sprites': ['planet/gas8', 'planet/gas9', 'planet/cloud5'],
        'land_sprites': ['land/sivae0'],
        'adjectives': ['radiant', 'anomalous', 'pulsing', 'exotic', 'energetic'],
        'base_habitability': 100,
        'moon_range': (0, 5),
        'dominant_materials': ['uranium', 'platinum', 'silver']
    },
    'F': {
        'name': 'Fog World',
        'description': 'A shrouded world cloaked in thick, dusty fog...',
        'mass_range': (0.5, 3.0),
        'orbital_range': (0.7, 1.5),
        'planet_sprites': ['planet/cloud0', 'planet/cloud1', 'planet/cloud4'],
        'land_sprites': ['land/cloud0', 'land/cloud1', 'land/cloud4'],
        'adjectives': ['shrouded', 'foggy', 'dusty', 'mysterious'],
        'base_habitability': 1000,
        'moon_range': (0, 1),
        'dominant_materials': ['silicon', 'copper', 'titanium']
    },
    'G': {
        'name': 'Garden World',
        'description': 'A verdant paradise with sprawling forests...',
        'mass_range': (0.8, 1.5),
        'orbital_range': (0.7, 1.5),
        'planet_sprites': ['planet/forest0', 'planet/forest1', 'planet/forest3', 'planet/earth0'],
        'land_sprites': ['land/forest0', 'land/forest1', 'land/forest3', 'land/earth0'],
        'adjectives': ['verdant', 'lush', 'forested', 'paradisiacal'],
        'base_habitability': 5000,
        'moon_range': (0, 2),
        'dominant_materials': ['silicon', 'iron', 'aluminum', 'copper']
    },
    'H': {
        'name': 'Arid World',
        'description': 'A parched, sandy desert world with sparse oases...',
        'mass_range': (0.5, 1.2),
        'orbital_range': (0.7, 1.7),
        'planet_sprites': ['planet/desert0', 'planet/desert1', 'planet/desert2'],
        'land_sprites': ['land/desert0', 'land/desert1', 'land/desert2'],
        'adjectives': ['arid', 'sandy', 'parched', 'sparse'],
        'base_habitability': 3000,
        'moon_range': (0, 2),
        'dominant_materials': ['silicon', 'iron', 'titanium']
    },
    'I': {
        'name': 'Ice Giant',
        'description': 'A frigid gas giant with swirling blue clouds...',
        'mass_range': (14, 17),
        'orbital_range': (15.0, 35.0),
        'planet_sprites': ['planet/gas0', 'planet/gas1', 'planet/gas4'],
        'land_sprites': [],
        'adjectives': ['frigid', 'swirling', 'icy', 'massive'],
        'base_habitability': 0,
        'moon_range': (5, 50),
        'dominant_materials': ['iron', 'silicon']
    },
    'J1': {
        'name': 'Gas Giant: Jupiter-like',
        'description': 'A massive, turbulent gas giant...',
        'mass_range': (300, 400),
        'orbital_range': (4.0, 15.0),
        'planet_sprites': ['planet/gas2', 'planet/gas3', 'planet/gas5'],
        'land_sprites': [],
        'adjectives': ['massive', 'turbulent', 'stormy', 'colossal'],
        'base_habitability': 0,
        'moon_range': (5, 50),
        'dominant_materials': ['iron', 'silicon']
    },
    'J2': {
        'name': 'Gas Giant: Saturn-like',
        'description': 'A serene gas giant with delicate rings...',
        'mass_range': (90, 120),
        'orbital_range': (5.0, 15.0),
        'planet_sprites': ['planet/gas6', 'planet/gas7'],
        'land_sprites': [],
        'adjectives': ['serene', 'ringed', 'vast', 'tranquil'],
        'base_habitability': 0,
        'moon_range': (5, 50),
        'dominant_materials': ['iron', 'silicon']
    },
    'K': {
        'name': 'Marginally Habitable',
        'description': 'A harsh, rocky world with a thin atmosphere...',
        'mass_range': (0.5, 1.5),
        'orbital_range': (1.5, 4.0),
        'planet_sprites': ['planet/rock10', 'planet/rock11', 'planet/desert3'],
        'land_sprites': ['land/rock10', 'land/rock11', 'land/desert3'],
        'adjectives': ['harsh', 'rocky', 'sparse', 'fragile'],
        'base_habitability': 3000,
        'moon_range': (0, 2),
        'dominant_materials': ['silicon', 'iron', 'aluminum']
    },
    'L': {
        'name': 'Proto-Ecosystem World',
        'description': 'A nascent world with primitive algae blooms...',
        'mass_range': (0.8, 2.0),
        'orbital_range': (0.7, 1.5),
        'planet_sprites': ['planet/forest2', 'planet/ocean0', 'planet/earth2'],
        'land_sprites': ['land/forest2', 'land/ocean0', 'land/earth2'],
        'adjectives': ['nascent', 'primal', 'moist', 'verdant'],
        'base_habitability': 4000,
        'moon_range': (0, 2),
        'dominant_materials': ['silicon', 'iron', 'copper']
    },
    'M': {
        'name': 'Earth-like',
        'description': 'A temperate, blue-green world with lush continents...',
        'mass_range': (0.8, 1.2),
        'orbital_range': (0.7, 1.5),
        'planet_sprites': ['planet/earth1', 'planet/earth2', 'planet/ocean2'],
        'land_sprites': ['land/earth1', 'land/earth2', 'land/ocean2'],
        'adjectives': ['temperate', 'lush', 'blue-green', 'fertile'],
        'base_habitability': 5000,
        'moon_range': (0, 2),
        'dominant_materials': ['silicon', 'iron', 'aluminum', 'copper']
    },
    'N': {
        'name': 'Toxic World',
        'description': 'A hostile planet with a corrosive miasma...',
        'mass_range': (0.5, 2.5),
        'orbital_range': (0.7, 4.0),
        'planet_sprites': ['planet/rock8', 'planet/cloud5', 'planet/cloud6'],
        'land_sprites': ['land/rock8', 'land/cloud5', 'land/cloud6'],
        'adjectives': ['toxic', 'hostile', 'corrosive', 'murky'],
        'base_habitability': 500,
        'moon_range': (0, 1),
        'dominant_materials': ['silicon', 'iron', 'titanium']
    },
    'O': {
        'name': 'Ocean World',
        'description': 'A shimmering, water-covered globe with deep oceans...',
        'mass_range': (0.8, 2.0),
        'orbital_range': (0.7, 1.5),
        'planet_sprites': ['planet/ocean1', 'planet/ocean2', 'planet/ice6'],
        'land_sprites': ['land/ocean1', 'land/ocean2', 'land/ocean3'],
        'adjectives': ['shimmering', 'watery', 'deep', 'vast'],
        'base_habitability': 4000,
        'moon_range': (0, 2),
        'dominant_materials': ['silicon', 'iron', 'aluminum']
    },
    'P': {
        'name': 'Glacial/Ice World',
        'description': 'A frozen, icy world with vast glaciers...',
        'mass_range': (0.3, 1.5),
        'orbital_range': (4.0, 100.0),
        'planet_sprites': ['planet/ice0', 'planet/ice4', 'planet/ice8'],
        'land_sprites': ['land/ice0', 'land/ice4', 'land/ice8'],
        'adjectives': ['frozen', 'icy', 'glacial', 'cold'],
        'base_habitability': 1000,
        'moon_range': (0, 1),
        'dominant_materials': ['tungsten', 'lead', 'silicon']
    },
    'Q': {
        'name': 'Quarantine',
        'description': 'An abandoned, scarred world with crumbling ruins...',
        'mass_range': (0.5, 1.5),
        'orbital_range': (0.7, 4.0),
        'planet_sprites': ['planet/rock15', 'planet/desert3', 'planet/rock7'],
        'land_sprites': ['land/rock15', 'land/desert3', 'land/rock7'],
        'adjectives': ['abandoned', 'scarred', 'ruined', 'desolate'],
        'base_habitability': 200,
        'moon_range': (0, 2),
        'dominant_materials': ['gold', 'silver', 'neodymium']
    },
    'R': {
        'name': 'Ringworld/Megastation',
        'description': 'A gleaming metal habitat orbiting with rings...',
        'mass_range': (0.01, 0.1),
        'orbital_range': (1.0, 4.0),
        'planet_sprites': ['planet/station/station0', 'planet/station/station1', 'planet/station/station2'],
        'land_sprites': ['land/station0', 'land/station3', 'land/station4'],
        'adjectives': ['gleaming', 'artificial'],
        'base_habitability': 5000,
        'moon_range': (0, 0),
        'dominant_materials': ['titanium', 'aluminum', 'copper']
    },
    'S': {
        'name': 'SuperEarth',
        'description': 'A massive, rocky world with towering mountains...',
        'mass_range': (2, 10),
        'orbital_range': (0.7, 4.0),
        'planet_sprites': ['planet/rock5', 'planet/rock6', 'planet/rock4'],
        'land_sprites': ['land/rock5', 'land/rock6', 'land/rock4'],
        'adjectives': ['massive', 'rocky', 'towering', 'rugged'],
        'base_habitability': 2100,
        'moon_range': (1, 5),
        'dominant_materials': ['silicon', 'iron', 'aluminum', 'titanium']
    },
    'T1': {
        'name': 'Gas Supergiant',
        'description': 'A colossal gas giant with raging storms...',
        'mass_range': (400, 1000),
        'orbital_range': (5.0, 100.0),
        'planet_sprites': ['planet/gas4', 'planet/gas9', 'planet/gas3'],
        'land_sprites': [],
        'adjectives': ['colossal', 'stormy', 'raging', 'vast'],
        'base_habitability': 0,
        'moon_range': (5, 50),
        'dominant_materials': ['iron', 'silicon']
    },
    'T2': {
        'name': 'Brown Dwarf',
        'description': 'A faintly glowing planet-like star...',
        'mass_range': (1000, 13000),
        'orbital_range': (5.0, 100.0),
        'planet_sprites': ['planet/gas8', 'planet/star/m0', 'planet/gas9'],
        'land_sprites': [],
        'adjectives': ['faintly', 'glowing', 'star-like', 'dim'],
        'base_habitability': 0,
        'moon_range': (0, 5),
        'dominant_materials': ['iron', 'silicon']
    },
    'U': {
        'name': 'Unstable Orbit',
        'description': 'A rogue, dusty world on an erratic path...',
        'mass_range': (0.01, 1.0),
        'orbital_range': (0.1, 100.0),
        'planet_sprites': ['planet/dust3', 'planet/dust7', 'planet/dust2'],
        'land_sprites': ['land/dust3', 'land/dust7', 'land/dust2'],
        'adjectives': ['rogue', 'dusty', 'erratic', 'remote'],
        'base_habitability': 100,
        'moon_range': (0, 0),
        'dominant_materials': ['silicon', 'iron']
    },
    'V': {
        'name': 'Volcanic Superworld',
        'description': 'A searing, Io-like world with relentless eruptions...',
        'mass_range': (0.3, 1.5),
        'orbital_range': (0.1, 0.7),
        'planet_sprites': ['planet/lava0', 'planet/lava1', 'planet/lava3'],
        'land_sprites': ['land/lava0', 'land/lava1', 'land/lava3'],
        'adjectives': ['violent', 'volcanic', 'eruptive', 'intense'],
        'base_habitability': 500,
        'moon_range': (0, 1),
        'dominant_materials': ['silicon', 'iron', 'titanium']
    },
    'W': {
        'name': 'Water Ice',
        'description': 'A cold, quenching sphere with subsurface oceans...',
        'mass_range': (0.05, 0.3),
        'orbital_range': (4.0, 100.0),
        'planet_sprites': ['planet/ice1', 'planet/ice5', 'planet/ice7'],
        'land_sprites': ['land/ice1', 'land/ice5', 'land/ice7'],
        'adjectives': ['cold', 'icy', 'subsurface', 'glistening'],
        'base_habitability': 600,
        'moon_range': (0, 1),
        'dominant_materials': ['tungsten', 'lead', 'silicon']
    },
    'Y': {
        'name': 'Demon Class',
        'description': 'A hellish world of extreme heat and radiation...',
        'mass_range': (0.5, 2.0),
        'orbital_range': (0.1, 0.7),
        'planet_sprites': ['planet/lava3', 'planet/rock9', 'planet/cloud7'],
        'land_sprites': ['land/lava3', 'land/rock9', 'land/cloud7'],
        'adjectives': ['hellish', 'radiated', 'infernal', 'harsh'],
        'base_habitability': 500,
        'moon_range': (0, 1),
        'dominant_materials': ['uranium', 'platinum', 'silver']
    },
    'Z': {
        'name': 'Zero-Gravity',
        'description': 'A tiny, airless asteroid with a pitted surface...',
        'mass_range': (0.001, 0.01),
        'orbital_range': (0.1, 100.0),
        'planet_sprites': ['planet/dust0', 'planet/dust1', 'planet/dust4'],
        'land_sprites': ['land/dust1', 'land/dust2', 'land/dust4'],
        'adjectives': [],
        'base_habitability': 0,
        'moon_range': [],
        'dominant_materials': ['silicon', 'iron']
    }
}

# Star image table
star_image = [
    {"class": "O", "type": "giant", "sprites": ["star/station0"], "base_habitability": 100},
    {"class": "O", "type": "normal", "sprites": ["star/station0"], "base_habitability": 100},
    {"class": "O", "type": "dwarf", "sprites": ["star/station0"], "base_habitability": 100},
    {"class": "B", "type": "giant", "sprites": ["star/station0"], "base_habitability": 200},
    {"class": "B", "type": "normal", "sprites": ["star/station0"], "base_habitability": 200},
    {"class": "B", "type": "dwarf", "sprites": ["star/station0"], "base_habitability": 200},
    {"class": "A", "type": "giant", "sprites": ["star/station0"], "base_habitability": 300},
    {"class": "A", "type": "normal", "sprites": ["star/station0"], "base_habitability": 300},
    {"class": "A", "type": "dwarf", "sprites": ["star/station0"], "base_habitability": 300},
    {"class": "F", "type": "giant", "sprites": ["star/planet0"], "base_habitability": 600},
    {"class": "F", "type": "normal", "sprites": ["star/station0"], "base_habitability": 600},
    {"class": "F", "type": "dwarf", "sprites": ["star/station0"], "base_habitability": 600},
    {"class": "G", "type": "giant", "sprites": ["star/station0"], "base_habitability": 1000},
    {"class": "G", "type": "normal", "sprites": ["star/station0"], "base_habitability": 1000},
    {"class": "G", "type": "dwarf", "sprites": ["star/station0"], "base_habitability": 1000},
    {"class": "K", "type": "giant", "sprites": ["star/station0"], "base_habitability": 800},
    {"class": "K", "type": "normal", "sprites": ["star/station0"], "base_habitability": 800},
    {"class": "K", "type": "dwarf", "sprites": ["star/station0"], "base_habitability": 800},
    {"class": "M", "type": "giant", "sprites": ["star/station0"], "base_habitability": 500},
    {"class": "M", "type": "normal", "sprites": ["star/station0"], "base_habitability": 500},
    {"class": "M", "type": "dwarf", "sprites": ["star/station0"], "base_habitability": 500}
]

# All trade goods
all_trade_goods = [
    'Clothing', 'Electronics', 'Equipment', 'Food',
    'Heavy Metals', 'Industrial', 'Luxury Goods',
    'Medical', 'Metal', 'Plastic'
]

# Asteroid types from map systems.txt
asteroid_types = [
    'small rock', 'medium rock', 'large rock',
    'small metal', 'medium metal', 'large metal'
]

# Minables from map systems.txt
valid_minables = [
    'aluminum', 'copper', 'gold', 'iron', 'lead',
    'neodymium', 'platinum', 'silicon', 'silver', 'titanium', 'tungsten', 'uranium'
]