# -*- coding: utf-8 -*-
"""
Created on Tue Nov 16 17:08:31 2021

@author: Linus
"""


from teco.project import Project
from teaser.teaser.data.input.citygml_input import load_gml_lxml
from teco.logic.buildingobjects.buildingphysics.en15804lcadata import En15804LcaData
from teco.logic.buildingobjects.buildingsystems.heatsupplysystem import HeatSupplySystem
from teaser.teaser.logic.buildingobjects.building import Building
import teco.data.input.lca_data_input as lca_data_input
import simulate as sim
from teaser.teaser.logic.buildingobjects.thermalzone import ThermalZone


if __name__ == '__main__':
    
    prj = Project(load_data=True)
    prj.name = "testArchetype"
    
    prj.use_b4 = True # Parameters for the calculation of the life cycle assessment. Phase "b4" according to EN15804 is used

    prj.add_residential(
        method="tabula_de",
        usage="single_family_house",
        name="Typ_I",
        year_of_construction=2015,
        number_of_floors=2,
        height_of_floors=2.5,
        net_leased_area=167.0,
        type_heat_supply_system=3) #building is added. method and usage specify the enrichment method

    prj.calc_all_buildings() #simulation parameters are calculated
    
    prj.export_aixlib() #model export
    
    
    #Simulation is started. Please exchange the file paths ;)
    sim.simulate(path="C:\\Users\\user\\TEASEROutput", prj=prj, loading_time=3600,
                 result_path="C:\\Users\\user\\TEASEROutput\\test")

    
    #Up to here, except for the "use_b4 parameter", all lines of code are TEASER+ 
    #only. Next comes the LCA part, which is based on EN15804. 

    
    #https://oekobaudat.de/OEKOBAU.DAT/datasetdetail/process.xhtml?uuid=c869c47e-ce43-45b4-b640-b0cd1746e450&version=20.19.120&stock=OBD_2021_II&lang=de
    lca_data_elec = En15804LcaData() #dataset for electricity
    lca_data_elec.load_lca_data_template("c869c47e-ce43-45b4-b640-b0cd1746e450", prj.data)
    
    prj.buildings[0].calc_lca_data(False, 50)
    prj.buildings[0].add_lca_data_heat_supply_system(False, 50)

    prj.buildings[0].add_lca_data_elec(lca_data_elec) #environmental indicators for electricity consumption

    utilities = En15804LcaData()
    utilities += prj.buildings[0].lca_data

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