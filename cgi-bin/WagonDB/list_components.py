#!./cgi_runner.sh

import cgi, html
import base
import add_test_functions
import os
from connect import connect

print("Content-type: text/html\n")

base.header(title='Components List')
base.top()

db = connect(0)
cur = db.cursor()

print('<div class="col-md-11 mx-4 my-4"><table class="table table-bordered table-hover table-active">')
print('<tr><th>Typecode<th># of Stock<th># Available</tr>')

cur.execute('select distinct typecode from COMPONENT_STOCK')
for _type in cur.fetchall():
    cur.execute('select component_id from COMPONENT_STOCK where typecode="%s"' % _type)
    stock = cur.fetchall()
    total = len(stock)

    used = 0
    for item in stock:
        cur.execute('select * from COMPONENT_USAGE where component_id=%s' % item[0])
        if cur.fetchall():
            used += 1

    print(f"<tr><td>{_type[0]}</td><td>{total}</td><td>{total-used}</td></tr>")

print("</table></div>")

base.bottom()

