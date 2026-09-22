from teco.project import Project
from teco.logic.buildingobjects.buildingphysics.en15804lcadata import En15804LcaData
import csv
from pathlib import Path

def export_building_gwp_csv(building, path="building_gwp_export.csv"):
    """

    Parameters
    ----------
    building: Instance of Building
    path: str
        set to teco/data/output/building_gwp_export.csv by Default

    Returns
    -------

    """

    data = En15804LcaData()

    data = data + building.lca_data

    data_list = gwp_to_list(data)

    head_row = ["a1", "a2", "a3", "a1_a3", "a4", "a5", "b1", "b2", "b3", "b4", "b5", "b6", "b7", "c1",
                "c2", "c3", "c4", "d", "sum", "sum with d"]

    export_list = [head_row, data_list]

    with open(path, "w", newline="") as csvfile:
        writer = csv.writer(csvfile, dialect="excel")
        writer.writerows(export_list)




def _coerce_lca(obj, *, building):
    """Return an En15804LcaData for `obj`, or None if impossible.
       Accepts either an En15804LcaData or a string UUID.
    """
    if isinstance(obj, En15804LcaData):
        return obj
    if isinstance(obj, str) and obj.strip():
        # Load by UUID using the project's data class
        try:
            tmp = En15804LcaData(parent=None)
            # building.parent should be the Project; its .data is the bound DataClass
            data_class = getattr(getattr(building, "parent", None), "data", None)
            tmp.load_lca_data_template(obj, data_class=data_class)
            return tmp
        except Exception as e:
            print(f"[export_be_gwp_csv] Could not resolve LCA dataset '{obj}': {e}")
            return None
    return None

def export_be_gwp_csv(building, path):
    """
    Export GWP by building element for a single building (like export_building_gwp_csv,
    but broken down per element with areas).
    """
    head_row = ["building_element", "overall_area", "a1", "a2", "a3", "a1_a3", "a4", "a5",
                "b1", "b2", "b3", "b4", "b5", "b6", "b7", "c1", "c2", "c3", "c4", "d",
                "sum", "sum with d"]

    # fresh accumulators for THIS building
    outer_walls = En15804LcaData(); ow_area = 0.0
    #doors = En15804LcaData(); do_area = 0.0
    rooftops = En15804LcaData(); rt_area = 0.0
    ground_floors = En15804LcaData(); gf_area = 0.0
    windows = En15804LcaData(); wn_area = 0.0
    inner_walls = En15804LcaData(); iw_area = 0.0
    floors = En15804LcaData(); fl_area = 0.0
    ceilings = En15804LcaData(); cl_area = 0.0

    # iterate zones of THIS building
    for zone in building.thermal_zones:
        for outer_wall in zone.outer_walls:
            if outer_wall:
                lca = _coerce_lca(outer_wall.lca_data, building=building)
                if lca: outer_walls = outer_walls + lca; ow_area += getattr(outer_wall, "area", 0.0)
        # for door in zone.doors:
        #     if door:
        #         lca = _coerce_lca(door.lca_data, building=building)
        #         if lca: doors = doors + lca; do_area += getattr(door, "area", 0.0)
        for rooftop in zone.rooftops:
            if rooftop:
                lca = _coerce_lca(rooftop.lca_data, building=building)
                if lca: rooftops = rooftops + lca; rt_area += getattr(rooftop, "area", 0.0)
        for ground_floor in zone.ground_floors:
            if ground_floor:
                lca = _coerce_lca(ground_floor.lca_data, building=building)
                if lca: ground_floors = ground_floors + lca; gf_area += getattr(ground_floor, "area", 0.0)
        for window in zone.windows:
            if window:
                lca = _coerce_lca(window.lca_data, building=building)
                if lca: windows = windows + lca; wn_area += getattr(window, "area", 0.0)
        for inner_wall in zone.inner_walls:
            if inner_wall:
                lca = _coerce_lca(inner_wall.lca_data, building=building)
                if lca: inner_walls = inner_walls + lca; iw_area += getattr(inner_wall, "area", 0.0)
        for floor in zone.floors:
            if floor:
                lca = _coerce_lca(floor.lca_data, building=building)
                if lca: floors = floors + lca; fl_area += getattr(floor, "area", 0.0)
        for ceiling in zone.ceilings:
            if ceiling:
                lca = _coerce_lca(ceiling.lca_data, building=building)
                if lca: ceilings = ceilings + lca; cl_area += getattr(ceiling, "area", 0.0)

    # rows
    export_list = [head_row]
    export_list.append(["outer_walls", ow_area] + gwp_to_list(outer_walls))
    #export_list.append(["doors", do_area] + gwp_to_list(doors))
    export_list.append(["rooftops", rt_area] + gwp_to_list(rooftops))
    export_list.append(["ground_floors", gf_area] + gwp_to_list(ground_floors))
    export_list.append(["windows", wn_area] + gwp_to_list(windows))
    export_list.append(["inner_walls", iw_area] + gwp_to_list(inner_walls))
    export_list.append(["floors", fl_area] + gwp_to_list(floors))
    export_list.append(["ceilings", cl_area] + gwp_to_list(ceilings))

    # resolve output path
    path = Path(path)
    file_path = path if path.suffix.lower() == ".csv" else path / f"{building.name}_gwp_by_be.csv"

    with open(file_path, "w", newline="") as csvfile:
        writer = csv.writer(csvfile, dialect="excel")
        writer.writerows(export_list)


def gwp_to_list(lca_data):
    return [lca_data.gwp.a1,
            lca_data.gwp.a2,
            lca_data.gwp.a3,
            lca_data.gwp.a1_a3,
            lca_data.gwp.a4,
            lca_data.gwp.a5,
            lca_data.gwp.b1,
            lca_data.gwp.b2,
            lca_data.gwp.b3,
            lca_data.gwp.b4,
            lca_data.gwp.b5,
            lca_data.gwp.b6,
            lca_data.gwp.b7,
            lca_data.gwp.c1,
            lca_data.gwp.c2,
            lca_data.gwp.c3,
            lca_data.gwp.c4,
            lca_data.gwp.d,
            lca_data.gwp.sum_stages(add_stage_d=False),
            lca_data.gwp.sum_stages(add_stage_d=True)
            ]



