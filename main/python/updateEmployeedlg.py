from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import *
import sqlite3


class updateEmployee(QWidget):
    """
    Dialog box to add a new employee.
    Fields:
    Name, Department, Designation, Salary, Salary Structure, Overtime rate, Working status
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Update Employee Info")
        self.mainlayout = QGridLayout()
        self.name = QLineEdit()
        self.name.setObjectName("name")
        self.label1 = QLabel("Name:")
        self.label2 = QLabel("Department")
        self.depart = QComboBox()
        self.depart.setObjectName("depart")
        with sqlite3.connect('test2.db') as conn:
            self.departlist = conn.execute('select * from departments').fetchall()
        self.departlist = [x[0] for x in self.departlist]
        self.depart.addItems(self.departlist)
        self.mainlayout.addWidget(self.name, 0, 1)
        self.mainlayout.addWidget(self.depart, 1, 1)
        self.mainlayout.addWidget(self.label1, 0, 0)
        self.mainlayout.addWidget(self.label2, 1, 0)
        self.label3 = QLabel("Designation")
        self.designation = QComboBox()
        self.designation.setObjectName("designation")
        self.designation.addItems(["Helper" ,"Operator"])
        self.mainlayout.addWidget(self.label3, 2, 0)
        self.mainlayout.addWidget(self.designation,2,1)
        self.label4 = QLabel("Salary")
        self.salary = QLineEdit()
        self.salary.setObjectName("salary")
        self.label5 = QLabel("Salary Structure")
        self.salarystruct = QComboBox()
        self.salarystruct.setObjectName("salarystruct")
        self.salarystruct.addItems(["Monthly","Daily"])
        self.label6 = QLabel("Overtime rate")
        self.overtime = QLineEdit()
        self.overtime.setObjectName("overtime")
        self.label7 = QLabel("Working Status")
        self.working = QComboBox()
        self.working.setObjectName("working")
        self.working.addItems(["Working","Resigned"])
        self.rejectbtn = QPushButton("Close")
        self.mainlayout.addWidget(self.label4, 3, 0)
        self.mainlayout.addWidget(self.salary, 3, 1)
        self.mainlayout.addWidget(self.label5, 4, 0)
        self.mainlayout.addWidget(self.salarystruct, 4, 1)
        self.mainlayout.addWidget(self.label6, 5, 0)
        self.mainlayout.addWidget(self.overtime, 5, 1)
        self.mainlayout.addWidget(self.label7, 6, 0)
        self.mainlayout.addWidget(self.working, 6, 1)
        self.mainlayout.addWidget(self.rejectbtn,8,1)
        self.rejectbtn.clicked.connect(self.close)
        self.setLayout(self.mainlayout)
        self.name.setFocusProxy(self)
        
