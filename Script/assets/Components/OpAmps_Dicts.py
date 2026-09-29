
#?----------------------------------------------------------------------------------------------------------------------------------------------------------------------
#?						  ___          _                          ____                                _
#?						 / _ \ _ __   / \   _ __ ___  _ __  ___  |  _ \ __ _ _ __ __ _ _ __ ___   ___| |_ ___ _ __ ___
#?						| | | | '_ \ / _ \ | '_ ` _ \| '_ \/ __| | |_) / _` | '__/ _` | '_ ` _ \ / _ \ __/ _ \ '__/ __|
#?						| |_| | |_) / ___ \| | | | | | |_) \__ \ |  __/ (_| | | | (_| | | | | | |  __/ ||  __/ |  \__ \
#?						 \___/| .__/_/   \_\_| |_| |_| .__/|___/ |_|   \__,_|_|  \__,_|_| |_| |_|\___|\__\___|_|  |___/
#?						      |_|                    |_|
#?----------------------------------------------------------------------------------------------------------------------------------------------------------------------
#!----------------------------------------------------------------------------------------------------------------------------------------------------------------------
#!   This Script works as a Parameter dictionary for the plecs opamps models.
#!   Do not modify the values in this file.
#!----------------------------------------------------------------------------------------------------------------------------------------------------------------------
#?----------------------------------------------------------------------------------------------------------------------------------------------------------------------
import  Lib.Param_Process           as        PM
#?----------------------------------------------------------------------------------------------------------------------------------------------------------------------

#! Call the Params-Processing class and point to the location of csv data
paramProcess		=	PM.ParamProcess()
opampImpedancePath  =   'Script/Data/OpAmp_Impedance/'
opampsNetlistPath   =	'Script/Data/Netlists/OpAmps/'

#! OpAmps models parameters
#?----------------------------------------------------------------------------------------------------------------------------------------------------------------------

# impedanceParam      =   paramProcess.outputImpedanceMatching(opampImpedancePath, 'Ideal')

Ideal				=	{																																	#*	ideal opamp model
							'Config'				: 	2																								,	#?	1->non ideal | 2->ideal/netlist
                            'Type'                  :   2                                                                                               ,   #?  1->limited outout | 2->unlimited output | 3->spice netlist
							'Gain'					: 	1e6																								,	#?	open-loop gain in V/V
							'BW'					: 	'inf'																							,	#?	open-loop bandwidth in Hz
							'Vcc'					: 	3																								,	#?	positive rail supply voltage
                            'Vee'					: 	0																								,	#?	negative rail supply voltage
                            'Rin'					:	'inf'																							,	#?	differential input resistance
                            'Cin'					:	0																								,	#?	differential input capacitance
                            'Ibp'                   :   0                                                                                               ,   #?  non-inverting input bias current
                            'Ibn'                   :   0                                                                                               ,   #?  inverting input bias current
                            'Rin_Pos'				:	'inf'																							,	#?	non-inverting input resistance
                            'Rin_Neg'				:	'inf'																							,	#?	inverting input resistance
                            'Cin_Pos'				:	0																								,	#?	non-inverting input capacitance
                            'Cin_Neg'				:	0																								,	#?	inverting input capacitance
                            'Ileak'					:	0   																							,	#?	output leakage current
                            'Ro'					:	0																								,	#?	output resistance
                            'Co'					:	0																								,	#?	output capacitance
                            'Zo'       :   {                                                                                                                #!  complex output impedance model
                                'Config'            :   3                                                                                               ,   #?  type of impedance network, 1->Network 1 | 2->Network 2 | 3->disable
                                'Network1'  :   {                                                                                                           #*  parameters of network 1
                                    'R1'                :   0                                                                                           ,   #?  first resistance
                                    'RL1'               :   0                                                                                           ,   #?  series resistance of first inductor
                                    'L1'                :   0                                                                                           ,   #?  first inductance
                                    'R2'                :   0                                                                                           ,   #?  second resistance
                                    'RL2'               :   0                                                                                           ,   #?  series resistance of second inductor
                                    'L2'                :   0                                                                                           ,   #?  first inductance
                                    'R3'                :   0                                                                                           ,   #?  third resistance
                                    'R4'                :   0                                                                                           ,   #?  fourth resistance
                                    'C1'                :   0                                                                                           ,   #?  first capacitance
                                },
                                'Network2'  :   {                                                                                                           #*  parameters of network 2
                                    'Rs'                :   0                                                                                           ,   #?  serial resistance
                                    'Ls'                :   0                                                                                           ,   #?  serial inductance
                                    'Rp1'               :   0                                                                                           ,   #?  parallel resistance 1
                                    'Lp1'               :   0                                                                                           ,   #?  parallel inductance
                                    'Rp2'               :   0                                                                                           ,   #?  parallel resistance 2
                                    'Cp1'               :   0                                                                                           ,   #?  parallel capacitance
                                    },
                            },
                            'Netlist'       :   {                                                                                                           #!  SPICE netlist parameters
                                    'File'              :   ''                                                                                          ,   #?  netlist file directory location
                                    'Type'              :   1                                                                                           ,   #?  description type, 1->.subckt | 2->.model
                                    'Name'              :   ''                                                                                              #?  spice model name as it appears in the netlist file
                            },
                            'Vos'                   :   0                                                                                               ,   #?  opamp input offset voltage
                            'Delay'					:	0																									#?	input-to-output deadtime delay
						}

