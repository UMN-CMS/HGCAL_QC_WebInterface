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

#import all data from csv files and set it up properly
TestData = pd.read_csv(mTD.get_test(), parse_dates=['Time'])
BoardData = pd.read_csv(mTD.get_board())
PeopleData = pd.read_csv(mTD.get_people())
mergetemp = TestData.merge(BoardData, on='Board ID', how='left')
AllData = mergetemp.merge(PeopleData, on='Person ID', how='left')
AllData = AllData.rename(columns={'Successful':'Outcome'})
AllData['Outcome'] = AllData['Outcome'].replace(0, 'Unsuccessful')
AllData['Outcome'] = AllData['Outcome'].replace(1, 'Successful')

tempRM = pd.read_csv(mTD.get_rm())
tempRM = tempRM.set_index('Test ID')
RM = tempRM.stack()
RM = RM.reset_index()
RM = RM.rename(columns={0:'Resistance'})
RM = RM.dropna()

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
def Histogram(columns, data, view, widgets, modules, slider):
    # creates a dictionary for the histogram data to go in
    hist_data = {}
    for i in modules:
        hist_data[i] = {}
        hist_data[i]['red'] = ColumnDataSource(data={'top':[], 'bottom':[], 'left':[], 'right':[]})
        hist_data[i]['green'] = ColumnDataSource(data={'top':[], 'bottom':[], 'left':[], 'right':[]})
    
    # creates a dictionary for the filtered data to be put in data tables
    std = ColumnDataSource(data={'pathway':[],'red std':[], 'red mean':[], 'green std':[], 'green mean':[]})
    # custom javascript to be run to actually create the plotted data client side
    # all done in javascript so it runs on the website and can update without refreshing the page
    x = CustomJS(args=dict(col=columns, hist=hist_data, data=data, view=view, modules=modules, slider=slider, std=std),code='''
// data arrays
const means_r=[];
const devs_r=[];
const means_g=[];
const devs_g=[];
const pathways=[];
// iterate over resistance measurement pathways
for (let i = 0; i < modules.length; i++) {
    const indices = view.filters[0].compute_indices(data);
    let mask = new Array(data.data[col].length).fill(false);
    [...indices].forEach((x)=>{mask[x] = true;})

    let mask_r = new Array(data.data[col].length).fill(false);
    [...indices].forEach((x)=>{mask_r[x] = true;})

    let mask_g = new Array(data.data[col].length).fill(false);
    [...indices].forEach((x)=>{mask_g[x] = true;})

    for (let j = 0; j < data.get_length(); j++) {
        if (data.data['level_1'][j] == modules[i] && mask[j] == true){
            mask[j] = true;
        } else {
            mask[j] = false;
        }

        if (data.data['level_1'][j] == modules[i] && mask_r[j] == true && data.data['Full ID'][j][12] == 0){
            mask_r[j] = true;
        } else {
            mask_r[j] = false;
        }

        if (data.data['level_1'][j] == modules[i] && mask_g[j] == true && data.data['Full ID'][j][12] == 1){
            mask_g[j] = true;
        } else {
            mask_g[j] = false;
        }
    }

    const all_data = data.data[col].filter((_,y)=>mask[y])
    let m = Math.max(...all_data);
    let min = Math.min(...all_data);

    // normalizes data to same scale
    let count_r = mask_r.filter(Boolean).length;
    let count_g = mask_g.filter(Boolean).length;

    // filter and bin data
    const good_data_r = data.data[col].filter((_,y)=>mask_r[y])
    const good_data_g = data.data[col].filter((_,y)=>mask_g[y])
    let bins = slider.value
    let scale = d3.scaleLinear().domain([min,m]).nice()
    let binner = d3.bin().domain(scale.domain()).thresholds(m*bins)

    let d_r = binner(good_data_r)
    let right_r = d_r.map(x=>x.x1)
    let left_r = d_r.map(x=>x.x0)
    let bottom_r = new Array(d_r.length).fill(0)
    let top_r = d_r.map(x=>x.length)
    for (let k = 0; k < top_r.length; k++) {
        top_r[k] = top_r[k]/count_r
    }
    hist[modules[i]]['red'].data['right'] = right_r;
    hist[modules[i]]['red'].data['left'] = left_r;
    hist[modules[i]]['red'].data['bottom'] = bottom_r;
    hist[modules[i]]['red'].data['top'] = top_r;
    hist[modules[i]]['red'].change.emit()

    let d_g = binner(good_data_g)
    let right_g = d_g.map(x=>x.x1)
    let left_g = d_g.map(x=>x.x0)
    let bottom_g = new Array(d_g.length).fill(0)
    let top_g = d_g.map(x=>x.length)
    for (let k = 0; k < top_g.length; k++) {
        top_g[k] = top_g[k]/count_g
    }
    hist[modules[i]]['green'].data['right'] = right_g;
    hist[modules[i]]['green'].data['left'] = left_g;
    hist[modules[i]]['green'].data['bottom'] = bottom_g;
    hist[modules[i]]['green'].data['top'] = top_g;
    hist[modules[i]]['green'].change.emit()

    means_r.push(d3.mean(good_data_r))
    means_g.push(d3.mean(good_data_g))
    devs_r.push(d3.deviation(good_data_r))
    devs_g.push(d3.deviation(good_data_g))
    pathways.push(modules[i])
}
std.data['red mean'] = means_r;
std.data['red std'] = devs_r;
std.data['green mean'] = means_g;
std.data['green std'] = devs_g;
std.data['pathway'] = pathways;
std.change.emit()
    ''')
    for widget in widgets:
        widget.js_on_change('value', x)
    slider.js_on_change('value', x)
    return hist_data, std

