#!/usr/bin/python3

import cgi
import cgitb
import base
import module_functions
import sys
import ADC_Plots as mp

cgitb.enable()

if len(sys.argv) != 1:
    sys.stdout = open('%(loc)s/summary.html' %{'loc':sys.argv[1]}, 'w')

else:
    #cgi header
    print("Content-type: text/html\n")

base.header(title='ADC Functionality')
base.top()

print('''
<script>
data = {};
Bokeh.embed.embed_item(data, 'exfilter');
</script>
<div id='exfilter' class='bk-root'></div>
'''.format(mp.ADC_Filter()))

base.bottom()

    

