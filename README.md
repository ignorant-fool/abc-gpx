# abc-gpx
A pseudo-inversion process for profile gravity data based on approximate bayesian computation methods.


## Workflow
1. Use ABC methods to perform a Bayesian pseudo-inversion of profile gravity data.
2. We will set priors on all body parameters
    - depth to top of body
    - depth extent of the body
    - the density contrast of the body
    - the dip of the body
    - thickness of the body
    - +- the X/Y location of the body (tbd.)
3. ABC workflow is roughly: 
    - generate samples for each parameter, fwd model the response
    - calculate the misfit from some reference body we're aiming for
    - throwaway every fwd model that isn't within +- eps of the reference body
    - do inference and uncertainty quantification on the reminaing fwd models and their parameters


## Notes:
- This project utilizes Poetry for keeping package version control.
- This project utilizes SimPEG for all it's geophysical modelling.


## References:
- Cockett, Rowan, Seogi Kang, Lindsey J. Heagy, Adam Pidlisecky, and Douglas W. Oldenburg. "SimPEG: An Open Source Framework for Simulation and Gradient Based Parameter Estimation in Geophysical Applications" Computers & Geosciences, September 2015. doi:10.1016/j.cageo.2015.09.015.
- Sunnåker M, Busetto AG, Numminen E, Corander J, Foll M, Dessimoz C. Approximate Bayesian computation. PLoS Comput Biol. 2013;9(1):e1002803. doi: 10.1371/journal.pcbi.1002803. Epub 2013 Jan 10. PMID: 23341757; PMCID: PMC3547661.