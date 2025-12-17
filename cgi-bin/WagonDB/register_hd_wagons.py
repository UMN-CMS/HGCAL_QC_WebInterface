#!/usr/bin/python3

import sys
import json 
import csv
import logging
import argparse
import components
from connect import connect

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Constants
LOCATION = "UMN"
INSTITUTION = "UMN"

MANU_RENAMES = { "Poly" : "PolyElectronics" }


# Helper Functions
def filter_boards(cur) -> list:
    """Fetch and filter board IDs that start with '320WH'."""
    try:
        cur.execute('SELECT full_id FROM Board')
        return [board[0] for board in cur.fetchall() if board[0].startswith('320WH')]
    except Exception as e:
        logger.error(f"Error fetching board IDs: {e}")
        return []

def check_if_registered(cur, barcode):
    """Check if board is already registered."""
    try:
        cur.execute('SELECT board_id FROM Board WHERE full_id = %s', (barcode,))
        board_id_result = cur.fetchall()
        board_id = board_id_result[0][0]

        cur.execute(
            'SELECT test_id FROM Test WHERE test_type_id = 7 AND board_id = %s '
            'ORDER BY day DESC, test_id DESC',
            (board_id,)
        )
        test_id_result = cur.fetchall()
        return test_id_result
    except Exception as e:
        logger.error(f"Error checking if board is registered for barcode {barcode}: {e}")
        return None

def get_typecode(cur, barcode):
    """Function to make a typcode (e.g WH-30A1)."""
    try:
        cur.execute('SELECT type_id FROM Board WHERE full_id = %s', (barcode,))
        type_id_result = cur.fetchone()
        if not type_id_result:
            logger.warning(f"No type ID found for barcode {barcode}")
            return None
        type_id = type_id_result[0]

        # Insert a hyphen after the first two characters
        if len(type_id) > 2:
            formatted_type_id = type_id[:2] + '-' + type_id[2:]
        else:
            logger.warning(f"Type ID '{type_id}' is too short to format")
            return None
        return formatted_type_id
    except Exception as e:
        logger.error(f"Error getting formatted type ID for barcode {barcode}: {e}")
        return None

def get_manufacturer(cur, barcode):
    try:
        # Fetch the manufacturer_id associated with the barcode
        cur.execute('SELECT manufacturer_id FROM Board WHERE full_id = %s', (barcode,))
        manufacturer_id_result = cur.fetchone()
        if not manufacturer_id_result:
            logger.warning(f"No manufacturer ID found for barcode {barcode}")
            return None
        manufacturer_id = manufacturer_id_result[0]

        # Fetch the name from the Manufacturers table
        cur.execute('SELECT name FROM Manufacturers WHERE manufacturer_id = %s', (manufacturer_id,))
        name_result = cur.fetchone()
        if not name_result:
            logger.warning(f"No manufacturer name found for manufacturer ID {manufacturer_id}")
            return None
        name = name_result[0]

        # Split the name by hyphen and return the second word
        name_parts = name.split('-')
        if len(name_parts) < 2:
            logger.warning(f"Manufacturer name '{name}' does not contain a hyphen")
            return None
        name_asm = name_parts[1].strip()
        if name_asm in MANU_RENAMES:
            name_asm = MANU_RENAMES[name_asm]
        return name_asm
    except Exception as e:
        logger.error(f"Error getting manufacturer for barcode {barcode}: {e}")
        return None


def get_name(barcode):
    """Generate a name label for the barcode."""
    return f"HD Wagon {barcode}"

BATCH_BOARD_DATES = {
    "WH-30A0:2" : "2024-08-09",
    "WH-31A0:1" : "2024-12-02",
    "WH-30B0:1" : "2025-01-20",
    "WH-20A0:1" : "2025-01-27", "WH-21A0:1" : "2025-01-27",
    "WH-30BT:1" : "2025-10-27", "WH-30BD:1" : "2025-10-27",
    "WH-30DT:1" : "2025-10-27", "WH-30DD:1" : "2025-10-27",
}

def get_date(typecode, batch):
    """Determine the production date based on typcode and batch."""
    fullcode="%s:%s"%(typecode,batch)
    if fullcode in BATCH_BOARD_DATES:
        return BATCH_BOARD_DATES[fullcode]
    else:
        return "UNKNOWN"

def get_batch(cur, barcode):
    """Get the full SN of the barcode, parse it to determine the board batch."""
    try:
        cur.execute('SELECT sn FROM Board WHERE full_id = %s', (barcode,))
        sn_result = cur.fetchone()
        if not sn_result:
            logger.warning(f"No serial number (sn) found for barcode {barcode}")
            return None
        sn = sn_result[0]

        # For preseries, return the second character of the sn, which is the batch character.        
        if len(sn) >= 3:
            if (barcode[3]=='0'):
                return sn[1]
            else:
                return sn[2]
        else:
            logger.warning(f"Serial number '{sn}' is too short to extract the second character")
            return None
    except Exception as e:
        logger.error(f"Error getting second character from serial number for barcode {barcode}: {e}")
        return None

