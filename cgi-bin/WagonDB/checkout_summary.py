#!./cgi_runner.sh

import cgi, html
import base
from connect import connect
from summary_functions import get
import module_functions
import sys

db = connect(0)
cur = db.cursor()

def run(static):
    base.header(title='Checkout Summary')
    base.top(static)

    # grabs all the information from check_out and sorts it by date
    cur.execute('select board_id,checkout_date,person_id,comment,checkin_id from Check_Out order by checkout_date desc')
    fetch = cur.fetchall()

    # sets up the table and header
    print('<div class="row">')
    print('<div class="col-md-5 ps-4 pt-4 mx-2 my-2"><h2>Check Out Summary</h2></div>')
    print('</div>')
    print('<div class="row">')
    print('<div class="col-md-12">')
    print('<div class="col-md-11 ps-5 py-4my-2"><table class="table table-hover">')
    print('<thead class="table-dark">')
    print('<tr>')
    print('<th> Full ID </th>')
    print('<th> Check Out Date </th>')
    print('<th> Person </th>')
    print('<th> Comment </th>')
    print('<th> Check In Date </th>')
    print('</tr>')
    print('</thead>')
    print('<tbody>')
    data = {}
    # runs twice, one to set up the dictionary and one to fill the dictionary
    for f in fetch:
        if f[0] == 0:
            continue
        cur.execute('select type_id from Board where board_id=%s' % f[0])
        type_id = cur.fetchall()[0][0]
        data[type_id] = []
    for f in fetch:
        if f[0] == 0:
            continue
        cur.execute('select type_id from Board where board_id=%s' % f[0])
        type_id = cur.fetchall()[0][0]
        # each subtype has a list of lists
        data[type_id].append(f)
    # iterates over the subtypes
    # sorts the checkout summary by subtype
    for k in data.keys():
        print('<tr><td colspan=5> %s </td></tr>' % k)
        # iterates over the lists for each subtype
        # d is a list
        for d in data[k]:
            # same pattern as for check in
            print('<tr>')
            cur.execute('select full_id from Board where board_id=%s' % d[0])
            sn = cur.fetchall()[0][0]
            if static:
                print('<td> <a href=./%(id)s_%(serial)s_module.html> %(serial)s </a></td>' %{'serial':sn, 'id':sn[3:9]})
            else:
                print('<td> <a href=module.py?board_id=%(id)s&full_id=%(serial)s> %(serial)s </a></td>' %{'serial':sn, 'id':d[0]})
            print('<td> %s </td>' % d[1])
            cur.execute('select person_name from People where person_id=%s' % d[2])
            print('<td> %s </td>' % cur.fetchall()[0][0])
            print('<td> %s </td>' % d[3])
            cur.execute('select checkin_date from Check_In where checkin_id=%s' % d[4])
            try:
                date = cur.fetchall()[0][0]
            except:
                date = None
            if date:
                print('<td> %s </td>' % date)
            else:
                print('<td> No check in date </td>')
            print('</tr>')


    print('</tbody></table></div></div>')

    base.bottom(static)

    
if __name__ == '__main__':
    #cgi header
    print("Content-type: text/html\n")

    run(False)
        

