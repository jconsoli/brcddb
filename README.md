# brcddb

**Updates: 17 July 2021**

* Miscellaneous bug fixes
* Added zone by target analysis to repor
* Several FICON improvements

**Updates: 7 Aug 2021**

* brcddb_fabric.py - Return fabric WWN in best_fab_name() if wwn=False but the fabric is not named.
* apps/report.py - Added WWN to the fabric name on the Table of Contents page
* apps/zone.py - Fixed bad call to api_int.get_batch()
* report/zone.py - Minor display issues cleaned up.

**Updates: 14 Aug 2021**

The primary purpose of these updates was to support the zone_merge.py application

* app_data/alert_tables.py - Added current firmware version to software version alert
* api/zone.py - Added enable_zonecfg()
* classes/fabric.py - Added s_del_eff_zonecfg()
* util/search.py - Added Added common search terms.
* brcddb_fabric.py - Commented out alert for LOGIN_BASE_ZONED

**Description**

A hierarchical relational database using Python data types. Used by the reporting and searching functions.

A simple copy of this folder to you Python Library Lib folder is dequate. In Unix environments, remember to set the executable attribute

Contains the following SAN automation applications:

* Includes a built in Excel Workbook report generator with extensive zoning analysis
* Automatically capture data for reporting purposes
* Capture and graph all port statistics for all ports with the maximum poll frequency supported by FOS
* Tool to validate Python development environment
* Sample zoning configuration application
* Sample applications to use the search capabilities.


See applications for sample modules that use this library.
