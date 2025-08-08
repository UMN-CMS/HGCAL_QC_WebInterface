from connect import connect
import numpy as np
import json
import csv
import datetime
import os
import io
import multiprocessing as mp
import time
import pickle
from collections import defaultdict

path = os.path.dirname(os.path.abspath(__file__))

db = connect(0)
cur = db.cursor(buffered=True)

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

    columns = ['Test Type ID', 'Name']
    writer = csv.writer(csv_file)
    writer.writerow(columns)

    cur.execute('select test_type,name from Test_Type')
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

    cur.execute('select board_id from Board')
    boards_list = cur.fetchall()
    Tests = []
    for b in boards_list:
        cur.execute('select Test.test_id, Attachments.attach from Test left join Attachments on Test.test_id=Attachments.test_id where Test.board_id=%s and Test.test_type_id=%s order by Test.day desc, Test.test_id desc' % (b[0],type_id))
        test_id = cur.fetchone()
        if test_id:
            Tests.append(test_id)

    Attach_Data = []
    for i in Tests:
        try:
            Attach_Data.append(json.loads(i[1])['test_data'])
        except KeyError:
            Attach_Data.append(json.loads(i[1]))

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
                if j == 'THERM':
                    continue
                writer_1.writerow({'Test ID': Tests[n][0], 'E Link': j, 'Resistance': Resistance})

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
                writer_2.writerow({'Test ID': Tests[n][0], 'ADC': v, 'Voltage': Voltage})

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
                writer_3.writerow({'Test ID': Tests[n][0], 'Chip': v, 'Temperature': Temp})

            for i in adc_keys:
                try:
                    slope = Attach_Data[n]['walk_engine_read_adc'][i][1]['slope']
                    intercept = Attach_Data[n]['walk_engine_read_adc'][i][1]['intercept']
                    r2 = Attach_Data[n]['walk_engine_read_adc'][i][1]['rsquared']
                except KeyError:
                    slope = Attach_Data[n]['walk_engine_read_adc'][i]['slope']
                    intercept = Attach_Data[n]['walk_engine_read_adc'][i]['intercept']
                    r2 = Attach_Data[n]['walk_engine_read_adc'][i]['rsquared']

                writer_4.writerow({'Test ID': Tests[n][0], 'ADC': i, 'slope': slope, 'intercept': intercept, 'rsquared': r2})
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

    cur.execute('select board_id from Board')
    boards_list = cur.fetchall()
    Tests = []
    for b in boards_list:
        cur.execute('select Test.test_id, Attachments.attach from Test left join Attachments on Test.test_id=Attachments.test_id where Test.board_id=%s and Test.test_type_id=%s order by Test.day desc, Test.test_id desc' % (b[0],type_id))
        test_id = cur.fetchone()
        if test_id:
            Tests.append(test_id)

    Attach_Data = []
    for i in Tests:
        try:
            Attach_Data.append(json.loads(i[1])['test_data'])
        except KeyError:
            Attach_Data.append(json.loads(i[1]))

    writer.writeheader()
    for n in range(len(Attach_Data)):
        try:
            writer.writerow({'Test ID': Tests[n][0],
                            'Module 1': Attach_Data[n][0],
                            'Module 2': Attach_Data[n][1],
                            'Module 3': Attach_Data[n][2],
                            'Module 4': Attach_Data[n][3],
                            'Module 5': Attach_Data[n][4],
                            'Module 6': Attach_Data[n][5],
                            'Module 7': Attach_Data[n][6],})
        except:
            continue

    csv_file.seek(0)

    return csv_file

def get_xpwr():
    csv_file = io.StringIO()

    header = ['Test ID', 'Voltage']
    writer = csv.DictWriter(csv_file, fieldnames=header)
    writer.writeheader()

    cur.execute('select test_type from Test_Type where name="X_PWR"')
    type_id = cur.fetchall()[0][0]

    cur.execute('select board_id from Board')
    boards_list = cur.fetchall()
    Tests = []
    for b in boards_list:
        cur.execute('select Test.test_id, Attachments.attach from Test left join Attachments on Test.test_id=Attachments.test_id where Test.board_id=%s and Test.test_type_id=%s order by Test.day desc, Test.test_id desc' % (b[0],type_id))
        test_id = cur.fetchone()
        if test_id:
            Tests.append(test_id)

    Attach_Data = []
    for i in Tests:
        try:
            Attach_Data.append(json.loads(i[1])['test_data'])
        except KeyError:
            Attach_Data.append(json.loads(i[1]))

    for n in range(len(Attach_Data)):
        writer.writerow({'Test ID': Tests[n][0], 'Voltage': Attach_Data[n]['voltage']})

    csv_file.seek(0)

    return csv_file

