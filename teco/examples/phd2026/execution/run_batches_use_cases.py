"""
This script is a version of run_batches_parametric.py that is only used for the
simulation of (much smaller) use case building datasets.

Key behaviour:

- Uses project_name exactly as given (e.g., 'p_8'); each project already has exactly one weather station.
- Filters projects by numeric range: --start-project N --end-project M  (matches p_<X> where X in [N..M]).
    - You need to set the run configuration as --start-project x --end-project y
- Per-building pickle artifacts (as in e4_...py).
- Fuel selection:
    - 'kw-o' in energy_system_name → heating oil EPD.
    - 'kw-g' in energy_system_name → natural gas EPD.
    - else → default to natural gas.
- Residential vs Non-residential add_* selection based on building_type_name.
- eta_boi = 0.85

NEW:
- Input file can be either XLSX (sheet 'jobs') or CSV. The loader auto-detects by suffix.
"""

from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import argparse
import csv
import gc
import pickle
import re
from array import array

import pandas as pd

# === TEASER / TECO imports ===
from teaser.logic.utilities import get_default_path
from teaser.logic.simulation.export_and_manifest import export_and_manifest
from teaser.logic.simulation.simulate import simulate

from teco.project import Project
from teco.logic.buildingobjects.buildingphysics.en15804lcadata import En15804LcaData
from teco.data.output.lca_csv_output import export_building_gwp_csv, export_be_gwp_csv

# =========================
# CONFIG
# =========================

REPO_ROOT = Path(__file__).resolve().parents[3]

# Default input path: can be .csv OR .xlsx
EXCEL_PATH = REPO_ROOT / "teco" / "diss_run" / "input" / "vw_use_case_urban_planning_teco.csv"
EXCEL_SHEET = "jobs"  # only used if EXCEL_PATH is an Excel file

# (1 year hourly)
SIM_START = 0
SIM_STOP = 8760 * 60 * 60  # seconds
SIM_INTERVALS = 8760  # hourly

SIMULATOR = "Dymola"

# Safety cap per project
PROJECT_BUILDING_CAP = 4

WEATHER_BASE = REPO_ROOT / "teaser" / "teaser" / "data" / "input" / "inputdata" / "weatherdata"

# Weather catalog (absolute paths)
WEATHER_CATALOG = {
    "East_Rural":  WEATHER_BASE / "East_Rural_20150101_20151231_Torgau.mos",
    "East_Urban":  WEATHER_BASE / "East_Urban_20150101_20151231_Berlin.mos",
    "North_Rural": WEATHER_BASE / "North_Rural_20150101_20151231_Steinfurt.mos",
    "North_Urban": WEATHER_BASE / "North_Urban_20150101_20151231_Hannover.mos",
    "South_Rural": WEATHER_BASE / "South_Rural_20150101_20151231_Pfaffenhofen an der Ilm.mos",
    "South_Urban": WEATHER_BASE / "South_Urban_20150101_20151231_Stuttgart.mos",
}

# LCA IDs
NATGAS_LCA_ID = "84aa7483-9824-49a9-a3e3-f9fb092ea7b7"
OIL_LCA_ID    = "6ecefd2c-71c8-44f1-9959-6a8567a661c9"

# Degree of efficiency for gas/oil boiler, conservative estimate
ETA_BOI = 0.85

# Base output directory (per-project subfolders are created under here)
OUTPUT_DIR = Path(r"Z:\teco_adj_output")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Absolute path for TEASER/Dymola exports (models, package, artifacts)
# → per-user default, typically C:\Users\<username>\TEASEROutput on Windows
# Switch to folder of separate partition on local machine to avoid storage capacity issues

TEASER_EXPORT_ROOT = Path(get_default_path())
# TEASER_EXPORT_ROOT = Path(r"C:\Users\adam-90hs4im1jlzm0gi\TEASEROutput")
TEASER_EXPORT_ROOT.mkdir(parents=True, exist_ok=True)

# =========================
# UTILITIES
# =========================

def _slug(val: Any) -> str:
    s = str(val) if val is not None else ""
    allowed = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-._"
    return "".join(ch if ch in allowed else "_" for ch in s)


def resolve_weather_path_from_catalog(station: str) -> str:
    """Use absolute paths from WEATHER_CATALOG. Fail clearly if missing."""
    try:
        p = Path(WEATHER_CATALOG[station])
    except KeyError:
        raise KeyError(f"Unknown weather_station '{station}'. Allowed: {list(WEATHER_CATALOG)}")
    if not p.is_file():
        raise FileNotFoundError(
            f"Weather file for station '{station}' not found at absolute path:\n{p}\n"
            f"Please update WEATHER_CATALOG with a valid .mos path."
        )
    return str(p)


