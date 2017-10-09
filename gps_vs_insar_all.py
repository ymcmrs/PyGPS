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
    
    if LE ==5:
        DATE ='200' + DATE
    
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

def UseGamma(inFile, task, keyword):
    if task == "read":
        f = open(inFile, "r")
        while 1:
            line = f.readline()
            if not line: break
            if line.count(keyword) == 1:
                strtemp = line.split(":")
                value = strtemp[1].strip()
                return value
        print "Keyword " + keyword + " doesn't exist in " + inFile
        f.close()    
###################################################################################################

INTRODUCTION = '''
    Generate GPS & InSAR compared results for the whole project.
'''

EXAMPLE = '''EXAMPLES:

    gps_vs_insar_all.py LosAngelesT71F479S1D
    
'''    
    

def cmdLineParse():
    parser = argparse.ArgumentParser(description='Compare InSAR results and GPS results both for APS and deformation.',\
                                     formatter_class=argparse.RawTextHelpFormatter,\
                                     epilog=INTRODUCTION+'\n'+EXAMPLE)

    parser.add_argument('projectName',help='Name of project.')
    parser.add_argument('--noramp',action="store_true", default=False,help='Interferograms does has no ramp.')
    parser.add_argument('--width',dest='width',help='width of unwrapped image.')
    
    inps = parser.parse_args()
        
    return inps

    
####################################################################################################
def main(argv):
    
    inps = cmdLineParse()
    projectName = inps.projectName
    if inps.noramp: RAMP ='.quad_fit'
    else: RAMP =''
    
    scratchDir = os.getenv('SCRATCHDIR')
    processDir = scratchDir + '/' + projectName + "/PROCESS"
    GPSDIR = scratchDir + '/' + projectName + "/GPS"
    GPSCOORD = GPSDIR + '/gps_coord.txt'
    ATMDIR = scratchDir + '/' + projectName + "/GPS/ATM"
    DEFDIR = scratchDir + '/' + projectName + "/GPS/DEF"
    VSDIR = scratchDir + '/' + projectName + "/GPS/GPS_VS_INSAR"
    
    if not os.path.isdir(ATMDIR):
        print 'No GPS-based atmmosphere folder is found. Start to generate by using download_gps_atm_all.py.'
        call_str ='download_gps_atm_all.py ' + projectName
        os.system(call_str)
        
    if not os.path.isdir(DEFDIR):
        print 'No GPS-based deformation folder is found. Start to generate by using download_gps_def_all.py.'
        call_str ='download_gps_def_all.py ' + projectName
        os.system(call_str)
    
    if not os.path.isdir(VSDIR):
        call_str='mkdir ' + VSDIR
        os.system(call_str)
    
    IFG_list = glob.glob(processDir + '/IFG*')
    UNW_list = glob.glob(processDir + '/IFG*/*rlks' + RAMP + '.unw')
    
    if inps.width:
        WIDTH = inps.width
    else:
        WIDTH = []
        DIFF_PAR_LIST = glob.glob(processDir + '/IFG*/*.diff_par')
        for kk in DIFF_PAR_LIST:
            W0 = UseGamma(kk, 'read', 'range_samp_1:')
            #W1 = UseGamma(kk, 'read', 'az_samp_1:')    
            W0 = str(int(W0))
            #print kk + ' ' + W0 + ' ' + W1
            
            WIDTH.append(W0)
   
    os.chdir(VSDIR)
    run_gps_vs_insar = VSDIR + '/run_gps_vs_insar'
    if os.path.isfile(run_gps_vs_insar):
        os.remove(run_gps_vs_insar)
        
    for kk in range(len(UNW_list)):
        igramDir = os.path.basename(os.path.dirname(UNW_list[kk]))
        IFGPair = igramDir.split(projectName+'_')[1].split('_')[0]
        Mdate = IFGPair.split('-')[0]
        Sdate = IFGPair.split('-')[1]
        
        if inps.width:
            call_str = 'echo gps_vs_insar.py ' + UNW_list[kk] + ' ' + WIDTH + ' -t ' + GPSCOORD + ' -m ' + Mdate + ' -s ' + Sdate + ' --Atm --Def --AtmDir ' + ATMDIR + ' --DefDir ' + DEFDIR + ' >>' + run_gps_vs_insar
        else:
            call_str = 'echo gps_vs_insar.py ' + UNW_list[kk] + ' ' + WIDTH[kk] + ' -t ' + GPSCOORD + ' -m ' + Mdate + ' -s ' + Sdate + ' --Atm --Def --AtmDir ' + ATMDIR + ' --DefDir ' + DEFDIR + ' >>' + run_gps_vs_insar
        os.system(call_str)
            
    call_str='$INT_SCR/createBatch.pl ' + run_gps_vs_insar + ' memory=3700 '  + ' walltime=0:30'
    os.system(call_str)       
            
               
    
    

if __name__ == '__main__':
    main(sys.argv[1:])

