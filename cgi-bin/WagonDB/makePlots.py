#!/usr/bin/python3

import pandas as pd
import matplotlib.pyplot as plt
import csv
import cgitb
import numpy as np
import datetime
import matplotlib.dates as mdates
from matplotlib.axis import Axis

cgitb.enable()

def makePlot(Test, Data, Board, SN, BitError, Tester):
    TestData = pd.read_csv('./static/files/Test.csv', parse_dates=['Time'])
    BoardData = pd.read_csv('./static/files/Board.csv')
    PeopleData = pd.read_csv('./static/files/People.csv')
    name = None

    if SN is not None:
        board_temp = BoardData.query('`Full ID` == @SN')['Board ID']
        Board_ID = board_temp.values.tolist()
        if Tester is not None:
            person_temp = PeopleData.query('`Person Name` == @Tester')['Person ID']
            person_id = person_temp.values.tolist()
            tests_temp = TestData.query('`Board ID` == @Board_ID & `Person ID` == @person_id')['Test ID']
            for i in Tester:  
                if i is Tester[0]:
                    name = ' for ' + i
                else:
                    name += i
                if i is not Tester[-1]:
                    name += ', '
        else:
            tests_temp = TestData.query('`Board ID` == @Board_ID')['Test ID']
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
        board_temp = BoardData.query('`Type ID` == @Board')['Board ID']
        board_ids = board_temp.values.tolist()
        if Tester is not None:
            person_temp = PeopleData.query('`Person Name` == @Tester')['Person ID']
            person_id = person_temp.values.tolist()
            tests_temp = TestData.query('`Board ID` == @board_ids & `Person ID` == @person_id')['Test ID']
            for i in Tester:  
                if i is Tester[0]:
                    name = ' for ' + i
                else:
                    name += i
                if i is not Tester[-1]:
                    name += ', '
        else:
            tests_temp = TestData.query('`Board ID` == @board_ids')['Test ID']

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
        tests_temp = TestData.iloc[:, 0]
        
    if Board is None and SN is None and Tester is not None:
        person_temp = PeopleData.query('`Person Name` == @Tester')['Person ID']
        person_id = person_temp.values.tolist()
        tests_temp = TestData.query('`Person ID` == @person_id')['Test ID']
        for i in Tester:
            if i is Tester[0]:
                name = ' for ' + i
            else:
                name += i
            if i is not Tester[-1]:
                name += ', '

    tests = tests_temp.values.tolist()

    if name is not None and Test is not None:
        title = Test + name
    else:
        title = Test

    if Test is None:
        dates = TestData.query('`Test ID` == @tests')['Time']
        successful_dates = TestData.query('`Test ID` == @tests & Successful == 1')['Time']
        time_series_data = []
        time_series_data_successful = []
        first = datetime.datetime(2023, 3, 1, 0, 0, 0)

        while (first <= datetime.datetime.now()):
            i = 0
            j = 0
            for d in dates:
                if d > first:
                    break
                else:
                    i += 1
            for d in successful_dates:
                if d > first:
                    break
                else:
                    j += 1
            time_series_data.append([first,i])
            time_series_data_successful.append([first,j])
            first += datetime.timedelta(days=1)
        x1,y1 = zip(*time_series_data)
        x2,y2 = zip(*time_series_data_successful)
        
        if name is not None:
            title = 'Total Tests Over Time' + name
        else:
            title = 'Total Tests Over Time'

        fig, ax = plt.subplots()
        plt.plot(x1, y1, label = 'Total')
        plt.plot(x2, y2, label = 'Successful')
        plt.title(title)
        plt.xlabel('Date')
        plt.ylabel('Number of Tests')
        plt.legend()
        Axis.set_major_locator(ax.xaxis,mdates.MonthLocator(interval=1))
        plt.gcf().autofmt_xdate()
        plt.savefig('../../static/files/TestsOverTime.png')
        plt.clf()


    if Test == 'Resistance Measurement':
        df = pd.read_csv('./static/files/Resistance_Measurement.csv')
        w = 0.25
        temp_max = 0
        useData = df.query('`Test ID` == @tests')

        for i in range(len(Data)):
            if Data[i] == True:
                plot_data = useData.iloc[:, i+1]
                plt.hist(plot_data, bins=np.arange(min(plot_data), max(plot_data) + w, w), label = useData.columns[i+1])
                temp_max = max(plot_data) if max(plot_data) > temp_max else temp_max

        plt.title(title)
        plt.legend(fontsize='xx-small')
        plt.xlabel('Resistance')
        plt.xlim([0, temp_max*1.5])
        plt.ylabel('Number of Boards')
        plt.savefig('../../static/files/Resistance_Measurement.png')

    if Test == 'ID Resistor':
        df = pd.read_csv('./static/files/ID_Resistor_Test_Data.csv')
        useData = df.query('`Test ID` == @tests')

        plt.hist(useData.iloc[:,1])
        plt.title(title)
        plt.xlabel('Resistance')
        plt.ylabel('Number of Boards')
        plt.savefig('../../static/files/ID_Resistor.png')

    if Test == 'I2C Read/Write':
        df = pd.read_csv('./static/files/I2C_ReadWrite_Test_Data.csv')
        w = 1000
        useData = df.query('`Test ID` == @tests')

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
        df = notData.query('`Test ID` == @tests')

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
            plt.xlabel('DAQ Delay')
            plt.ylabel('Number of Boards')
            plt.legend()
            ax = plt.gca()
            plt.text(0.02, 0.95, r'$\sigma=%.2f$' % (std, ), transform = ax.transAxes)
            plt.savefig('../../static/files/Bit_Error_Rate_EyeOpening')
            

makePlot('Bit Error Rate', [True,True,True], None, None, [True,True,False,False,False,True,False,False,False,False,False], ['Bryan'])
