#!/usr/bin/python3

import cgi
import base
from connect import connect
#import mysql.connector
from summary_functions import get
import module_functions
import sys

if len(sys.argv) != 1:
    sys.stdout = open('%(loc)s/summary.html' %{'loc':sys.argv[1]}, 'w')

else:
    #cgi header
    print("Content-type: text/html\n")

base.header(title='Summary')
base.top()

#List_of_rows = get()

print('<div class="row">')
print('<div class="col-md-5 ps-4 pt-4 mx-2 my-2"><h2>Test Summary</h2></div>')
print('</div>')
print('<div class="row">')
print('<div class="col-md-12">')
print('<div class="col-md-11 ps-5 py-4my-2"><table class="table table-hover">')
print('<thead class="table-dark">')
print('<tr>')
print('<th> S/N </th>')
print('<th colspan=3> Tests Passed </th>')
print('<th colspan=3> Tests Remaining </th>')
#print                    '<th> Final Status </th>'
print('</tr>')
print('</thead>')
print('<tbody>')

get()

#for row in List_of_rows:
    #print('<tr>')
    #if len(sys.argv) == 1:
        #print('<td> <a href=module.py?board_id=%(id)s&serial_num=%(serial)s> %(serial)s </a></td>' %{'serial':row[2], 'id':row[1]})
        ##print '<td> %s </td>' %row[1]
    #else:
        #print('<td> <a href="card_%(serial)s.html"> %(serial)s </a></td>' %{'serial':row[2]})
    #print('<td><ul>')
    #for tests in row[3][0:][::2]:
        #print('<li>%s' %tests)
    #print('</ul></td>')

    #print('<td><ul>')
    #for tests in row[3][1:][::2]:
        #print('<li>%s' %tests)
    #print('</ul></td>')

    #print('<td><ul>')
    #if len(sys.argv) == 1:
        #for tests in row[4][0:][::2]:
            #print('<li> <a href="add_test.py?serial_num=%(serial_num)s&board_id=%(board_id)d&suggested=%(test_type_id)d">%(name)s</a>' %{'board_id':row[0], 'serial_num':row[2], 'test_type_id':tests[1], 'name':tests[0]})

    #else:
        #for tests in row[4][0:][::2]:
            #print('<li>%s' %tests[0] )
    #print('</ul></td>')

    #print('<td><ul>')
    #if len(sys.argv) == 1:
        #for tests in row[4][1:][::2]:
            #print('<li> <a href="add_test.py?serial_num=%d&suggested=%d">%s</a>' %(row[0],tests[1],tests[0]))
    #else:
        #for tests in row[4][1:][::2]:
            #print('<li>%s' %tests[0])
    #print('</ul></td>')
    
    #print('</tr>')

print('</tbody></table></div></div>')


base.bottom()

    

