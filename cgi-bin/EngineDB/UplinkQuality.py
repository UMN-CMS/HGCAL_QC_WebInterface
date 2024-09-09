#!/usr/bin/python3

import cgi, html
import cgitb
import base
import module_functions
import sys
import UplinkPlots as mp

def run(static):
    base.header(title='Uplink Quality')
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
    cgitb.enable()
    #cgi header
    print("Content-type: text/html\n")
    
    run(False)
    