def parse_year_from_age_class(age: Any) -> int:
    """Use the first four-digit year found in the age class interval."""
    if age is None:
        return 0
    s = str(age).strip()
    if not s:
        return 0
    m = re.search(r"(\d{4})", s)
    return int(m.group(1)) if m else 0


def assign_heatload_for_building(result_csv_path: Path, building_name: str) -> Tuple[List[float], float]:
    """Extract hourly series and annual kWh from the project-wide heat-load CSV."""
    with open(result_csv_path, newline="") as f:
        reader = csv.reader(f)
        header = next(reader, None)
        if not header or header[0].strip().lower() != "building":
            raise ValueError(f"{result_csv_path} missing 'building' header; not a wide results CSV.")
        for row in reader:
            if row and row[0] == building_name:
                series = [float(x) for x in row[1:] if x != ""]
                return series, sum(series) / 1000.0
    return [], 0.0


def make_single_building_project(full_prj: Any, building_obj: Any) -> Any:
    """Create a single-building mini project snapshot (for LCA + export)."""
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


def lca_fuel_object(lca_id: str, data_store) -> En15804LcaData:
    o = En15804LcaData()
    o.load_lca_data_template(lca_id, data_store)
    return o


def project_number_from_name(pname: str) -> Optional[int]:
    """Expect project_name like 'p_141' → returns 141."""
    m = re.fullmatch(r"\s*p_(\d+)\s*", str(pname))
    return int(m.group(1)) if m else None


def project_output_dir(project_name: str) -> Path:
    """Return (and ensure) the per-project output folder under OUTPUT_DIR."""
    d = OUTPUT_DIR / project_name
    d.mkdir(parents=True, exist_ok=True)
    return d


def building_outputs_exist_ok(output_dir: Path, run_key: str, project_name: str) -> bool:
    """Check presence of both LCA CSVs for run_key inside the project's subfolder."""
    proj_out = output_dir / project_name
    a = proj_out / f"{_slug(run_key)}_results_gwp_building.csv"
    b = proj_out / f"{_slug(run_key)}_results_gwp_elements.csv"
    try:
        return a.exists() and b.exists() and a.stat().st_size > 100 and b.stat().st_size > 100
    except OSError:
        return False


def paths_for_project(project_name: str) -> Tuple[Path, Path, Path]:
    """
    TEASER export & artifacts still go under TEASER_EXPORT_ROOT/project_name,
    but the heat-load CSV goes to OUTPUT_DIR/<project_name>/<project_name>_heat_load.csv.
    """
    export_root = TEASER_EXPORT_ROOT
    package_dir = export_root / project_name
    artifacts_dir = package_dir / "artifacts"

    # Per-project output folder for the 3 CSVs
    proj_out_dir = project_output_dir(project_name)
    heatload_csv = proj_out_dir / f"{_slug(project_name)}_heat_load.csv"
    return package_dir, artifacts_dir, heatload_csv


def project_fully_done(df_proj: pd.DataFrame) -> bool:
    """All per-building LCA outputs already exist in OUTPUT_DIR/<project_name>?"""
    expected_run_keys = [str(rk) for rk in df_proj["run_key"].tolist()]
    pname = str(df_proj["project_name"].iloc[0])
    return all(building_outputs_exist_ok(OUTPUT_DIR, rk, pname) for rk in expected_run_keys)


def load_jobs(path: Path, sheet_name: str = "jobs") -> pd.DataFrame:
    """
    Load job definitions from either an Excel file (XLS/XLSX, using the given sheet)
    or a CSV file (no sheet).
    """
    suffix = path.suffix.lower()
    if suffix in {".xlsx", ".xls"}:
        return pd.read_excel(path, sheet_name=sheet_name)
    elif suffix == ".csv":
        return pd.read_csv(path)
    else:
        raise ValueError(f"Unsupported input file type for {path}. Use .csv or .xlsx/.xls.")


# =========================
# CORE
# =========================