#?----------------------------------------------------------------------------------------------------------------------------------------------------------------------

# impedanceParam      =   paramProcess.outputImpedanceMatching(opampImpedancePath, 'TLV316')
netlistpath		    =	paramProcess.Netlist_path(opampsNetlistPath, 'TLV316')

TLV316				=	{																																	#*	TLV316 opamp model
							'Config'				: 	2																								,	#?	1->non ideal | 2->ideal/netlist
                            'Type'                  :   2                                                                                               ,   #?  1->limited outout | 2->unlimited output | 3->spice netlist
							'Gain'					: 	10**(110.881/20)																				,	#?	open-loop gain in V/V
							'BW'					: 	32.0076																							,	#?	open-loop bandwidth in Hz
							'Vcc'					: 	3																								,	#?	positive rail supply voltage
                            'Vee'					: 	0																								,	#?	negative rail supply voltage
                            'Rin'					:	2e16																							,	#?	differential input resistance
                            'Cin'					:	2e-12																							,	#?	differential input capacitance
                            'Ibp'                   :   10e-12                                                                                          ,   #?  non-inverting input bias current
                            'Ibn'                   :   10e-12                                                                                          ,   #?  inverting input bias current
                            'Rin_Pos'				:	200e9																							,	#?	non-inverting input resistance
                            'Rin_Neg'				:	200e9																							,	#?	inverting input resistance
                            'Cin_Pos'				:	4e-12																							,	#?	non-inverting input capacitance
                            'Cin_Neg'				:	4e-12																							,	#?	inverting input capacitance
                            'Ileak'					:	0   																							,	#?	output leakage current
                            'Ro'					:	258.85																							,	#?	output resistance
                            'Co'					:	20.823e-12																						,	#?	output capacitance
                            'Zo'       :   {                                                                                                                #!  complex output impedance model
                                'Config'            :   3                                                                                               ,   #?  type of impedance network, 1->Network 1 | 2->Network 2 | 3->disable
                                'Network1'  :   {                                                                                                           #*  parameters of network 1
                                    'R1'                :   380                                                                                         ,   #?  first resistance
                                    'RL1'               :   3.071e-3                                                                                    ,   #?  series resistance of first inductor
                                    'L1'                :   4e-6                                                                                        ,   #?  first inductance
                                    'R2'                :   0                                                                                           ,   #?  second resistance
                                    'RL2'               :   0                                                                                           ,   #?  series resistance of second inductor
                                    'L2'                :   0                                                                                           ,   #?  first inductance
                                    'R3'                :   0                                                                                           ,   #?  third resistance
                                    'R4'                :   0                                                                                           ,   #?  fourth resistance
                                    'C1'                :   8e-12                                                                                       ,   #?  first capacitance
                                },
                                'Network2'  :   {                                                                                                           #*  parameters of network 2
                                    'Rs'                :   0                                                                                           ,   #?  serial resistance
                                    'Ls'                :   0                                                                                           ,   #?  serial inductance
                                    'Rp1'               :   0                                                                                           ,   #?  parallel resistance 1
                                    'Lp1'               :   0                                                                                           ,   #?  parallel inductance
                                    'Rp2'               :   0                                                                                           ,   #?  parallel resistance 2
                                    'Cp1'               :   0                                                                                           ,   #?  parallel capacitance
                                    },
                            },
                            'Netlist'       :   {                                                                                                           #!  SPICE netlist parameters
                                    'File'              :   netlistpath                                                                                 ,   #?  netlist file directory location
                                    'Type'              :   1                                                                                           ,   #?  description type, 1->.subckt | 2->.model
                                    'Name'              :   'TLV316'                                                                                        #?  spice model name as it appears in the netlist file
                            },
                            'Vos'                   :   4.5e-3                                                                                          ,   #?  opamp input offset voltage
                            'Delay'					:	0       																							#?	input-to-output deadtime delay
						}

