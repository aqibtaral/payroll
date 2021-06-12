import sys
from datetime import datetime as dt

import PySide2.QtPrintSupport
from PySide2 import QtCore, QtGui, QtWidgets

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, letter, mm, inch
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfgen import canvas
from reportlab.platypus import (Frame, Paragraph, SimpleDocTemplate, Table,
                                TableStyle)

HALF = ["From 1st to 15th", "From 16th to end", '']
ORIGIN = (20, 20)
BOTTOM_RIGHT = (575, 20)
TOP_LEFT = (20, 820)
TOP_RIGHT = (575, 820)
MID_Y = 420


# Letter is width : 612, Height: 792

def printRecipe():
    printer = PySide2.QtPrintSupport.QPrinter()
    dialog = PySide2.QtPrintSupport.QPrintDialog(printer)
    dialog.setModal(True)
    dialog.setWindowTitle("Print Document")
    if dialog.exec_() == True:
        # self.webViewBiblio.print(printer)
        document = QtWidgets.QTextEdit()
        document.setText("O MY WORD WAT THE PO LO FO O")
        # stringHtml=self.recipe.export("print")
        # document.setHtml(stringHtml)
        document.print_(printer)


def makedefaultform():
    canvas = canvas.Canvas('form.pdf', pagesize=letter)
    width, height = letter
    canvas.setLineWidth(.3)
    canvas.setFont('Helvetica', 12)

    canvas.drawString(30, 750, 'OFFICIAL COMMUNIQUE')
    canvas.drawString(30, 735, 'OF ACME INDUSTRIES')
    canvas.drawString(500, 750, "12/12/2010")
    canvas.line(480, 747, 580, 747)

    canvas.drawString(275, 725, 'AMOUNT OWED:')
    canvas.drawString(500, 725, "$1,000.00")
    canvas.line(378, 723, 580, 723)

    canvas.drawString(30, 703, 'RECEIVED BY:')
    canvas.line(120, 700, 580, 700)
    canvas.drawString(120, 703, "JOHN DOE")

    canvas.save()

    """ for x in range(20,int(width)-20,10):
        for y in range(20,420,10):
            myCanvas.drawString(x, y, '•') """

    # printable area is between x = 20 to x = 575
    # and for y it is y = 20 to 410 and then 430 to 820
    # myCanvas.drawCentredString(595/2, 820,"YS")
    # myCanvas.line(20,760,575,760)


def makedoc(somedata, depart, month, half, headers, footers, tstyle, canv, colW=None, rowH=None, TableAlign=None,
            FrameX=20, FrameY=430, FrameW=575 - 20, FrameH=320):
    """
    somedata: The Table data to display in main frame.
    depart: The name to display on top left.
    month: The name of month to display at top left.
    half: The part of month to display at top left. (1-15, 15-end, nothing)
    headers: The header names of the data in table.
    footers: The sums etc to show at the last row of table.
    tstyle: The tablestyle, where to draw grid etc.
    canv: The reportlab Canvas on which to draw all elements.
    """
    # Letter is width : 612, Height: 792
    # A4 is width : 595.2755, Height: 841.8897
    myCanvas = canv
    myCanvas.saveState()
    myCanvas.setFont('Helvetica', 9)
    myCanvas.setLineWidth(.3)
    width, height = A4
    makeHeader(myCanvas, depart, month, half)
    MainFrame = Frame(FrameX, FrameY, FrameW, FrameH, showBoundary=0, id="MainFrame")
    tabledata = somedata
    tabledata.insert(0, headers)
    tabledata.extend(footers)
    MainFrameTable = Table(tabledata, colW, rowH, style=tstyle, hAlign=TableAlign)
    MainFrame.addFromList([MainFrameTable], myCanvas)
    myCanvas.restoreState()


def makeHeader(can, depart, month, half):
    can.saveState()
    can.setLineWidth(0.6)
    can.line(20, 760, 575, 760)
    stylesheet = getSampleStyleSheet()
    Bstyle = stylesheet['Normal']
    topLeftHeader = Frame(20, 760, 120, 60, showBoundary=0, id='topLeftHeader')
    TopLeftHeaderData = [Paragraph(depart, Bstyle), Paragraph(HALF[half], Bstyle), Paragraph(month + " 2019", Bstyle)]
    topLeftHeader.addFromList(TopLeftHeaderData, can)
    topRightHeader = Frame(TOP_RIGHT[0] - 120, 760, 120, 60, showBoundary=0, id='topRightHeader')
    nowdate = dt.strftime(dt.now(), "%d-%B-%Y")
    # Paragraph("<para align=left>Paid: </para>",Bstyle)
    TopRightHeaderData = [Paragraph(f"<para align=right>Generated on: {nowdate}</para>", Bstyle)]
    topRightHeader.addFromList(TopRightHeaderData, can)
    CentreHeader = Frame(160, 760, 270, 60, showBoundary=0, id="CentreHeader")
    CentreHeaderData = [Paragraph("<para align=centre size=20>ERU</para>", Bstyle)]
    CentreHeader.addFromList(CentreHeaderData, can)
    can.restoreState()


