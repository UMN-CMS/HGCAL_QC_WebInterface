from connect import connect
import numpy as np
import json
import csv
import os
import io
import pandas as pd
import datetime
import pickle
import multiprocessing as mp

path = os.path.dirname(os.path.abspath(__file__))

p = '%s/../../static/WagonDB/' % path
if not os.path.isdir(p):
    os.makedirs(p)

db = connect(0)
cur = db.cursor(buffered=True)

# collects all the necessary data from the database to be put into .csv WagonDB for the plotting scripts

def get_test():
    # some data can easily be written into a .csv just by writing rows
    # in this case a csv.writer can be used

    csv_file = io.StringIO()

    columns = ['Test ID', 'Test Type ID', 'Board ID', 'Person ID', 'Time', 'Successful']
    writer = csv.writer(csv_file)
    writer.writerow(columns)

    cur.execute('select test_id, test_type_id, board_id, person_id, day, successful from Test order by day asc')
    Test_Data = cur.fetchall()
    writer.writerows(Test_Data)

    # need to tell the file pointer to go to the beginning
    csv_file.seek(0)

    return csv_file

def get_id_res():
    csv_file = io.StringIO()

    # some data requires decoding first
    # in this case it's better to use csv.DictWriter
    header = ['Test ID','Resistance']
    writer = csv.DictWriter(csv_file, fieldnames = header)

    # gets the test type id
    cur.execute('select test_type from Test_Type where name="ID Resistor Measurement"')
    test_type_id = cur.fetchall()[0][0]

    # gets the test ids for that test type
    cur.execute('select board_id from Board where full_id like "320W%"')
    boards_list = cur.fetchall()
    Tests = []
    for b in boards_list:
        cur.execute('select Test.test_id, Attachments.attach from Test left join Attachments on Test.test_id=Attachments.test_id where Test.board_id=%s and Test.test_type_id=%s order by Test.day desc, Test.test_id desc' % (b[0],test_type_id))
        test_id = cur.fetchone()
        if test_id:
            Tests.append(test_id)

    Attach_Data = []
    for i in Tests:
        Attach_Data.append(json.loads(i[1]))
    Resistance = []
    # gets the resistance out of the array
    for i in Attach_Data:
        try:
            Resistance.append(i["test_data"]['wagon type chip']['WAGON_TYPE -> GND'])
        except KeyError:
            try:
                Resistance.append(i['wagon type chip']['WAGON_TYPE -> GND'])
            except KeyError:
                Resistance.append(-1)

    # writes everything to the file
    writer.writeheader()
    for i in range(len(Tests)):
        writer.writerow({'Test ID':Tests[i][0], 'Resistance':Resistance[i]})

    csv_file.seek(0)

    return csv_file

def get_I2C():
    csv_file = io.StringIO()

    header= ['Test ID', 'Checks', 'Correct at Module 1', 'Correct at Module 2', 'Correct at Module 3']
    writer = csv.DictWriter(csv_file, fieldnames = header)

    cur.execute('select test_type from Test_Type where name="I2C Read/Write"')
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
    Attach_Data = []
    for i in Attach:
        Attach_Data.append(json.loads(i[0]))

    for i in range(len(Attach_Data)):
        print(Attach_Data[i])
        print(TestIDs[i])


    mod9999 = []
    mod0 = []
    mod1 = []
    mod2 = []
    for i in range(len(Attach_Data)):
        try:
            mod9999.append(Attach_Data[i]['num_iic_checks_mod9999'])
        except KeyError:
            mod9999.append(Attach_Data[i]['num_iic_checks_mod0'])
        mod0.append(Attach_Data[i]['num_iic_correct_mod0'])
        try:
            mod1.append(Attach_Data[i]['num_iic_correct_mod1'])
        except KeyError:
            mod1.append(-1)
        try:
            mod2.append(Attach_Data[i]['num_iic_correct_mod2'])
        except KeyError:
            mod2.append(-1)

    writer.writeheader()
    for i in range(len(TestIDs)):
        writer.writerow({'Test ID':TestIDs[i][0], 'Checks':mod9999[i], 'Correct at Module 1':mod0[i], 'Correct at Module 2':mod1[i], 'Correct at Module 3':mod2[i]})

    csv_file.seek(0)

    return csv_file

