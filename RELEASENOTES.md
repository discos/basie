# RELEASE NOTES

## v0.6.5

Release notes:
  - [x] Changed order in derotator commands for fixed position. Fixes #19.
  
## v0.6.4

Release notes:
  - [x] Added warning message if target coordinates are specified in equatorial
    frame including sexagesimal RA without 'h' suffix. Fixes #14.
  - [x] Added **SKYDIP** scan mode.
  - [x] Total Power backend configuration did not handle properly the enable
    string. Fixes #15.
  - [x] Disable Tsys measurements on Xarcos backend. Fixes #16.
  - [x] Better error messages

**Note On Skydip**: **SKYDIP** scan mode can be used as any other scan mode
and it presents the same set of options. The skydip will be executed with a fixed
offset of 1.0 degrees in azimuth with respect to the specified target.

## v0.6.3

Release notes:
  - [x] Angles now rounded to the 4th decimal point.
  - [x] **nop** instruction removed from roach backend configuration.
  - [x] added explicit **ftrack** parameter in configuration file.
  - [x] added **offset interleave** parameter in raster map scans.
  - [x] Fixes algorithm for Raster Maps scans using multifeed receiver.

**Note on ftrack**: in order to use ftrack procedures the user now must specify
```python
restFrequency = something_different_from_zero
ftrack = True
```
in the configuration file. Note that this will activate ftrack procedures even
when  the target velocity is null. On the contrary, setting a *restFrequency*
value and a target *velocity* will not automatically trigger the *ftrack*
procedure if not explicitly specified by the *ftrack* parameter in the
configuration file.

**Note on raster maps**: Raster maps now include a new parameter called
**offset_interleave**. If **offset_interleave** is differrent from zero this
will tell basie to add one subscan outside the map after **offset_interleave**
subscans inside the map. By default the offset position is taken 5 beamsizes
outside the map perimeter for single feed receivers, while it is take 5 receiver
extents for multifeed receivers.

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
