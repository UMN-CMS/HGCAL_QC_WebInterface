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
from bokeh.models.widgets import HTMLTemplateFormatter
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
BE = tempBE.dropna()

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

        end_date.setDate(end_date.getDate() + 1);
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

def Histogram(data, view, widgets, modules, slider):
    # creates a dictionary of data sources, need a data source for each plot element
    hist_fit = {}
    hist_data = {}
    for i in modules:
        hist_fit[i] = ColumnDataSource(data={'top':[], 'bottom':[], 'left':[], 'right':[]})
        hist_data[i] = ColumnDataSource(data={'top':[], 'bottom':[], 'left':[], 'right':[]})

    std = ColumnDataSource(data={'columns':[], 'fit mean':[], 'fit std':[], 'data mean':[], 'data std':[]})
    dt = ColumnDataSource(data={'Sub Type':[], 'Full ID':[], 'Person Name':[], 'Time':[], 'Outcome':[], 'E Link':[], 'Fit Eye Opening':[], 'Data Eye Opening':[], 'Fit Quality':[]})
    # custom javascript to be run to actually create the plotted data on the website
    # all done in javascript so it runs on the website and can update without refreshing the page
    x = CustomJS(args=dict(hist_fit=hist_fit, hist_data=hist_data, data=data, view=view, modules=modules, slider=slider, std=std, dt=dt),code='''
// make arrays for the data sources ahead of time to be appended to
const columns = [];
const type_ids = [];
const full_ids = [];
const names = [];
const dates = [];
const outcomes = [];
const elinks = [];
const fits = [];
const datas = [];
const qualities = [];
const fit_means = [];
const data_means = [];
const fit_stds = [];
const data_stds = [];
// iterate over all the E Links
for (let i = 0; i < modules.length; i++) {
    const indices = view.filters[0].compute_indices(data);
    let mask = new Array(data.data['E Link'].length).fill(false);
    [...indices].forEach((x)=>{mask[x] = true;})

    // modify mask for whether the E Link is correct
    // add all table data
    for (let j = 0; j < mask.length; j++) {
        if (data.data['E Link'][j] == modules[i] && mask[j] == true){
            mask[j] = true;
            type_ids.push(data.data['Sub Type'][j])
            full_ids.push(data.data['Full ID'][j])
            names.push(data.data['Person Name'][j])
            dates.push(data.data['Time'][j])
            outcomes.push(data.data['Outcome'][j])
            elinks.push(data.data['E Link'][j])
            fits.push(data.data['Fit Eye Opening'][j])
            datas.push(data.data['Data Eye Opening'][j])
            qualities.push(data.data['Fit Quality'][j])
        } else {
            mask[j] = false;
        }
    }

    // apply filter to the correct column
    const fit_good_data = data.data['Fit Eye Opening'].filter((_,y)=>mask[y])
    const data_good_data = data.data['Data Eye Opening'].filter((_,y)=>mask[y])
    // slider adjusts the number of thresholds
    let bins = slider.value
    // configure the scale of the graph
    let fit_scale = d3.scaleLinear().domain([0.45,0.85]).nice()
    let data_scale = d3.scaleLinear().domain([0.45,0.85]).nice()

    // .nice() makes it so that thresholds can only take on certain values
    let f_binner = d3.bin().domain(fit_scale.domain()).thresholds(2*bins)
    let d_binner = d3.bin().domain(data_scale.domain()).thresholds(2*bins)
    // bin data and fill the data sources
    let f_d = f_binner(fit_good_data)
    let d_d = d_binner(data_good_data)
    let f_right = f_d.map(x=>x.x1)
    let f_left = f_d.map(x=>x.x0)
    let f_bottom = new Array(f_d.length).fill(0)
    let f_top = f_d.map(x=>x.length);
    let d_right = d_d.map(x=>x.x1)
    let d_left = d_d.map(x=>x.x0)
    let d_bottom = new Array(d_d.length).fill(0)
    let d_top = d_d.map(x=>x.length);
    hist_fit[modules[i]].data['right'] = f_right;
    hist_fit[modules[i]].data['left'] = f_left;
    hist_fit[modules[i]].data['bottom'] = f_bottom;
    hist_fit[modules[i]].data['top'] = f_top;
    hist_fit[modules[i]].change.emit()
    hist_data[modules[i]].data['right'] = d_right;
    hist_data[modules[i]].data['left'] = d_left;
    hist_data[modules[i]].data['bottom'] = d_bottom;
    hist_data[modules[i]].data['top'] = d_top;
    hist_data[modules[i]].change.emit()
    // find the mean and standard deviation and push it to arrays
    // Eye Opening mean is always 200
    columns.push(modules[i])
    fit_means.push(d3.mean(fit_good_data))
    fit_stds.push(d3.deviation(fit_good_data))
    data_means.push(d3.mean(data_good_data))
    data_stds.push(d3.deviation(data_good_data))
}
// update data sources
// need .change.emit() for the changes to take effect
std.data['columns'] = columns;
std.data['fit mean'] = fit_means;
std.data['fit std'] = fit_stds;
std.data['data mean'] = data_means;
std.data['data std'] = data_stds;
std.change.emit()

dt.data['Sub Type'] = type_ids;
dt.data['Full ID'] = full_ids;
dt.data['Person Name'] = names;
dt.data['Time'] = dates;
dt.data['Outcome'] = outcomes;
dt.data['E Link'] = elinks;
dt.data['Fit Eye Opening'] = fits;
dt.data['Data Eye Opening'] = datas;
dt.data['Fit Quality'] = qualities;
dt.change.emit()
    ''')
    for widget in widgets:
        widget.js_on_change('value', x)
    slider.js_on_change('value', x)
    return hist_fit, hist_data, std, dt

