#!./cgi_runner.sh

import cgi, html
import cgitb
import base
from connect import connect

db = connect(1)
cur = db.cursor()

#cgi header
print("Content-type: text/html\n")

cgitb.enable()

base.header(title='Add information about the tester equipment')
base.top()

form = cgi.FieldStorage()

kria = form.getvalue('kria')
tester = form.getvalue('tester')
interposer = form.getvalue('interposer')
int_type = form.getvalue('interposer_type')
test_stand = form.getvalue('test_stand')

cur.execute('select role_id from Tester_Roles where description="Kria Controller"')
kria_id = cur.fetchall()[0][0]

cur.execute('select role_id from Tester_Roles where description="Wagon Tester"')
tester_id = cur.fetchall()[0][0]

if int_type == 'East':
    cur.execute('select role_id from Tester_Roles where description="East Interposer"')
    int_id = cur.fetchall()[0][0]
if int_type == 'West':
    cur.execute('select role_id from Tester_Roles where description="West Interposer"')
    int_id = cur.fetchall()[0][0]

cur.execute('select teststand_id from Teststand where name="%s"' % test_stand)
test_stand_id = cur.fetchall()
if test_stand_id:
    test_stand_id = test_stand_id[0][0]
else:
    cur.execute('insert into Teststand (name) values ("%s")' % test_stand)
    db.commit()
    cur.execute('select teststand_id from Teststand where name="%s"' % test_stand)
    test_stand_id = cur.fetchall()[0][0]

cur.execute('select role_id from Tester_Roles where description="Wagon Wheel 1"')
wheel_1_id = cur.fetchall()[0][0]

cur.execute('select role_id from Tester_Roles where description="Wagon Wheel 2"')
wheel_2_id = cur.fetchall()[0][0]

cur.execute('select role_id from Tester_Roles where description="Wagon Wheel 3"')
wheel_3_id = cur.fetchall()[0][0]

cur.execute('select role_id from Tester_Roles where description="Wagon Wheel 4"')
wheel_4_id = cur.fetchall()[0][0]

wheel_1 = form.getvalue('wheel_1')

try:
    wheel_2 = form.getvalue('wheel_2')
except:
    wheel_2 = None

try:
    wheel_3 = form.getvalue('wheel_3')
except:
    wheel_3 = None

try:
    wheel_4 = form.getvalue('wheel_4')
except:
    wheel_4 = None

info_dict = {kria_id: kria,
            tester_id: tester,
            int_id: interposer,
            wheel_1_id: wheel_1,
            wheel_2_id: wheel_2,
            wheel_3_id: wheel_3,
            wheel_4_id: wheel_4,
}

for k,v in info_dict.items():
    if v:
        cur.execute('select component_id from Tester_Component where full_id="%s"' % v)
        component = cur.fetchall()
        if component:
            pass
        else:
            cur.execute('insert into Tester_Component (full_id) values ("%s")' % v)
            db.commit()
        
for k,v in info_dict.items():
    if v:
        cur.execute('select component_id from Tester_Component where full_id="%s"' % v)
        component = cur.fetchall()
        info_dict[k] = component[0][0]
cur.execute('select config_id from Tester_Configuration order by config_id desc')
try:
    config_id = cur.fetchall()[0][0] + 1
except:
    config_id = 0

for k,v in info_dict.items():
    if v:
        cur.execute('insert into Tester_Configuration (config_id, role_id, component_id, teststand_id) values (%s, %s, %s, %s)' % (config_id, k, v, test_stand_id))
db.commit()
print('Begin')
print(config_id)
print('End')
                                    
base.bottom()

