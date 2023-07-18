#!/usr/bin/python3

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
)
from bokeh.embed import json_item
from bokeh.palettes import d3, brewer
from bokeh.layouts import column, row
import json

cgitb.enable()

TestData = pd.read_csv('./static/files/Test.csv', parse_dates=['Time'])
BoardData = pd.read_csv('./static/files/Board.csv')
PeopleData = pd.read_csv('./static/files/People.csv')
mergetemp = TestData.merge(BoardData, on='Board ID', how='left')
AllData = mergetemp.merge(PeopleData, on='Person ID', how='left')
AllData = AllData.rename(columns={'Successful':'Outcome'})
AllData['Outcome'] = AllData['Outcome'].replace(0, 'Unsuccessful')
AllData['Outcome'] = AllData['Outcome'].replace(1, 'Successful')

tempRM = pd.read_csv('./static/files/Resistance_Measurement.csv')
tempRM = tempRM.set_index('Test ID')
RM = tempRM.stack()
RM = RM.reset_index()
RM = RM.rename(columns={0:'Resistance'})
RM = RM.dropna()

tempI2C = pd.read_csv('./static/files/I2C_ReadWrite_Test_Data.csv')
tempI2C = tempI2C.set_index('Test ID')
tempI2C = tempI2C.rename(columns={'Correct at Module 1':'Module 1'})
tempI2C = tempI2C.rename(columns={'Correct at Module 2':'Module 2'})
tempI2C = tempI2C.rename(columns={'Correct at Module 3':'Module 3'})
I2C = tempI2C.stack()
I2C = I2C.reset_index()
I2C = I2C.rename(columns={0:'Checks'})
I2C = I2C.dropna()

tempBE = pd.read_csv('./static/files/Bit_Error_Rate_Test_Data.csv')
MP = tempBE.drop('Eye Opening', axis=1)
MP = MP.dropna()
EO = tempBE.drop('Midpoint', axis=1)
EO = EO.dropna()

tempIDR = pd.read_csv('./static/files/ID_Resistor_Test_Data.csv')
IDR = tempIDR.dropna()

temptext=('''

''')

colors = [d3['Category10'][10][0], d3['Category10'][10][1], d3['Category10'][10][2], d3['Category10'][10][3], d3['Category10'][10][4], d3['Category10'][10][5], d3['Category10'][10][6], d3['Category10'][10][7], d3['Category10'][10][8], d3['Category10'][10][9], brewer['Accent'][8][0], brewer['Accent'][8][3], brewer['Dark2'][8][0], brewer['Dark2'][8][2], brewer['Dark2'][8][3], brewer['Dark2'][8][4], brewer['Dark2'][8][5], brewer['Dark2'][8][6]]


def ResistanceHistogram(columns, data, view, widgets, modules, slider):
    hist_data = {}
    for i in modules:
        hist_data[i] = ColumnDataSource(data={'top':[], 'bottom':[], 'left':[], 'right':[]})
    
    dt = ColumnDataSource(data={'Type ID':[], 'Full ID':[], 'Person Name':[], 'Time':[], 'level_1':[], 'Resistance':[]})
    new_modules = ColumnDataSource(data={'modules':[]})
    x = CustomJS(args=dict(col=columns, hist=hist_data, data=data, view=view, modules=modules, slider=slider, new_modules_ds=new_modules, dt=dt),code='''
const new_modules = [];
const type_ids=[];
const full_ids=[];
const people=[];
const times=[];
const pathways=[];
const res=[];
for (let i = 0; i < modules.length; i++) {
    const indices = view.filters[0].compute_indices(data);
    let mask = new Array(data.data[col].length).fill(false);
    [...indices].forEach((x)=>{mask[x] = true;})
    for (let j = 0; j < data.get_length(); j++) {
        if (data.data['level_1'][j] == modules[i] && mask[j] == true){
            mask[j] = true;
            type_ids.push(data.data['Type ID'][j])
            full_ids.push(data.data['Full ID'][j])
            people.push(data.data['Person Name'][j])
            times.push(data.data['Time'][j])
            pathways.push(data.data['level_1'][j])
            res.push(data.data[col][j])
        } else {
            mask[j] = false;
        }
    }
    const good_data = data.data[col].filter((_,y)=>mask[y])
    let bins = slider.value
    let m = Math.max(...good_data);
    let scale = d3.scaleLinear().domain([0,m]).nice()
    let binner = d3.bin().domain(scale.domain()).thresholds(m*bins)
    let d = binner(good_data)
    let right = d.map(x=>x.x1)
    let left = d.map(x=>x.x0)
    let bottom = new Array(d.length).fill(0)
    let top = d.map(x=>x.length);
    hist[modules[i]].data['right'] = right;
    hist[modules[i]].data['left'] = left;
    hist[modules[i]].data['bottom'] = bottom;
    hist[modules[i]].data['top'] = top;
    hist[modules[i]].change.emit()
    if (right != -1) {
        new_modules.push(modules[i]);
    }
}
dt.data['Type ID'] = type_ids;
dt.data['Full ID'] = full_ids;
dt.data['Person Name'] = people;
dt.data['Time'] = times;
dt.data['level_1'] = pathways;
dt.data['Resistance'] = res;
dt.change.emit()
new_modules_ds.data['modules'] = new_modules;
new_modules_ds.change.emit()
    ''')
    for widget in widgets:
        widget.js_on_change('value', x)
    slider.js_on_change('value', x)
    return hist_data, new_modules, dt


