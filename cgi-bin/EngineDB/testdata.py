#!./cgi_runner.sh

import os
import cgi
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
    <script>
    data = {};
    Bokeh.embed.embed_item(data, 'exfilter');
    </script>
    <div id='exfilter' class='bk-root'></div>
    '''.format(mp.Filter()))

    base.bottom(static)

if __name__ == '__main__':
    #cgi header
    cgitb.enable()
    print("Content-type: text/html\n\n")

    run(False)
