#!/usr/bin/env bash
source /home/webapp/pro/HGCAL_QC_WebInterface/webappenv/bin/activate
export PYTHONPATH=$PYTHONPATH:$(dirname ${BASH_SOURCE[0]})
python3 "$@"