def get_elink_quality():
    header = ['Test ID', 'Phase', 'Bit Errors']
    writers = {}
    csvs = {}
    for i in range(42):
        csvs[i] = io.StringIO()

        writers[i] = csv.DictWriter(csvs[i], fieldnames=header)
        writers[i].writeheader()

    cur.execute('select test_type from Test_Type where name="Elink Quality"')
    type_id = cur.fetchall()[0][0]

    cur.execute('select board_id from Board')
    boards_list = cur.fetchall()
    Tests = []
    for b in boards_list:
        cur.execute('select Test.test_id, Attachments.attach from Test left join Attachments on Test.test_id=Attachments.test_id where Test.board_id=%s and Test.test_type_id=%s order by Test.day desc, Test.test_id desc' % (b[0],type_id))
        test_id = cur.fetchone()
        if test_id:
            Tests.append(test_id)

    Attach_Data = []
    for i in Tests:
        try:
            Attach_Data.append(json.loads(i[1])['test_data'])
        except KeyError:
            Attach_Data.append(json.loads(i[1]))

    for n in range(len(Attach_Data)):
        keys = Attach_Data[n].keys()
        for k in keys:
            for v in Attach_Data[n][k]:
                try:
                    writers[v[0]].writerow({'Test ID': Tests[n][0], 'Phase': k, 'Bit Errors': v[1]})
                except KeyError:
                    continue

    for i in range(42):
        csvs[i].seek(0)

    return csvs

def get_fast_command():
    csv_file = io.StringIO()

    header = ['Test ID', 'Phase', 'Channel', 'Bit Errors']
    writer = csv.DictWriter(csv_file, fieldnames=header)
    writer.writeheader()

    cur.execute('select test_type from Test_Type where name="Fast Command Quality"')
    type_id = cur.fetchall()[0][0]

    cur.execute('select board_id from Board')
    boards_list = cur.fetchall()
    Tests = []
    for b in boards_list:
        cur.execute('select Test.test_id, Attachments.attach from Test left join Attachments on Test.test_id=Attachments.test_id where Test.board_id=%s and Test.test_type_id=%s order by Test.day desc, Test.test_id desc' % (b[0],type_id))
        test_id = cur.fetchone()
        if test_id:
            Tests.append(test_id)

    Attach_Data = []
    for i in Tests:
        try:
            Attach_Data.append(json.loads(i[1])['test_data'])
        except KeyError:
            Attach_Data.append(json.loads(i[1]))

    for n in range(len(Attach_Data)):
        try:
            keys = Attach_Data[n].keys()
            for k in keys:
                for idx,v in enumerate(Attach_Data[n][k]):
                    writer.writerow({'Test ID': Tests[n][0], 'Phase': k, 'Channel': idx, 'Bit Errors': v})
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

    cur.execute('select board_id from Board')
    boards_list = cur.fetchall()
    Tests = []
    for b in boards_list:
        cur.execute('select Test.test_id, Attachments.attach from Test left join Attachments on Test.test_id=Attachments.test_id where Test.board_id=%s and Test.test_type_id=%s order by Test.day desc, Test.test_id desc' % (b[0],type_id))
        test_id = cur.fetchone()
        if test_id:
            Tests.append(test_id)

    Attach_Data = []
    for i in Tests:
        try:
            Attach_Data.append(json.loads(i[1])['test_data'])
        except KeyError:
            Attach_Data.append(json.loads(i[1]))

    for n in range(len(Attach_Data)):
        for i in Attach_Data[n]:
            try:
                writer.writerow({'Test ID': Tests[n][0], 'Module': i[0], 'Bit Errors': i[1]})
            except:
                continue

    csv_file.seek(0)

    return csv_file

