#!/usr/bin/python3

import cgi
import base
from connect import connect
import settings
import os.path
import sys

if __name__ == "__main__": 
    form = cgi.FieldStorage()
    attach_id = base.cleanCGInumber(form.getvalue('attach_id'))

    db=connect(0)
    cur=db.cursor()

    if(attach_id != 0):
        cur.execute("SELECT test_id, attachmime, originalname, attach FROM Attachments WHERE attach_id=%d" % (attach_id));

    if not cur.with_rows:
        print("Content-type: text/html\n")
        base.header("Attachment Request Error")
        base.top()
        print('<div class="col-md-6 ps-4 pt-4 mx-2 my-2">')
        print("<h1>Attachment not available</h1>")
        print('</div>')
        base.bottom()
    else:    
        thevals=cur.fetchall()
        f = thevals[0][3]
        attpath=settings.getAttachmentPathFor(thevals[0][0],attach_id)
        if not f:
            print("Content-type: text/html\n")
            base.header("Attachment Request Error")
            base.top()
            print("<h1>Attachment not found</h1>")
            base.bottom()        
        else:
            print('Content-type: %s \n\n' % (thevals[0][1]))
            print(f.decode("utf-8"))
        
    cur.close()

def save(attach_id):
    db=connect(0)
    cur=db.cursor()

    cur.execute("SELECT test_id, attachmime, originalname FROM Attachments WHERE attach_id=%d" % (attach_id));

    if not cur.with_rows:
        print("<h1>Attachment not available</h1>")
    else:    
        thevals=cur.fetchall();
        attpath=settings.getAttachmentPathFor(thevals[0][0],attach_id)
        if not os.path.isfile(attpath):
            print("<h1>Attachment not found</h1>")
        else:
            statinfo = os.stat(attpath)
            sys.stdout.write(file(attpath,"rb").read() )
    cur.close()
