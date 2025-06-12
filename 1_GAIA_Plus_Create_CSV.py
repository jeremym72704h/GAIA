import time
import math
import random
import pandas as pd
import numpy as np
import os
import re
import base64
from astroquery.gaia import Gaia
from astroquery.simbad import Simbad
from astropy.coordinates import SkyCoord
import astropy.units as u
import requests
from collections import defaultdict

# Configure logging
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Base64 encoding functions for cube and 2D grid systems
def encode_axis(n):
    """Encodes an integer 0–262,143 into 3-character Base64."""
    n = max(0, min(int(n), 262143))  # Clip to 18-bit range
    b = bytes([(n >> 12) & 0x3F, (n >> 6) & 0x3F, n & 0x3F])
    return base64.b64encode(b).decode('ascii')[:3]

def encode_cube(x, y, z):
    """Encodes 3D coordinates into a 9-character Base64 string."""
    return encode_axis(x) + encode_axis(y) + encode_axis(z)

def encode_2d(x, y):
    x = int(x)
    y = int(y)
    val = (x << 64) + y  # 128-bit total
    b = val.to_bytes(16, byteorder='big')  # 16 bytes = 128 bits
    return base64.b64encode(b).decode('ascii').rstrip('=')  # typically 22 chars

def decode_2d(b64):
    b64 += '=' * ((4 - len(b64) % 4) % 4)  # pad to multiple of 4
    val = int.from_bytes(base64.b64decode(b64), byteorder='big')
    x = (val >> 64) & ((1 << 64) - 1)
    y = val & ((1 << 64) - 1)
    return x, y


# Output files
output_dir = r"C:/Users/luser/OneDrive/Python_script/GAIA/"
endless_sky_csv = r"C:/Users/luser/OneDrive/Python_script/GAIA/GAIA_Plus.csv"
endless_sky_no_simbad_csv = r"C:/Users/luser/OneDrive/Python_script/GAIA/GAIA_Plus_Simbad.csv"
append_mode = False

# Star classification table
star_image_key = [
    {"class": "O", "type": "giant", "sprites": ["star/o0", "star/o0_supergiant", "star/o1"]},
    {"class": "O", "type": "normal", "sprites": ["star/o2", "star/o3", "star/o1_giant"]},
    {"class": "O", "type": "dwarf", "sprites": ["star/o4", "star/o5", "star/o2_dwarf", "star/o6"]},
    {"class": "B", "type": "giant", "sprites": ["star/b0", "star/b0_supergiant"]},
    {"class": "B", "type": "normal", "sprites": ["star/b1", "star/b1_giant", "star/b3"]},
    {"class": "B", "type": "dwarf", "sprites": ["star/b2", "star/b2_dwarf", "star/b4", "star/b5"]},
    {"class": "A", "type": "giant", "sprites": ["star/a0"]},
    {"class": "A", "type": "normal", "sprites": ["star/a1", "star/a3", "star/a5"]},
    {"class": "A", "type": "dwarf", "sprites": ["star/a6", "star/a8"]},
    {"class": "F", "type": "giant", "sprites": ["star/f0", "star/f0_supergiant"]},
    {"class": "F", "type": "normal", "sprites": ["star/f1", "star/f1_giant", "star/f3"]},
    {"class": "F", "type": "dwarf", "sprites": ["star/f2", "star/f2_dwarf", "star/f4"]},
    {"class": "G", "type": "giant", "sprites": ["star/g0", "star/g0_supergiant"]},
    {"class": "G", "type": "normal", "sprites": ["star/g1", "star/g1_giant", "star/g3"]},
    {"class": "G", "type": "dwarf", "sprites": ["star/g2", "star/g2_dwarf", "star/g4", "star/g5"]},
    {"class": "K", "type": "giant", "sprites": ["star/k0", "star/k0_supergiant"]},
    {"class": "K", "type": "normal", "sprites": ["star/k1", "star/k1_giant", "star/k3"]},
    {"class": "K", "type": "dwarf", "sprites": ["star/k2", "star/k2_dwarf", "star/k4", "star/k5"]},
    {"class": "M", "type": "giant", "sprites": ["star/m0", "star/m0_supergiant"]},
    {"class": "M", "type": "normal", "sprites": ["star/m1", "star/m1_giant", "star/m2", "star/m2_giant"]},
    {"class": "M", "type": "dwarf", "sprites": ["star/m3", "star/m3_dwarf", "star/m4", "star/m4_dwarf", "star/m5", "star/m6"]}
]


