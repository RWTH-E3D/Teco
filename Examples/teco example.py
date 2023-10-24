# -*- coding: utf-8 -*-
"""
Created on Tue Nov 16 17:08:31 2021

@author: Linus
"""


from teco.project import Project
from teco.logic.buildingobjects.buildingphysics.en15804lcadata import En15804LcaData
import simulate as sim




if __name__ == '__main__':
    
    prj = Project(load_data=True)
    prj.name = "testArchetype"
    
    prj.use_b4 = True # Parameters for the calculation of the life cycle assessment. Phase "b4" according to EN15804 is used
    
    prj.add_residential(
        method='iwu',
        usage='single_family_dwelling',
        name="Typ I",
        year_of_construction=2015,
        number_of_floors=2,
        height_of_floors=2.5,
        net_leased_area=167) #building is added. method and usage specify the enrichment method
    
    
    prj.calc_all_buildings() #simulation parameters are calculated
    
    prj.export_aixlib() #model export
    
    
    #Simulation is started. Please exchange the file paths ;)
    sim.simulate(path = "C:\\Users\\MSchildt\\TEASEROutput", prj = prj, loading_time = 3600, result_path = "C:\\Users\\MSchildt\\TEASEROutput\\test")

    
    #Up to here, except for the "use_b4 parameter", all lines of code are TEASER+ 
    #only. Next comes the LCA part, which is based on EN15804. 
    
    
    
    #https://oekobaudat.de/OEKOBAU.DAT/datasetdetail/process.xhtml?uuid=c869c47e-ce43-45b4-b640-b0cd1746e450&version=20.19.120&stock=OBD_2021_II&lang=de
    lca_data_elec = En15804LcaData() #dataset for electricity
    lca_data_elec.load_lca_data_template("c869c47e-ce43-45b4-b640-b0cd1746e450", prj.data)
    
    #energy systems are added to the building
    
    #floor heating
    prj.buildings[0].add_lca_data_template("ed997c1e-274c-4d38-a5bf-2016693c91a3", prj.buildings[0].net_leased_area)
    
    #hot water storage tank (500l -> 88.3 kg storage mass according to oekobaudat.de)
    prj.buildings[0].add_lca_data_template("d3f58b23-9526-43be-8a32-fb583dfebfaa", 88.3)
    
    #heat pump
    prj.buildings[0].add_lca_data_template("7d027677-b2e3-40dd-a4b1-91bd8f7383d5", 1)
    
    #
    prj.buildings[0].add_lca_data_template("dcd5e23a-9bec-40b6-b07c-1642fe696a2e", 30)
    
    prj.buildings[0].calc_lca_data(False, 50)  
    
    
    prj.buildings[0].add_lca_data_elec(lca_data_elec) #environmental indicators for electricity consumption
    prj.buildings[0].add_lca_data_heating(1.525, lca_data_elec) #environemntal indicators for heatload (calculated from the simulation)

# print loaded lca data to console
    indicators = ['pere', 'perm', 'pert', 'penre', 'penrm', 'penrt', 'sm', 'rsf', 'nrsf', 'fw', 'hwd', 'nhwd', 'rwd',
                  'cru', 'mfr', 'mer', 'eee', 'eet', 'gwp', 'odp', 'pocp', 'ap', 'ep', 'adpe', 'adpf']
    for indicator in indicators:
        print(indicator, ':', getattr(ut.lca_data, indicator).get_values_as_dict())
    