#?----------------------------------------------------------------------------------------------------------------------------------------------------------------------

# impedanceParam      =   paramProcess.outputImpedanceMatching(opampImpedancePath, 'OPA350')
netlistpath		    =	paramProcess.Netlist_path(opampsNetlistPath, 'OPA350')

OPA350				=	{																																	#*	OPA350 opamp model
							'Config'				: 	2																								,	#?	1->non ideal | 2->ideal/netlist
                            'Type'                  :   2                                                                                               ,   #?  1->limited outout | 2->unlimited output | 3->spice netlist
							'Gain'					: 	10**(126.831/20)																				,	#?	open-loop gain in V/V
							'BW'					: 	16.9869																							,	#?	open-loop bandwidth in Hz
							'Vcc'					: 	3																								,	#?	positive rail supply voltage
                            'Vee'					: 	0																								,	#?	negative rail supply voltage
                            'Rin'					:	1e13																							,	#?	differential input resistance
                            'Cin'					:	2.5e-12																							,	#?	differential input capacitance
                            'Ibp'                   :   10e-12                                                                                          ,   #?  non-inverting input bias current
                            'Ibn'                   :   10e-12                                                                                          ,   #?  inverting input bias current
                            'Rin_Pos'				:	10e13																							,	#?	non-inverting input resistance
                            'Rin_Neg'				:	10e13																							,	#?	inverting input resistance
                            'Cin_Pos'				:	6.5e-12																							,	#?	non-inverting input capacitance
                            'Cin_Neg'				:	6.5e-12																							,	#?	inverting input capacitance
                            'Ileak'					:	0       																						,	#?	output leakage current
                            'Ro'					:	344.64																							,	#?	output resistance
                            'Co'					:	5.26e-12																						,	#?	output capacitance
                            'Zo'       :   {                                                                                                                #!  complex output impedance model
                                'Config'            :   3                                                                                               ,   #?  type of impedance network, 1->Network 1 | 2->Network 2 | 3->disable
                                'Network1'  :   {                                                                                                           #*  parameters of network 1
                                    'R1'                :   0                                                                                           ,   #?  first resistance
                                    'RL1'               :   0                                                                                           ,   #?  series resistance of first inductor
                                    'L1'                :   0                                                                                           ,   #?  first inductance
                                    'R2'                :   0                                                                                           ,   #?  second resistance
                                    'RL2'               :   0                                                                                           ,   #?  series resistance of second inductor
                                    'L2'                :   0                                                                                           ,   #?  first inductance
                                    'R3'                :   0                                                                                           ,   #?  third resistance
                                    'R4'                :   0                                                                                           ,   #?  fourth resistance
                                    'C1'                :   0                                                                                           ,   #?  first capacitance
                                },
                                'Network2'  :   {                                                                                                           #*  parameters of network 2
                                    'Rs'                :   1.18792439e-12                                                                             ,   #?  serial resistance
                                    'Ls'                :   1.63628940e-14                                                                             ,   #?  serial inductance
                                    'Rp1'               :   3.37044222e-04                                                                             ,   #?  parallel resistance 1
                                    'Lp1'               :   2.45428060e-07                                                                             ,   #?  parallel inductance
                                    'Rp2'               :   4.74558132e+01                                                                             ,   #?  parallel resistance 2
                                    'Cp1'               :   3.17712492e-11                                                                             ,   #?  parallel capacitance
                                    },
                            },
                            'Netlist'       :   {                                                                                                           #!  SPICE netlist parameters
                                    'File'              :   netlistpath                                                                                 ,   #?  netlist file directory location
                                    'Type'              :   1                                                                                           ,   #?  description type, 1->.subckt | 2->.model
                                    'Name'              :   'OPAx350'                                                                                       #?  spice model name as it appears in the netlist file
                            },
                            'Vos'                   :   150e-6                                                                                          ,   #?  opamp input offset voltage
                            'Delay'					:	0       																							#?	input-to-output deadtime delay
						}

