#!./cgi_runner.sh

import cgi, html
import cgitb
import base
import module_functions
import sys
import i2cPlots as mp
             
cgitb.enable()
#cgi header
print("Content-type: text/html\n")

base.header(title='I2C Read/Write Data')
base.top()
# adds the bokeh filter to javascript and to the website layout
print('''
<div id='exfilter' class='bk-root'></div>
<script>
data = {};
Bokeh.embed.embed_item(data, 'exfilter');
</script>
'''.format(mp.Filter()))

base.bottom()

