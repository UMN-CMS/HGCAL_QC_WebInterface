#!./cgi_runner.sh

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
    Text,
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

# each value has its own data frame
csv_file_resist, csv_file_volt, csv_file_temp, csv_file_adc = mTD.get_adc_functionality()

temp = pd.read_csv(csv_file_resist)
ADC_resist = temp.dropna()
temp = pd.read_csv(csv_file_volt)
ADC_voltage = temp.dropna()
temp = pd.read_csv(csv_file_temp)
ADC_temp = temp.dropna()
temp = pd.read_csv(csv_file_adc)
ADC_main = temp.dropna()

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

colors = [d3['Category10'][10][0],
d3['Category10'][10][1], 
d3['Category10'][10][2], 
d3['Category10'][10][3], 
d3['Category10'][10][4], 
d3['Category10'][10][5], 
d3['Category10'][10][6], 
d3['Category10'][10][7], 
d3['Category10'][10][8], 
d3['Category10'][10][9], 
brewer['Accent'][8][0], 
brewer['Accent'][8][3], 
brewer['Dark2'][8][0], 
brewer['Dark2'][8][2], 
brewer['Dark2'][8][3], 
brewer['Dark2'][8][4], 
brewer['Dark2'][8][5], 
brewer['Dark2'][8][6], 
d3['Category20'][20][1], 
d3['Category20'][20][9], 
d3['Category20c'][20][19],
d3['Category20c'][20][12],
d3['Category20c'][20][4],
d3['Category20c'][20][0],
d3['Category20b'][20][16],
d3['Category20b'][20][8],
]


