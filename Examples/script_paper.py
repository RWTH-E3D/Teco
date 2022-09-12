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
    
    for building in project.buildings:
        if building.name.endswith("_I"):
            type1 = type1 + building.lca_data
        elif building.name.endswith("_II"):
            type2 = type2 + building.lca_data
        elif building.name.endswith("_III"):
            type3 = type3 + building.lca_data
        elif building.name.endswith("_IV"):
            type4 = type4 + building.lca_data
        else:
            print(building.name)
    
    head_row = ["building type", "a1", "a2", "a3", "a1_a3", "a4", "a5", "b1", "b2", "b3", "b4", "b5", "b6", "b7", "c1", "c2", "c3", "c4", "d", "sum", "sum with d"]
    
    type1_list = ["type1"]
    type1_list.extend(gwp_to_list(type1))
    
    type2_list = ["type2"]
    type2_list.extend(gwp_to_list(type2))
    
    type3_list = ["type3"]
    type3_list.extend(gwp_to_list(type3))
    
    type4_list = ["type4"]
    type4_list.extend(gwp_to_list(type4))
    
    export_list = [head_row, type1_list, type2_list, type3_list, type4_list]
    
    with open(path, "w", newline = "") as csvfile:
        writer = csv.writer(csvfile, dialect = "excel")
        writer.writerows(export_list)
    
                  
    
    
            
def export_be_gwp_csv(project, path="buildingelement_gwp_export.csv"):
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
    
    
    head_row = ["buildingelement", "a1", "a2", "a3", "a1_a3", "a4", "a5", "b1", "b2", "b3", "b4", "b5", "b6", "b7", "c1", "c2", "c3", "c4", "d", "sum", "sum with d", "area"]
    
    outer_walls_list = ["outer_walls"]
    outer_walls_list.extend(gwp_to_list(outer_walls))
    outer_walls_list.append(ow_area)
    
    doors_list = ["doors"]
#    doors_list.extend(gwp_to_list(doors))
    doors_list.append(do_area)
    
    rooftops_list = ["rooftops"]
    rooftops_list.extend(gwp_to_list(rooftops))
    rooftops_list.append(rt_area)
    
    ground_floors_list = ["ground_floors"]
    ground_floors_list.extend(gwp_to_list(ground_floors))
    ground_floors_list.append(gf_area)
    
    windows_list = ["windows"]
    windows_list.extend(gwp_to_list(windows))
    windows_list.append(wn_area)
    
    inner_walls_list = ["inner_walls"]
    inner_walls_list.extend(gwp_to_list(inner_walls))
    inner_walls_list.append(iw_area)
    
    floors_list = ["floors"]
    floors_list.extend(gwp_to_list(floors))
    floors_list.append(fl_area)
    
    ceilings_list = ["ceilings"]
    ceilings_list.extend(gwp_to_list(ceilings))
    ceilings_list.append(cl_area)
    
    
    export_list = [head_row, outer_walls_list, doors_list, rooftops_list, ground_floors_list, windows_list, inner_walls_list, floors_list, ceilings_list]
    
    with open(path, "w", newline = "") as csvfile:
        writer = csv.writer(csvfile, dialect = "excel")
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


if __name__ == '__main__':
    prj = Project(load_data=True)
    
    prj.name = "Teaser+Eco_paper"
    
    #prj.load_citygml(path = "D:\\Sciebo\\SmartQuart_E3D\\Geometrie\\SmartQuart_LoD2 District Models\\Final\\Bedburg\\converted or combined\\Bedburg_LoD2.gml", method = "tabula_de")
    prj.add_residential(
        method="tabula_de",
        usage="single_family_house",
        name="Typ I",
        year_of_construction=2015,
        number_of_floors=2,
        height_of_floors=2.5,
        net_leased_area=167)

    prj.used_library_calc = "AixLib"
    
    prj.calc_all_buildings()

    prj.export_aixlib(path = "C:\\Users\\MSchildt\\TEASEROutput")

    sim.simulate(path = "C:\\Users\\MSchildt\\TEASEROutput", prj = prj, loading_time = 3600, result_path = "C:\\Users\\MSchildt\\TEASEROutput\\results")
    
    lca_data_elec = En15804LcaData()
    lca_data_elec.load_lca_data_template("c869c47e-ce43-45b4-b640-b0cd1746e450", prj.data)
    
    utilities = En15804LcaData()

    
    for building in prj.buildings:
        
        #floor heating
        building.add_lca_data_template("ed997c1e-274c-4d38-a5bf-2016693c91a3", building.net_leased_area)
        
        #hot water storage tank (500l -> 88.3 kg storage mass according to oekobaudat.de)
        building.add_lca_data_template("d3f58b23-9526-43be-8a32-fb583dfebfaa", 88.3)
        
        #heat pump
        building.add_lca_data_template("7d027677-b2e3-40dd-a4b1-91bd8f7383d5", 1)
        
        #uebergabestation
        building.add_lca_data_template("dcd5e23a-9bec-40b6-b07c-1642fe696a2e", 30)
        
        
        
        utilities += building.lca_data

        building.calc_lca_data(False, 50)
        
        #print(building.lca_data.gwp.b6)
        
        
        
        building.add_lca_data_elec(lca_data_elec)
        
        building.add_lca_data_heating(1.525, lca_data_elec)

        print(building.lca_data.gwp.b6)
        
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
    
    export_building_gwp_csv(prj)
    export_be_gwp_csv(prj)
    
    now = datetime.now()
    
    current_time = now.strftime("%H:%M:%S")
    print("End =", current_time)


"""
def print_be_information(self):
   prints area and gwp of all buildingelements from the building.

  
    outer_walls = {"area": 0, "gwp": None }
    doors = {"area": 0, "gwp": None }
    rooftops = {"area": 0, "gwp": None }
    ground_floors = {"area": 0, "gwp": None }
    windows = {"area": 0, "gwp": None }
    inner_walls = {"area": 0, "gwp": None }
    floors = {"area": 0, "gwp": None }
    ceilings = {"area": 0, "gwp": None }
    
    for tz in self.thermal_zones:
        for ow in tz.outer_walls:
            outer_walls["area"] = outer_walls["area"] + ow.area
        for do in tz.doors:
            doors["area"] = doors["area"] + ow.area
        for rt in tz.rooftops:
            rooftops["area"] = rooftops["area"] + rt.area
        for gf in tz.ground_floors:
            ground_floors["area"] = ground_floors["area"] + gf.area
        for wn in tz.windows:
            windows["area"] = windows["area"] + wn.area
        for iw in tz.inner_walls:
            inner_walls["area"] = inner_walls["area"] + iw.area
        for fl in tz.floors:
            floors["area"] = floors["area"] + fl.area
        for ce in tz.ceilings:
            ceilings["area"] = ceilings["area"] + ce.area
            
            
    print("outer walls area: {}".format(outer_walls["area"]))
    print("doors area: {}".format(doors["area"]))
    print("rooftops area: {}".format(rooftops["area"]))
    print("ground_floors area: {}".format(ground_floors["area"]))
    print("windows area: {}".format(windows["area"]))
    print("inner_walls area: {}".format(inner_walls["area"]))
    print("floors area: {}".format(floors["area"]))
    print("ceilings area: {}".format(ceilings["area"]))
"""