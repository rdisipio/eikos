#!/usr/bin/env python

import os, sys

from array import array
import argparse
import xml.etree.ElementTree as ET

from ROOT import *

gSystem.Load( "libBAT.so")
gSystem.Load( "libEikos.so" )

from ROOT import *

BCLog.OpenLog("log.txt")
BCLog.SetLogLevel(BCLog.detail)
BCLog.OutSummary("Welcome to Eikos v2.0")

unfolder = EikosUnfolder()

# Read config file
parser = argparse.ArgumentParser(description='Eikos unfolder')
parser.add_argument( '-c', '--config', help="Configuration file", default="share/config_tt_allhad.xml" )
args = parser.parse_args()

xmlfilename = args.config
xmlconfig = ET.parse( xmlfilename ).getroot()

gparams = {}
xmlparams = xmlconfig.findall( "parameters/param" )
for param in xmlparams:
   name  = param.attrib['name']
   value = param.attrib['value']
   gparams[name] = value
   BCLog.OutSummary( "Param %-15s = %s" % (name,value) )

# Build template for diffxs
xmldiffxs = xmlconfig.findall( "diffxs" )[0]
diffxs_name = xmldiffxs.attrib['name']

diffxs_template = xmldiffxs.findall( "template" )[0]
fpath = diffxs_template.attrib['fpath']
fpath = fpath.replace("@INPUTPATH@", gparams['INPUTPATH'] )
fpath = fpath.replace("@PHSPACE@",   gparams['PHSPACE'] )
fpath = fpath.replace("@OBS@",       gparams['OBS'] )

hpath = diffxs_template.attrib['hpath']
hpath = hpath.replace("@OBS@",gparams['OBS'])
hpath = hpath.replace("@PHSPACE@",gparams['PHSPACE'])

f = TFile.Open( fpath )
h = f.Get( hpath ).Clone( diffxs_name )
unfolder.SetDiffXsTemplate( h )

# Define samples
xmlsamples = xmlconfig.findall( "samples/sample" )
for sample in xmlsamples:
   name = sample.attrib['name']

   xmldet = sample.findall("det")[0]

   fpath = xmldet.attrib['fpath']
   fpath = fpath.replace("@INPUTPATH@", gparams['INPUTPATH'] )
   fpath = fpath.replace("@PHSPACE@",   gparams['PHSPACE'] )
   fpath = fpath.replace("@OBS@", 	gparams['OBS'] )

   hpath = xmldet.attrib['hpath']
   hpath = hpath.replace("@OBS@",gparams['OBS'])
   hpath = hpath.replace("@PHSPACE@",gparams['PHSPACE'])   

xmlsystematics = xmlconfig.findall( "systematics/systematic" )
for syst in xmlsystematics:
   name  = syst.attrib['name']
   type  = syst.attrib['type']
   symm  = syst.attrib['symmetrize']
   label = syst.attrib['label'] 
   units = ""

   BCLog.OutSummary( "Defined systematic: %s" % ( name ) )
   unfolder.AddSystematic( name, -3.0, 3.0, label, units )

unfolder.PrintSummary()
