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
    
    return ST,DATE

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

def readdate(DATESTR):
    s1 = DATESTR
    DD=[]

    if ',' not in s1:
        DD.append(s1)
    else:
        k = len(s1.split(','))
        for i in range(k):
            DD.append(s1.split(',')[i])
            
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
    download_gps_atm_date.py 20150101 
    download_gps_atm_date.py 20150101 --station BGIS
    download_gps_atm_date.py 20150101 --station_txt search_gps_inside.txt
'''    
    


def cmdLineParse():
    parser = argparse.ArgumentParser(description='Download GPS data over SAR coverage.',\
                                     formatter_class=argparse.RawTextHelpFormatter,\
                                     epilog=INTRODUCTION+'\n'+EXAMPLE)

    parser.add_argument('date',help='GPS station name.')
    parser.add_argument('--station', dest='station_name', help='GPS station name.')
    parser.add_argument('--station_txt', dest='station_txt', help='GPS station txet file.')
    
    inps = parser.parse_args()

    
    return inps

    
####################################################################################################
def main(argv):
    
    inps = cmdLineParse()
    DATE = inps.date
    DATE = str(int(DATE))
    ST,DATE = yyyymmdd2yyyydd(DATE)
    YEAR = ST[0:4]
    DAY = ST[4:]
    
    
    Trop_GPS = 'Global_GPS_Trop_' + DATE 
    
    call_str = 'curl ftp://data-out.unavco.org/pub/products/troposphere/' + YEAR + '/' + DAY + '/' + ' >ttt' 
    os.system(call_str)
    
    call_str ="grep 'cwu' ttt > ttt1"
    os.system(call_str)
    
    call_str ="grep '.gz' ttt1 > ttt"
    os.system(call_str)
    BB = np.loadtxt('ttt',dtype=np.str)
    
    
    call_str = "awk '{print $5}' ttt >ttt1"
    os.system(call_str)
    
    AA = np.loadtxt('ttt1')
    kk = AA.size
    
    if kk>1:
        AA = map(int,AA)
        IDX = AA.index(max(AA))
        FILE = BB[int(IDX),8]
    else:
        AA = int(AA)
        FILE = BB[8]
    
    
    call_str = 'curl ftp://data-out.unavco.org/pub/products/troposphere/' + YEAR + '/' + DAY + '/' + ' >ttt' 
    os.system(call_str)
    call_str ="grep 'nmt' ttt > ttt1"
    os.system(call_str)
    
    call_str ="grep '.gz' ttt1 > ttt"
    os.system(call_str)
    BB = np.loadtxt('ttt',dtype=np.str)
    
    
    call_str = "awk '{print $5}' ttt >ttt1"
    os.system(call_str)
    
    AA = np.loadtxt('ttt1')
    kk = AA.size
    
    if kk>1:
        AA = map(int,AA)
        IDX = AA.index(max(AA))
        FILE_PWV = BB[int(IDX),8]
    else:
        AA = int(AA)
        FILE_PWV = BB[8]
    
    #print YEAR
    #print DAY
    
    if os.path.isfile(FILE):
        os.remove(FILE)
    
    call_str = 'wget -q ftp://data-out.unavco.org/pub/products/troposphere/' + YEAR + '/' + DAY + '/' + FILE
    print 'Downloading GPS troposphere data ...'
    os.system(call_str)
    print 'Download finish.'
    print ''
    
    
    call_str = 'wget -q ftp://data-out.unavco.org/pub/products/troposphere/' + YEAR + '/' + DAY + '/' + FILE_PWV
    print 'Downloading GPS PWV data ...'
    os.system(call_str)
    print 'Download finish.'
    print ''
    
    FILE0 = FILE.replace('.gz','')
    if os.path.isfile(FILE0):
        os.remove(FILE0)

    call_str = 'gzip -d ' + FILE
    os.system(call_str)
    
    call_str ='cp ' + FILE0 + ' ' + Trop_GPS
    os.system(call_str)

    os.remove(FILE0)    
    
    
    
    Trop_PWV_GPS = 'Global_GPS_PWV_' + DATE
    
    FILE0 = FILE_PWV.replace('.gz','')
    if os.path.isfile(FILE0):
        os.remove(FILE0)

    call_str = 'gzip -d ' + FILE_PWV
    os.system(call_str)
    
    call_str ='cp ' + FILE0 + ' ' + Trop_PWV_GPS
    os.system(call_str)

    os.remove(FILE0)    
    
    
    k=0
    
    if inps.station_name:
        DD=readdate(inps.station_name)
        k = len(DD)
    elif inps.station_txt:
        GPS= np.loadtxt(inps.station_txt, dtype = np.str)
        DD =GPS[:,0]
        k=len(DD)
        DD = DD.tolist()
    if k>0:
        print 'Extracting tropospheric delays for ' + str(int(k)) + ' GPS stations:'
        for i in range(k):
            Nm=DD[i]
            print Nm
            OUT = Nm+ '_Trop_' + DATE
            call_str = "grep " + Nm + ' ' + Trop_GPS + '> ' + OUT
            os.system(call_str)
            
            OUT = Nm+ '_Trop_PWV_' + DATE
            call_str = "grep " + Nm + ' ' + Trop_PWV_GPS + '> ' + OUT
            os.system(call_str)
            
            
if __name__ == '__main__':
    main(sys.argv[1:])

