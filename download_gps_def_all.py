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

def check_variable_name(path):
    s=path.split("/")[0]
    if len(s)>0 and s[0]=="$":
        p0=os.getenv(s[1:])
        path=path.replace(path.split("/")[0],p0)
    return path

def read_template(File, delimiter='='):
    '''Reads the template file into a python dictionary structure.
    Input : string, full path to the template file
    Output: dictionary, pysar template content
    Example:
        tmpl = read_template(KyushuT424F610_640AlosA.template)
        tmpl = read_template(R1_54014_ST5_L0_F898.000.pi, ':')
    '''
    template_dict = {}
    for line in open(File):
        line = line.strip()
        c = [i.strip() for i in line.split(delimiter, 1)]  #split on the 1st occurrence of delimiter
        if len(c) < 2 or line.startswith('%') or line.startswith('#'):
            next #ignore commented lines or those without variables
        else:
            atrName  = c[0]
            atrValue = str.replace(c[1],'\n','').split("#")[0].strip()
            atrValue = check_variable_name(atrValue)
            template_dict[atrName] = atrValue
    return template_dict

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

def is_number(s):
    try:
        int(s)
        return True
    except ValueError:
        return False        
        
###################################################################################################

INTRODUCTION = '''Download GPS displacements data for every SAR acquisitions.
    
'''

EXAMPLE = '''EXAMPLES:
    download_gps_def_all.py projectName
    download_gps_def_all.py LosAngelesT71F479S1D

'''    
    


def cmdLineParse():
    parser = argparse.ArgumentParser(description='Download GPS data over SAR coverage.',\
                                     formatter_class=argparse.RawTextHelpFormatter,\
                                     epilog=INTRODUCTION+'\n'+EXAMPLE)

    parser.add_argument('projectName',help='Project name.')
    
    inps = parser.parse_args()

    return inps

    
####################################################################################################
def main(argv):
    
    inps = cmdLineParse()
    projectName = inps.projectName
    scratchDir = os.getenv('SCRATCHDIR')
    templateDir = os.getenv('TEMPLATEDIR')
    templateFile = templateDir + "/" + projectName + ".template"
    templateContents=read_template(templateFile)
    processDir = scratchDir + '/' + projectName + "/PROCESS"
    slcDir     = scratchDir + '/' + projectName + "/SLC"
    gpsDir     = scratchDir + '/' + projectName + "/GPS"
    defDir     = scratchDir + '/' + projectName + "/GPS/DEF"
    ListSLC = os.listdir(slcDir)
    
    if not os.path.isdir(gpsDir):
        call_str = 'mkdir ' + gpsDir
        os.system(call_str)

    if not os.path.isdir(atmDir):
        call_str = 'mkdir ' + atmDir
        os.system(call_str)
    
    os.chdir(defDir)
    
    
    datelist_txt = gpsDir + '/datelist_txt'
    if os.path.isfile(datelist_txt):
        os.remove(datelist_txt)
    Datelist = []
    for kk in range(len(ListSLC)):
        if ( is_number(ListSLC[kk]) and len(ListSLC[kk])==6 ):    #  if SAR date number is 8, 6 should change to 8.
            DD='20' + ListSLC[kk]
            Year=int(DD[0:4])
            Month = int(DD[4:6])
            Day = int(DD[6:8])
            if  ( 1990 < Year < 2020 and 0 < Month < 13 and 0 < Day < 32 ):            
                Datelist.append(DD)
                call_str = 'echo ' + DD + ' >>' + datelist_txt
                os.system(call_str)
    
    map(int,Datelist)                
    Datelist.sort()
    map(str,Datelist)
    Date1 = Datelist[0]
    Date1 = Date1[0:4] + '-' + Date1[4:6] + '-' + Date1[6:8]
    Date2 = Datelist[len(Datelist)-1]
    Date2 = Date2[0:4] + '-' + Date2[4:6] + '-' + Date2[6:8]
      
    if 'masterDate'          in templateContents:
        masterDate0 = templateContents['masterDate']
        if masterDate0 in Datelist:
            masterDate = masterDate0
            print "masterDate : " + masterDate0
        else:
            masterDate=Datelist[0]
            print "The selected masterDate is not included in above datelist !!"
            print "The first date [ %s ] is chosen as the master date! " % Datelist[0] 
            
    else:  
        masterDate=Datelist[0]
        print "masterDate is not found in template!!! "
        print "The first date [ %s ] is chosen as the master date! " % Datelist[0] 

    if len(masterDate) ==8:
        masterDate = masterDate[2:8]
    
    SLCPAR = slcDir + '/' + masterDate + '/' + masterDate + '.slc.par'
    Search_GPS = gpsDir + '/search_gps.txt'
    
    if not os.path.isfile(Search_GPS):
        call_str = 'search_gps.py ' + ' -t ' +SLCPAR + ' -s ' + Date1 + ' -e ' + Date2
        os.system(call_str)
    
        call_str = 'mv search_gps.txt ' + Search_GPS
        os.system(call_str)
    
    
    call_str = 'download_gps_def.py ' + Search_GPS + ' --datetxt ' + datelist_txt
    os.system(call_str)
    
    
    
    

if __name__ == '__main__':
    main(sys.argv[1:])

