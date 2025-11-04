#3ds max weight tool for maya
# Authored and Designed by Thomas Dameris

import sys, os, json
import importlib
from functools import partial

import maya.cmds as cmds
from maya import OpenMayaUI as omui

from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtUiTools import QUiLoader
from shiboken2 import wrapInstance
 
#path to functions
path = r"YOUR PATH HERE"
if path not in sys.path:
    sys.path.append(path)

from Functions import weightToolMax_functions as skin
importlib.reload(skin)

#improt checks
skin.sanityCheck()

class weightTool_Max(QtWidgets.QWidget):
    window = None

    def __init__(self, parent=None):
        super(weightTool_Max, self).__init__(parent=parent)
        self.setWindowFlags(QtCore.Qt.Window)

        #load ui
        self.widgetPath = rYOUR PATH TO WIDGET FOLDER"
        self.widget = QUiLoader().load(self.widgetPath + r"/weightToolMax_UI.ui")
        self.widget.setParent(self)

        #window sizing
        self.setMinimumWidth(222)
        self.setMaximumWidth(222)
        self.setMaximumHeight(400)
        self.setMinimumHeight(400)
        self.resize(222, 400)

        #connect widgets
        widgetTypes = (
            QtWidgets.QPushButton,
            QtWidgets.QLineEdit,
            QtWidgets.QComboBox,
            QtWidgets.QSpinBox,
            QtWidgets.QDoubleSpinBox,
            QtWidgets.QCheckBox,
            QtWidgets.QListWidget,
        )
        storeNames = ("btns", "lineEdits", "combos", "spins", "dspins", "checks", "lists")
        sourceWidgets = tuple(self.widget.findChildren(t) for t in widgetTypes)

        for src, store in zip(sourceWidgets, storeNames):
            mapping = {w.objectName(): w for w in src if w.objectName()}
            setattr(self, store, mapping)
            for name, w in mapping.items():
                setattr(self, f"{name}UI", w)


        self.selection = []       
        self.selectedFaces = []
        self.selectedJoints = []
        self.copiedWeights = []    
        self.influenceList = []
        self.pickWeight = []


        #normalize and prune
        if hasattr(self, "normalizeBtnUI"):
            self.normalizeBtnUI.clicked.connect(self.normalizeWeightsUI)
        if hasattr(self, "pruneBtnUI"):
            self.pruneBtnUI.clicked.connect(self.pruneWeightsUI)

        #inf list and viewport update
        if hasattr(self, "grabVertexBtnUI"):
            self.grabVertexBtnUI.clicked.connect(self.updateInfluenceListUI)
        if hasattr(self, "currentInfListUI"):
            self.currentInfListUI.currentItemChanged.connect(self.updateViewportUI)
        if hasattr(self, "clearListBtnUI"):
            self.clearListBtnUI.clicked.connect(self.clearInfluenceListUI)

        #3ds max style quick weights
        if hasattr(self, "val0BtnUI"):
            self.val0BtnUI.clicked.connect(partial(self.setInfluenceWeightUI, 0.0))
        if hasattr(self, "val10BtnUI"):
            self.val10BtnUI.clicked.connect(partial(self.setInfluenceWeightUI, 0.1))
        if hasattr(self, "val25BtnUI"):
            self.val25BtnUI.clicked.connect(partial(self.setInfluenceWeightUI, 0.25))
        if hasattr(self, "val50BtnUI"):
            self.val50BtnUI.clicked.connect(partial(self.setInfluenceWeightUI, 0.5))
        if hasattr(self, "val75BtnUI"):
            self.val75BtnUI.clicked.connect(partial(self.setInfluenceWeightUI, 0.75))
        if hasattr(self, "val90BtnUI"):
            self.val90BtnUI.clicked.connect(partial(self.setInfluenceWeightUI, 0.9))
        if hasattr(self, "val100BtnUI"):
            self.val100BtnUI.clicked.connect(partial(self.setInfluenceWeightUI, 1.0))

            
        #custom set/scale
        if hasattr(self, "setWeightBtnUI"):
            self.setWeightBtnUI.clicked.connect(self.setCustomWeightUI)
        if hasattr(self, "scaleWeightBtnUI"):
            self.scaleWeightBtnUI.clicked.connect(self.scaleWeightsUI)
        if hasattr(self, "pickSetWeightBtnUI"):
            self.pickSetWeightBtnUI.clicked.connect(self.pickWeightUI)
        if hasattr(self, "growSelBtnUI"):
            self.growSelBtnUI.clicked.connect(partial(self.scaleSelectionUI, 1))
        if hasattr(self, "shrinkSelBtnUI"):
            self.shrinkSelBtnUI.clicked.connect(partial(self.scaleSelectionUI, 2))
        if hasattr(self, "LoopBtnUI"):
            self.LoopBtnUI.clicked.connect(partial(self.scaleSelectionUI, 5))
        if hasattr(self, "copyBtnUI"):
            self.copyBtnUI.clicked.connect(self.copyUI)
        if hasattr(self, "pasteBtnUI"):
            self.pasteBtnUI.clicked.connect(self.pasteUI)
        #init resize
        self.widget.resize(self.width(), self.height())

    ##################################### Weight Tool Functions ###########################################

    def copyUI(self):
        selection = cmds.ls(sl=True)
        self.copiedWeights = skin.copyWeights(selection)

    def pasteUI(self):
        selection = cmds.ls(sl=True)
        skin.pasteWeights(self.copiedWeights, selection)


    #normalize and prune
    def normalizeWeightsUI(self):
        selection = cmds.ls(sl=True, type="transform")
        skin.normalizeWeights(selection)

    def pruneWeightsUI(self):
        selection = cmds.ls(sl=True)
        tolerance = self.pruneSpinUI.value() if hasattr(self, "pruneSpinUI") else 0.01
        skin.pruneWeights(selection, tolerance)

    #3ds max style hotkeys
    def setInfluenceWeightUI(self, weight):
        selection = cmds.ls(sl=True, fl=True)
        influences = self.getListedInfluences()
        if influences:
            skin.setInfluenceWeight(selection, influences, weight)

    def setCustomWeightUI(self):
        selection = cmds.ls(sl=True)
        weight = self.setWgtSpinUI.value() if hasattr(self, "setWgtSpinUI") else 1.0
        influences = self.getListedInfluences()
        if influences:
            skin.setInfluenceWeight(selection, influences, weight)

    def scaleWeightsUI(self):
        selection = cmds.ls(sl=True)
        influences = self.getListedInfluences()
        if influences:
            scaleVal = self.scaleWgtSpinUI.value() if hasattr(self, "scaleWgtSpinUI") else 1.0
            skin.scaleWeights(selection, influences, scaleVal, clamp=True)

    ##################################### Paint Weight Stuff ###########################################
    def scaleSelectionUI(self, operation):
        skin.scaleSelection(operation)

    def selectAllVertsUI(self):
        selection = cmds.ls(sl=True)
        skin.selectObject(selection)

    def pickWeightUI(self):
        selection = cmds.ls(sl=True)
        verts = cmds.ls(cmds.polyListComponentConversion(selection, tv=True) or [], fl=True) or []
        if len(verts) != 1:
            cmds.error("select a single vert to get weights from")
        influences = self.getListedInfluences()
        if influences:
            vertWeight = skin.pickWeight(selection, influences)
            if hasattr(self, "setWgtSpinUI"):
                self.setWgtSpinUI.setValue(vertWeight)

    def setIntensityUI(self):
        value = self.brushIntensitySpin.value() if hasattr(self, "brushIntensitySpin") else 1.0
        skin.setIntensity(value)

    def updateIntensity(self):
        intensity = skin.updateIntensity()
        if hasattr(self, "brushIntensitySpin"):
            self.brushIntensitySpin.setValue(intensity)

    def clearInfluenceListUI(self):
        if hasattr(self, "currentInfListUI"):
            self.currentInfListUI.clear()

    def updateInfluenceListUI(self):
        selection = cmds.ls(sl=True)
        influencesList = skin.getCurrentInfluences(selection)
        if hasattr(self, "currentInfListUI"):
            self.currentInfListUI.clear()
            self.currentInfListUI.addItems(influencesList)

    def updateViewportUI(self):
        influences = self.getListedInfluences()
        if influences:
            skin.updateViewport(influences)

    def getListedInfluences(self):
        if hasattr(self, "currentInfListUI") and self.currentInfListUI.currentItem():
            return self.currentInfListUI.currentItem().text()
        return None
   
    def scaleSelectionUI(self, operation):
        skin.scaleSelection(operation)
        
    ##################################### QT stuff ###########################################

    def resizeEvent(self, event):
        self.widget.resize(self.width(), self.height())

    def closeEvent(self, event):
        super().closeEvent(event)

def openWindow():
    """
    ID Maya and attach tool window.
    """
    if QtWidgets.QApplication.instance():
        for win in QtWidgets.QApplication.allWindows():
            if 'weightTool_Max' in win.objectName():
                win.destroy()

    mayaMainWindowPtr = omui.MQtUtil.mainWindow()
    mayaMainWindow = wrapInstance(int(mayaMainWindowPtr), QtWidgets.QWidget)

    weightTool_Max.window = weightTool_Max(parent=mayaMainWindow)
    weightTool_Max.window.setObjectName('weightTool_Max')
    weightTool_Max.window.setWindowTitle('Weight Tool Max')
    weightTool_Max.window.show()
