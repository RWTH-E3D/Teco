from teaser.project import Project
import pathlib
import uuid
import seaborn as sns
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from pathlib import Path
import pickle

#Create df from gml file containing no building parts and no buildings with net leased area < 50m²

if __name__ == '__main__':
    project_path = pathlib.Path().absolute() # path for teaser and simulate.py (Path.cwd() doesn´t work)
    prj = Project(load_data=True)
    prj.name = "BS2023"

    #prj.load_citygml(path = f"input/district_residential_LoD2_YOCed.gml", method = "tabula_de")
    #prj.calc_all_buildings()

    metadata = {"case_id": [],
                "building_id": [],
                "teaser_year_of_construction": [],
                "teaser_building_age_group": [],
                "teaser_number_of_floors": [],
                "teaser_height_of_floors": [],
                "teaser_net_leased_area": []
                }


    print(len(prj.buildings))

    for building in prj.buildings:

        case_id = uuid.uuid1()

        metadata["case_id"].append(case_id)
        metadata["building_id"].append(building.name)
        #metadata["teaser_method"].append(building.construction_type)
        #metadata["teaser_archetype"].append(building.type_of_building)
        metadata["teaser_year_of_construction"].append(building.year_of_construction)
        metadata["teaser_building_age_group"].append(building.building_age_group)
        metadata["teaser_number_of_floors"].append(building.number_of_floors)
        metadata["teaser_height_of_floors"].append(building.height_of_floors)
        metadata["teaser_net_leased_area"].append(building.net_leased_area)



    #metadata_df = pd.DataFrame(metadata)

    #metadata_df = metadata_df[metadata_df.teaser_net_leased_area > 50]
    #metadata_df = metadata_df[metadata_df.building_id.str.contains("bt_") == False]
    #metadata_df.to_pickle("list_of_buildings.pkl")

    metadata_df = pd.read_pickle("list_of_buildings.pkl")
    metadata_df.to_csv("list_of_buildings.csv", index=False)
    metadata_df.teaser_building_age_group = metadata_df.teaser_building_age_group.astype('string')

#Perform simple statistics (%share of buildings by age group; m² distribution in % per age group)

no_of_buildings = metadata_df.shape[0]

share_of_buildings_1860_to_1918 = round(len(metadata_df[metadata_df.teaser_building_age_group.str.contains("1860") == True].index)
                                        / no_of_buildings, 3)*100

share_of_buildings_1919_to_1948 = round(len(metadata_df[metadata_df.teaser_building_age_group.str.contains("1919") == True].index)
                                        / no_of_buildings, 3)*100

share_of_buildings_1949_to_1957 = round(len(metadata_df[metadata_df.teaser_building_age_group.str.contains("1949") == True].index)
                                        / no_of_buildings, 3)*100

share_of_buildings_1958_to_1968 = round(len(metadata_df[metadata_df.teaser_building_age_group.str.contains("1958") == True].index)
                                        / no_of_buildings, 3)*100

share_of_buildings_1969_to_1978 = round(len(metadata_df[metadata_df.teaser_building_age_group.str.contains("1969") == True].index)
                                        / no_of_buildings, 3)*100

share_of_buildings_1979_to_1983 = round(len(metadata_df[metadata_df.teaser_building_age_group.str.contains("1979") == True].index)
                                        / no_of_buildings, 3)*100

share_of_buildings_1984_to_1994 = round(len(metadata_df[metadata_df.teaser_building_age_group.str.contains("1984") == True].index)
                                        / no_of_buildings, 3)*100

share_of_buildings_1995_to_2001 = round(len(metadata_df[metadata_df.teaser_building_age_group.str.contains("1995") == True].index)
                                        / no_of_buildings, 3)*100

share_of_buildings_2002_to_2009 = round(len(metadata_df[metadata_df.teaser_building_age_group.str.contains("2002") == True].index)
                                        / no_of_buildings, 3)*100

share_of_buildings_2010_to_2015 = round(len(metadata_df[metadata_df.teaser_building_age_group.str.contains("2010") == True].index)
                                        / no_of_buildings, 3)*100


m2_overall = metadata_df.teaser_net_leased_area.sum()

share_m2_1860_to_1918 = round(metadata_df[metadata_df.teaser_building_age_group.str.contains("1860") == True].teaser_net_leased_area.sum()
                              / m2_overall, 3)*100

share_m2_1919_to_1948 = round(metadata_df[metadata_df.teaser_building_age_group.str.contains("1919") == True].teaser_net_leased_area.sum()
                              / m2_overall, 3)*100

share_m2_1949_to_1957 = round(metadata_df[metadata_df.teaser_building_age_group.str.contains("1949") == True].teaser_net_leased_area.sum()
                              / m2_overall, 3)*100

