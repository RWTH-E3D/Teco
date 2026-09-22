"""This module contains functions for assigning utilities to Teco buildings according to tabula"""
import math

def look_up_case(building):
    """Function to assign a utility case id to a building. Each case id is linked to a special combination of utilities
    (see function add_utilities)

    Parameters
    ----------
    building : Building
        building to which a utility combination is to be assigned

    Returns
    -------

    case_id : int
        case 0, 1, 2, 3 or 4

    """
    if building.construction_type == "tabula_standard":

        if building.type_of_building != "apartment_block":
            return 3

        if building.year_of_construction <= 1994:
            return 0

        if building.year_of_construction <= 2009:
            return 1

        return 2

    else:
        return 0
        #raise NotImplementedError(f"{building.construction_type} not implemented yet!")

def look_up_storage_tank_weight(volume):
    """Function to return the corresponding weight of a thermal storage tank based on its volume according to ökobaudat

    Parameters
    ----------
    volume : int, float
        volume of the thermal storage tank
    Returns
    -------
    weight : int, float
        weight of the thermal storage tank
    """
    if volume is None:
        return 0
    if volume <= 200:
        return 56
    if volume <= 300:
        return 59.5
    if volume <= 500:
        return 88.3
    if volume <= 600:
        return 98
    if volume <= 750:
        return 140
    if volume <= 1000:
        return 164
    if volume <= 1250:
        return 174
    if volume <= 1500:
        return 210.5

    return 239.5


def add_utilities(case_id, building):
    """Procedure for adding utilities according to the selected case_id to a building

    Parameters
    ----------
    case_id : int
        utility case id
    building : Building
        building to which a utility combination is added

    """

    #gas condensing boiler120-400 kW
    building.add_lca_data_template("36d1bbf3-1e67-4a93-92f5-0321cc30018a", 1)

    conversion_dict_steel_watertank = {}

    if case_id == 0:
        pass
    elif case_id == 1:

        # thermal storage tank
        estimated_thremal_storage = building.net_leased_area * (200/300) #Estimation: 200l-tank per 300 m^2 NLA
        mass_storage_tank = look_up_storage_tank_weight(estimated_thremal_storage)
        building.add_lca_data_template("b273afc9-27a1-4a82-a390-8780fd631008", mass_storage_tank)

        # ventilation decentralized
        estimated_decentralized_ventilation = math.floor(building.net_leased_area / 100)
        building.add_lca_data_template("c8cf7494-2f23-4193-a185-f7d4fdfa36b6", estimated_decentralized_ventilation)

        # Flat solar collector
        roof_area = 0

        for tz in building.thermal_zones:
            for rt in tz.rooftops:
                roof_area += rt.area

        estimated_solar_thermal = roof_area / 3 #Estimation: 1/3 of roof area
        building.add_lca_data_template("60e0575b-6cb4-4ba4-a9f0-78d8fb65c9a9", estimated_solar_thermal)

    elif case_id == 2:
        # thermal storage tank
        estimated_thremal_storage = building.net_leased_area * (200 / 300)  # Estimation: 200l-tank per 300 m^2 NLA
        mass_storage_tank = look_up_storage_tank_weight(estimated_thremal_storage)
        building.add_lca_data_template("b273afc9-27a1-4a82-a390-8780fd631008", mass_storage_tank)

        # ventilation decentralized with heat recovery
        estimated_decentralized_ventilation = math.floor(building.net_leased_area / 100)
        building.add_lca_data_template("efabdf2d-993e-418c-ba86-85a3a91562a", estimated_decentralized_ventilation)

        # Flat solar collector
        roof_area = 0

        for tz in building.thermal_zones:
            for rt in tz.rooftops:
                roof_area += rt.area

        estimated_solar_thermal = roof_area / 3  # Estimation: 1/3 of roof area
        building.add_lca_data_template("60e0575b-6cb4-4ba4-a9f0-78d8fb65c9a9", estimated_solar_thermal)

    elif case_id == 3:
        # thermal storage tank
        estimated_thremal_storage = building.net_leased_area * (200 / 300)  # Estimation: 200l-tank per 300 m^2 NLA
        mass_storage_tank = look_up_storage_tank_weight(estimated_thremal_storage)
        building.add_lca_data_template("b273afc9-27a1-4a82-a390-8780fd631008", mass_storage_tank)