#!/usr/bin/python3

# framework for creating dynamic plots
import sys
import pandas as pd
import csv
import cgitb
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
from bokeh.transform import dodge
import json

cgitb.enable()

#import all data from csv files and set it up properly
TestData = pd.read_csv('./static/files/Test.csv', parse_dates=['Time'])
BoardData = pd.read_csv('./static/files/Board.csv')
PeopleData = pd.read_csv('./static/files/People.csv')
mergetemp = TestData.merge(BoardData, on='Board ID', how='left')
AllData = mergetemp.merge(PeopleData, on='Person ID', how='left')
AllData = AllData.rename(columns={'Successful':'Outcome'})
AllData['Outcome'] = AllData['Outcome'].replace(0, 'Unsuccessful')
AllData['Outcome'] = AllData['Outcome'].replace(1, 'Successful')

tempEC = pd.read_csv('./static/files/I2C.csv')
EC = tempEC.dropna()


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
def Histogram(data, view, widgets, modules, channels):
    # creates a dictionary for the histogram data to go in
    hist_data = {}
    dt = {}
    for i in channels:
        hist_data[i] = ColumnDataSource(data={'x': modules, 'Bit Errors': []})
    
    # creates a dictionary for the filtered data to be put in data tables
    dt = ColumnDataSource(data={'Type ID':[], 'Full ID':[], 'Person Name':[], 'Time':[], 'Outcome':[], 'Connector':[], 'Channel':[], 'Bit Errors':[]})
    # custom javascript to be run to actually create the plotted data client side
    # all done in javascript so it runs on the website and can update without refreshing the page
    x = CustomJS(args=dict(hist=hist_data, data=data, view=view, modules=modules, dt=dt, channels=channels),code='''
const type_ids=[];
const full_ids=[];
const people=[];
const times=[];
const outcomes=[];
const fibers_2 = [];
const pathways=[];
const res=[];
for (let k = 0; k < channels.length; k++) {
    const bit_errors = [];
    for (let i = 0; i < modules.length; i++) {
        const indices = view.filters[0].compute_indices(data);
        let mask = new Array(data.data['Bit Errors'].length).fill(false);
        [...indices].forEach((x)=>{mask[x] = true;})
        for (let j = 0; j < data.get_length(); j++) {
            if (data.data['Connector'][j] == modules[i] && mask[j] == true && data.data['Channel'][j] == channels[k]){
                mask[j] = true;
                type_ids.push(data.data['Type ID'][j])
                full_ids.push(data.data['Full ID'][j])
                people.push(data.data['Person Name'][j])
                times.push(data.data['Time'][j])
                outcomes.push(data.data['Outcome'][j])
                fibers_2.push(data.data['Connector'][j])
                pathways.push(data.data['Channel'][j])
                res.push(data.data['Bit Errors'][j])
            } else {
                mask[j] = false;
            }
        }
        const good_data = data.data['Bit Errors'].filter((_,y)=>mask[y])
        bit_errors.push(d3.mean(good_data))
    }
    // rather than binning, just add bit errors an array so that a bar will be plotted with that value
    hist[channels[k]].data['Bit Errors'] = bit_errors;
    hist[channels[k]].change.emit()
}
dt.data['Type ID'] = type_ids;
dt.data['Full ID'] = full_ids;
dt.data['Person Name'] = people;
dt.data['Time'] = times;
dt.data['Outcome'] = outcomes;
dt.data['Phase'] = pathways;
dt.data['Bit Errors'] = res;
dt.data['Fiber'] = fibers_2;
dt.change.emit()
    ''')
    for widget in widgets:
        widget.js_on_change('value', x)
    return hist_data, dt

