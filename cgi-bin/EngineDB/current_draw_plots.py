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
from bokeh.palettes import d3, brewer
from bokeh.layouts import column, row
from bokeh.models.widgets import HTMLTemplateFormatter
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

tempCD = pd.read_csv(mTD.get_current_draw())
CD = tempCD.dropna()


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

#color pallete to be used on graphs
colors = [d3['Category10'][10][0], d3['Category10'][10][1], d3['Category10'][10][2], d3['Category10'][10][3], d3['Category10'][10][4], d3['Category10'][10][5], d3['Category10'][10][6], d3['Category10'][10][7], d3['Category10'][10][8], d3['Category10'][10][9], brewer['Accent'][8][0], brewer['Accent'][8][3], brewer['Dark2'][8][0], brewer['Dark2'][8][2], brewer['Dark2'][8][3], brewer['Dark2'][8][4], brewer['Dark2'][8][5], brewer['Dark2'][8][6]]


#creates a matrix of filterable data to be used in the plot
def Histogram(data, view, widgets):
    # creates a dictionary for the histogram data to go in
    hist_data_1v5 = ColumnDataSource(data={'top':[], 'bottom':[], 'left':[], 'right':[]})
    hist_data_10v = ColumnDataSource(data={'top':[], 'bottom':[], 'left':[], 'right':[]})
    
    # creates a dictionary for the filtered data to be put in data tables
    dt = ColumnDataSource(data={'Sub Type':[], 'Full ID':[], 'Person Name':[], 'Time':[], 'Outcome':[], '1v5 Current':[], '10V Current':[]})
    std = ColumnDataSource(data={'1v5 std':[], '1v5 mean':[], 'ten std':[], 'ten mean':[]})
    # custom javascript to be run to actually create the plotted data client side
    # all done in javascript so it runs on the website and can update without refreshing the page
    x = CustomJS(args=dict(hist_1v5=hist_data_1v5, hist_10v=hist_data_10v, data=data, view=view, dt=dt, std=std),code='''
const type_ids=[];
const full_ids=[];
const people=[];
const times=[];
const outcomes=[];
const current_1v5=[];
const current_10v=[];

const indices = view.filters[0].compute_indices(data);
let mask = new Array(data.data['1.5V Current'].length).fill(false);
[...indices].forEach((x)=>{mask[x] = true;})

for (let j = 0; j < data.get_length(); j++) {
    if (mask[j] == true){
        type_ids.push(data.data['Sub Type'][j])
        full_ids.push(data.data['Full ID'][j])
        people.push(data.data['Person Name'][j])
        times.push(data.data['Time'][j])
        outcomes.push(data.data['Outcome'][j])
        current_1v5.push(data.data['1.5V Current'][j])
        current_10v.push(data.data['10V Current'][j])
    }
}
const good_data_1v5 = data.data['1.5V Current'].filter((_,y)=>mask[y])
const good_data_10v = data.data['10V Current'].filter((_,y)=>mask[y])
let m_1v5 = Math.max(...good_data_1v5);
let min_1v5 = Math.min(...good_data_1v5);
let scale_1v5 = d3.scaleLinear().domain([min_1v5,m_1v5]).nice()

let m_10v = Math.max(...good_data_10v);
let min_10v = Math.min(...good_data_10v);
let scale_10v = d3.scaleLinear().domain([min_10v,m_10v]).nice()

let binner = d3.bin()

let d_1v5 = binner(good_data_1v5)
let right_1v5 = d_1v5.map(x=>x.x1)
let left_1v5 = d_1v5.map(x=>x.x0)
let bottom_1v5 = new Array(d_1v5.length).fill(0)
let top_1v5 = d_1v5.map(x=>x.length);
hist_1v5.data['right'] = right_1v5;
hist_1v5.data['left'] = left_1v5;
hist_1v5.data['bottom'] = bottom_1v5;
hist_1v5.data['top'] = top_1v5;
hist_1v5.change.emit()

let d_10v = binner(good_data_10v)
let right_10v = d_10v.map(x=>x.x1)
let left_10v = d_10v.map(x=>x.x0)
let bottom_10v = new Array(d_10v.length).fill(0)
let top_10v = d_10v.map(x=>x.length);
hist_10v.data['right'] = right_10v;
hist_10v.data['left'] = left_10v;
hist_10v.data['bottom'] = bottom_10v;
hist_10v.data['top'] = top_10v;
hist_10v.change.emit()

dt.data['Sub Type'] = type_ids;
dt.data['Full ID'] = full_ids;
dt.data['Person Name'] = people;
dt.data['Time'] = times;
dt.data['Outcome'] = outcomes;
dt.data['1v5 Current'] = current_1v5;
dt.data['10V Current'] = current_10v;
dt.change.emit()
std.data['1v5 mean'] = [d3.mean(good_data_1v5)];
std.data['1v5 std'] = [d3.deviation(good_data_1v5)];
std.data['ten mean'] = [d3.mean(good_data_10v)];
std.data['ten std'] = [d3.deviation(good_data_10v)];
std.change.emit()
''')
    for widget in widgets:
        widget.js_on_change('value', x)
    return hist_data_1v5, hist_data_10v, dt, std

