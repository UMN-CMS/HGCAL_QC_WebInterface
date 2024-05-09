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
    Text,
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

temp = pd.read_csv('./static/files/ADC_functionality_resistance.csv')
ADC_resist = temp.dropna()
temp = pd.read_csv('./static/files/ADC_functionality_voltage.csv')
ADC_voltage = temp.dropna()
temp = pd.read_csv('./static/files/ADC_functionality_temp.csv')
ADC_temp = temp.dropna()
temp = pd.read_csv('./static/files/ADC_main.csv')
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

colors = [d3['Category10'][10][0], d3['Category10'][10][1], d3['Category10'][10][2], d3['Category10'][10][3], d3['Category10'][10][4], d3['Category10'][10][5], d3['Category10'][10][6], d3['Category10'][10][7], d3['Category10'][10][8], d3['Category10'][10][9], brewer['Accent'][8][0], brewer['Accent'][8][3], brewer['Dark2'][8][0], brewer['Dark2'][8][2], brewer['Dark2'][8][3], brewer['Dark2'][8][4], brewer['Dark2'][8][5], brewer['Dark2'][8][6], d3['Category20'][20][1], d3['Category20'][20][9], d3['Category20c'][20][19]]


def ADC_Histograms(data_resist, data_volt, data_temp, view, widgets, serial_numbers, resist_modules, volt_modules, temp_modules, slider):
    hist = {}
    td = {}
    std = {}
    for s in serial_numbers:
        td[s] = {}
        hist[s] = {}
        hist[s]['resist'] = {}
        hist[s]['volt'] = {}
        hist[s]['temp'] = {}
        for r in resist_modules[s]:
            hist[s]['resist'][r] = ColumnDataSource(data={'top':[], 'bottom':[], 'left':[], 'right':[]})
        for v in volt_modules[s]:
            hist[s]['volt'][v] = ColumnDataSource(data={'top':[], 'bottom':[], 'left':[], 'right':[]})
        for t in temp_modules[s]:
            hist[s]['temp'][t] = ColumnDataSource(data={'top':[], 'bottom':[], 'left':[], 'right':[]})

        td[s]['resist'] = ColumnDataSource(data={'E Link':[], 'Resistance':[], 'Outcome':[]})
        td[s]['volt'] = ColumnDataSource(data={'ADC':[], 'Voltage':[], 'Outcome':[]})
        td[s]['temp'] = ColumnDataSource(data={'Location':[], 'Temperature':[], 'Outcome':[]})
        std[s] = ColumnDataSource(data={'Quantity':[], 'mean':[], 'std':[]})
    x = CustomJS(args=dict(hist=hist, data_resist=data_resist, data_volt=data_volt, data_temp=data_temp, serial_numbers=serial_numbers, resist_modules=resist_modules, volt_modules=volt_modules, temp_modules=temp_modules, view=view, slider=slider, td=td, std=std),code='''
for (let i = 0; i < serial_numbers.length; i++) {
    const e_links=[];
    const adcs=[];
    const locations=[];
    const resist=[];
    const volt=[];
    const temp=[];
    const r_outcomes = [];
    const v_outcomes = [];
    const t_outcomes = [];
    const quantities = [];
    const means = [];
    const stds = [];
    let bins = slider.value
    const indices_resist = view['resistance'][serial_numbers[i]].filters[0].compute_indices(data_resist[serial_numbers[i]]);
    const indices_volt = view['voltage'][serial_numbers[i]].filters[0].compute_indices(data_volt[serial_numbers[i]]);
    const indices_temp = view['temperature'][serial_numbers[i]].filters[0].compute_indices(data_temp[serial_numbers[i]]);

    for (let k = 0; k < resist_modules[serial_numbers[i]].length; k++) {
        let mask_resist = new Array(data_resist[serial_numbers[i]].data['Resistance'].length).fill(false);
        [...indices_resist].forEach((x)=>{mask_resist[x] = true;})

        for (let j = 0; j < data_resist[serial_numbers[i]].data['E Link'].length; j++) {
            if (mask_resist[j] == true && data_resist[serial_numbers[i]].data['E Link'][j] == resist_modules[serial_numbers[i]][k]) {
                mask_resist[j] = true;
                e_links.push(data_resist[serial_numbers[i]].data['E Link'][j])
                resist.push(data_resist[serial_numbers[i]].data['Resistance'][j])
                r_outcomes.push(data_resist[serial_numbers[i]].data['Outcome'][j])
            } else {
                mask_resist[j] = false;
            }
        }

        const good_data = data_resist[serial_numbers[i]].data['Resistance'].filter((_,y)=>mask_resist[y])
        let m = Math.max(...good_data);
        let min = Math.min(...good_data);
        let scale = d3.scaleLinear().domain([min,m]).nice()
        let binner = d3.bin().domain(scale.domain()).thresholds(m*bins)
        let d = binner(good_data)

        quantities.push('Resistance')
        means.push(d3.mean(good_data))
        stds.push(d3.deviation(good_data))

        let right = d.map(x=>x.x1)
        let left = d.map(x=>x.x0)
        let bottom = new Array(d.length).fill(0)
        let top = d.map(x=>x.length);

        hist[serial_numbers[i]]['resist'][resist_modules[serial_numbers[i]][k]].data['right'] = right;
        hist[serial_numbers[i]]['resist'][resist_modules[serial_numbers[i]][k]].data['left'] = left;
        hist[serial_numbers[i]]['resist'][resist_modules[serial_numbers[i]][k]].data['top'] = top;
        hist[serial_numbers[i]]['resist'][resist_modules[serial_numbers[i]][k]].data['bottom'] = bottom;
        hist[serial_numbers[i]]['resist'][resist_modules[serial_numbers[i]][k]].change.emit()

    }

    td[serial_numbers[i]]['resist'].data['E Link'] = e_links;
    td[serial_numbers[i]]['resist'].data['Resistance'] = resist;
    td[serial_numbers[i]]['resist'].data['Outcome'] = r_outcomes;
    td[serial_numbers[i]]['resist'].change.emit()

    for (let k = 0; k < volt_modules[serial_numbers[i]].length; k++) {
        let mask_volt = new Array(data_volt[serial_numbers[i]].data['Voltage'].length).fill(false);
        [...indices_volt].forEach((x)=>{mask_volt[x] = true;})

        for (let j = 0; j < data_volt[serial_numbers[i]].data['ADC'].length; j++) {
            if (mask_volt[j] == true && data_volt[serial_numbers[i]].data['ADC'][j] == volt_modules[serial_numbers[i]][k]) {
                mask_volt[j] = true;
                adcs.push(data_volt[serial_numbers[i]].data['ADC'][j])
                volt.push(data_volt[serial_numbers[i]].data['Voltage'][j])
                v_outcomes.push(data_volt[serial_numbers[i]].data['Outcome'][j])
            } else {
                mask_volt[j] = false;
            }
        }

        const good_data = data_volt[serial_numbers[i]].data['Voltage'].filter((_,y)=>mask_volt[y])
        let m = Math.max(...good_data);
        let min = Math.min(...good_data);
        let scale = d3.scaleLinear().domain([min,m]).nice()
        let binner = d3.bin().domain(scale.domain()).thresholds(m*bins*2)
        let d = binner(good_data)

        quantities.push('Voltage')
        means.push(d3.mean(good_data))
        stds.push(d3.deviation(good_data))

        let right = d.map(x=>x.x1)
        let left = d.map(x=>x.x0)
        let bottom = new Array(d.length).fill(0)
        let top = d.map(x=>x.length);

        hist[serial_numbers[i]]['volt'][volt_modules[serial_numbers[i]][k]].data['right'] = right;
        hist[serial_numbers[i]]['volt'][volt_modules[serial_numbers[i]][k]].data['left'] = left;
        hist[serial_numbers[i]]['volt'][volt_modules[serial_numbers[i]][k]].data['top'] = top;
        hist[serial_numbers[i]]['volt'][volt_modules[serial_numbers[i]][k]].data['bottom'] = bottom;
        hist[serial_numbers[i]]['volt'][volt_modules[serial_numbers[i]][k]].change.emit()

    }

    td[serial_numbers[i]]['volt'].data['ADC'] = adcs;
    td[serial_numbers[i]]['volt'].data['Voltage'] = volt;
    td[serial_numbers[i]]['volt'].data['Outcome'] = v_outcomes;
    td[serial_numbers[i]]['volt'].change.emit()

    for (let k = 0; k < temp_modules[serial_numbers[i]].length; k++) {
        let mask_temp = new Array(data_temp[serial_numbers[i]].data['Temperature'].length).fill(false);
        [...indices_temp].forEach((x)=>{mask_temp[x] = true;})

        for (let j = 0; j < data_temp[serial_numbers[i]].get_length(); j++) {
            if (mask_temp[j] == true && data_temp[serial_numbers[i]].data['Location'][j] == temp_modules[serial_numbers[i]][k]) {
                mask_temp[j] = true;
                locations.push(data_temp[serial_numbers[i]].data['Location'][j])
                temp.push(data_temp[serial_numbers[i]].data['Temperature'][j])
                t_outcomes.push(data_temp[serial_numbers[i]].data['Outcome'][j])
            } else {
                mask_temp[j] = false;
            }
        }

        const good_data = data_temp[serial_numbers[i]].data['Temperature'].filter((_,y)=>mask_temp[y])
        let m = Math.max(...good_data);
        let min = Math.min(...good_data);
        let scale = d3.scaleLinear().domain([min,m]).nice()
        let binner = d3.bin().domain(scale.domain()).thresholds(m*bins)
        let d = binner(good_data)

        quantities.push('Temperature')
        means.push(d3.mean(good_data))
        stds.push(d3.deviation(good_data))

        let right = d.map(x=>x.x1)
        let left = d.map(x=>x.x0)
        let bottom = new Array(d.length).fill(0)
        let top = d.map(x=>x.length);

        hist[serial_numbers[i]]['temp'][temp_modules[serial_numbers[i]][k]].data['right'] = right;
        hist[serial_numbers[i]]['temp'][temp_modules[serial_numbers[i]][k]].data['left'] = left;
        hist[serial_numbers[i]]['temp'][temp_modules[serial_numbers[i]][k]].data['top'] = top;
        hist[serial_numbers[i]]['temp'][temp_modules[serial_numbers[i]][k]].data['bottom'] = bottom;
        hist[serial_numbers[i]]['temp'][temp_modules[serial_numbers[i]][k]].change.emit()

    }

    td[serial_numbers[i]]['temp'].data['Location'] = locations;
    td[serial_numbers[i]]['temp'].data['Temperature'] = temp;
    td[serial_numbers[i]]['temp'].data['Outcome'] = v_outcomes;
    td[serial_numbers[i]]['temp'].change.emit()

    std[serial_numbers[i]].data['Quantity'] = quantities;
    std[serial_numbers[i]].data['mean'] = means;
    std[serial_numbers[i]].data['std'] = stds;
    std[serial_numbers[i]].change.emit()
}
    ''')
    for widget in widgets:
        widget.js_on_change('value', x)
    slider.js_on_change('value', x)
    return hist, td, std

