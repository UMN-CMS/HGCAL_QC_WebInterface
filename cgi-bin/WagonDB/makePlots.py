#!/usr/bin/python3

import sys
import pandas as pd
import matplotlib.pyplot as plt
import csv
import cgitb
import numpy as np
from datetime import datetime as dt
import datetime
import matplotlib.dates as mdates
from matplotlib.axis import Axis

cgitb.enable()

def makePlot(Test, Data, Board, SN, BitError, Tester, Outcome, StartDate, EndDate):
    TestDataTemp = pd.read_csv('./static/files/Test.csv', parse_dates=['Time'])
    BoardData = pd.read_csv('./static/files/Board.csv')
    PeopleData = pd.read_csv('./static/files/People.csv')
    name = None

    if StartDate is None:
        StartDate = dt.strptime('03/14/23 00:00:00', '%m/%d/%y %H:%M:%S')
    else:
        StartDate = dt.strptime(StartDate, '%m/%d/%y %H:%M:%S')
    if EndDate is None:
        EndDate = dt.combine(datetime.date.today(), datetime.time(23,59,59))
    else:
        EndDate = dt.strptime(EndDate, '%m/%d/%y %H:%M:%S')

    TestData = TestDataTemp.query('Time >= @StartDate and Time <= @EndDate')
                    
    if SN is not None:
        Board_ID = BoardData.query('`Full ID` == @SN')['Board ID'].values.tolist()
        if Tester is not None:
            person_id = PeopleData.query('`Person Name` == @Tester')['Person ID'].values.tolist()
            tests_temp = TestData.query('`Board ID` == @Board_ID & `Person ID` == @person_id')
            for i in Tester:
                if i is Tester[0]:
                    name = ' for ' + i
                else:
                    name += i
                if i is not Tester[-1]:
                    name += ', '
        else:
            tests_temp = TestData.query('`Board ID` == @Board_ID')
        for i in SN:
            if name is not None:
                if i is SN[0]:
                    name += ' for ' + i
                else:
                    name += i
                if i is not SN[-1]:
                    name += ', '
            else:
                if i is SN[0]:
                    name = ' for ' + i
                else:
                    name += i
                if i is not SN[-1]:
                    name += ', '
    elif Board is not None:
        board_ids = BoardData.query('`Type ID` == @Board')['Board ID'].values.tolist()
        if Tester is not None:
            person_id = PeopleData.query('`Person Name` == @Tester')['Person ID'].values.tolist()
            tests_temp = TestData.query('`Board ID` == @board_ids & `Person ID` == @person_id')
            for i in Tester:  
                if i is Tester[0]:
                    name = ' for ' + i
                else:
                    name += i
                if i is not Tester[-1]:
                    name += ', '
        else:
            tests_temp = TestData.query('`Board ID` == @board_ids')

        for i in Board:
            if name is not None:
                if i is Board[0]:
                    name += ' for ' + i
                else:
                    name += i
                if i is not Board[-1]:
                    name += ', '
            else:
                if i is Board[0]:
                    name = ' for ' + i
                else:
                    name += i
                if i is not Board[-1]:
                    name += ', '
    else:
        tests_temp = TestData
        
    if Board is None and SN is None and Tester is not None:
        person_id = PeopleData.query('`Person Name` == @Tester')['Person ID'].values.tolist()
        tests_temp = TestData.query('`Person ID` == @person_id')
        for i in Tester:
            if i is Tester[0]:
                name = ' for ' + i
            else:
                name += i
            if i is not Tester[-1]:
                name += ', '

    total_tests = tests_temp.iloc[:,0].values.tolist()
    successful_tests = tests_temp.query('Successful == 1')['Test ID'].values.tolist()
    unsuccessful_tests = tests_temp.query('Successful == 0')['Test ID'].values.tolist()

    if name is not None and Test is not None:
        title = Test + name
    else:
        title = Test

    if Test is 'Total':
        fig, ax = plt.subplots()
        if Outcome[0] == True:
            first = StartDate
            dates = TestData.query('`Test ID` == @total_tests')['Time']
            time_series_data = []
            i = 0
            while (first <= EndDate):
                for d in dates:
                    if d > first and d < first+datetime.timedelta(days=1):
                        i += 1
                time_series_data.append([first,i])
                first += datetime.timedelta(days=1)
            x1,y1 = zip(*time_series_data)
            plt.plot(x1, y1, label = 'Total')
        if Outcome[1] == True:
            first = StartDate
            successful_dates = TestData.query('`Test ID` == @successful_tests')['Time']
            time_series_data_successful = []
            j = 0
            while (first <= EndDate):
                for d in successful_dates:
                    if d > first and d < first+datetime.timedelta(days=1):
                        j += 1
                time_series_data_successful.append([first,j])
                first += datetime.timedelta(days=1)
            x2,y2 = zip(*time_series_data_successful)
            plt.plot(x2, y2, label = 'Successful')
        if Outcome[2] == True:
            first = StartDate
            unsuccessful_dates = TestData.query('`Test ID` == @unsuccessful_tests')['Time']  
            time_series_data_unsuccessful = []
            k = 0
            while (first <= EndDate):
                for d in unsuccessful_dates:
                    if d > first and d < first+datetime.timedelta(days=1):
                        k += 1
                time_series_data_unsuccessful.append([first,k])
                first += datetime.timedelta(days=1)
            x3,y3 = zip(*time_series_data_unsuccessful)
            plt.plot(x3, y3, label = 'Unsuccessful')

        
        if name is not None:
            title = 'Total Tests Over Time' + name
        else:
            title = 'Total Tests Over Time'

        plt.title(title)
        plt.xlabel('Date')
        plt.ylabel('Number of Tests')
        plt.legend()
        #Axis.set_major_locator(ax.xaxis,mdates.MonthLocator(interval=1))
        plt.gcf().autofmt_xdate()
        plt.savefig('../../static/files/TestsOverTime.png')

    if Test == 'Compare Testers':
        for i in Tester:
            person_id = PeopleData.query('`Person Name` == @i')['Person ID'].values.tolist()
            plot_data = TestData.query('`Person ID` == @person_id')['Test ID'].values.tolist()
            plt.bar(i, len(plot_data))
        plt.title(title)
        plt.xlabel('Tester Name')
        plt.ylabel('Number of Tests Performed')
        plt.savefig('../../static/files/CompareTesters.png')

    if Test == 'Resistance Measurement':
        df = pd.read_csv('./static/files/Resistance_Measurement.csv')
        w = 0.25
        temp_max = 0

        if Outcome[1] == True:
            if Outcome[2] == True:
                useData = df.query('`Test ID` == @total_tests')
            else: 
                useData = df.query('`Test ID` == @successful_tests')
        else:
            if Outcome[2] == True:
                useData = df.query('`Test ID` == @unsuccessful_tests')
            else:
                useData = df.query('`Test ID` == @total_tests')

        for i in range(len(Data)):
            if Data[i] == True:
                plot_data = useData.iloc[:, i+1]
                plt.hist(plot_data, bins=np.arange(min(plot_data), max(plot_data) + w, w), label = useData.columns[i+1])
                temp_max = max(plot_data) if max(plot_data) > temp_max else temp_max

        plt.title(title)
        plt.legend(fontsize='xx-small')
        plt.xlabel('Resistance')
        plt.xlim([0, temp_max*1.8])
        plt.ylabel('Number of Boards')
        plt.savefig('../../static/files/Resistance_Measurement.png')

    if Test == 'ID Resistor':
        df = pd.read_csv('./static/files/ID_Resistor_Test_Data.csv')

        if Outcome[1] == True:
            if Outcome[2] == True:
                useData = df.query('`Test ID` == @total_tests')
            else: 
                useData = df.query('`Test ID` == @successful_tests')
        else:
            if Outcome[2] == True:
                useData = df.query('`Test ID` == @unsuccessful_tests')
            else:
                useData = df.query('`Test ID` == @total_tests')

        plt.hist(useData.iloc[:,1])
        plt.title(title)
        plt.xlabel('Resistance')
        plt.ylabel('Number of Boards')
        plt.savefig('../../static/files/ID_Resistor.png')

    if Test == 'I2C Read/Write':
        df = pd.read_csv('./static/files/I2C_ReadWrite_Test_Data.csv')
        w = 1000

        if Outcome[1] == True:
            if Outcome[2] == True:
                useData = df.query('`Test ID` == @total_tests')
            else: 
                useData = df.query('`Test ID` == @successful_tests')
        else:
            if Outcome[2] == True:
                useData = df.query('`Test ID` == @unsuccessful_tests')
            else:
                useData = df.query('`Test ID` == @total_tests')

        for i in range(len(Data)):
            if Data[i] == True:
                plot_data = useData.iloc[:, i+1]
                plt.hist(plot_data, bins=np.arange(-1, 11000, 1000), label = useData.columns[i+1], stacked=True)

        plt.title(title)
        plt.legend(fontsize='xx-small')
        plt.xlabel('Number of Checks')
        plt.ylabel('Number of Boards')
        plt.savefig('../../static/files/I2C_ReadWrite.png')

    if Test == 'Bit Error Rate':
        notData = pd.read_csv('./static/files/Bit_Error_Rate_Test_Data.csv')

        if Outcome[1] == True:
            if Outcome[2] == True:
                df = notData.query('`Test ID` == @total_tests')
            else: 
                df = notData.query('`Test ID` == @successful_tests')
        else:
            if Outcome[2] == True:
                df = notData.query('`Test ID` == @unsuccessful_tests')
            else:
                df = notData.query('`Test ID` == @total_tests')

        if Data[0] == True:
            w = 5
            if BitError[0] == True:
                CLK0 = df.query('`E Link` == "CLK0"')['Midpoint'] 
                plt.hist(CLK0, label = 'CLK0', bins=np.arange(0,400+w,w), stacked=True)
            if BitError[1] == True:
                CLK1 = df.query('`E Link` == "CLK1"')['Midpoint']
                plt.hist(CLK1, label = 'CLK1', bins=np.arange(0,400+w,w), stacked=True)
            if BitError[2] == True:
                CLK2 = df.query('`E Link` == "CLK2"')['Midpoint']
                plt.hist(CLK2, label = 'CLK2', bins=np.arange(0,400+w,w), stacked=True)
            if BitError[3] == True:
                TRIG0 = df.query('`E Link` == "TRIG0"')['Midpoint']
                plt.hist(TRIG0, label = 'TRIG0', bins=np.arange(0,400+w,w), stacked=True)
            if BitError[4] == True:
                TRIG1 = df.query('`E Link` == "TRIG1"')['Midpoint']
                plt.hist(TRIG1, label = 'TRIG1', bins=np.arange(0,400+w,w), stacked=True)
            if BitError[5] == True:
                TRIG2 = df.query('`E Link` == "TRIG2"')['Midpoint']
                plt.hist(TRIG2, label = 'TRIG2', bins=np.arange(0,400+w,w), stacked=True)
            if BitError[6] == True:
                TRIG3 = df.query('`E Link` == "TRIG3"')['Midpoint']
                plt.hist(TRIG3, label = 'TRIG3', bins=np.arange(0,400+w,w), stacked=True)
            if BitError[7] == True:
                TRIG4 = df.query('`E Link` == "TRIG4"')['Midpoint']
                plt.hist(TRIG4, label = 'TRIG4', bins=np.arange(0,400+w,w), stacked=True)
            if BitError[8] == True:
                TRIG5 = df.query('`E Link` == "TRIG5"')['Midpoint']
                plt.hist(TRIG5, label = 'TRIG5', bins=np.arange(0,400+w,w), stacked=True)
            if BitError[9] == True:
                TRIG6 = df.query('`E Link` == "TRIG6"')['Midpoint']
                plt.hist(TRIG6, label = 'TRIG6', bins=np.arange(0,400+w,w), stacked=True)
            if BitError[10] == True:
                TRIG7 = df.query('`E Link` == "TRIG7"')['Midpoint']
                plt.hist(TRIG7, label = 'TRIG7', bins=np.arange(0,400+w,w), stacked=True)

            plt.title(title + ': Midpoint')
            plt.xlabel('DAQ Delay')
            plt.ylabel('Number of Boards')
            plt.legend()
            plt.savefig('../../static/files/Bit_Error_Rate_Midpoint')
        
        if Data[1] == True:
            w = 5 
            plt.clf()
            if BitError[0] == True:
                CLK0 = df.query('`E Link` == "CLK0"')['Eye Opening'] 
                plt.hist(CLK0, label = 'CLK0', bins=np.arange(0,450+w,w), stacked=True)
                CLK0 = CLK0.values.tolist()
            else:
                CLK0 = []
            if BitError[1] == True:
                CLK1 = df.query('`E Link` == "CLK1"')['Eye Opening'] 
                plt.hist(CLK1, label = 'CLK1', bins=np.arange(0,450+w,w), stacked=True)
                CLK1 = CLK1.values.tolist()
            else:
                CLK1 = []
            if BitError[2] == True:
                CLK2 = df.query('`E Link` == "CLK2"')['Eye Opening'] 
                plt.hist(CLK2, label = 'CLK2', bins=np.arange(0,450+w,w), stacked=True)
                CLK2 = CLK2.values.tolist()
            else:
                CLK2 = []
            if BitError[3] == True:
                TRIG0 = df.query('`E Link` == "TRIG0"')['Eye Opening'] 
                plt.hist(TRIG0, label = 'TRIG0', bins=np.arange(0,450+w,w), stacked=True)
                TRIG0 = TRIG0.values.tolist()
            else:
                TRIG0 = []
            if BitError[4] == True:
                TRIG1 = df.query('`E Link` == "TRIG1"')['Eye Opening'] 
                plt.hist(TRIG1, label = 'TRIG1', bins=np.arange(0,450+w,w), stacked=True)
                TRIG1 = TRIG1.values.tolist()
            else:    
                TRIG1 = []
            if BitError[5] == True:
                TRIG2 = df.query('`E Link` == "TRIG2"')['Eye Opening'] 
                plt.hist(TRIG2, label = 'TRIG2', bins=np.arange(0,450+w,w), stacked=True)
                TRIG2 = TRIG2.values.tolist()
            else:
                TRIG2 = []
            if BitError[6] == True:
                TRIG3 = df.query('`E Link` == "TRIG3"')['Eye Opening'] 
                plt.hist(TRIG3, label = 'TRIG3', bins=np.arange(0,450+w,w), stacked=True)
                TRIG3 = TRIG3.values.tolist()
            else:
                TRIG3 = []
            if BitError[7] == True:
                TRIG4 = df.query('`E Link` == "TRIG4"')['Eye Opening'] 
                plt.hist(TRIG4, label = 'TRIG4', bins=np.arange(0,450+w,w), stacked=True)
                TRIG4 = TRIG4.values.tolist()
            else:
                TRIG4 = []
            if BitError[8] == True:
                TRIG5 = df.query('`E Link` == "TRIG5"')['Eye Opening'] 
                plt.hist(TRIG5, label = 'TRIG5', bins=np.arange(0,450+w,w), stacked=True)
                TRIG5 = TRIG5.values.tolist()
            else:
                TRIG5 = []
            if BitError[9] == True:
                TRIG6 = df.query('`E Link` == "TRIG6"')['Eye Opening'] 
                plt.hist(TRIG6, label = 'TRIG6', bins=np.arange(0,450+w,w), stacked=True)
                TRIG6 = TRIG6.values.tolist()
            else:
                TRIG6 = []
            if BitError[10] == True:
                TRIG7 = df.query('`E Link` == "TRIG7"')['Eye Opening'] 
                plt.hist(TRIG7, label = 'TRIG7', bins=np.arange(0,450+w,w), stacked=True)
                TRIG7 = TRIG7.values.tolist()
            else:
                TRIG7 = []

            total_data = CLK0+CLK1+CLK2+TRIG0+TRIG1+TRIG2+TRIG3+TRIG4+TRIG5+TRIG6+TRIG7
            std = np.std(total_data)
            plt.title(title + ': Eye Opening')
            plt.xlabel('Eye Opening Width')
            plt.ylabel('Number of Boards')
            plt.legend()
            ax = plt.gca()
            plt.text(0.02, 0.95, r'$\sigma=%.2f$' % (std, ), transform = ax.transAxes)
            plt.savefig('../../static/files/Bit_Error_Rate_EyeOpening')
            
makePlot('Compare Testers', [True,True,True], None, None, [True,True,False,True,False,False,False,False,False,False,False], ['Bryan', 'Jocelyn'], [True, True, True], '6/1/23 00:00:00', None)
