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

    # MitHSS
    utilitiess = En15804LcaData()

    for building in prj.buildings:
        building.calc_lca_data(False, 50)

        building.add_lca_data_elec(lca_data_elec)

        #building.add_lca_data_heat_supply_system(False, 50)

        utilitiess += building.lca_data

    print("GWP_Project")
    print("A1_A3: {} {}".format(utilitiess.gwp.a1_a3, utilitiess.gwp.unit))
    print("A4: {} {}".format(utilitiess.gwp.a4, utilitiess.gwp.unit))
    print("A5: {} {}".format(utilitiess.gwp.a5, utilitiess.gwp.unit))
    print("B1: {} {}".format(utilitiess.gwp.b1, utilitiess.gwp.unit))
    print("B6: {} {}".format(utilitiess.gwp.b6, utilitiess.gwp.unit))
    print("C1: {} {}".format(utilitiess.gwp.c1, utilitiess.gwp.unit))
    print("C2: {} {}".format(utilitiess.gwp.c2, utilitiess.gwp.unit))
    print("C3: {} {}".format(utilitiess.gwp.c3, utilitiess.gwp.unit))
    print("C4: {} {}".format(utilitiess.gwp.c4, utilitiess.gwp.unit))
    print("D: {} {}".format(utilitiess.gwp.d, utilitiess.gwp.unit))

    print("PERT_Project")
    print("A1_A3: {} {}".format(utilitiess.pert.a1_a3, utilitiess.pert.unit))
    print("A4: {} {}".format(utilitiess.pert.a4, utilitiess.pert.unit))
    print("A5: {} {}".format(utilitiess.pert.a5, utilitiess.pert.unit))
    print("B1: {} {}".format(utilitiess.pert.b1, utilitiess.pert.unit))
    print("B6: {} {}".format(utilitiess.pert.b6, utilitiess.pert.unit))
    print("C1: {} {}".format(utilitiess.pert.c1, utilitiess.pert.unit))
    print("C2: {} {}".format(utilitiess.pert.c2, utilitiess.pert.unit))
    print("C3: {} {}".format(utilitiess.pert.c3, utilitiess.pert.unit))
    print("C4: {} {}".format(utilitiess.pert.c4, utilitiess.pert.unit))
    print("D: {} {}".format(utilitiess.pert.d, utilitiess.pert.unit))

    print("PENRT_Project")
    print("A1_A3: {} {}".format(utilitiess.penrt.a1_a3, utilitiess.penrt.unit))
    print("A4: {} {}".format(utilitiess.penrt.a4, utilitiess.penrt.unit))
    print("A5: {} {}".format(utilitiess.penrt.a5, utilitiess.penrt.unit))
    print("B1: {} {}".format(utilitiess.penrt.b1, utilitiess.penrt.unit))
    print("B6: {} {}".format(utilitiess.penrt.b6, utilitiess.penrt.unit))
    print("C1: {} {}".format(utilitiess.penrt.c1, utilitiess.penrt.unit))
    print("C2: {} {}".format(utilitiess.penrt.c2, utilitiess.penrt.unit))
    print("C3: {} {}".format(utilitiess.penrt.c3, utilitiess.penrt.unit))
    print("C4: {} {}".format(utilitiess.penrt.c4, utilitiess.penrt.unit))
    print("D: {} {}".format(utilitiess.penrt.d, utilitiess.penrt.unit))

    ohneH = En15804LcaData()  # todo löschen

    for building in prj.buildings:
        building.calc_lca_data(False, 50)

        building.add_lca_data_elec(lca_data_elec)

        building.add_lca_data_heat_supply_system_ohneH(False, 50)

        ohneH += building.lca_data

    print("GWP_Project")
    print("A1_A3: {} {}".format(ohneH.gwp.a1_a3, ohneH.gwp.unit))
    print("A4: {} {}".format(ohneH.gwp.a4, ohneH.gwp.unit))
    print("A5: {} {}".format(ohneH.gwp.a5, ohneH.gwp.unit))
    print("B1: {} {}".format(ohneH.gwp.b1, ohneH.gwp.unit))
    print("B6: {} {}".format(ohneH.gwp.b6, ohneH.gwp.unit))
    print("C1: {} {}".format(ohneH.gwp.c1, ohneH.gwp.unit))
    print("C2: {} {}".format(ohneH.gwp.c2, ohneH.gwp.unit))
    print("C3: {} {}".format(ohneH.gwp.c3, ohneH.gwp.unit))
    print("C4: {} {}".format(ohneH.gwp.c4, ohneH.gwp.unit))
    print("D: {} {}".format(ohneH.gwp.d, ohneH.gwp.unit))

    print("PERT_Project")
    print("A1_A3: {} {}".format(ohneH.pert.a1_a3, ohneH.pert.unit))
    print("A4: {} {}".format(ohneH.pert.a4, ohneH.pert.unit))
    print("A5: {} {}".format(ohneH.pert.a5, ohneH.pert.unit))
    print("B1: {} {}".format(ohneH.pert.b1, ohneH.pert.unit))
    print("B6: {} {}".format(ohneH.pert.b6, ohneH.pert.unit))
    print("C1: {} {}".format(ohneH.pert.c1, ohneH.pert.unit))
    print("C2: {} {}".format(ohneH.pert.c2, ohneH.pert.unit))
    print("C3: {} {}".format(ohneH.pert.c3, ohneH.pert.unit))
    print("C4: {} {}".format(ohneH.pert.c4, ohneH.pert.unit))
    print("D: {} {}".format(ohneH.pert.d, ohneH.pert.unit))

    print("PENRT_Project")
    print("A1_A3: {} {}".format(ohneH.penrt.a1_a3, ohneH.penrt.unit))
    print("A4: {} {}".format(ohneH.penrt.a4, ohneH.penrt.unit))
    print("A5: {} {}".format(ohneH.penrt.a5, ohneH.penrt.unit))
    print("B1: {} {}".format(ohneH.penrt.b1, ohneH.penrt.unit))
    print("B6: {} {}".format(ohneH.penrt.b6, ohneH.penrt.unit))
    print("C1: {} {}".format(ohneH.penrt.c1, ohneH.penrt.unit))
    print("C2: {} {}".format(ohneH.penrt.c2, ohneH.penrt.unit))
    print("C3: {} {}".format(ohneH.penrt.c3, ohneH.penrt.unit))
    print("C4: {} {}".format(ohneH.penrt.c4, ohneH.penrt.unit))
    print("D: {} {}".format(ohneH.penrt.d, ohneH.penrt.unit))

    ohneHHE = En15804LcaData()  # todo löschen

    for building in prj.buildings:
        building.calc_lca_data(False, 50)

        building.add_lca_data_elec(lca_data_elec)

        building.add_lca_data_heat_supply_system_ohneHHE(False, 50)

        ohneHHE += building.lca_data

    print("GWP_Project")
    print("A1_A3: {} {}".format(ohneHHE.gwp.a1_a3, ohneHHE.gwp.unit))
    print("A4: {} {}".format(ohneHHE.gwp.a4, ohneHHE.gwp.unit))
    print("A5: {} {}".format(ohneHHE.gwp.a5, ohneHHE.gwp.unit))
    print("B1: {} {}".format(ohneHHE.gwp.b1, ohneHHE.gwp.unit))
    print("B6: {} {}".format(ohneHHE.gwp.b6, ohneHHE.gwp.unit))
    print("C1: {} {}".format(ohneHHE.gwp.c1, ohneHHE.gwp.unit))
    print("C2: {} {}".format(ohneHHE.gwp.c2, ohneHHE.gwp.unit))
    print("C3: {} {}".format(ohneHHE.gwp.c3, ohneHHE.gwp.unit))
    print("C4: {} {}".format(ohneHHE.gwp.c4, ohneHHE.gwp.unit))
    print("D: {} {}".format(ohneHHE.gwp.d, ohneHHE.gwp.unit))

    print("PERT_Project")
    print("A1_A3: {} {}".format(ohneHHE.pert.a1_a3, ohneHHE.pert.unit))
    print("A4: {} {}".format(ohneHHE.pert.a4, ohneHHE.pert.unit))
    print("A5: {} {}".format(ohneHHE.pert.a5, ohneHHE.pert.unit))
    print("B1: {} {}".format(ohneHHE.pert.b1, ohneHHE.pert.unit))
    print("B6: {} {}".format(ohneHHE.pert.b6, ohneHHE.pert.unit))
    print("C1: {} {}".format(ohneHHE.pert.c1, ohneHHE.pert.unit))
    print("C2: {} {}".format(ohneHHE.pert.c2, ohneHHE.pert.unit))
    print("C3: {} {}".format(ohneHHE.pert.c3, ohneHHE.pert.unit))
    print("C4: {} {}".format(ohneHHE.pert.c4, ohneHHE.pert.unit))
    print("D: {} {}".format(ohneHHE.pert.d, ohneHHE.pert.unit))

    print("PENRT_Project")
    print("A1_A3: {} {}".format(ohneHHE.penrt.a1_a3, ohneHHE.penrt.unit))
    print("A4: {} {}".format(ohneHHE.penrt.a4, ohneHHE.penrt.unit))
    print("A5: {} {}".format(ohneHHE.penrt.a5, ohneHHE.penrt.unit))
    print("B1: {} {}".format(ohneHHE.penrt.b1, ohneHHE.penrt.unit))
    print("B6: {} {}".format(ohneHHE.penrt.b6, ohneHHE.penrt.unit))
    print("C1: {} {}".format(ohneHHE.penrt.c1, ohneHHE.penrt.unit))
    print("C2: {} {}".format(ohneHHE.penrt.c2, ohneHHE.penrt.unit))
    print("C3: {} {}".format(ohneHHE.penrt.c3, ohneHHE.penrt.unit))
    print("C4: {} {}".format(ohneHHE.penrt.c4, ohneHHE.penrt.unit))
    print("D: {} {}".format(ohneHHE.penrt.d, ohneHHE.penrt.unit))

    ohneTWHE = En15804LcaData()  # todo löschen

    for building in prj.buildings:
        building.calc_lca_data(False, 50)

        building.add_lca_data_elec(lca_data_elec)

        building.add_lca_data_heat_supply_system_ohneTWHE(False, 50)

        ohneTWHE += building.lca_data

    print("GWP_Project")
    print("A1_A3: {} {}".format(ohneTWHE.gwp.a1_a3, ohneTWHE.gwp.unit))
    print("A4: {} {}".format(ohneTWHE.gwp.a4, ohneTWHE.gwp.unit))
    print("A5: {} {}".format(ohneTWHE.gwp.a5, ohneTWHE.gwp.unit))
    print("B1: {} {}".format(ohneTWHE.gwp.b1, ohneTWHE.gwp.unit))
    print("B6: {} {}".format(ohneTWHE.gwp.b6, ohneTWHE.gwp.unit))
    print("C1: {} {}".format(ohneTWHE.gwp.c1, ohneTWHE.gwp.unit))
    print("C2: {} {}".format(ohneTWHE.gwp.c2, ohneTWHE.gwp.unit))
    print("C3: {} {}".format(ohneTWHE.gwp.c3, ohneTWHE.gwp.unit))
    print("C4: {} {}".format(ohneTWHE.gwp.c4, ohneTWHE.gwp.unit))
    print("D: {} {}".format(ohneTWHE.gwp.d, ohneTWHE.gwp.unit))

    print("PERT_Project")
    print("A1_A3: {} {}".format(ohneTWHE.pert.a1_a3, ohneTWHE.pert.unit))
    print("A4: {} {}".format(ohneTWHE.pert.a4, ohneTWHE.pert.unit))
    print("A5: {} {}".format(ohneTWHE.pert.a5, ohneTWHE.pert.unit))
    print("B1: {} {}".format(ohneTWHE.pert.b1, ohneTWHE.pert.unit))
    print("B6: {} {}".format(ohneTWHE.pert.b6, ohneTWHE.pert.unit))
    print("C1: {} {}".format(ohneTWHE.pert.c1, ohneTWHE.pert.unit))
    print("C2: {} {}".format(ohneTWHE.pert.c2, ohneTWHE.pert.unit))
    print("C3: {} {}".format(ohneTWHE.pert.c3, ohneTWHE.pert.unit))
    print("C4: {} {}".format(ohneTWHE.pert.c4, ohneTWHE.pert.unit))
    print("D: {} {}".format(ohneTWHE.pert.d, ohneTWHE.pert.unit))

    print("PENRT_Project")
    print("A1_A3: {} {}".format(ohneTWHE.penrt.a1_a3, ohneTWHE.penrt.unit))
    print("A4: {} {}".format(ohneTWHE.penrt.a4, ohneTWHE.penrt.unit))
    print("A5: {} {}".format(ohneTWHE.penrt.a5, ohneTWHE.penrt.unit))
    print("B1: {} {}".format(ohneTWHE.penrt.b1, ohneTWHE.penrt.unit))
    print("B6: {} {}".format(ohneTWHE.penrt.b6, ohneTWHE.penrt.unit))
    print("C1: {} {}".format(ohneTWHE.penrt.c1, ohneTWHE.penrt.unit))
    print("C2: {} {}".format(ohneTWHE.penrt.c2, ohneTWHE.penrt.unit))
    print("C3: {} {}".format(ohneTWHE.penrt.c3, ohneTWHE.penrt.unit))
    print("C4: {} {}".format(ohneTWHE.penrt.c4, ohneTWHE.penrt.unit))
    print("D: {} {}".format(ohneTWHE.penrt.d, ohneTWHE.penrt.unit))


    # ohne CE bis ohne h/tw
    utilities = En15804LcaData()

    for building in prj.buildings:
        building.calc_lca_data(False, 50)

        building.add_lca_data_elec(lca_data_elec)

        building.add_lca_data_heat_supply_system_no_ce(False, 50)

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

    utility = En15804LcaData()  # todo löschen

    for building in prj.buildings:
        building.calc_lca_data(False, 50)

        building.add_lca_data_elec(lca_data_elec)

        building.add_lca_data_heat_supply_system_no_d(False, 50)

        utility += building.lca_data

    print("GWP_Project")
    print("A1_A3: {} {}".format(utility.gwp.a1_a3, utility.gwp.unit))
    print("A4: {} {}".format(utility.gwp.a4, utility.gwp.unit))
    print("A5: {} {}".format(utility.gwp.a5, utility.gwp.unit))
    print("B1: {} {}".format(utility.gwp.b1, utility.gwp.unit))
    print("B6: {} {}".format(utility.gwp.b6, utility.gwp.unit))
    print("C1: {} {}".format(utility.gwp.c1, utility.gwp.unit))
    print("C2: {} {}".format(utility.gwp.c2, utility.gwp.unit))
    print("C3: {} {}".format(utility.gwp.c3, utility.gwp.unit))
    print("C4: {} {}".format(utility.gwp.c4, utility.gwp.unit))
    print("D: {} {}".format(utility.gwp.d, utility.gwp.unit))

    print("PERT_Project")
    print("A1_A3: {} {}".format(utility.pert.a1_a3, utility.pert.unit))
    print("A4: {} {}".format(utility.pert.a4, utility.pert.unit))
    print("A5: {} {}".format(utility.pert.a5, utility.pert.unit))
    print("B1: {} {}".format(utility.pert.b1, utility.pert.unit))
    print("B6: {} {}".format(utility.pert.b6, utility.pert.unit))
    print("C1: {} {}".format(utility.pert.c1, utility.pert.unit))
    print("C2: {} {}".format(utility.pert.c2, utility.pert.unit))
    print("C3: {} {}".format(utility.pert.c3, utility.pert.unit))
    print("C4: {} {}".format(utility.pert.c4, utility.pert.unit))
    print("D: {} {}".format(utility.pert.d, utility.pert.unit))

    print("PENRT_Project")
    print("A1_A3: {} {}".format(utility.penrt.a1_a3, utility.penrt.unit))
    print("A4: {} {}".format(utility.penrt.a4, utility.penrt.unit))
    print("A5: {} {}".format(utility.penrt.a5, utility.penrt.unit))
    print("B1: {} {}".format(utility.penrt.b1, utility.penrt.unit))
    print("B6: {} {}".format(utility.penrt.b6, utility.penrt.unit))
    print("C1: {} {}".format(utility.penrt.c1, utility.penrt.unit))
    print("C2: {} {}".format(utility.penrt.c2, utility.penrt.unit))
    print("C3: {} {}".format(utility.penrt.c3, utility.penrt.unit))
    print("C4: {} {}".format(utility.penrt.c4, utility.penrt.unit))
    print("D: {} {}".format(utility.penrt.d, utility.penrt.unit))

    utilit = En15804LcaData()  # todo löschen

    for building in prj.buildings:
        building.calc_lca_data(False, 50)

        building.add_lca_data_elec(lca_data_elec)

        building.add_lca_data_heat_supply_system_no_s(False, 50)

        utilit += building.lca_data

    print("GWP_Project")
    print("A1_A3: {} {}".format(utilit.gwp.a1_a3, utilit.gwp.unit))
    print("A4: {} {}".format(utilit.gwp.a4, utilit.gwp.unit))
    print("A5: {} {}".format(utilit.gwp.a5, utilit.gwp.unit))
    print("B1: {} {}".format(utilit.gwp.b1, utilit.gwp.unit))
    print("B6: {} {}".format(utilit.gwp.b6, utilit.gwp.unit))
    print("C1: {} {}".format(utilit.gwp.c1, utilit.gwp.unit))
    print("C2: {} {}".format(utilit.gwp.c2, utilit.gwp.unit))
    print("C3: {} {}".format(utilit.gwp.c3, utilit.gwp.unit))
    print("C4: {} {}".format(utilit.gwp.c4, utilit.gwp.unit))
    print("D: {} {}".format(utilit.gwp.d, utilit.gwp.unit))

    print("PERT_Project")
    print("A1_A3: {} {}".format(utilit.pert.a1_a3, utilit.pert.unit))
    print("A4: {} {}".format(utilit.pert.a4, utilit.pert.unit))
    print("A5: {} {}".format(utilit.pert.a5, utilit.pert.unit))
    print("B1: {} {}".format(utilit.pert.b1, utilit.pert.unit))
    print("B6: {} {}".format(utilit.pert.b6, utilit.pert.unit))
    print("C1: {} {}".format(utilit.pert.c1, utilit.pert.unit))
    print("C2: {} {}".format(utilit.pert.c2, utilit.pert.unit))
    print("C3: {} {}".format(utilit.pert.c3, utilit.pert.unit))
    print("C4: {} {}".format(utilit.pert.c4, utilit.pert.unit))
    print("D: {} {}".format(utilit.pert.d, utilit.pert.unit))

    print("PENRT_Project")
    print("A1_A3: {} {}".format(utilit.penrt.a1_a3, utilit.penrt.unit))
    print("A4: {} {}".format(utilit.penrt.a4, utilit.penrt.unit))
    print("A5: {} {}".format(utilit.penrt.a5, utilit.penrt.unit))
    print("B1: {} {}".format(utilit.penrt.b1, utilit.penrt.unit))
    print("B6: {} {}".format(utilit.penrt.b6, utilit.penrt.unit))
    print("C1: {} {}".format(utilit.penrt.c1, utilit.penrt.unit))
    print("C2: {} {}".format(utilit.penrt.c2, utilit.penrt.unit))
    print("C3: {} {}".format(utilit.penrt.c3, utilit.penrt.unit))
    print("C4: {} {}".format(utilit.penrt.c4, utilit.penrt.unit))
    print("D: {} {}".format(utilit.penrt.d, utilit.penrt.unit))

    utili = En15804LcaData()  # todo löschen

    for building in prj.buildings:
        building.calc_lca_data(False, 50)

        building.add_lca_data_elec(lca_data_elec)

        building.add_lca_data_heat_supply_system_no_tw_for_h(False, 50)

        utili += building.lca_data

    print("GWP_Project")
    print("A1_A3: {} {}".format(utili.gwp.a1_a3, utili.gwp.unit))
    print("A4: {} {}".format(utili.gwp.a4, utili.gwp.unit))
    print("A5: {} {}".format(utili.gwp.a5, utili.gwp.unit))
    print("B1: {} {}".format(utili.gwp.b1, utili.gwp.unit))
    print("B6: {} {}".format(utili.gwp.b6, utili.gwp.unit))
    print("C1: {} {}".format(utili.gwp.c1, utili.gwp.unit))
    print("C2: {} {}".format(utili.gwp.c2, utili.gwp.unit))
    print("C3: {} {}".format(utili.gwp.c3, utili.gwp.unit))
    print("C4: {} {}".format(utili.gwp.c4, utili.gwp.unit))
    print("D: {} {}".format(utili.gwp.d, utili.gwp.unit))

    print("PERT_Project")
    print("A1_A3: {} {}".format(utili.pert.a1_a3, utili.pert.unit))
    print("A4: {} {}".format(utili.pert.a4, utili.pert.unit))
    print("A5: {} {}".format(utili.pert.a5, utili.pert.unit))
    print("B1: {} {}".format(utili.pert.b1, utili.pert.unit))
    print("B6: {} {}".format(utili.pert.b6, utili.pert.unit))
    print("C1: {} {}".format(utili.pert.c1, utili.pert.unit))
    print("C2: {} {}".format(utili.pert.c2, utili.pert.unit))
    print("C3: {} {}".format(utili.pert.c3, utili.pert.unit))
    print("C4: {} {}".format(utili.pert.c4, utili.pert.unit))
    print("D: {} {}".format(utili.pert.d, utili.pert.unit))

    print("PENRT_Project")
    print("A1_A3: {} {}".format(utili.penrt.a1_a3, utili.penrt.unit))
    print("A4: {} {}".format(utili.penrt.a4, utili.penrt.unit))
    print("A5: {} {}".format(utili.penrt.a5, utili.penrt.unit))
    print("B1: {} {}".format(utili.penrt.b1, utili.penrt.unit))
    print("B6: {} {}".format(utili.penrt.b6, utili.penrt.unit))
    print("C1: {} {}".format(utili.penrt.c1, utili.penrt.unit))
    print("C2: {} {}".format(utili.penrt.c2, utili.penrt.unit))
    print("C3: {} {}".format(utili.penrt.c3, utili.penrt.unit))
    print("C4: {} {}".format(utili.penrt.c4, utili.penrt.unit))
    print("D: {} {}".format(utili.penrt.d, utili.penrt.unit))

    util = En15804LcaData()  # todo löschen

    for building in prj.buildings:
        building.calc_lca_data(False, 50)

        building.add_lca_data_elec(lca_data_elec)

        building.add_lca_data_heat_supply_system_no_h_or_tw(False, 50)

        util += building.lca_data

    print("GWP_Project")
    print("A1_A3: {} {}".format(util.gwp.a1_a3, util.gwp.unit))
    print("A4: {} {}".format(util.gwp.a4, util.gwp.unit))
    print("A5: {} {}".format(util.gwp.a5, util.gwp.unit))
    print("B1: {} {}".format(util.gwp.b1, util.gwp.unit))
    print("B6: {} {}".format(util.gwp.b6, util.gwp.unit))
    print("C1: {} {}".format(util.gwp.c1, util.gwp.unit))
    print("C2: {} {}".format(util.gwp.c2, util.gwp.unit))
    print("C3: {} {}".format(util.gwp.c3, util.gwp.unit))
    print("C4: {} {}".format(util.gwp.c4, util.gwp.unit))
    print("D: {} {}".format(util.gwp.d, util.gwp.unit))

    print("PERT_Project")
    print("A1_A3: {} {}".format(util.pert.a1_a3, util.pert.unit))
    print("A4: {} {}".format(util.pert.a4, util.pert.unit))
    print("A5: {} {}".format(util.pert.a5, util.pert.unit))
    print("B1: {} {}".format(util.pert.b1, util.pert.unit))
    print("B6: {} {}".format(util.pert.b6, util.pert.unit))
    print("C1: {} {}".format(util.pert.c1, util.pert.unit))
    print("C2: {} {}".format(util.pert.c2, util.pert.unit))
    print("C3: {} {}".format(util.pert.c3, util.pert.unit))
    print("C4: {} {}".format(util.pert.c4, util.pert.unit))
    print("D: {} {}".format(util.pert.d, util.pert.unit))

    print("PENRT_Project")
    print("A1_A3: {} {}".format(util.penrt.a1_a3, util.penrt.unit))
    print("A4: {} {}".format(util.penrt.a4, util.penrt.unit))
    print("A5: {} {}".format(util.penrt.a5, util.penrt.unit))
    print("B1: {} {}".format(util.penrt.b1, util.penrt.unit))
    print("B6: {} {}".format(util.penrt.b6, util.penrt.unit))
    print("C1: {} {}".format(util.penrt.c1, util.penrt.unit))
    print("C2: {} {}".format(util.penrt.c2, util.penrt.unit))
    print("C3: {} {}".format(util.penrt.c3, util.penrt.unit))
    print("C4: {} {}".format(util.penrt.c4, util.penrt.unit))
    print("D: {} {}".format(util.penrt.d, util.penrt.unit))


    # export_building_gwp_csv(prj)
    # export_be_gwp_csv(prj)

    now = datetime.now()

    current_time = now.strftime("%H:%M:%S")
    print("End =", current_time)