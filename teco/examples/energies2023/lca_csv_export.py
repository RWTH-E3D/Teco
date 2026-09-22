import csv
from pathlib import Path
from teco.logic.buildingobjects.buildingphysics.en15804lcadata import En15804LcaData


def export_lca_csv_project_by_building(project, path, indicator):

    head_row = ["building_name", "net_leased_area ", "building_age_group" "a1", "a2", "a3", "a1_a3", "a4", "a5", "b1",
                "b2", "b3", "b4", "b5", "b6", "b7", "c1",
                "c2", "c3", "c4", "d", "sum", "sum with d"]

    data_list = []

    file_path = path / f"{project.name}_{indicator}_by_building.csv"

    for building in project.buildings:

        csv_row = [building.name, building.net_leased_area, building.building_age_group]
        csv_row.extend(indicator_to_list(building.lca_data, indicator))

        data_list.append(csv_row)

    with open(file_path, "w+", newline="") as csvfile:
        writer = csv.writer(csvfile, dialect="excel")
        writer.writerows([head_row, data_list])

def export_lca_csv_project_by_be(project, path, indicator):

    head_row = ["building_element", "overall_area ", "a1", "a2", "a3", "a1_a3", "a4", "a5", "b1",
                "b2", "b3", "b4", "b5", "b6", "b7", "c1",
                "c2", "c3", "c4", "d", "sum", "sum with d"]

    outer_walls = En15804LcaData()
    doors = En15804LcaData()
    rooftops = En15804LcaData()
    ground_floors = En15804LcaData()
    windows = En15804LcaData()
    inner_walls = En15804LcaData()
    floors = En15804LcaData()
    ceilings = En15804LcaData()

    ow_area = 0
    do_area = 0
    rt_area = 0
    gf_area = 0
    wn_area = 0
    iw_area = 0
    fl_area = 0
    cl_area = 0

    for building in project.buildings:
        for zone in building.thermal_zones:

            for outer_wall in zone.outer_walls:
                if outer_wall:
                    outer_walls = outer_walls + outer_wall.lca_data
                    ow_area += outer_wall.area
            for door in zone.doors:
                if door:
                    doors = doors + door.lca_data
                    do_area += door.area
            for rooftop in zone.rooftops:
                if rooftop:
                    rooftops = rooftops + rooftop.lca_data
                    rt_area += rooftop.area
            for ground_floor in zone.ground_floors:
                if ground_floor:
                    ground_floors = ground_floors + ground_floor.lca_data
                    gf_area += ground_floor.area
            for window in zone.windows:
                if window:
                    windows = windows + window.lca_data
                    wn_area += window.area
            for inner_wall in zone.inner_walls:
                if inner_wall:
                    inner_walls = inner_walls + inner_wall.lca_data
                    iw_area += inner_wall.area
            for floor in zone.floors:
                if floor:
                    floors = floors + floor.lca_data
                    fl_area += floor.area
            for ceiling in zone.ceilings:
                if ceiling:
                    ceilings = ceilings + ceiling.lca_data
                    cl_area += ceiling.area

        outer_walls_list = ["outer_walls", ow_area]
        outer_walls_list.extend(indicator_to_list(outer_walls, indicator))

        doors_list = ["doors", do_area]
        doors_list.extend(indicator_to_list(doors, indicator))

        rooftops_list = ["rooftops", rt_area]
        rooftops_list.extend(indicator_to_list(rooftops, indicator))

        ground_floors_list = ["ground_floors", gf_area]
        ground_floors_list.extend(indicator_to_list(ground_floors, indicator))

        windows_list = ["windows", wn_area]
        windows_list.extend(indicator_to_list(windows, indicator))

        inner_walls_list = ["inner_walls", iw_area]
        inner_walls_list.extend(indicator_to_list(inner_walls, indicator))

        floors_list = ["floors", fl_area]
        floors_list.extend(indicator_to_list(floors, indicator))

        ceilings_list = ["ceilings", cl_area]
        ceilings_list.extend(indicator_to_list(ceilings, indicator))

        export_list = [head_row, outer_walls_list, doors_list, rooftops_list, ground_floors_list, windows_list,
                       inner_walls_list, floors_list, ceilings_list]

        file_path = path / f"{project.name}_{indicator}_by_be.csv"

        with open(file_path, "w+", newline="") as csvfile:
            writer = csv.writer(csvfile, dialect="excel")
            writer.writerows(export_list)

    """
    element = En15804LcaData()

    element_area = 0

    for building in project.buildings:
        try:
            for zone in building.thermal_zones:
                try:
                    for element_part in getattr(zone, element_name):
                        if element_part:
                            element = element + element_part.lca_data
                            element_area += element_part.area
                except AttributeError:
                    print(f'NO ATTRIBUTE {element_name} IN ZONE {zone.name} OF BUILDING {building.name}')
                    break
        except AttributeError:
            print(f'NO ATTRIBUTE thermal_zones IN BUILDING {building.name}')
            break

    head_row = ["buildingelement", "a1", "a2", "a3", "a1_a3", "a4", "a5", "b1", "b2", "b3", "b4", "b5", "b6", "b7",
                "c1", "c2", "c3", "c4", "d", "sum", "sum with d", "area"]

    element_list = [element_name]

    element_list.extend((gwp_to_list(element)))

    element_list.append(element_area)

    export_list = [head_row, element_list]

    with open(path, "w", newline="") as csvfile:
        writer = csv.writer(csvfile, dialect="excel")
        writer.writerows(export_list)
"""
            
            
def indicator_to_list(lca_data, indicator):
    if indicator == "gwp":
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
                lca_data.gwp.sum_stages(False),
                lca_data.gwp.sum_stages(True)
                ]
    elif indicator == "odp":
        return [lca_data.odp.a1,
                lca_data.odp.a2,
                lca_data.odp.a3,
                lca_data.odp.a1_a3,
                lca_data.odp.a4,
                lca_data.odp.a5,
                lca_data.odp.b1,
                lca_data.odp.b2,
                lca_data.odp.b3,
                lca_data.odp.b4,
                lca_data.odp.b5,
                lca_data.odp.b6,
                lca_data.odp.b7,
                lca_data.odp.c1,
                lca_data.odp.c2,
                lca_data.odp.c3,
                lca_data.odp.c4,
                lca_data.odp.d,
                lca_data.odp.sum_stages(False),
                lca_data.odp.sum_stages(True)]
    elif indicator == "ap":
        return [lca_data.ap.a1,
                lca_data.ap.a2,
                lca_data.ap.a3,
                lca_data.ap.a1_a3,
                lca_data.ap.a4,
                lca_data.ap.a5,
                lca_data.ap.b1,
                lca_data.ap.b2,
                lca_data.ap.b3,
                lca_data.ap.b4,
                lca_data.ap.b5,
                lca_data.ap.b6,
                lca_data.ap.b7,
                lca_data.ap.c1,
                lca_data.ap.c2,
                lca_data.ap.c3,
                lca_data.ap.c4,
                lca_data.ap.d,
                lca_data.ap.sum_stages(False),
                lca_data.ap.sum_stages(True)
                ]