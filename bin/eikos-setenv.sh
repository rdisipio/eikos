export PATH=$PWD/bin:$PWD/share:$PATH
export PYTHONPATH=$PWD/python:$PYTHONPATH

[ ! -d output ] && mkdir -p output
[ ! -d output/img ] && mkdir -p output/img

setupATLAS
lsetup "lcgenv -p LCG_93 x86_64-centos7-gcc62-opt ROOT git"
