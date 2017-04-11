#include "Unfolder.h"

Unfolder::Unfolder( const std::string& name )
{
  m_name = name;
}

//~~~~~~~~~~~~~~~~~~~~~~~~~


Unfolder::~Unfolder()
{
}


////////////////////////////

void Unfolder::MCMCUserIterationInterface()
{
}

////////////////////////////

double Unfolder::LogLikelihood(std::vector<double, std::allocator<double> > const&)
{
   return 0;
}
