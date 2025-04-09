#!./cgi_runner.sh

import cgi, html
import cgitb
import base
import module_functions
import sys
import ElinkQPlots as mp


def run(static):
    base.header(title='E Link Quality')
    base.top(static)

    form = cgi.FieldStorage()
    elink = form.getvalue('elink')

    # links to the other E Link Quality plots
    # having them all on the same page and using a widget to change which plot is visible
    # was very slow as lots of javascript had to be run and many plots had to be generated
    if static:
        print('''
                  <a class="nav-link dropdown-toggle" href="#" id="navbarDropdownMenuLink" role="button" data-bs-toggle="dropdown" aria-expanded="false">
                    Change E Link
                  </a>
                  <ul class="dropdown-menu" aria-labelledby="navbarDropdownMenuLink">
                  </ul>
        ''')
    else:
        print('''
                  <a class="nav-link dropdown-toggle" href="#" id="navbarDropdownMenuLink" role="button" data-bs-toggle="dropdown" aria-expanded="false">
                    Change E Link
                  </a>
                  <ul class="dropdown-menu" aria-labelledby="navbarDropdownMenuLink">
        ''')
        for i in range(42):
            print('<li><a class="dropdown-item" href="ELinkQualityData.py?elink=%s">%s</a></li>' % (str(i), str(i)))
        print('</ul>')
    print('''
    <div id='exfilter' class='bk-root'></div>
    <script>
    data = {};
    Bokeh.embed.embed_item(data, 'exfilter');
    </script>
    '''.format(mp.ELinkFilter(str(elink))))

    base.bottom(static)

    
if __name__ == '__main__':
    cgitb.enable()
    #cgi header
    print("Content-type: text/html\n")
    
    run(False)

