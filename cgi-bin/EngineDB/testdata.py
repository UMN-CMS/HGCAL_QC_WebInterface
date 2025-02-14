#!./cgi_runner.sh

import cgi, html
import cgitb
import base
import module_functions
import sys
import total_tests as mp
import bokeh

def run(static):
    base.header(title='Total Tests Over Time')
    base.top(static)
    print('''
    <div id='exfilter' class='bk-root'></div>
    <script>
    data = {};
    Bokeh.embed.embed_item(data, 'exfilter');
    </script>
    '''.format(mp.Filter()))

    base.bottom(static)

if __name__ == '__main__':
    #cgi header
    cgitb.enable()
    print("Content-type: text/html\n\n")

    run(False)
