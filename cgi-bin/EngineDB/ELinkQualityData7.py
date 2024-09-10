#!./cgi_runner.sh

import cgi
import cgitb
import base
import module_functions
import sys
import ElinkQPlots as mp


def run(static):
    base.header(title='E Link Quality')
    base.top(static)
    # links to the other E Link Quality plots
    # having them all on the same page and using a widget to change which plot is visible
    # was very slow as lots of javascript had to be run and many plots had to be generated
    if static:
        print('''
                  <a class="nav-link dropdown-toggle" href="#" id="navbarDropdownMenuLink" role="button" data-bs-toggle="dropdown" aria-expanded="false">
                    Change E Link
                  </a>
                  <ul class="dropdown-menu" aria-labelledby="navbarDropdownMenuLink">
                    <li><a class="dropdown-item" href="ELinkQualityData.html">0.0</a></li>
                    <li><a class="dropdown-item" href="ELinkQualityData1.html">1.0</a></li>
                    <li><a class="dropdown-item" href="ELinkQualityData2.html">2.0</a></li>
                    <li><a class="dropdown-item" href="ELinkQualityData3.html">3.0</a></li>
                    <li><a class="dropdown-item" href="ELinkQualityData4.html">4.0</a></li>
                    <li><a class="dropdown-item" href="ELinkQualityData5.html">5.0</a></li>
                    <li><a class="dropdown-item" href="ELinkQualityData6.html">6.0</a></li>
                    <li><a class="dropdown-item" href="ELinkQualityData7.html">7.0</a></li>
                    <li><a class="dropdown-item" href="ELinkQualityData8.html">8.0</a></li>
                    <li><a class="dropdown-item" href="ELinkQualityData9.html">9.0</a></li>
                    <li><a class="dropdown-item" href="ELinkQualityData10.html">10.0</a></li>
                    <li><a class="dropdown-item" href="ELinkQualityData11.html">11.0</a></li>
                    <li><a class="dropdown-item" href="ELinkQualityData12.html">12.0</a></li>
                    <li><a class="dropdown-item" href="ELinkQualityData13.html">13.0</a></li>
                    <li><a class="dropdown-item" href="ELinkQualityData14.html">14.0</a></li>
                    <li><a class="dropdown-item" href="ELinkQualityData15.html">15.0</a></li>
                    <li><a class="dropdown-item" href="ELinkQualityData16.html">16.0</a></li>
                    <li><a class="dropdown-item" href="ELinkQualityData17.html">17.0</a></li>
                    <li><a class="dropdown-item" href="ELinkQualityData18.html">18.0</a></li>
                    <li><a class="dropdown-item" href="ELinkQualityData19.html">19.0</a></li>
                    <li><a class="dropdown-item" href="ELinkQualityData20.html">20.0</a></li>
                  </ul>
        ''')
    else:
        print('''
                  <a class="nav-link dropdown-toggle" href="#" id="navbarDropdownMenuLink" role="button" data-bs-toggle="dropdown" aria-expanded="false">
                    Change E Link
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
                    <li><a class="dropdown-item" href="ELinkQualityData16.py">16.0</a></li>
                    <li><a class="dropdown-item" href="ELinkQualityData17.py">17.0</a></li>
                    <li><a class="dropdown-item" href="ELinkQualityData18.py">18.0</a></li>
                    <li><a class="dropdown-item" href="ELinkQualityData19.py">19.0</a></li>
                    <li><a class="dropdown-item" href="ELinkQualityData20.py">20.0</a></li>
                  </ul>
        ''')
    print('''
    <script>
    data = {};
    Bokeh.embed.embed_item(data, 'exfilter');
    </script>
    <div id='exfilter' class='bk-root'></div>
    '''.format(mp.ELinkFilter(str(7.0))))

    base.bottom(static)

    
if __name__ == '__main__':
    cgitb.enable()
    #cgi header
    print("Content-type: text/html\n")
    
    run(False)

