#! /usr/bin/env python
############################################################
# Program is part of PyGPS v2.0                            #
# Copyright(c) 2017-2019, Yunmeng Cao                      #
# Author:  Yunmeng Cao                                     #
############################################################


import numpy as np
import getopt
import sys
import os
import h5py
import argparse
import math
import astropy.time
import dateutil.parser
import glob


def print_progress(iteration, total, prefix='calculating:', suffix='complete', decimals=1, barLength=50, elapsed_time=None):
    """Print iterations progress - Greenstick from Stack Overflow
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : number of decimals in percent complete (Int) 
        barLength   - Optional  : character length of bar (Int) 
        elapsed_time- Optional  : elapsed time in seconds (Int/Float)
    
    Reference: http://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console
    """
    filledLength    = int(round(barLength * iteration / float(total)))
    percents        = round(100.00 * (iteration / float(total)), decimals)
    bar             = '#' * filledLength + '-' * (barLength - filledLength)
    if elapsed_time:
        sys.stdout.write('%s [%s] %s%s    %s    %s secs\r' % (prefix, bar, percents, '%', suffix, int(elapsed_time)))
    else:
        sys.stdout.write('%s [%s] %s%s    %s\r' % (prefix, bar, percents, '%', suffix))
    sys.stdout.flush()
    if iteration == total:
        print("\n")

    '''
    Sample Useage:
    for i in range(len(dateList)):
        print_progress(i+1,len(dateList))
    '''
    return


def float_yyyymmdd(DATESTR):
    year = float(DATESTR.split('-')[0])
    month = float(DATESTR.split('-')[1])
    day = float(DATESTR.split('-')[2])
    
    date = year + month/12 + day/365 
    return date

def rm(FILE):
    call_str = 'rm ' + FILE
    os.system(call_str)

def add_zero(s):
    if len(s)==1:
        s="00"+s
    elif len(s)==2:
        s="0"+s
    return s   
    
def yyyymmdd2yyyydd(DATE):
    LE = len(str(int(DATE)))
    DATE = str(DATE)
    
    if LE == 6:
        YY = int(DATE[0:2])
        if YY > 80:
            DATE = '19' + DATE
        else:
            DATE = '20' + DATE
            
    year = int(str(DATE[0:4]))
    month = int(str(DATE[4:6]))
    day = int(str(DATE[6:8]))
    
    if year%4==0:
        x = [31,29,31,30,31,30,31,31,30,31,30,31]
    else:
        x = [31,28,31,30,31,30,31,31,30,31,30,31]

    kk = np.ones([12,1])
    kk[month-1:]= 0
    
    x = np.asarray(x)
    kk = np.asarray(kk)
    
    day1 = np.dot(x,kk)
    DD = day + day1 
    DD= str(int(DD[0]))
    
    DD = add_zero(str(DD))
   
    ST = str(year) + str(DD)
    
    return ST

def yyyy2yyyymmddhhmmss(t0):
    
    t0 = float(t0)/3600/24
    hh = int(t0*24)
    mm = int((t0*24 - int(t0*24))*60)
    ss = (t0*24*60 - int(t0*24*60))*60
    ST = str(hh)+':'+str(mm)+':'+str(ss)
    h0 = str(hh)
    return ST,h0

def unitdate(DATE):
    LE = len(str(int(DATE)))
    DATE = str(int(DATE))
    if LE==5:
        DATE = '200' + DATE  
    
    if LE == 6:
        YY = int(DATE[0:2])
        if YY > 80:
            DATE = '19' + DATE
        else:
            DATE = '20' + DATE
    return DATE

def readdate(DATESTR):
    s1 = DATESTR
    DD=[]

    if ',' not in s1:
        DD.append(str(int(s1)))
    else:
        k = len(s1.split(','))
        for i in range(k):
            DD.append(str(int(s1.split(',')[i])))
            
    return DD
        
        
###################################################################################################

INTRODUCTION = '''
    Extract the SAR synchronous GPS tropospheric products.
'''

EXAMPLE = '''EXAMPLES:

    extract_sar_atm_bash.py search_gps.txt imaging_time
    extract_sar_atm_bash.py search_gps.txt imaging_time --date 20180101
    extract_sar_atm_bash.py search_gps.txt imaging_time --date_txt date_list.txt

'''    
    


