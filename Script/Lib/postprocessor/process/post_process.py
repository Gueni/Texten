
#?-------------------------------------------------------------------------------------------------------------------------------------------------------------
#?                                           ____   ___  ____ _____   ____  ____   ___   ____ _____ ____ ____
#?                                          |  _ \ / _ \/ ___|_   _| |  _ \|  _ \ / _ \ / ___| ____/ ___/ ___|
#?                                          | |_) | | | \___ \ | |   | |_) | |_) | | | | |   |  _| \___ \___ \
#?                                          |  __/| |_| |___) || |   |  __/|  _ <| |_| | |___| |___ ___) |__) |
#?                                          |_|    \___/|____/ |_|   |_|   |_| \_\\___/ \____|_____|____/____/
#?
#?-------------------------------------------------------------------------------------------------------------------------------------------------------------
import numpy            as np
import scipy            as sc
import multiprocessing

from scipy.interpolate                  import interp1d
from Lib.postprocessor.core.interfaces  import IProcess
from Lib.postprocessor.core.config      import ProcessBaseConfig, ProcessFFTConfig, ProcessDissipationsConfig, ProcessThermalStatsConfig, ProcessSensitivityConfig
from Lib.postprocessor.core.context     import ProcessContext
from Lib.postprocessor.process.registry import ProcessRegistry
#?-------------------------------------------------------------------------------------------------------------------------------------------------------------

class ProcessBase(IProcess):
    """
    Base process inherit IProcess interface. Contains common attributes

    *Attributes:
        self.result_name (str)          :   initialized with ProcessBaseConfig.process_name
        self.data_slice  (data_slice)   :   ProcessBaseConfig.data_slice
    """
    def __init__(self, config : ProcessBaseConfig):
        self.result_name    = config.process_name
        self.data_slice     = config.data_slice

@ProcessRegistry.register("AMAX")
class ProcessAbsoluteMax(ProcessBase):
    """
    _summary_

    *Attributes:
        ProcessBase (_type_)    : _description_
    """
    def execute(self, context: ProcessContext):
        """
        _summary_

        *Args:
            context (ProcessContext)    : _description_
        """
        data                                                                    = context.raw_data[self.data_slice]
        context.result_repository.data[self.result_name][context.thread_index]  = np.nanmax(np.absolute(data),axis=1)

@ProcessRegistry.register("NMEAN")
class ProcessAverage(ProcessBase):
    """
    _summary_

    *Attributes:
        ProcessBase (_type_)    : _description_
    """
    def execute(self, context: ProcessContext):
        """
        _summary_

        *Args:
            context (ProcessContext)    : _description_
        """
        data                                                                    = context.raw_data[self.data_slice]
        context.result_repository.data[self.result_name][context.thread_index]  = np.nanmean(data, axis=1)

@ProcessRegistry.register("NMAX")
class ProcessPeak(ProcessBase):
    """
    _summary_

    *Attributes:
        ProcessBase (_type_)    : _description_
    """
    def execute(self, context: ProcessContext):
        """
        _summary_

        *Args:
            context (ProcessContext)    : _description_
        """
        data                                                                    = context.raw_data[self.data_slice]
        context.result_repository.data[self.result_name][context.thread_index]  = np.nanmax(data, axis=1)

@ProcessRegistry.register("RMS")
class ProcessRMS(ProcessBase):
    """
    Calculate the Root Mean Square (RMS) of signal data using trapezoidal integration.

    Computes the square root of the integral of squared values over time (normalized by duration).
    Uses `numpy.trapz()` for numerical integration, which approximates the area under the curve using the trapezoidal rule.

    [numpy.trapz() docs]: https://numpy.org/doc/1.25/reference/generated/numpy.trapz.html

    *Attributes:
        context : ProcessContext

    Raises  :
        ZeroDivisionError   If the time range (`delta_T = t_vec[-1] - t_vec[0]`) is zero.
        ValueError          If input data is invalid (e.g., non-numeric).
    """
    def execute(self, context: ProcessContext):
        """
        _summary_

        *Args:
            context (ProcessContext)    : _description_
        """
        #* Calculate the time interval (delta_T) based on the first and last time values.
        t_vec   = context.raw_data[0]
        data    = context.raw_data[self.data_slice]
        delta_T = t_vec[-1] - t_vec[0]

