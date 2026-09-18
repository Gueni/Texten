
#?-------------------------------------------------------------------------------------------------------------------------------------------------------------
#?												  ____  _     _____ ____ ____    __  __                   _
#?												 |  _ \| |   | ____/ ___/ ___|  |  \/  | __ _ _ __  _ __ (_)_ __   __ _
#?												 | |_) | |   |  _|| |   \___ \  | |\/| |/ _` | '_ \| '_ \| | '_ \ / _` |
#?												 |  __/| |___| |__| |___ ___) | | |  | | (_| | |_) | |_) | | | | | (_| |
#?												 |_|   |_____|_____\____|____/  |_|  |_|\__,_| .__/| .__/|_|_| |_|\__, |
#?												                                             |_|   |_|            |___/
#?-------------------------------------------------------------------------------------------------------------------------------------------------------------
import assets.Dependencies as dp


#?-------------------------------------------------------------------------------------------------------------------------------------------------------------
# Mode of operation used in miscellaneous lib to define the mode of operation (nanmax , absolute , mean ...) & the names of the corresponding matrices
Maps_index 			= {
                            'Standalone_data_mat' 	:   [

                                                            [4,5,1,6,9,10,11],
                                                            [-600,-600,-600,-600,-600,-600,-600,-600]
                                                        ] ,
							'Standalone_map_names'	:   [
                                                            "RMS", "AVG", "MAX", "MIN", "P2P" , "FIRST", "LAST", "FFT"
                                                        ],
                            #?--------------------------------------------------------------------------------------------------------------------------------
                            'DCDC_data_mat' 	    :   [
                                                            [1,4,5,1,4,5,1,1,1,5,5,1,1,9,9,10,11,10,11],
                                                            [-600,-600,-600,-600,-600,-600,-600,-600,-600,-600,-600,-600,-600,-600,-600,-600,-600,-600,-600]
                                                        ] ,
							'DCDC_map_names'	    :   [
                                                            "Peak_Currents", "RMS_Currents", "AVG_Currents", "Peak_Voltages" , "RMS_Voltages" , "AVG_Voltages",
                                                            "FFT_Current"  , "FFT_Voltage" , "Dissipations", "Elec_Stats"    , "Temps"        , "Thermal_Stats",
                                                            "Controls"     , "P2P_Currents", "P2P_Voltages", "FIRST_Currents", "LAST_Currents", "FIRST_Voltages",
                                                            "LAST_Voltages"
                                                        ]
						}

