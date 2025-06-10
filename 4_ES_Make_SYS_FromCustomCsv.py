import pandas as pd
import random
import re
import math
from typing import Dict , List , Tuple
import numpy as np
import logging
import os

system_name_counter = {}  # Place at module level, outside function

# Set up logging
logging.basicConfig(
    level=logging.DEBUG ,
    format='%(asctime)s - %(levelname)s - %(message)s' ,
    handlers=[
        logging.FileHandler('debug.log') ,
        logging.StreamHandler()
    ]
)

try:
    from endless_sky_data import (
        planetary_zones ,
        planet_classes ,
        star_image ,
        all_trade_goods ,
        asteroid_types ,
        valid_minables
    )

    logging.info("Successfully imported tables from endless_sky_data.py")
except ImportError as e:
    logging.error(f"Failed to import endless_sky_data: {e}")
    raise


def to_roman(num: int) -> str:
    """Convert integer to Roman numeral."""
    val = [(1000 , 'M') , (900 , 'CM') , (500 , 'D') , (400 , 'CD') ,
           (100 , 'C') , (90 , 'XC') , (50 , 'L') , (40 , 'XL') ,
           (10 , 'X') , (9 , 'IX') , (5 , 'V') , (4 , 'IV') , (1 , 'I')]
    result = ''
    for arabic , roman in val:
        while num >= arabic:
            result += roman
            num -= arabic
    return result


def sanitize_name(name: str , max_len: int = 20) -> str:
    """Sanitize system/planet name."""
    name = re.sub(r'[^\w\s-]' , '' , name.replace(' ' , ''))
    return name[:max_len].strip()


def get_system_name(row: pd.Series) -> Tuple[str, str]:
    """Get system name using sinbad_name, then Name_two, else fall back to 2D_sector-counter."""
    sinbad = str(row.get('sinbad_name', '')).strip()
    name_two = str(row.get('Name_two', '')).strip()
    sector = str(row.get('2D_sector', 'S000')).strip()

    if sinbad and len(sinbad) <= 20 and not re.match(r'^Gaia\sDR3\s\d+', sinbad):
        return sanitize_name(sinbad), sinbad
    if name_two:
        return sanitize_name(name_two), name_two

    if sector not in system_name_counter:
        system_name_counter[sector] = 0
    count = system_name_counter[sector]
    fallback_name = f"{sector}-{count:04d}"
    system_name_counter[sector] += 1
    return fallback_name, fallback_name


def get_star_attributes(star_class: str , star_type: str) -> str:
    """Get descriptive attributes for star."""
    if star_type == 'giant':
        return 'giant star' if star_class in ['O' , 'B' , 'F' , 'G' , 'K' , 'M'] else 'supergiant star'
    elif star_type == 'dwarf':
        return random.choice(['dwarf star' , 'small star'])
    elif star_class == 'G':
        return 'sun-like star'
    elif star_class in ['O' , 'B']:
        return 'bright star'
    elif star_class in ['K' , 'M']:
        return 'dull star'
    return 'star'


def get_star_params(star_type: str) -> Tuple[float , float , float]:
    """Generate star orbital parameters."""
    if star_type == 'giant':
        distance = random.uniform(10 , 100)
        period = random.uniform(200 , 1000)
    elif star_type == 'dwarf':
        distance = random.uniform(0 , 20)
        period = random.uniform(30 , 200)
    else:
        distance = random.uniform(0 , 50)
        period = random.uniform(50 , 500)
    offset = random.uniform(0 , 360)
    return distance , period , offset


def get_star_data(star_class: str) -> Dict:
    """Select random star data."""
    matching_stars = [s for s in star_image if s['class'] == star_class]
    if matching_stars:
        return random.choice(matching_stars)
    logging.warning(f"No matching star class {star_class}, using fallback O-giant")
    return star_image[0]  # Fallback to O-giant