#?----------------------------------------------------------------------------------------------------------------------------------------------------------------------

# impedanceParam      =   paramProcess.outputImpedanceMatching(opampImpedancePath, 'TS3021')
netlistpath		    =	paramProcess.Netlist_path(opampsNetlistPath, 'TS3021')

TS3021				=	{																																	#*	TS3021 opamp model
							'Config'				: 	2																								,	#?	1->non ideal | 2->ideal/netlist
                            'Type'                  :   2                                                                                               ,   #?  1->limited outout | 2->unlimited output | 3->spice netlist
							'Gain'					: 	10**(121.31/20)																				    ,	#?	open-loop gain in V/V
							'BW'					: 	1.03159e7																					    ,	#?	open-loop bandwidth in Hz
							'Vcc'					: 	3																								,	#?	positive rail supply voltage
                            'Vee'					: 	0																								,	#?	negative rail supply voltage
                            'Rin'					:	'inf'      																						,	#?	differential input resistance
                            'Cin'					:	0   																							,	#?	differential input capacitance
                            'Ibp'                   :   300e-9                                                                                          ,   #?  non-inverting input bias current
                            'Ibn'                   :   300e-9                                                                                          ,   #?  inverting input bias current
                            'Rin_Pos'				:	'inf'																							,	#?	non-inverting input resistance
                            'Rin_Neg'				:	'inf'																							,	#?	inverting input resistance
                            'Cin_Pos'				:	0   																							,	#?	non-inverting input capacitance
                            'Cin_Neg'				:	0   																							,	#?	inverting input capacitance
                            'Ileak'					:	0   																							,	#?	output leakage current
                            'Ro'					:	2500																						    ,	#?	output resistance
                            'Co'					:	2e-12   																						,	#?	output capacitance
                            'Zo'       :   {                                                                                                                #!  complex output impedance model
                                'Config'            :   3                                                                                               ,   #?  type of impedance network, 1->Network 1 | 2->Network 2 | 3->disable
                                'Network1'  :   {                                                                                                           #*  parameters of network 1
                                    'R1'                :   0                                                                                           ,   #?  first resistance
                                    'RL1'               :   0                                                                                           ,   #?  series resistance of first inductor
                                    'L1'                :   0                                                                                           ,   #?  first inductance
                                    'R2'                :   0                                                                                           ,   #?  second resistance
                                    'RL2'               :   0                                                                                           ,   #?  series resistance of second inductor
                                    'L2'                :   0                                                                                           ,   #?  first inductance
                                    'R3'                :   0                                                                                           ,   #?  third resistance
                                    'R4'                :   0                                                                                           ,   #?  fourth resistance
                                    'C1'                :   0                                                                                           ,   #?  first capacitance
                                },
                                'Network2'  :   {                                                                                                           #*  parameters of network 2
                                    'Rs'                :   2.25669074e-05                                                                              ,   #?  serial resistance
                                    'Ls'                :   3.89833329e-13                                                                              ,   #?  serial inductance
                                    'Rp1'               :   3.09122243e-06                                                                              ,   #?  parallel resistance 1
                                    'Lp1'               :   1.56005537e-13                                                                              ,   #?  parallel inductance
                                    'Rp2'               :   3.80150760e-02                                                                              ,   #?  parallel resistance 2
                                    'Cp1'               :   1.07927386e-15                                                                              ,   #?  parallel capacitance
                                    },
                            },
                            'Netlist'       :   {                                                                                                           #!  SPICE netlist parameters
                                    'File'              :   netlistpath                                                                                 ,   #?  netlist file directory location
                                    'Type'              :   1                                                                                           ,   #?  description type, 1->.subckt | 2->.model
                                    'Name'              :   'TS302x'                                                                                        #?  spice model name as it appears in the netlist file
                            },
                            'Vos'                   :   7e-3                                                                                            ,   #?  opamp input offset voltage
                            'Delay'					:	85e-9   																							#?	input-to-output deadtime delay
						}