# creates the webpage and plots the data
def Filter():
    # create a CDS with all the data to be used
    df_temp = AllData.merge(EC, on='Test ID', how='left')
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
    # modules are DAQ, East, West
    modules = np.unique(ds.data['Connector'].tolist()).tolist()
    # widget titles and data for those widgets has to be manually entered, as well as the type
    columns = ['Type ID', 'Full ID', 'Person Name', 'Outcome', 'Start Date', 'End Date']
    data = [ds.data['Type ID'].tolist(), ds.data['Full ID'].tolist(), ds.data['Person Name'].tolist(), ds.data['Outcome'], date_range, date_range]
    t = [multi_choice, multi_choice, multi_choice, multi_choice, start_date, end_date]

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
    # channels are 0, 1, 2 
    temp_channels = np.unique(ds.data['Channel'].tolist()).tolist()
    channels = []
    for t in temp_channels:
        # channels come in as integers so need to change to string
        channels.append(str(t))
    # calls the function that creates the plotting data
    hds, dt = Histogram(ds, view, widgets.values(), modules, channels)
    # creates the figure object
    p = figure(
        title='I2C',
        x_axis_label='Phase',        
        x_range=modules,
        y_axis_label='Number of Bit Errors (x100k)',
        tools='pan,wheel_zoom,box_zoom,reset,save',
        width = 925
        )
    place = [-0.2, 0, 0.2]
    for i in range(len(channels)):
        # tells the figure object what data source to use
        # dodge allows for plotting multiple elements side by side at the same value
        # place determines how far to shift the bar
        p.vbar(x=dodge('x', place[i], range=p.x_range), top='Bit Errors', source=hds[channels[i]], color=colors[i], width=0.20, legend_label=channels[i])
    
    p.x_range.range_padding = 0.1

    # creates data tables
    table_columns = [
                    TableColumn(field='Type ID', title='Type ID'),
                    TableColumn(field='Full ID', title='Full ID'),
                    TableColumn(field='Person Name', title='Person Name'),
                    TableColumn(field='Time', title='Date', formatter=DateFormatter()),
                    TableColumn(field='Outcome', title='Outcome'),
                    TableColumn(field='Fiber', title='Fiber'),
                    TableColumn(field='Phase', title='Phase'),
                    TableColumn(field='Bit Errors', title='Bit Errors'),
                    ]
    data_table = DataTable(source=dt, columns=table_columns, width=925, autosize_mode='fit_columns')

    p.legend.click_policy='hide'
    p.legend.label_text_font_size = '8pt'
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
    plot_json = json.dumps(json_item(row(column(row(w[0:3]), row(w[3:6]), p, data_table), layout)))
    return plot_json


################################################################################################################

def Gaussian2(data, view, widgets, serial_numbers, modules, n_sigma, channels):
    hist = {}
    pf = {}
    td = {}
    for i in modules:
        hist[i] = ColumnDataSource(data={'top':[], 'bottom':[], 'left':[], 'right':[]})
        pf[i] = ColumnDataSource(data={'pass':[], 'fail':[], 'x':['Fail', 'Pass']})
        td[i] = ColumnDataSource(data={'Serial Number':[], 'Module':[], 'Deviation':[], 'Pass/Fail':[]})
    x = CustomJS(args=dict(hist=hist, data=data, view=view, serial_numbers=serial_numbers, modules=modules, n_sigma=n_sigma, pf=pf, td=td, channels=channels),code='''
for (let i = 0; i < modules.length; i++) {
    const residules = [];

    var chis = {};
    for (let sn = 0; sn < serial_numbers.length; sn++) {
        chis[serial_numbers[sn]] = [];
    } 
    for (let k = 0; k < channels.length; k++) {
        const indices = view.filters[0].compute_indices(data);
        let mask = new Array(data.data['Bit Errors'].length).fill(false);
        [...indices].forEach((x)=>{mask[x] = true;})

        for (let j = 0; j < data.get_length(); j++) {
            if (mask[j] == true && data.data['Channel'][j] == channels[k] && data.data['Connector'][j] == modules[i]){
                mask[j] = true;
            } else {
                mask[j] = false;
            }
        }
        const good_data = data.data['Bit Errors'].filter((_,y)=>mask[y])
        let mean = d3.mean(good_data)
        let std = d3.deviation(good_data)
        for (let sn = 0; sn < serial_numbers.length; sn++) {
            const indices = view.filters[0].compute_indices(data);
            let mask_sn = new Array(data.data['Bit Errors'].length).fill(false);
            [...indices].forEach((x)=>{mask_sn[x] = true;})
            for (let j = 0; j < data.get_length(); j++) {
                if (mask_sn[j] == true && data.data['Channel'][j] == channels[k] && data.data['Connector'][j] == modules[i] && data.data['Full ID'][j] == serial_numbers[sn]){
                    mask_sn[j] = true;
                    let x = data.data['Bit Errors'][j] - mean;
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
            const good_data_sn = data.data['Bit Errors'].filter((_,y)=>mask_sn[y])
            let mean_sn = d3.mean(good_data_sn)
            let y = mean_sn - mean;
            let chi_sn = y/std;
            if (isNaN(chi_sn)) {
                chis[serial_numbers[sn]].push(0)
            } else {
                chis[serial_numbers[sn]].push(Math.abs(chi_sn))
            }
        }
    }

    let binner = d3.bin()
    let d = binner(residules)
    let right = d.map(x=>x.x1)
    let left = d.map(x=>x.x0)
    let bottom = new Array(d.length).fill(0)
    let top = d.map(x=>x.length);

    hist[modules[i]].data['right'] = right;
    hist[modules[i]].data['left'] = left;
    hist[modules[i]].data['bottom'] = bottom;
    hist[modules[i]].data['top'] = top;
    hist[modules[i]].change.emit()

    let t_pass = 0;
    let t_fail = 0;
    const sn_td = [];
    const mod_td = [];
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
            mod_td.push(channels[c])
            chi_td.push(chi_i)
        }
        if (fail == 0) {
            t_pass = t_pass + 1;
        } else {
            t_fail = t_fail + 1;
        }
    }
    pf[modules[i]].data['pass'] = [0, t_pass];
    pf[modules[i]].data['fail'] = [t_fail, 0];
    pf[modules[i]].change.emit()

    td[modules[i]].data['Serial Number'] = sn_td;
    td[modules[i]].data['Module'] = mod_td;
    td[modules[i]].data['Deviation'] = chi_td;
    td[modules[i]].data['Pass/Fail'] = pf_td;
    td[modules[i]].change.emit()
}
    ''')
    for widget in widgets:
        widget.js_on_change('value', x)
    n_sigma.js_on_change('value', x)
    return hist, pf, td

