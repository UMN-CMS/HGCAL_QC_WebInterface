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

# import the Bit Error rate data and split it into a midpoint and an eye opening dataframe
tempBE = pd.read_csv(mTD.get_bert())
MP = tempBE.drop('Eye Opening', axis=1)
MP = MP.dropna()
EO = tempBE.drop('Midpoint', axis=1)
EO = EO.dropna()

# custom javascript filter to control which data is displayed using the widgets
filter_code=('''
// get the selected multi_choice options and selected dates
const is_selected_map = new Map([
    ["multi_choice", (wi, pos, el, idx) => wi.value.includes(el)],
    ["date_range", (wi, pos, el, idx) => wi.value == el]
]);
// get true/false for each value
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
// function returns true if all values are false
function allfalse(value) {
    return value === false;
}
// set all passed vals to true if all are false
// makes it so if you have nothing selected then everything is displayed
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
// creates indices array that's the length of the data source
// determines true or false based on the column and passed val
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
// corrects indices based on selected date range
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

def Histogram(mp_data, eo_data, view, widgets, modules, slider):
    # creates a dictionary of data sources, need a data source for each plot element
    hist_data_mp = {}
    hist_data_eo = {}
    for i in modules:
        hist_data_mp[i] = {}
        hist_data_eo[i] = {}
        hist_data_mp[i]['red'] = ColumnDataSource(data={'top':[], 'bottom':[], 'left':[], 'right':[]})
        hist_data_mp[i]['green'] = ColumnDataSource(data={'top':[], 'bottom':[], 'left':[], 'right':[]})
        hist_data_eo[i]['red'] = ColumnDataSource(data={'top':[], 'bottom':[], 'left':[], 'right':[]})
        hist_data_eo[i]['green'] = ColumnDataSource(data={'top':[], 'bottom':[], 'left':[], 'right':[]})

    std = ColumnDataSource(data={'columns':[], 'Red Midpoint Mean':[], 'Red Midpoint std':[], 'Red std':[], 'Green Midpoint Mean':[], 'Green Midpoint std':[], 'Green std':[]})
    # custom javascript to be run to actually create the plotted data on the website
    # all done in javascript so it runs on the website and can update without refreshing the page
    x = CustomJS(args=dict(hist_mp=hist_data_mp, hist_eo=hist_data_eo, mp_data=mp_data, eo_data=eo_data, view=view, modules=modules, slider=slider, std=std),code='''
// make arrays for the data sources ahead of time to be appended to
const columns = [];
const std_ar_r = [];
const std_ar_g = [];
const means_r = [];
const means_g = [];
const std_2_r = [];
const std_2_g = [];
// iterate over all the E Links
for (let i = 0; i < modules.length; i++) {
    const indices = view.filters[0].compute_indices(mp_data);
    let mp_mask = new Array(mp_data.data['Midpoint'].length).fill(false);
    [...indices].forEach((x)=>{mp_mask[x] = true;})

    let mp_mask_r = new Array(mp_data.data['Midpoint'].length).fill(false);
    [...indices].forEach((x)=>{mp_mask_r[x] = true;})

    let mp_mask_g = new Array(mp_data.data['Midpoint'].length).fill(false);
    [...indices].forEach((x)=>{mp_mask_g[x] = true;})

    let eo_mask = new Array(mp_data.data['Midpoint'].length).fill(false);
    [...indices].forEach((x)=>{eo_mask[x] = true;})
    
    let eo_mask_r = new Array(mp_data.data['Midpoint'].length).fill(false);
    [...indices].forEach((x)=>{eo_mask_r[x] = true;})
    
    let eo_mask_g = new Array(mp_data.data['Midpoint'].length).fill(false);
    [...indices].forEach((x)=>{eo_mask_g[x] = true;})
    
    // modify mask for whether the E Link is correct
    for (let j = 0; j < mp_data.length; j++) {
        if (mp_data.data['E Link'][j] == modules[i] && mp_mask[j] == true){
            mp_mask[j] = true;
        } else {
            mp_mask[j] = false;
        }

        if (mp_data.data['E Link'][j] == modules[i] && mp_mask[j] == true && mp_data.data['Full ID'][j][12] == 0){
            mp_mask_r[j] = true;
        } else {
            mp_mask_r[j] = false;
        }

        if (mp_data.data['E Link'][j] == modules[i] && mp_mask[j] == true && mp_data.data['Full ID'][j][12] == 1){
            mp_mask_g[j] = true;
        } else {
            mp_mask_g[j] = false;
        }
    }
    for (let j = 0; j < eo_data.length; j++) {
        if (eo_data.data['E Link'][j] == modules[i] && eo_mask[j] == true){
            eo_mask[j] = true;
        } else {
            eo_mask[j] = false;
        }

        if (eo_data.data['E Link'][j] == modules[i] && eo_mask[j] == true && eo_data.data['Full ID'][j][12] == 0){
            eo_mask_r[j] = true;
        } else {
            eo_mask_r[j] = false;
        }

        if (eo_data.data['E Link'][j] == modules[i] && eo_mask[j] == true && eo_data.data['Full ID'][j][12] == 1){
            eo_mask_g[j] = true;
        } else {
            eo_mask_g[j] = false;
        }
    }

    const mp_all_data = mp_data.data['Midpoint'].filter((_,y)=>mp_mask[y])
    const eo_all_data = eo_data.data['Eye Opening'].filter((_,y)=>eo_mask[y])
    let mp_m = Math.max(...mp_all_data);
    let mp_min = Math.min(...mp_all_data);
    let eo_m = Math.max(...eo_all_data);
    let eo_min = Math.min(...eo_all_data);

    // apply filter to the correct column
    const mp_good_data_r = mp_data.data['Midpoint'].filter((_,y)=>mp_mask_r[y])
    const mp_good_data_g = mp_data.data['Midpoint'].filter((_,y)=>mp_mask_g[y])
    const eo_good_data_r = eo_data.data['Eye Opening'].filter((_,y)=>eo_mask_r[y])
    const eo_good_data_g = eo_data.data['Eye Opening'].filter((_,y)=>eo_mask_g[y])

    // slider adjusts the number of thresholds
    let bins = slider.value
    // configure the scale of the graph
    let mp_scale = d3.scaleLinear().domain([mp_min,mp_m]).nice()
    let eo_scale = d3.scaleLinear().domain([eo_min-2,eo_m+2]).nice()
    let n1 = (mp_m - mp_min)
    // .nice() makes it so that thresholds can only take on certain values
    let mp_binner = d3.bin().domain(mp_scale.domain()).thresholds(n1*bins*0.1)
    let eo_binner = d3.bin().domain(eo_scale.domain()).thresholds(4*bins)

    let count_mp_r = mp_mask_r.filter(Boolean).length
    let count_eo_r = eo_mask_r.filter(Boolean).length
    let count_mp_g = mp_mask_g.filter(Boolean).length
    let count_eo_g = eo_mask_g.filter(Boolean).length

    // bin data and fill the data sources
    let mp_d_r = mp_binner(mp_good_data_r)
    let eo_d_r = eo_binner(eo_good_data_r)
    let mp_right_r = mp_d_r.map(x=>x.x1)
    let mp_left_r = mp_d_r.map(x=>x.x0)
    let mp_bottom_r = new Array(mp_d_r.length).fill(0)
    let mp_top_r = mp_d_r.map(x=>x.length);
    let eo_right_r = eo_d_r.map(x=>x.x1)
    let eo_left_r = eo_d_r.map(x=>x.x0)
    let eo_bottom_r = new Array(eo_d_r.length).fill(0)
    let eo_top_r = eo_d_r.map(x=>x.length);

    let mp_d_g = mp_binner(mp_good_data_g)
    let eo_d_g = eo_binner(eo_good_data_g)
    let mp_right_g = mp_d_g.map(x=>x.x1)
    let mp_left_g = mp_d_g.map(x=>x.x0)
    let mp_bottom_g = new Array(mp_d_g.length).fill(0)
    let mp_top_g = mp_d_g.map(x=>x.length);
    let eo_right_g = eo_d_g.map(x=>x.x1)
    let eo_left_g = eo_d_g.map(x=>x.x0)
    let eo_bottom_g = new Array(eo_d_g.length).fill(0)
    let eo_top_g = eo_d_g.map(x=>x.length);

    for (let k = 0; k < mp_top_r.length; k++) {
        mp_top_r[k] = mp_top_r[k]/count_mp_r
    }
    for (let k = 0; k < eo_top_r.length; k++) {
        eo_top_r[k] = eo_top_r[k]/count_eo_r
    }
    for (let k = 0; k < mp_top_g.length; k++) {
        mp_top_g[k] = mp_top_g[k]/count_mp_g
    }
    for (let k = 0; k < eo_top_g.length; k++) {
        eo_top_g[k] = eo_top_g[k]/count_eo_g
    }

    hist_mp[modules[i]]['red'].data['right'] = mp_right_r;
    hist_mp[modules[i]]['red'].data['left'] = mp_left_r;
    hist_mp[modules[i]]['red'].data['bottom'] = mp_bottom_r;
    hist_mp[modules[i]]['red'].data['top'] = mp_top_r;
    hist_mp[modules[i]]['red'].change.emit()
    hist_eo[modules[i]]['red'].data['right'] = eo_right_r;
    hist_eo[modules[i]]['red'].data['left'] = eo_left_r;
    hist_eo[modules[i]]['red'].data['bottom'] = eo_bottom_r;
    hist_eo[modules[i]]['red'].data['top'] = eo_top_r;
    hist_eo[modules[i]]['red'].change.emit()

    hist_mp[modules[i]]['green'].data['right'] = mp_right_g;
    hist_mp[modules[i]]['green'].data['left'] = mp_left_g;
    hist_mp[modules[i]]['green'].data['bottom'] = mp_bottom_g;
    hist_mp[modules[i]]['green'].data['top'] = mp_top_g;
    hist_mp[modules[i]]['green'].change.emit()
    hist_eo[modules[i]]['green'].data['right'] = eo_right_g;
    hist_eo[modules[i]]['green'].data['left'] = eo_left_g;
    hist_eo[modules[i]]['green'].data['bottom'] = eo_bottom_g;
    hist_eo[modules[i]]['green'].data['top'] = eo_top_g;
    hist_eo[modules[i]]['green'].change.emit()
    // find the mean and standard deviation and push it to arrays
    // Eye Opening mean is always 200
    columns.push(modules[i])
    means_r.push(d3.mean(mp_good_data_r))
    std_2_r.push(d3.deviation(mp_good_data_r))
    std_ar_r.push(d3.deviation(eo_good_data_r))
    means_g.push(d3.mean(mp_good_data_g))
    std_2_g.push(d3.deviation(mp_good_data_g))
    std_ar_g.push(d3.deviation(eo_good_data_g))
}
// update data sources
// need .change.emit() for the changes to take effect
std.data['columns'] = columns;
std.data['Red Midpoint Mean'] = means_r;
std.data['Red Midpoint std'] = std_2_r;
std.data['Red std'] = std_ar_r;
std.data['Green Midpoint Mean'] = means_g;
std.data['Green Midpoint std'] = std_2_g;
std.data['Green std'] = std_ar_g;
std.change.emit()
    ''')
    for widget in widgets:
        widget.js_on_change('value', x)
    slider.js_on_change('value', x)
    return hist_data_mp, hist_data_eo, std

def Filter():
    # make ColumnDataSources from the Pandas Dataframes
    mp_temp = AllData.merge(MP, on='Test ID', how='left')
    mp_temp = mp_temp.dropna()
    ds_mp = ColumnDataSource(mp_temp)
    eo_temp = AllData.merge(EO, on='Test ID', how='left')
    eo_temp = eo_temp.dropna()
    ds_eo = ColumnDataSource(eo_temp)
    # make the widgets
    mc_widgets = {}
    dr_widgets = {}
    # lambda is the inputs they take in
    # MultiChoice and DatePicker are the widgets being created
    # this method is nice when creating a bunch of similar widgets at once
    multi_choice = (lambda x,y: MultiChoice(options=x, value=[], title=y), 'value')
    start_date = (lambda x,y,z: DatePicker(min_date=x,max_date=y, value='2023-03-14', title=z), 'value')
    today = datetime.date.today()
    end_date = (lambda x,y,z: DatePicker(min_date=x,max_date=y, value=today, title=z), 'value')
    min_date = pd.Timestamp((min(ds_mp.data['Time']))).date()
    date_range = []
    while min_date <= today:
        date_range.append(min_date)
        min_date += datetime.timedelta(days=1)
    # get the E Links
    modules = np.unique(ds_mp.data['E Link'].tolist()).tolist()

    # information for constructing widgets
    # column name has to be the name of the column in the data source that you're filtering with this widget
    columns = ['Type ID', 'Full ID', 'Outcome', 'Start Date', 'End Date']
    # values that you want to choose from in the widget
    data = [ds_mp.data['Type ID'].tolist(), ds_mp.data['Full ID'].tolist(), ds_mp.data['Outcome'], date_range, date_range]
    # type of widget
    t = [multi_choice, multi_choice, multi_choice, start_date, end_date]

    # create the widgets
    for i in range(len(columns)):
        # widget constructor is the lambda part
        # trigger is the part in quotes, what causes the widget to update
        # all these run their javascript when their value is changed
        widget_constructor, trigger = t[i]
        # multi choice and date picker widgets have to be configured slightly differently
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

    # applies the custom filter to the widgets and then to the data sources
    custom_filter = CustomJSFilter(args=dict(mc_widgets=mc_widgets, dr_widgets=dr_widgets),code=filter_code)
    view = CDSView(source=ds_mp, filters=[custom_filter])
    
    # creates the slider widget and combined the mc and dr widgets
    slider = Slider(start=1, end=18, value=4, step=1, title='Granularity')
    all_widgets = {**mc_widgets, **dr_widgets}
    widgets = {k:w['widget'] for k,w in all_widgets.items()}

    # calls the histogram to get the data sources used in plotting and tables
    mp_hist, eo_hist, std = Histogram(ds_mp, ds_eo, view, widgets.values(), modules, slider)

    mp_plots = {}
    eo_plots = {}
    for m in modules:
        # creates the figure objects
        p = figure(
            title='Midpoint for ' + m,
            x_axis_label='DAQ Delay',
            y_axis_label='Number of Boards',
            tools='pan,wheel_zoom,box_zoom,reset,save',
            width = 925
            )
        q = figure(
            title='Eye Opening for ' + m,
            x_axis_label='Eye Width',
            y_axis_label='Number of Boards',
            tools='pan,wheel_zoom,box_zoom,reset,save',
            width = 925
            )
        
        # adds glyphs to the figures
        # source determines what data source to use to make the plot
        # this allows the plot to update whenever the data source does
        p.quad(top='top', bottom='bottom', left='left', right='right', source=mp_hist[modules[i]]['red'], legend_label='Red Wagons', color = colors[3])
        p.quad(top='top', bottom='bottom', left='left', right='right', source=mp_hist[modules[i]]['green'], legend_label='Green Wagons', color = colors[2])

        q.quad(top='top', bottom='bottom', left='left', right='right', source=eo_hist[modules[i]]['red'], legend_label='Red Wagons', color = colors[3])
        q.quad(top='top', bottom='bottom', left='left', right='right', source=eo_hist[modules[i]]['green'], legend_label='Green Wagons', color = colors[2])
            
        p.legend.click_policy='hide'
        p.legend.label_text_font_size = '8pt'
        p.visible = False
        mp_plots[m] = p
        q.legend.click_policy='hide'
        q.legend.label_text_font_size = '8pt'
        q.visible = False
        eo_plots[m] = q

    # creates the data tables
    # they work the same way in terms of updating with the data source
    table_columns = [
                    TableColumn(field='columns', title='E Link'), 
                    TableColumn(field='Red Midpoint Mean', title='Red Midpoint Mean'),
                    TableColumn(field='Red Midpoint std', title='Red Midpoint Standard Deviation'),
                    TableColumn(field='Red std', title='Red Eye Width Standard Deviation'),
                    TableColumn(field='Green Midpoint Mean', title='Green Midpoint Mean'),
                    TableColumn(field='Green Midpoint std', title='Green Midpoint Standard Deviation'),
                    TableColumn(field='Green std', title='Green Eye Width Standard Deviation'),
                    ]
    table = DataTable(source=std, columns=table_columns, autosize_mode='fit_columns', width=1000)
    w = [*widgets.values()]
    
    # changes the options for the serial numbers widget based on the subtype selected
    subtypes = np.unique(ds_mp.data['Type ID'].tolist()).tolist()
    serial_numbers = {}
    for s in subtypes:
        serial_numbers[s] = np.unique(mp_temp.query('`Type ID` == @s')['Full ID'].values.tolist()).tolist()
    update_options = CustomJS(args=dict(serial_numbers=serial_numbers, widget=w[1]), code=('''
widget.options = serial_numbers[this.value]
'''))
    w[0].js_on_change('value', update_options)

    display_plot = CustomJS(args=dict(mp_plots=mp_plots, eo_plots=eo_plots), code=('''
for (let [name,plot] of Object.entries(mp_plots)){
    if (name == this.value){
        plot.visible = true
    } else {
        plot.visible = false
    }
}
for (let [name,plot] of Object.entries(eo_plots)){
    if (name == this.value){
        plot.visible = true
    } else {
        plot.visible = false
    }
}
'''))
    
    select = Select(title='E Link', options=modules)
    select.js_on_change('value', display_plot)
    # turns all the bokeh items into json and returns them
    plot_json = json.dumps(json_item(column(row(w[0:2] + [select]), row(w[2:]), slider, column(list(mp_plots.values())), column(list(eo_plots.values())), table)))
    return plot_json

