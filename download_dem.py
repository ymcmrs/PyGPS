#! /usr/bin/env python
############################################################
# Program is part of PyInt v1.2                            #
# Copyright(c) 2017, Yunmeng Cao                           #
# Author:  Yunmeng Cao                                     #
############################################################

import numpy as np
import gdal
import getopt
import sys
import os
import h5py
import argparse
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, FormatStrFormatter


#def read_region(STR):
#    WEST = STR.split('/')[0]
#    SOUTH = STR.split('/')[1].split('/')[0]
    
#    EAST = STR.split(SOUTH+'/')[1].split('/')[0]
#    NORTH = STR.split(SOUTH+'/')[1].split('/')[1]
    
#    WEST =float(WEST)
#    SOUTH=float(SOUTH)
#    EAST=float(EAST)
#    NORTH=float(NORTH)
#    return WEST,SOUTH,EAST,NORTH

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
    
        
#######################################################################################

INTRODUCTION = '''
    
    Downloading SRTM 30m data. *.tif. what you need to provide is west/south/east/north parameters.
    
'''


EXAMPLE = '''EXAMPLES:
    download_dem.py -r west/south/east/north -o OUT_NAME 
    download_dem.py -r west/south/east/north

    e.g.,
    download_dem.py -r " -30/32/-108/-106 "   
    download_dem.py -r " -30/32/-108/-106 " -o SouthCalifornia.tif
    
'''


def cmdLineParse():
    parser = argparse.ArgumentParser(description='Download SRTM 30m data.',\
                                     formatter_class=argparse.RawTextHelpFormatter,\
                                     epilog=INTRODUCTION+'\n'+EXAMPLE)

    parser.add_argument('-r', dest='region',help='DEM region of research area. west/south/east/north.')
    parser.add_argument('-o', dest= 'out',help='Output file name.')
    inps = parser.parse_args()

    if not inps.region:
        parser.print_usage()
        sys.exit(os.path.basename(sys.argv[0])+': error: west/east/south/north parameters should be provided.')

    return inps  


################################################################################################


def main(argv):
    
    inps = cmdLineParse()
    Region_Str = inps.region
    west,south,east,north = read_region(Region_Str)
    
    if inps.out: NM = inps.out
    else: NM = 'dem.tif'
    
    call_str='wget -O dem.tif "http://ot-data1.sdsc.edu:9090/otr/getdem?north=%f&south=%f&east=%f&west=%f&demtype=SRTMGL1"' % (north,south,east,west)
    os.system(call_str)
    
    call_str = 'mv dem.tif ' + NM
    os.system(call_str)
    
    GRD = NM.replace('tif','grd')
    call_str = 'gdal_translate ' + NM + ' -of GSBG  -a_nodata 0 ' + GRD
    os.system(call_str)
    
if __name__ == '__main__':
    main(sys.argv[1:])

