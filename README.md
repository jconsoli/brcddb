# brcddb

Consoli Solutions, LLC
jack@consoli-solutions.com
jack_consoli@yahoo.com

**04 Dec 2025**
* Added port summary by port use to switch report
* Miscellaneous messaging improvements
  
**19 Oct 2025**
* Added support for scan.py
* Added support for additional RNID reporting

**25 August 2025**
* Added scc policy to switch report
* Added defined vs active SCC_POLICY to best practice check
* Added different speed logins for groups to best practice check

**01 Mar 2025**
* Added zone clenup worksheet
* Misc bug fixes

**Update 20 Oct 2024**

Primary changes were to support the new chassis and report pages.

**Updates 6 March 2024**

* Miscellaneous bug fixes
* Improved error messaging
* Updated comments

**Updates 11 Feb 2023**

* Added checks for FICON ports with addresses > 0xFD
* Added zone groups to report

**Updates 01 Jan 2023**

* Primary change was shifting from a hard coded best practice table to one dynamically read from a Workbook
* Several utilitarian additions such as the ability to return FC-4 features in brcddb_login.py

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
* util/search.py - Added common search terms.
* brcddb_fabric.py - Commented out alert for LOGIN_BASE_ZONED

**Updates: 21 Aug 2021**

The purpose of these updates was to support the ability to generate CLI zone commands
with the zone_merge.py application.

* brcddb_fabric.py - Added Added copy_fab_obj()
* classes/project.py - Added flag for automatic switch add in s_add_fabric()
* classes/fabric.py - Bug in r_defined_eff_zonecfg_obj(). Added add_switch flag to __init__
* util/util.py - Added zone_cli().

**Updates: 14 NOv 2021**

* Deprecated pyfos_auth - previously only used in name only.
* Added util.parse_cli.py

**Updated 31 Dec 2021**

* Several comments and user messaging improved
* Replaced all bare exception clauses with explicit exceptions
* Miscellaneous bug fixes, especially around the mainframe


**Updated 28 Apr 2022**

* Added support for new URIs in FOS 9.1
* Moved some generic libraries from here to brcdapi

* **Description**

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
