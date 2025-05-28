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
    DataTable,
    DateFormatter,
    TableColumn,
    Select,
    Label,
    NumericInput,
)
from bokeh.embed import json_item
from bokeh.layouts import column, row
from bokeh.models.widgets import HTMLTemplateFormatter
import numpy as np
import pandas as pd
import json
from datetime import datetime as dt
import datetime
import makeTestingData as mTD

BoardData = pd.read_csv(mTD.get_board())
StatusData = pd.read_csv('./cache/current_board_status.csv')
mergetemp = TestData.merge(BoardData, on='Board ID', how='left')
AllData = mergetemp.merge(StatusData, on='Full ID', how='left')
AllData.dropna()

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

def makeTable(ds, widgets, view, test_names, serial_numbers, passed_widget, failed_widget, not_tested_widget):
    data_dict = {'Sub Type':[], 'Full ID':[], 'Location':[]}
    for name in test_names:
        data_dict[name] = []

    td = ColumnDataSource(data_dict)

    x = CustomJS(args=dict(td=td, data=ds, view=view, test_names=test_names, serial_numbers=serial_numbers, passed_widget=passed_widget, failed_widget=failed_widget, not_tested_widget=not_tested_widget),code='''
const type_ids = []
const full_ids = []
const locations = []
const test_dict = {}
for (let t = 0; t < test_names.length; t++) {
    test_dict[test_names[t]] = []
}

function check_all_true(el) {
    return el
}

const indices = view.filters[0].compute_indices(data);
let mask = new Array(data.data['Full ID'].length).fill(false);
[...indices].forEach((x)=>{mask[x] = true;})

for (let sn = 0; sn < serial_numbers.length; sn++) {
    let pass_mask = false
    let pass_all_mask = false
    let passed_vals = passed_widget.value
    let failed_vals = failed_widget.value
    let not_run_vals = not_tested_widget.value
    const passed_array = []
    const failed_array = []
    const not_run_array = []
    
    let location = ''
    let subtype = ''

    for (let j = 0; j < data.get_length(); j++) {
        if (mask[j] == true && data.data['Full ID'][j] == serial_numbers[sn]){
            pass_mask = true
            location = data.data['Location'][j]
            subtype = data.data['Sub Type'][j]
        }
    }

    if (passed_vals.length != 0) {
        for (let i = 0; i < passed_vals.length; i++) {
            let passed_this = false

            for (let j = 0; j < data.get_length(); j++) {
                if (mask[j] == true && data.data['Full ID'][j] == serial_numbers[sn]){
                    if (data.data['Test Name'][j] == passed_vals[i] && data.data['Status'][j] == 'Passed') {
                        passed_this = true
                    }
                }
            }
            passed_array.push(passed_this)
        }
    } else {
        passed_array.push(true)
    }

    if (failed_vals.length != 0) {
        for (let i = 0; i < failed_vals.length; i++) {
            let passed_this = false

            for (let j = 0; j < data.get_length(); j++) {
                if (mask[j] == true && data.data['Full ID'][j] == serial_numbers[sn]){
                    if (data.data['Test Name'][j] == failed_vals[i] && data.data['Status'][j] == 'Failed') {
                        passed_this = true
                    }
                }
            }
            failed_array.push(passed_this)
        }
    } else {
        failed_array.push(true)
    }

    if (not_run_vals.length != 0) {
        for (let i = 0; i < not_run_vals.length; i++) {
            let passed_this = false

            for (let j = 0; j < data.get_length(); j++) {
                if (mask[j] == true && data.data['Full ID'][j] == serial_numbers[sn]){
                    if (data.data['Test Name'][j] == not_run_vals[i] && data.data['Status'][j] == 'Not Run') {
                        passed_this = true
                    }
                }
            }
            not_run_array.push(passed_this)
        }
    } else {
        not_run_array.push(true)
    }

    if (pass_mask == true) {
        if (passed_array.every(check_all_true) == true && failed_array.every(check_all_true) == true && not_run_array.every(check_all_true) == true) {
            type_ids.push(subtype)
            locations.push(location)
            full_ids.push(serial_numbers[sn])

            for (let j = 0; j < data.get_length(); j++) {
                if (mask[j] == true && data.data['Full ID'][j] == serial_numbers[sn]){
                    test_dict[data.data['Test Name'][j]].push(data.data['Status'][j])
                }
            }

            for (let t = 0; t < test_names.length; t++) {
                if (test_dict[test_names[t]].length != full_ids.length) {
                    test_dict[test_names[t]].push('Not Run')
                }
            }
        }
    }
}
td.data['Sub Type'] = type_ids;
td.data['Full ID'] = full_ids;
td.data['Location'] = locations;
for (let t = 0; t < test_names.length; t++) {
    td.data[test_names[t]] = test_dict[test_names[t]];
}
td.change.emit()
''')

    for widget in widgets.values():
        widget.js_on_change('value', x)

    passed_widget.js_on_change('value', x)
    failed_widget.js_on_change('value', x)
    not_tested_widget.js_on_change('value', x)

    return td

