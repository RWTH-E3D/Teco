# -*- coding: utf-8 -*-
"""
TEASER+
Contact:
M.Sc. Avichal Malhotra: malhotra@e3d.rwth-aachen.de
M.Sc. Maxim Shamovich: shamovich@e3d.rwth-aachen.de
Yacine Tayeb: yacine.tayeb@rwth-aachen.de

www.e3d.rwth-aachen.de
Mathieustr. 30
52074 Aachen

Some GUI functions taken from CityLDT.
Please contact Avichal Malhotra or Simon Raming for any questions.
Original Repo for CityLDT: https://gitlab.e3d.rwth-aachen.de/e3d-software-tools/cityldt/cityldt.git
"""

# import of libraries
import os
import sys
import time

from PySide6 import QtWidgets, QtCore, QtGui

import gui_functions as gf
from teco.logic.buildingobjects.buildingphysics.en15804indicatorvalue import En15804IndicatorValue
from teco.project import Project  # or teco?
from teaser.logic import utilities  # or teco?
from teaser.logic.buildingobjects.building import Building
import teaser.data.input.citygml_input as citygml_in
import simulate as sim
from teco.logic.buildingobjects.buildingphysics.en15804lcadata import En15804LcaData
import json

# setting environment variable for PySide2
# dirname = os.path.dirname(PySide6.__file__)
# plugin_path = os.path.join(dirname, 'plugins', 'platforms')
# os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugin_path


# positions and dimensions of window
POSX = 275
POSY = 100
WIDTH = 650
HEIGHT = 600
SIZEFACTOR = 0
SIZER = False

teaser_path = os.path.join("C:/Users/tayeb/teaser") #############Todo: CHANGE THIS TO YOUR TEASER PATH
output_path = os.path.join("C:/Users/tayeb/TEASEROutput") #############Todo: CHANGE THIS TO YOUR OUTPUT PATH


class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        # initiate the parent
        super(MainWindow, self).__init__()
        self.initUI()

    def initUI(self):
        global POSX, POSY, WIDTH, HEIGHT, SIZEFACTOR, SIZER

        # setup of gui / layout
        if SIZER:
            POSX, POSY, WIDTH, HEIGHT, SIZEFACTOR = gf.screenSizer(POSX, POSY, WIDTH, HEIGHT, app)
            SIZER = False
        gf.windowSetup(self, POSX, POSY, WIDTH, HEIGHT, 'TEASER+ and Teco')

        # Setting main layout
        self.vbox = QtWidgets.QVBoxLayout(self)
        self.setLayout(self.vbox)

        # Loading banner
        gf.load_banner(self, r'../pictures/TEASER+_header.png', 3.25)

        # Setting Layout
        self.uGrid = QtWidgets.QGridLayout()

        self.btn_selFile = QtWidgets.QPushButton('Select file')
        self.btn_selFile.setMaximumWidth(100)
        self.btn_selFile.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.uGrid.addWidget(self.btn_selFile, 0, 0, 1, 1)

        self.btn_selDir = QtWidgets.QPushButton('Select folder')
        self.btn_selDir.setMaximumWidth(100)
        self.btn_selDir.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.uGrid.addWidget(self.btn_selDir, 0, 1, 1, 1)

        self.txtB_inPath = QtWidgets.QLineEdit()
        self.txtB_inPath.setPlaceholderText('Path to file or folder')
        self.txtB_inPath.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.txtB_inPath.setReadOnly(True)
        self.uGrid.addWidget(self.txtB_inPath, 0, 2, 1, 2)

        self.lbl_scanLoD = QtWidgets.QLabel('LoD scan progress:')
        self.uGrid.addWidget(self.lbl_scanLoD, 1, 0, 1, 1)

        self.pB_scanLoD = QtWidgets.QProgressBar(self)
        self.pB_scanLoD.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.uGrid.addWidget(self.pB_scanLoD, 1, 1, 1, 3)

        self.vbox.addLayout(self.uGrid)

        # for selecting all or individual buildings
        self.gB_buildings = QtWidgets.QGroupBox('')
        self.gB_buildings.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.vbox.addWidget(self.gB_buildings)
        # self.gB_buildings.setToolTip('When unchecked transformation will be done for all buildings in the file(s)')

        self.bGrid = QtWidgets.QGridLayout()
        self.gB_buildings.setLayout(self.bGrid)

        self.rb_allBuildings = QtWidgets.QRadioButton('Transform all buildings')
        self.bGrid.addWidget(self.rb_allBuildings, 0, 0, 1, 1)
        self.rb_allBuildings.setChecked(True)

        self.rb_selectBuildings = QtWidgets.QRadioButton('Select individual buildings')
        self.bGrid.addWidget(self.rb_selectBuildings, 0, 3, 1, 1)

        self.tbl_buildings = QtWidgets.QTableWidget()
        self.tbl_buildings.setColumnCount(6)
        self.tbl_buildings.setHorizontalHeaderLabels(
            ['File Name', 'Name of Building', 'Level of Detail (LoD)', 'Year of Construction (YoC)',
             'Gross Leased Area (GLA)', ''])
        self.tbl_buildings.verticalHeader().hide()
        # self.tbl_buildings.horizontalHeader().hide()
        self.tbl_buildings.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tbl_buildings.setEnabled(False)
        # self.tbl_buildings.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        # self.tbl_buildings.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        # self.tbl_buildings.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
        self.tbl_buildings.resizeColumnsToContents()
        self.tbl_buildings.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.bGrid.addWidget(self.tbl_buildings, 1, 0, 1, 6)

        # Gridbox for lower grid
        self.lGrid = QtWidgets.QGridLayout()
        self.btn_teaser = QtWidgets.QPushButton('TEASER Enrichment')
        self.btn_teaser.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.lGrid.addWidget(self.btn_teaser, 0, 0, 1, 1)
        self.btn_teaser.setEnabled(True)

        self.btn_teco = QtWidgets.QPushButton('TEASEREco')
        self.btn_teco.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.lGrid.addWidget(self.btn_teco, 0, 2, 1, 1)
        self.btn_teco.setEnabled(True)

        self.btn_about = QtWidgets.QPushButton('About')
        self.btn_about.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.lGrid.addWidget(self.btn_about, 1, 0, 1, 1)

        self.btn_reset = QtWidgets.QPushButton('Reset')
        self.btn_reset.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.lGrid.addWidget(self.btn_reset, 1, 1, 1, 1)

        self.btn_exit = QtWidgets.QPushButton('Exit')
        self.btn_exit.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.lGrid.addWidget(self.btn_exit, 1, 2, 1, 1)

        # self.btn_teaser = QtWidgets.QPushButton('Next')
        # self.lGrid.addWidget(self.btn_teaser, 0, 3, 1, 1)
        # self.btn_teaser.setEnabled(False)

        # setting some defaults
        self.inpPath = ''
        self.inpDir = ''
        self.expPath = ''
        self.completedLoD = 0
        # table row index to comboBox index
        self.buildingDict = {}

        self.vbox.addLayout(self.lGrid)
        self.btn_selFile.clicked.connect(self.func_selectFile)
        self.btn_selDir.clicked.connect(self.func_selectDir)
        self.rb_selectBuildings.toggled.connect(self.func_selB)
        self.btn_about.clicked.connect(self.func_about)
        self.btn_reset.clicked.connect(self.func_reset)
        self.btn_exit.clicked.connect(self.func_exit)
        self.btn_teaser.clicked.connect(self.func_teaser)
        self.btn_teco.clicked.connect(self.func_teco)
        # self.cB_curBuilding.currentTextChanged.connect(self.func_curBuildingChanged)

        # self.gB_buildings.toggled.connect(self.func_buildingSelection)

    def func_selectDir(self):
        res = gf.select_folder(self, self.txtB_inPath)
        if res:
            self.inpPath = res
            self.inpDir = os.path.dirname(res)
            gf.get_files(self)
        else:
            pass

    def func_selectFile(self):
        res = gf.select_gml(self)
        if res:
            self.inpPath = res
            gf.get_files(self)
        else:
            pass

    def func_selB(self) -> None:
        if self.rb_selectBuildings.isChecked():
            self.tbl_buildings.setEnabled(True)
        else:
            self.tbl_buildings.setEnabled(False)

    def func_about(self) -> None:
        global POSX, POSY
        POSX, POSY = gf.windowPosition(self)
        gf.next_window(self, about("about_teaser.txt"), False)

    def func_reset(self) -> None:
        global POSX, POSY
        choice = QtWidgets.QMessageBox.question(self, "Warning", "Are you sure you want to reset this window?")

        if choice == QtWidgets.QMessageBox.Yes:
            self.reset_variables()
            POSX, POSY = gf.windowPosition(self)
            gf.next_window(self, MainWindow(), close=True)

    def reset_variables(self) -> None:
        self.inpPath = ''
        self.inpDir = ''
        self.completedLoD = 0

    def func_exit(self) -> None:
        gf.close_application(self)

    def func_teaser(self) -> None:
        global POSX, POSY
        POSX, POSY = gf.windowPosition(self)
        if self.rb_allBuildings.isChecked():
            for key in self.buildingDict:
                self.buildingDict[key]["selected"] = True
        gf.next_window(self, TeaserEnrichment(self.buildingDict, self.inpPath, self))

    def func_teco(self) -> None:
        global POSX, POSY
        POSX, POSY = gf.windowPosition(self)
        if self.rb_allBuildings.isChecked():
            for key in self.buildingDict:
                self.buildingDict[key]["selected"] = True

        gf.next_window(self, Eco(self.buildingDict, self.inpPath, self))

    def onStateChanged(self) -> None:
        """gets called when a checkbox for a building is (un)checked to update the buildingDict"""
        ch = self.sender()
        ix = self.tbl_buildings.indexAt(ch.pos())
        self.buildingDict[ix.row()]["selected"] = ch.isChecked()
        curText = self.tbl_buildings.item(ix.row(), 1).text().split('/')[0]
        for i in range(self.tbl_buildings.rowCount()):
            if i != ix.row():
                if self.tbl_buildings.item(i, 1).text().split('/')[0] == curText:
                    self.cBoxes[i].setChecked(ch.isChecked())
                    self.buildingDict[i]["selected"] = ch.isChecked()
                    self.checkBoxChange(i, ch.isChecked())
        self.checkBoxChange(ix.row(), ch.isChecked())

    def checkBoxChange(self, row: int, state: bool) -> None:
        """changes Table"""
        if state:
            colorCode = (251, 255, 0)

            """
            # setting dummyValue to get right index of sorted list
            self.buildingDict[row] = "dummyValue"
            # getting and sorting all indexes of selected buildings
            sortedList = sorted(list(self.buildingDict.keys()))
            # getting the correceted Index location of the new building
            correctedIndex = sortedList.index(row) + 1
            # replacing the dummyValue
            self.buildingDict[row] = correctedIndex
            # add item to comboBox
            # self.cB_curBuilding.insertItem(correctedIndex, self.buildingDict[row]["filename"] + "/" + self.buildingDict[row]["buildingname"])
            # self.btn_saveBuildingParamsAndNext.setEnabled(True)

            for y in self.buildingDict:
                if y > row:
                    self.buildingDict[y] = self.buildingDict[y] + 1
            """
        else:
            colorCode = (255, 255, 255)

            """
            num = row

            # remove save building Parameters
            if row in self.b:
                del self.buildingDict[row]

            for y in self.buildingDict:
                if y > num:
                    self.buildingDict[y] = self.buildingDict[y] - 1

            # remove item from comboBox
            self.cB_curBuilding.removeItem(self.buildingDict[row])
            del self.buildingDict[row]

            # if self.cB_curBuilding.count() == 1 or self.cB_curBuilding.currentIndex() == self.cB_curBuilding.count() - 1:
            #     self.btn_saveBuildingParamsAndNext.setEnabled(False)
            """
        gf.setTableRowColor(self, colorCode, row)


