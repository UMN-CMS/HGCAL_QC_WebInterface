#!./cgi_runner.sh

import cgi, html
import cgitb
import base
import module_functions
import sys
import zipper_resistance_plots as mp

def run(static):
    base.header(title='Zipper Resistance Data')
    base.top(static)
    # adds the bokeh filter to javascript and to the website layout
    print('''
    <div id='exfilter' class='bk-root'></div>
    <script>
    data = {};
    Bokeh.embed.embed_item(data, 'exfilter');
    </script>
    '''.format(mp.Filter()))

    base.bottom(static)

    
if __name__ == '__main__':
    cgitb.enable()
    #cgi header
    print("Content-type: text/html\n")

    run(False)
        