# Lambda function to delete multiple segments at once from any given list like raw mapping
delete_segments     = lambda arr, seglen, segdel: dp.np.delete(dp.np.array(arr),dp.np.hstack([dp.np.r_[dp.np.cumsum([0]+seglen[:-1])[i] : dp.np.cumsum([0]+seglen[:-1])[i] + seglen[i]] for i in segdel])).tolist()
#?-------------------------------------------------------------------------------------------------------------------------------------------------------------
def gen_pmap_plt(Ctrl_plt,pmap_plt):
    """
    Generates plots mapping dictionaries for the html report.

    Args:
        Ctrl_plt (list): list of controller mappings
        pmap_plt (list): list of mappings
    """
    pmap_plt_dict , pmap_plt_ctrl_dict	=	dp.collections.OrderedDict(),dp.collections.OrderedDict()

    match dp.JSON['model']:
        case 'DCDC_S':
            for i in range(1,len(Ctrl_plt)):	#? controls scopes
                pmap_plt_ctrl_dict[f'{Ctrl_plt[0][i-1]}']	=	[	[
	                                                    					Ctrl_plt[i][j][1],
																			[f"{str(Ctrl_plt[i][j][0])} ({', '.join(str(item) for item in [str(dp.pmapping[f'{Ctrl_plt[i][j][1][k]}']) for k in range(len(Ctrl_plt[i][j][1]))])})"]				,
                  															[dp.pmapping[f'{Ctrl_plt[i][j][1][k]}'] for k in range(len(Ctrl_plt[i][j][1]))],
																			Ctrl_plt[i][j][2]*len(Ctrl_plt[i][j][1])

                  														]	for j in range(len(Ctrl_plt[i]))
                                                      				]
            for i in range(len(pmap_plt)) :
                pmap_plt_dict[f'{pmap_plt[i][0]}'] = [
																[	[f'{pmap_plt[i][1]}' ],
																	[f'{pmap_plt[i][0]}'+  " Current" +'(' + str(dp.pmapping[f'{pmap_plt[i][1]}']+1) + ')'],
																	[dp.pmapping[f'{pmap_plt[i][1]}']],
																	['[ A ]']
																],
																[	[f'{pmap_plt[i][2]}' ],
																	[f'{pmap_plt[i][0]}'+  " Voltage" +'(' + str(dp.pmapping[f'{pmap_plt[i][2]}']+1) + ')'],
																	[dp.pmapping[f'{pmap_plt[i][2]}']],
																	['[ V ]']
																]
																]
		#------------------------------------------------------------------------------------------------------------------------------------------------------------------
        case 'DCDC_D':
            for i in range(1,len(Ctrl_plt)):	#? controls scopes
                pmap_plt_ctrl_dict[f'{Ctrl_plt[0][i-1]}']	=	[	[
	                                                    					Ctrl_plt[i][j][1],
																			[f"{str(Ctrl_plt[i][j][0])} ({', '.join(str(item) for item in [str(dp.pmapping[f'{Ctrl_plt[i][j][1][k]}']) for k in range(len(Ctrl_plt[i][j][1]))])})"]				,
                  															[dp.pmapping[f'{Ctrl_plt[i][j][1][k]}'] for k in range(len(Ctrl_plt[i][j][1]))],
																			Ctrl_plt[i][j][2]*len(Ctrl_plt[i][j][1])

                  														]	for j in range(len(Ctrl_plt[i]))
                                                      				]

            for i in range(len(pmap_plt)) :
                if len(pmap_plt[i])==5:
                    pmap_plt_dict[f'{pmap_plt[i][0]}'] = [
															[	[f'{pmap_plt[i][1]}',f'{pmap_plt[i][2]}' ],
																[f'{pmap_plt[i][0]}'+  " Current" +'(' + str(dp.pmapping[f'{pmap_plt[i][1]}']+1) + ')' +
                 													 '(' + str(dp.pmapping[f'{pmap_plt[i][2]}']+1) + ')'],
																[dp.pmapping[f'{pmap_plt[i][1]}'],dp.pmapping[f'{pmap_plt[i][2]}']],
																['[ A ]','[ A ]']
															],
															[	[f'{pmap_plt[i][3]}',f'{pmap_plt[i][4]}' ],
																[f'{pmap_plt[i][0]}'+  " Voltage" +'(' + str(dp.pmapping[f'{pmap_plt[i][3]}']+1) + ')' +
                 													 '(' + str(dp.pmapping[f'{pmap_plt[i][4]}']+1) + ')'],
																[dp.pmapping[f'{pmap_plt[i][3]}'],dp.pmapping[f'{pmap_plt[i][4]}']],
																['[ V ]','[ V ]']
															]


															]
                else:
                        pmap_plt_dict[f'{pmap_plt[i][0]}'] = [
																[	[f'{pmap_plt[i][1]}'],
																	[f'{pmap_plt[i][0]}'+  " Current" +'(' + str(dp.pmapping[f'{pmap_plt[i][1]}']+1) + ')'],
																	[dp.pmapping[f'{pmap_plt[i][1]}']],
																	['[ A ]']
																],
																[	[f'{pmap_plt[i][2]}'],
																	[f'{pmap_plt[i][0]}'+  " Voltage" +'(' + str(dp.pmapping[f'{pmap_plt[i][2]}']+1) + ')'],
																	[dp.pmapping[f'{pmap_plt[i][2]}']],
																	['[ V ]']
																],


																]
        #------------------------------------------------------------------------------------------------------------------------------------------------------------------
        case _:				# Default Case
            print("ModelVar Value Error : dp.Config Value Error !")
            dp.sys.exit()
        #------------------------------------------------------------------------------------------------------------------------------------------------------------------
    return	pmap_plt_dict,pmap_plt_ctrl_dict

