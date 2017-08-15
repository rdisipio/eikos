#ifndef __EikosUnfolder_H__
#define __EikosUnfolder_H__

#include <TObject.h>
#include <TH1D.h>

#include <BAT/BCModel.h>
#include <BAT/BCMTFSystematic.h>
#include <BAT/BCMTFSystematicVariation.h>
#include <BAT/BCMTFTemplate.h>

#include <map>

#include "Sample.h"

//enum StatusCode { kSuccess = 0, kWarning = 1, kError = 2 };

/////////////////////////////////

//namespace Eikos {

class EikosUnfolder : public BCModel, public TObject
{
 public:
    EikosUnfolder();
    ~EikosUnfolder();

    inline size_t GetNSamples()       { return m_samples.size(); };
    inline size_t GetNSystematics()   { return m_systematics.size(); };

    int GetSampleIndex( const std::string& name );
    int GetSystematicIndex( const std::string& name );

    int AddSample( const std::string& sample_name, double x_min, double x_max, int color = -1, int fillstyle = -1, int linestyle = -1 );
    int AddSystematic( const std::string& sname, double min, double max, const std::string & latexname = "", const std::string & unitstring = ""  );
    int AddSystematicVariation( const std::string& sample_name, const std::string& systematic_name, const TH1D * h_u, const TH1D * h_d, const TH1D * h_n = NULL );
    int AddSystematicVariation( const std::string& sample_name, const std::string& systematic_name, double k_u, double k_d, const TH1D * h_n = NULL );

    void SetDiffXsTemplate( const TH1 * h );
    void SetData( const TH1D * data );
    std::vector<double>& GetData() { return m_data; };

    double LogLikelihood( const std::vector<double>& parameters );
//    void MCMCUserIterationinterface();

    ClassDef( EikosUnfolder, 1 )

 //~~~~~~~~~~~~~~~~~~~~~

 protected:
    std::string m_name;
    int         m_nbins;
    std::vector<double> m_xedges;
    std::vector<double>	m_bw;

    std::vector< Sample * >          m_samples;
    std::map< const std::string, int >     m_samples_index;

    std::vector< BCMTFSystematic * >       m_systematics;
    std::map< const std::string, int >     m_systematics_index;

    std::vector<double> m_data;
};

//} // namespace Eikos

#endif /** __EikosUnfolder_H__ */
