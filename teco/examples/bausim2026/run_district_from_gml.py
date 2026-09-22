"""
This script is used to run Teco for the use case district in the bausim 2026 paper.
It is fundamentally a copy of e6_multi_building_gml_lca_manual_assign.py (more information
about the workflow can be found in that file under \examples).

Note: The input data file has been enriched with proprietary information and cannot be made available.

Workflow
--------
1. Load building geometries from a CityGML file using citydpc.
2. (Optional) Run once with PRINT_BUILDING_IDS = True to discover all GML IDs.
   Optionally set EXPORT_TEMPLATE_EXCEL to a path to write a pre-filled .xlsx
   template (building IDs, year of construction, shared-wall count, detected
   building type) that you can fill in with archetype and construction_type.
3. Provide per-building archetype assignments — either:
   a. Point ARCHETYPE_ASSIGNMENTS_EXCEL at the filled-in .xlsx template, or
   b. Fill the ARCHETYPE_ASSIGNMENTS dict directly in the script.
   Both are optional: buildings without an entry fall back to archetype "sfh"
   with DEFAULT_CONSTRUCTION_TYPE.
4. Enrich buildings with HUB4LCA archetype data via load_dpc_buildings.
5. Run TEASER building-physics calculation.
6. Export an AixLib/Modelica package and simulate with Dymola.
7. Pickle one mini-project per building for memory-efficient LCA processing.
8. For each building: re-attach heat-load results, compute LCA, export CSVs.

Archetype assignment
--------------------
Two equivalent ways to specify archetypes and construction types per building:

A) Excel file (recommended for large datasets)
   Set ARCHETYPE_ASSIGNMENTS_EXCEL to the path of an .xlsx file with columns:
       building, archetype, construction_type
   The easiest way to create this file is the EXPORT_TEMPLATE_EXCEL option in
   discovery mode (step 2), which pre-fills the building metadata columns.
   When set, this takes priority over the dict below.

B) Hard-coded dictionary
   Populate ARCHETYPE_ASSIGNMENTS in the script:

       ARCHETYPE_ASSIGNMENTS = {
           "<gml_id>": {
               "archetype": "<archetype_key>",
               "construction_type": "<hub4lca_construction_type_string>",
           },
           ...
       }

Both sources are optional. Buildings not covered by either fall back to
archetype "sfh" with the construction type given by DEFAULT_CONSTRUCTION_TYPE.

Supported archetype keys:
    Residential    : "sfh", "mfh", "ab"
    Non-residential: "office", "culture", "education", "health",
                     "hospitality", "industrial", "retail"

For "sfh" and "mfh" the adjacency subtype (detached / semi_detached /
terraced) is resolved automatically from the shared-wall count:
    0 shared walls    ->  detached
    1 shared wall     ->  semi_detached
    >= 2 shared walls ->  terraced

Critical import order
---------------------
teco.project.Project MUST be imported before teaser.data.input.citydpc_input
(and before any teaser archetype module).  See e5 for a full explanation.
"""

from pathlib import Path
import pickle
import csv
import gc
import os
from array import array

# === TECO imports — MUST precede all teaser archetype / citydpc_input imports ===
from teco.project import Project
from teco.logic.buildingobjects.buildingphysics.en15804lcadata import En15804LcaData
from teco.data.output.lca_csv_output import export_building_gwp_csv, export_be_gwp_csv

import sys
import teco.logic.utilities as _teco_utilities_mod
sys.modules['teaser.logic.utilities'] = _teco_utilities_mod

from teco.logic.utilities import get_default_path, get_full_path
from teaser.logic.simulation.export_and_manifest import export_and_manifest
from teaser.logic.simulation.simulate import simulate

# === citydpc imports — after teco patch is applied ===
try:
    from citydpc.dataset import Dataset
    from citydpc.core.input.citygmlInput import load_buildings_from_xml_file
    from citydpc.tools.partywall import get_party_walls
except ImportError as exc:
    raise SystemExit(
        "This example requires the citydpc package.  Install it and retry."
    ) from exc

from teaser.data.input.citydpc_input import (
    load_dpc_buildings,
    alkis_sfh_codes,
    alkis_mfh_codes,
    alkis_th_codes,
    alkis_office_codes,
)


# =============================================================================
# Configuration — edit these before running
# =============================================================================

# Set to True on a first run to print all GML IDs from the dataset, then fill
# in ARCHETYPE_ASSIGNMENTS below and set back to False.
PRINT_BUILDING_IDS = False

