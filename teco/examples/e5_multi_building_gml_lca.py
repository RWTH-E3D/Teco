"""
e5_multi_building_gml_lca.py

Executes the full teco workflow (teaser enrichment + Dymola simulation + LCA
export) for a set of buildings loaded from a CityGML file via citydpc.

Workflow
--------
1. Load building geometries from a CityGML file using citydpc.
2. Enrich them with TABULA-DE archetype data via load_dpc_buildings.
3. Run TEASER building-physics calculation.
4. Export an AixLib/Modelica package and simulate with Dymola.
5. Pickle one mini-project per building for memory-efficient LCA processing.
6. For each building: re-attach heat-load results, compute LCA, export CSVs.

Critical import order
---------------------
teco.project.Project MUST be imported before teaser.data.input.citydpc_input
(and before any teaser archetype module).  Importing the teco package triggers
teco/__init__.py which calls teco_module_modifications.py.  That module patches
sys.modules so that teaser archetype classes (SingleFamilyHouse, etc.) inherit
from teco's Building/ThermalZone/BuildingElement when those archetype modules
are first loaded.  If the order were reversed the buildings would lack teco's
LCA methods (calc_lca_data, add_lca_data_heating, …).

As a side effect of the same patch, sys.modules['teaser.logic.utilities'] is
replaced by the teco package, so get_default_path / get_full_path must be
imported from teco.logic.utilities rather than from teaser.logic.utilities.
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

# teco_module_modifications (triggered above) patches sys.modules
# ['teaser.logic.utilities'] using __import__('teco.logic.utilities'), which
# returns the top-level teco *package* rather than the submodule.  Any teaser
# module subsequently imported that does
#   from teaser.logic.utilities import get_default_path, ...
# will therefore fail (those names live on the submodule, not the package).
# Fix: re-patch the entry to the actual teco.logic.utilities module object so
# all downstream teaser imports resolve correctly.
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

# citydpc_input is imported last so that its module-level archetype imports
# (SingleFamilyHouse, etc.) resolve Building from the already-patched sys.modules.
from teaser.data.input.citydpc_input import load_dpc_buildings


# ----------------- helpers -----------------

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

    # Copy teco-specific and data attributes needed during LCA.
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
    example_root = Path(__file__).resolve().parent / "examplefiles"
    citygml_path = example_root / "osm2Cgml_output_small.gml"
    if not citygml_path.exists():
        raise FileNotFoundError(f"Missing CityGML example file: {citygml_path}")

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

    use_party_walls = False
    party_walls = get_party_walls(dataset) if use_party_walls else [[None]]

    # ── 2. Create teco project and enrich with archetype data ─────────────────
    prj = Project(load_data=True)
    prj.name = "teco_gml_lca"
    prj.use_b4 = True
    prj.period_lca_scenario = 50

    # load_dpc_buildings populates prj.buildings.  Because teco's sys.modules
    # patch was applied earlier, each building is a teco Building instance with
    # full LCA capability.
    load_dpc_buildings(prj, dataset, party_walls, method="tabula_de")

    # ── 3. TEASER building-physics calculation ────────────────────────────────
    prj.number_of_elements_calc = 2
    prj.merge_windows_calc = False
    # teco's get_full_path anchors to the teco package; the weather file lives
    # inside the teaser package, so we resolve it via teaser's package location.
    import teaser as _teaser_pkg
    prj.weather_file_path = str(
        Path(_teaser_pkg.__file__).parent
        / "data" / "input" / "inputdata" / "weatherdata"
        / "TRY2015_510139065530_Jahr.mos"
    )
    prj.calc_all_buildings(raise_errors=True)

    # ── 4. Export Modelica/AixLib package + simulation manifest ───────────────
    export_root = Path(get_default_path())
    manifest_file = export_and_manifest(prj, str(export_root))
    package_dir = export_root / prj.name
    package_dir.mkdir(parents=True, exist_ok=True)

    # ── 5. Dymola simulation ──────────────────────────────────────────────────
    # Full year, hourly resolution.
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
        processes=6,
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
    # ÖKOBAUDAT dataset "1 kWh Endenergie Erdgas", ref. flow normalised to 1 MJ.
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

        # Re-attach simulated heat load from the Dymola results CSV.
        series, annual_kwh = assign_heatload_for_building(result_csv_dy, bname)
        setattr(building, "simulated_heat_load_annual_kwh", annual_kwh)
        building.simulated_heat_load = array("f", series) if series else None

        # Material/element LCA: A1–A3, B4 (replacements), C, D stages.
        building.calc_lca_data(True, 50)

        # Operational heating LCA — natural gas boiler at 90 % efficiency.
        building.add_lca_data_heating(0.90, lca_data_natural_gas)

        # Export per-building GWP results.
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