#        context.result_repository.data[self.result_name][context.thread_index] = np.sqrt(np.trapz((np.array(data))**2, x=t_vec) / delta_T)
        context.result_repository.data[self.result_name][context.thread_index] = np.sqrt(np.trapz(np.square((np.array(data))), x=t_vec) / delta_T)

@ProcessRegistry.register("AVG")
class ProcessAVG(ProcessBase):
    """
    Calculate the Average (AVG) of signal data using trapezoidal integration.

    Computes the integral of values over time (normalized by duration).
    Uses `numpy.trapz()` for numerical integration, which approximates the area under the curve using the trapezoidal rule.

    [numpy.trapz() docs]: https://numpy.org/doc/1.25/reference/generated/numpy.trapz.html

    *Attributes:
        context : ProcessContext

    Raises:
        ZeroDivisionError   If the time range (`delta_T = t_vec[-1] - t_vec[0]`) is zero.
        ValueError          If input data is invalid (e.g., non-numeric).
    """
    def execute(self, context: ProcessContext):
        """
        _summary_

        *Args:
            context (ProcessContext)    : _description_
        """
        #* Calculate the time interval (delta_T) based on the first and last time values.
        t_vec   = context.raw_data[0]
        data    = context.raw_data[self.data_slice]
        delta_T = t_vec[-1] - t_vec[0]

        context.result_repository.data[self.result_name][context.thread_index] = np.trapz(np.array(data), x=t_vec) / delta_T

@ProcessRegistry.register("NMIN")
class ProcessNegativePeak(ProcessBase):
    """
    _summary_

    *Attributes:
        ProcessBase (_type_)    : _description_
    """
    def execute(self, context: ProcessContext):
        """
        _summary_

        *Args:
            context (ProcessContext): _description_
        """
        data                                                                    = context.raw_data[self.data_slice]
        context.result_repository.data[self.result_name][context.thread_index]  = np.nanmin(data, axis=1)

@ProcessRegistry.register("MAX")
class ProcessMax(ProcessBase):
    """
    _summary_

    *Attributes:
        ProcessBase (_type_)    : _description_
    """
    def execute(self, context: ProcessContext):
        """
        _summary_

        *Args:
            context (ProcessContext)    : _description_
        """
        data                                                                    = context.raw_data[self.data_slice]
        context.result_repository.data[self.result_name][context.thread_index]  = np.max(data, axis=1)

@ProcessRegistry.register("MIN")
class ProcessMin(ProcessBase):
    """
    _summary_

    *Attributes:
        ProcessBase (_type_)    : _description_
    """
    def execute(self, context: ProcessContext):
        """
        _summary_

        *Args:
            ProcessBase (_type_)    : _description_
        """
        data = context.raw_data[self.data_slice]
        context.result_repository.data[self.result_name][context.thread_index] = np.min(data, axis=1)

@ProcessRegistry.register("P2P")
class ProcessPtP(ProcessBase):
    """
    _summary_

    *Attributes:
        ProcessBase (_type_)    : _description_
    """
    def execute(self, context: ProcessContext):
        """
        _summary_

        *Args:
            ProcessBase (_type_)    : _description_
        """
        data = context.raw_data[self.data_slice]
        context.result_repository.data[self.result_name][context.thread_index] = np.ptp(data, axis=1)

@ProcessRegistry.register("FIRST")
class ProcessFirst(ProcessBase):
    """
    _summary_

    *Attributes:
        ProcessBase (_type_)    : _description_
    """
    def execute(self, context: ProcessContext):
        """
        _summary_

        *Args:
            ProcessBase (_type_)    : _description_
        """
        data = context.raw_data[self.data_slice]
        context.result_repository.data[self.result_name][context.thread_index] = np.take(data, 0, axis=1)

