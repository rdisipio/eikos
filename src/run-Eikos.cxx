#include <BAT/BCLog.h>
#include <BAT/BCAux.h>

#include "Unfolder.h"

int main( int argc, char * argv[] )
{
  // set nicer style for drawing than the ROOT default
   BCAux::SetStyle();

   // open log file
   BCLog::OpenLog("log.txt");
   BCLog::SetLogLevel(BCLog::detail);

   Unfolder * unfolder = new Unfolder();

   unfolder->MarginalizeAll();
   unfolder->FindMode( unfolder->GetBestFitParameters() );
   // unfolder->PrintAllMarginalized("eikos_plots.ps");
 
   unfolder->PrintParameterPlot("eikos_parameters.eps");
   unfolder->PrintCorrelationPlot("eikos_correlation.eps");
   unfolder->PrintCorrelationMatrix("eikos_correlationMatrix.eps");
   unfolder->PrintKnowledgeUpdatePlots("eikos_update.ps");
//   unfolder->PrintResults("eikos.txt");

   delete unfolder;

   return 0;
}

