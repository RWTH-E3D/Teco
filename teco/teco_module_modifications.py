"""This module switches modules from teaserplus with modules from teco."""

# from teaser.project import Project
# import teco.logic.archetypebuildings.bmvbs.singlefamilydwelling
import teaser.logic.archetypebuildings.bmvbs.singlefamilydwelling
import teaser.logic.buildingobjects.buildingphysics.buildingelement
import teaser.data.dataclass
# import teaser.logic.buildingobjects.building

import sys
del sys.modules['teaser.logic.archetypebuildings.bmvbs.singlefamilydwelling']
sys.modules['teaser.logic.archetypebuildings.bmvbs.singlefamilydwelling'] = \
    __import__('teco.logic.archetypebuildings.bmvbs.singlefamilydwelling')

del sys.modules['teaser.logic.buildingobjects.buildingphysics.buildingelement']
sys.modules['teaser.logic.buildingobjects.buildingphysics.buildingelement'] = \
    __import__('teco.logic.buildingobjects.buildingphysics.buildingelement')

del sys.modules['teaser.logic.buildingobjects.buildingphysics.material']
sys.modules['teaser.logic.buildingobjects.buildingphysics.material'] = \
    __import__('teco.logic.buildingobjects.buildingphysics.material')

del sys.modules['teaser.data.input.buildingelement_input_json']
sys.modules['teaser.data.input.buildingelement_input_json'] = \
    __import__('teco.data.input.buildingelement_input_json')

del sys.modules['teaser.data.input.material_input_json']
sys.modules['teaser.data.input.material_input_json'] = \
    __import__('teco.data.input.material_input_json')

del sys.modules['teaser.data.dataclass']
sys.modules['teaser.data.dataclass'] = \
    __import__('teco.data.dataclass')

del sys.modules['teaser.logic.utilities']
sys.modules['teaser.logic.utilities'] = \
    __import__('teco.logic.utilities')

import sys
del sys.modules['teaser.logic.buildingobjects.building']
sys.modules['teaser.logic.buildingobjects.building'] = \
    __import__('teco.logic.buildingobjects.building')