def get_rm():
    csv_file = io.StringIO()

    header = ['Test ID','RTD -> VMON_LVS Module 1', 'ECON_RE_Sb -> HGCROC_RE_Sb Module 1', 'PWR_EN -> PG_LDO Module 1', 'RTD -> HGCROC_RE_Sb Module 1', 'HGCROC_RE_Hb -> HGCROC_RE_Sb Module 1', 'PG_DCDC -> ECON_RE_Hb Module 1', 'RTD -> VMON_LVS Module 2', 'ECON_RE_Sb -> HGCROC_RE_Sb Module 2', 'PWR_EN -> PG_LDO Module 2', 'RTD -> HGCROC_RE_Sb Module 2', 'HGCROC_RE_Hb -> HGCROC_RE_Sb Module 2', 'PG_DCDC -> ECON_RE_Hb Module 2', 'RTD -> VMON_LVS Module 3', 'ECON_RE_Sb -> HGCROC_RE_Sb Module 3', 'PWR_EN -> PG_LDO Module 3', 'RTD -> HGCROC_RE_Sb Module 3', 'HGCROC_RE_Hb -> HGCROC_RE_Sb Module 3', 'PG_DCDC -> ECON_RE_Hb Module 3']
    writer = csv.DictWriter(csv_file, fieldnames = header)

    cur.execute('select test_type from Test_Type where name="Resistance Measurement"')
    test_type_id = cur.fetchall()[0][0]

    cur.execute('select board_id from Board where full_id like "320W%"')
    boards_list = cur.fetchall()
    Tests = []
    for b in boards_list:
        cur.execute('select Test.test_id, Attachments.attach from Test left join Attachments on Test.test_id=Attachments.test_id where Test.board_id=%s and Test.test_type_id=%s order by Test.day desc, Test.test_id desc' % (b[0],test_type_id))
        test_id = cur.fetchone()
        if test_id:
            Tests.append(test_id)

    Attach_Data = []
    Tests_a = []
    for i in Tests:
        if i[0] not in [4792, 5092, 5127]:
            Attach_Data.append(json.loads(i[1]))
            Tests_a.append(i[0])

    RTD_VMON_1 = []
    ECON_HG_1 = []
    PWR_PG_1 = []
    RTD_HG_1 = []
    HG_HG_1 = []
    PG_ECON_1 = []
    RTD_VMON_2 = []
    ECON_HG_2 = []
    PWR_PG_2 = []
    RTD_HG_2 = []
    HG_HG_2 = []
    PG_ECON_2 = []
    RTD_VMON_3 = []
    ECON_HG_3 = []
    PWR_PG_3 = []
    RTD_HG_3 = []
    HG_HG_3 = []
    PG_ECON_3 = []
    
    # np.nan allows the column to be dropped later by df.dropna()
    # method is a little unpythonic but it allows the data to be formatted a little better
    for i in Attach_Data:
        try:
            RTD_VMON_1.append(i["module 1"]["RTD -> VMON_LVS"])
        except KeyError:
            try:
                RTD_VMON_1.append(i["test_data"]["module 1"]["RTD -> VMON_LVS"])
            except KeyError:
                RTD_VMON_1.append(np.nan)
        try:
            ECON_HG_1.append(i["module 1"]["ECON_RE_Sb -> HGCROC_RE_Sb"][0])
        except KeyError:
            try:
                ECON_HG_1.append(i["test_data"]["module 1"]["ECON_RE_Sb -> HGCROC_RE_Sb"][0])
            except KeyError:
                ECON_HG_1.append(np.nan)
        try:
            PWR_PG_1.append(i["module 1"]["PWR_EN -> PG_LDO"][0])
        except KeyError:
            try:
                PWR_PG_1.append(i["test_data"]["module 1"]["PWR_EN -> PG_LDO"][0])
            except KeyError:
                PWR_PG_1.append(np.nan)
        try:
            RTD_HG_1.append(i["module 1"]["RTD -> HGCROC_RE_Sb"])
        except KeyError:
            try:
                RTD_HG_1.append(i["test_data"]["module 1"]["RTD -> HGCROC_RE_Sb"])
            except KeyError:
                RTD_HG_1.append(np.nan)
        try:
            HG_HG_1.append(i["module 1"]["HGCROC_RE_Hb -> HGCROC_RE_Sb"][0])
        except KeyError:
            try:
                HG_HG_1.append(i["test_data"]["module 1"]["HGCROC_RE_Hb -> HGCROC_RE_Sb"][0])
            except KeyError:
                HG_HG_1.append(np.nan)
        try:
            PG_ECON_1.append(i["module 1"]["PG_DCDC -> ECON_RE_Hb"][0])
        except KeyError:
            try:
                PG_ECON_1.append(i["test_data"]["module 1"]["PG_DCDC -> ECON_RE_Hb"][0])
            except KeyError:
                PG_ECON_1.append(np.nan) 
        try:
            RTD_VMON_2.append(i["module 2"]["RTD -> VMON_LVS"])
        except KeyError:
            try:
                RTD_VMON_2.append(i["test_data"]["module 2"]["RTD -> VMON_LVS"])
            except KeyError:
                RTD_VMON_2.append(np.nan)
        try:
            ECON_HG_2.append(i["module 2"]["ECON_RE_Sb -> HGCROC_RE_Sb"][0])
        except KeyError:
            try:
                ECON_HG_2.append(i["test_data"]["module 2"]["ECON_RE_Sb -> HGCROC_RE_Sb"][0])
            except KeyError:
                ECON_HG_2.append(np.nan)
        try:
            PWR_PG_2.append(i["module 2"]["PWR_EN -> PG_LDO"][0])
        except KeyError:
            try:
                PWR_PG_2.append(i["test_data"]["module 2"]["PWR_EN -> PG_LDO"][0])
            except KeyError:
                PWR_PG_2.append(np.nan)
        try:
            RTD_HG_2.append(i["module 2"]["RTD -> HGCROC_RE_Sb"])
        except KeyError:
            try:
                RTD_HG_2.append(i["test_data"]["module 2"]["RTD -> HGCROC_RE_Sb"])
            except KeyError:
                RTD_HG_2.append(np.nan)
        try:
            HG_HG_2.append(i["module 2"]["HGCROC_RE_Hb -> HGCROC_RE_Sb"][0])
        except KeyError:
            try:
                HG_HG_2.append(i["test_data"]["module 2"]["HGCROC_RE_Hb -> HGCROC_RE_Sb"][0])
            except KeyError:
                HG_HG_2.append(np.nan)
        try:
            PG_ECON_2.append(i["module 2"]["PG_DCDC -> ECON_RE_Hb"][0])
        except KeyError:
            try:
                PG_ECON_2.append(i["test_data"]["module 2"]["PG_DCDC -> ECON_RE_Hb"][0])
            except KeyError:
                PG_ECON_2.append(np.nan)
        try:
            RTD_VMON_3.append(i["module 3"]["RTD -> VMON_LVS"])
        except KeyError:
            try:
                RTD_VMON_3.append(i["test_data"]["module 3"]["RTD -> VMON_LVS"])
            except KeyError:
                RTD_VMON_3.append(np.nan)
        try:
            ECON_HG_3.append(i["module 3"]["ECON_RE_Sb -> HGCROC_RE_Sb"][0])
        except KeyError:
            try:
                ECON_HG_3.append(i["test_data"]["module 3"]["ECON_RE_Sb -> HGCROC_RE_Sb"][0])
            except KeyError:
                ECON_HG_3.append(np.nan)
        try:
            PWR_PG_3.append(i["module 3"]["PWR_EN -> PG_LDO"][0])
        except KeyError:
            try:
                PWR_PG_3.append(i["test_data"]["module 3"]["PWR_EN -> PG_LDO"][0])
            except KeyError:
                PWR_PG_3.append(np.nan)
        try:
            RTD_HG_3.append(i["module 3"]["RTD -> HGCROC_RE_Sb"])
        except KeyError:
            try:
                RTD_HG_3.append(i["test_data"]["module 3"]["RTD -> HGCROC_RE_Sb"])
            except KeyError:
                RTD_HG_3.append(np.nan)
        try:
            HG_HG_3.append(i["module 3"]["HGCROC_RE_Hb -> HGCROC_RE_Sb"][0])
        except KeyError:
            try:
                HG_HG_3.append(i["test_data"]["module 3"]["HGCROC_RE_Hb -> HGCROC_RE_Sb"][0])
            except KeyError:
                HG_HG_3.append(np.nan)
        try:
            PG_ECON_3.append(i["module 3"]["PG_DCDC -> ECON_RE_Hb"][0])
        except KeyError:
            try:
                PG_ECON_3.append(i["test_data"]["module 3"]["PG_DCDC -> ECON_RE_Hb"][0])
            except KeyError:
                PG_ECON_3.append(np.nan)

    writer.writeheader()
    for i in range(len(Tests_a)):
        writer.writerow({'Test ID':Tests_a[i], 'RTD -> VMON_LVS Module 1':RTD_VMON_1[i], 'ECON_RE_Sb -> HGCROC_RE_Sb Module 1':ECON_HG_1[i], 'PWR_EN -> PG_LDO Module 1':PWR_PG_1[i], 'RTD -> HGCROC_RE_Sb Module 1':RTD_HG_1[i], 'HGCROC_RE_Hb -> HGCROC_RE_Sb Module 1':HG_HG_1[i], 'PG_DCDC -> ECON_RE_Hb Module 1':PG_ECON_1[i], 'RTD -> VMON_LVS Module 2':RTD_VMON_2[i], 'ECON_RE_Sb -> HGCROC_RE_Sb Module 2':ECON_HG_2[i], 'PWR_EN -> PG_LDO Module 2':PWR_PG_2[i], 'RTD -> HGCROC_RE_Sb Module 2':RTD_HG_2[i], 'HGCROC_RE_Hb -> HGCROC_RE_Sb Module 2':HG_HG_2[i], 'PG_DCDC -> ECON_RE_Hb Module 2':PG_ECON_2[i], 'RTD -> VMON_LVS Module 3':RTD_VMON_3[i], 'ECON_RE_Sb -> HGCROC_RE_Sb Module 3':ECON_HG_3[i], 'PWR_EN -> PG_LDO Module 3':PWR_PG_3[i], 'RTD -> HGCROC_RE_Sb Module 3':RTD_HG_3[i], 'HGCROC_RE_Hb -> HGCROC_RE_Sb Module 3':HG_HG_3[i], 'PG_DCDC -> ECON_RE_Hb Module 3':PG_ECON_3[i]})

    csv_file.seek(0)

    return csv_file

