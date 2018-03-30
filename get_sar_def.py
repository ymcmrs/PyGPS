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

    get_sar_def.py date_list imaging_time

'''    
    


def cmdLineParse():
    parser = argparse.ArgumentParser(description='Download GPS data over SAR coverage.',\
                                     formatter_class=argparse.RawTextHelpFormatter,\
                                     epilog=INTRODUCTION+'\n'+EXAMPLE)

    parser.add_argument('date_list',help='Date list for downloading trop list.')
    parser.add_argument('gps_txt',help='Center line UTC.')
    parser.add_argument('--average_number',dest='average_number',help='Number of defroamtions used for averaging.')
    
    inps = parser.parse_args()

    return inps

    
####################################################################################################
def main(argv):
    
    inps = cmdLineParse()
    LIST = inps.date_list
    DATE = np.loadtxt(LIST,dtype=np.str)
    DATE = DATE.tolist()
    N_DATE=len(DATE)
    
    
    GPS= np.loadtxt(inps.gps_txt, dtype = np.str)
    GPS_Nm =GPS[:,0]
    N_GPS=len(GPS_Nm)
    
    N_Av = 1
    if inps.average_number:
        N_Av = float(inps.average_number)
        
        
    print 'Start to get SAR asquisition related LOS deformations: '    
    for i in range(N_DATE):
        DATE0 = DATE[i]
        DATE0 = unitdate(DATE0)
        
        dt = dateutil.parser.parse(DATE0)
        time = astropy.time.Time(dt)
        #JD = time.jd - 2451545.0
        MJD = time.jd - 2400000  
        OUT = 'SAR_GPS_Def_' + DATE0
        
        MJD1 = float(MJD - N_Av)
        MJD2 = float(MJD + N_Av)
           
        #print MJD
        sum0 = 0
        for j in range(N_GPS):
            GPS0 = GPS_Nm[j] + '_TS_LOS'
            DATA = np.loadtxt(GPS0, dtype = np.str)
            YYYY = DATA[:,0]
            YYYY = YYYY.astype(np.float)
            
            MJD_TS = DATA[:,1]
            MJD_TS= MJD_TS.astype(np.float)
            #ff=np.where(MJD1 < MJD_TS & MJD_TS< MJD2)
            f0 = np.where(MJD_TS==MJD)
            
            LOS_TS = DATA[:,2]
            LOS_TS=LOS_TS.astype(np.float)
            
            LOS_SIG = DATA[:,3]
            LOS_SIG = LOS_SIG.astype(np.float)
            
            K0 = MJD_TS[(MJD1 < MJD_TS) & (MJD_TS < MJD2)]
            N_k0 = len(K0)
            
            if N_k0>1:
                sum0 = sum0 + 1
                #SIG = str(np.mean(LOS_SIG[ff]))
                SIG = np.mean(LOS_SIG[(MJD1 < MJD_TS) & (MJD_TS < MJD2)])
                #LOS = str(np.mean(LOS_TS[ff]))
                LOS = np.mean(LOS_TS[(MJD1 < MJD_TS) & (MJD_TS < MJD2)])
                #MAE = str(np.mean(np.abs((LOS - LOS_TS[ff]))))
                MAE = np.mean(np.abs(LOS - LOS_TS[(MJD1 < MJD_TS) & (MJD_TS < MJD2)]))
                
                
                SIG = str(SIG)
                LOS = str(LOS)
                MAE = str(MAE)
                
                call_str = 'echo ' + GPS0 + ' ' + LOS + ' ' + MAE + ' ' + SIG + ' >>' + OUT
                os.system(call_str)
        print DATE0  + '( MJD '+ str(int(MJD))+ ')' +': ' + str(int(sum0)) + ' stations available'
        
        

if __name__ == '__main__':
    main(sys.argv[1:])

