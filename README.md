# AE Python
Python scripting plugin for After Effects

***Read this document in other languages: [Japanese](./README_ja.md)***

## Features
* Directly edit data on After Effects with Python scripts
* Enabled to use classes and functions with the same names as After Effects default scripts (ExtendScript, JavaScript) 
  * Class and function reference: https://ae-scripting.docsforadobe.dev/introduction/overview.html
* Interoperation between Javascript and Python
* GUI development by Qt ([PySide2](https://pypi.org/project/PySide2/))

## System Requirements
* Adobe After Effects CS6 / CC~
* Windows 10 / 11
* [Python 3.10.9](https://www.python.org/downloads/release/python-3109/) (included in the distribution Zip)

## Installation
Copy each files and folders in the distribution Zip to the following locations.
* AEPython folder -> C:\Program Files\Adobe\Adobe After Effects {version}\Support Files\Plug-ins\AEPython
* AEPython.jsx -> C:\Program Files\Adobe\Adobe After Effects {version}\Support Files\Scripts\Startup\AEPython.jsx

## License
MIT License (see [LICENSE](./LICENSE).)

## Scripting Guide

### Run Python scripts from the Python Window
Select menu: Window -> Python

```Python
comp = ae.app.project.items.addComp("Comp1", 1920, 1080, 1, 10, 24)
comp.bgColor = [1.0, 1.0, 1.0]

text_layer = comp.layers.addText("This is an AE Python sample.")

text_prop = text_layer.property("Source Text")
text_document = text_prop.value
text_document.fontSize = 50
text_prop.setValue(text_document)
```

### Run .py files from the Python Window
Select .py file from File -> "Execute Python File" in the AEPython window.

[sample.py]
```Python
import AEPython as ae
ae.alert(ae.app.project.file)
```

### Run Python scripts from ExtendScript
```JavaScript
Python.exec("ae.app.project.activeItem.name = 'New Name'");
```

### Run .py files from ExtendScript
```JavaScript
Python.execFile("D:/sample.py");
```

### GUI by Qt
```Python 
from PySide2 import QtWidgets

import AEPython as ae
import qtae

class MyDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QtWidgets.QVBoxLayout()

        self.text_input = QtWidgets.QLineEdit("")
        layout.addWidget(self.text_input)

        self.button = QtWidgets.QPushButton("Add Text Layer!")
        self.button.clicked.connect(self.onButtonClicked)
        layout.addWidget(self.button)

        self.setLayout(layout)

    def onButtonClicked(self):
        text = self.text_input.text()
        layer = ae.app.project.activeItem.layers.addText(text)
        layer.position.setValue([100,100])

dialog = MyDialog(qtae.GetQtAEMainWindow())
dialog.show()
```