def Histograms(data_resist, data_volt, data_temp, data_adc, view, widgets, resist_modules, volt_modules, temp_modules, adc_modules, slider):
    # the dictionary has a dictionary for each quantity
    hist = {}
    td = {}
    hist['adc slope'] = ColumnDataSource(data={'top':[], 'bottom':[], 'left':[], 'right':[]})
    hist['adc intercept'] = ColumnDataSource(data={'top':[], 'bottom':[], 'left':[], 'right':[]})
    hist['adc r2'] = ColumnDataSource(data={'top':[], 'bottom':[], 'left':[], 'right':[]})
    hist['resist'] = {}
    hist['volt'] = ColumnDataSource(data={'top':[], 'bottom':[], 'left':[], 'right':[]})
    hist['temp'] = ColumnDataSource(data={'top':[], 'bottom':[], 'left':[], 'right':[]})
    # each quantity has a data source for each of its modules
    for r in resist_modules:
        hist['resist'][r] = ColumnDataSource(data={'top':[], 'bottom':[], 'left':[], 'right':[]})

    td['resist'] = ColumnDataSource(data={'E Link':[], 'Resistance':[], 'Outcome':[], 'Serial Number':[]})
    td['volt'] = ColumnDataSource(data={'ADC':[], 'Voltage':[], 'Outcome':[], 'Serial Number':[]})
    td['temp'] = ColumnDataSource(data={'Chip':[], 'Temperature':[], 'Outcome':[], 'Serial Number':[]})
    td['adc']  = ColumnDataSource(data={'ADC':[], 'Slope':[], 'Intercept':[], 'R Squared':[], 'Outcome':[], 'Serial Number':[]})
    std = ColumnDataSource(data={'Quantity':[], 'mean':[], 'std':[], 'module':[]})
    x = CustomJS(args=dict(hist=hist, data_resist=data_resist, data_volt=data_volt, data_temp=data_temp, resist_modules=resist_modules, volt_modules=volt_modules, temp_modules=temp_modules, view=view, slider=slider, td=td, std=std, data_adc=data_adc, adc_modules=adc_modules),code='''
// need several arrays to hold data
const r_sns = [];
const v_sns = [];
const t_sns = [];
const a_sns = [];
const e_links=[];
const adcs=[];
const locations=[];
const resist=[];
const volt=[];
const temp=[];
const locations_adc = [];
const slope = [];
const intercept = [];
const r_squared = [];
const r_outcomes = [];
const v_outcomes = [];
const t_outcomes = [];
const a_outcomes = [];
const quantities = [];
const modules = [];
const means = [];
const stds = [];
// construct bins and indices outside of the loop
let bins = slider.value
const indices_resist = view['resistance'].filters[0].compute_indices(data_resist);
const indices_volt = view['voltage'].filters[0].compute_indices(data_volt);
const indices_temp = view['temperature'].filters[0].compute_indices(data_temp);
const indices_adc = view['adc'].filters[0].compute_indices(data_adc);

// iterate over resistance modules
for (let k = 0; k < resist_modules.length; k++) {
    // create mask
    let mask_resist = new Array(data_resist.data['Resistance'].length).fill(false);
    [...indices_resist].forEach((x)=>{mask_resist[x] = true;})
    
    // const all_data = data_resist.data['Resistance'].filter((_,y)=>mask_resist[y])
    // let m = Math.max(...all_data);
    // let min = Math.min(...all_data);

    for (let j = 0; j < data_resist.data['E Link'].length; j++) {
        if (mask_resist[j] == true && data_resist.data['E Link'][j] == resist_modules[k]) {
            mask_resist[j] = true;
            r_sns.push(data_resist.data['Full ID'][j])
            e_links.push(data_resist.data['E Link'][j])
            resist.push(data_resist.data['Resistance'][j])
            r_outcomes.push(data_resist.data['Outcome'][j])
        } else {
            mask_resist[j] = false;
        }
    }

    // filter and bin data
    const good_data = data_resist.data['Resistance'].filter((_,y)=>mask_resist[y])
    let m = Math.max(...good_data);
    let min = Math.min(...good_data);
    let scale = d3.scaleLinear().domain([min,m]).nice()
    let binner = d3.bin().domain(scale.domain()).thresholds(10*bins)
    let d = binner(good_data)

    quantities.push('Resistance')
    modules.push(resist_modules[k])
    means.push(d3.mean(good_data))
    stds.push(d3.deviation(good_data))

    let right = d.map(x=>x.x1)
    let left = d.map(x=>x.x0)
    let bottom = new Array(d.length).fill(0)
    let top = d.map(x=>x.length);

    hist['resist'][resist_modules[k]].data['right'] = right;
    hist['resist'][resist_modules[k]].data['left'] = left;
    hist['resist'][resist_modules[k]].data['top'] = top;
    hist['resist'][resist_modules[k]].data['bottom'] = bottom;
    hist['resist'][resist_modules[k]].change.emit()

}

td['resist'].data['Serial Number'] = r_sns;
td['resist'].data['E Link'] = e_links;
td['resist'].data['Resistance'] = resist;
td['resist'].data['Outcome'] = r_outcomes;
td['resist'].change.emit()

let mask_volt = new Array(data_volt.data['Voltage'].length).fill(false);
[...indices_volt].forEach((x)=>{mask_volt[x] = true;})

const all_data = data_volt.data['Voltage'].filter((_,y)=>mask_volt[y])
let m = Math.max(...all_data);
let min = Math.min(...all_data);

for (let k = 0; k < volt_modules.length; k++) {
    for (let j = 0; j < data_volt.data['ADC'].length; j++) {
        if (mask_volt[j] == true && data_volt.data['ADC'][j] == volt_modules[k]) {
            v_sns.push(data_volt.data['Full ID'][j])
            adcs.push(data_volt.data['ADC'][j])
            volt.push(data_volt.data['Voltage'][j])
            v_outcomes.push(data_volt.data['Outcome'][j])
        }
    }
}

const good_data = data_volt.data['Voltage'].filter((_,y)=>mask_volt[y])
let scale = d3.scaleLinear().domain([min,m]).nice()
let binner = d3.bin().domain(scale.domain()).thresholds(m*bins*5)
let d = binner(good_data)

quantities.push('Voltage')
modules.push('')
means.push(d3.mean(good_data))
stds.push(d3.deviation(good_data))

let right = d.map(x=>x.x1)
let left = d.map(x=>x.x0)
let bottom = new Array(d.length).fill(0)
let top = d.map(x=>x.length);

hist['volt'].data['right'] = right;
hist['volt'].data['left'] = left;
hist['volt'].data['top'] = top;
hist['volt'].data['bottom'] = bottom;
hist['volt'].change.emit()

td['volt'].data['Serial Number'] = v_sns;
td['volt'].data['ADC'] = adcs;
td['volt'].data['Voltage'] = volt;
td['volt'].data['Outcome'] = v_outcomes;
td['volt'].change.emit()

let mask_temp = new Array(data_temp.data['Temperature'].length).fill(false);
[...indices_temp].forEach((x)=>{mask_temp[x] = true;})

const all_data_t = data_temp.data['Temperature'].filter((_,y)=>mask_temp[y])
let m_t = Math.max(...all_data_t);
let min_t = Math.min(...all_data_t);

for (let k = 0; k < temp_modules.length; k++) {
    for (let j = 0; j < data_temp.get_length(); j++) {
        if (mask_temp[j] == true && data_temp.data['Chip'][j] == temp_modules[k]) {
            t_sns.push(data_temp.data['Full ID'][j])
            locations.push(data_temp.data['Chip'][j])
            temp.push(data_temp.data['Temperature'][j])
            t_outcomes.push(data_temp.data['Outcome'][j])
        }
    }
}

const good_data_t = data_temp.data['Temperature'].filter((_,y)=>mask_temp[y])
let scale_t = d3.scaleLinear().domain([min_t,m_t]).nice()
let binner_t = d3.bin().domain(scale_t.domain()).thresholds(m_t)
let d_t = binner_t(good_data_t)

quantities.push('Temperature')
modules.push('')
means.push(d3.mean(good_data_t))
stds.push(d3.deviation(good_data_t))

right = d_t.map(x=>x.x1)
left = d_t.map(x=>x.x0)
bottom = new Array(d_t.length).fill(0)
top = d_t.map(x=>x.length);

hist['temp'].data['right'] = right;
hist['temp'].data['left'] = left;
hist['temp'].data['top'] = top;
hist['temp'].data['bottom'] = bottom;
hist['temp'].change.emit()

td['temp'].data['Serial Number'] = t_sns;
td['temp'].data['Chip'] = locations;
td['temp'].data['Temperature'] = temp;
td['temp'].data['Outcome'] = t_outcomes;
td['temp'].change.emit()

// can use the same mask for all
let mask_adc = new Array(data_adc.data['slope'].length).fill(false);
[...indices_adc].forEach((x)=>{mask_adc[x] = true;})

const all_data_slope = data_adc.data['slope'].filter((_,y)=>mask_adc[y])
let m_s = Math.max(...all_data_slope);
let min_s = Math.min(...all_data_slope);

const all_data_int = data_adc.data['intercept'].filter((_,y)=>mask_adc[y])
let m_i = Math.max(...all_data_int);
let min_i = Math.min(...all_data_int);

const all_data_r = data_adc.data['rsquared'].filter((_,y)=>mask_adc[y])
let m_r = Math.max(...all_data_r);
let min_r = Math.min(...all_data_r);

for (let k = 0; k < adc_modules.length; k++) {
    for (let j = 0; j < data_adc.get_length(); j++) {
        if (mask_adc[j] == true && data_adc.data['ADC'][j] == adc_modules[k]) {
            mask_adc[j] = true;
            a_sns.push(data_adc.data['Full ID'][j])
            locations_adc.push(data_adc.data['ADC'][j])
            slope.push(data_adc.data['slope'][j])
            intercept.push(data_adc.data['intercept'][j])
            r_squared.push(data_adc.data['rsquared'][j])
            a_outcomes.push(data_adc.data['Outcome'][j])
        }
    }
}

// create slope data
const good_data_slope = data_adc.data['slope'].filter((_,y)=>mask_adc[y])
let scale_s = d3.scaleLinear().domain([min_s,m_s]).nice()
let binner_s = d3.bin().domain(scale_s.domain()).thresholds(m_s*bins*5)
let d_s = binner_s(good_data_slope)

quantities.push('Slope')
modules.push('')
means.push(d3.mean(good_data_slope))
stds.push(d3.deviation(good_data_slope))

let right_s = d_s.map(x=>x.x1)
let left_s = d_s.map(x=>x.x0)
let bottom_s = new Array(d_s.length).fill(0)
let top_s = d_s.map(x=>x.length);

hist['adc slope'].data['right'] = right_s;
hist['adc slope'].data['left'] = left_s;
hist['adc slope'].data['top'] = top_s;
hist['adc slope'].data['bottom'] = bottom_s;
hist['adc slope'].change.emit()

// create intercept data
const good_data_int = data_adc.data['intercept'].filter((_,y)=>mask_adc[y])
let scale_i = d3.scaleLinear().domain([min_i,m_i]).nice()
let binner_i = d3.bin().domain(scale_i.domain()).thresholds(m_i*bins)
let d_i = binner_i(good_data_int)

quantities.push('Intercept')
modules.push('')
means.push(d3.mean(good_data_int))
stds.push(d3.deviation(good_data_int))

let right_i = d_i.map(x=>x.x1)
let left_i = d_i.map(x=>x.x0)
let bottom_i = new Array(d_i.length).fill(0)
let top_i = d_i.map(x=>x.length);

hist['adc intercept'].data['right'] = right_i;
hist['adc intercept'].data['left'] = left_i;
hist['adc intercept'].data['top'] = top_i;
hist['adc intercept'].data['bottom'] = bottom_i;
hist['adc intercept'].change.emit()

// create r squared data
const good_data_r = data_adc.data['rsquared'].filter((_,y)=>mask_adc[y])
scale = d3.scaleLinear().domain([min_r,m_r]).nice()
binner = d3.bin().domain(scale.domain()).thresholds(m*bins*5)
d = binner(good_data_r)

quantities.push('R Squared')
modules.push('')
means.push(d3.mean(good_data_r))
stds.push(d3.deviation(good_data_r))

right = d.map(x=>x.x1)
left = d.map(x=>x.x0)
bottom = new Array(d.length).fill(0)
top = d.map(x=>x.length);

hist['adc r2'].data['right'] = right;
hist['adc r2'].data['left'] = left;
hist['adc r2'].data['top'] = top;
hist['adc r2'].data['bottom'] = bottom;
hist['adc r2'].change.emit()

// update data tables

td['adc'].data['Serial Number'] = a_sns;
td['adc'].data['ADC'] = locations_adc;
td['adc'].data['Slope'] = slope;
td['adc'].data['Intercept'] = intercept;
td['adc'].data['R Squared'] = r_squared;
td['adc'].data['Outcome'] = a_outcomes;
td['adc'].change.emit()

std.data['Quantity'] = quantities;
std.data['module'] = modules;
std.data['mean'] = means;
std.data['std'] = stds;
std.change.emit()
''')
    for widget in widgets:
        widget.js_on_change('value', x)
    slider.js_on_change('value', x)
    return hist, td, std

