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

def float_yyyymmdd(DATESTR):
    year = float(DATESTR.split('-')[0])
    month = float(DATESTR.split('-')[1])
    day = float(DATESTR.split('-')[2])
    
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
    search_gps.py -p projectName
    search_gps.py -t SLCpar -s Date1 -e Date2
    search_gps.py -p projectName -s Date1 -e Date2
    
    search_gps.py -p LosAngelesT64F108S1A
    search_gps.py -t /Yunmeng/SCRATCH/20100101.slc.par
    search_gps.py -p LosAngelesT64F108S1A -s 2008-01-01 -e 2010-01-01

'''


def cmdLineParse():
    parser = argparse.ArgumentParser(description='Download GPS data over SAR coverage.',\
                                     formatter_class=argparse.RawTextHelpFormatter,\
                                     epilog=INTRODUCTION+'\n'+EXAMPLE)

    parser.add_argument('-p', dest = 'projectName',help='Project name of the processing datasets.')
    parser.add_argument('-t', dest='SLCpar', help='One SLC par file of the resaerch region.')
    parser.add_argument('-s', dest='Dbeg', help='Beginning date of available GPS data.')
    parser.add_argument('-e', dest='Dend', help='Ending date of available GPS data.')
    
    inps = parser.parse_args()
    
    if not inps.projectName and not inps.SLCpar:
        parser.print_usage()
        sys.exit(os.path.basename(sys.argv[0])+': error: projectName and SLCpar File, at least one is needed.')
    return inps

    return inps

################################################################################################


def main(argv):
    
    inps = cmdLineParse()
    
    if inps.projectName:
        projectName = inps.projectName
        scratchDir = os.getenv('SCRATCHDIR')
        templateDir = os.getenv('TEMPLATEDIR')
        slcDir     = scratchDir + '/' + projectName + "/SLC"
        #gpsDir     = scratchDir + '/' + projectName + "/PYGPS"
        ListSLC = os.listdir(slcDir)
        Datelist = []
        for kk in range(len(ListSLC)):
            if ( is_number(ListSLC[kk]) and len(ListSLC[kk])==6 ):    #  if SAR date number is 8, 6 should change to 8.
                DD=ListSLC[kk]
                Year=int(DD[0:2])
                Month = int(DD[2:4])
                Day = int(DD[4:6])
                if  ( 0 < Year < 20 and 0 < Month < 13 and 0 < Day < 32 ):            
                    Datelist.append(ListSLC[kk])
    
        map(int,Datelist)                
        Datelist.sort()
        map(str,Datelist)
        SLCpar = slcDir + "/" + Datelist[0] +"/" + Datelist[0] + ".slc.par"
        print "SLCpar file: %s" % SLCpar
    else:
        SLCpar = inps.SLCpar
        #gpsDir = os.getcwd() + '/PYGPS'
        
    #if not os.path.isdir(gpsDir):
    #    call_str = 'mkdir ' + gpsDir
    #    os.system(call_str)
    
    #call_str = 'cp ' + SLCpar + ' ' + gpsDir
    #os.system(call_str)
    
    #os.chdir(gpsDir)
    FILE = SLCpar 
    
    TS = UseGamma(FILE,'read','start_time:')
    TS=str(float(TS.split('s')[0]))
    
    INC = UseGamma(FILE,'read','incidence_angle:')
    INC = str(float(INC.split('degrees')[0]))
    
    HEAD = UseGamma(FILE,'read','heading:')
    HEAD = str(float(HEAD.split('degrees')[0]))
    
    ########################## Get GPS station infomation ##################################
    
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
    
    ########################### Get SAR coverage information #####################################
    
    BName = os.path.basename(FILE)
    Sufix = BName.split('.')[len(BName.split('.'))-1]
    if Sufix == 'par':
        print ' '
        call_str = "SLC_corners "+ FILE + " > corners.txt"
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
            
            
        north = MaxLat
        south = MinLat
        east = MaxLon
        west = MinLon

        print 'The coverage area of SAR image is :   '    
        print '*** maxlat: '+str(north)
        print '*** minlat: '+str(south)
        print '*** maxlon: '+str(east)
        print '*** minlon: '+str(west)
    
    rm('corners.txt')
    ######################## Search GPS stations #########################################
    
    print ''
    print 'Start to search available GPS stations in SAR coverage >>> '
    
    IDX = np.where( (MinLat< P_Lat) & (P_Lat < MaxLat) & ( MinLon< P_Lon) & (P_Lon < MaxLon))
    kk = []
    
    for i in IDX:
        kk.append(i)
        
    kk = np.array(kk)
    kk = kk.flatten()
    print '...'
    
    date1 = 0
    date2 = 99999999
    
    if inps.Dbeg:
        Dbeg = inps.Dbeg
        date1 = float_yyyymmdd(Dbeg)
        print date1
    if inps.Dend:
        Dend = inps.Dend
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
    
    
    TXT = "search_gps.txt"
    if os.path.isfile(TXT):
        os.remove(TXT)
    
    for i in range(x):
        Nm = P_Name[kk[i]]
        LAT = P_Lat[kk[i]]
        LON = P_Lon[kk[i]]
        DB = P_Dbeg[kk[i]] 
        DE = P_Dend[kk[i]]
        call_str = 'echo ' + str(Nm) + ' ' + str(LAT) + ' ' + str(LON)   + ' ' + str(DB) + ' ' + str(DE) + ' ' + str(TS) + ' ' + str(INC) + ' ' + str(HEAD) + ' >> ' + TXT
        os.system(call_str)
        print '     ' + str(Nm) + '           ' + str(LAT) + '       ' + str(LON) + '       ' + str(DB) + '     ' + str(DE) 
        
               

if __name__ == '__main__':
    main(sys.argv[1:])

