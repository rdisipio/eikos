#!/usr/bin/env python

import os, sys

from array import array
import xml.etree.ElementTree as ET

from ROOT import *

gSystem.Load( "libBAT.so")
from ROOT import BCAux#, BCLog

exit(1)
BCAux.SetStyle();

BCLog.OpenLog("log.txt")
BCLog.SetLogLevel(BCLog.detail)
BCLog.OutSummary("Welcome to Eikos v2.0")

