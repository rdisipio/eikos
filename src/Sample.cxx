#include "Sample.h"

ClassImp( Sample )

Sample::Sample( const std::string& name ) 
{
  m_name      = name;
  m_latex     = name;
  m_index     = -1;
  m_type      = SAMPLE_TYPE::kSignal;
  m_color     = -1;
  m_linestyle = -1;
  m_fillstyle = -1;
}

//~~~~~~~~~~~~~~~~~~~~~~~

Sample::~Sample()
{
}