# Fallback construction type used for buildings not listed in
# ARCHETYPE_ASSIGNMENTS (or if ARCHETYPE_ASSIGNMENTS is empty).
# Must be a valid hub4lca construction type string, e.g.:
#   "hub4lca_sfh_detached_west_urban_stagnant_massive_blt20-120kw-g"
DEFAULT_CONSTRUCTION_TYPE = "hub4lca_sfh_detached_north_urban_growing_massive_bc20-120kw-g-s-sfh"  # <-- fill in before running

# Per-building archetype and construction type assignments.
# Key   : GML building ID (string, as printed by PRINT_BUILDING_IDS mode)
# Value : dict with keys "archetype" and "construction_type"
# Note  : ignored if ARCHETYPE_ASSIGNMENTS_EXCEL is set.
ARCHETYPE_ASSIGNMENTS = {
    # Example entries — replace with actual GML IDs from your dataset:
    # "DEBW521AA0000vVK": {
    #     "archetype": "sfh",
    #     "construction_type": "hub4lca_sfh_detached_west_urban_stagnant_massive_blt20-120kw-g",
    # },
    # "DEBW521AA0000vVL": {
    #     "archetype": "mfh",
    #     "construction_type": "hub4lca_mfh_detached_west_urban_stagnant_massive_blt20-120kw-g",
    # },
}

# Path to an Excel file (.xlsx) with per-building assignments.
# The file must have columns: "building", "archetype", "construction_type".
# When set, this takes priority over ARCHETYPE_ASSIGNMENTS above.
# Set to None to use the dictionary above instead.
ARCHETYPE_ASSIGNMENTS_EXCEL = Path(__file__).resolve().parent / "bausim_2026_full.xlsx"

# When PRINT_BUILDING_IDS = True, optionally export an Excel template
# pre-filled with all building IDs so you can fill in the other columns.
# Set to None to skip the export.
EXPORT_TEMPLATE_EXCEL = None

# =============================================================================


# ----------------- helpers -----------------

def _detect_building_type(function) -> str:
    """Map an ALKIS function code to a human-readable building type."""
    if function in alkis_sfh_codes:
        return "sfh"
    elif function in alkis_mfh_codes:
        return "mfh"
    elif function in alkis_th_codes:
        return "th"
    elif function in alkis_office_codes:
        return "office"
    else:
        return "unknown"


def _estimate_net_floor_area(dpc_building, height_of_floor: float = 2.8):
    """Estimate net floor area (m²) from citydpc building geometry.

    Mirrors the logic of Building.set_gml_attributes(): footprint × num_floors.
    Footprint is the largest horizontal GML surface. Number of floors is taken
    from storeysAboveGround if present, otherwise derived from measuredHeight.
    Returns None if the geometry is insufficient.
    """
    try:
        surfaces = dpc_building.get_surfaces()
        footprint_candidates = [
            s.surface_area
            for s in surfaces
            if s.surface_orientation in (-2, -1) and s.surface_tilt == 0.0
        ]
        if not footprint_candidates:
            return None
        footprint = max(footprint_candidates)

        num_floors = getattr(dpc_building, "storeysAboveGround", None)
        if num_floors is None or num_floors == 0:
            height = getattr(dpc_building, "measuredHeight", None)
            if height is None:
                return None
            num_floors = max(1, round(height / height_of_floor))
        else:
            num_floors = int(num_floors)

        return round(footprint * num_floors, 1)
    except Exception:
        return None


def _load_archetype_assignments_from_excel(path) -> dict:
    """Load per-building archetype assignments from an Excel file.

    The file must contain the columns 'building', 'archetype', and
    'construction_type'. Returns a dict in the same format as
    ARCHETYPE_ASSIGNMENTS.
    """
    import pandas as pd
    df = pd.read_excel(path, dtype=str).fillna("")
    result = {}
    for _, row in df.iterrows():
        building_id = row["building"].strip()
        archetype = row["archetype"].strip()
        construction_type = row["construction_type"].strip()
        if building_id and archetype and construction_type:
            result[building_id] = {
                "archetype": archetype,
                "construction_type": construction_type,
            }
    return result


def _export_archetype_template_excel(path, building_data: list):
    """Write an Excel template pre-filled with building information.

    Each entry in building_data must be a dict with keys:
        'gml_id', 'year_of_construction', 'num_shared_walls', 'net_floor_area'.
    The resulting file has those read-only reference columns followed by
    the empty 'archetype' and 'construction_type' columns to be filled in.
    """
    import pandas as pd
    df = pd.DataFrame({
        "building": [b["gml_id"] for b in building_data],
        "year_of_construction": [b["year_of_construction"] for b in building_data],
        "num_shared_walls": [b["num_shared_walls"] for b in building_data],
        "building_type": [b["building_type"] for b in building_data],
        "net_floor_area": [b["net_floor_area"] for b in building_data],
        "archetype": [""] * len(building_data),
        "construction_type": [""] * len(building_data),
    })
    df.to_excel(path, index=False)
    print(f"Template written to: {path}")


