
#?-------------------------------------------------------------------------------------------------------------------------------------------------------------
#?                            ____   _    ____      _    __  __   ____  ____   ___   ____ _____ ____ ____ ___ _   _  ____
#?                           |  _ \ / \  |  _ \    / \  |  \/  | |  _ \|  _ \ / _ \ / ___| ____/ ___/ ___|_ _| \ | |/ ___|
#?                           | |_) / _ \ | |_) |  / _ \ | |\/| | | |_) | |_) | | | | |   |  _| \___ \___ \| ||  \| | |  _
#?                           |  __/ ___ \|  _ <  / ___ \| |  | | |  __/|  _ <| |_| | |___| |___ ___) |__) | || |\  | |_| |
#?                           |_| /_/   \_\_| \_\/_/   \_\_|  |_| |_|   |_| \_\\___/ \____|_____|____/____/___|_| \_|\____|
#?
#?-------------------------------------------------------------------------------------------------------------------------------------------------------------
import  os
import  copy

import  numpy                               as          np
import  Lib.Pyoptimize                      as          po

from    pymoo.optimize                      import      minimize as optmin
from    pymoo.termination                   import      get_termination
from    pymoo.algorithms.soo.nonconvex.ga   import      GA
#?-------------------------------------------------------------------------------------------------------------------------------------------------------------
class ParamProcess:
    def __init__(self):
        """
        Initialize the ParamProcess class with post-processing and simulation utilities.
        """

    #?-------------------------------------------------------------------------------------------------------------------------------------------------------------
    #? MOSFETs data processing
    #?-------------------------------------------------------------------------------------------------------------------------------------------------------------

    def MOSFETcaps(self, path, switch_name, type=""):
        """
        Calculate MOSFET capacitance, charge, and energy from CSV  files.

        This function reads capacitance data (C-V curves) from CSV files provided by
        datasheets or suppliers and computes:
            - Capacitance (Cmos)
            - Integrated charge (Qmos)
            - Stored energy (Emos)
            - Equivalent capacitances derived from charge (Cmos_tr)
            - Equivalent capacitances derived from energy (Cmos_er)

        ?Formulas used:
            - Charge from capacitance:
                Q(V) = ∫ C(V) dV    (trapezoidal integration using numpy.trapz)
            - Energy from capacitance:
                E(V) = ∫ C(V) * V dV = ∫ Q(V) dV
            - Differential capacitance from charge:
                C_tr = ΔQ / ΔV
            - Differential capacitance from energy:
                C_er = 2 * ΔE / Δ(V²)

        *Args    :
            path (str)        : Folder path to CSV datasheet
            switch_name (str) : MOSFET switch file name
            type (str, optional): Optional suffix for file type. Default is empty.

        !Returns:
            tuple: (Cmos, Qmos, Emos, Cmos_tr, Cmos_er)
                - Cmos      : Capacitance array [V, C] in Farads
                - Qmos      : Integrated charge array in Coulombs
                - Emos      : Integrated energy array in Joules
                - Cmos_tr   : Differential capacitance derived from charge
                - Cmos_er   : Differential capacitance derived from energy

        Libraries used:
            - numpy.trapz() for numerical integration, which approximates the area under the curve using the trapezoidal rule.
              [numpy.trapz() docs]: https://numpy.org/doc/1.25/reference/generated/numpy.trapz.html
        """

        # Construct full path to CSV
        switch      = path + switch_name + type

        # Extract capacitance arrays [V, C] from CSV
        Cmos        = self.extractArrays(switch)

        # Calculate C*V product for energy integration
        Vds_Cmos    = [Cmos[0], (np.multiply(np.array(Cmos[0]), np.array(Cmos[1]))).tolist()]

        # Initialize lists for charge and energy
        Qmos        = []
        Emos        = []

        # Integrate capacitance and energy using trapezoidal rule
        for i in range(len(Cmos[0])):
            # Charge calculation Q = ∫ C(V) dV
            idx             = self.get_index(Cmos, Cmos[0][i], 0)
            capacity        = (np.array(Cmos)[:, 0:idx+1]).tolist()
            charge          = float(np.trapz(capacity[1], x=capacity[0]))
            Qmos.append(np.around(charge, 3))

            # Energy calculation E = ∫ V * C(V) dV = ∫ Q(V) dV
            idx             = self.get_index(Vds_Cmos, Vds_Cmos[0][i], 0)
            capacityVoltage = (np.array(Vds_Cmos)[:, 0:idx+1]).tolist()
            energy          = float(np.trapz(capacityVoltage[1], x=capacityVoltage[0]))
            Emos.append(np.around(energy, 3))

        # Convert to SI units (Farads, Coulombs, Joules)
        Cmos[1]             = np.array(Cmos[1])*1e-12
        Cmos                = np.array(Cmos)
        Qmos                = np.array(Qmos)*1e-12
        Emos                = np.array(Emos)*1e-12

        # Compute equivalent capacitances
        # Cmos_tr from charge: C = ΔQ / ΔV
        # Cmos_er from energy: C = 2 * ΔE / Δ(V^2)
        Cmos_tr             = (Qmos[1:] / (Cmos[0][1:] - Cmos[0][0])).tolist()
        Cmos_er             = (2 * Emos[1:] / (Cmos[0][1:]**2 - Cmos[0][0]**2)).tolist()

        # Insert zero for first point to match array length
        Cmos_tr.insert(0, Cmos_tr[0])
        Cmos_er.insert(0, Cmos_er[0])

        # Convert arrays to lists for output
        Cmos                = Cmos.tolist()
        Qmos                = Qmos.tolist()
        Emos                = Emos.tolist()

        return Cmos, Qmos, Emos, Cmos_tr, Cmos_er

    def Forward_Transfer_data(self, switchesTransferPath, switch_name):
        """
        Extract forward transfer characteristics (Vds vs Ids) for a MOSFET switch.

        This function reads the MOSFET transfer characteristics from a CSV file
        (Vds vs Ids at different gate voltages), converts the extracted data
        into NumPy arrays for processing, and returns it as lists.

        *Args    :
            switchesTransferPath (str): Path to the folder containing transfer characteristics data.
            switch_name (str): Name identifier for the MOSFET switch.

        !Returns:
            tuple: Two lists:
                - Vdsvec: Drain-source voltage values (V)
                - Idsvec: Corresponding drain-source current values (A)
                        at different gate voltages; each row corresponds to a Vds point.

        Notes:
            - CSV files are expected to be structured with the first column as Vds and
            subsequent columns as Ids for different gate voltages.
            - Uses NumPy for array manipulation: https://numpy.org/doc/stable/
        """

        # Construct full file path and extract CSV data as arrays
        Transfer        = switchesTransferPath + switch_name + '_Transfer'
        Transfer_vec    = self.extractArrays(Transfer)

        # Extract Vds vector (first column)
        Vdsvec          = Transfer_vec[0]

        # Extract Ids matrix and transpose so each row corresponds to Vds
        Idsvec          = np.array(Transfer_vec[1:])
        Idsvec          = (np.array(Idsvec)).T.tolist()

        return Vdsvec, Idsvec

    def MOSFETenergies(self, path, switch_name, type=""):
        """
        This function reads MOSFET energy loss data from CSV ,
        reshapes it into a 3D array corresponding to voltage, current, and gate voltage,
        and applies unit conversion to Joules. It also generates a MATLAB-style
        3D array concatenation command string for visualization or further processing.

        *Args    :
            path (str): Directory path containing the energy data file.
            switch_name (str): Name identifier for the MOSFET switch.
            type (str, optional): Suffix specifying the type of energy data. Default is "".

        !Returns:
            tuple: Contains three elements:
                - current (list): Unique current values (A) present in the dataset.
                - cat (str): MATLAB-style 3D concatenation string representing LuT_3D.
                - Emos (list): 3D list of energy loss data (Joules), shaped as
                            [voltage, current, gate voltage].
        """

        # Construct full file path
        switch      = path + switch_name + type

        # Extract energy data arrays
        EmosData    = self.extractArrays(switch)
        EmosData    = np.array(EmosData)

        # Transpose to prepare for slicing
        EmosData_T  = EmosData[1:].T

        # Identify unique currents and dimensions
        current     = np.unique(EmosData[0]).tolist()
        volt_length = (EmosData[0].tolist()).count(EmosData[0][0])
        gate_length = len(EmosData) - 1
        curr_length = len(current)
        curr_idx    = np.array(list(range(0, curr_length)))

        # Initialize 3D energy array and MATLAB-style concatenation string
        LuT_3D      = np.empty((volt_length, curr_length, gate_length))

        # Populate 3D array and build concatenation string
        cat         = 'cat(3'
        for i in range(volt_length):
            indices         = i * curr_length + curr_idx
            LuT_3D[:][:][i] = EmosData_T[indices, :] #- EmosData_T[0][0])
            cat             = cat + ',' + 'LuT_3D' + '(:,:,' + str(i + 1) + ')'
        cat         = cat + ')'

        # Convert 3D array to list for output
        Emos        = LuT_3D.tolist()

        return current, cat, Emos

    def MOSFETrdson(self, path, switch_name, type=""):
        """
        This function reads Rds_on data from datasheets or supplier files,
        separates the independent variable (temperature or current) and
        the corresponding on-resistance values, and returns them as lists.
        In case of temperature, Rds_on data is absolute values. In case of
        current, Rds_on data is a multiplier of the nominal Rds_on value.

        *Args    :
            path (str): Directory path containing the Rds_on data file.
            switch_name (str): Name identifier for the MOSFET switch.
            type (str, optional): Suffix specifying the type of Rds_on data. Default is "".

        !Returns:
            tuple: Two lists:
                - Rvec: On-resistance values (Ohms or multiplier)
                - Xvec: Corresponding independent variable values
                        (temperature or current).
        """

        # Construct full file path
        Switch      = path + switch_name + type

        # Extract Rds_on and independent variable arrays
        R_X_Vec     = self.extractArrays(Switch)
        R_X_Types   = len(R_X_Vec)

        # Separate independent variable (X) and resistance (R) vectors
        Rvec        = []
        Xvec        = []
        for i in range(R_X_Types // 2):
            Xvec.append(R_X_Vec[i * 2])
            Rvec.append(R_X_Vec[i * 2 + 1])

        # Transpose arrays so each row corresponds to a dataset
        Rvec        = (np.array(Rvec)).tolist()
        Xvec        = (np.array(Xvec)).tolist()

        return Rvec, Xvec

    def DiodeVI_data(self, DiodeVIPath, diode_name):
        """
        This function reads diode V-I data from a CSV file,
        separates voltage and current values, and returns them as lists suitable for plotting or
        further analysis. In addition, dynamic resistance and threshold voltage are extracted.

        *Args    :
            DiodeVIPath (str): Path to the folder containing diode VI characteristics data.
            diode_name (str): Name identifier for the diode.

        !Returns:
            tuple: Four lists:
                - Vvec: Voltage values across the diode (V)
                - Ivec: Corresponding current values through the diode (A)
                - Rd: Dynamic resistance for each voltage vector
                - Vt: Threshold voltage for each voltage vector
        """

        # Construct full file path
        Diode   =   DiodeVIPath + diode_name + '_VI'

        # Extract V-I data arrays
        V_I     =   self.extractArrays(Diode)

        # Separate voltage and current vectors
        Vvec    =   (np.array(V_I[1:])).T      # Voltage array, transposed
        Ivec    =   np.array(V_I[0])           # Current array

        # Caclulate simple diode parameters
        Rd      =   (Vvec[-5] - Vvec[-1])/(Ivec[-5] - Ivec[-1])     # dynamic resistance is the slope
        Vt      =   Vvec[-1] - Rd*Ivec[-1]                          # threshold voltage is the y-intercept

        # Convert vectors to lists
        Vvec    =   Vvec.tolist()
        Ivec    =   Ivec.tolist()
        Rd      =   Rd.tolist()
        Vt      =   Vt.tolist()

        return Vvec, Ivec, Rd, Vt

    def getCoss(self, switch, blockingVoltage, time_energy):
        """
        Calculate the effective value of any of the capacitances of a MOSFET.

        This function computes Cmos at a given blocking voltage using either
        time-effective (Qmos-based) or energy-effective (Emos-based) methods
        commonly used in power electronics.

        *Args    :
            switch (dict): Dictionary containing MOSFET capacitance characteristics with keys:
                - 'Vvec': List of voltages (V)
                - 'Cvec': List of measured capacitances (F)
                - 'Qmos': List of stored charge values (Coulombs)
                - 'Emos': List of energy values (Joules)
            blockingVoltage (float): Voltage (V) at which to evaluate Cmos.
            time_energy (bool): Select calculation method:
                - True: Time-effective capacitance (Cmos = Qmos / ΔV)
                - False: Energy-effective capacitance (Cmos = 2*Emos / ΔV²)

        !Returns:
            float: Effective output capacitance (Cmos) in Farads.
        """

        # Extract voltage and capacitance arrays from dictionary
        voltageVector   = switch['Coss']['Vvec']
        CossVector      = switch['Coss']['Cvec']
        QossVector      = switch['Coss']['Qoss']
        EossVector      = switch['Coss']['Eoss']

        # Prepare voltage-capacitance pair for indexing
        Coss            = [voltageVector, CossVector]

        # Get the index of the closest voltage to the blockingVoltage
        Coss_idx        = self.get_index(Coss, blockingVoltage, 0)

        # Compute effective Coss based on selected method
        if time_energy:
            Qoss        = QossVector[Coss_idx]
            Coss_eff    = Qoss / (Coss[0][Coss_idx] - Coss[0][0])  # Time-effective
        else:
            Eoss        = EossVector[Coss_idx]
            Coss_eff    = 2 * Eoss / (Coss[0][Coss_idx]**2 - Coss[0][0]**2)  # Energy-effective

        # Round result to 2 decimal pF and convert back to Farads
        Coss_eff        = round(Coss_eff * 1e12, 2) * 1e-12

        return Coss_eff

    def getCmos(self, capacitance, Cmos_tr, cmos_er, blockingVoltage, time_energy):
            """
            Calculate the effective value of any of the capacitances of a MOSFET.

            This function computes Cmos at a given blocking voltage using either
            time-effective (Qmos-based) or energy-effective (Emos-based) methods
            commonly used in power electronics.

            *Args    :
                capacitance (list): List containing voltage and capacitance arrays [Vvec, Cvec].
                Cmos_tr (list): List of stored charge values (Coulombs)
                cmos_er (list): List of energy values (Joules)
                blockingVoltage (float): Voltage (V) at which to evaluate Cmos.
                time_energy (bool): Select calculation method:
                    - True: Time-effective capacitance (Cmos = Qmos / ΔV)
                    - False: Energy-effective capacitance (Cmos = 2*Emos / ΔV²)

            !Returns:
                float: Effective output capacitance (Cmos) in Farads.
            """

            # Get the index of the closest voltage to the blockingVoltage
            Cmos_idx        = self.get_index(capacitance, blockingVoltage, 0)

            # Compute effective Cmos based on selected method
            if time_energy:
                Cmos_eff    = Cmos_tr[Cmos_idx]     # Cmos = Qmos / ΔV      --> # Time-effective
            else:
                Cmos_eff    = cmos_er[Cmos_idx]     # Cmos = 2*Emos / ΔV²   --> # Energy-effective

            # Round result to 2 decimal pF and convert back to Farads
            Cmos_eff        = round(Cmos_eff * 1e12, 2) * 1e-12

            return Cmos_eff

    #?-------------------------------------------------------------------------------------------------------------------------------------------------------------
    #? Magnetics data processing
    #?-------------------------------------------------------------------------------------------------------------------------------------------------------------

    def Mags_CoreLoss_Data(self, TrafoCoreLossesPath, trafo_name):
        """
        This function reads core loss data for a transformer, reshapes it into a
        3D array representing temperature, flux, and voltage, and generates a
        MATLAB-style concatenation string for visualization or further processing.

        *Args    :
            TrafoCoreLossesPath (str): Path to the folder containing core loss data files.
            trafo_name (str): Name identifier for the transformer.

        !Returns:
            tuple: Contains three elements:
                - flux (list): Magnetic flux values in MegaWeber (Wb)
                - cat (str): MATLAB-style 3D concatenation string representing LuT_3D
                - loss (list): 3D list of core loss data (W), shaped as
                            [temperature, flux, voltage]
        """

        # Construct full file path
        Trafo           = TrafoCoreLossesPath + trafo_name

        # Extract core loss data
        coreData        = self.extractArrays(Trafo)
        coreData        = np.array(coreData)

        # Transpose to prepare for slicing
        coreData_T      = coreData[1:].T

        # Extract unique flux values and convert to MWb
        flux            = (np.unique(coreData[0]) * 1.0e-6 / 2.0).tolist()

        # Determine dimensions for 3D array
        temp_length     = (coreData[0].tolist()).count(coreData[0][0])
        voltage_length  = len(coreData) - 1
        flux_length     = len(flux)
        flux_idx        = np.array(list(range(0, flux_length)))

        # Initialize 3D array and MATLAB-style concatenation string
        LuT_3D          = np.empty((temp_length, flux_length, voltage_length))
        cat             = 'cat(3)'

        # Populate 3D array and build concatenation string
        cat = 'cat(3'
        for i in range(temp_length):
            indices         = i * flux_length + flux_idx
            LuT_3D[:][:][i] = coreData_T[indices, :]
            cat             = cat + ',' + 'LuT_3D' + '(:,:,' + str(i + 1) + ')'
        cat             = cat + ')'

        # Convert 3D array to list for output
        loss            = LuT_3D.tolist()

        return flux, cat, loss

    def Mags_FreqRes_Data(self, FreqResistancePath, mag_name):
        """
        This function reads resistance vs frequency data for one or more magnetic components
        (e.g., inductors, transformers) from CSV files, converts units to mOhm and kHz,
        and returns them as lists suitable for plotting or further analysis.

        *Args    :
            FreqResistancePath (str): Path to the folder containing frequency response data files.
            mag_name (list): List of names identifying the magnetic components.

        !Returns:
            tuple: Two lists:
                - Fvec: Frequency values in kHz for each component
                - Rvec: Corresponding resistance values in mΩ for each component
        """

        # Initialize lists for resistance and frequency vectors
        Rvec            = []
        Fvec            = []

        # Loop through each magnetic component
        for i in range(len(mag_name)):
            # Construct full file path for the component
            Winding     = FreqResistancePath + mag_name[i]

            # Extract frequency-resistance data arrays
            R_F         = self.extractArrays(Winding)

            # Convert units
            R           = (np.array(R_F[1:])*1e-3).tolist()  # mOhms -> Ohm
            F           = (np.array(R_F[0])*1e3).tolist()    # kHz -> Hz

            # Append to the output lists
            Rvec.append(R)
            Fvec.append(F)

        return Fvec, Rvec

    def Mags_LI_Data(self, InductanceCurrentPath, mag_name):
        """
        This function reads L-I data from CSV or simulation results for a given magnetic
        component (e.g., inductor or transformer winding), converts the units to Henries,
        and returns current and inductance values as lists suitable for plotting or analysis.

        *Args    :
            InductanceCurrentPath (str): Path to the folder containing inductance data files.
            mag_name (str): Name identifier for the magnetic component.

        !Returns:
            tuple: Two lists:
                - Ivec: Current values (A)
                - Lvec: Corresponding inductance values (H)
        """

        # Construct full file path
        Mag     = InductanceCurrentPath + mag_name

        # Extract L-I data arrays
        L_I_Vec = self.extractArrays(Mag)

        # Separate current and inductance vectors
        Ivec    = L_I_Vec[0]

        # Convert inductance to Henries and transpose
        Lvec    = np.array(L_I_Vec[1:])
        Lvec    = (np.array(Lvec) * 1e-6).T.tolist()

        return Ivec, Lvec

    #?-------------------------------------------------------------------------------------------------------------------------------------------------------------
    #? Analytical models processing
    #?-------------------------------------------------------------------------------------------------------------------------------------------------------------

    def PrechargeILVref(self, V_snub, V_LV_OP, Np, Ns, fs, Lfilter, Lks, Lkp, I_C_max, ILVmax, tonsnubmin, Points):
        """
        This function computes a voltage vector, corresponding precharge current references,
        and the final snubber turn-on time based on transformer parameters, leakage
        inductances, and snubber constraints.

        *Args    :
            V_snub (float)      : Snubber circuit voltage (V)
            V_LV_OP (float)     : Low-voltage operational voltage (V)
            Np (int)            : Primary winding turns
            Ns (int)            : Secondary winding turns
            fs (float)          : Switching frequency (Hz)
            Lfilter (float)     : Filter inductance (H)
            Lks (float)         : Secondary leakage inductance (H)
            Lkp (float)         : Primary leakage inductance (H)
            I_C_max (float)     : Maximum allowable snubber capacitor current (A)
            ILVmax (int)        : Maximum low-voltage current index
            tonsnubmin (float)  : Minimum allowable snubber turn-on time (s)
            Points (int)        : Number of points for voltage/current vector calculation

        !Returns:
            tuple: Contains three elements:
                - Vvec (list)           : Voltage vector (V)
                - Ivec (list)           : Precharge current reference vector (A)
                - ton_snub_final (float): Final snubber turn-on time (s)
        """

        # Compute turns ratio and low-voltage referred leakage inductance
        ntr             = Np / Ns
        L_leak_lv       = (Lks + Lkp) / (ntr ** 2)

        # Generate voltage vector
        Vvec            = list(np.linspace(0, V_LV_OP * ntr, Points))
        Ivec            = copy.deepcopy(Vvec)

        # Loop over each voltage and low-voltage current
        for V_HV in Vvec:
            Iref = 0
            for ILV in range(ILVmax + 1):
                Duty        = (V_snub - V_LV_OP) / (V_snub - V_HV / ntr)
                toff        = (1 - Duty) / (2 * fs)
                ton_snub    = pow(2 * L_leak_lv * ILV * toff / (V_snub - V_HV / ntr), 0.5)
                dI_LV       = (V_snub - V_LV_OP) * toff / Lfilter
                ILV_peak    = ILV + dI_LV / 2
                Ipeak_snub  = (V_snub - V_HV / ntr) * ton_snub / L_leak_lv
                IC_snub_P   = pow(2 * fs * ((ILV_peak**2 * toff) + ((V_snub - V_LV_OP)**2 * toff**3) / (3 * Lfilter**2)) -(ILV_peak * (V_snub - V_LV_OP) * toff**2 / Lfilter), 0.5)
                IC_snub_N   = Ipeak_snub * pow((2 * fs * ton_snub / 3), 0.5)
                IC_snub_RMS = pow(IC_snub_P**2 + IC_snub_N**2, 0.5)

                # Select precharge current if RMS current is below max
                if IC_snub_RMS < I_C_max:   Iref = ILV

            # Determine final snubber turn-on time
            if V_HV == 0:   ton_snub_final = tonsnubmin if ton_snub < tonsnubmin else ton_snub

            Ivec[Vvec.index(V_HV)] = Iref

        # Convert voltage vector to integer
        Vvec    = (np.array(Vvec).astype(int)).tolist()

        return Vvec, Ivec, ton_snub_final

    def dcdcAverageModelCalculate(self, ModelVars):
        """
        Calculate parameters for the average model of a DC-DC converter.

        This function extracts relevant parameters from the ModelVars dictionary
        and computes equivalent resistances, inductances, duty cycles, snubber
        components, and other derived quantities for the DC-DC converter average
        model, suitable for small-signal or simplified simulations.

        *Args    :
            ModelVars (dict): Dictionary containing all model parameters with keys for:
                - DCDC_Rail1: Information about the first DC-DC rail (MOSFETs, rectifiers, transformer, filter)
                - Common: Common parameters like PWM, control targets, and MCU settings

        !Returns:
            dict: Dictionary containing calculated average model parameters, including:
                - Resistances: Rds_on, Rds_ons, Rp, Rs, Rs2
                - Inductances: Lk (leakage), Lf (filter)
                - Duty cycle and timing: d, Tdead, Fs, Ts
                - Snubber components: Csnub, Rsnub, Csnubs, Rsnubs
                - Equivalent model coefficients: Ap2, A_dL, B_dL, C_dL, D_dL
                - Equivalent resistances for converter model: R_d, R_eq
                - Forward voltage of rectifier diode: Vd
        """

        # Extract MOSFET and rectifier resistances (divide by parallel count)
        Rds_on      = ModelVars['DCDC_Rail1']['LeftLeg_1']['Transistor']['Rds_on'] / ModelVars['DCDC_Rail1']['LeftLeg_1']['nParallel']
        Rds_ons     = ModelVars['DCDC_Rail1']['Rectifier_1']['Transistor']['Rds_on'] / ModelVars['DCDC_Rail1']['LeftLeg_1']['nParallel']

        # Transformer turns ratio and leakage inductance
        N_Tr        = ModelVars['DCDC_Rail1']['Trafo']['Np'] / ModelVars['DCDC_Rail1']['Trafo']['Ns']
        Lk          = ModelVars['DCDC_Rail1']['Trafo']['Lkp'] + ModelVars['DCDC_Rail1']['Trafo']['Lks'] * N_Tr**2

        # Filter inductance and resistance
        Lf          = ModelVars['DCDC_Rail1']['Lf']['L']
        DCR         = ModelVars['DCDC_Rail1']['Lf']['R']

        # Duty cycle, PWM deadtime, switching frequency/period
        d           = N_Tr * ModelVars['Common']['Control']['Targets']['Vout'] / ModelVars['DCDC_Rail1']['Control']['Inputs']['Vin']
        Tdead       = ModelVars['Common']['PWM']['Deadtimes_Rail_1']['S1']
        Fs          = ModelVars['Common']['MCU']['f_s']
        Ts          = ModelVars['Common']['MCU']['T_s']

        # Snubber capacitances and resistances
        Csnub       = ModelVars['DCDC_Rail1']['LeftLeg_1']['Coss']['C']
        Rsnub       = ModelVars['DCDC_Rail1']['LeftLeg_1']['Coss']['R']
        Csnubs      = ModelVars['DCDC_Rail1']['Rectifier_1']['Coss']['C']
        Rsnubs      = ModelVars['DCDC_Rail1']['Rectifier_1']['Coss']['R']

        # Equivalent series resistances
        Rp          = 2 * Rds_on
        Rs          = 2 * Rds_ons
        Rs2         = Rs + DCR

        # Assemble average model dictionary
        DCDC_Average = {
                            'Rds_on'  : Rds_on                                                       ,
                            'Rds_ons' : Rds_ons                                                      ,
                            'R_ss'    : 0                                                            ,
                            'N_Tr'    : N_Tr                                                         ,
                            'Lk'      : max(2e-6, Lk)                                                ,
                            'Lf'      : Lf                                                           ,
                            'DCR'     : DCR                                                          ,
                            'd'       : d                                                            ,
                            'Tdead'   : Tdead                                                        ,
                            'Fs'      : Fs                                                           ,
                            'Ts'      : Ts                                                           ,
                            'Csnub'   : Csnub                                                        ,
                            'Rsnub'   : Rsnub                                                        ,
                            'Csnubs'  : Csnubs                                                       ,
                            'Rsnubs'  : Rsnubs                                                       ,
                            'Rp'      : Rp                                                           ,
                            'Rs'      : Rs                                                           ,
                            'Rs2'     : Rs2                                                          ,
                            'Ap2'     : -(N_Tr/2*2*Rds_ons + 2*Rds_on) / Lk                          ,
                            'A_dL'    : Rp                                                           ,
                            'B_dL'    : Rs2 + Rp / N_Tr**2                                           ,
                            'C_dL'    : (Lf + Lk / N_Tr**2) * Lk / N_Tr                              ,
                            'D_dL'    : Lf + Lk / N_Tr**2                                            ,
                            'R_d'     : Rs * (0.5 + d/2 - Tdead * Fs) + DCR                          ,
                            'R_eq'    : Rs * (0.5 + d/2 - Tdead * Fs) + DCR                          ,
                            'Vd'      : ModelVars['DCDC_Rail1']['Rectifier_1']['BodyDiode']['Vf']
                        }


        return DCDC_Average

    #?-------------------------------------------------------------------------------------------------------------------------------------------------------------
    #? Battery cells data processing
    #?-------------------------------------------------------------------------------------------------------------------------------------------------------------

    def batteryParams(self, Path, Type):
        """
        This function processes battery data (e.g., voltage, SOC, current) provided as
        a table from a CSV. The data is reshaped into a MATLAB-style
        3D array to represent parameters as a function of current, state-of-charge (SOC),
        and temperature/time steps.

        *Args    :
            Path (str): Directory path containing the battery data file.
            Type (str): Filename or type identifier of the battery data.

        !Returns:
            tuple: Contains three elements:
                - current (list): List of unique battery currents (A) extracted from the first column.
                - cat (str): MATLAB-style 3D concatenation string for reconstructing 3D arrays.
                - Param (list): 3D list of battery parameters with shape (temp_length, curr_length, soc_length).
        """

       # Construct full file path
        Battery     = Path + Type

        # Extract arrays from the file using post-processing helper
        Data        = self.extractArrays(Battery)
        Data        = np.array(Data)

        # Transpose all columns except the first (currents)
        Data_T      = Data[1:].T

        # Identify unique current values from first column
        current     = (np.unique(Data[0])).tolist()
        temp_length = (Data[0].tolist()).count(Data[0][0])
        soc_length  = len(Data) - 1
        curr_length = len(current)
        curr_idx    = np.array(list(range(0, curr_length)))

        # Initialize empty 3D array and and MATLAB-style concatenation string
        LuT_3D      = np.empty((temp_length, curr_length, soc_length))

        # Populate 3D array and build concatenation string
        cat         = 'cat(3'
        for i in range(temp_length):
            indices             = i * curr_length + curr_idx
            LuT_3D[:][:][i]     = (Data_T[indices, :])
            cat                 = cat + ',' + 'LuT_3D' + '(:,:,' + str(i + 1) + ')'
        cat         = cat + ')'

        # Convert 3D array to list for output
        Param       = LuT_3D.tolist()

        return current, cat, Param

    def Battery_OCV(self, BatteryOCVPath, battery_state):
        """
        Extract battery open-circuit voltage (OCV) vs. state-of-charge (SOC) data.

        This function reads OCV data from  CSV files and
        organizes it into a list of voltage values and corresponding SOC points.
        Useful for battery modeling, SoC estimation, and DC-DC converter simulations.

        *Args    :
            BatteryOCVPath (str): Directory path containing the OCV data files.
            battery_state (str): Name identifier for the battery OCV dataset.

        !Returns:
            tuple: Contains two elements:
                - OCV (list): Open-circuit voltage values for each SOC point.
                - OCV_soc (list): Corresponding state-of-charge values (fraction or percentage).
        """

        # Construct full path to OCV data file
        Battery     = BatteryOCVPath + battery_state + '_OCV'

        # Extract arrays from the file using post-processing helper
        Data        = self.extractArrays(Battery)
        Data        = np.array(Data)

        # First column = SOC values
        OCV_soc     = np.unique(Data[0]).tolist()

        # Remaining columns = OCV values
        OCV         = np.array(Data[1:])
        OCV         = (OCV.T).tolist()  # Transpose so rows correspond to SOC points

        return OCV, OCV_soc

    #?-------------------------------------------------------------------------------------------------------------------------------------------------------------
    #? Lookup tables processing
    #?-------------------------------------------------------------------------------------------------------------------------------------------------------------

    def LuT3D_Generator(self, fileName, Xscale=1, Zscale=1, Zoffset=0):
        """
        This function reads tabular data from a file and reshapes it into a 3D array
        suitable for MATLAB-style 3D lookups. Scaling and offset options allow
        adjusting X-axis and Z-values for simulation or modeling purposes.

        *Args    :
            fileName (str): Path to the input data file.
            Xscale (float, optional): Scaling factor for X-axis values. Defaults to 1.
            Zscale (float, optional): Scaling factor for Z-values. Defaults to 1.
            Zoffset (float, optional): Offset for Z-values (applied before scaling). Defaults to 0.

        !Returns:
            tuple: Contains three elements:
                - X_axis (list): Unique X-axis values after scaling.
                - cat (str): MATLAB-style 3D concatenation string for reconstructing 3D arrays.
                - LuT_3D (list): 3D list of scaled Z-values with shape (Z_length, X_length, Y_length).
        """

        # Load the input file and convert to NumPy array
        inputFile       = fileName
        Data            = self.extractArrays(inputFile)
        Data            = np.array(Data)
        Data_T          = Data[1:].T

        # Unique X-axis values (scaled)
        X_axis          = ((np.unique(Data[0])) * Xscale).tolist()

        # Determine dimensions for 3D reshaping
        Z_length        = (Data[0].tolist()).count(Data[0][0])
        Y_length        = len(Data) - 1
        X_length        = len(X_axis)
        X_idx           = np.array(list(range(0, X_length)))

        # Initialize empty 3D array
        LuT_3D          = np.empty((Z_length, X_length, Y_length))

        # Fill 3D array with scaled and offset data
        cat             = 'cat(3'
        for i in range(Z_length):
            indices             = i * X_length + X_idx
            LuT_3D[:][:][i]     = (Data_T[indices, :] - Data[0][0] * Zoffset) * Zscale
            cat                 = cat + ',' + 'LuT_3D' + '(:,:,' + str(i + 1) + ')'
        cat             = cat + ')'

        # Convert NumPy array to Python list
        LuT_3D          = LuT_3D.tolist()

        return X_axis, cat, LuT_3D

    def LuT2D_Generator(self, fileName, Xscale=1, Fscale=1):
        """
        This function reads tabular data from a file and prepares X-axis values and
        corresponding function values, with optional scaling for both axes. Useful
        for control algorithms, interpolation, or MATLAB-style 2D lookups.

        *Args   :
            fileName    (str)               : Path to the input data file.
            Xscale      (float, optional)   : Scaling factor for X-axis values. Defaults to 1.
            Fscale      (float, optional)   : Scaling factor for function values (Y-axis). Defaults to 1.

        !Returns:
            tuple                           : Contains two elements:
                                                                    - Xvec (list): X-axis values after scaling.
                                                                    - Fvec (list): Corresponding function values after scaling and transposing.
        """

        # Load the input file and extract arrays
        inputFile       = fileName
        F_X_Vec         = self.extractArrays(inputFile)

        # Scale X-axis values
        Xvec            = (np.array(F_X_Vec[0]) * Xscale).tolist()

        # Extract and scale function values, transpose so each row corresponds to X
        Fvec            = np.array(F_X_Vec[1:])
        Fvec            = ((np.array(Fvec) * Fscale).T).tolist()

        return Xvec, Fvec

    def LuT1D_Generator(self, fileName, Xscale=1, Fscale=1):
        """
        This function reads tabular data from a file and prepares X-axis values and
        corresponding function values, with optional scaling for both axes. Useful
        for control algorithms, interpolation, or MATLAB-style 1D lookups.

        *Args   :
            fileName    (str)               : Path to the input data file.
            Xscale      (float, optional)   : Scaling factor for X-axis values. Defaults to 1.
            Fscale      (float, optional)   : Scaling factor for function values (Y-axis). Defaults to 1.

        !Returns:
            tuple                           : Contains two elements:
                                                                    - Xvec (list): X-axis values after scaling.
                                                                    - Fvec (list): Corresponding function values after scaling.
        """

        # Load the input file and extract arrays
        inputFile       = fileName
        F_X_Vec         = self.extractArrays(inputFile)

        # Scale X-axis values
        Xvec            = (np.array(F_X_Vec[0]) * Xscale).tolist()

        # Extract and scale function values
        Fvec            = np.array(F_X_Vec[1])
        Fvec            = (Fvec * Fscale).tolist()

        return Xvec, Fvec

    #?-------------------------------------------------------------------------------------------------------------------------------------------------------------
    #? Helper functions
    #?-------------------------------------------------------------------------------------------------------------------------------------------------------------

    def scaledList(self, arrayList, scale=1.0):
        """
        This function takes a list of arrays (or lists), multiplies each element
        by a given scaling factor, and returns the scaled list transposed.
        Useful for normalizing or converting units of multiple datasets at once.

        *Args   :
            arrayList       (list)              : List of arrays or lists to be scaled.
            scale           (float, optional)   : Scaling factor to apply. Defaults to 1.0.

        !Returns:
            list                                : List of scaled arrays, transposed.
        """

        # Convert all elements to lists for uniformity
        arrayList   = (np.array(arrayList)).tolist()

        # Scale each array or list
        for i in range(len(arrayList)):
            if isinstance(arrayList[i], np.ndarray):
                # If already a NumPy array, multiply directly and convert to list
                tempList        = (arrayList[i] * scale).tolist()
                arrayList[i]    = tempList

            else:
                # Convert list to NumPy array, scale, and convert back to list
                arrayList[i]    = (np.array(arrayList[i]) * scale).tolist()

        # Transpose the scaled list and return
        arrayList   = (np.array(arrayList)).T.tolist()

        return arrayList

    def limit_precision(self, nested_dict, precision):
        """
        Recursively limit the precision of numeric values in a nested dictionary or collection.

        This function traverses dictionaries, lists, tuples, and sets, truncating all numeric
        values to the specified number of significant digits. Non-numeric values are preserved
        as-is. Useful for logging, saving data, or formatting simulation results.

        *Args   :
            nested_dict     (dict)  : Dictionary to process (can be nested and contain lists/tuples/sets).
            precision       (int)   : Number of significant digits to keep.

        !Returns:
            dict                    : Dictionary (or nested collection) with numeric values truncated to the specified precision.
        """

        def truncate_value(value):
            """Truncate individual numeric value to the specified precision."""

            if isinstance(value, float):
                # Format float to specified significant digits
                return float(f"{value:.{precision}g}")

            elif isinstance(value, (int, complex)):
                # Leave integer and complex numbers as-is
                return value

            elif isinstance(value, str):
                try:
                    # Attempt to convert string to float and format
                    float_value = float(value)

                    return f"{float_value:.{precision}g}"

                except ValueError:
                    # Return original string if conversion fails
                    return value

            # Return non-numeric values as-is
            return value

        def traverse(obj):

            """Recursively traverse and truncate values in nested collections."""

            if isinstance(obj, dict):
                return {key: traverse(value) for key, value in obj.items()}
            elif isinstance(obj, list):
                return [traverse(item) for item in obj]
            elif isinstance(obj, tuple):
                return tuple(traverse(item) for item in obj)
            elif isinstance(obj, set):
                return {traverse(item) for item in obj}
            else:
                return truncate_value(obj)

        # Start recursive traversal
        return traverse(nested_dict)

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
        path                =   os.getcwd() + '/'
        data                =   np.loadtxt(path + fileName + '.csv' , delimiter=',')

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
        array   =   np.asarray(Data[Index])
        idx     =   np.nanargmin(np.abs(array - Point))

        return idx

    #?-------------------------------------------------------------------------------------------------------------------------------------------------------------
    #? Components parameters processing
    #?-------------------------------------------------------------------------------------------------------------------------------------------------------------

    def Netlist_path(self, netlistPath, componentName):
        """
        This function constructs the full path for components netlist file.

        *Args   :
            netlistPath     (str): Path to the folder containing the netlist file.
            componentName   (str): Name identifier for the component.

        !Returns:
            netlistpath (str)    : full file path pointing to the component netlist .lib file.
        """

        # Set the base path to the current working directory
        path            = os.getcwd() + '/'
        # Construct full file path
        netlistpath     = path + netlistPath + componentName + '.lib'
        return netlistpath

    def outputImpedanceMatching(self, path, device_name):
        """
        Perform impedance model fitting and return optimized circuit parameters.

        This function serves as the main high-level entry point for the complete
        impedance matching workflow. It loads the specified CSV file containing
        the device's impedance data (frequency, dB magnitude, and phase angle),
        performs hybrid optimization using a genetic algorithm followed by Nelder
        Mead refinement, and outputs the optimized RLC parameter set for the
        target circuit model    :

                    Z(s) = Rs + s*Ls + ((R1 + s*L1) || (R2 + 1/(s*C)))

        *Args   :
            path        (str)   : Folderpath to CSV file
            devicename  (str)   : Device file name

        """

        # Frequency band
        FMIN, FMAX          = 1e-1, 1e9
        N_POINTS            = 2000

        # GA params
        POP_SIZE            = 100
        N_GEN               = 100
        VERBOSE             = False

        # Hybrid NM params
        DO_NM               = True
        NM_MAX_ITER         = 3000

        # Parameter search space (low, high, log-scale)
        PARAM_SPACE         = [
                                (1e-4,  1e2,   True),   # Rs
                                (1e-12, 1e-3,  True),   # Ls
                                (1e-4,  2e2,   True),   # Rp1
                                (1e-12, 1e-3,  True),   # Lp1
                                (1e-4,  2e2,   True),   # Rp2
                                (1e-15, 1e-6,  True),   # Cp1
                            ]

        def build_freq_Z_from_lists(cols):
            """
            Convert frequency, dB, and degree lists into complex impedance values.

            This function takes a nested list containing three numeric lists:
            frequency values in Hz, magnitude values in dB, and phase values in
            degrees (angle), and converts them into two numpy arrays: a frequency
            array and a complex impedance array.

            The impedance is constructed as :   Z = 10^(dB/20) * exp(j * deg_in_radians)

            *Args   :
                cols (list of lists)        :   A nested list with exactly three sublists:
                                                    [
                                                        freq_list (list of float): Frequencies in Hz,
                                                        dB_list   (list of float): Magnitude in dB,
                                                        deg_list  (list of float): Phase in degrees
                                                    ]
                                                    Example:
                                                        [
                                                            [1, 4, 7],
                                                            [2, 5, 8],
                                                            [3, 6, 9]
                                                        ]
            !Returns:
                tuple                       :   freq (ndarray): 1D numpy array of frequencies in Hz.
                                                Z    (ndarray): 1D numpy array of complex impedance values computed from the magnitude and phase data.
            """

            freq_list, dB_list, deg_list    = cols
            freq                            = np.asarray(freq_list, dtype=float)
            dB                              = np.asarray(dB_list,   dtype=float)
            deg                             = np.asarray(deg_list,  dtype=float)

            # Convert dB/deg -> complex Z
            mag                             = 10.0 ** (dB / 20.0)
            Z                               = mag * np.exp(1j * np.deg2rad(deg))
            return freq, Z

        # Construct full path to CSV
        full_path               = path + device_name

        # Extract data
        freqs, dBs, degs        = self.extractArrays(full_path)
        freq, Z                 = build_freq_Z_from_lists([freqs, dBs, degs])

        # Selection
        freq_sel, Z_sel         = po.select_and_decimate(freq, Z, FMIN, FMAX, N_POINTS)
        s                       = 1j*2*np.pi*freq_sel

        problem                 = po.ImpedanceProblem(s, Z_sel, PARAM_SPACE)
        algorithm               = GA(pop_size=POP_SIZE, eliminate_duplicates=True)
        termination             = get_termination("n_gen", N_GEN)

        result_ga               = optmin(problem, algorithm, termination, verbose=VERBOSE)

        x_best                  = result_ga.X
        params_ga               = po.decode_params(x_best, PARAM_SPACE)

        # NELDER–MEAD REFINEMENT
        if DO_NM:

            def nm_objective(p):
                """
                _summary_

                *Args   :
                    p (_type_)  : _description_

                !Returns:
                    _type_      : _description_
                """
                return po.loss_combined(p, s, Z_sel, po.W_Z, po.W_Y, po.W_DB, po.W_PHASE, po.W_REL)

            p0                  = np.maximum(params_ga, po.POS_FLOOR)
            params_nm, nm_err   = po.nelder_mead(nm_objective, p0, max_iter=NM_MAX_ITER)

            #po.plot_impedance(freq_sel, Z_sel, params_nm, title="Hybrid(GA→NM)")
        return params_nm

#?-------------------------------------------------------------------------------------------------------------------------------------------------------------