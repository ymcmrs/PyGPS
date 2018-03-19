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
from matplotlib.ticker import MultipleLocator, FormatStrFormatter
import pysar._readfile as readfile


##############  function to search points in a polygan #########################
def cn_PnPoly(P, V):
    cn = 0    # the crossing number counter

    # repeat the first vertex at end
    V = tuple(V[:])+(V[0],)

    # loop through all edges of the polygon
    for i in range(len(V)-1):   # edge from V[i] to V[i+1]
        if ((V[i][1] <= P[1] and V[i+1][1] > P[1])   # an upward crossing
            or (V[i][1] > P[1] and V[i+1][1] <= P[1])):  # a downward crossing
            # compute the actual edge-ray intersect x-coordinate
            vt = (P[1] - V[i][1]) / float(V[i+1][1] - V[i][1])
            if P[0] < V[i][0] + vt * (V[i+1][0] - V[i][0]): # P[0] < intersect
                cn += 1  # a valid crossing of y=P[1] right of P[0]

    return cn % 2   # 0 if even (out), and 1 if odd (in)

#===================================================================

# wn_PnPoly(): winding number test for a point in a polygon
#     Input:  P = a point,
#             V[] = vertex points of a polygon
#     Return: wn = the winding number (=0 only if P is outside V[])

def wn_PnPoly(P, V):
    wn = 0   # the winding number counter
    # repeat the first vertex at end
    V = tuple(V[:]) + (V[0],)

    # loop through all edges of the polygon
    for i in range(len(V)-1):     # edge from V[i] to V[i+1]
        if V[i][1] <= P[1]:        # start y <= P[1]
            if V[i+1][1] > P[1]:     # an upward crossing
                if is_left(V[i], V[i+1], P) > 0: # P left of edge
                    wn += 1           # have a valid up intersect
        else:                      # start y > P[1] (no test needed)
            if V[i+1][1] <= P[1]:    # a downward crossing
                if is_left(V[i], V[i+1], P) < 0: # P right of edge
                    wn -= 1           # have a valid down intersect
    return wn

########################################################################


def float_yyyymmdd(DATESTR):
    if '-' in DATESTR:
        year = float(DATESTR.split('-')[0])
        month = float(DATESTR.split('-')[1])
        day = float(DATESTR.split('-')[2]) 
    else:
        if len(DATESTR)==6:
            DATESTR =='20' + DATESTR
        year = float(DATESTR[0:4])
        month = float(DATESTR[4:6])
        day = float(DATESTR[6:8])
    
    date = year + month/12 + day/365
    
    return date

def rm(FILE):
    call_str = 'rm ' + FILE
    os.system(call_str)
    
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

def is_number(s):
    try:
        int(s)
        return True
    except ValueError:
        return False
        
#######################################################################################

INTRODUCTION = '''
    Searching available GPS stations over the research region.
    
    Global GPS stations are referred the GPSNetMap of Nevada Geodetic Laboratory
    Details can be found from http://geodesy.unr.edu/NGLStationPages/gpsnetmap/GPSNetMap.html

'''


EXAMPLE = '''EXAMPLES:
    search_gps_pysar.py velocity.h5
    search_gps_pysar.py demGeo.h5 -s 20100102 -o gps_LosAngeles.txt
'''


def cmdLineParse():
    parser = argparse.ArgumentParser(description='Download GPS data over SAR coverage.',\
                                     formatter_class=argparse.RawTextHelpFormatter,\
                                     epilog=INTRODUCTION+'\n'+EXAMPLE)

    parser.add_argument('file', help='h5 file used to check area region.')
    parser.add_argument('-s', dest='start', help='start date.')
    parser.add_argument('-e', dest='end', help='end date.')
    parser.add_argument('-o', dest='out', help='output file name.')
    
    inps = parser.parse_args()
    

    return inps

################################################################################################