def cmdLineParse():
    parser = argparse.ArgumentParser(description='Extract the SAR synchronous GPS tropospheric products.',\
                                     formatter_class=argparse.RawTextHelpFormatter,\
                                     epilog=INTRODUCTION+'\n'+EXAMPLE)

    parser.add_argument('gps_txt',help='GPS station text file.')
    parser.add_argument('imaging_time',help='Center line UTC sec.')
    parser.add_argument('-d', '--date', dest='date_list', nargs='*',help='date list to extract.')
    parser.add_argument('--date-txt', dest='date_txt', nargs='*',help='date list text to extract.')
    
    inps = parser.parse_args()

    return inps

    
####################################################################################################
def main(argv):
    
    inps = cmdLineParse()
    date_list = []
    if inps.date_list:
        date_list = inps.date_list
    if inps.date_txt:
        date_list2 = np.loadtxt(LIST,dtype=np.str)
        date_list2 = date_list2.tolist()
        for list0 in date_list2:
            if list0 not in date_list:
                date_list.append(list0)
    
    path0 = os.getcwd()
    gps_dir = path0 + '/GPS/atm'
    
    if (not inps.date_txt) and (not inps.date_list):
        print('Obtain the GPS data-date automatically from %s' % gps_dir)
        date_list = [os.path.basename(x).split('_')[3] for x in glob.glob(gps_dir + '/Global_GPS_Trop*')]
        
    date_list = list(map(int, date_list))
    date_list = sorted(date_list)
    N = len(date_list)
    print('---------------------------------------')
    print('Total number of extracted date: %s ' % str(len(date_list)))
    print('---------------------------------------')
    
    t0 = inps.imaging_time
    SST,HH = yyyy2yyyymmddhhmmss(float(t0))
    t0 =float(t0)/3600/24
    t0 = float(t0)*24*12
    t0 = round(t0)
    t0 = t0 * 300
    
    hh0 = float(t0)/3600
    HH0 = int(round(float(hh0)/2)*2)
    Tm =str(int(t0))

    for i in range(N):
        print('---------------------')
        print('Extract job: ' + str(int(i+1)) + '/' + str(int(N)))
        DATE0 = str(date_list[i])
        DATE0 = unitdate(DATE0)
        
        dt = dateutil.parser.parse(DATE0)
        time = astropy.time.Time(dt)
        JD = time.jd - 2451545.0
        JDSEC = JD*24*3600        
        JDSEC_SAR = int(JDSEC + t0)
            
        GPS = np.loadtxt(inps.gps_txt, dtype = np.str)
        DD = GPS[:,0]
        k=len(DD)
        DD.tolist()    
            
        Trop_GPS = gps_dir + '/Global_GPS_Trop_' + str(DATE0)
        if not os.path.isfile(Trop_GPS):
            print('% is not found.' % Trop_GPS)
        else:    
            print('Extracting tropospheric delays for ' + str(int(k)) + ' GPS stations: %s' % DATE0)
            OUT = gps_dir + '/SAR_GPS_Trop_' + str(DATE0)
            if os.path.isfile(OUT):
                os.remove(OUT)
            
            for i in range(k):
                Nm=DD[i]
                print_progress(i+1, k, prefix='Station name: ', suffix=Nm)
                STR0 = '"' + str(JDSEC_SAR) + '.*' + str(Nm) + '"'
                call_str = "grep -E " + STR0 + ' ' + Trop_GPS + '>> ' + OUT
                os.system(call_str)
        
        PWV_GPS = gps_dir + '/Global_GPS_PWV_' + str(DATE0)
        if not os.path.isfile(PWV_GPS):
            print('% is not found.' % PWV_GPS)
        else:
            print('Extracting atmospheric PWV for ' + str(int(k)) + ' GPS stations: %s' % DATE0)
            OUT = gps_dir + '/SAR_GPS_PWV_' + str(DATE0)
            if os.path.isfile(OUT):
                os.remove(OUT)
            for i in range(k):
                Nm=DD[i]
                print_progress(i+1, k, prefix='Station name: ', suffix=Nm)
                STR0 = ' " ' + str(HH0) + ' ' + '.*' + str(Nm) + '"'
                call_str = "grep -E " + STR0 + ' ' + PWV_GPS + '>> ' + OUT
                os.system(call_str)
       
        os.system(call_str)   
            

if __name__ == '__main__':
    main(sys.argv[1:])

