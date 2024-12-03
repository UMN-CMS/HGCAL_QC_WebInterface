from connect import connect
import numpy as np
import json
import csv
import datetime
import os
import io

path = os.path.dirname(os.path.abspath(__file__))

db = connect(0)
cur = db.cursor()

def get_test():
    csv_file = io.StringIO()

    columns = ['Test ID', 'Test Type ID', 'Board ID', 'Person ID', 'Time', 'Successful']
    writer = csv.writer(csv_file)
    writer.writerow(columns)

    cur.execute('select test_id, test_type_id, board_id, person_id, day, successful from Test order by day asc')
    Test_Data = cur.fetchall()
    writer.writerows(Test_Data)

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

def get_adc_functionality():
    # opens four files at once
    csv_file_resist = io.StringIO()
    csv_file_volt = io.StringIO()
    csv_file_temp = io.StringIO()
    csv_file_adc = io.StringIO()

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
            Attach_Data.append(json.loads(i[0])['test_data'])
        except:
            Attach_Data.append(json.loads(i[0]))

    writer_1.writeheader()
    writer_2.writeheader()
    writer_3.writeheader()
    writer_4.writeheader()
    # this method of iterating over keys is preferrable
    # removes the need to use df.stack() like with the resistance measurement test
    for n in range(len(Attach_Data)):
        try:
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
                try:
                    slope = Attach_Data[n]['walk_engine_read_adc'][i][1]['slope']
                    intercept = Attach_Data[n]['walk_engine_read_adc'][i][1]['intercept']
                    r2 = Attach_Data[n]['walk_engine_read_adc'][i][1]['rsquared']
                except KeyError:
                    slope = Attach_Data[n]['walk_engine_read_adc'][i]['slope']
                    intercept = Attach_Data[n]['walk_engine_read_adc'][i]['intercept']
                    r2 = Attach_Data[n]['walk_engine_read_adc'][i]['rsquared']

                writer_4.writerow({'Test ID': TestIDs[n][0], 'ADC': i, 'slope': slope, 'intercept': intercept, 'rsquared': r2})
        except KeyError:
            pass

    csv_file_resist.seek(0)
    csv_file_volt.seek(0)
    csv_file_temp.seek(0)
    csv_file_adc.seek(0)

    return csv_file_resist, csv_file_volt, csv_file_temp, csv_file_adc

def get_eclock_rates():
    csv_file = io.StringIO()

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
            Attach_Data.append(json.loads(i[0])['test_data'])
        except Exception as e:
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

    csv_file.seek(0)

    return csv_file

def get_xpwr():
    csv_file = io.StringIO()

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
            Attach_Data.append(json.loads(i[0])['test_data'])
        except:
            Attach_Data.append(json.loads(i[0]))

    for n in range(len(Attach_Data)):
        writer.writerow({'Test ID': TestIDs[n][0], 'Voltage': Attach_Data[n]['voltage']})

    csv_file.seek(0)

    return csv_file

def get_elink_quality():
    csv_file = io.StringIO()

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
            Attach_Data.append(json.loads(i[0])['test_data'])
        except:
            Attach_Data.append(json.loads(i[0]))

    for n in range(len(Attach_Data)):
        keys = Attach_Data[n].keys()
        for k in keys:
            for v in Attach_Data[n][k]:
                writer.writerow({'Test ID': TestIDs[n][0], 'Phase': k, 'E Link': v[0], 'Bit Errors': v[1]})

    csv_file.seek(0)

    return csv_file

def get_fast_command():
    csv_file = io.StringIO()

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
            Attach_Data.append(json.loads(i[0])['test_data'])
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

    csv_file.seek(0)

    return csv_file

def get_uplink_quality():
    csv_file = io.StringIO()

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
            Attach_Data.append(json.loads(i[0])['test_data'])
        except:
            Attach_Data.append(json.loads(i[0]))

    for n in range(len(Attach_Data)):
        for i in Attach_Data[n]:
            writer.writerow({'Test ID': TestIDs[n][0], 'Module': i[0], 'Bit Errors': i[1]})

    csv_file.seek(0)

    return csv_file

