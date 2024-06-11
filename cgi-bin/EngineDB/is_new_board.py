#!/usr/bin/python3


import cgi
import base
import add_test_functions
import os


print("Content-type: text/html\n")

base.header(title='is_new_board')
base.top(False)


form = cgi.FieldStorage()

if form.getvalue('full_id'):
    full_id = cgi.escape(form.getvalue('full_id'))


    is_new_board_bool = add_test_functions.is_new_board(full_id)

    print('Begin')

    print(is_new_board_bool)

    print('End')


else:
    print ("NO SERIAL SENT")


base.bottom(False)