def _safe_name(name: str) -> str:
    """Return a filesystem-safe version of a building name."""
    return "".join(ch if ch.isalnum() or ch in "-._" else "_" for ch in name)


def assign_heatload_for_building(result_csv_path: Path, building_name: str):
    """
    Extract heat-load results for one building from the wide CSV written by
    simulate().

    Returns
    -------
    series : list[float]
        Hourly W·h values (length depends on simulation horizon).
    annual_kwh : float
        sum(series) / 1000.0
    """
    with open(result_csv_path, newline="") as f:
        reader = csv.reader(f)
        header = next(reader, None)
        if not header or header[0].strip().lower() != "building":
            raise ValueError(
                f"{result_csv_path} missing 'building' header; not a wide results CSV."
            )
        for row in reader:
            if not row:
                continue
            if row[0] == building_name:
                series = [float(x) for x in row[1:] if x != ""]
                annual_kwh = sum(series) / 1000.0
                return series, annual_kwh
    return [], 0.0


def _make_single_building_project(full_prj, building_obj):
    """
    Construct a mini teco.project.Project that contains exactly one building.
    Uses a pickle round-trip to deep-copy the building and sever all references
    back to the full project.
    """
    b_copy = pickle.loads(pickle.dumps(building_obj, protocol=pickle.HIGHEST_PROTOCOL))

    prj_cls = full_prj.__class__
    try:
        mini_prj = prj_cls(load_data=True)
    except TypeError:
        mini_prj = prj_cls()

    for attr in ("use_b4", "period_lca_scenario", "market_scenario", "data"):
        if hasattr(full_prj, attr):
            setattr(mini_prj, attr, getattr(full_prj, attr))

    if hasattr(b_copy, "parent"):
        b_copy.parent = mini_prj
    mini_prj.buildings = [b_copy]
    return mini_prj


# ----------------- main pipeline -----------------