def generate_planets_from_zones(star_habitability: int) -> List[Dict]:
    """Generate planets based on planetary zones."""
    logging.debug(f"Generating planets with star_habitability: {star_habitability}")
    planets = []
    scale = math.sqrt(1000 / max(1.0 , star_habitability))  # Scale distances by star
    terrestrial_classes = ['A' , 'B' , 'C' , 'D' , 'F' , 'G' , 'H' , 'K' , 'L' , 'M' , 'N' , 'O' , 'P' , 'Q' , 'R' ,
                           'S' , 'U' , 'V' , 'W' , 'Y' , 'Z']
    gas_giant_classes = ['J1' , 'J2' , 'T1']
    ice_giant_classes = ['I']
    zone_list = sorted(planetary_zones.items() , key=lambda x: x[1]['processing_order'])

    for zone_name , z_data in zone_list:
        if zone_name == 'asteroid_belt_zone':
            continue
        min_dist = z_data['distance_range_au'][0] * scale
        max_dist = z_data['distance_range_au'][1] * scale
        logging.debug(f"Processing zone {zone_name}: min_dist={min_dist}, max_dist={max_dist}")
        # Compatible planet classes
        compatible_classes = []
        for p_class , p_data in planet_classes.items():
            p_min , p_max = p_data['orbital_range']
            if p_min <= max_dist and p_max >= min_dist:
                if p_class in terrestrial_classes and z_data['max_terrestrial_planets'] > 0:
                    compatible_classes.append(p_class)
                elif p_class in gas_giant_classes and z_data['max_gas_giants'] > 0:
                    compatible_classes.append(p_class)
                elif p_class in ice_giant_classes and z_data['max_ice_giants'] > 0:
                    compatible_classes.append(p_class)

        # Generate planets
        n_terrestrial = min(z_data['max_terrestrial_planets'] ,
                            len([p for p in compatible_classes if p in terrestrial_classes]))
        n_gas = min(z_data['max_gas_giants'] , len([p for p in compatible_classes if p in gas_giant_classes]))
        n_ice = min(z_data['max_ice_giants'] , len([p for p in compatible_classes if p in ice_giant_classes]))
        logging.debug(f"Zone {zone_name}: n_terrestrial={n_terrestrial}, n_gas={n_gas}, n_ice={n_ice}")

        for _ in range(random.randint(0 , n_terrestrial)):
            if compatible_classes:
                p_class = random.choice([c for c in compatible_classes if c in terrestrial_classes])
                planets.append({'class': p_class , 'distance': random.uniform(min_dist , max_dist)})

        for _ in range(random.randint(0 , n_gas)):
            if compatible_classes:
                p_class = random.choice([c for c in compatible_classes if c in gas_giant_classes])
                planets.append({'class': p_class , 'distance': random.uniform(min_dist , max_dist)})

        for _ in range(random.randint(0 , n_ice)):
            if compatible_classes:
                p_class = random.choice([c for c in compatible_classes if c in ice_giant_classes])
                planets.append({'class': p_class , 'distance': random.uniform(min_dist , max_dist)})

    logging.debug(f"Generated {len(planets)} planets")
    return planets


