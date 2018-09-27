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


Generate toy MC sample
======================

```
cd run
eikos-generate-toyMC.py
```

You'll find a new file called ```toymc.root``` . It contains data, background, signal and prediction for the nominal, a few systematics and two alternative models.
The signal model is given by a Gamma distribution with shape parameter kappa and scale parameter theta. The two alternative models have a different value of either parameter.
The systematics are of two types: multiplicative (i.e. x' = a*x ) or additive (i.e. x' = x + a). 

To execute the program (batch mode) and store the output on a text file:
```
eikos.py input_toymc_simple.txt | tee stdout.txt
```

To create diffxs plots
```
eikos-plot-diffxs.py -c ../share/config_plot_toymc_x_abs.xml
eikos-plot-diffxs.py -c ../share/config_plot_toymc_x_rel.xml
```

To create systematics pull plots:
```
eikos-plot-systematics_pulls.py output/toymc_statsyst/x.toymc.statsyst.root
```

Other plots:
```
eikos-plot-migrations.py output/toymc_statsyst/x.toymc.statsyst.root
eikos-plot-corrections.py output/toymc_statsyst/x.toymc.statsyst.root 
eikos-plot-correlation-matrix.py output/toymc_statsyst/x.toymc.statsyst.root
```

Closure and stress tests
```
eikos.py ../share/input_toymc_statonly_closure.txt 
eikos-plot-closure.py closure
eikos-plot-closure.py stress
```

Configuration file
==================

This is a working example to be used with the ToyMC generated file. Detector systematics just need the reco-level. Modelling systematics need also the truth-level and response matrix in order to calcualte the correction factors.

```
set param  INPUTPATH $PWD
set param  OUTPUTPATH $PWD/output
set param  OUTPUTTAG toymc_statsyst
set param  LUMI 1.0
set param  PRECISION 2
set param  REGULARIZATION 1
set param  OBS x

set truth  path @INPUTPATH@/toymc.root:truth_nominal
set data   path @INPUTPATH@/toymc.root:data

add sample S
set sample S type signal
set sample S path nominal reco @INPUTPATH@/toymc.root:reco_nominal
set sample S path nominal resp @INPUTPATH@/toymc.root:response_nominal
set sample S path nominal gen  @INPUTPATH@/toymc.root:truth_nominal

add sample B
set sample B type background
set sample B path nominal reco @INPUTPATH@/toymc.root:bkg

add systematic syst1 -5 5
set systematic syst1 variations syst1_u syst1_d
set sample S path syst1_u reco @INPUTPATH@/toymc.root:reco_syst1_u
set sample S path syst1_d reco @INPUTPATH@/toymc.root:reco_syst1_d
set sample B path syst1_u reco @INPUTPATH@/toymc.root:bkg
set sample B path syst1_d reco @INPUTPATH@/toymc.root:bkg

add systematic syst2 -5 5
set systematic syst2 variations syst2_u syst2_d 
set sample S path syst2_u reco @INPUTPATH@/toymc.root:reco_syst2_u
set sample S path syst2_d reco @INPUTPATH@/toymc.root:reco_syst2_d
set sample B path syst2_u reco @INPUTPATH@/toymc.root:bkg
set sample B path syst2_d reco @INPUTPATH@/toymc.root:bkg

add systematic syst3 -5 5
set systematic syst3 variations syst3_u syst3_d 
set sample S path syst3_u reco @INPUTPATH@/toymc.root:reco_syst3_u
set sample S path syst3_d reco @INPUTPATH@/toymc.root:reco_syst3_d
set sample B path syst3_u reco @INPUTPATH@/toymc.root:bkg
set sample B path syst3_d reco @INPUTPATH@/toymc.root:bkg

add systematic syst4 -5 5
set systematic syst4 variations syst4_u syst4_d
set sample S path syst4_u reco @INPUTPATH@/toymc.root:reco_syst4_u
set sample S path syst4_d reco @INPUTPATH@/toymc.root:reco_syst4_d
set sample B path syst4_u reco @INPUTPATH@/toymc.root:bkg
set sample B path syst4_d reco @INPUTPATH@/toymc.root:bkg

add systematic syst_mod_kappa -5 5
set systematic syst_mod_kappa type modelling
set systematic syst_mod_kappa variations syst_mod_kappa_u @symmetrize@
set sample S path syst_mod_kappa_u reco @INPUTPATH@/toymc.root:reco_modelling_kappa
set sample S path syst_mod_kappa_u resp @INPUTPATH@/toymc.root:response_modelling_kappa
set sample S path syst_mod_kappa_u gen  @INPUTPATH@/toymc.root:truth_modelling_kappa
set sample B path syst_mod_kappa_u reco @INPUTPATH@/toymc.root:bkg

add systematic syst_mod_theta -5 5
set systematic syst_mod_theta type modelling
set systematic syst_mod_theta variations syst_mod_theta_u @symmetrize@
set sample S path syst_mod_theta_u reco @INPUTPATH@/toymc.root:reco_modelling_theta
set sample S path syst_mod_theta_u resp @INPUTPATH@/toymc.root:response_modelling_theta  
set sample S path syst_mod_theta_u gen  @INPUTPATH@/toymc.root:truth_modelling_theta
set sample B path syst_mod_theta_u reco @INPUTPATH@/toymc.root:bkg


set outfile $PWD/output/@OUTPUTTAG@/@OBS@.toymc.statsyst.root
set luminosity 1.0
set regularization curvature

set precision quick
set prior flat
run stage:prior nitr:0 drawplots:yes

set precision custom
set prior gauss
run stage:statsyst nitr:0 drawplots:yes writehist:yes

set precision custom
set prior gauss
run stage:statonly nitr:0 drawplots:no writehist:yes

exit
```