class TeaserEnrichment(QtWidgets.QWidget):
    """window to enrich / change building information"""

    def __init__(self, buildingDict: dict, inpPath: str, mainWindow):
        super(TeaserEnrichment, self).__init__()
        self.buildingDict = buildingDict
        self.inpPath = inpPath
        self.mW = mainWindow
        self.initUI()

    def initUI(self):
        global POSX, POSY, WIDTH, HEIGHT, SIZEFACTOR, SIZER
        if SIZER:
            POSX, POSY, WIDTH, HEIGHT, SIZEFACTOR = gf.screenSizer(POSX, POSY, WIDTH, HEIGHT, self.mW)
            SIZER = False
        gf.windowSetup(self, POSX, POSY, WIDTH, HEIGHT, 'CityLDT - CityGML LoD Transformation Tool - Transformation')

        self.vbox = QtWidgets.QVBoxLayout(self)
        self.setLayout(self.vbox)

        gf.load_banner(self, r'../pictures/TEASER+_header.png', 4)

        self.tbl_selBuildings = QtWidgets.QTableWidget()
        self.tbl_selBuildings.setColumnCount(7)
        self.tbl_selBuildings.setHorizontalHeaderLabels(
            ['Name of building/utility', 'LoD', 'YoC', 'YoC Class', 'No. of floors', 'Floor height [m]', 'Usage Type'])
        self.tbl_selBuildings.setEditTriggers(QtWidgets.QAbstractItemView.DoubleClicked)
        self.tbl_selBuildings.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

        self.vbox.addWidget(self.tbl_selBuildings)

        self.lGrid = QtWidgets.QGridLayout()

        self.comB_method = QtWidgets.QComboBox()
        self.comB_method.setPlaceholderText("Choose method here")
        self.comB_method.addItems(["IWU", "tabula_de", "tabula_dk", "urbanrenet"])
        self.lGrid.addWidget(self.comB_method, 0, 0, 1, 1)

        self.btn_saveToCityGML = QtWidgets.QPushButton("Save to CityGML file")
        self.lGrid.addWidget(self.btn_saveToCityGML, 1, 0, 1, 1)

        self.btn_saveToNewCityGML = QtWidgets.QPushButton("Save to new CityGML file")
        self.lGrid.addWidget(self.btn_saveToNewCityGML, 1, 1, 1, 1)

        self.btn_setupSim = QtWidgets.QPushButton("Setup simulation")
        self.btn_setupSim.setToolTip("Please save changes first")
        self.lGrid.addWidget(self.btn_setupSim, 2, 0, 1, 1)

        self.btn_returnMain = QtWidgets.QPushButton("Return to main window")
        self.lGrid.addWidget(self.btn_returnMain, 2, 1, 1, 1)

        self.vbox.addLayout(self.lGrid)

        ttl = 'Number of selected buildings - ' + str(len(self.buildingDict))
        # building parameters
        self.gB_buildingParameters = QtWidgets.QGroupBox(ttl)
        self.vbox.addWidget(self.gB_buildingParameters)
        self.vBox_forBPgB = QtWidgets.QVBoxLayout()
        self.gB_buildingParameters.setLayout(self.vBox_forBPgB)

        # building selection
        self.pGrid = QtWidgets.QGridLayout()

        self.lbl_curBuilding = QtWidgets.QLabel('Current building:')
        self.pGrid.addWidget(self.lbl_curBuilding, 0, 0, 1, 1)

        self.cB_curBuilding = QtWidgets.QComboBox()
        self.cB_curBuilding.addItems(['all (selected) buildings'])
        self.pGrid.addWidget(self.cB_curBuilding, 0, 1, 1, 2)

        self.btn_saveToCityGML.clicked.connect(lambda: self.func_saveToCityGML(False))
        self.btn_saveToNewCityGML.clicked.connect(lambda: self.func_saveToCityGML(True))
        self.btn_returnMain.clicked.connect(self.func_returnToMain)
        self.btn_setupSim.clicked.connect(self.func_setupSim)

        self.comB_method.currentTextChanged.connect(self.func_methodChanged)

        self.valueDict = {}

        self.combBoxesYoc = []
        self.combBoxesUse = []

        # for storing path to file
        self.fileToSimulate = ""
        # for checking if recent changes are identical to saved changes
        self.savedChanges = {}

        for key in self.buildingDict:
            # make sure that the building is selected
            if not self.buildingDict[key]["selected"]:
                continue

            rowCount = self.tbl_selBuildings.rowCount()
            self.tbl_selBuildings.insertRow(rowCount)

            newItem = QtWidgets.QTableWidgetItem(self.buildingDict[key]["buildingname"])
            newItem.setFlags(newItem.flags() & ~QtCore.Qt.ItemIsEditable)
            newItem.setToolTip(self.buildingDict[key]["buildingname"])
            self.tbl_selBuildings.setItem(rowCount, 0, newItem)

            newItem = QtWidgets.QTableWidgetItem(str(self.buildingDict[key]["values"]["LoD"]))
            newItem.setFlags(newItem.flags() & ~QtCore.Qt.ItemIsEditable)
            self.tbl_selBuildings.setItem(rowCount, 1, newItem)

            newItem = QtWidgets.QTableWidgetItem(str(self.buildingDict[key]["values"]["YoC"]))
            self.tbl_selBuildings.setItem(rowCount, 2, newItem)

            self.combBoxesYoc.append(QtWidgets.QComboBox(parent=self.tbl_selBuildings))
            self.combBoxesYoc[-1].setPlaceholderText("choose method first")
            self.tbl_selBuildings.setCellWidget(rowCount, 3, self.combBoxesYoc[-1])

            newItem = QtWidgets.QTableWidgetItem(str(self.buildingDict[key]["values"]["SAG"]))
            self.tbl_selBuildings.setItem(rowCount, 4, newItem)

            newItem = QtWidgets.QTableWidgetItem(str(self.buildingDict[key]["values"]["storeyHeight"]))
            self.tbl_selBuildings.setItem(rowCount, 5, newItem)

            self.combBoxesUse.append(QtWidgets.QComboBox(parent=self.tbl_selBuildings))
            self.combBoxesUse[-1].setPlaceholderText("choose method first")
            self.tbl_selBuildings.setCellWidget(rowCount, 6, self.combBoxesUse[-1])

            # make changes to editabiltiy of the table items
            if self.buildingDict[key]["values"]["YoC"] != "":
                self.tbl_selBuildings.cellWidget(rowCount, 3).setEnabled(False)

            # make changes to editabiltiy of the table items
            if self.buildingDict[key]["values"]["SAG"] != "" or self.buildingDict[key]["values"]["storeyHeight"] != "":
                self.tbl_selBuildings.item(rowCount, 5).setFlags(
                    self.tbl_selBuildings.item(rowCount, 5).flags() & ~QtCore.Qt.ItemIsEditable)
                self.tbl_selBuildings.item(rowCount, 4).setFlags(
                    self.tbl_selBuildings.item(rowCount, 4).flags() & ~QtCore.Qt.ItemIsEditable)

            self.valueDict[self.buildingDict[key]["buildingname"]] = self.buildingDict[key]["values"]

        self.tbl_selBuildings.itemChanged.connect(self.tableUpdater)

    '''
        # update title of groubbox according to number of buildings
        ttl = 'Number of selected buildings - ' + str(self.cB_curBuilding.count() - 1)
        self.gB_buildingParameters.setTitle(ttl)

        self.vBox_forBPgB.addLayout(self.pGrid)

        # Enrichmet properties
        self.dB_enrichment = QtWidgets.QGroupBox('Building Enrichment')
        self.vBox_forBPgB.addWidget(self.dB_enrichment)

        self.dGrid = QtWidgets.QGridLayout()
        self.dB_enrichment.setLayout(self.dGrid)

        self.lbl_year_of_construction = QtWidgets.QLabel('Year of Construction')
        self.dGrid.addWidget(self.lbl_year_of_construction, 0, 0, 1, 1)

        self.txtb_year_of_construction = QtWidgets.QLineEdit()
        # self.txtb_year_of_construction.setFixedWIDTH(250)
        self.txtb_year_of_construction.setPlaceholderText('Select individual building to overwrite')
        self.txtb_year_of_construction.setReadOnly(True)
        self.dGrid.addWidget(self.txtb_year_of_construction, 0, 1, 1, 1)

        self.lbl_dwelling_archetype = QtWidgets.QLabel('Select Archetype')
        self.dGrid.addWidget(self.lbl_dwelling_archetype, 0, 2, 1, 1)

        self.combobox_dwelling = QtWidgets.QComboBox()
        self.combobox_dwelling.addItems(
            [" ", "IWU Single Family Dwelling", "TABULA Single Family House", "TABULA Multi Family House",
             "TABULA Terraced House", "TABULA Apartment Block"])
        self.dGrid.addWidget(self.combobox_dwelling, 0, 3, 1, 1)

        self.lbl_weather = QtWidgets.QPushButton('Select Weather file')
        self.dGrid.addWidget(self.lbl_weather, 1, 0, 1, 1)

        self.txt_weather = QtWidgets.QLineEdit('')
        self.dGrid.addWidget(self.txt_weather, 1, 1, 1, 3)

        self.lbl_enrichment = QtWidgets.QLabel('Enrich models using pre-defined archetypes')
        self.dGrid.addWidget(self.lbl_enrichment, 2, 0, 1, 2)

        self.btn_enrich = QtWidgets.QPushButton('Click to custom enrich')
        self.dGrid.addWidget(self.btn_enrich, 2, 2, 1, 2)

        self.grp_out = QtWidgets.QGroupBox('Output Options')
        self.vBox_forBPgB.addWidget(self.grp_out)

        self.mGrid = QtWidgets.QGridLayout()
        self.grp_out.setLayout(self.mGrid)

        # Adding output options
        self.checkbox_modelica = QtWidgets.QCheckBox("Modelica Model")
        self.mGrid.addWidget(self.checkbox_modelica, 0, 0, 1, 1)

        self.checkbox_withsimulation = QtWidgets.QCheckBox("With Simulation (if Dymola installed locally)")
        self.mGrid.addWidget(self.checkbox_withsimulation, 0, 1, 1, 1)

        self.checkbox_gml_ade_file = QtWidgets.QCheckBox("CityGML Energy ADE")
        self.mGrid.addWidget(self.checkbox_gml_ade_file, 0, 2, 1, 1)

        self.lbl_dymola = QtWidgets.QPushButton('Select Dymola path')
        self.mGrid.addWidget(self.lbl_dymola, 1, 0, 1, 1)
        self.lbl_dymola.setEnabled(False)

        self.txt_dymola = QtWidgets.QLineEdit('')
        self.mGrid.addWidget(self.txt_dymola, 1, 1, 1, 2)
        self.txt_dymola.setEnabled(False)

        self.grp_save = QtWidgets.QGroupBox('Save As')
        self.vBox_forBPgB.addWidget(self.grp_save)

        self.m1Grid = QtWidgets.QGridLayout()
        self.grp_save.setLayout(self.m1Grid)

        # Adding save as options
        self.checkbox_excel = QtWidgets.QCheckBox(".anything else")
        self.m1Grid.addWidget(self.checkbox_excel, 0, 0, 1, 1)

        self.checkbox_CSV = QtWidgets.QCheckBox(".csv")
        self.m1Grid.addWidget(self.checkbox_CSV, 0, 1, 1, 1)

        self.checkbox_excel = QtWidgets.QCheckBox(".xsls")
        self.m1Grid.addWidget(self.checkbox_excel, 0, 2, 1, 1)

        self.lbl_outputpath = QtWidgets.QPushButton('Select Output path')
        self.m1Grid.addWidget(self.lbl_outputpath, 1, 0, 1, 1)
        self.lbl_outputpath.setEnabled(False)

        self.txt_outputpath = QtWidgets.QLineEdit('')
        self.m1Grid.addWidget(self.txt_outputpath, 1, 1, 1, 2)
        self.txt_outputpath.setEnabled(False)

        # Gridbox for lower grid
        self.lGrid = QtWidgets.QGridLayout()

        self.btn_back = QtWidgets.QPushButton('Main Window')
        self.btn_back.clicked.connect(self.func_returnToMain())
        self.lGrid.addWidget(self.btn_back, 0, 0, 1, 1)

        self.btn_teco = QtWidgets.QPushButton('TEASEREco')
        # self.btn_back.clicked.connect(self.func_next(choose="Teco"))
        self.lGrid.addWidget(self.btn_teco, 0, 1, 1, 1)

        # self.btn_teaser = QtWidgets.QPushButton('Execute')
        # self.lGrid.addWidget(self.btn_teaser, 0, 2, 1, 1)

        self.btn_about = QtWidgets.QPushButton('About')
        self.lGrid.addWidget(self.btn_about, 1, 0, 1, 1)

        self.btn_reset = QtWidgets.QPushButton('Reset')
        self.lGrid.addWidget(self.btn_reset, 1, 1, 1, 1)

        self.btn_exit = QtWidgets.QPushButton('Exit')
        self.lGrid.addWidget(self.btn_exit, 1, 2, 1, 1)

        self.vbox.addLayout(self.lGrid)

        # #Adding Label and button for file selection
        # self.label_selectfile = QtWidgets.QLabel("Select File")
        # self.lGrid.addWidget(self.label_selectfile, 0, 0, 1, 1)
        #
        # self.btn_selectfile = QtWidgets.QPushButton("Click to select")
        # self.lGrid.addWidget(self.btn_selectfile, 0, 1, 1, 1)
        #
        # #Adding label and combobox for building selection
        # self.label_selectbuilding = QtWidgets.QLabel("Select Building")
        # self.lGrid.addWidget(self.label_selectbuilding, 1, 0, 1, 1)
        #
        # self.dropdown_buildings = QtWidgets.QComboBox()
        # self.lGrid.addWidget(self.dropdown_buildings, 1, 1, 1, 1)
        #
        # #Adding horizontal partition
        # self.lGrid.addWidget(gf.divider(), 2, 0, 1, 2)

        # #Adding Enrichment
        # self.label_enrichment = QtWidgets.QLabel("Enrichment")
        # self.lGrid.addWidget(self.label_enrichment, 3, 0, 1, 1)
        #
        # #Adding enrichment options
        # self.checkbox_gml = QtWidgets.QCheckBox("Select GML File")
        # self.lGrid.addWidget(self.checkbox_gml, 4, 0, 1, 1)
        #
        # self.checkbox_ade = QtWidgets.QCheckBox("Select CityGML + Energy ADE")
        # self.lGrid.addWidget(self.checkbox_ade, 4, 1, 1, 1)
        #
        # #Adding horizontal partition
        # self.lGrid.addWidget(gf.divider(), 5, 0, 1, 2)
        #
        # #Add select dwelling
        # self.label_dwelling = QtWidgets.QLabel("Select Dwelling Archetype")
        # self.lGrid.addWidget(self.label_dwelling, 6, 0, 1, 1)
        #
        # self.combobox_dwelling = QtWidgets.QComboBox()
        # self.combobox_dwelling.addItems(["SFD", "MFD", "etc"])
        # self.lGrid.addWidget(self.combobox_dwelling, 6, 1, 1, 1)
        #
        # #Adding horizontal partition
        # self.lGrid.addWidget(gf.divider(), 7, 0, 1, 2)
        #
        # #Add select weather
        # self.label_weather = QtWidgets.QLabel("Select weather file")
        # self.lGrid.addWidget(self.label_weather, 8, 0, 1, 1)
        #
        # self.btn_weather = QtWidgets.QPushButton("Click to select")
        # self.lGrid.addWidget(self.btn_weather, 8, 1, 1, 1)
        #
        # # Adding horizontal partition
        # self.lGrid.addWidget(gf.divider(), 9, 0, 1, 2)
        #
        # #Add select weather
        # self.label_custom = QtWidgets.QLabel("Custom Enrichment")
        # self.lGrid.addWidget(self.label_custom, 10, 0, 1, 1)
        #
        # self.btn_custom = QtWidgets.QPushButton("Click for custom enrichment")
        # self.lGrid.addWidget(self.btn_custom, 10, 1, 1, 1)
        #
        # # Adding horizontal partition
        # self.lGrid.addWidget(gf.divider(), 11, 0, 1, 2)
        #
        # # Adding output options
        # self.checkbox_withsimulation = QtWidgets.QCheckBox("With Simulation (only if Dymola installed locally)")
        # self.lGrid.addWidget(self.checkbox_withsimulation, 12, 0, 1, 1)
        #
        # self.checkbox_modelica = QtWidgets.QCheckBox("Modelica Model")
        # self.lGrid.addWidget(self.checkbox_modelica, 12, 1, 1, 1)
        #
        # self.checkbox_gml_ade_file = QtWidgets.QCheckBox("CityGML Energy ADE")
        # self.lGrid.addWidget(self.checkbox_gml_ade_file, 13, 0, 1, 1)
        #
        # self.checkbox_csv = QtWidgets.QCheckBox("CSV Results (only if Dymola installed locally)")
        # self.lGrid.addWidget(self.checkbox_ade, 13, 1, 1, 1)
        #
        # # Adding horizontal partition
        # self.lGrid.addWidget(gf.divider(), 14, 0, 1, 2)
        #
        # self.btn_execute = QtWidgets.QPushButton("Click to execute")
        # self.lGrid.addWidget(self.btn_execute, 15, 0, 1, 1 '''

    def func_saveToCityGML(self, newFile: bool) -> None:
        """function to save changes from self.tbl_selBuildings to either the exisitng or a new file"""
        buildingsToChange = gf.getDataFromTable(self)

        if buildingsToChange == None:
            # failed to get values -> abort
            return
        elif buildingsToChange == {}:
            gf.messageBox(self, "Important", "Please make changes before saving.")
            return

        path = gf.saveChangesToCityGML(self, self.inpPath, newFile, buildingsToChange)
        if path != "":
            self.savedChanges = buildingsToChange
            self.fileToSimulate = path
            self.btn_setupSim.setEnabled(True)
            self.btn_setupSim.setToolTip("")

    def tableUpdater(self, item: QtWidgets.QTableWidgetItem) -> None:
        """function, called when something is changed within the table, to update QTableWidgetItem flags"""
        if item.column() == 2:
            if item.text() != "":
                self.tbl_selBuildings.cellWidget(item.row(), 3).setCurrentIndex(-1)
                self.tbl_selBuildings.cellWidget(item.row(), 3).setEnabled(False)
            else:
                self.tbl_selBuildings.cellWidget(item.row(), 3).setEnabled(True)
        elif item.column() == 4:
            if item.text() == "":
                self.tbl_selBuildings.item(item.row(), 5).setFlags(
                    self.tbl_selBuildings.item(item.row(), 5).flags() | QtCore.Qt.ItemIsEditable)

    def func_methodChanged(self) -> None:
        """function to update comboBoxes when method is changed"""
        # yoc_classes default from TypeBuildingElements.json
        yoc_classes = ["0-1918", "1919-1948", "1949-1968", "1969-1978", "1979-1983", "1984-1994", "1995-2015"]

        if self.comB_method.currentText() == "IWU":
            basepath = os.path.join(teaser_path, "../teaser/logic/archetypebuildings/bmvbs")

        elif self.comB_method.currentText() == "tabula_de":
            basepath = os.path.join(teaser_path, "../teaser/logic/archetypebuildings/tabula/de")
            yoc_classes = ["0-1859", "1860-1918", "1919-1948", "1949-1957", "1958-1968", "1969-1978", "1979-1983",
                           "1984-1994", "1995-2001", "2002-2009", "2010-2015", "2016-2100"]

        elif self.comB_method.currentText() == "tabula_dk":
            basepath = os.path.join(teaser_path, "../teaser/logic/archetypebuildings/tabula/dk")
            yoc_classes = ["0-1850", "1851-1931", "1931-1950", "1951-1960", "1961-1972", "1973-1978", "1979-1998",
                           "1999-2006", "2007-2010"]

        elif self.comB_method.currentText() == "urbanrenet":
            basepath = os.path.join(teaser_path, "../teaser/logic/archetypebuildings/urbanrenet")

        for combBox in self.combBoxesYoc:
            combBox.setPlaceholderText("click to select")
            i = combBox.currentIndex()
            toRemove = list(range(1, combBox.count()))
            if i != -1:
                toRemove.remove(i)
            toRemove.reverse()
            for y in toRemove:
                combBox.removeItem(y)
            combBox.addItems(yoc_classes)

        archeTypes = gf.getArchetypes(basepath)
        archeTypes = [self.comB_method.currentText() + "/" + x for x in archeTypes]
        for combBox in self.combBoxesUse:
            combBox.setPlaceholderText("click to select")
            i = combBox.currentIndex()
            toRemove = list(range(1, combBox.count()))
            if i != -1:
                toRemove.remove(i)
            toRemove.reverse()
            for y in toRemove:
                combBox.removeItem(y)
            combBox.addItems(archeTypes)

    def func_setupSim(self) -> None:
        """ first checks if there is info that would have needed to be saved"""

        buildingsToChange = gf.getDataFromTable(self)

        if buildingsToChange == {} and self.savedChanges == {}:
            # got no changes to save -> can continue with original file
            # gf.messageBox(self, "Important set method for buildings", "Please make sure to set a method for every building")
            return
        elif buildingsToChange == None:
            # failed to get values -> abort
            return
        elif buildingsToChange != self.savedChanges:
            gf.messageBox(self, "Important - unsaved changes!",
                          "Please make sure to save your changes before continuing!")
            return
        else:
            # changed values are all saved
            # make sure that method has been set for all buildings
            for key in self.buildingDict:
                if self.buildingDict[key]["selected"]:
                    buildingname = self.buildingDict[key]["buildingname"]
                    if buildingname not in buildingsToChange.keys():
                        gf.messageBox(self, "Error", f"Missing method for {buildingname}")
                        return
                    if "usage" not in buildingsToChange[buildingname]:
                        gf.messageBox(self, "Error", f"Missing method for {buildingname}")
                        return
                    if not self.buildingDict[key]["values"]["YoC"]:
                        if "YoC" not in buildingsToChange[buildingname]:
                            gf.messageBox(self, "Error",
                                          f"Missing year of construction for {buildingname}")
                            return
            fileToSimulate = self.fileToSimulate

        global POSX, POSY
        POSX, POSY = gf.windowPosition(self)
        gf.next_window(self, SetupSimulation(self, self.buildingDict, buildingsToChange, fileToSimulate))

    def func_returnToMain(self) -> None:
        self.hide()
        self.mW.show()


