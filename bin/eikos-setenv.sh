# BAT stuff
export PATH="${HOME}/local/bin:$PATH"
export LD_LIBRARY_PATH="${HOME}/local/lib:$LD_LIBRARY_PATH"
export CPATH="${HOME}/local/include:$CPATH"
export PKG_CONFIG_PATH="${HOME}/local/lib/pkgconfig:$PKG_CONFIG_PATH"
export BATINSTALLDIR=${HOME}/local

# Eikos stuff
export PATH=$PWD/bin:$PWD/share:$PATH
export LD_LIBRARY_PATH=$PWD/lib:$LD_LIBRARY_PATH
export PYTHONPATH=$PWD/python:$PYTHONPATH


[ ! -d run ]            && mkdir -p run
[ ! -d run/output ]     && mkdir -p run/output
[ ! -d run/output/img ] && mkdir -p run/output/img

#ln -sf share/Atlas* run/.
#ln -sf share/rootlogon.C run/.

#setupATLAS -c slc6
#lsetup root
#lsetup git
