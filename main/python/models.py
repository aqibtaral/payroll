"""
ROOOM FOR IMPROVEMENT:
use QDates.. : https://www.ics.com/blog/how-display-dates-using-qdate

"""
from PySide2 import QtCore, QtGui, QtSql, QtWidgets
from PySide2.QtCore import QDate, Qt
import sys
import Definitions
import myobjects
import sqlite3
from collections import Counter
from calendar import monthrange
from datetime import datetime
import pprint

db = QtSql.QSqlDatabase.addDatabase('QSQLITE')

# THE DATABASE/ATTENDANCE TABLE??? WILL BE SEPARATE FOR EACH YEAR....
db.setDatabaseName('test2.db')
ok = db.open()


def employeeModel():
    model = QtSql.QSqlTableModel()
    model.setTable('employees')
    for i in range(model.columnCount()):
        model.setHeaderData(i, QtCore.Qt.Horizontal, Definitions.TableHeaders['employees'][i])
    model.select()
    return model


def departmentModel():
    model = QtSql.QSqlTableModel()
    model.setTable('departments')
    model.setHeaderData(0, QtCore.Qt.Horizontal, 'Department')
    model.select()
    return model


def attendanceModelData(year='2019', month='01', department='Talking', half=0):
    """
    Takes in month/depart/half and returns a model + delegate that can be set
    for a view and will display the attendance for that month/depart in the
    table format with each cell representing a record in our 'attendance' table.

    
    """
    # SELECT date,department,"empname",status,"overtimeworked" FROM attendance INNER JOIN employees on
    # employees.empid = attendance.empid

    with sqlite3.connect("test2.db") as conn:
        cur = conn.cursor()
        # Note: in this query I tried doing LIKE "%-:month-%" but i guess the :month was not being replaced by the value in dict and instead being used to filter for date literally.
        departdata = cur.execute('SELECT "empname",designation FROM employees WHERE department=:dep',
                                 {'dep': department})
        departdata = dict(departdata.fetchall())
        ids = cur.execute('SELECT "empname","empid" FROM employees WHERE department=:dep', {'dep': department})
        ids = dict(ids.fetchall())
        rawdata = cur.execute(
            'SELECT date,department,"empname",designation,status,"overtimeworked" FROM attendance INNER JOIN employees on employees.empid = attendance.empid WHERE department =:department AND date LIKE :month',
            {'department': department, 'month': f"{year}-{month}-%"})

    empdict = {}

    for row in rawdata.fetchall():
        try:
            empdict[row[2]].update({row[0]: (row[4], row[5])})  # datetime.strptime(row[0], "%Y-%m-%d")
        except KeyError:
            empdict[row[2]] = {row[0]: (row[4], row[5])}

    return empdict, departdata, ids


class newLoanAdjustmentModel(QtCore.QAbstractTableModel):
    def __init__(self):
        super().__init__()
        self.loadempids()

    def loadempids(self):
        with sqlite3.connect("test2.db") as conn:
            query = "SELECT * FROM loanadjustments where amount > 0"
            result = conn.execute(query).fetchall()
        self.employees = [myobjects.Employee(empid) for empid, _ in result]

    def rowCount(self, parent=QtCore.QModelIndex()):
        if parent.isValid():
            return 0
        return len(self.employees)

    def columnCount(self, parent=QtCore.QModelIndex()):
        if parent.isValid():
            return 0
        return 2

    def data(self, index, role):
        row, col = index.row(), index.column()
        if role == QtCore.Qt.DisplayRole:
            if col == 0:
                return self.employees[row].name
            if col == 1:
                return self.employees[row].loans

    def headerData(self, section, orientation, role):
        if role == QtCore.Qt.DisplayRole and orientation == QtCore.Qt.Horizontal:
            if section == 0:
                return "Name"
            elif section == 1:
                return "Amount"

    def setData(self, index, value, role):
        if role == QtCore.Qt.EditRole:
            row, col = index.row(), index.column()
            if col == 1 and value:
                amount = value
                empid = self.employees[row].id
                with sqlite3.connect("test2.db") as conn:
                    query = f"update loanadjustments set amount = {amount} where empid = {empid}"
                    conn.execute(query)
                self.loadempids()
                self.dataChanged.emit(index, index)
                return True
        return False

    def flags(self, index):
        if index.column() == 1:
            return QtCore.Qt.ItemIsEditable | super().flags(index)
        else:
            return super().flags(index)

    def sync(self):
        pass


def loanAdjustmentModel():
    """Deprecated?"""
    model = loanAdjustmentModelnew()
    model.setEditStrategy(model.OnManualSubmit)
    model.setTable('loanadjustments')
    model.setRelation(0, QtSql.QSqlRelation('employees', 'empid', 'empname'))

    for i in range(model.columnCount()):
        model.setHeaderData(i, QtCore.Qt.Horizontal, Definitions.TableHeaders['loanadjustments'][i])
    model.setFilter("amount > 0")
    model.select()
    return model


