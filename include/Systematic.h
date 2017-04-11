#ifndef __SYSTEMATIC_H__
#define __SYSTEMATIC_H__

#include <string>

class Systematic
{
 public:
   Systematic();
   ~Systematic();

   const std::string& GetName() { return m_name; };

   void SetParIndex( int i ) { m_par_index = i;   };
   inline int GetParIndex() { return m_par_index; };

 protected:
   std::string m_name;
   int         m_par_index;

};

#endif /** __SYSTEMATIC_H__ */
