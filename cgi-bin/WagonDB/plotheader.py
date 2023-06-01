#!/usr/bin/python2

#import makePlots as mp

def plotheader():
    print('''
<div style="padding-top:5px; padding-left:15px; padding-bottom:5px" class="bg-secondary">       
    <button class="btn btn-secondary dropdown-toggle" type="button" id="SelectTest" data-bs-toggle="dropdown" aria-expanded="false">
        Select Test
    </button>
    <ul class="dropdown-menu" aria-labelledby="SelectTest">
        <a class="dropdown-item" href="./testdata.py"><li>Total Tests</li></a>
        <a class="dropdown-item" href="./ResistanceMeasurementData.py"><li>Resistance Measurement</li></a>
        <a class="dropdown-item" href="./IDResistorData.py"><li>ID Resistor</li></a>
        <a class="dropdown-item" href="./I2CData.py"><li>I2C Read/Write</li></a>
        <a class="dropdown-item" href="./BitErrorRateData.py"><li>Bit Error Rate</li></a>
        <a class="dropdown-item" href="./CompareTesters.py"><li>Compare Testers</li></a>
    </ul>

    <button class="dropdown-toggle btn btn-secondary" type="button" id="SelectBoards" data-bs-toggle="dropdown" aria-expanded="false" data-bs-auto-close="outside">
        Select Board
    </button>
    <ul class="dropdown-menu" aria-labelledby="SelectBoards">
        <li><a class="dropdown-item" href="#"><div class="form-check">
            <input class="form-check-input" type="checkbox" value="" id="WW20A1" onchange="Board(this)">
            <label for="WW20A1">WW20A1</label>
        </div></a></li>
        <li><a class="dropdown-item" href="#"><div class="form-check">
            <input class="form-check-input" type="checkbox" value="" id="WW10A1" onchange="Board(this)">
            <label for="WW10A1">WW10A1</label>
        </div></a></li>
        <li><a class="dropdown-item" href="#"><div class="form-check">
            <input class="form-check-input" type="checkbox" value="" id="WE20B1" onchange="Board(this)">
            <label for="WE20B1">WE20B1</label>
        </div></a></li>
        <li><a class="dropdown-item" href="#"><div class="form-check">
            <input class="form-check-input" type="checkbox" value="" id="WE20A1" onchange="Board(this)">
            <label for="WE20A1">WE20A1</label>
        </div></a></li>
        <li><a class="dropdown-item" href="#"><div class="form-check">
            <input class="form-check-input" type="checkbox" value="" id="WE10A1" onchange="Board(this)">
            <label for="WE10A1">WE10A1</label>
        </div></a></li>
        <li><a class="dropdown-item" href="#"><div class="form-check">
            <input class="form-check-input" type="checkbox" value="" id="WW30A3" onchange="Board(this)">
            <label for="WW30A3">WW30A3</label>
        </div></a></li>
        <li><a class="dropdown-item" href="#"><div class="form-check">
            <input class="form-check-input" type="checkbox" value="" id="599999" onchange="Board(this)">
            <label for="599999">599999</label>
        </div></a></li>
    </ul>
    <button class="dropdown-toggle btn btn-secondary" type="button" id="SearchSN" data-bs-toggle="dropdown" aria-expanded="false">
        Select SN
    </button>
    <div class="dropdown-menu" aria-labelledby="SearchSN">
        <input type="text" class="form-control" list="datalistOptions" placeholder="Search Serial Number" onchange="GetSN(this)">
        <datalist id="datalistOptions">
            <option value="320WW20A1000005">
            <option value="320WW20A1000004">
            <option value="320WW10A1000005">
            <option value="320WW10A1000007">
            <option value="320WW10A1000008">
            <option value="320WW10A1000004">
            <option value="320WE20B1000004">
            <option value="320WE20A1000004">
            <option value="320WE20B1000006">
            <option value="320WE10A1000004">
            <option value="320WE10A1000008">
            <option value="320WE10A1000007">
            <option value="320WE10A1000005">
            <option value="320WE20A1000005">
            <option value="320WW30A3000005">
            <option value="320599999900001">
            <option value="320WE20A1000006">
            <option value="320WE20A1000007">
            <option value="320WE20B1000008">
            <option value="320WE20B1000007">
            <option value="320WE10A1000012">
            <option value="320WE10A1000011">
            <option value="320WE10A1000010">
            <option value="320WE10A1000009">
            <option value="320WW20A1000007">
            <option value="320WW20A1000009">
            <option value="320WW10A1000011">
            <option value="320WW10A1000009">
            <option value="320WW10A1000012">
            <option value="320WW10A1000010">
            <option value="320WW20A1000006">
        </datalist>
    </div>
    <button class="dropdown-toggle btn btn-secondary" type="button" id="SelectTesters" data-bs-toggle="dropdown" aria-expanded="false" data-bs-auto-close="outside">
        Select Tester
    </button>
    <ul class="dropdown-menu" aria-labelledby="SelectTesters">
        <li><a class="dropdown-item" href="#"><div class="form-check">
            <input class="form-check-input" type="checkbox" value="" id="Rand">
            <label for="Rand">Rand</label>
        </div></a></li>
        <li><a class="dropdown-item" href="#"><div class="form-check">
            <input class="form-check-input" type="checkbox" value="" id="Garrett">
            <label for="Garrett">Garrett</label>
        </div></a></li>
        <li><a class="dropdown-item" href="#"><div class="form-check">
            <input class="form-check-input" type="checkbox" value="" id="Bryan">
            <label for="Bryan">Bryan</label>
        </div></a></li>
        <li><a class="dropdown-item" href="#"><div class="form-check">
            <input class="form-check-input" type="checkbox" value="" id="Jocelyn">
            <label for="Jocelyn">Jocelyn</label>
        </div></a></li>
    </ul>
    <button class="dropdown-toggle btn btn-secondary" type="button" id="SelectDate" data-bs-toggle="dropdown" aria-expanded="false" data-bs-auto-close="outside" style="padding-right:15px">
        Date Range
    </button>
    <div class="dropdown-menu">
        <table>
            <tr><td> Start Date </td><td> End Date </td></tr>
            <tr>
            <td>
                <input type="date" id="StartDate">
            </td>
            <td>
                <input type="date" id="EndDate">
            </td>
            </tr>
        </table>
    </div>
    <button class="btn btn-success" onClick="window.location.reload();"> Update Plot </button>
</div>
    ''')


def plotscript():
    print('''
<script>
    var Test = None;
    
    var Data = None;
    function Data(choice)
    {
        Data = choice;
    }

    var Board = None;
    function Board(choice)
    {

    }

    var BitError = None;
    function BitError(choice)
    {
        BitError = choice; 
    }

    var Tester = None;
    function Tester(choice)
    {
        Tester = choice;
    }

    var SN = None;
    function GetSN(choice)
    {
        SN = choice;
        window.location.reload();
    }
</script>
    ''')
