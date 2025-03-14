#!./cgi_runner.sh

import cgi, html
import cgitb
import base
import module_functions
import sys
import EClockPlots as mp

def run(static):
    base.header(title='E Clock Rates')
    base.top(static)

    print('''
    <div class="row">
    <div class="col-md-12 pt-4 ps-5 mx-2 my-2">
    <h5> These rates are relative to 320640000 Hz </h5>
    </div>
    </div>
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
    
    

