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

def create_generic_hist(attachments1, title, stats):

    # Handles one value under graph_title in 'module 1'
    graph_title = title

    values = []
    for attachment in attachments1:
        values.append(attachment['module 1'][graph_title])


    
    # Temporary step value 
    step = 0.01

    num_of_bins = 15
    
    if not (max(values) - min(values)) == 0:
        step = round(max(values) - min(values)) / num_of_bins



    start = np.floor(min(values) / step) * step
    stop = max(values) + step
    bin_edges = np.arange(start, stop, step=step)


    plt.hist(values, bins=bin_edges, density=False, histtype='bar')
    plt.xlabel(graph_title + " Values")
    plt.ylabel('Occurances')
    plt.title(graph_title + " Values")
    plt.grid(True)
    plt.xticks(np.arange(start, stop, step = step), rotation = 90)

    plt.tight_layout()
    plt.savefig('../static/files/gen_res/{}.png'.format(graph_title))
    plt.close()



    print('<img src="../static/files/gen_res/{}.png" >'.format(graph_title))

    add_to_stats(stats, graph_title, values)

def create_sub_generic_hist(attachments1, title, list_index, stats):
    # Handles a list under graph_title in 'module 1'
    graph_title = title

    values = []
    for attachment in attachments1:
        values.append(attachment['module 1'][graph_title][list_index])

    # Temporary step value 
    step = 0.01

    num_of_bins = 15
    
    if not (max(values) - min(values)) == 0:
        step = round(max(values) - min(values)) / num_of_bins


    start = np.floor(min(values) / step) * step
    stop = max(values) + step
    bin_edges = np.arange(start, stop, step=step)


    plt.hist(values, bin_edges, density=False, histtype='bar', color='red')
    plt.xlabel(graph_title + " Values")
    plt.ylabel('Occurances')
    plt.title(graph_title + " Values")
    plt.grid(True)
    plt.xticks(np.arange(start, stop, step = step), rotation = 90)

    plt.tight_layout()
    plt.savefig('../static/files/gen_res/{}.png'.format(graph_title))
    plt.close()



    print('<img src="../static/files/gen_res/{}.png" >'.format(graph_title))


    add_to_stats(stats, graph_title, values)

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
attachments1 = add_test_functions.get_test_attachments(1)

stats = {'analytic_type': 'General Resistance Test'}

#######################################################

create_generic_hist(attachments1, 'RTD -> VMON_LVS', stats)

#######################################################

create_sub_generic_hist(attachments1, 'ECON_RE_Sb -> HGCROC_RE_Sb', 0, stats)

#######################################################

create_sub_generic_hist(attachments1, 'PWR_EN -> PG_LDO', 0, stats)

########################################################

create_generic_hist(attachments1, 'RTD -> HGCROC_RE_Sb', stats)

########################################################

create_sub_generic_hist(attachments1, 'HGCROC_RE_Hb -> HGCROC_RE_Sb', 0, stats)

########################################################

create_sub_generic_hist(attachments1, 'PG_DCDC -> ECON_RE_Hb', 0, stats)

########################################################

print(json.dumps(stats, indent = 4))

with open('../static/files/gen_res/gen_res_stats.json', 'w') as open_file:
    json.dump(stats, open_file, indent = 4)


# TODO Actually print out all of the graphs after matplotlib is installed
# Done in the generic and sub_generic functions




base.bottom()


