# PyGPS
Incorporate GPS and InSAR based on python both for deformation estimation, atmosphere correction, and water vapor inversion problems.

######################################################################################   
1. Search available GPS stations over the research region. (All of the available GPS network over World will be used)     
2. Extract deformation from GPS for InSAR analysis      
3. Extract atmosphere data for InSAR atmosphere correction      
4. Develop new algorithms for incorporating GPS and InSAR  ( ing... )           
#######################################################################################    
     
Yunmeng
May 16, 2017

Usage Example:

step 1: search_gps_pysar.py (see usage)

step 2: 
       (troposhere products)                    (ground deformation products)
       download_gps_atm.py date_list            download_gps_def.py date_list
       get_sar_atm.py (see usage)               enu2los_all.py (see usage)
                                                get_sar_def.py (see usage) 
       


