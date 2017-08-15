#ifndef __SYSTEMATIC_H__
#define __SYSTEMATIC_H__

#include <TObject.h>

#include <string>

class Systematic : public TObject
{
 public:
   Systematic( const std::string& name = "" );
   ~Systematic();

   void SetParIndex( int i ) { m_par_index = i;   };
   inline int GetParIndex() { return m_par_index; };

   ClassDef( Systematic, 1 )

 protected:
   int         m_par_index;

};

#endif /** __SYSTEMATIC_H__ */
