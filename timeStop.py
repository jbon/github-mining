#############################################################################################
# SCRIPT INFORMATION
#############################################################################################

# LICENSE INFORMATION:
#---------------------
# timestop.py
# Delivers functions to trace execution time
# Author: Jérémy Bonvoisin
# Homepage: http://opensourcedesign.cc
# License: GPL v.3

#############################################################################################
# HEADER
#############################################################################################

import datetime

class timeStop:
    def __init__(self):
        self.lastStop = datetime.datetime.now()
        self.firstStop = self.lastStop
    def stop(self):
        newStop = datetime.datetime.now()
        intervalAbs = newStop - self.firstStop
        intervalRel = newStop - self.lastStop
        self.lastStop = newStop
        return str(intervalAbs.seconds//60) +"m "+ str(intervalAbs.seconds%60) + "s elapsed (" + str(intervalRel.seconds) + "s since last stop)"
