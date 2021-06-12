import sqlite3

class Employee(object):
    """
    Represents an employee. Each employee has the following attributes
    name:
    department:
    salary: 
    overtime: integer representing the amount the employee gets per hour of overtime work.
    salary_interval: string one of: Daily, Monthly. Represents the interval at which
                    the employee receives salary.
    """
    def __init__(self, _id):
        self.id = _id
        self.initInfo()

    def initInfo(self):
        self.overtimehours,self.daysabsent,self.dayspresent,self.meters,self.redyeing,self.loans = 0,0,0,0,0,0
        self.overtimepay, self.totalpay ,self.meters, self.redyeing,self.normalpay,self.advance = 0,0,0,0,0,0
        with sqlite3.connect('test2.db') as conn:
            empdata = conn.execute("""select "empname", department, designation, salary, "salaryint","""
                                    """ "overtimerate" from employees where empid = :id""",{'id':self.id})
            try:
                self.loans = conn.execute('select amount from loanadjustments where empid = :id', {'id':self.id}).fetchone()[0]
                if self.loans == None:
                    self.loans = 0
            except:
                self.loans = 0
        self.name, self.department, self.designation, self.salary, self.salary_interval, self.overtimerate = empdata.fetchone()  

    def setAttendanceDict(self, month, year=2019):
        """
        Return a dict representing the attendance of the employee
        for the given month/half/year. where the key refers to the 
        to the day and the value itself is the tupple representing status (P,4) (A,0) etc
        """    
        with sqlite3.connect('test2.db') as conn:
            attendance = conn.execute('select status,"overtimeworked",date from attendance where empid=:id and date like :date order by date asc',{'id':self.id, 'date':f"{year}-{month}-%"})
        self.attendance = {att[2]:(att[0],att[1]) for att in attendance.fetchall()}
                
    def setAttendanceHalf(self, month, half=0, year=2019):
        """
        This function aids the calculation of the salaries of employees whose salary is calculated on a daily basis.
        month:int(2 digit representation of month 01-12)
        half:int (0 or 1)
        """
        with sqlite3.connect('test2.db') as conn:
            if self.department == "Production":
                try:
                    self.meters = conn.execute('select meters from production where empid=:id and month=:month and half=:half',{'id':self.id, 'month':month, 'half':half}).fetchone()[0]
                except:
                    self.meters = 0
                try:
                    self.redyeing = conn.execute('select redyeing from production where empid=:id and month=:month and half=:half',{'id':self.id, 'month':month, 'half':half}).fetchone()[0]
                except:
                    self.redyeing = 0 
                    
            if half == 0:
                self.dayspresent = conn.execute('select count(*) from attendance WHERE status = "P" and date like :month and date <= :datelimit and empid = :id',{'month':f"{year}-{month}-%",'datelimit':f"{year}-{month}-15",'id':self.id}).fetchone()[0]
                self.overtimehours = conn.execute('select SUM("overtimeworked") from attendance WHERE date like :month and date <= :datelimit and empid = :id',{'month':f"{year}-{month}-%",'datelimit':f"{year}-{month}-15",'id':self.id}).fetchone()[0]
                self.daysabsent = conn.execute('select count(*) from attendance WHERE status = "A" and date like :month and date <= :datelimit and empid = :id',{'month':f"{year}-{month}-%",'datelimit':f"{year}-{month}-15",'id':self.id}).fetchone()[0]
                """ try:
                    self.loans = conn.execute('select amount from loanadjustments where empid = :id', {'id':self.id}).fetchone()[0]
                    if self.loans == None:
                        self.loans = 0
                except:
                    self.loans = 0 """
            elif half == 1:
                self.dayspresent = conn.execute('select count(*) from attendance WHERE status = "P" and date like :month and date > :datelimit and empid = :id',{'month':f"{year}-{month}-%",'datelimit':f"{year}-{month}-15",'id':self.id}).fetchone()[0]
                self.overtimehours = conn.execute('select SUM("overtimeworked") from attendance WHERE date like :month and date > :datelimit and empid = :id',{'month':f"{year}-{month}-%",'datelimit':f"{year}-{month}-15",'id':self.id}).fetchone()[0]
                self.daysabsent = conn.execute('select count(*) from attendance WHERE status = "A" and date like :month and date > :datelimit and empid = :id',{'month':f"{year}-{month}-%",'datelimit':f"{year}-{month}-15",'id':self.id}).fetchone()[0]
                """ try:
                    self.loans = conn.execute('select amount from loanadjustments where empid = :id', {'id':self.id}).fetchone()[0]        
                    if self.loans == None:
                        self.loans = 0
                except:
                    self.loans = 0 """

    def setAttendanceFull(self, month, year=2019):
        """
        This function aids the calculation of the salary of monthly paid staff.
        """
        with sqlite3.connect('test2.db') as conn:
            self.dayspresent = conn.execute('select count(*) from attendance WHERE status = "P" and date like :month and empid = :id',{'month':f"{year}-{month}-%",'id':self.id}).fetchone()[0]
            #self.overtimehours = conn.execute('select SUM("overtimeworked") from attendance WHERE date like :month and empid = :id',{'month':f"{year}-{month}-%",'id':self.id}).fetchone()[0]
            self.daysabsent = conn.execute('select count(*) from attendance WHERE status = "A" and date like :month and empid = :id',{'month':f"{year}-{month}-%",'id':self.id}).fetchone()[0]
            """ try:
                self.loans = conn.execute('select amount from loanadjustments where empid = :id', {'id':self.id}).fetchone()[0]        
                if self.loans == None:
                    self.loans = 0
            except:
                self.loans = 0 """

    def calculatePay(self):
        """
        Always need to call setAttendanceHalf before this function.
        setAttendanceHalf is used to tell this function which month's pay is to be calculated and also provides
        the necessary data for the calculation.
        """

        if self.department == 'Production':
            self.totalpay = self.meters * self.salary + self.redyeing * self.salary
            self.totalpay = round(self.totalpay)
            self.balance = self.totalpay - self.loans

        elif self.salary_interval == 'Daily':
            self.normalpay = self.dayspresent * self.salary
            self.overtimepay = self.overtimehours * self.overtimerate
            self.totalpay = self.normalpay + self.overtimepay
            self.balance = self.totalpay - self.loans

        elif self.salary_interval == 'Monthly':
            self.attendeduction = self.daysabsent*(self.salary//30)
            self.normalpay = self.salary - self.attendeduction
            self.overtimepay = self.overtimehours * self.overtimerate
            self.totalpay = self.normalpay
            self.balance = self.totalpay - self.loans


class Department(object):
    """
    Here we try to make a department object which will have the 
    following attributes for each month half:
    name
    total salary earned
    total loans/advances 
    Balance
    List of employees
    """
    def __init__(self, name):
        self.name = name
        self.month = '01'
        self.half = 0
        self.loadEmployees()
        self.total= 0
        self.totalloans = 0
        self.balance= 0
    
    def setMonth(self, month):
        self.month = f"{int(month):02}"
        

    def setHalf(self, half):
        self.half = half
        
    

    def loadEmployees(self):
        with sqlite3.connect('test2.db') as conn:
            ids = conn.execute('select empid from employees where department = :dept',{'dept':self.name})
        self.employees = [Employee(empid[0]) for empid in ids.fetchall()]
        
        
    def calculateFinances(self):
        """
        calculates the total salary earned by employees
        calculates the total loans/advances that the employees have taken this month/half
        calculates the balance to be paid to employees.
        """
        for employee in self.employees:
            try:
                employee.setAttendanceHalf(self.month, self.half)
                # Problem only arises when trying to calculate pay for employee who has no attendance record.
                employee.calculatePay()
            except:
                pass
        self.totalsalary = 0
        self.totalbalance = 0
        self.totalloans = 0
        for employee in self.employees:
            if employee.salary_interval == "Monthly" and not self.name == "Staff" :
                self.totalsalary += employee.overtimepay
            else:
                self.totalsalary += employee.totalpay
            self.totalloans += employee.loans
        self.totalbalance = self.totalsalary  - self.totalloans
