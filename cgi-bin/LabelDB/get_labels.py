import mysql 

from connect import connect

def get_labels(major_type=None, sub_type=None):

    db = connect(0)
    cur = db.cursor()

    if major_type != None and sub_type != None:
        
        query = "SELECT full_label FROM Label WHERE major_type_id=%s AND sub_type_id=%s"
        args = (major_type, sub_type)

        cur.execute(query, args)
        labels = cur.fetchall()

        return labels

    elif sub_type != None:

        query = "SELECT full_label FROM Label WHERE major_type_id=%s"
        args = (major_type,)

        cur.execute(query, args)
        labels = cur.fetchall()

        return labels

    else:
        print("Need to specify either major type or major type and subtype, not just subtype.")
