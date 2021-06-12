from fbs_runtime.application_context.PySide2 import ApplicationContext
# from PySide2.QtWidgets import QMainWindow
from PySide2 import QtCore, QtGui, QtWidgets, QtSql, QtPrintSupport
import sys
import sqlite3
import mainPayrollWindow
import sys
from models import (employeeModel, attendanceModel, departmentModel,
                    salaryModel, salarySummaryModel, newTransactionModel,
                    staffSalaryModel, loanAdjustmentModel, MyFilterModel,
                    newLoanAdjustmentModel, productionModel)
from addEmployeedlg import addEmployee
from updateEmployeedlg import updateEmployee
from transactiondlg import newTransactionDialog, dispTransactionDialog
from printing import (makeDepartmentPdf, makeStaffSalaryPdf, makeProductionPdf,
                      makeSalarySummaryPdf, makeStaffOvertimePdf)
from myobjects import Employee, Department
from delegates import attendanceDelegate
from views import attendanceTableView
from datetime import datetime
import pprint

MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November',
          'December']
# TODO "INPUT VALIDATION, MODERN INPUT FORMS, DELEGATE SETUP "
"""
NOTES: I HAVE INTRODUCED THE CUSTOM TABLEVIEW INTO THE MAINPAYROLLWINDOW.PY FILE WHICH WILL GET OVERWRITTEN WHENEVER A CHANGE TO UI IS MADE...
from views import attendanceTableView
self.atntable = attendanceTableView(self.frame)
"""


