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
from bokeh.transform import dodge
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

tempGPIO = pd.read_csv(mTD.get_gpio_functionality())
GPIO = tempGPIO.dropna()


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
def Histogram(data, view, widgets, pins, modules):
    # creates a dictionary for the histogram data to go in
    hist_data = {}
    dt = {}
    for i in modules:
        hist_data[i] = ColumnDataSource(data={'x': pins, 'Rate': []})
    
    # creates a dictionary for the filtered data to be put in data tables
    dt = ColumnDataSource(data={'Sub Type':[], 'Full ID':[], 'Person Name':[], 'Time':[], 'Outcome':[], 'Pin':[], 'Read':[], 'Write':[]})
    # custom javascript to be run to actually create the plotted data client side
    # all done in javascript so it runs on the website and can update without refreshing the page
    x = CustomJS(args=dict(hist=hist_data, data=data, view=view, dt=dt, pins=pins),code='''
const type_ids=[];
const full_ids=[];
const people=[];
const times=[];
const outcomes=[];
const channels_2=[];
const reads=[];
const writes=[];
const rp_rates=[];
const rf_rates=[];
const wp_rates=[];
const wf_rates=[];
for (let k = 0; k < pins.length; k++) {
    const indices = view.filters[0].compute_indices(data);
    let mask = new Array(data.data['Read'].length).fill(false);
    [...indices].forEach((x)=>{mask[x] = true;})

    let read_pass = 0;
    let read_fail = 0;
    let write_pass = 0;
    let write_fail = 0;

    for (let j = 0; j < data.get_length(); j++) {
        if (mask[j] == true && data.data['Pin'][j] == pins[k]){
            type_ids.push(data.data['Sub Type'][j])
            full_ids.push(data.data['Full ID'][j])
            people.push(data.data['Person Name'][j])
            times.push(data.data['Time'][j])
            outcomes.push(data.data['Outcome'][j])
            channels_2.push(data.data['Pin'][j])

            if (data.data['Read'][j] == 1){
                read_pass = read_pass + 1;
                reads.push('Pass')
            } else {
                read_fail = read_fail + 1;
                reads.push('Fail')
            }

            if (data.data['Write'][j] == 1){
                write_pass = write_pass + 1;
                writes.push('Pass')
            } else {
                write_fail = write_fail + 1;
                writes.push('Fail')
            }
        }
    }
    rp_rates.push(read_pass)
    rf_rates.push(read_fail)
    wp_rates.push(write_pass)
    wf_rates.push(write_fail)
}
hist['Failed Read'].data['Rate'] = rf_rates;
hist['Failed Read'].change.emit()
hist['Passed Read'].data['Rate'] = rp_rates;
hist['Passed Read'].change.emit()
hist['Failed Write'].data['Rate'] = wf_rates;
hist['Failed Write'].change.emit()
hist['Passed Write'].data['Rate'] = wp_rates;
hist['Passed Write'].change.emit()

dt.data['Sub Type'] = type_ids;
dt.data['Full ID'] = full_ids;
dt.data['Person Name'] = people;
dt.data['Time'] = times;
dt.data['Outcome'] = outcomes;
dt.data['Pin'] = channels_2;
dt.data['Read'] = reads;
dt.data['Write'] = writes;
dt.change.emit()

    ''')
    for widget in widgets:
        widget.js_on_change('value', x)
    return hist_data, dt

# creates the webpage and plots the data
def Filter():
    # create a CDS with all the data to be used
    df_temp = AllData.merge(GPIO, on='Test ID', how='left')
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
    pins = np.unique(ds.data['Pin']).tolist()
    modules = ['Failed Read', 'Passed Read', 'Failed Write', 'Passed Write']
    # widget titles and data for those widgets has to be manually entered, as well as the type
    columns = ['Major Type', 'Sub Type', 'Full ID', 'Person Name', 'Outcome', 'Start Date', 'End Date']
    data = [ds.data['Major Type'].tolist(), ds.data['Sub Type'].tolist(), ds.data['Full ID'].tolist(), ds.data['Person Name'].tolist(), ds.data['Outcome'], date_range, date_range]
    t = [multi_choice, multi_choice, multi_choice, multi_choice, multi_choice, start_date, end_date]
    # the phases are the different phases for which the bit errors are measured

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
    hds, dt = Histogram(ds, view, widgets.values(), pins, modules)
    # creates the figure object
    p = figure(
        title='GPIO Functionality',
        x_axis_label='Pin',        
        x_range=hds[modules[0]].data['x'],
        y_axis_label='# of occurances',
        tools='pan,wheel_zoom,box_zoom,reset,save',
        width = 1850
        )
    place = [-0.24, -0.08, 0.08, 0.24]
    colors = [d3['Category10'][10][1], d3['Category10'][10][0], d3['Category10'][10][3], d3['Category10'][10][2]]
    for i in range(len(modules)):
        # tells the figure object what data source to use
        # dodge allows for plotting multiple elements side by side at the same value
        # place determines how far to shift the bar
        p.vbar(x=dodge('x', place[i], range=p.x_range), top='Rate', source=hds[modules[i]], color=colors[i], width=0.15, legend_label=modules[i])
    
    p.x_range.range_padding = 0.1

    # creates data tables
    table_columns = [
                    TableColumn(field='Sub Type', title='Sub Type'),
                    TableColumn(field='Full ID', title='Full ID'),
                    TableColumn(field='Person Name', title='Person Name'),
                    TableColumn(field='Time', title='Date', formatter=DateFormatter()),
                    TableColumn(field='Outcome', title='Outcome'),
                    TableColumn(field='Pin', title='Pin'),
                    TableColumn(field='Read', title='Read'),
                    TableColumn(field='Write', title='Write'),
                    ]
    data_table = DataTable(source=dt, columns=table_columns, width=925, autosize_mode='fit_columns')

    p.legend.click_policy='hide'
    p.legend.label_text_font_size = '8pt'
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

    #converts the bokeh items to json and sends them to the webpage
    plot_json = json.dumps(json_item(row(column(row(w[0:4]), row(w[4:]), p, data_table))))
    return plot_json


