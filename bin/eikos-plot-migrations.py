#!/usr/bin/env python

import sys, os

#from numpy import array
from array import array
from ROOT import *

from defs import *

gROOT.SetBatch(1)

gROOT.Macro("rootlogon.C")
#gROOT.LoadMacro("AtlasUtils.C")

########################################################################

def NormalizeRows( h ):
   gStyle.SetPaintTextFormat("2.0f")
  
   nbinsX = h.GetNbinsX()
   nbinsY = h.GetNbinsY()

   for j in range( nbinsY ):
     sumw = 0.
     for i in range( nbinsX ):
       sumw += h.GetBinContent( i+1, j+1 )
     for i in range( nbinsX ):
       y_old = h.GetBinContent( i+1, j+1 )
       y_new = y_old / sumw if not sumw == 0. else 0.
       if abs(y_new) < 0.01: y_new = 0. #!!!
       h.SetBinContent( i+1, j+1, y_new ) 

   h.Scale( 100. )
   h.SetMaximum( 100. )
   h.SetMinimum( 0. )

########################################################################


def SetPalette( colset = "green" ):
    if colset == "green":
       stops = array( 'd', [ 0.00, 0.80, 1.00 ] )
       red   = array( 'd', [ 1.00, 0.43, 0.67 ] )
       green = array( 'd', [ 1.00, 0.78, 0.86 ] )
       blue  = array( 'd', [ 1.00, 0.69, 0.79 ] )
#        stops = array( 'd', [ 0.00, 0.25, 1.00 ] )        
#        red   = array( 'd', [ 0.67, 0.43, 0.05 ] )
#        green = array( 'd', [ 0.86, 0.78, 0.59 ] )
#        blue  = array( 'd', [ 0.79, 0.69, 0.53 ] )

    if colset == "blue":
        stops = array( 'd', [ 0.00, 0.80, 1.00 ] )
        
        red   = array( 'd', [ 1.00, 0.00, 0.00 ] )
        green = array( 'd', [ 1.00, 0.62, 0.40 ] )
        blue  = array( 'd', [ 1.00, 0.88, 0.72 ] )

    if colset == "blue2redB":
        stops = array( 'd', [ 0.00, 0.35, 0.65, 1.00 ] )
        
        # 286CP / 284CP / x / 177CP / 7627CP
        red   = array( 'd', [ 0.13, 0.45, 0.96, 0.74 ] )
        green = array( 'd', [ 0.31, 0.67, 0.69, 0.29 ] )
        blue  = array( 'd', [ 0.60, 0.85, 0.72, 0.14 ] )

    if colset == "blue2red":
        stops = array( 'd', [ 0.00, 0.10, 0.50, 0.90, 1.00 ] )
        # 286CP / 284CP / x / 177CP / 7627CP
        red   = array( 'd', [ 0.13, 0.45, 1.00, 0.96, 0.74 ] )
        green = array( 'd', [ 0.31, 0.67, 1.00, 0.69, 0.29 ] )
        blue  = array( 'd', [ 0.60, 0.85, 1.00, 0.72, 0.14 ] )

    TColor.CreateGradientColorTable( len(stops), stops, red, green, blue, 100 )
#gStyle.SetPalette(1)


########################################################################

def DrawGrid( h ):
    line = TLine()
    line.SetLineWidth( 1 )
    line.SetLineColor( kWhite )
    
    xaxis = h.GetXaxis()
    yaxis = h.GetYaxis()
    
    #xaxis.SetMoreLogLabels()
    #yaxis.SetMoreLogLabels()
    
    for binx in range( 0, h.GetNbinsX() ):
        xmin = xaxis.GetBinLowEdge( binx + 1 )
        
        if not xmin == xaxis.GetXmin():
            line.DrawLine( xmin, yaxis.GetXmin(), xmin, yaxis.GetXmax() )
    
    for biny in range( 0, h.GetNbinsY() ):
        ymin = yaxis.GetBinLowEdge( biny + 1 )
        
        if not ymin == yaxis.GetXmin():
            line.DrawLine( xaxis.GetXmin(), ymin, xaxis.GetXmax(), ymin )


########################################################################

def ATLAS_LABEL_custom( x, y, color ):
    ATLAS_LABEL( x, y, color )
#    myText( x+0.17, y,     color, "Simulation Internal #sqrt{s} = 13 TeV" )
    myText( x+0.17, y,     color, "Simulation Preliminary #sqrt{s} = 13 TeV" )

########################################################################


def MakeCanvas():
    c = TCanvas( "Response Matrix", "Response Matrix", 800, 800 )
    
    gPad.SetLeftMargin( 0.15 )
    gPad.SetRightMargin( 0.15 )
    gPad.SetBottomMargin( 0.15 )
    gPad.SetTopMargin( 0.05 )
    
    #c.SetLogy()
    #c.SetLogx()
    #c.SetLogz()
    
    return c


########################################################################

def MakeAllAbsValues( matrix ):
    hm = matrix.Clone( "abs" )
    hm.SetMinimum(-1.)
    hm.SetMaximum(1.)
    return hm
    for i in range( matrix.GetNbinsX() ):
        for j in range( matrix.GetNbinsY() ):
            v = matrix.GetBinContent( i+1, j+1 )
            hm.SetBinContent( i+1, j+1, abs(v) )
    
    return hm

