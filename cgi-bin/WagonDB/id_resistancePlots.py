#!./cgi_runner.sh

# framework for creating dynamic plots
import sys
import pandas as pd
import csv
import numpy as np
from datetime import datetime as dt
import datetime
from bokeh.plotting import figure
from bokeh.models import (
    ColumnDataSource, 
    CustomJS, 
    CheckboxGroup, 
    CustomJSFilter, 
    MultiChoice, 
    CDSView, 
    DatePicker,
    Slider,
    DataTable,
    DateFormatter,
    TableColumn,
    Select,
    Label,
    NumericInput,
)
from bokeh.embed import json_item
from bokeh.models.widgets import HTMLTemplateFormatter
from bokeh.palettes import d3, brewer
from bokeh.layouts import column, row
import json
import makeTestingData as mTD

#import all data from csv files and set it up properly
TestData = pd.read_csv(mTD.get_test(), parse_dates=['Time'])
BoardData = pd.read_csv(mTD.get_board())
PeopleData = pd.read_csv(mTD.get_people())
mergetemp = TestData.merge(BoardData, on='Board ID', how='left')
AllData = mergetemp.merge(PeopleData, on='Person ID', how='left')
AllData = AllData.rename(columns={'Successful':'Outcome'})
AllData['Outcome'] = AllData['Outcome'].replace(0, 'Unsuccessful')
AllData['Outcome'] = AllData['Outcome'].replace(1, 'Successful')

tempIDR = pd.read_csv(mTD.get_id_res())
IDR = tempIDR.dropna()

filter_code=('''
const is_selected_map = new Map([
    ["multi_choice", (wi, pos, el, idx) => wi.value.includes(el)],
    ["date_range", (wi, pos, el, idx) => wi.value == el]
]);
const passed_vals = new Map(
    Object.keys(mc_widgets).map(
        (col) => {
            let pos = mc_widgets[col].possible_vals;
            let wi = mc_widgets[col].widget;
            let t = mc_widgets[col].type;
            return [col, new Map(pos.map((x, i) => [x, is_selected_map.get(t)(wi, pos, x, i)]))];
        })
);
const keys = Array.from(passed_vals.keys());
function allfalse(value) {
    return value === false;
}
for (let k = 0; k < keys.length; k++) {
    const innermap = passed_vals.get(keys[k])
    const pv = Array.from(passed_vals.get(keys[k]).values())
    let bool = pv.every(allfalse);
    const nk = Array.from(passed_vals.get(keys[k]).keys())
    if (bool == true) {
        for (let i = 0; i < nk.length; i++) {
            innermap.set(nk[i], true)
        }
    passed_vals.set(keys[k], innermap);
    }
}
const indices = [];
for (let i = 0; i < source.get_length(); i++) {
    if (keys.every((k) => {
            return passed_vals.get(k).get(source.data[k][i])
        })) {
        indices.push(true);
    } else {
        indices.push(false);
    }
}
const dates = new Map(
    Object.keys(dr_widgets).map(
        (col) => {
            let pos = dr_widgets[col].possible_vals;
            let wi = dr_widgets[col].widget;
            let t = dr_widgets[col].type;
            return [col, new Map(pos.map((x, i) => [x, is_selected_map.get(t)(wi, pos, x, i)]))];
        })
);
const d_keys = Array.from(dates.get('Start Date').keys());
let start_date = 0;
let end_date = 0;
for (let i = 0; i < d_keys.length; i++) {
    if (dates.get('Start Date').get(d_keys[i]) == true) {
        let sd = d_keys[i];
        start_date = new Date(sd);
    }
    if (dates.get('End Date').get(d_keys[i]) == true) {
        let ed = d_keys[i];
        end_date = new Date(ed);

        end_date.setDate(end_date.getDate() + 1);
    }
}
for (let i = 0; i < source.get_length(); i++) {
    if (source.data['Time'][i] >= start_date && source.data['Time'][i] <= end_date && indices[i] == true) {
        indices[i] = true;
    } else {
        indices[i] = false;
    }
}
return indices;

''')

#create a color pallete to be used on graphs
colors = [d3['Category10'][10][0], d3['Category10'][10][1], d3['Category10'][10][2], d3['Category10'][10][3], d3['Category10'][10][4], d3['Category10'][10][5], d3['Category10'][10][6], d3['Category10'][10][7], d3['Category10'][10][8], d3['Category10'][10][9], brewer['Accent'][8][0], brewer['Accent'][8][3], brewer['Dark2'][8][0], brewer['Dark2'][8][2], brewer['Dark2'][8][3], brewer['Dark2'][8][4], brewer['Dark2'][8][5], brewer['Dark2'][8][6]]

