#!/usr/bin/env python

import os, sys
import argparse 
import xml.etree.ElementTree as ET

GeV = 1000.
iLumi = 36.1

from PlottingToolkit import *

from ROOT import *

gROOT.Macro( "rootlogon.C" ) 
gROOT.LoadMacro( "AtlasUtils.C" ) 
# os.path.expanduser( "share/rootlogon.C" ) )
#gROOT.LoadMacro( os.path.expanduser( "$PWD/share/AtlasUtils.C" ) )

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class PlotScale:
   unknown = 0
   linear  = 1
   logy    = 2
   logx    = 3
   bilog   = 4

   @classmethod
   def ToScale( self, txt ): 
      if   txt.lower() == "linear": return self.linear
      elif txt.lower() == "logy":   return self.logy
      elif txt.lower() == "logx":   return self.logx
      elif txt.lower() == "bilog":  return self.bilog
      else:                         return self.unknown

   @classmethod
   def ToString( self, scale ):
      if scale   == self.linear: return "linear"
      elif scale == self.logy:   return "logy"
      elif scale == self.logx:   return "logx"
      elif scale == self.bilog:  return "bilog"
      else:                      return "unknown"


class PlotWrapper:
   obs     = ""
   hname   = ""
   hpath   = ""
   xtitle  = ""
   ytitle  = ""
   scale   = PlotScale.linear
   tag     = "TightTop"
   phspace = "particle"
   meas    = "abs"
   latex   = "My plot"

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class SampleType:
   unknown     = 0
   data        = 1
   signal      = 2
   background  = 3
   datadriven  = 4
   uncertainty = 5

   @classmethod
   def ToType( self, txt ):
       t = txt.lower()
       if   t == "data":        return self.data
       elif t == "signal":      return self.signal
       elif t == "background":  return self.background
       elif t == "datadriven":  return self.datadriven
       elif t == "uncertainty": return self.uncertainty
       elif t == "unc":         return self.uncertainty
       else:                    return self.unknown

class SampleWrapper:
   id          = -1
   name        = ""
   type        = SampleType.unknown
   latex       = ""
   color       = 1
   markerstyle   = 0
   linewidth   = 3
   linestyle   = 1
   fill_color  = 0
   fill_style  = 1001
   alpha       = 1

####################################################


def ReadConfiguration( configFileName ):
   xmldoc = ET.parse( configFileName )

   if xmldoc == None:
      print "ERROR: cannot parse input file", configFileName
      exit(1)

   plots_configuration = {}

   tag     = ""
   latex   = ""
   phspace = ""
   meas    = ""

   for node in xmldoc.findall( ".//plots" ):
     tag         = node.attrib['tag']
     latex       = node.attrib['latex']
     phspace     = node.attrib['phspace']
     meas        = node.attrib['meas']

   for node in xmldoc.findall( ".//plots/plot" ):
     obs         = node.attrib['obs']
     hname = "%s_%s_%s_%s" % ( obs, phspace, tag, meas )

     plots_configuration[hname] = PlotWrapper()
     plots_configuration[hname].obs     = obs
     plots_configuration[hname].meas    = meas 
     plots_configuration[hname].hname   = hname
     plots_configuration[hname].hpath   = "" # to be determined later
     plots_configuration[hname].xtitle  = node.attrib['xtitle']
     plots_configuration[hname].ytitle  = node.attrib['ytitle']
     plots_configuration[hname].tag     = tag
     plots_configuration[hname].phspace = phspace
     plots_configuration[hname].latex   = latex
     plots_configuration[hname].meas   = meas

     scale  = node.attrib['scale']
     plots_configuration[hname].scale  = PlotScale.ToScale( scale )

   samples_configuration = {}
   i = 0
   for node in xmldoc.findall( ".//samples/sample" ):
      name = node.attrib['name']

      print "INFO: adding sample", name
      samples_configuration[name] = SampleWrapper()
      samples_configuration[name].id          = i
      samples_configuration[name].name        = name
      samples_configuration[name].hpath       = node.attrib['hpath']
      samples_configuration[name].type        = SampleType.ToType( node.attrib['type'] ) 
      samples_configuration[name].latex       = node.attrib['latex']
      samples_configuration[name].color       = int( node.attrib['color'] )
      samples_configuration[name].markerstyle = int( node.attrib['markerstyle'] ) if node.attrib.has_key('markerstyle') else 20
      samples_configuration[name].linewidth   = int( node.attrib['linewidth'] )   if node.attrib.has_key('linewidth')   else 1.
      samples_configuration[name].linestyle   = int( node.attrib['linestyle'] )   if node.attrib.has_key('linestyle')   else kSolid
      samples_configuration[name].fill_color  = int( node.attrib['fill_color'] )  if node.attrib.has_key('fill_color')  else 0
      samples_configuration[name].fill_style  = int( node.attrib['fill_sytle'] )  if node.attrib.has_key('fill_sytle')  else 1001 
      samples_configuration[name].alpha       = float( node.attrib['alpha'] )     if node.attrib.has_key('alpha')       else 1.

      i += 1

   input_files = {}
   for node in xmldoc.findall( ".//inputfiles/file" ):
      sample = node.attrib['sample']
      path  = node.attrib['path']

      input_files[sample] = path

   return plots_configuration, samples_configuration, input_files