def ResistanceFilter():
    df_temp = AllData.merge(RM, on='Test ID', how='left')
    df_temp = df_temp.dropna()
    ds = ColumnDataSource(df_temp)
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
    modules = np.unique(ds.data['level_1']).tolist()
    columns = ['Type ID', 'Full ID', 'Person Name', 'Outcome', 'Start Date', 'End Date']
    data = [ds.data['Type ID'].tolist(), ds.data['Full ID'].tolist(), ds.data['Person Name'].tolist(), ds.data['Outcome'], date_range, date_range]
    t = [multi_choice, multi_choice, multi_choice, multi_choice, start_date, end_date]

    p = figure(
        title='Resistance Measurement',
        x_axis_label='Resistance',
        y_axis_label='Number of Boards',
        tools='pan,wheel_zoom,box_zoom,reset,save',
        width = 925
        )

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

    custom_filter = CustomJSFilter(args=dict(mc_widgets=mc_widgets, dr_widgets=dr_widgets), code='''
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
    view = CDSView(source=ds, filters=[custom_filter])
    slider = Slider(start=1, end=16, value=4, step=1, title='Granularity')
    all_widgets = {**mc_widgets, **dr_widgets}
    widgets = {k:w['widget'] for k,w in all_widgets.items()}
    hds, new_modules, dt = ResistanceHistogram('Resistance', ds, view, widgets.values(), modules, slider)
    for i in range(len(modules)):
        p.quad(top='top', bottom='bottom', left='left', right='right', source=hds[modules[i]], legend_label=modules[i], color = colors[i])

    table_columns = [
                    TableColumn(field='Type ID', title='Type ID'),
                    TableColumn(field='Full ID', title='Full ID'),
                    TableColumn(field='Person Name', title='Person Name'),
                    TableColumn(field='Time', title='Date', formatter=DateFormatter()),
                    TableColumn(field='level_1', title='Pathway'),
                    TableColumn(field='Resistance', title='Resistance'),
                    ]
    data_table = DataTable(source=dt, columns=table_columns, width=925, autosize_mode='fit_columns')
    p.legend.click_policy='hide'
    p.legend.label_text_font_size = '8pt'
    w = [*widgets.values()]
    plot_json = json.dumps(json_item(column(row(w[0:3]), row(w[3:6]), slider, p, data_table)))
    return plot_json

################################################################################################################

def I2CHistogram(columns, data, view, widgets, modules):
    hist_data0 = ColumnDataSource(data={'top':[], 'x':['-1', '10000']})
    hist_data1 = ColumnDataSource(data={'top':[], 'x':['-1', '10000']})
    hist_data2 = ColumnDataSource(data={'top':[], 'x':['-1', '10000']})
    x = CustomJS(args=dict(col=columns, hist0=hist_data0, hist1=hist_data1, hist2=hist_data2, data=data, view=view, modules=modules),code='''
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
    let top = [u_counts, s_counts]; 
    console.log(top)
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


def I2CFilter():
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

    custom_filter = CustomJSFilter(args=dict(mc_widgets=mc_widgets, dr_widgets=dr_widgets), code='''
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
    view = CDSView(source=ds, filters=[custom_filter])
    all_widgets = {**mc_widgets, **dr_widgets}
    widgets = {k:w['widget'] for k,w in all_widgets.items()}
    hds0, hds1, hds2 = I2CHistogram('Checks', ds, view, widgets.values(), modules)
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
    plot_json = json.dumps(json_item(column(row(w[0:3]), row(w[3:6]), p)))
    return plot_json
    
#I2CFilter()

################################################################################################################

def BitErrorHistogram(mp_data, eo_data, view, widgets, modules, slider):
    hist_data_mp = {}
    hist_data_eo = {}
    for i in modules:
        hist_data_mp[i] = ColumnDataSource(data={'top':[], 'bottom':[], 'left':[], 'right':[]})
        hist_data_eo[i] = ColumnDataSource(data={'top':[], 'bottom':[], 'left':[], 'right':[]})

    std = ColumnDataSource(data={'columns':[], 'std':[]})
    dt = ColumnDataSource(data={'Type ID':[], 'Full ID':[], 'Person Name':[], 'Time':[], 'E Link':[], 'Midpoint':[], 'Eye Opening':[]})
    x = CustomJS(args=dict(hist_mp=hist_data_mp, hist_eo=hist_data_eo, mp_data=mp_data, eo_data=eo_data, view=view, modules=modules, slider=slider, std=std, dt=dt),code='''
const columns = [];
const std_ar = [];
const type_ids = [];
const full_ids = [];
const names = [];
const dates = [];
const elinks = [];
const midpoints = [];
const eye_openings = [];
for (let i = 0; i < modules.length; i++) {
    const indices = view.filters[0].compute_indices(mp_data);
    let mask = new Array(mp_data.data['Midpoint'].length).fill(false);
    [...indices].forEach((x)=>{mask[x] = true;})
    let mp_mask = mask;
    let eo_mask = mask;
    for (let j = 0; j < mp_data.length; j++) {
        if (mp_data.data['E Link'][j] == modules[i] && mp_mask[j] == true){
            mp_mask[j] = true;
            type_ids.push(mp_data.data['Type ID'][j])
            full_ids.push(mp_data.data['Full ID'][j])
            names.push(mp_data.data['Person Name'][j])
            dates.push(mp_data.data['Time'][j])
            elinks.push(mp_data.data['E Link'][j])
            midpoints.push(mp_data.data['Midpoint'][j])
            eye_openings.push(eo_data.data['Eye Opening'][j])
        } else {
            mp_mask[j] = false;
        }
    }
    for (let j = 0; j < eo_data.length; j++) {
        if (eo_data.data['E Link'][j] == modules[i] && eo_mask[j] == true){
            eo_mask[j] = true;
        } else {
            eo_mask[j] = false;
        }
    }
    const mp_good_data = mp_data.data['Midpoint'].filter((_,y)=>mp_mask[y])
    const eo_good_data = eo_data.data['Eye Opening'].filter((_,y)=>eo_mask[y])
    let bins = slider.value
    let mp_m = Math.max(...mp_good_data);
    let mp_min = Math.min(...mp_good_data);
    let eo_m = Math.max(...eo_good_data);
    let eo_min = Math.min(...eo_good_data);
    let mp_scale = d3.scaleLinear().domain([mp_min,mp_m]).nice()
    let eo_scale = d3.scaleLinear().domain([eo_min-2,eo_m+2]).nice()
    let n1 = (mp_m - mp_min)
    let mp_binner = d3.bin().domain(mp_scale.domain()).thresholds(n1*bins*0.1)
    let eo_binner = d3.bin().domain(eo_scale.domain()).thresholds(4*bins)
    let mp_d = mp_binner(mp_good_data)
    let eo_d = eo_binner(eo_good_data)
    let mp_right = mp_d.map(x=>x.x1)
    let mp_left = mp_d.map(x=>x.x0)
    let mp_bottom = new Array(mp_d.length).fill(0)
    let mp_top = mp_d.map(x=>x.length);
    let eo_right = eo_d.map(x=>x.x1)
    let eo_left = eo_d.map(x=>x.x0)
    let eo_bottom = new Array(eo_d.length).fill(0)
    let eo_top = eo_d.map(x=>x.length);
    hist_mp[modules[i]].data['right'] = mp_right;
    hist_mp[modules[i]].data['left'] = mp_left;
    hist_mp[modules[i]].data['bottom'] = mp_bottom;
    hist_mp[modules[i]].data['top'] = mp_top;
    hist_mp[modules[i]].change.emit()
    hist_eo[modules[i]].data['right'] = eo_right;
    hist_eo[modules[i]].data['left'] = eo_left;
    hist_eo[modules[i]].data['bottom'] = eo_bottom;
    hist_eo[modules[i]].data['top'] = eo_top;
    hist_eo[modules[i]].change.emit()
    columns.push(modules[i])
    std_ar.push(d3.deviation(eo_good_data));
}
std.data['columns'] = columns;
std.data['std'] = std_ar;
std.change.emit()
dt.data['Type ID'] = type_ids;
dt.data['Full ID'] = full_ids;
dt.data['Person Name'] = names;
dt.data['Time'] = dates;
dt.data['E Link'] = elinks;
dt.data['Midpoint'] = midpoints;
dt.data['Eye Opening'] = eye_openings;
dt.change.emit()
    ''')
    for widget in widgets:
        widget.js_on_change('value', x)
    slider.js_on_change('value', x)
    return hist_data_mp, hist_data_eo, std, dt

def BitErrorFilter():
    mp_temp = AllData.merge(MP, on='Test ID', how='left')
    mp_temp = mp_temp.dropna()
    ds_mp = ColumnDataSource(mp_temp)
    eo_temp = AllData.merge(EO, on='Test ID', how='left')
    eo_temp = eo_temp.dropna()
    ds_eo = ColumnDataSource(eo_temp)
    mc_widgets = {}
    dr_widgets = {}
    multi_choice = (lambda x,y: MultiChoice(options=x, value=[], title=y), 'value')
    start_date = (lambda x,y,z: DatePicker(min_date=x,max_date=y, value='2023-03-14', title=z), 'value')
    today = datetime.date.today()
    end_date = (lambda x,y,z: DatePicker(min_date=x,max_date=y, value=today, title=z), 'value')
    min_date = pd.Timestamp((min(ds_mp.data['Time']))).date()
    date_range = []
    while min_date <= today:
        date_range.append(min_date)
        min_date += datetime.timedelta(days=1)
    modules = np.unique(ds_mp.data['E Link'].tolist()).tolist()
    columns = ['Type ID', 'Full ID', 'Person Name', 'Outcome', 'Start Date', 'End Date']
    data = [ds_mp.data['Type ID'].tolist(), ds_mp.data['Full ID'].tolist(), ds_mp.data['Person Name'].tolist(), ds_mp.data['Outcome'], date_range, date_range]
    t = [multi_choice, multi_choice, multi_choice, multi_choice, start_date, end_date]

    p = figure(
        title='Midpoint',
        x_axis_label='DAQ Delay',
        y_axis_label='Number of Boards',
        tools='pan,wheel_zoom,box_zoom,reset,save',
        width = 925
        )
    q = figure(
        title='Eye Opening',
        x_axis_label='Eye Width',
        y_axis_label='Number of Boards',
        tools='pan,wheel_zoom,box_zoom,reset,save',
        width = 925
        )

    for i in range(len(columns)):
        widget_constructor, trigger = t[i]
        if t[i] == multi_choice:
            possible_vals = np.unique(data[i]).tolist()
            widget = widget_constructor(possible_vals, columns[i])
            typ = 'multi_choice'
            widget.js_on_change(trigger, CustomJS(args=dict(src1=ds_mp, src2=ds_eo), code='''
src1.change.emit()
src2.change.emit()
'''))
            mc_widgets[columns[i]] = {
                'type': typ,
                'possible_vals': possible_vals,
                'widget': widget,}
        else:
            possible_vals = data[i]
            widget = widget_constructor(min(data[i]),max(data[i]), columns[i])
            typ = 'date_range'
            widget.js_on_change(trigger, CustomJS(args=dict(src1=ds_mp, src2=ds_eo), code='''
src1.change.emit()
src2.change.emit()
'''))
            dr_widgets[columns[i]] = {
                'type': typ,
                'possible_vals': possible_vals,
                'widget': widget,}

    custom_filter = CustomJSFilter(args=dict(mc_widgets=mc_widgets, dr_widgets=dr_widgets), code='''
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
for (let i = 0; i < source.length; i++) {
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
for (let i = 0; i < source.length; i++) {
    if (source.data['Time'][i] >= start_date && source.data['Time'][i] <= end_date && indices[i] == true) {
        indices[i] = true;
    } else {
        indices[i] = false;
    }
}
return indices;
''')
    view = CDSView(source=ds_mp, filters=[custom_filter])
    slider = Slider(start=1, end=18, value=4, step=1, title='Granularity')
    all_widgets = {**mc_widgets, **dr_widgets}
    widgets = {k:w['widget'] for k,w in all_widgets.items()}
    mp_hist, eo_hist, std, dt = BitErrorHistogram(ds_mp, ds_eo, view, widgets.values(), modules, slider)
    for i in range(len(modules)):
        p.quad(top='top', bottom='bottom', left='left', right='right', source=mp_hist[modules[i]], legend_label=modules[i], color = colors[i])
        q.quad(top='top', bottom='bottom', left='left', right='right', source=eo_hist[modules[i]], legend_label=modules[i], color = colors[i])
        
    p.legend.click_policy='hide'
    p.legend.label_text_font_size = '8pt'
    q.legend.click_policy='hide'
    q.legend.label_text_font_size = '8pt'
    table_columns = [TableColumn(field='columns', title='E Link'), TableColumn(field='std', title='Standard Deviation')]
    table = DataTable(source=std, columns=table_columns)
    table_columns2 = [
                    TableColumn(field='Type ID', title='Type ID'),
                    TableColumn(field='Full ID', title='Full ID'),
                    TableColumn(field='Person Name', title='Person Name'),
                    TableColumn(field='Time', title='Date', formatter=DateFormatter()),
                    TableColumn(field='E Link', title='E Link'),
                    TableColumn(field='Midpoint', title='Midpoint'),
                    TableColumn(field='Eye Opening', title='Eye Opening'),
                    ]
    data_table = DataTable(source=dt, columns=table_columns2, autosize_mode='fit_columns')
    w = [*widgets.values()]
    plot_json = json.dumps(json_item(column(row(w[0:3]), row(w[3:6]), slider, p, q, table, data_table)))
    return plot_json

def TotalPlot(columns, data, view, widgets, date_range, modules):
    time_series_data_total = ColumnDataSource(data={'dates':[], 'counts':[]})
    time_series_data_suc = ColumnDataSource(data={'dates':[], 'counts':[]})
    time_series_data_unc = ColumnDataSource(data={'dates':[], 'counts':[]})
    x = CustomJS(args=dict(col=columns, tsd_total=time_series_data_total, tsd_suc=time_series_data_suc, tsd_unc=time_series_data_unc, data=data, view=view, date_range=date_range, modules=modules),code='''
for (let t = 0; t < modules.length; t++) {
    if (modules[t] == 'Total') {
        const indices = view.filters[0].compute_indices(data);
        let mask = new Array(data.data['Test ID'].length).fill(false);
        [...indices].forEach((x)=>{mask[x] = true;})
        console.log(mask)
        let count = 0;
        const dates = [];
        const counts = [];
        for (let m = 0; m < mask.length; m++) {
            if (mask[m] ==  true) {
                let temp_date = new Date(data.data['Time'][m]);
                let new_date = temp_date.toLocaleDateString();
                let date = new Date(new_date);
                date = new Date(date.setHours(date.getHours() - 5));
                for (let i = 0; i < date_range.length; i++) {
                    let day0 = new Date(date_range[i]);
                    let day1 = new Date(date_range[i]);
                    day1 = new Date(day1.setDate(day1.getDate() + 1));
                    if (day0 >= date) {
                        for (let j = 0; j < mask.length; j++) {
                            if (mask[j] == true && data.data['Time'][j] >= day0 && data.data['Time'][j] <= day1){
                                count++; 
                            }
                        }
                        dates.push(day0.getTime());
                        counts.push(count);
                    }
                }
                break;
            }
        }
        tsd_total.data['dates'] = dates;
        tsd_total.data['counts'] = counts;
        tsd_total.change.emit()
    } if (modules[t] == 'Successful') {
        const indices = view.filters[0].compute_indices(data);
        let mask = new Array(data.data['Test ID'].length).fill(false);
        [...indices].forEach((x)=>{mask[x] = true;})
        for (let m = 0; m < mask.length; m++) {
            if (mask[m] == true && data.data['Outcome'][m] == modules[t]) {
                mask[m] = true;
            } else {
                mask[m] = false;
            }
        }
        console.log(mask)
        let count = 0;
        const dates = [];
        const counts = [];
        for (let m = 0; m < mask.length; m++) {
            if (mask[m] ==  true) {
                let temp_date = new Date(data.data['Time'][m]);
                let new_date = temp_date.toLocaleDateString();
                let date = new Date(new_date);
                date = new Date(date.setHours(date.getHours() - 5));
                for (let i = 0; i < date_range.length; i++) {
                    let day0 = new Date(date_range[i]);
                    let day1 = new Date(date_range[i]);
                    day1 = new Date(day1.setDate(day1.getDate() + 1));
                    if (day0 >= date) {
                        for (let j = 0; j < mask.length; j++) {
                            if (mask[j] == true && data.data['Time'][j] >= day0 && data.data['Time'][j] <= day1){
                                count++; 
                            }
                        }
                        dates.push(day0.getTime());
                        counts.push(count);
                    }
                }
                break;
            }
        }
        tsd_suc.data['dates'] = dates;
        tsd_suc.data['counts'] = counts;
        tsd_suc.change.emit()
    } if (modules[t] == 'Unsuccessful') {
        const indices = view.filters[0].compute_indices(data);
        let mask = new Array(data.data['Test ID'].length).fill(false);
        [...indices].forEach((x)=>{mask[x] = true;})
        for (let m = 0; m < mask.length; m++) {
            if (mask[m] == true && data.data['Outcome'][m] == modules[t]) {
                mask[m] = true;
            } else {
                mask[m] = false;
            }
        }
        console.log(mask)
        let count = 0;
        const dates = [];
        const counts = [];
        for (let m = 0; m < mask.length; m++) {
            if (mask[m] ==  true) {
                let temp_date = new Date(data.data['Time'][m]);
                let new_date = temp_date.toLocaleDateString();
                let date = new Date(new_date);
                date = new Date(date.setHours(date.getHours() - 5));
                for (let i = 0; i < date_range.length; i++) {
                    let day0 = new Date(date_range[i]);
                    let day1 = new Date(date_range[i]);
                    day1 = new Date(day1.setDate(day1.getDate() + 1));
                    if (day0 >= date) {
                        for (let j = 0; j < mask.length; j++) {
                            if (mask[j] == true && data.data['Time'][j] >= day0 && data.data['Time'][j] <= day1){
                                count++; 
                            }
                        }
                        dates.push(day0.getTime());
                        counts.push(count);
                    }
                }
                break;
            }
        }
        tsd_unc.data['dates'] = dates;
        tsd_unc.data['counts'] = counts;
        tsd_unc.change.emit()
    }
}
console.log(tsd_total.data['counts'])
console.log(tsd_suc.data['counts'])
console.log(tsd_unc.data['counts'])
    ''')
    for widget in widgets:
        widget.js_on_change('value', x)
    return time_series_data_total, time_series_data_suc, time_series_data_unc


def TotalFilter():
    df_temp = AllData
    df_temp = df_temp.dropna()
    ds = ColumnDataSource(df_temp)
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
    modules = ['Total', 'Successful', 'Unsuccessful']
    columns = ['Type ID', 'Full ID', 'Person Name', 'Start Date', 'End Date']
    data = [ds.data['Type ID'].tolist(), ds.data['Full ID'].tolist(), ds.data['Person Name'].tolist(),  date_range, date_range]
    t = [multi_choice, multi_choice, multi_choice, start_date, end_date]

    p = figure(
        title='Total Tests Over Time',
        x_axis_label='Date',
        y_axis_label='Number of Tests',
        tools='pan,wheel_zoom,box_zoom,reset,save',
        width = 925,
        x_axis_type='datetime',
        )

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

    custom_filter = CustomJSFilter(args=dict(mc_widgets=mc_widgets, dr_widgets=dr_widgets), code='''
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
    view = CDSView(source=ds, filters=[custom_filter])
    all_widgets = {**mc_widgets, **dr_widgets}
    widgets = {k:w['widget'] for k,w in all_widgets.items()}
    tsd_total, tsd_suc, tsd_unc = TotalPlot('Resistance', ds, view, widgets.values(), date_range, modules)
    p.line('dates', 'counts', source=tsd_total, legend_label=modules[0], color=colors[0], line_width=2, muted_alpha=0.2)
    p.line('dates', 'counts', source=tsd_suc, legend_label=modules[1], color=colors[2], line_width=2, muted_alpha=0.2)
    p.line('dates', 'counts', source=tsd_unc, legend_label=modules[2], color=colors[3], line_width=2, muted_alpha=0.2)
    p.legend.click_policy='mute'
    p.legend.label_text_font_size = '8pt'
    p.legend.location = 'top_left'
    w = [*widgets.values()]
    plot_json = json.dumps(json_item(column(row(w[0:3]), row(w[3:5]), p)))
    return plot_json

############################################################################################################

def ComparePlot(columns, data, view, widgets, date_range, modules):
    tsd = {}
    for i in modules:
        tsd[i] = ColumnDataSource(data={'dates':[], 'counts':[]})
    
    dt = ColumnDataSource(data={'Person Name':[], 'counts':[]})
    x = CustomJS(args=dict(col=columns, tsd=tsd, data=data, view=view, dt=dt, date_range=date_range, modules=modules),code='''
const names = [];
const completed = [];
for (let t = 0; t < modules.length; t++) {
    const indices = view.filters[0].compute_indices(data);
    let mask = new Array(data.data['Test ID'].length).fill(false);
    [...indices].forEach((x)=>{mask[x] = true;})
    for (let m = 0; m < mask.length; m++) {
        if (mask[m] == true && data.data['Person Name'][m] == modules[t]) {
            mask[m] = true;
        } else {
            mask[m] = false;
        }
    }
    let count = 0;
    const dates = [];
    const counts = [];
    for (let m = 0; m < mask.length; m++) {
        if (mask[m] ==  true) {
            let temp_date = new Date(data.data['Time'][m]);
            let new_date = temp_date.toLocaleDateString();
            let date = new Date(new_date);
            date = new Date(date.setHours(date.getHours() - 5));
            for (let i = 0; i < date_range.length; i++) {
                let day0 = new Date(date_range[i]);
                let day1 = new Date(date_range[i]);
                day1 = new Date(day1.setDate(day1.getDate() + 1));
                if (day0 >= date) {
                    for (let j = 0; j < mask.length; j++) {
                        if (mask[j] == true && data.data['Time'][j] >= day0 && data.data['Time'][j] <= day1){
                            count++; 
                        }
                    }
                    dates.push(day0.getTime());
                    counts.push(count);
                }
            }
            break;
        }
    }
    tsd[modules[t]].data['dates'] = dates;
    tsd[modules[t]].data['counts'] = counts;
    tsd[modules[t]].change.emit()
    names.push(modules[t])
    completed.push(counts.slice(-1))
}
dt.data['Person Name'] = names;
dt.data['counts'] = completed;
dt.change.emit()
    ''')
    for widget in widgets:
        widget.js_on_change('value', x)
    return tsd, dt


def CompareFilter():
    df_temp = AllData
    df_temp = df_temp.dropna()
    ds = ColumnDataSource(df_temp)
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
    modules = np.unique(ds.data['Person Name'].tolist())
    columns = ['Type ID', 'Full ID', 'Outcome','Start Date', 'End Date']
    data = [ds.data['Type ID'].tolist(), ds.data['Full ID'].tolist(), ds.data['Outcome'].tolist(), date_range, date_range]
    t = [multi_choice, multi_choice, multi_choice, start_date, end_date]

    p = figure(
        title='Total Tests Over Time',
        x_axis_label='Date',
        y_axis_label='Number of Tests',
        tools='pan,wheel_zoom,box_zoom,reset,save',
        width = 925,
        x_axis_type='datetime',
        )

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

    custom_filter = CustomJSFilter(args=dict(mc_widgets=mc_widgets, dr_widgets=dr_widgets), code='''
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
    view = CDSView(source=ds, filters=[custom_filter])
    all_widgets = {**mc_widgets, **dr_widgets}
    widgets = {k:w['widget'] for k,w in all_widgets.items()}
    tsd,dt = ComparePlot('Resistance', ds,view, widgets.values(), date_range, modules)
    for i in range(len(modules)):
        p.line('dates', 'counts', source=tsd[modules[i]], legend_label=modules[i], color=colors[i], line_width=2)
        
    table_columns = [
                    TableColumn(field='Person Name', title='Person Name'),
                    TableColumn(field='counts', title='Tests Completed'),
                    ]
    data_table = DataTable(source=dt, columns=table_columns, autosize_mode='fit_columns')
    p.legend.click_policy='hide'
    p.legend.label_text_font_size = '8pt'
    p.legend.location = 'top_left'
    w = [*widgets.values()]
    plot_json = json.dumps(json_item(column(row(w[0:3]), row(w[3:5]), p, data_table)))
    return plot_json

#############################################################################################################

def IDHistogram(columns, data, views, widgets, subtypes, serial_numbers, slider):
    hist = {}
    td = {}
    for s in subtypes:
        hist[s] = {}
        for sn in serial_numbers[s]:
            hist[s][sn] = ColumnDataSource(data={'top':[], 'bottom':[], 'left':[], 'right':[]})

        td[s] = ColumnDataSource(data={'Full ID':[], 'Resistance':[]})

    x = CustomJS(args=dict(col=columns, hist=hist, data=data, views=views, subtypes=subtypes, serial_numbers=serial_numbers, slider=slider, td=td),code='''
for (let s = 0; s < subtypes.length; s++) {
    const full_ids = [];
    const res = [];
    for (let sn = 0; sn < serial_numbers[subtypes[s]].length; sn++) {
        const indices = views[subtypes[s]].filters[0].compute_indices(data[subtypes[s]]);
        let mask = new Array(data[subtypes[s]].data[col].length).fill(false);
        [...indices].forEach((x)=>{mask[x] = true;})
        for (let j = 0; j < data[subtypes[s]].get_length(); j++) {
            if (data[subtypes[s]].data['Full ID'][j] == serial_numbers[subtypes[s]][sn] && mask[j] == true){
                mask[j] = true;
                full_ids.push(serial_numbers[subtypes[s]][sn])
                res.push(data[subtypes[s]].data[col][j])
            } else {
                mask[j] = false;
            }
        }
        const good_data = data[subtypes[s]].data[col].filter((_,y)=>mask[y])
        let bins = slider.value
        let min = Math.min(...good_data);
        let m = Math.max(...good_data);
        let scale = d3.scaleLinear().domain([min-0.5,m+0.5]).nice()
        let binner = d3.bin().domain(scale.domain()).thresholds(m*bins)
        let d = binner(good_data)
        let right = d.map(x=>x.x1)
        let left = d.map(x=>x.x0)
        let bottom = new Array(d.length).fill(0)
        let top = d.map(x=>x.length);
        hist[subtypes[s]][serial_numbers[subtypes[s]][sn]].data['right'] = right;
        hist[subtypes[s]][serial_numbers[subtypes[s]][sn]].data['left'] = left;
        hist[subtypes[s]][serial_numbers[subtypes[s]][sn]].data['bottom'] = bottom;
        hist[subtypes[s]][serial_numbers[subtypes[s]][sn]].data['top'] = top;
        hist[subtypes[s]][serial_numbers[subtypes[s]][sn]].change.emit()
    }
    td[subtypes[s]].data['Full ID'] = full_ids;
    td[subtypes[s]].data['Resistance'] = res;
    td[subtypes[s]].change.emit()
}
    ''')
    for widget in widgets:
        widget.js_on_change('value', x)
    slider.js_on_change('value', x)
    return hist, td

def IDFilter():
    df_temp = AllData.merge(IDR, on='Test ID', how='left')
    df_temp = df_temp.dropna()
    ds = ColumnDataSource(df_temp)
    subtypes = np.unique(ds.data['Type ID'].tolist()).tolist()
    data_sources = {}
    serial_numbers = {}
    for s in subtypes:
        data_sources[s] = ColumnDataSource(df_temp.query('`Type ID` == @s'))
        serial_numbers[s] = np.unique(df_temp.query('`Type ID` == @s')['Full ID'].values.tolist()).tolist()
        
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

    custom_filter = CustomJSFilter(args=dict(mc_widgets=mc_widgets, dr_widgets=dr_widgets), code='''
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
    views = {}
    for s in subtypes:
        views[s] = CDSView(source=data_sources[s], filters=[custom_filter])
    slider = Slider(start=1, end=16, value=4, step=1, title='Granularity')
    all_widgets = {**mc_widgets, **dr_widgets}
    widgets = {k:w['widget'] for k,w in all_widgets.items()}

    hist,td = IDHistogram('Resistance', data_sources, views, widgets.values(), subtypes, serial_numbers, slider)
    plots = {}
    tables = {}
    for s in subtypes:
        p = figure(
            title='ID Resistance for ' + s,
            x_axis_label='Resistance',
            y_axis_label='Number of Boards',
            tools='pan,wheel_zoom,box_zoom,reset,save',
            width = 925
            )
        for sn in range(len(serial_numbers[s])): 
            p.quad(top='top', bottom='bottom', left='left', right='right', source=hist[s][serial_numbers[s][sn]], legend_label=serial_numbers[s][sn], color = colors[sn])
            p.visible = False
            p.legend.click_policy='hide'
            p.legend.label_text_font_size = '8pt' 
        plots[s] = p
        table_columns = [
                        TableColumn(field='Full ID', title='Full ID'),
                        TableColumn(field='Resistance', title='Resistance'),
                        ]
        data_table = DataTable(source=td[s], columns=table_columns, autosize_mode='fit_columns')
        data_table.visible = False
        tables[s] = data_table
            
    w = [*widgets.values()]
    display_plot = CustomJS(args=dict(plots=plots, tables=tables), code=('''
for (let [name,plot] of Object.entries(plots)){
    if (name == this.value){
        plot.visible = true
    } else {
        plot.visible = false
    }
}
for (let [name,table] of Object.entries(tables)){
    if (name == this.value){
        table.visible = true
    } else {
        table.visible = false
    }
}
'''))
    
    select = Select(title='Type ID', options=subtypes)
    select.js_on_change('value', display_plot)

    layout = column(row(w[0:2] + [select]), row(w[2:5]), slider, column(list(plots.values())),  column(list(tables.values())))
    plot_json = json.dumps(json_item(layout))
    return plot_json

