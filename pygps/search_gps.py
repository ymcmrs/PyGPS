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
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, FormatStrFormatter


############### function to get image corners ################
def get_h5py_atr(h5py_file):
    # This def is referred to mintpy readfile.py
    f = h5py.File(h5py_file, 'r')
    if len(f.attrs) > 0 and 'LAT_REF1' in f.attrs.keys():
        atr = dict(f.attrs)
    else:
         # grab the list of attrs in HDF5 file
        global atr_list
        
        def get_hdf5_attrs(name, obj):
            global atr_list
            if len(obj.attrs) > 0 and 'LAT_REF1' in obj.attrs.keys():
                atr_list.append(dict(obj.attrs))
        atr_list = []
        f.visititems(get_hdf5_attrs)
        # use the attrs with most items
        if atr_list:
            num_list = [len(i) for i in atr_list]
            atr = atr_list[np.argmax(num_list)]
        else:
            raise ValueError('No attribute LAT_REF1 found in file:', fname)
    # decode string format
    for key, value in atr.items():
        try:
            atr[key] = value.decode('utf8')
        except:
            atr[key] = value
    return atr

def read_region(STR):
    WEST = STR.split('/')[0]
    EAST = STR.split('/')[1].split('/')[0]
    
    SOUTH = STR.split(EAST+'/')[1].split('/')[0]
    NORTH = STR.split(EAST+'/')[1].split('/')[1]
    
    WEST =float(WEST)
    SOUTH=float(SOUTH)
    EAST=float(EAST)
    NORTH=float(NORTH)
    return WEST,SOUTH,EAST,NORTH


def get_corner_atr(atr):
    #atr=readfile.read_attribute(h5file)
    LAT1 = atr['LAT_REF1'];LAT2 = atr['LAT_REF2'];LAT3 = atr['LAT_REF3'];LAT4 = atr['LAT_REF4']
    LON1 = atr['LON_REF1'];LON2 = atr['LON_REF2'];LON3 = atr['LON_REF3'];LON4 = atr['LON_REF4']
   
    LAT = [float(LAT1),float(LAT2),float(LAT3),float(LAT4)]
    LON = [float(LON1),float(LON2),float(LON3),float(LON4)]
    
    return LAT,LON

def get_corner_box(box):
    WEST,SOUTH,EAST,NORTH = read_region(box);
    LAT1 = NORTH;LAT2 = NORTH;LAT3 = SOUTH;LAT4 = SOUTH
    LON1 = WEST;LON2 = EAST;LON3 = EAST;LON4 = WEST
    LAT = [float(LAT1),float(LAT2),float(LAT3),float(LAT4)]
    LON = [float(LON1),float(LON2),float(LON3),float(LON4)]
    
    return LAT,LON

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
        print("Keyword " + keyword + " doesn't exist in " + inFile)
        f.close()    

def is_number(s):
    try:
        int(s)
        return True
    except ValueError:
        return False
        
#######################################################################################

INTRODUCTION = '''
    Searching available GPS stations over an interested region.
    
    Global GPS stations are referred the GPSNetMap of Nevada Geodetic Laboratory
    Details can be found from http://geodesy.unr.edu/NGLStationPages/gpsnetmap/GPSNetMap.html

'''


EXAMPLE = '''EXAMPLES:
    search_gps.py -f geometryRadar.h5
    search_gps.py -b 120/122/34/38 -s 20100102 -e 20150101 -o gps_LosAngeles.txt
    search_gps.py -p 20100101.slc.par 
    search_gps.py -f velocity.h5 -e 20100102 -o gps_LosAngeles.txt
    search_gps.py -f ifgramStack.h5 -s 20100102 --inside -o gps_LosAngeles.txt
    search_gps.py -f timeseries.h5 -s 20100102 --extend_search 0.1 -o gps_LosAngeles.txt
'''


