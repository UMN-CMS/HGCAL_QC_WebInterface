#! /home/webapp/pro/HGCAL_QC_WebInterface/cgi-bin/EngineDB/cgi_runner.sh

import cgi, html
import cgitb
import base
import sys
import makeTestingData as mTD

mTD.write_datafiles()

