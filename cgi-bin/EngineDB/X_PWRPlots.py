#!/usr/bin/python3

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
from bokeh.palettes import d3, brewer
from bokeh.layouts import column, row
import json
import makeTestingData as mTD

TestData = pd.read_csv(mTD.get_test(), parse_dates=['Time'])
BoardData = pd.read_csv(mTD.get_board())
PeopleData = pd.read_csv(mTD.get_people())
mergetemp = TestData.merge(BoardData, on='Board ID', how='left')
AllData = mergetemp.merge(PeopleData, on='Person ID', how='left')
AllData = AllData.rename(columns={'Successful':'Outcome'})
AllData['Outcome'] = AllData['Outcome'].replace(0, 'Unsuccessful')
AllData['Outcome'] = AllData['Outcome'].replace(1, 'Successful')

tempXP = pd.read_csv(mTD.get_xpwr())
XP = tempXP.dropna()


# custom javascript filter to control which data is displayed using the widgets
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

#color pallete to be used on graphs
colors = [d3['Category10'][10][0], d3['Category10'][10][1], d3['Category10'][10][2], d3['Category10'][10][3], d3['Category10'][10][4], d3['Category10'][10][5], d3['Category10'][10][6], d3['Category10'][10][7], d3['Category10'][10][8], d3['Category10'][10][9], brewer['Accent'][8][0], brewer['Accent'][8][3], brewer['Dark2'][8][0], brewer['Dark2'][8][2], brewer['Dark2'][8][3], brewer['Dark2'][8][4], brewer['Dark2'][8][5], brewer['Dark2'][8][6]]


#creates a matrix of filterable data to be used in the plot
def Histogram(columns, data, view, widgets):
    # creates a dictionary for the histogram data to go in
    hist_data = ColumnDataSource(data={'top':[], 'bottom':[], 'left':[], 'right':[]})
    
    # creates a dictionary for the filtered data to be put in data tables
    dt = ColumnDataSource(data={'Type ID':[], 'Full ID':[], 'Person Name':[], 'Time':[], 'Outcome':[], 'Voltage':[]})
    std = ColumnDataSource(data={'std':[], 'mean':[]})
    # custom javascript to be run to actually create the plotted data client side
    # all done in javascript so it runs on the website and can update without refreshing the page
    x = CustomJS(args=dict(col=columns, hist=hist_data, data=data, view=view, dt=dt, std=std),code='''
const type_ids=[];
const full_ids=[];
const people=[];
const times=[];
const outcomes=[];
const res=[];

const indices = view.filters[0].compute_indices(data);
let mask = new Array(data.data[col].length).fill(false);
[...indices].forEach((x)=>{mask[x] = true;})

for (let j = 0; j < data.get_length(); j++) {
    if (mask[j] == true){
        type_ids.push(data.data['Type ID'][j])
        full_ids.push(data.data['Full ID'][j])
        people.push(data.data['Person Name'][j])
        times.push(data.data['Time'][j])
        outcomes.push(data.data['Outcome'][j])
        res.push(data.data[col][j])
    }
}

const good_data = data.data[col].filter((_,y)=>mask[y])
let m = Math.max(...good_data);
let scale = d3.scaleLinear().domain([0,m]).nice()
let binner = d3.bin()
let d = binner(good_data)
let right = d.map(x=>x.x1)
let left = d.map(x=>x.x0)
let bottom = new Array(d.length).fill(0)
let top = d.map(x=>x.length);
hist.data['right'] = right;
hist.data['left'] = left;
hist.data['bottom'] = bottom;
hist.data['top'] = top;
hist.change.emit()

dt.data['Type ID'] = type_ids;
dt.data['Full ID'] = full_ids;
dt.data['Person Name'] = people;
dt.data['Time'] = times;
dt.data['Outcome'] = outcomes;
dt.data['Voltage'] = res;
dt.change.emit()
std.data['mean'] = [d3.mean(good_data)];
std.data['std'] = [d3.deviation(good_data)];
std.change.emit()
''')
    for widget in widgets:
        widget.js_on_change('value', x)
    return hist_data, dt, std

