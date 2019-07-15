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
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit


def Nm2h(gps_txt,Nm):
    GPS= np.loadtxt(gps_txt, dtype = np.str)
    GPS_Nm =GPS[:,0]
    GPS_Nm = GPS_Nm.tolist()
    GPS_HEI = GPS[:,3]
    N=len(Nm)
    h = []
    for i in range(N):
        h0=GPS_HEI[GPS_Nm.index(Nm[i])]
        h.append(float(h0))
    
    h=list(map(float,h))
    h=[k/1000.0 for k in h]        
    return h

def fit_linear(h,y):
    
    def linear(x,a,b):
        return a*x+b
    
    popt, pcov = curve_fit(linear, h, y)
    a=popt[0]#popt
    b=popt[1]
    
    yvals=[kk*a+b for kk in h]
    res = np.array(y) - np.array(yvals)
    ss_res = np.sum(res**2)
    ss_tot = np.sum((y-np.mean(y))**2)
    r_squre = 1-(ss_res/ss_tot)    
    return a,b,r_squre**0.5

def get_data(gps_txt,date):
    call_str = 'grep ' + "'" + date+':' + "'" + ' -C 0 * >ttt'
    os.system(call_str)
    count = len(open('ttt','rU').readlines())
    
    if count > 10:
        GPS_ATM= np.loadtxt('ttt', dtype = np.str)
        GPS_Nm_Atm =GPS_ATM[:,1]
        GPS_Nm_Atm = GPS_Nm_Atm.tolist()
        GPS_Atm_Ts = GPS_ATM[:,3]
        GPS_Atm_Ts = GPS_Atm_Ts.tolist()
    
        y=list(map(float,GPS_Atm_Ts))
        y=[k/10.0 for k in y]
        y=list(map(float,y))  
    else: 
        GPS_Nm_Atm=''
        y=''
    return GPS_Nm_Atm,y
    

def model_para_date(gps_txt,date):
    Nm,y=get_data(gps_txt,date)
    if len(Nm)>10:
        Nm0=[]
        h = Nm2h(gps_txt,Nm)
        a,b,r = fit_linear(h,y)
        NN =len(y)
        pp =str(date)+ ' ' + str(a)+' ' + str(b) + ' ' + str(r) + ' ' + str(NN) + '\n'
        yvals=[kk*a+b for kk in h]
        res = np.array(y) - np.array(yvals)
        
        for i in range(len(Nm)):
            ST0 = Nm[i]+':Res:'+date
            Nm0.append(ST0)
        
    else:
        pp=''
        res=''
        Nm0=''
    return pp,res,Nm0
    
    
def unitday(dd):
    LE = len(str(int(dd)))
    DAY = str(int(dd))
    
    if LE==1:
        DAY = '00' + DAY 
    if LE == 2:
        DAY = '0' + DAY 
    return DAY

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
        
#######################################################################################

INTRODUCTION = '''
    Searching available GPS stations over the research region.
    
    Global GPS stations are referred the GPSNetMap of Nevada Geodetic Laboratory
    Details can be found from http://geodesy.unr.edu/NGLStationPages/gpsnetmap/GPSNetMap.html

'''


EXAMPLE = '''EXAMPLES:
    ts_topo_corr_model.py -f search_gps.txt -s 2018-001 -e 2018-110
    ts_topo_corr_model.py -f search_gps.txt -d 2018-001 -e 2018-110 -o LA_Linear_Para

'''


def cmdLineParse():
    parser = argparse.ArgumentParser(description='Download GPS data over SAR coverage.',\
                                     formatter_class=argparse.RawTextHelpFormatter,\
                                     epilog=INTRODUCTION+'\n'+EXAMPLE)

    parser.add_argument('-f',dest='file', help='gps station file')
    parser.add_argument('-s', dest='start',help='fitting date')
    parser.add_argument('-e', dest='end', help='topography model.')
    parser.add_argument('-o', dest='out', help='output parameters of the topo-model')
    
    inps = parser.parse_args()
    
    if not inps.file and not inps.start:
        parser.print_usage()
        sys.exit(os.path.basename(sys.argv[0])+': error: h5file or coverage box at least one should be provided.')

    

    return inps

################################################################################################


def main(argv):
    
    inps = cmdLineParse()
    gps_txt = inps.file
    GPS= np.loadtxt(gps_txt, dtype = np.str)
    GPS_Nm =GPS[:,0]
    GPS_Nm = GPS_Nm.tolist()
    N0 = len(GPS_Nm)
 
    Start_Date = inps.start
    End_Date = inps.end
    
    Start_Year = int(Start_Date.split('-')[0])
    Start_Day = int(Start_Date.split('-')[1])
    
    End_Year = int(End_Date.split('-')[0])
    End_Day = int(End_Date.split('-')[1])
    
    if inps.out:
        OUT = inps.out
    else:
        OUT = 'Model_Linear_TXT'
    
    f_res = open('RES_Trop','a')
    f = open(OUT,'a')
    for i in range(Start_Year,End_Year+1):        
        print('Start to estimate spatial model parameters of atmospheric delay: ' + str(i))
        
                
        #if Start_Year==End_Year:
        #    k1= Start_Day 
        #else:
        #    k1=1
            
        if i==End_Year:
            k0 = End_Day
        else:
            k0 = 366
        Nm = str(i)

        
        for j in range(k0):
            N = k0
            dd=str(int(j+1))
            day = unitday(dd)
            print_progress(j+1, N, prefix='Year: ', suffix=Nm)
            yy=str(i)
            yy=yy[2:4]
            
            date_str=yy+':'+day
            #print date_str
            SS,res0,Nm0=model_para_date(gps_txt,date_str)
            #print SS
            NR = len(res0)
            for ki in range(NR):
                STR00 = Nm0[ki]+' ' + str(res0[ki])+'\n'
                f_res.write(STR00)
            f.write(SS)         
        
    f.close()
    f_res.close()
    
  
    
    for i in range(N0):
        SN = GPS_Nm[i]+'_TS_Trop_Res'
        SN_str = GPS_Nm[i]+':Res:'
        call_str = 'grep ' + "'" + SN_str + "'" + ' -C 0  RES_Trop >ttt0'
        os.system(call_str)
        
        call_str="awk -F: '{print $3,$4,$5}' ttt0 >" + SN
        os.system(call_str)
        
        
           
if __name__ == '__main__':
    main(sys.argv[1:])