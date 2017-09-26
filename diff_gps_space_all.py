#! /usr/bin/env python
############################################################
# Program is part of PyGPS v1.0                            #
# Copyright(c) 2017, Yunmeng Cao                           #
# Author:  Yunmeng Cao                                     #
############################################################


import numpy as np
import getopt
import glob
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

INTRODUCTION = '''Generating differential GPS-based deformations and tropospheric delays.

'''

EXAMPLE = '''EXAMPLES:

    diff_gps_space_all.py projectName --Atm --Def
    diff_gps_space_all.py LosAngelesT71F479S1D  --Def
    diff_gps_space_all.py LosAngelesT71F479S1D  --Atm

'''    
    

def cmdLineParse():
    parser = argparse.ArgumentParser(description='Download GPS data over SAR coverage.',\
                                     formatter_class=argparse.RawTextHelpFormatter,\
                                     epilog=INTRODUCTION+'\n'+EXAMPLE)

    parser.add_argument('projectName',help='Name of project.')
    parser.add_argument('--Atm',action="store_true", default=False, help='Geting SAR LOS tropospheric delay.')
    parser.add_argument('--Def', action="store_true", default=False, help='Getting SAR LOS deformation.')
    
    inps = parser.parse_args()


    return inps

    
####################################################################################################
def main(argv):
    
    inps = cmdLineParse()
    projectName = inps.projectName
    
    scratchDir = os.getenv('SCRATCHDIR')
    templateDir = os.getenv('TEMPLATEDIR')
    DEMDIR = os.getenv('DEMDIR')
    templateFile = templateDir + "/" + projectName + ".template"
    
    projectDir = scratchDir + '/' + projectName
    processDir = scratchDir + '/' + projectName + "/PROCESS"
    IFGLIST = glob.glob(processDir+'/*_' +projectName + '_*') 
    atmDir = projectDir + '/GPS/ATM'
    defDir = projectDir + '/GPS/DEF'
    
    for kk in IFGLIST:
      
        ks = os.path.basename(kk)
        print 'Processing for interferogram %s.' % ks
        
        IFGPair = ks.split(projectName+'_')[1].split('_')[0]
        Mdate = IFGPair.split('-')[0]
        Sdate = IFGPair.split('-')[1]
        
        if inps.Atm:
            os.chdir(atmDir)
            call_str = 'diff_gps_space.py ' + Mdate + ' -d ' + Sdate + ' --Atm'
            os.system(call_str)
        
        if inps.Def:
            os.chdir(defDir)
            call_str = 'diff_gps_space.py ' + Mdate + ' -d ' + Sdate + ' --Def'
            os.system(call_str)
            
        if (not inps.Atm) and (not inps.Def):   
            os.chdir(atmDir)
            call_str = 'diff_gps_space.py ' + Mdate + ' -d ' + Sdate + ' --Atm'
            os.system(call_str)
            
            os.chdir(defDir)
            call_str = 'diff_gps_space.py ' + Mdate + ' -d ' + Sdate + ' --Def'
            os.system(call_str)
        
    sys.exit(1)   
    print 'Generate differential GPSresults for project %s done.' % projectName        
    

if __name__ == '__main__':
    main(sys.argv[1:])

