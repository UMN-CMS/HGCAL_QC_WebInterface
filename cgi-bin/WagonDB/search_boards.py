#!./cgi_runner.sh

import cgi, html
import cgitb
import base
import sys
from hold_filter_boardsd import Filter

def run(static):
    base.header(title='Search Boards')
    base.top(static)

    print('''
    <div id='render' class='bk-root'></div>
    <script>
    data = {};
    Bokeh.embed.embed_item(data, 'render');
    </script>
    '''.format(Filter()))

    base.bottom(static)

    
if __name__ == '__main__':
    cgitb.enable()
    #cgi header
    print("Content-type: text/html\n")
    
    run(False)

