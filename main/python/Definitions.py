"""
File containing all constant definitions
Table headers etc.
"""

TableHeaders = {'employees':{
                            0:'ID',
                            1:'Name',
                            2:'Depart',
                            3:'Dsgntn',
                            4:'Salary',
                            5:'Sal typ',
                            6:'Ov Rt',
                            7:'Wrkng'},
                'loanadjustments':{
                            0:'Name',
                            1:'Amount'
                },
                'salary':{},
                'attendance':{},
                }


TableCreateQuery = {
    'employees':
    """CREATE TABLE "employees" (
	"empid"	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
	"empname"	TEXT,
	"department"	TEXT,
	"designation"	TEXT,
	"salary"	INTEGER,
	"salaryint"	TEXT,
	"overtimerate"	INTEGER,
	"working"	TEXT,
	FOREIGN KEY("department") REFERENCES "departments"("department")
    )""",
    'departments':
    """CREATE TABLE "departments" (
	"department"	TEXT UNIQUE
    )""",
    'attendance':
    """CREATE TABLE "attendance" (
	"empid"	INTEGER,
	"date"	TEXT,
	"status"	TEXT,
	"overtimeworked"	INTEGER,
	FOREIGN KEY("empid") REFERENCES "employees"("empid"),
	PRIMARY KEY("date","empid")
    ) """,
    'loanadjustments':
    """CREATE TABLE "loanadjustments" (
	"empid"	INTEGER NOT NULL,
	"amount"	INTEGER DEFAULT 0,
	PRIMARY KEY("empid"),
	FOREIGN KEY("empid") REFERENCES "employees"("empid")
    ) """,
    'production':
    """CREATE TABLE "production" (
	"empid"	INTEGER NOT NULL,
	"month"	INTEGER NOT NULL,
	"half"	INTEGER NOT NULL,
	"meters"	INTEGER NOT NULL DEFAULT 0,
	"redyeing"	INTEGER NOT NULL DEFAULT 0,
	FOREIGN KEY("empid") REFERENCES "employees"("empid"),
	PRIMARY KEY("empid","month","half")
    ) """,
    'transactionsnew':
    """CREATE TABLE "transactionsnew" (
	"id"	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
	"empid"	INTEGER NOT NULL,
	"date"	TEXT NOT NULL,
	"credit"	INTEGER DEFAULT 0,
	"debit"	INTEGER DEFAULT 0,
	"description"	TEXT,
	FOREIGN KEY("empid") REFERENCES "employees"("empid")
    ) """}

