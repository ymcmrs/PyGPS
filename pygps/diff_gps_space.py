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

import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, FormatStrFormatter

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

def yyyy2yyyymmddhhmmss(t0):
    hh = int(t0*24)
    mm = int((t0*24 - int(t0*24))*60)
    ss = (t0*24*60 - int(t0*24*60))*60
    ST = str(hh)+':'+str(mm)+':'+str(ss)
    return ST  

def unitdate(DATE):
    LE = len(str(int(DATE)))
    DATE = str(DATE)
    
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

INTRODUCTION = '''Calculating InSAR LOS atmospheric delays and deformations:
    GPS stations are searched from Nevada Geodetic Laboratory by using search_gps.py 
    website:  http://geodesy.unr.edu/NGLStationPages/gpsnetmap/GPSNetMap.html
   
    GPS atmosphere data is download from UNAVOC, please check: download_gps_atm.py
    website:  ftp://data-out.unavco.org/pub/products/troposphere
    
    GPS deformation data is download from Nevada Geodetic Laboratory , plaese check: download_gps_def.py
    website:  http://geodesy.unr.edu/gps_timeseries/tenv3/IGS08

'''

EXAMPLE = '''EXAMPLES:
    diff_gps_space.py RefDate -d slaveDate --Atm --Def
    diff_gps_space.py RefDate --datetxt Datetxt --Atm --Def
    diff_gps_space.py 20150101 -d 20150203
    diff_gps_space.py 20150101 -d 20150203,20150501 --Atm
    diff_gps_space.py 20150101 --datetxt /Yunmeng/Pacaya/Date.txt --Def
'''    
    

def cmdLineParse():
    parser = argparse.ArgumentParser(description='Download GPS data over SAR coverage.',\
                                     formatter_class=argparse.RawTextHelpFormatter,\
                                     epilog=INTRODUCTION+'\n'+EXAMPLE)

    parser.add_argument('RefDate',help='Reference date of differential InSAR')
    parser.add_argument('-d', dest = 'date', help='date for estimation.')
    parser.add_argument('--datetxt', dest = 'datetxt', help='text file of date.')
    parser.add_argument('--Atm',action="store_true", default=False, help='Geting SAR LOS tropospheric delay.')
    parser.add_argument('--Def', action="store_true", default=False, help='Getting SAR LOS deformation.')
    
    inps = parser.parse_args()
    
    if not inps.date and not inps.datetxt:
        parser.print_usage()
        sys.exit(os.path.basename(sys.argv[0])+': error: date and date_txt File, at least one is needed.')

    return inps

    
####################################################################################################
def main(argv):
    
    inps = cmdLineParse()
    
    if inps.date:
        DATESTR = inps.date
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
    
    print('')
    print("Differential date: ")
    print(DD)
    
    RefDate = inps.RefDate
    REF_DEF = 'gps_def_los_' + unitdate(str(int(unitdate(RefDate))))
    REF_ATM = 'gps_atm_los_' + unitdate(str(int(unitdate(RefDate))))
    
    
    
    if inps.Def:
        if not os.path.isfile(REF_DEF):
            call_str = 'download_gps_def.py search_gps.txt -d ' + unitdate(str(int(unitdate(RefDate))))
            os.system(call_str)
            
        GPS_REF_DEF = np.loadtxt(REF_DEF,dtype=np.str)
        GPS_NM = GPS_REF_DEF[:,0]
        GPS_NM = GPS_NM.tolist()
        GPS_LAT = GPS_REF_DEF[:,1]
        GPS_LON = GPS_REF_DEF[:,2]
    
        REF_DEF_LOS = GPS_REF_DEF[:,3]
        REF_DEF_STD = GPS_REF_DEF[:,4]
        for i in range(k):
            DIFF = 'diff_def_' +unitdate(str(int(unitdate(RefDate)))) + '-' + unitdate(str(int(unitdate(DD[i]))))
            if os.path.isfile(DIFF):
                os.remove(DIFF)
                
            SLAVE = 'gps_def_los_' + unitdate(str(int(unitdate(DD[i]))))
            if not os.path.isfile(SLAVE):
                call_str = 'download_gps_def.py search_gps.txt -d ' + unitdate(str(int(unitdate(DD[i]))))
                os.system(call_str)
                
            GPS = np.loadtxt(SLAVE,dtype=np.str)
            NM = GPS[:,0]
            LAT = GPS[:,1]
            LON = GPS[:,2]
            DEF = GPS[:,3]
            STD = GPS[:,4]
            N = len(NM)
            for j in range(N):
                if NM[j] in GPS_NM:
                    idx = GPS_NM.index(NM[j])
                    DIFF_DEF =  float(DEF[j]) - float(REF_DEF_LOS[idx])
                    DIFF_STD = (float(STD[j])**2 + float(REF_DEF_STD[idx])**2)**0.5
                    
                    STR = str(NM[j]) + ' ' +str(LAT[j]) + ' ' + str(LON[j]) + ' ' + str(DIFF_DEF) + ' ' + str(DIFF_STD)
                    call_str = 'echo ' + STR + ' >> ' + DIFF
                    os.system(call_str)
       
    if inps.Atm:
        if not os.path.isfile(REF_ATM):
            call_str = 'download_gps_atm.py search_gps.txt -d ' + unitdate(str(int(unitdate(RefDate))))
            os.system(call_str)
            
        GPS_REF_ATM = np.loadtxt(REF_ATM,dtype=np.str)
        GPS_NM = GPS_REF_ATM[:,0]
        GPS_NM = GPS_NM.tolist()
        GPS_LAT = GPS_REF_ATM[:,1]
        GPS_LON = GPS_REF_ATM[:,2]
    
        REF_DEF_LOS = GPS_REF_ATM[:,3]
        REF_DEF_STD = GPS_REF_ATM[:,4]
        
        REF_ATM_LOS = GPS_REF_ATM[:,3]
        REF_ATM_STD = GPS_REF_ATM[:,6]
        for i in range(k):
            DIFF = 'diff_atm_' +unitdate(str(int(unitdate(RefDate)))) + '-' + unitdate(str(int(unitdate(DD[i]))))
            if os.path.isfile(DIFF):
                os.remove(DIFF)
                
            SLAVE = 'gps_atm_los_' + unitdate(str(int(unitdate(DD[i]))))
            if not os.path.isfile(SLAVE):
                call_str = 'download_gps_atm.py search_gps.txt -d ' + unitdate(str(int(unitdate(DD[i]))))
                os.system(call_str)
                
            GPS = np.loadtxt(SLAVE,dtype=np.str)
            NM = GPS[:,0]
            LAT = GPS[:,1]
            LON = GPS[:,2]
            ATM = GPS[:,3]
            STD = GPS[:,6]
            N = len(NM)
            for j in range(N):
                if NM[j] in GPS_NM:
                    idx = GPS_NM.index(NM[j])
                    DIFF_ATM =  float(ATM[j]) - float(REF_ATM_LOS[idx])
                    DIFF_STD = (float(STD[j])**2 + float(REF_ATM_STD[idx])**2)**0.5
                    
                    STR = str(NM[j]) + ' ' +str(LAT[j]) + ' ' + str(LON[j]) + ' ' + str(DIFF_ATM) + ' ' + str(DIFF_STD)
                    call_str = 'echo ' + STR + ' >> ' + DIFF
                    os.system(call_str)
    
    

if __name__ == '__main__':
    main(sys.argv[1:])

