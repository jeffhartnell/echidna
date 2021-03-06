import rat
from ROOT import RAT
import math
import echidna.core.spectra as spectra

def _scint_weights(times, T):
    """This method applies to the scintillator backgrounds.
    It produces the list of weights relative to each time period. 
    The calculation of weights is based on radioactive decay formula.
 
    Args:
      times (*list* of *int*): Time periods 
      T (float): The Half-life of a studied background

    Returns:
      Weights (*list* of *float*)
    """
    weights = [0]
    for time in times:
        weights.append( math.exp(-time/T) )
    return (weights)

def _av_weights(times, T):
    """This method applies to the backgrounds due to AV leaching.
    It produces the list of weights relative to each time period. 
    The calculation of weights is based on radioactive decay formula.
 
    Args:
      times (*list* of *int*): Time periods 
      T (float): The Half-life of a studied background

    Returns:
      Weights (*list* of *float*)
    """
    weights = [0]
    for time in times:
        weights.append( 1.0 )
    return (weights)

def fill_reco_spectrum(filename, spectrumname, T):
    """This function fills in the ndarray of energies, radii, times 
    and weights. It takes the reconstructed energies and positions
    of the events from the root file. In order to keep the statistics, 
    the time dependence is performed via adding weights to every event
    depending on the time period. Both, studied time and Half-life must 
    be written in the same units.  
    
    Args:
      filename (str): A root file to study 
      spectrumname (str): A name of future ndarray 
      T (float): The Half-life of a studied background

      Returns:
        spectrum (:class:`echidna.core.spectra.Spectra`) 
    """
    print filename
    print spectrumname
    dsreader = RAT.DU.DSReader(filename)
    spectrum = spectra.Spectra(str(spectrumname), dsreader.GetEntryCount())

    times = [0]
    for time_step in range(0, spectrum._time_bins):
        time = time_step * spectrum._time_width + spectrum._time_low 
        times.append(time)

    if 'AV' in spectrumname:
        print "AV WEIGHTS ARE CURRENTLY UNAVAILABLE"
        weights = _av_weights(times, T)
    else:
        weights = _scint_weights(times, T)

    for ievent in range(0, dsreader.GetEntryCount()):
        ds = dsreader.GetEntry(ievent)
        for ievent in range(0, ds.GetEVCount()):
            ev = ds.GetEV(ievent)       
            if not ev.DefaultFitVertexExists() or not ev.GetDefaultFitVertex().ContainsEnergy() or not ev.GetDefaultFitVertex().ValidEnergy():
                continue                                       
            energy = ev.GetDefaultFitVertex().GetEnergy()
            position = ev.GetDefaultFitVertex().GetPosition().Mag()            
            for time,weight in zip(times, weights):
                try:
                    spectrum.fill(energy, position, time, weight)
                except ValueError:
                    pass

    return spectrum
    

def fill_mc_spectrum(filename, spectrumname, T):
    """This function fills in the ndarray of true energies, radii, times 
    and weights. It takes the true energies and positions of the events
    from the root file. In order to keep the statistics, the time
    dependence is performed via adding weights to every event depending 
    on the time period. Both, studied time and Half-life must  be
    written in the same units.  
    
    Args:
      filename (str): A root file to study 
      spectrumname (str): A name of future ndarray 
      T (float): The Half-life of a studied background

      Returns:
        spectrum (:class:`echidna.core.spectra.Spectra`) 
    """
    print filename
    print spectrumname
    dsreader = RAT.DU.DSReader(filename)
    spectrum = spectra.Spectra(str(spectrumname), dsreader.GetEntryCount())

    times = [0]
    for time_step in range(0, spectrum._time_bins):
        time = time_step * spectrum._time_width + spectrum._time_low 
        times.append(time)

    if 'AV' in spectrumname:
        print "AV WEIGHTS ARE CURRENTLY UNAVAILABLE"
        weights = _av_weights(times, T)
    else:
        weights = _scint_weights(times, T)

    for ievent in range(0, dsreader.GetEntryCount()):
        ds = dsreader.GetEntry(ievent)
        mc = ds.GetMC()
        if mc.GetMCParticleCount() > 0 :
            energy = mc.GetScintQuenchedEnergyDeposit()
            position = mc.GetMCParticle(0).GetPosition().Mag()
            for time,weight in zip(times, weights):
                try:
                    spectrum.fill(energy, position, time, weight)
                except ValueError:
                    pass

    return spectrum
    
