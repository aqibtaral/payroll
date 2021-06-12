from PySide2 import QtWidgets, QtCore, QtGui
from PySide2.QtCore import Qt
from PySide2.QtSql import (QSqlQuery, QSqlRelation, QSqlRelationalDelegate,
        QSqlRelationalTableModel, QSqlTableModel)
import sys
import sqlite3
import myobjects
from dataclasses import dataclass
import datetime
import pprint

# This is going to contain the Custom Model / Proxymodel / Tableview / widgetmapping/ sqlrelational bullshit and everything 
# relevant to transactions..

# model.setTable("transactions")
# model.setRelation(2, QSqlRelation('employees', 'empid', 'name')) the 2 corresponds to the field in transaction table
# name is what u retrieve from employees table
# Balance calculation query:


LUL = """SELECT date,"empname",
       credit, debit,
       (SELECT sum(debit - credit)
        FROM transactionsnew AS T2
        WHERE T2.date <= transactionsnew.date and T2.empid = 23
       ) AS cumulative_sum
FROM transactionsnew inner join employees on transactionsnew.empid = employees.empid where transactionsnew.empid = 23
ORDER BY date;"""



@dataclass(order=True)
class transactionRecord:
    id: int
    name: str
    date: datetime.datetime
    amount: int
    description: str = ''



class newTransactionModel(QtCore.QAbstractTableModel):
    def __init__(self, employeeid, daterange=[]):
        super().__init__()
        self.employee = myobjects.Employee(employeeid)
        self.getAllTransactions()
        #self.department = myobjects.Department(department)
        #self.startdate = startdate
        #self.enddate = enddate
        #self.employees = self.department.employees
        #self.empids = [employee.id for employee in self.employees]
        #self.setTransactions()

    def getAllTransactions(self):
        with sqlite3.connect('test2.db') as conn:
            query = f"""SELECT id,date,"empname", credit, debit, (SELECT sum(debit - credit)
            FROM transactionsnew AS T2
            WHERE T2.date <= transactionsnew.date and T2.empid = {self.employee.id}) AS cumulative_sum
            FROM transactionsnew inner join employees on transactionsnew.empid = employees.empid 
            WHERE transactionsnew.empid = {self.employee.id}
            ORDER BY date;"""
            result = conn.execute(query).fetchall()
        if result:
            self.alltransactiondata = result
        pprint.pprint(result)

    @QtCore.Slot(object)
    def setDateRange(self, daterange):
        #print(enddate.toPython())
        self.daterange = daterange #??????
        
        
    def deletetransaction(self, index):
        transid = self.displaydata[index.row()]['transid']
        with sqlite3.connect('test2.db') as conn:
            conn.execute(f'delete from transactions where "transaction-id" = {transid}')   

    def rowCount(self,parent=QtCore.QModelIndex()):
        if parent.isValid():
            return 0
        return len(self.alltransactiondata)

    def columnCount(self,parent=QtCore.QModelIndex()):
        if parent.isValid():
            return 0
        return 5

    def data(self, index, role):
        row, col = index.row(), index.column()
        if role == QtCore.Qt.DisplayRole:
            if col == 0:
                return self.alltransactiondata[row][1]
            elif col == 1:
                return self.alltransactiondata[row][2]
            elif col == 2:
                return self.alltransactiondata[row][3]
            elif col == 3:
                return self.alltransactiondata[row][4]
            elif col == 4:
                return self.alltransactiondata[row][5]


    def headerData(self, section, orientation, role):
        if role == QtCore.Qt.DisplayRole and orientation == QtCore.Qt.Horizontal:
            if section == 0:
                return "Date"
            if section == 1:
                return "Name"
            if section == 2:
                return "Credit"
            if section == 3:
                return "Debit"
            if section == 4:
                return "Balance"
            if section == 5:
                return "Description"

    def setData(self, index, value, role):
        if role == QtCore.Qt.EditRole:
            row, col = index.row(), index.column()
            transid = self.transactiondata[row][0]
            if col == 1:
                query = f'update transactions set amount = {value} where "transaction-id" = {transid}'
                with sqlite3.connect('test2.db') as conn:
                    conn.execute(query)
            elif col == 2:
                query = f'update transactions set date = {value} where "transaction-id" = {transid}'
                with sqlite3.connect('test2.db') as conn:
                    conn.execute(query)
            self.setTransactions()
            self.dataChanged.emit(index,index)
            return True
        return False

    def flags(self, index):
        # if not index.column() == 0:
        #     return QtCore.Qt.ItemIsEditable | super().flags(index)
        # else:
        return super().flags(index)




""" proxy = QtCore.QSortFilterProxyModel()



app = QtWidgets.QApplication()
view = QtWidgets.QTableView()
view.setModel(newTransactionModel(23))
view.show()
exitcode = app.exec_()
sys.exit(exitcode) 
 """