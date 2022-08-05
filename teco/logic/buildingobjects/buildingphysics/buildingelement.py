"""This module contains the Base class for all building elements."""

from __future__ import division
from teco.logic.buildingobjects.buildingphysics.en15804lcadata import En15804LcaData
from teaser.logic.buildingobjects.buildingphysics.buildingelement import BuildingElement
import teco.data.input.buildingelement_input_json as buildingelement_input


class BuildingElement(BuildingElement):
    """
    lca_data : En15804LcaData
        enviromental indicators of the building element. The data referencing
        one building element
    additional_lca_data : En15804LcaData
        additional environmental indicators to the indicators from the materials
    service_life : int [a]
        service_life of the building element in years
    """



    def __init__(self, parent=None):
        """Constructor for BuildingElement
        """
        super(BuildingElement, self).__init__(
            parent,
        )
        
        self._lca_data = None
        self._additional_lca_data = None
        self._service_life = None

    def load_type_element(
            self,
            year,
            construction,
            data_class=None):
        """Typical element loader.

        Loads typical building elements according to their construction
        year and their construction type from a json.

        This function will only work if the parents to Building are set.

        Parameters
        ----------
        year : int
            Year of construction

        construction : str
            Construction type, code list ('heavy', 'light')

        data_class : DataClass()
            DataClass containing the bindings for TypeBuildingElement and
            Material (typically this is the data class stored in prj.data,
            but the user can individually change that. Default is
            self.parent.parent.parent.data (which is data_class in current
            project)

        """

        if data_class is None:
            data_class = self.parent.parent.parent.data
        else:
            data_class = data_class

        self.layer = None
        self._inner_convection = None
        self._inner_radiation = None
        self._outer_convection = None
        self._outer_radiation = None

        buildingelement_input.load_type_element(element=self,
                                                year=year,
                                                construction=construction,
                                                data_class=data_class)

    @property
    def lca_data(self):
        return self._lca_data

    @lca_data.setter
    def lca_data(self, value):
        self._lca_data = value
    
    @property
    def additional_lca_data(self):
        return self._additional_lca_data
    
    @additional_lca_data.setter
    def additional_lca_data(self, value):
        self._additional_lca_data = value
        
    @property
    def service_life(self):
        return self._service_life
    
    @service_life.setter
    def service_life(self, value):
        if value is not None:
            if not isinstance(value, int):
                try:
                    value = int(value)
                except TypeError:
                    print("Service life has to be integer")
                      
                
        self._service_life = value
    
    def calc_lca_data(self, use_b4 = None, period_lca_scenario = None):
        """calculates the LCA-data of the buildingelement and set it to the
        attribute lca_data
        

        Parameters
        ----------
        use_b4 : bool, optional
            if true environmental indicators of replaced buildingelements are added
            to stage B4. Otherwise they are added seperatly to the other stages
        period_lca_scenario : TYPE, optional
            period which is taken into account for LCA. The default is None.

        """
        
        if use_b4 is None:
            try:
                use_b4 = self.parent.parent.parent.use_b4
            except:
                use_b4 = False
        
        if self.layer != []:
            lca_data = En15804LcaData()
            lca_data.ref_flow_unit = "pcs"
            
            
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

    def _calc_lca_data_no_repl(self):
        """calculates the environmental indicators of the buildingelement 
        without any replacements
        

        Returns
        -------
        lca_data_be : En15804LcaData
            environmental indicators of the buildingelement without any
            replacements
        """
        
        lca_data_be = En15804LcaData()
        lca_data_be.ref_flow_unit = "pcs"
                
        for layer in self.layer:
            
            lca_data_layer = layer.material.lca_data
            lca_data_layer = lca_data_layer.convert_ref_unit(
                                    target_unit = "pcs",
                                    area = self.area,
                                    thickness = layer.thickness,
                                    density = layer.material.density
                                    )
            
            lca_data_be = lca_data_be + lca_data_layer
        if self.additional_lca_data is not None:
            if self.additional_lca_data.ref_flow_unit != "pcs":
                self.additional_lca_data = self.additional_lca_data.convert_ref_unit("pcs", area=self.area)

            lca_data_be = lca_data_be + self.additional_lca_data
            
        return lca_data_be
        
    def _calc_lca_data_layer_repl(self, ref_period=80):
        """calculates the LCA-data caused by layer replacement in a specific
        time period
        

        Parameters
        ----------
        ref_period : int, optional [a]
            reference time period. The default is 80 years.

        Returns
        -------
        lca_data_repl_layers : En15804LcaData
            environmental indicators from layer replacement

        """
        
        lca_data_repl_layers = En15804LcaData()
        lca_data_repl_layers.ref_flow_unit = "pcs"
        
        repl_layers_1, repl_interval_1 = self._get_repl_layers(True)
        repl_layers_2, repl_interval_2 = self._get_repl_layers(False)
        
        if repl_interval_1 < ref_period:
            for layer in repl_layers_1:
                
                lca_data_layer = layer.material.lca_data
                lca_data_layer = lca_data_layer.convert_ref_unit(
                                        target_unit = "pcs",
                                        area = self.area,
                                        thickness = layer.thickness,
                                        density = layer.material.density
                                        )
                lca_data_repl_layers = lca_data_repl_layers + lca_data_layer
                
        if repl_interval_2 < ref_period:
            for layer in repl_layers_2:
                
                lca_data_layer = layer.material.lca_data
                lca_data_layer = lca_data_layer.convert_ref_unit(
                                        target_unit = "pcs",
                                        area = self.area,
                                        thickness = layer.thickness,
                                        density = layer.material.density
                                        )
                
                lca_data_repl_layers = lca_data_repl_layers + lca_data_layer
                
        return lca_data_repl_layers

    def _get_repl_layers(self, side: bool):
        """returns all materials which must be replaced on one side of the
        buildingelement. Materials which are surrounded by layers with longer
        service life will not be replaced

        Parameters
        ----------
        side : bool
            is true for the first side of the element and false for the second

        Returns
        -------
        repl_layers : list
            layers to be replaced
        repl_interval : TYPE
            longest service life of the replaced layers (= interval in which
            the layers are replaced)

        """
        
        repl_layers = []
        
        if side:
            layers = self.layer
        else:
            layers = list(reversed(self.layer))
        
        if layers[0].material.service_life:
            repl_interval = layers[0].material.service_life
            
            repl_layers.append(layers[0])
            
            for layer in layers[1:]:
                if layer.material.service_life:
                    if layer.material.service_life <= repl_interval:
                        repl_layers.append(layer)
                    else:
                        break
                else:
                    break   
                
            return repl_layers, repl_interval
            
        else:
            return [], -1
        
        