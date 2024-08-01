import xml.etree.ElementTree as ET
import xml.dom.minidom

from connect import connect
import mysql.connector
import mysql

import sys
import os

form = cgi.FieldStorage()
serial_num = form.getvalue('full_id')
sys.path.insert(0, '../../hgcal-label-info/label-authority/')
import label_authority as la

db = connect(0)
cur = db.cursor()

# This is the parent (root) tag
root = ET.Element('ROOT')

# Adding Parts element to the root
data = ET.SubElement(root, 'PARTS')

# array of info for parts to add
board_ids, dates, locations = get_Info(serial_num)

#*for loop to add parts
new_part = ET.SubElement(data, 'PART')

#part info
part_batch_num = ET.SubElement(new_part, 'BATCH_NUMBER')
part_batch_num.text = "(batch number unknown)"
    
part_prod_date = ET.SubElement(new_part, 'PRODUCTION_DATE')
part_prod_date.text = "(get from EngineDB)"
    
part_name_lbl = ET.SubElement(new_part, 'NAME_LABEL')
part_name_lbl.text = "lpGBT (serial number)"
    
part_serial_num = ET.SubElement(new_part, 'SERIAL_NUMBER')
part_serial_num.text = "(serial number)"
    
part_barcode = ET.SubElement(new_part, 'BARCODE')
part_barcode.text = "ICLPG (serial number)"
    
part_manufac = ET.SubElement(new_part, 'MANUFACTURER')
part_manufac.text = "(manufacturer unknown)"   
    
part_kind = ET.SubElement(new_part, 'KIND_OF_PART')
part_kind.text = "lpGBT"
    
part_institution = ET.SubElement(new_part, 'INSTITUTION')
part_institution.text = "UMN"       
    
part_location = ET.SubElement(new_part, 'LOCATION')
part_location.text = "UMN"   
    
part_children = ET.SubElement(new_part, 'CHILDREN')

#child part info  
child_part = ET.SubElement(part_children, 'PART')
child_part.set('mode', 'auto')
    
child_kind_part = ET.SubElement(part_children, 'KIND_OF_PART')
child_kind_part.text = "lpGBT-stock"
    
child_serial_num = ET.SubElement(part_children, 'SERIAL_NUMBER')
child_serial_num.text = "(child serial number)"

# Converting xml data to byte object
_xml = ET.tostring(root)

# Writing out the file
with open("lpGBT_info.xml", "wb") as f:
    f.write(_xml)

def get_Info(barcode):
    
    # gets board id from the serial number(need barcode)
    decoded = la.decode(barcode)
    major = la.getMajorType(decoded.major_type_code)
    sub = major.getSubtypeByCode(decoded.subtype_code)
    board_sn = decoded.field_values['Serial Number'].value
    cur.execute('select board_id from Board where full_id="%s"' % board_sn)
    board_id = cur.fetchall()[0][0]
    
    board_ids = []
    for b in board_id:
        if b[0] != 0:
            #change statement to correctly get a board number
            cur.execute('select board from People where board_id="%s"' % b[0])
            board_num.append(cur.fetchall()[0][0])

    # gets 'production date' of lpGBT        
    cur.execute('select day from Test where board_id=%(b)s order by day desc' % board_id)
    _dates = cur.fetchall()
    dates = []
    for d in _dates:
        if d[0] != 0:
            #change statment for date
            cur.execute('select board from People where board_id="%s"' % d[0])
            dates.append(cur.fetchall()[0][0])

    # gets location of the lpGBT
    cur.execute('select location from Board where board_id=%s' % board_id)
    _locations = cur.fetchall()[0][0]
    locations = []
    for l in _locations:
        if l[0] != 0:
            #change statement for location
            cur.execute('select board from People where board_id="%s"' % l[0])
            locations.append(cur.fetchall()[0][0])

    return board_nums, dates, locations 

