#!/usr/bin/python3

import datetime
import os, sys
import cgi
import cgitb
import pylab
### Begin Comment Out For Server ###
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
### End Comment Out For Server ###
import base
import add_test_functions

cgitb.enable()

# chose a non-GUI backend
# matplotlib.use( 'Agg' )
print("Content-type: text/html\n")

base.header(title='Analytics')
base.top()


form = cgi.FieldStorage()


#######################################################


total_tests_w_times = add_test_functions.get_test_completion_times()
successful_tests_w_times = add_test_functions.get_successful_times()
new_date_time = []

oldest_day = datetime.datetime(year = total_tests_w_times[0][0].year, month = total_tests_w_times[0][0].month, day = total_tests_w_times[0][0].day)
newest_day = datetime.datetime(year = total_tests_w_times[-1][0].year, month = total_tests_w_times[-1][0].month, day = total_tests_w_times[-1][0].day)

# Split the boards by timeframes
tests_in_intervals = []
successful_in_intervals = []



########## For Total Tests ##########
# Find the range of days (newest_day - oldest_day)
day_range = (total_tests_w_times[-1][0] - oldest_day).days + 1


# List of the difference in days from first test until current test for each test
diff_in_days_vals = []
for item in total_tests_w_times:
    diff_in_days_vals.append((item[0]-oldest_day).days)

########## For Total Tests ##########




########## For Successful Tests ##########

# List of the difference in days from first test until current test for each test
diff_in_days_vals_success = []
for item in successful_tests_w_times:
    diff_in_days_vals_success.append((item[0]-oldest_day).days)

########## For Successful Tests ##########

########## Creating Bins ##########

bin_list = []
temp_month = oldest_day.month
temp_day = oldest_day.day
temp_year = oldest_day.year
datetime_diff = newest_day - oldest_day
day_diff = int(datetime_diff / datetime.timedelta(days = 1))
for index in range(day_diff + 1):
    try:
        bin_time_str = "{Month}-{Day}-{Year}".format(Year = temp_year, Month = temp_month, Day = temp_day)
        temp_bin_time = datetime.datetime.strptime(bin_time_str, '%m-%d-%Y')
        bin_list.append(bin_time_str)
    except:
        if temp_month >= 12:
            temp_month = 1
            temp_year += 1
            temp_day = 1
        else:
            temp_month += 1
            temp_day = 1
        bin_time_str = "{Month}-{Day}-{Year}".format(Year = temp_year, Month = temp_month, Day = temp_day)
        bin_list.append(bin_time_str)
    temp_day += 1
print(bin_list)

########## Creating Bins ##########
hist_list = []
hist_list.append(diff_in_days_vals)
hist_list.append(diff_in_days_vals_success)

#TODO more elegant
num_bins = day_range
bin_edge_list = []
for i in range(num_bins+1):
    bin_edge_list.append(i)

# Consider finding a different way to establish bins so dates are on the x-axis.
print("HIST", hist_list, "NUM", num_bins, "LEN", len(bin_list))
plt.hist(hist_list, bin_edge_list, density=False, histtype='bar', label=['Tests Completed', 'Tests Successful'])
plt.legend(prop={'size': 12})
plt.title("Completed Tests vs. Successful Tests per Day")
plt.xlabel('Date')
plt.xticks(np.arange(0.5,len(bin_list)+0.5, 1), labels = bin_list)
plt.xlim(0,len(bin_list))
plt.ylabel("Number of Tests")
plt.grid(True)
#plt.show()
plt.savefig('../static/files/completed_vs_successful.png')

#######################################################
plt.close()
#######################################################


# Fetches a list of datetime objects
test_times_datetime = add_test_functions.get_test_completion_times()

# Find the range of days (newest_day - oldest_day)
num_days = (test_times_datetime[-1][0] - oldest_day).days + 1

# List of the difference in days from first test until current test for each test
day_vals = []
for item in test_times_datetime:
    day_vals.append((item[0]-oldest_day).days)

# Creates a list of the number of tests completed by a certain date
total_completed_by_time = [] 
for i in range(0,num_days):
    temp = 0
    for val in day_vals:
        # Increases the number of completed tests if the difference in days is less than the day (number) associated with the respective bin
        if val <= i:
            temp = temp + 1
    # Appends the value of the number of tests completed to the list
    total_completed_by_time.append(temp)

print("TOTAL_Completed", total_completed_by_time)
plt.plot(total_completed_by_time)
plt.title("Total Number of Completed Tests vs. Time")
plt.xlabel('Date')
locs, labels = plt.xticks()
plt.xticks(np.arange(0,len(bin_list), 1), labels = bin_list)
plt.grid(True)
plt.ylabel('Total Tests Completed')

plt.savefig('../static/files/completed_over_time.png')



########################################################


print('<img src="../static/files/completed_vs_successful.png" style="float-right">')

print('<img src="../static/files/completed_over_time.png" style="float-right">')




base.bottom()








