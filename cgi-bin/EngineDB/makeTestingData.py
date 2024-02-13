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

with open('./static/files/Power-Ground_Resistance.csv', mode='w') as csv_file:
    header = ['Test ID','Voltage']
    writer = csv.DictWriter(csv_file, fieldnames = header)

    cur.execute('select test_type from Test_Type where name="Power-Ground Resistance"')
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
    Voltage = []
    for i in Attach_Data:
        try:
            Voltage.append(i['voltage'])
        except KeyError as e:
            Voltage.append(-1)

    writer.writeheader()
    for i in range(len(TestIDs)):
        writer.writerow({'Test ID':TestIDs[i][0], 'Voltage':Voltage[i]})

with open('./static/files/1.5V_Input_Check.csv', mode='w') as csv_file:
    header= ['Test ID', 'Voltage']
    writer = csv.DictWriter(csv_file, fieldnames = header)

    cur.execute('select test_type from Test_Type where name="1.5V Input Check"')
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
    Voltage = []
    for i in Attach_Data:
        try:
            Voltage.append(i['voltage'])
        except KeyError as e:
            Voltage.append(0)

    writer.writeheader()
    for i in range(len(TestIDs)):
        writer.writerow({'Test ID':TestIDs[i][0], 'Voltage':Voltage[i]})

with open('./static/files/10V_Input_Check.csv', mode='w') as csv_file:
    header= ['Test ID', 'Voltage']
    writer = csv.DictWriter(csv_file, fieldnames = header)

    cur.execute('select test_type from Test_Type where name="10V Input Check"')
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
    Voltage = []
    for i in Attach_Data:
        try:
            Voltage.append(i['voltage'])
        except KeyError as e:
            Voltage.append(0)

    writer.writeheader()
    for i in range(len(TestIDs)):
        writer.writerow({'Test ID':TestIDs[i][0], 'Voltage':Voltage[i]})

with open('./static/files/1.2V_Output_Check.csv', mode='w') as csv_file:
    header= ['Test ID', 'Voltage']
    writer = csv.DictWriter(csv_file, fieldnames = header)

    cur.execute('select test_type from Test_Type where name="1.2V Output Check"')
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
    Voltage = []
    for i in Attach_Data:
        try:
            Voltage.append(i['voltage'])
        except KeyError as e:
            Voltage.append(0)

    writer.writeheader()
    for i in range(len(TestIDs)):
        writer.writerow({'Test ID':TestIDs[i][0], 'Voltage':Voltage[i]})

with open('./static/files/RX_2.5V_Output_Check.csv', mode='w') as csv_file:
    header= ['Test ID', 'Voltage']
    writer = csv.DictWriter(csv_file, fieldnames = header)

    cur.execute('select test_type from Test_Type where name="RX 2.5V Output Check"')
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
    Voltage = []
    for i in Attach_Data:
        try:
            Voltage.append(i['voltage'])
        except KeyError as e:
            Voltage.append(0)

    writer.writeheader()
    for i in range(len(TestIDs)):
        writer.writerow({'Test ID':TestIDs[i][0], 'Voltage':Voltage[i]})

with open('./static/files/TX_2.5V_Output_Check.csv', mode='w') as csv_file:
    header= ['Test ID', 'Voltage']
    writer = csv.DictWriter(csv_file, fieldnames = header)

    cur.execute('select test_type from Test_Type where name="TX 2.5V Output Check"')
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
    Voltage = []
    for i in Attach_Data:
        try:
            Voltage.append(i['voltage'])
        except KeyError as e:
            Voltage.append(0)

    writer.writeheader()
    for i in range(len(TestIDs)):
        writer.writerow({'Test ID':TestIDs[i][0], 'Voltage':Voltage[i]})