class salaryModel(QtCore.QAbstractTableModel):
    def __init__(self):
        super().__init__()
        self.month = '01'
        self.half = 0
        self.department = 'Finish'

    norecord = QtCore.Signal(str)

    @QtCore.Slot(int)
    def setMonth(self, month):
        self.month = f"{month + 1:02}"
        self.initEmployeePay()
        self.headerDataChanged.emit(QtCore.Qt.Horizontal, 0, self.columnCount() - 1)

    @QtCore.Slot(int)
    def setHalf(self, half):
        self.half = half
        self.initEmployeePay()
        self.headerDataChanged.emit(QtCore.Qt.Horizontal, 0, self.columnCount() - 1)

    @QtCore.Slot(str)
    def setDepartment(self, department):
        self.department = department
        """ if self.department == "Staff":
            model = staffSalaryModel()
            self.overtimedata = model.getOvertimeData(self.month,self.half) """
        self.initEmployees()
        self.initEmployeePay()
        self.headerDataChanged.emit(QtCore.Qt.Horizontal, 0, self.columnCount() - 1)

    def initEmployees(self):
        with sqlite3.connect('test2.db') as conn:
            empids = conn.execute('select empid from employees where department = :dept', {'dept': self.department})
        self.employees = [myobjects.Employee(empid[0]) for empid in empids]

    def initEmployeePay(self):
        norecordlist = []
        model = staffSalaryModel()
        self.overtimedata = model.getOvertimeData(int(self.month), self.half)

        for employee in self.employees:
            try:
                employee.setAttendanceHalf(self.month, self.half)
                employee.calculatePay()

            except TypeError:
                employee.initInfo()
                norecordlist.append(', '.join([employee.name, employee.designation]))
        if norecordlist:
            result = '\n'.join(norecordlist)
            self.norecord.emit(result)

    def rowCount(self, parent=QtCore.QModelIndex()):
        if parent.isValid():
            return 0
        return len(self.employees)

    def columnCount(self, parent=QtCore.QModelIndex()):
        if parent.isValid():
            return 0
        if self.department == "Production":
            return 7
        return 9

    def data(self, index, role):
        row, col = index.row(), index.column()
        if role == QtCore.Qt.DisplayRole:
            employee = self.employees[row]
            if employee.salary_interval == 'Daily' and not employee.department == "Production":
                if col == 0:
                    return employee.name
                elif col == 1:
                    return employee.dayspresent
                elif col == 2:
                    return employee.overtimehours
                elif col == 3:
                    return employee.overtimerate
                elif col == 4:
                    return f"{employee.normalpay}"
                elif col == 5:
                    return employee.overtimepay
                elif col == 6:
                    return employee.totalpay
                elif col == 7:
                    return employee.loans
                elif col == 8:
                    return employee.balance

            elif employee.salary_interval == 'Monthly' and not employee.department == "Production":
                if col == 0:
                    return self.overtimedata[row]["name"]
                elif col == 1:
                    return self.overtimedata[row]["dayspresent"]
                elif col == 2:
                    return self.overtimedata[row]["overtimehours"]
                elif col == 3:
                    return self.overtimedata[row]["overtimerate"]
                elif col == 4:
                    return "0"  # hardcoded 0 because Staff are not paid salary with rest of departments, only paid Overtime.
                elif col == 5:
                    return self.overtimedata[row]["overtimepay"]
                elif col == 6:
                    return self.overtimedata[row]["overtimepay"]
                elif col == 7:
                    return "0"
                elif col == 8:
                    return self.overtimedata[row]["overtimepay"]

            elif employee.department == "Production":
                if col == 0:
                    return employee.name
                elif col == 1:
                    return employee.meters
                elif col == 2:
                    return employee.redyeing
                elif col == 3:
                    return employee.salary
                elif col == 4:
                    return employee.totalpay
                elif col == 5:
                    return employee.loans
                elif col == 6:
                    return employee.balance

    def setData(self, index, value, role):
        if role == QtCore.Qt.EditRole:
            if index.column() == 7:
                id = self.employees[index.row()].id
                with sqlite3.connect("test2.db") as conn:
                    query = f"REPLACE INTO loanadjustments ( empid, amount ) VALUES ( {id}, {value} )"
                    conn.execute(query)
                self.setDepartment(self.department)  # acts as a pseudo update for the table
            self.dataChanged.emit(index, index)
            return True
        else:
            return False

    def headerData(self, section, orientation, role):
        if role == QtCore.Qt.DisplayRole and orientation == QtCore.Qt.Horizontal:
            if self.department.lower() == "production":
                if section == 0:
                    return "Name"
                elif section == 1:
                    return "Meters"
                elif section == 2:
                    return "Redyeing"
                elif section == 3:
                    return "Rate"
                elif section == 4:
                    return "Total"
                elif section == 5:
                    return "Loans"
                elif section == 6:
                    return "Balance"
            else:
                if section == 0:
                    return "Name"
                elif section == 1:
                    return "P.Days"
                elif section == 2:
                    return "Ov Hrs"
                elif section == 3:
                    return "Ov Rt"
                elif section == 4:
                    return "Nrml Sal"
                elif section == 5:
                    return "Ov Sal"
                elif section == 6:
                    return "Total"
                elif section == 7:
                    return "Loans"
                elif section == 8:
                    return "Balance"

    def getPrintData(self, department, month, half):
        BigData = []
        self.setDepartment(department)
        self.setMonth(month)
        self.setHalf(half)
        for row in range(self.rowCount()):
            tmp = []
            for col in range(self.columnCount()):
                tmp.append(str(self.data(self.index(row, col), QtCore.Qt.DisplayRole)))
            BigData.append(tmp)
        return BigData

    def flags(self, index):
        if index.column() == 7:
            return QtCore.Qt.ItemIsEditable | super().flags(index)
        else:
            return super().flags(index)