#?----------------------------------------------------------------------------------------------------------------------------------------------------------------------

# impedanceParam      =   paramProcess.outputImpedanceMatching(opampImpedancePath, 'OPA992')
netlistpath		    =	paramProcess.Netlist_path(opampsNetlistPath, 'OPA992')

OPA992				=	{																																	#*	OPA992 opamp model
							'Config'				: 	2																								,	#?	1->non ideal | 2->ideal/netlist
                            'Type'                  :   2                                                                                               ,   #?  1->limited outout | 2->unlimited output | 3->spice netlist
							'Gain'					:   10**(141.751/20)																				,	#?	open-loop gain in V/V
							'BW'					: 	0.854015																						,	#?	open-loop bandwidth in Hz
							'Vcc'					: 	3																								,	#?	positive rail supply voltage
                            'Vee'					: 	0																								,	#?	negative rail supply voltage
                            'Rin'					:	100e6																							,	#?	differential input resistance
                            'Cin'					:	9e-12																							,	#?	differential input capacitance
                            'Ibp'                   :   10e-12                                                                                          ,   #?  non-inverting input bias current
                            'Ibn'                   :   10e-12                                                                                          ,   #?  inverting input bias current
                            'Rin_Pos'				:	6e12																							,	#?	non-inverting input resistance
                            'Rin_Neg'				:	6e12																							,	#?	inverting input resistance
                            'Cin_Pos'				:	1e-12																							,	#?	non-inverting input capacitance
                            'Cin_Neg'				:	1e-12																							,	#?	inverting input capacitance
                            'Ileak'					:	0																							    ,	#?	output leakage current
                            'Ro'					:	243.63	    																					,	#?	output resistance
                            'Co'					:	21.2983e-12 																					,	#?	output capacitance
                            'Zo'       :   {                                                                                                                #!  complex output impedance model
                                'Config'            :   3                                                                                               ,   #?  type of impedance network, 1->Network 1 | 2->Network 2 | 3->disable
                                'Network1'  :   {                                                                                                           #*  parameters of network 1
                                    'R1'                :   0                                                                                           ,   #?  first resistance
                                    'RL1'               :   0                                                                                           ,   #?  series resistance of first inductor
                                    'L1'                :   0                                                                                           ,   #?  first inductance
                                    'R2'                :   0                                                                                           ,   #?  second resistance
                                    'RL2'               :   0                                                                                           ,   #?  series resistance of second inductor
                                    'L2'                :   0                                                                                           ,   #?  first inductance
                                    'R3'                :   0                                                                                           ,   #?  third resistance
                                    'R4'                :   0                                                                                           ,   #?  fourth resistance
                                    'C1'                :   0                                                                                           ,   #?  first capacitance
                                },
                                'Network2'  :   {                                                                                                           #*  parameters of network 2
                                    'Rs'                :   1.20219490e-15                                                                              ,   #?  serial resistance
                                    'Ls'                :   1.60427033e-14                                                                              ,   #?  serial inductance
                                    'Rp1'               :   2.18063886e-06                                                                              ,   #?  parallel resistance 1
                                    'Lp1'               :   4.00113169e-07                                                                              ,   #?  parallel inductance
                                    'Rp2'               :   6.02979803e+01                                                                              ,   #?  parallel resistance 2
                                    'Cp1'               :   1.58662010e-06                                                                              ,   #?  parallel capacitance
                                    },
                            },
                            'Netlist'       :   {                                                                                                           #!  SPICE netlist parameters
                                    'File'              :   netlistpath                                                                                 ,   #?  netlist file directory location
                                    'Type'              :   1                                                                                           ,   #?  description type, 1->.subckt | 2->.model
                                    'Name'              :   'OPA2992'                                                                                       #?  spice model name as it appears in the netlist file
                            },
                            'Vos'                   :   1.2e-3                                                                                          ,   #?  opamp input offset voltage
                            'Delay'					:	0         																							#?	input-to-output deadtime delay
						}

