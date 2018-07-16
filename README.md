Eikos
=====

Installation
============

Master repository is https://gitlab.cern.ch/disipio/Eikos

Introductory slides: https://www.dropbox.com/s/uxfdtn74z7fxqpx/disipio_2017_10_18-eikos_bayesian_unfolding.pdf

To download the code
```bash
git clone https://gitlab.cern.ch/disipio/Eikos.git
```

To set up the environment:

```
source bin/eikos-setenv.sh 
```

This script will also create the directories output and img if not present.

To execute the program (batch mode):
```
eikos.py config.txt
```

To create diffxs plots
```
eikos-plot-diffxs.py -c share/config_plot_diffxs_tt_m_abs.xml
```

To create systematics pull plots:
```
eikos-plot-systematics_pulls.py
```

Configuration file
==================

This is a non-working example. Modeling systematics just need the reco-level. Modelling systematics need also the truth-level and response matrix in order to calcualte the correction factors.

```
set param  INPUTPATH /path/to/root/file/containing/histograms
set param  LUMI 36074.6
set param  PRECISION 2
set param  OBS tt_m
set data   path @INPUTPATH@/data/dataAll_13TeV.DAOD_TOPQ4.TightTop.histograms.root:@OBS@_passed_J1_1t1b_J2_1t1b
add sample ttAH
set sample ttAH type signal
set sample ttAH path nominal reco  @INPUTPATH@/nominal/mc.tt_pp8.nominal.root:@OBS@_passed_4j2b
set sample ttAH path nominal resp  @INPUTPATH@/nominal/mc.tt_pp8.nominal.root:response_particle_@OBS@_passed_4j2b
set sample ttAH path nominal gen   @INPUTPATH@/particle/mc.tt_pp8.nominal.root:@OBS@_passed_4j2b
add sample background
set sample background type background
set sample background path nominal reco @INPUTPATH@/nominal/mc.bkg.nominal.root:@OBS@_passed_4j2b

add systematic JES -5 5
set systematic JES variations JES__1u JES__1d
set sample ttAH       path JES__1u reco @INPUTPATH@/JES__1u/mc.tt_pp8.JES__1u.root:@OBS@_passed_4j2b
set sample background path JES__1u reco @INPUTPATH@/JES__1u/mc.bkg.JES__1u.root:@OBS@_passed_4j2b
set sample ttAH       path JES__1d reco @INPUTPATH@/JES__1d/mc.tt_pp8.JES__1d.root:@OBS@_passed_4j2b
set sample background path JES__1d reco @INPUTPATH@/JES__1d/mc.bkg.JES__1d.root:@OBS@_passed_4j2b

add systematic HardScattering -5 5
set systematic HardScattering type modelling
set systematic HardScattering variations mod_hs__1up @symmetrize@
set sample ttAH       path mod_hs__1up reco @INPUTPATH@/mod_hs__1up/mc.tt_mg5_amcp8.nominal.root:@OBS@_passed_4j2b
set sample ttAH       path mod_hs__1up resp @INPUTPATH@/mod_hs__1up/mc.tt_mg5_amcp8.nominal.root:response_particle_@OBS@_passed_4j2b
set sample ttAH       path mod_hs__1up gen  @INPUTPATH@/particle/mc.tt_mg5_amcp8.nominal.root:@OBS@_passed_4j2b
set sample background path mod_hs__1up reco @INPUTPATH@/mod_hs__1up/mc.bkg_mg5_amcp8.nominal.root:@OBS@_passed_4j2b

run
exit

```