class salarySummaryModel(QtCore.QAbstractTableModel):
    def __init__(self, month='01', half=0):
        super().__init__()
        self.month = month
        self.half = half
        self.meters = 0
        self.redyeing = 0
        self.loadDepartments()
        self.initDepartments()
        self.OVERTIMEROW = self.rowCount() - 5
        self.PRODUCTIONROW1 = self.rowCount() - 4
        self.PRODUCTIONROW2 = self.rowCount() - 3

    def setMonth(self, month):
        self.month = f"{month + 1:02}"
        self.initDepartments()
        self.headerDataChanged.emit(QtCore.Qt.Horizontal, 0, self.columnCount() - 1)

    def setHalf(self, half):
        self.half = half
        self.initDepartments()
        self.headerDataChanged.emit(QtCore.Qt.Horizontal, 0, self.columnCount() - 1)

    def loadDepartments(self):
        with sqlite3.connect('test2.db') as conn:
            deps = conn.execute('select * from departments where not department in ("Staff", "Production")').fetchall()
            self.departments = [myobjects.Department(x[0]) for x in deps]

    def initDepartments(self):
        for department in self.departments:
            department.setMonth(self.month)
            department.setHalf(self.half)
            department.loadEmployees()
            department.calculateFinances()
        self.getProductionData()
        self.getStaffOvertime()

    def getProductionData(self):
        self.proddata = []
        prod = myobjects.Department("Production")
        for emp in prod.employees:
            tmp = {}
            emp.setAttendanceHalf(self.month, self.half)
            emp.calculatePay()
            tmp["name"] = emp.name
            self.meters = emp.meters
            self.redyeing = emp.redyeing
            tmp["total"] = emp.totalpay
            tmp["balance"] = emp.balance
            tmp["loans"] = emp.loans
            self.proddata.append(tmp)

    def getStaffOvertime(self):
        model = staffSalaryModel()
        self.ovt = model.getOvertimeData(int(self.month), self.half)

    def rowCount(self, parent=QtCore.QModelIndex()):
        """
        DO NOT KNOW WHY parent=QtCore.QModelIndex() THIS IS HERE BUT JUST ACCEPT IT..
        """
        if parent.isValid():
            return 0
        return len(self.departments) + 5

    def columnCount(self, parent=QtCore.QModelIndex()):
        """
        DO NOT KNOW WHY parent=QtCore.QModelIndex() THIS IS HERE BUT JUST ACCEPT IT..
        DEPARTMENT_NAME    TOTAL   LESS_LOAN   BALANCE
        """
        if parent.isValid():
            return 0
        return 4

    def data(self, index, role):
        row, col = index.row(), index.column()
        if role == QtCore.Qt.DisplayRole:
            if row == self.OVERTIMEROW:
                if col == 0:
                    return "Staff Overtime"
                elif col == 1:
                    return self.ovt[-1]
                elif col == 2:
                    return "0"
                elif col == 3:
                    return self.ovt[-1]
            elif row in (self.PRODUCTIONROW1, self.PRODUCTIONROW2):
                if col == 0:
                    return self.proddata[row - self.rowCount() + 2]["name"]
                elif col == 1:
                    return self.proddata[row - self.rowCount() + 2]["total"]
                elif col == 2:
                    return self.proddata[row - self.rowCount() + 2]["loans"]
                elif col == 3:
                    return self.proddata[row - self.rowCount() + 2]["balance"]
            elif row == self.rowCount() - 2:
                if col == 0:
                    return "Meters"
                if col == 1:
                    return self.meters
                else:
                    return 0
            elif row == self.rowCount() - 1:
                if col == 0:
                    return "Redyeing"
                if col == 1:
                    return self.redyeing
                else:
                    return 0
            else:
                if col == 0:
                    return self.departments[row].name
                elif col == 1:
                    return self.departments[row].totalsalary
                elif col == 2:
                    return f'{self.departments[row].totalloans} '
                elif col == 3:
                    return self.departments[row].totalbalance

    def headerData(self, section, orientation, role):
        if role == QtCore.Qt.DisplayRole and orientation == QtCore.Qt.Horizontal:
            if section == 0:
                return 'Depart'
            elif section == 1:
                return 'Total Sal'
            elif section == 2:
                return 'Less Loan'
            elif section == 3:
                return 'Total Bal'

    def getPrintData(self, month, half):
        self.setHalf(half)
        self.setMonth(month)
        BigData = []
        totalsal, totalloan, totalbal = 0, 0, 0
        for row in range(self.rowCount()):
            tmp = []
            for col in range(self.columnCount()):
                if col == 0:
                    tmp.append(self.data(self.index(row, col), QtCore.Qt.DisplayRole))
                else:
                    value = round(float(self.data(self.index(row, col), QtCore.Qt.DisplayRole)))
                    tmp.append(value)
                    if self.data(self.index(row, 0), QtCore.Qt.DisplayRole) in ("Meters", "Redyeing"):
                        continue
                    if col == 1:
                        totalsal += value
                    if col == 2:
                        totalloan += value
                    if col == 3:
                        totalbal += value
            BigData.append(tmp)
        BigData.append(["TOTAL", f'{totalsal}', f'{totalloan}', f'{totalbal}'])
        return BigData


