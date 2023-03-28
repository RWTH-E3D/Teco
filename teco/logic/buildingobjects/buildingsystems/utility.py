"""This module contains the Utility Class"""

from teco.logic.buildingobjects.buildingphysics.en15804lcadata import En15804LcaData
import json

class Utility(object):
    """Utility Class



        Parameters
        ----------

        parent: Building()
            The parent class of this object, the Building the Utility belongs to.
            Allows for better control of hierarchical structures.
            (default: None)

        Attributes
        ----------
        """

    def __init__(self, parent=None, name=None):
        """Constructor for Utility
        """

        self._parent = parent
        self._lcadata = En15804LcaData()
        self._name = name

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, value):
        from teaser.logic.buildingobjects.building import Building
        import inspect

        if inspect.isclass(Building):
            self._parent = value

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        from teaser.logic.buildingobjects.building import Building
        import inspect

        if inspect.isclass(Building):
            self._name = value

    def load_lca_data_from_json(self):
        return
