from connect import connect
import numpy as np
import json
import csv

db = connect(0)
cur = db.cursor()

with open('./static/files/Test.csv', mode='w') as csv_file:
    columns = ['Test ID', 'Test Type ID', 'Board ID', 'Person ID', 'Time', 'Successful','comments']
    writer = csv.writer(csv_file)
    writer.writerow(columns)

    cur.execute('select * from Test')
    Test_Data = cur.fetchall()
    writer.writerows(Test_Data)

with open('./static/files/ID_Resistor_Test_Data.csv', mode='w') as csv_file:
    header = ['Test ID','Resistance']
    writer = csv.DictWriter(csv_file, fieldnames = header)

    cur.execute('select test_type from Test_Type where name="ID Resistor Measurement"')
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
    Resistance = []
    for i in Attach_Data:
        try:
            Resistance.append(i['wagon type chip']['WAGON_TYPE -> GND'])
        except KeyError as e:
            Resistance.append(-1)

    writer.writeheader()
    for i in range(len(TestIDs)):
        writer.writerow({'Test ID':TestIDs[i][0], 'Resistance':Resistance[i]})

with open('./static/files/I2C_ReadWrite_Test_Data.csv', mode='w') as csv_file:
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
    for i in Attach_Data:
        mod9999.append(i['num_iic_checks_mod9999'])
        mod0.append(i['num_iic_correct_mod0'])
        try:
            mod1.append(i['num_iic_correct_mod1'])
        except KeyError as e:
            mod1.append(-1)
        try:
            mod2.append(i['num_iic_correct_mod2'])
        except KeyError as e:
            mod2.append(-1)

    writer.writeheader()
    for i in range(len(TestIDs)):
        writer.writerow({'Test ID':TestIDs[i][0], 'Checks':mod9999[i], 'Correct at Module 1':mod0[i], 'Correct at Module 2':mod1[i], 'Correct at Module 3':mod2[i]})

with open('./static/files/Resistance_Measurement.csv', mode='w') as csv_file:
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

with open('./static/files/Bit_Error_Rate_Test_Data.csv', mode='w') as csv_file:
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

    for n in range(len(Attach_Data)):
            keys = Attach_Data[n].keys()
            for j in keys:
                writer.writerow({'Test ID':TestIDs[n][0], 'E Link':j, 'Midpoint':Attach_Data[n][j]['Midpoint'], 'Eye Opening':Attach_Data[n][j]['Eye Opening'], 'Passed':Attach_Data[n][j]['passed'], 'Midpoint Errors':Attach_Data[n][j]['Midpoint Errors']})
            
with open('./static/files/Board.csv', mode='w') as csv_file:
    header = ['Full ID', 'Board ID', 'Type ID']
    writer = csv.writer(csv_file)
    writer.writerow(header)
    
    cur.execute('select full_id,board_id,type_id from Board')
    Board_Data = cur.fetchall()
    writer.writerows(Board_Data)

with open('./static/files/People.csv', mode='w') as csv_file:
    header = ['Person ID', 'Person Name']
    writer = csv.writer(csv_file)
    writer.writerow(header)
    
    cur.execute('select * from People')
    People_Data = cur.fetchall()
    writer.writerows(People_Data)

with open('./static/files/Test_Types.csv', mode='w') as csv_file:
    columns = ['Test Type', 'Name', 'Required', 'Short Desc.', 'Long Desc.', 'Relative Order']
    writer = csv.writer(csv_file)
    writer.writerow(columns)

    cur.execute('select * from Test_Type')
    Test_Data = cur.fetchall()
    writer.writerows(Test_Data)

with open('./static/files/TestRevoke.csv', mode='w') as csv_file:
    columns = ['Test ID', 'Comment']
    writer = csv.writer(csv_file)
    writer.writerow(columns)

    cur.execute('select * from TestRevoke')
    Test_Data = cur.fetchall()
    writer.writerows(Test_Data)

with open('./static/files/Attachments.csv', mode='w') as csv_file:
    columns = ['Test ID', 'Attachment']
    writer = csv.writer(csv_file)
    writer.writerow(columns)

    cur.execute('select * from Attachments')
    Test_Data = cur.fetchall()
    writer.writerows(Test_Data)
