#!/usr/bin/python3

import connect
import json
import cgi
import base
import add_test_functions

def parse_data(form):
    try:
        serial = base.cleanCGInumber(form.getvalue('serial_num'))
        board_type = str(serial)[4:9]
        tester = cgi.escape(form.getvalue('tester'))
        test = cgi.escape(form.getvalue('test_type'))
        successful = base.cleanCGInumber(form.getvalue('successful'))
        comments = cgi.escape(form.getvalue('comments'))
    
    except KeyError: 
        print('Json must contain at least the following entries:\nserial\nboard_type\ntester\ntest\nsucessful\ncomments\n\nPlease double check your json file for these fields')
    
    db = connect.connect(0)
    cur = db.cursor()
   
    cur.execute('SELECT person_id, person_name FROM People;')

    tester_data = [(x, y) for x,y in cur if y.lower() == tester.lower()]
    person_id = tester_data[0][0]   
 
    if not tester_data:
        print("Invalid tester (for writting priveldges, please access DB administrators)")
        return None
    
    cur.execute('SELECT test_type, name FROM Test_Type;')
    
    test_type_data = [(x,y) for x,y in cur if y.lower() == test.lower()]

    if not test_type_data:
        print("Invalid test type, see Wagon DB webpage for valid test types")
        return None

    cur.execute('SELECT type_id FROM Board;')

    type_id = [x[0] for x in cur if int(x[0]) == int(board_type)]

    if not type_id:
        print('Please enter a valid board type id')
        return None

    if comments == "":
        print("Please enter comments for this test")
        return None

    cur.execute('SELECT type_id, test_type_id FROM Type_test_stitch WHERE type_id = %s AND test_type_id = %s;' % (type_id[0], test_type_data[0][0]))

    if not cur:
        print('Invalid test for this board type. Check the DB webpage for valid tests')
        return None

    test_dict = {'serial_num': serial, 'board_type': board_type, 'tester': tester, 'person_id': person_id, 'test': test, 'test_type': test_type_data[0][0], 'successful': successful, 'comments': comments}

    return test_dict

base_url = connect.get_base_url()

#cgi header
print("Content-type: text/html\n")

base.header(title="Add Test From JSON")
base.top()

form = cgi.FieldStorage()
test_dict = parse_data(form)
print(test_dict)

test_id = add_test_functions.add_test(test_dict['person_id'], test_dict['test_type'], test_dict['serial_num'], test_dict['successful'], test_dict['comments'])


for itest in range(1,4):
    if not form.getvalue('attach%d'%(itest)): continue
    afile = form['attach%d'%(itest)]
    filename = form.getvalue('attachname%d'%(itest))
    if (afile.filename):
        adesc= form.getvalue("attachdesc%d"%(itest))
        if adesc:
            adesc = cgi.escape(adesc)
        acomment= form.getvalue("attachcomment%d"%(itest))
        if acomment:
            acomment = cgi.escape(acomment)
        add_test_functions.add_test_attachment(test_id,afile,adesc,acomment)

base.bottom()

#print(test_dict)

