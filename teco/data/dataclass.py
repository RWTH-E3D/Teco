"""This module holds file paths and bindings for json data."""
import os
import sys
import teco.logic.utilities as utils
import json
import collections

v = sys.version_info
if v >= (2, 7):
    try:
        FileNotFoundError
    except NameError:
        FileNotFoundError = IOError


class DataClass(object):
    """Class for JSON data.

    This class loads all JSON files with statistic or template data needed
    for statistical data enrichment.

    Parameters
    ----------
    used_statistics : str
        This parameter indicates which statistical data about building
        elements should be used. Use 'iwu' or 'tabula_de'.

    Attributes
    ----------
    element_bind : collections.OrderedDict
        Ordered dictionary of the TypeBuildingElements binding.
    path_tb : str
        Full path to TypeBuildingElements.json. Default is
        teaser/data/input/inputdata/TypeBuildingElements.json.
    material_bind : collections.OrderedDict
        Ordered dictionary of the Material binding.
    path_mat : str
        Full path to MaterialTemplates.json. Default is
        teaser/data/input/inputdata/MaterialTemplates.json.
    conditions_bind : collections.OrderedDict
        Ordered dictionary of the UseConditions binding.
    path_uc : str
        Full path to UseConditions.json. Default is
        teaser/data/input/inputdata/UseConditions.json
    lca_data_bind : collections.OrderedDict
        Ordered dictionary of the lca_data binding.        
    lca_data_fallback_bind : collections.OrderedDict
        Ordered dictionary of the lca_data_fallback binding.

    """

    def __init__(self, used_statistic="iwu"):
        """Construct DataClass."""
        self.used_statistic = used_statistic
        self.element_bind = None
        if self.used_statistic == "iwu":
            self.path_tb = utils.get_full_path(
                "data/input/inputdata/TypeBuildingElements.json"
            )
            self.load_tb_binding()
        elif self.used_statistic == "tabula_de":
            self.path_tb = utils.get_full_path(
                os.path.join(
                    "data", "input", "inputdata", "TypeElements_TABULA_DE.json"
                )
            )
            self.load_tb_binding()
        elif self.used_statistic == "tabula_dk":
            self.path_tb = utils.get_full_path(
                os.path.join(
                    "data", "input", "inputdata", "TypeElements_TABULA_DK.json"
                )
            )
            self.load_tb_binding()
        elif self.used_statistic == "kfw":
            self.path_tb = utils.get_full_path(
                "data/input/inputdata/TypeElements_kfw.json"

            )
            self.load_tb_binding()
        elif self.used_statistic is None:
            pass
        self.material_bind = None
        self.path_mat = utils.get_full_path(
            "data/input/inputdata/MaterialTemplates.json"
        )
        self.conditions_bind = None
        self.path_uc = utils.get_full_path("data/input/inputdata/UseConditions.json")
        
        self.lca_data_bind = None
        self.path_lcad = utils.get_full_path("data/input/inputdata/LcaData.json")
        
        self.lca_data_fallback_bind = None
        self.path_lcad_fallback = utils.get_full_path("data/input/inputdata/LcaDataFallback.json")

        self.utilities_data_bind = None
        self.path_ud = utils.get_full_path("data/input/inputdata/Utilities.json")

        self.load_uc_binding()
        self.load_mat_binding()
        self.load_lcad_binding()
        self.load_lcad_fallback_binding()
        self.load_ud_binding()
        
        

    def load_tb_binding(self):
        """Load TypeBuildingElement json into binding classes."""
        if self.path_tb.endswith("json"):
            if os.path.isfile(self.path_tb):
                try:
                    with open(self.path_tb, "r+") as f:
                        self.element_bind = json.load(
                            f, object_pairs_hook=collections.OrderedDict
                        )
                except json.decoder.JSONDecodeError:
                    print("Your TypeElements file seems to be broken.")
            else:
                with open(self.path_tb, "w") as f:
                    self.element_bind = collections.OrderedDict()
                    self.element_bind["version"] = "0.7"

    def load_uc_binding(self):
        """Load UseConditions json into binding classes."""
        if self.path_uc.endswith("json"):
            if os.path.isfile(self.path_uc):
                try:
                    with open(self.path_uc, "r+") as f:
                        self.conditions_bind = json.load(
                            f, object_pairs_hook=collections.OrderedDict
                        )
                except json.decoder.JSONDecodeError:
                    raise IOError("Your UseConditions.json file seems to be broken.")
            else:
                with open(self.path_uc, "w") as f:
                    self.conditions_bind = collections.OrderedDict()
                    self.conditions_bind["version"] = "0.7"

    def load_mat_binding(self):
        """Load MaterialTemplates json into binding classes."""
        if self.path_mat.endswith("json"):
            if os.path.isfile(self.path_mat):
                try:
                    with open(self.path_mat, "r+") as f:
                        self.material_bind = json.load(
                            f, object_pairs_hook=collections.OrderedDict
                        )
                except json.decoder.JSONDecodeError:
                    print("Your Materials file seems to be broken.")
            else:
                with open(self.path_mat, "w") as f:
                    self.material_bind = collections.OrderedDict()
                    self.material_bind["version"] = "0.7"
    
    def load_lcad_binding(self):
        """Load LCAData json into binding classes."""
        if self.path_lcad.endswith("json"):
            if os.path.isfile(self.path_lcad):
                try:
                    with open(self.path_lcad, "r+") as f:
                        self.lca_data_bind = json.load(
                            f, object_pairs_hook=collections.OrderedDict
                        )
                except json.decoder.JSONDecodeError:
                    print("Your LCA-Data file seems to be broken.")
            else:
                with open(self.path_lcad, "w") as f:
                    self.lca_data_bind = collections.OrderedDict()
                    self.lca_data_bind["version"] = "0.7"
                    
    def load_lcad_fallback_binding(self):
        """Load LCAData-Fallback json into binding classes."""
        if self.path_lcad_fallback.endswith("json"):
            if os.path.isfile(self.path_lcad_fallback):
                try:
                    with open(self.path_lcad_fallback, "r+") as f:
                        self.lca_data_fallback_bind = json.load(
                            f, object_pairs_hook=collections.OrderedDict
                        )
                except json.decoder.JSONDecodeError:
                    print("Your LCA-Data-Fallback file seems to be broken.")
            else:
                with open(self.path_lcad_fallback, "w") as f:
                    self.lca_data_fallback_bind = collections.OrderedDict()
                    self.lca_data_fallback_bind["version"] = "0.7"

    def load_ud_binding(self):
        """Load utility data json into binding classes."""
        if self.path_ud.endswith("json"):
            if os.path.isfile(self.path_ud):
                try:
                    with open(self.path_ud, "r+") as f:
                        self.utilities_data_bind = json.load(f, object_pairs_hook=collections.OrderedDict)
                except json.decoder.JSONDecodeError:
                    print("Your utility data file seems to be broken.")
            else:
                with open(self.path_ud, "w") as f:
                    self.utilities_data_bind = collections.OrderedDict()