def get_simbad_names_sync(df_batch , default_names):
    """Query SIMBAD for additional names using RA and Dec, return only the primary name (main_id)."""
    custom_simbad = Simbad()
    custom_simbad.add_votable_fields('main_id' , 'ids' , 'ra' , 'dec')
    names_dict = {}
    batch_ids = df_batch['source_id'].tolist()
    total = len(batch_ids)
    found = 0

    for idx , sid in enumerate(batch_ids):
        max_retries = 3
        retry_delay = 1
        success = False

        # Validate RA/Dec first
        ra = df_batch.loc[df_batch['source_id'] == sid , 'ra'].iloc[0]
        dec = df_batch.loc[df_batch['source_id'] == sid , 'dec'].iloc[0]
        if not (-360 <= ra <= 360) or not (-90 <= dec <= 90):
            logger.error(f"Invalid RA/Dec for source_id {sid}: ra={ra}, dec={dec}")
            names_dict[sid] = default_names[sid]
            continue

        query_coord = SkyCoord(ra=ra * u.degree , dec=dec * u.degree , frame='icrs')

        for attempt in range(max_retries):
            try:
                # Try synchronous query first
                result = custom_simbad.query_region(query_coord , radius=30 * u.arcsec)
                success = True
            except Exception as e:
                if "synchronous TAP query was limited to 1080 seconds" in str(e):
                    logger.warning(f"TAP timeout for source_id {sid}. Switching to async mode.")
                    try:
                        result = custom_simbad.query_region_async(query_coord , radius=30 * u.arcsec).get()
                        success = True
                    except Exception as async_e:
                        logger.error(f"Async query failed for source_id {sid}: {async_e}")
                else:
                    logger.warning(
                        f"Attempt {attempt + 1} failed for source_id {sid}: {e}. Retrying in {retry_delay}s...")
                    time.sleep(retry_delay)
                    retry_delay *= 2
                    continue

            if success:
                name = default_names[sid]
                if result is not None and len(result) > 0:
                    main_id_col = 'main_id' if 'main_id' in result.colnames else 'MAIN_ID'
                    best_match_idx = 0
                    min_distance = float('inf')
                    for i in range(len(result)):
                        result_coord = SkyCoord(ra=result['ra'][i] * u.degree , dec=result['dec'][i] * u.degree ,
                                                frame='icrs')
                        distance = query_coord.separation(result_coord).arcsec
                        if result[main_id_col][i].startswith('*') and distance < min_distance:
                            best_match_idx = i
                            min_distance = distance
                    name = result[main_id_col][best_match_idx]
                    found += 1
                    if found <= 5:
                        logger.info(
                            f"Simbad source_id {sid} at RA={ra}°, Dec={dec}° found {name} (distance={min_distance:.2f} arcsec)")
                else:
                    logger.info(f"Simbad source_id {sid} at RA={ra}°, Dec={dec}° found None, using default {name}")
                names_dict[sid] = name
                break

        if not success:
            logger.error(f"Failed to query SIMBAD for source_id {sid} after {max_retries} attempts")
            names_dict[sid] = default_names[sid]
        time.sleep(0.1)  # Reduced sleep for async queries

    logger.info(f"SIMBAD query summary: Found matches for {found}/{total} stars ({found / total * 100:.1f}%)")
    return names_dict

