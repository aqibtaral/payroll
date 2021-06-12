# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'displaytransaction.ui',
# licensing of 'displaytransaction.ui' applies.
#
# Created: Mon Jul 15 08:00:14 2019
#      by: pyside2-uic  running on PySide2 5.12.1
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(388, 343)
        Dialog.setAutoFillBackground(False)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.label_4 = QtWidgets.QLabel(Dialog)
        self.label_4.setObjectName("label_4")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_4)
        self.fromdate = QtWidgets.QLineEdit(Dialog)
        self.fromdate.setClearButtonEnabled(True)
        self.fromdate.setObjectName("fromdate")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.fromdate)
        self.label_6 = QtWidgets.QLabel(Dialog)
        self.label_6.setObjectName("label_6")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_6)
        self.todate = QtWidgets.QLineEdit(Dialog)
        self.todate.setClearButtonEnabled(True)
        self.todate.setObjectName("todate")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.todate)
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setObjectName("label")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.label)
        self.department = QtWidgets.QComboBox(Dialog)
        self.department.setObjectName("department")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.department)
        self.label_2 = QtWidgets.QLabel(Dialog)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.employee = QtWidgets.QListWidget(Dialog)
        self.employee.setObjectName("employee")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.employee)
        self.verticalLayout.addLayout(self.formLayout)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)
        self.verticalLayout_2.addLayout(self.verticalLayout)
        self.label_4.setBuddy(self.fromdate)
        self.label_6.setBuddy(self.todate)
        self.label.setBuddy(self.department)
        self.label_2.setBuddy(self.employee)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtWidgets.QApplication.translate("Dialog", "New Transaction", None, -1))
        self.label_4.setText(QtWidgets.QApplication.translate("Dialog", "From:", None, -1))
        self.fromdate.setInputMask(QtWidgets.QApplication.translate("Dialog", "00-00-00", None, -1))
        self.fromdate.setText(QtWidgets.QApplication.translate("Dialog", "--", None, -1))
        self.label_6.setText(QtWidgets.QApplication.translate("Dialog", "To:", None, -1))
        self.todate.setInputMask(QtWidgets.QApplication.translate("Dialog", "00-00-00", None, -1))
        self.label.setText(QtWidgets.QApplication.translate("Dialog", "Department", None, -1))
        self.label_2.setText(QtWidgets.QApplication.translate("Dialog", "Employee", None, -1))