def Filter():
    # make ColumnDataSources from the Pandas Dataframes
    temp = AllData.merge(BE, on='Test ID', how='left')
    ds = ColumnDataSource(temp.dropna())
    # make the widgets
    mc_widgets = {}
    dr_widgets = {}
    # lambda is the inputs they take in
    # MultiChoice and DatePicker are the widgets being created
    # this method is nice when creating a bunch of similar widgets at once
    multi_choice = (lambda x,y: MultiChoice(options=x, value=[], title=y), 'value')
    start_date = (lambda x,y,z: DatePicker(min_date=x,max_date=y, value='2024-11-20', title=z), 'value')
    today = datetime.date.today()
    end_date = (lambda x,y,z: DatePicker(min_date=x,max_date=y, value=today, title=z), 'value')
    min_date = pd.Timestamp((min(ds.data['Time']))).date()
    date_range = []
    while min_date <= today:
        date_range.append(min_date)
        min_date += datetime.timedelta(days=1)
    # get the E Links
    modules = np.unique(ds.data['E Link'].tolist()).tolist()

    # information for constructing widgets
    # column name has to be the name of the column in the data source that you're filtering with this widget
    columns = ['Major Type', 'Sub Type', 'Full ID', 'Person Name', 'Outcome', 'Start Date', 'End Date']
    # values that you want to choose from in the widget
    data = [ds.data['Major Type'].tolist(), ds.data['Sub Type'].tolist(), ds.data['Full ID'].tolist(), ds.data['Person Name'].tolist(), ds.data['Outcome'], date_range, date_range]
    # type of widget
    t = [multi_choice, multi_choice, multi_choice, multi_choice, multi_choice, start_date, end_date]

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

    # applies the custom filter to the widgets and then to the data sources
    custom_filter = CustomJSFilter(args=dict(mc_widgets=mc_widgets, dr_widgets=dr_widgets),code=filter_code)
    view = CDSView(source=ds, filters=[custom_filter])
    
    # creates the slider widget and combined the mc and dr widgets
    slider = Slider(start=1, end=18, value=8, step=1, title='Granularity')
    all_widgets = {**mc_widgets, **dr_widgets}
    widgets = {k:w['widget'] for k,w in all_widgets.items()}

    # calls the histogram to get the data sources used in plotting and tables
    fit_hist, data_hist, std, dt = Histogram(ds, view, widgets.values(), modules, slider)

    # creates the figure objects
    p = figure(
        title='Fit Eye Opening',
        x_axis_label='',
        y_axis_label='Number of Boards',
        tools='pan,wheel_zoom,box_zoom,reset,save',
        width = 925
        )
    q = figure(
        title='Data Eye Opening',
        x_axis_label='',
        y_axis_label='Number of Boards',
        tools='pan,wheel_zoom,box_zoom,reset,save',
        width = 925
        )
    
    # adds glyphs to the figures
    # source determines what data source to use to make the plot
    # this allows the plot to update whenever the data source does
    for i in range(len(modules)):
        p.quad(top='top', bottom='bottom', left='left', right='right', source=fit_hist[modules[i]], legend_label=modules[i], color = colors[i])
        q.quad(top='top', bottom='bottom', left='left', right='right', source=data_hist[modules[i]], legend_label=modules[i], color = colors[i])
        
    p.legend.click_policy='hide'
    p.legend.label_text_font_size = '8pt'
    q.legend.click_policy='hide'
    q.legend.label_text_font_size = '8pt'

    module_template = '''
<div>
<a href="module.py?full_id=<%= value %>"target="_blank">
<%= value %>
</a>
</div> 
'''
    board = HTMLTemplateFormatter(template=module_template)

    # creates the data tables
    # they work the same way in terms of updating with the data source
    table_columns = [
                    TableColumn(field='columns', title='E Link'), 
                    TableColumn(field='fit mean', title='Fit Eye Mean'),
                    TableColumn(field='fit std', title='Fit Eye st. dev.'),
                    TableColumn(field='data mean', title='Data Eye Mean'),
                    TableColumn(field='data std', title='Data Eye st. dev.'),
                    ]
    table = DataTable(source=std, columns=table_columns, autosize_mode='fit_columns', width=800)
    table_columns2 = [
                    TableColumn(field='Sub Type', title='Sub Type'),
                    TableColumn(field='Full ID', title='Full ID', formatter=board),
                    TableColumn(field='Person Name', title='Tester'),
                    TableColumn(field='Time', title='Date', formatter=DateFormatter()),
                    TableColumn(field='Outcome', title='Outcome'), 
                    TableColumn(field='E Link', title='E Link'),
                    TableColumn(field='Fit Eye Opening', title='Fit Eye Opening'),
                    TableColumn(field='Data Eye Opening', title='Data Eye Opening'),
                    TableColumn(field='Fit Quality', title='Fit Quality'),
                    ]
    data_table = DataTable(source=dt, columns=table_columns2, autosize_mode='fit_columns', width=1000)
    w = [*widgets.values()]
    
    # changes the options for the barcodes widget based on the subtype selected
    subtypes = {}
    for major in np.unique(ds.data['Major Type'].tolist()).tolist():
        subtypes[major] = np.unique(temp.query('`Major Type` == @major')['Sub Type'].values.tolist()).tolist()
    serial_numbers = {}
    for s in np.unique(ds.data['Sub Type'].tolist()).tolist():
        serial_numbers[s] = np.unique(temp.query('`Sub Type` == @s')['Full ID'].values.tolist()).tolist()
    
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

    # gets the second half of the webpage with the residual plots
    # by having it in it's own function with it's own widgets it can be controlled separately
    #layout = Gaussian()
    # turns all the bokeh items into json and returns them
    plot_json = json.dumps(json_item(row(column(row(w[0:3]), row(w[3:5]), row(w[5:]), slider, p, q, table, data_table))))
    return plot_json


def Gaussian2(mp_data, eo_data, view, subtypes, barcodes, widgets, modules, n_sigma):
    hist_mp = {}
    hist_eo = {}
    pf_mp = {}
    pf_eo = {}
    td = {}
    for s in subtypes:
        hist_mp[s] = ColumnDataSource(data={'top':[], 'bottom':[], 'left':[], 'right':[]})
        hist_eo[s] = ColumnDataSource(data={'top':[], 'bottom':[], 'left':[], 'right':[]})
        # these data sources are set up for a vbar plot instead of a quad
        pf_mp[s] = ColumnDataSource(data={'pass':[], 'fail':[], 'x':['Fail', 'Pass']})
        pf_eo[s] = ColumnDataSource(data={'pass':[], 'fail':[], 'x':['Fail', 'Pass']})
        td[s] = ColumnDataSource(data={'Serial Number':[], 'Module':[], 'Midpoint Deviation':[], 'Pass/Fail MP':[], 'Eye Opening Deviation':[], 'Pass/Fail EO':[]})

    x = CustomJS(args=dict(hist_mp=hist_mp, hist_eo=hist_eo, mp_data=mp_data, eo_data=eo_data, views=view, subtypes=subtypes, barcodes=barcodes, modules=modules, n_sigma=n_sigma, pf_mp=pf_mp, pf_eo=pf_eo, td=td),code='''
// iterate by subtype
for (let s = 0; s < subtypes.length; s++) {
    // create an array for the residuals at the start
    const mp_residules = [];
    const eo_residules = [];

    // create a dictionary for each board's average deviation for each E Link
    var mp_chis = {};
    var eo_chis = {};
    // make an empty array for each board
    for (let sn = 0; sn < barcodes[subtypes[s]].length; sn++) {
        mp_chis[barcodes[subtypes[s]][sn]] = [];
        eo_chis[barcodes[subtypes[s]][sn]] = [];
    } 
    // iterate over E Links
    // each E Link will have a different midpoint, therefore need a different average for each
    for (let k = 0; k < modules[subtypes[s]].length; k++) {
        // create mask
        const indices = views[subtypes[s]].filters[0].compute_indices(mp_data[subtypes[s]]);
        let mask = new Array(mp_data[subtypes[s]].data['Midpoint'].length).fill(false);
        [...indices].forEach((x)=>{mask[x] = true;})

        // filter by E Link
        for (let j = 0; j < mp_data[subtypes[s]].get_length(); j++) {
            if (mask[j] == true && mp_data[subtypes[s]].data['E Link'][j] == modules[subtypes[s]][k]){
                mask[j] = true;
            } else {
                mask[j] = false;
            }
        }
        // apply filter
        const mp_good_data = mp_data[subtypes[s]].data['Midpoint'].filter((_,y)=>mask[y])
        const eo_good_data = eo_data[subtypes[s]].data['Eye Opening'].filter((_,y)=>mask[y])
        // calculate mean and standard deviation
        let mp_mean = d3.mean(mp_good_data)
        let eo_mean = d3.mean(eo_good_data)
        let mp_std = d3.deviation(mp_good_data)
        let eo_std = d3.deviation(eo_good_data)
        // iterate over barcodes
        for (let sn = 0; sn < barcodes[subtypes[s]].length; sn++) {
            const indices = views[subtypes[s]].filters[0].compute_indices(mp_data[subtypes[s]]);
            let mask_sn = new Array(mp_data[subtypes[s]].data['Midpoint'].length).fill(false);
            [...indices].forEach((x)=>{mask_sn[x] = true;})

            // iterate over all valid data points
            for (let j = 0; j < mp_data[subtypes[s]].get_length(); j++) {
                if (mask_sn[j] == true && mp_data[subtypes[s]].data['E Link'][j] == modules[subtypes[s]][k] && mp_data[subtypes[s]].data['Full ID'][j] == barcodes[subtypes[s]][sn]){
                    mask_sn[j] = true;
                    // calculate difference
                    let x1 = mp_data[subtypes[s]].data['Midpoint'][j] - mp_mean;
                    // prevents divide by zero error
                    if (mp_std == 0) {
                        let chi1 = 0;
                        mp_residules.push(chi1)
                    } else {
                        // calculate the number of standard deviations away that this data point is
                        let chi1 = x1/mp_std;
                        mp_residules.push(chi1)
                    }
                    let x2 = eo_data[subtypes[s]].data['Eye Opening'][j] - eo_mean;
                    if (eo_std == 0) {
                        let chi2 = 0;
                        eo_residules.push(chi2)
                    } else {
                        let chi2 = x2/eo_std;
                        eo_residules.push(chi2)
                    }
                } else {
                    mask_sn[j] = false;
                }
            }
            // filter data for this board and find the average
            const mp_good_data_sn = mp_data[subtypes[s]].data['Midpoint'].filter((_,y)=>mask_sn[y])
            let mean_sn1 = d3.mean(mp_good_data_sn)
            // determine how far the average for this board is from the overall average
            let y1 = mean_sn1 - mp_mean;
            if (mp_std == 0) {
                let chi_sn1 = 0;
                mp_chis[barcodes[subtypes[s]][sn]].push(Math.abs(chi_sn1))
            } else {
                let chi_sn1 = y1/mp_std;
                mp_chis[barcodes[subtypes[s]][sn]].push(Math.abs(chi_sn1))
            }

            const eo_good_data_sn = eo_data[subtypes[s]].data['Eye Opening'].filter((_,y)=>mask_sn[y])
            let mean_sn2 = d3.mean(eo_good_data_sn)
            let y2 = mean_sn2 - eo_mean;
            if (eo_std == 0) {
                let chi_sn2 = 0;
                eo_chis[barcodes[subtypes[s]][sn]].push(Math.abs(chi_sn2))
            } else {
                let chi_sn2 = y2/eo_std;
                eo_chis[barcodes[subtypes[s]][sn]].push(Math.abs(chi_sn2))
            }
        }
    }

    // create the residules histogram
    let binner = d3.bin()
    let d1 = binner(mp_residules)
    let right1 = d1.map(x=>x.x1)
    let left1 = d1.map(x=>x.x0)
    let bottom1 = new Array(d1.length).fill(0)
    let top1 = d1.map(x=>x.length);
    
    hist_mp[subtypes[s]].data['right'] = right1;
    hist_mp[subtypes[s]].data['left'] = left1;
    hist_mp[subtypes[s]].data['bottom'] = bottom1;
    hist_mp[subtypes[s]].data['top'] = top1;
    hist_mp[subtypes[s]].change.emit()

    let d2 = binner(eo_residules)
    let right2 = d2.map(x=>x.x1)
    let left2 = d2.map(x=>x.x0)
    let bottom2 = new Array(d2.length).fill(0)
    let top2 = d2.map(x=>x.length);
    
    hist_eo[subtypes[s]].data['right'] = right2;
    hist_eo[subtypes[s]].data['left'] = left2;
    hist_eo[subtypes[s]].data['bottom'] = bottom2;
    hist_eo[subtypes[s]].data['top'] = top2;
    hist_eo[subtypes[s]].change.emit()

    // determine if boards passed or failed
    let mp_t_pass = 0;
    let mp_t_fail = 0;
    let eo_t_pass = 0;
    let eo_t_fail = 0;
    const sn_td = [];
    const mod_td = [];
    const mp_chi_td = [];
    const eo_chi_td = [];
    const mp_pf_td = [];
    const eo_pf_td = [];
    // iterate over barcodes
    for (let sn = 0; sn < barcodes[subtypes[s]].length; sn++) {
        let mp_pass = 0;
        let mp_fail = 0;
        let eo_pass = 0;
        let eo_fail = 0;
        // iterate over the average residuals for this board
        for (let m = 0; m < mp_chis[barcodes[subtypes[s]][sn]].length; m++) {
            let chi_i_mp = mp_chis[barcodes[subtypes[s]][sn]][m]
            // check if it passes
            if (chi_i_mp <= n_sigma.value) {
                mp_pass = mp_pass + 1;
                mp_pf_td.push('PASS')
            } else {
                mp_fail = mp_fail + 1;
                mp_pf_td.push('FAIL')
            }
            sn_td.push(barcodes[subtypes[s]][sn])
            mod_td.push(modules[subtypes[s]][m])
            mp_chi_td.push(chi_i_mp)
        }

        for (let e = 0; e < eo_chis[barcodes[subtypes[s]][sn]].length; e++) {
            let chi_i = eo_chis[barcodes[subtypes[s]][sn]][e]
            if (chi_i <= n_sigma.value) {
                eo_pass = eo_pass + 1;
                eo_pf_td.push('PASS')
            } else {
                eo_fail = eo_fail + 1;
                eo_pf_td.push('FAIL')
            }
            eo_chi_td.push(chi_i)
        }

        // if all pass, only then does the board pass
        if (mp_fail == 0) {
            mp_t_pass = mp_t_pass + 1;
        } else {
            mp_t_fail = mp_t_fail + 1;
        }

        if (eo_fail == 0) {
            eo_t_pass = eo_t_pass + 1;
        } else {
            eo_t_fail = eo_t_fail + 1;
        }
    }
    pf_mp[subtypes[s]].data['pass'] = [0, mp_t_pass];
    pf_mp[subtypes[s]].data['fail'] = [mp_t_fail, 0];
    pf_mp[subtypes[s]].change.emit()

    pf_eo[subtypes[s]].data['pass'] = [0, eo_t_pass];
    pf_eo[subtypes[s]].data['fail'] = [eo_t_fail, 0];
    pf_eo[subtypes[s]].change.emit()

    td[subtypes[s]].data['Serial Number'] = sn_td;
    td[subtypes[s]].data['Module'] = mod_td;
    td[subtypes[s]].data['Midpoint Deviation'] = mp_chi_td;
    td[subtypes[s]].data['Pass/Fail MP'] = mp_pf_td;
    td[subtypes[s]].data['Eye Opening Deviation'] = eo_chi_td;
    td[subtypes[s]].data['Pass/Fail EO'] = eo_pf_td;
    td[subtypes[s]].change.emit()
}
    ''')
    for widget in widgets:
        widget.js_on_change('value', x)
    n_sigma.js_on_change('value', x)
    return hist_mp, hist_eo, td, pf_mp, pf_eo

def Gaussian():
    # make data sources
    mp_temp = AllData.merge(MP, on='Test ID', how='left')
    mp_temp = mp_temp.dropna()
    ds_mp = ColumnDataSource(mp_temp)
    eo_temp = AllData.merge(EO, on='Test ID', how='left')
    eo_temp = eo_temp.dropna()
    ds_eo = ColumnDataSource(eo_temp)

    # get subtypes list
    subtypes = np.unique(ds_mp.data['Sub Type'].tolist()).tolist()
    mp_data_sources = {}
    eo_data_sources = {}
    barcodes = {}
    modules = {}
    # make barcodes dict
    # make data sources for each subtype
    # sort E Links by subtype (not all have the same E Links)
    for s in subtypes:
        mp_data_sources[s] = ColumnDataSource(mp_temp.query('`Sub Type` == @s'))
        eo_data_sources[s] = ColumnDataSource(eo_temp.query('`Sub Type` == @s'))
        barcodes[s] = np.unique(mp_temp.query('`Sub Type` == @s')['Full ID'].values.tolist()).tolist()
        modules[s] = np.unique(mp_data_sources[s].data['E Link']).tolist()

    # widget creation is the same as before
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
    columns = ['Full ID', 'Outcome', 'Start Date', 'End Date']
    data = [ds_mp.data['Full ID'].tolist(), ds_mp.data['Outcome'], date_range, date_range]
    t = [multi_choice, multi_choice, start_date, end_date]

    for i in range(len(columns)):
        widget_constructor, trigger = t[i]
        if t[i] == multi_choice:
            possible_vals = np.unique(data[i]).tolist()
            widget = widget_constructor(possible_vals, columns[i])
            typ = 'multi_choice'
            widget.js_on_change(trigger, CustomJS(args=dict(src1=mp_data_sources, src2=eo_data_sources, subtypes=subtypes), code='''
for (let i = 0; i < subtypes.length; i++) {
    src1[subtypes[i]].change.emit()
    src2[subtypes[i]].change.emit()
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
            widget.js_on_change(trigger, CustomJS(args=dict(src1=mp_data_sources, src2=eo_data_sources, subtypes=subtypes), code='''
for (let i = 0; i < subtypes.length; i++) {
    src1[subtypes[i]].change.emit()
    src2[subtypes[i]].change.emit()
}
'''))
            dr_widgets[columns[i]] = {
                'type': typ,
                'possible_vals': possible_vals,
                'widget': widget,}

    # make and apply filter
    custom_filter = CustomJSFilter(args=dict(mc_widgets=mc_widgets, dr_widgets=dr_widgets),code=filter_code)
    views = {}
    for s in subtypes:
        views[s] = CDSView(source=mp_data_sources[s], filters=[custom_filter])

    # combine widgets
    all_widgets = {**mc_widgets, **dr_widgets}
    widgets = {k:w['widget'] for k,w in all_widgets.items()}

    # create widget to input passing criteria
    n_sigma = NumericInput(value=1, low=0.01, high=10, title='# of standard deviations for passing', mode='float')

    # get plotting data sources
    mp_hist, eo_hist, td, mp_pf, eo_pf = Gaussian2(mp_data_sources, eo_data_sources, views, subtypes, barcodes, widgets.values(), modules, n_sigma)

    # create dictionaries for plots
    mp_plots = {}
    eo_plots = {}
    mp_pf_plots = {}
    eo_pf_plots = {}
    data_tables = {}
    for s in subtypes:
        p = figure(
            title='Residual Distribution for Midpoint for ' + s,
            x_axis_label='# of Standard Deviations from Mean',
            y_axis_label='Number of Boards',
            tools='pan,wheel_zoom,box_zoom,reset,save',
            width = 925
            )

        p.quad(top='top', bottom='bottom', left='left', right='right', source=mp_hist[s], color = colors[0])
        p.visible = False
        mp_plots[s] = p

        r = figure(
            title='Residual Distribution for Eye Opening for ' + s,
            x_axis_label='# of Standard Deviations from Mean',
            y_axis_label='Number of Boards',
            tools='pan,wheel_zoom,box_zoom,reset,save',
            width = 925
            )

        r.quad(top='top', bottom='bottom', left='left', right='right', source=eo_hist[s], color = colors[0])
        r.visible = False
        eo_plots[s] = r

        q = figure(
            title='Midpoint Pass vs Fail for  ' + s,
            x_range=mp_pf[s].data['x'],
            x_axis_label='',
            y_axis_label='Number of Boards',
            tools='pan,wheel_zoom,box_zoom,reset,save',
            width = 925
            )

        q.vbar(x='x', top='pass', source=mp_pf[s], color=colors[2], width=0.8)
        q.vbar(x='x', top='fail', source=mp_pf[s], color=colors[3], width=0.8)
        q.visible = False
        mp_pf_plots[s] = q

        l = figure(
            title='Eye Opening Pass vs Fail for  ' + s,
            x_range=eo_pf[s].data['x'],
            x_axis_label='',
            y_axis_label='Number of Boards',
            tools='pan,wheel_zoom,box_zoom,reset,save',
            width = 925
            )

        l.vbar(x='x', top='pass', source=eo_pf[s], color=colors[2], width=0.8)
        l.vbar(x='x', top='fail', source=eo_pf[s], color=colors[3], width=0.8)
        l.visible = False
        eo_pf_plots[s] = l

        table_columns = [
                        TableColumn(field='Serial Number', title='Full ID'),
                        TableColumn(field='Module', title='Module'),
                        TableColumn(field='Midpoint Deviation', title='Midpoint Deviation'),
                        TableColumn(field='Pass/Fail MP', title='Pass/Fail'),
                        TableColumn(field='Eye Opening Deviation', title='Eye Opening Deviation'), 
                        TableColumn(field='Pass/Fail EO', title='Pass/Fail'),
                        ]
        data_tables[s] = DataTable(source=td[s], columns=table_columns, autosize_mode='fit_columns')
        data_tables[s].visible = False

    w = [*widgets.values()]

    # custom javascript that gets run when the subtypes select widget is changed
    # displays the plots for that subtype and hides the others
    # also changes full id options
    display_plot = CustomJS(args=dict(mp_plots=mp_plots, eo_plots=eo_plots, mp_pf_plots=mp_pf_plots, eo_pf_plots=eo_pf_plots, tables=data_tables, widget=w[0], barcodes=barcodes), code=('''
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
for (let [name,plot] of Object.entries(mp_pf_plots)){
    if (name == this.value){
        plot.visible = true
    } else {
        plot.visible = false
    }
}
for (let [name,plot] of Object.entries(eo_pf_plots)){
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
widget.options = barcodes[this.value]
'''))
    
    select = Select(title='Sub Type', options=subtypes)
    select.js_on_change('value', display_plot)

    # create and return layout
    # column and row objects only take it lists, need to make arguments lists
    layout = column(row(w[0:2] + [select]), row(w[2:5] + [n_sigma]), column(list(mp_plots.values())), column(list(mp_pf_plots.values())), column(list(eo_plots.values())), column(list(eo_pf_plots.values())), column(list(data_tables.values())))
    return layout
