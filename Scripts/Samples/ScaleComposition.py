# ScaleComposition.py
#
# This script scales the active comp and all the layers within it.
#
# First, it prompts the user for a scale_factor, a new comp width,
# or a new comp height.
#
# Next, it scales the comp and all the layers within it, including
# cameras.

import AEPython as ae
import qtae

from PySide2 import QtWidgets, QtCore

scriptName = "Scale Composition"


class ScaleComposition(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        # This variable stores the scale_factor.
        self.scale_factor = 1.0

        self.setWindowTitle(scriptName)
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        layout = QtWidgets.QVBoxLayout()

        label = QtWidgets.QLabel("Scale composition using:")
        layout.addWidget(label)

        self.scaleButton = QtWidgets.QRadioButton("New Scale Factor")
        self.widthButton = QtWidgets.QRadioButton("New Comp Width")
        self.heightButton = QtWidgets.QRadioButton("New Comp Height")
        self.scaleButton.clicked.connect(self.onScaleButtonClick)
        self.widthButton.clicked.connect(self.onWidthButtonClick)
        self.heightButton.clicked.connect(self.onHeightButtonClick)
        layout.addWidget(self.scaleButton)
        layout.addWidget(self.widthButton)
        layout.addWidget(self.heightButton)
        self.scaleButton.setChecked(True)

        self.text_input = QtWidgets.QLineEdit("1.0")
        self.text_input.setMaximumWidth(100)
        self.text_input.editingFinished.connect(self.on_textInput_changed)
        layout.addWidget(self.text_input)

        self.okButton = QtWidgets.QPushButton("Scale")
        self.okButton.clicked.connect(self.onScaleClick)
        layout.addWidget(self.okButton)

        self.setLayout(layout)

    def onScaleButtonClick(self):
        self.text_input.setText(str(self.scale_factor))

    def onWidthButtonClick(self):
        activeItem = ae.app.project.activeItem
        if activeItem == None or isinstance(activeItem, ae.CompItem) == False:
            ae.alert("Please select or open a composition first.", scriptName)
        else:
            self.text_input.setText(str(int(activeItem.width * self.scale_factor)))

    def onHeightButtonClick(self):
        activeItem = ae.app.project.activeItem
        if activeItem == None or isinstance(activeItem, ae.CompItem) == False:
            ae.alert("Please select or open a composition first.", scriptName)
        else:
            self.text_input.setText(str(int(activeItem.height * self.scale_factor)))

    def testNewScale(self, test_scale):
        is_ok = True
        activeItem = ae.app.project.activeItem
        if activeItem == None or isinstance(activeItem, ae.CompItem) == False:
            ae.alert("Please select or open a composition first.", scriptName)
        else:
            if test_scale * activeItem.width < 1 or test_scale * activeItem.width > 30000:
                is_ok = False
            elif test_scale * activeItem.height < 1 or test_scale * activeItem.height > 30000:
                is_ok = False

        return is_ok

    # This function is called when the user enters text for the scale.
    def on_textInput_changed(self):
        activeItem = ae.app.project.activeItem
        if activeItem == None or isinstance(activeItem, ae.CompItem) == False:
            ae.alert("Please select or open a composition first.", scriptName)
        else:
            # Set the scale_factor based on the text.
            value = self.text_input.text()
            try:
                value = float(value)
                isNaN = False
            except:
                isNaN = True

            if isNaN:
                ae.alert(value + " is not a number. Please enter a number.", scriptName)
            else:
                if self.scaleButton.isChecked() == True:
                    new_scale_factor = value
                elif self.widthButton.isChecked() == True:
                    new_scale_factor = value / activeItem.width
                else:
                    new_scale_factor = value / activeItem.height

                if self.testNewScale(new_scale_factor):
                    self.scale_factor = new_scale_factor
                else:
                    ae.alert("Value will make height or width out of range 1 to 30000. Reverting to previous value.", scriptName)
                    # Load text back in from current values.
                    if self.scaleButton.value == True:
                        self.onScaleButtonClick()
                    elif self.widthButton.value == True:
                        self.onWidthButtonClick()
                    else:
                        self.onHeightButtonClick()

    def onScaleClick(self):
        activeItem = ae.app.project.activeItem
        if activeItem == None or isinstance(activeItem, ae.CompItem) == False:
            ae.alert("Please select or open a composition first.", scriptName)
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
            null3DLayer.position.setValue([0, 0, 0])

            # Set null3DLayer as parent of all layers that don't have parents.
            makeParentLayerOfAllUnparented(activeComp, null3DLayer)

            # Set new comp width and height.
            activeComp.width = int(activeComp.width * self.scale_factor)
            activeComp.height = int(activeComp.height * self.scale_factor)

            # Then for all cameras, scale the Zoom parameter proportionately.
            scaleAllCameraZooms(activeComp, self.scale_factor)

            # Set the scale of the super parent null3DLayer proportionately.
            superParentScale = null3DLayer.scale.value
            superParentScale[0] = superParentScale[0] * self.scale_factor
            superParentScale[1] = superParentScale[1] * self.scale_factor
            superParentScale[2] = superParentScale[2] * self.scale_factor
            null3DLayer.scale.setValue(superParentScale)

            # Delete the super parent null3DLayer with dejumping enabled.
            null3DLayer.remove()

            ae.app.endUndoGroup()

            # Reset scale_factor to 1.0 for next use.
            self.scale_factor = 1.0
            if (self.scaleButton.isChecked()):
                self.text_input.setText("1.0")

# Sets newParent as the parent of all layers in theComp that don't have parents.
# This includes 2D/3D lights, camera, av, text, etc.
def makeParentLayerOfAllUnparented(theComp, newParent):
    for i in range(1, theComp.numLayers + 1):
        curLayer = theComp.layer(i)
        if curLayer != newParent and curLayer.parent == None:
            curLayer.parent = newParent

# Scales the zoom factor of every camera by the given scale_factor.
# Handles both single values and multiple keyframe values.
def scaleAllCameraZooms(theComp, scaleBy):
    for i in range(1, theComp.numLayers + 1):
        curLayer = theComp.layer(i)
        if curLayer.matchName == "ADBE Camera Layer":
            curZoom = curLayer.zoom
            if curZoom.numKeys == 0:
                curZoom.setValue(curZoom.value * scaleBy)
            else:
                for j in range(1, curZoom.numKeys + 1):
                    curZoom.setValueAtKey(j, curZoom.keyValue(j)*scaleBy)


dialog = ScaleComposition(qtae.GetQtAEMainWindow())
dialog.show()