def ADC_Filter():
    ds_resists = {}
    ds_volts = {}
    ds_temps = {}

    df_temp = AllData.merge(ADC_voltage, on='Test ID', how='left')
    df_temp = df_temp.dropna()
    ds = ColumnDataSource(df_temp)

    serial_numbers = np.unique(ds.data['Full ID'].tolist()).tolist()
    df_temp = AllData.merge(ADC_resist, on='Test ID', how='left')
    df_temp = df_temp.dropna()
    for s in serial_numbers:
        ds_resists[s] = ColumnDataSource(df_temp.query('`Full ID` == @s'))

    df_temp = AllData.merge(ADC_voltage, on='Test ID', how='left')
    df_temp = df_temp.dropna()
    for s in serial_numbers:
        ds_volts[s] = ColumnDataSource(df_temp.query('`Full ID` == @s'))

    df_temp = AllData.merge(ADC_temp, on='Test ID', how='left')
    df_temp = df_temp.dropna()
    for s in serial_numbers:
        ds_temps[s] = ColumnDataSource(df_temp.query('`Full ID` == @s'))
        
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
            widget.js_on_change(trigger, CustomJS(args=dict(src1=ds_resists, src2=ds_volts, src3=ds_temps, sns=serial_numbers), code='''
for (let i = 0; i < sns.length; i++) {
    src1[sns[i]].change.emit()
    src2[sns[i]].change.emit()
    src3[sns[i]].change.emit()
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
            widget.js_on_change(trigger, CustomJS(args=dict(src1=ds_resists, src2=ds_volts, src3=ds_temps, sns=serial_numbers), code='''
for (let i = 0; i < sns.length; i++) {
    src1[sns[i]].change.emit()
    src2[sns[i]].change.emit()
    src3[sns[i]].change.emit()
}
'''))
            dr_widgets[columns[i]] = {
                'type': typ,
                'possible_vals': possible_vals,
                'widget': widget,}

    custom_filter = CustomJSFilter(args=dict(mc_widgets=mc_widgets, dr_widgets=dr_widgets),code=filter_code)
    views = {}
    views['resistance'] = {}
    views['voltage'] = {}
    views['temperature'] = {}
    for s in serial_numbers:
        views['resistance'][s] = CDSView(source=ds_resists[s], filters=[custom_filter])
        views['voltage'][s] = CDSView(source=ds_volts[s], filters=[custom_filter])
        views['temperature'][s] = CDSView(source=ds_temps[s], filters=[custom_filter])
    slider = Slider(start=1, end=25, value=4, step=1, title='Granularity')
    all_widgets = {**mc_widgets, **dr_widgets}
    widgets = {k:w['widget'] for k,w in all_widgets.items()}

    resist_modules = {}
    volt_modules = {}
    temp_modules = {}
    for s in serial_numbers:
        resist_modules[s] = np.unique(ds_resists[s].data['E Link']).tolist()
        volt_modules[s] = np.unique(ds_volts[s].data['ADC']).tolist()
        temp_modules[s] = np.unique(ds_temps[s].data['Location']).tolist()

    hist, td, std = ADC_Histograms(ds_resists, ds_volts, ds_temps, views, widgets.values(), serial_numbers, resist_modules, volt_modules, temp_modules, slider)
    plots = {}
    plots['resist'] = {}
    plots['volt'] = {}
    plots['temp'] = {}
    tables = {}
    tables['resist'] = {}
    tables['volt'] = {}
    tables['temp'] = {}
    tables_2 = {}
    for s in serial_numbers:
        p_1 = figure(
            title='ADC Resistances for ' + s,
            x_axis_label='Resistance',
            y_axis_label='Number of Boards',
            tools='pan,wheel_zoom,box_zoom,reset,save',
            width = 925
            )

        p_2 = figure(
            title='ADC Voltages for ' + s,
            x_axis_label='Voltage',
            y_axis_label='Number of Boards',
            tools='pan,wheel_zoom,box_zoom,reset,save',
            width = 925
            )

        p_3 = figure(
            title='ADC Temperatures for ' + s,
            x_axis_label='Temperature',
            y_axis_label='Number of Boards',
            tools='pan,wheel_zoom,box_zoom,reset,save',
            width = 925
            )
        for n in range(len(resist_modules[s])): 
            p_1.quad(top='top', bottom='bottom', left='left', right='right', source=hist[s]['resist'][resist_modules[s][n]], legend_label=resist_modules[s][n], color = colors[n])
            p_1.visible = False
            p_1.legend.click_policy='hide'
            p_1.legend.label_text_font_size = '8pt' 
        for n in range(len(volt_modules[s])): 
            p_2.quad(top='top', bottom='bottom', left='left', right='right', source=hist[s]['volt'][volt_modules[s][n]], legend_label=volt_modules[s][n], color = colors[n])
            p_2.visible = False
            p_2.legend.click_policy='hide'
            p_2.legend.label_text_font_size = '8pt' 
        for n in range(len(temp_modules[s])): 
            p_3.quad(top='top', bottom='bottom', left='left', right='right', source=hist[s]['temp'][temp_modules[s][n]], legend_label=temp_modules[s][n], color = colors[n])
            p_3.visible = False
            p_3.legend.click_policy='hide'
            p_3.legend.label_text_font_size = '8pt' 
        plots['resist'][s] = p_1
        plots['volt'][s] = p_2
        plots['temp'][s] = p_3
        table_columns_resist = [
                        TableColumn(field='E Link', title='E link'),
                        TableColumn(field='Resistance', title='Resistance'),
                        TableColumn(field='Outcome', title='Outcome'),
                        ]
        data_table_1 = DataTable(source=td[s]['resist'], columns=table_columns_resist, autosize_mode='fit_columns')
        data_table_1.visible = False
        tables['resist'][s] = data_table_1

        table_columns_volt = [
                        TableColumn(field='ADC', title='ADC'),
                        TableColumn(field='Voltage', title='Voltage'),
                        TableColumn(field='Outcome', title='Outcome'),
                        ]
        data_table_2 = DataTable(source=td[s]['volt'], columns=table_columns_volt, autosize_mode='fit_columns')
        data_table_2.visible = False
        tables['volt'][s] = data_table_2

        table_columns_temp = [
                        TableColumn(field='Location', title='Location'),
                        TableColumn(field='Temperature', title='Temperature'),
                        TableColumn(field='Outcome', title='Outcome'),
                        ]
        data_table_3 = DataTable(source=td[s]['temp'], columns=table_columns_temp, autosize_mode='fit_columns')
        data_table_3.visible = False
        tables['temp'][s] = data_table_3

        table_columns_4 = [
                        TableColumn(field='Quantity', title='Quantity'),
                        TableColumn(field='mean', title='Mean'),
                        TableColumn(field='std', title='Standard Deviation'),
                        ]
        data_table_4 = DataTable(source=std[s], columns=table_columns_4, autosize_mode='fit_columns')
        data_table_4.visible = False
        tables_2[s] = data_table_4
            
    w = [*widgets.values()]
    # creates a custom select widget that changes which plot to display
    display_plot = CustomJS(args=dict(plots=plots, tables=tables, tables_2=tables_2), code=('''
for (let [name,plot] of Object.entries(plots['resist'])){
    if (name == this.value){
        plot.visible = true
    } else {
        plot.visible = false
    }
}
for (let [name,plot] of Object.entries(plots['volt'])){
    if (name == this.value){
        plot.visible = true
    } else {
        plot.visible = false
    }
}
for (let [name,plot] of Object.entries(plots['temp'])){
    if (name == this.value){
        plot.visible = true
    } else {
        plot.visible = false
    }
}
for (let [name,table] of Object.entries(tables['resist'])){
    if (name == this.value){
        table.visible = true
    } else {
        table.visible = false
    }
}
for (let [name,table] of Object.entries(tables['volt'])){
    if (name == this.value){
        table.visible = true
    } else {
        table.visible = false
    }
}
for (let [name,table] of Object.entries(tables['temp'])){
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
    
    select = Select(title='Full ID', options=serial_numbers)
    select.js_on_change('value', display_plot)

    layout = column(row(w[0:2] + [select]),
                    row(w[2:5]), 
                    slider, 
                    column(list(plots['resist'].values())), 
                    column(list(plots['volt'].values())), 
                    column(list(plots['temp'].values())), 
                    column(list(tables['resist'].values())), 
                    column(list(tables['volt'].values())), 
                    column(list(tables['temp'].values())), 
                    column(list(tables_2.values())))
    plot_json = json.dumps(json_item(layout))
    return plot_json

