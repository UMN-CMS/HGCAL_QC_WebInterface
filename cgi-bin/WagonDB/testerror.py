#!/usr/bin/python3

import cgi
import cgitb
import base
import sys
import makePlots as mp
import plotheader

cgitb.enable()

if len(sys.argv) != 1:
    sys.stdout = open('%(loc)s/summary.html' %{'loc':sys.argv[1]}, 'w')

else:
    #cgi header
    print("Content-type: text/html\n")

base.header(title='Total Tests Over Time')
base.top()

plotheader.plotheader()

print('''
<script>
data = {};
Bokeh.embed.embed_item(data, 'exfilter');
</script>
<div id='exfilter' class='bk-root'></div>
'''.format(mp.ResistanceFilter()))

base.bottom()