def Filter():
    # make data sources for each
    df_temp = AllData.merge(ADC_voltage, on='Test ID', how='left')
    df_temp = df_temp.dropna()
    ds_volt = ColumnDataSource(df_temp)

    df_temp = AllData.merge(ADC_resist, on='Test ID', how='left')
    df_temp = df_temp.dropna()
    ds_resist = ColumnDataSource(df_temp)

    df_temp = AllData.merge(ADC_temp, on='Test ID', how='left')
    df_temp = df_temp.dropna()
    ds_temp = ColumnDataSource(df_temp)

    df_temp = AllData.merge(ADC_main, on='Test ID', how='left')
    df_temp = df_temp.dropna()
    ds_adc = ColumnDataSource(df_temp)
        
    mc_widgets = {}
    dr_widgets = {}
    multi_choice = (lambda x,y: MultiChoice(options=x, value=[], title=y), 'value')
    start_date = (lambda x,y,z: DatePicker(min_date=x,max_date=y, value=x, title=z), 'value')
    today = datetime.date.today()
    end_date = (lambda x,y,z: DatePicker(min_date=x,max_date=y, value=today, title=z), 'value')
    min_date = pd.Timestamp((min(ds_adc.data['Time']))).date()
    date_range = []
    while min_date <= today:
        date_range.append(min_date)
        min_date += datetime.timedelta(days=1)
    columns = ['Major Type', 'Sub Type', 'Full ID', 'Person Name', 'Outcome', 'Start Date', 'End Date']
    data = [ds_adc.data['Major Type'].tolist(), ds_adc.data['Sub Type'].tolist(), ds_adc.data['Full ID'].tolist(), ds_adc.data['Person Name'].tolist(), ds_adc.data['Outcome'], date_range, date_range]
    t = [multi_choice, multi_choice, multi_choice, multi_choice, multi_choice, start_date, end_date]

    for i in range(len(columns)):
        widget_constructor, trigger = t[i]
        if t[i] == multi_choice:
            possible_vals = np.unique(data[i]).tolist()
            widget = widget_constructor(possible_vals, columns[i])
            typ = 'multi_choice'
            widget.js_on_change(trigger, CustomJS(args=dict(src1=ds_resist, src2=ds_volt, src3=ds_temp, src4=ds_adc), code='''
src1.change.emit()
src2.change.emit()
src3.change.emit()
src4.change.emit()
'''))
            mc_widgets[columns[i]] = {
                'type': typ,
                'possible_vals': possible_vals,
                'widget': widget,}
        else:
            possible_vals = data[i]
            widget = widget_constructor(min(data[i]),max(data[i]), columns[i])
            typ = 'date_range'
            widget.js_on_change(trigger, CustomJS(args=dict(src1=ds_resist, src2=ds_volt, src3=ds_temp, src4=ds_adc), code='''
src1.change.emit()
src2.change.emit()
src3.change.emit()
src4.change.emit()
'''))
            dr_widgets[columns[i]] = {
                'type': typ,
                'possible_vals': possible_vals,
                'widget': widget,}

    custom_filter = CustomJSFilter(args=dict(mc_widgets=mc_widgets, dr_widgets=dr_widgets),code=filter_code)
    views = {}
    views['resistance'] = CDSView(source=ds_resist, filters=[custom_filter])
    views['voltage'] = CDSView(source=ds_volt, filters=[custom_filter])
    views['temperature'] = CDSView(source=ds_temp, filters=[custom_filter])
    views['adc'] = CDSView(source=ds_adc, filters=[custom_filter])
    slider = Slider(start=1, end=25, value=4, step=1, title='Granularity')
    all_widgets = {**mc_widgets, **dr_widgets}
    widgets = {k:w['widget'] for k,w in all_widgets.items()}

    resist_modules = np.unique(ds_resist.data['E Link']).tolist()
    volt_modules = np.unique(ds_volt.data['ADC']).tolist()
    temp_modules = np.unique(ds_temp.data['Chip']).tolist()
    adc_modules = np.unique(ds_adc.data['ADC']).tolist()

    hist, td, std = Histograms(ds_resist, ds_volt, ds_temp, ds_adc, views, widgets.values(), resist_modules, volt_modules, temp_modules, adc_modules, slider)

    q_1 = figure(
        title='Slopes',
        x_axis_label='Slope',
        y_axis_label='Number of Boards',
        tools='pan,wheel_zoom,box_zoom,reset,save',
        width = 925
        )

    q_2 = figure(
        title='Intercepts',
        x_axis_label='Intercept',
        y_axis_label='Number of Boards',
        tools='pan,wheel_zoom,box_zoom,reset,save',
        width = 925
        )

    q_3 = figure(
        title='R Squareds',
        x_axis_label='R Squared',
        y_axis_label='Number of Boards',
        tools='pan,wheel_zoom,box_zoom,reset,save',
        width = 925
        )

    p_1 = figure(
        title='ADC Resistances',
        x_axis_label='Resistance',
        y_axis_label='Number of Boards',
        tools='pan,wheel_zoom,box_zoom,reset,save',
        width = 925
        )

    p_2 = figure(
        title='ADC Voltages',
        x_axis_label='Voltage',
        y_axis_label='Number of Boards',
        tools='pan,wheel_zoom,box_zoom,reset,save',
        width = 925
        )

    p_3 = figure(
        title='ADC Temperatures',
        x_axis_label='Temperature',
        y_axis_label='Number of Boards',
        tools='pan,wheel_zoom,box_zoom,reset,save',
        width = 925
        )

    q_1.quad(top='top', bottom='bottom', left='left', right='right', source=hist['adc slope'], color = colors[0])
    q_1.legend.click_policy='hide'
    q_1.legend.label_text_font_size = '8pt' 
    q_2.quad(top='top', bottom='bottom', left='left', right='right', source=hist['adc intercept'], color = colors[4])
    q_2.legend.click_policy='hide'
    q_2.legend.label_text_font_size = '8pt' 
    q_3.quad(top='top', bottom='bottom', left='left', right='right', source=hist['adc r2'], color = colors[8])
    q_3.legend.click_policy='hide'
    q_3.legend.label_text_font_size = '8pt' 

    for n in range(len(resist_modules)): 
        p_1.quad(top='top', bottom='bottom', left='left', right='right', source=hist['resist'][resist_modules[n]], legend_label=resist_modules[n], color = colors[n])
        p_1.legend.click_policy='hide'
        p_1.legend.label_text_font_size = '8pt' 

    p_2.quad(top='top', bottom='bottom', left='left', right='right', source=hist['volt'], color = colors[3])
    p_2.legend.click_policy='hide'
    p_2.legend.label_text_font_size = '8pt' 

    p_3.quad(top='top', bottom='bottom', left='left', right='right', source=hist['temp'], color = colors[2])
    p_3.legend.click_policy='hide'
    p_3.legend.label_text_font_size = '8pt' 

    module_template = '''
<div>
<a href="module.py?full_id=<%= value %>"target="_blank">
<%= value %>
</a>
</div> 
'''
    board = HTMLTemplateFormatter(template=module_template)

    table_columns_resist = [
                    TableColumn(field='Serial Number', title='Full ID', formatter=board),
                    TableColumn(field='E Link', title='E link'),
                    TableColumn(field='Resistance', title='Resistance'),
                    TableColumn(field='Outcome', title='Outcome'),
                    ]
    data_table_1 = DataTable(source=td['resist'], columns=table_columns_resist, autosize_mode='fit_columns')

    table_columns_volt = [
                    TableColumn(field='Serial Number', title='Full ID', formatter=board),
                    TableColumn(field='ADC', title='ADC'),
                    TableColumn(field='Voltage', title='Voltage'),
                    TableColumn(field='Outcome', title='Outcome'),
                    ]
    data_table_2 = DataTable(source=td['volt'], columns=table_columns_volt, autosize_mode='fit_columns')

    table_columns_temp = [
                    TableColumn(field='Serial Number', title='Full ID', formatter=board),
                    TableColumn(field='Chip', title='Chip'),
                    TableColumn(field='Temperature', title='Temperature'),
                    TableColumn(field='Outcome', title='Outcome'),
                    ]
    data_table_3 = DataTable(source=td['temp'], columns=table_columns_temp, autosize_mode='fit_columns')

    table_columns_adc = [
                    TableColumn(field='Serial Number', title='Full ID', formatter=board),
                    TableColumn(field='ADC', title='ADC'),
                    TableColumn(field='Slope', title='Slope'),
                    TableColumn(field='Intercept', title='Intercept'),
                    TableColumn(field='R Squared', title='R Squared'),
                    TableColumn(field='Outcome', title='Outcome'),
                    ]
    data_table_0 = DataTable(source=td['adc'], columns=table_columns_adc, autosize_mode='fit_columns')


    table_columns_4 = [
                    TableColumn(field='Quantity', title='Quantity'),
                    TableColumn(field='module', title='Module'),
                    TableColumn(field='mean', title='Mean'),
                    TableColumn(field='std', title='Standard Deviation'),
                    ]
    data_table_4 = DataTable(source=std, columns=table_columns_4, autosize_mode='fit_columns')
            
    w = [*widgets.values()]

    subtypes = {}
    for major in np.unique(ds_adc.data['Major Type'].tolist()).tolist():
        subtypes[major] = np.unique(df_temp.query('`Major Type` == @major')['Sub Type'].values.tolist()).tolist()
    serial_numbers = {}
    for s in np.unique(ds_adc.data['Sub Type'].tolist()).tolist():
        serial_numbers[s] = np.unique(df_temp.query('`Sub Type` == @s')['Full ID'].values.tolist()).tolist()
    
    all_subtypes = np.unique(ds_adc.data['Sub Type'].tolist()).tolist()
    all_serials = np.unique(ds_adc.data['Full ID'].tolist()).tolist()

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
    
    #L = ADC_Gaussian()

    layout = row(column(row(w[0:3]),
                    row(w[3:5]), 
                    row(w[5:]), 
                    slider, 
                    q_1, q_2, q_3,
                    p_1, p_2, p_3,
                    data_table_0,
                    data_table_1,
                    data_table_2,
                    data_table_3,
                    data_table_4))
    plot_json = json.dumps(json_item(layout))
    return plot_json