def build_and_simulate_project(df_proj: pd.DataFrame) -> Tuple[Path, Path, Path]:
    # Resolve weather (exactly one per project by design)
    station = str(df_proj["weather_station"].iloc[0]).strip()
    weather_path = resolve_weather_path_from_catalog(station)

    project_name = str(df_proj["project_name"].iloc[0])
    prj = Project(load_data=True)
    prj.name = project_name
    prj.use_b4 = True
    prj.period_lca_scenario = 50
    prj.weather_file_path = weather_path

    # Add buildings (cap)
    added = 0
    for _, row in df_proj.iterrows():
        if added >= PROJECT_BUILDING_CAP:
            break

        building_type = str(row.get("building_type_name", "")).strip().lower()
        method = "hub4lca"
        usage = row.get("usage")
        name = row.get("run_key")  # run_key == building name inside project
        year_of_construction = parse_year_from_age_class(row.get("age_class_name"))
        number_of_floors = row.get("storeys_above_ground")
        height_of_floors = row.get("storey_height")
        net_leased_area = row.get("net_leased_area")
        energy_system_name = str(row.get("energy_system_name", "") or "")
        # with_ahu = False
        with_ahu = ("hvac" in energy_system_name.lower())
        construction_type = row.get("construction_type")
        rotation = row.get("rotation")
        # statistic_selector = row.get("statistic_selector")

        is_res = building_type in {"mfh", "sfh", "ab"}

        kwargs_base = dict(
            method=method,
            usage=usage,
            name=name,
            year_of_construction=year_of_construction,
            number_of_floors=number_of_floors,
            height_of_floors=height_of_floors,
            net_leased_area=net_leased_area,
            with_ahu=with_ahu,
            construction_type=construction_type,
            rotation=rotation,
        )

        if is_res:
            prj.add_residential(**kwargs_base)
        else:
            kwargs_nr = dict(kwargs_base)
            # kwargs_nr["statistic_selector"] = statistic_selector
            prj.add_non_residential(**kwargs_nr)

        added += 1

    # TEASER calc + export + simulate
    prj.number_of_elements_calc = 2
    prj.merge_windows_calc = False
    prj.calc_all_buildings(raise_errors=True)

    # --- export root for TEASER/Dymola (per-user default) ---
    export_root = TEASER_EXPORT_ROOT
    export_root.mkdir(parents=True, exist_ok=True)

    # Export TEASER package & manifest into export_root
    manifest_file = export_and_manifest(prj, str(export_root))

    # Ensure package dir exists
    package_dir = export_root / prj.name
    package_dir.mkdir(parents=True, exist_ok=True)

    # Heat-load CSV will be written under OUTPUT_DIR/<project_name>/
    _, artifacts_dir, result_csv_path = paths_for_project(prj.name)

    simulate(
        path=str(export_root),
        manifest_path=str(manifest_file),
        loading_time=0.0,
        result_path=str(result_csv_path),
        simulator=SIMULATOR,
        start_time=SIM_START,
        stop_time=SIM_STOP,
        intervals=SIM_INTERVALS,
        processes=4,
    )
    print("Dymola Simulation erfolgreich:")
    print(f"Ergebnisse gespeichert in: {result_csv_path}")

    # Per-building artifacts (pickles) under export_root
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    for idx, b in enumerate(prj.buildings, start=1):
        mini = make_single_building_project(prj, b)
        bname = getattr(b, "name", f"building_{idx}")
        out_pkl = artifacts_dir / f"{_slug(bname)}.pkl"
        with open(out_pkl, "wb") as f:
            pickle.dump(mini, f, protocol=pickle.HIGHEST_PROTOCOL)
        del mini
    del prj
    gc.collect()

    return package_dir, artifacts_dir, result_csv_path


