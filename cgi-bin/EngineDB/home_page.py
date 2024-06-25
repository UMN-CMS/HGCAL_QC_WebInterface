#!/usr/bin/python3
import cgi
import cgitb
import base
import home_page_list
import sys

def run(static):
    try:
        base.header(title='Engine Test Home Page')
        base.top(static)

        print('<div class="row">')
        print('<div class="col-md-12 pt-4 ps-5 mx-2 my-2">')
        print('<h2>Count by Test</h2>' )
        print('</div>')
        print('</div>')
        home_page_list.render_list_tests()

        print('<hr>')

        print('<div class="row">')
        print('<div class="col-md-5 pt-2 ps-5 mx-2 my-2">')
        print('<h2>List of All Boards</h2>' )
        print('<b><em>(Sorted by Full ID)</em></b>&emsp;<badge class="badge bg-primary">Successful Tests</badge>')
        print('</div>')
        # this div adds spacing
        print('<div class="col-md-3"></div>')
        print('<div class="col-md-3">')
        print('<br>')
        if static:
            pass
        else:
            print('<a href="add_module.py">')
            print('<button type="button" class="btn btn-dark text-light">Add a New Board</button>')
            print('</a>')
        print('</div>')
        print('</div>')
        print('<br><br>')

        home_page_list.allboards(static)

        base.bottom(static)
    except Exception as e:
        print(e)

if __name__ == '__main__':
    cgitb.enable()
    #cgi header
    print("content-type: text/html\n\n")
    run(False)
