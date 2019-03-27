#!/usr/bin/env python

import rrdtool
ret = rrdtool.create("netPred.rrd",
                     "--start",'N',
                     "--step",'1',
                     "DS:inoctets:COUNTER:600:U:U",                     
                     "RRA:AVERAGE:0.5:1:1000",
                     "RRA:HWPREDICT:30000:0.1:0.1:60:3",	#30 -> 30000
                     "RRA:SEASONAL:60:0.1:2",
                     "RRA:DEVSEASONAL:60:0.1:2",
                     "RRA:DEVPREDICT:30000:4",
                       "RRA:FAILURES:30000:7:9:4")

if ret:
    print rrdtool.error()

