#!/usr/bin/python3

import connect
import json
import cgi
import base
import add_test_functions

def parse_data(form):
    try:
        full_id = (form.getvalue('full_id'))
        print("full_id:", full_id)
        
        # board_type is a str
        board_type = str(full_id)[3:9]
        print("board_type:", board_type)
        tester = cgi.escape(form.getvalue('tester'))
        print("tester:", tester)
        
        # test_name is a str
        test_name = str(cgi.escape(form.getvalue('test_type')))
        print("test_type:", test_name)
        successful = base.cleanCGInumber(form.getvalue('successful'))
        print("successful:", successful)
        comments = cgi.escape(form.getvalue('comments'))
        print("comments:", comments)    
        
        try:
            data = form.getvalue('data')
        except Exception as e:
            print(e)
            print("Data could not be retrieved from the JSON")

        try:
            config_id = form.getvalue('config_id')
        except:
            config_id = None

    except KeyError: 
        print('Json must contain at least the following entries:\nserial\nboard_type\ntester\ntest\nsucessful\ncomments\n\nPlease double check your json file for these fields')
    
    db = connect.connect(0)
    cur = db.cursor()
   
    cur.execute('SELECT person_id, person_name FROM People;')

    user_dict = cur.fetchall()

    person_id = 123
    valid_tester = False
    for i in user_dict:
        if i[1].lower() == tester.lower():
            valid_tester = True   
            person_id = i[0]

 
    if not valid_tester:
        print("Invalid tester (for writting priveldges, please access DB administrators)")
        return None


    # Creates output
    test_dict = {'full_id': full_id, 'board_type': board_type, 'tester': tester, 'person_id': person_id, 'test': test_name, 'successful': successful, 'comments': comments, 'config_id': config_id}


    print("          RETURNING TEST_DICT            ")
    return test_dict





##################################################################




base_url = connect.get_base_url()

#cgi header
print("Content-type: text/html\n")

base.header(title="Add Test From JSON")
base.top(False)

form = cgi.FieldStorage()
test_dict = parse_data(form)


test_id = add_test_functions.add_test(test_dict['person_id'], test_dict['test'], test_dict['full_id'], test_dict['successful'], test_dict['comments'], test_dict['config_id'])


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

if test_dict['test'] == 'LPGBT ID':
    add_test_functions.set_daq_chip_id(test_dict['full_id'], test_id)

base.bottom(False)

