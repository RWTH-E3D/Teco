"""
This example script can be used to load some materials from MaterialTemplates.json and
LcaData.json, using the En15804LcaData class.
It uses a custom Material class object instead of a Material class object from a Building instance.
"""


from __future__ import annotations
import json
from pathlib import Path

from teco.logic.buildingobjects.buildingphysics.en15804lcadata import En15804LcaData
from teco.data.input.material_input_json import load_material_id

# === Paths ===
HERE = Path(__file__).resolve().parent
LCA_FILE = HERE.parent / "data" / "input" / "inputdata" / "LcaData.json"
MAT_FILE = HERE.parent / "data" / "input" / "inputdata" / "MaterialTemplates.json"

# --- Minimal DataClassMock ---
class DataClassMock:
    """Provides the JSON bindings expected by material and LCA loaders."""
    def __init__(self, lca_json: Path, material_json: Path):
        with open(lca_json, encoding="utf-8") as f:
            self.lca_data_bind = json.load(f)
        with open(material_json, encoding="utf-8") as f:
            self.material_bind = json.load(f)

# --- Helper for readable output ---
def fmt(val):
    return "–" if val is None else f"{val:.4g}"

def print_material_summary(materials):
    print("\n=== Materials + EN15804 LCA (excerpt) ===")
    print(f"{'Material':<28} {'ρ [kg/m³]':>10}  {'Ref unit':>10}  {'GWP A1-A3':>10}  {'PERE A1-A3':>12}")
    print("-" * 80)
    for m in materials:
        lca = m.lca_data
        ref_unit = getattr(lca, "ref_flow_unit", "?")
        gwp_a1a3 = getattr(getattr(lca, "gwp", None), "a1_a3", None)
        pere_a1a3 = getattr(getattr(lca, "pere", None), "a1_a3", None)
        print(f"{(m.name or m.material_id)[:28]:<28} "
              f"{fmt(getattr(m, 'density', None)):>10}  {ref_unit:>10}  {fmt(gwp_a1a3):>10}  {fmt(pere_a1a3):>12}")


# --- Minimal material container (only the attrs the loader writes) ---
class Material:
    def __init__(self):
        self.material_id = None
        self.name = None
        self.density = None
        self.thermal_conduc = None
        self.heat_capac = None
        self.solar_absorp = None
        self.thickness_default = None
        self.thickness_list = None
        self.service_life = None
        self.lca_data = None

# --- Main demo ---
def main():
    data = DataClassMock(LCA_FILE, MAT_FILE)

    # pick a few materials that actually have an LCA id
    example_ids = [k for k, v in data.material_bind.items()
                   if k != "version" and v.get("lca_id")][:5]

    materials = []
    for mat_id in example_ids:
        m = Material()                              # <-- create material instance
        load_material_id(m, mat_id, data_class=data)  # <-- correct argument order
        materials.append(m)

    print(f"Loaded {len(materials)} materials from {MAT_FILE.name} "
          f"and linked their LCA datasets from {LCA_FILE.name}")
    print_material_summary(materials)

if __name__ == "__main__":
    main()