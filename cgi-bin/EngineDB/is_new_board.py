#!/usr/bin/python3


import cgi
import base
import add_test_functions
import os


print("Content-type: text/html\n")

base.header(title='is_new_board')
base.top()


form = cgi.FieldStorage()

if form.getvalue('serial_number'):
    serial_number = cgi.escape(form.getvalue('serial_number'))


    is_new_board_bool = add_test_functions.is_new_board(serial_number)

    print('Begin')

    print(is_new_board_bool)

    print('End')


else:
    print ("NO SERIAL SENT")


base.bottom()

