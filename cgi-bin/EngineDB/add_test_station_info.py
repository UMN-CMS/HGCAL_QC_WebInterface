#!/usr/bin/python3

import cgi
import base
from connect import connect

db = connect(1)
cur = db.cursor()

#cgi header
print("Content-type: text/html\n")

base.header(title='Add information about the tester equipment')
base.top(False)

form = cgi.FieldStorage()

zcu = form.getvalue('ZCU')
east_interposter = form.getvalue('east_interposer')
west_interposter = form.getvalue('west_interposer')
test_stand = form.getvalue('test_stand')

cur.execute('select role_id from Tester_Roles where description="ZCU"')
zcu_id = cur.fetchall()[0][0]

cur.execute('select role_id from Tester_Roles where description="East Interposer"')
east_int_id = cur.fetchall()[0][0]

cur.execute('select role_id from Tester_Roles where description="West Interposer"')
west_int_id = cur.fetchall()[0][0]

cur.execute('select teststand_id from Teststand where name="%s"' % test_stand)
test_stand_id = cur.fetchall()
if test_stand_id:
    test_stand_id = test_stand_id[0][0]
else:
    cur.execute('insert into Teststand (name) values (%s)' % test_stand)
    db.commit()
    cur.execute('select teststand_id from Teststand where name="%s"' % test_stand)
    test_stand_id = cur.fetchall()[0][0]

cur.execute('select role_id from Tester_Roles where description="Test Bridge 1"')
bridge_1_id = cur.fetchall()[0][0]

cur.execute('select role_id from Tester_Roles where description="Test Bridge 2"')
bridge_2_id = cur.fetchall()[0][0]

bridge_1 = form.getvalue('bridge_1')

bridge_2 = form.getvalue('bridge_2')

info_dict = {zcu_id: zcu,
            east_int_id: east_interposer,
            west_int_id: west_interposer,
            bridge_1_id: bridge_1,
            bridge_2_id: bridge_2,
 }

for k,v in info_dict.items():
    cur.execute('select component_id from Tester_Component where full_id="%s"' % v)
    component = cur.fetchall()
    if component:
        pass
    else:
        cur.execute('insert into Tester_Component (full_id) values (%s)' % v)
        db.commit()
        
for k,v in info_dict.items():
    cur.execute('select component_id from Tester_Component where full_id="%s"' % v)
    component = cur.fetchall()
    info_dict[k] = component[0][0]

cur.execute('select config_id from Tester_Configuration order by config_id desc')
config_id = cur.fetchall()[0][0] + 1

found_config = []

cur.execute('select config_id from Tester_Configuration where component_id=%s and teststand_id=%s' % (info_dict[zcu_id], test_stand_id))
config1 = cur.fetchall()
if config1:
    for c in config1:
        cur.execute('select config_id from Tester_Configuration where config_id=%s and component_id=%s' % (c[0], info_dict[east_int_id]))
        config2 = cur.fetchall()
        if config2:
            cur.execute('select config_id from Tester_Configuration where config_id=%s and component_id=%s' % (c[0], info_dict[west_int_id])) 
            config3 = cur.fetchall()
            if config3:
                cur.execute('select config_id from Tester_Configuration where config_id=%s and component_id=%s and role_id=%s' % (c[0], info_dict[bridge_1_id], bridge_1_id))
                config4 = cur.fetchall()
                if config4:
                    cur.execute('select config_id from Tester_Configuration where config_id=%s and component_id=%s and role_id=%s' % (c[0], info_dict[bridge_2_id], bridge_2_id))
                    config5 = cur.fetchall()
                    if config5:
                        print('Begin')
                        print(c[0])
                        print('End')
                        found_config.append(True)
                        break
                    else:
                        found_config.append(False)
                else:
                    found_config.append(False)
            else:
                found_config.append(False)
        else:
            found_config.append(False)
else:
    for k,v in info_dict.items():
        if v:
            cur.execute('insert into Tester_Configuration (config_id, role_id, component_id, teststand_id) values (%s, %s, %s, %s)' % (config_id, k, v, test_stand_id))
    db.commit()
    print('Begin')
    print(config_id)
    print('End')

if True not in found_config:
    for k,v in info_dict.items():
        if v:
            cur.execute('insert into Tester_Configuration (config_id, role_id, component_id, teststand_id) values (%s, %s, %s, %s)' % (config_id, k, v, test_stand_id))
    db.commit()
    print('Begin')
    print(config_id)
    print('End')
    
                                    
base.bottom(False)

