import pandas as pd
import numpy as np
from collections import Counter
import base64
import logging

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('GAIA_Plus_Thin_Map.log'),
        logging.StreamHandler()
    ]
)

# === You must define this ===
PARSEC_TO_LY = 3.26156

# === Encode/Decode base64_2D ===
def encode_2d(x: int, y: int) -> str:
    x = int(x)
    y = int(y)
    val = (x << 64) + y
    b = val.to_bytes(16, byteorder='big')
    return base64.b64encode(b).decode('ascii').rstrip('=')


def decode_2d(b64: str) -> tuple[int, int]:
    b64 += '=' * ((4 - len(b64) % 4) % 4)  # Pad to multiple of 4
    val = int.from_bytes(base64.b64decode(b64), byteorder='big')
    x = (val >> 64) & ((1 << 64) - 1)
    y = val & ((1 << 64) - 1)
    return x, y


def get_neighbor_keys(base64_key: str) -> list[str]:
    gx, gy = decode_2d(base64_key)
    neighbors = []
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            nx, ny = gx + dx, gy + dy
            neighbors.append(encode_2d(nx, ny))
    return neighbors

# === Load Data ===
df = pd.read_csv("GAIA_Plus.csv")

# === Compute base64_2D if not already present ===
df['flat_x'] = df['x_Coord']
df['flat_y'] = df['y_Coord'] + (df['z_Coord'] / 100)
df['grid_x'] = ((df['flat_x'] * PARSEC_TO_LY)).astype(int) + 75000
df['grid_y'] = ((df['flat_y'] * PARSEC_TO_LY)).astype(int) + 75000
df['base64_2D'] = df.apply(lambda row: encode_2d(row['grid_x'], row['grid_y']), axis=1)

# === Local Rarity Algorithm ===
unique_stars = []

for cube_key in df['base64_2D'].unique():
    neighbor_keys = get_neighbor_keys(cube_key)
    neighbor_df = df[df['base64_2D'].isin(neighbor_keys)].copy()

    # Count StarClass/Sub_Class in neighborhood
    neighbor_counts = Counter(
        neighbor_df['StarClass'].astype(str) + "/" + neighbor_df['Sub_Class'].astype(str)
    )

    # Current cube's stars
    local_df = df[df['base64_2D'] == cube_key].copy()
    local_df['class_combo'] = local_df['StarClass'].astype(str) + "/" + local_df['Sub_Class'].astype(str)
    local_df['rarity_score'] = local_df['class_combo'].map(
        lambda c: 1 / (neighbor_counts[c] if neighbor_counts[c] else 1)
    )

    if not local_df.empty:
        most_unique_star = local_df.sort_values('rarity_score', ascending=False).iloc[0]
        unique_stars.append((cube_key, most_unique_star))

# === Display Result ===
print("\n=== Most Unique Star per base64_2D Cube (Local Rarity) ===\n")
for cube, star in unique_stars:
    print(f"Cube: {cube}")
    print(star[['source_id', 'StarClass', 'Sub_Class', 'rarity_score']])
    print("-" * 60)

# Build a DataFrame of just the unique stars
unique_df = pd.DataFrame([star for _, star in unique_stars])

# Save to CSV
output_path = "C:/Users/luser/OneDrive/Python_script/GH_GAIA/GAIA_Plus_Thined.csv"
unique_df.to_csv(output_path, index=False)

print(f"\n✅ Saved {len(unique_df)} unique stars to:\n{output_path}")
