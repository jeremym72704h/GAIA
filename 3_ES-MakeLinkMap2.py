import pandas as pd
import numpy as np
import logging
import os
import math
import networkx as nx
import matplotlib.pyplot as plt
from datetime import datetime
import base64
import matplotlib

# Set Matplotlib's logger to a higher level!
matplotlib_logger = logging.getLogger('matplotlib')
matplotlib_logger.setLevel(logging.WARNING)

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('GAIA_Plus_Thin_Map.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
i = 0


def decode_2d(b64: str) -> tuple[int, int]:
    b64 += '=' * ((4 - len(b64) % 4) % 4)
    val = int.from_bytes(base64.b64decode(b64), byteorder='big')
    x = (val >> 64) & ((1 << 64) - 1)
    y = val & ((1 << 64) - 1)
    return x, y

def create_gravity_well_map(input_path: str, output_path: str) -> None:
    try:
        # Read the thinned CSV
        df = pd.read_csv(input_path)
        logging.info(f"Loaded thinned CSV with {len(df)} rows from {input_path}")
    except FileNotFoundError as e:
        logging.error(f"Input file not found: {e}")
        return
    except Exception as e:
        logging.error(f"Error reading CSV: {e}")
        return

    logger.info(f"CSV imported to Dataframe")
    # Decode base64_2D grid coordinates into integers
    df[['grid_x', 'grid_y']] = df['base64_2D'].apply(
        lambda b: pd.Series(decode_2d(b))
    )
    x_coords = df['grid_x'].values
    y_coords = df['grid_y'].values
    grav_force = df['gravitational_force'].values
    base64_2D = df['base64_2D'].values

    # Determine grid bounds and resolution
    x_min, x_max = min(x_coords), max(x_coords)
    y_min, y_max = min(y_coords), max(y_coords)
    grid_size_x, grid_size_y = 300, 20
    x_grid = np.linspace(x_min, x_max, grid_size_x)
    y_grid = np.linspace(y_min, y_max, grid_size_y)

    # Create a 2D interpolation of gravitational force
    X, Y = np.meshgrid(x_grid, y_grid)
    grav_map = np.zeros_like(X, dtype=float)
    for i in range(len(x_coords)):
        dist = np.sqrt((X - x_coords[i])**2 + (Y - y_coords[i])**2)
        weight = 1 / (dist + 1e-10)
        grav_map += weight * grav_force[i]
    grav_map /= np.sum(weight, axis=0)

    # Identify gravity well peaks
    peaks = []
    for i in range(len(x_coords)):
        grid_x_idx = np.abs(x_grid - x_coords[i]).argmin()
        grid_y_idx = np.abs(y_grid - y_coords[i]).argmin()
        if grav_map[grid_y_idx, grid_x_idx] > np.mean(grav_force):
            peaks.append((base64_2D[i], x_coords[i], y_coords[i], grav_force[i]))
    logging.info(f"Identified {len(peaks)} gravity well peaks")

    # Categorize systems
    threshold_high = np.percentile(grav_force, 90)
    threshold_med = np.percentile(grav_force, 50)
    rivers = [(c, x, y, g) for c, x, y, g in peaks if g >= threshold_high]
    creeks = [(c, x, y, g) for c, x, y, g in peaks if threshold_med <= g < threshold_high]
    brooks = [(c, x, y, g) for c, x, y, g in peaks if g < threshold_med]
    logging.info(f"Classified: {len(rivers)} rivers, {len(creeks)} creeks, {len(brooks)} brooks")

    # Create graph
    G = nx.Graph()
    for cube, x, y, g in peaks:
        G.add_node(cube, pos=(x, y), grav=g)

    # Connect rivers
    for i, (c1, x1, y1, g1) in enumerate(rivers):
        for j, (c2, x2, y2, g2) in enumerate(rivers[i+1:], start=i+1):
            dist = abs(x1 - x2) + abs(y1 - y2)
            if dist < 50:
                G.add_edge(c1, c2, weight=dist)

    # Connect creeks to rivers
    for c1, x1, y1, g1 in creeks:
        min_dist = float('inf')
        nearest_river = None
        for c2, x2, y2, g2 in rivers:
            dist = abs(x1 - x2) + abs(y1 - y2)
            if dist < min_dist:
                min_dist = dist
                nearest_river = c2
        if nearest_river and min_dist < 75:
            G.add_edge(c1, nearest_river, weight=min_dist)

    # Connect brooks to creeks or rivers
    for b1, x1, y1, g1 in brooks:
        min_dist = float('inf')
        nearest = None
        targets = creeks + rivers
        for c2, x2, y2, g2 in targets:
            dist = abs(x1 - x2) + abs(y1 - y2)
            if dist < min_dist:
                min_dist = dist
                nearest = c2
        if nearest and min_dist < 100:
            G.add_edge(b1, nearest, weight=min_dist)

    # Output linkages to CSV
    if i % 100 == 0:
        logger.info(f"Processed {i} cubes")
    edges = [(u, v, d['weight']) for u, v, d in G.edges(data=True)]
    if edges:
        # Build initial edge list
        edges_df = pd.DataFrame(edges , columns=['source' , 'target' , 'distance'])

        # Merge metadata for source and target
        metadata_cols = ['base64_2D' , 'StarClass' , 'Sub_Class' , 'quadrant' , 'gravitational_force' , 'rarity_score']
        metadata_cols = [col for col in metadata_cols if col in df.columns]

        source_metadata = df[metadata_cols].rename(columns=lambda c: f"source_{c}" if c != 'base64_2D' else 'source')
        target_metadata = df[metadata_cols].rename(columns=lambda c: f"target_{c}" if c != 'base64_2D' else 'target')

        edges_df = edges_df.merge(source_metadata , on='source' , how='left')
        edges_df = edges_df.merge(target_metadata , on='target' , how='left')

        os.makedirs(os.path.dirname(output_path.replace('.png', '.csv')), exist_ok=True)
        edges_df.to_csv(output_path.replace('.png', '.csv'), index=False)
        logging.info(f"Wrote {len(edges)} linkages to {output_path.replace('.png', '.csv')}")

    # Save gravity well map
    plt.figure(figsize=(10, 5))
    plt.contourf(X, Y, grav_map, levels=20, cmap='terrain')
    plt.colorbar(label='Gravitational Force')
    plt.scatter(x_coords, y_coords, c=grav_force, cmap='terrain', s=10, label='Systems')
    plt.xlabel('Flat X')
    plt.ylabel('Flat Y')
    plt.title('Gravity Well Map')
    date_code = datetime.now().strftime('%Y%m%d_%H%M')
    image_output_path = output_path.replace('[datecode]', date_code)
    os.makedirs(os.path.dirname(image_output_path), exist_ok=True)
    plt.savefig(image_output_path)
    plt.close()
    logging.info(f"Saved gravity well map to {image_output_path}")

def main():
    input_path = r"C:/Users/luser/OneDrive/Python_script/GAIA/GAIA_Plus_Thined.csv"
    output_path = r"C:/Users/luser/OneDrive/Python_script/GAIA/GAIA_Plus_Thin_Map.png"
    logging.info(f"Starting gravity well map generation at {input_path} to {output_path}")
    create_gravity_well_map(input_path, output_path)

if __name__ == '__main__':
    main()