def generate_system_old(row: pd.Series) -> str:
    """Generate system definition with zones and quoted attributes/trade."""
    system_name , _ = get_system_name(row)
    star_class = str(row.get('star_image_key' , 'G'))
    binary = float(row.get('binary_candidate' , 0.0))
    logging.debug(f"Generating system: {system_name}, star_class={star_class}, binary={binary}")

    # Initialize dependencies
    total_habitability = 0
    system_minables = set()
    landable_count = 0
    object_lines = []

    # Primary star
    primary_star = get_star_data(star_class)
    primary_sprite = random.choice(primary_star['sprites'])
    primary_type = primary_star['type']
    total_habitability += primary_star['base_habitability']
    attributes = get_star_attributes(star_class , primary_type)
    logging.debug(
        f"Primary star: sprite={primary_sprite}, type={primary_type}, habitability={primary_star['base_habitability']}")

    object_lines.append('object')
    object_lines.append(f'\tsprite "{primary_sprite}"')
    distance , period , offset = get_star_params(primary_type)
    object_lines.append(f'\tdistance {distance:.2f}')
    object_lines.append(f'\tperiod {period:.2f}')
    object_lines.append(f'\toffset {offset:.0f}')

    # Binary star
    if binary > 0.5:
        secondary_star = random.choice(star_image)
        secondary_sprite = random.choice(secondary_star['sprites'])
        secondary_type = secondary_star['type']
        logging.debug(f"Binary star: sprite={secondary_sprite}, type={secondary_type}")
        object_lines.append('object')
        object_lines.append(f'\tsprite "{secondary_sprite}"')
        distance , period , offset = get_star_params(secondary_type)
        object_lines.append(f'\tdistance {distance + random.uniform(10 , 50):.2f}')
        object_lines.append(f'\tperiod {period * 2:.2f}')
        object_lines.append(f'\toffset {offset + random.uniform(0 , 180):.0f}')

    # Generate planets from zones
    planets_data = generate_planets_from_zones(primary_star['base_habitability'])
    logging.debug(f"Generated {len(planets_data)} planets for system {system_name}")

    # Identify landable planets
    landable_planets = []
    for planet in planets_data:
        p_class = planet.get('class')
        if p_class not in planet_classes:
            continue
        p_data = planet_classes[p_class]
        system_minables.update(p_data['dominant_materials'])
        if p_data['base_habitability'] >= 3000 or p_class in ['M' , 'G' , 'L']:
            landable_planets.append(planet)

    # Ensure at least one landable planet
    if not landable_planets and planets_data:
        landable_planets.append(planets_data[0])
    logging.debug(f"Landable planets: {len(landable_planets)}")

    # Planets and moons
    planet_idx = 1
    for planet in planets_data:
        p_class = planet.get('class')
        if p_class not in planet_classes:
            continue
        p_data = planet_classes[p_class]
        is_landable = planet in landable_planets
        planet_name = f"{system_name}-{to_roman(planet_idx)}" if is_landable else ''
        if is_landable:
            landable_count += 1
            total_habitability += p_data['base_habitability']
        planet_block = []
        planet_block.append(f'\tobject {planet_name}')
        planet_block.append(f'\t\tsprite "{random.choice(p_data["planet_sprites"])}"')
        orbital_dist = planet['distance'] * 100  # AU to game units
        planet_block.append(f'\t\tdistance {orbital_dist:.2f}')
        planet_block.append(f'\t\tperiod {random.uniform(100 , 1000):.2f}')

        # Moons
        scale = math.sqrt(1000 / max(1.0 , primary_star['base_habitability']))
        zone_name = next((z for z , z_data in planetary_zones.items() if
                          z_data['distance_range_au'][0] * scale <= planet['distance'] <= z_data['distance_range_au'][
                              1] * scale) , None)
        moon_count = np.random.poisson(planetary_zones[zone_name]['average_major_moons']) if zone_name else 0
        for _ in range(moon_count):
            object_lines.append('object')
            object_lines.append(f'\t\tsprite "planet/moon{random.randint(0 , 3)}"')
            object_lines.append(f'\t\tdistance {random.uniform(0.1 , 0.5):.2f}')
            object_lines.append(f'\t\tperiod {random.uniform(10 , 50):.2f}')

        planet_idx += 1

    # Space station
    landable_count += 1
    object_lines.append(f'object "{system_name}-Station"')
    object_lines.append(f'\tsprite "planet/station/station{random.randint(0 , 2)}"')
    object_lines.append(f'\tdistance {random.uniform(500 , 1000):.0f}')
    object_lines.append(f'\tperiod {random.uniform(500 , 1500):.0f}')

    # Assemble output
    scale = math.sqrt(1000 / max(1.0 , primary_star['base_habitability']))
    output = [
        f'system "{system_name}"' ,
        f'\tpos {row.get("flat_x" , 0.0):.1f} {row.get("flat_y" , 0.0):.1f}' ,
        '\tgovernment Republic' ,
        f'\tattributes "{attributes}"' ,
        '\tarrival none' ,
        '\tlink none' ,
        f'\thabitable {total_habitability:.1f}' ,
        f'\tbelt {random.randint(1000 , 3000) * scale:.0f}'
    ]

    # Asteroids
    asteroid_count = random.randint(2 , 5)
    if any(z for z in planets_data if
           planetary_zones['asteroid_belt_zone']['distance_range_au'][0] * scale <= z['distance'] <=
           planetary_zones['asteroid_belt_zone']['distance_range_au'][1] * scale):
        asteroid_count += random.randint(1 , 3)
    for _ in range(asteroid_count):
        a_type = random.choice(asteroid_types)
        count = random.randint(1 , 50)
        speed = random.uniform(1.0 , 6.0)
        output.append(f'\tasteroids "{a_type}" {count} {speed:.2f}')

    # Minables
    for zone_name , z_data in planetary_zones.items():
        system_minables.update([m for m in z_data['dominant_materials'] if m in valid_minables])
    system_minables = sorted([m for m in system_minables if m in valid_minables])
    for minable in system_minables:
        count = random.randint(1 , 20)
        speed = random.uniform(2.0 , 6.0)
        output.append(f'\tminables {minable} {count} {speed:.2f}')

    # Trade
    for trade_item in sorted(all_trade_goods):
        value = random.randint(200 , 600)
        trade_name = f'"{trade_item}"' if ' ' in trade_item else trade_item
        output.append(f'\ttrade {trade_name} {value}')

    # Fleet
    output.extend([
        '\tfleet "Small Northern Planets" 300' ,
        '\tfleet "Small Republic Planets" 600' ,
        '\tfleet "Small Fields Merchants" 400'
    ])

    # Append objects
    output.extend(object_lines)

    logging.debug(f"System {system_name} generated with {len(output)} lines")
    return '\n'.join(output) + '\n'


