from teaser.project import Project
from teaser.data.input.citygml_input import load_gml_lxml
from Teco import simulate as sim

if __name__ == '__main__':
    prj = Project(load_data=True)
    prj.name = "testArchetype"

    """prj.use_b4 = True  # Parameters for the calculation of the life cycle assessment. Phase "b4" according to EN15804 is used

    prj.add_residential(
        method='iwu',
        usage='single_family_dwelling',
        name="Typ I",
        year_of_construction=2015,
        number_of_floors=2,
        height_of_floors=2.5,
        net_leased_area=167)  # building is added. method and usage specify the enrichment method
"""
    load_gml_lxml(path = "D:\\Users\\MSchildt\\Documents\\repos\\e3d_gitlab\\teco\\Examples\\FZK-Haus-LoD2-KIT-IAI-KHH-B36-V1.gml", prj = prj, method = "tabula_de")
    prj.calc_all_buildings()  # simulation parameters are calculated

    prj.export_aixlib()  # model export

    # Simulation is started. Please exchange the file paths ;)
    sim.simulate(path="C:\\Users\\MSchildt\\TEASEROutput", prj=prj, loading_time=3600,
                 result_path="C:\\Users\\MSchildt\\TEASEROutput\\results")
