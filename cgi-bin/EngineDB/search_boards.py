#!./cgi_runner.sh

import cgi, html
import cgitb
import base
import sys
from filter_boards import Filter

def run(static):
    base.header(title='Search Boards')
    base.top(static)

    print('''
    <div id='exfilter' class='bk-root'></div>
    <script>
    data = {};
    Bokeh.embed.embed_item(data, 'exfilter');
    </script>
    '''.format(Filter()))

    base.bottom(static)

    
if __name__ == '__main__':
    cgitb.enable()
    #cgi header
    print("Content-type: text/html\n")
    
    run(False)

