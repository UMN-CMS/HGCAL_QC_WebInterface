#!/usr/bin/python3

import cgi
import cgitb
import base
import module_functions
import sys
import plotheader
#import makePlots as mp
#makePlot arugments:(Test, Data, Board, SN, BitError, Tester)

cgitb.enable()

if len(sys.argv) != 1:
    sys.stdout = open('%(loc)s/summary.html' %{'loc':sys.argv[1]}, 'w')

else:
    #cgi header
    print("Content-type: text/html\n")

base.header(title='I2C Read/Write Data')
base.top()
plotheader.plotscript()

print('<div class="row">')
plotheader.plotheader()
print('''
<div>
<div style="float:left; padding-right:10px;">
    <img src="../../static/files/I2C_ReadWrite.png?ver=1.0">
</div>
<div>
<div style="float:leftt; padding-top:5px;">
<table>
    <th> Select Module </th>
    <tr><td style="padding-bottom:3px">
        <input class="form-check-input" type="checkbox" value="" checked=True>
        <label class="form-check-label">
            Module 1
        </label>
    </td></tr>
    <tr><td style="padding-bottom:3px">
        <input class="form-check-input" type="checkbox" value="" checked=True>
        <label class="form-check-label">
            Module 2
        </label>
    </td></tr>
</table>
</div>
</div>
<div>
<table>
    <th> Select Outcome </th>
    <tr><td style="padding-bottom:3px">
        <input class="form-check-input" type="checkbox" value="" checked=True>
        <label class="form-check-label">
            Successful
        </label>
    </td></tr>
    <tr><td style="padding-bottom:3px">
        <input class="form-check-input" type="checkbox" value="" checked=True>
        <label class="form-check-label">
            Unsuccessful
        </label>
    </td></tr>
</table>
</div>
''')
print('</div>')

base.bottom()

    

