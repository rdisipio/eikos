#ifndef __SAMPLE_H__
#define __SAMPLE_H__

#include <string>

#include <TObject.h>

class Sample : public TObject
{
 public:
   Sample( const std::string& name );
   ~Sample();

   void SetColor( int color )         { m_color     = color;     };
   void SetFillStyle( int fillstyle ) { m_fillstyle = fillstyle; };
   void SetLineStyle( int linestyle ) { m_linestyle = linestyle; };

   int GetColor()     { return m_color; };
   int GetFillStyle() { return m_fillstyle; };
   int GetLineStyle() { return m_linestyle; };

   ClassDef( Sample, 1 )

 protected:
   int m_color;
   int m_linestyle;
   int m_fillstyle;
};

#endif /** __SAMPLE_H__ */
