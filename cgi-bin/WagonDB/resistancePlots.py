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
        end_date = new Date(end_date.setDate(end_date.getDate() + 1));
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
        hist_data[i] = ColumnDataSource(data={'top':[], 'bottom':[], 'left':[], 'right':[]})
    
    # creates a dictionary for the filtered data to be put in data tables
    dt = ColumnDataSource(data={'Sub Type':[], 'Full ID':[], 'Person Name':[], 'Time':[], 'Outcome':[], 'level_1':[], 'Resistance':[]})
    std = ColumnDataSource(data={'pathway':[],'std':[], 'mean':[]})
    # custom javascript to be run to actually create the plotted data client side
    # all done in javascript so it runs on the website and can update without refreshing the page
    x = CustomJS(args=dict(col=columns, hist=hist_data, data=data, view=view, modules=modules, slider=slider, dt=dt, std=std),code='''
// data arrays
const type_ids=[];
const full_ids=[];
const people=[];
const times=[];
const outcomes=[];
const pathways=[];
const res=[];
const means=[];
const devs=[];
const pathways_2=[];
// iterate over resistance measurement pathways
for (let i = 0; i < modules.length; i++) {
    const indices = view.filters[0].compute_indices(data);
    let mask = new Array(data.data[col].length).fill(false);
    [...indices].forEach((x)=>{mask[x] = true;})

    const all_data = data.data[col].filter((_,y)=>mask[y])
    let m = Math.max(...all_data);

    for (let j = 0; j < data.get_length(); j++) {
        if (data.data['level_1'][j] == modules[i] && mask[j] == true){
            mask[j] = true;
            type_ids.push(data.data['Sub Type'][j])
            full_ids.push(data.data['Full ID'][j])
            people.push(data.data['Person Name'][j])
            times.push(data.data['Time'][j])
            outcomes.push(data.data['Outcome'][j])
            pathways.push(data.data['level_1'][j])
            res.push(data.data[col][j])
        } else {
            mask[j] = false;
        }
    }
    // filter and bin data
    const good_data = data.data[col].filter((_,y)=>mask[y])
    let bins = slider.value
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
    means.push(d3.mean(good_data))
    devs.push(d3.deviation(good_data))
    pathways_2.push(modules[i])
}
dt.data['Sub Type'] = type_ids;
dt.data['Full ID'] = full_ids;
dt.data['Person Name'] = people;
dt.data['Time'] = times;
dt.data['Outcome'] = outcomes;
dt.data['level_1'] = pathways;
dt.data['Resistance'] = res;
dt.change.emit()
std.data['mean'] = means;
std.data['std'] = devs;
std.data['pathway'] = pathways_2;
std.change.emit()
    ''')
    for widget in widgets:
        widget.js_on_change('value', x)
    slider.js_on_change('value', x)
    return hist_data, dt, std

