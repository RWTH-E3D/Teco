from teaser.data.input.citygml_input import load_gml_lxml
from teco.logic.buildingobjects.buildingsystems.utility import Utility
from teco.data.input.utility_input_json import load_en15804_lca_data
from teaser.project import Project

if __name__ == '__main__':

    prj = Project(load_data=True)

    prj.name = "test"

    prj.add_residential(
        method='tabula_de',
        usage='single_family_house',
        name="Typ I",
        year_of_construction=2015,
        number_of_floors=2,
        height_of_floors=2.5,
        net_leased_area=167)


    ut= Utility(parent=prj.buildings[0], name="Gas condensing boiler < 20 kW")

    load_en15804_lca_data(building_archetype="DE.N.SFH.11.Gen.ReEx.001.003",utility=ut,data_class=ut.parent.parent.data)

