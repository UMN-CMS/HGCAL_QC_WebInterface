#!/usr/bin/python3
from connect import connect
import module_functions
import numpy as np
import pandas as pd

db = connect(0)
cur = db.cursor()

def get():
    tt_ids = []
    cur.execute('select test_type from Test_Type')
    temp = cur.fetchall()
    for t in temp:
        tt_ids.append(t[0])
    subtypes = []
    cur.execute('select board_id from Board')
    temp = cur.fetchall()
    for t in temp:
        cur.execute('select type_id from Board where board_id="%s"' % t[0])
        new = cur.fetchall()
        subtypes.append(new[0][0])
    subtypes = np.unique(subtypes).tolist()
    
    serial_numbers = {}
    for s in subtypes:
        cur.execute('select full_id from Board where type_id="%s"' % s)
        li = []
        for l in cur.fetchall():
            li.append(l[0])
        serial_numbers[s] = np.unique(li).tolist()
    
        print('<tr><td colspan=7><a class="btn btn-dark" data-bs-toggle="collapse" href="#col%(id)s">%(id)s</a></td></tr>' %{'id':s})

        print('<tr><td class="hiddenRow" colspan=7>')
        print('<div class="collapse" id="col%s">' %s)
        print('<table>')
        for sn in serial_numbers[s]:
            cur.execute('select board_id from Board where full_id="%s"' % sn)
            board_id = cur.fetchall()[0][0]
            cur.execute('select test_type_id, successful from Test where board_id=%s' % board_id)
            temp = cur.fetchall()
            outcomes = []
            oc_dict = {}
            for i in tt_ids:
                oc_dict[i] = []
            for t in temp:
                oc_dict[t[0]].append(t[1])
            for t in tt_ids:
                if 1 in oc_dict[t]:
                    outcomes.append(True)
                else:
                    outcomes.append(False)
            cur.execute('select name from Test_Type')
            temp = cur.fetchall()
            names = []
            for t in temp:
                names.append(t[0])

            print('<tr>')
            print('<td> <a href=module.py?board_id=%(id)s&serial_num=%(serial)s> %(serial)s </a></td>' %{'serial':sn, 'id':s})
            print('<td><ul>')
            for idx,o in enumerate(outcomes[0:7]):
                if o == True:
                    if idx == 0:
                        print('<li>%s' %names[0])
                    if idx == 1:
                        print('<li>%s' %names[1])
                    if idx == 2:
                        print('<li>%s' %names[2])
                    if idx == 3:
                        print('<li>%s' %names[3])
                    if idx == 4:
                        print('<li>%s' %names[4])
                    if idx == 5:
                        print('<li>%s' %names[5])
                    if idx == 6:
                        print('<li>%s' %names[6])
            print('</ul></td>') 
            print('<td><ul>')
            for idx,o in enumerate(outcomes[7:14]):
                if o == True:
                    if idx == 0:
                        print('<li>%s' %names[7])
                    if idx == 1:
                        print('<li>%s' %names[8])
                    if idx == 2:
                        print('<li>%s' %names[9])
                    if idx == 3:
                        print('<li>%s' %names[10])
                    if idx == 4:
                        print('<li>%s' %names[11])
                    if idx == 5:
                        print('<li>%s' %names[12])
                    if idx == 6:
                        print('<li>%s' %names[13])
            print('</ul></td>') 
            print('<td><ul>')
            for idx,o in enumerate(outcomes[14:21]):
                if o == True:
                    if idx == 0:
                        print('<li>%s' %names[14])
                    if idx == 1:
                        print('<li>%s' %names[15])
                    if idx == 2:
                        print('<li>%s' %names[16])
                    if idx == 3:
                        print('<li>%s' %names[17])
                    if idx == 4:
                        print('<li>%s' %names[18])
                    if idx == 5:
                        print('<li>%s' %names[19])
                    if idx == 6:
                        print('<li>%s' %names[20])
            print('</ul></td>') 

            print('<td><ul>')
            for idx,o in enumerate(outcomes[0:7]):
                if o == False:
                    if idx == 0:
                        print('<li> <a href="add_test.py?serial_num=%(serial_num)s&board_id=%(board_id)s&suggested=%(test_type_id)s">%(name)s</a>' %{'board_id':s, 'serial_num':sn, 'test_type_id':tt_ids[0], 'name':names[0]})
                    if idx == 1:
                        print('<li> <a href="add_test.py?serial_num=%(serial_num)s&board_id=%(board_id)s&suggested=%(test_type_id)s">%(name)s</a>' %{'board_id':s, 'serial_num':sn, 'test_type_id':tt_ids[1], 'name':names[1]})
                    if idx == 2:
                        print('<li> <a href="add_test.py?serial_num=%(serial_num)s&board_id=%(board_id)s&suggested=%(test_type_id)s">%(name)s</a>' %{'board_id':s, 'serial_num':sn, 'test_type_id':tt_ids[2], 'name':names[2]})
                    if idx == 3:
                        print('<li> <a href="add_test.py?serial_num=%(serial_num)s&board_id=%(board_id)s&suggested=%(test_type_id)s">%(name)s</a>' %{'board_id':s, 'serial_num':sn, 'test_type_id':tt_ids[3], 'name':names[3]})
                    if idx == 4:
                        print('<li> <a href="add_test.py?serial_num=%(serial_num)s&board_id=%(board_id)s&suggested=%(test_type_id)s">%(name)s</a>' %{'board_id':s, 'serial_num':sn, 'test_type_id':tt_ids[4], 'name':names[4]})
                    if idx == 5:
                        print('<li> <a href="add_test.py?serial_num=%(serial_num)s&board_id=%(board_id)s&suggested=%(test_type_id)s">%(name)s</a>' %{'board_id':s, 'serial_num':sn, 'test_type_id':tt_ids[5], 'name':names[5]})
                    if idx == 6:
                        print('<li> <a href="add_test.py?serial_num=%(serial_num)s&board_id=%(board_id)s&suggested=%(test_type_id)s">%(name)s</a>' %{'board_id':s, 'serial_num':sn, 'test_type_id':tt_ids[6], 'name':names[6]})
            print('</ul></td>') 
            print('<td><ul>')
            for idx,o in enumerate(outcomes[7:14]):
                if o == False:
                    if idx == 0:
                        print('<li> <a href="add_test.py?serial_num=%(serial_num)s&board_id=%(board_id)s&suggested=%(test_type_id)s">%(name)s</a>' %{'board_id':s, 'serial_num':sn, 'test_type_id':tt_ids[7], 'name':names[7]})
                    if idx == 1:
                        print('<li> <a href="add_test.py?serial_num=%(serial_num)s&board_id=%(board_id)s&suggested=%(test_type_id)s">%(name)s</a>' %{'board_id':s, 'serial_num':sn, 'test_type_id':tt_ids[8], 'name':names[8]})
                    if idx == 2:
                        print('<li> <a href="add_test.py?serial_num=%(serial_num)s&board_id=%(board_id)s&suggested=%(test_type_id)s">%(name)s</a>' %{'board_id':s, 'serial_num':sn, 'test_type_id':tt_ids[9], 'name':names[9]})
                    if idx == 3:
                        print('<li> <a href="add_test.py?serial_num=%(serial_num)s&board_id=%(board_id)s&suggested=%(test_type_id)s">%(name)s</a>' %{'board_id':s, 'serial_num':sn, 'test_type_id':tt_ids[10], 'name':names[10]})
                    if idx == 4:
                        print('<li> <a href="add_test.py?serial_num=%(serial_num)s&board_id=%(board_id)s&suggested=%(test_type_id)s">%(name)s</a>' %{'board_id':s, 'serial_num':sn, 'test_type_id':tt_ids[11], 'name':names[11]})
                    if idx == 5:
                        print('<li> <a href="add_test.py?serial_num=%(serial_num)s&board_id=%(board_id)s&suggested=%(test_type_id)s">%(name)s</a>' %{'board_id':s, 'serial_num':sn, 'test_type_id':tt_ids[12], 'name':names[12]})
                    if idx == 6:
                        print('<li> <a href="add_test.py?serial_num=%(serial_num)s&board_id=%(board_id)s&suggested=%(test_type_id)s">%(name)s</a>' %{'board_id':s, 'serial_num':sn, 'test_type_id':tt_ids[13], 'name':names[13]})
            print('</ul></td>') 
            print('<td><ul>')
            for idx,o in enumerate(outcomes[14:21]):
                if o == False:
                    if idx == 0:
                        print('<li> <a href="add_test.py?serial_num=%(serial_num)s&board_id=%(board_id)s&suggested=%(test_type_id)s">%(name)s</a>' %{'board_id':s, 'serial_num':sn, 'test_type_id':tt_ids[14], 'name':names[14]})
                    if idx == 1:
                        print('<li> <a href="add_test.py?serial_num=%(serial_num)s&board_id=%(board_id)s&suggested=%(test_type_id)s">%(name)s</a>' %{'board_id':s, 'serial_num':sn, 'test_type_id':tt_ids[15], 'name':names[15]})
                    if idx == 2:
                        print('<li> <a href="add_test.py?serial_num=%(serial_num)s&board_id=%(board_id)s&suggested=%(test_type_id)s">%(name)s</a>' %{'board_id':s, 'serial_num':sn, 'test_type_id':tt_ids[16], 'name':names[16]})
                    if idx == 3:
                        print('<li> <a href="add_test.py?serial_num=%(serial_num)s&board_id=%(board_id)s&suggested=%(test_type_id)s">%(name)s</a>' %{'board_id':s, 'serial_num':sn, 'test_type_id':tt_ids[17], 'name':names[17]})
                    if idx == 4:
                        print('<li> <a href="add_test.py?serial_num=%(serial_num)s&board_id=%(board_id)s&suggested=%(test_type_id)s">%(name)s</a>' %{'board_id':s, 'serial_num':sn, 'test_type_id':tt_ids[18], 'name':names[18]})
                    if idx == 5:
                        print('<li> <a href="add_test.py?serial_num=%(serial_num)s&board_id=%(board_id)s&suggested=%(test_type_id)s">%(name)s</a>' %{'board_id':s, 'serial_num':sn, 'test_type_id':tt_ids[19], 'name':names[19]})
                    if idx == 6:
                        print('<li> <a href="add_test.py?serial_num=%(serial_num)s&board_id=%(board_id)s&suggested=%(test_type_id)s">%(name)s</a>' %{'board_id':s, 'serial_num':sn, 'test_type_id':tt_ids[20], 'name':names[20]})
            print('</ul></td>') 
            print('</tr>')

        print('</table>')
        print('</div>')
        print('</td></tr>')

