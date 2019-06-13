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

############### function to get image corners ################
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


def get_corner(h5file):
    atr=readfile.read_attribute(h5file)
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
    Get time series date list based on PYSAR file.

'''


EXAMPLE = '''EXAMPLES:

    get_date_list.py unwrapIfgram.h5
    get_date_list.py coherence.h5

'''


def cmdLineParse():
    parser = argparse.ArgumentParser(description='Download GPS data over SAR coverage.',\
                                     formatter_class=argparse.RawTextHelpFormatter,\
                                     epilog=INTRODUCTION+'\n'+EXAMPLE)

    parser.add_argument('h5_file', help='Get date list based on PYSAR interferograms h5 file.')

    inps = parser.parse_args()
    return inps

################################################################################################


def main(argv):
    
    inps = cmdLineParse() 
    H5 = inps.h5_file
    f_h5 = h5py.File(H5,'r')
    k1 = f_h5.keys()[0]
    k2 = f_h5[k1].keys()
    N = len(k2)
    
    DATE = []
    for i in range(N):
        DATE12=f_h5[k1][k2[i]].attrs['DATE12']
        DATE1 = DATE12[0:6]
        DATE2 = DATE12[7:13]
        if DATE1 not in DATE:
            DATE.append(DATE1)
        if DATE2 not in DATE:
            DATE.append(DATE2)
            
    N2 = len(DATE)
    OUT = 'date_list.txt'
    if os.path.isfile(OUT):
        os.remove(OUT)
     
    print 'Time series SAR date list:'
    for i in range(N2):
        print DATE[i]
        call_str = 'echo ' + DATE[i] + ' >> ' + OUT
        os.system(call_str)
        
   
               
if __name__ == '__main__':
    main(sys.argv[1:])

