"""
This is an example script that uses the En15804LcaData class for a plain display of
some data from the LcaData.json.
"""

import json
from pathlib import Path
from teco.logic.buildingobjects.buildingphysics.en15804lcadata import En15804LcaData
from teco.data.input.lca_data_input import load_en15804_lca_data_id

# === Paths ===
HERE = Path(__file__).resolve().parent
LCA_FILE = HERE.parent / "data" / "input" / "inputdata" / "LcaData.json"

# === Mock DataClass ===
class DataClassMock:
    """Minimal replacement for the real DataClass, just exposing .lca_data_bind."""
    def __init__(self, json_path):
        with open(json_path, encoding="utf-8") as f:
            self.lca_data_bind = json.load(f)

# === Helper for table formatting ===
def print_indicator_table(lca, indicators=("gwp", "pere", "penre")):
    """Prints a compact table of key indicators for an En15804LcaData object."""
    modules = ["a1_a3", "a4", "a5", "b1", "b2", "b3", "b4", "b5", "b6", "b7", "c2", "c3", "c4", "d"]
    print(f"\n{'Indicator':<10} {'Unit':<12} " + " ".join(f"{m.upper():>10}" for m in modules))
    print("-" * (24 + len(modules) * 11))

    for ind_name in indicators:
        ind = getattr(lca, ind_name)
        row = [f"{ind_name.upper():<10} {ind.unit:<12}"]
        for m in modules:
            val = getattr(ind, m)
            row.append(f"{val:>10.4g}" if val is not None else f"{'–':>10}")
        print(" ".join(row))

# === Example usage ===
def main():
    data_class = DataClassMock(LCA_FILE)
    print(f"Loaded {len(data_class.lca_data_bind)-1} entries from JSON")

    # pick a few known IDs
    example_ids = list(data_class.lca_data_bind.keys())[1:4]

    for lca_id in example_ids:
        lca = En15804LcaData()
        load_en15804_lca_data_id(lca, lca_id, data_class)

        print("\n" + "=" * 70)
        print(f"Name: {lca.name}")
        print(f"ID:   {lca.lca_data_id}")
        print(f"Ref flow: 1 {lca.ref_flow_unit}")
        print_indicator_table(lca)

if __name__ == "__main__":
    main()