#get()


def oldget():
    
    db = connect(0)
    cur = db.cursor()
    
    cur.execute("SELECT sn, board_id, full_id FROM Board ORDER by sn ASC")
    rows = cur.fetchall()
 
    
    serial_numbers = []
    for board in rows:
        serial_numbers.append(board[0])
        
    pass_dic = dict()
    for sn in serial_numbers:
        cur.execute("SELECT Test_Type.name,Test.test_id FROM Test_Type, Board, Test WHERE Board.sn = %(n)s And Test.board_id = Board.board_id AND Test_Type.test_type = Test.test_type_id AND Test_Type.required =1 AND Test.successful = 1 ORDER by relative_order" %{"n": sn})
        passed = cur.fetchall()
        revoked = module_functions.Portage_fetch_revokes(sn)
        temp1 = []
        for x in passed:
            if x[1] not in revoked:
                if x[0] not in temp1:
                    temp1.append(x[0])
        pass_dic[sn] = temp1

    list_of_all_required_tests = []
    test_dict = { }
    cur.execute("SELECT name,test_type FROM Test_Type WHERE Test_Type.required = 1 ORDER by relative_order")
    for names in cur:
        list_of_all_required_tests.append(names[0])
        test_dict[names[0]]=names[1]

    List_of_lists = []
    for tests in rows:
        small_list = []
        rem_list = []
        for items in tests:
            small_list.append(items)
        small_list.append(pass_dic[tests[0]])
        for remaining in list_of_all_required_tests:
            if remaining not in pass_dic[tests[0]]:
                remneeds=[ remaining, test_dict[remaining] ]
                rem_list.append(remneeds)
        small_list.append(rem_list)
        List_of_lists.append(small_list)

    print(List_of_lists[0][4])
    return List_of_lists


def get_testers():
    
    db = connect(0)
    cur = db.cursor()
    
    cur.execute("SELECT person_id, person_name FROM People ORDER by person_id ASC")
    rows = cur.fetchall()
    
    people = []
    for person in rows:
        pid = person[0]
        name = person[1]
        p = {"name": name, "pid": pid, "tests": []}
        
        cur.execute("SELECT Test.test_id, Test.test_type_id, Test_Type.name, Board.board_id, Board.full_id FROM Test, Board, Test_Type WHERE Test.board_id = Board.board_id AND Test.person_id = %s AND Test_Type.test_type = Test.test_type_id ORDER BY Board.board_id ASC" % pid)
        tests = cur.fetchall()

        for t in tests:
            p['tests'].append(t)

        people.append(p)

    return people

if __name__ == "__main__":
    get_testers()

