#! /usr/bin/env python
############################################################
# Program is part of PyGPS v2.0                            #
# Copyright(c) 2017-2019, Yunmeng Cao                      #
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
    
def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass
 
    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass
 
    return False    
    
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
    h0 = str(hh)
    return ST,h0

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

INTRODUCTION = '''
    Extract the SAR synchronous GPS tropospheric products.
'''

EXAMPLE = '''EXAMPLES:

    extract_sar_atm.py search_gps.txt imaging_time
    extract_sar_atm.py search_gps.txt imaging_time --date 20180101
    extract_sar_atm.py search_gps.txt imaging_time --date_txt date_list.txt

'''    
    


def cmdLineParse():
    parser = argparse.ArgumentParser(description='Extract the SAR synchronous GPS tropospheric products.',\
                                     formatter_class=argparse.RawTextHelpFormatter,\
                                     epilog=INTRODUCTION+'\n'+EXAMPLE)

    parser.add_argument('gps_txt',help='GPS station text file.')
    parser.add_argument('imaging_time',help='Center line UTC sec.')
    parser.add_argument('-d', '--date', dest='date_list', nargs='*',help='date list to extract.')
    parser.add_argument('--date-txt', dest='date_txt',help='date list text to extract.')
    
    inps = parser.parse_args()

    return inps

    
