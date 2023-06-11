import sys
import os

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

import _AEPython as _ae
import AEPython as ae

__MainWindow = None
__PythonWindow = None


def __init_qt():
    app = QApplication.instance()
    if app is not None:
        return

    app = QApplication(sys.argv)

    style = '''
QMainWindow, QDialog, QAbstractButton, QLabel{
    background-color: #444444;
    color: #ffffff;
}
'''

    app.setStyleSheet(style)


class PythonWindow(QMainWindow):
    class Logger:
        def __init__(self, editor: QTextEdit, color=None, show=None):
            self.editor = editor
            self.color = editor.textColor() if color is None else color
            self.show = show

        def write(self, message: str):
            self.editor.moveCursor(QTextCursor.End)
            self.editor.setTextColor(self.color)
            self.editor.insertPlainText(message)

            if self.show is not None:
                self.show()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle('AE Python')

        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)

        layout = QVBoxLayout()
        self.centralWidget.setLayout(layout)

        label_output = QLabel("Output:")
        layout.addWidget(label_output)

        self.textedit_output = QTextEdit("")
        self.textedit_output.setStyleSheet("background-color: #e0e0e0;")
        layout.addWidget(self.textedit_output)

        label_code = QLabel("Code:")
        layout.addWidget(label_code)

        self.textedit_code = QPlainTextEdit("")
        layout.addWidget(self.textedit_code)

        self.button_execute = QPushButton("Execute")
        self.button_execute.clicked.connect(self.__execute)
        layout.addWidget(self.button_execute)

        exec_action = QAction("Execute Python File", self)
        exec_action.triggered.connect(self.__execute_file)

        file_menu = self.menuBar().addMenu("File")
        file_menu.addAction(exec_action)

        sys.stdout = self.Logger(self.textedit_output)
        sys.stderr = self.Logger(self.textedit_output, QColor(255, 0, 0), self.show)
        print("AE Python 1.0.0")

    def __execute(self):
        code = self.textedit_code.toPlainText()
        exec(code, globals(), _ae.locals)

    def __execute_file(self):
        file_path = QFileDialog.getOpenFileName(self, "Execute Python File", "", "Python (*.py)")[0]
        if file_path == '':
            return

        dont_write_bytecode = sys.dont_write_bytecode
        module_dir = os.path.dirname(file_path)
        sys.path.insert(0, module_dir)
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location(file_path, file_path)
            module = importlib.util.module_from_spec(spec)
            sys.dont_write_bytecode = True
            spec.loader.exec_module(module)
        except:
            import traceback
            traceback.print_exc()
        finally:
            sys.dont_write_bytecode = dont_write_bytecode
            if module_dir in sys.path:
                sys.path.remove(module_dir)


def GetQtAEMainWindow():
    global __MainWindow
    if __MainWindow is None:
        import win32gui
        __MainWindow = QWidget()
        win32gui.SetParent(__MainWindow.winId(), _ae.getMainHWND())
    return __MainWindow


def ShowPythonWindow():
    __PythonWindow.show()


__init_qt()
__PythonWindow = PythonWindow(GetQtAEMainWindow())