def get_i2c():
    csv_file = io.StringIO()

    header = ['Test ID', 'Connector', 'Channel', 'Bit Errors']
    writer = csv.DictWriter(csv_file, fieldnames=header)
    writer.writeheader()

    cur.execute('select test_type from Test_Type where name="I2C"')
    type_id = cur.fetchall()[0][0]

    cur.execute('select board_id from Board')
    boards_list = cur.fetchall()
    Tests = []
    for b in boards_list:
        cur.execute('select Test.test_id, Attachments.attach from Test left join Attachments on Test.test_id=Attachments.test_id where Test.board_id=%s and Test.test_type_id=%s order by Test.day desc, Test.test_id desc' % (b[0],type_id))
        test_id = cur.fetchone()
        if test_id:
            Tests.append(test_id)

    Attach_Data = []
    for i in Tests:
        try:
            Attach_Data.append(json.loads(i[1])['test_data'])
        except KeyError:
            Attach_Data.append(json.loads(i[1]))

    for n in range(len(Attach_Data)):
        try:
            keys = Attach_Data[n].keys()
            for k in keys:
                keys_2 = Attach_Data[n][k].keys()
                for v in keys_2:
                    writer.writerow({'Test ID': Tests[n][0], 'Connector': k, 'Channel': v, 'Bit Errors': Attach_Data[n][k][v]})
        except:
            continue

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

    cur.execute('select board_id from Board')
    boards_list = cur.fetchall()
    Tests = []
    for b in boards_list:
        cur.execute('select Test.test_id, Attachments.attach from Test left join Attachments on Test.test_id=Attachments.test_id where Test.board_id=%s and Test.test_type_id=%s order by Test.day desc, Test.test_id desc' % (b[0],type_id))
        test_id = cur.fetchone()
        if test_id:
            Tests.append(test_id)

    Attach_Data = []
    for i in Tests:
        try:
            try:
                Attach_Data.append(json.loads(i[1])['test_data'])
            except KeyError:
                Attach_Data.append(json.loads(i[1]))

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
                        writer.writerow({'Test ID': Tests[i][0], 'Pin': c, 'Read': 0, 'Write': 0})
                    elif c in read_keys and c not in write_keys:
                        writer.writerow({'Test ID': Tests[i][0], 'Pin': c, 'Read': 0, 'Write': 1})
                    elif c in write_keys and c not in read_keys:
                        writer.writerow({'Test ID': Tests[i][0], 'Pin': c, 'Read': 1, 'Write': 0})
                    else:
                        writer.writerow({'Test ID': Tests[i][0], 'Pin': c, 'Read': 1, 'Write': 1})
            except IndexError:
                for c in chips:
                        writer.writerow({'Test ID': Tests[i][0], 'Pin': c, 'Read': 1, 'Write': 1})
            
            
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

    cur.execute('select board_id from Board')
    boards_list = cur.fetchall()
    Tests = []
    for b in boards_list:
        cur.execute('select Test.test_id, Attachments.attach from Test left join Attachments on Test.test_id=Attachments.test_id where Test.board_id=%s and Test.test_type_id=%s order by Test.day desc, Test.test_id desc' % (b[0],type_id))
        test_id = cur.fetchone()
        if test_id:
            Tests.append(test_id)

    Attach_Data = []
    for i in Tests:
        try:
            Attach_Data.append(json.loads(i[1])['test_data'])
        except KeyError:
            Attach_Data.append(json.loads(i[1]))

    for n in range(len(Attach_Data)):
        try:
            writer.writerow({'Test ID': Tests[n][0], '1.5V Current': Attach_Data[n]['Current_1V5'], '10V Current': Attach_Data[n]['Current_10V']})
        except KeyError:
            continue

    csv_file.seek(0)

    return csv_file

def get_crossover_link():
    csv_file = io.StringIO()

    header = ['Test ID', 'Crossover Link', 'Phase', 'Bit Errors']
    writer = csv.DictWriter(csv_file, fieldnames=header)
    writer.writeheader()

    cur.execute('select test_type from Test_Type where name="Crossover link quality"')
    type_id = cur.fetchall()[0][0]

    cur.execute('select board_id from Board')
    boards_list = cur.fetchall()
    Tests = []
    for b in boards_list:
        cur.execute('select Test.test_id, Attachments.attach from Test left join Attachments on Test.test_id=Attachments.test_id where Test.board_id=%s and Test.test_type_id=%s order by Test.day desc, Test.test_id desc' % (b[0],type_id))
        test_id = cur.fetchone()
        if test_id:
            Tests.append(test_id)

    Attach_Data = []
    for i in Tests:
        try:
            Attach_Data.append(json.loads(i[1])['test_data'])
        except KeyError:
            Attach_Data.append(json.loads(i[1]))

    phases = [0, 50, 100, 150, 200, 250, 300, 350]

    for n in range(len(Attach_Data)):
        keys = Attach_Data[n].keys()
        for k in keys:
            for idx,v in enumerate(Attach_Data[n][k]):
                try:
                    if k == '3':
                        continue
                    writer.writerow({'Test ID': Tests[n][0], 'Crossover Link': k, 'Phase': phases[idx], 'Bit Errors': v})
                except (KeyError, TypeError):
                    continue

    csv_file.seek(0)

    return csv_file

