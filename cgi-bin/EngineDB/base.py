#!./cgi_runner.sh

import re
import sys
import connect

def header(title=''):
    print('<!doctype html>')
    print('<html lang="en">')
    print('<head>')
    print('<meta charset="utf-8">')
    print('<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-EVSTQN3/azprG1Anm3QDgpJLIm9Nao0Yz1ztcQTwFspd3yD65VohhpuuCOmLASjC" crossorigin="anonymous">')
    print('<title> %s </title>' %title)
    print('''
<script src="https://cdn.bokeh.org/bokeh/release/bokeh-2.3.3.js"
        crossorigin="anonymous"></script>
<script src="https://cdn.bokeh.org/bokeh/release/bokeh-widgets-2.3.3.js"
        crossorigin="anonymous"></script>
<script src="https://cdn.bokeh.org/bokeh/release/bokeh-tables-2.3.3.js"
        crossorigin="anonymous"></script>
<script src="https://d3js.org/d3.v7.min.js"></script>
    ''')
    print('</head>')

def top(static):
    print('<body style="background-color:#e6e6e6; overflow-x:hidden">')
    print('''<div class="container py-4" style="width:100%">
    <div class="row">
        <div class="col-4">
        ''')
    if static:
        print('''
            <a href="home_page.html" class="d-flex text-decoration-none ">
                <h1 class="text-dark">HGCAL Board Test</h1>
            </a>
        ''')
        print('''
            <hr style="margin-top:-0.5em">
            <h6 class="text-dark">Maintained by the University of Minnesota CMS Group</h6>
        </div>
        <div class="col-6"></div>
        <div class="col-1">
            <img src="../files/goldy2.png" style="float:leftt">
        </div>
    </div>
    </div>
    ''')
    else:
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
    if static:
        print('''<nav id="navbar" class="navbar navbar-expand-lg navbar-dark bg-dark sticky-top">
  <div class="container-fluid">
    <a class="navbar-brand" href="home_page.html">%s</a>
    <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNavDropdown" aria-controls="navbarNavDropdown" aria-expanded="false" aria-label="Toggle navigation">
      <span class="navbar-toggler-icon"></span>
    </button>
    <div class="collapse navbar-collapse" id="navbarNavDropdown">
      <ul class="navbar-nav">
        <li class="nav-item">
          <a class="nav-link active" aria-current="page" href="home_page.html">Home</a>
        </li>
        <li class="nav-item">
            <a class="nav-link" href="https://sites.google.com/umn.edu/cms-hgcal-factory/home">HGCAL Factory</a>
        </li>
        <li class="nav-item">
          <a class="nav-link" href="search.html">Search Tests</a>
        </li>
        <li class="nav-item">
          <a class="nav-link" href="search_boards.html">Boards</a>
        </li>
        <li class="nav-item">
          <a class="nav-link" href="register_boards_form.html">Register Boards</a>
        </li>
        <li class="nav-item dropdown">
          <a class="nav-link dropdown-toggle" href="#" id="navbarDropdownMenuLink" role="button" data-bs-toggle="dropdown" aria-expanded="false">
            Board Check
          </a>
          <ul class="dropdown-menu" aria-labelledby="navbarDropdownMenuLink">
            <li><a class="dropdown-item" href="checkin_summary.html">Checkin Summary</a></li>
            <li><a class="dropdown-item" href="checkout_summary.html">Checkout Summary</a></li>
          </ul>
        </li>
        <li class="nav-item dropdown">
          <a class="nav-link dropdown-toggle" href="#" id="navbarDropdown" role="button" data-bs-toggle="dropdown" aria-expanded="false">
            Summary
          </a>
          <ul class="dropdown-menu" aria-labelledby="navbarDropdown">
            <li><a class="dropdown-item" href="summary.html">Board Summary</a></li>
            <li><a class="dropdown-item" href="tester_summary.html">Tester Summary</a></li>
            <li><a class="dropdown-item" href="board_images.html">Photo Repository</a></li>
          </ul>
        </li>
        <li class="nav-item dropdown">
          <a class="nav-link dropdown-toggle" href="#" id="navbarDropdownMenuLink" role="button" data-bs-toggle="dropdown" aria-expanded="false">
            Plots
          </a>
          <ul class="dropdown-menu" aria-labelledby="navbarDropdownMenuLink">
            <li><a class="dropdown-item" href="testdata.html">Total Tests</a></li>
            <li><a class="dropdown-item" href="boarddata.html">Board Status</a></li>
            <li><a class="dropdown-item" href="CompareTesters.html">Compare Testers</a></li>
            <li><a class="dropdown-item" href="ADC_functionality.html">ADC Functionality</a></li>
            <li><a class="dropdown-item" href="EClockData.html">E Clock Rates</a></li>
            <li><a class="dropdown-item" href="ELinkQualityData.html">E Link Quality</a></li>
            <li><a class="dropdown-item" href="FastCommandQualityData.html">Fast Command Quality</a></li>
            <li><a class="dropdown-item" href="UplinkQuality.html">Uplink Quality</a></li>
            <li><a class="dropdown-item" href="X_PWRData.html">Startup Current and Voltage</a></li>
            <li><a class="dropdown-item" href="I2CData.html">I2C</a></li>
            <li><a class="dropdown-item" href="GPIO_functionality.html">GPIO Functionality</a></li>
            <li><a class="dropdown-item" href="CurrentDrawData.html">Current Draw</a></li>
          </ul>
        </li>
      </ul>
    </div>
  </div>
</nav>
'''% "EngineDB")

    else:
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
            <a class="nav-link" href="https://sites.google.com/umn.edu/cms-hgcal-factory/home">HGCAL Factory</a>
        </li>
        <li class="nav-item">
          <a class="nav-link" href="search.py">Search Tests</a>
        </li>
        <li class="nav-item">
          <a class="nav-link" href="search_boards.py">Search Boards</a>
        </li>
        <li class="nav-item">
          <a class="nav-link" href="register_boards_form.py">Register Boards</a>
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
            <li><a class="dropdown-item" href="summary.py">Board Summary</a></li>
            <li><a class="dropdown-item" href="tester_summary.py">Tester Summary</a></li>
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
            <li><a class="dropdown-item" href="board_grade.py">Grade Board</a></li>
          </ul>
        </li>
        <li class="nav-item dropdown">
          <a class="nav-link dropdown-toggle" href="#" id="navbarDropdownMenuLink" role="button" data-bs-toggle="dropdown" aria-expanded="false">
            Plots
          </a>
          <ul class="dropdown-menu" aria-labelledby="navbarDropdownMenuLink">
            <li><a class="dropdown-item" href="testdata.py">Total Tests</a></li>
            <li><a class="dropdown-item" href="boarddata.py">Board Status</a></li>
            <li><a class="dropdown-item" href="CompareTesters.py">Compare Testers</a></li>
            <li><a class="dropdown-item" href="X_PWRData.py">Startup Current and Voltage</a></li>
            <li><a class="dropdown-item" href="EClockData.py">E Clock Rates</a></li>
            <li><a class="dropdown-item" href="ADC_functionality.py">ADC Functionality</a></li>
            <li><a class="dropdown-item" href="EyeOpeningData.py">Eye Opening</a></li>
            <li><a class="dropdown-item" href="ELinkQualityData.py?elink=0">E Link Quality</a></li>
            <li><a class="dropdown-item" href="CurrentDrawData.py">Current Draw</a></li>
            <li><a class="dropdown-item" href="CrossoverLinkData.py">Crossover Link Quality</a></li>
          </ul>
        </li>
        <li class="nav-item">
          <a class="nav-link" href="teststand_debug.py">Test Stand Debug</a>
        </li>
      </ul>
    </div>
  </div>
