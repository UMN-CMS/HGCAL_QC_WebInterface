#!/usr/bin/python3

import cgi
import cgitb
import base
import module_functions
import sys
import plotheader
#import makePlots as mp
#makePlot arguments:(Test, Data, Board, SN, BitError, Tester)

cgitb.enable()

if len(sys.argv) != 1:
    sys.stdout = open('%(loc)s/summary.html' %{'loc':sys.argv[1]}, 'w')

else:
    #cgi header
    print("Content-type: text/html\n")

base.header(title='Resistance Measurement Data')
base.top()
plotheader.plotscript()

print('<div class="row">')
plotheader.plotheader()
print('''
<div>
<div style="float:left; padding-right:10px">
    <img src="../../static/files/Resistance_Measurement.png?ver=1.2">
</div>
<div>
<div style="float:left; padding-top:5px;">
<table>
    <th> Select Pathway </th>
    <tr><td style="padding-bottom:3px">
        <input class="form-check-input" type="checkbox" value="">
        <label class="form-check-label">
            RTD -> VMON_LVS Module 1
        </label>
    </td></tr>
    <tr><td style="padding-bottom:3px">
        <input class="form-check-input" type="checkbox" value="">
        <label class="form-check-label">
            RTD -> VMON_LVS Module 2
        </label>
    </td></tr>
    <tr><td style="padding-bottom:3px">
        <input class="form-check-input" type="checkbox" value="">
        <label class="form-check-label">
            ECON_RE_Sb -> HGCROC_RE_Sb Module 1
        </label>
    </td></tr>
    <tr><td style="padding-bottom:3px">
        <input class="form-check-input" type="checkbox" value="">
        <label class="form-check-label">
            ECON_RE_Sb -> HGCROC_RE_Sb Module 2
        </label>
    </td></tr>
    <tr><td style="padding-bottom:3px">
        <input class="form-check-input" type="checkbox" value="">
        <label class="form-check-label">
            PWR_EN -> PG_LDO Module 1
        </label>
    </td></tr>
    <tr><td style="padding-bottom:3px">
        <input class="form-check-input" type="checkbox" value="">
        <label class="form-check-label">
            PWR_EN -> PG_LDO Module 2
        </label>
    </td></tr>
    <tr><td style="padding-bottom:3px">
        <input class="form-check-input" type="checkbox" value="">
        <label class="form-check-label">
            RTD -> HGCROC_RE_Sb Module 1
        </label>
    </td></tr>
    <tr><td style="padding-bottom:3px">
        <input class="form-check-input" type="checkbox" value="">
        <label class="form-check-label">
            RTD -> HGCROC_RE_Sb Module 2
        </label>
    </td></tr>
    <tr><td style="padding-bottom:3px">
        <input class="form-check-input" type="checkbox" value="">
        <label class="form-check-label">
            HGCROC_RE_Hb -> HGCROC_RE_Sb Module 1
        </label>
    </td></tr>
    <tr><td style="padding-bottom:3px">
        <input class="form-check-input" type="checkbox" value="">
        <label class="form-check-label">
            HGCROC_RE_Hb -> HGCROC_RE_Sb Module 2
        </label>
    </td></tr>
    <tr><td style="padding-bottom:3px">
        <input class="form-check-input" type="checkbox" value="">
        <label class="form-check-label">
            PG_DCDC -> HGCROC_RE_Sb Module 1
        </label>
    </td></tr>
    <tr><td style="padding-bottom:3px">
        <input class="form-check-input" type="checkbox" value="">
        <label class="form-check-label">
            PG_DCDC -> HGCROC_RE_Sb Module 2
        </label>
    </td></tr>
</table>
</div>
<div>
<table>
    <th style="float:leftt; padding-top:5px"> Select Outcome </th>
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
</div>
</div>

''')

print('</div>')

base.bottom()

    

