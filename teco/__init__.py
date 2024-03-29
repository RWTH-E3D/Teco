'''
teco
=========
An extension to TEASER (Tool for Energy Analysis and Simulation for Efficient Retrofit) and TEASERplus
'''
import sys
import os

v = sys.version_info
if v >= (3, 3):
    py33 = True
    py27 = False
elif v >= (2, 7) and v < (3,):
    py33 = False
    py27 = True
else:
    raise Exception('This software runs on python versions 2.7 or >=3.3 only!')

new_path = os.path.join(os.path.expanduser('~'), ("TEASEROutput"))
if not os.path.exists(new_path):
    os.makedirs(new_path)

if sys.platform.startswith('win'):
    def read_file(path, mode='r'):
        fp = open(path, mode)
        try:
            data = fp.read()
            return data
        finally:
            fp.close()
    # hot patch loaded module :-)
    import mako.util
    mako.util.read_file = read_file
    del read_file

from teco.logic.utilities import division_from_json
from teco.logic.buildingobjects.buildingphysics.buildingelement import BuildingElement
from teco.logic.buildingobjects.building import Building
from teco.data.dataclass import DataClass
from teco.logic.buildingobjects.thermalzone import ThermalZone
import teco.teco_module_modifications
