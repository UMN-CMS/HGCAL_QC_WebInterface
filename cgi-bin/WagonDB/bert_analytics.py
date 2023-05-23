#!/usr/bin/python3


import os, sys
import cgi
import cgitb
import pylab
import json

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

import base
import add_test_functions

def create_generic_hist(attachments1, title, number_val, stats):

    # Handles one value under graph_title in 'module 1'
    graph_title = title

    values = []
    for attachment in attachments1:
        if not attachment[str(number_val)] == None:
            if not attachment[str(number_val)][graph_title] == None:
                values.append(attachment[str(number_val)][graph_title])


    # if no values, can't make graph, so return
    if len(values) == 0:
        return


    step = 10
    num_of_bins = 15
    
    if not (max(values) - min(values)) == 0:
        step = round(max(values) - min(values)) / num_of_bins
    

    start = np.floor(min(values) / step) * step
    stop = max(values) + step
    bin_edges = np.arange(start, stop, step=step)


    plt.hist(values, bins=bin_edges, density=False, histtype='bar')
    plt.xlabel(graph_title + " Values")
    plt.ylabel('Occurances')
    full_title = graph_title + " " + str(number_val) + " Values"
    plt.title(full_title)
    plt.grid(True)
    plt.xticks(np.arange(start, stop, step = step), rotation = 90)

    plt.tight_layout()

    plt.savefig('../static/files/bert/{0}_{1}.png'.format(graph_title, number_val))
    plt.close()


    print('<img src="../static/files/bert/{0}_{1}.png" >'.format(graph_title, number_val))


    add_to_stats(stats, full_title, values)

# Adds statistics to the "stats" python dictionary
def add_to_stats(stats, full_title, values):
    mean = sum(values) / len(values)
    stand_deviation = np.std(values)

    stats['{}'.format(full_title)] = {
            'STD': stand_deviation,
            'range': max(values) - min(values),
            'mean': mean,
            'max': max(values),
            'min': min(values),
            'passing_range': ( mean - stand_deviation, mean + stand_deviation )
            }


#############End of Functions##########################



cgitb.enable()

# chose a non-GUI backend
# matplotlib.use( 'Agg' )
print("Content-type: text/html\n")

base.header(title='Analytics')
base.top()


form = cgi.FieldStorage()

# Gets the attachment from the DB
attachments4 = add_test_functions.get_test_attachments(4)
stats = {'analytic_type': "Bit Error Rate Test"}

########################################################

for index in range(1, 11):
    create_generic_hist(attachments4, 'Midpoint', index, stats)
    create_generic_hist(attachments4, 'Eye Opening', index, stats)

########################################################

print(json.dumps(stats, indent = 4))

with open('../static/files/bert/bert_stats.json', 'w') as open_file:
    json.dump(stats, open_file, indent = 4)

# TODO Actually print out all of the graphs after matplotlib is installed
# Done in the generic and sub_generic functions




base.bottom()