def get_i2c():
    csv_file = io.StringIO()

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
            Attach_Data.append(json.loads(i[0])['test_data'])
        except:
            Attach_Data.append(json.loads(i[0]))

    for n in range(len(Attach_Data)):
        keys = Attach_Data[n].keys()
        for k in keys:
            keys_2 = Attach_Data[n][k].keys()
            for v in keys_2:
                writer.writerow({'Test ID': TestIDs[n][0], 'Connector': k, 'Channel': v, 'Bit Errors': Attach_Data[n][k][v]})

    csv_file.seek(0)

    return csv_file

def get_gpio_functionality():
    csv_file = io.StringIO()

    header = ['Test ID', 'Pin', 'Read', 'Write']
    writer = csv.DictWriter(csv_file, fieldnames=header)
    writer.writeheader()

    cur.execute('select test_type from Test_Type where name="GPIO functionality"')
    type_id = cur.fetchall()[0][0]

    cur.execute('select attach from Attachments where test_id=282')
    fetch = cur.fetchall()[0][0]
    chips = json.loads(fetch)['walked_read'][0][3].keys()

    cur.execute('select test_id from Test where test_type_id={}'.format(type_id))
    TestIDs = cur.fetchall()

    query = 'select attach from Attachments where '
    for i in TestIDs:
        query += 'test_id={}'.format(i[0])
        if i is not TestIDs[-1]:
            query += ' or '
    cur.execute(query)
    Attach = cur.fetchall()

    for i in range(len(Attach)):
        try:
            try:
                data = json.loads(Attach[i][0])['test_data']
            except:
                data = json.loads(Attach[i][0])

            try:
                read_data = data['walked_read']
                read_keys = []
                for d in read_data:
                    read_keys.append(d[0])

                write_data = data['walked_write']
                write_keys = []
                for d in write_data:
                    write_keys.append(d[0])
                
                for c in chips:
                    if c in read_keys and c in write_keys:
                        writer.writerow({'Test ID': TestIDs[i][0], 'Pin': c, 'Read': 0, 'Write': 0})
                    elif c in read_keys and c not in write_keys:
                        writer.writerow({'Test ID': TestIDs[i][0], 'Pin': c, 'Read': 0, 'Write': 1})
                    elif c in write_keys and c not in read_keys:
                        writer.writerow({'Test ID': TestIDs[i][0], 'Pin': c, 'Read': 1, 'Write': 0})
                    else:
                        writer.writerow({'Test ID': TestIDs[i][0], 'Pin': c, 'Read': 1, 'Write': 1})
            except IndexError:
                for c in chips:
                        writer.writerow({'Test ID': TestIDs[i][0], 'Pin': c, 'Read': 1, 'Write': 1})
            
            
        except json.decoder.JSONDecodeError:
            pass

    csv_file.seek(0)

    return csv_file

def get_current_draw():
    csv_file = io.StringIO()

    header = ['Test ID', '1.5V Current', '10V Current']
    writer = csv.DictWriter(csv_file, fieldnames=header)
    writer.writeheader()

    cur.execute('select test_type from Test_Type where name="Current Draw"')
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
            Attach_Data.append(json.loads(i[0])['test_data'])
        except:
            Attach_Data.append(json.loads(i[0]))

    for n in range(len(Attach_Data)):
        writer.writerow({'Test ID': TestIDs[n][0], '1.5V Current': Attach_Data[n]['Current_1V5'], '10V Current': Attach_Data[n]['Current_10V']})

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
        try:
            type_id = cur.fetchall()[0][0]
        except:
            continue

        cur.execute('select test_type_id from Type_test_stitch where type_id=%s' % type_id)
        for t in cur.fetchall():
            cur.execute('select name from Test_Type where test_type=%s' % t[0])
            name = cur.fetchall()[0][0]

            cur.execute('select day,successful from Test where board_id=%s and test_type_id=%s order by day desc' % (board[3], t[0]))
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
        
        cur.execute('select type_id from Board_type where type_sn="%s"' % type_sn)
        type_id = cur.fetchall()[0][0]
        cur.execute('select test_type_id from Type_test_stitch where type_id=%s' % type_id)
        temp = cur.fetchall()
        stitch_types = []
        for test in temp:
            stitch_types.append(test[0])

        tests_needed[b[0]] = len(stitch_types)

    return tests_needed