@ProcessRegistry.register("LAST")
class ProcessLast(ProcessBase):
    """
    _summary_

    *Attributes:
        ProcessBase (_type_)    : _description_
    """
    def execute(self, context: ProcessContext):
        data = context.raw_data[self.data_slice]
        context.result_repository.data[self.result_name][context.thread_index] = np.take(data, -1, axis=1)

@ProcessRegistry.register("FFT")
class ProcessFFT(ProcessBase):
    """
    Decompose signals into their frequency components using the Fast Fourier Transform (FFT) algorithm.
    The signal is in the form of a nested list.
    A non-uniformly sampled signal will be resampled using linear interpolation.
    The harmonic orders are referenced to the fundamental frequency of the signal, and only the desired harmonics will be returned.

    ?Methods:

        execute(context)            :
        resample(time, signal)      :   Resample a signal to have uniform time points
        safe_get(my_list, index)    :   Safely retrieve an element from a list by index
        pyFFT(signal, fs)           :   Decompose a discrete signal into its frequency components using the Fast Fourier Transform (FFT) algorithm.
                                        Amplitudes of the harmonics are normalized and returned along side the phase and constituent frequencies
    """

    def __init__(self, config: ProcessFFTConfig):
        """
        _summary_

        *Args:
            config (ProcessFFTConfig)   : _description_
        """
        super().__init__(config)
        self.hrmcs          = np.arange(0,config.hrmcs+1,1, dtype=int).tolist()
        self.to_file_ts     = config.to_file_ts
        self.fund_freq      = config.fund_freq

    def execute(self, context: ProcessContext):
        """
        _summary_

        *Args:
            context (ProcessContext)    : _description_
        """
        t_vec               = context.raw_data[0]
        data                = context.raw_data[self.data_slice]
        FFT_IDX1,FFT_IDX2   = context.thread_index*len(self.hrmcs), context.thread_index*len(self.hrmcs) + len(self.hrmcs)

        #* initialize empty matrix for the FFT results
        fft_mat             =   np.zeros((len(data),len(self.hrmcs)))

        #* resample signal if not uniformly sampled
        if self.to_file_ts == 0 :   time_vec,signal_mat  =  self.resample(t_vec,data)
        else                    :   time_vec,signal_mat  =  t_vec,data

        #* calculate sampling time of the signal
        dt                      =   time_vec[1]-time_vec[0]
        fs                      =   1/dt

        #* compute the FFT and identify harmonics of interest
        #* PyFFT now is called only once on the full (n_signals,n_samples)
        #* instead of looping over each signal alone
        Magnitude,_,Freq        =   self.pyFFT(signal_mat,fs)
        harmonics               =   np.array(self.hrmcs,dtype=int)*self.fund_freq
        idx                     =   np.where(np.in1d(Freq,harmonics))[0]

        #* reduce the full FFT array to the specified harmonics only
        #*
        Mag_array  = [self.safe_get(Magnitude.T,index) for index in idx if self.safe_get(Magnitude.T,index) is not None]
        Mag_array  = np.array(Mag_array).T
        n_pad      = len(self.hrmcs) - Mag_array.shape[1]
        fft_mat    = np.pad(Mag_array , ((0,0) , (0 , n_pad)) , 'constant')

        context.result_repository.data[self.result_name][FFT_IDX1 : FFT_IDX2 , :] = np.transpose(fft_mat)

    def resample(self, time, signal):
        """
        Resample a signal to have uniform time points.

        *Args:
            time    (numpy.ndarray)  :  Time values of the original signal.
            signal  (numpy.ndarray)  :  Signal values.

        !Returns:
            tuple                    :  Tuple containing the resampled time values and the corresponding resampled signal values.
        """

        #* Resample the signal onto a uniformly spaced time grid
        #* Interpolate the original signal values onto the new time grid
        #* Return the resampled time and signal
        new_t       = np.linspace(time.min(), time.max(), signal.shape[-1])
        new_signal  = interp1d(time, signal , axis=-1 , kind='linear', bounds_error=False,fill_value='extrapolate')(new_t)
        return new_t,new_signal

    def safe_get(self,my_list, index):
        """
        Safely retrieve an element from a list by index.

        *Args:
            my_list (list)  :   The list from which to retrieve the element.
            index   (int )  :   The index of the element to retrieve.

        !Returns:
            The element at the specified index, or None if the index is out of range.
        """

        #* Safely retrieve an element from a list by index
        #* Returns None if the index is out of range instead of raising an error
        try:
            return my_list[index]
        except IndexError:
            return None

    def pyFFT(self,signal,fs):
        """
        Decompose a discrete signal into its frequency components using the Fast Fourier Transform (FFT) algorithm.
        Amplitudes of the harmonics are normalized and returned along side the phase and constituent frequencies.

        This function uses SciPy's FFT implementation (scipy.fft) which provides efficient numerical computation
        of the discrete Fourier Transform. The function automatically utilizes all available CPU cores for parallel
        computation.

        Libraries used:
            - scipy.fft (https://docs.scipy.org/doc/scipy/reference/fft.html) : Fast Fourier Transform implementation

        *Args:
            signal  (numpy.ndarray)     :   Input time-domain signal (1D array)
            fs      (float)             :   Sampling frequency of the signal in Hz

        !Returns:
        tuple
                                        :   Contains three elements:
                                                - amplitude (numpy.ndarray) : Scaled FFT magnitude spectrum
                                                - phase     (numpy.ndarray) : Phase angles in degrees [0-360]
                                                - frequency (numpy.ndarray) : Frequency bins in Hz corresponding to the amplitude/phase values
        """

        #* calculate frequency and sample points for one-sided the fourier transform
        N                   =   signal.shape[-1]
        freq                =   np.arange(0,fs/2+fs/N,fs/N)
        freq                =   np.round(freq/1e4)*1e4
        freq                =   np.unique(freq)

        #* compute the FFT with parallel computation
        fft                 =   sc.fft.fft(x=signal,axis=-1,workers=multiprocessing.cpu_count())

        #* normalize the amplitude and calculate the phase
        amplitude           =   np.abs(fft)
        amplitude[...,0]    =   (1/N)*amplitude[...,0]
        amplitude[...,1:N]  =   (2/N)*amplitude[...,1:N]
        amplitude           =   amplitude[..., 0:int(N/2+N%2)+1]
        phase               =   np.angle(fft[...,0:int(N/2+N%2)+1],deg=True)

        return amplitude,phase,freq