class Eco(QtWidgets.QWidget):
    """ Window for TEASER+eco
    """

    def __init__(self, buildingDict: dict, inpPath: str, mainWindow):
        super(Eco, self).__init__()
        self.buildingDict = buildingDict
        self.inpPath = inpPath
        self.mW = mainWindow
        self.prj = Project(True)
        self.prj.name = "GUI_test"
        self.prj.used_library_calc = "AixLib"
        self.tbl_selBuildings = QtWidgets.QTableWidget()
        self.initUI()

        self.building_groups = []

    def initUI(self):
        global POSX, POSY, WIDTH, HEIGHT, SIZEFACTOR, SIZER
        if SIZER:
            POSX, POSY, WIDTH, HEIGHT, SIZEFACTOR = gf.screenSizer(POSX, POSY, WIDTH, HEIGHT, app)
            SIZER = False

        gf.windowSetup(self, POSX + 10, POSY - 10, WIDTH + 310, HEIGHT + 10, 'Teaser+eco')

        # creating main layout
        self.vbox = QtWidgets.QVBoxLayout(self)
        self.setLayout(self.vbox)

        gf.load_banner(self, r'../pictures/Teco.png', 4)

        self.tbl_selBuildings = QtWidgets.QTableWidget()
        self.tbl_selBuildings.setColumnCount(11)
        self.tbl_selBuildings.setHorizontalHeaderLabels(
            ['Name of building', 'LoD', 'YoC', 'YoC Class', 'No. of floors', 'Floor height[m]', 'Usage Type',
             'Method', 'NLA[m²]', 'Heat Energy Carrier', 'Heat Energy Carrier Elec'])
        self.tbl_selBuildings.setEditTriggers(QtWidgets.QAbstractItemView.DoubleClicked)
        self.vbox.addWidget(self.tbl_selBuildings)

        # Gridbox for lower grid
        self.lGrid = QtWidgets.QGridLayout()

        self.comB_method = QtWidgets.QComboBox()
        self.comB_method.setPlaceholderText("Choose method here")
        self.comB_method.addItems(["IWU", "tabula_de", "tabula_dk", "urbanrenet"])
        self.lGrid.addWidget(self.comB_method, 0, 0, 1, 1)

        ttl = 'Number of selected buildings - ' + str(len(self.buildingDict))
        # building parameters
        self.gB_buildingParameters = QtWidgets.QGroupBox(ttl)

        self.lbl_curBuilding = QtWidgets.QLabel('Current building:')
        self.lGrid.addWidget(self.lbl_curBuilding)

        self.cB_curBuilding = QtWidgets.QComboBox()
        self.cB_curBuilding.addItems(['all (selected) buildings'])
        self.lGrid.addWidget(self.cB_curBuilding)

        self.comB_method.currentTextChanged.connect(self.func_methodChanged)

        self.valueDict = {}

        self.combBoxesYoc = []
        self.combBoxesUse = []

        # for storing path to file
        self.fileToSimulate = ""
        # for checking if recent changes are identical to saved changes
        self.savedChanges = {}

        self.add_building_window = addBuilding(self.prj, self, self.buildingDict)  # needed for setupSimulation

        # add row for select for all button
        self.tbl_selBuildings.insertRow(0)

        # add button for selecting first use for all
        new_item_sfa = QtWidgets.QPushButton("select first use for all")
        new_item_sfa.setToolTip("Assign the first building's usage value for all buildings")
        new_item_sfa.clicked.connect(self.func_select_first_use_for_all)
        widget_sfa = QtWidgets.QWidget()
        layout_sfa = QtWidgets.QHBoxLayout()
        layout_sfa.addWidget(new_item_sfa)
        widget_sfa.setLayout(layout_sfa)
        self.tbl_selBuildings.setCellWidget(0, 6, widget_sfa)

        # add button for selecting first YoC for all
        new_item_sfa = QtWidgets.QPushButton("select first YoC for all")
        new_item_sfa.setToolTip("Assign the first building's YoC value for all buildings")
        new_item_sfa.clicked.connect(self.func_select_first_yoc_for_all)
        widget_sfa = QtWidgets.QWidget()
        layout_sfa = QtWidgets.QHBoxLayout()
        layout_sfa.addWidget(new_item_sfa)
        widget_sfa.setLayout(layout_sfa)
        self.tbl_selBuildings.setCellWidget(0, 3, widget_sfa)

        i = 0
        for key in self.buildingDict:
            # make sure that the building is selected
            if not self.buildingDict[key]["selected"]:
                continue
            else:
                # self.prj.buildings[i] = Building(parent=self.prj, name=self.buildingDict[key]["buildingname"],
                #                            year_of_construction=self.buildingDict[key]["values"]["YoC"])
                # cg.load_gml_lxml(path=self.inpPath, prj=self.prj,method=self.comB_method.currentText())

                i += 1
                rowCount = self.tbl_selBuildings.rowCount()
                self.tbl_selBuildings.insertRow(rowCount)

                #### Column 0 #####
                newItem = QtWidgets.QTableWidgetItem(self.buildingDict[key]["buildingname"])
                newItem.setFlags(newItem.flags() & ~QtCore.Qt.ItemIsEditable)
                newItem.setToolTip(self.buildingDict[key]["buildingname"])
                self.tbl_selBuildings.setItem(rowCount, 0, newItem)

                #### Column 1 ####
                newItem = QtWidgets.QTableWidgetItem(str(self.buildingDict[key]["values"]["LoD"]))
                newItem.setFlags(newItem.flags() & ~QtCore.Qt.ItemIsEditable)
                self.tbl_selBuildings.setItem(rowCount, 1, newItem)

                #### Column 2 ####
                newItem = QtWidgets.QTableWidgetItem(str(self.buildingDict[key]["values"]["YoC"]))
                self.tbl_selBuildings.setItem(rowCount, 2, newItem)

                #### Column 3 ####
                self.combBoxesYoc.append(QtWidgets.QComboBox(parent=self.tbl_selBuildings))
                self.combBoxesYoc[-1].setPlaceholderText("select")
                self.tbl_selBuildings.setCellWidget(rowCount, 3, self.combBoxesYoc[-1])
                self.tbl_selBuildings.cellWidget(rowCount, 3).setEnabled(False)
                # make changes to editabiltiy of the table items
                if self.buildingDict[key]["values"]["YoC"] != "":
                    self.combBoxesYoc[-1].setToolTip(
                        "YoC is given, YoC Class set automatically according to time frames from TABULA typology")

                else:
                    self.combBoxesYoc[-1].setToolTip("first choose method down below")

                #### Column 4 ####
                # Storeys Above Ground
                newItem = QtWidgets.QTableWidgetItem(str(self.buildingDict[key]["values"]["SAG"]))
                self.tbl_selBuildings.setItem(rowCount, 4, newItem)

                #### Column 5 ####
                newItem = QtWidgets.QTableWidgetItem(str(self.buildingDict[key]["values"]["storeyHeight"]))
                self.tbl_selBuildings.setItem(rowCount, 5, newItem)
                # ToDo: Floor height priority: GML tag -> geometry -> fallback

                # make changes to editabiltiy of the table items
                if self.buildingDict[key]["values"]["SAG"] != "" or self.buildingDict[key]["values"][
                    "storeyHeight"] != "":
                    self.tbl_selBuildings.item(rowCount, 5).setFlags(
                        self.tbl_selBuildings.item(rowCount, 5).flags() & ~QtCore.Qt.ItemIsEditable)
                    self.tbl_selBuildings.item(rowCount, 4).setFlags(
                        self.tbl_selBuildings.item(rowCount, 4).flags() & ~QtCore.Qt.ItemIsEditable)

                #### Column 6 ####
                self.combBoxesUse.append(QtWidgets.QComboBox(parent=self.tbl_selBuildings))
                self.combBoxesUse[-1].setPlaceholderText("select")
                self.combBoxesUse[-1].setToolTip("first choose method down below")
                self.tbl_selBuildings.setCellWidget(rowCount, 6, self.combBoxesUse[-1])
                self.tbl_selBuildings.cellWidget(rowCount, 6).setEnabled(False)

                if self.buildingDict[key]["values"]["usage"] != "":
                    self.combBoxesUse[-1].setToolTip("Usage is given")
                else:
                    self.combBoxesUse[-1].setToolTip("first choose method down below")

                self.valueDict[self.buildingDict[key]["buildingname"]] = self.buildingDict[key]["values"]

                #### Column 7 ####
                newItem = QtWidgets.QTableWidgetItem(str(self.comB_method.currentText()))
                self.tbl_selBuildings.setItem(rowCount, 7, newItem)

                #### Column 8 ####
                newItem = QtWidgets.QTableWidgetItem(str(self.buildingDict[key]["values"]["area"]))
                self.tbl_selBuildings.setItem(rowCount, 8, newItem)

                #### Column 9 ####
                newItem = QtWidgets.QTableWidgetItem("")
                self.tbl_selBuildings.setItem(rowCount, 9, newItem)

                #### Column 10 ####
                newItem = QtWidgets.QTableWidgetItem("")
                self.tbl_selBuildings.setItem(rowCount, 10, newItem)

        self.tbl_selBuildings.resizeRowsToContents()
        gf.resize_header(self)

        self.tbl_selBuildings.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

        self.bGrid = QtWidgets.QGridLayout()
        self.bGrid.addWidget(self.tbl_selBuildings, 1, 0, 1, 6)

        self.vbox.addLayout(self.bGrid)

        self.btn_add_bldg = QtWidgets.QPushButton('Add building or utility')
        self.btn_add_bldg.clicked.connect(self.add_building)
        self.lGrid.addWidget(self.btn_add_bldg, 0, 1, 1, 1)

        self.btn_saveToCityGML = QtWidgets.QPushButton("Save to CityGML file")
        self.btn_saveToCityGML.clicked.connect(lambda: self.func_saveToCityGML(False))
        self.lGrid.addWidget(self.btn_saveToCityGML, 2, 1, 1, 1)

        self.btn_remove_entry = QtWidgets.QPushButton('Remove selected entry')
        self.btn_remove_entry.clicked.connect(self.func_remove_entry)
        self.btn_remove_entry.setToolTip("Press on the number of the row you want to delete")
        self.lGrid.addWidget(self.btn_remove_entry, 2, 2, 1, 1)

        self.btn_saveToNewCityGML = QtWidgets.QPushButton("Save to new CityGML file")
        self.btn_saveToNewCityGML.clicked.connect(lambda: self.func_saveToCityGML(True))
        self.lGrid.addWidget(self.btn_saveToNewCityGML, 2, 0, 1, 1)

        self.btn_setupSim = QtWidgets.QPushButton("Setup simulation")
        self.btn_setupSim.clicked.connect(self.func_setupSim)
        self.btn_setupSim.setToolTip("Please save changes first")
        self.lGrid.addWidget(self.btn_setupSim, 1, 0, 1, 1)

        self.btn_back = QtWidgets.QPushButton('Main Window')
        self.btn_back.clicked.connect(self.func_returnToMain)
        self.lGrid.addWidget(self.btn_back, 1, 2, 1, 1)

        self.btn_about = QtWidgets.QPushButton('About')
        self.btn_about.clicked.connect(self.func_about)
        self.lGrid.addWidget(self.btn_about, 0, 2, 1, 1)

        self.btn_reset = QtWidgets.QPushButton('Reset')
        self.btn_reset.clicked.connect(self.func_reset)
        self.lGrid.addWidget(self.btn_reset, 1, 1, 1, 1)

        self.vbox.addLayout(self.lGrid)

        # self.tbl_selBuildings.itemChanged.connect(self.tableUpdater)

    def func_saveToCityGML(self, newFile: bool) -> None:
        """function to save changes from self.tbl_selBuildings to either the exisitng or a new file"""
        buildingsToChange = gf.getDataFromTable(self)

        if buildingsToChange == None:
            # failed to get values -> abort
            return
        elif buildingsToChange == {}:
            gf.messageBox(self, "Important", "Please make changes before saving.")
            return

        path = gf.saveChangesToCityGML(self, self.inpPath, newFile, buildingsToChange)
        if path != "":
            self.savedChanges = buildingsToChange
            self.fileToSimulate = path
            self.btn_setupSim.setEnabled(True)
            self.btn_setupSim.setToolTip("")

    def tableUpdater(self, item: QtWidgets.QTableWidgetItem) -> None:
        """function, called when something is changed within the table, to update QTableWidgetItem flags"""
        if item.column() == 2:
            if item.text() != "":
                self.tbl_selBuildings.cellWidget(item.row(), 3).setCurrentIndex(-1)
                self.tbl_selBuildings.cellWidget(item.row(), 3).setEnabled(False)
            else:
                self.tbl_selBuildings.cellWidget(item.row(), 3).setEnabled(True)
        elif item.column() == 4:
            if item.text() == "":
                self.tbl_selBuildings.item(item.row(), 5).setFlags(
                    self.tbl_selBuildings.item(item.row(), 5).flags() | QtCore.Qt.ItemIsEditable)

        gf.resize_header(self)

    def func_methodChanged(self) -> None:
        """function to update comboBoxes when method is changed"""
        # yoc_classes default from TypeBuildingElements.json
        yoc_classes = ["0-1918", "1919-1948", "1949-1968", "1969-1978", "1979-1983", "1984-1994", "1995-2015"]

        basepath = ""

        if self.comB_method.currentText() == "IWU":
            basepath = os.path.join(teaser_path, "../teaser/logic/archetypebuildings/bmvbs")

        elif self.comB_method.currentText() == "tabula_de":
            basepath = os.path.join(teaser_path, "../teaser/logic/archetypebuildings/tabula/de")
            yoc_classes = ["0-1859", "1860-1918", "1919-1948", "1949-1957", "1958-1968", "1969-1978", "1979-1983",
                           "1984-1994", "1995-2001", "2002-2009", "2010-2015", "2016-2100"]

        elif self.comB_method.currentText() == "tabula_dk":
            basepath = os.path.join(teaser_path, "../teaser/logic/archetypebuildings/tabula/dk")
            yoc_classes = ["0-1850", "1851-1931", "1931-1950", "1951-1960", "1961-1972", "1973-1978", "1979-1998",
                           "1999-2006", "2007-2010"]

        elif self.comB_method.currentText() == "urbanrenet":
            basepath = os.path.join(teaser_path, "../teaser/logic/archetypebuildings/urbanrenet")

        archeTypes = gf.getArchetypes(basepath)
        archeTypes = [self.comB_method.currentText() + "/" + x for x in archeTypes]

        for i in range(1, self.tbl_selBuildings.rowCount()):
            self.tbl_selBuildings.item(i, 7).setText(self.comB_method.currentText())

        for i in range(len([0 for key in self.buildingDict if self.buildingDict[key]["selected"]])):

            if self.buildingDict[i]["values"]["YoC"] == "":
                self.combBoxesYoc[i].setEnabled(True)
                self.combBoxesYoc[i].setToolTip("choose YoC Class from time frames according to TABULA typology")
                self.combBoxesYoc[i].addItems(yoc_classes)

            else:
                self.combBoxesYoc[i].setEnabled(False)
                self.combBoxesYoc[i].setToolTip("YoC Class is already set")
                self.combBoxesYoc[i].setPlaceholderText(self.buildingDict[i]["values"]["YoC"])

            if self.buildingDict[i]["values"]["usage"] == "":
                self.combBoxesUse[i].setEnabled(True)
                self.combBoxesUse[i].setPlaceholderText("select")
                self.combBoxesUse[i].setToolTip("select Usage according to the chosen method")
                self.combBoxesUse[i].addItems(archeTypes)
            else:
                self.combBoxesUse[i].setEnabled(False)
                self.combBoxesUse[i].setToolTip("Usage is already set")
                self.combBoxesUse[i].setPlaceholderText(self.buildingDict[i]["values"]["usage"])

        gf.resize_header(self)

    def func_setupSim(self) -> None:
        """ first checks if there is info that would have needed to be saved"""

        buildingsToChange = gf.getDataFromTable(self)

        if buildingsToChange == {} and self.savedChanges == {}:
            # got no changes to save -> can continue with original file
            gf.messageBox(self, "Important set method for buildings",
                          "Please make sure to set a method for every building")
            return
        if buildingsToChange == None:
            # failed to get values -> abort
            return
        elif buildingsToChange != self.savedChanges:
            gf.messageBox(self, "Important - unsaved changes!",
                          "Please make sure to save your changes before continuing!")
            return
        else:
            # changed values are all saved
            # make sure that method has been set for all buildings
            for key in self.buildingDict:
                if self.buildingDict[key]["selected"]:
                    buildingname = self.buildingDict[key]["buildingname"]

                    if buildingname not in buildingsToChange.keys():
                        gf.messageBox(self, "Error", f"Missing method for {buildingname}")
                        return
                    '''if "usage" not in buildingsToChange[buildingname]:
                        gf.messageBox(self, "Error", f"Missing method for {buildingname}")
                        return
                    '''
                    if not self.buildingDict[key]["values"]["YoC"]:
                        if "YoC" not in buildingsToChange[buildingname]:
                            gf.messageBox(self, "Error",
                                          f"Missing year of construction for {buildingname}")
                            return
            fileToSimulate = self.fileToSimulate

        global POSX, POSY
        POSX, POSY = gf.windowPosition(self)
        gf.next_window(self, SetupSimulation(self, self.buildingDict, buildingsToChange, fileToSimulate))

    def func_returnToMain(self) -> None:
        self.hide()
        self.mW.show()

    def add_building(self):
        """Function to open the addBuilding-Window
        """

        global POSX, POSY
        POSX, POSY = gf.windowPosition(self)
        gf.next_window(self, self.add_building_window, False)

    def func_about(self) -> None:
        global POSX, POSY
        POSX, POSY = gf.windowPosition(self)
        gf.next_window(self, about("about_teco.txt"), False)

    def func_reset(self) -> None:
        global POSX, POSY
        choice = QtWidgets.QMessageBox.question(self, "Warning", "Are you sure you want to reset this window?")

        if choice == QtWidgets.QMessageBox.Yes:
            POSX, POSY = gf.windowPosition(self)
            gf.next_window(self, Eco(self.buildingDict, self.inpPath, self.mW), close=True)

    def func_select_first_use_for_all(self):
        """Function to choose value of the dropdown menus of Use the same as the first drop-down menu"""
        i = 0
        for key in self.buildingDict:
            if self.buildingDict[key]["selected"]:
                combBox = self.combBoxesUse[i]
                combBox.setCurrentIndex(self.combBoxesUse[0].currentIndex())
                i += 1

    def func_select_first_yoc_for_all(self):
        """Function to choose value of the dropdown menus of YOC the same as the first drop-down menu"""
        for key in self.buildingDict:
            if self.buildingDict[key]["selected"]:
                combBox = self.combBoxesYoc[key]
                combBox.setCurrentIndex(self.combBoxesYoc[0].currentIndex())

    def func_remove_entry(self):
        """Function to remove a building from the list
        """
        selected = self.tbl_selBuildings.selectionModel().selectedRows()
        if selected:
            for index in sorted(selected):
                self.tbl_selBuildings.removeRow(index.row())
        else:
            gf.messageBox(self, "Error", "Please select a row to remove")