def get_bert():
    csv_file = io.StringIO()

    header = ['Test ID', 'E Link', 'Fit Eye Opening', 'Data Eye Opening', 'Module', 'Mod Elink', 'Fit Quality']
    writer = csv.DictWriter(csv_file, fieldnames=header)
    writer.writeheader()

    cur.execute('select test_type from Test_Type where name="Bit Error Rate Test"')
    test_type_id = cur.fetchall()[0][0]

    cur.execute('select board_id from Board where full_id like "320W%"')
    boards_list = cur.fetchall()
    TestIDs = []
    for b in boards_list:
        cur.execute('select Test.test_id, Attachments.attach from Test left join Attachments on Test.test_id=Attachments.test_id where Test.board_id=%s and Test.test_type_id=%s order by Test.day desc, Test.test_id desc' % (b[0],test_type_id))
        test_id = cur.fetchone()
        if test_id:
            TestIDs.append(test_id)

    Attach_Data = []
    for i in TestIDs:
        try:
            Attach_Data.append(json.loads(i[1])['test_data'])
        except KeyError:
            Attach_Data.append(json.loads(i[1]))

    # a nicer, more pythonic way of writing the data
    # does the stacking ahead of time with the E Links
    # when the attached data is in a nicer format like this test, this is the better way to do it
    for n in range(len(Attach_Data)):
            keys = Attach_Data[n].keys()
            for j in keys:
                try:
                    writer.writerow({'Test ID':TestIDs[n][0], 'E Link':j, 'Fit Eye Opening':Attach_Data[n][j]['Fit Eye Opening'], 'Data Eye Opening':Attach_Data[n][j]['Data Eye Opening'], 'Module':Attach_Data[n][j]['Module'], 'Mod Elink':Attach_Data[n][j]['Mod_Elink'], 'Fit Quality':Attach_Data[n][j]['Fit Quality']})
                except KeyError:
                    try:
                        writer.writerow({'Test ID':TestIDs[n][0], 'E Link':j, 'Fit Eye Opening':Attach_Data[n][j]['Fit Eye Opening'], 'Data Eye Opening':Attach_Data[n][j]['Data Eye Opening'], 'Module':Attach_Data[n][j]['Module'], 'Mod Elink':'CLK', 'Fit Quality':Attach_Data[n][j]['Fit Quality']})
                    except KeyError:
                        continue

    csv_file.seek(0)

    return csv_file
               
