# -*- coding: utf-8 -*-
"""
Created on Mon Dec  6 15:30:02 2021

@author: Linus Cuypers (cuypers@e3d.rwth-aachen.de)
"""

from teco.project import Project
from teco.logic.buildingobjects.buildingphysics.en15804lcadata import En15804LcaData
import csv

import simulate as sim

from datetime import datetime

now = datetime.now()

current_time = now.strftime("%H:%M:%S")
print("Start =", current_time)


def export_building_gwp_csv(project, path="building_gwp_export.csv"):
    
    type1 = En15804LcaData()
    type2 = En15804LcaData()
    type3 = En15804LcaData()
    type4 = En15804LcaData()
    general_project = En15804LcaData()

    for building_ in project.buildings:
        if building_.name.endswith("_I"):
            type1 = type1 + building_.lca_data
        elif building_.name.endswith("_II"):
            type2 = type2 + building_.lca_data
        elif building_.name.endswith("_III"):
            type3 = type3 + building_.lca_data
        elif building_.name.endswith("_IV"):
            type4 = type4 + building_.lca_data
        else:
            print(building_.name)
        general_project += building_.lca_data

    head_row = ["building type", "a1", "a2", "a3", "a1_a3", "a4", "a5", "b1", "b2", "b3", "b4", "b5", "b6", "b7", "c1",
                "c2", "c3", "c4", "d", "sum", "sum with d"]

    type1_list = ["type1"]
    type1_list.extend(gwp_to_list(type1))

    type2_list = ["type2"]
    type2_list.extend(gwp_to_list(type2))

    type3_list = ["type3"]
    type3_list.extend(gwp_to_list(type3))

    type4_list = ["type4"]
    type4_list.extend(gwp_to_list(type4))

    general_project_gwp = ["general_project_gwp"]
    general_project_gwp.extend(gwp_to_list(general_project))
    general_project_odp = ["general_project_odp"]
    general_project_odp.extend(odp_to_list(general_project))
    general_project_ap = ["general_project_ap"]
    general_project_ap.extend(ap_to_list(general_project))
    general_project_pert = ["general_project_pert"]
    general_project_pert.extend(pert_to_list(general_project))
    general_project_penrt = ["general_project_penrt"]
    general_project_penrt.extend(penrt_to_list(general_project))

    export_list = [head_row, type1_list, type2_list, type3_list, type4_list, general_project_gwp,
                   general_project_odp, general_project_ap, general_project_pert, general_project_penrt]

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


def odp_to_list(lca_data):
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
            lca_data.odp.sum_stages(True)
            ]


def ap_to_list(lca_data):
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


def pert_to_list(lca_data):
    return [lca_data.pert.a1,
            lca_data.pert.a2,
            lca_data.pert.a3,
            lca_data.pert.a1_a3,
            lca_data.pert.a4,
            lca_data.pert.a5,
            lca_data.pert.b1,
            lca_data.pert.b2,
            lca_data.pert.b3,
            lca_data.pert.b4,
            lca_data.pert.b5,
            lca_data.pert.b6,
            lca_data.pert.b7,
            lca_data.pert.c1,
            lca_data.pert.c2,
            lca_data.pert.c3,
            lca_data.pert.c4,
            lca_data.pert.d,
            lca_data.pert.sum_stages(False),
            lca_data.pert.sum_stages(True)
            ]


def penrt_to_list(lca_data):
    return [lca_data.penrt.a1,
            lca_data.penrt.a2,
            lca_data.penrt.a3,
            lca_data.penrt.a1_a3,
            lca_data.penrt.a4,
            lca_data.penrt.a5,
            lca_data.penrt.b1,
            lca_data.penrt.b2,
            lca_data.penrt.b3,
            lca_data.penrt.b4,
            lca_data.penrt.b5,
            lca_data.penrt.b6,
            lca_data.penrt.b7,
            lca_data.penrt.c1,
            lca_data.penrt.c2,
            lca_data.penrt.c3,
            lca_data.penrt.c4,
            lca_data.penrt.d,
            lca_data.penrt.sum_stages(False),
            lca_data.penrt.sum_stages(True)
            ]


