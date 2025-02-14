#!./cgi_runner.sh

import module_functions
import cgi, html
import base

#print("Location: %s/home_page.py\n\n" % base_url)
#cgi header
print("Content-type: text/html\n")

form = cgi.FieldStorage()
full_id = html.escape(form.getvalue("full_id"))
fileitems = [form['top_view'], form['bottom_view']]

base.header(title='Add Image')
base.top(False)

#takes the image from the add_board_image page and sends it to module functions
for idx,item in enumerate(fileitems):
    if idx == 0:
        view = 'Top'
    if idx == 1:
        view = 'Bottom'
    try:
        module_functions.add_board_image(str(full_id), item, view)
    except Exception as e:
        print("Issue uploading")
        print(e)

base.bottom(False)

