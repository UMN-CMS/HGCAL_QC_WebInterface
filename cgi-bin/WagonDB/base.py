#!/usr/bin/python3

# this file contains all the base code to make the header, footer, main menu, etc, for the webpages

import re
import sys
import connect

def header(title=''):
    print('<!doctype html>')
    print('<html lang="en">')
    print('<head>')
    if len(sys.argv) == 1:
        print('<meta charset="utf-8">')
        print('<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-EVSTQN3/azprG1Anm3QDgpJLIm9Nao0Yz1ztcQTwFspd3yD65VohhpuuCOmLASjC" crossorigin="anonymous">')
        #print('<link  rel="stylesheet" href="../static/css/bootstrap.min.css">')
        #print('<link  rel="stylesheet" href="../static/css/style.css">')
    else:
        print('<meta charset="utf-8">')
        print('<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-EVSTQN3/azprG1Anm3QDgpJLIm9Nao0Yz1ztcQTwFspd3yD65VohhpuuCOmLASjC" crossorigin="anonymous">')
        #print('<link  rel="stylesheet" href="bootstrap.min.css">')
        #print('<link  rel="stylesheet" href="style.css">')
    print('<title> %s </title>' %title)
    print('''
<script src="https://cdn.bokeh.org/bokeh/release/bokeh-2.3.3.min.js"
        crossorigin="anonymous"></script>
<script src="https://cdn.bokeh.org/bokeh/release/bokeh-widgets-2.3.3.min.js"
        crossorigin="anonymous"></script>
<script src="https://cdn.bokeh.org/bokeh/release/bokeh-tables-2.3.3.min.js"
        crossorigin="anonymous"></script>
<script src="https://d3js.org/d3.v7.min.js"></script>
    ''')
    #print('''
#<script src="https://cdn.bokeh.org/bokeh/release/bokeh-mathjax-2.3.3.min.js"
        #crossorigin="anonymous"></script>
    #''')
    print('</head>')

