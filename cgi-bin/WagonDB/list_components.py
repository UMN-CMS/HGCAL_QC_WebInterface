#!./cgi_runner.sh

import cgi, html
import base
import add_test_functions
import os
from connect import connect

form = cgi.FieldStorage()
db = connect(0)
cur = db.cursor()

if form.getvalue("typecode"):
    typecode = form.getvalue("typecode")
    print('Content-Type: text/plain')
    print('Content-Disposition: attachment; filename=%s_available.csv' % typecode)
    print()
    cur.execute('SELECT barcode FROM COMPONENT_STOCK WHERE typecode="%s" AND component_id NOT IN (SELECT component_id from COMPONENT_USAGE)' % typecode)
    for barcode in cur.fetchall():
        print(f"{barcode[0]},")

else:

    print("Content-type: text/html\n")

    base.header(title='Components List')
    base.top()


    print('<div class="col-md-11 mx-4 my-4"><table class="table table-bordered table-hover table-active">')
    print('<tr><th>Typecode<th># Known<th># Available</tr>')

    cur.execute('select distinct typecode from COMPONENT_STOCK')
    for _type in cur.fetchall():
        cur.execute('select COUNT(component_id) from COMPONENT_STOCK where typecode="%s"' % _type)
        total = cur.fetchall()[0][0]

        cur.execute('SELECT COUNT(barcode) from COMPONENT_STOCK WHERE typecode="%s" AND component_id NOT IN (SELECT component_id from COMPONENT_USAGE)' %_type)
        available = cur.fetchall()[0][0]

        print(f'<tr><td><a href="list_components.py?typecode={_type[0]}">{_type[0]}</a></td><td>{total}</td><td>{available}</td></tr>')

    print("</table></div>")

    base.bottom()