def generate_system(row: pd.Series) -> str:
    system_name, _ = get_system_name(row)
    star_class = str(row.get('star_image_key', 'G'))
    binary = float(row.get('binary_candidate', 0.0))

    total_habitability = 0
    system_minables = set()
    landable_count = 0
    object_lines = []

    # Primary star
    primary_star = get_star_data(star_class)
    primary_sprite = random.choice(primary_star['sprites'])
    primary_type = primary_star['type']
    total_habitability += primary_star['base_habitability']
    attributes = get_star_attributes(star_class, primary_type)

    object_lines.append('\tobject')
    object_lines.append(f'\t\tsprite "{primary_sprite}"')
    distance, period, offset = get_star_params(primary_type)
    object_lines.append(f'\t\tdistance {distance:.2f}')
    object_lines.append(f'\t\tperiod {period:.2f}')
    object_lines.append(f'\t\toffset {offset:.0f}')

    # Binary star
    if binary > 0.5:
        secondary_star = random.choice(star_image)
        secondary_sprite = random.choice(secondary_star['sprites'])
        secondary_type = secondary_star['type']
        object_lines.append('\tobject')
        object_lines.append(f'\t\tsprite "{secondary_sprite}"')
        distance, period, offset = get_star_params(secondary_type)
        object_lines.append(f'\t\tdistance {distance + random.uniform(10, 50):.2f}')
        object_lines.append(f'\t\tperiod {period * 2:.2f}')
        object_lines.append(f'\t\toffset {offset + random.uniform(0, 180):.0f}')

    # Generate planets
    planets_data = generate_planets_from_zones(primary_star['base_habitability'])

    # Filter landables
    landable_planets = []
    for planet in planets_data:
        p_class = planet.get('class')
        if p_class not in planet_classes:
            continue
        p_data = planet_classes[p_class]
        system_minables.update(p_data['dominant_materials'])
        if p_data['base_habitability'] >= 3000 or p_class in ['M', 'G', 'L']:
            landable_planets.append(planet)

    # Ensure at least one landable
    if not landable_planets and planets_data:
        landable_planets.append(planets_data[0])

    planet_idx = 1
    for planet in planets_data:
        p_class = planet.get('class')
        if p_class not in planet_classes:
            continue
        p_data = planet_classes[p_class]
        is_landable = planet in landable_planets
        planet_name = f"{system_name}-{to_roman(planet_idx)}" if is_landable else ''
        if is_landable:
            landable_count += 1
            total_habitability += p_data['base_habitability']

        # Begin planet block
        planet_block = []
        planet_block.append(f'\tobject {planet_name}' if planet_name else '\tobject')
        planet_block.append(f'\t\tsprite "{random.choice(p_data["planet_sprites"])}"')
        orbital_dist = planet['distance'] * 100
        planet_block.append(f'\t\tdistance {orbital_dist:.2f}')
        planet_block.append(f'\t\tperiod {random.uniform(100, 1000):.2f}')

        # Add moons (properly nested)
        scale = math.sqrt(1000 / max(1.0, primary_star['base_habitability']))
        zone_name = next((z for z, z_data in planetary_zones.items()
                          if z_data['distance_range_au'][0] * scale <= planet['distance'] <=
                          z_data['distance_range_au'][1] * scale), None)
        moon_count = np.random.poisson(planetary_zones[zone_name]['average_major_moons']) if zone_name else 0
        for _ in range(moon_count):
            planet_block.append(f'\t\tobject')
            planet_block.append(f'\t\t\tsprite "planet/moon{random.randint(0, 3)}"')
            planet_block.append(f'\t\t\tdistance {random.uniform(0.1, 0.5):.2f}')
            planet_block.append(f'\t\t\tperiod {random.uniform(10, 50):.2f}')

        object_lines.extend(planet_block)
        planet_idx += 1

    # Add station
    landable_count += 1
    object_lines.append(f'\tobject "{system_name}-Station"')
    object_lines.append(f'\t\tsprite "planet/station/station{random.randint(0, 2)}"')
    object_lines.append(f'\t\tdistance {random.uniform(500, 1000):.0f}')
    object_lines.append(f'\t\tperiod {random.uniform(500, 1500):.0f}')

    # System header
    scale = math.sqrt(1000 / max(1.0, primary_star['base_habitability']))
    output = [
        f'system "{system_name}"',
        f'\tpos {row.get("flat_x", 0.0):.1f} {row.get("flat_y", 0.0):.1f}',
        '\tgovernment Republic',
        f'\tattributes "{attributes}"',
        '\tarrival none',
        '\tlink none',
        f'\thabitable {total_habitability:.1f}',
        f'\tbelt {random.randint(1000, 3000) * scale:.0f}'
    ]

    # Asteroids
    asteroid_count = random.randint(2, 5)
    if any(z for z in planets_data if
           planetary_zones['asteroid_belt_zone']['distance_range_au'][0] * scale <= z['distance'] <=
           planetary_zones['asteroid_belt_zone']['distance_range_au'][1] * scale):
        asteroid_count += random.randint(1, 3)
    for _ in range(asteroid_count):
        a_type = random.choice(asteroid_types)
        count = random.randint(1, 50)
        speed = random.uniform(1.0, 6.0)
        output.append(f'\tasteroids "{a_type}" {count} {speed:.2f}')

    # Minables
    for zone_name, z_data in planetary_zones.items():
        system_minables.update([m for m in z_data['dominant_materials'] if m in valid_minables])
    system_minables = sorted([m for m in system_minables if m in valid_minables])
    for minable in system_minables:
        count = random.randint(1, 20)
        speed = random.uniform(2.0, 6.0)
        output.append(f'\tminables {minable} {count} {speed:.2f}')

    # Trade
    for trade_item in sorted(all_trade_goods):
        value = random.randint(200, 600)
        trade_name = f'"{trade_item}"' if ' ' in trade_item else trade_item
        output.append(f'\ttrade {trade_name} {value}')

    # Fleets
    output.extend([
        '\tfleet "Small Northern Planets" 300',
        '\tfleet "Small Republic Planets" 600',
        '\tfleet "Small Fields Merchants" 400'
    ])

    # Add all system objects
    output.extend(object_lines)

    return '\n'.join(output) + '\n'