def get_simbad_names(df_batch, default_names):
    """Query SIMBAD for additional names using RA and Dec, return only the primary name (main_id)."""
    custom_simbad = Simbad()
    custom_simbad.add_votable_fields('main_id', 'ids', 'ra', 'dec')
    names_dict = {}
    batch_ids = df_batch['source_id'].tolist()
    total = len(batch_ids)
    found = 0

    for idx, sid in enumerate(batch_ids):
        max_retries = 3
        retry_delay = 1
        success = False
        for attempt in range(max_retries):
            try:
                ra = df_batch.loc[df_batch['source_id'] == sid, 'ra'].iloc[0]
                dec = df_batch.loc[df_batch['source_id'] == sid, 'dec'].iloc[0]

                if not (-360 <= ra <= 360) or not (-90 <= dec <= 90):
                    raise ValueError(f"Invalid RA/Dec for source_id {sid}: ra={ra}, dec={dec}")

                query_coord = SkyCoord(ra=ra * u.degree, dec=dec * u.degree, frame='icrs')
                result = custom_simbad.query_region(query_coord, radius=30 * u.arcsec)

                name = default_names[sid]
                if result is not None and len(result) > 0:
                    main_id_col = 'main_id' if 'main_id' in result.colnames else 'MAIN_ID'
                    best_match_idx = 0
                    min_distance = float('inf')
                    for i in range(len(result)):
                        result_coord = SkyCoord(ra=result['ra'][i] * u.degree, dec=result['dec'][i] * u.degree, frame='icrs')
                        distance = query_coord.separation(result_coord).arcsec
                        if result[main_id_col][i].startswith('*') and distance < min_distance:
                            best_match_idx = i
                            min_distance = distance
                    name = result[main_id_col][best_match_idx]
                    found += 1
                    if found <= 5:
                        logger.info(f"Simbad source_id {sid} at RA={ra}°, Dec={dec}° found {name}")
                else:
                    logger.info(f"Simbad source_id {sid} at RA={ra}°, Dec={dec}° found None, using default {name}")

                names_dict[sid] = name
                time.sleep(0.3)
                success = True
                break
            except (TimeoutError, ConnectionError, requests.exceptions.RequestException) as e:
                if attempt < max_retries - 1:
                    logger.warning(f"Attempt {attempt + 1} failed for source_id {sid}: {e}. Retrying in {retry_delay}s...")
                    time.sleep(retry_delay)
                    retry_delay *= 2
                else:
                    logger.error(f"Failed to query SIMBAD for source_id {sid} after {max_retries} attempts: {e}")
                    names_dict[sid] = default_names[sid]
                    break
            except Exception as e:
                logger.error(f"Unexpected error querying SIMBAD for source_id {sid}: {e}")
                names_dict[sid] = default_names[sid]
                break
        if not success and sid not in names_dict:
            names_dict[sid] = default_names[sid]

    logger.info(f"SIMBAD query summary: Found matches for {found}/{total} stars ({found/total*100:.1f}%)")
    return names_dict

def get_star_classification(star_class, luminosity_class):
    """Map star_class and luminosity_class to StarClass and Sub_Class from the table."""
    sub_class_map = {"I": "giant", "V": "dwarf"}
    sub_class = sub_class_map.get(luminosity_class, "normal")
    for entry in star_image_key:
        if entry["class"] == star_class and entry["type"] == sub_class:
            return {
                "StarClass": star_class,
                "Sub_Class": sub_class,
                "Sys_Icons": entry["sprites"][0]
            }
    return {"StarClass": star_class, "Sub_Class": sub_class, "Sys_Icons": f"star/{star_class}0"}

def calculate_remaining_mass_earth(mass):
    """Calculate remaining mass in Earth masses (0.14% of total system mass)."""
    EARTH_MASS_KG = 5.972e24
    STAR_MASS_FRACTION = 0.9986
    if pd.isna(mass):
        return 0.0
    total_system_mass = mass / STAR_MASS_FRACTION
    remaining_mass_kg = total_system_mass - mass
    return max(0.0, remaining_mass_kg / EARTH_MASS_KG)

