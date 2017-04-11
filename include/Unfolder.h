#ifndef __UNFOLDER_H__
#define __UNFOLDER_H__

#include <BAT/BCModel.h>
#include <TH1D.h>

class Sample;
class Systematic;

/////////////////////////////////

class Unfolder : public BCModel
{
 public:
    Unfolder( const std::string& name = "Eikos unfolder" );
    ~Unfolder();

    int GetNSamples();
    int GetNSystematics();

    int GetSampleIndex( const std::string& name ) const;
    int GetSystematicIndex( const std::string& name ) const;

    int AddSample( const std::string& sample_name, double x_min, double x_max, int color = -1, int fillstyle = -1, int linestyle = -1 );
    int AddSystematic( const std::string& sample_name, const std::string& systematic_name, const TH1D * h_u, const TH1D * h_d, const TH1D * h_n = NULL );

    double LogLikelihood( const std::vector<double>& parameters );
    void MCMCUserIterationInterface();

 //~~~~~~~~~~~~~~~~~~~~~

 protected:
    std::string m_name;
    std::vector< Sample * >     m_samples;
    std::vector< Systematic * > m_systematics;

};

#endif /** __UNFOLDER_H__ */
