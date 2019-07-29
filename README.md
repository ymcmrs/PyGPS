# PyGPS
## Extracing displacement and atmospheric parameters from GPS products for improving InSAR geodesy.
#### GPS products from [Nevada Geodetic Laboratory](http://geodesy.unr.edu/) and [UNAVCO](https://www.unavco.org/) are supported.    

+ Search available GPS stations over an interested region [yes]
+ Download the GPS products of interest [yes]
+ Extract the spatio-temporal displacement and atmospheric products (time-series or near SAR epoch) [yes]
+ Mitigating the atmospheric effects for InSAR geodesy [not yet]
+ Generate high-resolution atmospheric water vapor map by fusing InSAR and GPS measurement [not yet]


#### General Work-flow:
 
    step1: search_gps.py                  [Done. Available]
    step2: download_gps_atm.py            [Done. Available]
    step3: extract_sar_atm.py             [Done. Available]
    step4: elevation_correlation.py       [Done. open later]
    step5: variogram_gps.py               [Done. open later]
    step6: gps_variogram_modeling.py      [Done. open later]
    step7: interp_sar_tropo.py            [Done. open later]
    step8: generate_timeseries_tropo.py   [Done. open later]
    
    app: pygpsApp.py                      [Done. open later]
