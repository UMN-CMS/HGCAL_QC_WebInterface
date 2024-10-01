import json
import sys
from connect import connect
import sys

sys.path.insert(0, '../../hgcal-label-info/label-authority/')
import label_authority as la

cnx = connect(1)
cur = cnx.cursor()

# updates the tables with the most recent data from the dictionary
def update_metatables(majortypes):
   
    cnx = connect(1)
    cur = cnx.cursor()

    print("\nChecking for new major types and subtypes:\n")

    # Make an orphan category for Major and Sub type to house lost labels

    sql = "SELECT major_type_id FROM Major_Type WHERE name='ORPHAN'"
    cur.execute(sql)

    try:
        cur.fetchall()[0][0]
    except:
        print("Adding ORPHAN major type identified by major_sn={} and major_code={}".format(99, "XX"))
        sql = "INSERT INTO Major_Type (name, major_sn, major_code) VALUES (%s, %s, %s)"
        val = ("ORPHAN", "99", "XX")

        cur.execute(sql, val)

        cnx.commit()
   
    sql = "SELECT sub_type_id FROM Sub_Type WHERE name='ORPHAN'"
    cur.execute(sql)

    try:
        cur.fetchall()[0][0]
    except:
        print("Adding ORPHAN sub type identified by sub_sn={} and sub_code={}".format(9999, "XXXX"))
        sql = "INSERT INTO Sub_Type (name, sub_sn, sub_code, digits, identifier_name) VALUES (%s, %s, %s, %s, %s)"
        val = ("ORPHAN", "9999", "XXXX", "4", "ORPHAN")

        cur.execute(sql, val)
   
        cnx.commit()
     

    for key in majortypes:
    
        major_code = majortypes[key]["major_code"]
        major_sn = str(majortypes[key]["major_sn"]) if len(str(majortypes[key]["major_sn"])) == 2 else "0" + str(majortypes[key]["major_sn"])
        name = key
        if major_code == '': continue

        cur = cnx.cursor()

        sql = "SELECT major_type_id FROM Major_Type WHERE major_sn = %s"
        val = (major_sn,)

        cur.execute(sql, val)
       
        try:
            results = cur.fetchall()
            maj_id = results[0][0]
        except:
            print("No row present for {}, will add into Major_Type table".format(name))
            sql = "INSERT INTO Major_Type (name, major_sn, major_code) VALUES (%s, %s, %s)"
            val = (name, major_sn, major_code)

            cur.execute(sql, val)
            cnx.commit()

            print(cur.rowcount, "record inserted into Major_Type with name {}".format(name))

        if majortypes[key]["subtypes"] == None:
            print("No subtype associated with {}".format(key))
            continue

        for sub_key, info in majortypes[key]["subtypes"].items():
 
            if "name" not in info.keys():
                name = sub_key
                identifier = sub_key
            else:
                name = info["name"]
                identifier = sub_key

            sub_code = info["sub_code"]
            sub_sn = info["sub_sn"]
            digits = len(sub_code)

            sql = "SELECT sub_type_id FROM Sub_Type WHERE sub_sn = %s and sub_code = %s"
            val = (sub_sn, sub_code)

            cur.execute(sql, val)
        
            try:
                results = cur.fetchall()
                sub_id = results[0][0]
                #print("Row present for {}, skipping insert".format(name))
            except:
                print("No row present for {}, will add into Sub_Type table".format(name))
                sql = "INSERT INTO Sub_Type (name, sub_sn, sub_code, identifier_name, digits) VALUES (%s, %s, %s, %s, %s)"
                val = (name, sub_sn, sub_code, identifier, digits)

                cur.execute(sql, val)
                cnx.commit()

                print(cur.rowcount, "record inserted into Sub_Type with name {}".format(name))

            sql = "SELECT major_type_id FROM Major_Type WHERE major_sn = %s"
            val = (major_sn,)

            cur.execute(sql, val)
            maj_id = cur.fetchall()[0][0]

            sql = 'SELECT sub_type_id FROM Sub_Type WHERE sub_code = %s and sub_sn = %s'
            val = (sub_code, sub_sn)

            cur.execute(sql, val)
            sub_ids = cur.fetchall()

            for sub in sub_ids:
                sub_id = sub[0]

                sql = "SELECT * from Major_Sub_Stitch WHERE major_type_id = %s and sub_type_id = %s"
                val = (maj_id, sub_id)

                cur.execute(sql, val)

                try:
                    val = cur.fetchall()[0][0]
                    #print("Entry present in stitch table ({},{}), skipping insert".format(maj_id, sub_id))
                    continue
                except:

                    sql = "INSERT INTO Major_Sub_Stitch (major_type_id, sub_type_id) VALUES (%s, %s)"
                    val = (maj_id, sub_id)

                    cur.execute(sql, val)
                    cnx.commit()

#uploads the label to the database
def upload_label(label):

    try:
        decoded = la.decode(label)
        major = la.getMajorType(decoded.major_type_code)
        sub = major.getSubtypeByCode(decoded.subtype_code)
        sn_fv = decoded.field_values['SerialNumber']

        type_code = str(decoded.major_type_code) + str(decoded.subtype_code)
        sn = sn_fv.value
    except: 
        print(f"Unable to decode label f{label}, will insert with blank type code and sn")
        type_code = "XXXXXX"
        sn = "XXXXXX"

    # uploads the label into the database
    query = "INSERT INTO Label (full_label, type_sn, type_code, sn, creation_date) VALUES (%s, %s, %s, %s, NOW())"
    args = (label, "000000", type_code, sn)

    try:
        cur.execute(query, args)
        cnx.commit()
        print('Begin')
        for i in args:
            print(i)
        print('End')
    except Exception as e:
        print(e)
        print("Issue uploading label with sn={}, please check for duplicates.".format(label))

# this uses the label authority over the database
def decode_label(label):
    print("LABEL:", label) 
    decoded = la.decode(label)
    major = la.getMajorType(decoded.major_type_code)
    sub = major.getSubtypeByCode(decoded.subtype_code)
    sn = decoded.field_values['SerialNumber']
    
    return [major.name, sub.name, sn.value, major.code, sub.code]
