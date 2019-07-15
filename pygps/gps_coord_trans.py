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
        print("Keyword " + keyword + " doesn't exist in " + inFile)
        f.close()

        
        
#######################################################################################

INTRODUCTION = '''
    Transform GPS station coordinates (latitude and longitude) into radar coordinates.
    Lookup table and the relative dem_par should be provided. 

'''


EXAMPLE = '''EXAMPLES:
    gps_coord_trans.py search_gps.txt -l Lookup_Table -p DEM_Par -o OUT
    gps_coord_trans.py search_gps.txt -l Lookup_Table -p DEM_Par
    
    gps_coord_trans.py search_gps.txt -l 20100101.utm_to_rdc -p 20100101.dem.par
    gps_coord_trans.py search_gps.txt -l 20100101.utm_to_rdc -p 20100101.dem.par -o gps_coord.txt


'''


def cmdLineParse():
    parser = argparse.ArgumentParser(description='Transforming GPS coordinates into radar coordinates.',\
                                     formatter_class=argparse.RawTextHelpFormatter,\
                                     epilog=INTRODUCTION+'\n'+EXAMPLE)

    parser.add_argument('gps_txt',help='Available GPS station information.')
    parser.add_argument('-l', dest='lt', help='lookup table of coordinates transfomration.')
    parser.add_argument('-p', dest='dem_par', help='Parameter file of lookup table.')
    parser.add_argument('-o', dest='out', help='Output file name of the generated GPS coordinates text.')
    
    inps = parser.parse_args()
    
    if not inps.lt:
        parser.print_usage()
        sys.exit(os.path.basename(sys.argv[0])+': error: lookup table should be provided.')

    if not inps.dem_par:
        parser.print_usage()
        sys.exit(os.path.basename(sys.argv[0])+': error: dem_par file should be provided.')

    return inps

################################################################################################
        
def main(argv):
    
    inps = cmdLineParse()
    TXT = inps.gps_txt
    LTFile = inps.lt
    UTMPAR = inps.dem_par
    
    if inps.out: OUT = inps.out
    else: OUT = 'gps_coord.txt'
        
    GPS= np.loadtxt(TXT, dtype = np.str)
    GPS_Nm =GPS[:,0]
    GPS_Nm = GPS_Nm.tolist()
    GPS_LAT = GPS[:,1]
    GPS_LON = GPS[:,2]
    N = len(GPS_Nm)     
    
    nWidthUTM = UseGamma(UTMPAR, 'read', 'width:')
    nLineUTM  = UseGamma(UTMPAR, 'read', 'nlines:')
   
    Corner_LAT = UseGamma(UTMPAR, 'read', 'corner_lat:') 
    Corner_LON = UseGamma(UTMPAR, 'read', 'corner_lon:')

    Corner_LAT =Corner_LAT.split(' ')[0]
    Corner_LON =Corner_LON.split(' ')[0]

    post_Lat = UseGamma(UTMPAR, 'read', 'post_lat:')
    post_Lon = UseGamma(UTMPAR, 'read', 'post_lon:')

    post_Lat =post_Lat.split(' ')[0]
    post_Lon =post_Lon.split(' ')[0] 
    data = read_data(LTFile,'>c8',nWidthUTM,nLineUTM)   # real: range     imaginary: azimuth
    
    if os.path.isfile(OUT):
        os.remove(OUT)
        
    for i in range(N):
        LAT = GPS_LAT[i]
        LON = str(float(GPS_LON[i])-360)
        NM =GPS_Nm[i]
        XX = int (( float(LAT) - float(Corner_LAT) ) / float(post_Lat))  # latitude   width   range
        YY = int (( float(LON) - float(Corner_LON) ) / float(post_Lon))  # longitude   nline  azimuth
             
        CPX_OUT = data[XX][YY]    
        Range = int(CPX_OUT.real)
        Azimuth = int(CPX_OUT.imag)
 
        STR = str(NM) + ' ' + str(float(LAT)) + ' ' + str(float(LON)) + ' ' + str(Azimuth) + ' ' + str(Range) 
        call_str = 'echo ' + STR + ' >> ' + OUT
        os.system(call_str)
        
        print(str(NM) + ': ' + str(LAT) + ' (la) ' + str(LON) + ' (lo) ' + str(Azimuth) + ' (az) ' + str(Range) + ' (ra) ')
##############################################################################
if __name__ == '__main__':
    main(sys.argv[1:])