@ProcessRegistry.register("DISSIPATIONS")
class ProcessDissipation(ProcessBase):
    """
    Compute total power dissipation:
        1. Calculate average dissipation from simulation results (dissip).
        2. Compute resistive dissipation as squared RMS currents multiplied by resistance values (res_dissip).
        3. Concatenate both into Dissipation_matrix, representing the overall power losses.
    """

    def __init__(self, config : ProcessDissipationsConfig):
        """
        _summary_

        *Args:
            config (ProcessDissipationsConfig): _description_
        """
        super().__init__(config)
        self.res_list       = config.res_list
        self.current_idx    = config.current_idx

    def execute(self, context: ProcessContext):
        """
        _summary_

        *Args:
            context (ProcessContext): _description_
        """
        dissip      = context.result_repository.data["AVG_Dissipations"][context.thread_index]
        res_dissip  = (np.square(context.result_repository.data["RMS_Currents"][context.thread_index][:self.current_idx]))*context.res_list

        context.result_repository.data[self.result_name][context.thread_index] = np.concatenate((dissip, res_dissip))

@ProcessRegistry.register("THERMALSTATS")
class ProcessThermalStats(ProcessBase):
    """
    Calculate thermal statistics including efficiency, total dissipation, and input power.

    """
    def __init__(self, config : ProcessThermalStatsConfig):
        """
        _summary_

        *Args:
            config (ProcessThermalStatsConfig): _description_
        """
        super().__init__(config)
        self.dcdc_d         = config.dcdc_d
        self.rail_idx       = config.rail_idx
        self.common_idx     = config.common_idx
        self.pout_idx       = config.pout_idx
        self.p_aux          = config.p_aux
        self.phase          = config.phase

    def execute(self, context: ProcessContext):
        """
        _summary_

        *Args:
            context (ProcessContext): _description_
        """
        #* Return empty array if results invalid, else return matrix
        if "Thermal_Stats" in context.result_repository.data:
            if context.result_repository.data["Thermal_Stats"].shape == (1, 1) or self.dcdc_d: #11 -> Temperatures
                context.result_repository.data[self.result_name][context.thread_index] = np.empty((1,))
                return

        #* Get total loss of each rail and common/shared parts
        P_rail      =   np.sum(context.result_repository.data["Dissipations"][context.thread_index][self.rail_idx:self.common_idx+1])
        P_common    =   np.sum(context.result_repository.data["Dissipations"][context.thread_index][self.common_idx+1:])

        #* Get average output power
        Pout        =   np.nanmean(context.result_repository.data["Elec_Stats"][context.thread_index][self.pout_idx])

        #* Calculate efficiency for each factorial value (phase scaling) including auxiliary power losses
        Eff         =   np.array([(((Pout / ( Pout + P_rail + (factorial * P_common))*100.0) if ( Pout + P_rail + (factorial * P_common)) != 0 else 0.0)) for factorial in list(range(1, self.phase + 1))])
        Eff_Aux     =   np.array([(((Pout / ( Pout + (P_rail + (factorial * P_common))+context.p_aux)*100.0) if ( Pout + P_rail + (factorial * P_common)) != 0 else 0.0)) for factorial in list(range(1, self.phase + 1))])

        #* Calculate total dissipation and input power as sum of Pout and losses
        Ptot        =   np.array([(P_rail*factorial + P_common*np.square(factorial)) for factorial in list(range(1, self.phase + 1))])
        Pin         =   np.array([((P_rail + Pout)*factorial + P_common*np.square(factorial)) for factorial in list(range(1, self.phase + 1))])

        #* Concatenate all results into final thermal matrix
        context.result_repository.data[self.result_name][context.thread_index] = np.concatenate((Ptot, Eff, Eff_Aux, Pin))

