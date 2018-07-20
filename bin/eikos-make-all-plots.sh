#!/bin/bash

infile=$PWD/output/toymc_statsyst/x.toymc.statsyst.root 

eikos-plot-corrections.py $infile
eikos-plot-migrations.py $infile
eikos-plot-systematics_pulls.py $infile
eikos-plot-diffxs.py config_plot_toymc_x_abs.xml
eikos-plot-diffxs.py config_plot_toymc_x_abs.xml

