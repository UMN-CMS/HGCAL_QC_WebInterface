#!/usr/bin/python3

import sys
import json 
import logging
import argparse
import components
from connect import connect

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Constants
LOCATION = "UMN"
INSTITUTION = "University of Minnesota"

MANU_RENAMES = { "Poly" : "PolyElectronics" }

KOPS = {
    'IC-ECD':'ECON-D',
    'IC-ECD-A':'ECON-D-A',
    'IC-ECD-B':'ECON-D-B',
    'IC-ECD-D':'ECON-D-D',
    'IC-ECD-F':'ECON-D-F',
    'IC-ECT':'ECON-T',
    'WH-21AT':'HD Wagon 2F Bottom D and T - Avocado',
    'WH-21AT-AAA':'HD Wagon 2F Bottom D and T - Qual AAA - Avocado',
    'WH-21AD':'HD Wagon 2F Bottom D only - Avocado',
    'WH-21AD-AAA':'HD Wagon 2F Bottom D only - Qual AAA - Avocado',
    'WH-21A1':'HD Wagon 2F Bottom PCB - Avocado',
    'WH-20AT':'HD Wagon 2F D and T - Grapes',
    'WH-20AT-BA':'HD Wagon 2F D and T - Qual BA - Grapes',
    'WH-20AD':'HD Wagon 2F D only - Grapes',
    'WH-20A1':'HD Wagon 2F PCB - Grapes',
    'WH-31AT':'HD Wagon 3F LR D and T - Apple',
    'WH-31AT-AAAA':'HD Wagon 3F LR D and T - Qual AAAA - Apple',
    'WH-31AD':'HD Wagon 3F LR D only - Apple',
    'WH-31AD-AAAA':'HD Wagon 3F LR D only - Qual AAAA - Apple',
    'WH-31A1':'HD Wagon 3F LR PCB - Apple',
    'WH-31BT':'HD Wagon 3F Top D and T - Cherry',
    'WH-31BT-AAAA':'HD Wagon 3F Top D and T - Qual AAAA - Cherry',
    'WH-31BT-BAAA':'HD Wagon 3F Top D and T - Qual BAAA - Cherry',
    'WH-31BD':'HD Wagon 3F Top D only - Cherry',
    'WH-31B1':'HD Wagon 3F Top PCB - Cherry',
    'WH-30AT':'HD Wagon 3F TypeA D and T - Pineapple',
    'WH-30A0':'HD Wagon 3F TypeA D and T - Pineapple -PRESERIES',
    'WH-30AT-AAA':'HD Wagon 3F TypeA D and T - Qual AAA - Pineapple',
    'WH-30AD':'HD Wagon 3F TypeA D only - Pineapple',
    'WH-30AD-AAA':'HD Wagon 3F TypeA D only - Qual AAA - Pineapple',
    'WH-30A1':'HD Wagon 3F TypeA PCB - Pineapple',
    'WH-30BT':'HD Wagon 3F TypeB D and T - Banana',
    'WH-30BT-AAA':'HD Wagon 3F TypeB D and T - Qual AAA - Banana',
    'WH-30BT-BAA':'HD Wagon 3F TypeB D and T - Qual BAA - Banana',
    'WH-30BD':'HD Wagon 3F TypeB D only - Banana',
    'WH-30BD-AAA':'HD Wagon 3F TypeB D only - Qual AAA - Banana',
    'WH-30B1':'HD Wagon 3F TypeB PCB - Banana',
    'WH-30CT':'HD Wagon 3F TypeC D and T - Pumpkin',
    'WH-30CT-AAA':'HD Wagon 3F TypeC D and T - Qual AAA - Pumpkin',
    'WH-30CD':'HD Wagon 3F TypeC D only - Pumpkin',
    'WH-30C1':'HD Wagon 3F TypeC PCB - Pumpkin',
    'WH-30DT':'HD Wagon 3F TypeD D and T - Donut',
    'WH-30DT-AAA':'HD Wagon 3F TypeD D and T - Qual AAA - Donut',
    'WH-30DT-BAB':'HD Wagon 3F TypeD D and T - Qual BAB - Donut',
    'WH-30DD':'HD Wagon 3F TypeD D only - Donut',
    'WH-30D1':'HD Wagon 3F TypeD PCB - Donut',
    'WH-30DD-AAA':'HD Wagon 3F TypeD D only - Qual AAA - Donut'
}

class MyXML():
    def __init__(self, writer):
        self.writer=writer
        self.stack=[]
        self.writer.write("<?xml version='1.1'?>\n")
        
    def open_tag(self, tag, attr=None):
        if attr is None:
            self.writer.write("%s<%s>\n"%(' '*len(self.stack)*2,tag))
            self.stack.append(tag)

    def close_tag(self, tag=None):
        if tag is not None:
            if tag!=self.stack[-1]:
                print("Non-matching tags '%s' != '%s'"%(tag,self.stack[-1]))
        self.writer.write("%s</%s>\n"%(' '*(len(self.stack)-1)*2,tag))
        self.stack=self.stack[:-1]

    def simple_item(self, tag, value, attr=None):
        if attr is None:
            self.writer.write("%s<%s>%s</%s>\n"%(' '*len(self.stack)*2,tag,value,tag))
        

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
    "WH-30BT:2" : "2026-03-19", "WH-30BD:2" : "2026-03-19",
    "WH-30DT:2" : "2026-03-26", "WH-30DD:2" : "2026-03-26",
    "WH-21AT:2" : "2026-03-19", "WH-21AD:2" : "2026-03-19",
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

