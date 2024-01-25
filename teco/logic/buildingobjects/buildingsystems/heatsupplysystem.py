# created December 2023
# by Clara Schmitz (master thesis)

"""This module includes a class for the Heat Supply System
"""
import math

from teaser.teaser.logic.buildingobjects.buildingsystems.heatsupplysystem import HeatSupplySystem
from teco.logic.buildingobjects.buildingphysics.en15804lcadata import En15804LcaData
from teaser.teaser.logic.buildingobjects.buildingsystems.fedemandwater import FEDemandWater
from teaser.teaser.logic.buildingobjects.buildingsystems.fedemandheating import FEDemandHeating

# todo in der Klammer hinter den LCA-IDs steht nicht die Nutzungsdauer sondern jeweils in der ÖKOBAUDAT-Einheit wie viel hiervon genutzt wird
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

        self._lca_data = None
        self._period_lca_scenario = None
        self._use_b4 = None

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
                self._use_b4 = self.parent.parent.use_b4
            except:
                self._use_b4 = False

        if period_lca_scenario is None:
            try:
                self._period_lca_scenario = self.parent.parent.period_lca_scenario
            except:
                print("Please enter a period for the LCA-scenario!")
        else:
            self._period_lca_scenario = period_lca_scenario

        self._lca_data_pipes()
        self._lca_data_heat_generator()
        self._lca_data_storage()
        self._lca_data_pump()
        self._lca_data_solar()
        self._lca_data_heat_transfer()
        self._lca_data_fe()

        # print(self._lca_data.lca_data.gwp.b6)

        print("A1_A3: {} {}".format(self._lca_data.gwp.a1_a3, self._lca_data.gwp.unit))
        print("A4: {} {}".format(self._lca_data.gwp.a4, self._lca_data.gwp.unit))
        print("A5: {} {}".format(self._lca_data.gwp.a5, self._lca_data.gwp.unit))
        print("B1: {} {}".format(self._lca_data.gwp.b1, self._lca_data.gwp.unit))
        print("B6: {} {}".format(self._lca_data.gwp.b6, self._lca_data.gwp.unit))
        print("C1: {} {}".format(self._lca_data.gwp.c1, self._lca_data.gwp.unit))
        print("C2: {} {}".format(self._lca_data.gwp.c2, self._lca_data.gwp.unit))
        print("C3: {} {}".format(self._lca_data.gwp.c3, self._lca_data.gwp.unit))
        print("C4: {} {}".format(self._lca_data.gwp.c4, self._lca_data.gwp.unit))
        print("D: {} {}".format(self._lca_data.gwp.d, self._lca_data.gwp.unit))

    def _lca_data_pipes(self):
        """Helper function for matrix calculation.

        Gathers all material properties of the building element and returns
        them as a np.array. Needed for the calculation of the matrix in
        equivalent_res(t_bt) especially for walls.

        Returns
        ----------

        """

        length_horizontal_heating = 0
        length_strand_heating = 0
        length_tethers_heating = 0
        length_horizontal_water = 0
        length_strand_water = 0
        length_stubs_water = 0

        # heating
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

        amount_steel_pipes = length_pipes_26 * 1.63 + length_pipes_20 * 1.26
        amount_pipe_insulation = length_pipes_26 * area_insulation_26 + length_pipes_20 * area_insulation_20

        if amount_steel_pipes:
            self._get_lca_data("8622539c-592c-45b0-9a4b-e5f8b4fea367", "kg", amount_steel_pipes, 25)

        print("pipes:")
        print("A1_A3: {} {}".format(self._lca_data.gwp.a1_a3, self._lca_data.gwp.unit))
        print("A4: {} {}".format(self._lca_data.gwp.a4, self._lca_data.gwp.unit))
        print("A5: {} {}".format(self._lca_data.gwp.a5, self._lca_data.gwp.unit))
        print("B1: {} {}".format(self._lca_data.gwp.b1, self._lca_data.gwp.unit))
        print("B6: {} {}".format(self._lca_data.gwp.b6, self._lca_data.gwp.unit))
        print("C1: {} {}".format(self._lca_data.gwp.c1, self._lca_data.gwp.unit))
        print("C2: {} {}".format(self._lca_data.gwp.c2, self._lca_data.gwp.unit))
        print("C3: {} {}".format(self._lca_data.gwp.c3, self._lca_data.gwp.unit))
        print("C4: {} {}".format(self._lca_data.gwp.c4, self._lca_data.gwp.unit))
        print("D: {} {}".format(self._lca_data.gwp.d, self._lca_data.gwp.unit))

        if amount_pipe_insulation:
            self._get_lca_data("75ce5bab-4506-4f7e-8c20-a638a98b7537", "m^3", amount_pipe_insulation, 25)

        print("pipes_insulation:")
        print("A1_A3: {} {}".format(self._lca_data.gwp.a1_a3, self._lca_data.gwp.unit))
        print("A4: {} {}".format(self._lca_data.gwp.a4, self._lca_data.gwp.unit))
        print("A5: {} {}".format(self._lca_data.gwp.a5, self._lca_data.gwp.unit))
        print("B1: {} {}".format(self._lca_data.gwp.b1, self._lca_data.gwp.unit))
        print("B6: {} {}".format(self._lca_data.gwp.b6, self._lca_data.gwp.unit))
        print("C1: {} {}".format(self._lca_data.gwp.c1, self._lca_data.gwp.unit))
        print("C2: {} {}".format(self._lca_data.gwp.c2, self._lca_data.gwp.unit))
        print("C3: {} {}".format(self._lca_data.gwp.c3, self._lca_data.gwp.unit))
        print("C4: {} {}".format(self._lca_data.gwp.c4, self._lca_data.gwp.unit))
        print("D: {} {}".format(self._lca_data.gwp.d, self._lca_data.gwp.unit))

        # water
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

        amount_pb_pipes = length_pipes_water * weight
        amount_pb_pipes_insulation = length_pipes_water * area_insulation

        if amount_pb_pipes:
            self._get_lca_data("83a21998-b507-429e-bbe3-b5629e601138", "kg", amount_pb_pipes, 25)

        print("pb_pipes:")
        print("A1_A3: {} {}".format(self._lca_data.gwp.a1_a3, self._lca_data.gwp.unit))
        print("A4: {} {}".format(self._lca_data.gwp.a4, self._lca_data.gwp.unit))
        print("A5: {} {}".format(self._lca_data.gwp.a5, self._lca_data.gwp.unit))
        print("B1: {} {}".format(self._lca_data.gwp.b1, self._lca_data.gwp.unit))
        print("B6: {} {}".format(self._lca_data.gwp.b6, self._lca_data.gwp.unit))
        print("C1: {} {}".format(self._lca_data.gwp.c1, self._lca_data.gwp.unit))
        print("C2: {} {}".format(self._lca_data.gwp.c2, self._lca_data.gwp.unit))
        print("C3: {} {}".format(self._lca_data.gwp.c3, self._lca_data.gwp.unit))
        print("C4: {} {}".format(self._lca_data.gwp.c4, self._lca_data.gwp.unit))
        print("D: {} {}".format(self._lca_data.gwp.d, self._lca_data.gwp.unit))

        if amount_pb_pipes_insulation:
            self._get_lca_data("75ce5bab-4506-4f7e-8c20-a638a98b7537", "m^3", amount_pb_pipes_insulation, 25)

        print("pb_pipes_insulation:")
        print("A1_A3: {} {}".format(self._lca_data.gwp.a1_a3, self._lca_data.gwp.unit))
        print("A4: {} {}".format(self._lca_data.gwp.a4, self._lca_data.gwp.unit))
        print("A5: {} {}".format(self._lca_data.gwp.a5, self._lca_data.gwp.unit))
        print("B1: {} {}".format(self._lca_data.gwp.b1, self._lca_data.gwp.unit))
        print("B6: {} {}".format(self._lca_data.gwp.b6, self._lca_data.gwp.unit))
        print("C1: {} {}".format(self._lca_data.gwp.c1, self._lca_data.gwp.unit))
        print("C2: {} {}".format(self._lca_data.gwp.c2, self._lca_data.gwp.unit))
        print("C3: {} {}".format(self._lca_data.gwp.c3, self._lca_data.gwp.unit))
        print("C4: {} {}".format(self._lca_data.gwp.c4, self._lca_data.gwp.unit))
        print("D: {} {}".format(self._lca_data.gwp.d, self._lca_data.gwp.unit))

    def _lca_data_heat_generator(self):

        if self.heat_system == "gas":
            if self._heat_generation == "circulating water heater":

                amount_heat_generator = math.ceil(self._heat_load / 1000 / 20)  # 20 kW / pcs

                if amount_heat_generator:
                    self._get_lca_data("8acef115-85c0-45f8-9999-9d3b87692fa7", "pcs", amount_heat_generator, 18)

            elif self._heat_generation == "low temperature":

                n_400 = 0
                n_120 = 0
                n_20 = 0

                sizes = [400, 120, 20]
                count = {}

                for size in sizes:
                    devices_count = self._heat_load // size
                    if devices_count > 0:
                        if size == 20:
                            n_20 += int(devices_count)
                        else:
                            count[size] = int(devices_count)

                if count:
                    n_400 = count.get(400, 0)
                    n_120 = count.get(120, 0)

                if self._heat_load < 20 or not count:
                    n_20 = 1

                print("n_400:", n_400)
                print("n_120:", n_120)
                print("n_20:", n_20)

                if n_400:
                    self._get_lca_data("cf9764d1-3aba-4e5e-8795-a8f1ee93d9e5", "pcs", n_400, 20)

                if n_120:
                    self._get_lca_data("38053775-45d9-4649-8299-ec8a5a60cbd9", "pcs", n_120, 20)

                if n_20:
                    self._get_lca_data("e1ccc83d-01d7-407a-ab59-8c3e1265e8cf", "pcs", n_20, 20)

            else:
                n_400 = 0
                n_120 = 0
                n_20 = 0

                sizes = [400, 120, 20]
                count = {}

                for size in sizes:
                    devices_count = self._heat_load // size
                    if devices_count > 0:
                        if size == 20:
                            n_20 += int(devices_count)
                        else:
                            count[size] = int(devices_count)

                if count:
                    n_400 = count.get(400, 0)
                    n_120 = count.get(120, 0)

                if self._heat_load < 20 or not count:
                    n_20 = 1

                print("n_400:", n_400)
                print("n_120:", n_120)
                print("n_20:", n_20)

                if n_400:
                    self._get_lca_data("36d1bbf3-1e67-4a93-92f5-0321cc30018a", "pcs", n_400, 20)

                if n_120:
                    self._get_lca_data("0fa37281-b976-458b-880e-46268ca7a294", "pcs", n_120, 20)

                if n_20:
                    self._get_lca_data("12bd4f95-1ff1-4b63-8654-e2dca3fd38fe", "pcs", n_20, 20)

            if self.parent.net_leased_area <= 180:
                if self.parent.year_of_construction >= 2016 or self._year_of_retrofit >= 2016:
                    self._get_lca_data("6e520eb3-0b5e-4c7a-b702-244f93faff73", "pcs", 1, 18)
                else:
                    if self.parent.net_leased_area <= 130:
                        self._get_lca_data("6e520eb3-0b5e-4c7a-b702-244f93faff73", "pcs", 1, 18)
                    else:
                        self._get_lca_data("8595cc43-c24f-4002-8d2b-c9386de7fae4", "pcs", 1, 18)

            else:
                if self.parent.net_leased_area >= 210:
                    self._get_lca_data("4411ce80-6a9a-4088-94bb-426805d99bfc", "pcs", 1, 18)
                else:
                    self._get_lca_data("8595cc43-c24f-4002-8d2b-c9386de7fae4", "pcs", 1, 18)

        elif self._heat_system == "oil":
            if self._heat_generation == "condensing":
                n_400 = 0
                n_120 = 0
                n_20 = 0

                sizes = [400, 120, 20]
                count = {}

                for size in sizes:
                    devices_count = self._heat_load // size
                    if devices_count > 0:
                        if size == 20:
                            n_20 += int(devices_count)
                        else:
                            count[size] = int(devices_count)

                if count:
                    n_400 = count.get(400, 0)
                    n_120 = count.get(120, 0)

                if self._heat_load < 20 or not count:
                    n_20 = 1

                print("n_400:", n_400)
                print("n_120:", n_120)
                print("n_20:", n_20)

                if n_400:
                    self._get_lca_data("e88588a0-0974-4214-86bd-dcbf5caf656a", "pcs", n_400, 20)

                if n_120:
                    self._get_lca_data("ca68d35e-ebe2-402f-8efe-d29c26dada04", "pcs", n_120, 20)

                if n_20:
                    self._get_lca_data("0c44c3ec-2984-4985-995c-90a4881505a0", "pcs", n_20, 20)
            else:
                n_400 = 0
                n_120 = 0
                n_20 = 0

                sizes = [400, 120, 20]
                count = {}

                for size in sizes:
                    devices_count = self._heat_load // size
                    if devices_count > 0:
                        if size == 20:
                            n_20 += int(devices_count)
                        else:
                            count[size] = int(devices_count)

                if count:
                    n_400 = count.get(400, 0)
                    n_120 = count.get(120, 0)

                if self._heat_load < 20 or not count:
                    n_20 = 1

                print("n_400:", n_400)
                print("n_120:", n_120)
                print("n_20:", n_20)

                if n_400:
                    self._get_lca_data("4e5198e4-4eea-4550-8853-b76a6d6f9f05", "pcs", n_400, 20)

                if n_120:
                    self._get_lca_data("e69bcb28-f58b-443b-b62f-810bbdf6cedb", "pcs", n_120, 20)

                if n_20:
                    self._get_lca_data("2aa9cc62-46ee-447f-85e8-50d03e0574f4", "pcs", n_20, 20)

            if self.parent.year_of_construction >= 2016 or self._year_of_retrofit >= 2016:
                amount_tank_1500 = math.ceil(self.parent.net_leased_area / 100)

            else:
                amount_tank_1500 = math.ceil(self.parent.net_leased_area / 100) * 2

            self._get_lca_data("45d181ba-c3c0-4ecb-bd94-7ad3aa7cef83", "pcs", amount_tank_1500, 30)

        elif self._heat_system == "electricity":

            if self._heat_generation == "night storage":
                amount_night_storage = math.ceil(self._heat_load / 1000 / 21)
                self._get_lca_data("4ce46be9-2f9c-4686-aa21-7ebf34783674", "pcs", amount_night_storage, 15)

            elif self._heat_generation == "heatpump air":
                n_14 = 0
                n_10 = 0
                n_7 = 0

                sizes = [14, 10, 7]
                count = {}

                for size in sizes:
                    devices_count = self._heat_load // size
                    if devices_count > 0:
                        if size == 7:
                            n_7 += int(devices_count)
                        else:
                            count[size] = int(devices_count)

                if count:
                    n_14 = count.get(14, 0)
                    n_10 = count.get(10, 0)

                if self._heat_load < 7 or not count:
                    n_7 = 1

                print("n_14:", n_14)
                print("n_10:", n_10)
                print("n_7:", n_7)

                if n_14:
                    self._get_lca_data("4a08f220-1c52-453c-bf8f-f209586e96c8", "pcs", n_14, 20)

                if n_10:
                    self._get_lca_data("7c0455a7-fc89-4c3c-8225-d528e4375662", "pcs", n_10, 20)

                if n_7:
                    self._get_lca_data("efa279e8-0ac1-4883-b87c-0cb11e17d265", "pcs", n_7, 20)

            else:
                n_70 = 0
                n_20 = 0
                n_10 = 0

                sizes = [70, 20, 10]
                count = {}

                for size in sizes:
                    devices_count = self._heat_load // size
                    if devices_count > 0:
                        if size == 10:
                            n_10 += int(devices_count)
                        else:
                            count[size] = int(devices_count)

                if count:
                    n_70 = count.get(70, 0)
                    n_20 = count.get(20, 0)

                if self._heat_load < 10 or not count:
                    n_10 = 1

                print("n_70:", n_70)
                print("n_20:", n_20)
                print("n_10:", n_10)

                if n_70:
                    self._get_lca_data("062fc223-898a-42bd-a133-8e0fe95cb7a5", "pcs", n_70, 20)
                    self._get_lca_data("b12f748d-5aa2-4cf6-a0b7-46ce0465ee02", "pcs", n_70, 20)

                if n_20:
                    self._get_lca_data("063cabc8-b90e-4629-b514-a39dc10f0552", "pcs", n_20, 20)
                    self._get_lca_data("3d3873a9-16dd-4771-82be-f7b79bbd3f53", "pcs", n_20, 20)

                if n_10:
                    self._get_lca_data("3bf7183e-741e-4fb7-a32e-574e76e3e747", "pcs", n_10, 20)
                    self._get_lca_data("1a27c109-1e99-45e7-b198-7c79f926b996", "pcs", n_10, 20)

        elif self._heat_system == "biomass":
            n_120 = 0
            n_20 = 0

            sizes = [120, 20]
            count = {}

            for size in sizes:
                devices_count = self._heat_load // size
                if devices_count > 0:
                    if size == 20:
                        n_20 += int(devices_count)
                    else:
                        count[size] = int(devices_count)

            if count:
                n_120 = count.get(120, 0)

            if self._heat_load < 20 or not count:
                n_20 = 1

            print("n_120:", n_120)
            print("n_20:", n_20)

            if n_120:
                self._get_lca_data("49660117-13cd-4475-a66b-a13801723a37", "pcs", n_120, 20)

            if n_20:
                self._get_lca_data("0e03a1c1-0aa9-4e94-bbc5-653d967b0d8d", "pcs", n_20, 20)

        else:
            self._get_lca_data("dcd5e23a-9bec-40b6-b07c-1642fe696a2e", "pcs", 1, 30)

    def _lca_data_storage(self):

        if self._storage:
            self._get_lca_data("d3f58b23-9526-43be-8a32-fb583dfebfaa", "pcs", 1, 20)
        else:
            pass

    def _lca_data_pump(self):

        if "centralised" in self._pipe_routing_heating:

            if self._design_temp_flow == 70:
                temp_diff = 15
            elif self._design_temp_flow == 55:
                temp_diff = 10
            else:
                temp_diff = 7

            flow_rate = self._heat_load / (1 * 1.163 * temp_diff)

            if flow_rate > (240 * 0.06):
                self._get_lca_data("9fe2649f-bd76-41d8-b952-0021143f1ef7", "pcs", 1, 10)
            elif flow_rate < 2.3:
                self._get_lca_data("301c6f09-ce88-4818-96c3-e420fe799d62", "pcs", 1, 10)
            else:
                self._get_lca_data("b4e4d89b-e4d0-4df3-a233-deacc76b2fee", "pcs", 1, 10)

        else:
            pass

    def _lca_data_solar(self):

        if self._storage == "solar":
            amount_solar_collector = self.parent.net_leased_area / 100 * 3.05
            self._get_lca_data("60e0575b-6cb4-4ba4-a9f0-78d8fb65c9a9", "m^2", amount_solar_collector, 20)
        else:
            pass

    def _lca_data_heat_transfer(self):

        if "heatpump" in self._heat_generation:
            amount_heat_transfer = self.parent.net_leased_area
            self._get_lca_data("ed997c1e-274c-4d38-a5bf-2016693c91a3", "m^2", amount_heat_transfer, 30)
        else:

            # radiator Type 22 0,5 m * 1 m [kg]
            if self._design_temp_flow == 55:
                amount_heat_transfer = self._heat_load / 735 * 31.3
            else:
                amount_heat_transfer = self._heat_load / 1169 * 31.3
            # 35 °C only for heatpump
            self._get_lca_data("c6de5beb-ffe9-4b5f-aba8-c0c2d3528c58", "kg", amount_heat_transfer, 30)

    def _lca_data_fe(self):
        """Calculates the total annual energy demand of the heat_supply_system

                Parameters
                ----------
                """
        fedheating = FEDemandHeating(parent=self)
        fedwater = FEDemandWater(parent=self)

        fe_demand = fedheating.calc_final_energy_demand_heating() + fedwater.calc_final_energy_demand_water()

        if self._heat_system == "gas":

            if "low temperature" in self._heat_generation:
                self._get_lca_data("e58a3c28-4818-43e3-9e72-f08267926613", "MJ", fe_demand)

            else:
                self._get_lca_data("6167bec3-0bc2-425a-9c87-479fa310f8f2", "MJ", fe_demand)

        elif self._heat_system == "oil":
            self._get_lca_data("63854c13-11d1-4f97-ad97-052ecd3e6e3d", "MJ", fe_demand)

        elif self._heat_system == "biomass":
            self._get_lca_data("fb11f8ce-d3c7-4823-ba13-0c1f4a304799", "MJ", fe_demand)

        elif self._heat_generation == "night storage":
            self._get_lca_data("149d05eb-7e8c-4755-9efa-347510b3ae4e", "MJ", fe_demand)

        elif "heatpump air" in self._heat_generation:

            n_14 = 0
            n_10 = 0
            n_7 = 0

            sizes = [14, 10, 7]
            count = {}

            for size in sizes:
                devices_count = self._heat_load // size
                if devices_count > 0:
                    if size == 7:
                        n_7 += int(devices_count)
                    else:
                        count[size] = int(devices_count)

            if count:
                n_14 = count.get(14, 0)
                n_10 = count.get(10, 0)

            if self._heat_load < 7 or not count:
                n_7 = 1

            print("n_14:", n_14)
            print("n_10:", n_10)
            print("n_7:", n_7)

            if n_14:
                self._get_lca_data("5b00afcd-8b26-4945-857f-e280946e823f", "MJ", fe_demand)

            if n_10:
                self._get_lca_data("05a620f5-e5ba-4593-a55c-690e2a47c8db", "MJ", fe_demand)

            if n_7:
                self._get_lca_data("4607b899-9c83-4764-a621-8e79c94887ec", "MJ", fe_demand)

        elif "heatpump ground" in self._heat_generation:
            self._get_lca_data("3fd6d7dc-6618-42f4-b6be-f5b6f9a38763", "MJ", fe_demand)

        else:

            if self._heat_load < 120:
                self._get_lca_data("3c3a8f6b-ec6f-4358-8e7d-f42f05f59c10", "MJ", fe_demand)

            else:
                self._get_lca_data("9b123a02-9967-4a5c-8630-eb78aa4f6c45", "MJ", fe_demand)

    def _get_lca_data(self, lca_id, unit, amount, service_life=None, data_class=None):
        """"LCA-data loader.

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
        lca_data = En15804LcaData()
        lca_data.ref_flow_unit = unit

        if data_class is None:
            data_class = self.parent.parent.data
        else:
            data_class = data_class

        lca_data.load_lca_data_template(lca_id, data_class)

        if lca_data.ref_flow_unit != unit:
            try:
                lca_data = lca_data.convert_ref_unit(unit)
            except:
                print("Unit of the reference flow has to be " + unit + "!")

        if service_life:
            n_repl = math.ceil(self._period_lca_scenario / service_life)

            if self._use_b4:

                lca_data = lca_data * (n_repl + 1) * amount
                lca_data = lca_data.sum_to_b4()

            else:

                lca_data = lca_data * n_repl * amount

        else:
            lca_data = lca_data * self._period_lca_scenario * amount

        if self._lca_data:
            self._lca_data += lca_data
        else:
            self._lca_data = lca_data

        """value = self._period_lca_scenario

        if self.year_of_retrofit > 1 and not None:
            year_of_retrofit = self.year_of_retrofit
        else:
            year_of_retrofit = self.parent.year_of_construction

        while value >= 30:
            year_of_retrofit += 30

            self.retrofit_heat_supply_system(year_of_retrofit=year_of_retrofit)

            value -= 30"""

        """aus building_element
        if self.service_life:

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

        self.lca_data = lca_data"""

    @property
    def lca_data(self):
        return self._lca_data

    @lca_data.setter
    def lca_data(self, value):
        self._lca_data = value