def get_board(): 
    csv_file = io.StringIO()

    header = ['Full ID', 'Board ID', 'Sub Type', 'Location', 'Major Type']
    writer = csv.writer(csv_file)
    writer.writerow(header)
    
    cur.execute('select full_id,board_id,type_id,location from Board')
    Temp_Data = cur.fetchall()
    Board_Data = []
    for line in Temp_Data:
        Board_Data.append(line + (line[0][3:5],))
    writer.writerows(Board_Data)

    csv_file.seek(0)

    return csv_file

def get_people():
    csv_file = io.StringIO()

    header = ['Person ID', 'Person Name']
    writer = csv.writer(csv_file)
    writer.writerow(header)
    
    cur.execute('select * from People')
    People_Data = cur.fetchall()
    writer.writerows(People_Data)

    csv_file.seek(0)

    return csv_file

def get_test_types():
    csv_file = io.StringIO()

    columns = ['Test Type ID', 'Name', 'Required', 'Short Desc.', 'Long Desc.', 'Relative Order']
    writer = csv.writer(csv_file)
    writer.writerow(columns)

    cur.execute('select * from Test_Type')
    Test_Data = cur.fetchall()
    writer.writerows(Test_Data)

    csv_file.seek(0)

    return csv_file

def get_attachments():
    csv_file = io.StringIO()

    columns = ['Test ID', 'Attach ID']
    writer = csv.writer(csv_file)
    writer.writerow(columns)

    cur.execute('select test_id, attach_id from Attachments')
    Test_Data = cur.fetchall()
    writer.writerows(Test_Data)

    csv_file.seek(0)

    return csv_file

