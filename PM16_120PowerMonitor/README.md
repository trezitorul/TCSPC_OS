# PM16-120 Power Monitor

## Installation

Install [Thorlabs Optical Power Monitor software](https://www.thorlabs.com/software_pages/ViewSoftwarePage.cfm?Code=OPM)

[Operation manual](https://www.thorlabs.com/software/MUC/OPM/v1.0/TL_OPM_V1.0_web-secured.pdf)

## Code

TLPM.py contains TLPM class. PowerMeter.py contains the PowerMeter class to facilitate measurement, an example of which is in ex1.py. 

TLPM.py adapted from [Thorlabs](https://github.com/Thorlabs/Light_Analysis_Examples/tree/main/Python/Thorlabs%20PMxxx%20Power%20Meters)

May need to change DLL loading in TLPM.py lines 238-239 as per prev link's README.md
