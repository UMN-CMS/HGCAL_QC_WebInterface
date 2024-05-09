#!/usr/bin/python3

import cgi
import cgitb
import base
from connect import connect
import mysql.connector
from summary_functions import get_testers
import module_functions
import sys

cgitb.enable()

if len(sys.argv) != 1:
    sys.stdout = open('%(loc)s/testers.html' %{'loc':sys.argv[1]}, 'w')

else:
    #cgi header
    print("Content-type: text/html\n")

base.header(title='Testers')
base.top()

people = get_testers()

print('<div class="row">')
print('<div class="col-md-5 ps-4 pt-4 mx-2 my-2"><h2>Tester Summary</h2></div>')
print('</div>')

for tester in people:
    print('<div class="row">')
    print('<div class="col-md-12 ps-5 py-2 mx-2 my-2">')
    print('<h3>%s</h3>' % tester["name"])
    print('</div>') 
    print('<div class="col-md-11 ps-5 py-2 my-2"><table class="table table-hover">')
    print('<thead class="table-dark">')
    print('<tr>')
    print('<th> Board ID </th>')
    print('<th colspan=2> Tests Completed </th>')
    print('</tr>')
    print('</thead>')
    print('<tbody>')
    board_id = ""
    i = 0
    for test in tester['tests']:
        prev_id = board_id
        board_id = test[3]
        if prev_id != board_id:
            print('</tr>')
            print('<tr>')
            if i != 0:
                print('</tr>')
                print('</ul></td>')
            if len(sys.argv) == 1:
                print('<td> <a href=module.py?board_id=%(id)s&serial_num=%(sn)s> %(sn)s </a></td>' %{'id':test[3], 'sn':test[4]})
            else:
                print('<td> <a href="card_%(id)s.html"> %(test_name)s </a></td>' %{'id':test[4], 'test_name':test[2]})
            print('<td><ul>')
        print('<li>%s' % test[2])

        i += 1

    print('</tbody></table></div></div>')


base.bottom()

    

