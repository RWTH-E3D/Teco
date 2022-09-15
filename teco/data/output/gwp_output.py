from teaser.project import Project
from teco.logic.buildingobjects.buildingphysics.en15804lcadata import En15804LcaData
import csv

path = "building_gwp_export.csv"


def export_building_gwp_csv(project, path):
    # GWP of the whole Project?

    gwp_list = []
    for building in project.buildings:
        gwp_list.extend(building.lca_data.gwp)

    with open(path, "w", newline="") as csvfile:
        writer = csv.writer(csvfile, dialect="excel")
        writer.writerows()


# how do I make the function written in script_paper.py cleaner and more general? (thats the goal right?)
# on what can I test? bedburg gml and two more files on \Sciebo\SmartQuart_Hiwi\TEASER+,Teco\
# whats the type of building.lca_data.gwp
# in teco_main there is a project.py in a teaser folder, why was it deleted in development later?