def Gaussian():
    df_temp = AllData.merge(EC, on='Test ID', how='left')
    df_temp = df_temp.dropna()
    ds = ColumnDataSource(df_temp)
    serial_numbers = np.unique(ds.data['Full ID'].tolist()).tolist()
    # modules are DAQ, East, West
    modules = np.unique(ds.data['Connector'].tolist()).tolist()

    # channels are 0, 1, 2
    temp_channels = np.unique(ds.data['Channel'].tolist()).tolist()
    channels = []
    for t in temp_channels:
        channels.append(str(t))

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
    data = [ds.data['Type ID'].tolist(), ds.data['Full ID'], ds.data['Outcome'], date_range, date_range]
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

    hist, pf, td = Gaussian2(ds, view, widgets.values(), serial_numbers, modules, n_sigma, channels)
    plots = {}
    pf_plots = {}
    tables = {}
    for m in modules:
        p = figure(
            title='Residual Distribution for ' + m,
            x_axis_label='# of Standard Deviations from Mean',
            y_axis_label='Number of Boards',
            tools='pan,wheel_zoom,box_zoom,reset,save',
            width = 925
            )

        p.quad(top='top', bottom='bottom', left='left', right='right', source=hist[m], color = colors[0])
        p.visible = False
        plots[m] = p

        q = figure(
            title='Pass vs Fail for ' + m,
            x_range=pf[m].data['x'],
            x_axis_label='',
            y_axis_label='Number of Boards',
            tools='pan,wheel_zoom,box_zoom,reset,save',
            width = 925
            )

        q.vbar(x='x', top='pass', source=pf[m], color=colors[2], width=0.8)
        q.vbar(x='x', top='fail', source=pf[m], color=colors[3], width=0.8)
        q.visible = False
        pf_plots[m] = q

        table_columns = [
                        TableColumn(field='Serial Number', title='Full ID'),
                        TableColumn(field='Module', title='Clock'),
                        TableColumn(field='Deviation', title='# of Standard Deviations'),
                        TableColumn(field='Pass/Fail', title='Pass/Fail'),
                        ]
        data_table = DataTable(source=td[m], columns=table_columns, autosize_mode='fit_columns')
        data_table.visible = False
        tables[m] = data_table
            
    display_plot = CustomJS(args=dict(plots=plots, widgets=pf_plots, tables=tables), code=('''
for (let [name,plot] of Object.entries(plots)){
    if (name == this.value){
        plot.visible = true
    } else {
        plot.visible = false
    }
}
for (let [name,widget] of Object.entries(widgets)){
    if (name == this.value){
        widget.visible = true
    } else {
        widget.visible = false
    }
}
for (let [name,widget] of Object.entries(tables)){
    if (name == this.value){
        widget.visible = true
    } else {
        widget.visible = false
    }
}
'''))
    
    select = Select(title='Connector', options=modules)
    select.js_on_change('value', display_plot)

    w = [*widgets.values()]
    subtypes = np.unique(ds.data['Type ID'].tolist()).tolist()
    serial_numbers = {}
    for s in subtypes:
        serial_numbers[s] = np.unique(df_temp.query('`Type ID` == @s')['Full ID'].values.tolist()).tolist()
    update_options = CustomJS(args=dict(serial_numbers=serial_numbers, widget=w[1]), code=('''
widget.options = serial_numbers[this.value]
'''))
    w[0].js_on_change('value', update_options)

    # column and row objects only take it lists, need to make arguments lists
    layout = column(row(w[0:2] + [select]), row(w[2:5]), row([n_sigma]), column(list(plots.values())), column(list(pf_plots.values())), column(list(tables.values())))
    return layout