def makeDepartmentPdf(departmentdata1, departmentdata2=[]):
    """
    Only workable if there are Less than 12 entries per department. Otherwise they dont fit on a single page.
    """
    myCanvas = canvas.Canvas("grid.pdf", pagesize=A4)
    myCanvas.line(20, 420, 575, 420)
    headers = ["Name", "#Days", "Ovr Hrs", "Ovr Rate", "Salary", "Ovr Amnt", "Total", "Loans", "Balance"]
    tstyle = [('GRID', (0, 0), (-1, -1), 1, colors.black),
              ('GRID', (-3, -2), (-1, -2), 2, colors.black),
              ('SPAN', (0, -2), (5, -1))]
    total, bal, loan = 0, 0, 0
    for row in departmentdata1['table']:
        total += int(float(row[-3]))
        loan += int(float(row[-2]))
        bal += int(float(row[-1]))
    footers = [['Received By:', '', '', '', '', '', f'{total}', f'{loan}', f'{bal}'], []]
    makedoc(departmentdata1['table'], departmentdata1['department'], departmentdata1['month'], departmentdata1['half'],
            headers, footers, tstyle, myCanvas)
    if departmentdata2:
        myCanvas.translate(0, -400)
        total, bal, loan = 0, 0, 0
        for row in departmentdata2['table']:
            total += int(float(row[-3]))
            loan += int(float(row[-2]))
            bal += int(float(row[-1]))
        footers2 = [['Received By:', '', '', '', '', '', f'{total}', f'{loan}', f'{bal}'], []]
        makedoc(departmentdata2['table'], departmentdata2['department'], departmentdata2['month'],
                departmentdata2['half'], headers, footers2, tstyle, myCanvas)
    myCanvas.save()


def makeStaffSalaryPdf(staffdata):
    myCanvas = canvas.Canvas("grid.pdf", pagesize=A4)
    stylesheet = getSampleStyleSheet()
    Bstyle = stylesheet['Normal']
    headers = [Paragraph("<b>Name</b>", Bstyle), "Salary", "Absnt", "Minus", "Total", "Loans", "Balance", "Signature"]
    tstyle = [('GRID', (0, 0), (-1, -1), 1, colors.black),
              ('GRID', (0, -1), (-1, -1), 2, colors.black),
              ('ALIGN', (1, 1), (-1, -1), 'RIGHT')]
    sal, deduct, total, bal, loan = 0, 0, 0, 0, 0
    for row in staffdata['table']:
        sal += int(float(row[1]))
        deduct += int(float(row[3]))
        total += int(float(row[4]))
        loan += int(float(row[5]))
        bal += int(float(row[6]))
    footers = [['', f'{sal}', '', f'{deduct}', f'{total}', f'{loan}', f'{bal}', '']]
    colsizes = [1.5 * inch, 0.8 * inch, 0.5 * inch, 0.5 * inch, 0.8 * inch, 0.8 * inch, 0.8 * inch, 1.5 * inch]
    tableAlign = ['RIGHT', 'RIGHT', 'RIGHT', 'RIGHT', 'RIGHT', 'RIGHT', 'RIGHT', 'RIGHT']
    makedoc(staffdata['table'], staffdata['department'], staffdata['month'], staffdata['half'], headers, footers,
            tstyle, myCanvas, colW=colsizes, rowH=0.7 * inch, FrameY=20, FrameH=730)
    myCanvas.save()


def makeProductionPdf(data, month, half):
    myCanvas = canvas.Canvas("grid.pdf", pagesize=A4)
    myCanvas.line(20, 420, 575, 420)
    stylesheet = getSampleStyleSheet()
    Bstyle = stylesheet['Normal']
    headers = [Paragraph("<b>Meters</b>", Bstyle), Paragraph("<b>Redyeing</b>", Bstyle),
               Paragraph("<b>Total</b>", Bstyle), Paragraph("<b>Loans</b>", Bstyle),
               Paragraph("<b>Balance</b>", Bstyle)]
    tstyle = [('GRID', (0, 0), (-1, -1), 1, colors.black),
              ('SPAN', (0, -2), (3, -1))]
    footers = [[], [], [], ["Received By:", '', '', '', ''], []]
    table = [[data["meters"], data["redyeing"], data["total"], data["loans"], data["balance"]]]
    makedoc(table, data["name"], month, half, headers, footers, tstyle, myCanvas)
    myCanvas.save()


def makeStaffOvertimePdf(data, month, half):
    myCanvas = canvas.Canvas("grid.pdf", pagesize=A4)
    myCanvas.line(20, 420, 575, 420)
    stylesheet = getSampleStyleSheet()
    Bstyle = stylesheet['Normal']
    headers = [Paragraph("<b>Name</b>", Bstyle), Paragraph("<b>Rate</b>", Bstyle), Paragraph("<b>Hours</b>", Bstyle),
               Paragraph("<b>Total</b>", Bstyle)]
    tstyle = [('GRID', (0, 0), (-1, -1), 1, colors.black),
              ('SPAN', (0, -2), (2, -1))]
    footers = [[], [], ["Received By:", '', '', '', ''], []]
    makedoc(data, "Staff Overtime", month, half, headers, footers, tstyle, myCanvas)
    myCanvas.save()


def makeSalarySummaryPdf(data, month, half):
    myCanvas = canvas.Canvas("grid.pdf", pagesize=A4)
    myCanvas.line(20, 420, 575, 420)
    stylesheet = getSampleStyleSheet()
    Bstyle = stylesheet['Normal']
    headers = [Paragraph("<b>Department</b>", Bstyle), Paragraph("<b>Total</b>", Bstyle),
               Paragraph("<b>Loans</b>", Bstyle), Paragraph("<b>Balance</b>", Bstyle)]
    tstyle = [('GRID', (0, 0), (-1, -1), 1, colors.black),
              ('GRID', (0, 10), (-1, 10), 2, colors.black),
              ('SPAN', (0, 11), (-1, 11))]
    footers = [data.pop()]
    makedoc(data, "Salary Summary", month, half, headers, footers, tstyle, myCanvas)
    myCanvas.save()