# creates the webpage and plots the data
def Filter():
    # create a CDS with all the data to be used
    df_temp = AllData.merge(RM, on='Test ID', how='left')
    df_temp = df_temp.dropna()
    ds = ColumnDataSource(df_temp)
    subtypes = {}
    for major in np.unique(ds.data['Major Type'].tolist()).tolist():
        subtypes[major] = np.unique(df_temp.query('`Major Type` == @major')['Sub Type'].values.tolist()).tolist()
    serial_numbers = {}
    for s in np.unique(ds.data['Sub Type'].tolist()).tolist():
        serial_numbers[s] = np.unique(df_temp.query('`Sub Type` == @s')['Full ID'].values.tolist()).tolist()

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
    columns = ['Major Type', 'Sub Type', 'Full ID', 'Person Name', 'Outcome', 'Start Date', 'End Date']
    data = [ds.data['Major Type'].tolist(), ds.data['Sub Type'].tolist(), ds.data['Full ID'].tolist(), ds.data['Person Name'].tolist(), ds.data['Outcome'], date_range, date_range]
    t = [multi_choice, multi_choice, multi_choice, multi_choice, multi_choice, start_date, end_date]
    
    # creates the figure object
    p = figure(
        title='Resistance Measurement',
        x_axis_label='Resistance',
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
    slider = Slider(start=1, end=16, value=4, step=1, title='Granularity')
    all_widgets = {**mc_widgets, **dr_widgets}
    widgets = {k:w['widget'] for k,w in all_widgets.items()}
    # calls the function that creates the plotting data
    hds, dt, std = Histogram('Resistance', ds, view, widgets.values(), modules, slider)
    # tells the figure object what data source to use
    for i in range(len(modules)):
        p.quad(top='top', bottom='bottom', left='left', right='right', source=hds[modules[i]], legend_label=modules[i], color = colors[i])

    # creates data tables
    table_columns = [
                    TableColumn(field='Sub Type', title='Sub Type'),
                    TableColumn(field='Full ID', title='Full ID'),
                    TableColumn(field='Person Name', title='Person Name'),
                    TableColumn(field='Time', title='Date', formatter=DateFormatter()),
                    TableColumn(field='Outcome', title='Outcome'),
                    TableColumn(field='level_1', title='Pathway'),
                    TableColumn(field='Resistance', title='Resistance'),
                    ]
    data_table = DataTable(source=dt, columns=table_columns, width=925, autosize_mode='fit_columns')
    table_columns_2 = [
                    TableColumn(field='pathway', title='Pathway'),
                    TableColumn(field='mean', title='Mean'),
                    TableColumn(field='std', title='Standard Deviation'),
                    ]
    data_table_2 = DataTable(source=std, columns=table_columns_2, autosize_mode='fit_columns')
    p.legend.click_policy='hide'
    p.legend.label_text_font_size = '8pt'
    w = [*widgets.values()]
    
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
    layout = Gaussian()
    #converts the bokeh items to json and sends them to the webpage
    plot_json = json.dumps(json_item(row(column(row(w[0:3]), row(w[3:5]), row(w[5:]), slider, p, data_table, data_table_2), layout)))
    return plot_json

################################################################################################################

def Gaussian2(data, view, widgets, subtypes, serial_numbers, modules, n_sigma):
    hist = {}
    pf = {}
    td = {}
    # residual data is split up by subtype since different subtypes have different modules
    for s in subtypes:
        hist[s] = ColumnDataSource(data={'top':[], 'bottom':[], 'left':[], 'right':[]})
        pf[s] = ColumnDataSource(data={'pass':[], 'fail':[], 'x':['Fail', 'Pass']})
        td[s] = ColumnDataSource(data={'Serial Number':[], 'Module':[], 'Deviation':[], 'Pass/Fail':[]})
    x = CustomJS(args=dict(hist=hist, data=data, views=view, subtypes=subtypes, serial_numbers=serial_numbers, modules=modules, n_sigma=n_sigma, pf=pf, td=td),code='''
// iterate over subtypes
for (let s = 0; s < subtypes.length; s++) {
    const residules = [];

    // create dictionary for whether each module passes/fails for each sn
    var chis = {};
    for (let sn = 0; sn < serial_numbers[subtypes[s]].length; sn++) {
        chis[serial_numbers[subtypes[s]][sn]] = [];
    } 
    for (let k = 0; k < modules[subtypes[s]].length; k++) {
        const indices = views[subtypes[s]].filters[0].compute_indices(data[subtypes[s]]);
        let mask = new Array(data[subtypes[s]].data['Resistance'].length).fill(false);
        [...indices].forEach((x)=>{mask[x] = true;})

        // modify mask
        for (let j = 0; j < data[subtypes[s]].get_length(); j++) {
            if (mask[j] == true && data[subtypes[s]].data['level_1'][j] == modules[subtypes[s]][k]){
                mask[j] = true;
            } else {
                mask[j] = false;
            }
        }
        // filter data and calculate mean and standard deviation
        const good_data = data[subtypes[s]].data['Resistance'].filter((_,y)=>mask[y])
        let mean = d3.mean(good_data)
        let std = d3.deviation(good_data)
        // iterate over serial numbers
        for (let sn = 0; sn < serial_numbers[subtypes[s]].length; sn++) {
            // remake mask, prevents bug where everything is false
            const indices = views[subtypes[s]].filters[0].compute_indices(data[subtypes[s]]);
            let mask_sn = new Array(data[subtypes[s]].data['Resistance'].length).fill(false);
            [...indices].forEach((x)=>{mask_sn[x] = true;})
            for (let j = 0; j < data[subtypes[s]].get_length(); j++) {
                if (mask_sn[j] == true && data[subtypes[s]].data['level_1'][j] == modules[subtypes[s]][k] && data[subtypes[s]].data['Full ID'][j] == serial_numbers[subtypes[s]][sn]){
                    mask_sn[j] = true;
                    let x = data[subtypes[s]].data['Resistance'][j] - mean;
                    let chi = x/std;
                    residules.push(chi)
                } else {
                    mask_sn[j] = false;
                }
            }
            // find the average of all the tests done on this board
            // this average is what determines whether the board passes or not
            // this is nice for when a board has multiple of the same tests done on it
            const good_data_sn = data[subtypes[s]].data['Resistance'].filter((_,y)=>mask_sn[y])
            let mean_sn = d3.mean(good_data_sn)
            let y = mean_sn - mean;
            let chi_sn = y/std;
            chis[serial_numbers[subtypes[s]][sn]].push(Math.abs(chi_sn))
        }
    }

    let binner = d3.bin()
    let d = binner(residules)
    let right = d.map(x=>x.x1)
    let left = d.map(x=>x.x0)
    let bottom = new Array(d.length).fill(0)
    let top = d.map(x=>x.length);
    
    hist[subtypes[s]].data['right'] = right;
    hist[subtypes[s]].data['left'] = left;
    hist[subtypes[s]].data['bottom'] = bottom;
    hist[subtypes[s]].data['top'] = top;
    hist[subtypes[s]].change.emit()

    let t_pass = 0;
    let t_fail = 0;
    const sn_td = [];
    const mod_td = [];
    const chi_td = [];
    const pf_td = [];
    // determine which boards pass and fail
    for (let sn = 0; sn < serial_numbers[subtypes[s]].length; sn++) {
        let pass = 0;
        let fail = 0;
        for (let c = 0; c < chis[serial_numbers[subtypes[s]][sn]].length; c++) {
            let chi_i = chis[serial_numbers[subtypes[s]][sn]][c]
            if (chi_i <= n_sigma.value) {
                pass = pass + 1;
                pf_td.push('PASS')
            } else {
                fail = fail + 1;
                pf_td.push('FAIL')
            }
            sn_td.push(serial_numbers[subtypes[s]][sn])
            mod_td.push(modules[subtypes[s]][c])
            chi_td.push(chi_i)
        }
        if (fail == 0) {
            t_pass = t_pass + 1;
        } else {
            t_fail = t_fail + 1;
        }
    }
    pf[subtypes[s]].data['pass'] = [0, t_pass];
    pf[subtypes[s]].data['fail'] = [t_fail, 0];
    pf[subtypes[s]].change.emit()

    td[subtypes[s]].data['Serial Number'] = sn_td;
    td[subtypes[s]].data['Module'] = mod_td;
    td[subtypes[s]].data['Deviation'] = chi_td;
    td[subtypes[s]].data['Pass/Fail'] = pf_td;
    td[subtypes[s]].change.emit()
}
    ''')
    for widget in widgets:
        widget.js_on_change('value', x)
    n_sigma.js_on_change('value', x)
    return hist, pf, td

def Gaussian():
    df_temp = AllData.merge(RM, on='Test ID', how='left')
    df_temp = df_temp.dropna()
    ds = ColumnDataSource(df_temp)
    subtypes = np.unique(ds.data['Sub Type'].tolist()).tolist()
    data_sources = {}
    serial_numbers = {}
    modules = {}
    for s in subtypes:
        data_sources[s] = ColumnDataSource(df_temp.query('`Sub Type` == @s'))
        serial_numbers[s] = np.unique(df_temp.query('`Sub Type` == @s')['Full ID'].values.tolist()).tolist()
        modules[s] = np.unique(data_sources[s].data['level_1']).tolist()

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
    columns = ['Full ID', 'Outcome', 'Start Date', 'End Date']
    data = [ds.data['Full ID'], ds.data['Outcome'], date_range, date_range]
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

    all_widgets = {**mc_widgets, **dr_widgets}
    widgets = {k:w['widget'] for k,w in all_widgets.items()}

    n_sigma = NumericInput(value=1, low=0.01, high=10, title='# of standard deviations for passing', mode='float')

    hist, pf, td = Gaussian2(data_sources, views, widgets.values(), subtypes, serial_numbers, modules, n_sigma)
    plots = {}
    pf_plots = {}
    data_tables = {}
    for s in subtypes:
        p = figure(
            title='Residual Distribution for ' + s,
            x_axis_label='# of Standard Deviations from Mean',
            y_axis_label='Number of Boards',
            tools='pan,wheel_zoom,box_zoom,reset,save',
            width = 925
            )

        p.quad(top='top', bottom='bottom', left='left', right='right', source=hist[s], color = colors[0])
        p.visible = False
        plots[s] = p

        q = figure(
            title='Pass vs Fail for  ' + s,
            x_range=pf[s].data['x'],
            x_axis_label='',
            y_axis_label='Number of Boards',
            tools='pan,wheel_zoom,box_zoom,reset,save',
            width = 925
            )

        q.vbar(x='x', top='pass', source=pf[s], color=colors[2], width=0.8)
        q.vbar(x='x', top='fail', source=pf[s], color=colors[3], width=0.8)
        q.visible = False
        pf_plots[s] = q

        table_columns = [
                        TableColumn(field='Serial Number', title='Full ID'),
                        TableColumn(field='Module', title='Module'),
                        TableColumn(field='Deviation', title='# of Standard Deviations'),
                        TableColumn(field='Pass/Fail', title='Pass/Fail'),
                        ]
        data_tables[s] = DataTable(source=td[s], columns=table_columns, autosize_mode='fit_columns')
        data_tables[s].visible = False
            
    w = [*widgets.values()]
    # creates a custom select widget that changes which plot to display
    display_plot = CustomJS(args=dict(plots=plots, pf_plots=pf_plots, tables=data_tables, widget=w[0], serial_numbers=serial_numbers), code=('''
for (let [name,plot] of Object.entries(plots)){
    if (name == this.value){
        plot.visible = true
    } else {
        plot.visible = false
    }
}
for (let [name,widget] of Object.entries(pf_plots)){
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
widget.options = serial_numbers[this.value]
'''))
    
    select = Select(title='Sub Type', options=subtypes)
    select.js_on_change('value', display_plot)

    # column and row objects only take it lists, need to make arguments lists
    layout = column(row(w[0:2] + [select]), row(w[2:5] + [n_sigma]), column(list(plots.values())), column(list(pf_plots.values())), column(list(data_tables.values())))
    return layout