def main():
    """Generate systems from CSV."""
    logging.info("Starting script execution")
    csv_path = r"C:/Users/luser/OneDrive/Python_script/GH_GAIA/GAIA_Plus.csv"
    logging.info(f"Attempting to read CSV: {os.path.abspath(csv_path)}")

    try:
        df = pd.read_csv(csv_path)
        logging.info(f"CSV loaded successfully, {len(df)} rows")
    except FileNotFoundError as e:
        logging.error(f"CSV file not found: {e}")
        return
    except pd.errors.EmptyDataError as e:
        logging.error(f"CSV file is empty: {e}")
        return
    except Exception as e:
        logging.error(f"Error reading CSV: {e}")
        return

    if df.empty:
        logging.warning("CSV is empty, no systems will be generated")
        return

    systems = []
    for idx , row in df.iterrows():
        logging.debug(f"Processing row {idx}: sinbad_name={row.get('sinbad_name' , 'N/A')}")
        system_output = generate_system(row)
        if system_output.strip():
            systems.append(system_output)
        else:
            logging.warning(f"No output generated for row {idx}")

    logging.info(f"Generated {len(systems)} systems")

    output_file = 'map_systems_new.txt'
    try:
        with open(output_file , 'w' , encoding='utf-8') as f:
            f.write('\n\n'.join(systems))
        logging.info(f"Output written to {os.path.abspath(output_file)}")
    except Exception as e:
        logging.error(f"Failed to write output file: {e}")
        return


if __name__ == '__main__':
    main()