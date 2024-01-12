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
        method='tabula_de',
        usage='multi_family_house',
        name="Typ I",
        year_of_construction=2015,
        number_of_floors=2,
        height_of_floors=2.5,
        net_leased_area=395,
        type_heat_supply_system=1) #building is added. method and usage specify the enrichment method


    """building = Building(parent=prj)
    heatsystem = HeatSupplySystem(parent=building)

    print(type(heatsystem.parent).__name__)

    prj.calc_all_buildings() #simulation parameters are calculated
    
    prj.export_aixlib() #model export
    
    
    #Simulation is started. Please exchange the file paths ;)
    sim.simulate(path = "C:\\Users\\clara\\TEASEROutput", prj = prj, loading_time = 3600, result_path = "C:\\Users\\clara\\TEASEROutput\\test")

    
    #Up to here, except for the "use_b4 parameter", all lines of code are TEASER+ 
    #only. Next comes the LCA part, which is based on EN15804. 
    
    
    
    #https://oekobaudat.de/OEKOBAU.DAT/datasetdetail/process.xhtml?uuid=c869c47e-ce43-45b4-b640-b0cd1746e450&version=20.19.120&stock=OBD_2021_II&lang=de
    lca_data_elec = En15804LcaData() #dataset for electricity
    lca_data_elec.load_lca_data_template("c869c47e-ce43-45b4-b640-b0cd1746e450", prj.data)
    
    prj.buildings[0].calc_lca_data(False, 50)  

    prj.buildings[0].add_lca_data_elec(lca_data_elec) #environmental indicators for electricity consumption
    prj.buildings[0].add_lca_data_heat_supply_system(False, 50) #environemntal indicators for heatload (calculated from the simulation)"""

    