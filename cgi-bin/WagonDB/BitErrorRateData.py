#!/usr/bin/python3

import cgi
import cgitb
import base
import module_functions
import sys
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

print('<div class="row">')
print('''
<div>       
    <button class="btn btn-secondary dropdown-toggle" type="button" id="SelectTest" data-bs-toggle="dropdown" aria-expanded="false">
        Test
    </button>
    <ul class="dropdown-menu" aria-labelledby="SelectTest">
        <li><a class="dropdown-item" href="#">Resistance Measurement</a></li>
        <li><a class="dropdown-item" href="#">ID Resistor</a></li>
        <li><a class="dropdown-item" href="#">I2C Read/Write</a></li>
        <li><a class="dropdown-item" href="#">Bit Error Rate</a></li>
    </ul>

    <button class="multiselect dropdown-toggle btn btn-secondary" type="button" id="SelectBoards" data-bs-toggle="dropdown" aria-expanded="false">
        <span class="multiselect-selected-text">
            Select Board
        </span>
    </button>
    <ul class="dropdown-menu" aria-labelledby="SelectBoards">
        <li><a class="dropdown-item" href="#">WW20A1</a></li>
        <li><a class="dropdown-item" href="#">WW10A1</a></li>
        <li><a class="dropdown-item" href="#">WE10A1</a></li>
        <li><a class="dropdown-item" href="#">WE20B1</a></li>
    </ul>
    <button class="btn btn-secondary dropdown-toggle" type="button" id="SelectTest" data-bs-toggle="dropdown" aria-expanded="false">
        Tester
    </button>
    <ul class="dropdown-menu" aria-labelledby="SelectTester">
        <li><a class="dropdown-item" href="#">Rand</a></li>
        <li><a class="dropdown-item" href="#">Bryan</a></li>
    </ul>
</div>
''')
print('''
<div>
    <img src="../../static/files/Bit_Error_Rate_Midpoint.png">
</div>
<div>
    <img src="../../static/files/Bit_Error_Rate_EyeOpening.png"> 
</div>
<div>
<div style="float:left">
<table>
    <tr><td>
        <input class="form-check-input" type="checkbox" value="">
        <label class="form-check-label">
            Clock 0
        </label>
    </td></tr>
    <tr><td>
        <input class="form-check-input" type="checkbox" value="">
        <label class="form-check-label">
            Clock 1
        </label>
    </td></tr>
    <tr><td>
        <input class="form-check-input" type="checkbox" value="">
        <label class="form-check-label">
            Clock 2
        </label>
    </td></tr>
    <tr><td>
        <input class="form-check-input" type="checkbox" value="">
        <label class="form-check-label">
            Trigger 0
        </label>
    </td></tr>
    <tr><td>
        <input class="form-check-input" type="checkbox" value="">
        <label class="form-check-label">
            Trigger 1
        </label>
    </td></tr>
    <tr><td>
        <input class="form-check-input" type="checkbox" value="">
        <label class="form-check-label">
            Trigger 2
        </label>
    </td></tr>
    <tr><td>
        <input class="form-check-input" type="checkbox" value="">
        <label class="form-check-label">
            Trigger 3
        </label>
    </td></tr>
    <tr><td>
        <input class="form-check-input" type="checkbox" value="">
        <label class="form-check-label">
            Trigger 4
        </label>
    </td></tr>
    <tr><td>
        <input class="form-check-input" type="checkbox" value="">
        <label class="form-check-label">
            Trigger 5
        </label>
    </td></tr>
    <tr><td>
        <input class="form-check-input" type="checkbox" value="">
        <label class="form-check-label">
            Trigger 6
        </label>
    </td></tr>
    <tr><td>
        <input class="form-check-input" type="checkbox" value="">
        <label class="form-check-label">
            Trigger 7
        </label>
    </td></tr>
</table>
</div>
<div style="float:leftt">
    <button> Update Plot </button>
</div>
</div>
''')
print('</div>')

base.bottom()

    

