#!/usr/bin/python3 -B
from connect import connect
import sys
import os
import pandas as pd
import numpy as np
import datetime
from datetime import datetime as dt

sys.path.insert(0, '../../hgcal-label-info/label-authority/')
import label_authority as la

db = connect(1)
cur = db.cursor()

hd_wagon = la.getMajorType('WH')
subtypes = hd_wagon.getAllSubtypes()

for s in subtypes:
    sub = hd_wagon.getSubtypeByCode(s)

    code = 'WH' + sub.code
    cur.execute('insert into Board_type (name, type_sn) values ("%s", "%s")' % (sub.name, code))
    db.commit()

    cur.execute('select type_id from Board_type where type_sn="%s"' % code)
    type_id = cur.fetchall()[0][0]
    cur.execute('insert into Type_test_stitch (type_id, test_type_id) values (%s, %s)' % (type_id, 0))
    cur.execute('insert into Type_test_stitch (type_id, test_type_id) values (%s, %s)' % (type_id, 4))

    db.commit()
