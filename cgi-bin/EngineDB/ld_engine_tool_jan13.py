#!/usr/bin/python3

import json 
import csv
import logging
from connect import connect

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Constants
PRODUCTION_DATE = "2024-11-22"
LOCATION = "UMN"
INSTITUTION = "UMN"
MANUFACTURER = "Caltronics-Minnesota"
COMMENT_DESCRIPTION = "Preproduction"
CSV_FILE = "ld_eng_250113.csv"

# Helper Functions
def filter_boards(cur) -> list:
    """
    Fetch boards from the database and filter out excluded boards,
    keeping only those starting with '320EL10'.
    """
    try:
        # Fetch boards from the database
        cur.execute('SELECT full_id FROM Board')
        board_list = cur.fetchall()

        # Filter out excluded boards
        filtered_boards = [
            board[0] for board in board_list
            if board[0].startswith('320EL10')
        ]
        return filtered_boards
    except Exception as e:
        logger.error(f"Error in filter_boards: {e}")
        return []

def get_lpgbt_ids(cur, barcode):
    """
    Retrieve LPGBT IDs for a given barcode.
    
    Parameters:
        cur (cursor): Database cursor to execute queries.
        barcode (str): The board's barcode to query for LPGBT IDs.
    
    Returns:
        list: A list of LPGBT IDs if available, or None if not found.
    """
    try:
        # Fetch the board ID associated with the barcode
        cur.execute('SELECT board_id FROM Board WHERE full_id = %s', (barcode,))
        board_id_result = cur.fetchall()
        if not board_id_result:
            return None
        
        board_id = board_id_result[0][0]

        # Fetch the most recent test ID for LPGBT
        cur.execute(
            'SELECT test_id FROM Test WHERE test_type_id = 22 AND board_id = %s '
            'ORDER BY day DESC, test_id DESC',
            (board_id,)
        )
        test_id_result = cur.fetchall()
        if not test_id_result:
            return None
        
        test_id = test_id_result[0][0]

        # Fetch the attached LPGBT IDs
        cur.execute('SELECT attach FROM Attachments WHERE test_id = %s', (test_id,))
        lpgbt_ids_result = cur.fetchall()
        if not lpgbt_ids_result:
            return None
        
        lpgbt_ids = lpgbt_ids_result[0][0]
        return extract_ids(lpgbt_ids)
    except Exception as e:
        logger.error(f"Error retrieving LPGBT IDs for barcode {barcode}: {e}")
        return None

def extract_ids(byte_data):
    json_str = byte_data.decode('utf-8')
    data_dict = json.loads(json_str)

    test_data = data_dict['test_data']

    if not test_data or all('id' not in value for value in test_data.values()):
        return None

    id_list = [f"{value['id']:08x}".upper() for key, value in test_data.items() if 'id' in value]

    return id_list

def check_if_registered(cur, barcode):
    try:
        # Fetch the board ID associated with the barcode
        cur.execute('SELECT board_id FROM Board WHERE full_id = %s', (barcode,))
        board_id_result = cur.fetchall()
        board_id = board_id_result[0][0]

        # Fetch the most recent test ID for LPGBT
        cur.execute(
            'SELECT test_id FROM Test WHERE test_type_id = 26 AND board_id = %s '
            'ORDER BY day DESC, test_id DESC',
            (board_id,)
        )
        test_id_result = cur.fetchall()
        return test_id_result
    except Exception as e:
        logger.error(f"Error checking if board is registered for barcode {barcode}: {e}")
        return None
     
def run():
    """Main execution function."""
    try:
        db = connect(1)
        cur = db.cursor()

        all_ld_engines = filter_boards(cur)

        print(all_ld_engines)

        with open(CSV_FILE, mode='w', newline='') as file:
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

            for barcode in all_ld_engines:
                print(barcode)
                label_typecode = f"{barcode[3:5]}-{barcode[5:8]}"
                serial_number = barcode
                name_label = f"LD Engine {barcode[7:8]} {barcode}"
                batch_number = f"{barcode[10:11]}"

                # Skip board if it is already registered
                is_registered = check_if_registered(cur, barcode)
                if is_registered:
                    continue

                 
                # Retrieve LPGBT IDs
                lpgbt_ids = get_lpgbt_ids(cur, barcode)
                # GET LPGBT IDs
                if lpgbt_ids is not None:
                    made_from_typecode0 = "IC-LPG"
                    made_from_sn0 = lpgbt_ids[0]
                    made_from_typecode1 = "IC-LPG"
                    made_from_sn1 = lpgbt_ids[1]
                    made_from_typecode2 = "IC-LPG"
                    made_from_sn2 = lpgbt_ids[2]
                else:
                    continue

                # Get LDO ID
                cur.execute('select LDO from Board where full_id="%s"' % barcode)
                LDO_result = cur.fetchall()
                ldo = LDO_result[0][0]
                if ldo:
#                    ldo = LDO_result[0][0]
                    made_from_typecode3 = "IC-LDH"
                    made_from_sn3 = ldo
                else:
                    continue

                print("registered", is_registered)
                print("lpgbt_ids", lpgbt_ids)
                print("LDO_result", LDO_result)
                # Get Bare Code
                bare_code = barcode[:barcode.find('0', barcode.find('0') + 1)] + 'B' + barcode[barcode.find('0', barcode.find('0') + 1) + 1:]
                made_from_typecode4 = f"{bare_code[3:5]}-{bare_code[5:8]}"
                made_from_sn4 = bare_code

                    # Write the row to the CSV
                writer.writerow([
                    label_typecode, serial_number, barcode, LOCATION,
                    INSTITUTION, MANUFACTURER, name_label, PRODUCTION_DATE,
                    batch_number, COMMENT_DESCRIPTION, made_from_typecode0,
                    made_from_sn0, made_from_typecode1, made_from_sn1,
                    made_from_typecode2, made_from_sn2, made_from_typecode3,
                    made_from_sn3, made_from_typecode4, made_from_sn4 
                ])

            print(f"CSV file '{CSV_FILE}' created successfully.")

    except Exception as e:
        logger.error(f"Error in run function: {e}")
if __name__ == '__main__':
    print("Content-type: text/html\n")
    run()
