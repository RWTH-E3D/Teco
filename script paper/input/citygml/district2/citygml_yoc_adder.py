# this script is a short cut version of the e3d CityLDT (see espacially  LDTtransformation.py -> setBuildingElements(...) )

import os
import lxml.etree as ET


def add_yoc_to_element(building_E: ET.Element, nss: dict, yoc: int, overwrite: bool) -> None:
    prefix = "bldg"
    tagName = "yearOfConstruction"
    preTag = prefix + tagName
    # sBOrder list contains elements in the desired order. running the loop will add their last index if present to the dict, allowing other elements to be appended in the right place
    sBOrder = {'gml:description': -1, 'gml:name': -1, 'core:creationDate': -1, "core:externalReference": -1, 'core:relativeToTerrain': -1, 'gen:measureAttribute': -1, 'gen:stringAttribute': -1, 'bldg:class': -1, 'bldg:function': -1, 'bldg:usage': -1, 'bldg:yearOfConstruction': -1}
    for tag in sBOrder:
        target = building_E.findall(tag, nss)
        if target != []:
            index = building_E.index(target[-1])
            sBOrder[tag] = index

    # getting the right index to insert yoc element
    found = False
    insertIndex = 0
    for tag in sBOrder:
        if tag == preTag:
            found = True
            sBOrder[tag] = insertIndex +1
            continue
        if not found:
            if sBOrder[tag] != -1 and sBOrder[tag] > insertIndex:
                insertIndex = sBOrder[tag]
        else:
            if sBOrder[tag] != -1:
                sBOrder[tag] -=- 1

    check = building_E.find(preTag, nss)
    if check != None and overwrite:
        check.text = str(yoc)
    elif check == None:
        new_E = ET.Element(ET.QName(nss[prefix], tagName))
        new_E.text = str(yoc)
        building_E.insert(insertIndex + 1, new_E)


def add_yoc_to_file(path: str, yoc: int, overwrite: bool = False) -> None:
    """read file located under path and add year of construction (yoc) to every building, if overwrite is true, existing yoc's will be overwritten"""
    

    parser = ET.XMLParser(remove_blank_text=True)
    tree = ET.parse(path, parser)
    root = tree.getroot()
    nss = root.nsmap

    # getting all buildings in file
    buildings_in_file = root.findall('core:cityObjectMember/bldg:Building', nss)

    # iterating all buildings
    for building_E in buildings_in_file:
        bps_in_bldg = building_E.findall('./bldg:consistsOfBuildingPart', nss)
        if bps_in_bldg != []:
            for co_bp_E in bps_in_bldg:
                bp_E = co_bp_E.find('bldg:BuildingPart', nss)
                add_yoc_to_element(bp_E, nss, yoc, overwrite)
        else:
            add_yoc_to_element(building_E, nss, yoc, overwrite)
        
    newPath = os.path.splitext(path)[0] + "_YOCed.gml"
    
    print(newPath)
    tree.write(newPath, pretty_print = True, xml_declaration=True, encoding='utf-8', standalone='yes', method="xml")
    print(f"new file written to:{newPath}")
    

add_yoc_to_file(r"Essen_Vogelheim_2021_12_26_only_ids_commented_BPs.gml", 1965)


# uncomment the lines below to run as command line tool
# import sys
# import distutils
# def checkInputs(args):
#     if len(args) != 2 and len(args) != 3:
#         print("please enter the parameters in the following order:\npath_to_file year_of_construction (overwrite (optional) 1)")
#         return
#     if not (os.path.isfile(args[0]) and args[0].endswith(".gml")):
#         print(f"the given path ({args[0]}) is not valid. Please choose a different file")
#     try:
#         inted = int(args[1])
#     except:
#         print(f"failed to transform {args[1]} to int. Please choose a different number")
#     if len(args) == 3:
#         overwrite = bool(distutils.util.strtobool(args[2]))
#     else:
#         overwrite = False

#     add_yoc_to_file(args[0], inted, overwrite)
    


# if __name__ == "__main__":
#     print("eh")
#     checkInputs(sys.argv[1:])