def top():
    print('<body style="background-color:#e6e6e6; overflow-x:hidden">')
    print('''<div class="container py-4" style="width:100%">
    <div class="row">
        <div class="col-4">
        ''')
    if len(sys.argv) == 1:
        print('''
            <a href="home_page.py" class="d-flex text-decoration-none ">
                <h1 class="text-dark">HGCAL Board Test</h1>
            </a>
        ''')
        print('''
            <hr style="margin-top:-0.5em">
            <h6 class="text-dark">Maintained by the University of Minnesota CMS Group</h6>
        </div>
        <div class="col-6"></div>
        <div class="col-1">
            <img src="../../static/files/goldy2.png" style="float:leftt">
        </div>
    </div>
    </div>
    ''')
    else:
        print('''           <a href="index.html" class="d-flex text-decoration-none ">
            <h1 class="text-dark">HGCAL Board Test</h1>
        </a>
        ''')
        
        print('''        <hr style="margin-top:-0.5em">
                <h6 class="text-dark">Maintained by the University of Minnesota CMS Group</h6>
            </div>
            <div class="col-6"></div>
            <div class="col-1">
                <img src="../static/files/goldy2.png" style="float-right">
            </div>
        </div>
    </div>
    ''')
    if len(sys.argv) == 1:
        print('''<nav id="navbar" class="navbar navbar-expand-lg navbar-dark bg-dark sticky-top">
  <div class="container-fluid">
    <a class="navbar-brand" href="home_page.py">%s</a>
    <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNavDropdown" aria-controls="navbarNavDropdown" aria-expanded="false" aria-label="Toggle navigation">
      <span class="navbar-toggler-icon"></span>
    </button>
    <div class="collapse navbar-collapse" id="navbarNavDropdown">
      <ul class="navbar-nav">
        <li class="nav-item">
          <a class="nav-link active" aria-current="page" href="home_page.py">Home</a>
        </li>
        <li class="nav-item">
          <a class="nav-link" href="testers.py">Testers</a>
        </li>
        <li class="nav-item dropdown">
          <a class="nav-link dropdown-toggle" href="#" id="navbarDropdownMenuLink" role="button" data-bs-toggle="dropdown" aria-expanded="false">
            Board Check
          </a>
          <ul class="dropdown-menu" aria-labelledby="navbarDropdownMenuLink">
            <li><a class="dropdown-item" href="board_checkin.py">Board Checkin</a></li>
            <li><a class="dropdown-item" href="board_checkout.py">Board Checkout</a></li>
            <li><a class="dropdown-item" href="checkin_summary.py">Checkin Summary</a></li>
            <li><a class="dropdown-item" href="checkout_summary.py">Checkout Summary</a></li>
          </ul>
        </li>
        <li class="nav-item dropdown">
          <a class="nav-link dropdown-toggle" href="#" id="navbarDropdown" role="button" data-bs-toggle="dropdown" aria-expanded="false">
            Summary
          </a>
          <ul class="dropdown-menu" aria-labelledby="navbarDropdown">
            <li><a class="dropdown-item" href="summary.py">Summary</a></li>
            <li><a class="dropdown-item" href="analytics.py">Analytics</a></li>
            <li><a class="dropdown-item" href="board_images.py">Photo Repository</a></li>
          </ul>
        </li>
        <li class="nav-item dropdown">
          <a class="nav-link dropdown-toggle" href="#" id="navbarDropdownMenuLink" role="button" data-bs-toggle="dropdown" aria-expanded="false">
            Admin
          </a>
          <ul class="dropdown-menu" aria-labelledby="navbarDropdownMenuLink">
            <li><a class="dropdown-item" href="add_tester.py">Add New Tester</a></li>
            <li><a class="dropdown-item" href="add_new_test_template.py">Add New Test Template</a></li>
          </ul>
        </li>
        <li class="nav-item dropdown">
          <a class="nav-link dropdown-toggle" href="#" id="navbarDropdownMenuLink" role="button" data-bs-toggle="dropdown" aria-expanded="false">
            Plots
          </a>
          <ul class="dropdown-menu" aria-labelledby="navbarDropdownMenuLink">
            <li><a class="dropdown-item" href="testdata.py">Total Tests</a></li>
            <li><a class="dropdown-item" href="CompareTesters.py">Compare Testers</a></li>
            <li><a class="dropdown-item" href="ResistanceMeasurementData.py">Resistance Measurement</a></li>
            <li><a class="dropdown-item" href="IDResistorData.py">ID Resistor</a></li>
            <li><a class="dropdown-item" href="I2CData.py">I2C Read/Write</a></li>
            <li><a class="dropdown-item" href="BitErrorRateData.py">Bit Error Rate</a></li>
          </ul>
        </li>
      </ul>
    </div>
  </div>
</nav>
'''%connect.get_db_name())

    else:
        print('''<nav id="navbar" class="navbar navbar-expand-lg navbar-dark bg-dark sticky-top">
  <div class="container-fluid">
    <a class="navbar-brand" href="index.html">%s</a>
    <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNavDropdown" aria-controls="navbarNavDropdown" aria-expanded="false" aria-label="Toggle navigation">
      <span class="navbar-toggler-icon"></span>
    </button>
    <div class="collapse navbar-collapse" id="navbarNavDropdown">
      <ul class="navbar-nav">
        <li class="nav-item">
          <a class="nav-link active" aria-current="page" href="index.html">Home</a>
        </li>
        <li class="nav-item">
          <a class="nav-link" href="testers.html">Testers</a>
        </li>
        <li class="nav-item dropdown">
          <a class="dropdown-toggle" href="#" id="navbarDropdownMenuLink" role="button" data-bs-toggle="dropdown" aria-expanded="false">
            Summary
          </a>
          <ul class="dropdown-menu" aria-labelledby="navbarDropdownMenuLink">
            <li><a class="dropdown-item" href="summary.html">Summary</a></li>
            <li><a class="dropdown-item" href="summary.html">Summary</a></li>
          </ul>
        </li>
        <li class="nav-item dropdown">
          <a class="dropdown-toggle" href="#" id="navbarDropdownMenuLink" role="button" data-bs-toggle="dropdown" aria-expanded="false">
            Admin
          </a>
          <ul class="dropdown-menu" aria-labelledby="navbarDropdownMenuLink">
            <li><a class="dropdown-item" href="add_tester.html">Add New Tester</a></li>
            <li><a class="dropdown-item" href="add_new_test_template.html">Add New Test Template</a></li>
          </ul>
        </li>
      </ul>
    </div>
  </div>
</nav>
'''%connect.get_db_name())