class SetupSimulation(QtWidgets.QWidget):
    """Window to setup simulation"""

    def __init__(self, parent: object, buildingDict: dict, buildingsToChange: dict, fileToSimulate: str):
        super(SetupSimulation, self).__init__()
        self.parent = parent
        self.buildingDict = buildingDict
        self.prj = parent.prj
        self.buildingsToChange = buildingsToChange
        self.fileToSimulate = fileToSimulate
        self.simulation_program = "Dymola"
        self.initUI()

    def initUI(self):
        global POSX, POSY, WIDTH, HEIGHT, SIZEFACTOR, SIZER
        gf.windowSetup(self, POSX, POSY, WIDTH - 200, HEIGHT - 100, 'TEASER+ - Setup simulation')

        self.vbox = QtWidgets.QVBoxLayout(self)
        self.setLayout(self.vbox)

        self.gB_categories = QtWidgets.QGroupBox("Select categories for impact assessment (LCIA)")
        self.gB_categories.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.vbox.addWidget(self.gB_categories)

        self.uGrid = QtWidgets.QGridLayout()
        self.gB_categories.setMaximumWidth(700)
        self.gB_categories.setLayout(self.uGrid)

        checkbox_labels = [
            "cru", "mfr", "mer", "eee", "eet", "gwp", "odp", "pocp",
            "ap", "ep", "adpe", "adpf", "pere", "pert", "penre", "penrm",
            "penrt", "sm", "rsf", "nrsf", "fw", "hwd", "nhwd", "rwd"
        ]

        self.checkboxes = [QtWidgets.QCheckBox("All")]
        for label in checkbox_labels:
            self.checkboxes.append(QtWidgets.QCheckBox(label))

        for i, checkbox in enumerate(self.checkboxes):
            self.uGrid.addWidget(checkbox, i // 9, i % 9, 1, 1)

        self.mGrid = QtWidgets.QGridLayout()
        self.vbox.addLayout(self.mGrid)

        self.btn_heatloadPath = QtWidgets.QPushButton("Select TEASER Heatload output path")
        self.btn_heatloadPath.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.btn_heatloadPath.setMaximumWidth(200)
        self.mGrid.addWidget(self.btn_heatloadPath, 0, 0, 1, 1)

        self.txtB_heatloadPath = QtWidgets.QLineEdit("")
        self.txtB_heatloadPath.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.txtB_heatloadPath.setPlaceholderText("Path to heatload file")
        self.txtB_heatloadPath.setEnabled(False)
        self.mGrid.addWidget(self.txtB_heatloadPath, 0, 1, 1, 4)

        self.btn_tecoLCApath = QtWidgets.QPushButton("Select Teco LCA .CSV output path")
        self.btn_tecoLCApath.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.btn_tecoLCApath.setMaximumWidth(200)
        self.mGrid.addWidget(self.btn_tecoLCApath, 1, 0, 1, 1)

        self.txtB_tecoLCApath = QtWidgets.QLineEdit("")
        self.txtB_tecoLCApath.setPlaceholderText("Path to .csv output path")
        self.txtB_tecoLCApath.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.txtB_tecoLCApath.setEnabled(False)
        self.mGrid.addWidget(self.txtB_tecoLCApath, 1, 1, 1, 4)

        self.lbl_weatherFile = QtWidgets.QLabel("Select weather file")
        self.lbl_weatherFile.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.lbl_weatherFile.setMaximumWidth(200)
        self.mGrid.addWidget(self.lbl_weatherFile, 2, 0, 1, 1)

        self.comB_weatherFile = QtWidgets.QComboBox()
        self.comB_weatherFile.setPlaceholderText("Click to select weather file")
        self.comB_weatherFile.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.mGrid.addWidget(self.comB_weatherFile, 2, 1, 1, 4)

        weatherpath = os.path.join(teaser_path, "../teaser", "data", "input", "inputdata", "weatherdata")

        for candidate in os.listdir(weatherpath):
            if os.path.isfile(os.path.join(weatherpath, candidate)) and candidate.endswith(".mos"):
                self.comB_weatherFile.addItem(candidate)

        self.comB_weatherFile.setCurrentIndex(1)

        self.btn_expPath = QtWidgets.QPushButton("Select export path")
        self.btn_expPath.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.btn_expPath.setMaximumWidth(200)
        self.mGrid.addWidget(self.btn_expPath, 3, 0, 1, 1)

        self.txtB_expPath = QtWidgets.QLineEdit("")
        self.txtB_expPath.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.txtB_expPath.setEnabled(False)
        self.txtB_expPath.setPlaceholderText("Path to simulation results")
        self.mGrid.addWidget(self.txtB_expPath, 3, 1, 1, 4)

        self.lGrid = QtWidgets.QGridLayout()
        self.vbox.addLayout(self.lGrid)
        self.lGrid.setColumnMinimumWidth(1, 20)

        self.lbl_epd_electrical = QtWidgets.QLabel("Choose EPD for electrical energy")
        self.lbl_epd_electrical.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.lbl_epd_electrical.setMaximumWidth(200)
        self.lGrid.addWidget(self.lbl_epd_electrical, 0, 0, 1, 1)

        # self.lbl_space = QtWidgets.QLabel("      ")
        # self.lGrid.addWidget(self.lbl_space, 0, 1, 1, 1)

        self.lbl_epdCarriers = QtWidgets.QLabel("Enter EPDs and primary energy factors for heat energy carriers")
        self.lbl_epdCarriers.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.lbl_epdCarriers.setMaximumWidth(550)
        self.lGrid.addWidget(self.lbl_epdCarriers, 0, 2, 1, 4)

        self.button_add_carrier = QtWidgets.QPushButton("Add carrier")
        self.button_add_carrier.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.button_add_carrier.setMaximumWidth(100)
        self.button_add_carrier.clicked.connect(self.add_carrier)
        self.lGrid.addWidget(self.button_add_carrier, 0, 5, 1, 1)

        self.comB_epd_electrical = QtWidgets.QComboBox()
        self.comB_epd_electrical.setPlaceholderText("Choose EPD for electrical energy")
        epd_electrical_items = [
            "Residual electricity mix 2030",
            "Residual electricity mix 2040",
            "Residual electricity mix 2050",
            "Electricity grid mix scenario 2030",
            "Electricity grid mix scenario 2040",
            "Electricity grid mix scenario 2050",
            "Electricity mix scenario 2030",
            "Electricity mix scenario 2040",
            "Electricity mix scenario 2050"
        ]
        self.comB_epd_electrical.addItems(epd_electrical_items)
        self.comB_epd_electrical.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.comB_epd_electrical.setMaximumWidth(200)
        self.lGrid.addWidget(self.comB_epd_electrical, 1, 0, 1, 1)

        heat_energy_items = [
            "District heating from waste",
            "District heating from biogas",
            "District heating from biomass (solid)",
            "District heating from lignite",
            "District heating from natural gas",
            "District heating from light fuel oil",
            "District heating from hard coal",
            "District heating mix Germany",
            "Thermal energy from natural gas",
            "Thermal energy from light fuel oil",
            "Light fuel oil",
            "Heavy fuel oil",
            "Liquefied petroleum gas (LPG)",
            "Biogas (1 kg)",
            "Wood pellets (6,2% moisture / 5,8% H2O content)",
            "Vegetable oil fuel (rapeseed, 1 kg)"
        ]
        self.pef_dict = {
            "District heating from waste":1.1,
            "District heating from biogas":1.1,
            "District heating from biomass (solid)":1.1,
            "District heating from lignite":1.2,
            "District heating from natural gas":1.1,
            "District heating from light fuel oil":1.1,
            "District heating from hard coal":1.1,
            "District heating mix Germany":2.8,
            "Thermal energy from natural gas":1.1,
            "Thermal energy from light fuel oil":1.1,
            "Light fuel oil":1.1,
            "Heavy fuel oil":1.1,
            "Liquefied petroleum gas (LPG)":1.1,
            "Biogas (1 kg)":1.1,
            "Wood pellets (6,2% moisture / 5,8% H2O content)":0.2,
            "Vegetable oil fuel (rapeseed, 1 kg)":1.1
        }
        ###### source: BBSR

        self.lbl_carrier1 = QtWidgets.QLabel("Carrier1")
        self.lbl_carrier1.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.lbl_carrier1.setMaximumWidth(70)
        self.lGrid.addWidget(self.lbl_carrier1, 1, 2, 1, 1)

        self.comB_carrier1 = QtWidgets.QComboBox()
        self.comB_carrier1.setPlaceholderText("heat energy carrier EPD for carrier1")
        self.comB_carrier1.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.comB_carrier1.setMaximumWidth(250)
        self.comB_carrier1.addItems(heat_energy_items)
        self.lGrid.addWidget(self.comB_carrier1, 1, 3, 1, 2)

        self.txtB_carrier1PEF = QtWidgets.QLineEdit("")
        self.txtB_carrier1PEF.setPlaceholderText("PEF")
        self.txtB_carrier1PEF.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.txtB_carrier1PEF.setMaximumWidth(30)
        self.lGrid.addWidget(self.txtB_carrier1PEF, 1, 5, 1, 1)  # ToDo: set range

        self.lbl_carrier2 = QtWidgets.QLabel("Carrier2")
        self.lbl_carrier2.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.lbl_carrier2.setMaximumWidth(70)
        self.lGrid.addWidget(self.lbl_carrier2, 2, 2, 1, 1)

        self.comB_carrier2 = QtWidgets.QComboBox()
        self.comB_carrier2.setPlaceholderText("heat energy carrier EPD for carrier2")
        self.comB_carrier2.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.comB_carrier2.setMaximumWidth(250)
        self.comB_carrier2.addItems(heat_energy_items)
        self.lGrid.addWidget(self.comB_carrier2, 2, 3, 1, 2)

        self.txtB_carrier2PEF = QtWidgets.QLineEdit("")
        self.txtB_carrier2PEF.setPlaceholderText("PEF")  # ToDo: set range
        self.txtB_carrier2PEF.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.txtB_carrier2PEF.setMaximumWidth(30)
        self.lGrid.addWidget(self.txtB_carrier2PEF, 2, 5, 1, 1)

        self.lbl_carrier3 = QtWidgets.QLabel("Carrier3")
        self.lGrid.addWidget(self.lbl_carrier3, 3, 2, 1, 1)

        self.comB_carrier3 = QtWidgets.QComboBox()
        self.comB_carrier3.setPlaceholderText("heat energy carrier EPD for carrier3")
        self.comB_carrier3.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.comB_carrier3.setMaximumWidth(250)
        self.comB_carrier3.addItems(heat_energy_items)
        self.lGrid.addWidget(self.comB_carrier3, 3, 3, 1, 2)

        self.heat_carrier_counter = 3

        self.txtB_carrier3PEF = QtWidgets.QLineEdit("")
        self.txtB_carrier3PEF.setPlaceholderText("PEF")  # ToDo: set range
        self.txtB_carrier3PEF.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.txtB_carrier3PEF.setMaximumWidth(30)
        self.lGrid.addWidget(self.txtB_carrier3PEF, 3, 5, 1, 1)

        self.txtB_temporalBoundary = QtWidgets.QLabel("Enter temporal boundary")
        self.txtB_temporalBoundary.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.txtB_temporalBoundary.setMaximumWidth(170)
        self.lGrid.addWidget(self.txtB_temporalBoundary, 2, 0, 1, 1)

        self.lbl_temporalBoundary = QtWidgets.QLineEdit("50")
        self.lbl_temporalBoundary.setPlaceholderText("Time in years")
        self.lbl_temporalBoundary.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.lbl_temporalBoundary.setToolTip("Time in years")
        self.lbl_temporalBoundary.setMaximumWidth(30)
        self.lGrid.addWidget(self.lbl_temporalBoundary, 2, 1, 1, 1)

        '''self.lbl_eff = QtWidgets.QLabel('Energy conversion efficiency')
        self.lbl_eff.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.lbl_eff.setMaximumWidth(150)
        self.lGrid.addWidget(self.lbl_eff, 3, 0, 1, 1)

        self.txtB_eff = QtWidgets.QLineEdit('1.525')
        self.txtB_eff.setMaximumWidth(100)
        self.lGrid.addWidget(self.txtB_eff, 3, 1, 1, 1)'''

        self.dGrid = QtWidgets.QGridLayout()

        self.btn_start_sim = QtWidgets.QPushButton('Start simulation')
        self.btn_start_sim.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.dGrid.addWidget(self.btn_start_sim, 0, 0, 1, 1)

        # self.btn_start_dym = QtWidgets.QPushButton('Start simulation with dymola')
        # self.dGrid.addWidget(self.btn_start_dym, 0, 1, 1, 1)

        self.btn_return = QtWidgets.QPushButton("Return to Teco LCA window")
        self.btn_return.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.dGrid.addWidget(self.btn_return, 0, 1, 1, 1)

        self.vbox.addLayout(self.dGrid)

        self.comB_carrier1.currentTextChanged.connect(self.set_pef)
        self.comB_carrier2.currentTextChanged.connect(self.set_pef)
        self.comB_carrier3.currentTextChanged.connect(self.set_pef)
        self.btn_heatloadPath.clicked.connect(self.func_selectDir_heatload_path)
        self.btn_tecoLCApath.clicked.connect(self.func_selectDir_csv)
        self.btn_start_sim.clicked.connect(self.func_choose_program)
        # self.btn_start_dym.clicked.connect(self.func_startSimulation)
        self.btn_return.clicked.connect(self.func_return)
        self.btn_expPath.clicked.connect(self.func_selectDir_out)
        self.btn_expPath.clicked.connect(self.func_selectDir_out)

    '''def func_expPath(self) -> None:
        """select export path"""
        path = gf.select_folder(self, self.txtB_expPath, "Select export folder")
        if path:
            self.expPath = path
        else:
            pass'''

    def set_pef(self):
        sender = self.sender()

        for i in range(1, self.heat_carrier_counter + 1):
            if sender == self.__getattribute__("comB_carrier" + str(i)):
                text = sender.currentText()
                self.__getattribute__(f"txtB_carrier{i}PEF").setText(str(self.pef_dict[text]))


    def func_choose_program(self):

        global POSX, POSY
        POSX, POSY = gf.windowPosition(self)
        gf.next_window(self, SimulationProgram(self), False)

    def func_startSimulation(self) -> None:
        """starts simulation proccess"""

        bp_counter = {}

        bld_IWU = []
        bld_tabula_de = []
        bld_tabula_dk = []
        bld_urbanrenet = []
        bld_undefined = []
        # print(self.buildingDict)
        if self.simulation_program == "OpenModelica":
            print("OpenModelica")
            # ToDo add OpenModelica
        for key in self.buildingDict:
            if self.buildingDict[key]["selected"]:
                buildingname = self.buildingDict[key]["buildingname"]
                if "/" in buildingname:
                    parent = buildingname.split("/")[0]
                    if parent not in bp_counter:
                        bp_counter[parent] = 1
                    else:
                        bp_counter[parent] -= - 1
                    buildingname_teasered = parent + "/bp" + str(bp_counter[parent])
                else:
                    buildingname_teasered = buildingname
                if buildingname in self.buildingsToChange.keys():
                    if "usage" in self.buildingsToChange[buildingname]:
                        if self.buildingsToChange[buildingname]["usage"].startswith("IWU"):
                            bld_IWU.append(buildingname_teasered)
                        elif self.buildingsToChange[buildingname]["usage"].startswith("tabula_de"):
                            bld_tabula_de.append(buildingname_teasered)
                        elif self.buildingsToChange[buildingname]["usage"].startswith("tabula_dk"):
                            bld_tabula_dk.append(buildingname_teasered)
                        elif self.buildingsToChange[buildingname]["usage"].startswith("urbanrenet"):
                            bld_urbanrenet.append(buildingname_teasered)
                        else:
                            print(f"Error getting the right method for {buildingname}")
                            bld_undefined.append(buildingname_teasered)
                    else:
                        bld_undefined.append(buildingname_teasered)
                else:
                    bld_undefined.append(buildingname_teasered)

        weatherfile = self.comB_weatherFile.currentText()

        print(f"simulate file {self.fileToSimulate}")

        print(f"IWU for these buildings: {bld_IWU}")
        print(f"tabula_de for these buildings: {bld_tabula_de}")
        print(f"tabula_dk for these buildings: {bld_tabula_dk}")
        print(f"urbanrenet for these buildings: {bld_urbanrenet}")
        print(f"undefined method: {bld_undefined}")
        print(f"using the weatherfile {weatherfile}")

        print(f"and exporting to {self.txtB_expPath}")

        # create project
        prj_lca = Project(load_data=True)
        prj_lca.name = "GUI_Teco_LCA"
        prj_lca.use_b4 = True

        usage_dict = {"singlefamilyhouse": "sfh", "terracedhouse": "th", "multifamilyhouse": "mfh",
                      "apartmentblock": "ap", 'singlefamilydwelling': "sfd", "office": "office"}

        buildingIDs = []

        for key in range(self.parent.tbl_selBuildings.rowCount() - 1):
            buildingIDs.append(self.parent.tbl_selBuildings.item(key + 1, 0).text())

        # and self.led_elec_lca != "" and self.led_heat_lca != "" time
        if self.txtB_expPath != "" and self.txtB_tecoLCApath != "" and self.lbl_temporalBoundary != "" and self.txtB_heatloadPath != "" \
                 and self.comB_epd_electrical.currentIndex() != -1 and self.comB_weatherFile.currentIndex() != -1:

            # gml_copy_list = cg.choose_gml_lxml(self.fileToSimulate, buildingIDs)
            # cg.load_gml_lxml(self.fileToSimulate, prj, method="To-Do", chosen_gmls=gml_copy_list)

            archetypes_list = []

            # add infos from setup simulation window (heat energy carrier,..) to teco window:

            heat_energy_all = ""

            for i in range(1,self.heat_carrier_counter+1):
                if self.__getattribute__("comB_carrier" + str(i)).currentIndex() != -1:
                    heat_energy_all += self.__getattribute__("comB_carrier" + str(i)).currentText() + "\n"

            heat_energy_all = heat_energy_all[:-1]

            for j in range(1,self.parent.tbl_selBuildings.rowCount()):
                new_item = QtWidgets.QTableWidgetItem(self.comB_epd_electrical.currentText())
                self.parent.tbl_selBuildings.setItem(j,10,new_item)
                new_item = QtWidgets.QTableWidgetItem(heat_energy_all)
                self.parent.tbl_selBuildings.setItem(j,9,new_item)

            self.parent.tbl_selBuildings.resizeRowsToContents()

            for i in range(1,self.parent.tbl_selBuildings.rowCount()):
                try:
                    if i <= len(self.parent.combBoxesUse):
                        # check yoC isnt more than 1978 if usage is tabula_de/appartmentblock
                        if self.parent.combBoxesUse[i-1].currentText().split('/')[1] == "apartmentblock":
                            if int(self.parent.combBoxesYoc[i-1].currentText()) > 1978:
                                raise("Error: Apartment block archetype does not support YoC after 1978")
                                continue

                        archetypes_list.append(usage_dict[self.parent.combBoxesUse[i-1].currentText().split('/')[1]])
                except IndexError:
                    gf.messageBox(self, "Error", "Error: Please select a usage for each building")
                    return

            #
            yoc_list = []
            for i in range(1, self.parent.tbl_selBuildings.rowCount()):
                if self.parent.tbl_selBuildings.item(i, 2).text() != None:
                    yoc_list.append(self.parent.tbl_selBuildings.item(i, 2).text())
                else:
                    yoc_list.append(self.parent.combBoxesUse[i-1].currentText())

            # prj_lca.load_citygml(method= self.parent.comB_method.currentText(),gml_bldg_ids=buildingIDs, path=self.fileToSimulate, archetypes=archetypes_list)
            chosen_gmls = citygml_in.choose_gml_lxml(self.fileToSimulate, bldg_ids=buildingIDs)
            gml_copy, boundary_box = citygml_in.load_gml_lxml(self.fileToSimulate, prj_lca,
                                                              method=self.parent.comB_method.currentText(),
                                                              chosen_gmls=chosen_gmls,
                                                              archetypes=archetypes_list, yoc_list=yoc_list)

            if hasattr(self.parent.add_building_window, 'add_building_data'):
                for bldg in self.parent.add_building_window.add_building_data:
                    prj_lca.add_residential(method=self.parent.add_building_window.add_building_data[bldg]["method"],
                                            usage=self.parent.add_building_window.add_building_data[bldg]["usage"],
                                            name=bldg,
                                            year_of_construction=
                                            self.parent.add_building_window.add_building_data[bldg][
                                                "year_of_construction"],
                                            number_of_floors=self.parent.add_building_window.add_building_data[bldg][
                                                "number_of_floors"],
                                            height_of_floors=self.parent.add_building_window.add_building_data[bldg][
                                                "height_of_floors"],
                                            net_leased_area=self.parent.add_building_window.add_building_data[bldg][
                                                "net_leased_area"])
                for i in range(self.parent.add_building_window.tbl_lca.rowCount()):
                    building_no = int(self.parent.add_building_window.tbl_lca.item(i, 2).text())
                    prj_lca.buildings[building_no - 1].add_lca_data_template(
                        self.parent.add_building_window.tbl_lca.item(i, 0).text(),
                        float(self.parent.add_building_window.tbl_lca.item(i,
                                                                           1).text()))

            # ToDo: remove unnecessary prj variable in the other classes

            prj_lca.number_of_elements_calc = 2  # oder doch = 4?
            prj_lca.calc_all_buildings()
            # prj_lca.export_parameters_txt()
            prj_lca.weather_file_path = utilities.get_full_path(
                os.path.join("data", "input", "inputdata", "weatherdata", weatherfile))

            # prj_lca.used_library_calc = "AixLib"
            prj_lca.export_aixlib()

            # prj_lca.save_citygml(file_name="C:\\Users\\tayeb\\TEASEROutput\\test.gml")

            prj_lca.period_lca_scenario = int(self.lbl_temporalBoundary.text() or 50)

            if self.txtB_expPath.text() != "":
                path1 = self.txtB_expPath.text().replace("/", "\\")
            else:
                path1 = utilities.get_default_path()

            if self.txtB_tecoLCApath.text() != "":
                path2 = self.txtB_tecoLCApath.text().replace("/", "\\")
            else:
                path2 = os.path.join(output_path, "results.csv")

            sim.simulate(path=path1, prj=prj_lca, loading_time=3600, result_path=path2)



            lca_data_elec = En15804LcaData()
            lca_data_elec.name = self.comB_epd_electrical.currentText()
            self.load_en15804_lca_data_gui("electricity", lca_data_elec)

            heat_energy_list = heat_energy_all.split("\n")
            lca_data_heat_list = []
            for heat_energy in heat_energy_list:
                lca_data_heat = En15804LcaData()
                lca_data_heat.name = heat_energy
                lca_data_heat_list.append(lca_data_heat)
                self.load_en15804_lca_data_gui("heating", lca_data_heat)

            for building in prj_lca.buildings:
                building.calc_lca_data(False, int(self.lbl_temporalBoundary.text()))
                building.add_lca_data_elec(lca_data_elec)
                for i,lca_data_heat in enumerate(lca_data_heat_list):
                    pef = self.__getattribute__(f"txtB_carrier{i+1}PEF").text()
                    if pef != "":
                        building.add_lca_data_heating(float(pef), lca_data_heat) # is this correct?
                    else:
                        building.add_lca_data_heating(1, lca_data_heat)


            global POSX, POSY
            POSX, POSY = gf.windowPosition(self)
            gf.next_window(self, result(prj_lca, self.parent, self.checkboxes), False)

            return

        else:
            gf.messageBox(self, "Error", "Please select all necessary data before continuing")
            return

    def func_return(self) -> None:
        self.hide()
        self.parent.show()

    def func_selectDir_out(self):
        """function to select the directory"""
        dirpath = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory")
        self.txtB_expPath.setText(dirpath)

    def func_selectDir_csv(self):
        """function to select the result.csv path"""
        dirpath = QtWidgets.QFileDialog.getSaveFileName(self, 'Select .csv file')

        self.txtB_tecoLCApath.setText(dirpath[0])

    def func_selectDir_heatload_path(self):
        """function to select the heatload path"""
        dirpath = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory")
        self.txtB_heatloadPath.setText(dirpath)

    def add_carrier(self):
        self.heat_carrier_counter += 1

        lbl_carrier_new = QtWidgets.QLabel("Carrier" + str(self.heat_carrier_counter))
        self.lGrid.addWidget(lbl_carrier_new, self.lGrid.rowCount(), 0, 1, 1)

        comB_carrier_new = QtWidgets.QComboBox()
        comB_carrier_new.setPlaceholderText(f"heat energy carrier EPD for carrier {self.heat_carrier_counter}")
        comB_carrier_new.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        comB_carrier_new.setMaximumWidth(250)
        self.lGrid.addWidget(comB_carrier_new, self.lGrid.rowCount() - 1, 2, 1, 1)
        setattr(self, f"comB_carrier{self.heat_carrier_counter}", comB_carrier_new)

        txtB_pef_new = QtWidgets.QLineEdit()
        txtB_pef_new.setPlaceholderText("PEF")
        txtB_pef_new.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        txtB_pef_new.setMaximumWidth(30)
        self.lGrid.addWidget(txtB_pef_new, self.lGrid.rowCount() - 1, 5, 1, 1)
        setattr(self, f"txtB_carrier{self.heat_carrier_counter}PEF", txtB_pef_new)

        self.resize(QtCore.QSize(self.width(), self.height() + 30))

        comB_carrier_new.addItems([
            "District heating from waste",
            "District heating from biogas",
            "District heating from biomass (solid)",
            "District heating from lignite",
            "District heating from natural gas",
            "District heating from light fuel oil",
            "District heating from hard coal",
            "District heating mix Germany",
            "Thermal energy from natural gas",
            "Thermal energy from light fuel oil",
            "Light fuel oil",
            "Heavy fuel oil",
            "Liquefied petroleum gas (LPG)",
            "Biogas (1 kg)",
            "Wood pellets (6,2% moisture / 5,8% H2O content)",
            "Vegetable oil fuel (rapeseed, 1 kg)"
        ])

    def load_en15804_lca_data_gui(self, category, lca_data):

        with open("../teco/data/input/inputdata/LcaData_gui.json") as f:
            data = json.load(f)

            for item_name, data_item in data[category].items():
                if lca_data.name == item_name:

                    pere = En15804IndicatorValue()
                    perm = En15804IndicatorValue()
                    pert = En15804IndicatorValue()
                    penre = En15804IndicatorValue()
                    penrm = En15804IndicatorValue()
                    penrt = En15804IndicatorValue()
                    sm = En15804IndicatorValue()
                    rsf = En15804IndicatorValue()
                    nrsf = En15804IndicatorValue()
                    fw = En15804IndicatorValue()
                    hwd = En15804IndicatorValue()
                    nhwd = En15804IndicatorValue()
                    rwd = En15804IndicatorValue()
                    cru = En15804IndicatorValue()
                    mfr = En15804IndicatorValue()
                    mer = En15804IndicatorValue()
                    eee = En15804IndicatorValue()
                    eet = En15804IndicatorValue()
                    gwp = En15804IndicatorValue()
                    odp = En15804IndicatorValue()
                    pocp = En15804IndicatorValue()
                    ap = En15804IndicatorValue()
                    ep = En15804IndicatorValue()
                    adpe = En15804IndicatorValue()
                    adpf = En15804IndicatorValue()

                    pere.set_values(**data_item["pere"])
                    perm.set_values(**data_item["perm"])
                    pert.set_values(**data_item["pert"])
                    penre.set_values(**data_item["penre"])
                    penrm.set_values(**data_item["penrm"])
                    penrt.set_values(**data_item["penrt"])
                    sm.set_values(**data_item["sm"])
                    rsf.set_values(**data_item["rsf"])
                    nrsf.set_values(**data_item["nrsf"])
                    fw.set_values(**data_item["fw"])
                    hwd.set_values(**data_item["hwd"])
                    nhwd.set_values(**data_item["nhwd"])
                    rwd.set_values(**data_item["rwd"])
                    cru.set_values(**data_item["cru"])
                    mfr.set_values(**data_item["mfr"])
                    mer.set_values(**data_item["mer"])
                    eee.set_values(**data_item["eee"])
                    eet.set_values(**data_item["eet"])
                    gwp.set_values(**data_item["gwp-total"])
                    odp.set_values(**data_item["odp"])
                    pocp.set_values(**data_item["pocp"])
                    ap.set_values(**data_item["ap"])
                    ep.set_values(**data_item["ep-terrestrial"]) # or marine or freshwater
                    adpe.set_values(**data_item["adpe"])
                    adpf.set_values(**data_item["adpf"])

                    lca_data.pere = pere
                    lca_data.perm = perm
                    lca_data.pert = pert
                    lca_data.penre = penre
                    lca_data.penrm = penrm
                    lca_data.penrt = penrt
                    lca_data.sm = sm
                    lca_data.rsf = rsf
                    lca_data.nrsf = nrsf
                    lca_data.fw = fw
                    lca_data.hwd = hwd
                    lca_data.nhwd = nhwd
                    lca_data.rwd = rwd
                    lca_data.cru = cru
                    lca_data.mfr = mfr
                    lca_data.mer = mer
                    lca_data.eee = eee
                    lca_data.eet = eet
                    lca_data.gwp = gwp
                    lca_data.odp = odp
                    lca_data.pocp = pocp
                    lca_data.ap = ap
                    lca_data.ep = ep
                    lca_data.adpe = adpe
                    lca_data.adpf = adpf


class SimulationProgram(QtWidgets.QWidget):
    def __init__(self, parent):
        super(SimulationProgram, self).__init__()
        self.parent = parent
        self.initUI()

    def initUI(self):
        global POSX, POSY, WIDTH, HEIGHT

        gf.windowSetup(self, POSX + 10, POSY + 10, 300, 150, 'OpenModelica or Dymola')

        self.vbox = QtWidgets.QVBoxLayout(self)
        self.setLayout(self.vbox)

        self.lbl = QtWidgets.QLabel("Please select the simulation type")
        self.vbox.addWidget(self.lbl)

        self.btn1 = QtWidgets.QPushButton("OpenModelica")
        self.vbox.addWidget(self.btn1)

        self.btn2 = QtWidgets.QPushButton("Dymola")
        self.vbox.addWidget(self.btn2)

        self.btn1.clicked.connect(self.func_openmodelica)
        self.btn2.clicked.connect(self.func_dymola)

    def func_openmodelica(self):
        self.hide()
        self.parent.simulation_program = "OpenModelica"
        self.parent.show()
        self.parent.func_startSimulation()

    def func_dymola(self):
        self.hide()
        self.parent.simulation_program = "Dymola"
        self.parent.show()
        self.parent.func_startSimulation()


class about(QtWidgets.QWidget):
    def __init__(self, file_path):
        super(about, self).__init__()
        self.file_path = file_path
        self.initUI()

    def initUI(self):
        global POSX, POSY, WIDTH, HEIGHT, SIZEFACTOR

        gf.windowSetup(self, POSX + 10, POSY + 10, WIDTH, HEIGHT, 'CityBIT - About')

        # creating main layout
        self.vbox = QtWidgets.QVBoxLayout(self)
        self.setLayout(self.vbox)

        gf.load_banner(self, r'../pictures/e3dHeader.png', 4)

        self.textwidget = QtWidgets.QPlainTextEdit()
        self.vbox.addWidget(self.textwidget)
        with open(self.file_path, 'r') as file:
            text = file.read()
        self.textwidget.setPlainText(text)
        self.textwidget.setReadOnly(True)

        self.lGrid = QtWidgets.QGridLayout()

        self.btn_repo = QtWidgets.QPushButton('Open repository')
        self.lGrid.addWidget(self.btn_repo, 0, 0, 1, 1)

        self.btn_close = QtWidgets.QPushButton('Close')
        self.lGrid.addWidget(self.btn_close, 0, 1, 1, 1)

        self.vbox.addLayout(self.lGrid)

        self.btn_repo.clicked.connect(self.open_repo)
        self.btn_close.clicked.connect(self.close_about)

    def open_repo(self):
        os.startfile('https://gitlab.e3d.rwth-aachen.de/e3d-software-tools/teaser')

    def close_about(self):
        self.hide()


class addBuilding(QtWidgets.QWidget):
    """Window to add buildings to the TEASER+eco-project
    """

    def __init__(self, prj, parent, buildingDict):
        # initiate the parent
        self.prj = prj
        self.parent = parent
        super(addBuilding, self).__init__()
        self.buildingDict = buildingDict
        self.initUI()

    def initUI(self):
        global POSX, POSY, WIDTH, HEIGHT, SIZEFACTOR, SIZER
        gf.windowSetup(self, POSX + 10, POSY, 650, 450, 'Add building')

        self.only_int = QtGui.QIntValidator()
        self.only_double = QtGui.QDoubleValidator()

        self.vbox = QtWidgets.QHBoxLayout(self)
        self.setLayout(self.vbox)

        self.gB_parameters = QtWidgets.QGroupBox('Building')
        self.vbox.addWidget(self.gB_parameters, 1, QtCore.Qt.AlignmentFlag.AlignLeft)

        self.pGrid = QtWidgets.QGridLayout()
        self.gB_parameters.setLayout(self.pGrid)

        self.lbl_name = QtWidgets.QLabel('Name:')
        self.pGrid.addWidget(self.lbl_name, 0, 1, 1, 1)

        self.led_name = QtWidgets.QLineEdit('')
        self.pGrid.addWidget(self.led_name, 0, 2, 1, 1)

        self.lbl_year = QtWidgets.QLabel('Year of construction:')
        self.pGrid.addWidget(self.lbl_year, 1, 1, 1, 1)

        self.led_year = QtWidgets.QLineEdit('')
        self.pGrid.addWidget(self.led_year, 1, 2, 1, 1)
        self.led_year.setValidator(self.only_int)

        self.lbl_nla = QtWidgets.QLabel('Net leased area:')
        self.pGrid.addWidget(self.lbl_nla, 2, 1, 1, 1)

        self.led_nla = QtWidgets.QLineEdit('')
        self.pGrid.addWidget(self.led_nla, 2, 2, 1, 1)

        self.lbl_numb_flr = QtWidgets.QLabel('Number of floors:')
        self.pGrid.addWidget(self.lbl_numb_flr, 3, 1, 1, 1)

        self.led_numb_flr = QtWidgets.QLineEdit('')
        self.pGrid.addWidget(self.led_numb_flr, 3, 2, 1, 1)
        self.led_numb_flr.setValidator(self.only_int)

        self.lbl_height_flr = QtWidgets.QLabel('height of floors:')
        self.pGrid.addWidget(self.lbl_height_flr, 4, 1, 1, 1)

        self.led_height_flr = QtWidgets.QLineEdit('')
        self.pGrid.addWidget(self.led_height_flr, 4, 2, 1, 1)
        self.led_height_flr.setPlaceholderText('3.50')
        self.led_height_flr.setValidator(self.only_double)

        self.lbl_method = QtWidgets.QLabel('Method:')
        self.pGrid.addWidget(self.lbl_method, 5, 1, 1, 1)

        self.cb_method = QtWidgets.QComboBox()
        self.pGrid.addWidget(self.cb_method, 5, 2, 1, 1)
        self.cb_method.addItems(["", 'iwu', 'urbanrenet', 'tabula_de'])

        self.lbl_usage = QtWidgets.QLabel('Usage:')
        self.pGrid.addWidget(self.lbl_usage, 6, 1, 1, 1)

        self.cb_usage = QtWidgets.QComboBox()
        self.pGrid.addWidget(self.cb_usage, 6, 2, 1, 1)
        self.cb_usage.addItems([""])
        self.cb_usage.setEnabled(False)

        self.lbl_quantity = QtWidgets.QLabel('Amount:')
        self.pGrid.addWidget(self.lbl_quantity, 7, 1, 1, 1)

        self.led_quantity = QtWidgets.QLineEdit('1')
        self.pGrid.addWidget(self.led_quantity, 7, 2, 1, 1)
        self.led_quantity.setValidator(self.only_int)

        self.btn_add_building = QtWidgets.QPushButton('Add building')
        self.pGrid.addWidget(self.btn_add_building, 8, 1, 1, 2)

        self.gB_add_lca = QtWidgets.QGroupBox('Add Utility')
        self.vbox.addWidget(self.gB_add_lca, 1, QtCore.Qt.AlignmentFlag.AlignLeft)

        self.lBox = QtWidgets.QGridLayout(self)
        self.gB_add_lca.setLayout(self.lBox)

        self.textwidget = QtWidgets.QPlainTextEdit()
        self.textwidget.setPlainText(
            'Utility infos \nLink to OEKOBAUDAT Search engine: \nhttps://www.oekobaudat.de/no_cache/en/database/search.html')
        self.textwidget.setReadOnly(True)
        self.lBox.addWidget(self.textwidget, 0, 0, 1, 2)

        self.lbl_uuid = QtWidgets.QLabel('UUID')
        self.lBox.addWidget(self.lbl_uuid, 1, 0, 1, 1)

        self.led_uuid = QtWidgets.QLineEdit('')
        self.lBox.addWidget(self.led_uuid, 1, 1, 1, 1)

        self.lbl_amount = QtWidgets.QLabel('Amount')
        self.lBox.addWidget(self.lbl_amount, 2, 0, 1, 1)

        self.led_amount = QtWidgets.QLineEdit('')
        self.lBox.addWidget(self.led_amount, 2, 1, 1, 1)
        self.led_amount.setValidator(self.only_double)

        self.lbl_building_nbr = QtWidgets.QRadioButton('Building No.')
        self.lBox.addWidget(self.lbl_building_nbr, 3, 0, 1, 1)
        self.lbl_building_nbr.setChecked(True)

        self.led_building_nbr = QtWidgets.QLineEdit('')
        self.lBox.addWidget(self.led_building_nbr, 3, 1, 1, 1)
        self.lbl_building_nbr.clicked.connect(lambda: self.led_building_nbr.setEnabled(True))

        self.lbl_district = QtWidgets.QRadioButton('District')
        self.lBox.addWidget(self.lbl_district, 4, 0, 1, 1)

        self.led_district = QtWidgets.QLineEdit('')
        self.led_district = QtWidgets.QLineEdit('')
        self.lBox.addWidget(self.led_district, 4, 1, 1, 1)
        # self.led_district.connect(self.lbl_district.isChecked(), self.led_district.setEnabled(True))

        self.btn_add_lca_to_list = QtWidgets.QPushButton('Add Utility to list')
        self.lBox.addWidget(self.btn_add_lca_to_list, 5, 0, 1, 2)

        self.tbl_lca = QtWidgets.QTableWidget()
        self.tbl_lca.setColumnCount(3)
        self.tbl_lca.setHorizontalHeaderLabels(['UUID', 'Amount', 'Building No.'])
        self.tbl_lca.verticalHeader().hide()
        # self.tbl_lca.horizontalHeader().hide()
        self.tbl_lca.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tbl_lca.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        self.tbl_lca.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        self.lBox.addWidget(self.tbl_lca, 6, 0, 1, 2)

        self.btn_add_lca = QtWidgets.QPushButton('Add Utilities')
        self.lBox.addWidget(self.btn_add_lca, 7, 0, 1, 2)

        self.cb_method.currentTextChanged.connect(self.method_changed)
        self.btn_add_lca.clicked.connect(self.add_lca)
        self.btn_add_lca_to_list.clicked.connect(self.add_lca_to_list)
        self.btn_add_building.clicked.connect(self.add_building)

        self.additonal_lca_data = []  # list with LCA-Data IDs

    def method_changed(self, value):
        """Function to set suitable archetypes for the methods in the usage 
        combo box

        Parameters
        ----------
        value : str
            method (e.g. 'iwu').

        """

        self.cb_usage.clear()

        if value == "":
            self.cb_usage.addItem("")
            self.cb_usage.setEnabled(False)
        else:
            self.cb_usage.setEnabled(True)
            if value == "iwu":
                self.cb_usage.addItem('singlefamilydwelling')
            elif value == "urbanrenet":
                self.cb_usage.addItems(
                    ['est1a', 'est1b', 'est2', 'est3', 'est4a', 'est4b', 'est5' 'est6', 'est7', 'est8a', 'est8b'])
            elif value == "tabula_de":
                self.cb_usage.addItems(
                    ["singlefamilyhouse", "terracedhouse", "multifamilyhouse", "apartmentblock"])

    def add_building(self):
        """Function to add the building to the project
        """

        method = self.cb_method.currentText()
        usage = self.cb_usage.currentText()
        year_of_construction = self.led_year.text()
        number_of_floors = self.led_numb_flr.text()
        height_of_floors = self.led_height_flr.text()
        name = self.led_name.text()
        net_leased_area = self.led_nla.text()
        building_quantity = self.led_quantity.text()

        if method != "" and usage != "" and year_of_construction != "" and number_of_floors != "" and height_of_floors != "" and name != "" and building_quantity != "" and net_leased_area != "":
            building_quantity = int(building_quantity)
            net_leased_area = float(net_leased_area)
            first_index = self.parent.tbl_selBuildings.rowCount()

            for i in range(building_quantity):

                if building_quantity > 1:
                    index = first_index + i + 1
                else:
                    index = ""

                usage_dict = {'singlefamilydwelling': 'single_family_dwelling',
                              'singlefamilyhouse': 'single_family_house',
                              'terracedhouse': 'terraced_house',
                              'multifamilyhouse': 'multi_family_house',
                              'apartmentblock': 'apartment_block',
                              'est1a': 'est1a',
                              'est1b': 'est1b',
                              'est2': 'est2',
                              'est3': 'est3',
                              'est4a': 'est4a',
                              'est4b': 'est4b',
                              'est5': 'est5',
                              'est6': 'est6',
                              'est7': 'est7',
                              'est8a': 'est8a',
                              'est8b': 'est8b'}
                self.add_building_data = {}
                self.add_building_data[name + str(index)] = {'method': method, 'usage': usage_dict[usage],
                                                             'name': name + str(index),
                                                             'year_of_construction': year_of_construction,
                                                             'number_of_floors': number_of_floors,
                                                             'height_of_floors': height_of_floors,
                                                             'net_leased_area': net_leased_area}

                rowPosition = self.parent.tbl_selBuildings.rowCount()
                self.parent.tbl_selBuildings.insertRow(rowPosition)

                self.parent.tbl_selBuildings.setItem(rowPosition, 0,
                                                     QtWidgets.QTableWidgetItem(name + str(index)))
                self.parent.tbl_selBuildings.setItem(rowPosition, 2,
                                                     QtWidgets.QTableWidgetItem(str(year_of_construction)))
                self.parent.tbl_selBuildings.setItem(rowPosition, 3, QtWidgets.QTableWidgetItem(str(net_leased_area)))
                self.parent.tbl_selBuildings.setItem(rowPosition, 4, QtWidgets.QTableWidgetItem(str(number_of_floors)))
                self.parent.tbl_selBuildings.setItem(rowPosition, 5, QtWidgets.QTableWidgetItem(str(height_of_floors)))
                self.parent.tbl_selBuildings.setItem(rowPosition, 6, QtWidgets.QTableWidgetItem(str(usage)))
                self.parent.tbl_selBuildings.setItem(rowPosition, 7, QtWidgets.QTableWidgetItem(str(method)))
                self.parent.building_groups.append([first_index, len(self.prj.buildings) - 1])

            self.close()
        else:
            gf.messageBox(self, 'Error', 'Please fill out all fields')
        return

    def add_lca_to_list(self):
        """Function to add the additional LCA-data to the building
        """
        lca_id = self.led_uuid.text()
        amount = self.led_amount.text()
        building_nbr = self.led_building_nbr.text()

        if lca_id != "" and amount != "" and building_nbr != "":
            rowPosition = self.tbl_lca.rowCount()
            self.tbl_lca.insertRow(rowPosition)

            self.tbl_lca.setItem(rowPosition, 0, QtWidgets.QTableWidgetItem(lca_id))
            self.tbl_lca.setItem(rowPosition, 1, QtWidgets.QTableWidgetItem(amount))
            self.tbl_lca.setItem(rowPosition, 2, QtWidgets.QTableWidgetItem(building_nbr))

            self.tbl_lca.resizeRowsToContents()
        else:
            gf.messageBox(self, 'Error', 'Please fill out all fields')

    def add_lca(self):

        for i in range(self.tbl_lca.rowCount()):
            if (self.tbl_lca.item(i, 0) is None) or (self.tbl_lca.item(i, 1) is None) or (
                    self.tbl_lca.item(i, 2) is None):
                gf.messageBox(self, "error", "Please fill in all fields of Utility row " + str(i) + "!")
                break
            '''building_no = int(self.tbl_lca.item(i, 2).text())
            key = [key for key in self.prj.buildings if
                   self.prj.buildings[key].name == self.parent.tbl_selBuildings.item(building_no, 0).text()]
            self.prj.buildings[key].add_lca_data_template(self.tbl_lca.item(i, 0).text(),
                                                          float(self.tbl_lca.item(i, 1).text()))'''

        self.close()
        return


class addLca(QtWidgets.QWidget):
    """Window to add additional LCA-data to the building.
    """

    def __init__(self, prj, parent):
        self.prj = prj
        self.parent = parent
        super(addLca, self).__init__()
        self.initUI()

    def initUI(self):
        global POSX, POSY, WIDTH, HEIGHT, SIZEFACTOR, SIZER
        gf.windowSetup(self, POSX + 300, POSY, 300, 400, 'Add LCA-data')

        self.only_double = QtGui.QDoubleValidator()

        self.vbox = QtWidgets.QVBoxLayout(self)
        self.setLayout(self.vbox)

        self.gB_lca = QtWidgets.QGroupBox('LCA-data')
        self.vbox.addWidget(self.gB_lca)

        self.lGrid = QtWidgets.QGridLayout()
        self.gB_lca.setLayout(self.lGrid)

        self.only_double = QtGui.QDoubleValidator()

        self.lbl_uuid = QtWidgets.QLabel('LCA-data id')
        self.lGrid.addWidget(self.lbl_uuid, 0, 1, 1, 1)

        self.led_uuid = QtWidgets.QLineEdit('')
        self.lGrid.addWidget(self.led_uuid, 0, 2, 1, 1)

        self.lbl_amount = QtWidgets.QLabel('Amount')
        self.lGrid.addWidget(self.lbl_amount, 1, 1, 1, 1)

        self.led_amount = QtWidgets.QLineEdit('')
        self.lGrid.addWidget(self.led_amount, 1, 2, 1, 1)
        self.led_amount.setValidator(self.only_double)

        self.btn_add = QtWidgets.QPushButton('Add')
        self.vbox.addWidget(self.btn_add)

        self.btn_add.clicked.connect(self.add)

    def add(self):
        """Function to add the additional LCA-data to the building
        """
        lca_id = self.led_uuid.text()
        amount = self.led_amount.text()

        rowPosition = self.parent.tbl_lca.rowCount()
        self.parent.tbl_lca.insertRow(rowPosition)

        self.parent.tbl_lca.setItem(rowPosition, 0, QtWidgets.QTableWidgetItem(lca_id))
        self.parent.tbl_lca.setItem(rowPosition, 1, QtWidgets.QTableWidgetItem(amount))

        self.parent.tbl_lca.resizerowsToContents()


class result(QtWidgets.QWidget):
    """Window to display the result of the life cycle assessment"""

    def __init__(self, prj, parent, checkboxes):

        self.prj = prj
        self.eco = parent
        self.ind_checkboxes = checkboxes
        super(result, self).__init__()
        self.initUI()

    def initUI(self):
        global POSX, POSY, WIDTH, HEIGHT, SIZEFACTOR, SIZER
        gf.windowSetup(self, POSX + 10, POSY + 300, 750, 400, 'Result')

        self.vbox = QtWidgets.QVBoxLayout(self)
        self.setLayout(self.vbox)

        self.cb_indicator = QtWidgets.QComboBox()
        self.vbox.addWidget(self.cb_indicator)
        if self.ind_checkboxes[0].isChecked():
            self.cb_indicator.addItems(checkbox.text() for checkbox in self.ind_checkboxes)
        else:
            self.cb_indicator.addItems(checkbox.text() for checkbox in self.ind_checkboxes if checkbox.isChecked())

        self.lbl_unit = QtWidgets.QLabel('Unit:')
        self.vbox.addWidget(self.lbl_unit)

        self.cb_unit = QtWidgets.QComboBox()
        self.vbox.addWidget(self.cb_unit)

        self.tbl_lca = QtWidgets.QTableWidget()
        self.tbl_lca.setColumnCount(22)
        self.tbl_lca.setHorizontalHeaderLabels(['Building',
                                                "amount",
                                                "a1",
                                                "a2",
                                                "a3",
                                                "a1_a3",
                                                "a4",
                                                "a5",
                                                "b1",
                                                "b2",
                                                "b3",
                                                "b4",
                                                "b5",
                                                "b6",
                                                "b7",
                                                "c1",
                                                "c2",
                                                "c3",
                                                "c4",
                                                "d",
                                                "sum",
                                                "sum wd"
                                                ])
        # Add unit change possibility
        self.tbl_lca.verticalHeader().hide()
        self.tbl_lca.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tbl_lca.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        self.tbl_lca.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        self.vbox.addWidget(self.tbl_lca)

        self.cGrid = QtWidgets.QGridLayout()

        self.btn_copy = QtWidgets.QPushButton('Copy csv to Clipboard')
        self.cGrid.addWidget(self.btn_copy, 0, 0, 1, 1)

        self.checkbox_ger = QtWidgets.QCheckBox("'German Excel'")
        self.cGrid.addWidget(self.checkbox_ger, 0, 1, 1, 1)

        self.vbox.addLayout(self.cGrid)

        self.select_lca()

        self.cb_unit.currentTextChanged.connect(self.change_unit)
        self.btn_copy.clicked.connect(self.copy_to_clipboard)
        self.cb_indicator.currentTextChanged.connect(self.select_lca)

    def change_unit(self):
        if self.cb_unit.currentText() == "kg" or "kg " in self.cb_unit.currentText() or self.cb_unit.currentText() == "MJ" or self.cb_unit.currentText() == "L":
            for i in range(2,self.tbl_lca.columnCount()):
                if self.tbl_lca.item(0,i) is not None and self.tbl_lca.item(0,i).text() not in ['None', ""]:
                    self.tbl_lca.setItem(0, i, QtWidgets.QTableWidgetItem(f"{float(self.tbl_lca.item(0, i).text()) * 1000:.3f}"))
        elif self.cb_unit.currentText() == "T" or "T " in self.cb_unit.currentText() or self.cb_unit.currentText() == "GJ" or self.cb_unit.currentText() == "m":
            for i in range(2,self.tbl_lca.columnCount()):
                if self.tbl_lca.item(0,i) is not None and self.tbl_lca.item(0,i).text() not in ['None', ""]:
                    self.tbl_lca.setItem(0, i, QtWidgets.QTableWidgetItem(f"{float(self.tbl_lca.item(0, i).text()) * 0.001:.3f}"))
        # Todo: add other units conversions

    def select_lca(self):

        indicator = self.cb_indicator.currentText()

        while (self.tbl_lca.rowCount() > 0):
            self.tbl_lca.removeRow(0)

        building_groups = self.eco.building_groups.copy()

        for key, building in enumerate(self.prj.buildings):
            building_groups.append([key, key])
        for building_group in building_groups:

            amount = building_group[1] - building_group[0] + 1

            building = self.prj.buildings[building_group[0]]

            lca_data = building.lca_data * amount

            lca_data_dict = self.lca_data_to_dict(lca_data)

            content = [building.name, amount]

            #Todo: add possible units for the rest of indicators
            if indicator == "pere":
                content.extend(lca_data_dict["pere"])
                self.add_lca_row(content)
                self.remove_units_from_combobox()
                self.cb_unit.addItems(['MJ', 'GJ'])
            elif indicator == "pert":
                content.extend(lca_data_dict["pert"])
                self.add_lca_row(content)
                self.remove_units_from_combobox()
                self.cb_unit.addItems(['MJ', 'GJ'])
            elif indicator == "penre":
                content.extend(lca_data_dict["penre"])
                self.add_lca_row(content)
                self.remove_units_from_combobox()
                self.cb_unit.addItems(['MJ', 'GJ'])
            elif indicator == "penrm":
                content.extend(lca_data_dict["penrm"])
                self.add_lca_row(content)
                self.remove_units_from_combobox()
                self.cb_unit.addItems(['MJ', 'GJ'])
            elif indicator == "penrt":
                content.extend(lca_data_dict["penrt"])
                self.add_lca_row(content)
                self.remove_units_from_combobox()
                self.cb_unit.addItems(['MJ', 'GJ'])
            elif indicator == "sm":
                content.extend(lca_data_dict["sm"])
                self.add_lca_row(content)
                self.remove_units_from_combobox()
                self.cb_unit.addItems(['kg', 'T'])
            elif indicator == "rsf":
                content.extend(lca_data_dict["rsf"])
                self.add_lca_row(content)
                self.remove_units_from_combobox()
                self.cb_unit.addItems(['MJ', 'GJ'])
            elif indicator == "nrsf":
                content.extend(lca_data_dict["nrsf"])
                self.add_lca_row(content)
                self.remove_units_from_combobox()
                self.cb_unit.addItems(['MJ', 'GJ'])
            elif indicator == "fw":
                content.extend(lca_data_dict["fw"])
                self.add_lca_row(content)
                self.remove_units_from_combobox()
                self.cb_unit.addItems(['m³', 'L'])
            elif indicator == "hwd":
                content.extend(lca_data_dict["hwd"])
                self.add_lca_row(content)
                self.remove_units_from_combobox()
                self.cb_unit.addItems(['kg', 'T'])
            elif indicator == "nhwd":
                content.extend(lca_data_dict["nhwd"])
                self.add_lca_row(content)
                self.remove_units_from_combobox()
                self.cb_unit.addItems(['kg', 'T'])
            elif indicator == "rwd":
                content.extend(lca_data_dict["rwd"])
                self.add_lca_row(content)
                self.remove_units_from_combobox()
                self.cb_unit.addItems(['kg', 'T'])
            elif indicator == "cru":
                content.extend(lca_data_dict["cru"])
                self.add_lca_row(content)
                self.remove_units_from_combobox()
                self.cb_unit.addItems(['kg', 'T'])
            elif indicator == "mfr":
                content.extend(lca_data_dict["mfr"])
                self.add_lca_row(content)
                self.remove_units_from_combobox()
                self.cb_unit.addItems(['kg', 'T'])
            elif indicator == "mer":
                content.extend(lca_data_dict["mer"])
                self.add_lca_row(content)
                self.remove_units_from_combobox()
                self.cb_unit.addItems(['kg', 'T'])
            elif indicator == "eee":
                content.extend(lca_data_dict["eee"])
                self.add_lca_row(content)
                self.remove_units_from_combobox()
                self.cb_unit.addItems(['MJ', 'GJ'])
            elif indicator == "eet":
                content.extend(lca_data_dict["eet"])
                self.add_lca_row(content)
                self.remove_units_from_combobox()
                self.cb_unit.addItems(['MJ', 'GJ'])
            elif indicator == "gwp":
                content.extend(lca_data_dict["gwp"])
                self.add_lca_row(content)
                self.remove_units_from_combobox()
                self.cb_unit.addItems(['kg CO2 eq.', 'T CO2 eq.'])
            elif indicator == "odp":
                content.extend(lca_data_dict["odp"])
                self.add_lca_row(content)
                self.remove_units_from_combobox()
                self.cb_unit.addItems(['kg R11 eq.', 'T R11 eq.'])
            elif indicator == "pocp":
                content.extend(lca_data_dict["pocp"])
                self.add_lca_row(content)
                self.remove_units_from_combobox()
                self.cb_unit.addItems(['kg Ethene eq.', 'T Ethene eq.'])
            elif indicator == "ap":
                content.extend(lca_data_dict["ap"])
                self.add_lca_row(content)
                self.remove_units_from_combobox()
                self.cb_unit.addItems(['kg SO2 eq.', 'T SO2 eq.'])
            elif indicator == "ep":
                content.extend(lca_data_dict["ep"])
                self.add_lca_row(content)
                self.remove_units_from_combobox()
                self.cb_unit.addItems(['kg Phosphate eq.', 'T Phosphate eq.'])
            elif indicator == "adpe":
                content.extend(lca_data_dict["adpe"])
                self.add_lca_row(content)
                self.remove_units_from_combobox()
                self.cb_unit.addItems(['kg Sb eq.', 'T Sb eq.'])
            elif indicator == "adpf":
                content.extend(lca_data_dict["adpf"])
                self.add_lca_row(content)
                self.remove_units_from_combobox()
                self.cb_unit.addItems(['MJ', 'GJ'])

            self.lbl_unit.setText('Unit: ' + self.cb_unit.currentText())

    def remove_units_from_combobox(self):
        for i in range(self.cb_unit.count()):
            self.cb_unit.removeItem(0)

    def lca_data_to_dict(self, lca_data):

        result = {}

        result['pere'] = self.indicator_to_list(lca_data.pere)
        result['pert'] = self.indicator_to_list(lca_data.pert)
        result['penre'] = self.indicator_to_list(lca_data.penre)
        result['penrm'] = self.indicator_to_list(lca_data.penrm)
        result['penrt'] = self.indicator_to_list(lca_data.penrt)
        result['sm'] = self.indicator_to_list(lca_data.sm)
        result['rsf'] = self.indicator_to_list(lca_data.rsf)
        result['nrsf'] = self.indicator_to_list(lca_data.nrsf)
        result['fw'] = self.indicator_to_list(lca_data.fw)
        result['hwd'] = self.indicator_to_list(lca_data.hwd)
        result['nhwd'] = self.indicator_to_list(lca_data.nhwd)
        result['rwd'] = self.indicator_to_list(lca_data.rwd)
        result['cru'] = self.indicator_to_list(lca_data.cru)
        result['mfr'] = self.indicator_to_list(lca_data.mfr)
        result['mer'] = self.indicator_to_list(lca_data.mer)
        result['eee'] = self.indicator_to_list(lca_data.eee)
        result['eet'] = self.indicator_to_list(lca_data.eet)
        result['gwp'] = self.indicator_to_list(lca_data.gwp)
        result['odp'] = self.indicator_to_list(lca_data.odp)
        result['pocp'] = self.indicator_to_list(lca_data.pocp)
        result['ap'] = self.indicator_to_list(lca_data.ap)
        result['ep'] = self.indicator_to_list(lca_data.ep)
        result['adpe'] = self.indicator_to_list(lca_data.adpe)
        result['adpf'] = self.indicator_to_list(lca_data.adpf)

        return result

    def indicator_to_list(self, indicator):

        result = []

        result.append(indicator.a1)
        result.append(indicator.a2)
        result.append(indicator.a3)
        result.append(indicator.a1_a3)
        result.append(indicator.a4)
        result.append(indicator.a5)
        result.append(indicator.b1)
        result.append(indicator.b2)
        result.append(indicator.b3)
        result.append(indicator.b4)
        result.append(indicator.b5)
        result.append(indicator.b6)
        result.append(indicator.b7)
        result.append(indicator.c1)
        result.append(indicator.c2)
        result.append(indicator.c3)
        result.append(indicator.c4)
        result.append(indicator.d)
        result.append(indicator.sum_stages(False))
        result.append(indicator.sum_stages(True))

        return result

    def add_lca_row(self, row):

        rowPosition = self.tbl_lca.rowCount()
        self.tbl_lca.insertRow(rowPosition)
        self.tbl_lca.setItem(rowPosition, 0, QtWidgets.QTableWidgetItem(str(row[0]))) # Building
        self.tbl_lca.setItem(rowPosition, 1, QtWidgets.QTableWidgetItem(str(row[1]))) # Amount
        for i in range(2,len(row)):
            if row[i] is not None:
                self.tbl_lca.setItem(rowPosition, i, QtWidgets.QTableWidgetItem(f"{row[i]:.3f}"))

    def copy_to_clipboard(self):
        """Function to copy the result to clipboard
        """

        self.clipboard = QtGui.QClipboard()

        self.clipboard.setText(self.tbl_to_csv(self.checkbox_ger.isChecked()))

    def tbl_to_csv(self, german=False):

        csv = "Building,amount,a1,a2,a3,a1_a3,a4,a5,b1,b2,b3,b4,b5,b6,b7,c1,c2,c3,c4,d,sum,sum+d\n"

        for row in range(self.tbl_lca.rowCount()):
            for column in range(self.tbl_lca.columnCount()):
                csv += self.tbl_lca.item(row, column).text()
                csv += ","

            csv += "\n"

        csv.replace("None", "")

        if german is True:
            csv = csv.replace(",", ";")
            csv = csv.replace(".", ",")

        return csv


if __name__ == "__main__":

    if not QtWidgets.QApplication.instance():
        app = QtWidgets.QApplication(sys.argv)
    else:
        app = QtWidgets.QApplication.instance()

    app.setStyle('Fusion')
    widget = MainWindow()
    widget.show()
    sys.exit(app.exec())
