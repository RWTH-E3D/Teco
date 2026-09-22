
from pathlib import Path
from teco.project import Project
import old_simulate as sim
import utilities as ut

from teco.logic.buildingobjects.buildingphysics.en15804lcadata import En15804LcaData
import old_lca_csv_export as lca_csv


prj = Project(load_data=True)

for i in range(1917, 1980):
     prj.add_residential(
            method='zub',
            usage='multi_family_house',
            name="ResidentialBuildingTabula",
            year_of_construction=i,
            number_of_floors=2,
            height_of_floors=2.5,
            net_leased_area=167.0,
            construction_type = "SchleswigHolstein_woodenconstruction")



prj.calc_all_buildings()

for building in prj.buildings:
    building.calc_lca_data(False, 50)
    print(building.lca_data.gwp.a1_a3)