def return_resistances(op_dict):
    """
    Return a list of resistances based on the configuration specified in op_dict.

    Calculates equivalent resistances for all components in the power converter
    considering series/parallel combinations and scaling factors.

    Args:
        op_dict (dict): Dictionary containing model variables and configuration.

    Returns:
        np.ndarray: Array of resistance values for all components in the system.

    Raises:
        SystemExit: If an invalid configuration is specified
    """

	# Extract model variables dictionary
    model_vars 			= op_dict['ModelVars']
    rail1 				= model_vars['DCDC_Rail1']
    common 				= model_vars['Common']

    # Extract component groups for easier access
    RCsnubber 			= rail1['RCsnubber']
    clamp 				= rail1['RCDclamp1']
    freewheeler 		= rail1['FRW']

    # Helper function to calculate capacitor equivalent resistance
    cap_resistance 		= lambda cap_config: cap_config['Rsingle'] * (cap_config['nSer'] / cap_config['nPar'])
    resistor_network 	= lambda res_config: res_config['R'] / res_config.get('nPar', 1)

    match dp.JSON['model']:
        case 'DCDC_S':  # Single DC-DC Converter
            dp.Resistances = [
                # Current Transformer
                rail1['CT']['Trafo']['Rpri'],           				# CT Primary winding resistance
                rail1['CT']['Trafo']['Rsec'],           				# CT Secondary winding resistance

                # Choke Snubber Network
                cap_resistance(RCsnubber['Choke']['Cs']),     			# Choke snubber capacitor ESR
                resistor_network(RCsnubber['Choke']['Rs']),   			# Choke snubber resistor
                RCsnubber['Choke']['Rpar'],                   			# Choke snubber parallel resistor

                # RCD Clamp Network
                cap_resistance(clamp['Cs']),            				# Clamp capacitor ESR
                float(clamp['Rs']['R']),                				# Clamp resistor (single)

                # Freewheeling Diode Network
                cap_resistance(freewheeler['BlockingCap']), 			# Freewheeler blocking cap ESR
                freewheeler['Resistor']['R'],               			# Freewheeler resistor
                cap_resistance(freewheeler['ImpedanceCap']),			# Freewheeler impedance cap ESR

                # Damping and Sensing
                rail1['Coe1']['Rd'],                    				# Damping resistor
                rail1['LV_currentSense']['R'],          				# LV current sense resistor

                # HV Side Capacitors
                cap_resistance(rail1['Cpi']),           				# HV X-cap 1 ESR
                cap_resistance(rail1['Cin']),           				# HV X-cap 2 ESR
                rail1['HV_currentSense']['R'],          				# HV current sense resistor
                cap_resistance(rail1['Cb']),            				# Blocking capacitor ESR

                # Transformer Snubber
                cap_resistance(RCsnubber['Trafo']['Cs']), 				# Transformer snubber cap ESR
                resistor_network(RCsnubber['Trafo']['Rs']), 			# Transformer snubber resistor

                # MOSFET Snubbers (4 devices)
                4 * cap_resistance(RCsnubber['SR_MOSFET']['Cs']),     	# MOSFET snubber cap ESR
                4 * resistor_network(RCsnubber['SR_MOSFET']['Rs']),   	# MOSFET snubber resistor

                # HV Y-Caps (4 capacitors)
                4 * cap_resistance(rail1['Cyi']),       				# HV Y-cap ESR

                # LV Full Bridge Snubbers (2 bridges)
                2 * cap_resistance(RCsnubber['LV_FB']['Cs']),     		# LV FB snubber cap ESR
                2 * resistor_network(RCsnubber['LV_FB']['Rs']),   		# LV FB snubber resistor

                # HV Snubber Caps (2 capacitors)
                2 * cap_resistance(rail1['Cc']),        				# HV snubber cap ESR

                # Output Capacitors
                cap_resistance(rail1['Co']),            				# Output ceramic cap ESR
                cap_resistance(rail1['Coe1']),          				# Output electrolytic cap ESR
                4 * cap_resistance(rail1['Cyo']),       				# Output Y-cap ESR (4 capacitors)

                # Voltage Sensing
                (rail1['HV_voltageSense']['Divider']['R1'] +
                 rail1['HV_voltageSense']['Divider']['R2']), 			# HV voltage divider total resistance

                # HV Common Mode Choke (2 windings)
                2 * rail1['HVcmc']['Rwind'],            				# HV CMC winding resistance

                # Common Components (LV Filter)
                cap_resistance(common['Coc1']),         				# LV Filter X-cap 1 ESR
                cap_resistance(common['Coc2']),         				# LV Filter X-cap 2 ESR
                cap_resistance(common['Coec2']),        				# LV Filter electrolytic cap ESR
                4 * cap_resistance(common['Cyoc']),     				# LV Filter Y-cap ESR (4 capacitors)
                2 * common['LVdmc']['Rwind'],           				# LV DMC winding resistance (2 windings)
                2 * common['LVcmc']['Rwind'],           				# LV CMC winding resistance (2 windings)

                # Busbar Resistances
                common['Busbars_PCB']['LV_Filter']['PlusResistance'],   # Positive busbar resistance
                common['Busbars_PCB']['LV_Filter']['MinusResistance']   # Negative busbar resistance
            ]

        case 'DCDC_D':  # Dual DC-DC Converter
            dp.Resistances = []  # To be implemented

        case _:  # Invalid configuration
            print("Resistances Value Error : Resistances Value Error!")
            dp.sys.exit()

    return dp.np.array(dp.Resistances)

