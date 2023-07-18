#!/usr/bin/python3
from connect import connect
import module_functions
import numpy as np
import pandas as pd
#import mysql.connector

def get():
    TestData = pd.read_csv('./static/files/Test.csv')
    BoardData = pd.read_csv('./static/files/Board.csv')
    df = TestData.merge(BoardData, on='Board ID', how='left')
    TestTypes = pd.read_csv('./static/files/Test_Types.csv')
    
    subtypes = np.unique(df['Type ID']).tolist()
    serial_numbers = {}
    for s in subtypes:
        serial_numbers[s] = np.unique(df.query('`Type ID` ==  @s')['Full ID']).tolist()
        print('<tr><td colspan=5><a class="btn btn-dark" data-bs-toggle="collapse" href="#col%(id)s">%(id)s</a></td></tr>' %{'id':s})

        print('<tr><td class="hiddenRow" colspan=5>')
        print('<div class="collapse" id="col%s">' %s)
        print('<table>')
        for sn in serial_numbers[s]:
            data = df.query('`Full ID` == @sn')[['Test Type ID','Successful']]
            tt_ids = TestTypes['Test Type'].tolist()
            names = TestTypes['Name'].tolist()
            outcomes = []
            for t in tt_ids:
                if 1 in data.query('`Test Type ID` == @t')['Successful'].values.tolist():
                    outcomes.append(True)
                else:
                    outcomes.append(False)
            print('<tr>')
            print('<td> <a href=module.py?board_id=%(id)s&serial_num=%(serial)s> %(serial)s </a></td>' %{'serial':sn, 'id':s})
            print('<td><ul>')
            for idx,o in enumerate(outcomes[0:2]):
                if o == True:
                    if idx == 0:
                        print('<li>%s' %TestTypes.query('`Test Type` ==  1')['Name'].values.tolist()[0])
                    if idx == 1:
                        print('<li>%s' %TestTypes.query('`Test Type` ==  2')['Name'].values.tolist()[0])
            print('</ul></td>') 
            print('<td><ul>')
            for idx,o in enumerate(outcomes[2:4]):
                if o == True:
                    if idx == 0:
                        print('<li>%s' %TestTypes.query('`Test Type` ==  3')['Name'].values.tolist()[0])
                    if idx == 1:
                        print('<li>%s' %TestTypes.query('`Test Type` ==  4')['Name'].values.tolist()[0])
            print('</ul></td>') 

            print('<td><ul>')
            for idx,o in enumerate(outcomes[0:2]):
                if o == False:
                    if idx == 0:
                        print('<li> <a href="add_test.py?serial_num=%(serial_num)s&board_id=%(board_id)s&suggested=%(test_type_id)s">%(name)s</a>' %{'board_id':s, 'serial_num':sn, 'test_type_id':tt_ids[0], 'name':names[0]})
                    if idx == 1:
                        print('<li> <a href="add_test.py?serial_num=%(serial_num)s&board_id=%(board_id)s&suggested=%(test_type_id)s">%(name)s</a>' %{'board_id':s, 'serial_num':sn, 'test_type_id':tt_ids[1], 'name':names[1]})
            print('</ul></td>') 
            print('<td><ul>')
            for idx,o in enumerate(outcomes[2:4]):
                if o == False:
                    if idx == 0:
                        print('<li> <a href="add_test.py?serial_num=%(serial_num)s&board_id=%(board_id)s&suggested=%(test_type_id)s">%(name)s</a>' %{'board_id':s, 'serial_num':sn, 'test_type_id':tt_ids[2], 'name':names[2]})
                    if idx == 1:
                        print('<li> <a href="add_test.py?serial_num=%(serial_num)s&board_id=%(board_id)s&suggested=%(test_type_id)s">%(name)s</a>' %{'board_id':s, 'serial_num':sn, 'test_type_id':tt_ids[3], 'name':names[3]})
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