# creates the webpage and plots the data
def Filter():
    # create a CDS with all the data to be used
    df_temp = AllData.merge(XP, on='Test ID', how='left')
    df_temp = df_temp.dropna()
    ds = ColumnDataSource(df_temp)

    # create the widgets to be used
    mc_widgets = {}
    dr_widgets = {}
    multi_choice = (lambda x,y: MultiChoice(options=x, value=[], title=y), 'value')
    start_date = (lambda x,y,z: DatePicker(min_date=x,max_date=y, value=x, title=z), 'value')
    today = datetime.date.today()
    end_date = (lambda x,y,z: DatePicker(min_date=x,max_date=y, value=today, title=z), 'value')
    min_date = pd.Timestamp((min(ds.data['Time']))).date()
    date_range = []
    while min_date <= today:
        date_range.append(min_date)
        min_date += datetime.timedelta(days=1)
    # widget titles and data for those widgets has to be manually entered, as well as the type
    columns = ['Type ID', 'Full ID', 'Person Name', 'Outcome', 'Start Date', 'End Date']
    data = [ds.data['Type ID'].tolist(), ds.data['Full ID'].tolist(), ds.data['Person Name'].tolist(), ds.data['Outcome'], date_range, date_range]
    t = [multi_choice, multi_choice, multi_choice, multi_choice, start_date, end_date]
    
    # creates the figure object
    p = figure(
        title='X PWR',
        x_axis_label='Voltage',
        y_axis_label='Number of Boards',
        tools='pan,wheel_zoom,box_zoom,reset,save',
        width = 925
        )

    # constructs the widgets
    for i in range(len(columns)):
        widget_constructor, trigger = t[i]
        if t[i] == multi_choice:
            possible_vals = np.unique(data[i]).tolist()
            widget = widget_constructor(possible_vals, columns[i])
            typ = 'multi_choice'
            widget.js_on_change(trigger, CustomJS(args=dict(src=ds), code='src.change.emit()'))
            mc_widgets[columns[i]] = {
                'type': typ,
                'possible_vals': possible_vals,
                'widget': widget,}
        else:
            possible_vals = data[i]
            widget = widget_constructor(min(data[i]),max(data[i]), columns[i])
            typ = 'date_range'
            widget.js_on_change(trigger, CustomJS(args=dict(src=ds), code='src.change.emit()'))
            dr_widgets[columns[i]] = {
                'type': typ,
                'possible_vals': possible_vals,
                'widget': widget,}

    #custom data filter, has to be written in javascript to be integrated into the website
    custom_filter = CustomJSFilter(args=dict(mc_widgets=mc_widgets, dr_widgets=dr_widgets),code=filter_code)
    #implements the filter on the data source
    view = CDSView(source=ds, filters=[custom_filter])
    #sets up all the objects to be created
    all_widgets = {**mc_widgets, **dr_widgets}
    widgets = {k:w['widget'] for k,w in all_widgets.items()}
    # calls the function that creates the plotting data
    hds, dt, std = Histogram('Voltage', ds, view, widgets.values())
    # tells the figure object what data source to use
    p.quad(top='top', bottom='bottom', left='left', right='right', source=hds, color = colors[0])

    # creates data tables
    table_columns = [
                    TableColumn(field='Type ID', title='Type ID'),
                    TableColumn(field='Full ID', title='Full ID'),
                    TableColumn(field='Person Name', title='Person Name'),
                    TableColumn(field='Time', title='Date', formatter=DateFormatter()),
                    TableColumn(field='Outcome', title='Outcome'),
                    TableColumn(field='Voltage', title='Voltage'),
                    ]
    data_table = DataTable(source=dt, columns=table_columns, width=925, autosize_mode='fit_columns')
    table_columns_2 = [
                    TableColumn(field='mean', title='Mean'),
                    TableColumn(field='std', title='Standard Deviation'),
                    ]
    data_table_2 = DataTable(source=std, columns=table_columns_2, autosize_mode='fit_columns')

    w = [*widgets.values()]
    subtypes = np.unique(ds.data['Type ID'].tolist()).tolist()
    serial_numbers = {}
    for s in subtypes:
        serial_numbers[s] = np.unique(df_temp.query('`Type ID` == @s')['Full ID'].values.tolist()).tolist()
    update_options = CustomJS(args=dict(serial_numbers=serial_numbers, widget=w[1]), code=('''
widget.options = serial_numbers[this.value]
'''))
    w[0].js_on_change('value', update_options)
    # gets the second half of the webpage where the residuals are displayed
    # since it's a separate function, the data can be filtered separately
    layout = Gaussian()
    #converts the bokeh items to json and sends them to the webpage
    plot_json = json.dumps(json_item(row(column(row(w[0:3]), row(w[3:6]), p, data_table, data_table_2), layout)))
    return plot_json