def tofile_map_gen(mapping_Raw, lengths):
    """
        Generate mapping dicts.

        Args:
            mapping_Raw (dict)  : raw mapping dictionary.
            lengths     (list)  : list of lengths of segments.

        Returns:        (dict)  : orderedDict of mapping.
    """
    # c: segment counter, idx_shift: starting index for multiple mapping
    c, idx_shift 			= 0, 1

    # Names for each mapping segment
    Maps_names 				= ["Peak_Currents", "Peak_Voltages", "Dissipations", "Elec_Stats", "Temps", "Thermal_Stats", "Controls"]

	# Initialize ordered dictionaries for mappings
    Tofile_mapping_multiple = dp.collections.OrderedDict()

    for i in range(1, len(lengths)):
		# Extract segment from raw mapping data
        segment 									= dp.copy.deepcopy(mapping_Raw[c + 1:lengths[i] + c + 1])

        # Create mapping with continuous indexing for multiple dictionary
        Tofile_mapping_multiple[Maps_names[i - 1]] 	= dp.collections.OrderedDict(zip(segment, range(idx_shift, len(segment) + idx_shift)))

		# Update counters for next segment
        c 			+= lengths[i]
        idx_shift	+= lengths[i]

    return Tofile_mapping_multiple

def dump_headers(raw_dict, names,Ycumsum,YLcumsum,segments,segments_idx):
    """
    Process and dump header information to JSON files.

    This function processes raw header data, applies various transformations,
    and saves the results to multiple JSON files organized by data categories.

    Args:
        raw_dict: Dictionary containing raw header data
        names   : Identifier used to lookup file naming conventions in Maps_index
    """
    # Initialize counter for tracking position in processed data
	# and lambda function for appending suffixes
    c 				= 0
    add_str 		= lambda lst, s: [x + s for x in lst]

    # Implicitly make a copy of raw mapping and remove segments
    ts_header       = delete_segments(raw_dict, segments,segments_idx)

    # Save the processed time series header to file with each element on new line
    with open(dp.Header_File, 'w') as f:
        f.write('[\n')
        for i, item in enumerate(ts_header):
            dp.json.dump(item, f)
            if i < len(ts_header) - 1:
                f.write(',')
            f.write('\n')
        f.write(']')

    # Define slices for different data categories with corresponding suffixes
    slices 			= [
    				slice(1, dp.Y_list[1]+1)		,	# rms   current
    				slice(1, dp.Y_list[1]+1)		,	# avg   current
    				slice(Ycumsum[1], Ycumsum[2])	,	# rms   voltage
    				slice(Ycumsum[1], Ycumsum[2])	,	# avg   voltage
    				slice(1, dp.Y_list[1]+1)		,	# fft   current
    				slice(Ycumsum[1], Ycumsum[2])	,	# fft   voltage
    				slice(1, dp.Y_list[1]+1)		,	# P2P   current
    				slice(Ycumsum[1], Ycumsum[2])   ,	# P2P   voltage
    				slice(1, dp.Y_list[1]+1)		,	# FIRST current
    				slice(1, dp.Y_list[1]+1)	    ,   # LAST  current
    				slice(Ycumsum[1], Ycumsum[2])	,	# FIRST voltage
    				slice(Ycumsum[1], Ycumsum[2])		# LAST  voltage
    			]
    suffixes 		= [' RMS', ' AVG', ' RMS', ' AVG', ' FFT', ' FFT', ' P2P', ' P2P', ' FIRST', ' LAST', ' FIRST', ' LAST']

    # Get lengths for each segment from cumulative Y_Length values
    # exp:                     [77,77,69,69,77,69,77,69,77,77,69,69]
    lengths 		= YLcumsum[[ 1, 2, 4, 5, 6, 7,13,14,15,16,17,18,19]].tolist()

    # Process each segment: add suffix and pair with insertion length
    sublists 		= [(add_str(raw_dict[s], suf), l) for s, suf, l in zip(slices, suffixes, lengths)]

	# Build temporary dictionary by inserting processed segments at specified positions
    temp_raw_dict 	= dp.functools.reduce(lambda acc, x: dp.np.insert(acc, x[1], dp.np.array(x[0])), sublists, dp.copy.copy(dp.np.array(raw_dict))).tolist()

    # Save each data category to separate JSON files with each element on new line
    for i, length in enumerate(dp.Y_Length[1:], 1):
        # Generate filename based on mapping index
        header_file = f"Script/assets/Headers/{Maps_index[names][i-1]}.json"

		# Write segment data to file as a list with each element on new line
        with open(header_file, 'w') as file:
            file.write('[\n')
            segment_data = temp_raw_dict[c+1:c+1+length]
            for j, item in enumerate(segment_data):
                file.write('  ')
                dp.json.dump(item, file)
                if j < len(segment_data) - 1:
                    file.write(',')
                file.write('\n')
            file.write(']')
        c += length

