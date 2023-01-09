# AE Python
After Effects 内部用 Python プラグイン

***Read this document in other languages: [English](./README.md)***

## 特徴
* After Effect 上のデータを Python スクリプトで直接編集
* After Effects 標準スクリプト（ExtendScript, JavaScript）と同名のクラス・関数を利用可能
  * クラス・関数リファレンス： https://ae-scripting.docsforadobe.dev/introduction/overview.html
* Javascript <--> Python の相互連携
* Qt ([PySide2](https://pypi.org/project/PySide2/)) による GUI開発

## 動作環境
* Adobe After Effects CS6 / CC~
* Windows 10 / 11
* [Python 3.10.9](https://www.python.org/downloads/release/python-3109/) （配布 Zip に同梱）

## インストール
配布 Zip 内の各項目をそれぞれ下記の場所にコピー
* AEPython フォルダ -> C:\Program Files\Adobe\Adobe After Effects {バージョン}\Support Files\Plug-ins\AEPython
* AEPython.jsx -> C:\Program Files\Adobe\Adobe After Effects {バージョン}\Support Files\Scripts\Startup\AEPython.jsx

## ライセンス
MITライセンス（[LICENSE](./LICENSE) を参照）

## スクリプティングガイド

### Python Window から Python スクリプトを実行
Window メニュー -> Python を選択

```Python
comp = ae.app.project.items.addComp("Comp1", 1920, 1080, 1, 10, 24)
comp.bgColor = [1.0, 1.0, 1.0]

text_layer = comp.layers.addText("This is an AE Python sample.")

text_prop = text_layer.property("Source Text")
text_document = text_prop.value
text_document.fontSize = 50
text_prop.setValue(text_document)
```

### Python Window から .py ファイルを実行
AEPython ウインドウの File -> Execute Python File から .py ファイルを選択

[sample.py]
```Python
import AEPython as ae
ae.alert(ae.app.project.file)
```

### ExtendScript から Python スクリプトを実行
```JavaScript
Python.exec("ae.app.project.activeItem.name = 'New Name'");
```

### ExtendScript から .py ファイルを実行
```JavaScript
Python.execFile("D:/sample.py");
```

### Qt で GUI を作成
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