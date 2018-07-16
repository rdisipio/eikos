#!/usr/bin/env python

import os, sys
from ROOT import *
from array import array

#############################

class SystType:
   additive       = 0
   multiplicative = 1

#~~~~~~~

class Systematic(object):
  def __init__( self, name="syst", type=SystType.multiplicative, effect=10., twosided=True ):
    self.name     = name
    self.type     = type
    self.effect   = effect
    self.twosided = twosided

#~~~~~~~

  def Apply(self, x):
    y = 0.

    if self.type == SystType.additive:
      y = x + self.effect
    elif self.type == SystType.multiplicative:
      y = x * ( 1 + self.effect/100.)
    else:
      print "ERROR: unknown systematic type", self.type

    return y

#############################


outpath = "data/toymc/"

syst = "nominal"
Nevents = 10000

known_systematics = [
  Systematic( name="syst1_u", type=SystType.multiplicative, effect=5.00,  twosided=True ),
  Systematic( name="syst1_d", type=SystType.multiplicative, effect=-5.00, twosided=True ),
  Systematic( name="syst2_u", type=SystType.multiplicative, effect=-2.00, twosided=True ),
  Systematic( name="syst2_d", type=SystType.multiplicative, effect=3.00,  twosided=True ),
  Systematic( name="syst3_u", type=SystType.additive,       effect=20.,   twosided=True ),
  Systematic( name="syst3_d", type=SystType.additive,       effect=-20.,  twosided=True ),
]

ofilename = "toymc.%s.root" % ( syst )
ofile = TFile.Open( outpath + ofilename, "RECREATE" )
ofile.cd()

# Observable (think of pT) is drawn from a Gamma distribution
# then smeared according to the chosen systematic

xedges = array( 'd', [ 0., 10., 20., 30., 40., 50., 70.,  100. ] )
_h = {
 'nominal' : TH1F( "x_nominal", "Observable X", len(xedges)-1, xedges )
}
for syst in known_systematics:
  _h[syst.name] = _h['nominal'].Clone( "x_%s"%syst.name )
  print "INFO: systematic %-10s: %.2f %i" % ( syst.name, syst.effect, syst.type )
for h in _h.values(): h.Sumw2()

f_gamma = TF1("fgamma", "TMath::GammaDist(x, [0], [1], [2])", 0, 100 );
f_gamma.SetParameters( 4., 0., 10. )

for ievent in range(Nevents):
  x = f_gamma.GetRandom()

  _h['nominal'].Fill( x )

  for syst in known_systematics:
    y = syst.Apply(x)
    _h[syst.name].Fill( y )

ofile.Write()
ofile.Close()