def get_tests_required():
    cur.execute('select Test_Type.name from Test_Type left join Type_test_stitch on Test_Type.test_type=Type_test_stitch.test_type_id where type_id=62 order by relative_order asc')
    temp = cur.fetchall()
    ld_tests = []
    for t in temp:
        ld_tests.append(t[0])

    cur.execute('select Test_Type.name from Test_Type left join Type_test_stitch on Test_Type.test_type=Type_test_stitch.test_type_id where type_id=122 order by relative_order asc')
    temp = cur.fetchall()
    hd_tests = []
    for t in temp:
        hd_tests.append(t[0])

    cur.execute('select Test_Type.name from Test_Type left join Type_test_stitch on Test_Type.test_type=Type_test_stitch.test_type_id where type_id=72 order by relative_order asc')
    temp = cur.fetchall()
    zp_tests = []
    for t in temp:
        zp_tests.append(t[0])

    return ld_tests, hd_tests, zp_tests

def get_board_for_filter():
    csv_file = io.StringIO()

    header = ['Full ID', 'Major Type', 'Sub Type', 'Location', 'Test Name', 'Status', 'Date Completed', 'Real Dates']
    writer = csv.DictWriter(csv_file, fieldnames=header)
    writer.writeheader()

    cur.execute('select full_id,type_id,location,board_id from Board')
    boards = cur.fetchall()

    prev_ids = {}
    for board in boards:
        cur.execute('select type_id from Board_type where type_sn="%s"' % board[1])
        type_id = cur.fetchall()[0][0]

        cur.execute('select test_type_id from Type_test_stitch where type_id=%s' % type_id)
        for t in cur.fetchall():
            cur.execute('select name from Test_Type where test_type=%s' % t[0])
            name = cur.fetchall()[0][0]

            cur.execute('select day,successful from Test where board_id=%s and test_type_id=%s order by day desc, test_id desc' % (board[3], t[0]))
            test = cur.fetchall()
            if test:
                if test[0][1] == 1:
                    writer.writerow({'Full ID': board[0],
                                    'Major Type': board[0][3:5],
                                    'Sub Type': board[1],
                                    'Location': board[2],
                                    'Test Name': name,
                                    'Status': 'Passed',
                                    'Date Completed': test[0][0],
                                    'Real Dates': test[0][0],
                                    })
                if test[0][1] == 0:
                    writer.writerow({'Full ID': board[0],
                                    'Major Type': board[0][3:5],
                                    'Sub Type': board[1],
                                    'Location': board[2],
                                    'Test Name': name,
                                    'Status': 'Failed',
                                    'Date Completed': test[0][0],
                                    'Real Dates': test[0][0],
                                    })
            else:
                writer.writerow({'Full ID': board[0],
                                'Major Type': board[0][3:5],
                                'Sub Type': board[1],
                                'Location': board[2],
                                'Test Name': name,
                                'Status': 'Not Run',
                                'Date Completed': datetime.datetime.now(),
                                'Real Dates': datetime.datetime.now(),
                                })
    
    csv_file.seek(0)

    return csv_file