#?----------------------------------------------------------------------------------------------------------------------------------------------------------------------

# impedanceParam      =   paramProcess.outputImpedanceMatching(opampImpedancePath, 'TLV916')
netlistpath		    =	paramProcess.Netlist_path(opampsNetlistPath, 'TLV916')

TLV916				=	{																																	#*	TLV916 opamp model
							'Config'				: 	2																								,	#?	1->non ideal | 2->ideal/netlist
                            'Type'                  :   2                                                                                               ,   #?  1->limited outout | 2->unlimited output | 3->spice netlist
							'Gain'					:   10**(141.751/20)																				,	#?	open-loop gain in V/V
							'BW'					: 	0.854015																						,	#?	open-loop bandwidth in Hz
							'Vcc'					: 	3																								,	#?	positive rail supply voltage
                            'Vee'					: 	0																								,	#?	negative rail supply voltage
                            'Rin'					:	100e6																							,	#?	differential input resistance
                            'Cin'					:	9e-12																						    ,	#?	differential input capacitance
                            'Ibp'                   :   10e-12                                                                                          ,   #?  non-inverting input bias current
                            'Ibn'                   :   10e-12                                                                                          ,   #?  inverting input bias current
                            'Rin_Pos'				:	6e12																							,	#?	non-inverting input resistance
                            'Rin_Neg'				:	6e12																							,	#?	inverting input resistance
                            'Cin_Pos'				:	1e-12																							,	#?	non-inverting input capacitance
                            'Cin_Neg'				:	1e-12																							,	#?	inverting input capacitance
                            'Ileak'					:	0   																							,	#?	output leakage current
                            'Ro'					:   243.63	  																						,	#?	output resistance
                            'Co'					:	21.2983e-12																						,	#?	output capacitance
                            'Zo'       :   {                                                                                                                #!  complex output impedance model
                                'Config'            :   3                                                                                               ,   #?  type of impedance network, 1->Network 1 | 2->Network 2 | 3->disable
                                'Network1'  :   {                                                                                                           #*  parameters of network 1
                                    'R1'                :   0                                                                                           ,   #?  first resistance
                                    'RL1'               :   0                                                                                           ,   #?  series resistance of first inductor
                                    'L1'                :   0                                                                                           ,   #?  first inductance
                                    'R2'                :   0                                                                                           ,   #?  second resistance
                                    'RL2'               :   0                                                                                           ,   #?  series resistance of second inductor
                                    'L2'                :   0                                                                                           ,   #?  first inductance
                                    'R3'                :   0                                                                                           ,   #?  third resistance
                                    'R4'                :   0                                                                                           ,   #?  fourth resistance
                                    'C1'                :   0                                                                                           ,   #?  first capacitance
                                },
                                'Network2'  :   {                                                                                                           #*  parameters of network 2
                                    'Rs'                :   1.20219490e-15                                                                              ,   #?  serial resistance
                                    'Ls'                :   1.60427033e-14                                                                              ,   #?  serial inductance
                                    'Rp1'               :   2.18063886e-06                                                                              ,   #?  parallel resistance 1
                                    'Lp1'               :   4.00113169e-07                                                                              ,   #?  parallel inductance
                                    'Rp2'               :   6.02979803e+01                                                                              ,   #?  parallel resistance 2
                                    'Cp1'               :   1.58662010e-06                                                                              ,   #?  parallel capacitance
                                    },
                            },
                            'Netlist'       :   {                                                                                                           #!  SPICE netlist parameters
                                    'File'              :   netlistpath                                                                                 ,   #?  netlist file directory location
                                    'Type'              :   1                                                                                           ,   #?  description type, 1->.subckt | 2->.model
                                    'Name'              :   'TLV9162'                                                                                       #?  spice model name as it appears in the netlist file
                            },
                            'Vos'                   :   1.2e-3                                                                                          ,   #?  opamp input offset voltage
                            'Delay'					:	0          																							#?	input-to-output deadtime delay
						}

#?----------------------------------------------------------------------------------------------------------------------------------------------------------------------