def cmdLineParse():
    parser = argparse.ArgumentParser(description='Search available GPS data over an interested area.',\
                                     formatter_class=argparse.RawTextHelpFormatter,\
                                     epilog=INTRODUCTION+'\n'+EXAMPLE)

    parser.add_argument('-f',dest='file', help='h5 file used to check area region.')
    parser.add_argument('-p',dest='slc_par', help='slc_par file used to check area region, GAMMA/SLC_corners will be called.')
    parser.add_argument('-b','--box', dest='box',help='box corners of research region. e.g., 120/122/33/34 ')
    parser.add_argument('-s', '--start-date',dest='start', help='start date, GPS data should be available before this date.')
    parser.add_argument('-e', '--end-date',dest='end', help='end date, GPS data should be availabe after this date.')
    parser.add_argument('-o','--out', dest='out', help='output file name.')
    parser.add_argument('--inside', action="store_true", default=False, help='Constraining stations inside the SAR coverage, otherwise, in the corner rectangle region.')
    parser.add_argument('--extend_search', dest='extend_search', help='extend the search region based on the box corner.')
    
    inps = parser.parse_args()
    
    if not inps.file and not inps.box and not inps.slc_par:
        parser.print_usage()
        sys.exit(os.path.basename(sys.argv[0])+': error: h5file or slc_par or coverage box at least one should be provided.')

    

    return inps

################################################################################################


