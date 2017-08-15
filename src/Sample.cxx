#include "Sample.h"

ClassImp( Sample )

Sample::Sample( const std::string& name ) 
{
  m_color     = -1;
  m_linestyle = -1;
  m_fillstyle = -1;
}

//~~~~~~~~~~~~~~~~~~~~~~~

Sample::~Sample()
{
}