@ProcessRegistry.register("SENSITIVITY")
class ProcessSensitivity(ProcessBase):
    """
    Calculate Sensitivity on parent map.

    """

    def __init__(self, config : ProcessSensitivityConfig):
        """
        _summary_

        *Args:
            config (ProcessSensitivityConfig): _description_
        """
        super().__init__(config)
        self.perturbation               = config.perturbation
        self.fft_cft                    = config.fft_cfg
        self.post_fix                   = config.post_fix
        self.parent_process_res_name    = ""
        self.Y0                         = []
        self.fallback                   = np.nan
        self.slice                      = 0

    def execute(self, context: ProcessContext):
        """
        _summary_

        *Args:
            context (ProcessContext): _description_
        """
        idx         = context.thread_index
        if "FFT" in self.parent_process_res_name:
            hrmcs   = self.fft_cft.hrmcs+1
        else:
            hrmcs   = 1
        self.slice  = slice(idx*hrmcs, idx*hrmcs + hrmcs)

        if idx == 0:
            self.parent_process_res_name    = self.result_name.replace(self.post_fix, "")
            self.Y0                         = context.result_repository.data[self.parent_process_res_name][self.slice]

        else:
            dY      = context.result_repository.data[self.parent_process_res_name][self.slice] - self.Y0

            with np.errstate(divide='ignore',invalid='ignore'):
                S       = np.multiply(np.divide(np.divide(dY,self.Y0), self.perturbation), 100)
                S       = np.nan_to_num(S, nan=self.fallback, posinf=self.fallback, neginf=self.fallback)
            context.result_repository.data[self.result_name][slice((idx-1)*hrmcs, (idx-1)*hrmcs + hrmcs)] = S
#?-------------------------------------------------------------------------------------------------------------------------------------------------------------
