#!./cgi_runner.sh

import cgi, html
import cgitb
import base
import module_functions
import sys
import ADC_Plots as mp


def run(static):
    base.header(title='ADC Functionality')
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
    cgitb.enable()
    #cgi header
    print("Content-type: text/html\n")
    
    run(False)
