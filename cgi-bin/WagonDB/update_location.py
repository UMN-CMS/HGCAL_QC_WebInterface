#!/usr/bin/python3

import cgi
import base
from connect import connect


print("Content-type: text/html\n")

base.header(title='Update Location')
base.top(False)

db = connect(1)
cur = db.cursor()

form = cgi.FieldStorage()

if form.getvalue('serial_number'):
    serial_number = cgi.escape(form.getvalue('serial_number'))
    loc = cgi.escape(form.getvalue('location'))
    loc = 'Last seen at ' + loc

    try:
        # updates the location of the board in the database
        cur.execute('update Board set location="%s" where full_id="%s"' %(loc, serial_number))
        db.commit()

        # tells GUI where to look
        print('Begin')

        print('Location Updated.')

        print('End')
    except:
        print('Begin')

        print('An Error Occured when updating the location.')

        print('End')
        


else:
    print ("NO SERIAL SENT")


base.bottom(False)