share_m2_1958_to_1968 = round(metadata_df[metadata_df.teaser_building_age_group.str.contains("1958") == True].teaser_net_leased_area.sum()
                              / m2_overall, 3)*100

share_m2_1969_to_1978 = round(metadata_df[metadata_df.teaser_building_age_group.str.contains("1969") == True].teaser_net_leased_area.sum()
                              / m2_overall, 3)*100

share_m2_1979_to_1983 = round(metadata_df[metadata_df.teaser_building_age_group.str.contains("1979") == True].teaser_net_leased_area.sum()
                              / m2_overall, 3)*100

share_m2_1984_to_1994 = round(metadata_df[metadata_df.teaser_building_age_group.str.contains("1984") == True].teaser_net_leased_area.sum()
                              / m2_overall, 3)*100

share_m2_1995_to_2001 = round(metadata_df[metadata_df.teaser_building_age_group.str.contains("1995") == True].teaser_net_leased_area.sum()
                              / m2_overall, 3)*100

share_m2_2002_to_2009 = round(metadata_df[metadata_df.teaser_building_age_group.str.contains("2002") == True].teaser_net_leased_area.sum()
                              / m2_overall, 3)*100

share_m2_2010_to_2015 = round(metadata_df[metadata_df.teaser_building_age_group.str.contains("2010") == True].teaser_net_leased_area.sum()
                              / m2_overall, 3)*100

#Stacked bar chart of m2 and absolute no. of building shares per building age group

x = ['Share of buildings', r'Share of $m^{2}_{NLA}$']
y = np.array([0, 20, 40, 60, 80, 100])

y1 = np.array([share_of_buildings_1860_to_1918, share_m2_1860_to_1918])
y2 = np.array([share_of_buildings_1919_to_1948, share_m2_1919_to_1948])
y3 = np.array([share_of_buildings_1949_to_1957, share_m2_1949_to_1957])
y4 = np.array([share_of_buildings_1958_to_1968, share_m2_1958_to_1968])
y5 = np.array([share_of_buildings_1969_to_1978, share_m2_1969_to_1978])
y6 = np.array([share_of_buildings_1979_to_1983, share_m2_1979_to_1983])
y7 = np.array([share_of_buildings_1984_to_1994, share_m2_1984_to_1994])
y8 = np.array([share_of_buildings_1995_to_2001, share_m2_1995_to_2001])
y9 = np.array([share_of_buildings_2002_to_2009, share_m2_2002_to_2009])
y10 = np.array([share_of_buildings_2010_to_2015, share_m2_2010_to_2015])

bar_width = 0.25

y1_color ='#000506'
y2_color ='#023843'
y3_color ='#145967'
y4_color ='#207182'
y5_color ='#10859c'
y6_color ='#2496ad'
y7_color ='#45b0c6'
y8_color ='#73cbdd'
y9_color ='#9adae7'
y10_color ='#ddf4f8'

plt.bar(x, y1, edgecolor='black', width= bar_width, color=y1_color)
plt.bar(x, y2, bottom=y1, edgecolor='black', width= bar_width, color=y2_color)
plt.bar(x, y3, bottom=y1+y2, edgecolor='black', width= bar_width, color=y3_color)
plt.bar(x, y4, bottom=y1+y2+y3, edgecolor='black', width= bar_width, color=y4_color)
plt.bar(x, y5, bottom=y1+y2+y3+y4, edgecolor='black', width= bar_width, color=y5_color)
plt.bar(x, y6, bottom=y1+y2+y3+y4+y5, edgecolor='black', width= bar_width, color=y6_color)
plt.bar(x, y7, bottom=y1+y2+y3+y4+y5+y6, edgecolor='black', width= bar_width, color=y7_color)
plt.bar(x, y8, bottom=y1+y2+y3+y4+y5+y6+y7, edgecolor='black', width= bar_width, color=y8_color)
plt.bar(x, y9, bottom=y1+y2+y3+y4+y5+y6+y7+y8, edgecolor='black', width= bar_width, color=y9_color)
plt.bar(x, y10, bottom=y1+y2+y3+y4+y5+y6+y7+y8+y9, edgecolor='black', width= bar_width, color=y10_color)
plt.xlabel("n = 302")
plt.ylabel("[%]")
plt.yticks(y)
plt.legend(["1860 to 1918", "1919 to 1948", "1949 to 1957",
            "1958 to 1968", "1969 to 1978", "1979 to 1983",
            "1984 to 1994", "1995 to 2001", "2002 to 2009", "2010 to 2015"], labelspacing=-2.5, bbox_to_anchor=(0.67, 0.2), frameon=False)
plt.title(r"Share of buildings and $m^{2}_{NLA}$ among building age classes")
plt.show()