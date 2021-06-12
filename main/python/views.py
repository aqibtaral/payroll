from PySide2 import QtWidgets, QtCore, QtGui
import sys
from models import attendanceModel
from delegates import attendanceDelegate


# https://github.com/kevinfol/QtSpreadSheet/tree/08d57025bab7f0addf7ea37843b0ed7eb3682a54/QtSpreadSheet

class attendanceTableView(QtWidgets.QTableView):
    def __init__(self, parent=None, model=attendanceModel('01', 'Finish')):
        """
        This init method is unnecessary since everything is being manually set in the mainwindow's init Ui anyway.
        """
        super().__init__(parent)
        self.attenmodel = model
        self.setModel(self.attenmodel)
        self.delegate = attendanceDelegate()
        self.setItemDelegate(self.delegate)
        self.delegate.closeEditor.connect(self.setFocus)  # its being overwritten

    def keyPressEvent(self, event):
        """Custom Keypress Event for a tableview
        that replicates the functionallity of a spreadsheet
        software like excel for pressing the enter key.
        it enables editing and moves to the next row rather than column
        """
        if event.key() in (QtCore.Qt.Key_Tab, QtCore.Qt.Key_Backtab):
            return
        elif event.key() in (QtCore.Qt.Key_Return, QtCore.Qt.Key_Enter):
            # Qt.Key_Return refers to BIG enter key in the middle of keyboard
            # Qt.Key_Enter is the numpad enter key
            # we captured the Enter key press, now we need to move to the next row
            nNextRow = self.currentIndex().row() + 1
            nNextColumn = self.currentIndex().column()
            if nNextRow == self.model().rowCount():
                # we are all the way down, we can't go any further
                nNextRow = 0
                nNextColumn = self.currentIndex().column() + 1
                if nNextColumn == self.model().columnCount():
                    nNextColumn -= 1

            if self.state() == QtWidgets.QAbstractItemView.EditingState:
                # if we are editing, confirm and move to the row below
                oNextIndex = self.model().index(nNextRow, nNextColumn)
                self.setCurrentIndex(oNextIndex)
                self.selectionModel().select(oNextIndex, QtCore.QItemSelectionModel.ClearAndSelect)
            else:
                # if we're not editing, start editing
                self.edit(self.currentIndex())
        else:
            # any other key was pressed, inform base class
            super().keyPressEvent(event)


def keyPressEvent(self, event):
    """Custom Keypress Event for a tableview
        that replicates the functionallity of a spreadsheet
        software like excel for pressing the enter key.
    it enables editing and moves to the next row rather than column"""

    if event.key() == QtCore.Qt.Key_Return:
        # we captured the Enter key press, now we need to move to the next row
        nNextRow = self.currentIndex().row() + 1
        if nNextRow + 1 > self.model().rowCount(self.currentIndex()):
            # we are all the way down, we can't go any further
            nNextRow = nNextRow - 1

        if self.state() == QAbstractItemView.EditingState:
            # if we are editing, confirm and move to the row below
            oNextIndex = self.model().index(nNextRow, self.currentIndex().column())
            self.setCurrentIndex(oNextIndex)
            self.selectionModel().select(oNextIndex, QItemSelectionModel.ClearAndSelect)
        else:
            # if we're not editing, start editing
            self.edit(self.currentIndex())
    else:
        # any other key was pressed, inform base class
        QAbstractItemView.keyPressEvent(event)


""" app = QtWidgets.QApplication()
view = attendanceTableView()
view.showMaximized()
exitcode = app.exec_()
sys.exit(exitcode) """
