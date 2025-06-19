#!/usr/bin/python3

#
# This script handles all requests related to components
#


import cgi, html
import base
from connect import connect
import settings
import os.path
import sys
import json
import cgitb
import mysql.connector

#cgitb.enable()
#print("Content-Type: text/html\n")

def add_component(cnx,cur,barcode,typecode):
    try:
        cur.execute('INSERT INTO COMPONENT_STOCK (barcode, typecode) VALUES (?,?)',(barcode,typecode,))
        cnx.commit()
        return (200,"Ok",)
    except mysql.connector.Error as e:
        return (400,f"Error on add_component: {e}")    

def get_used_for(cur,barcode):
    retval={}
    try:
        cur.execute("SELECT barcode,typecode from COMPONENT_STOCK JOIN COMPONENT_USAGE WHERE COMPONENT_STOCK.component_id=COMPONENT_USAGE.component_id AND COMPONENT_USAGE.used_in_barcode LIKE ?",(barcode,))        
        for (barcode,typecode) in cur:
            if typecode not in retval:
                retval[typecode]=[]
            retval[typecode].append(barcode)
        return (200,retval,)
    except mysql.connector.Error as e:
        return (400,f"Error on get_used_for: {e}")

def get_unused_stock(cur,typecode,quantity=1):
    try:
        retval=[]
        if typecode is None:
            cur.execute("SELECT typecode,barcode FROM COMPONENT_STOCK WHERE component_id NOT IN (SELECT component_id from COMPONENT_USAGE) ORDER BY entered, barcode LIMIT %d"%quantity)
            for (typecode,barcode) in cur:
                retval.append((typecode,barcode))
        else:
            cur.execute("SELECT barcode FROM COMPONENT_STOCK WHERE typecode=? AND component_id NOT IN (SELECT component_id from COMPONENT_USAGE) ORDER BY entered,barcode LIMIT ?",(typecode,quantity))
            for (barcode) in cur:
                retval.append(barcode)
        return (200,retval,)    
    except mysql.connector.Error as e:
        return (400,f"Error on get_unused_stock: {e}")

def mark_used(ctx,cur,barcode,tomake):
    try:
        cur.execute("SELECT component_id FROM COMPONENT_STOCK WHERE barcode=?",(barcode,))
        row=cur.fetchone()
        if row is None:
            return (404,"Barcode '%s' not found in stock"%(barcode));
        cid=int(row[0])
        
        if tomake is not None and len(tomake)>10:
            cur.execute("INSERT INTO COMPONENT_USAGE (component_id, used_in_barcode) VALUES (?,?)",(cid,tomake,))
        else:
            cur.execute("INSERT INTO COMPONENT_USAGE (component_id) VALUES (?)",(cid,))
        ctx.commit()
    except mysql.connector.Error as e:
        if e.errno == 1062:
            return (409,"Barcode %s already used to make something else"%(barcode))
        else:
            return (400,f"Error on mark_used: {e}")
    return (200,"Ok")
    
def argas(args,name,notprovided=None):
    if name in args:
        return args[name]
    return notprovided

args={}
if "REQUEST_METHOD" in os.environ:
    form = cgi.FieldStorage()
    for key in form.keys():
        args[key]=form[key].value
else:
    import argparse
    parser = argparse.ArgumentParser(description="Components")
    parser.add_argument("-r", "--req", type=str, default=None, choices=['get_unused_stock','get_used_for','add_component','mark_used'],help="Request type")
    parser.add_argument("-b", "--barcode", type=str, default=None, help="Barcode")
    parser.add_argument("-m", "--tomake", type=str, default=None, help="To make barcode")
    parser.add_argument("-t", "--typecode", type=str, default=None, help="Typecode")
    parser.add_argument("-q", "--quantity", type=int, default=None, help="Quantity requested")
    a = parser.parse_args()
    for (key,value) in vars(a).items():
        args[key]=value
    print(args)
    
#default behavior
if 'req' not in args:
    args['req']="get_unused_stock"
    args['quantity']=20

req=args['req']
result=(404,"Unknown")

if req in ["get_unused_stock","get_used_for"]:
    db=connect(0)
    cur=db.cursor(prepared=True)
    if req == "get_unused_stock": result=get_unused_stock(cur,argas(args,"typecode"),int(argas(args,"quantity",1)))
    if req == "get_used_for": result=get_used_for(cur,argas(args,"barcode"))

if req in ["add_component","mark_used"]:
    db=connect(1)
    cur=db.cursor(prepared=True)
    if req == "add_component":
        result=add_component(db,cur,argas(args,"barcode"),argas(args,"typecode"))
    if req == "mark_used":
        result=mark_used(db,cur,argas(args,"barcode"),argas(args,"tomake"))

if result[0]>299:
    codes={ 404: "Not Found", 400: "Bad Request", 409: "Conflict"}
    print("Status: %d %s"%(result[0],codes[result[0]]))
    print("Content-type: text/plain")
    print("\n")
    print(result[1])
else:
    print("Status: 200 OK\n")
    print("Content-type: text/json")
    print(json.dumps(result[1]))
