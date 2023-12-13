# created June 2015
# by TEASER4 Development Team

"""This module includes the ThermalZone class
"""
from __future__ import division
from teaser.teaser.logic.buildingobjects.thermalzone import ThermalZone
from teco.logic.buildingobjects.buildingphysics.en15804lcadata import En15804LcaData


class ThermalZone(ThermalZone):
    """
    
    lca_data : En15804LcaData
        enviromental indicator of the thermalzone. The data referencing to
        one thermalzone
    """

    def __init__(self, parent=None):
        """Constructor for ThermalZone
        """


        super(ThermalZone, self).__init__(
            parent,
        )
        
        self._lca_data = None

    @property
    def lca_data(self):
        return self._lca_data

    @lca_data.setter
    def lca_data(self, value):
        self._lca_data = value
        
    def get_buildingelements(self):
        """returns a list of all buildingelements of the thermalzone
        

        Returns
        -------
        building_elements : list

        """
        building_elements = []
        
        building_elements.extend(self.outer_walls)
        building_elements.extend(self.ground_floors)
        building_elements.extend(self.rooftops)
        building_elements.extend(self.inner_walls)
        building_elements.extend(self.floors)
        building_elements.extend(self.windows)
        building_elements.extend(self.ceilings)
        
        return building_elements

    def calc_lca_data(self, use_b4 = None, period_lca_scenario = None):
        """sums up every LCA-data from building elements oft he thermalzone.
 
    
        Parameters
        ----------
        use_b4 : bool, optional
            if true all replaced materials and building elements are added to
            stage B4. The default is None.
        period_lca_scenario : int [a], optional
            period of use taken into account for LCA.

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
                
        building_elements = self.get_buildingelements()
        
        for building_element in building_elements:

            try:
                building_element.calc_lca_data(use_b4, period_lca_scenario)
                lca_data = lca_data + building_element.lca_data
            except:
                print("Error while adding {}".format(type(building_element).__name__))
            
        self.lca_data = lca_data