# creates the webpage and plots the data
def Filter():
    # create a CDS with all the data to be used
    df_temp = AllData.merge(RM, on='Test ID', how='left')
    df_temp = df_temp.dropna()
    ds = ColumnDataSource(df_temp)
    subtypes = np.unique(ds.data['Type ID'].tolist()).tolist()
    serial_numbers = {}
    for s in subtypes:
        serial_numbers[s] = np.unique(df_temp.query('`Type ID` == @s')['Full ID'].values.tolist()).tolist()

    # create the widgets to be used
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
    # widget titles and data for those widgets has to be manually entered, as well as the type
    columns = ['Type ID', 'Full ID', 'Outcome', 'Start Date', 'End Date']
    data = [ds.data['Type ID'].tolist(), ds.data['Full ID'].tolist(), ds.data['Outcome'], date_range, date_range]
    t = [multi_choice, multi_choice, multi_choice, start_date, end_date]
    
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
    slider = Slider(start=1, end=16, value=4, step=1, title='Granularity')
    all_widgets = {**mc_widgets, **dr_widgets}
    widgets = {k:w['widget'] for k,w in all_widgets.items()}
    # calls the function that creates the plotting data
    hds, std = Histogram('Resistance', ds, view, widgets.values(), modules, slider)
    plots = {}
    for m in modules:

        # creates the figure object
        p = figure(
            title='Resistance Measurement for ' + m,
            x_axis_label='Resistance',
            y_axis_label='Number of Boards',
            tools='pan,wheel_zoom,box_zoom,reset,save',
            width = 925
            )

        # tells the figure object what data source to use
        p.quad(top='top', bottom='bottom', left='left', right='right', source=hds[m]['red'], color = colors[3], legend_label = 'Red Wagons')
        p.quad(top='top', bottom='bottom', left='left', right='right', source=hds[m]['green'], color = colors[2], legend_label = 'Green Wagons')
        p.visible = False
        p.legend.click_policy='hide'
        p.legend.label_text_font_size = '8pt'
        plots[m] = p

    # creates data tables
    table_columns = [
                    TableColumn(field='pathway', title='Pathway'),
                    TableColumn(field='red mean', title='Red Mean'),
                    TableColumn(field='red std', title='Red Standard Deviation'),
                    TableColumn(field='green mean', title='Green Mean'),
                    TableColumn(field='green std', title='Green Standard Deviation'),
                    ]
    data_table = DataTable(source=std, columns=table_columns, autosize_mode='fit_columns', width=1000)
    w = [*widgets.values()]
    
    update_options = CustomJS(args=dict(serial_numbers=serial_numbers, widget=w[1]), code=('''
widget.options = serial_numbers[this.value]
'''))
    w[0].js_on_change('value', update_options)

    display_plot = CustomJS(args=dict(plots=plots), code=('''
for (let [name,plot] of Object.entries(plots)){
    if (name == this.value){
        plot.visible = true
    } else {
        plot.visible = false
    }
}
'''))
    
    select = Select(title='Pathway', options=modules)
    select.js_on_change('value', display_plot)
    #converts the bokeh items to json and sends them to the webpage
    plot_json = json.dumps(json_item(column(row(w[0:2] + [select]), row(w[2:]), slider, column(list(plots.values())), data_table)))
    return plot_json

