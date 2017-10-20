Eikos
=====

Installation
============

Master repository is https://gitlab.cern.ch/disipio/Eikos

To download the code
```bash
git clone https://:@gitlab.cern.ch:8443/disipio/Eikos.git
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