def bottom():

    if len(sys.argv) == 1:
        print('''</div>
<footer class="footer-fluid bg-dark text-light py-3">
  <!-- Grid container -->
  <div class="container">
    <!--Grid row-->
    <div class="row">
      <!--Grid column-->
      <div class="col-lg-6 col-md-12 mb-4 mb-md-0">
        <h5 class="text-uppercase">HGCAL Board Test</h5>

        <p>
            Maintained by the UMN CMS Group. For inquiries or to report a bug, contact Bryan Crossman at cros0400@umn.edu
        </p>
      </div>

      <div class="col-lg-3 col-md-6 mb-4 mb-md-0">
      </div>

      <div class="col-lg-3 col-md-6 mb-4 mb-md-0">
        <h5 class="text-uppercase mb-0">Links</h5>

        <ul class="list-unstyled ms-2">
          <li>
            <a href="home_page.py" class="text-light text-decoration-none">Home</a>
          </li>
          <li>
            <a href="testers.py" class="text-light text-decoration-none">Testers</a>
          </li>
          <li>
            <span class="text-light">Summary</a>
            <ul class="list">
                <li>
                    <a href="summary_east.py" class="text-light text-decoration-none">\tSummary</a>
                </li>
                <li>
                    <a href="summary_west.py" class="text-light text-decoration-none">\tSummary</a>
                </li>
            </ul>
          </li>
          <li>
            <a href="../EngineDB/home_page.py" class="text-light text-decoration-none">HGCAL Engine Test</a>
          </li>
        </ul>
      </div>
    </div>
  </div>
</footer>''')
    else:
        print('''</div>
<footer class="footer-fluid bg-dark text-light py-3">
  <!-- Grid container -->
  <div class="container">
    <!--Grid row-->
    <div class="row">
      <!--Grid column-->
      <div class="col-lg-6 col-md-12 mb-4 mb-md-0">
        <h5 class="text-uppercase">HGCAL Board Test</h5>

        <p>
            Maintained by the UMN CMS Group. For inquiries or to report a bug, contact Bryan Crossman at cros0400@umn.edu
        </p>
      </div>

      <div class="col-lg-3 col-md-6 mb-4 mb-md-0">
      </div>

      <div class="col-lg-3 col-md-6 mb-4 mb-md-0">
        <h5 class="text-uppercase mb-0">Links</h5>

        <ul class="list-unstyled ms-2">
          <li>
            <a href="index.html" class="text-light text-decoration-none">Home</a>
          </li>
          <li>
            <a href="testers.html" class="text-light text-decoration-none">Testers</a>
          </li>
          <li>
            <span class="text-light">Summary</a>
            <ul class="list">
                <li>
                    <a href="summary_east.html" class="text-light text-decoration-none">\tSummary</a>
                </li>
                <li>
                    <a href="summary_west.html" class="text-light text-decoration-none">\tSummary</a>
                </li>
            </ul>
          </li>
          <li>
            <a href="../EngineDB/home_page.py" class="text-light text-decoration-none">HGCAL Engine Test</a>
          </li>
        </ul>
      </div>
    </div>
  </div>
</footer>''')
    
    print('</div>')
    print('<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/js/bootstrap.bundle.min.js" integrity="sha384-MrcW6ZMFYlzcLA8Nl+NtUVF0sA7MsXsP1UyJoMp4YLEuNSfAP+JcXn/tWtIaxVXM" crossorigin="anonymous"></script>')
    print('</body>')
    print('</html>')
    
def cleanCGInumber(cgitext):
    if cgitext is None:
        return 0
    return int(re.sub('[^0-9]','',cgitext))