def get_full_typecode(ctx, cur, barcode):
    nmodules=int(barcode[3+2+0])+int(barcode[3+2+1])
    typecode=barcode[3:5]+"-"+barcode[5:9]+"-"

    cur.execute("select attach from Attachments inner join Test where Test.test_id=Attachments.test_id and Test.test_type_id=29 and Test.board_id=(SELECT board_id from Board where full_id='%s')"%(barcode))
    n=0
    attach=""
    for result in cur:
        attach=result[0]
        if n>0:
            logger.warning("Multiple attachments for ECONs, confusing!")
    econ_info=json.loads(attach)
    retval=[]
    for nmod in range(1,nmodules+1):
        typecode+=econ_info["ECOND-M%d"%nmod]["full_id"][8]
    return typecode
        
def get_econs(ctx, cur, barcode, writer):
    """Find ECON scan data in DB"""

    nmodules=int(barcode[3+2+0])+int(barcode[3+2+1])
    typecode=barcode[3:5]+"-"+barcode[5:9]+"-"

    cur.execute("select attach from Attachments inner join Test where Test.test_id=Attachments.test_id and Test.test_type_id=29 and Test.board_id=(SELECT board_id from Board where full_id='%s')"%(barcode))
    n=0
    attach=""
    for result in cur:
        attach=result[0]
        if n>0:
            logger.warning("Multiple attachments for ECONs, confusing!")
    econ_info=json.loads(attach)
    retval=[]
    for nmod in range(1,nmodules+1):
        # go
        writer.open_tag("PART")
        writer.simple_item("KIND_OF_PART",KOPS["IC-ECD-%s"%(econ_info["ECOND-M%d"%nmod]["full_id"][8])])
        writer.simple_item("SERIAL_NUMBER",econ_info["ECOND-M%d"%nmod]["full_id"])
        writer.open_tag("PREDEFINED_ATTRIBUTES")
        writer.open_tag("ATTRIBUTE")
        writer.simple_item("NAME","ECON Position")
        writer.simple_item("VALUE","M%d"%nmod)
        writer.close_tag("ATTRIBUTE")
        writer.close_tag("PREDEFINED_ATTRIBUTES")
        writer.close_tag("PART")

        typecode+=econ_info["ECOND-M%d"%nmod]["full_id"][8]
        if barcode[3+2+3]=='T':            
            writer.open_tag("PART")
            writer.simple_item("KIND_OF_PART",KOPS["IC-ECT"])
            writer.simple_item("SERIAL_NUMBER",econ_info["ECONT-M%d"%nmod]["full_id"])
            writer.open_tag("PREDEFINED_ATTRIBUTES")
            writer.open_tag("ATTRIBUTE")
            writer.simple_item("NAME","ECON Position")
            writer.simple_item("VALUE","M%d"%nmod)
            writer.close_tag("ATTRIBUTE")
            writer.close_tag("PREDEFINED_ATTRIBUTES")
            writer.close_tag("PART")
    
def get_description(barcode,batch):
    """Check if the batch character is a number or a letter to assign a comment field."""
    return "Pre-series" if barcode[3+3+2]=='0' else "Pre-production" if batch=="1" else "Production"

def run(xml_file, bconly):
    """Main execution function."""
    try:
        db = connect(1)
        cur = db.cursor()
        ofile = None

        all_hd_wagons = filter_boards(cur)

        if xml_file is None:
            writer = MyXML(sys.stdout)
        else:
            writer = MyXML(open(xml_file, mode='w'))

        writer.open_tag("ROOT")
        writer.open_tag("PARTS")
            
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
#        writer.writerow(header_row)

        success = 0
        
        for barcode in all_hd_wagons:

            if bconly is not None and bconly!=barcode:
                continue

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

            writer.open_tag("PART")
            label_typecode=get_full_typecode(db,cur,barcode)
            writer.simple_item("KIND_OF_PART",KOPS[label_typecode])
            writer.simple_item("SERIAL_NUMBER",barcode)
            writer.simple_item("BARCODE",barcode)
            writer.simple_item("NAME_LABEL",name_label)
            writer.simple_item("PRODUCTION_DATE",production_date)
            writer.simple_item("MANUFACTURER",manufacturer)
            writer.simple_item("LOCATION",LOCATION)
            writer.simple_item("INSTITUTION",INSTITUTION)
            writer.simple_item("BATCH_NUMBER",batch)
            writer.simple_item("COMMENT_DESCRIPTION",comment)

            writer.open_tag("CHILDREN")
            
            bareboard = get_bare_board(db, cur, barcode)
            writer.open_tag("PART")
            writer.simple_item("KIND_OF_PART",KOPS[bareboard[0]])
            writer.simple_item("SERIAL_NUMBER",bareboard[1])
            writer.close_tag("PART")

            
            get_econs(db, cur, barcode, writer)

            writer.close_tag("CHILDREN")
            writer.close_tag("PART")
            
            
#            writer.writerow(items)
    
            success += 1

        writer.close_tag("PARTS")
        writer.close_tag("ROOT")

        logger.info(f"XML file for {success} HD wagons created successfully.")
#        if ofile is not None:
#            ofile.close()

    except Exception as e:
        logger.error(f"Critical error in run function: {e}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Register LD wagons by exporting data to an XML file.")
    parser.add_argument("-o", "--output", type=str, default=None, help="Output XML file name (e.g., output.xml)")
    parser.add_argument("-b","--barcode",type=str, default=None, help="Only process the given barcode")
    args = parser.parse_args()

    if args.output is None:        
        print("Content-type: text/xml")
        print('Content-disposition: attachment; filename="hd_wagons_register.xml"\n')
    run(args.output,args.barcode)
