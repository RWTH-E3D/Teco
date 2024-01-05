# created December 2023
# by Clara Schmitz (master thesis)

"""This module includes a class for the Heat Supply System
"""
import math

from teaser.teaser.logic.buildingobjects.buildingsystems.heatsupplysystem import HeatSupplySystem
from teco.logic.buildingobjects.buildingphysics.en15804lcadata import En15804LcaData


class HeatSupplySystem(HeatSupplySystem):

    """

        Parameters
            ----------

            parent: Building()

            Attributes
            ----------

        """

    def __init__(self, parent=None):
        """Constructor for HeatSupplySystem
        """

        super(HeatSupplySystem, self).__init__(
            parent,
        )

        self.lca_data = None
        self.component = []
        self.service_life = None

    def calc_lca_data(self, use_b4=None, period_lca_scenario=None):
        """calculates the LCA-data of the buildingelement and set it to the
            attribute lca_data


        Parameters
        ----------
        use_b4 : bool, optional
            if true all replaced materials and building elements are added to
            stage B4. The default is None.
        period_lca_scenario : int [a], optional
            period of use taken into account for LCA.

        """

        if use_b4 is None:
            try:
                use_b4 = self.parent.parent.parent.use_b4
            except:
                use_b4 = False

        if period_lca_scenario is None:
            try:
                period_lca_scenario = self.parent.parent.parent.period_lca_scenario
            except:
                print("Please enter a period for the LCA-scenario!")

        lca_data = En15804LcaData()
        lca_data.ref_flow_unit = "pcs"

        if self.service_life:

            n_be_repl = int(period_lca_scenario / self.service_life)
            remaining_period = period_lca_scenario % self.service_life

            if use_b4:
                lca_data = n_be_repl * self.calc_lca_data_no_repl()
                lca_data = lca_data + (n_be_repl + 1) * self._calc_lca_data_layer_repl(self.service_life)
                lca_data = lca_data + self._calc_lca_data_layer_repl(remaining_period)
                lca_data = lca_data.sum_to_b4()
                lca_data = lca_data + self.calc_lca_data_no_repl()

            else:
                lca_data = (n_be_repl + 1) * self._calc_lca_data_no_repl()
                lca_data = lca_data + (n_be_repl + 1) * self._calc_lca_data_layer_repl(self.service_life)
                lca_data = lca_data + self._calc_lca_data_layer_repl(remaining_period)
        else:
            if use_b4:
                lca_data = self._calc_lca_data_layer_repl(period_lca_scenario)
                lca_data = lca_data.sum_to_b4()
                lca_data = lca_data + self._calc_lca_data_no_repl()
            else:
                lca_data = self._calc_lca_data_no_repl()
                lca_data = lca_data + self._calc_lca_data_layer_repl(period_lca_scenario)

        self.lca_data = lca_data

        heat_supply_system = self.get_buildingelements()

        for building_element in building_elements:

            try:
                building_element.calc_lca_data(use_b4, period_lca_scenario)
                lca_data = lca_data + building_element.lca_data
            except:
                print("Error while adding {}".format(type(building_element).__name__))

        self.lca_data = lca_data

    def _lca_data_pipes(self):
        """Helper function for matrix calculation.

        Gathers all material properties of the building element and returns
        them as a np.array. Needed for the calculation of the matrix in
        equivalent_res(t_bt) especially for walls.

        Returns
        ----------

        """

        lca_data = En15804LcaData()
        lca_data.ref_flow_unit = "kg"

        if self._pipe_routing_heating == "centralised outside":

            length_horizontal_heating = 4 * self._length_char - 10
            length_strand_heating = self._length_char * self.parent.number_of_floors
            length_tethers_heating = self._length_char * self.parent.number_of_floors * 2 / 3

        elif self._pipe_routing_heating == "centralised inside":

            length_horizontal_heating = 2 * self._length_char - 10
            length_strand_heating = self._length_char * self.parent.number_of_floors / 2
            length_tethers_heating = self._length_char * self.parent.number_of_floors * 4

        elif self._pipe_routing_heating == "decentralised":

            length_strand_heating = self._length_char * self.parent.number_of_floors * 6
            length_tethers_heating = self._length_char * self.parent.number_of_floors

        length_pipes_26 = length_strand_heating + length_tethers_heating
        area_insulation_26 = (0.026 * 1.5) ** 2 * math.pi - 0.026 ** 2 * math.pi

        length_pipes_20 = length_horizontal_heating
        area_insulation_20 = (0.02 * 1.5) ** 2 * math.pi - 0.02 ** 2 * math.pi

        lca = lca_stahlrohr * (length_pipes_26 * 1.63 + length_pipes_20 * 1.26) + \
              lca_data_daemmung * (length_pipes_26 * area_insulation_26 + length_pipes_20 * area_insulation_20)

        if self._pipe_routing_water == "centralised with circulation":

            length_horizontal_water = 2 * self._length_char - 10
            length_strand_water = self._length_char * self.parent.number_of_floors / 2
            length_stubs_water = self._length_char * self.parent.number_of_floors / 2

        elif self._pipe_routing_water == "centralised without circulation":

            length_horizontal_water = self._length_char - 5
            length_strand_water = self._length_char * self.parent.number_of_floors / 4
            length_stubs_water = self._length_char * self.parent.number_of_floors / 2

        elif self._pipe_routing_water == "decentralised":

            length_stubs_water = self._length_char * self.parent.number_of_floors / 2

        length_pipes_water = length_horizontal_water + length_strand_water + length_stubs_water

        if math.ceil(self.parent.net_leased_area / 100) <= 1:
            weight = 0.082
            area_insulation = (0.014 * 1.5) ** 2 * math.pi - 0.014 ** 2 * math.pi
        elif math.ceil(self.parent.net_leased_area / 100) == 2:
            weight = 0.089
            area_insulation = (0.016 * 1.5) ** 2 * math.pi - 0.016 ** 2 * math.pi
        else:
            weight = 0.115
            area_insulation = (0.02 * 1.5) ** 2 * math.pi - 0.02 ** 2 * math.pi

        lca = lca_pb * length_pipes_water * weight + lca_data_insulation * length_pipes_water * area_insulation


    # auch service life integrieren bei folgenden Formeln (aus ÖKOBAUDAT)
    def _lca_data_heat_generation(self):
        lca_data = En15804LcaData()
        lca_data.ref_flow_unit = "pcs"

        if self.heat_system == "gas":
            if self._heat_generation == "circulating water heater":
                lca_data = math.ceil(self.parent.simulated_heat_load / 1000 / 20) * lca_cwh  # 20 kW [pcs]
            elif self._heat_generation == "low temperature":
                sizes = [400, 120, 20]
                count = {}
                volume = self.parent.simulated_heat_load / 1000
                for size in sorted(sizes, reverse=True):
                    count = volume // size
                    if count > 0:
                        count[size] = count
                        volume %= size
                lca_data = count[400] * lca_400 + count[120] * lca_120 + count[20] * lca_20
            else:
                sizes = [400, 120, 20]
                count = {}
                volume = self.parent.simulated_heat_load / 1000
                for size in sorted(sizes, reverse=True):
                    count = volume // size
                    if count > 0:
                        count[size] = count
                        volume %= size
                lca_data = count[400] * lca_400 + count[120] * lca_120 + count[20] * lca_20

            if self.parent.net_leased_area <= 180:
                if self.parent.year_of_construction >= 2016 or self._year_of_retrofit >= 2016:
                    lca_data = lca_data + lca_tank_2700
                else:
                    if self.parent.net_leased_area <= 130:
                        lca_data = lca_data + lca_tank_2700
                    else:
                        lca_data = lca_data + lca_tank_4850

            else:
                if self.parent.net_leased_area >= 210:
                   lca_data = lca_data + lca_tank_6400
                else:
                    lca_data = lca_data + lca_tank_4850

        elif self._heat_system == "oil":
            if self._heat_generation == "condensing":
                sizes = [400, 120, 20]
                count = {}
                volume = self.parent.simulated_heat_load / 1000
                for size in sorted(sizes, reverse=True):
                    count = volume // size
                    if count > 0:
                        count[size] = count
                        volume %= size
                lca_data = count[400] * lca_400 + count[120] * lca_120 + count[20] * lca_20
            else:
                sizes = [400, 120, 20]
                count = {}
                volume = self.parent.simulated_heat_load / 1000
                for size in sorted(sizes, reverse=True):
                    count = volume // size
                    if count > 0:
                        count[size] = count
                        volume %= size
                lca_data = count[400] * lca_400 + count[120] * lca_120 + count[20] * lca_20

            if self.parent.year_of_construction >= 2016 or self._year_of_retrofit >= 2016:
                lca_data = math.ceil(self.parent.net_leased_area / 100) * lca_1500  # 1500 l [pcs]
            else:
                lca_data = math.ceil(self.parent.net_leased_area / 100) * lca_1500 * 2  # 3000 l [pcs]

        elif self._heat_system == "electricity":
            if self._heat_generation == "night storage":
                    lca_data = math.ceil(self.parent.simulated_heat_load / 1000 / 21) + lca_data_ns  # 21 kW [pcs]
            elif self._heat_generation == "heatpump air":
                sizes = [14, 10, 7]
                count = {}
                volume = self.parent.simulated_heat_load / 1000
                for size in sorted(sizes, reverse=True):
                    count = volume // size
                    if count > 0:
                        count[size] = count
                        volume %= size
                lca_data = count[14] * lca_14 + count[10] * lca_10 + count[7] * lca_7
            else:
                sizes = [70, 20, 10]
                count = {}
                volume = self.parent.simulated_heat_load / 1000
                for size in sorted(sizes, reverse=True):
                    count = volume // size
                    if count > 0:
                        count[size] = count
                        volume %= size
                lca_data = count[70] * lca_70 + count[20] * lca_20 + count[10] * lca_10 + \
                           count[70] * lca_70_pipes + count[20] * lca_20_pipes + count[10] * lca_10_pipes
        elif self._heat_system == "biomass":
            sizes = [120, 20]
            count = {}
            volume = self.parent.simulated_heat_load / 1000
            for size in sorted(sizes, reverse=True):
                count = volume // size
                if count > 0:
                    count[size] = count
                    volume %= size
            lca_data = count[120] * lca_120 + count[20] * lca_20
        else:
            lca_data = lca_distirct


    def _lca_data_buffer_storage(self):
        # water
        lca_data = En15804LcaData()
        lca_data.ref_flow_unit = "pcs"

    def _lca_data_pump(self):
        lca_data = En15804LcaData()
        lca_data.ref_flow_unit = "pcs"
        if self._pipe_routing_heating == "centralised":

            if self._design_temp_flow == 90:
                temp_diff = 20
            elif self._design_temp_flow == 70:
                temp_diff = 15
            elif self._design_temp_flow == 55:
                temp_diff = 10
            else:
                temp_diff = 7

            flow_rate = self.parent.simulated_heat_load / (1 * 1.163 * temp_diff)

            if flow_rate > (240 * 0.06):  # https://www.viva-aqua.de/250-watt-umwaelzpumpe
                lca_data = lca_data_250bis1000
            elif flow_rate < 2.3:  # https://www.ando-technik.com/ebara-heizungspumpe-ego-25-60-180-230v-50w
                lca_data = lca_data_bis50
            else:
                lca_data = lca_data_50bis250

    def _lca_data_solar(self):
        #Kollektor
        lca_data = En15804LcaData()
        lca_data.ref_flow_unit = "pcs"
        if self._storage_water == "solar":
            lca_data = lca_data_flachkollektor * self.parent.net_leased_area / 100 * 3.05


    def _lca_data_radiator(self):
        # FB oder Heizkörper
        lca_data = En15804LcaData()
        lca_data.ref_flow_unit = "pcs"
        if "heatpump" in self._heat_generation:
            lca_data = self.parent.net_leased_area * lca_data_fbheizung  # floor heating 100mm distance [m^2]
        else:
            if self._design_temp_flow == 55:
                lca_data = self.parent.simulated_heat_load / 735 * 31.3 * lca_data_heizkörper  # radiator Type 22 0,5 m * 1 m [kg]
            else:
                lca_data = self.parent.simulated_heat_load / 1169 * 31.3 * lca_data_heizkörper # radiator Type 22 0,5 m * 1 m [kg]
            # 35 °C only for heatpump

    def _lca_data_pe(self, pe_heating, pe_water):
        """Calculates the total annual primary energy demand of the heat_supply_system

                Parameters
                ----------
                pe_heating : PEDemandHeating()
                    PEDemandHeating() instance of TEASER
                pe_water : PEDemandWater()
                    PEDemandWater() instance of TEASER
                """

        ass_error_1 = "pe_heating has to be an instance of PEDemandHeating()"
        ass_error_2 = "pe_water has to be an instance of PEDemandWater()"

        assert type(pe_heating).__name__ == "PEDemandHeating", ass_error_1
        assert type(pe_water).__name__ == "PEDemandWater", ass_error_2

        pe_energy = pe_heating.calc_primary_energy_demand_heating() + pe_water.calc_primary_energy_demand_water()

    @property
    def lca_data(self):
        return self._lca_data

    @lca_data.setter
    def lca_data(self, value):
        self._lca_data = value
