#! /usr/bin/env python
############################################################
# Program is part of PyGPS v1.0                            #
# Copyright(c) 2017, Yunmeng Cao                           #
# Author:  Yunmeng Cao                                     #
############################################################


import os
import sys
import glob
import time
import argparse

import h5py
import numpy as np

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

def read_data(inFile, dtype, nWidth, nLength):
    data = np.fromfile(inFile, dtype, int(nLength)*int(nWidth)).reshape(int(nLength),int(nWidth)) 
    
    return data

def is_number(s):
    try:
        int(s)
        return True
    except ValueError:
        return False
    
def add_zero(s):
    if len(s)==1:
        s="000"+s
    elif len(s)==2:
        s="00"+s
    elif len(s)==3:
        s="0"+s
    return s


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

def read_h5(FILE):
    f = h5py.File(FILE,'r')
    kl1 = f.keys()[0]
    kl2 = f[kl1].keys()[0]
    data = f[kl1].get(kl2)[()]
    
    return data
    f.close()
    
#######################################################################################

INTRODUCTION = '''
    Transform GPS station coordinates (latitude and longitude) into radar coordinates.
    Lookup table and the relative dem_par should be provided. 

'''


EXAMPLE = '''EXAMPLES:

    gps_geometry_pymis.py search_gps.txt geo2rdc.h5 incidence head
    gps_geometry_pymis.py search_gps.txt geo2rdc.h5 incidence.h5 heading.h5
    gps_geometry_pymis.py search_gps.txt geo2rdc.h5 incidence.h5 160.2



'''


def cmdLineParse():
    parser = argparse.ArgumentParser(description='Transforming GPS coordinates into radar coordinates.',\
                                     formatter_class=argparse.RawTextHelpFormatter,\
                                     epilog=INTRODUCTION+'\n'+EXAMPLE)

    parser.add_argument('gps_txt',help='Available GPS station information.')
    parser.add_argument('geo2rdc', help='lookup table of coordinates transfomration.')
    parser.add_argument('inc', help='incidence file or value.')
    parser.add_argument('head',help='heading file or value.')
    
    inps = parser.parse_args()


    return inps

################################################################################################
        
def main(argv):
    
    inps = cmdLineParse()
    TXT = inps.gps_txt
    LT = inps.geo2rdc
    
    
    f_lt = h5py.File(LT,'r')
    kl1 = f_lt.keys()[0]
    kl2 = f_lt[kl1].keys()[0]
    
    data = f_lt[kl1].get(kl2)[()]
    atr_lt = f_lt[kl1].attrs 
    nWidthUTM = f_lt[kl1].attrs['WIDTH']
    nLineUTM = f_lt[kl1].attrs['FILE_LENGTH']
    
    Corner_LAT = f_lt[kl1].attrs['Y_FIRST']
    Corner_LON = f_lt[kl1].attrs['X_FIRST']
    post_Lat =f_lt[kl1].attrs['Y_STEP']
    post_Lon =f_lt[kl1].attrs['X_STEP']
    
    
    if os.path.isfile(inps.inc):
        DATA_INC = read_h5(inps.inc)
    else:
        INC = inps.inc
        
    if os.path.isfile(inps.head):
        DATA_HEAD = read_h5(inps.head)
    else:
        HEAD = inps.head
    
    
    
    
    OUT ='gps_geometry_par.txt'
        
    GPS= np.loadtxt(TXT, dtype = np.str)
    GPS_Nm =GPS[:,0]
    GPS_Nm = GPS_Nm.tolist()
    GPS_LAT = GPS[:,1]
    GPS_LON = GPS[:,2]
    GPS_HEI = GPS[:,3]

    N = len(GPS_Nm)     
    
    
    if os.path.isfile(OUT):
        os.remove(OUT)
        
    for i in range(N):
        LAT = GPS_LAT[i]
        LON = str(float(GPS_LON[i])-360)
        HEI = GPS_HEI[i]
        NM =GPS_Nm[i]
        XX = int (( float(LAT) - float(Corner_LAT) ) / float(post_Lat))  # latitude   width   range
        YY = int (( float(LON) - float(Corner_LON) ) / float(post_Lon))  # longitude   nline  azimuth
             
        CPX_OUT = data[XX][YY]    
        Range = int(CPX_OUT.real)
        Azimuth = int(CPX_OUT.imag)
        
        if os.path.isfile(inps.inc):
            INC = DATA_INC[Azimuth][Range]
        if os.path.isfile(inps.head):
            HEAD = DATA_HEAD[Azimuth][Range]
    
 
        STR = str(NM) + ' ' + str(float(LAT)) + ' ' + str(float(LON)) + ' ' + str(float(HEI)) + ' '  + str(Azimuth) + ' ' + str(Range) + ' '  + str(INC) + ' ' + str(HEAD) 
        call_str = 'echo ' + STR + ' >> ' + OUT
        os.system(call_str)
        
        print STR
##############################################################################
if __name__ == '__main__':
    main(sys.argv[1:])