# creates the webpage and plots the data
def Filter():
    # create a CDS with all the data to be used
    df_temp = AllData.merge(CD, on='Test ID', how='left')
    df = df_temp.dropna()
    ds = ColumnDataSource(df)

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
    columns = ['Major Type', 'Sub Type', 'Full ID', 'Person Name', 'Outcome', 'Start Date', 'End Date']
    data = [ds.data['Major Type'].tolist(), ds.data['Sub Type'].tolist(), ds.data['Full ID'].tolist(), ds.data['Person Name'].tolist(), ds.data['Outcome'], date_range, date_range]
    t = [multi_choice, multi_choice, multi_choice, multi_choice, multi_choice, start_date, end_date]
    
    # creates the figure objects
    p = figure(
        title='1.5V Current Drawn',
        x_axis_label='Current',
        y_axis_label='Number of Boards',
        tools='pan,wheel_zoom,box_zoom,reset,save',
        width = 925
        )

    q = figure(
        title='10V Current Drawn',
        x_axis_label='Current',
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
    hds_1v5, hds_10v, dt, std = Histogram(ds, view, widgets.values())
    # tells the figure object what data source to use
    p.quad(top='top', bottom='bottom', left='left', right='right', source=hds_1v5, color = colors[0])
    q.quad(top='top', bottom='bottom', left='left', right='right', source=hds_10v, color = colors[2])

    module_template = '''
<div>
<a href="module.py?full_id=<%= value %>"target="_blank">
<%= value %>
</a>
</div> 
'''
    board = HTMLTemplateFormatter(template=module_template)

    # creates data tables
    table_columns = [
                    TableColumn(field='Sub Type', title='Sub Type'),
                    TableColumn(field='Full ID', title='Full ID', formatter=board),
                    TableColumn(field='Person Name', title='Person Name'),
                    TableColumn(field='Time', title='Date', formatter=DateFormatter()),
                    TableColumn(field='Outcome', title='Outcome'),
                    TableColumn(field='1v5 Current', title='1.5V Current'),
                    TableColumn(field='10V Current', title='10V Current'),
                    ]
    data_table = DataTable(source=dt, columns=table_columns, width=925, autosize_mode='fit_columns')
    table_columns_2 = [
                    TableColumn(field='1v5 mean', title='1.5V Mean'),
                    TableColumn(field='1v5 std', title='1.5V Standard Deviation'),
                    TableColumn(field='ten mean', title='10V Mean'),
                    TableColumn(field='ten std', title='10V Standard Deviation'),
                    ]
    data_table_2 = DataTable(source=std, columns=table_columns_2, autosize_mode='fit_columns')

    w = [*widgets.values()]

    subtypes = {}
    for major in np.unique(ds.data['Major Type'].tolist()).tolist():
        subtypes[major] = np.unique(df.query('`Major Type` == @major')['Sub Type'].values.tolist()).tolist()
    serial_numbers = {}
    for s in np.unique(ds.data['Sub Type'].tolist()).tolist():
        serial_numbers[s] = np.unique(df.query('`Sub Type` == @s')['Full ID'].values.tolist()).tolist()
    
    all_subtypes = np.unique(ds.data['Sub Type'].tolist()).tolist()
    all_serials = np.unique(ds.data['Full ID'].tolist()).tolist()

    update_options = CustomJS(args=dict(subtypes=subtypes, widget=w[1], all_subtypes=all_subtypes), code=('''
if (this.value.length != 0) {
    widget.options = subtypes[this.value]
} else {
    widget.options = all_subtypes
}
'''))
    w[0].js_on_change('value', update_options)
    
    update_options_2 = CustomJS(args=dict(serial_numbers=serial_numbers, widget=w[2], all_serials=all_serials), code=('''
if (this.value.length != 0) {
    widget.options = serial_numbers[this.value]
} else {
    widget.options = all_serials
}
'''))
    w[1].js_on_change('value', update_options_2)

    # gets the second half of the webpage where the residuals are displayed
    # since it's a separate function, the data can be filtered separately
    #layout = Gaussian()
    #converts the bokeh items to json and sends them to the webpage
    plot_json = json.dumps(json_item(row(column(row(w[0:3]), row(w[3:5]), row(w[5:]), p, q, data_table, data_table_2))))
    return plot_json


################################################################################################################

def Gaussian2(data, view, widgets, serial_numbers, n_sigma):
    hist_1v5 = ColumnDataSource(data={'top':[], 'bottom':[], 'left':[], 'right':[]})
    hist_10v = ColumnDataSource(data={'top':[], 'bottom':[], 'left':[], 'right':[]})
    pf_1v5 = ColumnDataSource(data={'pass':[], 'fail':[], 'x':['Fail', 'Pass']})
    pf_10v = ColumnDataSource(data={'pass':[], 'fail':[], 'x':['Fail', 'Pass']})
    td = ColumnDataSource(data={'Serial Number':[], 'Deviation':[], 'Pass/Fail':[]})
    x = CustomJS(args=dict(hist_1v5=hist_1v5, hist_10v=hist_10v, data=data, view=view, serial_numbers=serial_numbers, n_sigma=n_sigma, pf_1v5=pf_1v5, pf_10v=pf_10v, td=td),code='''
const residules_1v5 = [];

var chis_1v5 = {};
for (let sn = 0; sn < serial_numbers.length; sn++) {
    chis_1v5[serial_numbers[sn]] = [];
} 

const indices = view.filters[0].compute_indices(data);
let mask = new Array(data.data['1.5V Current'].length).fill(false);
[...indices].forEach((x)=>{mask[x] = true;})

const good_data_1v5 = data.data['1.5V Current'].filter((_,y)=>mask[y])
let mean_1v5 = d3.mean(good_data_1v5)
let std_1v5 = d3.deviation(good_data_1v5)
for (let sn = 0; sn < serial_numbers.length; sn++) {
    const indices = view.filters[0].compute_indices(data);
    let mask_sn = new Array(data.data['1.5V Current'].length).fill(false);
    [...indices].forEach((x)=>{mask_sn[x] = true;})
    for (let j = 0; j < data.get_length(); j++) {
        if (mask_sn[j] == true && data.data['Full ID'][j] == serial_numbers[sn]){
            mask_sn[j] = true;
            let x = data.data['1.5V Current'][j] - mean_1v5;
            if (std_1v5 == 0) {
                let chi = 0;
                residules_1v5.push(chi)
            } else {
                let chi = x/std_1v5;
                residules_1v5.push(chi)    
            }
        } else {
            mask_sn[j] = false;
        }
    }
    const good_data_sn = data.data['1.5V Current'].filter((_,y)=>mask_sn[y])
    let mean_sn = d3.mean(good_data_sn)
    let y = mean_sn - mean_1v5;
    let chi_sn = y/std_1v5;
    if (isNaN(chi_sn)) {
        chis_1v5[serial_numbers[sn]].push(0)
    } else {
        chis_1v5[serial_numbers[sn]].push(Math.abs(chi_sn))
    }
}

let binner = d3.bin()
let d_1v5 = binner(residules_1v5)
let right_1v5 = d_1v5.map(x=>x.x1)
let left_1v5 = d_1v5.map(x=>x.x0)
let bottom_1v5 = new Array(d_1v5.length).fill(0)
let top_1v5 = d_1v5.map(x=>x.length);

const residules_10v = [];

var chis_10v = {};
for (let sn = 0; sn < serial_numbers.length; sn++) {
    chis_10v[serial_numbers[sn]] = [];
} 

const good_data_10v = data.data['10V Current'].filter((_,y)=>mask[y])
let mean_10v = d3.mean(good_data_10v)
let std_10v = d3.deviation(good_data_10v)
for (let sn = 0; sn < serial_numbers.length; sn++) {
    const indices = view.filters[0].compute_indices(data);
    let mask_sn = new Array(data.data['10V Current'].length).fill(false);
    [...indices].forEach((x)=>{mask_sn[x] = true;})
    for (let j = 0; j < data.get_length(); j++) {
        if (mask_sn[j] == true && data.data['Full ID'][j] == serial_numbers[sn]){
            mask_sn[j] = true;
            let x = data.data['10V Current'][j] - mean_10v;
            if (std_10v == 0) {
                let chi = 0;
                residules_10v.push(chi)
            } else {
                let chi = x/std_10v;
                residules_10v.push(chi)    
            }
        } else {
            mask_sn[j] = false;
        }
    }
    const good_data_sn = data.data['10V Current'].filter((_,y)=>mask_sn[y])
    let mean_sn = d3.mean(good_data_sn)
    let y = mean_sn - mean_10v;
    let chi_sn = y/std_10v;
    if (isNaN(chi_sn)) {
        chis_10v[serial_numbers[sn]].push(0)
    } else {
        chis_10v[serial_numbers[sn]].push(Math.abs(chi_sn))
    }
}

let d_10v = binner(residules_10v)
let right_10v = d_10v.map(x=>x.x1)
let left_10v = d_10v.map(x=>x.x0)
let bottom_10v = new Array(d_10v.length).fill(0)
let top_10v = d_10v.map(x=>x.length);

hist_1v5.data['right'] = right_1v5;
hist_1v5.data['left'] = left_1v5;
hist_1v5.data['bottom'] = bottom_1v5;
hist_1v5.data['top'] = top_1v5;
hist_1v5.change.emit()

hist_10v.data['right'] = right_10v;
hist_10v.data['left'] = left_10v;
hist_10v.data['bottom'] = bottom_10v;
hist_10v.data['top'] = top_10v;
hist_10v.change.emit()

let t_pass_1v5 = 0;
let t_fail_1v5 = 0;
let t_pass_10v = 0;
let t_fail_10v = 0;
const sn_td = [];
const chi_td_1v5 = [];
const pf_td_1v5 = [];
const chi_td_10v = [];
const pf_td_10v = [];
for (let sn = 0; sn < serial_numbers.length; sn++) {
    let pass_1v5 = 0;
    let fail_1v5 = 0;
    for (let c = 0; c < chis_1v5[serial_numbers[sn]].length; c++) {
        let chi_i = chis_1v5[serial_numbers[sn]][c]
        if (chi_i <= n_sigma.value) {
            pass_1v5 = pass_1v5 + 1;
            pf_td_1v5.push('PASS')
        } else {
            fail_1v5 = fail_1v5 + 1;
            pf_td_1v5.push('FAIL')
        }
        chi_td_1v5.push(chi_i)
    }
    if (fail_1v5 == 0) {
        t_pass_1v5 = t_pass_1v5 + 1;
    } else {
        t_fail_1v5 = t_fail_1v5 + 1;
    }

    let pass_10v = 0;
    let fail_10v = 0;
    for (let c = 0; c < chis_10v[serial_numbers[sn]].length; c++) {
        let chi_i = chis_10v[serial_numbers[sn]][c]
        if (chi_i <= n_sigma.value) {
            pass_10v = pass_10v + 1;
            pf_td_10v.push('PASS')
        } else {
            fail_10v = fail_10v + 1;
            pf_td_10v.push('FAIL')
        }
        chi_td_10v.push(chi_i)
    }
    if (fail_10v == 0) {
        t_pass_10v = t_pass_10v + 1;
    } else {
        t_fail_10v = t_fail_10v + 1;
    }

    sn_td.push(serial_numbers[sn])
}
pf_1v5.data['pass'] = [0, t_pass_1v5];
pf_1v5.data['fail'] = [t_fail_1v5, 0];
pf_1v5.change.emit()

pf_10v.data['pass'] = [0, t_pass_10v];
pf_10v.data['fail'] = [t_fail_10v, 0];
pf_10v.change.emit()

td.data['Serial Number'] = sn_td;
td.data['1.5V Deviation'] = chi_td_1v5;
td.data['1.5V Pass/Fail'] = pf_td_1v5;
td.data['10V Deviation'] = chi_td_10v;
td.data['10V Pass/Fail'] = pf_td_10v;
td.change.emit()
    ''')
    for widget in widgets:
        widget.js_on_change('value', x)
    n_sigma.js_on_change('value', x)
    return hist_1v5, hist_10v, pf_1v5, pf_10v, td

def Gaussian():
    df_temp = AllData.merge(CD, on='Test ID', how='left')
    df = df_temp.dropna()
    ds = ColumnDataSource(df)
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
    columns = ['Major Type', 'Sub Type', 'Full ID', 'Outcome', 'Start Date', 'End Date']
    data = [ds.data['Major Type'].tolist(), ds.data['Sub Type'], ds.data['Full ID'].tolist(), ds.data['Outcome'], date_range, date_range]
    t = [multi_choice, multi_choice, multi_choice, multi_choice, start_date, end_date]

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

    hist_1v5, hist_10v, pf_1v5, pf_10v, td = Gaussian2(ds, view, widgets.values(), serial_numbers, n_sigma)
    p_1 = figure(
        title='Residual Distribution for 1.5V Current',
        x_axis_label='# of Standard Deviations from Mean',
        y_axis_label='Number of Boards',
        tools='pan,wheel_zoom,box_zoom,reset,save',
        width = 925
        )

    p_1.quad(top='top', bottom='bottom', left='left', right='right', source=hist_1v5, color = colors[0])

    q_1 = figure(
        title='Pass vs Fail',
        x_range=pf_1v5.data['x'],
        x_axis_label='',
        y_axis_label='Number of Boards',
        tools='pan,wheel_zoom,box_zoom,reset,save',
        width = 925
        )

    q_1.vbar(x='x', top='pass', source=pf_1v5, color=colors[2], width=0.8)
    q_1.vbar(x='x', top='fail', source=pf_1v5, color=colors[3], width=0.8)

    p_2 = figure(
        title='Residual Distribution for 1.5V Current',
        x_axis_label='# of Standard Deviations from Mean',
        y_axis_label='Number of Boards',
        tools='pan,wheel_zoom,box_zoom,reset,save',
        width = 925
        )

    p_2.quad(top='top', bottom='bottom', left='left', right='right', source=hist_10v, color = colors[0])

    q_2 = figure(
        title='Pass vs Fail',
        x_range=pf_10v.data['x'],
        x_axis_label='',
        y_axis_label='Number of Boards',
        tools='pan,wheel_zoom,box_zoom,reset,save',
        width = 925
        )

    q_2.vbar(x='x', top='pass', source=pf_10v, color=colors[2], width=0.8)
    q_2.vbar(x='x', top='fail', source=pf_10v, color=colors[3], width=0.8)

    table_columns = [
                    TableColumn(field='Serial Number', title='Full ID'),
                    TableColumn(field='1.5V Deviation', title='# of Standard Deviations 1.5V'),
                    TableColumn(field='1.5V Pass/Fail', title='Pass/Fail 1.5V'),
                    TableColumn(field='10V Deviation', title='# of Standard Deviations 10V'),
                    TableColumn(field='10V Pass/Fail', title='Pass/Fail 10V'),
                    ]
    data_tables = DataTable(source=td, columns=table_columns, autosize_mode='fit_columns')
            
    w = [*widgets.values()]

    subtypes = {}
    for major in np.unique(ds.data['Major Type'].tolist()).tolist():
        subtypes[major] = np.unique(df.query('`Major Type` == @major')['Sub Type'].values.tolist()).tolist()
    serial_numbers = {}
    for s in np.unique(ds.data['Sub Type'].tolist()).tolist():
        serial_numbers[s] = np.unique(df.query('`Sub Type` == @s')['Full ID'].values.tolist()).tolist()
    
    all_subtypes = np.unique(ds.data['Sub Type'].tolist()).tolist()
    all_serials = np.unique(ds.data['Full ID'].tolist()).tolist()

    update_options = CustomJS(args=dict(subtypes=subtypes, widget=w[1], all_subtypes=all_subtypes), code=('''
if (this.value.length != 0) {
    widget.options = subtypes[this.value]
} else {
    widget.options = all_subtypes
}
'''))
    w[0].js_on_change('value', update_options)
    
    update_options_2 = CustomJS(args=dict(serial_numbers=serial_numbers, widget=w[2], all_serials=all_serials), code=('''
if (this.value.length != 0) {
    widget.options = serial_numbers[this.value]
} else {
    widget.options = all_serials
}
'''))
    w[1].js_on_change('value', update_options_2)

    layout = column(row(w[0:3]), row([w[3]] + [n_sigma]), row(w[4:]), p_1, q_1, p_2, q_2, data_tables)
    return layout



