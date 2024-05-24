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

# rename columns and stack the dataframe for better formatting
tempI2C = pd.read_csv('./static/files/I2C_ReadWrite_Test_Data.csv')
tempI2C = tempI2C.set_index('Test ID')
tempI2C = tempI2C.rename(columns={'Correct at Module 1':'Module 1'})
tempI2C = tempI2C.rename(columns={'Correct at Module 2':'Module 2'})
tempI2C = tempI2C.rename(columns={'Correct at Module 3':'Module 3'})
I2C = tempI2C.stack()
I2C = I2C.reset_index()
I2C = I2C.rename(columns={0:'Checks'})
I2C = I2C.dropna()

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

#create a color pallete to be used on graphs
colors = [d3['Category10'][10][0], d3['Category10'][10][1], d3['Category10'][10][2], d3['Category10'][10][3], d3['Category10'][10][4], d3['Category10'][10][5], d3['Category10'][10][6], d3['Category10'][10][7], d3['Category10'][10][8], d3['Category10'][10][9], brewer['Accent'][8][0], brewer['Accent'][8][3], brewer['Dark2'][8][0], brewer['Dark2'][8][2], brewer['Dark2'][8][3], brewer['Dark2'][8][4], brewer['Dark2'][8][5], brewer['Dark2'][8][6]]


def Histogram(columns, data, view, widgets, modules):
    # one cds for each module
    hist_data0 = ColumnDataSource(data={'top':[], 'x':['-1', '10000']})
    hist_data1 = ColumnDataSource(data={'top':[], 'x':['-1', '10000']})
    hist_data2 = ColumnDataSource(data={'top':[], 'x':['-1', '10000']})
    x = CustomJS(args=dict(col=columns, hist0=hist_data0, hist1=hist_data1, hist2=hist_data2, data=data, view=view, modules=modules),code='''
// iterate over modules
for (let i = 0; i < modules.length; i++) {
    const indices = view.filters[0].compute_indices(data);
    let mask = new Array(data.data[col].length).fill(false);
    [...indices].forEach((x)=>{mask[x] = true;})
    for (let j = 0; j < data.get_length(); j++) {
        if (data.data['level_1'][j] == modules[i] && mask[j] == true){
            mask[j] = true;
        } else {
            mask[j] = false;
        }
    }
    // filter data and determine pass or fail
    const good_data = data.data[col].filter((_,y)=>mask[y])
    let s_counts = 0;
    let u_counts = 0;
    for (let j = 0; j < good_data.length; j++) {
        if (good_data[j] == 10000){
            s_counts++;
        } else if (good_data[j] == -1){
            u_counts++;
        }
    }
    // update correct data source
    let top = [u_counts, s_counts]; 
    if (i == 0) {
        hist0.data["top"] = top
        hist0.change.emit()
    }
    if (i == 1) {
        hist1.data["top"] = top
        hist1.change.emit()
    }
    if (i == 2) {
        hist2.data["top"] = top
        hist2.change.emit()
    }
}
    ''')
    for widget in widgets:
        widget.js_on_change('value', x)
    return hist_data0, hist_data1, hist_data2


def Filter():
    df_temp = AllData.merge(I2C, on='Test ID', how='left')
    df_temp = df_temp.dropna()
    newdf = pd.DataFrame(df_temp)
    ds = ColumnDataSource(newdf)
    mc_widgets = {}
    dr_widgets = {}
    multi_choice = (lambda x,y: MultiChoice(options=x, value=[], title=y), 'value')
    start_date = (lambda x,y,z: DatePicker(min_date=x,max_date=y, value='2023-03-14', title=z), 'value')
    today = datetime.date.today()
    end_date = (lambda x,y,z: DatePicker(min_date=x,max_date=y, value=today, title=z), 'value')
    min_date = pd.Timestamp((min(ds.data['Time']))).date()
    date_range = []
    while min_date <= today:
        date_range.append(min_date)
        min_date += datetime.timedelta(days=1)
    modules = ['Module 1', 'Module 2', 'Module 3']
    columns = ['Type ID', 'Full ID', 'Person Name', 'Outcome', 'Start Date', 'End Date']
    data = [ds.data['Type ID'].tolist(), ds.data['Full ID'].tolist(), ds.data['Person Name'].tolist(), ds.data['Outcome'], date_range, date_range]
    t = [multi_choice, multi_choice, multi_choice, multi_choice, start_date, end_date]

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

    custom_filter = CustomJSFilter(args=dict(mc_widgets=mc_widgets, dr_widgets=dr_widgets),code=filter_code)
    view = CDSView(source=ds, filters=[custom_filter])
    all_widgets = {**mc_widgets, **dr_widgets}
    widgets = {k:w['widget'] for k,w in all_widgets.items()}
    hds0, hds1, hds2 = Histogram('Checks', ds, view, widgets.values(), modules)
    p = figure(
        title='I2C Read/Write',
        x_range=hds0.data['x'],
        x_axis_label='Checks',
        y_axis_label='Number of Boards',
        tools='pan,wheel_zoom,box_zoom,reset,save',
        width = 925
        )

    p.vbar(x='x', top='top', source=hds0, legend_label=modules[0], color=colors[0], width=0.8)
    p.vbar(x='x', top='top', source=hds1, legend_label=modules[1], color=colors[1], width=0.8)
    p.vbar(x='x', top='top', source=hds2, legend_label=modules[2], color=colors[2], width=0.8)
    p.legend.click_policy='hide'
    p.legend.label_text_font_size = '8pt'
    w = [*widgets.values()]

    # update options for serial numbers upon selecting a subtype
    subtypes = np.unique(ds.data['Type ID'].tolist()).tolist()
    serial_numbers = {}
    for s in subtypes:
        serial_numbers[s] = np.unique(df_temp.query('`Type ID` == @s')['Full ID'].values.tolist()).tolist()
    update_options = CustomJS(args=dict(serial_numbers=serial_numbers, widget=w[1]), code=('''
widget.options = serial_numbers[this.value]
'''))
    w[0].js_on_change('value', update_options)

    plot_json = json.dumps(json_item(column(row(w[0:3]), row(w[3:6]), p)))
    return plot_json
    

