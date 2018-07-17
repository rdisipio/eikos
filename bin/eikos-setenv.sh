export PATH=$PWD/bin:$PWD/share:$PATH
export PYTHONPATH=$PWD/python:$PYTHONPATH

[ ! -d run ]            && mkdir -p run
[ ! -d run/output ]     && mkdir -p run/output
[ ! -d run/output/img ] && mkdir -p run/output/img

setupATLAS
lsetup "lcgenv -p LCG_93 x86_64-centos7-gcc62-opt ROOT"
lsetup git
