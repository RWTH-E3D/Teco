from teco.project import Project
from teco.logic.buildingobjects.buildingphysics.en15804lcadata import En15804LcaData
import csv

import simulate as sim


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


def export_be_gwp_csv(project, element_name, path="buildingelement_gwp_export.csv"):
    """

    Parameters
    ----------
    project: Instance of teco Project class
    element_name: str
        outer_walls, rooftops, ground_floors, windows, inner_walls, floors, ceilings, foundation, internalfloors
    path: str
        set to teco/data/output/buildingelement_gwp_export.csv by Default

    Returns
    -------

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
            lca_data.gwp.sum_stages(False),
            lca_data.gwp.sum_stages(True)
            ]