def main(argv):
    
    inps = cmdLineParse() 
    if inps.file:
        atr = get_h5py_atr(inps.file)
        LAT,LON = get_corner_atr(atr)
        VP = [[LAT[0],LON[0]],[LAT[1],LON[1]],[LAT[3],LON[3]],[LAT[2],LON[2]],[LAT[0],LON[0]]];
    elif inps.box:
        LAT,LON = get_corner_box(inps.box)
        VP = [[LAT[0],LON[0]],[LAT[1],LON[1]],[LAT[2],LON[2]],[LAT[3],LON[3]],[LAT[0],LON[0]]];
    elif inps.slc_par:
        call_str = "SLC_corners "+ inps.slc_par + " > corners.txt"
        os.system(call_str)
        
        File = open("corners.txt","r")
        InfoLine = File.readlines()[8:10]      
        File.close()
           
        MinLat = float(InfoLine[0].split(':')[1].split('  max. ')[0])
        MaxLat = float(InfoLine[0].split(':')[2])
        MinLon = float(InfoLine[1].split(':')[1].split('  max. ')[0])
        MaxLon = float(InfoLine[1].split(':')[2])
        
        if ((MinLon < 0) and (MaxLon < 0 ) ):
            MinLon = MinLon + 360
            MaxLon = MaxLon + 360
        elif ((MinLon < 0) and (MaxLon > 0 )):
            MinLon = MinLon + 360
            MaxLon = MaxLon + 360
            IDX = np.where(P_Lon > 0)
            P_Lon[IDX] = P_Lon[IDX] + 360
            
        NORTH = MaxLat
        SOUTH = MinLat
        EAST = MaxLon
        WEST = MinLon
        
        LAT1 = NORTH;LAT2 = NORTH;LAT3 = SOUTH;LAT4 = SOUTH
        LON1 = WEST;LON2 = EAST;LON3 = EAST;LON4 = WEST
        LAT = [float(LAT1),float(LAT2),float(LAT3),float(LAT4)]
        LON = [float(LON1),float(LON2),float(LON3),float(LON4)]
        VP = [[LAT[0],LON[0]],[LAT[1],LON[1]],[LAT[3],LON[3]],[LAT[2],LON[2]],[LAT[0],LON[0]]];
    
    PSXY = 'gps_latlon'
    PSTEXT = 'gps_latlon_name'
    
    OUT= 'search_gps.txt'
    if inps.inside:
        OUT = 'search_gps_inside.txt'
    if inps.out:
        OUT = inps.out
    
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
    
    call_str = "awk '{print $4}' tt >t_Height"
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
    
    P_Height = np.loadtxt('t_Height')
    P_Height = np.asarray(P_Height)
    
    P_Dbeg = np.loadtxt('t_Dbeg',dtype = np.str)
    P_Dend = np.loadtxt('t_Dend',dtype = np.str)
    
    rm('t_Lat'),rm('t_Lon'),rm('t_Dbeg'),rm('t_Name'),rm('DataHoldings.txt'),rm('t_Dend'),rm('tt'),rm('t_height')
    

    MinLat = min(LAT)
    MaxLat = max(LAT)
    MinLon = min(LON)
    MaxLon = max(LON)
    
    VP1 = [[MinLat,MaxLon],[MinLat,MinLon],[MaxLat,MinLon],[MaxLat,MaxLon],[MinLat,MaxLon]]
    
    if inps.extend_search:
        dx = float(inps.extend_search)
        MinLat = MinLat - dx
        MaxLat = MaxLat + dx
        MinLon = MinLon - dx
        MaxLon = MaxLon + dx
        OUT = 'search_gps_extend.txt'
    if inps.out:
        OUT = inps.out
   
    
    if ((MinLon < 0) and (MaxLon < 0 ) ):
        MinLon = MinLon + 360
        MaxLon = MaxLon + 360
    elif ((MinLon < 0) and (MaxLon > 0 )):
        MinLon = MinLon + 360
        MaxLon = MaxLon + 360
        IDX = np.where(P_Lon > 0)
        P_Lon[IDX] = P_Lon[IDX] + 360
    
    print('')
    print('Start to search available GPS stations in SAR coverage >>> ')

    
    IDX = np.where( (MinLat< P_Lat) & (P_Lat < MaxLat) & ( MinLon< P_Lon) & (P_Lon < MaxLon))
    #print IDX
    kk = []
    
    for i in IDX:
        #print i
        kk.append(i)
    #print kk    
    kk = np.array(kk)
    kk = kk.flatten()
    print('...')
    
    date1 = 99999999
    date2 = 0
    
    if inps.start:
        Dbeg = inps.start
        date1 = float_yyyymmdd(Dbeg)
        print(date1)
    if inps.end:
        Dend = inps.end
        date2 = float_yyyymmdd(Dend)
        print(date2)
        
    x = len(kk)
    kk_mod = []
    kk_flag = []
    
    for i in range(x):
        dt1 = float_yyyymmdd(P_Dbeg[kk[i]])
        dt2 = float_yyyymmdd(P_Dend[kk[i]])
        #if (dt1 > date1 and dt1 < date2) or (dt2 > date1 and dt2 < date2) or ( dt1<date1 and date2 < dt2):
        if (dt1 < date1 and dt2 > date2):
            k_flag = 1
            LA0 = P_Lat[kk[i]];LO0  = P_Lon[kk[i]]
            PP0 = [float(LA0),float(LO0)-360];
            #print PP0
            k_inside = cn_PnPoly(PP0, VP)
            k_out_corner = cn_PnPoly(PP0, VP1)
            
            if k_inside==1:
                k0 = 1
            elif k_out_corner==1:
                k0 = 3
            else:
                k0 = 2                
            
            if inps.inside:
                k_flag = k_inside
            if k_flag==1:            
                kk_mod.append(kk[i])
                kk_flag.append(k0)
                
                
    
    kk = kk_mod
    x = len(kk)
    if x ==0:
        print('No GPS station is found in the SAR coverage!')
    else:
        print('Number of available GPS station:  %s' % str(x))
        print('')
        print('  Station Name      Lat(deg)      Long(deg)       Height(m)      Date_beg      Date_end  ')
    
 
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
        #LAT0 = (int(LAT*10000))/10000
        LAT0 = '%.4f'%LAT
        #LON0 = (int(LON*10000))/10000
        LON0 = '%.4f'%LON
        HEI = P_Height[kk[i]]
        DB = P_Dbeg[kk[i]] 
        DE = P_Dend[kk[i]]
        flag0 = kk_flag[i]
        #call_str = 'echo ' + str(Nm) + ' ' + str(LAT) + ' ' + str(LON)   + ' ' + str(DB) + ' ' + str(DE) + ' ' + str(TS) + ' ' + str(INC) + ' ' + str(HEAD) + ' >> ' + OUT
        call_str = 'echo ' + str(Nm) + ' ' + str(LAT) + ' ' + str(LON)   + ' '+ str(HEI) + ' '  + str(DB) + ' ' + str(DE) +  ' ' + str(int(flag0)) + ' >> ' + OUT
        #call_str = 'echo ' + str(Nm) + ' ' + str(LAT) + ' ' + str(LON)   + ' ' + str(DB) + ' ' + str(DE) + ' >> ' + OUT
        os.system(call_str)
        
        if float(LON) > 180:
            LON = str(float(LON)-360)
            
        call_str = 'echo ' + str(LON) + ' ' + str(LAT)  + ' >> ' + PSXY
        os.system(call_str)
        
        call_str = 'echo '  + str(LON) +' ' + str(LAT) + ' ' + str(Nm)  + ' >> ' + PSTEXT
        os.system(call_str)
        print('     ' + str(Nm) + '           ' + str(LAT0) + '       ' + str(LON0) +'       ' + str(HEI) + '       ' + str(DB) + '     ' + str(DE) + ' ' +str(int(flag0)))
        
               
if __name__ == '__main__':
    main(sys.argv[1:])