</nav>
'''% "EngineDB")

def bottom(static):

    if static:
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
            <a href="home_page.html" class="text-light text-decoration-none">Home</a>
          </li>
          <li>
            <span class="text-light">Summary</a>
            <ul class="list">
                <li><a class="text-light text-decoration-none" href="summary.html">\tBoard Summary</a></li>
                <li><a class="text-light text-decoration-none" href="tester_summary.html">\tTester Summary</a></li>
                <li><a class="text-light text-decoration-none" href="board_images.html">\tPhoto Repository</a></li>
            </ul>
          </li>
          <li>
            <a href="../WagonDB/home_page.html" class="text-light text-decoration-none">HGCAL Wagon Test</a>
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
            <span class="text-light">Summary</a>
            <ul class="list">
                <li><a class="text-light text-decoration-none" href="summary.py">\tBoard Summary</a></li>
                <li><a class="text-light text-decoration-none" href="tester_summary.py">\tTester Summary</a></li>
                <li><a class="text-light text-decoration-none" href="board_images.py">\tPhoto Repository</a></li>
            </ul>
          </li>
          <li>
            <a href="../WagonDB/home_page.py" class="text-light text-decoration-none">HGCAL Wagon Test</a>
          </li>
            <li>
                <a href="https://sites.google.com/umn.edu/cms-hgcal-factory/home" class="text-light text-decoration-none">HGCAL Factory</a>
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

