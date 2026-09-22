"""
This example script can be used to simulate a larger batch of buildings (up to 500 is recommended) with TEASER, and to
complement the heat load results with GWP for a given life cycle length, for both
the building and its components, per life cycle stage.
It pickles and un-pickles on a per-building basis, so large-scale use is more feasible.
"""

from pathlib import Path
import pickle
import csv
import gc
import os
from array import array

# === TEASER / TECO imports ===
from teaser.logic.utilities import get_default_path
from teaser.logic.simulation.export_and_manifest import export_and_manifest
from teaser.logic.simulation.simulate import simulate

from teco.project import Project
from teco.logic.buildingobjects.buildingphysics.en15804lcadata import En15804LcaData
from teco.data.output.lca_csv_output import export_building_gwp_csv, export_be_gwp_csv


# ----------------- helpers -----------------
def _safe_name(name: str) -> str:
    return "".join(ch if ch.isalnum() or ch in "-._" else "_" for ch in name)


def assign_heatload_for_building(result_csv_path: Path, building_name: str):
    """
    Returns (series, annual_kwh) for exactly one building from a wide results CSV written by simulate().

    - series: list[float] of hourly W·h values (length depends on simulation horizon)
    - annual_kwh: float, sum(series)/1000.0
    """
    with open(result_csv_path, newline="") as f:
        reader = csv.reader(f)
        header = next(reader, None)
        if not header or header[0].strip().lower() != "building":
            raise ValueError(f"{result_csv_path} missing 'building' header; not a wide results CSV.")
        for row in reader:
            if not row:
                continue
            if row[0] == building_name:
                series = [float(x) for x in row[1:] if x != ""]
                annual_kwh = sum(series) / 1000.0
                return series, annual_kwh
    # if we get here, building wasn't in the CSV
    return [], 0.0


def _make_single_building_project(full_prj, building_obj):
    """
    Construct a mini-project that contains exactly one building.
    Uses a pickle roundtrip to deep-copy the building and sever references.
    """
    b_copy = pickle.loads(pickle.dumps(building_obj, protocol=pickle.HIGHEST_PROTOCOL))

    prj_cls = full_prj.__class__
    try:
        mini_prj = prj_cls(load_data=True)
    except TypeError:
        mini_prj = prj_cls()

    # copy essential project-level flags used by TECO
    for attr in ("use_b4", "period_lca_scenario", "market_scenario", "data"):
        if hasattr(full_prj, attr):
            setattr(mini_prj, attr, getattr(full_prj, attr))

    if hasattr(b_copy, "parent"):
        b_copy.parent = mini_prj
    mini_prj.buildings = [b_copy]
    return mini_prj


# ----------------- main pipeline -----------------
def main():
    # 1) Build/load project
    prj = Project(load_data=True)
    prj.use_b4 = True
    prj.period_lca_scenario = 50
    prj.name = "teco_tabula_full"

    # --- Buildings ---
    #

    # prj.add_residential(
    #     method="hub4lca",
    #     usage="single_family_house_detached",
    #     name="sfhd",
    #     year_of_construction=1915,
    #     number_of_floors=2,
    #     height_of_floors=2.7,
    #     net_leased_area=120.0,
    #     with_ahu=False,
    #     inner_wall_approximation_approach="teaser_default",
    #     construction_type="hub4lca_sfh_detached_south_urban_stagnant_massive_blt20-120kw-g",
    # )