def get_check_in():
    csv_file = io.StringIO()

    columns = ['Board ID', 'Check In Time', 'Check Out Time']
    writer = csv.DictWriter(csv_file, fieldnames=columns)
    writer.writeheader()

    cur.execute('select board_id, checkin_date from Check_In')
    CheckIn_Data = cur.fetchall()
    for c in CheckIn_Data:
        cur.execute('select checkout_date from Check_Out where board_id=%s' % c[0])
        checkout_date = cur.fetchall()
        if checkout_date:
            writer.writerow({'Board ID': c[0], 'Check In Time': c[1], 'Check Out Time': checkout_date[0][0]})
        else:
            writer.writerow({'Board ID': c[0], 'Check In Time': c[1], 'Check Out Time': datetime.datetime.fromtimestamp(0)})

    csv_file.seek(0)

    return csv_file

def get_check_out():
    csv_file = io.StringIO()

    columns = ['Board ID', 'Person ID', 'Shipping Location', 'Time']
    writer = csv.writer(csv_file)
    writer.writerow(columns)

    cur.execute('select board_id, person_id, comment, checkout_date from Check_Out')
    check_out = cur.fetchall()
    for c in check_out:
        loc = c[2].split()[-1]
        writer.writerow((c[0], c[1], loc, c[3]))

    csv_file.seek(0)

    return csv_file

def get_zipper_rm():
    csv_file = io.StringIO()

    header = ['Test ID','Resistance']
    writer = csv.DictWriter(csv_file, fieldnames = header)

    cur.execute('select test_type from Test_Type where name="Zipper Resistance Measurement"')
    test_type_id = cur.fetchall()[0][0]

    cur.execute('select board_id from Board where full_id like "320Z%"')
    boards_list = cur.fetchall()
    Tests = []
    for b in boards_list:
        cur.execute('select Test.test_id, Attachments.attach from Test left join Attachments on Test.test_id=Attachments.test_id where Test.board_id=%s and Test.test_type_id=%s order by Test.day desc, Test.test_id desc' % (b[0],test_type_id))
        test_id = cur.fetchone()
        if test_id:
            Tests.append(test_id)

    Attach_Data = []
    for i in Tests:
        Attach_Data.append(json.loads(i[1]))
    Resistance = []
    Tests_a = []
    for idx,i in enumerate(Attach_Data):
        try:
            Resistance.append(i["test_data"]['wagon type chip']['WAGON_TYPE -> GND'])
            Tests_a.append(Tests[idx][0])
        except KeyError:
            try:
                Resistance.append(i['wagon type chip']['WAGON_TYPE -> GND'])
                Tests_a.append(Tests[idx][0])
            except KeyError:
                pass

    writer.writeheader()
    for i in range(len(Tests_a)):
        writer.writerow({'Test ID':Tests_a[i], 'Resistance':Resistance[i]})

    csv_file.seek(0)

    return csv_file

def get_zipper_bert():
    csv_file = io.StringIO()

    header = ['Test ID', 'E Link', 'Fit Eye Opening', 'Data Eye Opening', 'Fit Quality']
    writer = csv.DictWriter(csv_file, fieldnames=header)
    writer.writeheader()

    cur.execute('select test_type from Test_Type where name="Zipper Bit Error Rate Test"')
    test_type_id = cur.fetchall()[0][0]

    cur.execute('select board_id from Board where full_id like "320Z%"')
    boards_list = cur.fetchall()
    TestIDs = []
    for b in boards_list:
        cur.execute('select Test.test_id, Attachments.attach from Test left join Attachments on Test.test_id=Attachments.test_id where Test.board_id=%s and Test.test_type_id=%s order by Test.day desc, Test.test_id desc' % (b[0],test_type_id))
        test_id = cur.fetchone()
        if test_id:
            TestIDs.append(test_id)

    Attach_Data = []
    for i in TestIDs:
        Attach_Data.append(json.loads(i[1]))

    # a nicer, more pythonic way of writing the data
    # does the stacking ahead of time with the E Links
    # when the attached data is in a nicer format like this test, this is the better way to do it
    for n in range(len(Attach_Data)):
            keys = Attach_Data[n]
            for j,k in enumerate(keys):
                try:
                    writer.writerow({'Test ID':TestIDs[n][0], 'E Link':f'Link {j}', 'Fit Eye Opening':k['Fit Eye Opening'], 'Data Eye Opening':k['Data Eye Opening'], 'Fit Quality':k['Fit Quality']})
                except KeyError:
                    continue

    csv_file.seek(0)

    return csv_file
    
