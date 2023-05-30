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

base.header(title='Bit Error Rate Data')
base.top()
plotheader.plotscript()

print('<div class="row">')
plotheader.plotheader()
print('''
<div>
<table>
<tr>
<td>
    <img src="../../static/files/Bit_Error_Rate_Midpoint.png">
</td>
<td>
    <img src="../../static/files/Bit_Error_Rate_EyeOpening.png"> 
</td>
<td>
<div style="padding-left:5px">
    <table>
        <th> Select Components </th>
        <tr><td style="padding-bottom:3px">
            <input class="form-check-input" type="checkbox" value="">
            <label class="form-check-label">
                Clock 0
            </label>
        </td></tr>
        <tr><td style="padding-bottom:3px">
            <input class="form-check-input" type="checkbox" value="">
            <label class="form-check-label">
                Clock 1
            </label>
        </td></tr>
        <tr><td style="padding-bottom:3px">
            <input class="form-check-input" type="checkbox" value="">
            <label class="form-check-label">
                Clock 2
            </label>
        </td></tr>
        <tr><td style="padding-bottom:3px">
            <input class="form-check-input" type="checkbox" value="">
            <label class="form-check-label">
                Trigger 0
            </label>
        </td></tr>
        <tr><td style="padding-bottom:3px">
            <input class="form-check-input" type="checkbox" value="">
            <label class="form-check-label">
                Trigger 1
            </label>
        </td></tr>
        <tr><td style="padding-bottom:3px">
            <input class="form-check-input" type="checkbox" value="">
            <label class="form-check-label">
                Trigger 2
            </label>
        </td></tr>
        <tr><td style="padding-bottom:3px">
            <input class="form-check-input" type="checkbox" value="">
            <label class="form-check-label">
                Trigger 3
            </label>
        </td></tr>
        <tr><td style="padding-bottom:3px">
            <input class="form-check-input" type="checkbox" value="">
            <label class="form-check-label">
                Trigger 4
            </label>
        </td></tr>
        <tr><td style="padding-bottom:3px">
            <input class="form-check-input" type="checkbox" value="">
            <label class="form-check-label">
                Trigger 5
            </label>
        </td></tr>
        <tr><td style="padding-bottom:3px">
            <input class="form-check-input" type="checkbox" value="">
            <label class="form-check-label">
                Trigger 6
            </label>
        </td></tr>
        <tr><td style="padding-bottom:3px">
            <input class="form-check-input" type="checkbox" value="">
            <label class="form-check-label">
                Trigger 7
            </label>
        </td></tr>
    </table>
</div>
</td>
<td>
<div style="padding-left:5px">
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
</tr>
</table>
</div>
''')
print('</div>')

base.bottom()

    

