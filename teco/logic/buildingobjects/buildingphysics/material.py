# created June 2015
# by TEASER4 Development Team


import re
import uuid
from teaser.logic.buildingobjects.buildingphysics.material import Material
import teco.data.input.material_input_json as material_input
import teco.data.output.material_output as material_output
from teco.logic.buildingobjects.buildingphysics.en15804lcadata import En15804LcaData


class Material(Material):
    """
    lca_data : En15804LcaData
        material environmental product declaration indicators according to 
        EN 15804
    service_life : int [a]
        service life of the material

    """

    def __init__(self, parent=None):
        """Constructor of Material.
        """
        super(Material, self).__init__(
            parent,
        )
        self._lca_data = None
        self._service_life = None
                
    @property
    def lca_data(self):
        return self._lca_data
    
    @lca_data.setter
    def lca_data(self, value):
        if isinstance(value, En15804LcaData):
            self._lca_data = value
        else:
            print("lca_data must be an En15804IndicatorValue-Object!")
            
    @property
    def service_life(self):
        return self._service_life

    @service_life.setter
    def service_life(self, value):
        if value != None:
            if not isinstance(value, int):
                try:
                    value = int(value)
                except:
                    raise ValueError("Service Life has to be integer")
                      
                
        self._service_life = value