def get_tests_needed_dict():
    
    cur.execute('select board_id from Check_In')
    boards = cur.fetchall()

    tests_needed = {}
    for b in boards:
        try:
            cur.execute('select type_id from Board where board_id=%s' % b[0])
            type_sn = cur.fetchall()[0][0]
        except IndexError:
            continue
        
        cur.execute('select full_id from Board where board_id=%s' % b[0])
        full_id = cur.fetchall()[0][0]
        
        cur.execute('select type_id from Board_type where type_sn="%s"' % type_sn)
        type_id = cur.fetchall()[0][0]
        cur.execute('select test_type_id from Type_test_stitch where type_id=%s' % type_id)
        temp = cur.fetchall()
        stitch_types = []
        for test in temp:
            stitch_types.append(test[0])

        tests_needed[full_id] = len(stitch_types)

    return tests_needed

def get_stitch_types():
    cur.execute('''
        select BT.type_sn, TTS.type_id, TT.test_type, TT.name
        from Type_test_stitch TTS
        join Board_type BT on BT.type_id=TTS.type_id
        join Test_Type TT on TTS.test_type_id = TT.test_type
    ''')
    stitch_types_by_subtype = {}
    for type_sn, type_id, test_type_id, test_name in cur.fetchall():
        stitch_types_by_subtype.setdefault(type_sn, []).append((test_type_id, test_name))

    return stitch_types_by_subtype


def get_board_states():

    cur.execute('''
        select B.full_id, B.type_id, B.board_id, BT.name as nickname, BT.type_id as bt_type_id, B.location, C.checkin_date  
        from Board B
        join Board_type BT on B.type_id=BT.type_sn
        join Check_In C on B.board_id=C.board_id
        order by B.type_id
    ''')
    all_boards = cur.fetchall()

    boards_by_major_type = {}
    board_info = {}
    for full_id, type_sn, board_id, nickname, bt_type_id, location, checkin_date in all_boards:
        boards_by_major_type.setdefault(type_sn[0:2], []).append(full_id)
        board_info[full_id] = {
                'board_id': board_id,
                'type_sn': type_sn,
                'bt_type_id': bt_type_id,
                'nickname': nickname,
                'check_in_time': checkin_date,
                'location': location,
        }

    cur.execute('''
        select T.board_id, T.test_type_id, T.successful
        from Test T
        join (
            select board_id, test_type_id, MAX(test_id) as latest_test_id
            from Test
            group by board_id, test_type_id
        ) latest on T.test_id = latest.latest_test_id
    ''')

    test_results = {}
    for board_id, test_type_id, successful in cur.fetchall():
        test_results.setdefault(board_id, {})[test_type_id] = successful

    cur.execute('''
        select TTS.type_id, TT.test_type, TT.name
        from Type_test_stitch TTS
        join Test_Type TT on TTS.test_type_id = TT.test_type
    ''')
    stitch_types_by_subtype = {}
    for type_id, test_type_id, test_name in cur.fetchall():
        stitch_types_by_subtype.setdefault(type_id, []).append((test_type_id, test_name))

    cur.execute('select board_id from Check_Out')
    shipped_board_ids = set(row[0] for row in cur.fetchall())

    csvs_to_return = []

    for major_type, boards in boards_by_major_type.items():
        bt_type_id = board_info[boards[0]]['bt_type_id']
        stitch_types = stitch_types_by_subtype.get(bt_type_id, [])

        csv_file = io.StringIO()

        writer = csv.writer(csv_file)
        header = ['Subtype', 'Nickname', 'Full ID', 'Check In Time', 'Location']

        for test_type_id, test_name in stitch_types:
            header.append(test_name)

        header.append('Status')
        writer.writerow(header)

        for full_id in boards:
            row = [
                    board_info[full_id]['type_sn'],
                    board_info[full_id]['nickname'],
                    full_id, 
                    board_info[full_id]['check_in_time'],
                    board_info[full_id]['location'],
                    ]
            board_id = board_info[full_id]['board_id']
            failed = {}
            outcomes = {}
            for test_type_id, test_name in stitch_types:
                result = test_results.get(board_id, {}).get(test_type_id)
                outcomes[test_name] = result == 1
                failed[test_name] = result == 0
                if result == 1:
                    row.append('Passed')
                elif result == 0:
                    row.append('Failed')
                else:
                    row.append('Not Run')


            num_tests_passed = sum(outcomes.values())
            num_tests_req = len(outcomes)
            num_tests_failed = sum(failed.values())

            if board_id in shipped_board_ids:
                status = 'Shipped'
            elif num_tests_failed != 0:
                status = 'Failed QC'
            elif num_tests_passed == num_tests_req:
                status = 'Ready for Shipping'
            elif (num_tests_passed == num_tests_req - 1 and not outcomes.get('Registered', False)):
                status = 'Passed QC, Awaiting Registration'
            else:
                status = 'Awaiting Testing'

            row.append(status)
            writer.writerow(row)

        csv_file.seek(0)
        csvs_to_return.append(csv_file)

    return csvs_to_return