# impedanceParam      =   paramProcess.outputImpedanceMatching(opampImpedancePath, 'TLV900')
netlistpath		    =	paramProcess.Netlist_path(opampsNetlistPath, 'TLV900')

TLV900				=	{																																	#*	TLV900 opamp model
							'Config'				: 	2																								,	#?	1->non ideal | 2->ideal/netlist
                            'Type'                  :   2                                                                                               ,   #?  1->limited outout | 2->unlimited output | 3->spice netlist
							'Gain'					:   10**(120.568/20)																				,	#?	open-loop gain in V/V
							'BW'					: 	1.05928																							,	#?	open-loop bandwidth in Hz
							'Vcc'					: 	3																								,	#?	positive rail supply voltage
                            'Vee'					: 	0																								,	#?	negative rail supply voltage
                            'Rin'					:	'inf'																							,	#?	differential input resistance
                            'Cin'					:	0   																						    ,	#?	differential input capacitance
                            'Ibp'                   :   5e-12                                                                                           ,   #?  non-inverting input bias current
                            'Ibn'                   :   5e-12                                                                                           ,   #?  inverting input bias current
                            'Rin_Pos'				:	'inf'																							,	#?	non-inverting input resistance
                            'Rin_Neg'				:	'inf'																							,	#?	inverting input resistance
                            'Cin_Pos'				:	0   																							,	#?	non-inverting input capacitance
                            'Cin_Neg'				:	0   																							,	#?	inverting input capacitance
                            'Ileak'					:	0   																							,	#?	output leakage current
                            'Ro'					:	1256																							,	#?	output resistance
                            'Co'					:	19.880514e-12																					,	#?	output capacitance
                            'Zo'       :   {                                                                                                                #!  complex output impedance model
                                'Config'            :   3                                                                                               ,   #?  type of impedance network, 1->Network 1 | 2->Network 2 | 3->disable
                                'Network1'  :   {                                                                                                           #*  parameters of network 1
                                    'R1'                :   1350                                                                                        ,   #?  first resistance
                                    'RL1'               :   1.4472e-3                                                                                   ,   #?  series resistance of first inductor
                                    'L1'                :   175e-6                                                                                      ,   #?  first inductance
                                    'R2'                :   0                                                                                           ,   #?  second resistance
                                    'RL2'               :   0                                                                                           ,   #?  series resistance of second inductor
                                    'L2'                :   0                                                                                           ,   #?  first inductance
                                    'R3'                :   0                                                                                           ,   #?  third resistance
                                    'R4'                :   0                                                                                           ,   #?  fourth resistance
                                    'C1'                :   5.5e-12                                                                                     ,   #?  first capacitance
                                },
                                'Network2'  :   {                                                                                                           #*  parameters of network 2
                                    'Rs'                :   0                                                                                           ,   #?  serial resistance
                                    'Ls'                :   0                                                                                           ,   #?  serial inductance
                                    'Rp1'               :   0                                                                                           ,   #?  parallel resistance 1
                                    'Lp1'               :   0                                                                                           ,   #?  parallel inductance
                                    'Rp2'               :   0                                                                                           ,   #?  parallel resistance 2
                                    'Cp1'               :   0                                                                                           ,   #?  parallel capacitance
                                    },
                            },
                            'Netlist'       :   {                                                                                                           #!  SPICE netlist parameters
                                    'File'              :   netlistpath                                                                                 ,   #?  netlist file directory location
                                    'Type'              :   1                                                                                           ,   #?  description type, 1->.subckt | 2->.model
                                    'Name'              :   'TLV9002'                                                                                       #?  spice model name as it appears in the netlist file
                            },
                            'Vos'                   :   2.0e-3                                                                                          ,   #?  opamp input offset voltage
                            'Delay'					:	14.88e-9   																							#?	input-to-output deadtime delay
						}

#?----------------------------------------------------------------------------------------------------------------------------------------------------------------------

# impedanceParam      =   paramProcess.outputImpedanceMatching(opampImpedancePath, 'TLV900')
netlistpath		    =	paramProcess.Netlist_path(opampsNetlistPath, 'TLV906')

