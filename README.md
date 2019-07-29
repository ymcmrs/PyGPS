# PyGPS
## Extracing displacement and atmospheric parameters from GPS products for improving InSAR geodesy.
#### GPS products from [Nevada Geodetic Laboratory](http://geodesy.unr.edu/) and [UNAVCO](https://www.unavco.org/) are supported.    

+ Search available GPS stations over an interested region [yes]
+ Download the GPS products of interest [yes]
+ Extract the spatio-temporal displacement and atmospheric products (time-series or near SAR epoch) [yes]
+ Mitigating the atmospheric effects for InSAR geodesy [not yet]
+ Generate high-resolution atmospheric water vapor map by fusing InSAR and GPS measurement [not yet]


Steps:

(1) search_gps.py
(2) download_gps_atm.py
(3) extract_sar_atm.py
(4) elevation_correlation.py
(5) variogram_gps.py
(6) gps_variogram_modeling.py
(7) interp_sar_tropo.py
(8) generate_timeseries_tropo.py
(9) pygpsApp.py