####################TABULA#############################


    #####
    #SFH#
    #####

    # prj.add_residential(
    #     method="tabula_de",
    #     usage="single_family_house",
    #     name="sfh_1918",
    #     year_of_construction=1890,
    #     number_of_floors=2,
    #     height_of_floors=2.7,
    #     net_leased_area=142.0,
    #     with_ahu=False,
    #     inner_wall_approximation_approach="teaser_default"
    # )
    #
    # prj.add_residential(
    #     method="tabula_de",
    #     usage="single_family_house",
    #     name="sfh_1948",
    #     year_of_construction=1945,
    #     number_of_floors=2,
    #     height_of_floors=2.7,
    #     net_leased_area=303.0,
    #     with_ahu=False,
    #     inner_wall_approximation_approach="teaser_default"
    # )
    #
    # prj.add_residential(
    #     method="tabula_de",
    #     usage="single_family_house",
    #     name="sfh_1957",
    #     year_of_construction=1955,
    #     number_of_floors=2,
    #     height_of_floors=2.7,
    #     net_leased_area=111.0,
    #     with_ahu=False,
    #     inner_wall_approximation_approach="teaser_default"
    # )
    #
    # prj.add_residential(
    #     method="tabula_de",
    #     usage="single_family_house",
    #     name="sfh_1968",
    #     year_of_construction=1965,
    #     number_of_floors=2,
    #     height_of_floors=2.7,
    #     net_leased_area=121.0,
    #     with_ahu=False,
    #     inner_wall_approximation_approach="teaser_default"
    # )
    #
    # prj.add_residential(
    #     method="tabula_de",
    #     usage="single_family_house",
    #     name="sfh_1978",
    #     year_of_construction=1975,
    #     number_of_floors=1,
    #     height_of_floors=2.7,
    #     net_leased_area=173.0,
    #     with_ahu=False,
    #     inner_wall_approximation_approach="teaser_default"
    # )
    #
    prj.add_residential(
        method="tabula_de",
        usage="single_family_house",
        name="sfh_1983",
        year_of_construction=1980,
        number_of_floors=2,
        height_of_floors=2.7,
        net_leased_area=216.0,
        with_ahu=False,
        inner_wall_approximation_approach="teaser_default"
    )
    #
    # prj.add_residential(
    #     method="tabula_de",
    #     usage="single_family_house",
    #     name="sfh_1994",
    #     year_of_construction=1990,
    #     number_of_floors=2,
    #     height_of_floors=2.7,
    #     net_leased_area=150.0,
    #     with_ahu=False,
    #     inner_wall_approximation_approach="teaser_default"
    # )
    #
    # prj.add_residential(
    #     method="tabula_de",
    #     usage="single_family_house",
    #     name="sfh_2001",
    #     year_of_construction=2000,
    #     number_of_floors=2,
    #     height_of_floors=2.7,
    #     net_leased_area=122.0,
    #     with_ahu=False,
    #     inner_wall_approximation_approach="teaser_default"
    # )
    #
    # prj.add_residential(
    #     method="tabula_de",
    #     usage="single_family_house",
    #     name="sfh_2009",
    #     year_of_construction=2006,
    #     number_of_floors=2,
    #     height_of_floors=2.7,
    #     net_leased_area=147.0,
    #     with_ahu=False,
    #     inner_wall_approximation_approach="teaser_default"
    # )
    #
    # prj.add_residential(
    #     method="tabula_de",
    #     usage="single_family_house",
    #     name="sfh_2015",
    #     year_of_construction=2012,
    #     number_of_floors=2,
    #     height_of_floors=2.7,
    #     net_leased_area=147.0,
    #     with_ahu=False,
    #     inner_wall_approximation_approach="teaser_default"
    # )
    #
    # #####
    # #TH#
    # #####
    #
    # prj.add_residential(
    #     method="tabula_de",
    #     usage="terraced_house",
    #     name="th_1860",
    #     year_of_construction=1890,
    #     number_of_floors=2,
    #     height_of_floors=2.7,
    #     net_leased_area=96.0,
    #     with_ahu=False,
    #     inner_wall_approximation_approach="teaser_default"
    # )
    #
    # prj.add_residential(
    #     method="tabula_de",
    #     usage="terraced_house",
    #     name="th_1948",
    #     year_of_construction=1945,
    #     number_of_floors=2,
    #     height_of_floors=2.7,
    #     net_leased_area=113.0,
    #     with_ahu=False,
    #     inner_wall_approximation_approach="teaser_default"
    # )
    #
    # prj.add_residential(
    #     method="tabula_de",
    #     usage="terraced_house",
    #     name="th_1957",
    #     year_of_construction=1955,
    #     number_of_floors=2,
    #     height_of_floors=2.7,
    #     net_leased_area=150.0,
    #     with_ahu=False,
    #     inner_wall_approximation_approach="teaser_default"
    # )
    #
    # prj.add_residential(
    #     method="tabula_de",
    #     usage="terraced_house",
    #     name="th_1968",
    #     year_of_construction=1965,
    #     number_of_floors=2,
    #     height_of_floors=2.7,
    #     net_leased_area=117.0,
    #     with_ahu=False,
    #     inner_wall_approximation_approach="teaser_default"
    # )
    #
    # prj.add_residential(
    #     method="tabula_de",
    #     usage="terraced_house",
    #     name="th_1978",
    #     year_of_construction=1975,
    #     number_of_floors=2,
    #     height_of_floors=2.7,
    #     net_leased_area=106.0,
    #     with_ahu=False,
    #     inner_wall_approximation_approach="teaser_default"
    # )
    #
    # prj.add_residential(
    #     method="tabula_de",
    #     usage="terraced_house",
    #     name="th_1983",
    #     year_of_construction=1980,
    #     number_of_floors=2,
    #     height_of_floors=2.7,
    #     net_leased_area=108.0,
    #     with_ahu=False,
    #     inner_wall_approximation_approach="teaser_default"
    # )
    #
    # prj.add_residential(
    #     method="tabula_de",
    #     usage="terraced_house",
    #     name="th_1994",
    #     year_of_construction=1993,
    #     number_of_floors=2,
    #     height_of_floors=2.7,
    #     net_leased_area=128.0,
    #     with_ahu=False,
    #     inner_wall_approximation_approach="teaser_default"
    # )
    #
    # prj.add_residential(
    #     method="tabula_de",
    #     usage="terraced_house",
    #     name="th_2001",
    #     year_of_construction=1999,
    #     number_of_floors=2,
    #     height_of_floors=2.7,
    #     net_leased_area=149.0,
    #     with_ahu=False,
    #     inner_wall_approximation_approach="teaser_default"
    # )
    #
    # prj.add_residential(
    #     method="tabula_de",
    #     usage="terraced_house",
    #     name="th_2009",
    #     year_of_construction=2007,
    #     number_of_floors=2,
    #     height_of_floors=2.7,
    #     net_leased_area=152.0,
    #     with_ahu=False,
    #     inner_wall_approximation_approach="teaser_default"
    # )
    #
    # prj.add_residential(
    #     method="tabula_de",
    #     usage="terraced_house",
    #     name="th_2015",
    #     year_of_construction=2013,
    #     number_of_floors=2,
    #     height_of_floors=2.7,
    #     net_leased_area=196.0,
    #     with_ahu=False,
    #     inner_wall_approximation_approach="teaser_default"
    # )
    #
    # #####
    # #MFH#
    # #####
    #
    # prj.add_residential(
    #     method="tabula_de",
    #     usage="multi_family_house",
    #     name="mfh_1860",
    #     year_of_construction=1861,
    #     number_of_floors=3,
    #     height_of_floors=2.7,
    #     net_leased_area=312.0,
    #     with_ahu=False,
    #     inner_wall_approximation_approach="teaser_default"
    # )
    #
    # prj.add_residential(
    #     method="tabula_de",
    #     usage="multi_family_house",
    #     name="mfh_1948",
    #     year_of_construction=1946,
    #     number_of_floors=3,
    #     height_of_floors=2.7,
    #     net_leased_area=312.0,
    #     with_ahu=False,
    #     inner_wall_approximation_approach="teaser_default"
    # )
    #
    # prj.add_residential(
    #     method="tabula_de",
    #     usage="multi_family_house",
    #     name="mfh_1957",
    #     year_of_construction=1955,
    #     number_of_floors=2,
    #     height_of_floors=2.7,
    #     net_leased_area=632.0,
    #     with_ahu=False,
    #     inner_wall_approximation_approach="teaser_default"
    # )
    #
    # prj.add_residential(
    #     method="tabula_de",
    #     usage="multi_family_house",
    #     name="mfh_1968",
    #     year_of_construction=1966,
    #     number_of_floors=4,
    #     height_of_floors=2.7,
    #     net_leased_area=3129.0,
    #     with_ahu=False,
    #     inner_wall_approximation_approach="teaser_default"
    # )
    #
    # prj.add_residential(
    #     method="tabula_de",
    #     usage="multi_family_house",
    #     name="mfh_1978",
    #     year_of_construction=1976,
    #     number_of_floors=4,
    #     height_of_floors=2.7,
    #     net_leased_area=469.0,
    #     with_ahu=False,
    #     inner_wall_approximation_approach="teaser_default"
    # )
    #
    # prj.add_residential(
    #     method="tabula_de",
    #     usage="multi_family_house",
    #     name="mfh_1983",
    #     year_of_construction=1980,
    #     number_of_floors=3,
    #     height_of_floors=2.7,
    #     net_leased_area=654.0,
    #     with_ahu=False,
    #     inner_wall_approximation_approach="teaser_default"
    # )
    #
    # prj.add_residential(
    #     method="tabula_de",
    #     usage="multi_family_house",
    #     name="mfh_1994",
    #     year_of_construction=1992,
    #     number_of_floors=4,
    #     height_of_floors=2.7,
    #     net_leased_area=778.0,
    #     with_ahu=False,
    #     inner_wall_approximation_approach="teaser_default"
    # )
    #
    # prj.add_residential(
    #     method="tabula_de",
    #     usage="multi_family_house",
    #     name="mfh_2001",
    #     year_of_construction=2000,
    #     number_of_floors=4,
    #     height_of_floors=2.7,
    #     net_leased_area=835.0,
    #     with_ahu=False,
    #     inner_wall_approximation_approach="teaser_default"
    # )
    #
    # prj.add_residential(
    #     method="tabula_de",
    #     usage="multi_family_house",
    #     name="mfh_2009",
    #     year_of_construction=2007,
    #     number_of_floors=3,
    #     height_of_floors=2.7,
    #     net_leased_area=2190.0,
    #     with_ahu=False,
    #     inner_wall_approximation_approach="teaser_default"
    # )
    #
    # prj.add_residential(
    #     method="tabula_de",
    #     usage="multi_family_house",
    #     name="mfh_2015",
    #     year_of_construction=2012,
    #     number_of_floors=5,
    #     height_of_floors=2.7,
    #     net_leased_area=1305.0,
    #     with_ahu=False,
    #     inner_wall_approximation_approach="teaser_default"
    # )
    #
    # #####
    # #AB#
    # #####
    #
    # prj.add_residential(
    #     method="tabula_de",
    #     usage="apartment_block",
    #     name="ab_1918",
    #     year_of_construction=1917,
    #     number_of_floors=4,
    #     height_of_floors=2.7,
    #     net_leased_area=829.0,
    #     with_ahu=False,
    #     inner_wall_approximation_approach="teaser_default"
    # )
    #
    # prj.add_residential(
    #     method="tabula_de",
    #     usage="apartment_block",
    #     name="ab_1948",
    #     year_of_construction=1947,
    #     number_of_floors=5,
    #     height_of_floors=2.7,
    #     net_leased_area=1484.0,
    #     with_ahu=False,
    #     inner_wall_approximation_approach="teaser_default"
    # )
    #
    # prj.add_residential(
    #     method="tabula_de",
    #     usage="apartment_block",
    #     name="ab_1957",
    #     year_of_construction=1955,
    #     number_of_floors=6,
    #     height_of_floors=2.7,
    #     net_leased_area=1603.0,
    #     with_ahu=False,
    #     inner_wall_approximation_approach="teaser_default"
    # )
    #
    # prj.add_residential(
    #     method="tabula_de",
    #     usage="apartment_block",
    #     name="ab_1968",
    #     year_of_construction=1967,
    #     number_of_floors=5,
    #     height_of_floors=2.7,
    #     net_leased_area=3887.0,
    #     with_ahu=False,
    #     inner_wall_approximation_approach="teaser_default"
    # )
    #
    # prj.add_residential(
    #     method="tabula_de",
    #     usage="apartment_block",
    #     name="ab_1978",
    #     year_of_construction=1977,
    #     number_of_floors=7,
    #     height_of_floors=2.7,
    #     net_leased_area=3322.0,
    #     with_ahu=False,
    #     inner_wall_approximation_approach="teaser_default"
    # )



    # --- TEASER calculation knobs (unchanged) ---
    prj.number_of_elements_calc = 2
    prj.merge_windows_calc = False
    prj.calc_all_buildings(raise_errors=True)

    # 2) Export + manifest (name fixes happen inside)
    export_root = Path(get_default_path())
    manifest_file = export_and_manifest(prj, str(export_root))
    package_dir = export_root / prj.name
    package_dir.mkdir(parents=True, exist_ok=True)

    # 3) Simulation timing
    # Choose either the 1-year block or 1-week block
    # --- 1 year hourly ---
    # start_time = 0
    # stop_time = 8760 * 3600
    # intervals = 8760

    # --- 1 week hourly  ---
    start_time = 0
    stop_time = 8760 * 60 * 60
    intervals = 8760

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

    print("Dymola Simulation erfolgreich:")
    print(f"Ergebnisse gespeichert in: {result_csv_dy}")

    # 4) Create ONE pickle per building (mini-project artifacts), then free the big project
    artifacts_dir = package_dir / "artifacts"
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    for idx, b in enumerate(prj.buildings, start=1):
        mini = _make_single_building_project(prj, b)
        bname = getattr(b, "name", f"building_{idx}")
        out_pkl = artifacts_dir / f"{_safe_name(bname)}.pkl"
        with open(out_pkl, "wb") as f:
            pickle.dump(mini, f, protocol=pickle.HIGHEST_PROTOCOL)
        del mini
    # free big project before LCA loop
    del prj
    gc.collect()

    # 5) Prepare LCA fuel once (natural gas EPD: 1 kWh Endenergie Erdgas)
    lca_data_natural_gas = En15804LcaData()
    lca_data_natural_gas.load_lca_data_template(
        # ÖKOBAUDAT dataset
        "84aa7483-9824-49a9-a3e3-f9fb092ea7b7",
        Project(load_data=True).data,  # access to data store for LCA template
    )

    # 6) TECO LCA exports — loop over per-building artifacts
    for pkl_file in sorted(artifacts_dir.glob("*.pkl")):
        with open(pkl_file, "rb") as f:
            mini_prj = pickle.load(f)

        # safety check: exactly one building
        if len(mini_prj.buildings) != 1:
            print(f"[WARN] Artifact has {len(mini_prj.buildings)} buildings: {pkl_file.name}; skipping.")
            del mini_prj
            gc.collect()
            continue

        building = mini_prj.buildings[0]
        bname = getattr(building, "name", pkl_file.stem)
        safe_bname = _safe_name(bname)

        # attach simulated heat load only for this building
        series, annual_kwh = assign_heatload_for_building(result_csv_dy, bname)
        # store annual energy (kWh) and an optional compact hourly vector (W·h)
        setattr(building, "simulated_heat_load_annual_kwh", annual_kwh)
        building.simulated_heat_load = array("f", series) if series else None

        # material/element LCA for A1–A3… (True=include stage D; 50-year period consistent with prj)
        building.calc_lca_data(True, 50)

        # add operational heating (uses simulated heat energy internally)
        # example boiler efficiency eta_boi = 0.90
        building.add_lca_data_heating(0.90, lca_data_natural_gas)

        # per-building exports
        export_building_gwp_csv(
            building=building,
            path=package_dir / f"results_gwp_building_{safe_bname}.csv",
        )
        export_be_gwp_csv(
            building=building,
            path=package_dir / f"results_gwp_elements_{safe_bname}.csv",
        )

        # free per-building mini project before next
        del mini_prj
        gc.collect()

    print("LCA export done.")
    print(f"- Folder: {package_dir}")


if __name__ == "__main__":
    # Execute from Python as usual:
    #   python e3_single_building_lca.py
    main()
