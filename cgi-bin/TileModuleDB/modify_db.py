#!./cgi_runner.sh
import cgi, html
import cgitb
import base
import sys
sys.path.insert(0, '../../hgcal-label-info/label-authority/')
import label_authority as la

from connect import connect

db = connect(1)
cur = db.cursor()

TB = la.getMajorType("TB")

for s in TB.getAllSubtypes():
    name = TB.getSubtypeByCode(s).name
    code = "TB" + s
    cur.execute("insert into Board_type (type_sn, name) values ('%s', '%s')" % (code, name))
    db.commit()

    cur.execute("select type_id from Board_type where type_sn='%s'" % code)
    type_id = cur.fetchall()[0][0]

    cur.execute("insert into Type_test_stitch (type_id, test_type_id) values (%s, 2)" % type_id)
    db.commit()

