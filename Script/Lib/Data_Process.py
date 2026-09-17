
#?-------------------------------------------------------------------------------------------------------------------------------------------------------------
#?                                ____    _  _____  _      ____  ____   ___   ____ _____ ____ ____ ___ _   _  ____
#?                               |  _ \  / \|_   _|/ \    |  _ \|  _ \ / _ \ / ___| ____/ ___/ ___|_ _| \ | |/ ___|
#?                               | | | |/ _ \ | | / _ \   | |_) | |_) | | | | |   |  _| \___ \___ \| ||  \| | |  _
#?                               | |_| / ___ \| |/ ___ \  |  __/|  _ <| |_| | |___| |___ ___) |__) | || |\  | |_| |
#?                               |____/_/   \_\_/_/   \_\ |_|   |_| \_\\___/ \____|_____|____/____/___|_| \_|\____|
#?
#?-------------------------------------------------------------------------------------------------------------------------------------------------------------
import assets.Dependencies as dp
#?-------------------------------------------------------------------------------------------------------------------------------------------------------------
class Processing:
    def __init__(self):
        """
        Initialize the DataProcess class.
        """

        pass

    def norm_results_csv(self,results):
        """
        Normalize a list of lists by padding shorter sublists with NaN values to match the longest sublist.

        *Args   :
            results (list)  : A list containing multiple lists of varying lengths.

        !Returns:
            list            : A list of lists padded with NaN values to match the longest sublist length.
        """
        # Transpose the sublists into columns filling missing entries with nan zip_longest(*results,fillvalue=dp.np.nan)
        # Transpose back to rows to get original sublists padded to max length
        # Convert each tuple back to a list
        return list(map(list,zip(*dp.itertools.zip_longest(*results,fillvalue=dp.np.nan))))

    def extractArrays(self,fileName):
        """
        Reads a CSV file that contains comma-separated numerical data and returns the individual columns
        of the CSV file as a nested list.

        *Args   :
            fileName (str)      :   The name of the CSV file to be read, including the file extension. This file
                                    should be located in the current working directory.

        !Returns:
            list                :   A nested list containing the individual columns of the CSV file. The outer list is a
                                    list of columns, where each element of the list is a list of values in that column.

        !Raises:
            FileNotFoundError   : If the specified CSV file cannot be found in the current working directory.
            ValueError          : If the specified CSV file is empty or does not contain any numerical data.

        ?Example:
            If the CSV file contains the following data:
                                                            1,2,3
                                                            4,5,6
                                                            7,8,9

            Calling extractArrays('data.csv') will return:  [[1.0, 4.0, 7.0], [2.0, 5.0, 8.0], [3.0, 6.0, 9.0]]
        """

        # Set the base path to the current working directory.
        # Load the data from the csv file
        path                =   dp.os.getcwd() + '/'
        data                =   dp.np.loadtxt(path + fileName + '.csv' , delimiter=',')

        # Ensure 2D shape even if the csv has only one row
        if data.ndim == 1   :   data = data.reshape(1,-1)

        return data.T.tolist()

    def get_index(self,Data: list, Point: float, Index: int) -> int:
        """
        Returns the index of the given target point if found in the data list.

        *Args   :
        - Data  (list)      : A nested list of numerical data.
        - Point (float)     : The target point to search for in the data.
        - Index (int)       : The index of the sub-list in Data to search.

        !Returns:
        - int               : The index of the closest value to the target point in the specified sub-list of Data.

        !Raises :
        - TypeError         : If Data is not a list or if Point is not a float.
        - IndexError        : If the specified index is out of range for the Data list.
        - ValueError        : If the specified sub-list is empty.

        ?Example:
        data = [[1.1, 2.2, 3.3], [-4.4, -5.5, -6.6], [7.7, 8.8, 9.9]]
        get_index(data, 2.0, 0)
        1
        get_index(data, -5.0, 1)
        1
        get_index(data, 8.8, 2)
        1
        """

        # Convert the specified column (Data[Index]) to a NumPy array.
        # Find the index of the element closest to the given Point, ignoring NaNs.
        # Return the index of the closest value.
        array   =   dp.np.asarray(Data[Index])
        idx     =   dp.np.nanargmin(dp.np.abs(array - Point))

        return idx

    def analytical_magnetic_loss(self, nestedresults, FFT_current, l):
        """
        Calculate magnetic losses analytically for transformer core losses, primary copper losses,
        secondary copper losses, choke core and copper losses.

        *Args   :
            nestedresults   (dict)            : Nested results containing flux linkage and voltages for transformers and chokes.
            FFT_current     (numpy.ndarray)   : FFT current values.
            l               (int)             : Index for time step or frequency bin.

        !Returns:
            tuple                             : Tuple containing core losses, primary copper losses, secondary copper losses,
                                                choke core and copper losses.
        """

        # Initialize empty lists to store transformer and choke losses
        # Initialize empty lists to store interpolated resistances for primary, secondary, and inductor windings
        core_loss, pri_copper_loss, sec_copper_loss, choke_core_loss, choke_copper_loss = [], [], [], [], []
        R_pri, R_sec, R_ind                                                             = [],[],[]

        # ----- Core losses calculation -----
        # Extract transformer flux from nested results.
        # Calculate peak flux (half of peak-to-peak) rounded to 12 decimals.
        # Parameters for core loss calculation using IGSE method.
        # Compute core loss and append to the list.
        flux_link     = nestedresults[dp.pmapping['Transformer Flux']]
        point_flux    = dp.np.round((dp.np.max(flux_link)-dp.np.min(flux_link))/2 , decimals=12 )
        Bp            = point_flux/(dp.mdlVars['DCDC_Rail1']['Trafo']['Core']['Ae'] * dp.mdlVars['DCDC_Rail1']['Trafo']['Np'])
        d             = [nestedresults[dp.pmapping['PWM Modulator Primary Modulator Duty Cycle'] + dp.Y_list[3] + 1]]
        d             = self.rms_avg('AVG', d, nestedresults[0])
        # Vc            = dp.mdlVars['DCDC_Rail1']['Trafo']['Core']['Vc']
        SP_tfo        = dp.mdlVars['DCDC_Rail1']['Trafo']['Core']['SP_tfo']
        # d             = 0.532
        Bp            = 0.10776
        Vc            = 468e-6 * 72.5e-3
        core_loss.append(self.IGSE('trap', SP_tfo, d, dp.F_Fund, Bp, Vc))

        #? ----- Primary and secondary copper losses -----
        # Extract harmonic frequencies and winding resistances & scaling factors.
        f_tfo     = [0] + dp.mdlVars['DCDC_Rail1']['Trafo']['Winding']['Harmonics']
        pri_Rvec  = dp.mdlVars['DCDC_Rail1']['Trafo']['Winding']['Rpri']['Rvec']
        pri_Rscale = dp.mdlVars['DCDC_Rail1']['Trafo']['Winding']['Rpri']['Rscale']
        sec_Rvec  = dp.mdlVars['DCDC_Rail1']['Trafo']['Winding']['Rsec']['Rvec']
        sec_Rscale = dp.mdlVars['DCDC_Rail1']['Trafo']['Winding']['Rsec']['Rscale']

        # Extract DC or fundamental resistances for primary and secondary.
        for i in range(len(pri_Rvec)):
            R_pri.append(pri_Rvec[i][-1])
            R_sec.append(sec_Rvec[i][-1])

        # Compute optimized AC resistances using rac_lac_values method.
        res_optimize_pri = self.rac_lac_values('min', dp.mdlVars['DCDC_Rail1']['Trafo']['Lm'], dp.np.array(f_tfo) * 1e5, dp.np.array(R_pri))
        res_optimize_sec = self.rac_lac_values('min', dp.mdlVars['DCDC_Rail1']['Trafo']['Lm'] / 100, dp.np.array(f_tfo) * 1e5, dp.np.array(R_sec))  # Adjust Lm for secondary

        # Compute copper losses by summing I^2 * R for each harmonic, scaled appropriately.
        pri_copper_loss.append(dp.np.sum(res_optimize_pri['Rac_calculated'] * pri_Rscale * 0.5 * dp.np.square(FFT_current[l*len(dp.harmonics):(l+1)*len(dp.harmonics), dp.pmapping['Transformer Primary Current']-1][f_tfo[1:]])))
        sec_copper_loss.append(dp.np.sum(res_optimize_sec['Rac_calculated'] * sec_Rscale * 0.5 * dp.np.square(FFT_current[l*len(dp.harmonics):(l+1)*len(dp.harmonics), dp.pmapping['Transformer Secondary Current']-1][f_tfo[1:]])))

        # Compute optimized Rac and Lac using Dowell's equation
        # Foil winding for primary: two parallel foils with five turns, repeated twice
        f = dp.np.logspace(3,7,2000)
        Zw_pri, Rdc_pri, Ldc_pri, Fr_pri, Fl_pri, Q_pri = self.analytical_impedance(f,25,70e-6*170,2*5,47e-3,1,110e-3,1,2)
        res_optimize_pri = self.Dowell_Rac_Lac(f,Zw_pri,Rdc_pri,Ldc_pri,Fr_pri,Fl_pri,Q_pri,dp.mdlVars['DCDC_Rail1']['Trafo']['Lm'])

        # Foil winding for secondary: Three parallel foils with one turn
        Zw_sec, Rdc_sec, Ldc_sec, Fr_sec, Fl_sec, Q_sec = self.analytical_impedance(f,25,0.6e-3,1,47e-3,1,110e-3,1,3)
        res_optimize_sec = self.Dowell_Rac_Lac(f,Zw_sec,Rdc_sec,Ldc_sec,Fr_sec,Fl_sec,Q_sec,dp.mdlVars['DCDC_Rail1']['Trafo']['Lm'])

        #? ----- Choke core losses -----
        # Peak AC component of choke current
        # Calculate peak flux density in the choke core
        # Compute core loss using trapezoidal integration (IGSE method)
        Iind    = nestedresults[dp.pmapping['DC Choke Current']]
        Iindp   = (dp.np.max(Iind) - dp.np.min(Iind)) / 2
        Bpl     = (dp.mdlVars['DCDC_Rail1']['Lf']['L'] * Iindp) / (dp.mdlVars['DCDC_Rail1']['Lf']['N'] * dp.mdlVars['DCDC_Rail1']['Lf']['Core']['Ae'])
        Sp_choke = dp.mdlVars['DCDC_Rail1']['Lf']['Core']['SP_l']
        Vcl      = dp.mdlVars['DCDC_Rail1']['Lf']['Core']['Vc']
        choke_core_loss.append(self.IGSE('tri', Sp_choke, d, 2 * dp.F_Fund, Bpl, Vcl))

        #? ----- Choke copper losses -----
        # Extract FFT of choke current for the current iteration
        # Winding resistance vector and scaling
        # Collect last element of each Rvec for use in calculation
        # Compute copper loss: sum of (R_ac * scale * I²/2) over all harmonics
        choke_current_fft = FFT_current[l*len(dp.harmonics):l*len(dp.harmonics)+len(dp.harmonics),dp.pmapping['DC Choke Current']-1]
        ind_Rvec          = dp.mdlVars['DCDC_Rail1']['Lf']['Winding']['Rwind']['Rvec']
        ind_Rscale        = dp.mdlVars['DCDC_Rail1']['Lf']['Winding']['Rwind']['Rscale']
        f_ind             = dp.mdlVars['DCDC_Rail1']['Lf']['Winding']['Harmonics']
        for i in range(len(ind_Rvec)):R_ind.append(ind_Rvec[i][-1])
        choke_copper_loss.append(dp.np.sum(dp.np.array(R_ind[1:]) * ind_Rscale * (1/2) * dp.np.square(choke_current_fft[f_ind[1:]])) + (dp.np.array(R_ind[0]) * ind_Rscale * dp.np.square(choke_current_fft[0])))

        # Return arrays of calculated losses for transformers and chokes.
        return dp.np.array(core_loss), dp.np.array(pri_copper_loss), dp.np.array(sec_copper_loss), dp.np.array(choke_core_loss), dp.np.array(choke_copper_loss)

    @dp.deprecated(reason="Candidate for remove?")
    def drop_Extra_Cols(self, filename, idx_start, idx_end):
        """
        Drop specified columns range from a CSV file.

        *Args   :
            filename     (str)     : Path to the CSV file.
            dissip_start (int)     : Starting index of columns to be dropped.
            dissip_end   (int)     : Ending index (exclusive) of columns to be dropped.

        """

        # Read the CSV file into a DataFrame
        # Drop the columns between idx_start and idx_end
        # Overwrite the original CSV with the updated DataFrame
        df                  = dp.pd.read_csv(filename, header=None)
        df.drop(df.columns[idx_start:idx_end], axis=1, inplace=True)
        df.to_csv(filename, index=False, header=None)

    def LuT_2D(self, x, y, z):
        """
        Create a 2D Look-Up Table (LuT) using linear interpolation.

        *Args   :
            x (list)                : List of values for the first dimension.
            y (list)                : List of values for the second dimension.
            z (numpy.ndarray)       : 2D array of values for the LuT.

        !Returns:
            RegularGridInterpolator : Interpolation function for the LuT.
        """

        # Create a 2D linear interpolator over the grid defined by (x, y) with values z
        # Return the interpolation function for later evaluation
        interp_func     = dp.sc.interpolate.RegularGridInterpolator((x, y), z, method='linear', bounds_error=False, fill_value=None)
        return interp_func

    def LuT_3D(self, x, y, z, data):
        """
        Create a 3D Look-Up Table (LuT) using linear interpolation.

        *Args   :
            x (list)                : List of values for the first dimension.
            y (list)                : List of values for the second dimension.
            z (list)                : List of values for the third dimension.
            data (numpy.ndarray)    : 3D array of values for the LuT.

        !Returns:
            RegularGridInterpolator: Interpolation function for the LuT.
        """

        # Create a 3D linear interpolator over the grid defined by (x, y, z) with values in 'data'
        # Return the interpolation function for later evaluation
        interp_func     = dp.sc.interpolate.RegularGridInterpolator((x,y,z), data, method='linear', bounds_error=False, fill_value=None)
        return interp_func

    def IIR_Filter(self, Time, Signal, Cutoff, Order=2, BType='low', FType='butter'):
        """
        Design and apply an Infinite Impulse Response (IIR) filter to a signal with zero-phase distortion.

        This function uses SciPy's signal processing module (scipy.signal) to design and apply Butterworth, Chebyshev,
        or other IIR filters. Zero-phase filtering is achieved using filtfilt, which processes the signal forward
        and backward to eliminate phase delay.

        Libraries Used:
        - scipy.signal.iirfilter  (https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.iirfilter.html): Designs an IIR filter of specified type (Butterworth, Chebyshev, etc.) and order.
        - scipy.signal.filtfilt   (https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.filtfilt.html) : Applies zero-phase filtering by processing the signal forward and backward.

        *Args   :
            Time      (numpy.ndarray)       : Time vector corresponding to the signal (in seconds). Used to calculate the sampling frequency.
            Signal    (numpy.ndarray)       : Input signal to be filtered (1D array).
            Cutoff    (float or list)       : Cutoff frequency (Hz) for low/high-pass filters, or [low, high] frequencies for band-pass/stop filters.
            Order     (int, optional)       : Order of the filter. Higher orders provide steeper roll-off but may introduce numerical instability. Default: 2.
            BType     (str, optional)       : Filter type: 'low' (low-pass), 'high' (high-pass), 'band' (band-pass), or 'bandstop'. Default: 'low'.
            FType     (str, optional)       : Filter design type: 'butter' (Butterworth), 'cheby1' (Chebyshev Type I), 'cheby2' (Chebyshev Type II), or 'ellip' (elliptic). Default: 'butter'.

        !Returns:
            numpy.ndarray                   : The filtered signal with zero-phase distortion.
        """

        # Calculate the time step and sampling frequency for signal processing. The sampling frequency is determined
        # as the inverse of the time step, which establishes the Nyquist frequency (half the sampling rate) as the
        # maximum frequency that can be accurately represented. To prevent aliasing and ensure filter stability,
        # the cutoff frequency must not exceed this Nyquist limit.
        dt                  =   Time[1] - Time[0]
        Fs                  =   1.0/dt
        Fn                  =   min(Fs/2-1, Cutoff)

        # An IIR filter is then designed with the specified cutoff frequency, and finally, zero-phase filtering
        # is applied to eliminate phase distortion in the filtered signal.
        b,a                 =   dp.sc.signal.iirfilter(Order, Wn=Fn, fs=Fs, btype=BType, ftype=FType)
        Signal_Filtered     =   dp.sc.signal.filtfilt(b, a, Signal)

        return Signal_Filtered

    def findMissingResults(self,path,itr,threads_vector,Threads):
        """
        In case of a crash find and reconstruct the missing results using the last iteration and thread and path.

        Parameters     :
                                path     :               string
                                                         path to results folder.
                                itr      :               int
                                                         Last iteration number.
                                Threads  :               int
                                                         Last Thread count.
        Returns        :        Missing  :               List
                                                         List of missing data.
        """

        # Initialize lists to store filenames and extracted iteration numbers
        file_list   = []
        Iters       = []

        # Determine expected iteration range based on hierarchical setting
        if dp.JSON['hierarchical']:
            iteration_range = list(range(1, sum(threads_vector[0:itr+1]) + 1))
        else:
            iteration_range = list(range(1, Threads * (itr + 1) + 1))

        # Gather all result filenames in the path
        for filename in dp.os.scandir(path):
            file_list.append(str(filename.path.replace("\\", "/")))

        # Extract iteration numbers from filenames
        for i in range(len(file_list)):
            x = file_list[i].split("s_")[-1]
            x = x.split(".")[0]
            x = x.split("_")[-1]
            Iters.append(int(x))
            Iters.sort()

        # Identify missing iterations by comparing with expected range
        Set = set(Iters)
        Missing = [x for x in iteration_range if x not in Set]

        return Missing

    def last_filled_X(self):
        """
        Determine the length of the last non-zero input list from JSON data.

        Returns:    int: Length of the last non-zero input list, or 0 if all are [0].
        """

        # Construct a list of X input lists from the JSON file
        lists = [dp.JSON[f'X{i}'] for i in range(1, 11)]

        # Iterate from the last list to the first
        # Convert string representation to actual list
        # and return the length of the first non-zero list encountered
        for lst in reversed(lists):
            lst = dp.ast.literal_eval(lst)
            if lst != [0]:
                return len(lst)

        # Return 0 if all lists are [0]
        return 0

    def deratingDCDC(self,Params,Tw,Vout,Pout,Derate=True):
        """
        Applies power and current derating functions on the DCDC output power and current in buck direction using water temperature
        and output voltage as the derating conditions. Between the boundary conditions, the power and currents are calculated through
        the standard linear function.

        The operation of the DCDC is divided into 3 regions: continuous duration, 10-sec duration and 2-sec duration. In each time duration,
        a maximum current and/or power are allowed based on the boundary conditions and the linear derating.

        Args:
            Params (dictionary): contains the boundary conditions for the DCDC
            Tw (float): water temperature of application
            Vout (float): output voltage of application
            Pout (float): output power of application
            Derate (bool, optional): a flag to determine if the derated output power will be applied. Defaults to True.

        Returns:
            (tuple): containing max allowed power and max allowed continuous, 10s and 2s currents.
        """

        # Nominal and max/min values for voltage, water temperature, and power/current ratings forming the boundary coniditons
        Vmin           ,Vnom            ,Vmax           =   Params['Vmin']          , Params['Vnom']        , Params['Vmax']
        Twater_nom     ,Twater_max                      =   Params['Twater_nom']    , Params['Twater_max']
        Pmax_2s_nom     ,Pmax_2s_max                    =   Params['Pmax_2s_nom']   , Params['Pmax_2s_max']
        Pmax_10s_nom    ,Pmax_10s_max                   =   Params['Pmax_10s_nom']  , Params['Pmax_10s_max']
        Pcont_nom       ,Pcont_max                      =   Params['Pcont_nom']     , Params['Pcont_max']
        Imax_2s_nom     ,Imax_2s_max                    =   Pmax_2s_nom/Vnom        , Pmax_2s_max/Vnom
        Imax_10s_nom    ,Imax_10s_max                   =   Pmax_10s_nom/Vnom       , Pmax_10s_max/Vnom
        Icont_nom       ,Icont_max                      =   Pcont_nom/Vnom          , Pcont_max/Vnom

        # Linear derating based on water temperature for output power
        Pcont_Tw                                                                       =    self.linearDerating(Twater_nom,Twater_max,
                                                                                                                Pcont_nom,Pcont_max,
                                                                                                                Pcont_max,Pcont_nom,
                                                                                                                Tw)
        P10s_Tw                                                                        =    self.linearDerating(Twater_nom,Twater_max,
                                                                                                                Pmax_10s_nom,Pmax_10s_max,
                                                                                                                Pmax_10s_max,Pmax_10s_nom,
                                                                                                                Tw)
        P2s_Tw                                                                         =    self.linearDerating(Twater_nom,Twater_max,
                                                                                                                Pmax_2s_nom,Pmax_2s_max,
                                                                                                                Pmax_2s_max,Pmax_2s_nom,
                                                                                                                Tw)

        # Linear derating based on water temperature for output current
        Icont_Tw                                                                       =    self.linearDerating(Twater_nom,Twater_max,
                                                                                                                Icont_nom,Icont_max,
                                                                                                                Icont_max,Icont_nom,
                                                                                                                Tw)
        I10s_Tw                                                                        =    self.linearDerating(Twater_nom,Twater_max,
                                                                                                                Imax_10s_nom,Imax_10s_max,
                                                                                                                Imax_10s_max,Imax_10s_nom,
                                                                                                                Tw)
        I2s_Tw                                                                         =    self.linearDerating(Twater_nom,Twater_max,
                                                                                                                Imax_2s_nom,Imax_2s_max,
                                                                                                                Imax_2s_max,Imax_2s_nom,
                                                                                                                Tw)

        # Linear derating based on output voltage for output current
        I2s_Vo                                                                         =    self.linearDerating(Vnom,Vmax,
                                                                                                                P2s_Tw/Vnom,P2s_Tw/Vmax,
                                                                                                                P2s_Tw/Vmax,P2s_Tw/Vnom,
                                                                                                                Vout)
        I10s_Vo                                                                        =    self.linearDerating(Vnom,Vmax,
                                                                                                                P10s_Tw/Vnom,P10s_Tw/Vmax,
                                                                                                                P10s_Tw/Vmax,P10s_Tw/Vnom,
                                                                                                                Vout)
        Icont_Vo                                                                       =    self.linearDerating(Vnom,Vmax,
                                                                                                                Pcont_Tw/Vnom,Pcont_Tw/Vmax,
                                                                                                                Pcont_Tw/Vmax,Pcont_Tw/Vnom,
                                                                                                                Vout)

        # Linear derating based on output voltage for output power
        Pmax_Vo                                                                        =    self.linearDerating(Vmin,Vnom,
                                                                                                                Vmin*P2s_Tw/Vnom,Vnom*P2s_Tw/Vnom,
                                                                                                                Vmin*P2s_Tw/Vnom,Vnom*P2s_Tw/Vnom,
                                                                                                                Vout)

        # Take the minimum of allowed output currents forming the current limits
        I2s                                                                            =    round(min(I2s_Tw,I2s_Vo),4)
        I10s                                                                           =    round(min(I10s_Tw,I10s_Vo),4)
        Icont                                                                          =    round(min(Icont_Tw,Icont_Vo),4)

        # Derated output power will only be applied if flag is set to true
        Pmax                                                                           =    Pout
        if (Derate):
            Pmax                                                                       =    min(Pout,P2s_Tw,Pmax_Vo)
        Iout                                                                           =    round(Pmax/Vout,4)

        # Return max power and current limits
        return Pmax,I2s,I10s,Icont,Iout

    def hierarchicalSims(self,Map):
        """
        Determine the hierarchical simulation indices based on a provided map. The hierarchical structure of the DCDC is based load duration.
        This is divided into 3 durations, a continuous duration, 10s and 2s. This function is hard-coded and requires a certain order of sweep
        parmeters map. This map along with the DCDC boundary conditions must be provided by the user.

        Args:
            Map (list): list of sweep parameter sets.

        Returns:
            list: Flattened list of thread counts for continuous, 10-sec, and 2-sec simulations.
        """

        # Initialize lists to store thread counts and iteration indices
        thread_vector                       = []
        iter_continous, iter_10s, iter_2s   = [], [], []

        # Loop through each simulation parameter set and apply the derating
        for i in range(len(Map)):
            _,_,I10s,Icont,Iout = self.deratingDCDC(dp.mdlVars['Common']['Thermal']['Derating'],Map[i][1],Map[i][3],Map[i][4])

            # Assign iteration to appropriate category
            if (Iout > I10s):
                iter_2s.append(iter_10s_1)

            elif (Iout <= I10s and Iout > Icont):
                iter_10s.append(iter_continous)
                iter_10s_1 = i

            else:
                iter_continous = i

        # Remove duplicates from iteration lists
        iter_10s    =   list(dp.np.unique(dp.np.array(iter_10s)))
        iter_2s     =   list(dp.np.unique(dp.np.array(iter_2s)))

        # Calculate thread counts for continuous, 10s, and 2s simulations
        for i in range(len(iter_10s)):
            thread_1 = iter_10s[i]+1-self.last_filled_X()*i
            thread_2 = iter_2s[i]-iter_10s[i]
            thread_3 = self.last_filled_X()-(thread_1+thread_2)

            thread_vector.append(thread_1)
            thread_vector.append(thread_2)
            thread_vector.append(thread_3)

        # Return the flattened list of thread counts
        return thread_vector

    def linearDerating(self,X1,X2,Y1,Y2,Ymin,Ymax,X):
        """
        Calculates a linear derating factor (Y) based on the given inputs.

        Args:
            X1 (float): The lower limit of the X range.
            X2 (float): The upper limit of the X range.
            Y1 (float): The derating factor when X=X1.
            Y2 (float): The derating factor when X=X2.
            Ymin (float): The minimum allowable value of the derating factor Y.
            Ymax (float): The maximum allowable value of the derating factor Y.
            X (float): The X value for which the derating factor is to be calculated.

        Returns:
            float: The linearly interpolated derating factor Y for the given X.

        Raises:
            ValueError: If X2 is equal to X1, which would result in a division by zero error.
        """

        # Calculate slope and intercept for linear relation
        m = (Y2 - Y1) / (X2 - X1)
        b = Y1 - m * X1

        # Linear interpolation
        Y = m * X + b

        # Clamp to Ymin and Ymax
        Y = min(Y, Ymax)
        Y = max(Y, Ymin)

        # return the derating factor
        return Y

    def IGSE(self, Wf, SP, d, f_s, Bp, Vc):
        """
        Analytical magnetic core loss calculation from IGSE- Improved Generailzed Steinmetz Equation for trapezoidal and triangular magnetic flux density waveform
        Args:
            Wf (str)    : Waveform selection - 'trap' for trapezoidal magnetic flux density waveform
                                               'tri' for triangular magnetic flux density waveform
            SP          : Steinmetz parameters of the core (k,a,b)
            d (0... 1)  : Duty cycle
            f_s (Hz)    : Switching frequency
            Bp (T)      : Magnetic field peak value
            Vc (m3)     : Core volume
        Returns:
            Pave_core(W) : Average core losses
        """

        # Helper function to compute ki based on Steinmetz parameters
        def ki(k,a,b):
            f = lambda theta, a: (abs(dp.np.cos(theta)))**SP[1]
            integral, error = dp.sc.integrate.quad(f, 0, 2* dp.np.pi, args=(SP[1]))
            ki = SP[0]/((2*dp.np.pi)**(SP[1]-1) * 2**(SP[2]-SP[1]) * integral)
            return ki

        # Compute average core loss density based on waveform type
        # and Multiply by core volume to get total average core loss
        match Wf:
            case 'trap':
                 Pave_density = ki(SP[0], SP[1], SP[2]) * f_s**SP[1] * Bp**SP[2] * 2**(SP[1]+SP[2]) * d**(1-SP[1])
                 Pave_core = Pave_density * Vc
            case 'tri':
                Pave_density = ki(SP[0], SP[1], SP[2]) * f_s**SP[1] * Bp**SP[2] * 2**SP[2] * (d**(1-SP[1]) + (1-d)**(1-SP[1]))
                Pave_core = Pave_density * Vc

        # return average core losses
        return Pave_core

    def I2GSE(self, Wf, n, SP, SR, d, f_s, Bp, dBdt, Vc, qr=0):
        """
        Analytical magnetic core loss calculation from I2GSE- Improved Improved Generailzed Steinmetz Equation for trapezoidal and triangular magnetic flux density waveform.
        This result is added with the IGSE solution to get the I2GSE solution.
        Args:
            Wf (str)    : Waveform selection - 'trap' for trapezoidal magnetic flux density waveform
                                               'tri' for triangular magnetic flux density waveform
            n           : number of transitions to 0 voltage (for PSFB n = 2)
            SR          : Relaxation parameters of the core (kr,ar,br,tau)
            d (0... 1)  : Duty cycle
            f_s (Hz)    : Switching frequency
            dBdt (T)    : Magnetic field variation before the transition to 0 voltage of transformer's primary
            Vc (m3)     : Core volume
            qr          : Relaxation parameter for triangular flux density waveform
        Returns:
            Pave_core(W) : Average core losses including IGSE loss
        """
        # Calculate time period, time spent at zero voltage and peak to peak magnetic flux value
        T = 1/f_s
        t1 = (T/2) - d*(T/2)
        Ton = d*T/2
        dB = dBdt * Ton

        # Compute average core loss density based on waveform type with relaxation parameter and multiply by core volume
        # Add the core loss with IGSE loss to get total average core loss
        match Wf:
            case 'trap':
                Pave_density = n * 1/T * SR[0] * abs(dBdt)**SR[1] * abs(dB)**SR[2] * (1-dp.np.exp(-t1/SR[3]))
                P_rl = Pave_density * Vc
                Pave_core = dp.np.sum(self.IGSE('trap', SP, d, f_s, Bp, Vc) + P_rl)
            case 'tri':
                if d < 0.5:
                    Pave_density = dp.np.exp(-qr * (d/(1-d)))
                else :
                    d = 1-d
                    Pave_density = dp.np.exp(-qr * (d/(1-d)))
                Q_rl = Pave_density * Vc
                Pave_core = dp.np.sum(self.IGSE('tri', SP, d, f_s, Bp, Vc) + Q_rl)

        # return average core losses
        return Pave_core

    def rac_lac_values(self, method, L_primary, frequencies, Z_real_csv):
        """
        Calculate AC resistance (Rac) and AC inductance (Lac) values from measured
        real resistance values of a transformer using either a minimize or least-squares method.

        *Args   :
            method (str)        : Optimization method selection
                                    - 'min' for minimize method
                                    - 'ls'  for least squares method
            L_primary (H)       : Magnetizing inductance of the transformer
            frequencies (Hz)    : Array of harmonic frequency spectrum
            Z_real_csv (Ω)      : Array of measured real resistance values corresponding to frequencies

        !Returns:
            dict                : Dictionary containing optimized/calculated parameters:
                                    - 'Rac'                  : Optimized AC resistance vector
                                    - 'Lac'                  : Optimized AC inductance vector
                                    - 'Rac_calculated'       : AC resistance including DC component
                                    - 'Z_real_residual'      : Residual AC resistance
                                    - 'Z_real_calculated'    : Reconstructed real resistance
                                    - 'Percentage_difference': Percentage difference between measured and calculated
        """

        #* -------------------------------
        #* Step 1: Preprocess input data
        #* -------------------------------

        # Extract DC resistance (frequency == 0)
        R_dc                = Z_real_csv[frequencies == 0][0]

        # Remove DC component from frequency and resistance arrays
        valid_index         = frequencies != 0
        frequencies         = dp.np.array(frequencies[valid_index])
        Z_real_csv          = dp.np.array(Z_real_csv[valid_index])

        #* -------------------------------
        #* Step 2: Initialize parameters
        #* -------------------------------

        # Initial AC resistance (small positive values) and AC inductance (evenly split)
        R_ac                = dp.np.ones(len(frequencies)) * 1e-3
        L_ac                = dp.np.full(len(frequencies), L_primary / len(frequencies))

        # Concatenate into a single initial guess vector for optimization
        initial             = dp.np.concatenate([R_ac, L_ac])

        # Compute angular frequencies and AC residuals
        omega               = 2 * dp.np.pi * frequencies
        Z_real_residual_csv = Z_real_csv - R_dc

        #* -------------------------------
        #* Step 3: Select optimization method
        #* -------------------------------
        match method:

            case 'min':

                #* -----------------------------------
                #* Define cost function for minimize
                #* -----------------------------------

                def cost_minimize(params, omega, Z_real_residual_csv):
                    """
                    Cost function for the 'minimize' optimization method.

                    Computes the squared error between measured residual AC resistance
                    and the modeled AC resistance using the Rac/Lac parameterization.

                    *Args   :
                        params              (array): Concatenated array of AC resistances (R_ac) and AC inductances (L_ac) for each frequency.
                        omega               (array): Angular frequencies (2 * pi * f) of the harmonics.
                        Z_real_residual_csv (array): Measured AC resistance (real part) with DC removed.

                    !Returns:
                        float                      : Sum of squared errors between measured and modeled AC resistance.
                    """

                    # Split parameters
                    # First half is AC resistance values and Second half is AC inductance values
                    R_ac            = params[:len(frequencies)]
                    L_ac            = params[len(frequencies):]

                    # Compute inductive reactance (XL = ω * L)
                    X_lac           = omega * L_ac

                    # Compute modeled AC resistance (Z_real_residual = R_ac * (X_lac^2) / (R_ac^2 + X_lac^2))
                    num             = R_ac * X_lac**2
                    den             = R_ac**2 + X_lac**2
                    Z_real_residual = num / den

                    # Compute error vector
                    error           = Z_real_residual_csv - Z_real_residual

                    # Return sum of squared errors
                    return sum(error**2)

                #* -----------------------------------
                #* Define inequality constraints
                #* -----------------------------------

                def R_ac_constraint(params):
                    """
                    Inequality constraint for AC resistance (Rac) during optimization.

                    Ensures that Rac is monotonically increasing with frequency,
                    i.e., each successive Rac value must be greater than the previous one.

                    *Args   :
                        params (array)  : Concatenated array of AC resistances (R_ac) and AC inductances (L_ac) for each frequency.

                    !Returns:
                        list            : Differences between consecutive Rac values.
                                          All values must be >= 0 to satisfy the monotonic increase constraint.
                    """

                    # Extract AC resistance values
                    R_ac    = params[:len(frequencies)]

                    # Return differences between consecutive Rac values
                    # Positive values satisfy the monotonic increase constraint
                    return [
                                R_ac[4] - R_ac[3],  # R5 > R4
                                R_ac[3] - R_ac[2],  # R4 > R3
                                R_ac[2] - R_ac[1],  # R3 > R2
                                R_ac[1] - R_ac[0]   # R2 > R1
                            ]

                def L_ac_constraint(params):
                    """
                    Inequality constraint for AC inductance (Lac) during optimization.

                    Ensures that the sum of all AC inductances does not exceed
                    the primary magnetizing inductance of the transformer.

                    *Args   :
                        params (array)  : Concatenated array of AC resistances (R_ac) and AC inductances (L_ac) for each frequency.

                    !Returns:
                        float           : Difference between total primary inductance and sum of Lac.
                                          Must be >= 0 to satisfy the constraint.
                    """

                    # Extract AC inductance values
                    L_ac    = params[len(frequencies):]

                    # Compute constraint Positive value ensures sum(Lac) <= L_primary
                    return L_primary - sum(L_ac)

                # Constraints for the 'minimize' method:
                    # - Rac must be monotonically increasing with frequency
                    # - Sum of Lac values must not exceed the primary inductance
                constraints = [
                                {'type': 'ineq', 'fun': R_ac_constraint},  # Rac monotonic increase constraint
                                {'type': 'ineq', 'fun': L_ac_constraint}   # Total Lac <= L_primary constraint
                            ]

                #* -----------------------------------
                #* Define bounds for optimization
                #* -----------------------------------

                bounds      = (

                                [(1e-6, 100e-3)] * len(frequencies) +                           # Bounds for Rac
                                [((L_primary / len(frequencies)), 1e-3)] * len(frequencies)     # Bounds for Lac
                            )

                # Perform constrained minimization
                res         = dp.sc.optimize.minimize(cost_minimize, initial, args=(omega, Z_real_residual_csv), bounds=bounds, constraints=constraints)

            case 'ls':

                #* -----------------------------------
                #* Define cost function for least squares
                #* -----------------------------------

                def cost_leastsquares(params, omega, Z_real_residual_csv):
                    """
                    Cost function for the 'least_squares' optimization method.

                    Computes the residual error between measured AC resistance and the modeled
                    AC resistance using the Rac/Lac parameterization. Unlike the 'minimize' method,
                    it returns the error vector instead of the sum of squared errors.

                    *Args   :
                        params              (array): Concatenated array of AC resistances (R_ac) and AC inductances (L_ac) for each frequency.
                        omega               (array): Angular frequencies (2 * pi * f) of the harmonics.
                        Z_real_residual_csv (array): Measured AC resistance (real part) with DC removed.

                    !Returns:
                        array                      : Residual error vector (Z_real_residual_csv - Z_real_residual) for use in least squares fitting.
                    """

                    # Split parameters
                    R_ac            = params[:len(frequencies)]      # AC resistance vector
                    L_ac            = params[len(frequencies):]      # AC inductance vector

                    # Compute inductive reactance
                    X_lac           = omega * L_ac                   # XL = ω * L

                    # Compute modeled AC resistance
                    num             = R_ac * X_lac**2
                    den             = R_ac**2 + X_lac**2
                    Z_real_residual = num / den

                    # Compute residual error vector
                    error           = Z_real_residual_csv - Z_real_residual

                    return error

                #* -----------------------------------
                #* Define bounds for least squares
                #* -----------------------------------

                lb      = [1e-6] * len(frequencies) + [L_primary / len(frequencies)] * len(frequencies)
                ub      = [100e-3] * len(frequencies) + [1e-3] * len(frequencies)

                # Perform least squares fitting
                res     = dp.sc.optimize.least_squares(cost_leastsquares, initial, args=(omega, Z_real_residual_csv), bounds=(lb, ub))

        #* -------------------------------
        #* Step 4: Extract fitted parameters
        #* -------------------------------

        fitted_param        = res.x
        R_fit               = fitted_param[:len(frequencies)]
        L_fit               = fitted_param[len(frequencies):]

        # Compute residual AC resistance
        Xl_fit              = omega * L_fit
        Z_real_residual     = (R_fit * Xl_fit**2) / (R_fit**2 + Xl_fit**2)

        # Reconstruct total real resistance
        Z_real_calculated   = Z_real_residual + R_dc

        # Compute percentage difference between measured and calculated values
        percentage_difference = ((Z_real_calculated - Z_real_csv) / Z_real_csv) * 100

        #* -------------------------------
        #* Step 5: Prepare output dictionary
        #* -------------------------------

        res_optimize        = {
                                'Rac': R_fit,
                                'Lac': L_fit,
                                'Rac_calculated': R_fit + R_dc,
                                'Z_real_residual': Z_real_residual,
                                'Z_real_calculated': Z_real_calculated,
                                'Percentage_difference': percentage_difference
                            }

        return res_optimize

    def analytical_impedance(self,f,T,h,m,b,Nt,Tl,n,par):
        """
        Calculate analytical impedance(Zw) from Dowell's equation for the wire used in the winding.

        *Args   :
            f           (Hz)        : Array of frequency for Dowell curve
            Temperature (°C)        : Temperature of the winding for resistivity calculation
            h           (m)         : Height or diameter of round conductor
            m           (unitless)  : Number of winding layers
            b           (m)         : Winding breadth
            Nt          (unitless)  : Number of turns per layer
            Tl          (m)         : mean turn length
            n           (unitless)  : Porosity factor (0.785 for round conductor and 1 for foil conductor)
            par         (unitles)   : Number of parallel foil

        !Returns:
            Zw          (Ω)         : Total impedance (Rac + j*w*Lac) from Dowell's equation
            Rdc         (Ω)         : DC resistance of the winding
            Ldc         (H)         : DC leakage inductance with respect to only one layer under DC conditions
            Fr          (unitless)  : Ratio of Rac to Rdc
            Fl          (unitless)  : Ratio of Lac to Ldc
            Q           (unitless)  : Normalized frequency factor h/skin_depth
        """
        # Constants
        # permeability of free space (H/m), resistivity(Ω.m) of copper at 20°C and temp. coefficient of Copper
        mu0     = 4*dp.np.pi*1e-7
        ro      = 1.71e-8
        temp_coeff = 0.00393

        # Compute diameter of equivalent square conductor (m) for given winding wire geometry
        w       = 2*dp.np.pi*f
        d       = dp.np.sqrt(dp.np.pi/4) * h * par

        # Compute skin depth effect at a given temperature T
        rho     = ro*(1+temp_coeff*(T-20))
        skin    = dp.np.sqrt((2*rho)/(w*mu0))

        #* Compute Dowell's parameters
        # alpha, D, M, and Q- normalized height of layer relative to skin depth
        alpha   = dp.np.sqrt(1j*w*mu0*n*(1/rho))
        D       = 2*alpha*d*dp.np.tanh(alpha*d/2)
        M       = alpha*d *(1/dp.np.tanh(alpha*d))
        Q       = d/skin

        # Compute ratio of ac resistance to dc resistance
        Fr      = dp.np.real(M)+ (m**2 - 1)*(dp.np.real(D)/3)
        Rdc     = m*rho*Nt**2*Tl/(n*b*d)
        Rac     = Rdc * Fr

        # Compute ratio of ac leakage inductance to dc leakage inductance
        Fl      = (3*dp.np.imag(M) + (m**2 - 1)*dp.np.imag(D))/(m**2 * abs(alpha**2 * d**2))
        Ldc     = (mu0* m**3 *Nt**2 *Tl *d)/ (3*b)
        Lac     = Ldc*Fl
        Zw      = Rac + 1j*w*Lac

        return Zw, Rdc, Ldc, Fr, Fl, Q

    def Dowell_Rac_Lac(self,f,Zw,Rdc,Ldc,Fr,Fl,Q,Lm):
        """
        Calculate AC resistance (Rac) and AC inductance (Lac) values from Dowell's analytical impedance calculation and optimization algorithm.

        *Args   :
            f   (Hz)        : Array of frequency
            Zw  (Ω)         : Total impedance (Rac + j*w*Lac) from Dowell's equation
            Rdc (Ω)         : DC resistance of the winding
            Ldc (H)         : DC leakage inductance with respect to only one layer under DC conditions
            Fr  (unitless)  : Ratio of Rac to Rdc
            Fl  (unitless)  : Ratio of Lac to Ldc
            Q   (unitless)  : Normalized frequency factor
            Lm  (H)         : Magnetizing inductance of transformer

        !Returns:
           dict             : Dictionary containing optimized/calculated parameters:
                                - 'Rac'     : Optimized AC resistance vector
                                - 'Lac'     : Optimized AC inductance vector
                                - 'Z_fit'   : Calculated impedance from the optimized Rac and Lac
        """

        #* -------------------------------------
        #* Step 1: Compute equivalent impedance
        #* -------------------------------------

        def eq_impedance(f,Rdc,R,L):
            """
            Calculate equivalent impedance of the parallel Rac and Lac circuit.

            *Args   :
                f   (Hz)    : Array of frequency
                Rdc (Ω)     : DC resistance of the winding
                R   (Ω)     : Array of AC resistances
                L   (H)     : Array of AC inductances

            !Returns:
                Zeq (Ω)     : Equivalent impedance (Rdc + ∑ (Rac || Lac))
            """
            w    = 2*dp.np.pi*f
            Zeq = Rdc + 0j
            for Ri, Li in zip(R, L):
                Zeq += (Ri * (w*Li)**2 + 1j* Ri**2 * w*Li)/(Ri**2 + w*Li**2)
            return Zeq

        #* -------------------------------
        #* Step 2: Define Cost function
        #* -------------------------------

        def cost_minimize(params, f, Zw, Fr, Fl, Rdc, Ldc):
            """
            Cost function for minimize optimization method.

            Computes the squared error between Dowell impedance and the modeled equivalent circuit impedance.

            *Args   :
                params  (array): Concatenated array of AC resistances (Rac) and AC inductances (Lac).
                f       (Hz)        : Array of frequency
                Zw      (Ω)         : Total impedance (Rac + j*w*Lac) from Dowell's analytical equation
                Rdc     (Ω)         : DC resistance of the winding
                Ldc     (H)         : DC leakage inductance with respect to only one layer under DC conditions
                Fr      (unitless)  : Ratio of Rac to Rdc
                Fl      (unitless)  : Ratio of Lac to Ldc

            !Returns:
                float               : Sum of squared errors between Dowell impedance and the modeled equivalent circuit impedance.
            """
            # Split parameters
            # First half is AC resistance values and Second half is AC inductance values
            R = params[:5]
            L = params[5:]

            # Compute equivalent impedance for the split parameters
            Ze = eq_impedance(f,Rdc,R,L)

            # Compute error vector
            err = (Zw- Ze)

            # Return sum of squared errors
            return sum(err.real**2 + err.imag**2)

        #* -------------------------------
        #* Step 3: Initialize parameters
        #* -------------------------------

        # Initial AC resistance and AC inductance(small positive values)
        Rk = dp.np.ones(5)*1e-3
        Lk = dp.np.ones(5)*0.1e-6

        # Concatenate into a single initial guess vector for optimization
        initial = dp.np.concatenate([Rk,Lk])

        #*--------------------------------
        #* Define inequality constraints
        #*--------------------------------

        def Rk_constraint(params):
            """
            Inequality constraint for AC resistance (Rac) during optimization.
            Ensures that Rac is monotonically increasing with frequency,
            i.e., each successive Rac value must be greater than the previous one.

            *Args   :
                params (array)  : Concatenated array of AC resistances (R_ac) and AC inductances (L_ac).
            !Returns:
                list            : Differences between consecutive Rac values. All values
                                  must be >= 0 to satisfy the monotonic increase constraint.
            """

            # Extract AC resistance values
            Rk = params[:5]

            # Return differences between consecutive Rac values
            # Positive values satisfy the monotonic increase constraint
            return [Rk[4] - Rk[3],                  # R5 > R4
                    Rk[3] - Rk[2],                  # R4 > R3
                    Rk[2] - Rk[1],                  # R3 > R2
                    Rk[1] - Rk[0] ]                 # R2 > R1

        def Lk_constraint(params):
            """
            Inequality constraint for AC inductance (Lac) during optimization.
            Ensures that the sum of all AC inductances does not exceed
            the primary magnetizing inductance of the transformer.

            *Args   :
                params (array)  : Concatenated array of AC resistances (R_ac) and AC inductances (L_ac) for each frequency.
            !Returns:
                list            : Differences between consecutive Lac values and difference between total primary inductance and sum of Lac.
                                  Must be >= 0 to satisfy the constraint.
            """

            # Extract AC inductance values
            Lk = params[5:]

            # Return differences between consecutive Lac values and difference between total primary inductance and sum of Lac
            # Positive values satisfy the monotonic decrease constraint
            return [Lk[0] - Lk[1],                                                  # L1 > L2
                    Lk[1] - Lk[2],                                                  # L2 > L3
                    Lk[2] - Lk[3],                                                  # L3 > L4
                    Lk[3] - Lk[4],                                                  # L4 > L5
                    Lm - sum(Lk)]                                                   # sum(Lac) < Lm,

        # Constraints for the 'minimize' method:
            # - Rac must be monotonically increasing with frequency
            # - Sum of Lac values must not exceed the primary inductance
        constraints = [{'type':'ineq', 'fun': Rk_constraint},                       # Rac monotonic increase constraint
                       {'type':'ineq', 'fun': Lk_constraint}]                       # Lac monotonic decrease and Total Lac <= L_primary constraint

        #*--------------------------------
        #* Define bounds for optimization
        #*--------------------------------
        bounds = (
                    [(1e-6, 100e-3)]* 5                                            # Rac bounds
                    + [(0.1e-6, 1e-3)]* 5                                          # Lac bounds
                 )

        # Perform constrained minimization
        res_min = dp.minimize(cost_minimize, initial, args= (f, Zw, Fr,Fl, Rdc, Ldc), bounds=bounds, constraints=constraints,)

        #* -------------------------------
        #* Step 4: Extract fitted parameters
        #* -------------------------------
        fitted_param_min     = res_min.x
        R_fit_min            = dp.np.array(fitted_param_min[:5])
        L_fit_min            = dp.np.array(fitted_param_min[5:])

        # Calculate equivalent impedance from the fitted Rac and Lac
        Z_fit_min            = eq_impedance(f,Rdc,R_fit_min, L_fit_min)

        #* -------------------------------
        #* Step 5: Prepare output dictionary
        #* -------------------------------
        res_optimize        = {
                                    'Rac': R_fit_min,
                                    'Lac': L_fit_min,
                                    'Z_fit': Z_fit_min,
                                }
        return res_optimize

#?-------------------------------------------------------------------------------------------------------------------------------------------------------------