def get_bare_board(ctx, cur, barcode):
    """Determine what kind of ECON is required and allocate out of the components tables"""
    retval = []
    used = components.get_used_for(cur, barcode)
    if used[0]!=200:
        logger.error(f"Problem in the used_for : {used[0]}")
        return []
    used=used[1]

    barecode="WH-%s1"%(barcode[3+2:3+2+3])
    if barecode in used:
        return (barecode,used[barecode][0])
    bbid=components.get_unused_stock(cur,barecode)
    if bbid[0]==200 and len(bbid[1])>0:
        components.mark_used(ctx,cur,bbid[1][0],barcode)
        return (barecode,bbid[1][0])
    else:
        logger.error(f,"No bare board available for {barecode}")
        return ("","")

def get_econ(ctx, cur, used, econ_tc, wagon_bc):
    if (econ_tc in used) and (len(used[econ_tc])>0):
        econ_bc = used[econ_tc][0]
        used[econ_tc]=used[econ_tc][1:]
        return econ_bc
    else:
        stock = components.get_unused_stock(cur,econ_tc)
        if stock[0]==200 and len(stock[1])>0:
            components.mark_used(ctx, cur, stock[1][0], wagon_bc)
            return stock[1][0]
        else:
            logger.error(f,"No {econ_tc} available for {wagon_bc}")
            return None

def get_econs(ctx, cur, barcode):
    """Determine what kind of ECON is required and allocate out of the components tables"""
    print(barcode)
    retval = []
    used = components.get_used_for(cur, barcode)
    if used[0]!=200:
        logger.error(f"Problem in the used_for : {used[0]}")
        return []
    used=used[1]
    nmodules=int(barcode[3+2+0])+int(barcode[3+2+1])
    for nmod in range(1,nmodules+1):
        econd_code = "ECON-D-"+barcode[3+2+4+int((nmod-1)/2)]
        econt_code = "ECON-T"
        # go
        retval.append("IC-ECD")
        retval.append(get_econ(ctx, cur, used, econd_code, barcode))
        if barcode[3+2+3]=='T':
            retval.append("IC-ECT")
            retval.append(get_econ(ctx, cur, used, econt_code, barcode))
        else:
            retval.append("")
            retval.append("")
    for nmod in range(nmodules,4):
        retval.append("")
        retval.append("")
        retval.append("")
        retval.append("")
    return retval
    
def get_description(barcode,batch):
    """Check if the batch character is a number or a letter to assign a comment field."""
    return "Pre-series" if barcode[3+3+2]=='0' else "Pre-production" if batch=="1" else "Production"
 
def run(csv_file):
    """Main execution function."""
    try:
        db = connect(1)
        cur = db.cursor()
        ofile = None

        all_hd_wagons = filter_boards(cur)

        if csv_file is None:
            writer = csv.writer(sys.stdout)
        else:
            ofile = open(csv_file, mode='w', newline='')
            writer = csv.writer(ofile)

        # Write the header row
        necons=4*2 
        header_row=[
            "LABEL_TYPECODE", "SERIAL_NUMBER", "BARCODE", "LOCATION",
            "INSTITUTION", "MANUFACTURER", "NAME_LABEL", "PRODUCTION_DATE",
	    "BATCH_NUMBER", "COMMENT_DESCRIPTION",
            "MADE-FROM-TYPECODE[0]", "MADE-FROM-SN[0]"  # For the bare board
            ]
        for i in range(1,necons+1):
            header_row.append("MADE-FROM-TYPECODE[%d]"%i)
            header_row.append("MADE-FROM-SN[%d]"%i)
        writer.writerow(header_row)

        success = 0
        
        for barcode in all_hd_wagons:

            # for now, ignore preseries
            if barcode[3+2+3]=='0':
                logger.info(f"Skipping preseries {barcode}")
                continue
            
            if check_if_registered(cur, barcode):
                logger.info(f"Skipping {barcode}, already registered")
                continue

            logger.info(f"Processing barcode: {barcode}")
            
            label_typecode = get_typecode(cur, barcode)
            manufacturer = get_manufacturer(cur, barcode)
            batch = get_batch(cur, barcode)
            name_label = get_name(barcode)
            production_date = get_date(label_typecode, batch)
            comment = get_description(barcode, batch)

            bareboard = get_bare_board(db, cur, barcode)
            econs = get_econs(db, cur, barcode)
            
            items = [
                label_typecode, barcode, barcode, LOCATION,
                INSTITUTION, manufacturer, name_label, production_date,
                batch, comment]
            items.extend(bareboard)
            items.extend(econs)
            
            writer.writerow(items)
    
            success += 1

        logger.info(f"CSV file for {success} HD wagons created successfully.")
        if ofile is not None:
            ofile.close()

    except Exception as e:
        logger.error(f"Critical error in run function: {e}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Register LD wagons by exporting data to a CSV file.")
    parser.add_argument("-o", "--output", type=str, default=None, help="Output CSV file name (e.g., output.csv)")
    args = parser.parse_args()

    if args.output is None:        
        print("Content-type: text/csv")
        print('Content-disposition: attachment; filename="hd_wagons_register.csv"\n')
    run(args.output)