########################################################################


def MakeUniformBins( h ):
   nbins_x = h.GetNbinsX()
   xmin = h.GetXaxis().GetXmin()
   xmax = h.GetXaxis().GetXmax()

   nbins_y = h.GetNbinsY()
   ymin = h.GetYaxis().GetXmin() 
   ymax = h.GetYaxis().GetXmax()

   hnew = TH2D( "hcorr", "hcorr", nbins_x, 0, nbins_x, nbins_y, 0, nbins_y )
#   hnew = TH2D( "hcorr", "hcorr", nbins, xmin, xmax, nbins, xmin, xmax )

   for i in range(nbins_x):
      for j in range(nbins_y):
         y = h.GetBinContent( i+1, j+1 )
         hnew.SetBinContent( i+1, j+1, y )

   for i in range(nbins_x):
     hnew.GetXaxis().SetNdivisions( nbins_x, 0, 0 )

   for i in range(nbins_y):
     hnew.GetYaxis().SetNdivisions( nbins_y, 0, 0 )

#     hnew.GetXaxis().SetBinLabel( i+1, "%i" % (i+1) )
#     hnew.GetYaxis().SetBinLabel( i+1, "%i" % (i+1) )
     
#     hnew.GetXaxis().SetBinLabel( i+1, "%.1g" % h.GetXaxis().GetXbins()[i+1] )
#     hnew.GetYaxis().SetBinLabel( i+1, "%.1g" % h.GetYaxis().GetXbins()[i+1] )

   hnew.GetXaxis().SetLabelOffset(999)
   hnew.GetYaxis().SetLabelOffset(999)

   return hnew


#######################################################################

def KillZeros( h, z_min = 1.0 ):

    for i in range( h.GetNbinsX() ):
        for j in range( h.GetNbinsY() ):
            z = h.GetBinContent( i+1, j+1 )
            if z < z_min: h.SetBinContent( i+1, j+1, -100000000 )
    return h


phspace = "particle"
obs = "t2_pt"

# Make the plot

gStyle.SetPaintTextFormat( "3.0f%" )
gStyle.SetHistMinimumZero()

if phspace == "parton":
  SetPalette( "blue" )
else:
  SetPalette( "green" )


infilename = "output/statsyst/%s.diffxs.root" % obs
if len(sys.argv) > 1: 
   infilename = sys.argv[1]
infile = TFile.Open( infilename )
obs = infilename.split("/")[-1].split(".")[0]

if len( sys.argv ) > 2:
  obs = sys.argv[2]

hname = "migrations"
h_raw = infile.Get( hname )

if h_raw == None:
  print "ERROR: invalid histogram", hname, infilename
  exit(1)

NormalizeRows( h_raw )

c = MakeCanvas()

#uniform binning?
#h  = h_raw
h = MakeUniformBins( h_raw )
KillZeros( h )
#h.SetMinimum(1.0)

h.Draw("colz text")
DrawGrid( h )
h.GetZaxis().SetRangeUser( 0., 100. )
h.GetZaxis().SetLabelSize(0.03)
h.GetZaxis().SetTitle( "Migrations [%]" )
h.GetZaxis().SetTitleSize( 0.04 )
h.GetZaxis().SetTitleOffset( 1.1 )

h.GetXaxis().SetLabelSize( 0.05 )
h.GetYaxis().SetLabelSize( 0.05	)
h.GetXaxis().SetTitleSize( 0.04 )
h.GetYaxis().SetTitleSize( 0.04 )
#h.GetXaxis().SetLabelOffset(0.01)
h.GetXaxis().SetTitleOffset(1.3)
h.GetYaxis().SetTitleOffset(1.8)
#h.GetXaxis().SetTickLength(0)
#h.GetYaxis().SetTickLength(0)

labelX = TText()
labelY = TText()
labelX.SetTextSize(0.04)
labelX.SetTextAlign(23)
labelY.SetTextSize(0.04)
labelY.SetTextAlign(32)

ylabel = h.GetYaxis().GetBinLowEdge(1) - 0.2*h.GetYaxis().GetBinWidth(1)
xlabel = h.GetXaxis().GetBinLowEdge(1) - 0.1*h.GetXaxis().GetBinWidth(1)
for i in range(h.GetNbinsX()+1):
   xlow = h_raw.GetXaxis().GetBinLowEdge(i+1)
   x = h.GetXaxis().GetBinLowEdge(i+1)
   labelX.DrawText( x, ylabel, "%g"%xlow )
for i in range(h.GetNbinsY()+1):
   xlow = h_raw.GetYaxis().GetBinLowEdge(i+1)
   y = h.GetYaxis().GetBinLowEdge(i+1)
   labelY.DrawText( xlabel, y, "%g"%xlow )

u = "[%s]"%units[obs] if not units[obs]=="" else ""
h.GetXaxis().SetTitle( "Detector level %s %s" % (pretty_names[obs], u ) )
h.GetYaxis().SetTitle( "Truth level %s %s" % ( pretty_names[obs], u ) )

h.SetMarkerSize(1.5)

gPad.RedrawAxis()

c.SaveAs( "output/img/migrations_%s.pdf" % ( obs ) )
