#! /usr/bin/env python
############################################################
# Program is part of PySAR v1.2                            #
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

def read_data(inFile, dtype, nWidth, nLength):
    data = np.fromfile(inFile, dtype, int(nLength)*int(nWidth)).reshape(int(nLength),int(nWidth))  
    return data

    
        
#######################################################################################

INTRODUCTION = '''
    
    Plotting the 2D figures, such as unwrapped/wrapped interferogram and coherence map, with or without DEM and GPS stations.
    
'''


EXAMPLE = '''EXAMPLES:
    plot_gps_insar.py file width -d DEM
    plot_gps_insar.py file width -d DEM -t gps_coord.txt
    plot_gps_insar.py file width -t gps_coord.txt
    
    plot_gps_insar.py 20150101-20160101.diff_filt.cor 3228 -d /Yunmeng/DEM/Pacaya.dem
    plot_gps_insar.py 20150101-20160101.diff_filt.unw 3228 -d /Yunmeng/DEM/Pacaya.dem
    plot_gps_insar.py 20150101-20160101.diff_filt.int 3228 -d /Yunmeng/DEM/Pacaya.dem -t search_gps.txt

'''


def cmdLineParse():
    parser = argparse.ArgumentParser(description='Download GPS data over SAR coverage.',\
                                     formatter_class=argparse.RawTextHelpFormatter,\
                                     epilog=INTRODUCTION+'\n'+EXAMPLE)

    parser.add_argument('FILE',help='2D file that need to be plotted.')
    parser.add_argument('WIDTH', help='width of the 2D file. i.e., range columns for RDC, longitude conlumns for GEC.')
    parser.add_argument('-d','--dem', dest='dem', help='background DEM that used to show the background terrain.')
    parser.add_argument('-t', dest='txt', help='information of gps stations tesxt whose columns should obey: Name, lat, lon, range, azimuth')
    parser.add_argument('-m','--mask',dest='mask',  help='Masking the image with mask file.')
    
    inps = parser.parse_args()

    return inps

################################################################################################


def main(argv):
    
    inps = cmdLineParse()
    
    FILE = inps.FILE
    WIDTH = inps.WIDTH
    SUFIX = os.path.basename(FILE).split('.')[len(os.path.basename(FILE).split('.')) -1]
    print SUFIX
    
    if SUFIX =='unw' or SUFIX=='cor': 
        dtype = '>f4'
        dsize = 4
    elif SUFIX =='int': 
        dtype ='>c8'    
        dsize = 8
#    else: 
#        print 'file cannot be recognized.'
#        parser.print_usage()
#        sys.exit(1)
    
    SIZE = os.path.getsize(FILE)
    LENGTH = int(int(SIZE)/int(WIDTH)/dsize)
    
    
    H5_FILE = os.path.basename(FILE) + '.h5'
    DATA = read_data(FILE,dtype,WIDTH,LENGTH)
    
    Name = SUFIX
    f = h5py.File(H5_FILE,'w')
    group = f.create_group(Name)
    dset = group.create_dataset(Name,data=DATA,compression ='gzip')
    group.attrs['WIDTH'] = WIDTH
    group.attrs['FILE_LENGTH'] = LENGTH    
    f.close()
                   
    STR_DEM = ''
    if inps.dem:
        DEM = inps.dem
        SIZE = os.path.getsize(FILE)
        dsize = int(int(SIZE)/int(WIDTH)/int(LENGTH))
        if dsize == 4: dtype_dem = '>f4'
        else: dtype_dem = '>i2'    
        H5_DEM = os.path.basename(DEM) + '.h5'
        DATA = read_data(DEM,dtype_dem,WIDTH,LENGTH)
        Name = 'dem'
        f = h5py.File(H5_DEM,'w')
        group = f.create_group(Name)
        dset = group.create_dataset(Name,data=DATA,compression ='gzip')
        group.attrs['WIDTH'] = WIDTH
        group.attrs['FILE_LENGTH'] = LENGTH    
        f.close()
        
        STR_DEM = ' --dem ' + H5_DEM + ' --dem-nocontour '
        
    STR_MASK = '' 
    if inps.mask:
        MASK = inps.mask
        STR_MASK = ' --mask ' + MASK
        
    call_str = 'view.py ' + H5_FILE + STR_DEM + STR_MASK
    os.system(call_str)     
    
if __name__ == '__main__':
    main(sys.argv[1:])

