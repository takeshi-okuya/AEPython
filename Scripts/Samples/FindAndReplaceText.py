# Find and Replace Text
# 
# This script finds and/or replaces text in the Source Text property of 
# all selected text layers.
# 
# It presents a UI with two text entry areas: a Find Text box for the
# text to find and a Replacement Text box for the new text.
#
# When the user clicks the Find All button, the layer selection is modified 
# to include only those text layers that include the Find Text string as a 
# value in the Source Text property or any keyframe on the Source Text 
# property.
#
# When the user clicks the Replace All button, the layer selection is 
# modified as for Find All, and all instances of the Find Text string are 
# are replaced in the Source Text property and any keyframes on the 
# Source Text property.
#
# A button labeled "?" provides a brief explanation.

import AEPython as ae
import qtae

from PySide2 import QtWidgets, QtCore

scriptName = "Find and Replace Text"


class FindAndReplaceText(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle(scriptName)
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

        topLayout = QtWidgets.QVBoxLayout()
        formLayout = QtWidgets.QFormLayout()
        hBoxLayout = QtWidgets.QHBoxLayout()

        self.findText = QtWidgets.QLineEdit()
        formLayout.addRow("Find Text:", self.findText)

        self.replacementText = QtWidgets.QLineEdit()
        formLayout.addRow("Replacement Text:", self.replacementText)

        findAllButton = QtWidgets.QPushButton("Find All")
        findAllButton.clicked.connect(self.onFindAll)
        hBoxLayout.addWidget(findAllButton)

        replaceButton = QtWidgets.QPushButton("Replace All")
        replaceButton.clicked.connect(self.onReplaceAll)
        hBoxLayout.addWidget(replaceButton)

        helpButton = QtWidgets.QPushButton("?")
        helpButton.setFixedWidth(30)
        helpButton.clicked.connect(self.onShowHelp)
        hBoxLayout.addWidget(helpButton)

        topLayout.addLayout(formLayout)
        topLayout.addLayout(hBoxLayout)
        self.setLayout(topLayout)

    # This function is used  during the Find All process.
    # It deselects the layer if it is not a text layer or if it does not
    # contain the Find Text string.
    def deselectLayerIfFindStringNotFound(self, theLayer, findString):
        # foundIt is initialized to false. It is set to true only if the Find Text string is 
        # contained in the Source Text (sourceText) property, as determined by the  
        # test in the nested if/else block below.
        foundIt = False

        # Get the Source Text property, if there is one.
        sourceText = theLayer.sourceText
        # Test to see if the Find Text value is contained in the Source Text property.
        if sourceText is not None:
            if sourceText.numKeys == 0:
                # textValue is a TextDocument. Check the string inside.
                if findString in sourceText.value.text:
                    foundIt = True
            else:
                # Do the test for each keyframe:
                for keyIndex in range(1, sourceText.numKeys + 1):
                    # textValue is a TextDocument. Check the string inside.
                    if findString in sourceText.keyValue(keyIndex).text:
                        foundIt = True
                        break

        # Deselect the layer if foundIt was not set to true in the tests of the Source Text property.
        if foundIt == False:
            theLayer.selected = False

    # This function is called when the Find All button is clicked.
    # It changes which layers are selected by deselecting layers that are not text layers
    # or do not contain the Find Text string. Only text layers containing the Find Text string 
    # will remain selected.
    def onFindAll(self):
        # Show a message and return if there is no value specified in the Find Text box.
        myFindString = self.findText.text()
        if myFindString == "":
            ae.alert("No text was entered in the Find Text box. The selection was not changed.", scriptName)
            return

        # Start an undo group.  By using this with an endUndoGroup(), you
        # allow users to undo the whole script with one undo operation.
        ae.app.beginUndoGroup("Find All")

        # Get the active composition.
        activeItem = ae.app.project.activeItem
        if activeItem is not None and isinstance(activeItem, ae.CompItem):
            # Check each selected layer in the active composition.
            activeComp = activeItem
            selectedLayers = activeComp.selectedLayers
            for layer in selectedLayers:
                self.deselectLayerIfFindStringNotFound(layer, myFindString)

        ae.app.endUndoGroup()

    # This function replaces findString with replaceString in the layer's 
    # sourceText property.
    # The method changes all keyframes, if there are keyframes, or just 
    # the value, if there are not keyframes.
    def replaceTextInLayer(self, theLayer, findString: str, replaceString: str):
        changedSomething = False

        # Get the sourceText property, if there is one.
        sourceText = theLayer.sourceText
        if sourceText is not None:
            if sourceText.numKeys == 0:
                # textValue is a TextDocument. Retrieve the string inside
                oldString = sourceText.value.text
                if findString in oldString:
                    newString = oldString.replace(findString, replaceString)
                    if oldString != newString:
                        sourceText.setValue(newString)
                        changedSomething = True
            else:
                # Do it for each keyframe:
                for keyIndex in range(1, sourceText.numKeys + 1):
                    # textValue is a TextDocument. Retrieve the string inside
                    oldString = sourceText.keyValue(keyIndex).text
                    if findString in oldString:
                        newString = oldString.replace(findString, replaceString)
                        if oldString != newString:
                            sourceText.setValueAtKey(keyIndex, newString)
                            changedSomething = True

        # Return a boolean saying whether we replaced the text
        return changedSomething

    # Called when the Replace All button is clicked
    # Replaces the Find Text string with the Replacement Text string everywhere within 
    # the set of selected layers.  Does not change the selected flag of any layers.
    def onReplaceAll(self):
        myFindString = self.findText.text()
        myReplaceString = self.replacementText.text()

        # Show a message and return if there is no string specified in the Find Text box.
        if myFindString == "":
            ae.alert("No text was entered in the Find Text box. No changes were made.", scriptName)

        # Start an undo group.  By using this with an endUndoGroup(), you
        # allow users to undo the whole script with one undo operation.
        ae.app.beginUndoGroup("Replace All")

        # If we don't make any changes, we'll put up an alert at the end.
        numLayersChanged = 0

        # Get the active comp
        activeItem = ae.app.project.activeItem
        if activeItem is not None and isinstance(activeItem, ae.CompItem):
            activeComp = activeItem

            # try to apply to every selected layer
            selectedLayers = activeComp.selectedLayers
            for curLayer in selectedLayers:
                # The method returns true if it changes any text, false otherwise.
                if self.replaceTextInLayer(curLayer, myFindString, myReplaceString) == True:
                    numLayersChanged += 1

        # Print a message if no layers were affected
        if numLayersChanged == 0:
            ae.alert(f"The string {myFindString} was not found in any of the selected layers. No changes were made", scriptName)

        ae.app.endUndoGroup()

    # Called when the "?" button is clicked
    def onShowHelp(self):
        ae.alert(
            scriptName + ":\n" +
            "Select one or more layers and enter text to find in the Find Text box. \n" +
            "Click Find All to change (narrow) the layer selection to include only those text layers with a Source Text property that contain the text specified in the Find Text box.\n" +
            "Click Replace All to replace all instances of the Find Text string with the Replacement Text string. Replacements are made only within selected text layers, and the selection remains unchanged.\n" +
            "Searches and replacements occur for Source Text properties and all of their keyframes.",
            scriptName
        )


findAndReplaceText = FindAndReplaceText(qtae.GetQtAEMainWindow())
findAndReplaceText.show()
