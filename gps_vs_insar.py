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

def read_data(inFile, dtype, nWidth, nLength):
    data = np.fromfile(inFile, dtype, int(nLength)*int(nWidth)).reshape(int(nLength),int(nWidth))  
    return data        

def min_dist(MASK,RANGE,AZIMUTH):
    LL,CC = MASK.shape
    x = np.arange(1,CC+1,1)
    y = np.arange(1,LL+1,1)
    
    xx_range,yy_azimuth = np.meshgrid(x,y)
    DR = xx_range - int(RANGE)
    DA = yy_azimuth - int(AZIMUTH)
    DD = (DR**2 + DA**2)**0.5

    IDX = np.where(MASK==0)
    DD[IDX] = 999999
    LL,CC = np.where(DD==DD.min())  
    MM = DD.min()
    NN= len(LL)
    return MM,LL[0],CC[0],NN
    
###################################################################################################

INTRODUCTION = '''
    Compare InSAR results and GPS results both for atmospheric delays and deformations.
    
    GPS stations are searched from Nevada Geodetic Laboratory by using search_gps.py 
    website:  http://geodesy.unr.edu/NGLStationPages/gpsnetmap/GPSNetMap.html
   
'''

EXAMPLE = '''EXAMPLES:
    gps_vs_insar.py UnwrapImage width gps_coord.txt -m RefDate -s slaveDate -r RefGPS --Atm --Def
    gps_vs_insar.py UnwrapImage width gps_coord.txt -m RefDate -s slaveDate --Atm --Def

    gps_vs_insar.py 20150101_20150123.filt_diff.unw 3229 -t gps_coord.txt -m 20100101 -s 20110101 -r 7ODM --Atm
    gps_vs_insar.py 20150101_20150123.filt_diff.unw 3229 -t gps_coord.txt -m 20100101 -s 20110101 -r 7ODM --Atm --Def
    gps_vs_insar.py 20150101_20150123.filt_diff.unw 3229 -t gps_coord.txt --Atm
    gps_vs_insar.py 20150101_20150123.filt_diff.unw 3229 --Def --Atm

'''    
    

def cmdLineParse():
    parser = argparse.ArgumentParser(description='Compare InSAR results and GPS results both for APS and deformation.',\
                                     formatter_class=argparse.RawTextHelpFormatter,\
                                     epilog=INTRODUCTION+'\n'+EXAMPLE)

    parser.add_argument('UNW',help='unwrapped interferograms.')
    parser.add_argument('width',help='width of the unwrap image.')
    parser.add_argument('-m', dest = 'master', help='Master date of interferograms.')
    parser.add_argument('-s', dest = 'slave', help='Slave date of interferograms.')
    parser.add_argument('-r','--RefGPS', dest = 'ref_gps',  help='Referenced GPS station.')
    parser.add_argument('--max_dist', dest = 'max_dist',  help='maximum search radius of InSAR results.')
    parser.add_argument('--diff_atm', dest = 'diff_atm',  help='differential file of GPS ASP results.')
    parser.add_argument('--diff_def', dest = 'diff_def',  help='differential file of GPS Def results.')
    parser.add_argument('-t','--trans',dest='gps_coord',  help='GPS coordinates transfomration file.')
    parser.add_argument('--byteorder', dest = 'byteorder', help='byte order of the unwrap image.')
    parser.add_argument('--Atm',action="store_true", default=False, help='Comparing APS results of InSAR and GPS.')
    parser.add_argument('--Def', action="store_true", default=False, help='Comparing DEF results of InSAR and GPS.')
    
    inps = parser.parse_args()
        
    if not inps.Atm and not inps.Def:
        parser.print_usage()
        sys.exit(os.path.basename(sys.argv[0])+': error: Comparison of Atm and Def, at least one is needed.')

    return inps

    
