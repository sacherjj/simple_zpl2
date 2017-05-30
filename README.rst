===========
Simple ZPL2
===========


.. image:: https://img.shields.io/pypi/v/simple_zpl2.svg
        :target: https://pypi.python.org/pypi/simple_zpl2

.. image:: https://img.shields.io/travis/sacherjj/simple_zpl2.svg
        :target: https://travis-ci.org/sacherjj/simple_zpl2

.. image:: https://readthedocs.org/projects/simple-zpl2/badge/?version=latest
        :target: https://simple-zpl2.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status

.. image:: https://pyup.io/repos/github/sacherjj/simple_zpl2/shield.svg
     :target: https://pyup.io/repos/github/sacherjj/simple_zpl2/
     :alt: Updates


Simple Project to help in building ZPL2 strings for printing barcodes with Zebra or compatible label printers.


* Free software: MIT license
* Documentation: https://simple-zpl2.readthedocs.io.


Features
--------

* Methods for adding ZPL2 entries in the label data
* Error handling for data entered into methods, to maintain valid ZPL data
* Using web service to render ZPL2 label as PNG for quick development
* Simple class to print to network based ZPL label printer



Not Implemented Commands
------------------------

The following commands are not implemented via methods or objects.  They can be added to the ZPL Document
using the `add_zpl_raw()` method.

Fields planned for implementation:

* ^CC/~CC - Change Caret
* ^CD/~CD - Change Delimiter
* ^CT/~CT - Change Tilde
* ^FP - Field Parameter
* ^FR - Field Reverse Print
* ^FT - Field Typeset
* ^FV - Field Variable
* ^FW - Field Orientation
* ^GC - Graphic Diagonal Line
* ^GE - Graphic Ellipse
* ^GF - Graphic Field
* ^GS - Graphic Symbol
* ~HI - Host Identification
* ~HQ - Host Query
* ~HS - Host Status Return
* ^ID - Object Delete
* ^IL - Image Load
* ^IM - Image Move
* ^IS - Image Save
* ^LR - Label Reverse Print
* ^LS - Label Shift
* ^LT - Label Top
* ^PM - Printing Mirror Image of Label
* ^PO - Print Orientation
* ^SF - Serialization Field

Fields with no current plan of implementation:

* ^A@ - Use Font Name to Call Font
* ^CF - Change Default Font
* ^CI - Change International Font/Encoding
* ^CM - Change Memory Letter Designation
* ^CN - Cut Now
* ^CO - Cache On
* ^CP - Remove Label
* ^CV - Code Validation
* ^CW - Font Identifier
* ~DB - Download Bitmap Font
* ~DE - Download Encoding
* ^DF - Download Format
* ~DG - Download Graphics
* ~DN - Abort Download Graphic
* ~DS - Download Intellifont
* ~DT - Download Bounded TTF
* ~DU - Download Unbounded TTF
* ~DY - Download Objects
* ^FC - Field Clock
* ^FH - Field Hexadecimal Indicator
* ^FL - Font Linking
* ^FN - Field Number
* ~HB - Battery Status
* ~HD - Head Diagnostic
* ^HF - Host Format
* ^HG - Host Graphic
* ^HH - Configuration Label Return
* ~HM - Host RAM Status
* ^HT - Host Linked Fonts List
* ~HU - Return ZebraNet Alert Configuration
* ^HV - Host Verification
* ^HW - Host Directory List
* ^HY - Upload Graphics
* ^HZ - Display Description Information
* ~JA - Cancel All
* ^JB - Initialize Flash Memory
* ~JB - Reset Optional Memory
* ~JC - Set Media Sensor Calibration
* ~JD - Enable Communication Diagnostics
* ~JE - Disable Diagnostics
* ~JF - Set Battery Condition
* ~JG - Graphing Sensor Calibration
* ^JH - Early Warning Settings
* ^JI - Start Zebra BASIC with Command
* ~JI - Start Zebra BASIC
* ^JJ - Set Auxiliary Port
* ~JL - Set Label Length
* ^JM - Ser Dots per mm
* ~JN - Head Test Fatal
* ~JO - Head Test Non-Fatal
* ~JP - Pause and Cancel Format
* ~JQ - Terminate Zebra BASIC
* ~JR - Power On Reset
* ^JS - Sensor Select
* ~JS - Change Backfeed Sequence
* ^JT - Head Test Interval
* ^JU - Configuration Update
* ^JW - Set Ribbon Tension
* ~JX - Cancel Partially Input Format
* ^JZ - Reprint After Error
* ~KB - Kill Battery
* ^KD - Select Date and Time Format
* ^KL - Define Language
* ^KN - Define Printer Name
* ^KP - Define Password
* ^KV - Kiosk Values
* ^LF - List Font Links
* ^LL - Label Length
* ^MA - Set Maintenance Alerts
* ^MC - Map Clear
* ^MD - Media Darkness
* ^MF - Media Feed
* ^MI - Set Maintenance Information Message
* ^ML - Maximum Label Length
* ^MM - Print Mode
* ^MN - Media Tracking
* ^MP - Mode Protection
* ^MT - Media Type
* ^MU - Set Units of Measurement
* ^MW - Modify Head Cold Warning
* ^NC - Select Primary Network Device
* ~NC - Network Connect
* ^ND - Change Network Settings
* ^NI - Network ID Number
* ~NR - Set All Network Printers Transparent
* ^NS - Changed Wired Network Settings
* ~NT - Set Printer Transparent
* ^PA - Advanced Text Properties
* ^PF - Slew Dot Rows
* ^PH/~PH - Slew to Home Position
* ~PL - Present Length Addition
* ^PN - Present Now
* ^PP/~PP - Programmable Pause
* ~PR - Applicator Reprint
* ^PR - Print Rate
* ~PS - Print Start
* ^PW - Print Width
* ~RO - Reset Advanced Counters
* ^SC - Set Serial Communications
* ~SD - Set Darkness
* ^SE - Select Encoding Table
* ^SI - Set Sensor Intensity
* ^SL - Set Mode and Language
* ^SO - Set Offset for RTC
* ^SQ - Halt ZebraNet Alert
* ^SR - Ser Printhead Resistance
* ^SS - Set Media Sensors
* ^ST - Set Date and Time
* ^SX - Set ZebraNet Alert
* ^SZ - Set ZPL Mode
* ~TA - Tear-off Adjust Position
* ^TO - Transfer Object
* ~WC - Print Configuration Label
* ^WD - Print Directory Label
* ~WQ - Write Query
* ^XB - Suppress Backfeed
* ^XF - Recall Format
* ^XG - Recall Graphic
* ^XS - Dynamic Media Calibration

Credits
---------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage

