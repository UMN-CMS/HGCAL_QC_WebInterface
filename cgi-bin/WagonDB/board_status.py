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
)
from bokeh.embed import json_item
from bokeh.palettes import d3, brewer
from bokeh.layouts import column, row
import json
import makeTestingData as mTD

TestData = pd.read_csv(mTD.get_test(), parse_dates=['Time'])
BoardData = pd.read_csv(mTD.get_board())
PeopleData = pd.read_csv(mTD.get_people())
TestTypeData = pd.read_csv(mTD.get_test_types())
TestTypeData = TestTypeData.rename(columns={'Name':'Test Name'})
CheckInData = pd.read_csv(mTD.get_check_in())
mergetemp = TestData.merge(BoardData, on='Board ID', how='left')
mergetemp = mergetemp.merge(CheckInData, on='Board ID', how='left')
AllData = mergetemp.merge(PeopleData, on='Person ID', how='left')
AllData = AllData.rename(columns={'Successful':'Outcome'})
AllData['Outcome'] = AllData['Outcome'].replace(0, 'Unsuccessful')
AllData['Outcome'] = AllData['Outcome'].replace(1, 'Successful')
AllData = AllData.merge(TestTypeData, on='Test Type ID', how='left')
tests_needed = mTD.get_tests_needed_dict()

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
return indices;

''')

colors = [d3['Category10'][10][0], d3['Category10'][10][1], d3['Category10'][10][2], d3['Category10'][10][3], d3['Category10'][10][4], d3['Category10'][10][5], d3['Category10'][10][6], d3['Category10'][10][7], d3['Category10'][10][8], d3['Category10'][10][9], brewer['Accent'][8][0], brewer['Accent'][8][3], brewer['Dark2'][8][0], brewer['Dark2'][8][2], brewer['Dark2'][8][3], brewer['Dark2'][8][4], brewer['Dark2'][8][5], brewer['Dark2'][8][6], d3['Category20'][20][1], d3['Category20'][20][9], d3['Category20c'][20][19]]

def TotalPlot(data, view, widgets, date_range, boards, start_widget, end_widget):
    data_failed = ColumnDataSource(data={'dates':[], 'counts':[]})
    data_done = ColumnDataSource(data={'dates':[], 'counts':[]})
    data_shipped = ColumnDataSource(data={'dates':[], 'counts':[]})
    data_inprog = ColumnDataSource(data={'dates':[], 'counts':[]})

    x = CustomJS(args=dict(data_failed=data_failed, data_done=data_done, data_shipped=data_shipped, data_inprog=data_inprog, data=data, view=view, date_range=date_range, boards=boards, tests_needed=tests_needed, start_widget=start_widget, end_widget=end_widget),code='''
const indices = view.filters[0].compute_indices(data);
let mask = new Array(data.data['Test ID'].length).fill(false);
[...indices].forEach((x)=>{mask[x] = true;})

const dates = []
const tsd_failed = []
const tsd_done = []
const tsd_shipped = []
const tsd_inprog = []

let day0 = new Date(date_range[0]);
for (let d = 0; d < date_range.length; d++) {
    let day2 = new Date(date_range[d]);
    let day1 = new Date(day2.setDate(day2.getDate() + 1));

    if (day2 < new Date(start_widget.value) || day2 > new Date(end_widget.value)){
        continue;
    }

    let total_failed = 0;
    let total_done = 0;
    let total_inprog = 0;
    let total_shipped = 0;

    for (let b = 0; b < boards.length; b++) {
        let status = false;
        let tests_passed = 0;
        const tests_run = [];

        for (let m = 0; m < mask.length; m++) {
            if (mask[m] ==  true && new Date(data.data['Check In Time'][m]) >= day0 && new Date(data.data['Check In Time'][m]) <= day1 && data.data['Full ID'][m] == boards[b]){
                status = 'in_prog';
                if (new Date(data.data['Check Out Time'][m]) >= day0 && new Date(data.data['Check Out Time'][m]) <= day1){
                    status = 'Shipped';
                    break
                }
                if (data.data['Time'][m] >= day0 && data.data['Time'][m] <= day1 && tests_run.includes(data.data['Test Name'][m]) != true){
                    if (data.data['Outcome'][m] == 'Unsuccessful'){
                        status = 'Failed';
                        break
                    } else {
                        tests_passed = tests_passed + 1;
                        tests_run.push(data.data['Test Name'][m])
                    }
                }
            }
        }
        
        if (status != false) {
            if (status == 'Failed') {
                total_failed = total_failed + 1;
            } else if (status == 'Shipped') {
                total_shipped = total_shipped + 1;
            } else if (tests_passed == tests_needed[boards[b]]) {
                total_done = total_done + 1;
            } else {
                total_inprog = total_inprog + 1;
            }
        }
    }
    dates.push(day2.getTime())
    tsd_failed.push(total_failed)
    tsd_done.push(total_done)
    tsd_shipped.push(total_shipped)
    tsd_inprog.push(total_inprog)
}
data_failed.data['dates'] = dates;
data_failed.data['counts'] = tsd_failed;
data_failed.change.emit()
data_done.data['dates'] = dates;
data_done.data['counts'] = tsd_done;
data_done.change.emit()
data_shipped.data['dates'] = dates;
data_shipped.data['counts'] = tsd_shipped;
data_shipped.change.emit()
data_inprog.data['dates'] = dates;
data_inprog.data['counts'] = tsd_inprog;
data_inprog.change.emit()
''')
    for widget in widgets:
        widget.js_on_change('value', x)
    return data_failed, data_done, data_inprog, data_shipped

def Filter():
    df = AllData
    df = df.dropna()
    ds = ColumnDataSource(df)
    mc_widgets = {}
    dr_widgets = {}
    multi_choice = (lambda x,y: MultiChoice(options=x, value=[], title=y), 'value')
    start_date = (lambda x,y,z: DatePicker(min_date=x,max_date=y, value=x, title=z), 'value')
    today = datetime.date.today()
    end_date = (lambda x,y,z: DatePicker(min_date=x,max_date=y, value=today, title=z), 'value')
    min_date = pd.Timestamp((min(ds.data['Check In Time']))).date()
    date_range = []
    while min_date <= today:
        date_range.append(min_date)
        min_date += datetime.timedelta(days=1)
    columns = ['Major Type', 'Sub Type', 'Full ID']
    data = [ds.data['Major Type'].tolist(), ds.data['Sub Type'].tolist(), ds.data['Full ID'].tolist()]
    t = [multi_choice, multi_choice, multi_choice]

    p = figure(
        title='Board Status Over Time',
        x_axis_label='Date',
        y_axis_label='',
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

    start_date = DatePicker(min_date=min(date_range), max_date=max(date_range), value=min(date_range), title='Start Date')
    end_date = DatePicker(min_date=min(date_range), max_date=max(date_range), value=today, title='End Date')

    custom_filter = CustomJSFilter(args=dict(mc_widgets=mc_widgets, dr_widgets=dr_widgets),code=filter_code)
    view = CDSView(source=ds, filters=[custom_filter])
    all_widgets = {**mc_widgets, **dr_widgets}
    widgets = {k:w['widget'] for k,w in all_widgets.items()}
    data_failed, data_done, data_inprog, data_shipped = TotalPlot(ds, view, widgets.values(), date_range, np.unique(ds.data['Full ID'].tolist()), start_date, end_date)
    p.line('dates', 'counts', source=data_inprog, legend_label='In Progress', color=colors[0], line_width=2, muted_alpha=0.2)
    p.line('dates', 'counts', source=data_done, legend_label='Finished', color=colors[2], line_width=2, muted_alpha=0.2)
    p.line('dates', 'counts', source=data_failed, legend_label='Failed', color=colors[3], line_width=2, muted_alpha=0.2)
    p.line('dates', 'counts', source=data_shipped, legend_label='Shipped', color=colors[5], line_width=2, muted_alpha=0.2)
    table_columns = [
                    TableColumn(field='dates', title='Dates', formatter=DateFormatter()),
                    TableColumn(field='total_counts', title='Total Tests Completed'),
                    TableColumn(field='suc_counts', title='Successful Tests Completed'),
                    TableColumn(field='unc_counts', title='Unsuccessful Tests Completed'),
                    ]
    #data_table = DataTable(source=dt, columns=table_columns, autosize_mode='fit_columns')
    p.legend.click_policy='mute'
    p.legend.label_text_font_size = '8pt'
    p.legend.location = 'top_left'
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

    plot_json = json.dumps(json_item(column(row(w[0:3]), row([start_date, end_date]), p)))
    return plot_json