TLV906				=	{																																	#*	TLV906 opamp model
							'Config'				: 	2																								,	#?	1->non ideal | 2->ideal/netlist
                            'Type'                  :   2                                                                                               ,   #?  1->limited outout | 2->unlimited output | 3->spice netlist
							'Gain'					: 	10**(110.881/20)																				,	#?	open-loop gain in V/V
							'BW'					: 	32.0076																							,	#?	open-loop bandwidth in Hz
							'Vcc'					: 	3																								,	#?	positive rail supply voltage
                            'Vee'					: 	0																								,	#?	negative rail supply voltage
                            'Rin'					:	'inf'																							,	#?	differential input resistance
                            'Cin'					:	2e-12																							,	#?	differential input capacitance
                            'Ibp'                   :   0.5e-12                                                                                         ,   #?  non-inverting input bias current
                            'Ibn'                   :   0.5e-12                                                                                         ,   #?  inverting input bias current
                            'Rin_Pos'				:	'inf'																							,	#?	non-inverting input resistance
                            'Rin_Neg'				:	'inf'																							,	#?	inverting input resistance
                            'Cin_Pos'				:	4e-12																							,	#?	non-inverting input capacitance
                            'Cin_Neg'				:	4e-12																							,	#?	inverting input capacitance
                            'Ileak'					:	0   																							,	#?	output leakage current
                            'Ro'					:	258.85																							,	#?	output resistance
                            'Co'					:	20.823e-12																						,	#?	output capacitance
                            'Zo'       :   {                                                                                                                #!  complex output impedance model
                                'Config'            :   3                                                                                               ,   #?  type of impedance network, 1->Network 1 | 2->Network 2 | 3->disable
                                'Network1'  :   {                                                                                                           #*  parameters of network 1
                                    'R1'                :   366.395                                                                                     ,   #?  first resistance
                                    'RL1'               :   0.26802e-3                                                                                  ,   #?  series resistance of first inductor
                                    'L1'                :   1.8e-6                                                                                      ,   #?  first inductance
                                    'R2'                :   0                                                                                           ,   #?  second resistance
                                    'RL2'               :   0                                                                                           ,   #?  series resistance of second inductor
                                    'L2'                :   0                                                                                           ,   #?  first inductance
                                    'R3'                :   0                                                                                           ,   #?  third resistance
                                    'R4'                :   0                                                                                           ,   #?  fourth resistance
                                    'C1'                :   6e-12                                                                                       ,   #?  first capacitance
                                },
                                'Network2'  :   {                                                                                                           #*  parameters of network 2
                                    'Rs'                :   0                                                                                           ,   #?  serial resistance
                                    'Ls'                :   0                                                                                           ,   #?  serial inductance
                                    'Rp1'               :   0                                                                                           ,   #?  parallel resistance 1
                                    'Lp1'               :   0                                                                                           ,   #?  parallel inductance
                                    'Rp2'               :   0                                                                                           ,   #?  parallel resistance 2
                                    'Cp1'               :   0                                                                                           ,   #?  parallel capacitance
                                    },
                            },
                            'Netlist'       :   {                                                                                                           #!  SPICE netlist parameters
                                    'File'              :   netlistpath                                                                                 ,   #?  netlist file directory location
                                    'Type'              :   1                                                                                           ,   #?  description type, 1->.subckt | 2->.model
                                    'Name'              :   'TLV9062'                                                                                       #?  spice model name as it appears in the netlist file
                            },
                            'Vos'                   :   2.0e-3                                                                                          ,   #?  opamp input offset voltage
                            'Delay'					:	0       																							#?	input-to-output deadtime delay
						}

#?----------------------------------------------------------------------------------------------------------------------------------------------------------------------

#!	assemble all opamps to be transferred to the PLECS model
#?----------------------------------------------------------------------------------------------------------------------------------------------------------------------

AllOpAmps 			= 	{
							'Ideal' 				: 	Ideal 			,
                            'TLV316'				:	TLV316			,
                            'OPA350'                :   OPA350          ,
                            'TS3021'                :   TS3021          ,
                            'OPA992'                :   OPA992          ,
                            'TLV916'                :   TLV916          ,
                            'TLV900'                :   TLV900          ,
                            'TLV906'                :   TLV906
						}
#?----------------------------------------------------------------------------------------------------------------------------------------------------------------------