class MainWindow(QtWidgets.QMainWindow):
    updateRequested = QtCore.Signal()

    def __init__(self):
        super().__init__()
        self.ui = mainPayrollWindow.Ui_MainWindow()
        self.ui.setupUi(self)
        with sqlite3.connect('test2.db') as conn:
            self.departments = conn.execute('SELECT department FROM departments').fetchall()
        self.departments = [x[0] for x in self.departments]
        self.initBeautification()
        self.ui.stack.setCurrentIndex(0)
        self.init_navbar()
        self.initUI()

    def initUI(self):
        self.empmodel = employeeModel()
        self.atnmodel = attendanceModel('01', 'Finish', 2019, 0)
        self.atndelegate = attendanceDelegate()
        self.proddelagate = QtWidgets.QStyledItemDelegate()
        self.deptmodel = departmentModel()
        self.salarymodel = salaryModel()
        self.transactionmodel = newTransactionModel(23)
        self.salsummarymodel = salarySummaryModel()
        self.staffsalarymodel = staffSalaryModel()
        self.loanadjustmentmodel = newLoanAdjustmentModel()
        # self.init_menubar()
        self.init_emp_stackpage()
        self.init_attend_stackpage()
        self.init_dept_stackpage()
        self.init_departsalary_stackpage()
        self.init_salsummary_stackpage()
        self.init_transaction_stackpage()
        self.init_staffsalary_stackpage()
        self.init_payroll_stackpage()
        # self.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.FramelessWindowHint)
        self.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.MSWindowsFixedSizeDialogHint)

    def init_navbar(self):
        self.ui.empnav.clicked.connect(lambda: self.switchstackto(0))
        self.ui.depnav.clicked.connect(lambda: self.switchstackto(1))
        self.ui.attendnav.clicked.connect(lambda: self.switchstackto(2))
        self.ui.salsumnav.clicked.connect(lambda: self.switchstackto(3))
        self.ui.depsalnav.clicked.connect(lambda: self.switchstackto(4))
        self.ui.transnav.clicked.connect(lambda: self.switchstackto(5))
        self.ui.printnav.clicked.connect(lambda: self.switchstackto(6))
        self.ui.staffsalnav.clicked.connect(lambda: self.switchstackto(7))

    def init_menubar(self):
        self.ui.actionEmployees.triggered.connect(lambda: self.switchstackto(0))
        self.ui.actionDepartments.triggered.connect(lambda: self.switchstackto(1))
        self.ui.actionMark_attendance.triggered.connect(lambda: self.switchstackto(2))
        self.ui.actionDepartment_Wise.triggered.connect(lambda: self.switchstackto(3))
        self.ui.actionChoose_Department.triggered.connect(lambda: self.switchstackto(4))
        self.ui.actionNew_transaction.triggered.connect(lambda: self.switchstackto(5))
        self.ui.actionPrint_Preview.triggered.connect(lambda: self.switchstackto(6))
        self.ui.actionStaff_Salary.triggered.connect(lambda: self.switchstackto(7))

    def del_emp(self):
        row = self.ui.empTable.currentIndex().row()
        if row > -1:
            reply = QtWidgets.QMessageBox.question(self, 'Confirm delete', 'Delete selected row?',
                                                   QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)
            if reply == QtWidgets.QMessageBox.Yes:
                self.empmodel.removeRow(row)
                self.empmodel.select()
        else:
            QtWidgets.QMessageBox.information(self, 'Nothing Selected', 'Please select a row to delete.',
                                              QtWidgets.QMessageBox.Ok)

    def del_dept(self):
        row = self.ui.deptable.currentIndex().row()
        if row > -1:
            reply = QtWidgets.QMessageBox.question(self, 'Confirm delete', 'Delete selected row?',
                                                   QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)
            if reply == QtWidgets.QMessageBox.Yes:
                self.deptmodel.removeRow(row)
                self.deptmodel.select()
        else:
            QtWidgets.QMessageBox.information(self, 'Nothing Selected', 'Please select a row to delete.',
                                              QtWidgets.QMessageBox.Ok)

    def init_dept_stackpage(self):
        font = QtGui.QFont()
        font.setPointSize(14)
        self.ui.deptable.setModel(self.deptmodel)
        self.ui.adddeptbtn.clicked.connect(self.showAddDepDialog)
        self.ui.deldepbtn.clicked.connect(self.del_dept)
        self.ui.deptable.setFont(font)
        self.ui.deptable.resizeColumnsToContents()
        self.ui.deptable.resizeRowsToContents()

    def showAddDepDialog(self):
        text, okPressed = QtWidgets.QInputDialog.getText(self, "Add Department", "Department Name:",
                                                         QtWidgets.QLineEdit.Normal, "")
        if okPressed and text != '':
            with sqlite3.connect('test2.db') as conn:
                conn.execute('insert into departments(department) values(:depart)', {'depart': text})
        self.deptmodel.select()

    def showAddEmpDialog(self):
        """
        Jugaari entry, should be using QSqlTablemodel that has already been attached to the view to insert row or record to model...
        """
        dlg = addEmployee()
        dlg.exec()
        if dlg.data:
            with sqlite3.connect('test2.db') as conn:
                conn.execute(
                    'INSERT INTO employees("empname",department,designation,salary,"salaryint","overtimerate","working") VALUES(:name,:depart,:designation,:salary,:salarystruct,:overtime,:working)',
                    dlg.data)
        self.empmodel.select()

    def showUpdateEmpDialog(self):
        """
        Show upon double clicking the employee Table,
        should already have the current record's entries pre filled into the form.
        Lets try with Data mapping...later
        """
        dlg = updateEmployee()
        model = self.empmodel
        mapper = QtWidgets.QDataWidgetMapper(dlg)
        mapper.setModel(model)
        mapper.addMapping(dlg.name, model.fieldIndex("empname"))
        mapper.addMapping(dlg.depart, model.fieldIndex("department"))
        mapper.addMapping(dlg.designation, model.fieldIndex("designation"))
        mapper.addMapping(dlg.salary, model.fieldIndex("salary"))
        mapper.addMapping(dlg.overtime, model.fieldIndex("overtimerate"))
        mapper.addMapping(dlg.working, model.fieldIndex("working"))
        mapper.addMapping(dlg.salarystruct, model.fieldIndex("salaryint"))
        mapper.setCurrentIndex(self.ui.empTable.currentIndex().row())
        dlg.show()

    def UpdateAllModels(self):
        print("Updating all models but not setting tables to them...")
        self.atnmodel = attendanceModel('01', 'Finish', 2019, 0)
        self.salarymodel = salaryModel()
        self.transactionmodel = transactionModel()
        self.salsummarymodel = salarySummaryModel()
        self.staffsalarymodel = staffSalaryModel()

    @QtCore.Slot(str)
    def filterEmpTable(self, depfilter):
        if depfilter == "All":
            self.empmodel.setFilter('')
            self.ui.empTable.resizeRowsToContents()
        else:
            self.empmodel.setFilter(f'department="{depfilter}"')
            self.ui.empTable.resizeRowsToContents()

    def init_emp_stackpage(self):
        font = QtGui.QFont()
        font.setPointSize(14)
        self.ui.empTable.setFont(font)
        self.ui.empTable.setModel(self.empmodel)
        header = self.ui.empTable.horizontalHeader()  # ???
        self.ui.empdepoption.clear()
        self.ui.empdepoption.addItem('All')
        self.ui.empdepoption.addItems(self.departments)
        self.ui.empdepoption.currentTextChanged.connect(self.filterEmpTable)
        self.ui.empTable.resizeColumnsToContents()
        self.ui.empTable.resizeRowsToContents()
        self.ui.empTable.doubleClicked.connect(self.showUpdateEmpDialog)
        self.ui.addempbtn.clicked.connect(self.showAddEmpDialog)
        self.ui.delempbtn.clicked.connect(self.del_emp)
        self.ui.empTable.setColumnWidth(1, 200)

    def init_attend_stackpage(self):
        # font size 12 is good
        font = QtGui.QFont()
        font.setPointSize(12)
        self.ui.atntable.setFont(font)
        self.ui.monthoption.clear()
        self.ui.halfoption.clear()
        self.ui.depoption.clear()
        self.ui.monthoption.addItems(MONTHS)
        self.ui.halfoption.addItems(['First Half (1 - 15)', 'Second Half (16 - End of month)'])
        self.ui.depoption.addItems(self.departments)
        self.ui.monthoption.currentIndexChanged.connect(self.atnmodel.setMonth)
        self.ui.halfoption.currentIndexChanged.connect(self.atnmodel.setHalf)
        self.ui.depoption.currentTextChanged.connect(self.atnmodel.setDept)
        self.ui.monthoption.currentIndexChanged.connect(self.ui.atntable.resizeColumnsToContents)
        self.ui.halfoption.currentIndexChanged.connect(self.ui.atntable.resizeColumnsToContents)
        self.ui.depoption.currentTextChanged.connect(self.ui.atntable.resizeColumnsToContents)
        self.ui.depoption.currentTextChanged.connect(self.setAttendanceDelegate)
        self.ui.atntable.setItemDelegate(self.atndelegate)
        self.atndelegate.closeEditor.connect(self.ui.atntable.setFocus)
        self.ui.atntable.setModel(self.atnmodel)
        self.ui.atntable.resizeColumnsToContents()
        self.ui.atntable.resizeRowsToContents()

    @QtCore.Slot(str)
    def setAttendanceDelegate(self, department):
        if department == "Production":
            self.ui.atntable.setItemDelegate(self.proddelagate)
        else:
            self.ui.atntable.setItemDelegate(self.atndelegate)

    def updateAttendancePage(self):
        with sqlite3.connect('test2.db') as conn:
            self.departments = conn.execute('SELECT department FROM departments').fetchall()
        self.departments = [x[0] for x in self.departments]
        self.ui.depoption.clear()
        self.ui.depoption.addItems(self.departments)
        self.ui.atntable.setModel(self.atnmodel)

    def showNoRecordError(self, norecordlist):
        QtWidgets.QMessageBox.warning(self.ui.saldeptable, "ERROR",
                                      f"No attendance record found for \n\n{norecordlist}")

    def init_departsalary_stackpage(self):
        font = QtGui.QFont()
        font.setPointSize(14)
        self.ui.saldeptable.setFont(font)
        self.ui.monthoption_2.clear()
        self.ui.halfoption_2.clear()
        self.ui.monthoption_2.addItems(
            ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October',
             'November', 'December'])
        self.ui.halfoption_2.addItems(['First Half (1 - 15)', 'Second Half (16 - End of month)'])
        with sqlite3.connect('test2.db') as conn:
            departments = conn.execute('SELECT department FROM departments').fetchall()
        departments = [x[0] for x in departments]
        self.ui.depoption_2.clear()
        self.ui.depoption_2.addItems(self.departments)
        self.ui.monthoption_2.currentIndexChanged.connect(self.salarymodel.setMonth)
        self.ui.halfoption_2.currentIndexChanged.connect(self.salarymodel.setHalf)
        self.ui.depoption_2.currentTextChanged.connect(self.salarymodel.setDepartment)
        self.salarymodel.norecord.connect(self.showNoRecordError)
        self.salarymodel.initEmployees()
        self.salarymodel.initEmployeePay()
        # self.departmentSalaryProxy = QtCore.QSortFilterProxyModel(self)
        # self.departmentSalaryProxy.setSourceModel(self.salarymodel)
        # filterString = QtCore.QRegExp("^[1-9]\d*$")
        # self.departmentSalaryProxy.setFilterRegExp(filterString)
        # self.departmentSalaryProxy.setFilterKeyColumn(6)
        self.ui.saldeptable.setModel(self.salarymodel)
        self.ui.saldeptable.resizeColumnsToContents()
        self.ui.saldeptable.resizeRowsToContents()

    def init_salsummary_stackpage(self):
        font = QtGui.QFont()
        font.setPointSize(14)
        self.ui.salsumarytable.setFont(font)
        self.ui.salmonthoption.clear()
        self.ui.salhalfoption.clear()
        self.ui.salmonthoption.addItems(
            ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October',
             'November', 'December'])
        self.ui.salhalfoption.addItems(['First Half (1 - 15)', 'Second Half (16 - End of month)'])
        self.ui.salmonthoption.currentIndexChanged.connect(self.salsummarymodel.setMonth)
        self.ui.salhalfoption.currentIndexChanged.connect(self.salsummarymodel.setHalf)
        self.ui.salsumarytable.setModel(self.salsummarymodel)
        self.ui.loanAdjustmentsTable.setModel(self.loanadjustmentmodel)
        self.loanadjustmentmodel.dataChanged.connect(
            lambda: self.salsummarymodel.setHalf(self.ui.salhalfoption.currentIndex()))
        self.ui.loanAdjustmentsTable.resizeColumnsToContents()
        self.ui.salsumarytable.resizeColumnsToContents()
        self.ui.salsumarytable.resizeRowsToContents()

    def showNewTransDlg(self):
        """
        transactionsnew table fields:  id empid date credit debit description
        """

        """  @QtCore.Slot(object)
        def updateDB(data):
        
            self.transactionmodel.setEmployee(data['empid'])
            #self.transactionmodel.headerDataChanged.emit(QtCore.Qt.Horizontal,0,self.transactionmodel.columnCount()-1) """

        dlg = newTransactionDialog()
        dlg.dataready.connect(self.transactionmodel.appendTransaction)
        dlg.exec_()

    def showDispTransDlg(self):
        """
        Sets filters in proxymodel
        """

        @QtCore.Slot(object)
        def setTransaction(data):
            self.transactionmodel.setEmployee(data['empid'])
            # self.transproxy.setSourceModel(self.transactionmodel)
            self.transproxy.setFilterDate(data['fromdate'], data['todate'])

        dlg = dispTransactionDialog()
        dlg.dataready.connect(setTransaction)
        dlg.exec()

    @QtCore.Slot()
    def deleteTransaction(self):
        row = self.ui.tableView.currentIndex().row()
        if row > -1:
            reply = QtWidgets.QMessageBox.question(self, 'Confirm delete', 'Delete selected row?',
                                                   QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)
            if reply == QtWidgets.QMessageBox.Yes:
                self.transactionmodel.deletetransaction(self.ui.tableView.currentIndex())

        else:
            QtWidgets.QMessageBox.information(self, 'Nothing Selected', 'Please select a row to delete.',
                                              QtWidgets.QMessageBox.Ok)

    def init_transaction_stackpage(self):
        font = QtGui.QFont()
        font.setPointSize(14)
        self.transproxy = MyFilterModel()
        self.transproxy.setSourceModel(self.transactionmodel)

        self.ui.tableView.setFont(font)
        self.ui.newtrans.clicked.connect(self.showNewTransDlg)
        self.ui.deltrans.clicked.connect(self.deleteTransaction)
        self.ui.disptrans.clicked.connect(self.showDispTransDlg)
        self.ui.tableView.setModel(self.transproxy)
        self.ui.tableView.resizeColumnsToContents()
        self.ui.tableView.resizeRowsToContents()
        # self.ui.deltrans.clicked.connect(lambda : self.transactionmodel.deletetransaction(self.ui.tableView.currentIndex()))

    def init_staffsalary_stackpage(self):
        font = QtGui.QFont()
        font.setPointSize(14)
        self.ui.salsumarytable_2.setFont(font)
        self.ui.salmonthoption_2.currentIndexChanged.connect(self.staffsalarymodel.setMonth)
        self.ui.salmonthoption_2.clear()
        self.ui.salmonthoption_2.addItems(MONTHS)
        self.ui.salsumarytable_2.setModel(self.staffsalarymodel)
        self.ui.salsumarytable_2.resizeColumnsToContents()
        self.ui.salsumarytable_2.resizeRowsToContents()

    def askToUpdateTransactions(self):
        """Automatically makes entry into the 
        transactionsnew table of all employees that exist in the
        loan adjustments table.
        """

        UpdateTransactions = QtWidgets.QMessageBox.question(self, 'Update Transactions', 'Update Transactions?',
                                                            QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)
        if UpdateTransactions == QtWidgets.QMessageBox.Yes:
            with sqlite3.connect('test2.db') as conn:
                query = "select * from loanadjustments"  # this returns (empid , credit)
                emps = conn.execute(query).fetchall()
                date = datetime.strftime(datetime.now(), "%Y-%m-%d")
                list_of_transactions = [(empid, date, credit, 0, 'LoanAdj') for empid, credit in emps]
                conn.executemany(
                    "insert into transactionsnew (empid, date, credit, debit, description) values (?,?,?,?,?)",
                    list_of_transactions)  # this needs (empid, date, credit, debit, description)
            self.transactionmodel.getAllTransactions()  # Updates / refreshes the tableview

    def setupPrinting(self):
        if self.ui.payrollSummaryRadio.isChecked():
            # get salary summmary data and send for printing
            month = self.ui.payrollMonth.currentIndex()
            half = self.ui.payrollHalf.currentIndex()
            data = self.salsummarymodel.getPrintData(month, half)
            printdata = [['Loan Adjustments', '', '', '']]
            rows, cols = self.loanadjustmentmodel.rowCount(), self.loanadjustmentmodel.columnCount()
            for row in range(0, rows, 2):
                tmp = []
                tmp.append(self.loanadjustmentmodel.data(self.loanadjustmentmodel.index(row, 0), QtCore.Qt.DisplayRole))
                tmp.append(self.loanadjustmentmodel.data(self.loanadjustmentmodel.index(row, 1), QtCore.Qt.DisplayRole))
                tmp.append(
                    self.loanadjustmentmodel.data(self.loanadjustmentmodel.index(row + 1, 0), QtCore.Qt.DisplayRole))
                tmp.append(
                    self.loanadjustmentmodel.data(self.loanadjustmentmodel.index(row + 1, 1), QtCore.Qt.DisplayRole))
                printdata.append(tmp)
            data.extend(printdata)
            makeSalarySummaryPdf(data, MONTHS[month], half)


        elif self.ui.payrollDeptRadio.isChecked():
            # get department payroll data and send for printing
            department = self.ui.payrollDepartment.currentText()
            month = self.ui.payrollMonth.currentIndex()
            half = self.ui.payrollHalf.currentIndex()
            data = self.salarymodel.getPrintData(department, month, half)
            departmentdata1 = {}
            departmentdata2 = {}
            departmentdata1['table'] = data
            departmentdata1['month'] = MONTHS[month]
            departmentdata1['department'] = department
            departmentdata1['half'] = half
            if self.ui.checkBox.isChecked():
                department2 = self.ui.payrollDepartment_3.currentText()
                month2 = self.ui.payrollMonth_3.currentIndex()
                half2 = self.ui.payrollHalf_3.currentIndex()
                data2 = self.salarymodel.getPrintData(department2, month2, half)
                departmentdata2['table'] = data2
                departmentdata2['month'] = MONTHS[month2]
                departmentdata2['department'] = department2
                departmentdata2['half'] = half2
            # makegrid(data, department, MONTHS[month], half)
            makeDepartmentPdf(departmentdata1, departmentdata2)

        elif self.ui.payrollStaffOvertimeRadio.isChecked():
            half = self.ui.payrollHalf.currentIndex()
            month = self.ui.payrollMonth.currentIndex()
            data = self.staffsalarymodel.getOvertimeData(month + 1, half)
            tabledata = []
            for row in range(len(data[0]) - 1):
                tmp = []
                tmp.append(data[row]['name'])
                tmp.append(data[row]['overtimerate'])
                tmp.append(data[row]['overtimehours'])
                tmp.append(data[row]['overtimepay'])
                tabledata.append(tmp)
            tabledata.append(['', '', '', data[-1]])
            makeStaffOvertimePdf(tabledata, MONTHS[month], half)

        elif self.ui.payrollProdRadio.isChecked():
            # get production data and send for printing
            month = self.ui.payrollMonth.currentIndex()
            half = self.ui.payrollHalf.currentIndex()
            emp = self.productionemployees[self.ui.payrollProduction.currentIndex()]
            tmp = {}
            emp.setAttendanceHalf(month + 1, half)
            emp.calculatePay()
            tmp["meters"] = emp.meters
            tmp["redyeing"] = emp.redyeing
            tmp["total"] = emp.totalpay
            tmp["loans"] = emp.loans
            tmp["balance"] = emp.balance
            tmp["name"] = emp.name
            tmp["sum"] = emp.meters + emp.redyeing
            makeProductionPdf(tmp, MONTHS[month], half)

        elif self.ui.payrollStaffRadio.isChecked():
            # get monthly staff data and send for printing
            # self.staffsalarymodel=staffSalaryModel()
            month = self.ui.payrollMonth.currentIndex()
            half = 2
            data = self.staffsalarymodel.getPrintData(
                month)  # dont need to add +1 coz its using the models own setMonth which adds 1 anyway
            staffdata = {}
            staffdata['table'] = data
            staffdata['month'] = MONTHS[month]
            staffdata['half'] = half
            staffdata['department'] = "Staff Salary"
            makeStaffSalaryPdf(staffdata)

        ShowPdf = QtWidgets.QMessageBox.question(self, 'View Payroll', 'Open payroll PDF for printing?',
                                                 QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)
        if ShowPdf == QtWidgets.QMessageBox.Yes:
            # open doc in adobe pdf
            QtGui.QDesktopServices.openUrl("grid.pdf")

        self.askToUpdateTransactions()

    def init_payroll_stackpage(self):
        self.ui.payrollDepartment.clear()
        self.ui.payrollDepartment_3.clear()
        self.ui.payrollDepartment.addItems(self.departments)
        self.ui.payrollDepartment_3.addItems(self.departments)
        self.ui.payrollMonth.clear()
        self.ui.payrollMonth.addItems(MONTHS)
        self.ui.payrollMonth_3.clear()
        self.ui.payrollMonth_3.addItems(MONTHS)
        self.ui.payrollHalf_3.clear()
        self.ui.payrollHalf_3.addItems(["1 - 15", "15 - end of month"])
        self.ui.payrollHalf.clear()
        self.ui.payrollHalf.addItems(["1 - 15", "15 - end of month"])
        prod = Department("Production")
        self.productionemployees = prod.employees
        self.ui.payrollProduction.clear()
        self.ui.payrollProduction.addItems([emp.name for emp in self.productionemployees])
        self.ui.genPayroll.clicked.connect(self.setupPrinting)

    def switchstackto(self, index):
        if index == 0:
            pass
            # self.ui.empTable.setModel(self.empmodel)
            # self.init_emp_stackpage()
        elif index == 1:
            pass
            # self.ui.deptable.setModel(self.deptmodel)
            # self.init_dept_stackpage()
        elif index == 2:
            pass
            # self.updateAttendancePage()
        # self.init_attend_stackpage()
        elif index == 3:
            self.salsummarymodel.initDepartments()
            self.loanadjustmentmodel = newLoanAdjustmentModel()  # dirty fix
            self.ui.loanAdjustmentsTable.setModel(self.loanadjustmentmodel)
            # self.loanadjustmentmodel.loadempids()
            # self.init_salsummary_stackpage()
        elif index == 4:
            self.salarymodel.setDepartment(self.salarymodel.department)
        elif index == 5:
            pass
            # self.init_transaction_stackpage()
        elif index == 6:
            pass
            # self.init_payroll_stackpage()
        elif index == 7:
            pass
            # self.init_staffsalary_stackpage()

        self.ui.stack.setCurrentIndex(index)

    def initBeautification(self):
        """
        This function sets all the visual goodies,
        Like making font larger
        setting font style
        setting window theme 
        setting title / icon etc
        """
        pass


if __name__ == '__main__':
    appctxt = ApplicationContext()  # 1. Instantiate ApplicationContext
    window = MainWindow()
    # window.resize(250, 150)
    window.show()
    exit_code = appctxt.app.exec_()  # 2. Invoke appctxt.app.exec_()
    sys.exit(exit_code)