class attendanceModel(QtCore.QAbstractTableModel):
    """
    Doing with Employee objects.
    """

    def __init__(self, month, department, year=2019, half=0):
        super().__init__()
        self.month = month
        self.year = year
        self.half = half
        self.department = department
        self.load_data()

    editCompleted = QtCore.Signal(str)

    @QtCore.Slot(int)
    def setMonth(self, newmonth):
        self.month = f"{newmonth + 1:02}"
        self.load_data()
        self.headerDataChanged.emit(QtCore.Qt.Horizontal, 0, self.columnCount() - 1)

    @QtCore.Slot(str)
    def setDept(self, newdept):
        self.department = newdept
        self.load_data()
        self.dataChanged.emit(self.index(0, 0), self.index(self.rowCount() - 1, self.columnCount() - 1))
        self.headerDataChanged.emit(QtCore.Qt.Horizontal, 0, self.columnCount() - 1)

    @QtCore.Slot(int)
    def setYear(self, newyear):
        self.year = newyear
        self.headerDataChanged.emit(QtCore.Qt.Horizontal, 0, self.columnCount() - 1)

    @QtCore.Slot(int)
    def setHalf(self, newhalf):
        self.half = newhalf
        for employee in self.employees:
            employee.setAttendanceHalf(self.month, self.half)
        self.headerDataChanged.emit(QtCore.Qt.Horizontal, 0, self.columnCount() - 1)

    def load_data(self):
        """
        updates the current cell's data.
        IMPROVEMENT, DONT CALL THIS ON EVERY CELL UPDATE, instead just call datachanged on one cell.
        """
        with sqlite3.connect('test2.db') as conn:
            employeeids = conn.execute('select empid from employees where department =:dep', {'dep': self.department})
            self.employees = [myobjects.Employee(empid[0]) for empid in employeeids.fetchall()]
        for employee in self.employees:
            employee.setAttendanceDict(self.month, self.year)
            employee.setAttendanceHalf(self.month, self.half)
            # employee.calculatePay()

    def rowCount(self, parent=QtCore.QModelIndex()):
        if parent.isValid():
            return 0
        return len(self.employees)

    def columnCount(self, parent=QtCore.QModelIndex()):
        if parent.isValid():
            return 0
        if self.department == "Production":
            return 4
        lengthofmonth = monthrange(self.year, int(self.month))[1]
        return 7 + (15 if self.half == 0 else lengthofmonth - 15)

    def data(self, index, role):
        row, col = index.row(), index.column()
        if role == QtCore.Qt.DisplayRole:
            if self.department == "Production":
                if col == 0:
                    return self.employees[row].name
                elif col == 1:
                    return self.employees[row].designation
                elif col == 2:
                    return self.employees[row].meters
                elif col == 3:
                    return self.employees[row].redyeing
            else:
                try:
                    if col == 0:
                        return self.employees[row].name
                    elif col == 1:
                        return self.employees[row].designation
                    elif col == self.columnCount() - 1:
                        # Total Calculated based on adjacent column data
                        return int(self.data(self.index(row, col - 1), QtCore.Qt.DisplayRole)) + int(
                            self.data(self.index(row, col - 2), QtCore.Qt.DisplayRole))

                    elif col == self.columnCount() - 2:
                        # Overtime Amount Rs
                        return self.employees[row].overtimehours * self.employees[row].overtimerate
                    elif col == self.columnCount() - 3:
                        # Daily Earned Rs
                        return self.employees[row].dayspresent * self.employees[row].salary if self.employees[
                                                                                                   row].salary_interval == "Daily" else 0
                    elif col == self.columnCount() - 4:
                        # Overtime total
                        return self.employees[row].overtimehours
                    elif col == self.columnCount() - 5:
                        # Present Days
                        return self.employees[row].dayspresent
                except:
                    return 0
                if col in range(2, self.columnCount() - 2):
                    date = self.getdate(index)
                    try:
                        return str(self.employees[row].attendance[date])
                    except KeyError:
                        return " - "
        if role == QtCore.Qt.BackgroundRole:
            if col in range(self.columnCount() - 5, self.columnCount()):
                return QtGui.QBrush(QtCore.Qt.GlobalColor.white)
            elif col not in (0, 1):
                if self.getdate(index, 'obj').weekday() == 6:
                    return QtGui.QBrush(QtCore.Qt.yellow)

    def headerData(self, section, orientation, role):
        if role == QtCore.Qt.DisplayRole and orientation == QtCore.Qt.Horizontal:
            if self.department == "Production":
                if section == 0:
                    return "Employee Name"
                elif section == 1:
                    return "Designation"
                elif section == 2:
                    return "Meters"
                elif section == 3:
                    return "Redyeing"
            else:
                if section == 0:
                    return "Employee Names"
                elif section == 1:
                    return "Dsgntn"
                elif section == self.columnCount() - 5:
                    return "#Days"
                elif section == self.columnCount() - 4:
                    return "#Hrs"
                elif section == self.columnCount() - 3:
                    return "Daily"
                elif section == self.columnCount() - 2:
                    return "Ov Amt"
                elif section == self.columnCount() - 1:
                    return "Total"

                else:
                    index = self.index(0, section)
                    date = self.getdate(index, 'obj')
                    dformat = '%d / %a'
                    return datetime.strftime(date, dformat)
        """ if role == QtCore.Qt.FontRole and orientation == QtCore.Qt.Horizontal:
            F = QtGui.QFont()
            F.setBold(True)
            return F """

    def getdate(self, index, returntype='str'):
        """
        returns the date that the current index corresponds to in either string format or datetime object based on
        the value of returntype parameter.
        returntype one of: 
                        'str' : return as string. This is default.
                        'obj' : return as datetime object. to get custom formatting / colors for weekdays..
                        
        """
        if index.column() == -1:
            return datetime.now().date()
        day = index.column() - 1 + 15 * self.half
        # {day:02} is the way in python3 fstrings to pad an integer to a certain length, using {day:2} pads with a space instead of a 0.
        date = f"{self.year}-{self.month}-{day:02}"
        if returntype == 'str':
            return date
        elif returntype == 'obj':
            return datetime.strptime(date, '%Y-%m-%d')

    def setData(self, index, value, role):
        """
        Expects input value to be as a tuple (status, overtime)
        """
        if role == QtCore.Qt.EditRole:
            row, col = index.row(), index.column()
            """ if col in range(self.columnCount() -5,self.columnCount()):
                return False """
            date = self.getdate(index)
            _id = self.employees[row].id
            if self.department == "Production":
                if col == 2:
                    # Meters
                    with sqlite3.connect("test2.db") as conn:
                        cur = conn.cursor()
                        query = f'UPDATE production SET meters={value} WHERE empid ={_id} AND month="{self.month}" AND half={self.half}'  # prone to injection xd
                        asd = cur.execute(query)
                        _ = cur.execute(
                            'INSERT OR IGNORE INTO production(empid,month,half,meters) values (:id,:month,:half,:meters)',
                            {'meters': value, 'id': _id, 'month': self.month, 'half': self.half})
                elif col == 3:
                    # Redyeing
                    with sqlite3.connect("test2.db") as conn:
                        cur = conn.cursor()
                        asd = cur.execute(
                            'UPDATE production SET redyeing=:redyeing WHERE empid =:id AND month=:month AND half=:half ',
                            {'redyeing': value, 'id': _id, 'month': self.month, 'half': self.half})
                        _ = cur.execute(
                            'INSERT OR IGNORE INTO production(empid,month,half,redyeing) values (:id,:month,:half,:redyeing)',
                            {'redyeing': value, 'id': _id, 'month': self.month, 'half': self.half})
                self.employees[row].setAttendanceDict(self.month, self.year)
                self.employees[row].setAttendanceHalf(self.month, self.half)
                self.dataChanged.emit(index, index)

            else:
                status, overtime = value.split(',')  # THIS IS FRAGILE .. NEEDS FIXING........
                status = status.upper()
                with sqlite3.connect("test2.db") as conn:
                    cur = conn.cursor()
                    asd = cur.execute(
                        'UPDATE attendance SET status=:status,"overtimeworked"=:overtime WHERE empid =:id AND date=:date ',
                        {'status': status, 'overtime': overtime, 'id': _id, 'date': date})
                    _ = cur.execute(
                        'INSERT OR IGNORE INTO attendance(empid,date,status,"overtimeworked") values (:id,:date,:status,:overtime )',
                        {'status': status, 'overtime': overtime, 'id': _id, 'date': date})
                # self.load_data() # testing to see if the table updates properly without loading the entire table again...
                self.employees[row].setAttendanceDict(self.month, self.year)
                self.employees[row].setAttendanceHalf(self.month, self.half)
                self.dataChanged.emit(index,
                                      index)  # This recalls the data function on all cells bounded by the rectangle (topleft,bottomright) which is (index,index) but since our data function has no way to see the updated database, the tableview doesnt update...comment might be outdated... lol
            return True
        else:
            return False

    def flags(self, index):
        if self.department == "Production" and index.column() not in (0, 1):
            return QtCore.Qt.ItemIsEditable | super().flags(index)
        elif index.column() not in (0, 1, self.columnCount() - 1, self.columnCount() - 2):
            return QtCore.Qt.ItemIsEditable | super().flags(index)
        else:
            return super().flags(index)


