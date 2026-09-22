"""This module contains the calculations necessary for the BS2023 paper"""

from pathlib import Path
from teco.project import Project
import old_simulate as sim
import utilities as ut

from teco.logic.buildingobjects.buildingphysics.en15804lcadata import En15804LcaData
import old_lca_csv_export as lca_csv

if __name__ == '__main__':

    method = "zub" #select method

    #constants
    path_weather = Path.cwd() / "input" / "weatherdata" / "TRY2015_535578100702_Jahr.mos"
    path_citygml = Path.cwd() / "input" / "district_residential_LoD2_YOCed.gml"
    path_models = Path.cwd() / "output" / "models" / method
    path_results_models = Path.cwd() / "output" / "results_models" / method
    path_results_lca = Path.cwd() / "output" / "results_lca"

    prj = Project(load_data=True)
    prj.name = f"bs2023_masc_{method}"

    prj.weather_file_path = path_weather

    prj.load_citygml(path=path_citygml, method=method)
    #prj.add_residential(
    #        method='tabula_de',
    #        usage='terraced_house',
    #        name="ResidentialBuildingTabula",
    #        year_of_construction=1968,
    #        number_of_floors=2,
    #        height_of_floors=2.5,
    #        net_leased_area=167.0)


    prj.calc_all_buildings()

    prj.export_aixlib(path = path_models)


    sim.simulate(path = str(path_models), prj = prj, loading_time = 3600, result_path = str(path_results_models / "result.csv") )



    lca_data_electricity = En15804LcaData()
    lca_data_electricity.load_lca_data_template("c869c47e-ce43-45b4-b640-b0cd1746e450", prj.data)

    lca_data_natural_gas = En15804LcaData()
    lca_data_natural_gas.load_lca_data_template("b0ab4c94-268d-40a8-9a46-ba0606c647d1", prj.data)


    #utilities =  En15804LcaData()

    for building in prj.buildings:
        case = ut.look_up_case(building)
        ut.add_utilities(case, building)

        #utilities+=building.lca_data

        building.calc_lca_data(False, 50)

        building.add_lca_data_elec(lca_data_electricity)
        building.add_lca_data_heating(0.95, lca_data_natural_gas)



    lca_csv.export_lca_csv_project_by_building(prj, path_results_lca, "gwp")
    lca_csv.export_lca_csv_project_by_building(prj, path_results_lca, "odp")
    lca_csv.export_lca_csv_project_by_building(prj, path_results_lca, "ap")

    lca_csv.export_lca_csv_project_by_be(prj, path_results_lca, "gwp")
    lca_csv.export_lca_csv_project_by_be(prj, path_results_lca, "odp")
    lca_csv.export_lca_csv_project_by_be(prj, path_results_lca, "ap")



    # lca_csv.export_lca_csv_lca_data(utilities, Path.cwd() / "output" / "results_lca"/"util_gwp.csv", "gwp")
    # lca_csv.export_lca_csv_lca_data(utilities, Path.cwd() / "output" / "results_lca"/"util_odp.csv", "odp")
    # lca_csv.export_lca_csv_lca_data(utilities, Path.cwd() / "output" / "results_lca"/"util_ap.csv", "ap")