from teco.logic.buildingobjects.buildingsystems.utility import Utility
from teco.data.input.utility_input_json import load_en15804_lca_data
from teco.project import Project
import simulate as sim

if __name__ == '__main__':

    prj = Project(load_data=True)

    prj.name = "test_utilities_data"

    prj.add_residential(
        method='tabula_de',
        usage='single_family_house',
        name="Typ I",
        year_of_construction=2015,
        number_of_floors=2,
        height_of_floors=2.5,
        net_leased_area=167.0)

    prj.calc_all_buildings()  # simulation parameters are calculated

    prj.export_aixlib()  # model export

    # Simulation is started. Please exchange the file paths ;)
    sim.simulate(path="C:\\Users\\tayeb\\TEASEROutput", prj=prj, loading_time=3600,
                 result_path="C:\\Users\\tayeb\\TEASEROutput\\test")

    # Instance of Utility class is created
    ut = Utility(parent=prj.buildings[0], name="Gas condensing boiler < 20 kW")

    # load lca data from Utilities.json
    load_en15804_lca_data(utility=ut, data_class=prj.data, building_archetype='')

    # print loaded lca data to console
    indicators = ['pere', 'perm', 'pert', 'penre', 'penrm', 'penrt', 'sm', 'rsf', 'nrsf', 'fw', 'hwd', 'nhwd', 'rwd',
                  'cru', 'mfr', 'mer', 'eee', 'eet', 'gwp', 'odp', 'pocp', 'ap', 'ep', 'adpe', 'adpf']
    for indicator in indicators:
        print(indicator, ':', getattr(ut.lca_data, indicator).get_values_as_dict())