class oldTransactionModel(QtCore.QAbstractTableModel):
    def __init__(self, department='Gray', startdate='2019-01-01', enddate='2019-02-01'):
        super().__init__()
        self.department = myobjects.Department(department)
        self.startdate = startdate
        self.enddate = enddate
        self.employees = self.department.employees
        self.empids = [employee.id for employee in self.employees]
        self.setTransactions()

    @QtCore.Slot(str)
    def setendDate(self, enddate):
        # print(enddate.toPython())
        self.enddate = enddate.toPython()
        self.setTransactions()

    def deletetransaction(self, index):
        transid = self.displaydata[index.row()]['transid']
        with sqlite3.connect('test2.db') as conn:
            conn.execute(f'delete from transactions where "transaction-id" = {transid}')
        self.setTransactions()

    @QtCore.Slot(str)
    def setstartDate(self, startdate):
        # print("startdate:",startdate)
        self.startdate = startdate.toPython()
        self.setTransactions()

    @QtCore.Slot(str)
    def setDepartment(self, department):
        # print(department)
        self.department = myobjects.Department(department)
        self.employees = self.department.employees
        self.empids = [employee.id for employee in self.employees]
        self.setTransactions()

    def setTransactions(self):

        with sqlite3.connect('test2.db') as conn:
            # {'empids':self.empids, 'startdate': f"{self.startyear}-{self.startmonth:02}-{self.startday:02}" ,'enddate': f"{self.endyear}-{self.endmonth:02}-{self.endday:02}"}
            query = f"SELECT * FROM transactions WHERE empid in ({','.join(['?'] * len(self.empids))}) and date between '{self.startdate}' and '{self.enddate} order by date desc'"
            self.transactiondata = conn.execute(query, self.empids).fetchall()

            # transactiondata = conn.execute('select * from transactions where empid in (:empids) and date between :startdate and :enddate',{'startdate':self.startdate,'enddate':self.enddate,'empids':self.empids})

        self.displaydata = []
        for x in self.transactiondata:
            tmp = {}
            tmp['transid'] = x[0]
            tmp['empname'] = myobjects.Employee(x[1]).name
            tmp['date'] = x[2]
            tmp['amount'] = x[3]
            self.displaydata.append(tmp)

        self.headerDataChanged.emit(QtCore.Qt.Horizontal, 0, self.columnCount() - 1)

    def rowCount(self, parent=QtCore.QModelIndex()):
        if parent.isValid():
            return 0
        return len(self.transactiondata)

    def columnCount(self, parent=QtCore.QModelIndex()):
        if parent.isValid():
            return 0
        return 3

    def data(self, index, role):
        row, col = index.row(), index.column()
        if role == QtCore.Qt.DisplayRole:
            if col == 0:
                return self.displaydata[row]['empname']
            elif col == 1:
                return self.displaydata[row]['amount']
            elif col == 2:
                return self.displaydata[row]['date']

    def headerData(self, section, orientation, role):
        if role == QtCore.Qt.DisplayRole and orientation == QtCore.Qt.Horizontal:
            if section == 0:
                return "Name"
            if section == 1:
                return "Loan Amount"
            if section == 2:
                return "Date"

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
            self.dataChanged.emit(index, index)
            return True
        return False

    def flags(self, index):
        if not index.column() == 0:
            return QtCore.Qt.ItemIsEditable | super().flags(index)
        else:
            return super().flags(index)