def ADC_Gaussian2(data_resist, data_volt, data_temp, data_adc, view, widgets, serial_numbers, resist_modules, volt_modules, temp_modules, adc_modules, n_sigma):
    hist = {}
    pf = {}
    td = {}

    hist['adc slope'] = ColumnDataSource(data={'top':[], 'bottom':[], 'left':[], 'right':[]})
    hist['adc intercept'] = ColumnDataSource(data={'top':[], 'bottom':[], 'left':[], 'right':[]})
    hist['adc r2'] = ColumnDataSource(data={'top':[], 'bottom':[], 'left':[], 'right':[]})
    hist['resist'] = ColumnDataSource(data={'top':[], 'bottom':[], 'left':[], 'right':[]})
    hist['volt'] = ColumnDataSource(data={'top':[], 'bottom':[], 'left':[], 'right':[]})
    hist['temp'] = ColumnDataSource(data={'top':[], 'bottom':[], 'left':[], 'right':[]})

    pf['adc slope'] = ColumnDataSource(data={'pass':[], 'fail':[], 'x':['Fail', 'Pass']})
    pf['adc intercept'] = ColumnDataSource(data={'pass':[], 'fail':[], 'x':['Fail', 'Pass']})
    pf['adc r2'] = ColumnDataSource(data={'pass':[], 'fail':[], 'x':['Fail', 'Pass']})
    pf['resist'] = ColumnDataSource(data={'pass':[], 'fail':[], 'x':['Fail', 'Pass']})
    pf['volt'] = ColumnDataSource(data={'pass':[], 'fail':[], 'x':['Fail', 'Pass']})
    pf['temp'] = ColumnDataSource(data={'pass':[], 'fail':[], 'x':['Fail', 'Pass']})

    td['resist'] = ColumnDataSource(data={'Serial Number':[], 'Module':[], 'Pass/Fail':[], 'Deviation':[]})
    td['volt'] = ColumnDataSource(data={'Serial Number':[], 'Module':[], 'Pass/Fail':[], 'Deviation':[]})
    td['temp'] = ColumnDataSource(data={'Serial Number':[], 'Module':[], 'Pass/Fail':[], 'Deviation':[]})
    td['adc slope'] = ColumnDataSource(data={'Serial Number':[], 'Module':[], 'Pass/Fail':[], 'Deviation':[]})
    td['adc intercept'] = ColumnDataSource(data={'Serial Number':[], 'Module':[], 'Pass/Fail':[], 'Deviation':[]})
    td['adc r2'] = ColumnDataSource(data={'Serial Number':[], 'Module':[], 'Pass/Fail':[], 'Deviation':[]})

    x = CustomJS(args=dict(hist=hist, data_resist=data_resist, data_volt=data_volt, data_temp=data_temp, serial_numbers=serial_numbers, resist_modules=resist_modules, volt_modules=volt_modules, temp_modules=temp_modules, view=view, n_sigma=n_sigma, data_adc=data_adc, adc_modules=adc_modules, pf=pf, td=td),code='''
// this follows the same pattern as residual plots for WagonDB, just for way more quantities
const indices_resist = view['resistance'].filters[0].compute_indices(data_resist);
const indices_volt = view['voltage'].filters[0].compute_indices(data_volt);
const indices_temp = view['temperature'].filters[0].compute_indices(data_temp);
const indices_adc = view['adc'].filters[0].compute_indices(data_adc);

const residules_resist = [];
const residules_volt = [];
const residules_temp = [];
const residules_slope = [];
const residules_int = [];
const residules_r2 = [];
var chis_1 = {};
var chis_2 = {};
var chis_3 = {};
var chis_4 = {};
var chis_5 = {};
var chis_6 = {};

for (let i = 0; i < serial_numbers.length; i++) {
    chis_1[serial_numbers[i]] = [];
    chis_2[serial_numbers[i]] = [];
    chis_3[serial_numbers[i]] = [];
    chis_4[serial_numbers[i]] = [];
    chis_5[serial_numbers[i]] = [];
    chis_6[serial_numbers[i]] = [];
}

let binner = d3.bin()

for (let k = 0; k < resist_modules.length; k++) {
    let mask_resist = new Array(data_resist.data['Resistance'].length).fill(false);
    [...indices_resist].forEach((x)=>{mask_resist[x] = true;})

    for (let j = 0; j < data_resist.data['E Link'].length; j++) {
        if (mask_resist[j] == true && data_resist.data['E Link'][j] == resist_modules[k]) {
            mask_resist[j] = true;
        } else {
            mask_resist[j] = false;
        }
    }

    const good_data = data_resist.data['Resistance'].filter((_,y)=>mask_resist[y])
    let mean = d3.mean(good_data)
    let std = d3.deviation(good_data)
    for (let sn = 0; sn < serial_numbers.length; sn++) {
        let mask_sn = new Array(data_resist.data['Resistance'].length).fill(false);
        [...indices_resist].forEach((x)=>{mask_sn[x] = true;})

        for (let j = 0; j < data_resist.get_length(); j++) {
            if (mask_sn[j] == true && data_resist.data['Full ID'][j] == serial_numbers[sn] && data_resist.data['E Link'][j] == resist_modules[k]){
                mask_sn[j] = true;
                let x = data_resist.data['Resistance'][j] - mean;
                if (std == 0) {
                    let chi = 0;
                    residules_resist.push(chi)
                } else {
                    let chi = x/std;
                    residules_resist.push(chi)
                }
            } else {
                mask_sn[j] = false;
            }
        }
        const good_data_sn = data_resist.data['Resistance'].filter((_,y)=>mask_sn[y])
        let mean_sn = d3.mean(good_data_sn)
        let y = mean_sn - mean;
        let chi_sn = y/std;
        chis_1[serial_numbers[sn]].push(Math.abs(chi_sn))
    }
}

let d_1 = binner(residules_resist)
let right_1 = d_1.map(x=>x.x1)
let left_1 = d_1.map(x=>x.x0)
let bottom_1 = new Array(d_1.length).fill(0)
let top_1 = d_1.map(x=>x.length);

hist['resist'].data['right'] = right_1;
hist['resist'].data['left'] = left_1;
hist['resist'].data['bottom'] = bottom_1;
hist['resist'].data['top'] = top_1;
hist['resist'].change.emit()

let t_pass_1 = 0;
let t_fail_1 = 0;
const sn_td_1 = [];
const mod_td_1 = [];
const chi_td_1 = [];
const pf_td_1 = [];
for (let sn = 0; sn < serial_numbers.length; sn++) {
    let pass = 0;
    let fail = 0;
    for (let c = 0; c < chis_1[serial_numbers[sn]].length; c++) {
        let chi_i = chis_1[serial_numbers[sn]][c]
        if (chi_i <= n_sigma.value) {
            pass = pass + 1;
            pf_td_1.push('PASS')
        } else {
            fail = fail + 1;
            pf_td_1.push('FAIL')
        }
        sn_td_1.push(serial_numbers[sn])
        mod_td_1.push(resist_modules[c])
        chi_td_1.push(chi_i)
    }
    if (fail == 0) {
        t_pass_1 = t_pass_1 + 1;
    } else {
        t_fail_1 = t_fail_1 + 1;
    }
}
pf['resist'].data['pass'] = [0, t_pass_1];
pf['resist'].data['fail'] = [t_fail_1, 0];
pf['resist'].change.emit()

td['resist'].data['Serial Number'] = sn_td_1;
td['resist'].data['Module'] = mod_td_1;
td['resist'].data['Deviation'] = chi_td_1;
td['resist'].data['Pass/Fail'] = pf_td_1;
td['resist'].change.emit()

for (let k = 0; k < volt_modules.length; k++) {
    let mask_volt = new Array(data_volt.data['Voltage'].length).fill(false);
    [...indices_volt].forEach((x)=>{mask_volt[x] = true;})

    for (let j = 0; j < data_volt.data['ADC'].length; j++) {
        if (mask_volt[j] == true && data_volt.data['ADC'][j] == volt_modules[k]) {
            mask_volt[j] = true;
        } else {
            mask_volt[j] = false;
        }
    }

    const good_data = data_volt.data['Voltage'].filter((_,y)=>mask_volt[y])
    let mean = d3.mean(good_data)
    let std = d3.deviation(good_data)
    for (let sn = 0; sn < serial_numbers.length; sn++) {
        let mask_sn = new Array(data_volt.data['Voltage'].length).fill(false);
        [...indices_volt].forEach((x)=>{mask_sn[x] = true;})

        for (let j = 0; j < data_volt.get_length(); j++) {
            if (mask_sn[j] == true && data_volt.data['Full ID'][j] == serial_numbers[sn] && data_volt.data['ADC'][j] == volt_modules[k]){
                mask_sn[j] = true;
                let x = data_volt.data['Voltage'][j] - mean;
                if (std == 0) {
                    let chi = 0;
                    residules_volt.push(chi)
                } else {
                    let chi = x/std;
                    residules_volt.push(chi)
                } 
            } else {
                mask_sn[j] = false;
            }
        }
        const good_data_sn = data_volt.data['Voltage'].filter((_,y)=>mask_sn[y])
        let mean_sn = d3.mean(good_data_sn)
        let y = mean_sn - mean;
        if (std == 0) {
            let chi_sn = 0;
            chis_2[serial_numbers[sn]].push(Math.abs(chi_sn))
        } else {
            let chi_sn = y/std;
            chis_2[serial_numbers[sn]].push(Math.abs(chi_sn))
        } 
    }
}

let d_2 = binner(residules_volt)
let right_2 = d_2.map(x=>x.x1)
let left_2 = d_2.map(x=>x.x0)
let bottom_2 = new Array(d_2.length).fill(0)
let top_2 = d_2.map(x=>x.length);

hist['volt'].data['right'] = right_2;
hist['volt'].data['left'] = left_2;
hist['volt'].data['bottom'] = bottom_2;
hist['volt'].data['top'] = top_2;
hist['volt'].change.emit()

let t_pass_2 = 0;
let t_fail_2 = 0;
const sn_td_2 = [];
const mod_td_2 = [];
const chi_td_2 = [];
const pf_td_2 = [];
for (let sn = 0; sn < serial_numbers.length; sn++) {
    let pass = 0;
    let fail = 0;
    for (let c = 0; c < chis_2[serial_numbers[sn]].length; c++) {
        let chi_i = chis_2[serial_numbers[sn]][c]
        if (chi_i <= n_sigma.value) {
            pass = pass + 1;
            pf_td_2.push('PASS')
        } else {
            fail = fail + 1;
            pf_td_2.push('FAIL')
        }
        sn_td_2.push(serial_numbers[sn])
        mod_td_2.push(volt_modules[c])
        chi_td_2.push(chi_i)
    }
    if (fail == 0) {
        t_pass_2 = t_pass_2 + 1;
    } else {
        t_fail_2 = t_fail_2 + 1;
    }
}
pf['volt'].data['pass'] = [0, t_pass_2];
pf['volt'].data['fail'] = [t_fail_2, 0];
pf['volt'].change.emit()

td['volt'].data['Serial Number'] = sn_td_2;
td['volt'].data['Module'] = mod_td_2;
td['volt'].data['Deviation'] = chi_td_2;
td['volt'].data['Pass/Fail'] = pf_td_2;
td['volt'].change.emit()

for (let k = 0; k < temp_modules.length; k++) {
    let mask_temp = new Array(data_temp.data['Temperature'].length).fill(false);
    [...indices_temp].forEach((x)=>{mask_temp[x] = true;})

    for (let j = 0; j < data_temp.data['Chip'].length; j++) {
        if (mask_temp[j] == true && data_temp.data['Chip'][j] == temp_modules[k]) {
            mask_temp[j] = true;
        } else {
            mask_temp[j] = false;
        }
    }

    const good_data = data_temp.data['Temperature'].filter((_,y)=>mask_temp[y])
    let mean = d3.mean(good_data)
    let std = d3.deviation(good_data)
    for (let sn = 0; sn < serial_numbers.length; sn++) {
        let mask_sn = new Array(data_temp.data['Temperature'].length).fill(false);
        [...indices_temp].forEach((x)=>{mask_sn[x] = true;})

        for (let j = 0; j < data_temp.get_length(); j++) {
            if (mask_sn[j] == true && data_temp.data['Full ID'][j] == serial_numbers[sn] && data_temp.data['Chip'][j] == temp_modules[k]){
                mask_sn[j] = true;
                let x = data_temp.data['Temperature'][j] - mean;
                let chi = x/std;
                residules_temp.push(chi)
            } else {
                mask_sn[j] = false;
            }
        }
        const good_data_sn = data_temp.data['Temperature'].filter((_,y)=>mask_sn[y])
        let mean_sn = d3.mean(good_data_sn)
        let y = mean_sn - mean;
        let chi_sn = y/std;
        chis_3[serial_numbers[sn]].push(Math.abs(chi_sn))
    }
}

let d_3 = binner(residules_temp)
let right_3 = d_3.map(x=>x.x1)
let left_3 = d_3.map(x=>x.x0)
let bottom_3 = new Array(d_3.length).fill(0)
let top_3 = d_3.map(x=>x.length);

hist['temp'].data['right'] = right_3;
hist['temp'].data['left'] = left_3;
hist['temp'].data['bottom'] = bottom_3;
hist['temp'].data['top'] = top_3;
hist['temp'].change.emit()

let t_pass_3 = 0;
let t_fail_3 = 0;
const sn_td_3 = [];
const mod_td_3 = [];
const chi_td_3 = [];
const pf_td_3 = [];
for (let sn = 0; sn < serial_numbers.length; sn++) {
    let pass = 0;
    let fail = 0;
    for (let c = 0; c < chis_3[serial_numbers[sn]].length; c++) {
        let chi_i = chis_3[serial_numbers[sn]][c]
        if (chi_i <= n_sigma.value) {
            pass = pass + 1;
            pf_td_3.push('PASS')
        } else {
            fail = fail + 1;
            pf_td_3.push('FAIL')
        }
        sn_td_3.push(serial_numbers[sn])
        mod_td_3.push(temp_modules[c])
        chi_td_3.push(chi_i)
    }
    if (fail == 0) {
        t_pass_3 = t_pass_3 + 1;
    } else {
        t_fail_3 = t_fail_3 + 1;
    }
}
pf['temp'].data['pass'] = [0, t_pass_3];
pf['temp'].data['fail'] = [t_fail_3, 0];
pf['temp'].change.emit()

td['temp'].data['Serial Number'] = sn_td_3;
td['temp'].data['Module'] = mod_td_3;
td['temp'].data['Deviation'] = chi_td_3;
td['temp'].data['Pass/Fail'] = pf_td_3;
td['temp'].change.emit()

let mask_adc = new Array(data_adc.data['slope'].length).fill(false);
[...indices_adc].forEach((x)=>{mask_adc[x] = true;})

const good_data = data_adc.data['slope'].filter((_,y)=>mask_adc[y])
let mean = d3.mean(good_data)
let std = d3.deviation(good_data)
for (let sn = 0; sn < serial_numbers.length; sn++) {
    for (let k = 0; k < adc_modules.length; k++) {
        let mask_sn = new Array(data_adc.data['slope'].length).fill(false);
        [...indices_adc].forEach((x)=>{mask_sn[x] = true;})

        for (let j = 0; j < data_adc.get_length(); j++) {
            if (mask_sn[j] == true && data_adc.data['Full ID'][j] == serial_numbers[sn] && data_adc.data['ADC'][j] == adc_modules[k]){
                mask_sn[j] = true;
                let x = data_adc.data['slope'][j] - mean;
                let chi = x/std;
                residules_slope.push(chi)
            } else {
                mask_sn[j] = false;
            }
        }
        const good_data_sn = data_adc.data['slope'].filter((_,y)=>mask_sn[y])
        let mean_sn = d3.mean(good_data_sn)
        let y = mean_sn - mean;
        let chi_sn = y/std;
        chis_4[serial_numbers[sn]].push(Math.abs(chi_sn))
    }
}

let d_4 = binner(residules_slope)
let right_4 = d_4.map(x=>x.x1)
let left_4 = d_4.map(x=>x.x0)
let bottom_4 = new Array(d_4.length).fill(0)
let top_4 = d_4.map(x=>x.length);

hist['adc slope'].data['right'] = right_4;
hist['adc slope'].data['left'] = left_4;
hist['adc slope'].data['bottom'] = bottom_4;
hist['adc slope'].data['top'] = top_4;
hist['adc slope'].change.emit()

let t_pass_4 = 0;
let t_fail_4 = 0;
const sn_td_4 = [];
const mod_td_4 = [];
const chi_td_4 = [];
const pf_td_4 = [];
for (let sn = 0; sn < serial_numbers.length; sn++) {
    let pass = 0;
    let fail = 0;
    for (let c = 0; c < chis_4[serial_numbers[sn]].length; c++) {
        let chi_i = chis_4[serial_numbers[sn]][c]
        if (chi_i <= n_sigma.value) {
            pass = pass + 1;
            pf_td_4.push('PASS')
        } else {
            fail = fail + 1;
            pf_td_4.push('FAIL')
        }
        sn_td_4.push(serial_numbers[sn])
        mod_td_4.push(adc_modules[c])
        chi_td_4.push(chi_i)
    }
    if (fail == 0) {
        t_pass_4 = t_pass_4 + 1;
    } else {
        t_fail_4 = t_fail_4 + 1;
    }
}
pf['adc slope'].data['pass'] = [0, t_pass_4];
pf['adc slope'].data['fail'] = [t_fail_4, 0];
pf['adc slope'].change.emit()

td['adc slope'].data['Serial Number'] = sn_td_4;
td['adc slope'].data['Module'] = mod_td_4;
td['adc slope'].data['Deviation'] = chi_td_4;
td['adc slope'].data['Pass/Fail'] = pf_td_4;
td['adc slope'].change.emit()

const good_data_2 = data_adc.data['intercept'].filter((_,y)=>mask_adc[y])
let mean_i = d3.mean(good_data_2)
let std_i = d3.deviation(good_data_2)
for (let sn = 0; sn < serial_numbers.length; sn++) {
    for (let k = 0; k < adc_modules.length; k++) {
        let mask_sn = new Array(data_adc.data['slope'].length).fill(false);
        [...indices_adc].forEach((x)=>{mask_sn[x] = true;})

        for (let j = 0; j < data_adc.get_length(); j++) {
            if (mask_sn[j] == true && data_adc.data['Full ID'][j] == serial_numbers[sn] && data_adc.data['ADC'][j] == adc_modules[k]){
                mask_sn[j] = true;
                let x = data_adc.data['intercept'][j] - mean_i;
                let chi = x/std_i;
                residules_int.push(chi)
            } else {
                mask_sn[j] = false;
            }
        }
        const good_data_sn = data_adc.data['intercept'].filter((_,y)=>mask_sn[y])
        let mean_sn = d3.mean(good_data_sn)
        let y = mean_sn - mean_i;
        let chi_sn = y/std_i;
        chis_5[serial_numbers[sn]].push(Math.abs(chi_sn))
    }
}

let d_5 = binner(residules_int)
let right_5 = d_5.map(x=>x.x1)
let left_5 = d_5.map(x=>x.x0)
let bottom_5 = new Array(d_5.length).fill(0)
let top_5 = d_5.map(x=>x.length);

hist['adc intercept'].data['right'] = right_5;
hist['adc intercept'].data['left'] = left_5;
hist['adc intercept'].data['bottom'] = bottom_5;
hist['adc intercept'].data['top'] = top_5;
hist['adc intercept'].change.emit()

let t_pass_5 = 0;
let t_fail_5 = 0;
const sn_td_5 = [];
const mod_td_5 = [];
const chi_td_5 = [];
const pf_td_5 = [];
for (let sn = 0; sn < serial_numbers.length; sn++) {
    let pass = 0;
    let fail = 0;
    for (let c = 0; c < chis_5[serial_numbers[sn]].length; c++) {
        let chi_i = chis_5[serial_numbers[sn]][c]
        if (chi_i <= n_sigma.value) {
            pass = pass + 1;
            pf_td_5.push('PASS')
        } else {
            fail = fail + 1;
            pf_td_5.push('FAIL')
        }
        sn_td_5.push(serial_numbers[sn])
        mod_td_5.push(adc_modules[c])
        chi_td_5.push(chi_i)
    }
    if (fail == 0) {
        t_pass_5 = t_pass_5 + 1;
    } else {
        t_fail_5 = t_fail_5 + 1;
    }
}
pf['adc intercept'].data['pass'] = [0, t_pass_5];
pf['adc intercept'].data['fail'] = [t_fail_5, 0];
pf['adc intercept'].change.emit()

td['adc intercept'].data['Serial Number'] = sn_td_5;
td['adc intercept'].data['Module'] = mod_td_5;
td['adc intercept'].data['Deviation'] = chi_td_5;
td['adc intercept'].data['Pass/Fail'] = pf_td_5;
td['adc intercept'].change.emit()

const good_data_3 = data_adc.data['rsquared'].filter((_,y)=>mask_adc[y])
let mean_r = d3.mean(good_data_3)
let std_r = d3.deviation(good_data_3)
for (let sn = 0; sn < serial_numbers.length; sn++) {
    for (let k = 0; k < adc_modules.length; k++) {
        let mask_sn = new Array(data_adc.data['slope'].length).fill(false);
        [...indices_adc].forEach((x)=>{mask_sn[x] = true;})

        for (let j = 0; j < data_adc.get_length(); j++) {
            if (mask_sn[j] == true && data_adc.data['Full ID'][j] == serial_numbers[sn] && data_adc.data['ADC'][j] == adc_modules[k]){
                mask_sn[j] = true;
                let x = data_adc.data['rsquared'][j] - mean_r;
                let chi = x/std_r;
                residules_r2.push(chi)
            } else {
                mask_sn[j] = false;
            }
        }
        const good_data_sn = data_adc.data['rsquared'].filter((_,y)=>mask_sn[y])
        let mean_sn = d3.mean(good_data_sn)
        let y = mean_sn - mean_r;
        let chi_sn = y/std_r;
        chis_6[serial_numbers[sn]].push(Math.abs(chi_sn))
    }
}

let d_6 = binner(residules_r2)
let right_6 = d_6.map(x=>x.x1)
let left_6 = d_6.map(x=>x.x0)
let bottom_6 = new Array(d_6.length).fill(0)
let top_6 = d_6.map(x=>x.length);

hist['adc r2'].data['right'] = right_6;
hist['adc r2'].data['left'] = left_6;
hist['adc r2'].data['bottom'] = bottom_6;
hist['adc r2'].data['top'] = top_6;
hist['adc r2'].change.emit()

let t_pass_6 = 0;
let t_fail_6 = 0;
const sn_td_6 = [];
const mod_td_6 = [];
const chi_td_6 = [];
const pf_td_6 = [];
for (let sn = 0; sn < serial_numbers.length; sn++) {
    let pass = 0;
    let fail = 0;
    for (let c = 0; c < chis_6[serial_numbers[sn]].length; c++) {
        let chi_i = chis_6[serial_numbers[sn]][c]
        if (chi_i <= n_sigma.value) {
            pass = pass + 1;
            pf_td_6.push('PASS')
        } else {
            fail = fail + 1;
            pf_td_6.push('FAIL')
        }
        sn_td_6.push(serial_numbers[sn])
        mod_td_6.push(adc_modules[c])
        chi_td_6.push(chi_i)
    }
    if (fail == 0) {
        t_pass_6 = t_pass_6 + 1;
    } else {
        t_fail_6 = t_fail_6 + 1;
    }
}
pf['adc r2'].data['pass'] = [0, t_pass_6];
pf['adc r2'].data['fail'] = [t_fail_6, 0];
pf['adc r2'].change.emit()

td['adc r2'].data['Serial Number'] = sn_td_6;
td['adc r2'].data['Module'] = mod_td_6;
td['adc r2'].data['Deviation'] = chi_td_6;
td['adc r2'].data['Pass/Fail'] = pf_td_6;
td['adc r2'].change.emit()
''')
    for widget in widgets:
        widget.js_on_change('value', x)
    n_sigma.js_on_change('value', x)
    return hist, pf, td

