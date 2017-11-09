# Root variables
ROOTCFLAGS   := $(shell root-config --cflags)
ROOTLIBS     := -lMinuit $(shell root-config --libs)
ROOTLIBS     += -lRooFitCore -lRooFit -lRooStats -lFoam -lMathMore

# compiler and flags
OMPFLAGS     = -fopenmp -lgomp
CXX          = g++
CXXFLAGS     =  -g -Wall -fPIC -Wno-deprecated -O2
LD           = /usr/bin/ld -m elf_x86_64
LDFLAGS      =  -g -O2
SOFLAGS      = -shared

# standard commands
RM           = rm -f
MV           = mv
ECHO         = echo
CINT         = /cvmfs/atlas.cern.ch/repo/sw/software/17.4.0/sw/lcg/app/releases/ROOT/5.30.02/x86_64-slc5-gcc43-opt/root/bin/rootcint

# add ROOT flags
CXXFLAGS    += $(ROOTCFLAGS) 

CXXFLAGS    += -I. -I./include -I$(BATINSTALLDIR)/include
LIBS        += -L$(BATINSTALLDIR)/lib -lBATmodels -lBAT -lBATmtf $(ROOTLIBS)

CXXSRCS      = src/EikosUnfolder.cxx src/Sample.cxx

CXXOBJS      = $(patsubst %.cxx,%.o,$(CXXSRCS))

EXEOBJS      =
MYPROGS      = run-Eikos

GARBAGE      = $(CXXOBJS) $(EXEOBJS) *.o *~ link.d $(MYPROGS) src/*Dict.cxx src/*Dict.o src/*.pcm

# targets
all : library

link.d : $(patsubst %.cxx,%.h,$(CXXSRCS))
	$(CXX) -MM $(CXXFLAGS) $(CXXSRCS) > link.d;

-include link.d

src/EikosUnfolderDict.cxx :  
	rootcint -f src/EikosUnfolderDict.cxx -c include/EikosUnfolder.h include/LinkDef.h

%.o : %.cxx
	$(CXX) $(CXXFLAGS) -fPIC -c $< -o $@

clean :
	$(RM) $(GARBAGE)

library: src/EikosUnfolderDict.o $(CXXOBJS)
	@echo
	@echo Building shared library libEikos.so
	@echo 
	$(CXX) -shared -fPIC -Wl,-soname,libEikos.so -o libEikos.so $(CXXOBJS) src/EikosUnfolderDict.o $(LIBS) -lc

install:
	mv libEikos.so $(BATINSTALLDIR)/lib
	mv EikosUnfolderDict_rdict.pcm $(BATINSTALLDIR)/lib

print :
	echo compiler  : $(CXX)
	echo c++ srcs  : $(CXXSRCS)
	echo c++ objs  : $(CXXOBJS)
	echo c++ flags : $(CXXFLAGS)
	echo libs      : $(LIBS)
	echo so flags  : $(SOFLAGS)

	echo rootlibs  : $(ROOTLIBS)

