#!/usr/bin/python3

import cgi
import cgitb
import base
from connect import connect

db = connect(1)
cur = db.cursor()

#cgi header
print("Content-type: text/html\n")

cgitb.enable()

base.header(title='Add information about the tester equipment')
base.top(False)

form = cgi.FieldStorage()

zcu = form.getvalue('ZCU')
try:
    east_interposer = form.getvalue('east_interposer')
    west_interposer = form.getvalue('west_interposer')
except:
    east_interposer = None
    west_interposer = None

try:
    hd_interposer = form.getvalue('hd_interposer')
except:
    hd_interposer = None

test_stand = form.getvalue('test_stand')

cur.execute('select role_id from Tester_Roles where description="ZCU"')
zcu_id = cur.fetchall()[0][0]

cur.execute('select role_id from Tester_Roles where description="East Interposer"')
east_int_id = cur.fetchall()[0][0]

cur.execute('select role_id from Tester_Roles where description="West Interposer"')
west_int_id = cur.fetchall()[0][0]

cur.execute('select role_id from Tester_Roles where description="HD Interposer"')
hd_int_id = cur.fetchall()[0][0]

cur.execute('select role_id from Tester_Roles where description="DAQ 1 VTRX"')
vtrx1_id = cur.fetchall()[0][0]

cur.execute('select role_id from Tester_Roles where description="DAQ 2 VTRX"')
vtrx2_id = cur.fetchall()[0][0]

cur.execute('select teststand_id from Teststand where name="%s"' % test_stand)
test_stand_id = cur.fetchall()
if test_stand_id:
    test_stand_id = test_stand_id[0][0]
else:
    cur.execute('insert into Teststand (name) values ("%s")' % test_stand)
    db.commit()
    cur.execute('select teststand_id from Teststand where name="%s"' % test_stand)
    test_stand_id = cur.fetchall()[0][0]

cur.execute('select role_id from Tester_Roles where description="Test Bridge 1"')
bridge_1_id = cur.fetchall()[0][0]

cur.execute('select role_id from Tester_Roles where description="Test Bridge 2"')
bridge_2_id = cur.fetchall()[0][0]

bridge_1 = form.getvalue('bridge_1')

bridge_2 = form.getvalue('bridge_2')

vtrx_1 = form.getvalue('vtrx_1')
vtrx_2 = form.getvalue('vtrx_2')

info_dict = {zcu_id: zcu,
            east_int_id: east_interposer,
            west_int_id: west_interposer,
            hd_int_id: hd_interposer,
            vtrx1_id: vtrx_1,
            vtrx2_id: vtrx_2,
            bridge_1_id: bridge_1,
            bridge_2_id: bridge_2,
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

found_config = []

cur.execute('select config_id from Tester_Configuration where component_id=%s and teststand_id=%s' % (info_dict[zcu_id], test_stand_id))
config1 = cur.fetchall()
if config1:
    for c in config1:
        cur.execute('select config_id from Tester_Configuration where config_id=%s and component_id=%s and role_id=%s' % (c[0], info_dict[bridge_1_id], bridge_1_id))
        config2 = cur.fetchall()
        if config2:
            cur.execute('select config_id from Tester_Configuration where config_id=%s and component_id=%s and role_id=%s' % (c[0], info_dict[bridge_2_id], bridge_2_id)) 
            config3 = cur.fetchall()
            if config3:
                if vtrx_1:
                    cur.execute('select config_id from Tester_Configuration where config_id=%s and component_id=%s and role_id=%s' % (c[0], info_dict[vtrx1_id], vtrx1_id))
                    config4 = cur.fetchall()
                    if config4:
                        if vtrx_2:
                            cur.execute('select config_id from Tester_Configuration where config_id=%s and component_id=%s and role_id=%s' % (c[0], info_dict[vtrx2_id], vtrx2_id))
                            config5 = cur.fetchall()
                            if config5:
                                if hd_interposer:
                                    cur.execute('select config_id from Tester_Configuration where config_id=%s and component_id=%s' % (c[0], info_dict[hd_int_id]))
                                    config6 = cur.fetchall()
                                    if config6:
                                        print('Begin')
                                        print(c[0])
                                        print('End')
                                        found_config.append(True)
                                        break
                                    else:
                                        found_config.append(False)
                                else:
                                    cur.execute('select config_id from Tester_Configuration where config_id=%s and component_id=%s' % (c[0], info_dict[east_int_id]))
                                    config6 = cur.fetchall()
                                    if config6:
                                        cur.execute('select config_id from Tester_Configuration where config_id=%s and component_id=%s' % (c[0], info_dict[west_int_id]))
                                        config7 = cur.fetchall()
                                        if config7:
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
                            if hd_interposer:
                                cur.execute('select config_id from Tester_Configuration where config_id=%s and component_id=%s' % (c[0], info_dict[hd_int_id]))
                                config6 = cur.fetchall()
                                if config6:
                                    print('Begin')
                                    print(c[0])
                                    print('End')
                                    found_config.append(True)
                                    break
                                else:
                                    found_config.append(False)
                            else:
                                cur.execute('select config_id from Tester_Configuration where config_id=%s and component_id=%s' % (c[0], info_dict[east_int_id]))
                                config6 = cur.fetchall()
                                if config6:
                                    cur.execute('select config_id from Tester_Configuration where config_id=%s and component_id=%s' % (c[0], info_dict[west_int_id]))
                                    config7 = cur.fetchall()
                                    if config7:
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
                    if vtrx_2:
                        cur.execute('select config_id from Tester_Configuration where config_id=%s and component_id=%s and role_id=%s' % (c[0], info_dict[vtrx2_id], vtrx2_id))
                        config5 = cur.fetchall()
                        if config5:
                            if hd_interposer:
                                cur.execute('select config_id from Tester_Configuration where config_id=%s and component_id=%s' % (c[0], info_dict[hd_int_id]))
                                config6 = cur.fetchall()
                                if config6:
                                    print('Begin')
                                    print(c[0])
                                    print('End')
                                    found_config.append(True)
                                    break
                                else:
                                    found_config.append(False)
                            else:
                                cur.execute('select config_id from Tester_Configuration where config_id=%s and component_id=%s' % (c[0], info_dict[east_int_id]))
                                config6 = cur.fetchall()
                                if config6:
                                    cur.execute('select config_id from Tester_Configuration where config_id=%s and component_id=%s' % (c[0], info_dict[west_int_id]))
                                    config7 = cur.fetchall()
                                    if config7:
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
                        if hd_interposer:
                            cur.execute('select config_id from Tester_Configuration where config_id=%s and component_id=%s' % (c[0], info_dict[hd_int_id]))
                            config6 = cur.fetchall()
                            if config6:
                                print('Begin')
                                print(c[0])
                                print('End')
                                found_config.append(True)
                                break
                            else:
                                found_config.append(False)
                        else:
                            cur.execute('select config_id from Tester_Configuration where config_id=%s and component_id=%s' % (c[0], info_dict[east_int_id]))
                            config6 = cur.fetchall()
                            if config6:
                                cur.execute('select config_id from Tester_Configuration where config_id=%s and component_id=%s' % (c[0], info_dict[west_int_id]))
                                config7 = cur.fetchall()
                                if config7:
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

