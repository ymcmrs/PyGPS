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

    parser.add_argument('gps_txt',help='Available GPS station information.')
    parser.add_argument('-d', dest='time', help='SAR acquisition time.')
    parser.add_argument('--datetxt', dest='datetxt', help='text file of date for downloading.')
    
    inps = parser.parse_args()

    return inps

    
####################################################################################################
def main(argv):
    
    inps = cmdLineParse()
    
    TXT = inps.gps_txt
    GPS= np.loadtxt(TXT, dtype = np.str)
    GPS_Nm =GPS[:,0]
    GPS_Nm = GPS_Nm.tolist()
    GPS_LAT = GPS[:,1]
    GPS_LON = GPS[:,2]
    N = len(GPS_Nm) 
    t0 = GPS[0,5]
    t0 =float(t0)/3600/24
    t0 = float(t0)*24*12
    t0 = round(t0)
    t0 = t0 * 300
    
    Tm =str(int(t0))
    
    Theta = float(GPS[0,6])
    HEAD = float(GPS[0,7])

    if HEAD < 0:
          HEAD = HEAD+360 

    Theta = Theta*np.pi/180.0
    HEAD = HEAD*np.pi/180.0    

    unitVec=[np.cos(HEAD)*np.sin(Theta),-np.sin(Theta)*np.sin(HEAD),-np.cos(Theta)]    
    unitVar = [unitVec[0]**2,unitVec[1]**2,unitVec[2]**2]
    
    if inps.time:
        DATESTR = inps.time
        DD=readdate(DATESTR)
        k = len(DD)
    else:
        DATETXT = inps.datetxt
        DD = np.loadtxt(DATETXT)
        k = DD.size
        AA =[]
        if k ==1:
            AA.append(str(int(DD)))
        else:
            for i in range(k):
                AA.append(str(int(DD[i])))
        DD = AA
        
    print ''
    print "Downloaded date: "
    print DD
    
    for j in range(k):
        OUT = 'gps_def_raw_' + unitdate(str(int(DD[j])))
        if os.path.isfile(OUT):
            os.remove(OUT)
    
    print 'Start to download GPS deformation data >>>'
    print ''
    for i in range(N):
        Nm =str(GPS_Nm[i])
        print_progress(i+1, N, prefix='Station name: ', suffix=Nm)
        FILE = Nm + '.IGS08.tenv3'
        
        if not os.path.isfile(FILE):
            call_str = "wget -q http://geodesy.unr.edu/gps_timeseries/tenv3/IGS08/" + FILE
            os.system(call_str)
        
        
        for j in range(k):
            OUT = 'gps_def_raw_' + unitdate(str(int(DD[j])))
            OUT_LOS = 'gps_def_los_' + unitdate(str(int(DD[j])))
            DT = unitdate(str(int(DD[j])))
            ST = date2yymondd(DT)
                    
            call_str = "grep " + ST + ' ' + FILE + '>> ' + OUT
            os.system(call_str)
    
    call_str = 'rm *tenv3'
    os.system(call_str)
    
    print 'Available GPS station number for each SAR aquisition: ' 
    
    for i in range(k):
        OUT = 'gps_def_raw_' + unitdate(str(int(DD[i])))
        OUT_LOS = 'gps_def_los_' + unitdate(str(int(DD[i])))
        if os.path.isfile(OUT_LOS):
            os.remove(OUT_LOS)
        
        GPS = np.loadtxt(OUT,dtype = np.str)
        NM = GPS[:,0]
        Def_E = GPS[:,8]
        Def_N = GPS[:,10]
        Def_U = GPS[:,12]
        
        Sig_E = GPS[:,14]
        Sig_N = GPS[:,15]
        Sig_U = GPS[:,16]
        
        
        Def_E = Def_E.astype(np.float)
        Def_N = Def_N.astype(np.float)
        Def_U = Def_U.astype(np.float)
        
        Sig_E = Sig_E.astype(np.float)
        Sig_N = Sig_N.astype(np.float)
        Sig_U = Sig_U.astype(np.float)
        
        
        Def_LOS = Def_E*unitVec[0] + Def_N*unitVec[1] + Def_U*unitVec[2]
        Sig_LOS = ((Sig_E**2)*(unitVec[0]**2) + (Sig_N**2)*(unitVec[1]**2) + (Sig_U**2)*(unitVec[2]**2))**0.5
        
        N0 = len(Def_LOS)
        
        for j in range(N0):
            LAT = GPS_LAT[GPS_Nm.index(NM[j])]
            LON = GPS_LON[GPS_Nm.index(NM[j])]
            STR = str(NM[j]) + ' ' + str(LAT) + ' ' + str(LON) + ' ' + str(Def_LOS[j]) + ' ' + str(Sig_LOS[j])
            call_str = 'echo ' + STR + ' >> ' + OUT_LOS 
            os.system(call_str)
        print str(DD[i]) + ' :' + str(N0)    
            
            
if __name__ == '__main__':
    main(sys.argv[1:])

