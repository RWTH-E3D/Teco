"""This module extents the TEASERplus project module with LCA specific parameters,
which includes the Project class, which is the API for TEASER."""

from teaser import project
import teco.logic.utilities as utilities
import teco.data.dataclass as dataclass


class Project(project.Project):

    """
    period_lca_scenario : int [a]
        period which is taken into account for LCA
    use_b4 : bool
        if true environmental indicators of replaced buildingelements are added
        to stage B4. Otherwise they are added seperatly to the other stages
    required_stages : list of strings
        List of stages that must be present in the data sets for the LCA. The program issues an error if a data set does
        not contain values for one of the required stages. Stages A1-A3, C3 and C4 are required as default.

    """

    utilities = utilities
    dataclass = dataclass

    def __init__(self, load_data):
        """Constructor of Teco Project
        """
        super(Project, self).__init__(load_data)

        self._period_lca_scenario = 50
        self._use_b4 = False
        self.required_stages = ["a1_a3", "c3", "c4"]

    @property
    def use_b4(self):
        return self._use_b4

    @use_b4.setter
    def use_b4(self, value):
        if isinstance(value, bool):
            self._use_b4 = value
        else:
            try:
                value = bool(value)
                self._use_b4 = value
            except ValueError:
                print("Can´t convert value to boolean")

    @property
    def period_lca_scenario(self):
        return self._period_lca_scenario

    @period_lca_scenario.setter
    def period_lca_scenario(self, value):
        if isinstance(value, int):
            self._period_lca_scenario = value
        else:
            try:
                value = int(value)
                self._period_lca_scenario = value
            except ValueError:
                print("Can´t convert value to integer")