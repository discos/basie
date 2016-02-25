# RELEASE NOTES

## v0.6.2

Release notes:
  - [x] **POINT** scans now use **MANAGEMENT/CalibrationTool** data recorder by
    default as the **MANAGEMENT/Point** recorder was causing randomatic errors.
  - [x] Backend names are now automatically postfixed with **CT** for 
    CalibrationTool recordings associated with POINT scans. 
    Addresses [Nuraghe issue #25](http://www.med.ira.inaf.it/mantisbt/view.php?id=25).
  - [x] Procedure names are now prefixed with **PROC_** instead of the
    whole PROCEDURE_ synthax for better readability.
  - [x] **MAP** scan modes (both **RASTER** and **OTF** maps) now
    allow to specify the separation between each subscan
    alternatively in terms of **absolute degrees** or in terms of
    **number of subscans per beamsize**. 
  - [x] Increased test coverage.

**Note on multifeed maps**: using a fixed value value in
degrees for specifying the separation between each subscan in
the map may cause a non uniform sampling of the map area. The
user should take into account the geometry of the multifeed
receiver in its Best Coverage configuration and divide the
space between each feed evenly in order to obtain a regular
grid, this can also be subject to numerical rounding errors.
The *scans-per-beam* notation in this case is instead assured
to produce regularly sampled areas. 

## v0.6.1

Release notes: 

  - [x] added **POINT** scan mode for pointing scans
  - [x] added ZEROFF procedure to **reset offsets** in pointing scans
  - [x] removed initization instructions from **roach** backend
  - [x] updated requirements with less restrictive **numpy version**
  - [x] updated examples in template files

Note that with this release **ROACH** backend will not perform any
backend initialization from schedule before executing the relative
scan, this means that backend setup must be executed manually by the
user before launching the schedule. That's not the case for all other
backends which continue to perform proper backend initialization as
specified in the **.bck** file produced by basie. 

Note that offsets measured and applied by means of the **POINT** scans
will add up to the ones specified in the following scans unless they
are explictly zeroed by means of the **azelOffsets=0.0d,0.0d**
command. Such zeroing takes place at the beginning of every **POINT**
scan. 

## v0.6 First public release

Released with Nuraghe 0.6