if __name__ == '__main__':
    prj = Project(load_data=True)

    prj.name = "Teaser+Eco_paper"

    prj.weather_file_path = "C:\\Users\\schmitz\\PycharmProjects\\teco\\Examples\\TRY2015_535578100702_Jahr.mos"
    # Bedburg = TRY2015_510139065530_Jahr.mos  ; Hamburg = TRY2015_535578100702_Jahr.mos

    prj.load_citygml(path="C:\\Users\\schmitz\\PycharmProjects\\teco\\Examples\\Hamburg_no_buildingparts.gml", method="tabula_de")
    """prj.add_residential(
        method="tabula_de",
        usage="single_family_house",
        name="Typ_VI",
        year_of_construction=2015,
        number_of_floors=3,
        height_of_floors=2.5,
        net_leased_area=172.0,
        type_heat_supply_system=3)"""

    prj.used_library_calc = "AixLib"

    prj.calc_all_buildings()

    prj.export_aixlib(path="C:\\Users\\schmitz\\TEASEROutput")

    sim.simulate(path="C:\\Users\\schmitz\\TEASEROutput", prj=prj, loading_time=3600,
                 result_path="C:\\Users\\schmitz\\TEASEROutput\\results")

    lca_data_elec = En15804LcaData()
    lca_data_elec.load_lca_data_template("c869c47e-ce43-45b4-b640-b0cd1746e450", prj.data)


    utilities = En15804LcaData()

    for building in prj.buildings:
        building.calc_lca_data(False, 50)

        building.add_lca_data_elec(lca_data_elec)

        building.add_lca_data_heat_supply_system(False, 50)

        utilities += building.lca_data

    print("GWP_Project")
    print("A1_A3: {} {}".format(utilities.gwp.a1_a3, utilities.gwp.unit))
    print("A4: {} {}".format(utilities.gwp.a4, utilities.gwp.unit))
    print("A5: {} {}".format(utilities.gwp.a5, utilities.gwp.unit))
    print("B1: {} {}".format(utilities.gwp.b1, utilities.gwp.unit))
    print("B6: {} {}".format(utilities.gwp.b6, utilities.gwp.unit))
    print("C1: {} {}".format(utilities.gwp.c1, utilities.gwp.unit))
    print("C2: {} {}".format(utilities.gwp.c2, utilities.gwp.unit))
    print("C3: {} {}".format(utilities.gwp.c3, utilities.gwp.unit))
    print("C4: {} {}".format(utilities.gwp.c4, utilities.gwp.unit))
    print("D: {} {}".format(utilities.gwp.d, utilities.gwp.unit))

    print("PERT_Project")
    print("A1_A3: {} {}".format(utilities.pert.a1_a3, utilities.pert.unit))
    print("A4: {} {}".format(utilities.pert.a4, utilities.pert.unit))
    print("A5: {} {}".format(utilities.pert.a5, utilities.pert.unit))
    print("B1: {} {}".format(utilities.pert.b1, utilities.pert.unit))
    print("B6: {} {}".format(utilities.pert.b6, utilities.pert.unit))
    print("C1: {} {}".format(utilities.pert.c1, utilities.pert.unit))
    print("C2: {} {}".format(utilities.pert.c2, utilities.pert.unit))
    print("C3: {} {}".format(utilities.pert.c3, utilities.pert.unit))
    print("C4: {} {}".format(utilities.pert.c4, utilities.pert.unit))
    print("D: {} {}".format(utilities.pert.d, utilities.pert.unit))

    print("PENRT_Project")
    print("A1_A3: {} {}".format(utilities.penrt.a1_a3, utilities.penrt.unit))
    print("A4: {} {}".format(utilities.penrt.a4, utilities.penrt.unit))
    print("A5: {} {}".format(utilities.penrt.a5, utilities.penrt.unit))
    print("B1: {} {}".format(utilities.penrt.b1, utilities.penrt.unit))
    print("B6: {} {}".format(utilities.penrt.b6, utilities.penrt.unit))
    print("C1: {} {}".format(utilities.penrt.c1, utilities.penrt.unit))
    print("C2: {} {}".format(utilities.penrt.c2, utilities.penrt.unit))
    print("C3: {} {}".format(utilities.penrt.c3, utilities.penrt.unit))
    print("C4: {} {}".format(utilities.penrt.c4, utilities.penrt.unit))
    print("D: {} {}".format(utilities.penrt.d, utilities.penrt.unit))


    # export_building_gwp_csv(prj)
    # export_be_gwp_csv(prj)

    now = datetime.now()

    current_time = now.strftime("%H:%M:%S")
    print("End =", current_time)