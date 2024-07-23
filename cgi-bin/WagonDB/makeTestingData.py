from connect import connect
import numpy as np
import json
import csv
import os
import io
import pandas as pd

path = os.path.dirname(os.path.abspath(__file__))

p = '%s/../../static/WagonDB/' % path
if not os.path.isdir(p):
    os.makedirs(p)

db = connect(0)
cur = db.cursor()

# collects all the necessary data from the database to be put into .csv WagonDB for the plotting scripts

def get_test():
    # some data can easily be written into a .csv just by writing rows
    # in this case a csv.writer can be used

    csv_file = io.StringIO()

    columns = ['Test ID', 'Test Type ID', 'Board ID', 'Person ID', 'Time', 'Successful']
    writer = csv.writer(csv_file)
    writer.writerow(columns)

    cur.execute('select test_id, test_type_id, board_id, person_id, day, successful from Test')
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
    cur.execute('select test_id from Test where test_type_id="{}"'.format(test_type_id))
    TestIDs = cur.fetchall()

    # selects the attachment for all the test ids
    query = 'select attach from Attachments where '
    for i in TestIDs:
        # adds the test id to the query
        query += 'test_id={}'.format(i[0])
        # adds or if the test id isn't the last one
        if i is not TestIDs[-1]:
            query += ' or '
    # collects attachments
    cur.execute(query)
    Attach = cur.fetchall()
    Attach_Data = []
    # decodes the json
    for i in Attach:
        Attach_Data.append(json.loads(i[0]))
    Resistance = []
    # gets the resistance out of the array
    for i in Attach_Data:
        try:
            Resistance.append(i['wagon type chip']['WAGON_TYPE -> GND'])
        except KeyError as e:
            Resistance.append(-1)

    # writes everything to the file
    writer.writeheader()
    for i in range(len(TestIDs)):
        writer.writerow({'Test ID':TestIDs[i][0], 'Resistance':Resistance[i]})

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
        except KeyError as e:
            RTD_VMON_1.append(np.nan)
        try:
            ECON_HG_1.append(i["module 1"]["ECON_RE_Sb -> HGCROC_RE_Sb"][0])
        except KeyError as e:
            ECON_HG_1.append(np.nan)
        try:
            PWR_PG_1.append(i["module 1"]["PWR_EN -> PG_LDO"][0])
        except KeyError as e:
            PWR_PG_1.append(np.nan)
        try:
            RTD_HG_1.append(i["module 1"]["RTD -> HGCROC_RE_Sb"])
        except KeyError as e:
            RTD_HG_1.append(np.nan)
        try:
            HG_HG_1.append(i["module 1"]["HGCROC_RE_Hb -> HGCROC_RE_Sb"][0])
        except KeyError as e:
            HG_HG_1.append(np.nan)
        try:
            PG_ECON_1.append(i["module 1"]["PG_DCDC -> ECON_RE_Hb"][0])
        except KeyError as e:
            PG_ECON_1.append(np.nan) 
        try:
            RTD_VMON_2.append(i["module 2"]["RTD -> VMON_LVS"])
        except KeyError as e:
            RTD_VMON_2.append(np.nan)
        try:
            ECON_HG_2.append(i["module 2"]["ECON_RE_Sb -> HGCROC_RE_Sb"][0])
        except KeyError as e:
            ECON_HG_2.append(np.nan)
        try:
            PWR_PG_2.append(i["module 2"]["PWR_EN -> PG_LDO"][0])
        except KeyError as e:  
            PWR_PG_2.append(np.nan)
        try:
            RTD_HG_2.append(i["module 2"]["RTD -> HGCROC_RE_Sb"])
        except KeyError as e:
            RTD_HG_2.append(np.nan)
        try:
            HG_HG_2.append(i["module 2"]["HGCROC_RE_Hb -> HGCROC_RE_Sb"][0])
        except KeyError as e:
            HG_HG_2.append(np.nan)
        try:
            PG_ECON_2.append(i["module 2"]["PG_DCDC -> ECON_RE_Hb"][0])
        except KeyError as e:
            PG_ECON_2.append(np.nan)
        try:
            RTD_VMON_3.append(i["module 3"]["RTD -> VMON_LVS"])
        except KeyError as e:
            RTD_VMON_3.append(np.nan)
        try:
            ECON_HG_3.append(i["module 3"]["ECON_RE_Sb -> HGCROC_RE_Sb"][0])
        except KeyError as e:
            ECON_HG_3.append(np.nan)
        try:
            PWR_PG_3.append(i["module 3"]["PWR_EN -> PG_LDO"][0])
        except KeyError as e:  
            PWR_PG_3.append(np.nan)
        try:
            RTD_HG_3.append(i["module 3"]["RTD -> HGCROC_RE_Sb"])
        except KeyError as e:
            RTD_HG_3.append(np.nan)
        try:
            HG_HG_3.append(i["module 3"]["HGCROC_RE_Hb -> HGCROC_RE_Sb"][0])
        except KeyError as e:
            HG_HG_3.append(np.nan)
        try:
            PG_ECON_3.append(i["module 3"]["PG_DCDC -> ECON_RE_Hb"][0])
        except KeyError as e:
            PG_ECON_3.append(np.nan)

    writer.writeheader()
    for i in range(len(TestIDs)):
        writer.writerow({'Test ID':TestIDs[i][0], 'RTD -> VMON_LVS Module 1':RTD_VMON_1[i], 'ECON_RE_Sb -> HGCROC_RE_Sb Module 1':ECON_HG_1[i], 'PWR_EN -> PG_LDO Module 1':PWR_PG_1[i], 'RTD -> HGCROC_RE_Sb Module 1':RTD_HG_1[i], 'HGCROC_RE_Hb -> HGCROC_RE_Sb Module 1':HG_HG_1[i], 'PG_DCDC -> ECON_RE_Hb Module 1':PG_ECON_1[i], 'RTD -> VMON_LVS Module 2':RTD_VMON_2[i], 'ECON_RE_Sb -> HGCROC_RE_Sb Module 2':ECON_HG_2[i], 'PWR_EN -> PG_LDO Module 2':PWR_PG_2[i], 'RTD -> HGCROC_RE_Sb Module 2':RTD_HG_2[i], 'HGCROC_RE_Hb -> HGCROC_RE_Sb Module 2':HG_HG_2[i], 'PG_DCDC -> ECON_RE_Hb Module 2':PG_ECON_2[i], 'RTD -> VMON_LVS Module 3':RTD_VMON_3[i], 'ECON_RE_Sb -> HGCROC_RE_Sb Module 3':ECON_HG_3[i], 'PWR_EN -> PG_LDO Module 3':PWR_PG_3[i], 'RTD -> HGCROC_RE_Sb Module 3':RTD_HG_3[i], 'HGCROC_RE_Hb -> HGCROC_RE_Sb Module 3':HG_HG_3[i], 'PG_DCDC -> ECON_RE_Hb Module 3':PG_ECON_3[i]})

    csv_file.seek(0)

    return csv_file

def get_bert():
    csv_file = io.StringIO()

    header = ['Test ID', 'E Link', 'Midpoint', 'Eye Opening', 'Passed', 'Midpoint Errors']
    writer = csv.DictWriter(csv_file, fieldnames=header)
    writer.writeheader()

    cur.execute('select test_type from Test_Type where name="Bit Error Rate Test"')
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

    # a nicer, more pythonic way of writing the data
    # does the stacking ahead of time with the E Links
    # when the attached data is in a nicer format like this test, this is the better way to do it
    for n in range(len(Attach_Data)):
            keys = Attach_Data[n].keys()
            for j in keys:
                try:
                    writer.writerow({'Test ID':TestIDs[n][0], 'E Link':j, 'Midpoint':Attach_Data[n][j]['Midpoint'], 'Eye Opening':Attach_Data[n][j]['Eye Opening'], 'Passed':Attach_Data[n][j]['passed'], 'Midpoint Errors':Attach_Data[n][j]['Midpoint Errors']})
                except:
                    pass

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
        if line[0][4] == 'H':
            Board_Data.append(line + ('HD',))
        else:
            Board_Data.append(line + ('LD',))
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


