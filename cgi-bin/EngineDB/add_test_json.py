#!/usr/bin/python3

import connect
import json
import cgi
import base
import add_test_functions

def parse_data(form):
    try:
        serial = form.getvalue('serial_num')
        print("serial_num:", serial)
        
        # board_type is a str
        board_type = str(serial)[4:10]
        print("board_type:", board_type)
        tester = cgi.escape(form.getvalue('tester'))
        print("tester:", tester)
        
        # test_type is an integer
        #test_type = int(cgi.escape(form.getvalue('test_type')))
        test_type = cgi.escape(form.getvalue('name'))
        print("test_type:", test_type)
        successful = base.cleanCGInumber(form.getvalue('successful'))
        print("successful:", successful)
        try:
            comments = cgi.escape(form.getvalue('comments'))
            print("comments:", comments)    
        except:
            print("No comments??!?")
            comments = ""
        
        try:
            data = form.getvalue('data')
        except Exception as e:
            print(e)
            print("Data could not be retrieved from the JSON")

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


    ####################
    # Tester has been verified
    ####################

    cur.execute('SELECT test_type, name FROM Test_Type;')
    test_dict0 = cur.fetchall()

    test_name = ""
    valid_test = False
    for i in test_dict0:
        print("Current index value:", i, "                   ")
        #if int(i[1]) == test_type:
        if i[1] == test_type:
            test_name = str(i[1])
            test_type = int(i[0])
            valid_test = True

    # test_type_data = [(x,y) for x,y in cur if y.lower() == test.lower()]

    if not valid_test:
        print("Invalid test type, see Wagon DB webpage for valid test types")
        return None

    ####################
    # Test type has been verified
    ####################
    

    cur.execute('SELECT type_sn FROM Board_type;')
    type_id_dict = cur.fetchall()


    valid_board_ID = False
   
    for i in type_id_dict:
        if i[0] == board_type:
            valid_board_ID = True
        

    if not valid_board_ID:
        print('Please enter a valid board type id')
        print("Board_type", board_type)
        # return None

    if comments == "":
        print("Please enter comments for this test")
        #return None


    #######################
    # Valid Test Board
    #######################



    cur.execute('SELECT type_id, test_type_id FROM Type_test_stitch WHERE type_id = "%s" AND test_type_id = %i;' % (board_type, int(test_type)))

    if not cur:
        print('Invalid test for this board type. Check the DB webpage for valid tests')
        return None



    # Creates output
    test_dict = {'serial_num': serial, 'board_type': board_type, 'tester': tester, 'person_id': person_id, 'test': test_name, 'test_type': test_type, 'successful': successful, 'comments': comments}


    print("          RETURNING TEST_DICT            ")
    return test_dict





##################################################################




base_url = connect.get_base_url()

#cgi header
print("Content-type: text/html\n")

base.header(title="Add Test From JSON")
base.top()

form = cgi.FieldStorage()
test_dict = parse_data(form)

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