def calculate_3d_coordinates(row):
    """Calculate 3D Cartesian coordinates from RA, Dec, and parallax."""
    ra_rad = math.radians(row['ra'])
    dec_rad = math.radians(row['dec'])
    distance = 1000 / row['parallax'] if row['parallax'] > 0 else 100000
    x = distance * math.cos(dec_rad) * math.cos(ra_rad)
    y = distance * math.cos(dec_rad) * math.sin(ra_rad)
    z = distance * math.sin(dec_rad)
    return x, y, z

def approximate_bv(bp_rp):
    """Approximate B-V color index from Gaia's bp_rp using a polynomial fit."""
    if pd.isna(bp_rp):
        return np.nan
    a = -0.0238
    b = 0.6485
    c = -0.0175
    return a + b * bp_rp + c * (bp_rp ** 2)

def determine_quadrant(row):
    """Approximate Galactic quadrant using Galactic longitude (l)."""
    l = row['l'] if 'l' in row else 0
    if 0 <= l < 90:
        return "1"
    elif 90 <= l < 180:
        return "2"
    elif 180 <= l < 270:
        return "3"
    else:
        return "4"

def estimate_mass(bp_rp, teff, abs_mag):
    """Estimate stellar mass based on bp_rp, teff, and abs_mag."""
    if pd.isna(bp_rp) or pd.isna(teff) or pd.isna(abs_mag):
        return 0.5 * 1.989e30
    if bp_rp < 0.5:
        class_type = "hot_main"
    elif bp_rp < 1.5:
        class_type = "dwarf"
    else:
        class_type = "cool_dwarf"

    if teff >= 6000:
        mass = 1.0
    elif teff >= 4000:
        mass = 0.5
    else:
        mass = 0.1

    if abs_mag < 5:
        mass *= 1.5
    return mass * 1.989e30

def calculate_absolute_magnitude(phot_g_mean_mag, parallax):
    """Calculate absolute magnitude from apparent magnitude and parallax."""
    if pd.isna(parallax) or parallax <= 0:
        return np.nan
    distance_pc = 1000 / parallax
    return phot_g_mean_mag - 5 * math.log10(distance_pc) + 5

def estimate_luminosity(abs_mag, teff):
    """Estimate luminosity in solar units using absolute magnitude and temperature."""
    if pd.isna(abs_mag) or pd.isna(teff):
        return 1.0
    if teff > 30000:
        bc = -0.2
    elif teff > 10000:
        bc = -0.1
    elif teff > 7500:
        bc = 0.0
    elif teff > 6000:
        bc = 0.1
    elif teff > 4000:
        bc = 0.2
    else:
        bc = 0.3
    m_bol = abs_mag + bc
    m_bol_sun = 4.74
    return 10 ** (0.4 * (m_bol_sun - m_bol))

def estimate_age(teff):
    """Estimate stellar age in Gyr."""
    if pd.isna(teff):
        return 5.0
    return max(0, min(13, 10 - (teff / 10000)))

def assign_planet_types(star_class, distance):
    """Assign planet types based on star class and distance."""
    if pd.isna(distance):
        distance = 100000
    if star_class in ["O", "B"]:
        return "Gas Giant"
    elif star_class in ["A", "F", "G"] and distance < 5000:
        return "Rocky, Gas Giant"
    else:
        return "Rocky"

def determine_luminosity_class(abs_mag):
    """Determine luminosity class based on abs_g_mag."""
    if pd.isna(abs_mag):
        return "V"
    if abs_mag < 0:
        return "I"
    else:
        return "V"

def classify_star(teff):
    """Classify star based on temperature (teff_gspphot)."""
    if pd.isna(teff):
        return "M"
    if teff > 30000:
        return "O"
    elif 10000 <= teff < 30000:
        return "B"
    elif 7500 <= teff < 10000:
        return "A"
    elif 6000 <= teff < 7500:
        return "F"
    elif 5200 <= teff < 6000:
        return "G"
    elif 3700 <= teff < 5200:
        return "K"
    else:
        return "M"

