from connect import connect, get_base_url
import cgitb; cgitb.enable()
import mysql

import re

def natural_sort(l): 
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    return sorted(l, key=alphanum_key)

# Function for grabbing all types of labels and printing them out as a table
def label_type_table():

    db = connect(0)
    cur = db.cursor()
    
    # Major type query
    query = "SELECT major_type_id, name FROM Major_Type"
    cur.execute(query)
    
    rows = cur.fetchall()
    rows = sorted(rows, key=lambda x: x[1])

    print('''
<div class="container mx-2 my-2">
    <div class="row">
        <div class="col-md-12 pt-4 ps-5 mx-2 my-2">
            <h1>Label Types</h1>
        </div>
    </div>
    <div class="row">
        <div class="col-md-12 pt-3 pb-5 ps-5 pe-5 mx-2 my-2">
        <div class="accordion" id="accordionExample">
''')

    for idx, tup in enumerate(rows):
        maj_id = tup[0]
        name = tup[1]

        query = "select sub_type_id, name from Sub_Type WHERE sub_type_id in (select sub_type_id from Major_Sub_Stitch WHERE major_type_id = %s)"
        args = (maj_id,)
        cur.execute(query, args)

        subs = cur.fetchall()
        #subs = natural_sort(subs)

        print('''
          <div class="accordion-item">
            <h2 class="accordion-header" id="headingOne">
              <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapse{1}" aria-expanded="true" aria-controls="collapseOne">
                {0}
              </button>
            </h2>
            <div id="collapse{1}" class="accordion-collapse collapse" aria-labelledby="headingOne" data-bs-parent="#accordionExample">
              <div class="accordion-body">
                <ul class="list-group">            
        '''.format(name, idx))

        for row in subs:
            sub_id = row[0]
            name = row[1]
            base_url = get_base_url()

            query = "SELECT COUNT(*) FROM Label WHERE sub_type_id=%s AND major_type_id=%s"
            args = (sub_id, maj_id)

            cur.execute(query, args)
            num_labels = cur.fetchall()[0][0]

            print('<li class="list-group-item"><a href="{}labels_subtype.py?major_type_id={}&sub_type_id={}">{}\tNum. Labels: {}</a></li>'.format(base_url, maj_id, sub_id, name, num_labels))

        print('''
                </ul>
              </div>
            </div>
          </div>''')

    print('''      </div>
        </div>
      </div>
    </div>
    ''')
