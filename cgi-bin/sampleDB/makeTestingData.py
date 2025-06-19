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