def select_mapping():
    """
       This function selects the appropriate mapping based on the 'model' value and performs the necessary setup.

       Select Plecs mapping based on the value of the 'model' field in the JSON configuration.

    """
    # initialize mapping parameters
    if dp.JSON["model"] == 'DCDC_S' or dp.JSON['model'] == 'DCDC_D':
        dp.mode      = dp.pmap.Maps_index['DCDC_data_mat'][0]
        dp.map_index = dp.pmap.Maps_index['DCDC_data_mat'][1]
        dp.map_names = dp.pmap.Maps_index['DCDC_map_names']

    elif not dp.JSON["model"]: #standalone case
        dp.mode      = dp.pmap.Maps_index['Standalone_data_mat'][0]
        dp.map_index = dp.pmap.Maps_index['Standalone_data_mat'][1]
        dp.map_names = dp.pmap.Maps_index['Standalone_map_names']

    else:
        raise NameError(dp.JSON['model'])

    # define lambda local function for fetching and loading json files for raw mappings
    load_json        = lambda subdir, name: dp.json.load(open(f"{dp.pathlib.Path.cwd()}/Script/assets/Mapping/{subdir}/{name}"))

    match dp.JSON['model']:
        case 'DCDC_S'	:

            # the actual data lengths in the original raw mapping inside the json example : SIGNAL_MAPPING\DCDC_S\pmap_Raw.json
            dp.segments                    = [1,77,69,62,15,18,8,167]

            # Get Single DC-DC Converter raw Mappings
            DCDC_pmap_Raw               = load_json("DCDC_S"	, "pmap_Raw.json")
            DCDC_pmap_plt               = load_json("DCDC_S"	, "pmap_plt.json")
            DCDC_Constants              = load_json("DCDC_S"	, "Constants.json")
            DCDC_Ctrl_plt               = load_json("DCDC_S"	, "Ctrl_plt.json")

            # Lengths related to all exported and calculated data (Y_Length) and Lengths related to plecs output only (Y_list).
            dp.Y_Length            		=  [1,77,77,77,69,69,69,77,69,62,15,18,8,167,77,69,77,77,69,69]
            dp.Y_list              		=  [1,77,69,25,15,18,167]

            # Calculate cumulative sums for data partitioning
            Ycumsum     		        = dp.np.cumsum(dp.Y_list)
            dp.Ycumsum                  = Ycumsum
            YLcumsum    		        = dp.np.cumsum(dp.Y_Length)
            dp.YLcumsum                 = YLcumsum

            # Output power Index in Electstat maps.
            dp.Pout_idx            		=  13
            dp.Rail_idx            		=  15
            dp.Common_idx          		=  53

            # Number of phases : single , dual ...
            dp.phase               		=  2

			# Index up to which all currents related to resistive loads
            dp.current_idx         		=  37

            # Number of columns of commun data (exp : LV filter)
            dp.com_cols            		=  6

			# Generate json header files.
            dump_headers(DCDC_pmap_Raw,'DCDC_map_names',Ycumsum,YLcumsum,dp.segments, [3, 6])

            # delete segments of data from raw mapping : 3=> 62 dissipations , 6 => 8 thermals
            DCDC_pmap_Raw               = delete_segments(DCDC_pmap_Raw, dp.segments, [3, 6])

			# Generate DCDC mapping dicts normal mapping and multiplots mapping.
            dp.pmapping 				= dp.collections.OrderedDict(zip(DCDC_pmap_Raw, range(0, len(DCDC_pmap_Raw))))
            dp.pmap_multi	            = tofile_map_gen(DCDC_pmap_Raw,dp.Y_list)

			# Generate PWM dictionary from specific slice of the mapping
            pwm_slice 					= DCDC_pmap_Raw[DCDC_pmap_Raw.index("PWM Modulator Primary PWM Outputs S1"):DCDC_pmap_Raw.index("PWM Modulator Auxiliary PWM Outputs Sdis")]
            dp.pwm_dict 				= dp.collections.OrderedDict(zip(pwm_slice, map(DCDC_pmap_Raw.index, pwm_slice)))

			# Generate html plots mapping dict & ctrls mapping.
            dp.pmap_plt,dp.pmap_plt_ctrl= gen_pmap_plt(DCDC_Ctrl_plt, DCDC_pmap_plt)

			# Generate constants dictionary
            dp.constant_dict 			= dp.collections.OrderedDict((sub[0], [sub[0], dp.pmapping[sub[0]], sub[1]]) for sub in DCDC_Constants)

			# Set plot title list and index range for..
            dp.plt_title_list  			= DCDC_pmap_plt
    #------------------------------------------------------------------------------------------------------------------------------------------------------------------
        case 'DCDC_D' 	:	#? Assign dual rail mapping

            # the actual data lengths in the original raw mapping
            dp.segments            = [1,136,120,1,17,1,1,327]

            # Get Dual DC-DC Converter Mappings
            DCDC_DUAL_pmap_Raw  = load_json("DCDC_D"		, "pmap_Raw.json")
            DCDC_DUAL_pmap_plt  = load_json("DCDC_D"		, "pmap_plt.json")
            DCDC_DUAL_Constants = load_json("DCDC_D"		, "Constants.json")
            DCDC_DUAL_Ctrl_plt  = load_json("DCDC_D"		, "Ctrl_plt.json")
			# Lengths related to all exported and calculated data and Lengths related to plecs output only.
            dp.Y_Length            		=  [1,136,136,136,120,120,120,136,120,1,17,1,1,327,136,120,136,136,120,120]

            dp.Y_list              		=  [1,136,120,1,17,1,327]

            # Calculate cumulative sums for data partitioning
            Ycumsum     		        = dp.np.cumsum(dp.Y_list)
            dp.Ycumsum                  = Ycumsum
            YLcumsum    		        = dp.np.cumsum(dp.Y_Length)
            dp.YLcumsum                 = YLcumsum

			# Output power Index in Electstat maps.
            dp.Pout_idx            		=  0
            dp.Rail_idx            		=  0
            dp.Common_idx          		=  0

            # Number of phases : single , dual ...
            dp.phase               		=  2

			# Index up to which all currents related to resistive loads.
            dp.current_idx         		=  0

            # Number of columns of commun data (exp : LV filter).
            dp.com_cols            		=  0

			# Generate json header files.
            dump_headers(DCDC_DUAL_pmap_Raw,'DCDC_map_names',Ycumsum,YLcumsum,dp.segments, [3,6])

            # delete segments of data from raw mapping : 3=> 1 dissipations , 6 => 1 thermals
            DCDC_DUAL_pmap_Raw = delete_segments(DCDC_DUAL_pmap_Raw, dp.segments, [3,6])

			# Generate DCDC mapping dicts both for 3D and multiple plots.
            dp.pmapping 				= dp.collections.OrderedDict(zip(DCDC_DUAL_pmap_Raw, range(0, len(DCDC_DUAL_pmap_Raw))))
            dp.pmap_multi	            = tofile_map_gen(DCDC_DUAL_pmap_Raw,dp.Y_list)

			# Generate PWM dictionary from specific slice of the mapping
            pwm_slice 					= DCDC_DUAL_pmap_Raw[DCDC_DUAL_pmap_Raw.index("PWM Modulator Carrier Waveforms 1 Rail 1"):DCDC_DUAL_pmap_Raw.index("PWM Modulator Auxiliary PWM Outputs Sdis Rail 2")]
            dp.pwm_dict 				= dp.collections.OrderedDict(zip(pwm_slice, map(DCDC_DUAL_pmap_Raw.index, pwm_slice)))

			# Generate DCDC html plots mapping dict & ctrls mapping.
            dp.pmap_plt,dp.pmap_plt_ctrl= gen_pmap_plt(DCDC_DUAL_Ctrl_plt, DCDC_DUAL_pmap_plt)

			# Generate constant dictionary
            dp.constant_dict 			= dp.collections.OrderedDict((sub[0], [sub[0], dp.pmapping[sub[0]], sub[1]]) for sub in DCDC_DUAL_Constants)

			# Set plot title list and index range for
            dp.plt_title_list  			= DCDC_DUAL_pmap_plt

		#------------------------------------------------------------------------------------------------------------------------------------------------------------------
        case '':
            pass
		#------------------------------------------------------------------------------------------------------------------------------------------------------------------
        case _			:	#? Default Case
            print("ModelVar Value Error : model Value Error ! ")
            dp.sys.exit()
#?-------------------------------------------------------------------------------------------------------------------------------------------------------------