#!../../cgi_runner.sh

import cgi
import jq

# import cgitb
import html
import itertools as it
import json
import sys
from joblib import Memory
from util import MEMORY, cacheDisk

sys.path.append("../..")

import connect
import jq
from pathlib import Path
import numpy as np
import json
import sys

sys.path.append("api")

from bokeh.plotting import figure, show
from bokeh.embed import file_html, json_item
from bokeh.models import CustomJS, TextInput, AjaxDataSource
import cgitb
import cgi
from bokeh.layouts import column
from jinja2 import Environment, PackageLoader, select_autoescape, FileSystemLoader
from latest_tests import getLatestResults


def parseArgs():
    args = cgi.parse()
    jq_expr = args.get("jq")[0]
    bins = args.get("nbins")
    if bins:
        nbins = int(bins[0])
    else:
        nbins=None
    return dict(jq_expr=jq_expr, nbins=nbins)


def main():
    print("Content-Type: application/json\n\n")
    args = parseArgs()
    results = getLatestResults(include_attach=True, jq_expr=args["jq_expr"])
    nbins = args["nbins"]
    if nbins:
        hist, edges = np.histogram(results, bins=nbins)
    else:
        hist, edges = np.histogram(results)

    data = dict(
        values=hist.tolist(), left=edges[:-1].tolist(), right=edges[1:].tolist()
    )
    print(json.dumps(data))


if __name__ == "__main__":
    cgitb.enable()
    main()
