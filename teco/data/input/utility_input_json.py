"""This module contains functions to load LCA JSON-data of utilities from dataclass into En15804LcaData objects"""

import json
from teco.logic.buildingobjects.buildingsystems.utility import Utility

from teco.logic.buildingobjects.buildingphysics.en15804indicatorvalue import En15804IndicatorValue



def load_en15804_lca_data(building_archetype, utility, data_class):
    """LCA-data loader with building archetype as identification.

    Loads LCA-data specified in the JSON.

    Parameters
    ----------
    building_archetype : str
        code for archetype in JSON

    utility : Utility()
        utility class instance

    data_class : DataClass()
        DataClass containing the bindings for LCA-data
        (typically this is the data class stored in prj.data,
        but the user can individually change that.

    """

    bindings = data_class.utilities_data_bind

    for archetype, data in bindings.items():
        if archetype == building_archetype:

            try:
                data = data['Utilities'][utility.name]
            except KeyError:
                print("Could not find utility with name: " + utility.name)

            pere = En15804IndicatorValue()
            perm = En15804IndicatorValue()
            pert = En15804IndicatorValue()
            penre = En15804IndicatorValue()
            penrm = En15804IndicatorValue()
            penrt = En15804IndicatorValue()
            sm = En15804IndicatorValue()
            rsf = En15804IndicatorValue()
            nrsf = En15804IndicatorValue()
            fw = En15804IndicatorValue()
            hwd = En15804IndicatorValue()
            nhwd = En15804IndicatorValue()
            rwd = En15804IndicatorValue()
            cru = En15804IndicatorValue()
            mfr = En15804IndicatorValue()
            mer = En15804IndicatorValue()
            eee = En15804IndicatorValue()
            eet = En15804IndicatorValue()
            gwp = En15804IndicatorValue()
            odp = En15804IndicatorValue()
            pocp = En15804IndicatorValue()
            ap = En15804IndicatorValue()
            ep = En15804IndicatorValue()
            adpe = En15804IndicatorValue()
            adpf = En15804IndicatorValue()

            pere.set_values(**data["pere"])
            perm.set_values(**data["perm"])
            pert.set_values(**data["pert"])
            penre.set_values(**data["penre"])
            penrm.set_values(**data["penrm"])
            penrt.set_values(**data["penrt"])
            sm.set_values(**data["sm"])
            rsf.set_values(**data["rsf"])
            nrsf.set_values(**data["nrsf"])
            fw.set_values(**data["fw"])
            hwd.set_values(**data["hwd"])
            nhwd.set_values(**data["nhwd"])
            rwd.set_values(**data["rwd"])
            cru.set_values(**data["cru"])
            mfr.set_values(**data["mfr"])
            mer.set_values(**data["mer"])
            eee.set_values(**data["eee"])
            eet.set_values(**data["eet"])
            gwp.set_values(**data["gwp"])
            odp.set_values(**data["odp"])
            pocp.set_values(**data["pocp"])
            ap.set_values(**data["ap"])
            ep.set_values(**data["ep"])
            adpe.set_values(**data["adpe"])
            adpf.set_values(**data["adpf"])

            utility.lca_data.pere = pere
            utility.lca_data.perm = perm
            utility.lca_data.pert = pert
            utility.lca_data.penre = penre
            utility.lca_data.penrm = penrm
            utility.lca_data.penrt = penrt
            utility.lca_data.sm = sm
            utility.lca_data.rsf = rsf
            utility.lca_data.nrsf = nrsf
            utility.lca_data.fw = fw
            utility.lca_data.hwd = hwd
            utility.lca_data.nhwd = nhwd
            utility.lca_data.rwd = rwd
            utility.lca_data.cru = cru
            utility.lca_data.mfr = mfr
            utility.lca_data.mer = mer
            utility.lca_data.eee = eee
            utility.lca_data.eet = eet
            utility.lca_data.gwp = gwp
            utility.lca_data.odp = odp
            utility.lca_data.pocp = pocp
            utility.lca_data.ap = ap
            utility.lca_data.ep = ep
            utility.lca_data.adpe = adpe
            utility.lca_data.adpf = adpf