def main():
    # ── 1. Load CityGML via citydpc ───────────────────────────────────────────
    root = Path(__file__).resolve().parent
    citygml_path = root / "bausim_2026_district.gml"
    if not citygml_path.exists():
        raise FileNotFoundError(f"Missing CityGML file: {citygml_path}")

    dataset = Dataset()
    load_buildings_from_xml_file(dataset, str(citygml_path))

    # Provide a fallback height for buildings without measuredHeight in the GML.
    for b in dataset.get_building_list():
        if b.measuredHeight is None:
            b.measuredHeight = 6.15

    # Optional: cap the number of buildings for quick tests.
    max_buildings = None
    if max_buildings is not None:
        dataset.buildings = {
            k: v
            for i, (k, v) in enumerate(dataset.buildings.items())
            if i < max_buildings
        }

    # Always compute party walls — needed for shared-wall counts in template
    # export and for the actual archetype adjacency logic.
    all_party_walls = get_party_walls(dataset)

    # ── Print building IDs and stop (discovery mode) ─────────────────────────
    if PRINT_BUILDING_IDS:
        building_data = []
        for b in dataset.get_building_list():
            bldg_common_walls = [lst for lst in all_party_walls if b.gml_id in lst]
            building_data.append({
                "gml_id": b.gml_id,
                "year_of_construction": getattr(b, "yearOfConstruction", None),
                "num_shared_walls": len(bldg_common_walls),
                "building_type": _detect_building_type(getattr(b, "function", None)),
                "net_floor_area": _estimate_net_floor_area(b),
            })
        print("Building GML IDs in dataset:")
        for bd in building_data:
            print(f"  {bd['gml_id']}  yoc={bd['year_of_construction']}  "
                  f"shared_walls={bd['num_shared_walls']}  "
                  f"type={bd['building_type']}")
        if EXPORT_TEMPLATE_EXCEL is not None:
            _export_archetype_template_excel(EXPORT_TEMPLATE_EXCEL, building_data)
        else:
            print("\nTip: set EXPORT_TEMPLATE_EXCEL to a path to write an Excel "
                  "template ready to fill in.")
        print("\nFill in ARCHETYPE_ASSIGNMENTS or ARCHETYPE_ASSIGNMENTS_EXCEL, "
              "then set PRINT_BUILDING_IDS = False and re-run.")
        return

    # ── Resolve archetype assignments from Excel or dict ─────────────────────
    if ARCHETYPE_ASSIGNMENTS_EXCEL is not None:
        assignments = _load_archetype_assignments_from_excel(ARCHETYPE_ASSIGNMENTS_EXCEL)
        print(f"Loaded {len(assignments)} archetype assignments from Excel.")
    else:
        assignments = ARCHETYPE_ASSIGNMENTS

    if DEFAULT_CONSTRUCTION_TYPE is None and not assignments:
        raise ValueError(
            "DEFAULT_CONSTRUCTION_TYPE is None and no archetype assignments were provided. "
            "Please set DEFAULT_CONSTRUCTION_TYPE or populate ARCHETYPE_ASSIGNMENTS "
            "/ ARCHETYPE_ASSIGNMENTS_EXCEL before running."
        )

    use_party_walls = False
    party_walls = all_party_walls if use_party_walls else [[None]]

    # ── 2. Create teco project and enrich with hub4lca archetype data ─────────
    prj = Project(load_data=True)
    prj.name = "bausim2026_teco"
    prj.use_b4 = True
    prj.period_lca_scenario = 50

    load_dpc_buildings(
        prj,
        dataset,
        party_walls,
        method="hub4lca",
        archetypes=assignments,
        construction_type=DEFAULT_CONSTRUCTION_TYPE,
    )

    # ── 3. TEASER building-physics calculation ────────────────────────────────
    prj.number_of_elements_calc = 2
    prj.merge_windows_calc = False
    import teaser as _teaser_pkg
    prj.weather_file_path = str(
        Path(_teaser_pkg.__file__).parent
        / "data" / "input" / "inputdata" / "weatherdata"
        / "North_Urban_20150101_20151231_Hannover.mos"
    )
    prj.calc_all_buildings(raise_errors=True)

    # ── 4. Export Modelica/AixLib package + simulation manifest ───────────────
    export_root = Path(get_default_path())
    manifest_file = export_and_manifest(prj, str(export_root))
    package_dir = export_root / prj.name
    package_dir.mkdir(parents=True, exist_ok=True)

    # ── 5. Dymola simulation ──────────────────────────────────────────────────
    start_time = 0
    stop_time = 8760 * 3600
    intervals = 8760

    # Uncomment for a quick one-week test run instead:
    # start_time = 0
    # stop_time = 3600 * 24 * 7
    # intervals = 24 * 7

    result_csv_dy = package_dir / "results_dy.csv"
    simulate(
        path=str(export_root),
        manifest_path=str(manifest_file),
        loading_time=0.0,
        result_path=str(result_csv_dy),
        simulator="Dymola",
        start_time=start_time,
        stop_time=stop_time,
        intervals=intervals,
        processes=8,
    )

    print("Dymola simulation finished.")
    print(f"Results saved to: {result_csv_dy}")

    # ── 6. Pickle one mini-project per building, then release full project ─────
    artifacts_dir = package_dir / "artifacts"
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    for idx, b in enumerate(prj.buildings, start=1):
        mini = _make_single_building_project(prj, b)
        bname = getattr(b, "name", f"building_{idx}")
        out_pkl = artifacts_dir / f"{_safe_name(bname)}.pkl"
        with open(out_pkl, "wb") as f:
            pickle.dump(mini, f, protocol=pickle.HIGHEST_PROTOCOL)
        del mini

    del prj
    gc.collect()

    # ── 7. Prepare the fuel LCA dataset (loaded once, reused per building) ────
    lca_data_natural_gas = En15804LcaData()
    lca_data_natural_gas.load_lca_data_template(
        "84aa7483-9824-49a9-a3e3-f9fb092ea7b7",
        Project(load_data=True).data,
    )

    # ── 8. Per-building LCA calculation and CSV export ─────────────────────────
    for pkl_file in sorted(artifacts_dir.glob("*.pkl")):
        with open(pkl_file, "rb") as f:
            mini_prj = pickle.load(f)

        if len(mini_prj.buildings) != 1:
            print(
                f"[WARN] Artifact has {len(mini_prj.buildings)} buildings: "
                f"{pkl_file.name}; skipping."
            )
            del mini_prj
            gc.collect()
            continue

        building = mini_prj.buildings[0]
        bname = getattr(building, "name", pkl_file.stem)
        safe_bname = _safe_name(bname)

        series, annual_kwh = assign_heatload_for_building(result_csv_dy, bname)
        setattr(building, "simulated_heat_load_annual_kwh", annual_kwh)
        building.simulated_heat_load = array("f", series) if series else None

        building.calc_lca_data(True, 50)
        building.add_lca_data_heating(0.90, lca_data_natural_gas)

        export_building_gwp_csv(
            building=building,
            path=package_dir / f"results_gwp_building_{safe_bname}.csv",
        )
        export_be_gwp_csv(
            building=building,
            path=package_dir / f"results_gwp_elements_{safe_bname}.csv",
        )

        del mini_prj
        gc.collect()

    print("LCA export done.")
    print(f"Results folder: {package_dir}")


if __name__ == "__main__":
    main()