def Filter():
    ds = ColumnDataSource(df)

    # create the widgets to be used
    mc_widgets = {}
    dr_widgets = {}
    multi_choice = (lambda x,y: MultiChoice(options=x, value=[], title=y), 'value')
    start_date = (lambda x,y,z: DatePicker(min_date=x,max_date=y, value=x, title=z), 'value')
    today = datetime.date.today()
    today_plus_one = today + datetime.timedelta(days=1)
    end_date = (lambda x,y,z: DatePicker(min_date=x,max_date=y, value=today_plus_one, title=z), 'value')
    min_date = pd.Timestamp((min(ds.data['Real Dates']))).date()
    date_range = []
    while min_date <= today_plus_one:
        date_range.append(min_date)
        min_date += datetime.timedelta(days=1)
    # widget titles and data for those widgets has to be manually entered, as well as the type
    columns = ['Major Type', 'Sub Type', 'Full ID', 'Location', 'Start Date', 'End Date']
    data = [ds.data['Major Type'].tolist(), ds.data['Sub Type'], ds.data['Full ID'].tolist(), ds.data['Location'].tolist(), date_range, date_range]
    t = [multi_choice, multi_choice, multi_choice, multi_choice, start_date, end_date]

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
    all_widgets = {**mc_widgets}
    widgets = {k:w['widget'] for k,w in all_widgets.items()}

    test_names = np.unique(ds.data['Test Name'].tolist()).tolist()
    serial_numbers = np.unique(ds.data['Full ID'].tolist()).tolist()

    passed_widget = MultiChoice(options=test_names, value=[], title='Passed Test')
    failed_widget = MultiChoice(options=test_names, value=[], title='Failed Test')
    not_tested_widget = MultiChoice(options=test_names, value=[], title='Has not run Test')

    td = makeTable(ds, widgets, view, test_names, serial_numbers, passed_widget, failed_widget, not_tested_widget)
    
    # html template formatter can be used to apply typical html code to bokeh elements
    template = '''
<div style="font-size: 150%">
<%= value %>
</div> 
'''
    bigger_font = HTMLTemplateFormatter(template=template)

    module_template = '''
<div style="font-size: 150%">
<a href="module.py?full_id=<%= value %>"target="_blank">
<%= value %>
</a>
</div> 
'''
    board = HTMLTemplateFormatter(template=module_template)

    color_template = '''
<div style="font-size: 150%; background:<%=
    (function color() {
        if (value == 'Passed'){
            return('#d1e7dd')}
        else if (value == 'Failed'){
            return('#f8d7da')}
        else if (value == 'Not Run'){
            return('#d3d3d4')}
        }())%>;">
<%= value %>
</div> 
'''

    color_status = HTMLTemplateFormatter(template=color_template)

    table_columns = [
                    TableColumn(field='Sub Type', title='Sub Type', formatter=bigger_font),
                    TableColumn(field='Full ID', title='Full ID', formatter=board),
                    TableColumn(field='Location', title='Location', formatter=bigger_font),
                    ]

    test_columns = {}
    def_cols = [
                    TableColumn(field='Sub Type', title='Sub Type', formatter=bigger_font),
                    TableColumn(field='Full ID', title='Full ID', formatter=board),
                    TableColumn(field='Location', title='Location', formatter=bigger_font),
                    ]

    for name in test_names:
        col = TableColumn(field=name, title=name, formatter=color_status)
        table_columns.append(col)
        test_columns[name] = col

    data_table = DataTable(source=td, columns=table_columns, row_height = 40, autosize_mode='fit_columns', height=600, width=1900)

    show_columns = CustomJS(args=dict(table=data_table, test_names=test_names, LD_wagon_tests=LD_wagon_tests, HD_wagon_tests=HD_wagon_tests, zipper_tests=zipper_tests, test_columns=test_columns, def_cols=def_cols), code=('''
const visible_columns = [];
for (let i = 0; i < def_cols.length; i++) {
    visible_columns.push(def_cols[i])
}
if (this.value.length != 0) {
    for (let j = 0; j < this.value.length; j++) {
        if (this.value[j] == 'WW' || this.value[j] == 'WE'){
            for (let k = 0; k < LD_wagon_tests.length; k++){
                if (!(visible_columns.includes(test_columns[LD_wagon_tests[k]]))){
                    visible_columns.push(test_columns[LD_wagon_tests[k]])
                }
            }
        }
        if (this.value[j] == 'WH'){
            for (let k = 0; k < HD_wagon_tests.length; k++){
                if (!(visible_columns.includes(test_columns[HD_wagon_tests[k]]))){
                    visible_columns.push(test_columns[HD_wagon_tests[k]])
                }
            }
        }
        if (this.value[j] == 'ZP'){
            for (let k = 0; k < zipper_tests.length; k++){
                if (!(visible_columns.includes(test_columns[zipper_tests[k]]))){
                    visible_columns.push(test_columns[zipper_tests[k]])
                }
            }
        }
    }
} else {
    for (let i = 0; i < test_names.length; i++) {
        visible_columns.push(test_columns[test_names[i]])
    }
}
table.columns = visible_columns
'''))

    w = [*widgets.values()]
    w[0].js_on_change('value', show_columns)

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

    return json.dumps(json_item(row(column(row(w), row([passed_widget,failed_widget,not_tested_widget]), data_table))))

