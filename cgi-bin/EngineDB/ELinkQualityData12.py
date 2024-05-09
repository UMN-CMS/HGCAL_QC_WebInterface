#!/usr/bin/python3

import cgi
import cgitb
import base
import module_functions
import sys
import ElinkQPlots as mp

cgitb.enable()

if len(sys.argv) != 1:
    sys.stdout = open('%(loc)s/summary.html' %{'loc':sys.argv[1]}, 'w')

else:
    #cgi header
    print("Content-type: text/html\n")

base.header(title='E Link Quality')
base.top()
print('''
          <a class="nav-link dropdown-toggle" href="#" id="navbarDropdownMenuLink" role="button" data-bs-toggle="dropdown" aria-expanded="false">
            Change E Link Phase
          </a>
          <ul class="dropdown-menu" aria-labelledby="navbarDropdownMenuLink">
            <li><a class="dropdown-item" href="ELinkQualityData.py">0.0</a></li>
            <li><a class="dropdown-item" href="ELinkQualityData1.py">1.0</a></li>
            <li><a class="dropdown-item" href="ELinkQualityData2.py">2.0</a></li>
            <li><a class="dropdown-item" href="ELinkQualityData3.py">3.0</a></li>
            <li><a class="dropdown-item" href="ELinkQualityData4.py">4.0</a></li>
            <li><a class="dropdown-item" href="ELinkQualityData5.py">5.0</a></li>
            <li><a class="dropdown-item" href="ELinkQualityData6.py">6.0</a></li>
            <li><a class="dropdown-item" href="ELinkQualityData7.py">7.0</a></li>
            <li><a class="dropdown-item" href="ELinkQualityData8.py">8.0</a></li>
            <li><a class="dropdown-item" href="ELinkQualityData9.py">9.0</a></li>
            <li><a class="dropdown-item" href="ELinkQualityData10.py">10.0</a></li>
            <li><a class="dropdown-item" href="ELinkQualityData11.py">11.0</a></li>
            <li><a class="dropdown-item" href="ELinkQualityData12.py">12.0</a></li>
            <li><a class="dropdown-item" href="ELinkQualityData13.py">13.0</a></li>
            <li><a class="dropdown-item" href="ELinkQualityData14.py">14.0</a></li>
            <li><a class="dropdown-item" href="ELinkQualityData15.py">15.0</a></li>
          </ul>
''')
print('''
<script>
data = {};
Bokeh.embed.embed_item(data, 'exfilter');
</script>
<div id='exfilter' class='bk-root'></div>
'''.format(mp.ELinkFilter(str(12.0))))

base.bottom()

    

