#!./cgi_runner.sh
import cgi, html
import cgitb
import base
import home_page_list
import sys

cgitb.enable()
#cgi header
print("content-type: text/html\n\n")

try:
    base.header(title='Engine Test Home Page')
    base.top(admin=True)

    print('<div class="row">')
    print('<div class="col-md-12 pt-4 ps-5 mx-2 my-2">')
    print('<h2>Count by Test</h2>' )
    print('</div>')
    print('</div>')
    home_page_list.render_list_tests()

    # the following is obsolete

    #print('<hr>')

    #print('<div class="row">')
    #print('<div class="col-md-5 pt-2 ps-5 mx-2 my-2">')
    #print('<h2>List of all LD Engines</h2>' )
    #print('<b><em>(Sorted by Full ID)</em></b>&emsp;<badge class="badge bg-success">Successful Tests</badge>')
    #print('</div>')
    ## this div adds spacing
    #print('<div class="col-md-3"></div>')
    #print('<div class="col-md-3">')
    #print('<br>')
    #print('<a href="add_module.py">')
    #print('<button type="button" class="btn btn-dark text-light">Add a New Board</button>')
    #print('</a>')
    #print('</div>')
    #print('</div>')
    #print('<br><br>')

    #home_page_list.allboards(static, 'EL')

    #print('<div class="row">')
    #print('<div class="col-md-5 pt-2 ps-5 mx-2 my-2">')
    #print('<h2>List of all HD Engines</h2>' )
    #print('<b><em>(Sorted by Full ID)</em></b>&emsp;<badge class="badge bg-success">Successful Tests</badge>')
    #print('</div>')
    ## this div adds spacing
    #print('<div class="col-md-3"></div>')
    #print('<div class="col-md-3">')
    #print('<br>')
    #print('<a href="add_module.py">')
    #print('<button type="button" class="btn btn-dark text-light">Add a New Board</button>')
    #print('</a>')
    #print('</div>')
    #print('</div>')
    #print('<br><br>')

    #home_page_list.allboards(static, 'EH')

    base.bottom()
except Exception as e:
    raise
    print(e)