class newTransactionModel(QtCore.QAbstractTableModel):
    def __init__(self, employeeid):
        super().__init__()
        self.employee = myobjects.Employee(employeeid)
        self.getAllTransactions()

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
        self.headerDataChanged.emit(QtCore.Qt.Horizontal, 0, self.columnCount() - 1)
        # pprint.pprint(self.alltransactiondata)

    @QtCore.Slot(int)
    def setEmployee(self, empid):
        self.employee = myobjects.Employee(empid)
        self.getAllTransactions()

    # THE ROWCOUNT ISNT UPDATING WHEN WE INSERT A TRANSACTION??...????
    # This is the way to append information to table.. not reload the entire model... F
    @QtCore.Slot(object)
    def appendTransaction(self, data):
        """Appends the data at the end of table"""
        count = self.rowCount()
        self.beginInsertRows(QtCore.QModelIndex(), count, count)
        with sqlite3.connect('test2.db') as conn:
            _ = conn.execute(
                'insert into transactionsnew (empid, date, credit, debit) values (:empid, :date, :credit, :debit)',
                data)
        self.setEmployee(data['empid'])
        self.endInsertRows()

    def deletetransaction(self, index):
        self.beginRemoveRows(QtCore.QModelIndex(), 0, 0)
        transid = self.alltransactiondata[index.row()][0]
        with sqlite3.connect('test2.db') as conn:
            conn.execute(f'delete from transactionsnew where "id" = {transid}')
        self.getAllTransactions()
        self.endRemoveRows()

    def rowCount(self, parent=QtCore.QModelIndex()):
        if parent.isValid():
            return 0
        return len(self.alltransactiondata)

    def columnCount(self, parent=QtCore.QModelIndex()):
        if parent.isValid():
            return 0
        return 5

    def data(self, index, role):
        row, col = index.row(), index.column()
        if role == QtCore.Qt.DisplayRole:
            if col == 0:
                return QDate.fromString(self.alltransactiondata[row][1], QtCore.Qt.ISODate)
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
        """TO BE IMPLEMENTED.. MAYBE WITH THE SAME POPUL DIALOG UPON EDIT REQUEST. LIKE EMPLOYEE TABLE
        datawidgetmapper???
        """
        if role == QtCore.Qt.EditRole and not value == "":
            row, col = index.row(), index.column()
            transid = self.alltransactiondata[row][0]
            if col == 2:
                query = f'update transactionsnew set credit = {value} where id = {transid}'
                with sqlite3.connect('test2.db') as conn:
                    conn.execute(query)
            elif col == 3:
                query = f'update transactionsnew set debit = {value} where id = {transid}'
                with sqlite3.connect('test2.db') as conn:
                    conn.execute(query)
            """ elif col == 5:
                query = f'update transactionsnew set description = {value} where id = {transid}' """
            self.getAllTransactions()
            self.dataChanged.emit(index, index)
            return True
        return False

    def flags(self, index):
        # wtf should be 2,3 for credit debit
        if not index.column() in (0, 1):
            return QtCore.Qt.ItemIsEditable | super().flags(index)
        else:
            return super().flags(index)


