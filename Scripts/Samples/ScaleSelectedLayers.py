# Scale Selected Layers
#
# This script scales the selected layers within the active comp.
#
# First, it prompts the user for a scale_factor.
# Next, it scales all selected layers, including cameras.

import AEPython as ae
import qtae

from PySide2 import QtWidgets, QtCore

scriptName = "Scale Selected Layers"


class ScaleSelectedLayers(QtWidgets.QDialog):
    def __init__(self, parent):
        super().__init__(parent)

        # This variable stores the scale_factor.
        self.scale_factor = 1.0
        self.scale_about_center = True

        self.setWindowTitle(scriptName)
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        layout = QtWidgets.QVBoxLayout()

        self.cornerButton = QtWidgets.QRadioButton('Scale about Upper Left')
        self.centerButton = QtWidgets.QRadioButton('Scale about Center')
        self.cornerButton.clicked.connect(self.onCornerButtonClick)
        self.centerButton.clicked.connect(self.onCenterButtonClick)
        layout.addWidget(self.cornerButton)
        layout.addWidget(self.centerButton)
        self.cornerButton.setChecked(True)

        self.text_input = QtWidgets.QLineEdit("1.0")
        self.text_input.setMaximumWidth(100)
        self.text_input.editingFinished.connect(self.on_textInput_changed)
        layout.addWidget(self.text_input)

        self.okButton = QtWidgets.QPushButton("Scale")
        self.okButton.clicked.connect(self.onScaleClick)
        layout.addWidget(self.okButton)

        self.setLayout(layout)

    # This function is called when the user clicks the "Scale about Upper Left" button
    def onCornerButtonClick(self):
        self.scale_about_center = False

    # This function is called when the user clicks the "Scale about Upper Left" button
    def onCenterButtonClick(self):
        self.scale_about_center = True

    # This function is called when the user enters text for the scale.
    def on_textInput_changed(self):
        # Set the scale_factor based on the text.
        value = self.text_input.text()
        try:
            self.scale_factor = float(value)
        except:
            ae.alert(value + " is not a number. Please enter a number.", scriptName)

    def onScaleClick(self):
        activeItem = ae.app.project.activeItem
        if activeItem is None or isinstance(activeItem, ae.CompItem) == False:
            ae.alert("Please select or open a composition first.", scriptName)
        else:
            selectedLayers = activeItem.selectedLayers
            if len(selectedLayers) == 0:
                ae.alert("Please select at least one layer in the active comp first.", scriptName)
            else:
                # Validate the input field, in case the user didn't defocus it first (which often can be the case).
                self.on_textInput_changed()

                activeComp = activeItem

                # By bracketing the operations with begin/end undo group, we can
                # undo the whole script with one undo operation.
                ae.app.beginUndoGroup(scriptName)

                # Create a null 3D layer.
                null3DLayer = activeItem.layers.addNull()
                null3DLayer.threeDLayer = True

                # Set its position to (0,0,0).
                if self.scale_about_center:
                    null3DLayer.position.setValue([activeComp.width * 0.5, activeComp.height * 0.5, 0])
                else:
                    null3DLayer.position.setValue([0, 0, 0])

                # Set null3DLayer as parent of all layers that don't have parents.
                makeParentLayerOfUnparentedInArray(selectedLayers, null3DLayer)

                # Then for all cameras, scale the Zoom parameter proportionately.
                scaleCameraZoomsInArray(selectedLayers, self.scale_factor)

                # Set the scale of the super parent null3DLayer proportionately.
                superParentScale = null3DLayer.scale.value
                superParentScale[0] = superParentScale[0] * self.scale_factor
                superParentScale[1] = superParentScale[1] * self.scale_factor
                superParentScale[2] = superParentScale[2] * self.scale_factor
                null3DLayer.scale.setValue(superParentScale)

                # Delete the super parent null3DLayer with dejumping enabled.
                null3DLayer.remove()

                # Everything we just did changed the selection. Reselect those
                # same layers again.
                for layer in selectedLayers:
                    layer.selected = True

                ae.app.endUndoGroup()

                # Reset scale_factor to 1.0 for next use.
                self.scale_factor = 1.0
                self.text_input.setText("1.0")


# Sets newParent as the parent of all layers in theComp that don't have parents.
# This includes 2D/3D lights, camera, av, text, etc.
def makeParentLayerOfUnparentedInArray(layerArray: list[ae.Layer], newParent: ae.Layer):
    for curLayer in layerArray:
        if curLayer != newParent and curLayer.parent is None:
            curLayer.parent = newParent

# Scales the zoom factor of every camera by the given scale_factor.
# Handles both single values and multiple keyframe values.
def scaleCameraZoomsInArray(layerArray: list[ae.Layer], scaleBy: float):
    for curLayer in layerArray:
        if curLayer.matchName == "ADBE Camera Layer":
            curZoom = curLayer.zoom
            if curZoom.numKeys == 0:
                curZoom.setValue(curZoom.value * scaleBy)
            else:
                for j in range(1, curZoom.numKeys + 1):
                    curZoom.setValueAtKey(j, curZoom.keyValue(j)*scaleBy)


dialog = ScaleSelectedLayers(qtae.GetQtAEMainWindow())
dialog.show()
