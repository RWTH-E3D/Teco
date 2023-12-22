# created December 2023
# by Clara Schmitz (master thesis)

"""This module includes a class for the Heat Supply System
"""
from teaser.teaser.logic.buildingobjects.buildingsystems.heat_supply_system import HeatSupplySystem
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

        if self.parent.pipe_routing_heating == "centralised outside":

            length_horizontal_heating = 4 * self.parent.length_char - 10
            length_strand_heating = self.parent.length_char * self.parent.parent.number_of_floors
            length_tethers_heating = self.parent.length_char * self.parent.parent.number_of_floors * 2 / 3

        elif self.parent.pipe_routing_heating == "centralised inside":

            length_horizontal_heating = 2 * self.parent.length_char - 10
            length_strand_heating = self.parent.length_char * self.parent.parent.number_of_floors / 2
            length_tethers_heating = self.parent.length_char * self.parent.parent.number_of_floors * 4

        elif self.parent.pipe_routing_heating == "decentralised":

            length_strand_heating = self.parent.length_char * self.parent.parent.number_of_floors * 6
            length_tethers_heating = self.parent.length_char * self.parent.parent.number_of_floors

        if self.parent.pipe_routing_water == "centralised with circulation":

            length_horizontal_water = 2 * self.parent.length_char - 10
            length_strand_water = self.parent.length_char * self.parent.parent.number_of_floors / 2
            length_stubs_water = self.parent.length_char * self.parent.parent.number_of_floors / 2

        elif self.parent.pipe_routing_water == "centralised without circulation":

            length_horizontal_water = self.parent.length_char - 5
            length_strand_water = self.parent.length_char * self.parent.parent.number_of_floors / 4
            length_stubs_water = self.parent.length_char * self.parent.parent.number_of_floors / 2

        elif self.parent.pipe_routing_water == "decentralised":

            length_stubs_water = self.parent.length_char * self.parent.parent.number_of_floors / 2

        length_pipes_heating = length_horizontal_heating + length_strand_heating + length_tethers_heating
        length_pipes_water = length_horizontal_water + length_strand_water + length_stubs_water

        # todo unit für Dämmung ist m³


    # auch service life integrieren bei folgenden Formeln (aus ÖKOBAUDAT)
    def _lca_data_heat_generation(self):
        # auch Öl- und Gastank
        lca_data = En15804LcaData()
        lca_data.ref_flow_unit = "pcs"

    def _lca_data_buffer_storage(self):
        # water

    def _lca_data_pump(self):
        #Umwälzpumpe

    def _lca_data_solar(self):
        #Kollektor

    def _lca_data_radiator(self):
        # FB oder Heizkörper

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
