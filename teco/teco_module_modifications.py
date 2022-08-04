"""This module switches modules from teaserplus with modules from teco."""

import sys
import teaser.data.dataclass
import teaser.logic.utilities
import teaser.logic.buildingobjects.building
import teaser.logic.buildingobjects.thermalzone
import teaser.logic.buildingobjects.buildingphysics.buildingelement
# import teaser.logic.buildingobjects.buildingphysics.material

del sys.modules['teaser.data.dataclass']
sys.modules['teaser.data.dataclass'] = \
    __import__('teco.data.dataclass')

del sys.modules['teaser.logic.utilities']
sys.modules['teaser.logic.utilities'] = \
    __import__('teco.logic.utilities')

del sys.modules['teaser.logic.buildingobjects.building']
sys.modules['teaser.logic.buildingobjects.building'] = \
    __import__('teco.logic.buildingobjects.building')

del sys.modules['teaser.logic.buildingobjects.thermalzone']
sys.modules['teaser.logic.buildingobjects.thermalzone'] = \
    __import__('teco.logic.buildingobjects.thermalzone')

del sys.modules['teaser.logic.buildingobjects.buildingphysics.buildingelement']
sys.modules['teaser.logic.buildingobjects.buildingphysics.buildingelement'] = \
    __import__('teco.logic.buildingobjects.buildingphysics.buildingelement')

# del sys.modules['teaser.logic.buildingobjects.buildingphysics.material']
# sys.modules['teaser.logic.buildingobjects.buildingphysics.material'] = \
#     __import__('teco.logic.buildingobjects.buildingphysics.material')