# created August 2022
# by TEASERplus and TECO Team

"""This module includes the Building class
"""

import uuid
from teaser.logic.buildingobjects.building import Building
from teco.logic.buildingobjects.buildingphysics.en15804lcadata import En15804LcaData


class Building(Building):

    """
    lca_data : En15804LcaData
        enviromental indicators of the building. The data referencing to
        one building
    additional_lca_data : En15804LcaData
        additional environmental indicators to the indicators from the
        buildingelements (e.g.central heating system)
    _estimate_elec_demand : float [MJ]
        estimate annual electric demand of the building (without heating)
    simulated_heat_load : list
        heat load simulated for this building. Value is used to calculated the
        enviromental indicators for heating
"""

    def __init__(
            self,
            parent=None,
            name=None,
            year_of_construction=None,
            net_leased_area=None,
            with_ahu=False,
            internal_gains_mode=1,
    ):
        """Constructor of Building Class
        """

        super(Building, self).__init__(
            parent,
            name,
            year_of_construction,
            net_leased_area,
            with_ahu,
            internal_gains_mode,
        )

        self._lca_data = None
        self._additional_lca_data = None

        self._estimate_elec_demand = None
        self._simulated_heat_load = None

    @property
    def lca_data(self):
        return self._lca_data

    @lca_data.setter
    def lca_data(self, value):
        self._lca_data = value

    @property
    def additional_lca_data(self):
        return self._additional_lca_data

    @additional_lca_data.setter
    def additional_lca_data(self, value):
        self._additional_lca_data = value

    @property
    def simulated_heat_load(self):
        return self._simulated_heat_load

    @simulated_heat_load.setter
    def simulated_heat_load(self, value):
        self._simulated_heat_load = value

    def calc_lca_data(self, use_b4 = None, period_lca_scenario = None):
        """calculates the environmental indicators of the building. Without
        environmental indicators from heating and electric demand
        
        Parameters
        ----------
        use_b4 : bool, optional
            if true environmental indicators of replaced buildingelements are 
            added to stage B4. Otherwise they are added seperatly to the other stages
        period_lca_scenario : int, optional
            period of use taken into account for LCA. Default is the project 
            period (period_lca_scenario in project class)
        """
        lca_data = En15804LcaData()
        
        if use_b4 is None:
            try:
                use_b4 = self.parent.parent.parent.use_b4
            except:
                use_b4 = False
        
        if period_lca_scenario == None:
            try:
                period_lca_scenario = self.parent.parent.parent.period_lca_scenario
            except:
                print("Please enter a period for the LCA-scenario!")
        
        for thermal_zone in self.thermal_zones:
            
            try:
                thermal_zone.calc_lca_data(use_b4, period_lca_scenario)
                lca_data = lca_data + thermal_zone.lca_data
            except:
                print("Error while adding lca-data from thermal zone")
                
        if self.additional_lca_data is not None:
            if self.additional_lca_data.ref_flow_unit == "pcs":
                scalar = self.additional_lca_data.ref_flow_value
                lca_data = lca_data + self.additional_lca_data * scalar
            
        self.lca_data = lca_data
        
    def est_elec_demand(self):
        """roughly estimates the electricity demand of the building due to it´s
        size, without electricity used for heating (e.g. for heat pumps)
        
        """
        
        q_el_ges_a = None
        d_a = 365 #days in a year
        q_el_b = 63 #Wh/(m^2 d) DIN 18599-10
        a_ngf = self.net_leased_area
        h_B = 8 #hours lighting per day estimate from DIN 18599-10
        q_el_B = 10 * a_ngf*d_a * h_B * 0.001 #estimate from DIN 18599-4
        q_el_wp = 0 #electrical energy for heat pump allready considered in heatload
        
        q_el_ges_a = d_a * q_el_b * a_ngf * 0.001 + q_el_B + q_el_wp
        
        q_el_ges_a = q_el_ges_a * 3.6 #conversion kWh -> MJ       
        
        self._estimate_elec_demand = q_el_ges_a
    
    def add_lca_data_elec(self, lca_data):
        """Calculates enviromental indicators resulting form electric 
        energy consumption

        Parameters
        ----------
        lca_data : En15804LcaData
            LCA-Dataset representing the used power generation mix

        """
        
        if self._estimate_elec_demand is None:
            self.est_elec_demand()
        
        if lca_data.ref_flow_unit != "MJ":
            try:
                lca_data = lca_data.convert_ref_unit("MJ")
            except:
                print("Unit of the reference flow has to be MJ!")
        
        lca_data = lca_data * self._estimate_elec_demand
        
        if self.lca_data is not None:
            self.lca_data = self.lca_data + lca_data
        else:
            self.lca_data = lca_data
    
    def _calc_simulated_annual_heat_energy(self):
        """calculates the annual heating energy from the simulated heatload

        Returns
        -------
        result : Float
            annual heating energy.

        """
        if self.simulated_heat_load is not None:
            previous_ts = None
            
            result = 0
            
            for data_tp in self.simulated_heat_load:
                if previous_ts is not None:
                    result = result + data_tp[1] * (data_tp[0] - previous_ts)
                previous_ts = data_tp[0]
            
            result = result * 0.000001
            
            return result
                
                
    
    def add_lca_data_heating(self, efficiency, lca_data, annual_heat_energy = None):
        """Calculates enviromental indicators resulting form heating

        Parameters
        ----------
        efficiency : float
            overall efficiency of the heating-system.
        annual_heat_load : float [MJ]
            heat load of the building over a year.
        lca_data : En15804LcaData
            LCA-Dataset representing the used energy carrier.

        """
        if annual_heat_energy is None:
            annual_heat_energy = self._calc_simulated_annual_heat_energy()
        
        if lca_data.ref_flow_unit != "MJ":
            try:
                lca_data = lca_data.convert_ref_unit("MJ")
            except:
                print("Unit of the reference flow has to be MJ!")
        lca_data = lca_data * (1/efficiency) * annual_heat_energy * self.parent.period_lca_scenario
        lca_data.unit = "pcs"
                
        if self.lca_data is not None:
            self.lca_data = self.lca_data + lca_data
        else:
            self.lca_data = lca_data
        
    def add_lca_data_template(self, lca_data_id, amount):
        """This function loads environmental indicators from the JSON,
        multiplies it with an amount and add it to the building LCA-Data

        Parameters
        ----------
        lca_data_id : uuid
            uuid of the Dataset to be loaded.
        amount : float
            factor.
        """
        lca_data = En15804LcaData()
        
        lca_data.load_lca_data_template(lca_data_id, data_class = self.parent.data)
        
        if self.lca_data is not None:
            self.lca_data = self.lca_data + lca_data * amount
        else:
            self.lca_data = lca_data * amount
        
    def print_be_information(self):
        """prints area of all buildingelements
        """
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