for i in range(0,20):
    colors.append(d3['Category20c'][20][i])

def Histogram(columns, data, views, widgets, subtypes, serial_numbers, slider):
    # each subtype gets its own subpage, this is done by changing which plot is visible
    # each serial number is then iterated over and plotted individually as a legend entry
    hist = {}
    dt = {}
    for s in subtypes:
        hist[s] = ColumnDataSource(data={'top':[], 'bottom':[], 'left':[], 'right':[]})
        dt[s] = ColumnDataSource(data={'Full ID': [], 'Person Name': [], 'Time': [], 'Outcome': [], 'Resistance': []})

    td = ColumnDataSource(data={'Subtype': subtypes, 'mean': [], 'std':[]})

    x = CustomJS(args=dict(col=columns, hist=hist, data=data, views=views, subtypes=subtypes, slider=slider, td=td, dt=dt),code='''
// create arrays for table
const means = [];
const devs = [];

// iterate over subtypes
for (let s = 0; s < subtypes.length; s++) {
    const sns = [];
    const resists = [];
    const people = [];
    const times = [];
    const outcomes = [];

    const indices = views[subtypes[s]].filters[0].compute_indices(data[subtypes[s]]);
    let mask = new Array(data[subtypes[s]].data[col].length).fill(false);
    [...indices].forEach((x)=>{mask[x] = true;})

    for (let i = 0; i < mask.length; i++) {
        if (mask[i] == true) {
            sns.push(data[subtypes[s]].data['Full ID'][i])
            resists.push(data[subtypes[s]].data[col][i])
            people.push(data[subtypes[s]].data['Person Name'][i])
            times.push(data[subtypes[s]].data['Time'][i])
            outcomes.push(data[subtypes[s]].data['Outcome'][i])
        }
    }

    const good_data = data[subtypes[s]].data[col].filter((_,y)=>mask[y])
    let bins = 2*slider.value
    let min = Math.min(...good_data);
    let m = Math.max(...good_data);
    let scale = d3.scaleLinear().domain([min-0.5,m+0.5]).nice()
    let binner = d3.bin().domain(scale.domain()).thresholds(bins)
    let d = binner(good_data)
    let right = d.map(x=>x.x1)
    let left = d.map(x=>x.x0)
    let bottom = new Array(d.length).fill(0)
    let top = d.map(x=>x.length);

    // fill data sources
    hist[subtypes[s]].data['right'] = right;
    hist[subtypes[s]].data['left'] = left;
    hist[subtypes[s]].data['bottom'] = bottom;
    hist[subtypes[s]].data['top'] = top;
    hist[subtypes[s]].change.emit()

    dt[subtypes[s]].data['Full ID'] = sns;
    dt[subtypes[s]].data['Person Name'] = people;
    dt[subtypes[s]].data['Time'] = times;
    dt[subtypes[s]].data['Outcome'] = outcomes;
    dt[subtypes[s]].data['Resistance'] = resists;
    dt[subtypes[s]].change.emit()

    means.push(d3.mean(good_data))
    devs.push(d3.deviation(good_data))
}

td.data['mean'] = means;
td.data['std'] = devs;
td.change.emit()
''')
    for widget in widgets:
        widget.js_on_change('value', x)
    slider.js_on_change('value', x)
    return hist, dt, td

