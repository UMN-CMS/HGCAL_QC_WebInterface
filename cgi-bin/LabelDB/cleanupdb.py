from connect import connect

db = connect(1)
cur = db.cursor()

cur.execute('select full_label from Label where major_type_id=17')
for f in cur.fetchall():
    code = f[0][3:9]
    sn = f[0][9:]
    cur.execute('update Label set type_code="%s" where full_label="%s"' % (code, f[0]))
    cur.execute('update Label set sn="%s" where full_label="%s"' % (sn, f[0]))

db.commit()
    

cur.execute('select sub_type_id from Major_Sub_Stitch where major_type_id=17')
for s in cur.fetchall():
    cur.execute('select sub_code from Sub_Type where sub_type_id=%s' %s[0])
    code = cur.fetchall()[0][0]

    code = 'WE' + code
    cur.execute('update Label set sub_type_id=%(id)s where type_code="%(code)s"' % {'id': s[0], 'code': code})

db.commit()
