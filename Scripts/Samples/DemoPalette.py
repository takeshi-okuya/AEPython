# Demo Palette
#
# This script creates and shows a floating palette.
# The floating palette contains buttons that launch a variety of
# demo scripts.

import sys
import os.path
import importlib.util

import AEPython as ae
import qtae

from PySide2 import QtWidgets, QtCore


class ScriptDemos(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Script Demos")
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        self.gridLayout = QtWidgets.QGridLayout()
        self.setLayout(self.gridLayout)

        self.addScriptButton(0, 0, "Find and Replace Text", "FindAndReplaceText.py")
        self.addScriptButton(1, 0, "Scale Composition", "ScaleComposition.py")
        self.addScriptButton(2, 0, "Scale Selected Layers", "ScaleSelectedLayers.py")
        self.addScriptButton(0, 1, "Sort Layers by In Point", "SortLayersByInPoint.py")
        self.addScriptButton(1, 1, "Render and Email", "RenderAndEmail.py")

        helpButton = QtWidgets.QPushButton("?")
        helpButton.clicked.connect(self.onHelpButtonClick)
        self.gridLayout.addWidget(helpButton, 2, 1)

    def addScriptButton(self, row, column, buttonLabel, buttonScriptName):
        button = QtWidgets.QPushButton(buttonLabel)
        button.clicked.connect(lambda: self.onScriptButtonClick(buttonScriptName))
        button.setMinimumWidth(180)
        self.gridLayout.addWidget(button, row, column)

    # Called when a button is pressed, to invoke its associated script
    def onScriptButtonClick(self, pyFileName: str):
        moduleDirPath = os.path.dirname(__file__)
        pyFilePath = os.path.join(moduleDirPath, pyFileName)
        name = os.path.splitext(pyFileName)[0]

        spec = importlib.util.spec_from_file_location(name, pyFilePath)
        module = importlib.util.module_from_spec(spec)

        sys.path.insert(0, moduleDirPath)
        try:
            spec.loader.exec_module(module)
        finally:
            sys.path.remove(moduleDirPath)

    # Called when a button is pressed, to invoke its associated script
    def onHelpButtonClick(self):
        ae.alert(
            "Click a button to run one of the following scripts:\n\n" +
            "Find and Replace Text:\n" +
            "Launches a UI to find and replace text values. Finds and replaces text within values and keyframe values of selected text layers of the active comp.\n" +
            "\n" +
            "Scale Composition:\n" +
            "Launches a UI to scale the active comp. Scales all layers, including cameras, and also the comp dimensions.\n" +
            "\n" +
            "Scale Selected Layers:\n" +
            "Launches a UI to scale the selected layers of the active comp. Scales all selected layers, including cameras.\n" +
            "\n" +
            "Sort Layers by In Point:\n" +
            "Reorders all layers in the active comp by in-point.\n" +
            "\n" +
            "Render and Email:\n" +
            "Renders all queued render items and then sends you an email message when the render batch is done. Refer to Help for more information on this script.\n" +
            "", "Demo Palette"
        )


script_demos = ScriptDemos(qtae.GetQtAEMainWindow())
script_demos.show()
