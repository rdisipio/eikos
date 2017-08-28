#ifndef __SAMPLE_H__
#define __SAMPLE_H__

#include <string>
#include <map>

#include <TObject.h>
#include <TNamed.h>

enum SAMPLE_TYPE { kData = 0, kSignal = 1, kBackground = 2, kDataDriven = 3, kNSampleTypes = 4 };

class Sample : public TObject
{
 public:
 
   Sample( const std::string& name = "AnySample" );
   ~Sample();

   void SetName( const std::string& name )  { m_name      = name;      };
   void SetLatex( const std::string& tex )  { m_latex      = tex;      };
   void SetType( SAMPLE_TYPE type )   { m_type      = type;      };
   void SetIndex( int index )         { m_index     = index;     };

   void SetColor( int color )         { m_color     = color;     };
   void SetFillStyle( int fillstyle ) { m_fillstyle = fillstyle; };
   void SetLineStyle( int linestyle ) { m_linestyle = linestyle; };

   SAMPLE_TYPE GetType() { return m_type; };
   int GetIndex()       { return m_index; };
   int GetColor()       { return m_color; };
   int GetFillStyle()   { return m_fillstyle; };
   int GetLineStyle()   { return m_linestyle; };

   ClassDef( Sample, 1 )

 protected:
   std::string m_name;
   std::string m_latex;
   int m_index;
   int m_color;
   int m_linestyle;
   int m_fillstyle;
   SAMPLE_TYPE m_type;
};

typedef std::map< const std::string, Sample > SampleCollection_t;

#endif /** __SAMPLE_H__ */
