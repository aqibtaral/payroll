from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import *
import sqlite3


class addEmployee(QDialog):
    """
    Dialog box to add a new employee.
    Fields:
    Name, Department, Designation, Salary, Salary Structure, Overtime rate, Working status
    """
    def __init__(self):
        super().__init__()
        self.data = {}
        
        self.widgets = []
        self.setWindowTitle("Add Employee")
        self.mainlayout = QGridLayout()
        self.name = QLineEdit()
        self.name.setObjectName("name")
        self.widgets.append(self.name)
        self.label1 = QLabel("Name:")
        self.label2 = QLabel("Department")
        self.depart = QComboBox()
        self.depart.setObjectName("depart")
        self.name.editingFinished.connect(lambda: self.depart.setFocus())
        self.widgets.append(self.depart)
        with sqlite3.connect('test2.db') as conn:
            self.departlist = conn.execute('select * from departments').fetchall()
        self.departlist = [x[0] for x in self.departlist]
        self.depart.addItems(self.departlist)
        self.depart.activated.connect(lambda: self.designation.setFocus())
        self.mainlayout.addWidget(self.name, 0, 1)
        self.mainlayout.addWidget(self.depart, 1, 1)
        self.mainlayout.addWidget(self.label1, 0, 0)
        self.mainlayout.addWidget(self.label2, 1, 0)
        self.label3 = QLabel("Designation")
        self.designation = QComboBox()
        self.designation.setObjectName("designation")
        self.designation.addItems(["Helper" ,"Operator"])
        self.mainlayout.addWidget(self.label3, 2, 0)
        self.designation.activated.connect(lambda: self.salary.setFocus())
        self.mainlayout.addWidget(self.designation,2,1)
        self.label4 = QLabel("Salary")
        self.salary = QLineEdit()
        self.salary.setObjectName("salary")
        self.salary.editingFinished.connect(lambda: self.salarystruct.setFocus())
        self.widgets.append(self.salary)
        self.label5 = QLabel("Salary Structure")
        self.salarystruct = QComboBox()
        self.salarystruct.setObjectName("salarystruct")
        self.salarystruct.addItems(["Monthly","Daily"])
        self.salarystruct.activated.connect(lambda: self.overtime.setFocus())
        self.label6 = QLabel("Overtime rate")
        self.overtime = QLineEdit()
        self.overtime.setObjectName("overtime")
        self.label7 = QLabel("Working Status")
        self.overtime.editingFinished.connect(lambda: self.working.setFocus())
        self.working = QComboBox()
        self.working.setObjectName("working")
        self.working.activated.connect(lambda: self.acceptbtn.setFocus())
        self.working.addItems(["Working","Resigned"])
        self.mainlayout.addWidget(self.label4, 3, 0)
        self.mainlayout.addWidget(self.salary, 3, 1)
        self.mainlayout.addWidget(self.label5, 4, 0)
        self.mainlayout.addWidget(self.salarystruct, 4, 1)
        self.mainlayout.addWidget(self.label6, 5, 0)
        self.mainlayout.addWidget(self.overtime, 5, 1)
        self.mainlayout.addWidget(self.label7, 6, 0)
        self.mainlayout.addWidget(self.working, 6, 1)
        self.acceptbtn = QPushButton("Add Employee")
        self.rejectbtn = QPushButton("Cancel")
        self.mainlayout.addWidget(self.acceptbtn,8,0)
        self.mainlayout.addWidget(self.rejectbtn,8,1)
        self.acceptbtn.clicked.connect(self.giveData)
        self.rejectbtn.clicked.connect(self.close)
        self.widgets.append(self.designation)
        self.widgets.append(self.salarystruct)
        self.widgets.append(self.working)
        self.widgets.append(self.overtime)
        self.setLayout(self.mainlayout)
    
    def giveData(self):
        for widget in self.widgets:
            try:
                self.data[widget.objectName()] = widget.currentText()
            except:
                self.data[widget.objectName()] = widget.text()
        self.close()