#ifndef __SAMPLE_H__
#define __SAMPLE_H__

class Sample
{
 public:
   Sample( const std::string& name );
   ~Sample();

   inline std::string& GetName() { return m_name; };

   void SetName( const std::string& name ) { m_name = name; };
   
   void SetColor( int color )         { m_color     = color;     };
   void SetFillStyle( int fillstyle ) { m_fillstyle = fillstyle; };
   void SetLineStyle( int linestyle ) { m_linestyle = linestyle; };

   int GetColor()     { return m_color; };
   int GetFillStyle() { return m_fillstyle; };
   int GetLineStyle() { return m_linestyle; };

 protected:
   std::string m_name;

   int m_color;
   int m_linestyle;
   int m_fillstyle;
};

#endif /** __SAMPLE_H__ */
