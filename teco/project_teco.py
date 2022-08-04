"""This module extents the TEASERplus project module with LCA specific parameters,
which includes the Project class, which is the API for TEASER."""

from teaser import project


class Project(project.Project):

    """
    period_lca_scenario : int [a]
        period which is taken into account for LCA
    use_b4 : bool
        if true environmental indicators of replaced buildingelements are added
        to stage B4. Otherwise they are added seperatly to the other stages

    """

    def __init__(self, load_data):
        """Constructor of Teco Project
        """
        super(Project, self).__init__(load_data)

        self._period_lca_scenario = 50
        self._use_b4 = False

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