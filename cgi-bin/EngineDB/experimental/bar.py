#!../cgi_runner.sh

import jq
from pathlib import Path
import numpy as np
import json
import sys

sys.path.append("api")

from bokeh.plotting import figure, show
from bokeh.embed import file_html, json_item
from bokeh.models import (
    CustomJS,
    TextInput,
    AjaxDataSource,
    ColumnDataSource,
    TextAreaInput,
)
import cgitb
import cgi
from bokeh.layouts import column, row
from jinja2 import Environment, PackageLoader, select_autoescape, FileSystemLoader
from api.latest_tests import getLatestResults


def parseArgs():
    args = cgi.parse()
    jq_expr = args.get("jq")[0]
    xlabel = args.get("xlabel")[0]
    ylabel = args.get("ylabel")[0]
    return dict(jq_expr=jq_expr, xlabel=xlabel, ylabel=ylabel)


def main():

    template_path = (Path(__file__).parent / "").absolute()

    loader = FileSystemLoader(template_path)
    env = Environment(
        loader=loader,
        autoescape=select_autoescape(),
    )
    print("Content-Type: text/html\n\n")

    template = env.get_template("histogram.html")

    # results = getLatestResults(include_attach=True)
    # args = parseArgs()
    # hist, edges = np.histogram(results)
    p = figure(x_range=[])

    cds = ColumnDataSource()

    p.vbar(source=cds, x="names", top="vals", width=0.9)

    text_input = TextAreaInput(
        value='map(select( (.type_id | test("EL10[EW]")) and .test_name == "Thermal Cycle")) | .[] | .attach.test_data.site',
        title="Query:",
    )

    nbins_input = TextInput(title="NBins")
    xlabel_input = TextInput(title="X Label")
    ylabel_input = TextInput(title="Y Label")

    callback = CustomJS(
        args=dict(source=cds, te=text_input, nbins=nbins_input, plot=p),
        code="""
        const base_url = "https://cmslab1.spa.umn.edu/Factory/EngineDB/experimental/api/histogrammer.py?"
        const data = {jq: te.value}
        if(nbins.value){
             data.nbins = parseInt(nbins.value);
        }
        const search_params = new URLSearchParams(data);
        console.log(base_url + search_params.toString())
        const d = fetch(base_url + search_params.toString()).then(
           x=> {
           x.json().then(d =>{
        console.log(plot)
        console.log(d);
            plot.x_range.factors = d.names;
        source.data = d;
        }); })
        """,
    )

    xlabel_input.js_on_change(
        "change",
        CustomJS(
            args=dict(source=cds, p=p.xaxis),
            code="""
        console.log(cb_obj.value);
        p[0].axis_label=cb_obj.value; """,
        ),
    )
    ylabel_input.js_on_change(
        "change",
        CustomJS(
            args=dict(source=cds, p=p.yaxis),
            code="""
        console.log(cb_obj.value);
        p[0].axis_label=cb_obj.value; """,
        ),
    )

    p.xaxis.axis_label = "Value"
    p.yaxis.axis_label = "Count"
    p.xaxis.axis_label_text_font_size = "15pt"
    p.yaxis.axis_label_text_font_size = "15pt"

    text_input.js_on_change("value", callback)
    nbins_input.js_on_change("value", callback)
    item_text = json.dumps(
        json_item(
            column(text_input, row(xlabel_input, ylabel_input, nbins_input), p),
            "myplot",
        )
    )
    print(template.render(plots={"myplot": item_text}))


if __name__ == "__main__":
    cgitb.enable()
    main()