def run_lca_for_project(df_proj: pd.DataFrame, artifacts_dir: Path, result_csv_path: Path) -> None:
    # Prepare EPDs once
    _data = Project(load_data=True).data
    lca_gas = lca_fuel_object(NATGAS_LCA_ID, _data)
    lca_oil = lca_fuel_object(OIL_LCA_ID, _data)

    # Map run_key → energy_system_name (fuel selection)
    fuel_pref: Dict[str, str] = {}
    for _, row in df_proj.iterrows():
        rk = str(row.get("run_key"))
        es = str(row.get("energy_system_name") or "")
        fuel_pref[rk] = es

    # Per-project output folder
    project_name = str(df_proj["project_name"].iloc[0])
    proj_out_dir = project_output_dir(project_name)

    # Iterate artifacts; skip buildings that already have both CSVs
    for pkl_file in sorted(artifacts_dir.glob("*.pkl")):
        bname = pkl_file.stem  # identical to run_key by construction
        if building_outputs_exist_ok(OUTPUT_DIR, bname, project_name):
            print(f"[SKIP] {bname} already processed.")
            continue

        with open(pkl_file, "rb") as f:
            mini_prj = pickle.load(f)
        try:
            if len(mini_prj.buildings) != 1:
                print(f"[WARN] Artifact has {len(mini_prj.buildings)} buildings: {pkl_file.name}; skipping.")
                continue

            building = mini_prj.buildings[0]

            # Attach heat from this project's results
            series, annual_kwh = assign_heatload_for_building(result_csv_path, bname)
            setattr(building, "simulated_heat_load_annual_kwh", annual_kwh)
            building.simulated_heat_load = array("f", series) if series else None

            # Material/element LCA (include stage D; 50-year period)
            building.calc_lca_data(True, 50)

            # Fuel rule: kw-o → oil; kw-g → gas; else default gas
            es_lower = str(fuel_pref.get(bname, "")).lower()
            fuel = lca_oil if ("kw-o" in es_lower) else (lca_gas if ("kw-g" in es_lower) else lca_gas)

            # Operational heating LCA
            building.add_lca_data_heating(ETA_BOI, fuel)

            # Exports into per-project OUTPUT_DIR/<project_name> with the desired names
            export_building_gwp_csv(
                building=building,
                path=proj_out_dir / f"{_slug(bname)}_results_gwp_building.csv",
            )
            export_be_gwp_csv(
                building=building,
                path=proj_out_dir / f"{_slug(bname)}_results_gwp_elements.csv",
            )
        finally:
            del mini_prj
            gc.collect()


def main() -> None:
    ap = argparse.ArgumentParser(description="Resumable TEASER→Dymola→TECO per-building runner (use case datasets).")
    ap.add_argument("--start-project", type=int, required=True, help="First project number (inclusive), matching p_<N>.")
    ap.add_argument("--end-project", type=int, required=True, help="Last project number (inclusive), matching p_<M>.")
    args = ap.parse_args()

    # Load input from XLSX (sheet 'jobs') or CSV, depending on EXCEL_PATH suffix
    df = load_jobs(EXCEL_PATH, EXCEL_SHEET)

    # Required columns
    required_cols = [
        "project_name", "weather_station", "building_type_name", "usage", "run_key",
        "age_class_name", "storeys_above_ground", "storey_height", "net_leased_area",
        "energy_system_name", "construction_type", "rotation",
        # "statistic_selector",
    ]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise KeyError(f"Input file {EXCEL_PATH} is missing required columns: {missing}")

    # Extract numeric project number and filter range (expect 'p_<number>')
    df["project_no"] = df["project_name"].map(project_number_from_name)
    if df["project_no"].isna().any():
        bad = df[df["project_no"].isna()]["project_name"].unique().tolist()
        raise ValueError(f"Found project_name(s) not matching 'p_{{number}}': {bad}")

    lo, hi = args.start_project, args.end_project
    df = df[(df["project_no"] >= lo) & (df["project_no"] <= hi)].copy()

    # Safety cap
    counts = df.groupby("project_name")["run_key"].count()
    violators = counts[counts > PROJECT_BUILDING_CAP]
    if not violators.empty:
        raise ValueError(f"Some project_name groups exceed {PROJECT_BUILDING_CAP} rows: {violators.to_dict()}")

    # Iterate projects in numeric order
    # sort=False to keep numerical order ("project_no"); sort=True is lexicographical
    for project_name, grp in df.sort_values(["project_no", "run_key"]).groupby("project_name", sort=False):
        print(f"\n=== {project_name} ===")

        # Derive paths for this project
        package_dir, artifacts_dir, result_csv_path = paths_for_project(project_name)

        # If fully done → skip entire project
        if project_fully_done(grp):
            print(f"[SKIP PROJECT] {project_name} — all outputs present in {OUTPUT_DIR / project_name}.")
            continue

        # If partial artifacts/results exist → resume; else build+simulate first
        if package_dir.exists() and artifacts_dir.exists() and result_csv_path.exists():
            print(f"[RESUME] Using existing artifacts & heat-load results for {project_name}.")
        else:
            print(f"[BUILD+SIM] {project_name}")
            package_dir, artifacts_dir, result_csv_path = build_and_simulate_project(grp)

        # Run LCA for missing buildings only
        run_lca_for_project(grp, artifacts_dir, result_csv_path)

        # Final check
        if not project_fully_done(grp):
            print(f"[WARN] {project_name} not fully complete (some outputs missing).")

    print("\nAll requested projects completed.")


if __name__ == "__main__":
    main()