def main(argv):
    
    inps = cmdLineParse()
    FILE = inps.file
    atr=readfile.read_attribute(FILE)
    
    if inps.out: OUT = inps.out
    else: OUT = 'search_gps.txt'
    
    PSXY = 'search_gps_psxy'
    PSTEXT = 'search_gps_pstext'
    #TS = atr['CENTER_LINE_UTC']
    #HEAD = atr['HEADING']
    #INC = str((float(atr['LOOK_REF1'])+float(atr['LOOK_REF2']))/2)  # mean look angle
    
    
    if 'X_FIRST' in atr:
        lat1 = float(atr['Y_FIRST'])
        lon1 = float(atr['X_FIRST'])
        
        lat2 = float(atr['Y_FIRST'])
        lon2 = float(atr['X_FIRST'])+int(atr['X_MAX'])*float(atr['X_STEP'])
        
        lat3 = float(atr['Y_FIRST'])+int(atr['Y_MAX'])*float(atr['Y_STEP'])
        lon3 = float(atr['X_FIRST'])+int(atr['X_MAX'])*float(atr['X_STEP'])
        
        lat4 = float(atr['Y_FIRST'])+int(atr['Y_MAX'])*float(atr['Y_STEP'])
        lon4 = float(atr['X_FIRST'])
        
        v1 = [lat1,lon1]
        v2 = [lat2,lon2]
        v3 = [lat3,lon3]
        v4 = [lat4,lon4]
        
    if 'LAT_REF1' in atr:
        v1 = [float(atr['LAT_REF1']),float(atr['LON_REF1'])]
        v2 = [float(atr['LAT_REF2']),float(atr['LON_REF2'])]
        v3 = [float(atr['LAT_REF3']),float(atr['LON_REF3'])]    
        v4 = [float(atr['LAT_REF4']),float(atr['LON_REF4'])]
      
    V =[v1,v2,v3,v4]
    LAT =[v1[0],v2[0],v3[0],v4[0]]
    LON=[v1[1],v2[1],v3[1],v4[1]]
    
    call_str = 'wget -q http://geodesy.unr.edu/NGLStationPages/DataHoldings.txt'
    os.system(call_str)

    call_str = 'tail -n +2 DataHoldings.txt > tt'
    os.system(call_str)
    
    call_str = "awk '{print $1}' tt >t_Name"
    os.system(call_str)
    
    call_str = "awk '{print $2}' tt >t_Lat"
    os.system(call_str)
    
    call_str = "awk '{print $3}' tt >t_Lon"
    os.system(call_str)

    call_str = "awk '{print $8}' tt >t_Dbeg"
    os.system(call_str)
    
    call_str = "awk '{print $9}' tt >t_Dend"
    os.system(call_str)
    
    P_Name = np.loadtxt('t_Name',dtype = np.str)
    
    P_Lat = np.loadtxt('t_Lat')
    P_Lat = np.asarray(P_Lat)
    
    P_Lon = np.loadtxt('t_Lon')
    P_Lon = np.asarray(P_Lon)
    
    P_Dbeg = np.loadtxt('t_Dbeg',dtype = np.str)
    P_Dend = np.loadtxt('t_Dend',dtype = np.str)
    
    rm('t_Lat'),rm('t_Lon'),rm('t_Dbeg'),rm('t_Name'),rm('DataHoldings.txt'),rm('t_Dend'),rm('tt')
    
    print LAT
    print LON
    MinLat = min(LAT)
    MaxLat = max(LAT)
    MinLon = min(LON)
    MaxLon = max(LON)
    
    if ((MinLon < 0) and (MaxLon < 0 ) ):
        MinLon = MinLon + 360
        MaxLon = MaxLon + 360
    elif ((MinLon < 0) and (MaxLon > 0 )):
        MinLon = MinLon + 360
        MaxLon = MaxLon + 360
        IDX = np.where(P_Lon > 0)
        P_Lon[IDX] = P_Lon[IDX] + 360
    
    print ''
    print 'Start to search available GPS stations in SAR coverage >>> '

    
    IDX = np.where( (MinLat< P_Lat) & (P_Lat < MaxLat) & ( MinLon< P_Lon) & (P_Lon < MaxLon))
    #print IDX
    kk = []
    
    for i in IDX:
        #print i
        kk.append(i)
    #print kk    
    kk = np.array(kk)
    kk = kk.flatten()
    print '...'
    
    date1 = 0
    date2 = 99999999
    
    if inps.start:
        Dbeg = inps.start
        date1 = float_yyyymmdd(Dbeg)
        print date1
    if inps.end:
        Dend = inps.end
        date2 = float_yyyymmdd(Dend)
        print date2
        
    x = len(kk)
    kk_mod = []
    
    for i in range(x):
        dt1 = float_yyyymmdd(P_Dbeg[kk[i]])
        dt2 = float_yyyymmdd(P_Dend[kk[i]])
        if (dt1 > date1 and dt1 < date2) or (dt2 > date1 and dt2 < date2) or ( dt1<date1 and date2 < dt2):
            kk_mod.append(kk[i])
    
    kk = kk_mod
    x = len(kk)
    if x ==0:
        print 'No GPS station is found in the SAR coverage!'
    else:
        print 'Number of available GPS station:  %s' % str(x)
        print ''
        print '  Station Name      Lat(deg)      Long(deg)       Date_beg      Date_end  '
    
 
    if os.path.isfile(OUT):
        os.remove(OUT)
        
    if os.path.isfile(PSXY):
        os.remove(PSXY)
    
    if os.path.isfile(PSTEXT):
        os.remove(PSTEXT)
    
    for i in range(x):
        Nm = P_Name[kk[i]]
        LAT = P_Lat[kk[i]]
        LON = P_Lon[kk[i]]
        DB = P_Dbeg[kk[i]] 
        DE = P_Dend[kk[i]]
        #call_str = 'echo ' + str(Nm) + ' ' + str(LAT) + ' ' + str(LON)   + ' ' + str(DB) + ' ' + str(DE) + ' ' + str(TS) + ' ' + str(INC) + ' ' + str(HEAD) + ' >> ' + OUT
        call_str = 'echo ' + str(Nm) + ' ' + str(LAT) + ' ' + str(LON)   + ' ' + str(DB) + ' ' + str(DE) + ' 0 35.5 -167.8025324' + ' >> ' + OUT
        #call_str = 'echo ' + str(Nm) + ' ' + str(LAT) + ' ' + str(LON)   + ' ' + str(DB) + ' ' + str(DE) + ' >> ' + OUT
        os.system(call_str)
        
        if float(LON) > 180:
            LON = str(float(LON)-360)
            
        call_str = 'echo ' + str(LON) + ' ' + str(LAT)  + ' >> ' + PSXY
        os.system(call_str)
        
        call_str = 'echo '  + str(LON) +' ' + str(LAT) + ' ' + str(Nm)  + ' >> ' + PSTEXT
        os.system(call_str)
        print '     ' + str(Nm) + '           ' + str(LAT) + '       ' + str(LON) + '       ' + str(DB) + '     ' + str(DE) 
        
               
if __name__ == '__main__':
    main(sys.argv[1:])

