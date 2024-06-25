import mysql 

from connect import connect

# gets all of the printed labels for a specific major type and subtype
def get_labels(major_type=None, sub_type=None):

    db = connect(0)
    cur = db.cursor()

    if major_type != None and sub_type != None:
        
        if type(sub_type) == list:
            query = 'select full_label from Label where major_type_id=%s AND (' % major_type
            for s in sub_type:
                query += 'sub_type_id=%s' % s
                if s is not sub_type[-1]:
                    query += ' or '
                else:
                    query += ')'
            
            cur.execute(query)
            labels = cur.fetchall()

        else:
            query = "SELECT full_label FROM Label WHERE major_type_id=%s AND sub_type_id=%s order by full_label"
            args = (major_type, sub_type)

            cur.execute(query, args)
            labels = cur.fetchall()

        return labels

    elif sub_type != None:

        query = "SELECT full_label FROM Label WHERE major_type_id=%s order by full_label"
        args = (major_type,)

        cur.execute(query, args)
        labels = cur.fetchall()

        return labels

    else:
        print("Need to specify either major type or major type and subtype, not just subtype.")