####################################################################################################
def main(argv):
    
    inps = cmdLineParse()
    date_list = []
    if inps.date_list:
        date_list = inps.date_list
    if inps.date_txt:
        date_list2 = np.loadtxt(inps.date_txt,dtype=np.str)
        date_list2 = date_list2.tolist()
        for list0 in date_list2:
            if (list0 not in date_list) and is_number(list0):
                date_list.append(list0)
    
    path0 = os.getcwd()
    gps_dir = path0 + '/GPS/atm'
    
    if (not inps.date_txt) and (not inps.date_list):
        print('Obtain the GPS data-date automatically from %s' % gps_dir)
        date_list = [os.path.basename(x).split('_')[3] for x in glob.glob(gps_dir + '/Global_GPS_Trop*')]
        
    date_list = list(map(int, date_list))
    date_list = sorted(date_list)
    N = len(date_list)
    print('---------------------------------------')
    print('Total number of extracted date: %s ' % str(len(date_list)))
    for k0 in date_list:
        print(k0)
    #print('---------------------------------------')
    
    t0 = inps.imaging_time
    SST,HH = yyyy2yyyymmddhhmmss(float(t0))
    t0 =float(t0)/3600/24
    t0 = float(t0)*24*12
    t0 = round(t0)
    t0 = t0 * 300
    
    hh0 = float(t0)/3600
    HH0 = int(round(float(hh0)/2)*2)
    Tm =str(int(t0))
    
    GPS = np.loadtxt(inps.gps_txt, dtype = np.str)
    DD = GPS[:,0]
    k=len(DD)
    DD.tolist()
    
    print('---------------------')
    print('Extract Tropospheric Delays: ')
    for i in range(N):
        #print('---------------------')
        #print('Job of Extract Tropospheric Delays: ' + str(int(i+1)) + '/' + str(int(N)))
        DATE0 = str(date_list[i])
        DATE0 = unitdate(DATE0)
        
        dt = dateutil.parser.parse(DATE0)
        time = astropy.time.Time(dt)
        JD = time.jd - 2451545.0
        JDSEC = JD*24*3600        
        JDSEC_SAR = int(JDSEC + t0)
        
        Trop_GPS = gps_dir + '/Global_GPS_Trop_' + str(DATE0)
        Trop_SAR = gps_dir + '/SAR_GPS_Trop_' + str(DATE0)
        tt_all = 'tt_' + str(DATE0)
        tt_name = 'tt_name_' + str(DATE0)
        
        if os.path.isfile(Trop_SAR):
            if os.path.getsize(Trop_SAR)==0:
                os.remove(Trop_SAR)
        
        if not os.path.isfile(Trop_GPS):
            #print('% is not found.' % Trop_GPS)
            #SSS = DATE0 + '[No]'
            SSS = DATE0 + ' [No ' + str(int(i+1)) + '/' + str(int(N)) + ']'
            print_progress(i+1, N, prefix='Date: ', suffix=SSS)
        elif os.path.isfile(Trop_SAR):
            SSS = DATE0 + ' [Yes ' + str(int(i+1)) + '/' + str(int(N)) + ']'
            print_progress(i+1, N, prefix='Date: ', suffix=SSS)
        else:
            #SSS = DATE0 + '[Yes]'
            SSS = DATE0 + ' [Yes ' + str(int(i+1)) + '/' + str(int(N)) + ']'
            print_progress(i+1, N, prefix='Date: ', suffix=SSS)
            Trop_SAR = gps_dir + '/SAR_GPS_Trop_' + str(DATE0)
            # remove the first four lines
            count = len(open(Trop_GPS,'r').readlines())
            call_str = 'sed -n 5,' + str(count) + 'p ' +  Trop_GPS + ' >' + tt_all
            os.system(call_str)
            # extract all of the available station names
            call_str = "awk '{print $10}' " + tt_all + ' >' + tt_name
            os.system(call_str)
            
            GPS_all = np.loadtxt(tt_name, dtype = np.str)
            DD_all = GPS_all
            k_all=len(DD_all)
            #print(k_all)
            DD_all.tolist()
        
            RR = np.zeros((k_all,),dtype = bool)
            for i in range(k_all):
                k0 = DD_all[i]
                if k0 in DD:
                    RR[i] = 1
        
            data = np.loadtxt(tt_all, dtype = np.str)
            data_use = data[RR]
            #print(data_use.shape)
        
            JDSEC_all = data_use[:,0]
            #JDSEC_all = np.asarray(JDSEC_all,dtype = int)
            nn = len(JDSEC_all)
            RR2 = np.zeros((nn,),dtype = bool)
            for i in range(nn):
                #print(int(float(JDSEC_all[i])))
                if int(float(JDSEC_all[i])) == JDSEC_SAR:
                    RR2[i] =1

            data_use_final = data_use[RR2]
            #print(data_use_final.shape)     
            np.savetxt(Trop_SAR,data_use_final,fmt='%s', delimiter=',')    
            os.remove(tt_all)
            os.remove(tt_name)
        
    print('---------------------')
    print('Extract Atmospheric PWV: ')    
    ## Extract PWV data ####     
    for i in range(N):
        #print('---------------------')
        #print('Extract Atmospheric PWV: ' + str(int(i+1)) + '/' + str(int(N)))
        DATE0 = str(date_list[i])
        DATE0 = unitdate(DATE0)
        PWV_GPS = gps_dir + '/Global_GPS_PWV_' + str(DATE0)
        PWV_SAR = gps_dir + '/SAR_GPS_PWV_' + str(DATE0)
        if os.path.isfile(PWV_SAR):
            if os.path.getsize(PWV_SAR)==0:
                os.remove(PWV_SAR)
                
        if not os.path.isfile(PWV_GPS):
            #print('% is not found.' % PWV_GPS)
            SSS = DATE0 + ' [No ' + str(int(i+1)) + '/' + str(int(N)) + ']'
            print_progress(i+1, N, prefix='Date: ', suffix=SSS)
        elif os.path.isfile(PWV_SAR):
            SSS = DATE0 + ' [Yes ' + str(int(i+1)) + '/' + str(int(N)) + ']'
            print_progress(i+1, N, prefix='Date: ', suffix=SSS)
        else:
            SSS = DATE0 + ' [Yes ' + str(int(i+1)) + '/' + str(int(N)) + ']'
            print_progress(i+1, N, prefix='Date: ', suffix=SSS)

            tt_all = 'tt_' + str(DATE0)
            tt_name = 'tt_name_' + str(DATE0)
            
            count = len(open(PWV_GPS,'r').readlines())
            call_str = 'sed -n 2,' + str(count) + 'p ' +  PWV_GPS + ' >' + tt_all
            os.system(call_str)
            # extract all of the available station names
            call_str = "awk '{print $18}' " + tt_all + ' >' + tt_name
            os.system(call_str)
            
            GPS_all = np.loadtxt(tt_name, dtype = np.str)
            DD_all = GPS_all
            k_all=len(DD_all)
            #print(k_all)
            DD_all.tolist()
            
            data = np.loadtxt(tt_all, dtype = np.str)
            row,col = data.shape
            RR = np.zeros((row,),dtype = bool)
            for i in range(row):
                k0 = DD_all[i]
                if k0 in DD:
                    RR[i] = 1
            data_use = data[RR]
            #print(data_use.shape)
            HH_all = data_use[:,2]
            nn = len(HH_all)
            RR2 = np.zeros((nn,),dtype = bool)
            for i in range(nn):
                if int(float(HH_all[i])) == HH0:
                    RR2[i] =1

            data_use_final = data_use[RR2]
            #print(data_use_final.shape)     
            np.savetxt(PWV_SAR,data_use_final,fmt='%s', delimiter=',')  
            os.remove(tt_all)
            os.remove(tt_name)
            
    print('Done.')     
    sys.exit(1)        

if __name__ == '__main__':
    main(sys.argv[1:])

