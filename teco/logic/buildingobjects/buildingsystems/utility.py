"""This module contains the Utility Class"""

from teco.logic.buildingobjects.buildingphysics.en15804lcadata import En15804LcaData
import json

class Utility(object):
    """Utility Class



        Parameters
        ----------

        parent: Building()


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

    @property
    def lca_data(self):
        return self._lcadata