####################################################################################################
def main(argv):
    
    inps = cmdLineParse()
    UNW = inps.UNW
    WIDTH = inps.width
    UNW_NM = os.path.basename(UNW)
    
    if inps.gps_coord:  GPS_COORD = inps.gps_coord
    else: GPS_COORD = 'gps_coord.txt'
        
    if not os.path.isfile(GPS_COORD):
        parser.print_usage()
        sys.exit(os.path.basename(sys.argv[0])+': error: GPS coordinates transformation file is not found.')
    
    if inps.byteorder: Byteorder = inps.byteorder
    else: Byteorder ='big'
        
    if inps.max_dist: Max_Dist = inps.max_dist
    else: Max_Dist = 5        # default maximun search radius is 4 pixel.    
    
    
    SIZE = os.path.getsize(UNW)
    LENGTH = int(int(SIZE)/int(WIDTH)/4)
    
    if Byteorder == 'big': dtype = '>f4'
    else: dtype = '<f4'
    
    InSAR_Data = read_data(UNW,dtype,WIDTH,LENGTH)
    GPS_INFO = np.loadtxt(GPS_COORD,dtype=np.str)
    GPS_NM = GPS_INFO[:,0]
    GPS_NM = GPS_NM.tolist()
    GPS_LAT = GPS_INFO[:,1]
    GPS_LON = GPS_INFO[:,2]
    GPS_RANGE = GPS_INFO[:,3]
    GPS_AZIMUTH = GPS_INFO[:,4]
  
    
    if inps.Atm:
        if inps.master: Master = inps.master
        else: Master = UNW_NM.split('-')[0]
        Master = unitdate(Master)
    
        if inps.slave: Master = inps.master
        else: Slave = UNW_NM.split('-')[1].split('_')[0]
        Slave = unitdate(Slave)
        
        if inps.diff_atm: DIFF_ATM = inps.diff_atm
        else: 
            DIFF_ATM = 'diff_atm_' + Master + '-' + Slave
        
        if not os.path.isfile(DIFF_ATM):
            call_str = 'diff_gps_space.py ' + Master + ' -d ' + Slave + ' --Atm'
            os.system(call_str)
        
        GPS = np.loadtxt(DIFF_ATM,dtype=np.str)
        NM = GPS[:,0]
        LAT = GPS[:,1]
        LON = GPS[:,2]
        GPS_ZTD = GPS[:,3]
        GPS_STD = GPS[:,4]
        
        N =len(NM)
        
        DIST_ATM = []
        RANGE_ATM = []
        AZIMUTH_ATM = []
        NUMBER_ATM = []
        NM_ATM = []
        ZTD_ATM = []
        STD_ATM = []
        LAT_ATM = []
        LON_ATM = []
        
        for j in range(N):
                #print_progress(j+1, N, prefix='Station name: ', suffix = NM[j])
                idx = GPS_NM.index(NM[j])
                RANGE = GPS_RANGE[idx]
                AZIMUTH = GPS_AZIMUTH[idx]
                XX= min_dist(InSAR_Data,RANGE,AZIMUTH)
                STR = NM[j]
                print_progress(j+1, N, prefix='Station name: ', suffix = STR)
                DD = float(XX[0])
                if DD< Max_Dist:
                    NM_ATM.append(NM[j])
                    DIST_ATM.append(XX[0])
                    AZIMUTH_ATM.append(XX[1])
                    RANGE_ATM.append(XX[2])
                    NUMBER_ATM.append(XX[3])
                    ZTD_ATM.append(GPS_ZTD[j])
                    STD_ATM.append(GPS_STD[j])
                    LAT_ATM.append(LAT[j])
                    LON_ATM.append(LON[j])
                    
        if inps.ref_gps:
            REF_NM = inps.ref_gps
            if REF_NM in NM_ATM:
                IDX = NM_ATM.index(REF_NM)
                print 'Referenced GPS station is: %s' % REF_NM
            else:
                print 'Provided GPS station has been masked (i.e., has no InSAR results)!!'
                IDX = 0
                REF_NM = NM_ATM[0]
                print 'GPS station %s is chosen as the referenced point!!' % NM_ATM[0]
        else:
            IDX = 0
            REF_NM = NM_ATM[0]
        
        REF_RANGE = int(RANGE_ATM[IDX])
        REF_AZIMUTH =int(AZIMUTH_ATM[IDX])
        
        InSAR = InSAR_Data
        InSAR = InSAR - InSAR[REF_AZIMUTH][REF_RANGE]
        InSAR = -InSAR
        
        ZTD_ATM = map(float,ZTD_ATM)
        ZTD_ATM = np.asarray(ZTD_ATM)
        GPS0 = ZTD_ATM - ZTD_ATM[IDX]
        N =len(NM_ATM)
        
        SS =STD_ATM
        for i in range(N):
            STD_ATM[i] = (float(SS[i])**2 + float(SS[IDX])**2)**0.5
        STD_ATM[IDX] =0
        
        ATM_TXT = Master + '-' + Slave + '_InSAR_GPS_ATM_' + REF_NM
        if os.path.isfile(ATM_TXT):
            os.remove(ATM_TXT)
        
        for i in range(N):
            STR = str(NM_ATM[i]) + ' ' + str(LAT_ATM[i]) + ' ' + str(LON_ATM[i]) + ' ' + str(RANGE_ATM[i]) + ' ' + str(AZIMUTH_ATM[i]) + ' ' + str(InSAR[AZIMUTH_ATM[i]][RANGE_ATM[i]]/4/np.pi*0.056) + ' ' + str(GPS0[i]) + ' ' + str(STD_ATM[i]) + ' ' + str(DIST_ATM[i]) + ' ' + str(NUMBER_ATM[i])

            call_str = 'echo ' + STR + ' >> '  + ATM_TXT
            os.system(call_str) 
            
            
