#! /usr/bin/env python
############################################################
# Program is part of PyGPS v1.0                            #
# Copyright(c) 2017, Yunmeng Cao                           #
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

INTRODUCTION = '''GPS:
    GPS stations are searched from Nevada Geodetic Laboratory by using search_gps.py 
    website:  http://geodesy.unr.edu/NGLStationPages/gpsnetmap/GPSNetMap.html
   
    GPS atmosphere data is download from UNAVOC, please check: download_gps_atm.py
    website:  ftp://data-out.unavco.org/pub/products/troposphere
    
    GPS deformation data is download from Nevada Geodetic Laboratory                              
    website:  http://geodesy.unr.edu/gps_timeseries/tenv3/IGS08
    
'''

EXAMPLE = '''EXAMPLES:

    get_sar_atm.py date_list search_gps.txt imaging_time
    get_sar_atm.py date_list gps_geometry.txt imaging_time

'''    
    


def cmdLineParse():
    parser = argparse.ArgumentParser(description='Download GPS data over SAR coverage.',\
                                     formatter_class=argparse.RawTextHelpFormatter,\
                                     epilog=INTRODUCTION+'\n'+EXAMPLE)

    parser.add_argument('date_list',help='Date list for downloading trop list.')
    parser.add_argument('gps_txt',help='GPS station text file.')
    parser.add_argument('imaging_time',help='Center line UTC.')
    
    inps = parser.parse_args()

    return inps

    
####################################################################################################
def main(argv):
    
    inps = cmdLineParse()
    LIST = inps.date_list
    DATE = np.loadtxt(LIST,dtype=np.str)
    DATE = DATE.tolist()
    N=len(DATE)
    TXT =inps.gps_txt
    
    t0 = inps.imaging_time
    SST,HH = yyyy2yyyymmddhhmmss(float(t0))
    t0 =float(t0)/3600/24
    t0 = float(t0)*24*12
    t0 = round(t0)
    t0 = t0 * 300
    HH0 = int(round(float(HH)/2)*2)
    Tm =str(int(t0))
    
    for i in range(N):
        
        DATE0 = unitdate(DATE[i])
        dt = dateutil.parser.parse(DATE0)
        time = astropy.time.Time(dt)
        JD = time.jd - 2451545.0
        JDSEC = JD*24*3600
        
        Research_File = 'Research_GPS_Trop_'+DATE0
        Research_File_PWV = 'Research_GPS_PWV_'+DATE0
        print ''
        print "SAR acquisition time (UTC) is: " +DATE0[0:4] + ' ' + DATE0[4:6] + ' ' +DATE0[6:8] + ' ' + SST
        JDSEC_SAR = int(JDSEC + t0)
        print "SAR acquisition time (J2000) is: " + str(JDSEC_SAR) + ' (SEC)'
        print ''
        
        OUT = 'SAR_GPS_Trop_RAW_' + DATE0
        OUT2 = 'SAR_GPS_Trop_' + DATE0
        if os.path.isfile(OUT):
            os.remove(OUT)
            
        if not os.path.isfile(Research_File):
            call_str =  'get_research_atm_date.py ' + DATE0 + ' --station_txt ' + TXT
            os.system(call_str)
                
        call_str = "grep " + str(JDSEC_SAR) + ' ' + Research_File + ' > ' + OUT
        os.system(call_str)
        
        
        print 'UTC: (Hour) ' + str(HH0) + ' (PWV constant will be used)'
        
        OUT = 'SAR_GPS_PWV_RAW_' + DATE0
        OUT2 = 'SAR_GPS_PWV_' + DATE0
        STR_HH = ' ' + str(HH0) + ' '
        call_str = "grep ' " + str(HH0) + " ' " + Research_File_PWV + " > " + OUT
        os.system(call_str)
        
        call_str = "awk '{print $18,$7,$9} ' "+ OUT + ' >' +OUT2
        os.system(call_str)   
            

if __name__ == '__main__':
    main(sys.argv[1:])

