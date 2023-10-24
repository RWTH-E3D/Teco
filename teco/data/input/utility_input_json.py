"""This module contains functions to load LCA JSON-data of utilities from dataclass into En15804LcaData objects"""

import json
from teco.logic.buildingobjects.buildingsystems.utility import Utility
from teaser.teaser.logic.archetypebuildings.tabula.de.terracedhouse import TerracedHouse
from teaser.teaser.logic.archetypebuildings.tabula.de.apartmentblock import ApartmentBlock
from teaser.teaser.logic.archetypebuildings.tabula.de.multifamilyhouse import MultiFamilyHouse
from teaser.teaser.logic.archetypebuildings.tabula.de.singlefamilyhouse import SingleFamilyHouse
from teco.logic.buildingobjects.buildingphysics.en15804indicatorvalue import En15804IndicatorValue



def load_en15804_lca_data(utility, data_class, building_archetype=''):
    """LCA-data loader with building archetype as identification.

    Loads LCA-data specified in the JSON.

    Parameters
    ----------

    utility : Utility()
        utility class instance

    data_class : DataClass()
        DataClass containing the bindings for LCA-data
        (typically this is the data class stored in prj.data,
        but the user can individually change that.

    building_archetype : str
        code for archetype in JSON
    """

    # build archetype code
    if building_archetype == '':
        building_archetype = 'DE.N.'
        if type(utility.parent) is SingleFamilyHouse: building_archetype += 'SFH.'
        elif type(utility.parent) is MultiFamilyHouse: building_archetype += 'MFH.'
        elif type(utility.parent) is TerracedHouse: building_archetype += 'TH.'
        elif type(utility.parent) is ApartmentBlock: building_archetype += 'AB.'

    bindings = data_class.utilities_data_bind

    for archetype, data in bindings.items():

        if building_archetype in archetype:

            if data['Building_age_group'][0] <= utility.parent.year_of_construction <= data['Building_age_group'][1]:

                try:
                    data = data['Utilities'][utility.name]
                except KeyError:
                    print("Could not find utility: " + utility.name + "\nin archetype: " + archetype)
                    continue

                utility.lca_data.pere.set_values(**data["pere"])
                utility.lca_data.perm.set_values(**data["perm"])
                utility.lca_data.pert.set_values(**data["pert"])
                utility.lca_data.penre.set_values(**data["penre"])
                utility.lca_data.penrm.set_values(**data["penrm"])
                utility.lca_data.penrt.set_values(**data["penrt"])
                utility.lca_data.sm.set_values(**data["sm"])
                utility.lca_data.rsf.set_values(**data["rsf"])
                utility.lca_data.nrsf.set_values(**data["nrsf"])
                utility.lca_data.fw.set_values(**data["fw"])
                utility.lca_data.hwd.set_values(**data["hwd"])
                utility.lca_data.nhwd.set_values(**data["nhwd"])
                utility.lca_data.rwd.set_values(**data["rwd"])
                utility.lca_data.cru.set_values(**data["cru"])
                utility.lca_data.mfr.set_values(**data["mfr"])
                utility.lca_data.mer.set_values(**data["mer"])
                utility.lca_data.eee.set_values(**data["eee"])
                utility.lca_data.eet.set_values(**data["eet"])
                utility.lca_data.gwp.set_values(**data["gwp"])
                utility.lca_data.odp.set_values(**data["odp"])
                utility.lca_data.pocp.set_values(**data["pocp"])
                utility.lca_data.ap.set_values(**data["ap"])
                utility.lca_data.ep.set_values(**data["ep"])
                utility.lca_data.adpe.set_values(**data["adpe"])
                utility.lca_data.adpf.set_values(**data["adpf"])

                return # lca data only need to be loaded once

