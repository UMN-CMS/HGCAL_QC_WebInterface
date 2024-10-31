#!./cgi_runner.sh

import cgi, html
import cgitb
import base
import module_functions
import sys
import bit_error_ratePlots as mp

def run(static):
    base.header(title='Bit Error Rate Data')
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
    cgitb.enable()
    #cgi header
    print("Content-type: text/html\n")
    run(False)