############################################


def FetchHistograms( hname ):
    histograms = {}

    for sample, sample_config in samples_configuration.iteritems():

       infilename = input_files[sample].replace( "@OBS@", plots_configuration[hname].obs )
       infile     = TFile.Open( infilename )

       newname = "%s_%s" % ( sample, sample_config.hpath )
       gROOT.cd()
       hpath = sample_config.hpath.replace( "@OBS@", plots_configuration[hname].obs )
       histograms[sample] = infile.Get( hpath ).Clone( newname )
#       print "DEBUG:", sample, hpath, infilename

       DivideByBinWidth( histograms[sample] )

    gROOT.cd()
    return histograms


############################################

def SetHistogramsStyle( hlist ):
    for sample, h in hlist.iteritems():
       col  = samples_configuration[sample].color
       ms   = samples_configuration[sample].markerstyle
       ls   = samples_configuration[sample].linestyle
       type = samples_configuration[sample].type
       lw   = samples_configuration[sample].linewidth
       fill_col = samples_configuration[sample].fill_color
       fill_sty = samples_configuration[sample].fill_style
       alpha    = samples_configuration[sample].alpha

       if type == SampleType.data:
           SetTH1FStyle( h, color=kBlack, markersize=1, markerstyle=20, linewidth=lw )  
       if type == SampleType.signal:      
          SetTH1FStyle( h, color=col, markersize=1, markerstyle=ms, linewidth=lw, linestyle=ls, fillcolor=0, fillstyle=0 )
       if type == SampleType.uncertainty:
          SetTH1FStyle( h, color=col, markersize=0, markerstyle=0, linewidth=0, fillcolor=fill_col, fillstyle=fill_sty, fill_alpha=alpha )

    SetAxesStyle( hlist.values() )

############################################

def DoPlot( pconfig ):
   print "INFO: plotting %s" % ( pconfig.hname )

   histograms = FetchHistograms( pconfig.hname )

   SetHistogramsStyle( histograms )

   pad0.SetLogy(False)
   pad0.SetLogx(False)
   pad1.SetLogy(False)
   pad1.SetLogx(False)

   pad0.cd()

   factor=1.
   if pconfig.meas=="abs" : factor=2.
   else: factor = 1.6
   histograms['data'].GetYaxis().SetTitle( plot.ytitle )
   if plot.scale in [ PlotScale.logy, PlotScale.bilog ]:
      histograms['data'].SetMaximum( 50*histograms['data'].GetBinContent( histograms['data'].GetMaximumBin() ))
      histograms['data'].SetMinimum( 0.07*histograms['data'].GetMinimum() )
   if plot.scale in [ PlotScale.linear, PlotScale.logx ]:
     histograms['data'].SetMaximum( 2. * histograms['data'].GetBinContent( histograms['data'].GetMaximumBin() ))
#      histograms['data'].SetMaximum( factor * histograms['data'].GetBinContent( histograms['data'].GetMaximumBin() ))
     histograms['data'].SetMinimum( 0. )

   histograms['data'].GetXaxis().SetNdivisions(508)

   histograms['data'].Draw("p")
   histograms['statsyst'].Draw( 'e2 same' )
#   histograms['statonly'].Draw( 'e2 same' )

   predictions = []
   ordered_samples = [ "" for i in range( len(histograms) ) ]
   for sname, h in histograms.iteritems():
     if sname in [ 'data', 'statsyst', 'statonly' ]: continue
     h.Draw("hist ][ same")
     predictions += [ h ]
     id = samples_configuration[sname].id
     ordered_samples[id] = sname
   ordered_samples = [ s for s in ordered_samples if s != "" ]  

   histograms[ordered_samples[0]].Draw("hist ][ same")
   histograms['data'].Draw("ep same")

   # Print Legend
   lparams = {
        'xoffset' : 0.57,
        'yoffset' : 0.92,
        'width'   : 0.3,
        'height'  : 0.048
        }

   leg = MakeLegend( lparams )
   leg.AddEntry( histograms['data'], samples_configuration['data'].latex, "ep" )
   for sname in ordered_samples:
      leg.AddEntry( histograms[sname], samples_configuration[sname].latex, "l" )