def ADC_Gaussian():
    df_temp = AllData.merge(ADC_voltage, on='Test ID', how='left')
    df_temp = df_temp.dropna()
    ds_volt = ColumnDataSource(df_temp)

    serial_numbers = np.unique(ds_volt.data['Full ID'].tolist()).tolist()

    df_temp = AllData.merge(ADC_resist, on='Test ID', how='left')
    df_temp = df_temp.dropna()
    ds_resist = ColumnDataSource(df_temp)

    df_temp = AllData.merge(ADC_temp, on='Test ID', how='left')
    df_temp = df_temp.dropna()
    ds_temp = ColumnDataSource(df_temp)

    df_temp = AllData.merge(ADC_main, on='Test ID', how='left')
    df_temp = df_temp.dropna()
    ds_adc = ColumnDataSource(df_temp)
        
    mc_widgets = {}
    dr_widgets = {}
    multi_choice = (lambda x,y: MultiChoice(options=x, value=[], title=y), 'value')
    start_date = (lambda x,y,z: DatePicker(min_date=x,max_date=y, value=x, title=z), 'value')
    today = datetime.date.today()
    end_date = (lambda x,y,z: DatePicker(min_date=x,max_date=y, value=today, title=z), 'value')
    min_date = pd.Timestamp((min(ds_adc.data['Time']))).date()
    date_range = []
    while min_date <= today:
        date_range.append(min_date)
        min_date += datetime.timedelta(days=1)
    columns = ['Major Type', 'Sub Type', 'Full ID', 'Outcome', 'Start Date', 'End Date']
    data = [ds_adc.data['Major Type'].tolist(), ds_adc.data['Sub Type'].tolist(), ds_adc.data['Full ID'], ds_adc.data['Outcome'], date_range, date_range]
    t = [multi_choice, multi_choice, multi_choice, multi_choice, start_date, end_date]

    for i in range(len(columns)):
        widget_constructor, trigger = t[i]
        if t[i] == multi_choice:
            possible_vals = np.unique(data[i]).tolist()
            widget = widget_constructor(possible_vals, columns[i])
            typ = 'multi_choice'
            widget.js_on_change(trigger, CustomJS(args=dict(src1=ds_resist, src2=ds_volt, src3=ds_temp, src4=ds_adc), code='''
src1.change.emit()
src2.change.emit()
src3.change.emit()
src4.change.emit()
'''))
            mc_widgets[columns[i]] = {
                'type': typ,
                'possible_vals': possible_vals,
                'widget': widget,}
        else:
            possible_vals = data[i]
            widget = widget_constructor(min(data[i]),max(data[i]), columns[i])
            typ = 'date_range'
            widget.js_on_change(trigger, CustomJS(args=dict(src1=ds_resist, src2=ds_volt, src3=ds_temp, src4=ds_adc), code='''
src1.change.emit()
src2.change.emit()
src3.change.emit()
src4.change.emit()
'''))
            dr_widgets[columns[i]] = {
                'type': typ,
                'possible_vals': possible_vals,
                'widget': widget,}

    custom_filter = CustomJSFilter(args=dict(mc_widgets=mc_widgets, dr_widgets=dr_widgets),code=filter_code)
    views = {}
    views['resistance'] = CDSView(source=ds_resist, filters=[custom_filter])
    views['voltage'] = CDSView(source=ds_volt, filters=[custom_filter])
    views['temperature'] = CDSView(source=ds_temp, filters=[custom_filter])
    views['adc'] = CDSView(source=ds_adc, filters=[custom_filter])
    all_widgets = {**mc_widgets, **dr_widgets}
    widgets = {k:w['widget'] for k,w in all_widgets.items()}

    resist_modules = np.unique(ds_resist.data['E Link']).tolist()
    volt_modules = np.unique(ds_volt.data['ADC']).tolist()
    temp_modules = np.unique(ds_temp.data['Chip']).tolist()
    adc_modules = np.unique(ds_adc.data['ADC']).tolist()

    n_sigma = NumericInput(value=1, low=0.01, high=10, title='# of standard deviations for passing', mode='float')

    hist, pf, td = ADC_Gaussian2(ds_resist, ds_volt, ds_temp, ds_adc, views, widgets.values(), serial_numbers, resist_modules, volt_modules, temp_modules, adc_modules, n_sigma)

    q_1 = figure(
        title='Residual Distribution for Slopes',
        x_axis_label='# of Standard Deviations from Mean',
        y_axis_label='Number of Boards',
        tools='pan,wheel_zoom,box_zoom,reset,save',
        width = 925
        )

    q_2 = figure(
        title='Residual Distribution for Intercepts',
        x_axis_label='# of Standard Deviations from Mean',
        y_axis_label='Number of Boards',
        tools='pan,wheel_zoom,box_zoom,reset,save',
        width = 925
        )

    q_3 = figure(
        title='Residual Distribution for R Squareds',
        x_axis_label='# of Standard Deviations from Mean',
        y_axis_label='Number of Boards',
        tools='pan,wheel_zoom,box_zoom,reset,save',
        width = 925
        )

    q_4 = figure(
        title='Residual Distribution for ADC Resistances',
        x_axis_label='# of Standard Deviations from Mean',
        y_axis_label='Number of Boards',
        tools='pan,wheel_zoom,box_zoom,reset,save',
        width = 925
        )

    q_5 = figure(
        title='Residual Distribution for ADC Voltages',
        x_axis_label='# of Standard Deviations from Mean',
        y_axis_label='Number of Boards',
        tools='pan,wheel_zoom,box_zoom,reset,save',
        width = 925
        )

    q_6 = figure(
        title='Residual Distribution for ADC Temperatures',
        x_axis_label='# of Standard Deviations from Mean',
        y_axis_label='Number of Boards',
        tools='pan,wheel_zoom,box_zoom,reset,save',
        width = 925
        )

    q_1.quad(top='top', bottom='bottom', left='left', right='right', source=hist['adc slope'], color = colors[0])
    q_1.visible = False

    q_2.quad(top='top', bottom='bottom', left='left', right='right', source=hist['adc intercept'], color = colors[0])
    q_2.visible = False

    q_3.quad(top='top', bottom='bottom', left='left', right='right', source=hist['adc r2'], color = colors[0])
    q_3.visible = False

    q_4.quad(top='top', bottom='bottom', left='left', right='right', source=hist['resist'], color = colors[0])
    q_4.visible = False

    q_5.quad(top='top', bottom='bottom', left='left', right='right', source=hist['volt'], color = colors[0])
    q_5.visible = False

    q_6.quad(top='top', bottom='bottom', left='left', right='right', source=hist['temp'], color = colors[0])
    q_6.visible = False

    p_1 = figure(
        title='Pass vs Fail for Slope',
        x_range=pf['adc slope'].data['x'],
        x_axis_label='',
        y_axis_label='Number of Boards',
        tools='pan,wheel_zoom,box_zoom,reset,save',
        width = 925
        )

    p_2 = figure(
        title='Pass vs Fail for Intercept',
        x_range=pf['adc intercept'].data['x'],
        x_axis_label='',
        y_axis_label='Number of Boards',
        tools='pan,wheel_zoom,box_zoom,reset,save',
        width = 925
        )

    p_3 = figure(
        title='Pass vs Fail for R Squared',
        x_range=pf['adc r2'].data['x'],
        x_axis_label='',
        y_axis_label='Number of Boards',
        tools='pan,wheel_zoom,box_zoom,reset,save',
        width = 925
        )

    p_4 = figure(
        title='Pass vs Fail for ADC Resistance',
        x_range=pf['resist'].data['x'],
        x_axis_label='',
        y_axis_label='Number of Boards',
        tools='pan,wheel_zoom,box_zoom,reset,save',
        width = 925
        )

    p_5 = figure(
        title='Pass vs Fail for ADC Voltage',
        x_range=pf['volt'].data['x'],
        x_axis_label='',
        y_axis_label='Number of Boards',
        tools='pan,wheel_zoom,box_zoom,reset,save',
        width = 925
        )

    p_6 = figure(
        title='Pass vs Fail for ADC Temperature',
        x_range=pf['temp'].data['x'],
        x_axis_label='',
        y_axis_label='Number of Boards',
        tools='pan,wheel_zoom,box_zoom,reset,save',
        width = 925
        )

    p_1.vbar(x='x', top='pass', source=pf['adc slope'], color=colors[2], width=0.8)
    p_1.vbar(x='x', top='fail', source=pf['adc slope'], color=colors[3], width=0.8)
    p_1.visible = False

    p_2.vbar(x='x', top='pass', source=pf['adc intercept'], color=colors[2], width=0.8)
    p_2.vbar(x='x', top='fail', source=pf['adc intercept'], color=colors[3], width=0.8)
    p_2.visible = False

    p_3.vbar(x='x', top='pass', source=pf['adc r2'], color=colors[2], width=0.8)
    p_3.vbar(x='x', top='fail', source=pf['adc r2'], color=colors[3], width=0.8)
    p_3.visible = False

    p_4.vbar(x='x', top='pass', source=pf['resist'], color=colors[2], width=0.8)
    p_4.vbar(x='x', top='fail', source=pf['resist'], color=colors[3], width=0.8)
    p_4.visible = False

    p_5.vbar(x='x', top='pass', source=pf['volt'], color=colors[2], width=0.8)
    p_5.vbar(x='x', top='fail', source=pf['volt'], color=colors[3], width=0.8)
    p_5.visible = False

    p_6.vbar(x='x', top='pass', source=pf['temp'], color=colors[2], width=0.8)
    p_6.vbar(x='x', top='fail', source=pf['temp'], color=colors[3], width=0.8)
    p_6.visible = False

    q_plots = {'Slope': q_1, 'Intercept': q_2, 'R Squared': q_3, 'Resistance': q_4, 'Voltage': q_5, 'Temperature': q_6}
    p_plots = {'Slope': p_1, 'Intercept': p_2, 'R Squared': p_3, 'Resistance': p_4, 'Voltage': p_5, 'Temperature': p_6}

    table_columns = [
                    TableColumn(field='Serial Number', title='Full ID'),
                    TableColumn(field='Module', title='Module'),
                    TableColumn(field='Deviation', title='Deviation'),
                    TableColumn(field='Pass/Fail', title='Pass/Fail'),
                    ]
    d_1 = DataTable(source=td['adc slope'], columns=table_columns, autosize_mode='fit_columns')
    d_2 = DataTable(source=td['adc intercept'], columns=table_columns, autosize_mode='fit_columns')
    d_3 = DataTable(source=td['adc r2'], columns=table_columns, autosize_mode='fit_columns')
    d_4 = DataTable(source=td['resist'], columns=table_columns, autosize_mode='fit_columns')
    d_5 = DataTable(source=td['volt'], columns=table_columns, autosize_mode='fit_columns')
    d_6 = DataTable(source=td['temp'], columns=table_columns, autosize_mode='fit_columns')
    d_1.visible = False
    d_2.visible = False
    d_3.visible = False
    d_4.visible = False
    d_5.visible = False
    d_6.visible = False

    tables = {'Slope': d_1, 'Intercept': d_2, 'R Squared': d_3, 'Resistance': d_4, 'Voltage': d_5, 'Temperature': d_6}

    w = [*widgets.values()]

    subtypes = {}
    for major in np.unique(ds_adc.data['Major Type'].tolist()).tolist():
        subtypes[major] = np.unique(df_temp.query('`Major Type` == @major')['Sub Type'].values.tolist()).tolist()
    serial_numbers = {}
    for s in np.unique(ds_adc.data['Sub Type'].tolist()).tolist():
        serial_numbers[s] = np.unique(df_temp.query('`Sub Type` == @s')['Full ID'].values.tolist()).tolist()
    
    all_subtypes = np.unique(ds_adc.data['Sub Type'].tolist()).tolist()
    all_serials = np.unique(ds_adc.data['Full ID'].tolist()).tolist()

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

    # this allows you to select which value you're seeing residuals for
    display_plot = CustomJS(args=dict(p_plots=p_plots, q_plots=q_plots, tables=tables), code=('''
for (let [name,plot] of Object.entries(p_plots)){
    if (name == this.value){
        plot.visible = true
    } else {
        plot.visible = false
    }
}
for (let [name,plot] of Object.entries(q_plots)){
    if (name == this.value){
        plot.visible = true
    } else {
        plot.visible = false
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
    
    select = Select(title='ADC Value', options=list(q_plots.keys()))
    select.js_on_change('value', display_plot)
        
    # column and row objects only take it lists, need to make arguments lists
    layout = column(row(w[0:2] + [select]),
                    row(w[2:4] + [n_sigma]),
                    row(w[4:]),
                    column(list(q_plots.values())),
                    column(list(p_plots.values())),
                    column(list(tables.values())))
    return layout