def get_eye_opening():
    csv_file = io.StringIO()

    header = ['Test ID', 'lpGBT', 'Area', 'Height', 'Width']
    writer = csv.DictWriter(csv_file, fieldnames=header)
    writer.writeheader()

    cur.execute('select test_type from Test_Type where name="Eye Opening"')
    type_id = cur.fetchall()[0][0]

    cur.execute('select board_id from Board')
    boards_list = cur.fetchall()
    Tests = []
    for b in boards_list:
        cur.execute('select Test.test_id, Attachments.attach from Test left join Attachments on Test.test_id=Attachments.test_id where Test.board_id=%s and Test.test_type_id=%s order by Test.day desc, Test.test_id desc' % (b[0],type_id))
        test_id = cur.fetchone()
        if test_id:
            Tests.append(test_id)

    Attach_Data = []
    for i in Tests:
        try:
            Attach_Data.append(json.loads(i[1])['test_data'])
        except KeyError:
            Attach_Data.append(json.loads(i[1]))

    for n in range(len(Attach_Data)):
        try:
            data = Attach_Data[n]['DAQ']
            writer.writerow({'Test ID': Tests[n][0], 'lpGBT': 'DAQ', 'Area': data['area'], 'Height': data['max_width_y'], 'Width': data['max_width']})

        except KeyError:
            try:
                data1 = Attach_Data[n]['DAQ1']
                data2 = Attach_Data[n]['DAQ2']
                writer.writerow({'Test ID': Tests[n][0], 'lpGBT': 'DAQ1', 'Area': data1['area'], 'Height': data1['max_width_y'], 'Width': data1['max_width']})
                writer.writerow({'Test ID': Tests[n][0], 'lpGBT': 'DAQ2', 'Area': data2['area'], 'Height': data2['max_width_y'], 'Width': data2['max_width']})
            except KeyError:
                continue

    csv_file.seek(0)

    return csv_file

def get_check_out():
    csv_file = io.StringIO()

    columns = ['Board ID', 'Person ID', 'Shipping Location', 'Time']
    writer = csv.writer(csv_file)
    writer.writerow(columns)

    cur.execute('select CO.board_id, CO.person_id, B.location, CO.checkout_date from Check_Out CO join Board B on CO.board_id=B.board_id')
    check_out = cur.fetchall()
    for c in check_out:
        loc = c[2].split()[-1]
        writer.writerow((c[0], c[1], loc, c[3]))

    csv_file.seek(0)

    return csv_file

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
            elif (
                outcomes.get('Thermal Cycle') is False and 
                sum(v for k,v in outcomes.items() if k != 'Thermal Cycle' and k != 'Registered') == num_tests_req - 2
            ):
                status = 'Passed QC Minus Thermal Cycle'
            elif (num_tests_passed == num_tests_req - 1 and not outcomes.get('Registered', False)):
                status = 'Passed QC, Awaiting Registration'
            else:
                status = 'Awaiting Testing'

            row.append(status)
            writer.writerow(row)

        csv_file.seek(0)
        csvs_to_return.append(csv_file)

    return csvs_to_return