def write_board_statuses_file():

    status = {}

    stitch_types = {}

    cur.execute('select type_sn from Board_type')
    types = cur.fetchall()
    
    today = datetime.date.today()
    min_date = datetime.date(2024, 10, 4)
    while min_date <= today:
        status[str(min_date)] = {}
        for s in types:
            stitch_types[s[0]] = []
            cur.execute('select type_id from Board_type where type_sn="%s"' % s[0])
            type_id = cur.fetchall()[0][0]
            cur.execute('select test_type_id from Type_test_stitch where type_id=%s' % type_id)
            temp = cur.fetchall()
            for test in temp:
                stitch_types[s[0]].append(test[0])

            try:
                status[str(min_date)][s[0][0:2]][s[0]] = {}
            except KeyError:
                status[str(min_date)][s[0][0:2]] = {}
                status[str(min_date)][s[0][0:2]][s[0]] = {}
            
        min_date += datetime.timedelta(days=1)

    last = next(reversed(status))
    for day in status.keys():
        day1 = datetime.datetime.strptime(day, '%Y-%m-%d') + datetime.timedelta(days=1)
        day1 = datetime.datetime.combine(day1, datetime.time.min).strftime('%Y-%m-%d %H:%M:%S')
        cur.execute('select board_id from Check_In where checkin_date < "%s"' % day1)
        boards = cur.fetchall()

        with open('/home/webapp/pro/HGCAL_QC_WebInterface/cgi-bin/WagonDB/cache/current_board_status.csv', 'w') as csv_file:

            header = ['Sub Type', 'Full ID', 'Status']
            writer = csv.writer(csv_file)
            writer.writerow(header)

            for b in boards:
                if b[0] == 0:
                    continue
                cur.execute('select full_id from Board where board_id="%s"' % b[0])
                sn = cur.fetchall()[0][0]
                failed = {}
                outcomes = {}
                # makes an array of falses the length of the number of tests
                for t in stitch_types[sn[3:9]]:
                    outcomes[t] = False
                    failed[t] = False

                cur.execute('select test_type_id, successful, day from Test where board_id=%s and day<"%s" order by day desc, test_id desc' % (b[0], day1))
                temp = cur.fetchall()
                ids = []
                for t in temp:
                    if t[0] not in ids:
                        if t[1] == 1:
                            outcomes[t[0]] = True
                        else:
                            failed[t[0]] = True
                    ids.append(t[0])

                num = list(outcomes.values()).count(True)
                total = len(outcomes.values())
                failed_num = list(failed.values()).count(True)

                cur.execute('select board_id from Check_Out where board_id=%s' % b[0])
                checked_out = cur.fetchall()
                if checked_out:
                    s = 'Shipped'
                else:
                    if failed_num != 0:
                        s = 'Failed QC'
                    else:
                        if num == total:
                            s = 'Ready for Shipping'
                        elif (num == total-1 and outcomes[7] == False):
                            s = 'Passed QC, Awaiting Registration'
                        else:
                            s = 'Awaiting Testing'
                
                

                try:
                    status[day][sn[3:5]][sn[3:9]][s] += 1
                except:
                    status[day][sn[3:5]][sn[3:9]][s] = 1
                try:
                    status[day][sn[3:5]][sn[3:9]]['Total'] += 1
                except:
                    status[day][sn[3:5]][sn[3:9]]['Total'] = 1

                if day == last:
                    writer.writerow([sn[3:9], sn, s])


    with open('/home/webapp/pro/HGCAL_QC_WebInterface/cgi-bin/WagonDB/cache/store_board_status.pkl', "wb") as f:
        pickle.dump(status, f)


def get_board_statuses():

    with open('/home/webapp/pro/HGCAL_QC_WebInterface/cgi-bin/WagonDB/cache/store_board_status.pkl', "rb") as f:
        status = pickle.load(f)

    return status

def write_datafiles():
    write_board_statuses_file()
