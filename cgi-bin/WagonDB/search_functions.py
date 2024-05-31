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


TestData = pd.read_csv('./static/files/Test.csv', parse_dates=['Time'])
BoardData = pd.read_csv('./static/files/Board.csv')
PeopleData = pd.read_csv('./static/files/People.csv')
TestTypeData = pd.read_csv('./static/files/Test_Types.csv')
TestTypeData = TestTypeData.rename(columns={'Name':'Test Name'})
mergetemp = TestData.merge(BoardData, on='Board ID', how='left')
AllData = mergetemp.merge(PeopleData, on='Person ID', how='left')
AllData = AllData.rename(columns={'Successful':'Outcome'})
AllData['Outcome'] = AllData['Outcome'].replace(0, 'Unsuccessful')
AllData['Outcome'] = AllData['Outcome'].replace(1, 'Successful')
AllData = AllData.merge(TestTypeData, on='Test Type ID', how='left')
AttachData = pd.read_csv('./static/files/Attachments.csv')
AllData = AllData.merge(AttachData, on='Test ID', how='left')
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

def makeTable(ds, widgets, view):
    td = ColumnDataSource({'Type ID':[], 'Full ID':[], 'Person Name':[], 'Test Type':[], 'Date':[], 'Outcome':[], 'Raw Time':[], 'Location':[], 'Color':[], 'Attachment':[]})

    x = CustomJS(args=dict(td=td, data=ds, view=view),code='''
const type_ids=[];
const full_ids=[];
const people=[];
const tests=[];
const times=[];
const outcomes=[];
const raw_time=[];
const locations=[];
const colors=[];
const attachments=[];

const indices = view.filters[0].compute_indices(data);
let mask = new Array(data.data['Full ID'].length).fill(false);
[...indices].forEach((x)=>{mask[x] = true;})
for (let j = 0; j < data.get_length(); j++) {
    if (mask[j] == true){
        type_ids.push(data.data['Type ID'][j])
        full_ids.push(data.data['Full ID'][j])
        people.push(data.data['Person Name'][j])
        tests.push(data.data['Test Name'][j])
    
        // converts date to a readable format
        let temp_date = new Date(data.data['Time'][j]);
        let date = temp_date.toString().slice(4, 24)
        times.push(date)
        raw_time.push(temp_date.valueOf())

        outcomes.push(data.data['Outcome'][j])
        locations.push(data.data['Location'][j])
        colors.push(data.data['Color'][j])
        attachments.push(data.data['Attach ID'][j])
    }
}
td.data['Type ID'] = type_ids;
td.data['Full ID'] = full_ids;
td.data['Person Name'] = people;
td.data['Test Type'] = tests;
td.data['Date'] = times;
td.data['Outcome'] = outcomes;
td.data['Raw Time'] = raw_time;
td.data['Location'] = locations;
td.data['Color'] = colors;
td.data['Attachment'] = attachments;
td.change.emit()
''')

    for widget in widgets.values():
        widget.js_on_change('value', x)

    return td

def Filter():
    ds = ColumnDataSource(AllData)

    # create the widgets to be used
    mc_widgets = {}
    dr_widgets = {}
    multi_choice = (lambda x,y: MultiChoice(options=x, value=[], title=y), 'value')
    start_date = (lambda x,y,z: DatePicker(min_date=x,max_date=y, value=x, title=z), 'value')
    today = datetime.date.today()
    end_date = (lambda x,y,z: DatePicker(min_date=x,max_date=y, value=today, title=z), 'value')
    min_date = pd.Timestamp((min(ds.data['Time']))).date()
    date_range = []
    while min_date <= today:
        date_range.append(min_date)
        min_date += datetime.timedelta(days=1)
    # widget titles and data for those widgets has to be manually entered, as well as the type
    columns = ['Type ID', 'Full ID', 'Test Name', 'Location', 'Color', 'Person Name', 'Outcome', 'Start Date', 'End Date']
    data = [ds.data['Type ID'].tolist(), ds.data['Full ID'].tolist(), ds.data['Test Name'].tolist(), ds.data['Location'].tolist(), ds.data['Color'].tolist(), ds.data['Person Name'].tolist(), ds.data['Outcome'], date_range, date_range]
    t = [multi_choice, multi_choice, multi_choice, multi_choice, multi_choice, multi_choice, multi_choice, start_date, end_date]

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
    all_widgets = {**mc_widgets, **dr_widgets}
    widgets = {k:w['widget'] for k,w in all_widgets.items()}

    td = makeTable(ds, widgets, view)
    
    # html template formatter can be used to apply typical html code to bokeh elements
    template = '''
<div style="font-size: 150%">
<%= value %>
</div> 
'''
    bigger_font = HTMLTemplateFormatter(template=template)

    link_template = '''
<div style="font-size: 150%">
<a href="get_attach.py?attach_id=<%= value %>"target="_blank">
Attach
</a>
</div> 
'''
    link = HTMLTemplateFormatter(template=link_template)

    table_columns = [
                    TableColumn(field='Type ID', title='Type ID', formatter=bigger_font),
                    TableColumn(field='Full ID', title='Full ID', formatter=bigger_font),
                    TableColumn(field='Test Type', title='Test Type', formatter=bigger_font),
                    TableColumn(field='Person Name', title='Person Name', formatter=bigger_font),
                    TableColumn(field='Date', title='Time', formatter=bigger_font),
                    TableColumn(field='Raw Time', title='Raw Time', formatter=bigger_font),
                    TableColumn(field='Location', title='Location', formatter=bigger_font),
                    TableColumn(field='Outcome', title='Outcome', formatter=bigger_font),
                    TableColumn(field='Color', title='Color', formatter=bigger_font),
                    TableColumn(field='Attachment', title='Attachment', formatter=link),
                    ]

    data_table = DataTable(source=td, columns=table_columns, row_height = 40, autosize_mode='fit_columns', width_policy = 'fit', height=600)

    w = [*widgets.values()]
    subtypes = np.unique(ds.data['Type ID'].tolist()).tolist()
    serial_numbers = {}
    for s in subtypes:
        serial_numbers[s] = np.unique(AllData.query('`Type ID` == @s')['Full ID'].values.tolist()).tolist()
    update_options = CustomJS(args=dict(serial_numbers=serial_numbers, widget=w[1]), code=('''
widget.options = serial_numbers[this.value]
'''))
    w[0].js_on_change('value', update_options)

    return json.dumps(json_item(row(column(row(w[0:5]), row(w[5:]), data_table))))

