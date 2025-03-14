#!/usr/bin/python3

import cgi, html
import cgitb; cgitb.enable()
import base
import home_page_list
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

    db = connect(0)
    cur = db.cursor()

    cur.execute('select full_id from Board')
    boards = cur.fetchall()
    hd_engines = filter_boards(boards)
#    print(hd_engines)

    csv_file = "barePCB_EH.csv"

    with open(csv_file, mode='w', newline='') as file:
        writer = csv.writer(file)

        # Write the header row
        writer.writerow([
            "LABEL_TYPECODE", "SERIAL_NUMBER", "BARCODE", "LOCATION", 
            "INSTITUTION", "MANUFACTURER", "NAME_LABEL", "PRODUCTION_DATE",
	    "BATCH_NUMBER"
        ])


        for barcode in hd_engines:
#            print(barcode)
            bare_barcode = barcode[:8] + "B" + barcode[9:]
#            print(bare_barcode)
            label_typecode = f"{bare_barcode[3:5]}-{bare_barcode[5:9]}"
#            print(label_typecode)

            cur.execute('select sn from Board where full_id="%s"' % barcode)
            sn_result = cur.fetchall()
            serial_number = sn_result[0][0]
#            print(serial_number)

            cur.execute('select manufacturer_id from Board where full_id="%s"' % barcode)
            man_id_result = cur.fetchall()
            man_id = man_id_result[0][0]
#            print(man_id)

            if man_id == 1:
                manufacturer = "AdvancedPCB APCT"
            elif man_id == None:
                manufacturer = "AdvancedPCB APCT" #Temp for the bug
#                manufacturer = "NULL"
            else:
                manufacturer = "Unknown"

            if "0QFB" in label_typecode:
                name_label = f"Bare HD Full Engine {bare_barcode}"
            elif "0QHB" in label_typecode:
                name_label = f"Bare HD Half Engine {bare_barcode}"

            production_date = '2024-06-18'
            batch_number = '1'
            location = "Minnesota"
            institution = "Minnesota"

            # Write the row to the CSV
            writer.writerow([
                label_typecode, serial_number, bare_barcode, location,
                institution, manufacturer, name_label, production_date,
		batch_number
            ])

    print(f"CSV file '{csv_file}' created successfully.")

def filter_boards(board_list):
    # Filter the list for boards starting with '320EH0Q'
    filtered_boards = [board[0] for board in board_list if board[0].startswith('320EH0Q')]
    return filtered_boards

def extract_ids(byte_data):
    json_str = byte_data.decode('utf-8')
    
    data_dict = json.loads(json_str)
    
    test_data = data_dict['test_data']
    
    id_dict = {f"{key}_id": hex(value['id']) for key, value in test_data.items()}
    
    return id_dict

def create_csv(serial_num, lpgbt_ids_dict):
    csv_file = "lpgbt_ids.csv"
    
    with open(csv_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["full_id", "DAQ1_id", "DAQ2_id", "TRIG1_id", "Trig2_id", "Trig3_id", "Trig4_id", "LDO_id"])

        csv_row = [
            serial_num,
            lpgbt_ids_dict.get('DAQ1_id', 'NULL'),
            lpgbt_ids_dict.get('DAQ2_id', 'NULL'),
            lpgbt_ids_dict.get('TRG1_id', 'NULL'),
            lpgbt_ids_dict.get('TRG2_id', 'NULL'),
            lpgbt_ids_dict.get('TRG3_id', 'NULL'),
            lpgbt_ids_dict.get('TRG4_id', 'NULL'),
            'NULL'  # Assuming LDO_id is not available
        ]
        writer.writerow(csv_row)

    print(f"CSV file '{csv_file}' created successfully.")

if __name__ == '__main__':
    print("Content-type: text/html\n")
#    parser = argparse.ArgumentParser(description="Process serial number to generate CSV.")
#    parser.add_argument('serial_num', type=str, help='Serial number of the board')

#    args = parser.parse_args()

    run()
