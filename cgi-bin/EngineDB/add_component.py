#!/usr/bin/python3

import cgi, html
import base
from connect import connect


print("Content-type: text/html\n")

base.header(title='Add Component')
base.top(False)

db = connect(1)
cur = db.cursor()

form = cgi.FieldStorage()

if form.getvalue('full_id'):
    full_id = html.escape(form.getvalue('full_id'))
    barcode = html.escape(form.getvalue('barcode'))

    try:
        cur.execute('update Board set LDO="%s" where full_id="%s"' %(barcode, full_id))
        db.commit()

        # tells GUI where to look
        print('Begin')

        print(f'Updated LDO columns with value {barcode}.')

        print('End')
    except:
        print('Begin')

        print('An Error Occured when updating the LDO.')

        print('End')
        


else:
    print ("NO SERIAL SENT")


base.bottom(False)

