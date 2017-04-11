#include <BAT/BCLog.h>
#include <BAT/BCAux.h>
#include <BAT/BCSummaryTool.h>

#include "Unfolder.h"

int main( int argc, char * argv[] )
{
  // set nicer style for drawing than the ROOT default
   BCAux::SetStyle();

   // open log file
   BCLog::OpenLog("log.txt");
   BCLog::SetLogLevel(BCLog::detail);

   Unfolder * unfolder = new Unfolder();
   BCSummaryTool * summary = new BCSummaryTool( unfolder );

   unfolder->MarginalizeAll();
   unfolder->FindMode( unfolder->GetBestFitParameters() );
   // unfolder->PrintAllMarginalized("eikos_plots.ps");
 
   summary->PrintParameterPlot("eikos_parameters.eps");
   summary->PrintCorrelationPlot("eikos_correlation.eps");
   summary->PrintCorrelationMatrix("eikos_correlationMatrix.eps");
   summary->PrintKnowledgeUpdatePlots("eikos_update.ps");
   unfolder->PrintResults("eikos.txt");

   delete unfolder;
   delete summary;

   return 0;
}

