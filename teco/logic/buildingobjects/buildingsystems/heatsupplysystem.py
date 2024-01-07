# created December 2023
# by Clara Schmitz (master thesis)

"""This module includes a class for the Heat Supply System
"""
import math

from teaser.teaser.logic.buildingobjects.buildingsystems.heatsupplysystem import HeatSupplySystem
from teco.logic.buildingobjects.buildingphysics.en15804lcadata import En15804LcaData
import teco.data.input.lca_data_input as lca_data_input


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

        lca_data = En15804LcaData()
        lca_data.ref_flow_unit = "pcs"
        self.component = []
        self.service_life = None

    def _load_lca_data_template(self, lca_id, data_class=None):
        """LCA-data loader.

        Loads LCA-data specified in the json.

        Parameters
        ----------

        lca_id : str
            LCA-data Identifier

        data_class : DataClass
            DataClass containing the bindings for LCA-data and LCA-data
            -fallbacks (typically this is the data class stored in prj.data,
            but the user can individually change that.)

        """

        if data_class is None:
            data_class = self.parent.parent.parent.parent.data

        lca_data_input.load_en15804_lca_data_id(lca_data=self,
                                                lca_id=lca_id,
                                                data_class=data_class)

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

        lca_data = self._lca_data_pipes() + self._lca_data_heat_generator() + self._lca_data_storage() + \
                   self._lca_data_pump() + self._lca_data_solar() + self._lca_data_heat_transfer() + self._lca_data_fe()

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

    def _lca_data_pipes(self):
        """Helper function for matrix calculation.

        Gathers all material properties of the building element and returns
        them as a np.array. Needed for the calculation of the matrix in
        equivalent_res(t_bt) especially for walls.

        Returns
        ----------

        """

        lca_data_steel_pipe = self._load_lca_data_template("8622539c-592c-45b0-9a4b-e5f8b4fea367")
        lca_data_pipe_insulation = self._load_lca_data_template("75ce5bab-4506-4f7e-8c20-a638a98b7537")
        lca_data_pipe_pb = self._load_lca_data_template("83a21998-b507-429e-bbe3-b5629e601138")

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

        lca_data_pipes_heating = lca_data_steel_pipe * (length_pipes_26 * 1.63 + length_pipes_20 * 1.26) + \
              lca_data_pipe_insulation * (length_pipes_26 * area_insulation_26 + length_pipes_20 * area_insulation_20)

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

        lca_data_pipes_water = lca_data_pipe_pb * length_pipes_water * weight + \
                               lca_data_pipe_insulation * length_pipes_water * area_insulation

        return lca_data_pipes_water + lca_data_pipes_heating

    # auch service life integrieren bei folgenden Formeln (aus ÖKOBAUDAT)
    def _lca_data_heat_generator(self):

        if self.heat_system == "gas":
            if self._heat_generation == "circulating water heater":
                lca_data_circulating_water_heater = self._load_lca_data_template("8acef115-85c0-45f8-9999-9d3b87692fa7")
                lca_data_heat_generator = math.ceil(self.parent.simulated_heat_load / 1000 / 20) * \
                                          lca_data_circulating_water_heater  # 20 kW [pcs]
            elif self._heat_generation == "low temperature":
                sizes = [400, 120, 20]
                count = {}
                lca_data_low_temp_400 = self._load_lca_data_template("cf9764d1-3aba-4e5e-8795-a8f1ee93d9e5")
                lca_data_low_temp_120 = self._load_lca_data_template("38053775-45d9-4649-8299-ec8a5a60cbd9")
                lca_data_low_temp_20 = self._load_lca_data_template("e1ccc83d-01d7-407a-ab59-8c3e1265e8cf")
                volume = self.parent.simulated_heat_load / 1000
                for size in sorted(sizes, reverse=True):
                    count = volume // size
                    if count > 0:
                        count[size] = count
                        volume %= size
                lca_data_heat_generator = count[400] * lca_data_low_temp_400 + count[120] * lca_data_low_temp_120 + \
                           count[20] * lca_data_low_temp_20
            else:
                sizes = [400, 120, 20]
                count = {}
                lca_data_condensing_400 = self._load_lca_data_template("36d1bbf3-1e67-4a93-92f5-0321cc30018a")
                lca_data_condensing_120 = self._load_lca_data_template("0fa37281-b976-458b-880e-46268ca7a294")
                lca_data_condensing_20 = self._load_lca_data_template("12bd4f95-1ff1-4b63-8654-e2dca3fd38fe")
                volume = self.parent.simulated_heat_load / 1000
                for size in sorted(sizes, reverse=True):
                    count = volume // size
                    if count > 0:
                        count[size] = count
                        volume %= size
                lca_data_heat_generator = count[400] * lca_data_condensing_400 + \
                                          count[120] * lca_data_condensing_120 + count[20] * lca_data_condensing_20

            lca_data_tank_6400 = self._load_lca_data_template("4411ce80-6a9a-4088-94bb-426805d99bfc")
            lca_data_tank_4850 = self._load_lca_data_template("8595cc43-c24f-4002-8d2b-c9386de7fae4")
            lca_data_tank_2700 = self._load_lca_data_template("6e520eb3-0b5e-4c7a-b702-244f93faff73")

            if self.parent.net_leased_area <= 180:
                if self.parent.year_of_construction >= 2016 or self._year_of_retrofit >= 2016:
                    lca_data_heat_generator += lca_data_tank_2700
                else:
                    if self.parent.net_leased_area <= 130:
                        lca_data_heat_generator += lca_data_tank_2700
                    else:
                        lca_data_heat_generator += lca_data_tank_4850

            else:
                if self.parent.net_leased_area >= 210:
                   lca_data_heat_generator += lca_data_tank_6400
                else:
                    lca_data_heat_generator += lca_data_tank_4850

        elif self._heat_system == "oil":
            if self._heat_generation == "condensing":
                sizes = [400, 120, 20]
                count = {}
                lca_data_condensing_400 = self._load_lca_data_template("e88588a0-0974-4214-86bd-dcbf5caf656a")
                lca_data_condensing_120 = self._load_lca_data_template("ca68d35e-ebe2-402f-8efe-d29c26dada04")
                lca_data_condensing_20 = self._load_lca_data_template("0c44c3ec-2984-4985-995c-90a4881505a0")
                volume = self.parent.simulated_heat_load / 1000
                for size in sorted(sizes, reverse=True):
                    count = volume // size
                    if count > 0:
                        count[size] = count
                        volume %= size
                lca_data_heat_generator = count[400] * lca_data_condensing_400 + \
                                          count[120] * lca_data_condensing_120 + count[20] * lca_data_condensing_20
            else:
                sizes = [400, 120, 20]
                count = {}
                lca_data_low_temp_400 = self._load_lca_data_template("4e5198e4-4eea-4550-8853-b76a6d6f9f05")
                lca_data_low_temp_120 = self._load_lca_data_template("e69bcb28-f58b-443b-b62f-810bbdf6cedb")
                lca_data_low_temp_20 = self._load_lca_data_template("2aa9cc62-46ee-447f-85e8-50d03e0574f4")
                volume = self.parent.simulated_heat_load / 1000
                for size in sorted(sizes, reverse=True):
                    count = volume // size
                    if count > 0:
                        count[size] = count
                        volume %= size
                lca_data_heat_generator = count[400] * lca_data_low_temp_400 + \
                                          count[120] * lca_data_low_temp_120 + count[20] * lca_data_low_temp_20

            lca_data_tank_1500 = self._load_lca_data_template("cf25e2c1-848a-44f4-92b7-4b77f7e3b4ec")
            if self.parent.year_of_construction >= 2016 or self._year_of_retrofit >= 2016:
                lca_data_heat_generator += math.ceil(self.parent.net_leased_area / 100) * lca_data_tank_1500
            else:
                lca_data_heat_generator += math.ceil(self.parent.net_leased_area / 100) * lca_data_tank_1500 * 2

        elif self._heat_system == "electricity":

            if self._heat_generation == "night storage":
                lca_data_night_storage = self._load_lca_data_template("4ce46be9-2f9c-4686-aa21-7ebf34783674")
                lca_data_heat_generator = math.ceil(self.parent.simulated_heat_load / 1000 / 21) * lca_data_night_storage

            elif self._heat_generation == "heatpump air":
                sizes = [14, 10, 7]
                count = {}
                lca_data_heatpump_air_14 = self._load_lca_data_template("4a08f220-1c52-453c-bf8f-f209586e96c8")
                lca_data_heatpump_air_10 = self._load_lca_data_template("7c0455a7-fc89-4c3c-8225-d528e4375662")
                lca_data_heatpump_air_7 = self._load_lca_data_template("efa279e8-0ac1-4883-b87c-0cb11e17d265")
                volume = self.parent.simulated_heat_load / 1000
                for size in sorted(sizes, reverse=True):
                    count = volume // size
                    if count > 0:
                        count[size] = count
                        volume %= size
                lca_data_heat_generator = count[14] * lca_data_heatpump_air_14 + \
                                          count[10] * lca_data_heatpump_air_10 + count[7] * lca_data_heatpump_air_7
            else:
                sizes = [70, 20, 10]
                count = {}
                lca_data_heatpump_ground_70 = self._load_lca_data_template("062fc223-898a-42bd-a133-8e0fe95cb7a5")
                lca_data_heatpump_ground_20 = self._load_lca_data_template("063cabc8-b90e-4629-b514-a39dc10f0552")
                lca_data_heatpump_ground_10 = self._load_lca_data_template("3bf7183e-741e-4fb7-a32e-574e76e3e747")

                lca_data_ground_collectors_70 = self._load_lca_data_template("b12f748d-5aa2-4cf6-a0b7-46ce0465ee02")
                lca_data_ground_collectors_20 = self._load_lca_data_template("3d3873a9-16dd-4771-82be-f7b79bbd3f53")
                lca_data_ground_collectors_10 = self._load_lca_data_template("1a27c109-1e99-45e7-b198-7c79f926b996")
                volume = self.parent.simulated_heat_load / 1000
                for size in sorted(sizes, reverse=True):
                    count = volume // size
                    if count > 0:
                        count[size] = count
                        volume %= size
                lca_data_heat_generator = count[70] * lca_data_heatpump_ground_70 + \
                                          count[20] * lca_data_heatpump_ground_20 + \
                                          count[10] * lca_data_heatpump_ground_10 + \
                                          count[70] * lca_data_ground_collectors_70 + \
                                          count[20] * lca_data_ground_collectors_20 + \
                                          count[10] * lca_data_ground_collectors_10
        elif self._heat_system == "biomass":
            sizes = [120, 20]
            count = {}
            lca_data_pellets_120 = self._load_lca_data_template("49660117-13cd-4475-a66b-a13801723a37")
            lca_data_pellets_20 = self._load_lca_data_template("0e03a1c1-0aa9-4e94-bbc5-653d967b0d8d")
            volume = self.parent.simulated_heat_load / 1000
            for size in sorted(sizes, reverse=True):
                count = volume // size
                if count > 0:
                    count[size] = count
                    volume %= size
            lca_data_heat_generator = count[120] * lca_data_pellets_120 + count[20] * lca_data_pellets_20
        else:
            lca_data_district = self._load_lca_data_template("dcd5e23a-9bec-40b6-b07c-1642fe696a2e")
            lca_data_heat_generator = lca_data_district

        return lca_data_heat_generator

    def _lca_data_storage(self):

        if self._storage:
            lca_data_storage = self._load_lca_data_template("d3f58b23-9526-43be-8a32-fb583dfebfaa")
        else:
            lca_data_storage = 0

        return lca_data_storage

        # todo was mit Wasser und Solar Speicher?

    def _lca_data_pump(self):

        if self._pipe_routing_heating == "centralised":

            if self._design_temp_flow == 70:
                temp_diff = 15
            elif self._design_temp_flow == 55:
                temp_diff = 10
            else:
                temp_diff = 7

            flow_rate = self.parent.simulated_heat_load / (1 * 1.163 * temp_diff)

            lca_data_pump_1000 = self._load_lca_data_template("9fe2649f-bd76-41d8-b952-0021143f1ef7")
            lca_data_pump_250 = self._load_lca_data_template("b4e4d89b-e4d0-4df3-a233-deacc76b2fee")
            lca_data_pump_50 = self._load_lca_data_template("301c6f09-ce88-4818-96c3-e420fe799d62")

            if flow_rate > (240 * 0.06):  # https://www.viva-aqua.de/250-watt-umwaelzpumpe
                lca_data_pump = lca_data_pump_1000
            elif flow_rate < 2.3:  # https://www.ando-technik.com/ebara-heizungspumpe-ego-25-60-180-230v-50w
                lca_data_pump = lca_data_pump_50
            else:
                lca_data_pump = lca_data_pump_250

        else:
            lca_data_pump = 0

        return lca_data_pump

    def _lca_data_solar(self):

        if self._storage == "solar":
            lca_data_solar_collector = self.parent.net_leased_area / 100 * 3.05 * \
                                 self._load_lca_data_template("60e0575b-6cb4-4ba4-a9f0-78d8fb65c9a9")
        else:
            lca_data_solar_collector = 0

        return lca_data_solar_collector

    def _lca_data_heat_transfer(self):

        if "heatpump" in self._heat_generation:
            lca_data_heat_transfer = self.parent.net_leased_area * \
                                self._load_lca_data_template("ed997c1e-274c-4d38-a5bf-2016693c91a3")
        else:
            lca_data_radiator = self._load_lca_data_template("c6de5beb-ffe9-4b5f-aba8-c0c2d3528c58")
            # radiator Type 22 0,5 m * 1 m [kg]
            if self._design_temp_flow == 55:
                lca_data_heat_transfer = self.parent.simulated_heat_load / 735 * 31.3 * lca_data_radiator
            else:
                lca_data_heat_transfer = self.parent.simulated_heat_load / 1169 * 31.3 * lca_data_radiator
            # 35 °C only for heatpump

        return lca_data_heat_transfer

    def _lca_data_fe(self, fe_heating, fe_water):
        """Calculates the total annual energy demand of the heat_supply_system

                Parameters
                ----------
                fe_heating : FEDemandHeating()
                    FEDemandHeating() instance of TEASER
                fe_water : FEDemandWater()
                    FEDemandWater() instance of TEASER
                """

        ass_error_1 = "fe_heating has to be an instance of FEDemandHeating()"
        ass_error_2 = "fe_water has to be an instance of FEDemandWater()"

        assert type(fe_heating).__name__ == "FEDemandHeating", ass_error_1
        assert type(fe_water).__name__ == "FEDemandWater", ass_error_2

        fe_demand = fe_heating.calc_final_energy_demand_heating() + fe_water.calc_final_energy_demand_water()

        if self._heat_system == "gas":

            if "low temperature" in self._heat_generation:
                lca_data_fe = fe_demand * lca_niedertemp_enev

            else:
                lca_data_fe = fe_demand * lca_brennwert_enev

        elif self._heat_system == "oil":

            if "low temperature" in self._heat_generation:
                lca_data_fe = fe_demand * lca_niedertemp_enev

            else:
                lca_data_fe = fe_demand * lca_brennwert_enev

        elif self._heat_system == "biomass":

            lca_data_fe = fe_demand * lca_pellets

        elif self._heat_generation == "night storage":

            lca_data_fe = fe_demand * lca_elektrodurchlauf

        elif "heatpump air" in self._heat_generation:

            # todo change to correct values
            sizes = [14, 10, 7]
            count = {}
            lca_data_heatpump_air_14 = self._load_lca_data_template("4a08f220-1c52-453c-bf8f-f209586e96c8")
            lca_data_heatpump_air_10 = self._load_lca_data_template("7c0455a7-fc89-4c3c-8225-d528e4375662")
            lca_data_heatpump_air_7 = self._load_lca_data_template("efa279e8-0ac1-4883-b87c-0cb11e17d265")
            volume = self.parent.simulated_heat_load / 1000
            for size in sorted(sizes, reverse=True):
                count = volume // size
                if count > 0:
                    count[size] = count
                    volume %= size
            lca_data_fe = (count[14] * lca_data_heatpump_air_14 + \
                                      count[10] * lca_data_heatpump_air_10 + count[7] * lca_data_heatpump_air_7) \
                                      * fe_demand

        elif "heatpump ground" in self._heat_generation:

            # todo change to correct values
            sizes = [10, 20, 70]
            count = {}
            lca_data_heatpump_ground_70 = self._load_lca_data_template("4a08f220-1c52-453c-bf8f-f209586e96c8")
            lca_data_heatpump_ground_20 = self._load_lca_data_template("7c0455a7-fc89-4c3c-8225-d528e4375662")
            lca_data_heatpump_ground_10 = self._load_lca_data_template("efa279e8-0ac1-4883-b87c-0cb11e17d265")
            volume = self.parent.simulated_heat_load / 1000
            for size in sorted(sizes, reverse=True):
                count = volume // size
                if count > 0:
                    count[size] = count
                    volume %= size
            lca_data_fe = (count[70] * lca_data_heatpump_ground_70 + \
                           count[20] * lca_data_heatpump_ground_20 + count[10] * lca_data_heatpump_ground_10) \
                          * fe_demand

        elif self._heat_generation == "biomass":

            lca_data_fe = fe_demand * lca_Fern_biomass

        elif self._heat_generation == "gas - high chp":

            lca_data_fe = fe_demand * lca_Fern_gas_KWK

        else:

            lca_data_fe = fe_demand * lca_Fern_gas_keinKWK


        return lca_data_fe

    @property
    def lca_data(self):
        return self._lca_data

    @lca_data.setter
    def lca_data(self, value):
        self._lca_data = value