#   leg.AddEntry( histograms['statonly'], "Stat. Unc.", "f" )
   leg.AddEntry( histograms['statsyst'], "Stat. #oplus Syst. Unc.", "f" )
   leg.Draw()
   leg.SetY1( leg.GetY1() - lparams['height'] * leg.GetNRows() )

   PrintATLASLabel( 0.23, 0.87, "Internal", iLumi )
#   PrintATLASLabel( 0.23, 0.87, "Preliminary", iLumiAll )

   txt = TLatex()
   txt.SetNDC()
   txt.SetTextFont(42)
   if pconfig.phspace == "particle": 
     txt.SetTextSize(0.05)
     txt.DrawLatex( 0.23, 0.75, "%s" % pconfig.latex )
   else:                             
     txt.SetTextSize(0.04)
     txt.DrawLatex( 0.23, 0.775, "%s" % "Parton level" )
     txt.SetTextSize(0.035)
     txt.DrawLatex( 0.23, 0.73,"%s" % pconfig.latex)

   
   #if pconfig.phspace == "particle":
   #   txt.DrawLatex( 0.23, 0.75, "Fiducial particle level" )
   #elif pconfig.phspace == "parton":
   #   txt.DrawLatex( 0.23, 0.75, "Fiducial parton level" )
   #elif pconfig.phspace == "full":
   #   txt.DrawLatex( 0.23, 0.75, "Full phase-space" )
   #else:
   #   pass

   if plot.scale == PlotScale.linear:
      pad0.SetLogx(False)
   if plot.scale == PlotScale.logy: 
      pad0.SetLogy(True)
   if plot.scale == PlotScale.logx:
      pad0.SetLogx(True)
   if plot.scale == PlotScale.bilog: 
      pad0.SetLogy(True)
      pad0.SetLogx(True)
   
   if not plot.scale in [ PlotScale.logy, PlotScale.bilog ]:
     # Mask the damn zero!
     box = TPad( "mask", "mask", 0.15, 0.0, 0.185, 0.04, kWhite, 0, 0 )
     box.Draw()

   # Draw ratio pad

   pad1.cd()

   yrange = [ 0.4, 1.6 ]
   if pconfig.meas in [ "abs", "AbsoluteDiffXs" ]:
     #yrange = [ 0.4, 1.6 ]
     yrange = [ 0., 2.4 ]
   elif pconfig.meas in [ "rel", "RelativeDiffXs" ]:
      yrange = [ 0.4, 1.6 ]
      if pconfig.obs in [ 'tt_HT' ]: yrange = [ 0., 2.4 ]
      if pconfig.obs in [ 't1_y', 't2_y', 'tt_y', 'tt_yB', 'tt_cosThS', 'tt_chi' ]: yrange = [ 0.65, 1.35 ]
   else:
      print "ERROR: unknwon type of measurement", pconfig.meas
   print "DEBUG:", pconfig.obs, yrange

   frame, tot_unc, ratio = DrawRatio( histograms['statsyst'], predictions, plot.xtitle, yrange )   

   if plot.scale in [ PlotScale.bilog, PlotScale.logx ]: 
     pad1.SetLogx(True)
     pad1.SetLogy(False)
     frame.GetXaxis().SetMoreLogLabels(True)
     frame.GetXaxis().SetNoExponent(True)

    ## save image

   c.cd()
   for ext in [ "pdf" ]:
     imgname = "output/img/%s.%s" % ( pconfig.hname, ext )
     c.SaveAs( imgname ) 


############################################

if __name__ == "__main__":
   
   parser = argparse.ArgumentParser( description="%prog [options] configfile.xml" )
   parser.add_argument( "-b", "--batch", help="Batch mode [%default]", dest="batch", default=True )
   parser.add_argument( "-c", "--config", help="XML configuration [%default]", dest="config", default="config.xml" )
   args = parser.parse_args()
 
   if args.batch:
        gROOT.SetBatch(True)

   configFileName = args.config
   plots_configuration, samples_configuration, input_files = ReadConfiguration( configFileName )

   c, pad0, pad1 = MakeCanvas()

   for key, plot in plots_configuration.iteritems():
      DoPlot( plot )
 
