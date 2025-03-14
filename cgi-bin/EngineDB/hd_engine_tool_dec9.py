#!/usr/bin/python3

import cgi, html
import cgitb; cgitb.enable()
import base
#import home_page_list
#import module_functions
from connect import connect
import pandas as pd
import numpy as np
import json 
import csv
import argparse
 
def run():
#    base.header(title='Engine DB')
#    base.top(True)

    db = connect(1)
    cur = db.cursor()

    cur.execute('select full_id from Board')
    boards = cur.fetchall()
    ld_engines = filter_boards(boards)

    csv_file = "hd_eng_241210.csv"
 
    with open(csv_file, mode='w', newline='') as file:
        writer = csv.writer(file)

        # Write the header row
        writer.writerow([
            "LABEL_TYPECODE", "SERIAL_NUMBER", "BARCODE", "LOCATION",
            "INSTITUTION", "MANUFACTURER", "NAME_LABEL", "PRODUCTION_DATE",
	    "BATCH_NUMBER", "COMMENT_DESCRIPTION", "MADE-FROM-TYPECODE[0]", 
            "MADE-FROM-SN[0]", "MADE-FROM-TYPECODE[1]", "MADE-FROM-SN[1]",
            "MADE-FROM-TYPECODE[2]", "MADE-FROM-SN[2]", "MADE-FROM-TYPECODE[3]",
	    "MADE-FROM-SN[3]", "MADE-FROM-TYPECODE[4]", "MADE-FROM-SN[4]"
        ])

        for barcode in ld_engines:
            print(barcode)
            label_typecode = f"{barcode[3:5]}-{barcode[5:8]}"
            serial_number = barcode
            barcode = barcode
            location = "UMN"
            institution = "UMN"
            manufacturer = "Caltronics-Minnesota"
            name_label = f"HD Engine {barcode[7:8]} {barcode}"
            production_date = "2024-11-22"
            batch_number = f"{barcode[10:11]}"
            comment_description = "Preproduction"

            # GET LPGBT IDs
            cur.execute('select board_id from Board where full_id="%s"' % barcode)
            board_id_result = cur.fetchall()
            board_id = board_id_result[0][0]

            cur.execute('select test_id from Test where test_type_id=22 and board_id="%s"' % board_id) #lpgbt 
            test_id_result = cur.fetchall()
            if test_id_result: 
                test_id = test_id_result[0][0]
                cur.execute('Select attach from Attachments where test_id="%s"' % test_id)
                lpgbt_ids_result = cur.fetchall()
                if lpgbt_ids_result:
                    lpgbt_ids = lpgbt_ids_result[0][0]
                    print(lpgbt_ids)
                    lpgbt_ids = extract_ids(lpgbt_ids)
                    if lpgbt_ids is not None:
                        made_from_typecode0 = "IC-LPG"
                        made_from_sn0 = lpgbt_ids[0]
                        made_from_typecode1 = "IC-LPG"
                        made_from_sn1 = lpgbt_ids[1]
                        made_from_typecode2 = "IC-LPG"
                        made_from_sn2 = lpgbt_ids[2]

            		# Get LDO ID
                        cur.execute('select LDO from Board where full_id="%s"' % barcode)
                        LDO_result = cur.fetchall()
                        if LDO_result:
                            ldo = LDO_result[0][0]
                            made_from_typecode3 = "IC-LDH"
                            made_from_sn3 = ldo

                            # Get Bare Code
                            bare_code = barcode[:barcode.find('0', barcode.find('0') + 1)] + 'B' + barcode[barcode.find('0', barcode.find('0') + 1) + 1:]
                            made_from_typecode4 = f"{bare_code[3:5]}-{bare_code[5:8]}"
                            made_from_sn4 = bare_code

                            # Write the row to the CSV
                            writer.writerow([
                                label_typecode, serial_number, barcode, location,
                                institution, manufacturer, name_label, production_date,
                                batch_number, comment_description, made_from_typecode0,
                                made_from_sn0, made_from_typecode1, made_from_sn1,
                                made_from_typecode2, made_from_sn2, made_from_typecode3,
                                made_from_sn3, made_from_typecode4, made_from_sn4 
                            ])

        print(f"CSV file '{csv_file}' created successfully.")
#    base.bottom(True)

def filter_boards(board_list):
    # Filter the list for boards starting with '320EH0Q'
    filtered_boards = [board[0] for board in board_list if board[0].startswith('320EH0Q')]
    return filtered_boards

def extract_ids(byte_data):
    json_str = byte_data.decode('utf-8')
    data_dict = json.loads(json_str)
    
    test_data = data_dict['test_data']

    if not test_data or all('id' not in value for value in test_data.values()):
        return None

    id_list = [f"{value['id']:08x}".upper() for key, value in test_data.items() if 'id' in value]

    return id_list

if __name__ == '__main__':
    print("Content-type: text/html\n")
    run()