def get_status_over_time():

    cur.execute('''
        SELECT B.full_id, B.type_id, B.board_id, BT.name as nickname, BT.type_id as bt_type_id, B.location, C.checkin_date
        FROM Board B
        JOIN Board_type BT ON B.type_id=BT.type_sn
        JOIN Check_In C ON B.board_id=C.board_id
    ''')
    board_rows = cur.fetchall()

    cur.execute('''
        SELECT T.board_id, T.test_type_id, T.successful, T.day
        FROM Test T
        ORDER BY T.day
    ''')
    test_rows = cur.fetchall()

    cur.execute('SELECT board_id, checkout_date FROM Check_Out')
    checkout_rows = cur.fetchall()

    cur.execute('''
        SELECT TTS.type_id, TT.test_type, TT.name
        FROM Type_test_stitch TTS
        JOIN Test_Type TT ON TTS.test_type_id = TT.test_type
    ''')
    stitch_type_map = defaultdict(list)
    for type_id, test_type_id, test_name in cur.fetchall():
        stitch_type_map[type_id].append((test_type_id, test_name))

    board_info = {}
    all_dates = set()
    for full_id, type_sn, board_id, nickname, bt_type_id, location, checkin_date in board_rows:
        board_info[board_id] = {
            'full_id': full_id,
            'type_sn': type_sn,
            'nickname': nickname,
            'bt_type_id': bt_type_id,
            'location': location,
            'checkin_date': checkin_date,
        }
        all_dates.add(checkin_date.date())

    checkout_dates = {}
    for board_id, checkout_date in checkout_rows:
        checkout_dates[board_id] = checkout_date
        all_dates.add(checkout_date.date())

    test_history = defaultdict(lambda: defaultdict(list))
    for board_id, test_type_id, successful, timestamp in test_rows:
        test_history[board_id][test_type_id].append((timestamp, successful))
        all_dates.add(timestamp.date())

    all_dates = sorted(all_dates)
    status_over_time = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(int))))

    for date in all_dates:
        for board_id, info in board_info.items():
            if info['checkin_date'].date() > date:
                continue  # not yet checked in

            full_id = info['full_id']
            type_sn = info['type_sn']
            major_type = type_sn[:2]
            subtype = type_sn
            bt_type_id = info['bt_type_id']
            stitch_types = stitch_type_map.get(bt_type_id, [])

            # Get most recent test outcomes before or on this date
            outcomes = {}
            failed = {}
            for test_type_id, test_name in stitch_types:
                tests = test_history[board_id][test_type_id]
                latest = None
                for ts, success in tests:
                    if ts.date() <= date:
                        latest = success
                    else:
                        break
                if latest is not None:
                    outcomes[test_name] = latest == 1
                    failed[test_name] = latest == 0
                else:
                    outcomes[test_name] = None
                    failed[test_name] = None

            num_tests_passed = sum(1 for v in outcomes.values() if v is True)
            num_tests_req = len(stitch_types)
            num_tests_failed = sum(1 for v in failed.values() if v is True)

            # Determine status
            if checkout_dates.get(board_id, None) and checkout_dates[board_id].date() <= date:
                status = 'Shipped'
            elif num_tests_failed:
                status = 'Failed QC'
            elif num_tests_passed == num_tests_req:
                status = 'Ready for Shipping'
            elif (num_tests_passed == num_tests_req - 1 and not outcomes.get('Registered', False)):
                status = 'Passed QC, Awaiting Registration'
            else:
                status = 'Awaiting Testing'

            status_over_time[date][major_type][subtype][status] += 1
            status_over_time[date][major_type][subtype]['Total'] += 1

    return status_over_time


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

    for day in status.keys():
        day1 = datetime.datetime.strptime(day, '%Y-%m-%d') + datetime.timedelta(days=1)
        day1 = datetime.datetime.combine(day1, datetime.time.min).strftime('%Y-%m-%d %H:%M:%S')
        cur.execute('select board_id from Check_In where checkin_date < "%s"' % day1)
        boards = cur.fetchall()

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
                    s = 'Failed'
                else:
                    if num == total:
                        s = 'Passed'
                    else:
                        if (num == total-1 and outcomes[24] == False) or (num == total-2 and outcomes[24] == False and outcomes[26] == False):
                            s = 'Thermal'
                        elif (num == total-1 and outcomes[26] == False):
                            s = 'Not Registered'
                        else:
                            s = 'Awaiting'

            try:
                status[day][sn[3:5]][sn[3:9]][s] += 1
            except:
                status[day][sn[3:5]][sn[3:9]][s] = 1
            try:
                status[day][sn[3:5]][sn[3:9]]['Total'] += 1
            except:
                status[day][sn[3:5]][sn[3:9]]['Total'] = 1

    with open('/home/webapp/pro/HGCAL_QC_WebInterface/cgi-bin/EngineDB/cache/store_board_status.pkl', "wb") as f:
        pickle.dump(status, f)


def get_board_statuses():

    with open('/home/webapp/pro/HGCAL_QC_WebInterface/cgi-bin/EngineDB/cache/store_board_status.pkl', "rb") as f:
        status = pickle.load(f)

    return status

def write_datafiles():
    write_board_statuses_file()
