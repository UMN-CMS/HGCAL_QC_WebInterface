#!/usr/bin/python3

try:
    import cgi
    import cgitb; cgitb.enable()
    import base
    import label_functions
    import sys

    if(len(sys.argv) != 1):
        stdout = sys.stdout
        sys.stdout = open('%(loc)s/index.html' %{ 'loc':sys.argv[1]}, 'w') 
    else:
        #cgi header
        print("content-type: text/html\n\n")

    base.header(title='HGCAL Labeling Home Page')
    base.top()

    label_functions.label_type_table()

    base.bottom()

    if len(sys.argv) != 1:
        sys.stdout.close()
        sys.stdout = stdout
except Exception as e:
    print(e)
