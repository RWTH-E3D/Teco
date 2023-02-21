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

    def __init__(self, parent=None):
        """Constructor for Utility
        """

        self.parent = parent
        self.lcadata = En15804LcaData()

    @property
    def parent(self):
        return self.__parent

    @parent.setter
    def parent(self, value):
        from teaser.logic.buildingobjects.building import Building
        import inspect

        if inspect.isclass(Building):
            self.__parent = value

    def add_utility(self,building_archetype):  # not completely implemented!
        """
        Add utility to the en15804lcadata class of archetype

        Parameters
        ----------
        building_archetype: str

        Returns
        -------

        """
        with open("C:\\Users\\tayeb\\teco\\teco\\data\\input\\inputdata\\utilities.json",'r') as f:

            file= json.load(f)
            print(file)
            self.lcadata.gwp.unit = file[building_archetype]['Utilities']['Unit']

            # store in en15804lcadata class object
            for stage in file[building_archetype]['Utilities']["lca_data"]:
                setattr(self.lcadata.gwp, stage, float(stage.value))

