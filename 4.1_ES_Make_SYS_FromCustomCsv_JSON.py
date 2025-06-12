import csv
import json
from collections import defaultdict
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

logger = logging.getLogger(__name__)
i = 0

class System:
    def __init__(self, name):
        self.name = name
        self.star = None
        self.government = None
        self.pos = None
        self.links = []

    def to_dict(self):
        return {
            "name": self.name,
            "star": self.star,
            "government": self.government,
            "pos": list(self.pos) if self.pos else None,
            "links": self.links
        }

# Load systems from CSV
def load_systems_from_csv(csv_path):
    systems = {}

    # First pass: create all systems
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            name = row["Name_two"].strip()
            if name not in systems:
                systems[name] = System(name)

            sys = systems[name]
            # Position
            try:
                sys.pos = (int(row["x"]), int(row["y"]))
            except:
                pass

            # Government
            if row.get("government"):
                sys.government = row["government"].strip()

            # Star (optional)
            if row.get("star"):
                sys.star = row["star"].strip()

    # Second pass: populate links
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            name = row["Name_two"].strip()
            sys = systems[name]

            if "links" in row and row["links"]:
                link_names = [ln.strip() for ln in row["links"].split(",")]
                for link_name in link_names:
                    if link_name not in systems:
                        systems[link_name] = System(link_name)  # Create placeholder
                    if link_name not in sys.links:
                        sys.links.append(link_name)

    return systems

# Save to JSON
def save_systems_to_json(systems, json_path):
    system_list = [s.to_dict() for s in systems.values()]
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(system_list, f, indent=2)

# Entry point
if __name__ == "__main__":
    csv_input = r"C:\Apps\Scripted\GAIA\GAIA_Plus_Thined.csv"            # Change this if needed
    json_output = r"C:\Apps\Scripted\GAIA\systems.json"     # Output file

    systems = load_systems_from_csv(csv_input)
    save_systems_to_json(systems, json_output)
    print(f"Exported {len(systems)} systems to {json_output}")