################################################################################################################

def Gaussian2(data, view, widgets, serial_numbers, n_sigma):
    hist = ColumnDataSource(data={'top':[], 'bottom':[], 'left':[], 'right':[]})
    pf = ColumnDataSource(data={'pass':[], 'fail':[], 'x':['Fail', 'Pass']})
    td = ColumnDataSource(data={'Serial Number':[], 'Deviation':[], 'Pass/Fail':[]})
    x = CustomJS(args=dict(hist=hist, data=data, view=view, serial_numbers=serial_numbers, n_sigma=n_sigma, pf=pf, td=td),code='''
const residules = [];

var chis = {};
for (let sn = 0; sn < serial_numbers.length; sn++) {
    chis[serial_numbers[sn]] = [];
} 

const indices = view.filters[0].compute_indices(data);
let mask = new Array(data.data['Voltage'].length).fill(false);
[...indices].forEach((x)=>{mask[x] = true;})

const good_data = data.data['Voltage'].filter((_,y)=>mask[y])
let mean = d3.mean(good_data)
let std = d3.deviation(good_data)
for (let sn = 0; sn < serial_numbers.length; sn++) {
    const indices = view.filters[0].compute_indices(data);
    let mask_sn = new Array(data.data['Voltage'].length).fill(false);
    [...indices].forEach((x)=>{mask_sn[x] = true;})
    for (let j = 0; j < data.get_length(); j++) {
        if (mask_sn[j] == true && data.data['Full ID'][j] == serial_numbers[sn]){
            mask_sn[j] = true;
            let x = data.data['Voltage'][j] - mean;
            if (std == 0) {
                let chi = 0;
                residules.push(chi)
            } else {
                let chi = x/std;
                residules.push(chi)    
            }
        } else {
            mask_sn[j] = false;
        }
    }
    const good_data_sn = data.data['Voltage'].filter((_,y)=>mask_sn[y])
    let mean_sn = d3.mean(good_data_sn)
    let y = mean_sn - mean;
    let chi_sn = y/std;
    if (isNaN(chi_sn)) {
        chis[serial_numbers[sn]].push(0)
    } else {
        chis[serial_numbers[sn]].push(Math.abs(chi_sn))
    }
}

let binner = d3.bin()
let d = binner(residules)
let right = d.map(x=>x.x1)
let left = d.map(x=>x.x0)
let bottom = new Array(d.length).fill(0)
let top = d.map(x=>x.length);

hist.data['right'] = right;
hist.data['left'] = left;
hist.data['bottom'] = bottom;
hist.data['top'] = top;
hist.change.emit()

let t_pass = 0;
let t_fail = 0;
const sn_td = [];
const chi_td = [];
const pf_td = [];
for (let sn = 0; sn < serial_numbers.length; sn++) {
    let pass = 0;
    let fail = 0;
    for (let c = 0; c < chis[serial_numbers[sn]].length; c++) {
        let chi_i = chis[serial_numbers[sn]][c]
        if (chi_i <= n_sigma.value) {
            pass = pass + 1;
            pf_td.push('PASS')
        } else {
            fail = fail + 1;
            pf_td.push('FAIL')
        }
        sn_td.push(serial_numbers[sn])
        chi_td.push(chi_i)
    }
    if (fail == 0) {
        t_pass = t_pass + 1;
    } else {
        t_fail = t_fail + 1;
    }
}
pf.data['pass'] = [0, t_pass];
pf.data['fail'] = [t_fail, 0];
pf.change.emit()

td.data['Serial Number'] = sn_td;
td.data['Deviation'] = chi_td;
td.data['Pass/Fail'] = pf_td;
td.change.emit()
    ''')
    for widget in widgets:
        widget.js_on_change('value', x)
    n_sigma.js_on_change('value', x)
    return hist, pf, td