class staffSalaryModel(QtCore.QAbstractTableModel):
    def __init__(self):
        super().__init__()
        self.employees = []
        self.getEmployees()
        self.setMonth(1)

    def getEmployees(self):
        with sqlite3.connect("test2.db") as conn:
            query = 'select empid from employees where "salaryint" = "Monthly" and department <> "Production"'
            emps = conn.execute(query).fetchall()
            if emps:
                self.employees = [myobjects.Employee(empid[0]) for empid in emps]

    @QtCore.Slot(int)
    def setMonth(self, month):
        self.month = f"{month + 1:02}"
        for emp in self.employees:
            emp.setAttendanceFull(self.month)
            emp.calculatePay()
        self.headerDataChanged.emit(QtCore.Qt.Horizontal, 0, self.columnCount() - 1)

    def rowCount(self, parent=QtCore.QModelIndex()):
        if parent.isValid():
            return 0
        return len(self.employees)

    def columnCount(self, parent=QtCore.QModelIndex()):
        if parent.isValid():
            return 0
        return 7

    def data(self, index, role):
        row, col = index.row(), index.column()
        if role == QtCore.Qt.DisplayRole:
            if col == 0:
                return self.employees[row].name
            if col == 1:
                return self.employees[row].salary
            if col == 2:
                return self.employees[row].daysabsent
            if col == 3:
                return int(self.employees[row].daysabsent * (self.employees[row].salary // 30))
            if col == 4:
                return self.employees[row].totalpay
            if col == 5:
                return self.employees[row].loans
            if col == 6:
                return self.employees[row].balance

    def headerData(self, section, orientation, role):
        if role == QtCore.Qt.DisplayRole and orientation == QtCore.Qt.Horizontal:
            if section == 0:
                return "Name"
            if section == 1:
                return "Salary"
            if section == 2:
                return "Absnt"
            if section == 3:
                return "Absnt cut"
            if section == 4:
                return "Total"
            if section == 5:
                return "Loan"
            if section == 6:
                return "Balance"

    def getPrintData(self, month):
        BigData = []
        self.setMonth(month)
        for row in range(self.rowCount()):
            tmp = []
            for col in range(self.columnCount()):
                tmp.append(str(self.data(self.index(row, col), QtCore.Qt.DisplayRole)))
            BigData.append(tmp)
        return BigData

    def getOvertimeData(self, month, half):
        """
        Gives the ALL staff's overtime data for the given half of the month.
        Do not call SetMonth coz its for the table with FULL month salary.
        """
        month = f"{month:02}"
        BigData = []
        total = 0
        for emp in self.employees:
            emp.setAttendanceHalf(month, half)
            if emp.overtimehours:  # and emp.department == "Staff" ( If we dont want to show department's staff overtime here):
                emp.calculatePay()
                tmp = {}
                tmp["name"] = emp.name
                tmp["overtimehours"] = emp.overtimehours
                tmp["overtimepay"] = emp.overtimepay
                tmp["overtimerate"] = emp.overtimerate
                tmp["dayspresent"] = emp.dayspresent
                total += emp.overtimepay
                BigData.append(tmp)
        BigData.append(total)
        return BigData


class MyFilterModel(QtCore.QSortFilterProxyModel):
    """This is for the transaction page to filter dates"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.minDate = QDate.fromString('2019-01-01', QtCore.Qt.ISODate)
        self.maxDate = QDate(datetime.now())

    def setFilterDate(self, minDate, maxDate):
        self.minDate = QDate.fromString(minDate, QtCore.Qt.ISODate)
        self.maxDate = QDate.fromString(maxDate, QtCore.Qt.ISODate)
        self.invalidateFilter()

    def filterAcceptsRow(self, sourceRow, sourceParent):
        dateindex = self.sourceModel().index(sourceRow, 0, sourceParent)
        return (self.dateInRange(self.sourceModel().data(dateindex, QtCore.Qt.DisplayRole)))

    def dateInRange(self, date):
        if isinstance(date, QtCore.QDateTime):
            date = date.date()

        return ((not self.minDate.isValid() or date >= self.minDate)
                and (not self.maxDate.isValid() or date <= self.maxDate))


class productionModel(QtCore.QAbstractTableModel):
    """This is for the attendance table to display if department is set to
    production
    ::::: pointless? since we just fixed the delegate..
    """

    def __init__(self):
        super().__init__()
        self.loadProductionData()
        self.month = "01"
        self.setHalf(0)

    def loadProductionData(self):
        self.production = myobjects.Department("Production").employees

    @QtCore.Slot(int)
    def setHalf(self, half):
        self.half = half
        for emp in self.production:
            emp.setAttendanceHalf(self.month, self.half)

    @QtCore.Slot(int)
    def setMonth(self, month):
        month = f"{month:02}"
        self.month = month
        for emp in self.production:
            emp.setAttendanceHalf(self.month, self.half)

    def rowCount(self, parent=QtCore.QModelIndex()):
        if parent.isValid():
            return 0
        return len(self.production)

    def columnCount(self, parent=QtCore.QModelIndex()):
        if parent.isValid():
            return 0
        return 3

    def data(self, index, role):
        row, col = index.row(), index.column()
        if role == QtCore.Qt.DisplayRole:
            if col == 0:
                return self.production[row].name
            elif col == 1:
                return self.production[row].meters
            elif col == 2:
                return self.production[row].redyeing

    def headerData(self, section, orientation, role):
        if role == QtCore.Qt.DisplayRole and orientation == QtCore.Qt.Horizontal:
            if section == 0:
                return "Name"
            if section == 1:
                return "Meters"
            if section == 2:
                return "Redyeing"

    def setData(self, index, value, role):
        row, col = index.row(), index.column()
        if role == QtCore.Qt.EditRole:
            _id = self.production[row].id
            if col == 2:
                # Meters
                with sqlite3.connect("test2.db") as conn:
                    cur = conn.cursor()
                    asd = cur.execute(
                        'UPDATE production SET meters=:meters WHERE empid =:id AND month=:month AND half=:half ',
                        {'meters': value, 'id': _id, 'month': self.month, 'half': self.half})
                    _ = cur.execute(
                        'INSERT OR IGNORE INTO production(empid,month,half,meters) values (:id,:month,:half,:meters)',
                        {'meters': value, 'id': _id, 'month': self.month, 'half': self.half})
            elif col == 3:
                # Redyeing
                with sqlite3.connect("test2.db") as conn:
                    cur = conn.cursor()
                    asd = cur.execute(
                        'UPDATE production SET redyeing=:redyeing WHERE empid =:id AND month=:month AND half=:half ',
                        {'redyeing': value, 'id': _id, 'month': self.month, 'half': self.half})
                    _ = cur.execute(
                        'INSERT OR IGNORE INTO production(empid,month,half,redyeing) values (:id,:month,:half,:redyeing)',
                        {'redyeing': value, 'id': _id, 'month': self.month, 'half': self.half})
                self.production[row].setAttendanceHalf(self.month, self.half)
                self.dataChanged.emit(index, index)

            return True
        return False

    def flags(self, index):
        if index.column() in (1, 2):
            return QtCore.Qt.ItemIsEditable | super().flags(index)
        else:
            return super().flags(index)


################################
# TESTING AREA 
################################  
# model = attendanceModel2('01','Finish',2019,0)
""" model = staffSalaryModel() 
model.getOvertimeData(1,0)
 app = QtWidgets.QApplication()
view = QtWidgets.QTableView()
view.setModel(model)
view.showMaximized()
exitcode = app.exec_()
sys.exit(exitcode) """
# model = departmentModel()
# model = salaryModel()
# model.norecord.connect(lambda x: QtWidgets.QMessageBox.warning(view,"ERROR",f"No attendance record found for \n {x}"))
# model.initEmployeePay()
# view.show()
