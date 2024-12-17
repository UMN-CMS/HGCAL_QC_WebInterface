#!./cgi_runner.sh

import cgi, html
import cgitb
import base
import module_functions
import sys
import board_status as mp
import bokeh

def run(static):
    base.header(title='Board Status Over Time')
    base.top(static)
    print('''
    <script>
    data = {};
    Bokeh.embed.embed_item(data, 'filter');
    </script>
    <div id='filter' class='bk-root'></div>
    '''.format(mp.Filter()))

    base.bottom(static)

if __name__ == '__main__':
    #cgi header
    cgitb.enable()
    print("Content-type: text/html\n\n")

    run(False)
