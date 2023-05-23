from connect import connect
import matplotlib
import matplotlib.pyplot  as plt
import numpy as np
import datetime
import matplotlib.dates as mdates
from matplotlib.axis import Axis
import json


db = connect(0)

cur = db.cursor()

cur.execute('SELECT person_id FROM People WHERE person_name="Bryan"')

IDtemp = cur.fetchone()
myID = IDtemp[0]

cur.execute("SELECT test_id FROM Test WHERE person_id={} AND successful=1".format(myID))

passed_tests = cur.fetchall()

print(len(passed_tests))

def select_test_per_board(SN):
    print("Getting tests for board with Serial number {}".format(SN))
    db = connect(0)
    cur = db.cursor()

    cur.execute('select board_id from Board where full_id="{}"'.format(SN))
    BoardID =  cur.fetchall()[0][0]
    print(BoardID)

    cur.execute('select test_id,successful from Test where board_id={}'.format(BoardID))
    tests = cur.fetchall()
    print(tests)
    return tests

#tests = select_test_per_board("320WW20A1000005")
#npresults = np.array([t[1] for t in tests])
#print(npresults)
#plt.hist(npresults, bins=2)
#plt.savefig("./test.png")

def tests_over_time(SerialNumber=None,SubType=None,Tester=None):
    db = connect(0)
    cur = db.cursor()
    
    query = "select day from Test"
    title = "Tests over Time"

    if SerialNumber is not None:
        cur.execute('select board_id from Board where full_id="{}"'.format(SerialNumber))
        BoardID = cur.fetchall()[0][0]
        query += ' where board_id="{}"'.format(BoardID)
        title += " for " + SerialNumber

    if SubType is not None:
        if SerialNumber is not None:
            query += ' and'
            title += " and "
        else:
            query += ' where'
            title += " for "
        cur.execute('select board_id from Board where type_id="{}"'.format(SubType))
        BoardID = cur.fetchall()
        for i in BoardID:
            query += ' board_id={}'.format(i[0])
            if i is not BoardID[-1]:
                query += ' or'
        title += SubType

    if Tester is not None:
        cur.execute('select person_id from People where person_name="{}"'.format(Tester))
        person_id = cur.fetchall()[0][0]
        if SerialNumber is not None or SubType is not None:
            query += ' and'
            title += " and "
        else: 
            query += ' where'
            title += " for "    
        query += ' person_id="{}"'.format(person_id)
        title += Tester

    cur.execute(query)
    dates = cur.fetchall()
    #print(dates)
    first = datetime.datetime(2023, 1, 1, 12, 0, 0)

    query2 = "select day from Test where successful=1"

    if SerialNumber is not None:
        cur.execute('select board_id from Board where full_id="{}"'.format(SerialNumber))
        BoardID = cur.fetchall()[0][0]
        query2 += ' and board_id="{}"'.format(BoardID)

    elif SubType is not None:
        cur.execute('select board_id from Board where type_id="{}"'.format(SubType))
        BoardID = cur.fetchall()
        query2 += " and"
        for i in BoardID:
            query2 += ' board_id={}'.format(i[0])
            if i is not BoardID[-1]:
                query2 += ' or'

    elif Tester is not None:
        cur.execute('select person_id from People where person_name="{}"'.format(Tester))
        person_id = cur.fetchall()[0][0]
        query2 += ' and person_id="{}"'.format(person_id)

    cur.execute(query2)
    successful_dates = cur.fetchall()
    #print(successful_dates)

    time_series_data = []
    time_series_data_successful = []

    while (first <= datetime.datetime.now()):
        i = 0
        j = 0
        for d in dates:
            if d[0] > first:
                break
            else:
                i += 1
        for d in successful_dates:
            if d[0] > first:
                break
            else:
                j += 1
        time_series_data.append([first,i])
        time_series_data_successful.append([first,j])
        first += datetime.timedelta(days=7)                
    tempx1,tempy1 = zip(*time_series_data)
    tempx2,tempy2 = zip(*time_series_data_successful)
    
    fig, ax = plt.subplots()
    plt.plot(tempx1,tempy1,label = "Total")
    plt.plot(tempx2,tempy2,label = "Successful")
    plt.title(title)
    plt.xlabel("Date")
    plt.ylabel("Number of Tests")
    plt.legend()
    Axis.set_major_locator(ax.xaxis,mdates.MonthLocator(interval=1))
    plt.gcf().autofmt_xdate()

    FileName = "./tests_over_time"

    if SerialNumber is not None:
        FileName += "_SN"+SerialNumber

    if SubType is not None:
        FileName += "_SubType"+SubType
    
    if Tester is not None:
        FileName += "_Tester"+Tester

    plt.savefig(FileName + ".png")


def data_from_test_type(TestType):
    db = connect(0)
    cur = db.cursor()

    cur.execute('select test_type from Test_Type where name="{}"'.format(TestType))
    test_type_id = cur.fetchall()[0][0]

    cur.execute('select test_id from Test where test_type_id="{}"'.format(test_type_id))
    TestIDs = cur.fetchall()

    query = 'select attach from Attachments where '
    for i in TestIDs:
        query += 'test_id={}'.format(i[0])
        if i is not TestIDs[-1]:
            query += ' or '
        
    cur.execute(query)
    Attach = cur.fetchall()
    Data = []
    for i in Attach:
       Data.append(json.loads(i[0]))
    Resistance = []
    for i in Data:
        Resistance.append(i['wagon type chip']['WAGON_TYPE -> GND'])
    plt.hist(Resistance)
    plt.xlabel("Resistance (Ohms)")
    plt.ylabel("Number of Boards")
    plt.title("ID Resistor Measurements")
    plt.savefig("./ID_Resistor_Data.png")

data_from_test_type("ID Resistor Measurement")