############################## deformation comparison #########################################

    if inps.Def:
        if inps.master: Master = inps.master
        else: Master = UNW_NM.split('-')[0]
        Master = unitdate(Master)
  
        if inps.slave: Slave = inps.slave
        else: Slave = UNW_NM.split('-')[1].split('_')[0]
        Slave = unitdate(Slave)
        
        if inps.diff_def: DIFF_DEF = inps.diff_def
        else:   
            DIFF_DEF = 'diff_def_' + Master + '-' + Slave
            
        if not os.path.isfile(DIFF_DEF):
            call_str = 'diff_gps_space.py ' + Master + ' -d ' + Slave + ' --Def'
            os.system(call_str)    
            
        GPS = np.loadtxt(DIFF_DEF,dtype=np.str)
        NM = GPS[:,0]
        LAT = GPS[:,1]
        LON = GPS[:,2]
        GPS_DEF = GPS[:,3]
        GPS_STD = GPS[:,4]
        
        N =len(NM)
        
        DIST_DEF = []
        RANGE_DEF = []
        AZIMUTH_DEF = []
        NUMBER_DEF = []
        NM_DEF = []
        ZTD_DEF = []
        STD_DEF = []
        LAT_DEF = []
        LON_DEF = []
        
        for j in range(N):
                print_progress(j+1, N, prefix='Station name: ', suffix=NM[j])
                
                if NM[j] in GPS_NM:
                    idx = GPS_NM.index(NM[j])
                    RANGE = GPS_RANGE[idx]
                    AZIMUTH = GPS_AZIMUTH[idx]
                    XX= min_dist(InSAR_Data,RANGE,AZIMUTH)
                    DD = float(XX[0])
                    if DD< Max_Dist:
                        NM_DEF.append(NM[j])
                        DIST_DEF.append(XX[0])
                        RANGE_DEF.append(XX[2])
                        AZIMUTH_DEF.append(XX[1])
                        NUMBER_DEF.append(XX[3])
                        ZTD_DEF.append(GPS_DEF[j])
                        STD_DEF.append(GPS_STD[j])
                        LAT_DEF.append(LAT[j])
                        LON_DEF.append(LON[j])
                    
        if inps.ref_gps:
            REF_NM = inps.ref_gps
            if REF_NM in NM_DEF:
                IDX = NM_DEF.index(REF_NM)
                print 'Referenced GPS station is: %s' % REF_NM
            else:
                print 'Provided GPS station has been masked (i.e., has no InSAR results)!!'
                IDX = 0
                REF_NM = NM_DEF[0]
                print 'GPS station %s is chosen as the referenced point!!' % NM_DEF[0]
        else:
            IDX = 0
            REF_NM = NM_DEF[0]
        
        REF_RANGE = int(RANGE_DEF[IDX])
        REF_AZIMUTH =int(AZIMUTH_DEF[IDX])
        
        InSAR = InSAR_Data
        InSAR = InSAR - InSAR[REF_AZIMUTH][REF_RANGE]
        
        ZTD_DEF = map(float,ZTD_DEF)
        ZTD_DEF = np.asarray(ZTD_DEF)
        GPS0 = ZTD_DEF - ZTD_DEF[IDX]
        N =len(NM_DEF)
        
        for i in range(N):
            STD_DEF[i] = (float(STD_DEF[i])**2 + float(STD_DEF[IDX])**2)**0.5
        STD_DEF[IDX] =0
        
        DEF_TXT = Master + '-' + Slave + '_InSAR_GPS_DEF_' + REF_NM
        if os.path.isfile(DEF_TXT):
            os.remove(DEF_TXT)
        
        for i in range(N):
            if (-1<int(AZIMUTH_DEF[i]) and int(AZIMUTH_DEF[i])< int(LENGTH)) and (-1<int(RANGE_DEF[i]) and int(RANGE_DEF[i])<int(WIDTH)):
                STR = str(NM_DEF[i]) + ' ' + str(LAT_DEF[i]) + ' ' + str(LON_DEF[i]) + ' ' + str(RANGE_DEF[i]) + ' ' + str(AZIMUTH_DEF[i]) + ' ' + str(InSAR[AZIMUTH_DEF[i]][RANGE_DEF[i]]/4/np.pi*0.056) + ' ' + str(GPS0[i]) + ' ' + str(STD_DEF[i]) + ' ' + str(DIST_DEF[i]) + ' ' + str(NUMBER_DEF[i])
                call_str = 'echo ' + STR + ' >> '  + DEF_TXT
                os.system(call_str) 
    

    
    


if __name__ == '__main__':
    main(sys.argv[1:])

