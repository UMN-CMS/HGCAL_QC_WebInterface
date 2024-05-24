from connect import connect
import numpy as np
import json
import csv
import datetime

db = connect(0)
cur = db.cursor()

def run():
    with open('./static/files/Test.csv', mode='w') as csv_file:
        columns = ['Test ID', 'Test Type ID', 'Board ID', 'Person ID', 'Time', 'Successful','comments']
        writer = csv.writer(csv_file)
        writer.writerow(columns)

        cur.execute('select * from Test')
        Test_Data = cur.fetchall()
        writer.writerows(Test_Data)
     
    with open('./static/files/Board.csv', mode='w') as csv_file:
        header = ['Full ID', 'Board ID', 'Type ID', 'Location']
        writer = csv.writer(csv_file)
        writer.writerow(header)
        
        cur.execute('select full_id,board_id,type_id,location from Board')
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
        columns = ['Test Type ID', 'Name', 'Required', 'Short Desc.', 'Long Desc.', 'Relative Order']
        writer = csv.writer(csv_file)
        writer.writerow(columns)

        cur.execute('select * from Test_Type')
        Test_Data = cur.fetchall()
        writer.writerows(Test_Data)

    # opens four files at once
    with open('./static/files/ADC_functionality_resistance.csv', mode='w') as csv_file_resist, open('./static/files/ADC_functionality_voltage.csv', mode='w') as csv_file_volt, open('./static/files/ADC_functionality_temp.csv', mode='w') as csv_file_temp, open('./static/files/ADC_main.csv', mode='w') as csv_file_adc:
        # need a writer for each file
        header_resist = ['Test ID', 'E Link', 'Resistance']
        writer_1 = csv.DictWriter(csv_file_resist, fieldnames = header_resist)

        header_volt = ['Test ID', 'ADC', 'Voltage']
        writer_2 = csv.DictWriter(csv_file_volt, fieldnames = header_volt)

        header_temp = ['Test ID', 'Chip', 'Temperature']
        writer_3 = csv.DictWriter(csv_file_temp, fieldnames = header_temp)

        header_adc = ['Test ID', 'ADC', 'slope', 'intercept', 'rsquared']
        writer_4 = csv.DictWriter(csv_file_adc, fieldnames = header_adc)

        cur.execute('select test_type from Test_Type where name="ADC functionality"')
        type_id = cur.fetchall()[0][0]

        cur.execute('select test_id from Test where test_type_id={}'.format(type_id))
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
            try:
                Attach_Data.append(json.loads(i[0]['test_data']))
            except:
                Attach_Data.append(json.loads(i[0]))

        writer_1.writeheader()
        writer_2.writeheader()
        writer_3.writeheader()
        writer_4.writeheader()
        # this method of iterating over keys is preferrable
        # removes the need to use df.stack() like with the resistance measurement test
        for n in range(len(Attach_Data)):
            resist_keys = Attach_Data[n]['engine_all_rtd'].keys()
            volt_keys = Attach_Data[n]['int_volts'].keys()
            temp_keys = Attach_Data[n]['temp'].keys()
            adc_keys = Attach_Data[n]['walk_engine_read_adc'].keys()

            for j in resist_keys:
                Resistance = Attach_Data[n]['engine_all_rtd'][j]
                writer_1.writerow({'Test ID': TestIDs[n][0], 'E Link': j, 'Resistance': Resistance})

            # format is different for some older tests so this converts
            for k in volt_keys:
                if k[0:4] == 'east': 
                    v = k[0:4] + '_' + k[4:-1] + k[-1]
                    v = v.upper()
                elif k[0:4] == 'west': 
                    v = k[0:4] + '_' + k[4:-1] + k[-1]
                    v = v.upper()
                elif k[0:4] == 'daqv': 
                    v = k[0:3] + '_' + k[3:-1] + k[-1]
                    v = v.upper()
                else:
                    v = k
                        
                Voltage = Attach_Data[n]['int_volts'][k]
                writer_2.writerow({'Test ID': TestIDs[n][0], 'ADC': v, 'Voltage': Voltage})

            # format is different for some older tests so this converts
            for l in temp_keys:
                if l[0:4] == 'east': 
                    v = 'EAST_Temperature'
                elif l[0:4] == 'west': 
                    v = 'WEST_Temperature'
                elif l[0:3] == 'daq': 
                    v = 'DAQ_Temperature'
                else:
                    v = l

                try:
                    Temp = Attach_Data[n]['temp'][l]['temperature']
                except:
                    Temp = Attach_Data[n]['temp'][l]
                writer_3.writerow({'Test ID': TestIDs[n][0], 'Chip': v, 'Temperature': Temp})

            for i in adc_keys:
                slope = Attach_Data[n]['walk_engine_read_adc'][i][1]['slope']
                intercept = Attach_Data[n]['walk_engine_read_adc'][i][1]['intercept']
                r2 = Attach_Data[n]['walk_engine_read_adc'][i][1]['rsquared']
                writer_4.writerow({'Test ID': TestIDs[n][0], 'ADC': i, 'slope': slope, 'intercept': intercept, 'rsquared': r2})

    with open('./static/files/EClockRates.csv', mode='w') as csv_file:
        header = ['Test ID', 'Module 1', 'Module 2', 'Module 3', 'Module 4', 'Module 5', 'Module 6', 'Module 7']
        writer = csv.DictWriter(csv_file, fieldnames=header)
        
        cur.execute('select test_type from Test_Type where name="EClock Rates"')
        type_id = cur.fetchall()[0][0]

        cur.execute('select test_id from Test where test_type_id={}'.format(type_id))
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
            try:
                Attach_Data.append(json.loads(i[0]['test_data']))
            except:
                Attach_Data.append(json.loads(i[0]))

        writer.writeheader()
        for n in range(len(Attach_Data)):
            writer.writerow({'Test ID': TestIDs[n][0],
                            'Module 1': Attach_Data[n][0],
                            'Module 2': Attach_Data[n][1],
                            'Module 3': Attach_Data[n][2],
                            'Module 4': Attach_Data[n][3],
                            'Module 5': Attach_Data[n][4],
                            'Module 6': Attach_Data[n][5],
                            'Module 7': Attach_Data[n][6],})

    with open('./static/files/X_PWR.csv', mode='w') as csv_file:
        header = ['Test ID', 'Voltage']
        writer = csv.DictWriter(csv_file, fieldnames=header)
        writer.writeheader()

        cur.execute('select test_type from Test_Type where name="X_PWR"')
        type_id = cur.fetchall()[0][0]

        cur.execute('select test_id from Test where test_type_id={}'.format(type_id))
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
            try:
                Attach_Data.append(json.loads(i[0]['test_data']))
            except:
                Attach_Data.append(json.loads(i[0]))

        for n in range(len(Attach_Data)):
            writer.writerow({'Test ID': TestIDs[n][0], 'Voltage': Attach_Data[n]['voltage']})

    with open('./static/files/ElinkQuality.csv', mode='w') as csv_file:
        header = ['Test ID', 'Phase', 'E Link', 'Bit Errors']
        writer = csv.DictWriter(csv_file, fieldnames=header)
        writer.writeheader()

        cur.execute('select test_type from Test_Type where name="Elink Quality"')
        type_id = cur.fetchall()[0][0]

        cur.execute('select test_id from Test where test_type_id={}'.format(type_id))
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
            try:
                Attach_Data.append(json.loads(i[0]['test_data']))
            except:
                Attach_Data.append(json.loads(i[0]))

        for n in range(len(Attach_Data)):
            keys = Attach_Data[n].keys()
            for k in keys:
                for v in Attach_Data[n][k]:
                    writer.writerow({'Test ID': TestIDs[n][0], 'Phase': k, 'E Link': v[0], 'Bit Errors': v[1]})

    with open('./static/files/FastCommandQuality.csv', mode='w') as csv_file:
        header = ['Test ID', 'Phase', 'Channel', 'Bit Errors']
        writer = csv.DictWriter(csv_file, fieldnames=header)
        writer.writeheader()

        cur.execute('select test_type from Test_Type where name="Fast Command Quality"')
        type_id = cur.fetchall()[0][0]

        cur.execute('select test_id from Test where test_type_id={}'.format(type_id))
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
            try:
                Attach_Data.append(json.loads(i[0]['test_data']))
            except:
                Attach_Data.append(json.loads(i[0]))

        for n in range(len(Attach_Data)):
            try:
                keys = Attach_Data[n].keys()
                for k in keys:
                    for idx,v in enumerate(Attach_Data[n][k]):
                        writer.writerow({'Test ID': TestIDs[n][0], 'Phase': k, 'Channel': idx, 'Bit Errors': v})
            except AttributeError:
                pass

    with open('./static/files/UplinkQuality.csv', mode='w') as csv_file:
        header = ['Test ID', 'Module', 'Bit Errors']
        writer = csv.DictWriter(csv_file, fieldnames=header)
        writer.writeheader()

        cur.execute('select test_type from Test_Type where name="Uplink Quality"')
        type_id = cur.fetchall()[0][0]

        cur.execute('select test_id from Test where test_type_id=%(id)s and day>="%(date)s"' %{'id':type_id, 'date':datetime.datetime(2024, 4, 1)})
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
            try:
                Attach_Data.append(json.loads(i[0]['test_data']))
            except:
                Attach_Data.append(json.loads(i[0]))

        for n in range(len(Attach_Data)):
            for i in Attach_Data[n]:
                writer.writerow({'Test ID': TestIDs[n][0], 'Module': i[0], 'Bit Errors': i[1]})

    with open('./static/files/I2C.csv', mode='w') as csv_file:
        header = ['Test ID', 'Connector', 'Channel', 'Bit Errors']
        writer = csv.DictWriter(csv_file, fieldnames=header)
        writer.writeheader()

        cur.execute('select test_type from Test_Type where name="I2C"')
        type_id = cur.fetchall()[0][0]

        cur.execute('select test_id from Test where test_type_id={}'.format(type_id))
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
            try:
                Attach_Data.append(json.loads(i[0]['test_data']))
            except:
                Attach_Data.append(json.loads(i[0]))

        for n in range(len(Attach_Data)):
            keys = Attach_Data[n].keys()
            for k in keys:
                keys_2 = Attach_Data[n][k].keys()
                for v in keys_2:
                    writer.writerow({'Test ID': TestIDs[n][0], 'Connector': k, 'Channel': v, 'Bit Errors': Attach_Data[n][k][v]})

#    with open('./static/files/GPIO_Functionality.csv', mode='w') as csv_file:
#        header = ['Test ID', 'Pin', 'Passes', 'Fails']
#        writer = csv.DictWriter(csv_file, fieldnames=header)
#        writer.writeheader()
#
#        cur.execute('select test_type from Test_Type where name="GPIO functionality"')
#        type_id = cur.fetchall()[0][0]
#
#        cur.execute('select test_id from Test where test_type_id={}'.format(type_id))
#        TestIDs = cur.fetchall()
# 
#        query = 'select attach from Attachments where '
#        for i in TestIDs:
#            query += 'test_id={}'.format(i[0])
#            if i is not TestIDs[-1]:
#                query += ' or '
#        cur.execute(query)
#        Attach = cur.fetchall()
#
#        for i in range(len(Attach)):
#            try:
#                json.loads(Attach[i][0])
#            except json.decoder.JSONDecodeError:





if __name__ == '__main__':
    run()
