#! /usr/bin/env python
############################################################
# Program is part of TSSAR v1.0                            #
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
    download_gps_atm.py search_gps.txt -d 20150101
    download_gps_atm.py search_gps.txt -d 20150101,20150203
    download_gps_atm.py search_gps.txt -datetxt /Yunmeng/SCRATCH/LosAngeles.txt
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
    GPS_LAT = GPS[:,1]
    GPS_LON = GPS[:,2]
    GPS_Nm = GPS_Nm.tolist()
    
    Thelta = float(GPS[0,6])
    HEAD = float(GPS[0,7])
    
    pi = math.pi
    Thelta = Thelta/180*pi
    
    N = len(GPS_Nm) 
    t0 = GPS[0,5]
    t0 =float(t0)/3600/24
    t0 = float(t0)*24*12
    t0 = round(t0)
    t0 = t0 * 300
    
    Tm =str(int(t0))
    
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
    
    
    SST = yyyy2yyyymmddhhmmss(float(t0))
    
    for i in range(k):       
        DATE = str(int(DD[i]))
        print_progress(i+1, k, prefix='Downloading GPS ZTD for acquisition:  ', suffix=DATE)
        
        DATE = unitdate(DATE)
        dt = dateutil.parser.parse(DATE)
        time = astropy.time.Time(dt)
        JD = time.jd - 2451545.0
        JDSEC = JD*24*3600
    
        print ''
        print "SAR acquisition time (UTC) is: " +DATE[0:4] + ' ' + DATE[4:6] + ' ' +DATE[6:8] + ' ' + SST
        JDSEC_SAR = int(JDSEC + t0)
        print "SAR acquisition time (J2000) is: " + str(JDSEC_SAR) + ' (SEC)'
        print ''
        
        ST = yyyymmdd2yyyydd(DATE)
        
        YEAR = ST[0:4]
        DAY = ST[4:]      
    
    
        #######################  search the biggest one to download ################################
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
    
    
        if os.path.isfile(FILE):
            os.remove(FILE)
    
        call_str = 'wget -q ftp://data-out.unavco.org/pub/products/troposphere/' + YEAR + '/' + DAY + '/' + FILE
        print call_str
        print 'Downloading GPS troposphere data >>> '
        os.system(call_str)
        print 'Download finish.'
        print ''
    
        print 'Start to get ZTD data in SAR coverage >>>'
        FILE0 = FILE.replace('.gz','')
        if os.path.isfile(FILE0):
            os.remove(FILE0)

        call_str = 'gzip -d ' + FILE
        os.system(call_str)
    
        OUT = 'gps_atm_raw_'+unitdate(str(DD[i]))
    
        if os.path.isfile(OUT):
            os.remove(OUT)    
    
        Tm = str(JDSEC_SAR)
    
        print '...'
        for j in range(N):
            Nm=GPS_Nm[j]
            call_str = "grep " + Nm + ' ' + FILE0 + '> tt'
            os.system(call_str)
        
            call_str = "grep " + Tm + ' tt ' + '>> ' + OUT
            os.system(call_str)
        
        
        RAW_ATM = np.loadtxt(OUT, dtype = np.str)
        ZTD = RAW_ATM[:,1]
        ZDD = RAW_ATM[:,2]
        ZWD = RAW_ATM[:,3]
        ZWD_SIG = RAW_ATM[:,4]
        
        N0 = len(ZTD)
        if N0 == 1:
            ZTD_LOS = float(ZTD)/math.cos(Thelta)
            ZDD_LOS = float(ZDD)/math.cos(Thelta)
            ZWD_LOS = float(ZWD)/math.cos(Thelta)
            ZWD_SIG_LOS = float(ZWD_SIG)/math.cos(Thelta)
            
        else:
            ZTD = map(float,ZTD)
            ZDD = map(float,ZDD)
            ZWD = map(float,ZWD)
            ZWD_SIG = map(float,ZWD_SIG)
            
            ZTD_LOS = np.divide(ZTD,math.cos(Thelta))
            ZDD_LOS = np.divide(ZDD,math.cos(Thelta))
            ZWD_LOS = np.divide(ZWD,math.cos(Thelta))
            ZWD_SIG_LOS = np.divide(ZWD_SIG,math.cos(Thelta))

        NM = RAW_ATM[:,9]
                
        OUT = 'gps_atm_los_' + unitdate(str(DD[i]))
        if os.path.isfile(OUT):
            os.remove(OUT) 
                    
        for j in range(N0):
            LAT = GPS_LAT[GPS_Nm.index(NM[j])]
            LON = GPS_LON[GPS_Nm.index(NM[j])]
            STR = str(NM[j]) + ' ' + str(LAT) + ' ' + str(LON) + ' ' + str(ZTD_LOS[j]) + ' ' +str(ZDD_LOS[j]) + ' ' + str(ZWD_LOS[j]) + ' ' + str(ZWD_SIG_LOS[j])
            call_str = 'echo ' + STR + '>> ' + OUT
            os.system(call_str)
                
        count = len(open(OUT,'rU').readlines())
        print ''
        print 'Number of available GPS stations with ZTD data at SAR acquisition: ' + str(count)
        print str(DD[i]) + ' Done.'
        print ''
    
    

if __name__ == '__main__':
    main(sys.argv[1:])

