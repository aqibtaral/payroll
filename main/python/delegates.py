from PySide2 import QtCore, QtWidgets, QtGui
import sys
from models import attendanceModel
import pprint
from PySide2.QtGui import QRegExpValidator
from PySide2.QtCore import QRegExp


class AttendanceEditorWidget(QtWidgets.QWidget):


    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QtWidgets.QHBoxLayout(self)
        self.line1 = QtWidgets.QLineEdit(self)
        self.line2 = QtWidgets.QLineEdit(self)
        self.line1.setMinimumSize(2,2)
        self.line2.setMinimumSize(2,2)
        rx1 = QRegExp("[aApPlL]")
        self.line1.setValidator(QRegExpValidator(rx1))
        self.layout.setContentsMargins(1,0,0,1)
        self.layout.setSpacing(0)
        self.layout.addWidget(self.line1)
        self.layout.addWidget(self.line2)
        self.line2.setMaxLength(2)
        self.line1.setText('P')
        self.line2.setText('0')
        self.line1.textChanged.connect(self.line2.setFocus)
        # self.line1.setFocus()
        self.setFocusProxy(self.line1)
    

class AllDelegateShit(QtWidgets.QStyledItemDelegate):
    def __init__(self, parent):
        return super().__init__(parent)
    
    def createEditor(self, parameter_list):
        pass

    def displayText(self, parameter_list):
        pass

    def editorEvent(self, parameter_list):
        pass

    def eventFilter(self, parameter_list):
        pass
    
    def initStyleOption(self, parameter_list):
        pass
        
    def itemEditorFactory(self, parameter_list):
        pass
    def paint(self, parameter_list):
        pass

    def setEditorData(self, parameter_list):
        pass
          
        


class attendanceDelegate(QtWidgets.QStyledItemDelegate):
    def __init__(self, parent = None):
        self.parent = parent
        QtWidgets.QStyledItemDelegate.__init__(self, parent)


    def sizeHint(self, option, index):
        return 2*QtCore.QSize(5,5)
        
    def createEditor(self, parent, option, index):
        """
        This returns the widget that the View will use when user requests to edit the given index of model.
        """
        editor = AttendanceEditorWidget(parent)
        editor.installEventFilter(self)
        """ atten, ovt = index.data(QtCore.Qt.DisplayRole)
        editor.line1.setText(atten)
        editor.line2.setText(ovt) """
        return editor
    
    def eventFilter(self, editor, event):
        if event.type() == QtCore.QEvent.KeyPress and event.key() in (QtCore.Qt.Key_Return,QtCore.Qt.Key_Enter):
            if editor.line1.hasFocus():
                editor.line2.setFocus()
                editor.line2.selectAll()
                return True
        return super().eventFilter(editor,event)

    def setModelData(self, editor, model, index):
        """
        This sets the model data by extracting relevant data 
        from the editor which is the widget that was displayed 
        to the user when user was editing. Doesnt return anything.
        """
        atten = editor.line1.text()
        ovt = editor.line2.text()
        data = f"{atten},{ovt}"
        model.setData(index, data, QtCore.Qt.EditRole)


""" model = attendanceModel("01","Gray")
#model.getOvertimeData(1,0)

app = QtWidgets.QApplication()
#w = AttendanceEditorWidget()
#w.show()
view = QtWidgets.QTableView()
view.setModel(model)
view.setTabKeyNavigation(False)
atndel = attendanceDelegate(view)
view.setItemDelegate(atndel)
view.doubleClicked.connect(view.resizeColumnsToContents)
view.show()
exitcode = app.exec_()
sys.exit(exitcode) """