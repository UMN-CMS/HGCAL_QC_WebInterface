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

tempIDR = pd.read_csv('./static/files/ID_Resistor_Test_Data.csv')
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
    td = {}
    std = {}
    for s in subtypes:
        hist[s] = {}
        for sn in serial_numbers[s]:
            hist[s][sn] = ColumnDataSource(data={'top':[], 'bottom':[], 'left':[], 'right':[]})

        td[s] = ColumnDataSource(data={'Full ID':[], 'Resistance':[], 'Outcome':[]})
        std[s] = ColumnDataSource(data={'Full ID':[], 'mean':[], 'std':[]})

    x = CustomJS(args=dict(col=columns, hist=hist, data=data, views=views, subtypes=subtypes, serial_numbers=serial_numbers, slider=slider, td=td, std=std),code='''
// iterate over subtypes
for (let s = 0; s < subtypes.length; s++) {
    // create arrays for table
    const full_ids = [];
    const res = [];
    const outcomes = [];
    const serials = [];
    const means = [];
    const stds = [];
    // iterate over serial numbers
    for (let sn = 0; sn < serial_numbers[subtypes[s]].length; sn++) {
        // create mask
        const indices = views[subtypes[s]].filters[0].compute_indices(data[subtypes[s]]);
        let mask = new Array(data[subtypes[s]].data[col].length).fill(false);
        [...indices].forEach((x)=>{mask[x] = true;})
        for (let j = 0; j < data[subtypes[s]].get_length(); j++) {
            if (data[subtypes[s]].data['Full ID'][j] == serial_numbers[subtypes[s]][sn] && mask[j] == true){
                mask[j] = true;
                full_ids.push(serial_numbers[subtypes[s]][sn])
                res.push(data[subtypes[s]].data[col][j])
                outcomes.push(data[subtypes[s]].data['Outcome'][j])
            } else {
                mask[j] = false;
            }
        }
        // bin data by subtype
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
        // fill data sources
        hist[subtypes[s]][serial_numbers[subtypes[s]][sn]].data['right'] = right;
        hist[subtypes[s]][serial_numbers[subtypes[s]][sn]].data['left'] = left;
        hist[subtypes[s]][serial_numbers[subtypes[s]][sn]].data['bottom'] = bottom;
        hist[subtypes[s]][serial_numbers[subtypes[s]][sn]].data['top'] = top;
        hist[subtypes[s]][serial_numbers[subtypes[s]][sn]].change.emit()
        serials.push(serial_numbers[subtypes[s]][sn])
        means.push(d3.mean(good_data))
        stds.push(d3.deviation(good_data))
    }
    td[subtypes[s]].data['Full ID'] = full_ids;
    td[subtypes[s]].data['Resistance'] = res;
    td[subtypes[s]].data['Outcome'] = outcomes;
    td[subtypes[s]].change.emit()
    std[subtypes[s]].data['Full ID'] = serials;
    std[subtypes[s]].data['mean'] = means;
    std[subtypes[s]].data['std'] = stds;
    std[subtypes[s]].change.emit()
}
    ''')
    for widget in widgets:
        widget.js_on_change('value', x)
    slider.js_on_change('value', x)
    return hist, td, std

def Filter():
    df_temp = AllData.merge(IDR, on='Test ID', how='left')
    df_temp = df_temp.dropna()
    ds = ColumnDataSource(df_temp)
    # create subtypes array and serial numbers dictionary
    # each subtype has its own data source
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

    custom_filter = CustomJSFilter(args=dict(mc_widgets=mc_widgets, dr_widgets=dr_widgets),code=filter_code)
    views = {}
    for s in subtypes:
        views[s] = CDSView(source=data_sources[s], filters=[custom_filter])
    slider = Slider(start=1, end=16, value=4, step=1, title='Granularity')
    all_widgets = {**mc_widgets, **dr_widgets}
    widgets = {k:w['widget'] for k,w in all_widgets.items()}

    hist, td, std = Histogram('Resistance', data_sources, views, widgets.values(), subtypes, serial_numbers, slider)
    # holds all the plot objects by subtype
    plots = {}
    tables = {}
    tables_2 = {}
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
                        TableColumn(field='Outcome', title='Outcome'),
                        ]
        data_table = DataTable(source=td[s], columns=table_columns, autosize_mode='fit_columns')
        data_table.visible = False
        tables[s] = data_table

        table_columns_2 = [
                        TableColumn(field='Full ID', title='Full ID'),
                        TableColumn(field='mean', title='Mean'),
                        TableColumn(field='std', title='Standard Deviation'),
                        ]
        data_table_2 = DataTable(source=std[s], columns=table_columns_2, autosize_mode='fit_columns')
        data_table_2.visible = False
        tables_2[s] = data_table_2
            
    w = [*widgets.values()]
    # creates a custom select widget that changes which plot to display
    display_plot = CustomJS(args=dict(plots=plots, tables=tables, tables_2=tables_2), code=('''
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
for (let [name,table] of Object.entries(tables_2)){
    if (name == this.value){
        table.visible = true
    } else {
        table.visible = false
    }
}
'''))
    
    select = Select(title='Type ID', options=subtypes)
    select.js_on_change('value', display_plot)

    # column and row objects only take it lists, need to make arguments lists
    layout = column(row(w[0:2] + [select]), row(w[2:5]), slider, column(list(plots.values())),  column(list(tables.values())), column(list(tables_2.values())))
    plot_json = json.dumps(json_item(layout))
    return plot_json