def Filter():
    df_temp = AllData.merge(IDR, on='Test ID', how='left')
    df_temp = df_temp.dropna()
    ds = ColumnDataSource(df_temp)
    # create subtypes array and serial numbers dictionary
    # each subtype has its own data source
    subtypes = np.unique(ds.data['Sub Type'].tolist()).tolist()
    data_sources = {}
    serial_numbers = {}
    for s in subtypes:
        data_sources[s] = ColumnDataSource(df_temp.query('`Sub Type` == @s'))
        serial_numbers[s] = np.unique(df_temp.query('`Sub Type` == @s')['Full ID'].values.tolist()).tolist()

    mc_widgets = {}
    dr_widgets = {}
    multi_choice = (lambda x,y: MultiChoice(options=x, value=[], title=y), 'value')
    start_date = (lambda x,y,z: DatePicker(min_date=x,max_date=y, value='2024-11-20', title=z), 'value')
    today = datetime.date.today()
    end_date = (lambda x,y,z: DatePicker(min_date=x,max_date=y, value=today, title=z), 'value')
    min_date = pd.Timestamp((min(ds.data['Time']))).date()
    date_range = []
    while min_date <= today:
        date_range.append(min_date)
        min_date += datetime.timedelta(days=1)
    columns = ['Person Name', 'Outcome', 'Start Date', 'End Date']
    data = [ds.data['Person Name'].tolist(), ds.data['Outcome'], date_range, date_range]
    t = [multi_choice, multi_choice, start_date, end_date]

    for i in range(len(columns)):
        widget_constructor, trigger = t[i]
        if t[i] == multi_choice:
            possible_vals = np.unique(data[i]).tolist()
            widget = widget_constructor(possible_vals, columns[i])
            typ = 'multi_choice'
            widget.js_on_change(trigger, CustomJS(args=dict(src=data_sources, subtypes=subtypes), code='''
for (let i = 0; i < subtypes.length; i++) {
    src[subtypes[i]].change.emit()
}
'''))
            mc_widgets[columns[i]] = {
                'type': typ,
                'possible_vals': possible_vals,
                'widget': widget,}
        else:
            possible_vals = data[i]
            widget = widget_constructor(min(data[i]),max(data[i]), columns[i])
            typ = 'date_range'
            widget.js_on_change(trigger, CustomJS(args=dict(src=data_sources, subtypes=subtypes), code='''
for (let i = 0; i < subtypes.length; i++) {
    src[subtypes[i]].change.emit()
}
'''))
            dr_widgets[columns[i]] = {
                'type': typ,
                'possible_vals': possible_vals,
                'widget': widget,}

    custom_filter = CustomJSFilter(args=dict(mc_widgets=mc_widgets, dr_widgets=dr_widgets),code=filter_code)
    views = {}
    for s in subtypes:
        views[s] = CDSView(source=data_sources[s], filters=[custom_filter])
    slider = Slider(start=1, end=16, value=8, step=1, title='Granularity')
    all_widgets = {**mc_widgets, **dr_widgets}
    widgets = {k:w['widget'] for k,w in all_widgets.items()}

    module_template = '''
<div>
<a href="module.py?full_id=<%= value %>"target="_blank">
<%= value %>
</a>
</div> 
'''
    board = HTMLTemplateFormatter(template=module_template)

    hist, dt, td = Histogram('Resistance', data_sources, views, widgets.values(), subtypes, serial_numbers, slider)
    # holds all the plot objects by subtype
    plots = {}
    tables = {}
    for idx,s in enumerate(subtypes):
        p = figure(
            title='ID Resistance by Subtype ',
            x_axis_label='Resistance',
            y_axis_label='Number of Boards',
            tools='pan,wheel_zoom,box_zoom,reset,save',
            width = 925
            )

        p.quad(top='top', bottom='bottom', left='left', right='right', source=hist[s], color = colors[4])
        p.legend.click_policy='hide'
        p.legend.label_text_font_size = '8pt' 
        p.visible = False

        plots[s] = p

        tc2 = [
                TableColumn(field='Full ID', title='Full ID', formatter=board),
                TableColumn(field='Person Name', title='Tester'),
                TableColumn(field='Time', title='Date'),
                TableColumn(field='Outcome', title='Outcome'),
                TableColumn(field='Resistance', title='Resistance'),
                ]
        tables[s] = DataTable(source=dt[s], columns=tc2, autosize_mode='fit_columns')
        tables[s].visible = False

    table_columns = [
                    TableColumn(field='Subtype', title='Subtype'),
                    TableColumn(field='mean', title='Mean'),
                    TableColumn(field='std', title='Standard Deviation'),
                    ]
    data_table = DataTable(source=td, columns=table_columns, autosize_mode='fit_columns')

    display_plot = CustomJS(args=dict(plots=plots, tables=tables), code=('''
for (let [name,plot] of Object.entries(plots)){
    if (name == this.value){
        plot.visible = true
    } else {
        plot.visible = false
    }
}
for (let [name,plot] of Object.entries(tables)){
    if (name == this.value){
        plot.visible = true
    } else {
        plot.visible = false
    }
}
'''))
    
    select = Select(title='Sub Type', options=subtypes)
    select.js_on_change('value', display_plot)

    w = [*widgets.values()]

    # column and row objects only take it lists, need to make arguments lists
    layout = column(row(w[0:2] + [select]), row(w[2:5]), slider, column(list(plots.values())), data_table, column(list(tables.values())))
    plot_json = json.dumps(json_item(layout))
    return plot_json