def Gaussian():
    df_temp = AllData.merge(XP, on='Test ID', how='left')
    df_temp = df_temp.dropna()
    ds = ColumnDataSource(df_temp)
    serial_numbers = np.unique(ds.data['Full ID'].tolist()).tolist()

    mc_widgets = {}
    dr_widgets = {}
    multi_choice = (lambda x,y: MultiChoice(options=x, value=[], title=y), 'value')
    start_date = (lambda x,y,z: DatePicker(min_date=x,max_date=y, value=x, title=z), 'value')
    today = datetime.date.today()
    end_date = (lambda x,y,z: DatePicker(min_date=x,max_date=y, value=today, title=z), 'value')
    min_date = pd.Timestamp((min(ds.data['Time']))).date()
    date_range = []
    while min_date <= today:
        date_range.append(min_date)
        min_date += datetime.timedelta(days=1)
    columns = ['Type ID', 'Full ID', 'Outcome', 'Start Date', 'End Date']
    data = [ds.data['Type ID'].tolist(), ds.data['Full ID'].tolist(), ds.data['Outcome'], date_range, date_range]
    t = [multi_choice, multi_choice, multi_choice, start_date, end_date]

    for i in range(len(columns)):
        widget_constructor, trigger = t[i]
        if t[i] == multi_choice:
            possible_vals = np.unique(data[i]).tolist()
            widget = widget_constructor(possible_vals, columns[i])
            typ = 'multi_choice'
            widget.js_on_change(trigger, CustomJS(args=dict(src=ds), code='''
    src.change.emit()
'''))
            mc_widgets[columns[i]] = {
                'type': typ,
                'possible_vals': possible_vals,
                'widget': widget,}
        else:
            possible_vals = data[i]
            widget = widget_constructor(min(data[i]),max(data[i]), columns[i])
            typ = 'date_range'
            widget.js_on_change(trigger, CustomJS(args=dict(src=ds), code='''
    src.change.emit()
'''))
            dr_widgets[columns[i]] = {
                'type': typ,
                'possible_vals': possible_vals,
                'widget': widget,}

    custom_filter = CustomJSFilter(args=dict(mc_widgets=mc_widgets, dr_widgets=dr_widgets),code=filter_code)
    view = CDSView(source=ds, filters=[custom_filter])

    all_widgets = {**mc_widgets, **dr_widgets}
    widgets = {k:w['widget'] for k,w in all_widgets.items()}

    n_sigma = NumericInput(value=1, low=0.01, high=10, title='# of standard deviations for passing', mode='float')

    hist, pf, td = Gaussian2(ds, view, widgets.values(), serial_numbers, n_sigma)
    p = figure(
        title='Residual Distribution',
        x_axis_label='# of Standard Deviations from Mean',
        y_axis_label='Number of Boards',
        tools='pan,wheel_zoom,box_zoom,reset,save',
        width = 925
        )

    p.quad(top='top', bottom='bottom', left='left', right='right', source=hist, color = colors[0])

    q = figure(
        title='Pass vs Fail',
        x_range=pf.data['x'],
        x_axis_label='',
        y_axis_label='Number of Boards',
        tools='pan,wheel_zoom,box_zoom,reset,save',
        width = 925
        )

    q.vbar(x='x', top='pass', source=pf, color=colors[2], width=0.8)
    q.vbar(x='x', top='fail', source=pf, color=colors[3], width=0.8)

    table_columns = [
                    TableColumn(field='Serial Number', title='Full ID'),
                    TableColumn(field='Deviation', title='# of Standard Deviations'),
                    TableColumn(field='Pass/Fail', title='Pass/Fail'),
                    ]
    data_tables = DataTable(source=td, columns=table_columns, autosize_mode='fit_columns')
            
    w = [*widgets.values()]
    subtypes = np.unique(ds.data['Type ID'].tolist()).tolist()
    serial_numbers = {}
    for s in subtypes:
        serial_numbers[s] = np.unique(df_temp.query('`Type ID` == @s')['Full ID'].values.tolist()).tolist()
    update_options = CustomJS(args=dict(serial_numbers=serial_numbers, widget=w[1]), code=('''
widget.options = serial_numbers[this.value]
'''))
    w[0].js_on_change('value', update_options)

    layout = column(row(w[0:3]), row(w[3:5] + [n_sigma]), p, q, data_tables)
    return layout



