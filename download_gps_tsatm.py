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
    hh = int(t0*24)
    mm = int((t0*24 - int(t0*24))*60)
    ss = (t0*24*60 - int(t0*24*60))*60
    ST = str(hh)+':'+str(mm)+':'+str(ss)
    return ST  

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

def unitday(dd):
    LE = len(str(int(dd)))
    DAY = str(int(dd))
    
    if LE==1:
        DAY = '00' + DAY 
    if LE == 2:
        DAY = '0' + DAY 
        
    return DAY

def unit_utc2sec(UTC):
    OUR = UTC.split(':')[0]
    MIN = UTC.split(':')[1]
    
    SEC =int(int(OUR)*12*300 + (int(MIN)/5)*300)
        
    return SEC


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
    Download time series tropospheric delays for interested GPS stations.
    
    Global GPS stations are referred the GPSNetMap of Nevada Geodetic Laboratory
    Details can be found from http://geodesy.unr.edu/NGLStationPages/gpsnetmap/GPSNetMap.html

'''


EXAMPLE = '''EXAMPLES:
    download_gps_tsatm.py -p BGIS -s 2001-001 -e 2017-365 
    
'''


def cmdLineParse():
    parser = argparse.ArgumentParser(description='Download GPS data over SAR coverage.',\
                                     formatter_class=argparse.RawTextHelpFormatter,\
                                     epilog=INTRODUCTION+'\n'+EXAMPLE)

    parser.add_argument('-p',dest='station', help='GPS stations name')
    parser.add_argument('-s', dest='start', help='start date.')
    parser.add_argument('-e', dest='end', help='end date.')
    parser.add_argument('-t', dest='utc_time', help='troposphere of UTC time, e.g., 14:00')
    parser.add_argument('-o', dest='out', help='output file name.')
    parser.add_argument('--inside', action="store_true", default=False, help='Constraining stations inside the SAR coverage, otherwise, in the corner rectangle region.')
    parser.add_argument('--extend_search', dest='extend_search', help='extend the search region based on the box corner.')
    inps = parser.parse_args()
    
    if not inps.station:
        parser.print_usage()
        sys.exit(os.path.basename(sys.argv[0])+': error: GPS station should be provided.')
    

    return inps

    
####################################################################################################
def main(argv):
    
    inps = cmdLineParse()
    GPS_Station = inps.station
    Start_Date = inps.start
    End_Date = inps.end
    
    if inps.utc_time:
        UTC = inps.utc_time
    else:
        UTC = '14:00'
    
    SEC=unit_utc2sec(UTC)
    SEC = str(SEC)
    
    Start_Year = int(Start_Date.split('-')[0])
    Start_Day = int(Start_Date.split('-')[1])
    
    End_Year = int(End_Date.split('-')[0])
    End_Day = int(End_Date.split('-')[1])
    
    # ftp://gneiss.nbmg.unr.edu/trop/1997/001/AIS10010.97zpd.gz
    
    STRFILE = GPS_Station+'_TS_Trop'
    if os.path.isfile(STRFILE):
        os.remove(STRFILE)
    
    for i in range(Start_Year,End_Year+1):        
        print 'Start to download atmosphere date for year: ' + str(i)
        if not i==End_Year:
            Nm =str(i)
   
            for j in range(366):
                N = 366
                print_progress(j+1, N, prefix='Year: ', suffix=Nm)
                yy=str(i)
                dd=str(int(j+1))
                day = unitday(dd)
                STR_WEB = 'ftp://gneiss.nbmg.unr.edu/trop/' + yy + '/' + day + '/' + GPS_Station+ day+'0.' + yy[2:4]+'zpd.gz'
                call_str = 'wget -q ' + STR_WEB
                os.system(call_str)
                
                FF=GPS_Station+ day+'0.' + yy[2:4]+'zpd.gz'    
                call_str = 'zgrep -A0 ' + "'" + GPS_Station + ' ' + yy[2:4] + ':'+day+':'+SEC+"' " + FF + ' >>' + STRFILE
                print call_str
                os.system(call_str)
            
             
        else:
            Nm =str(i)
            for j in range(End_Day):
                N = End_Day
                print_progress(j+1, N, prefix='Year: ', suffix=Nm)
                yy=str(End_Year)
                dd=str(int(j+1))
                day = unitday(dd)
                STR_WEB = 'ftp://gneiss.nbmg.unr.edu/trop/' + yy + '/' + day + '/' + GPS_Station+ day+'0.' + yy[2:4]+'zpd.gz'
                call_str = 'wget -q ' + STR_WEB
                print STR_WEB
                os.system(call_str)  
                
                FF=GPS_Station+ day+'0.' + yy[2:4]+'zpd.gz'  
                call_str = 'zgrep -A0 ' + "'" + GPS_Station + ' ' + yy[2:4] + ':'+day+':'+SEC+"' " + FF + ' >>' + STRFILE
                print call_str
                os.system(call_str)
    

if __name__ == '__main__':
    main(sys.argv[1:])

