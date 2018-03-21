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
import astropy.time
import dateutil.parser
import math

from matplotlib.ticker import MultipleLocator, FormatStrFormatter

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

def date2yymondd(DATE):
    Mon = ['JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC']
    
    if len(str(int(DATE)))==5:
        YY = DATE[0:1]
        MM = DATE[1:3]
        MO = Mon[int(MM)-1]
        DD = DATE[3:5]
        
    if len(str(int(DATE)))==6:
        YY = DATE[0:2]
        MM = DATE[2:4]
        MO = Mon[int(MM)-1]
        DD = DATE[4:6]
    if len(str(int(DATE)))==8:
        YY = DATE[2:4]
        MM = DATE[4:6]
        MO = Mon[int(MM)-1]
        DD = DATE[6:8]
        
        
    ST = YY+MO+DD
    return ST
        

def yyyy2yyyymmddhhmmss(t0):
    hh = int(t0*24)
    mm = int((t0*24 - int(t0*24))*60)
    ss = (t0*24*60 - int(t0*24*60))*60
    ST = str(hh)+':'+str(mm)+':'+str(ss)
    return ST  


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
    download_gps_def.py search_gps.txt -d 20150101
    download_gps_def.py search_gps.txt -d 20150101,20150203
    download_gps_def.py search_gps.txt -datetxt /Yunmeng/SCRATCH/LosAngeles.txt
'''    
    


def cmdLineParse():
    parser = argparse.ArgumentParser(description='Download GPS data over SAR coverage.',\
                                     formatter_class=argparse.RawTextHelpFormatter,\
                                     epilog=INTRODUCTION+'\n'+EXAMPLE)

    parser.add_argument('gps_file',help='GPS station file. geometry or general')
    parser.add_argument('--inc', dest='incidence', help='incidence angle for deformation change.')
    parser.add_argument('--head', dest='head', help='Heading angle for deformation change.')
    
    inps = parser.parse_args()

    return inps

    
####################################################################################################
def main(argv):
    
    inps = cmdLineParse()
    GPS = inps.gps_geometry_file
    GPS= np.loadtxt(TXT, dtype = np.str)
    GPS_Nm =GPS[:,0]
    GPS_Nm = GPS_Nm.tolist()
    N = len(GPS_Nm) 

    k_flag = 0
    if inps.inc and inps.head:
        INC =inps.inc
        HEAD =inps.head
        k_flag = 1
    
    print 'Start to estimate GPS LOS deformation data >>>'
    print ''
    for i in range(N):
        Nm =str(GPS_Nm[i])
        print_progress(i+1, N, prefix='Station name: ', suffix=Nm)
        if k_flag==0:
            INC = GPS[i,5]
            HEAD = GPS[i,6]
        
        call_str = 'enu2los.py ' + Nm + ' ' + str(INC) + ' ' + str(HEAD)
        os.system(call_str)
        
            
            
if __name__ == '__main__':
    main(sys.argv[1:])

