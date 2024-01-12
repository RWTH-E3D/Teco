from teco.project import Project
from teaser.teaser.data.input.citygml_input import load_gml_lxml
from teco.logic.buildingobjects.buildingphysics.en15804lcadata import En15804LcaData
from teco.logic.buildingobjects.buildingsystems.heatsupplysystem import HeatSupplySystem
from teaser.teaser.logic.buildingobjects.building import Building
from teaser.teaser.logic.archetypebuildings.tabula.de.singlefamilyhouse import SingleFamilyHouse
import teco.data.input.lca_data_input as lca_data_input
from teaser.teaser.logic.buildingobjects.thermalzone import ThermalZone
import simulate as sim

if __name__ == '__main__':
    prj = Project(load_data=True)
    prj.name = "testArchetype"

    prj.use_b4 = True  # Parameters for the calculation of the life cycle assessment. Phase "b4" according to EN15804 is used

    sfh = SingleFamilyHouse(parent = prj, name="SingleFamilyHouse", year_of_construction=1997, number_of_floors=2, height_of_floors=2.8, net_leased_area=200, type_heat_supply_system=2,
                        with_ahu=False, internal_gains_mode=1, construction_type="tabula_retrofit")

    sfh.generate_archetype()

    """building = Building(name="SingleFamilyHouse", year_of_construction=1997, net_leased_area=200, type_heat_supply_system=2,
                        with_ahu=False, internal_gains_mode=1)

    #print(building.year_of_construction)
    #print(building.year_of_retrofit)

    building.simulated_heat_load = 22
    heatsystem = HeatSupplySystem(parent=building)
    thermalzone = ThermalZone(parent=building)
    # print(type(thermalzone.parent).__name__)

    building.set_heat_supply_system(heatsystem)
    heatsystem.setting_values()
    print(heatsystem.parent.year_of_construction)
    #print(heatsystem.year_of_retrofit)
    #print(heatsystem._oversizing_factor)
    print(heatsystem.heat_generation)
    print(heatsystem.heat_system)
    print(heatsystem.pipe_routing_water)
    print(heatsystem._heat_loss_distribution_heating)
    print(heatsystem._design_temp_flow)

    # print(type(heatsystem.parent).__name__)
    # if "Bu" in type(heatsystem.parent).__name__:
      #  print("yes")"""
