from connect import connect
import numpy as np
import json
import csv

db = connect(0)
cur = db.cursor()

with open('./static/files/Labels.csv', mode='w') as csv_file:
    columns = ['Label ID', 'Full Label', 'Type Code', 'SN', 'Major Type ID', 'Sub Type ID', 'Time']
    writer = csv.writer(csv_file)
    writer.writerow(columns)

    cur.execute('select label_id, full_label, type_code, sn, major_type_id, sub_type_id, creation_date from Label')
    Test_Data = cur.fetchall()
    writer.writerows(Test_Data)

with open('./static/files/MajorType.csv', mode='w') as csv_file:
    columns = ['Major Type ID', 'Major Type']
    writer = csv.writer(csv_file)
    writer.writerow(columns)

    cur.execute('select major_type_id, name, major_code from Major_Type')
    Test_Data = cur.fetchall()
    data = []
    for t in Test_Data:
        data.append([t[0], t[1] + ', ' + t[2]])
    writer.writerows(data)

with open('./static/files/SubType.csv', mode='w') as csv_file:
    columns = ['Sub Type ID', 'Sub Type']
    writer = csv.writer(csv_file)
    writer.writerow(columns)

    cur.execute('select sub_type_id, name, sub_code from Sub_Type')
    Test_Data = cur.fetchall()
    data = []
    for t in Test_Data:
        data.append([t[0], t[1] + ', ' + t[2]])
    writer.writerows(data)
