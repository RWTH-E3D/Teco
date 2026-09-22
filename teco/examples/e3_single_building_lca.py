"""
This example script can be used to simulate one (or more) buildings with TEASER, and to
complement the heat load results with GWP for a given life cycle length, for both
the building and its components, per life cycle stage.
It pickles and un-pickles the entire project, so large-scale use is not recommended.
"""

# e3_single_building_lca.py
from pathlib import Path
import pickle
import csv
import gc
from array import array

# === TEASER / TECO imports ===
from teaser.logic.utilities import get_default_path
from teaser.logic.simulation.export_and_manifest import export_and_manifest
from teaser.logic.simulation.simulate import simulate

from teco.project import Project
from teco.logic.buildingobjects.buildingphysics.en15804lcadata import En15804LcaData
from teco.data.output.lca_csv_output import export_building_gwp_csv, export_be_gwp_csv


# ----------------- helpers -----------------
def assign_heatloads_from_csv(
    prj,
    result_csv_path: Path,
    *,
    store_hourly_compact: bool = True,
) -> None:
    """
    Re-attach simulated heat-loads from the wide CSV written by simulate().

    - Always computes and stores 'simulated_heat_load_annual_kwh' on each building.
    - If 'store_hourly_compact' is True (default), attaches an array('f') with 8760 values
      to 'building.simulated_heat_load' (compact ~4 B/value), preserving TECO's legacy
      expectation that this attribute exists when heating LCA sums the series.
      If False, no hourly series is kept (only the annual_kwh float is stored).
    """
    by_name = {b.name: b for b in prj.buildings}
    with open(result_csv_path, newline="") as f:
        reader = csv.reader(f)
        header = next(reader, None)
        if not header or header[0].strip().lower() != "building":
            raise ValueError(
                f"{result_csv_path} is not a wide results CSV (missing 'building' header)."
            )

        for row in reader:
            if not row:
                continue
            bname = row[0]
            # parse numeric columns; tolerate empty strings
            series = [float(x) for x in row[1:] if x != ""]
            b = by_name.get(bname)
            if b is None:
                print(f"[assign_heatloads_from_csv] Unknown building '{bname}', skipping.")
                continue

            # Store annual energy in kWh (sum of W·h divided by 1000)
            annual_kwh = sum(series) / 1000.0
            setattr(b, "simulated_heat_load_annual_kwh", annual_kwh)

            if store_hourly_compact:
                # keep a compact 8760-vector so legacy summations still work
                b.simulated_heat_load = array("f", series)
            else:
                # don't keep hourly data -> minimize memory
                b.simulated_heat_load = None


# ----------------- main pipeline -----------------
def main():
    # 1) Build/load project
    prj = Project(load_data=True)
    prj.use_b4 = True
    prj.period_lca_scenario = 50

    prj.name = "teco_tabula_test"

    # --- Buildings ---

    prj.add_residential(
        method="tabula_de",
        usage="single_family_house",
        name="sfh",
        year_of_construction=1950,
        number_of_floors=2,
        height_of_floors=3.0,
        net_leased_area=45.0,
        inner_wall_approximation_approach="teaser_default",
        construction_type="tabula_standard"
    )


    # --- TEASER calculation knobs (unchanged) ---
    prj.number_of_elements_calc = 2
    prj.merge_windows_calc = False
    prj.calc_all_buildings(raise_errors=True)

# #########################DEBUG#####################################
# This snippet was used to identify any missing areas or lca datasets for materials in outer walls and rooftops.
#
#     b = prj.buildings[0]
#     print("OW area sum:", sum(ow.area for z in b.thermal_zones for ow in z.outer_walls))
#     print("RT area sum:", sum(rt.area for z in b.thermal_zones for rt in z.rooftops))
#
#     z0 = b.thermal_zones[0]
#     ow0 = z0.outer_walls[0]
#     print("OW element ref:", getattr(ow0.lca_data, "ref_flow_value", None),
#           getattr(ow0.lca_data, "ref_flow_unit", None))
#     for i, layer in enumerate(getattr(ow0, "layer", [])):
#         mat = getattr(layer, "material", None)
#         lca = getattr(mat, "lca_data", None) or getattr(layer, "lca_data", None)
#         print(f" layer {i}: {getattr(mat, 'name', None)}",
#               getattr(lca, "ref_flow_value", None), getattr(lca, "ref_flow_unit", None))
#
#     rt0 = z0.rooftops[0]
#     print("RT element ref:", getattr(rt0.lca_data, "ref_flow_value", None),
#           getattr(rt0.lca_data, "ref_flow_unit", None))
#     for i, layer in enumerate(getattr(rt0, "layer", [])):
#         mat = getattr(layer, "material", None)
#         lca = getattr(mat, "lca_data", None) or getattr(layer, "lca_data", None)
#         print(f" RT layer {i}: {getattr(mat, 'name', None)}",
#               getattr(lca, "ref_flow_value", None), getattr(lca, "ref_flow_unit", None))
#
#     #########################DEBUG#####################################

    # 2) Export + manifest (name fixes happen inside) → then pickle snapshot
    export_root = Path(get_default_path())
    manifest_file = export_and_manifest(prj, str(export_root))
    package_dir = export_root / prj.name
    package_dir.mkdir(parents=True, exist_ok=True)

    snapshot_path = package_dir / "project_snapshot.pkl"
    with open(snapshot_path, "wb") as f:
        pickle.dump(prj, f, protocol=pickle.HIGHEST_PROTOCOL)

    # 3) Simulation timing


    # (1 year hourly)
    # start_time = 0
    # stop_time = 8760 * 60 * 60  # seconds
    # intervals = 8760  # hourly

    # # 1 week
    start_time = 0
    stop_time = 3600 * 24 * 7  # seconds
    intervals = 24 * 7   # hourly

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

    # 4) Free the build-time project before loading the snapshot to avoid
    #    holding two full graphs in RAM at once
    del prj
    gc.collect()

    #    Re-load snapshot (decouples from sim layer) + reattach results
    with open(snapshot_path, "rb") as f:
        prj_for_lca = pickle.load(f)

    # Attach results; default keeps a compact hourly array + annual_kwh
    assign_heatloads_from_csv(prj_for_lca, result_csv_dy, store_hourly_compact=True)

    # 5) TECO LCA exports (per building)
    lca_data_natural_gas = En15804LcaData()
    lca_data_natural_gas.load_lca_data_template(
        # ÖKOBAUDAT: 1 kWh Endenergie Erdgas (ref. flow 3.6 MJ normalised to 1 MJ)
        "84aa7483-9824-49a9-a3e3-f9fb092ea7b7",
        prj_for_lca.data,
    )
    # Debug check for actual normalised reference flow value and unit (is 1 MJ)
    #print(lca_data_natural_gas.ref_flow_value, lca_data_natural_gas.ref_flow_unit)

    for building in prj_for_lca.buildings:
        # material/element LCA for A1–A3, etc.
        building.calc_lca_data(True, 50)

        # add operational heating (uses simulated heat energy internally)
        # eta_boi = 0.90
        building.add_lca_data_heating(0.90, lca_data_natural_gas)

        # per-building exports
        export_building_gwp_csv(
            building=building,
            path=package_dir / f"results_gwp_building_{building.name}.csv",
        )
        export_be_gwp_csv(
            building=building,
            path=package_dir / f"results_gwp_elements_{building.name}.csv",
        )

    print("LCA export done.")
    print(f"- Folder: {package_dir}")


if __name__ == "__main__":
    main()
