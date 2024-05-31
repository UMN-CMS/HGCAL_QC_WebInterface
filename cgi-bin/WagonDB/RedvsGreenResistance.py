#!/usr/bin/python3

import cgi
import cgitb
import base
import module_functions
import sys
import red_vs_green_resistance as mp

def run(static):
    base.header(title='Red vs Green Resistance')
    base.top(static)
    # adds the bokeh filter to javascript and to the website layout
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
    print("Content-type: text/html\n")

    run(False)