def calculate_relative_force(mass, distance_pc):
    """Calculate relative gravitational force."""
    G = 6.674e-11
    M_earth = 5.972e24
    pc_to_m = 3.0857e16
    distance_m = distance_pc * pc_to_m
    force = G * mass * M_earth / (distance_m ** 2)
    min_mass = 0.1 * 1.989e30
    max_distance_m = 100000 * pc_to_m
    min_force = G * min_mass * M_earth / (max_distance_m ** 2)
    return force / min_force if min_force > 0 else 1.0

# Create the output directory if it doesn't exist
try:
    os.makedirs(output_dir, exist_ok=True)
except PermissionError as e:
    raise PermissionError(f"Cannot create directory at {output_dir}. Check write permissions: {e}")

# Initialize Simbad custom query
custom_simbad = Simbad()
custom_simbad.add_votable_fields('main_id', 'ids')

# Batch query Gaia DR3 by RA and Dec ranges
batch_size = 10000
ra_step = 1
dec_step = 1
ra_ranges = [(i, i + ra_step) for i in range(0, 360, ra_step)]
dec_ranges = [(i, i + dec_step) for i in range(-90, 90, dec_step)]

for ra_idx, (ra_start, ra_end) in enumerate(ra_ranges):
    for dec_idx, (dec_start, dec_end) in enumerate(dec_ranges):
        try:
            print(f"Querying Gaia DR3 for RA range {ra_start} to {ra_end}, Dec range {dec_start} to {dec_end}...")
            query = f"""
            SELECT TOP {batch_size} 
                gs.source_id, gs.ra, gs.dec, gs.parallax, 
                gs.phot_g_mean_mag, gs.phot_bp_mean_mag, gs.phot_rp_mean_mag, 
                gs.bp_rp, gs.bp_g, gs.g_rp, gs.radial_velocity, 
                gs.l, gs.b, gs.ecl_lon, gs.ecl_lat,
                ap.teff_gspphot, ap.radius_gspphot
            FROM gaiadr3.gaia_source AS gs
            LEFT JOIN gaiadr3.astrophysical_parameters AS ap ON gs.source_id = ap.source_id
            WHERE gs.parallax > 0.01
            AND gs.ra BETWEEN {ra_start} AND {ra_end}
            AND gs.dec BETWEEN {dec_start} AND {dec_end}
            AND gs.ra IS NOT NULL AND gs.dec IS NOT NULL
            AND gs.phot_g_mean_mag IS NOT NULL
            AND gs.phot_bp_mean_mag IS NOT NULL
            AND gs.phot_rp_mean_mag IS NOT NULL
            AND ap.teff_gspphot IS NOT NULL
            AND gs.l IS NOT NULL
            """
            job = Gaia.launch_job(query)
            result = job.get_results()
            df = result.to_pandas()

            if df.empty:
                print(f"No data returned for RA range {ra_start} to {ra_end}, Dec range {dec_start} to {dec_end}, skipping...")
                continue

            print(f"Processing {len(df)} stars for RA range {ra_start} to {ra_end}, Dec range {dec_start} to {dec_end}...")

            df['Computed_Distance_Parsec'] = df['parallax'].apply(lambda p: 1000 / p if p > 0 else float('inf'))

            milkyway_stars = df[df['Computed_Distance_Parsec'] <= 100000].copy()

            if not milkyway_stars.empty:
                coords = milkyway_stars.apply(calculate_3d_coordinates, axis=1, result_type='expand')
                milkyway_stars[['x_Coord', 'y_Coord', 'z_Coord']] = coords

                # Calculate Base64 cube coordinates (1-light-year cubes)
                PARSEC_TO_LY = 3.26
                milkyway_stars['cube_x'] = ((milkyway_stars['x_Coord'] * PARSEC_TO_LY) / 1).astype(int) + 75000
                milkyway_stars['cube_y'] = ((milkyway_stars['y_Coord'] * PARSEC_TO_LY) / 1).astype(int) + 75000
                milkyway_stars['cube_z'] = ((milkyway_stars['z_Coord'] * PARSEC_TO_LY) / 1).astype(int) + 75000
                milkyway_stars['base64_Cube'] = milkyway_stars.apply(
                    lambda row: encode_cube(row['cube_x'], row['cube_y'], row['cube_z']),
                    axis=1
                )

                # Calculate Base64 2D grid coordinates (1-light-year grids)
                milkyway_stars['flat_x'] = milkyway_stars['x_Coord']
                milkyway_stars['flat_y'] = milkyway_stars['y_Coord'] + (milkyway_stars['z_Coord'] / 100)
                milkyway_stars['grid_x'] = ((milkyway_stars['flat_x'] * PARSEC_TO_LY) / 1).astype(int) + 75000
                milkyway_stars['grid_y'] = ((milkyway_stars['flat_y'] * PARSEC_TO_LY) / 1).astype(int) + 75000
                milkyway_stars['base64_2D'] = milkyway_stars.apply(
                    lambda row: encode_2d(row['grid_x'], row['grid_y']),
                    axis=1
                )

                milkyway_stars['quadrant'] = milkyway_stars.apply(determine_quadrant, axis=1)

                milkyway_stars['abs_g_mag'] = milkyway_stars.apply(
                    lambda row: calculate_absolute_magnitude(row['phot_g_mean_mag'], row['parallax']), axis=1)

                milkyway_stars['B_V'] = milkyway_stars['bp_rp'].apply(approximate_bv)

                milkyway_stars['mass'] = milkyway_stars.apply(
                    lambda row: estimate_mass(row['bp_rp'], row['teff_gspphot'], row['abs_g_mag']), axis=1)
                milkyway_stars['gravitational_force'] = milkyway_stars.apply(
                    lambda row: calculate_relative_force(row['mass'], row['Computed_Distance_Parsec']), axis=1)

                milkyway_stars['star_class'] = milkyway_stars['teff_gspphot'].apply(classify_star)
                milkyway_stars['luminosity_class'] = milkyway_stars['abs_g_mag'].apply(determine_luminosity_class)

                milkyway_stars[['StarClass', 'Sub_Class', 'Sys_Icons']] = milkyway_stars.apply(
                    lambda row: pd.Series(get_star_classification(row['star_class'], row['luminosity_class'])), axis=1)

                milkyway_stars['Remaining_Mass_Earth'] = milkyway_stars['mass'].apply(calculate_remaining_mass_earth)

                milkyway_stars['planet_types'] = milkyway_stars.apply(
                    lambda row: assign_planet_types(row['StarClass'], row['Computed_Distance_Parsec']), axis=1)
                milkyway_stars['age_gyr'] = milkyway_stars['teff_gspphot'].apply(estimate_age)
                milkyway_stars['game_x'] = milkyway_stars['flat_x'] / 1000
                milkyway_stars['game_y'] = milkyway_stars['flat_y'] / 1000
                milkyway_stars['game_z'] = milkyway_stars['z_Coord'] / 1000
                milkyway_stars['estimate_lum'] = milkyway_stars.apply(
                    lambda row: estimate_luminosity(row['abs_g_mag'], row['teff_gspphot']), axis=1)

                # Assign trade values
                trade_goods = {
                    "Clothing": (250, 255),
                    "Electronics": (600, 605),
                    "Equipment": (361, 366),
                    "Food": (100, 105),
                    "Heavy Metals": (800, 805),
                    "Luxury Goods": (900, 905),
                    "Industrial": (650, 655),
                    "Medical": (500, 505),
                    "Metal": (200, 205),
                    "Plastic": (300, 305)
                }
                trade_data = [
                    {good: random.uniform(min_val, max_val) for good, (min_val, max_val) in trade_goods.items()}
                    for _ in range(len(milkyway_stars))
                ]
                for good in trade_goods:
                    milkyway_stars[good] = [data[good] for data in trade_data]

                # Flag potential binary systems (cubes with exactly 2 stars)
                cube_counts = milkyway_stars['base64_Cube'].value_counts()
                milkyway_stars['binary_candidate'] = milkyway_stars['base64_Cube'].map(cube_counts == 2)

                grid_index = str(ra_idx * 180 + dec_idx).zfill(4)
                milkyway_stars['counter'] = [str(i).zfill(4) for i in range(len(milkyway_stars))]
                milkyway_stars['Name_two'] = milkyway_stars.apply(
                    lambda row: f"S{row['quadrant']}{grid_index}-{row['counter']}",
                    axis=1
                )

                # Calculate 2D and 3D sectors (16,300-light-year cubes)
                min_game_x = milkyway_stars['game_x'].min()
                min_game_y = milkyway_stars['game_y'].min()
                min_game_z = milkyway_stars['game_z'].min()
                milkyway_stars['game_x_adj'] = milkyway_stars['game_x'] - min_game_x
                milkyway_stars['game_y_adj'] = milkyway_stars['game_y'] - min_game_y
                milkyway_stars['game_z_adj'] = milkyway_stars['game_z'] - min_game_z
                milkyway_stars['sector_x'] = (milkyway_stars['game_x_adj'] / 5).astype(int)
                milkyway_stars['sector_y'] = (milkyway_stars['game_y_adj'] / 5).astype(int)
                milkyway_stars['sector_z'] = (milkyway_stars['game_z_adj'] / 5).astype(int)
                milkyway_stars['2D_sector'] = milkyway_stars.apply(
                    lambda row: f"S{row['quadrant']}{str(row['sector_x'] * 20 + row['sector_y']).zfill(2)}",
                    axis=1
                )
                milkyway_stars['3D_sector'] = milkyway_stars.apply(
                    lambda row: f"S{row['quadrant']}{str(row['sector_z'] * 400 + row['sector_x'] * 20 + row['sector_y']).zfill(3)}",
                    axis=1
                )
                milkyway_stars = milkyway_stars.drop(columns=['cube_x', 'cube_y', 'cube_z', 'grid_x', 'grid_y', 'game_x_adj', 'game_y_adj', 'game_z_adj', 'sector_x', 'sector_y', 'sector_z'])

                simbad_batch_size = 100
                default_names = milkyway_stars.set_index('source_id')['Name_two'].to_dict()
                for start in range(0, len(milkyway_stars), simbad_batch_size):
                    df_batch = milkyway_stars[start:start + simbad_batch_size]
                    simbad_names = get_simbad_names(df_batch, default_names)
                    milkyway_stars.loc[df_batch.index, 'simbad_names'] = df_batch['source_id'].map(simbad_names)
                    time.sleep(1)

                milkyway_stars = milkyway_stars.drop(columns=['star_class', 'luminosity_class'])

                mode = 'a' if append_mode else 'w'
                header = not append_mode
                try:
                    milkyway_stars.to_csv(endless_sky_csv, mode=mode, header=header, index=False)
                    append_mode = True
                    print(f"Appended {len(milkyway_stars)} stars to {endless_sky_csv}")

                    no_simbad_matches = milkyway_stars[milkyway_stars['Name_two'] != milkyway_stars['simbad_names']]
                    no_simbad_matches.to_csv(endless_sky_no_simbad_csv, mode=mode, header=header, index=False)
                    print(f"Appended {len(no_simbad_matches)} stars with no SIMBAD name match to {endless_sky_no_simbad_csv}")
                except PermissionError as e:
                    print(f"Error writing to {endless_sky_csv} or {endless_sky_no_simbad_csv}: {e}")
                    continue

                append_mode = True

        except Exception as e:
            print(f"Error processing RA range {ra_start} to {ra_end}, Dec range {dec_start} to {dec_end}: {e}")
            continue

print("Processing complete.")
print(f"Endless Sky stars saved to {endless_sky_csv}")
print(f"Stars with no SIMBAD name match saved to {endless_sky_no_simbad_csv}")