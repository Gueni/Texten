
#?----------------------------------------------------------------------------------------------------------------------------------------------------------------------
#?						 ____          _ _       _                 ____                                _
#?						/ ___|_      _(_) |_ ___| |__   ___  ___  |  _ \ __ _ _ __ __ _ _ __ ___   ___| |_ ___ _ __ ___
#?						\___ \ \ /\ / / | __/ __| '_ \ / _ \/ __| | |_) / _` | '__/ _` | '_ ` _ \ / _ \ __/ _ \ '__/ __|
#?						 ___) \ V  V /| | || (__| | | |  __/\__ \ |  __/ (_| | | | (_| | | | | | |  __/ ||  __/ |  \__ \
#?						|____/ \_/\_/ |_|\__\___|_| |_|\___||___/ |_|   \__,_|_|  \__,_|_| |_| |_|\___|\__\___|_|  |___/
#?
#?----------------------------------------------------------------------------------------------------------------------------------------------------------------------
#!----------------------------------------------------------------------------------------------------------------------------------------------------------------------
#!   This Script works as a Parameter dictionary for the plecs switches models.
#!   Do not modify the values in this file.
#!----------------------------------------------------------------------------------------------------------------------------------------------------------------------
#?----------------------------------------------------------------------------------------------------------------------------------------------------------------------
import 	copy

import 	numpy 					as	np
import  Lib.Param_Process		as	PM
#?----------------------------------------------------------------------------------------------------------------------------------------------------------------------

#! 	call the Params-Processing class and point to the location of csv data
paramProcess			=	PM.ParamProcess()
switchesTransferPath	=	'Script/Data/Switches_Forward_Transfer/'
switchesCossPath		=	'Script/Data/Switches_Coss/'
switchesCrssPath		=	'Script/Data/Switches_Crss/'
switchesCissPath		=	'Script/Data/Switches_Ciss/'
switchesRdsonPath		= 	'Script/Data/Switches_Rdson/'
switchesIdsonPath		= 	'Script/Data/Switches_Rdson_Ids/'
switchesEoffPath    	=   'Script/Data/Switches_Eoff/'
switchesEonPath    		=   'Script/Data/Switches_Eon/'
bodyDiodeVIPath 		=	'Script/Data/Diodes_VI/'

#! GAN Switches models parameters
#?----------------------------------------------------------------------------------------------------------------------------------------------------------------------
Coss,Qoss,Eoss,Coss_tr,Coss_er		=	paramProcess.MOSFETcaps(switchesCossPath,'GS66508T','_Coss')
Crss,Qrss,Erss,Crss_tr,Crss_er 		=	paramProcess.MOSFETcaps(switchesCrssPath,'GS66508T','_Crss')
Ciss,Qiss,Eiss,Ciss_tr,Ciss_er 		=	paramProcess.MOSFETcaps(switchesCissPath,'GS66508T','_Ciss')
Coss_eff 							=	paramProcess.getCmos(Coss,Coss_tr,Coss_er,Coss[0][0],True)
Ciss_eff 							=	paramProcess.getCmos(Ciss,Ciss_tr,Ciss_er,Ciss[0][0],True)
Crss_eff 							=	paramProcess.getCmos(Crss,Crss_tr,Crss_er,Crss[0][0],True)
Cds 						        =	(np.array(Coss[1]) - np.array(Crss[1])).tolist()
Cgs						        	=	(np.array(Ciss[1]) - np.array(Crss[1])).tolist()
Cgd						        	=	Crss[1]
Cds_tr						        =	(np.array(Coss_tr) - np.array(Crss_tr)).tolist()
Cgs_tr						        =	(np.array(Ciss_tr) - np.array(Crss_tr)).tolist()
Cgd_tr						        =	Crss_tr
Cds_er						        =	(np.array(Coss_er) - np.array(Crss_er)).tolist()
Cgs_er						        =	(np.array(Ciss_er) - np.array(Crss_er)).tolist()
Cgd_er						        =	Crss_er
Cds_eff 							=	paramProcess.getCmos([Coss[0],Cds],Cds_tr,Cds_er,Coss[0][0],True)
Cgs_eff 							=	paramProcess.getCmos([Ciss[0],Cgs],Cgs_tr,Cgs_er,Ciss[0][0],True)
Cgd_eff 							=	Crss_eff
Rvec,Tvec							=	paramProcess.MOSFETrdson(switchesRdsonPath,'GS66508T','_Rdson')
Nvec,Ivec 							=	paramProcess.MOSFETrdson(switchesIdsonPath,'GS66508T','_Rdson')
Ioff,catOFF,Eoff					=	paramProcess.MOSFETenergies(switchesEoffPath,'GS66508T','_Eoff')
Voff,catOFF_Temp,Eoff_Temp			=	paramProcess.MOSFETenergies(switchesEoffPath,'GS66508T','_Eoff_Temp')
Ion,catON,Eon 						=	paramProcess.MOSFETenergies(switchesEonPath,'GS66508T','_Eon')
Von,catON_Temp,Eon_Temp				=	paramProcess.MOSFETenergies(switchesEonPath,'GS66508T','_Eon_Temp')
Vfvec,Ifvec,Rd,Vt					=	paramProcess.DiodeVI_data(bodyDiodeVIPath,'GS66508T')
Vds_vec,Ids_vec 					=	paramProcess.Forward_Transfer_data(switchesTransferPath,'GS66508T')

GS66508T			=	{																																	#*	GS66508T parameters
							'Config'						:	1																						,	#!	1->electric integrated | 2->electric separate | 3->thermal integrated | 4->thermal separate
							'Transistor'  			: 	{																									#!	transistors parameters
									'Config'				:	2																						,	#?	1->real with limited di/dt | 2->ideal switch | 3->behavioral model
									'Thermal'           	:   'GaN_Systems/GS66508_v3'                                  								,   #? 	selected transistor
									'Custom'            	:   ['Rgon','1','Rgoff','1','vgsoff','1','g','m:g']                 						,   #? 	transistor provided custom variables
									'g_fs'					:	1e6																						,	#?	forward transconductance
									'Rg'					:	1																						,	#?	internal gate resistance
									'Lg'					:	3.1e-9*0																				,	#?	gate pin inductance
									'Rds_on'            	:   Rvec[-1][-1]*1e-3																		,   #? 	transistor ON resistance
									'Rds_off'				:	'inf'																					,	#?	transistor OFF resistance
									'Rvec'					:	(np.array(Rvec)*1e-3).tolist()														,	#?	absolute Rdson vector corresponding to junction temperature
									'Tvec'					:	Tvec 																					,	#?	junction temperature vector for Rdson
									'RTconfig'				:	1																						,	#?	choose which RT vector to be used
									'RdsonScale'			:	1.0																						,	#?	Rdson scaling to account for min, typ and max deviations
									'Nvec'					:	Nvec 																					,	#?	normalized Rdson vector corresponding to current
									'Ivec'					:	Ivec																					,	#?	current vector for normalized Rdson
									'NIconfig'				:	1																						,	#?	choose which NI vector to be used
									'IdsonScale'			:	1.0																						,	#?	Idson resistance scaling to account for min, typ and max deviations
									'Rsrc'					:	0.1e-3*0																				,	#?	kelvin source pin resistance
									'Lsrc'					:	100e-12*0																				,	#?	kelvin source pin inductance
									'Ls'					:	100e-12*0																				,	#?	package source inductance
                                    'Ld'					:	170e-12*0																				,	#?	package drain inductance
									'Rs'					:	0.1e-3*0																				,	#?	package source resistance
									'Rd'					:	0.1e-3*0																				,	#?	package drain inductance
									'Ksrc'					:	1																						,	#?	kelvin source option, 0->no kelvin | 1->kelvin
									'Vblock'            	:   650                                	 													,   #? 	transistor blocking voltage
									'Id'                	:   30	                                 													,   #? 	transistor drain current
									'Tr'                	:   0                                   													,   #? 	transistor rise time
									'Tf'                	:   0                                       												, 	#? 	transistor fall time
									'Avalanche'		:	{																									#!	transistor avalanche parameters
										'Config'			:	2																						,	#?	1->enable | 2->disable
										'Voltage'			:	650 																					,	#?	avalanche voltage
										'Resistance'		:	1e-3																						#?	avalanche resistance to break voltage state-dependency
									},
									'Transfer'		:	{																									#!	transistor forward transfer parameters
										'Vds'				:	Vds_vec																					,	#?	drain-source voltage vector
										'Vgs'				:	list(np.arange(0.0,7.0+0.4,0.4))														,	#?	gate-source voltage vector
										'Ids'				:	Ids_vec																					,	#?	drain current vector
										'Factor_ON'			:	1.0																						,	#?	scaling factor for Ids at turn ON
										'Factor_OFF'		:	1.0																						,	#?	scaling factor for Ids at turn OFF
										'Factor_Vgs_ON'		:	1.0																						,	#?	scaling factor for Vgs at turn ON
										'Factor_Vgs_OFF'	:	1.0																						,	#?	scaling factor for Vgs at turn OFF
										'Vcoss'				:	0																						,	#?	initial voltage of the Coss
									},
						},
							'BodyDiode'  			:	{																									#!	body diodes paramteters
									'Config'				:	4																						,	#?	1->non-ideal RR | 2->non-ideal | 3->ideal RR | 4->ideal
									'Thermal'           	:   ''                                  													,   #? 	separate body diode
									'Custom'            	:   []					                 													,   #? 	body diode provided custrom variables
									'Rd_on'             	:   Rd[-1]													                              	,  	#? 	body diode ON resistance
									'Rd_off'				:	'inf'																					,	#?	body diode OFF resistance
									'Vf'					:	Vt[-1]																					,	#? 	body diode forward voltage
									'If'                	:   30	                                 													,   #? 	body diode forward current
									'dIr'               	:   1000e6                                 													,   #? 	body diode current slope
									'Lrr'					:	1e-9																					,	#?	body diode reverse recovery inductance
									'Trr'               	:   0	                                  													,   #? 	body diode reverse recovery time
									'Irr'               	:   0                                      													,   #? 	body diode reverse recovery current
									'Qrr'               	:   0			                              												,	#? 	body diode reverse recovery charge
									'Is'                  	:   0              																		   	,	#? 	body diode reference current
									'Vs'					:	0																						,	#?	body diode reference voltage
                                    'VIcurve'		:	{																									#!	body diode VI characteristics
                                        'Vfvec'				:	Vfvec																					,	#?	forward voltage vector
                                        'Ifvec'				:	Ifvec																					,	#?	forward current vector
										'Rdvec'				:	Rd																						,	#?	dynamic resistance vector
										'Vtvec'				:	Vt																						,	#?	threshold voltage vector
                                        'Temps'				:	[25,150]																				,	#?	temperature vector
                                        'Vfscale'			:	1.529																						#?	Vf scaling to account for min, typ and max deviations
									},
						},
							'GateDriver'			:	{																									#!	gate driver parameters
									'Config'				:	3																						,	#?	1->high-side | 2->low-side | 3->disable
									'Von'					:	12																						,	#?	ON driving voltage
									'Voff'					:	0																						,	#?	OFF driving voltage
									'Ron'					:	5																						,	#?	sourcing output resistance
									'Roff'					:	5																						,	#?	sinking output resistance
									'Lon'					:	0																						,	#?	sourcing output inductance
									'Loff'					:	0																						,	#?	sinking output inductance
									'Cload'					:	0																						,	#?	capacitive load on output
									'Rload'					:	'inf'																					,	#?	resistive load on output
									'Delay'					:	0																						,	#?	input-to-output total deadtime
									'Trise'					:	0																						,	#?	output rising time
									'Tfall'					:	0																						,	#?	output falling time
									'UVLO_Start'			:	7.0																						,	#?	UVLO startup voltage threshold
									'UVLO_Stop'				:	6.5																						,	#?	UVLO shutdown voltage threshold
									'UVLO_Delay'			:	100e-9																					,	#?	delay between UVLO startup and shutdown
									'Init_State'			:	0																						,	#?	initial toggling state, 0->OFF | 1->ON
									'CurrentLimit'	:	{																									#*	current limit of driver stage
										'Config'			:	2																						,	#?	1->enable | 2->disable
										'Ts'				: 	0 																						,	#?	sampling time between inductive & capacitive links
										'tau'				: 	0																						,	#?	first-order delay between inductive & capacitive links
                                    	'Rs'				: 	0																						,	#?	source impedance of inductive link
										'Cs'				:	1e-12																					,	#?	source capacitance of capacitive link
                                        'UpLim'				: 	10																						,	#?	max current limit on capacitive link
                                        'LoLim'				: 	-10																						,	#?	min current limit on capacitive link
                                        'Voffset'			: 	0																							#?	voltage offset between inductive & capacitive links
									},
									'Masking'		:	{																									#*	switching stages masking
										'ON'	:	{																										#	ON path masking
											'Config'		:	2																						,	#?	1->enable | 2->disable
											'HIGH'	:	{																									#!	HIGH mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[0, 0]																						#?	mask output
											},
											'LOW'	:	{																									#!	LOW mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[1, 1]																						#?	mask output
											}
										},
										'OFF'	:	{																										#	OFF path masking
											'Config'		:	2																						,	#?	1->enable | 2->disable
											'HIGH'	:	{																									#!	HIGH mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[0, 0]																						#?	mask output
											},
											'LOW'	:	{																									#!	LOW mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[1, 1]																						#?	mask output
											}
										}
									},
									'Boot'			:	{																									#*	bootstrap/charge pump parameters
										'Config'			:	1																						,	#?	1->bootstrap | 2->charge pump
										'Von'				:	14																						,	#?	boostrap driving voltage
										'Cboot'				:	4.7e-6																					,	#?	bootstrap capacitance
										'Vinit'				:	0																						,	#?	bootstrap capacitance initial voltage
										'Rboot'				:	10																						,	#?	bootstrap resistance
										'Vfboot'			:	0.87																					,	#?	bootstrap diode forward voltage
										'Rdboot'			:	1e-3																					,	#?	bootstrap diode ON-state resistance
										'Ichrg'				:	300e-6																					,	#?	charge pump supply current
										'Idis'				:	5e-6																					,	#?	charge pump loading or leakage current
										'Cpar'				:	0																						,	#?	charge pump parallel cap to break state/source dependency
									    'UVLO_Start'		:	11.6																					,	#?	threshold value to start the charge pump
										'UVLO_Stop'			:	12.4																						#?	threshold value to stop the charge pump
									},
							},
							'GateNetwork'			:	{																									#!	gate drive circuit parameters
									'Config'				:	2																						,	#?	1-> enable | 2->disable
									'ON_Path'		:	{																									#*	sourcing path parameters
										'Rg'				:	5																						,	#?	gate ON path resistance
										'Lg'				:	0																						,	#?	gate ON path inductance
										'Rload'				:	10e3																					,	#?	gate pull down resistance
										'Diode'	:	{																										#	reverse blocking diode parameters
											'Vf'			:	0																						,	#?	forward voltage
											'Rd_on'			:	0																						,	#?	ON-state resistance
										},
									},
									'OFF_Path'		:	{																									#*	sinking path parameters
										'Rg'				:	5																						,	#?	gate OFF path resistance
										'Lg'				:	0																						,	#?	gate OFF path inductance
										'Diode'	:	{																										#	reverse blocking diode parameters
											'Vf'			:	0																						,	#?	forward voltage
											'Rd_on'			:	0																						,	#?	ON-state resistance
										},
									},
									'NegVolt'		:	{																									#*	negative voltage generator parameters
										'Config'			:	2																						,	#?	1-> enable | 2->disable
										'Dz'	:	{																										#	zener diode parameters
											'Vf'			:	0.7																						,	#?	forward voltage
											'Rd_on'			:	1e-3																					,	#?	ON-state resistance
											'Vz'			:	2																						,	#?	Zener breakdown voltage
											'Rz'			:	1e-3																					,	#?	Zener resistance
										},
										'Dp'	:	{																										#	peak detector diode
											'Vf'			:	0.0																						,	#?	forward voltage
											'Rd_on'			:	0.0																						,	#?	ON-state resistance
										},
										'Cz'	:	{																										#	Zener capacitor parameters
											'Config'		:	1																						,	#?	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
											'Csingle'		:	1e-6																					,	#?	single capacitor value
											'Rsingle'		:	5e-3																					,	#?	ESR of single capacitor
											'Lsingle'		:	0																						,	#?	ESL of single capacitor
											'nPar'			:	1																						,	#?	number of parallel connections
											'nSer'			:	1																						,	#?	number of series connections
											'Vinit'			:	0																						,	#?	capacitor initial voltage
										},
										'Cp'	:	{																										#	peak detector capacitor parameters
											'Config'		:	1																						,	#?	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
											'Csingle'		:	2.2e-6																					,	#?	single capacitor value
											'Rsingle'		:	5e-3																					,	#?	ESR of single capacitor
											'Lsingle'		:	0																						,	#?	ESL of single capacitor
											'nPar'			:	1																						,	#?	number of parallel connections
											'nSer'			:	1																						,	#?	number of series connections
											'Vinit'			:	0																						,	#?	capacitor initial voltage
										},
										'Rp1'				:	43																						,	#?	current limiter of peak detector current
										'Rp2'				:	4.7e3																					,	#?	load resistor to charge the zener diode
									},
								},
							'nParallel'   					:	1                                       												,   #? 	number of parallel devices
							'Rth_jc'						:	[0.015,0.23,0.24,0.015]																	,	#?	junction-to-case thermal resistance
							'Cth_jc'						:	[8e-5,7.4e-4,6.5e-3,2e-3]																,	#?	junction-to-case thermal capacitance
							'Rth_ca'              			:   3.50            																		,   #? 	case-to-ambient thermal resistance
							'Cth_ca'              			:   0.0             																		,   #? 	case-to-ambient thermal capacitance
							'Tinit'							:	0.0																						,	#?	initial juntion temperature
							'Pinit'							:	0.0																						,	#?	initial power dissipation
							'Coss'					: 	{																									#!	device Coss parameters
								'C'							:	Coss_eff					 															,	#?	device parasitic output capacitance
								'R'							:	0																						,	#?	Coss resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Coss inductance to reduce current slope
								'Coss_er'					:	Coss_er																					,	#?	energy-related Coss
								'Coss_tr'					:	Coss_tr																					,	#?	time-related Coss
								'Vvec'						:	Coss[0]																					,	#? 	device Coss voltage vector
								'Cvec'						:	Coss[1]																					,	#?	device Coss capacity vector
								'Offset'					:	0																						,	#?	parasitic offset to Coss
                                'Factor'					:	1.0																						,	#?	parasitic tolerance to Coss
								'Qoss'						:	Qoss																					,	#?	equivalent charge of Coss
								'Eoss'						:	Eoss																					,	#?	equivalent energy of Coss
								'Config'					:	5																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
						},
							'Crss'					:	{																									#!	device Crss parameters
                                'C'							:	Crss_eff					 															,	#?	device parasitic reverse transfer capacitance
								'R'							:	0																						,	#?	Crss resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Crss inductance to reduce current slope
								'Crss_er'					:	Crss_er																					,	#?	energy-related Crss
								'Crss_tr'					:	Crss_tr																					,	#?	time-related Crss
								'Vvec'						:	Crss[0]																					,	#?	device Crss voltage vector
                                'Cvec'						:	Crss[1]																					,	#?	device Crss capacity vector
								'Qvec'						:	Qrss																					,	#?	device accumulated Crss charge vector
								'Offset'					:	0																						,	#?	parasitic offset to Crss
								'Factor'					:	1.0																						,	#?	parasitic tolerance to Crss
								'Qrss'						:	Qrss																					,	#?	equivalent charge of Crss
								'Erss'						:	Erss																					,	#?	equivalent energe of Crss
								'Config'					:	5																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
						},
							'Ciss'					:	{																									#!	device Ciss parameters
								'C'							:	Ciss_eff					 															,	#?	device parasitic input capacitance
								'R'							:	0																						,	#?	Ciss resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Ciss inductance to reduce current slope
								'Ciss_er'					:	Ciss_er																					,	#?	energy-related Ciss
								'Ciss_tr'					:	Ciss_tr																					,	#?	time-related Ciss
								'Vvec'						:	Ciss[0]																					,	#?	device Ciss voltage vector
								'Cvec'						:	Ciss[1]																					,	#?	device Ciss capacity vector
								'Offset'					:	0																						,	#?	parasitic offset to Ciss
								'Factor'					:	1.0																						,	#?	parasitic tolerance to Ciss
								'Qiss'						:	Qiss																					,	#?	equivalent charge of Ciss
								'Eiss'						:	Eiss																					,	#?	equivalent energy of Ciss
								'Config'					:	5																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Cds'					:	{																									#!	device Cds parameters
								'C'							:	Cds_eff					 																,	#?	device parasitic Cds capacitance
								'R'							:	0																						,	#?	Cds resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Cds inductance to reduce current slope
								'Cds_er'					:	Cds_er																					,	#?	energy-related Cds
								'Cds_tr'					:	Cds_tr																					,	#?	time-related Cds
								'Vvec'						:	Coss[0]																					,	#?	device Cds voltage vector
								'Cvec'						:	Cds																						,	#?	device Cds capacity vector
								'Offset_ON'					:	0																						,	#?	tuning offset for turn ON
								'Offset_OFF'				:	0																						,	#?	tuning offset for turn OFF
								'Factor_ON'					:	1.0																						,	#?	tuning factor for turn ON
								'Factor_OFF'				:	1.0																						,	#?	tuning factor for turn OFF
								'Config'					:	4																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Cgd'					:	{																									#!	device Cgd parameters
								'C'							:	Cgd_eff							 														,	#?	device parasitic Cgd capacitance
								'R'							:	0																						,	#?	Cgd resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Cgd inductance to reduce current slope
								'Cgd_er'					:	Cgd_er																					,	#?	energy-related Cgd
								'Cgd_tr'					:	Cgd_tr																					,	#?	time-related Cgd
								'Vvec'						:	Crss[0]																					,	#?	device Cgd voltage vector
								'Cvec'						:	Cgd																						,	#?	device Cgd capacity vector
								'Offset_ON'					:	0																						,	#?	tuning offset for turn ON
								'Offset_OFF'				:	0																						,	#?	tuning offset for turn OFF
								'Factor_ON'					:	1.0																						,	#?	tuning factor for turn ON
								'Factor_OFF'				:	1.0																						,	#?	tuning factor for turn OFF
								'Config'					:	4																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Cgs'					:	{																									#!	device Cgs parameters
								'C'							:	Cgs_eff					 																,	#?	device parasitic Cgs capacitance
								'R'							:	0																						,	#?	Cgs resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Cgs inductance to reduce current slope
								'Cgs_er'					:	Cgs_er																					,	#?	energy-related Cgs
								'Cgs_tr'					:	Cgs_tr																					,	#?	time-related Cgs
								'Vvec'						:	Ciss[0]																					,	#?	device Cgs voltage vector
								'Cvec'						:	Cgs																						,	#?	device Cgs capacity vector
								'Offset_ON'					:	0																						,	#?	tuning offset for turn ON
								'Offset_OFF'				:	0																						,	#?	tuning offset for turn OFF
								'Factor_ON'					:	1.0																						,	#?	tuning factor for turn ON
								'Factor_OFF'				:	1.0																						,	#?	tuning factor for turn OFF
								'Config'					:	4																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Eoff'					:	{																									#!	transistor turn-OFF energy losses
									'Ivec'					:	Ioff																					,	#?	turn-OFF energy current vector
									'Rgvec'					:	[0,100]																					,	#?	OFF path gate resistances vector
									'Tjvec'					:	[-55,175]																				,	#?	junction temperature vector
                                    'Vvec'					:	Voff																					,	#?	turn-OFF voltage vector
                                    'Evec'					:	Eoff																					,	#?	turn-OFF energy vectors
									'Evec_Temp'				:	Eoff_Temp																				,	#?	turn-OFF energy temp scaling vectors
                                    'CAT'					:	catOFF																					,	#?	octave Eoff energy syntax
									'CAT_Temp'				:	catOFF_Temp																				,	#?	octave Eoff energy temp scaling syntax
									'Vgs'					:	0																						,	#?	used OFF path gate-source voltage
									'Vth'					:	1.5																						,	#?	used OFF path threshold voltage
									'Rg'					:	0																							#?	used OFF path gate resistance
						},
							'Eon'					:	{																									#!	transistor turn-ON energy losses
									'Ivec'					:	Ion																						,	#?	turn-ON energy current vector
									'Rgvec'					:	[0,100]																					,	#?	ON path gate resistances vector
									'Tjvec'					:	[-55,175]																				,	#?	junction temperature vector
                                    'Vvec'					:	Von																						,	#?	turn-ON voltage vector
                                    'Evec'					:	Eon																						,	#?	turn-ON energy vectors
									'Evec_Temp'				:	Eon_Temp																				,	#?	turn-ON energy temp scaling vectors
                                    'CAT'					:	catON																					,	#?	octave Eon energy syntax
									'CAT_Temp'				:	catON_Temp																				,	#?	octave Eon energy temp scaling syntax
									'Vgs'					:	12																						,	#?	used ON path gate-source voltage
									'Vth'					:	1.5																						,	#?	used ON path threshold voltage
									'Rg'					:	0																							#?	used ON path gate resistance
						},
							'Tau_deg'						:	100e-9																					,	#?	deglitch filter for currents and voltages
							'RCsnubber'						:	2																						,	#?	1->enable | 2->disable
						}

#?----------------------------------------------------------------------------------------------------------------------------------------------------------------------

Coss,Qoss,Eoss,Coss_tr,Coss_er		=	paramProcess.MOSFETcaps(switchesCossPath,'AIMDQ75R060M1H','_Coss')
Crss,Qrss,Erss,Crss_tr,Crss_er 		=	paramProcess.MOSFETcaps(switchesCrssPath,'AIMDQ75R060M1H','_Crss')
Ciss,Qiss,Eiss,Ciss_tr,Ciss_er 		=	paramProcess.MOSFETcaps(switchesCissPath,'AIMDQ75R060M1H','_Ciss')
Coss_eff 							=	paramProcess.getCmos(Coss,Coss_tr,Coss_er,Coss[0][0],True)
Ciss_eff 							=	paramProcess.getCmos(Ciss,Ciss_tr,Ciss_er,Ciss[0][0],True)
Crss_eff 							=	paramProcess.getCmos(Crss,Crss_tr,Crss_er,Crss[0][0],True)
Cds 						        =	(np.array(Coss[1]) - np.array(Crss[1])).tolist()
Cgs						        	=	(np.array(Ciss[1]) - np.array(Crss[1])).tolist()
Cgd						        	=	Crss[1]
Cds_tr						        =	(np.array(Coss_tr) - np.array(Crss_tr)).tolist()
Cgs_tr						        =	(np.array(Ciss_tr) - np.array(Crss_tr)).tolist()
Cgd_tr						        =	Crss_tr
Cds_er						        =	(np.array(Coss_er) - np.array(Crss_er)).tolist()
Cgs_er						        =	(np.array(Ciss_er) - np.array(Crss_er)).tolist()
Cgd_er						        =	Crss_er
Cds_eff 							=	paramProcess.getCmos([Coss[0],Cds],Cds_tr,Cds_er,Coss[0][0],True)
Cgs_eff 							=	paramProcess.getCmos([Ciss[0],Cgs],Cgs_tr,Cgs_er,Ciss[0][0],True)
Cgd_eff 							=	Crss_eff
Rvec,Tvec							=	paramProcess.MOSFETrdson(switchesRdsonPath,'AIMDQ75R060M1H','_Rdson')
Nvec,Ivec 							=	paramProcess.MOSFETrdson(switchesIdsonPath,'AIMDQ75R060M1H','_Rdson')
Ioff,catOFF,Eoff					=	paramProcess.MOSFETenergies(switchesEoffPath,'AIMDQ75R060M1H','_Eoff')
Voff,catOFF_Temp,Eoff_Temp			=	paramProcess.MOSFETenergies(switchesEoffPath,'AIMDQ75R060M1H','_Eoff_Temp')
Ion,catON,Eon 						=	paramProcess.MOSFETenergies(switchesEonPath,'AIMDQ75R060M1H','_Eon')
Von,catON_Temp,Eon_Temp				=	paramProcess.MOSFETenergies(switchesEonPath,'AIMDQ75R060M1H','_Eon_Temp')
Vfvec,Ifvec,Rd,Vt					=	paramProcess.DiodeVI_data(bodyDiodeVIPath,'AIMDQ75R060M1H')
Vds_vec,Ids_vec 					=	paramProcess.Forward_Transfer_data(switchesTransferPath,'AIMDQ75R060M1H')

AIMDQ75R060M1H		=	{																																	#*	AIMDQ75R060M1H parameters
							'Config'						:	1																						,	#!	1->electric integrated | 2->electric separate | 3->thermal integrated | 4->thermal separate
							'Transistor'  			: 	{																									#!	transistors parameters
									'Config'				:	2																						,	#?	1->real model | 2->ideal model | 3->behavioral model
									'Thermal'           	:   ''                                  													,   #? 	selected transistor
									'Custom'            	:   []                 																		,   #? 	transistor provided custom variables
									'g_fs'					:	8.3																						,	#?	forward transconductance
									'Rg'					:	7.0																						,	#?	internal gate resistance
									'Lg'					:	9.52e-9*0																				,	#?	gate pin inductance
									'Rds_on'            	:   Rvec[-1][-1]*1e-3																		,   #? 	transistor ON resistance
									'Rds_off'				:	'inf'																					,	#?	transistor OFF resistance
									'Rvec'					:	(np.array(Rvec)*1e-3).tolist()														,	#?	absolute Rdson vector corresponding to junction temperature
									'Tvec'					:	Tvec 																					,	#?	junction temperature vector for Rdson
									'RTconfig'				:	1																						,	#?	choose which RT vector to be used
									'RdsonScale'			:	1.0																						,	#?	Rdson scaling to account for min, typ and max deviations
									'Nvec'					:	Nvec 																					,	#?	normalized Rdson vector corresponding to current
									'Ivec'					:	Ivec																					,	#?	current vector for normalized Rdson
									'NIconfig'				:	2																						,	#?	choose which NI vector to be used (Vgs=15,18,20)
									'IdsonScale'			:	1.0																						,	#?	Idson resistance scaling to account for min, typ and max deviations
									'Rsrc'					:	47.2e-3*0																				,	#?	kelvin source pin resistance
									'Lsrc'					:	5.57e-9*0																				,	#?	kelvin source pin inductance
									'Ls'					:	4.62e-9*0																				,	#?	package source inductance
                                    'Ld'					:	2.19e-9*0																				,	#?	package drain inductance
									'Rs'					:	993e-6*0																				,	#?	package source resistance
									'Rd'					:	46.3e-6*0																				,	#?	package drain inductance
									'Ksrc'					:	1																						,	#?	kelvin source option, 0->no kelvin | 1->kelvin
									'Vblock'            	:   750                                	 													,   #? 	transistor blocking voltage
									'Id'                	:   32	                                 													,   #? 	transistor drain current
									'Tr'                	:   0                                   													,   #? 	transistor rise time
									'Tf'                	:   0                                       												, 	#? 	transistor fall time
									'Avalanche'		:	{																									#!	transistor avalanche parameters
										'Config'			:	2																						,	#?	1->enable | 2->disable
										'Voltage'			:	750 																					,	#?	avalanche voltage
										'Resistance'		:	1e-3																						#?	avalanche resistance to break voltage state-dependency
									},
									'Transfer'		:	{																									#!	transistor forward transfer parameters
										'Vds'				:	Vds_vec																					,	#?	drain-source voltage vector
										'Vgs'				:	list(np.arange(0.0,21.0,0.35))														,	#?	gate-source voltage vector
										'Ids'				:	Ids_vec																					,	#?	drain current vector
										'Factor_ON'			:	1.0																						,	#?	scaling factor for Ids at turn ON
										'Factor_OFF'		:	1.0																						,	#?	scaling factor for Ids at turn OFF
										'Factor_Vgs_ON'		:	1.0																						,	#?	scaling factor for Vgs at turn ON
										'Factor_Vgs_OFF'	:	1.0																						,	#?	scaling factor for Vgs at turn OFF
										'Vcoss'				:	0																						,	#?	initial voltage of the Coss
									},
						},
							'BodyDiode'  			:	{																									#!	body diodes paramteters
									'Config'				:	4																						,	#?	1->non-ideal RR | 2->non-ideal | 3->ideal RR | 4->ideal
									'Thermal'           	:   ''                                  													,   #? 	separate body diode
									'Custom'            	:   []					                 													,   #? 	body diode provided custrom variables
									'Rd_on'             	:   Rd[-1]													                              	,  	#? 	body diode ON resistance
									'Rd_off'				:	'inf'																					,	#?	body diode OFF resistance
									'Vf'					:	Vt[-1]																					,	#? 	body diode forward voltage
									'If'                	:   32	                                 													,   #? 	body diode forward current
									'dIr'               	:   1000e6                                 													,   #? 	body diode current slope
									'Lrr'					:	1e-9																					,	#?	body diode reverse recovery inductance
									'Trr'               	:   16e-9                                  													,   #? 	body diode reverse recovery time
									'Irr'               	:   0                                      													,   #? 	body diode reverse recovery current
									'Qrr'               	:   57e-9			                              											,	#? 	body diode reverse recovery charge
									'Is'                  	:   11.1              																		, 	#? 	body diode reference current
									'Vs'					:	500																						,	#?	body diode reference voltage
                                    'VIcurve'		:	{																									#!	body diode VI characteristics
                                        'Vfvec'				:	Vfvec																					,	#?	forward voltage vector
                                        'Ifvec'				:	Ifvec																					,	#?	forward current vector
										'Rdvec'				:	Rd																						,	#?	dynamic resistance vector
										'Vtvec'				:	Vt																						,	#?	threshold voltage vector
                                        'Temps'				:	[25,175]																				,	#?	temperature vector
                                        'Vfscale'			:	1.359																						#?	Vf scaling to account for min, typ and max deviations
									},
						},
							'GateDriver'			:	{																									#!	gate driver parameters
									'Config'				:	3																						,	#?	1->high-side | 2->low-side | 3->disable
									'Von'					:	18																						,	#?	ON driving voltage
									'Voff'					:	0																						,	#?	OFF driving voltage
									'Ron'					:	5																						,	#?	sourcing output resistance
									'Roff'					:	0.55																					,	#?	sinking output resistance
									'Lon'					:	0																						,	#?	sourcing output inductance
									'Loff'					:	0																						,	#?	sinking output inductance
									'Cload'					:	0																						,	#?	capacitive load on output
									'Rload'					:	'inf'																					,	#?	resistive load on output
									'Delay'					:	0																						,	#?	input-to-output total deadtime
									'Trise'					:	0																						,	#?	output rising time
									'Tfall'					:	0																						,	#?	output falling time
									'UVLO_Start'			:	7.0																						,	#?	UVLO startup voltage threshold
									'UVLO_Stop'				:	6.5																						,	#?	UVLO shutdown voltage threshold
									'UVLO_Delay'			:	100e-9																					,	#?	delay between UVLO startup and shutdown
									'Init_State'			:	0																						,	#?	initial toggling state, 0->OFF | 1->ON
									'CurrentLimit'	:	{																									#*	current limit of driver stage
										'Config'			:	2																						,	#?	1->enable | 2->disable
										'Ts'				: 	0 																						,	#?	sampling time between inductive & capacitive links
										'tau'				: 	0																						,	#?	first-order delay between inductive & capacitive links
                                    	'Rs'				: 	0																						,	#?	source impedance of inductive link
										'Cs'				:	1e-12																					,	#?	source capacitance of capacitive link
                                        'UpLim'				: 	10																						,	#?	max current limit on capacitive link
                                        'LoLim'				: 	-10																						,	#?	min current limit on capacitive link
                                        'Voffset'			: 	0																							#?	voltage offset between inductive & capacitive links
									},
									'Masking'		:	{																									#*	switching stages masking
										'ON'	:	{																										#	ON path masking
											'Config'		:	2																						,	#?	1->enable | 2->disable
											'HIGH'	:	{																									#!	HIGH mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[0, 0]																						#?	mask output
											},
											'LOW'	:	{																									#!	LOW mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[1, 1]																						#?	mask output
											}
										},
										'OFF'	:	{																										#	OFF path masking
											'Config'		:	2																						,	#?	1->enable | 2->disable
											'HIGH'	:	{																									#!	HIGH mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[0, 0]																						#?	mask output
											},
											'LOW'	:	{																									#!	LOW mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[1, 1]																						#?	mask output
											}
										}
									},
									'Boot'			:	{																									#*	bootstrap/charge pump parameters
										'Config'			:	1																						,	#?	1->bootstrap | 2->charge pump
										'Von'				:	14																						,	#?	boostrap driving voltage
										'Cboot'				:	4.7e-6																					,	#?	bootstrap capacitance
										'Vinit'				:	0																						,	#?	bootstrap capacitance initial voltage
										'Rboot'				:	10																						,	#?	bootstrap resistance
										'Vfboot'			:	0.87																					,	#?	bootstrap diode forward voltage
										'Rdboot'			:	1e-3																					,	#?	bootstrap diode ON-state resistance
										'Ichrg'				:	300e-6																					,	#?	charge pump supply current
										'Idis'				:	5e-6																					,	#?	charge pump loading or leakage current
										'Cpar'				:	0																						,	#?	charge pump parallel cap to break state/source dependency
									    'UVLO_Start'		:	11.6																					,	#?	threshold value to start the charge pump
										'UVLO_Stop'			:	12.4																						#?	threshold value to stop the charge pump
									},
							},
							'GateNetwork'			:	{																									#!	gate drive circuit parameters
									'Config'				:	2																						,	#?	1-> enable | 2->disable
									'ON_Path'		:	{																									#*	sourcing path parameters
										'Rg'				:	10																						,	#?	gate ON path resistance
										'Lg'				:	0																						,	#?	gate ON path inductance
										'Rload'				:	10e3																					,	#?	gate pull down resistance
										'Diode'	:	{																										#	reverse blocking diode parameters
											'Vf'			:	0																						,	#?	forward voltage
											'Rd_on'			:	0																						,	#?	ON-state resistance
										},
									},
									'OFF_Path'		:	{																									#*	sinking path parameters
										'Rg'				:	10																						,	#?	gate OFF path resistance
										'Lg'				:	0																						,	#?	gate OFF path inductance
										'Diode'	:	{																										#	reverse blocking diode parameters
											'Vf'			:	0																						,	#?	forward voltage
											'Rd_on'			:	0																						,	#?	ON-state resistance
										},
									},
									'NegVolt'		:	{																									#*	negative voltage generator parameters
										'Config'			:	2																						,	#?	1-> enable | 2->disable
										'Dz'	:	{																										#	zener diode parameters
											'Vf'			:	0.7																						,	#?	forward voltage
											'Rd_on'			:	1e-3																					,	#?	ON-state resistance
											'Vz'			:	2																						,	#?	Zener breakdown voltage
											'Rz'			:	1e-3																					,	#?	Zener resistance
										},
										'Dp'	:	{																										#	peak detector diode
											'Vf'			:	0.0																						,	#?	forward voltage
											'Rd_on'			:	0.0																						,	#?	ON-state resistance
										},
										'Cz'	:	{																										#	Zener capacitor parameters
											'Config'		:	1																						,	#?	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
											'Csingle'		:	1e-6																					,	#?	single capacitor value
											'Rsingle'		:	5e-3																					,	#?	ESR of single capacitor
											'Lsingle'		:	0																						,	#?	ESL of single capacitor
											'nPar'			:	1																						,	#?	number of parallel connections
											'nSer'			:	1																						,	#?	number of series connections
											'Vinit'			:	0																						,	#?	capacitor initial voltage
										},
										'Cp'	:	{																										#	peak detector capacitor parameters
											'Config'		:	1																						,	#?	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
											'Csingle'		:	2.2e-6																					,	#?	single capacitor value
											'Rsingle'		:	5e-3																					,	#?	ESR of single capacitor
											'Lsingle'		:	0																						,	#?	ESL of single capacitor
											'nPar'			:	1																						,	#?	number of parallel connections
											'nSer'			:	1																						,	#?	number of series connections
											'Vinit'			:	0																						,	#?	capacitor initial voltage
										},
										'Rp1'				:	43																						,	#?	current limiter of peak detector current
										'Rp2'				:	4.7e3																					,	#?	load resistor to charge the zener diode
									},
								},
							'nParallel'   					:	1                                       												,   #? 	number of parallel devices
							'Rth_jc'						:	0.90																					,	#?	junction-to-case thermal resistance
							'Cth_jc'						:	0.00																					,	#?	junction-to-case thermal capacitance
							'Rth_ca'              			:   [1.0682,1.2039,0.7389,0.427] 															,   #? 	case-to-ambient thermal resistance
							'Cth_ca'              			:   [12.8939,1.6758,0.0755,169.4661]            											,   #? 	case-to-ambient thermal capacitance
							'Tinit'							:	0.0																						,	#?	initial juntion temperature
							'Pinit'							:	0.0																						,	#?	initial power dissipation
							'Coss'					: 	{																									#!	device Coss parameters
								'C'							:	Coss_eff					 															,	#?	device parasitic output capacitance
								'R'							:	0																						,	#?	Coss resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Coss inductance to reduce current slope
								'Coss_er'					:	Crss_er																					,	#?	energy-related Coss
								'Coss_tr'					:	Coss_tr																					,	#?	time-related Coss
								'Vvec'						:	Coss[0]																					,	#? 	device Coss voltage vector
								'Cvec'						:	Coss[1]																					,	#?	device Coss capacity vector
								'Offset'					:	0*25.0e-12																				,	#?	parasitic offset to Coss
                                'Factor'					:	1.0																						,	#?	parasitic tolerance to Coss
								'Qoss'						:	Qoss																					,	#?	equivalent charge of Coss
								'Eoss'						:	Eoss																					,	#?	equivalent energy of Coss
								'Config'					:	5																							#?	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
						},
                        	'Crss'					:	{																									#!	device Crss parameters
                                'C'							:	Crss_eff					 															,	#?	device parasitic reverse transfer capacitance
								'R'							:	0																						,	#?	Crss resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Crss inductance to reduce current slope
								'Crss_er'					:	Crss_er																					,	#?	energy-related Crss
								'Crss_tr'					:	Crss_tr																					,	#?	time-related Crss
								'Vvec'						:	Crss[0]																					,	#?	device Crss voltage vector
                                'Cvec'						:	Crss[1]																					,	#?	device Crss capacity vector
								'Qvec'						:	Qrss																					,	#?	device accumulated Crss charge vector
								'Offset'					:	0																						,	#?	parasitic offset to Crss
								'Factor'					:	1.0																						,	#?	parasitic tolerance to Crss
								'Qrss'						:	Qrss																					,	#?	equivalent charge of Crss
								'Erss'						:	Erss																					,	#?	equivalent energe of Crss
								'Config'					:	5																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
						},
							'Ciss'					:	{																									#!	device Ciss parameters
								'C'							:	Ciss_eff					 															,	#?	device parasitic input capacitance
								'R'							:	0																						,	#?	Ciss resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Ciss inductance to reduce current slope
								'Ciss_er'					:	Ciss_er																					,	#?	energy-related Ciss
								'Ciss_tr'					:	Ciss_tr																					,	#?	time-related Ciss
								'Vvec'						:	Ciss[0]																					,	#?	device Ciss voltage vector
								'Cvec'						:	Ciss[1]																					,	#?	device Ciss capacity vector
								'Offset'					:	0																						,	#?	parasitic offset to Ciss
								'Factor'					:	1.0																						,	#?	parasitic tolerance to Ciss
								'Qiss'						:	Qiss																					,	#?	equivalent charge of Ciss
								'Eiss'						:	Eiss																					,	#?	equivalent energy of Ciss
								'Config'					:	5																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Cds'					:	{																									#!	device Cds parameters
								'C'							:	Cds_eff					 																,	#?	device parasitic Cds capacitance
								'R'							:	0																						,	#?	Cds resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Cds inductance to reduce current slope
								'Cds_er'					:	Cds_er																					,	#?	energy-related Cds
								'Cds_tr'					:	Cds_tr																					,	#?	time-related Cds
								'Vvec'						:	Coss[0]																					,	#?	device Cds voltage vector
								'Cvec'						:	Cds																						,	#?	device Cds capacity vector
								'Offset_ON'					:	0																						,	#?	tuning offset for turn ON
								'Offset_OFF'				:	0																						,	#?	tuning offset for turn OFF
								'Factor_ON'					:	1.0																						,	#?	tuning factor for turn ON
								'Factor_OFF'				:	1.0																						,	#?	tuning factor for turn OFF
								'Config'					:	4																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Cgd'					:	{																									#!	device Cgd parameters
								'C'							:	Cgd_eff							 														,	#?	device parasitic Cgd capacitance
								'R'							:	0																						,	#?	Cgd resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Cgd inductance to reduce current slope
								'Cgd_er'					:	Cgd_er																					,	#?	energy-related Cgd
								'Cgd_tr'					:	Cgd_tr																					,	#?	time-related Cgd
								'Vvec'						:	Crss[0]																					,	#?	device Cgd voltage vector
								'Cvec'						:	Cgd																						,	#?	device Cgd capacity vector
								'Offset_ON'					:	0																						,	#?	tuning offset for turn ON
								'Offset_OFF'				:	0																						,	#?	tuning offset for turn OFF
								'Factor_ON'					:	1.0																						,	#?	tuning factor for turn ON
								'Factor_OFF'				:	1.0																						,	#?	tuning factor for turn OFF
								'Config'					:	4																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Cgs'					:	{																									#!	device Cgs parameters
								'C'							:	Cgs_eff					 																,	#?	device parasitic Cgs capacitance
								'R'							:	0																						,	#?	Cgs resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Cgs inductance to reduce current slope
								'Cgs_er'					:	Cgs_er																					,	#?	energy-related Cgs
								'Cgs_tr'					:	Cgs_tr																					,	#?	time-related Cgs
								'Vvec'						:	Ciss[0]																					,	#?	device Cgs voltage vector
								'Cvec'						:	Cgs																						,	#?	device Cgs capacity vector
								'Offset_ON'					:	0																						,	#?	tuning offset for turn ON
								'Offset_OFF'				:	0																						,	#?	tuning offset for turn OFF
								'Factor_ON'					:	1.0																						,	#?	tuning factor for turn ON
								'Factor_OFF'				:	1.0																						,	#?	tuning factor for turn OFF
								'Config'					:	4																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Eoff'					:	{																									#!	transistor turn-OFF energy losses
									'Ivec'					:	Ioff																					,	#?	turn-OFF energy current vector
                                    'Rgvec'					:	[1.0,2.2,4.7,10.0,22.0,47.0,100.0]														,	#?	OFF path gate resistances vector
									'Tjvec'					:	[-55,25,75,150,175]																		,	#?	junction temperature vector
                                    'Vvec'					:	Voff																					,	#?	turn-OFF voltage vector
                                    'Evec'					:	Eoff																					,	#?	turn-OFF energy vectors
									'Evec_Temp'				:	Eoff_Temp																				,	#?	turn-OFF energy temp scaling vectors
                                    'CAT'					:	catOFF																					,	#?	octave Eoff energy syntax
									'CAT_Temp'				:	catOFF_Temp																				,	#?	octave Eoff energy temp scaling syntax
									'Vgs'					:	0																						,	#?	used OFF path gate-source voltage
									'Vth'					:	4.3																						,	#?	used OFF path threshold voltage
									'Rg'					:	10.0																						#?	used OFF path gate resistance
						},
							'Eon'					:	{																									#!	transistor turn-ON energy losses
									'Ivec'					:	Ion																						,	#?	turn-ON energy current vector
									'Rgvec'					:	[1.0,2.2,4.7,10.0,22.0,47.0,100.0]														,	#?	ON path gate resistances vector
									'Tjvec'					:	[-55,25,75,150,175]																		,	#?	junction temperature vector
                                    'Vvec'					:	Von																						,	#?	turn-ON voltage vector
                                    'Evec'					:	Eon																						,	#?	turn-ON energy vectors
									'Evec_Temp'				:	Eon_Temp																				,	#?	turn-ON energy temp scaling vectors
                                    'CAT'					:	catON																					,	#?	octave Eon energy syntax
									'CAT_Temp'				:	catON_Temp																				,	#?	octave Eon energy temp scaling syntax
									'Vgs'					:	18																						,	#?	used ON path gate-source voltage
									'Vth'					:	4.3																						,	#?	used ON path threshold voltage
									'Rg'					:	10.0																						#?	used ON path gate resistance
						},
							'Tau_deg'						:	100e-9																					,	#?	deglitch filter for currents and voltages
							'RCsnubber'						:	2																						,	#?	1->enable | 2->disable
						}

#?----------------------------------------------------------------------------------------------------------------------------------------------------------------------

Coss,Qoss,Eoss,Coss_tr,Coss_er		=	paramProcess.MOSFETcaps(switchesCossPath,'AIMDQ75R060M2H','_Coss')
Crss,Qrss,Erss,Crss_tr,Crss_er 		=	paramProcess.MOSFETcaps(switchesCrssPath,'AIMDQ75R060M2H','_Crss')
Ciss,Qiss,Eiss,Ciss_tr,Ciss_er 		=	paramProcess.MOSFETcaps(switchesCissPath,'AIMDQ75R060M2H','_Ciss')
Coss_eff 							=	paramProcess.getCmos(Coss,Coss_tr,Coss_er,Coss[0][0],True)
Ciss_eff 							=	paramProcess.getCmos(Ciss,Ciss_tr,Ciss_er,Ciss[0][0],True)
Crss_eff 							=	paramProcess.getCmos(Crss,Crss_tr,Crss_er,Crss[0][0],True)
Cds 						        =	(np.array(Coss[1]) - np.array(Crss[1])).tolist()
Cgs						        	=	(np.array(Ciss[1]) - np.array(Crss[1])).tolist()
Cgd						        	=	Crss[1]
Cds_tr						        =	(np.array(Coss_tr) - np.array(Crss_tr)).tolist()
Cgs_tr						        =	(np.array(Ciss_tr) - np.array(Crss_tr)).tolist()
Cgd_tr						        =	Crss_tr
Cds_er						        =	(np.array(Coss_er) - np.array(Crss_er)).tolist()
Cgs_er						        =	(np.array(Ciss_er) - np.array(Crss_er)).tolist()
Cgd_er						        =	Crss_er
Cds_eff 							=	paramProcess.getCmos([Coss[0],Cds],Cds_tr,Cds_er,Coss[0][0],True)
Cgs_eff 							=	paramProcess.getCmos([Ciss[0],Cgs],Cgs_tr,Cgs_er,Ciss[0][0],True)
Cgd_eff 							=	Crss_eff
Rvec,Tvec							=	paramProcess.MOSFETrdson(switchesRdsonPath,'AIMDQ75R060M2H','_Rdson')
Nvec,Ivec 							=	paramProcess.MOSFETrdson(switchesIdsonPath,'AIMDQ75R060M2H','_Rdson')
Ioff,catOFF,Eoff					=	paramProcess.MOSFETenergies(switchesEoffPath,'AIMDQ75R060M2H','_Eoff')
Voff,catOFF_Temp,Eoff_Temp			=	paramProcess.MOSFETenergies(switchesEoffPath,'AIMDQ75R060M2H','_Eoff_Temp')
Ion,catON,Eon 						=	paramProcess.MOSFETenergies(switchesEonPath,'AIMDQ75R060M2H','_Eon')
Von,catON_Temp,Eon_Temp				=	paramProcess.MOSFETenergies(switchesEonPath,'AIMDQ75R060M2H','_Eon_Temp')
Vfvec,Ifvec,Rd,Vt					=	paramProcess.DiodeVI_data(bodyDiodeVIPath,'AIMDQ75R060M2H')
Vds_vec,Ids_vec 					=	paramProcess.Forward_Transfer_data(switchesTransferPath,'AIMDQ75R060M2H')

AIMDQ75R060M2H		=	{																																	#*	AIMDQ75R060M2H parameters
							'Config'						:	1																						,	#!	1->electric integrated | 2->electric separate | 3->thermal integrated | 4->thermal separate
							'Transistor'  			: 	{																									#!	transistors parameters
									'Config'				:	2																						,	#?	1->real model | 2->ideal model | 3->behavioral model
									'Thermal'           	:   ''                                  													,   #? 	selected transistor
									'Custom'            	:   []                 																		,   #? 	transistor provided custom variables
									'g_fs'					:	8.3																						,	#?	forward transconductance
									'Rg'					:	4.5																						,	#?	internal gate resistance
									'Lg'					:	9.52e-9*0																				,	#?	gate pin inductance
									'Rds_on'            	:   Rvec[-1][-1]*1e-3																		,   #? 	transistor ON resistance
									'Rds_off'				:	'inf'																					,	#?	transistor OFF resistance
									'Rvec'					:	(np.array(Rvec)*1e-3).tolist()														,	#?	absolute Rdson vector corresponding to junction temperature
									'Tvec'					:	Tvec 																					,	#?	junction temperature vector for Rdson
									'RTconfig'				:	1																						,	#?	choose which RT vector to be used
									'RdsonScale'			:	1.0																						,	#?	Rdson scaling to account for min, typ and max deviations
									'Nvec'					:	Nvec 																					,	#?	normalized Rdson vector corresponding to current
									'Ivec'					:	Ivec																					,	#?	current vector for normalized Rdson
									'NIconfig'				:	2																						,	#?	choose which NI vector to be used (Vgs=15,18,20)
									'IdsonScale'			:	1.0																						,	#?	Idson resistance scaling to account for min, typ and max deviations
									'Rsrc'					:	47.2e-3*0																				,	#?	kelvin source pin resistance
									'Lsrc'					:	5.57e-9*0																				,	#?	kelvin source pin inductance
									'Ls'					:	4.62e-9*0																				,	#?	package source inductance
                                    'Ld'					:	2.19e-9*0																				,	#?	package drain inductance
									'Rs'					:	993e-6*0																				,	#?	package source resistance
									'Rd'					:	46.3e-6*0																				,	#?	package drain inductance
									'Ksrc'					:	1																						,	#?	kelvin source option, 0->no kelvin | 1->kelvin
									'Vblock'            	:   750                                	 													,   #? 	transistor blocking voltage
									'Id'                	:   30	                                 													,   #? 	transistor drain current
									'Tr'                	:   0                                   													,   #? 	transistor rise time
									'Tf'                	:   0                                       												, 	#? 	transistor fall time
									'Avalanche'		:	{																									#!	transistor avalanche parameters
										'Config'			:	2																						,	#?	1->enable | 2->disable
										'Voltage'			:	750 																					,	#?	avalanche voltage
										'Resistance'		:	1e-3																						#?	avalanche resistance to break voltage state-dependency
									},
									'Transfer'		:	{																									#!	transistor forward transfer parameters
										'Vds'				:	Vds_vec																					,	#?	drain-source voltage vector
										'Vgs'				:	list(np.arange(0.0,21.0,0.35))														,	#?	gate-source voltage vector
										'Ids'				:	Ids_vec																					,	#?	drain current vector
										'Factor_ON'			:	1.0																						,	#?	scaling factor for Ids at turn ON
										'Factor_OFF'		:	1.0																						,	#?	scaling factor for Ids at turn OFF
										'Factor_Vgs_ON'		:	1.0																						,	#?	scaling factor for Vgs at turn ON
										'Factor_Vgs_OFF'	:	1.0																						,	#?	scaling factor for Vgs at turn OFF
										'Vcoss'				:	0																						,	#?	initial voltage of the Coss
									},
						},
							'BodyDiode'  			:	{																									#!	body diodes paramteters
									'Config'				:	4																						,	#?	1->non-ideal RR | 2->non-ideal | 3->ideal RR | 4->ideal
									'Thermal'           	:   ''                                  													,   #? 	separate body diode
									'Custom'            	:   []					                 													,   #? 	body diode provided custrom variables
									'Rd_on'             	:   Rd[-1]													                              	,  	#? 	body diode ON resistance
									'Rd_off'				:	'inf'																					,	#?	body diode OFF resistance
									'Vf'					:	Vt[-1]																					,	#? 	body diode forward voltage
									'If'                	:   30	                                 													,   #? 	body diode forward current
									'dIr'               	:   4000e6                                 													,   #? 	body diode current slope
									'Lrr'					:	1e-9																					,	#?	body diode reverse recovery inductance
									'Trr'               	:   5.4e-9                                 													,   #? 	body diode reverse recovery time
									'Irr'               	:   16*0                                   													,   #? 	body diode reverse recovery current
									'Qrr'               	:   44e-9			                              											,	#? 	body diode reverse recovery charge
									'Is'                  	:   13.8              																		, 	#? 	body diode reference current
									'Vs'					:	500																						,	#?	body diode reference voltage
                                    'VIcurve'		:	{																									#!	body diode VI characteristics
                                        'Vfvec'				:	Vfvec																					,	#?	forward voltage vector
                                        'Ifvec'				:	Ifvec																					,	#?	forward current vector
										'Rdvec'				:	Rd																						,	#?	dynamic resistance vector
										'Vtvec'				:	Vt																						,	#?	threshold voltage vector
                                        'Temps'				:	[25,75,150]																				,	#?	temperature vector
                                        'Vfscale'			:	1.25																						#?	Vf scaling to account for min, typ and max deviations
									},
						},
							'GateDriver'			:	{																									#!	gate driver parameters
									'Config'				:	3																						,	#?	1->high-side | 2->low-side | 3->disable
									'Von'					:	18																						,	#?	ON driving voltage
									'Voff'					:	0																						,	#?	OFF driving voltage
									'Ron'					:	5																						,	#?	sourcing output resistance
									'Roff'					:	0.55																					,	#?	sinking output resistance
									'Lon'					:	0																						,	#?	sourcing output inductance
									'Loff'					:	0																						,	#?	sinking output inductance
									'Cload'					:	0																						,	#?	capacitive load on output
									'Rload'					:	'inf'																					,	#?	resistive load on output
									'Delay'					:	0																						,	#?	input-to-output total deadtime
									'Trise'					:	0																						,	#?	output rising time
									'Tfall'					:	0																						,	#?	output falling time
									'UVLO_Start'			:	7.0																						,	#?	UVLO startup voltage threshold
									'UVLO_Stop'				:	6.5																						,	#?	UVLO shutdown voltage threshold
									'UVLO_Delay'			:	100e-9																					,	#?	delay between UVLO startup and shutdown
									'Init_State'			:	0																						,	#?	initial toggling state, 0->OFF | 1->ON
									'CurrentLimit'	:	{																									#*	current limit of driver stage
										'Config'			:	2																						,	#?	1->enable | 2->disable
										'Ts'				: 	0 																						,	#?	sampling time between inductive & capacitive links
										'tau'				: 	0																						,	#?	first-order delay between inductive & capacitive links
                                    	'Rs'				: 	0																						,	#?	source impedance of inductive link
										'Cs'				:	1e-12																					,	#?	source capacitance of capacitive link
                                        'UpLim'				: 	10																						,	#?	max current limit on capacitive link
                                        'LoLim'				: 	-10																						,	#?	min current limit on capacitive link
                                        'Voffset'			: 	0																							#?	voltage offset between inductive & capacitive links
									},
									'Masking'		:	{																									#*	switching stages masking
										'ON'	:	{																										#	ON path masking
											'Config'		:	2																						,	#?	1->enable | 2->disable
											'HIGH'	:	{																									#!	HIGH mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[0, 0]																						#?	mask output
											},
											'LOW'	:	{																									#!	LOW mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[1, 1]																						#?	mask output
											}
										},
										'OFF'	:	{																										#	OFF path masking
											'Config'		:	2																						,	#?	1->enable | 2->disable
											'HIGH'	:	{																									#!	HIGH mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[0, 0]																						#?	mask output
											},
											'LOW'	:	{																									#!	LOW mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[1, 1]																						#?	mask output
											}
										}
									},
									'Boot'			:	{																									#*	bootstrap/charge pump parameters
										'Config'			:	1																						,	#?	1->bootstrap | 2->charge pump
										'Von'				:	14																						,	#?	boostrap driving voltage
										'Cboot'				:	4.7e-6																					,	#?	bootstrap capacitance
										'Vinit'				:	0																						,	#?	bootstrap capacitance initial voltage
										'Rboot'				:	10																						,	#?	bootstrap resistance
										'Vfboot'			:	0.87																					,	#?	bootstrap diode forward voltage
										'Rdboot'			:	1e-3																					,	#?	bootstrap diode ON-state resistance
										'Ichrg'				:	300e-6																					,	#?	charge pump supply current
										'Idis'				:	5e-6																					,	#?	charge pump loading or leakage current
										'Cpar'				:	0																						,	#?	charge pump parallel cap to break state/source dependency
									    'UVLO_Start'		:	11.6																					,	#?	threshold value to start the charge pump
										'UVLO_Stop'			:	12.4																						#?	threshold value to stop the charge pump
									},
							},
							'GateNetwork'			:	{																									#!	gate drive circuit parameters
									'Config'				:	2																						,	#?	1-> enable | 2->disable
									'ON_Path'		:	{																									#*	sourcing path parameters
										'Rg'				:	10																						,	#?	gate ON path resistance
										'Lg'				:	0																						,	#?	gate ON path inductance
										'Rload'				:	10e3																					,	#?	gate pull down resistance
										'Diode'	:	{																										#	reverse blocking diode parameters
											'Vf'			:	0																						,	#?	forward voltage
											'Rd_on'			:	0																						,	#?	ON-state resistance
										},
									},
									'OFF_Path'		:	{																									#*	sinking path parameters
										'Rg'				:	10																						,	#?	gate OFF path resistance
										'Lg'				:	0																						,	#?	gate OFF path inductance
										'Diode'	:	{																										#	reverse blocking diode parameters
											'Vf'			:	0																						,	#?	forward voltage
											'Rd_on'			:	0																						,	#?	ON-state resistance
										},
									},
									'NegVolt'		:	{																									#*	negative voltage generator parameters
										'Config'			:	2																						,	#?	1-> enable | 2->disable
										'Dz'	:	{																										#	zener diode parameters
											'Vf'			:	0.7																						,	#?	forward voltage
											'Rd_on'			:	1e-3																					,	#?	ON-state resistance
											'Vz'			:	2																						,	#?	Zener breakdown voltage
											'Rz'			:	1e-3																					,	#?	Zener resistance
										},
										'Dp'	:	{																										#	peak detector diode
											'Vf'			:	0.0																						,	#?	forward voltage
											'Rd_on'			:	0.0																						,	#?	ON-state resistance
										},
										'Cz'	:	{																										#	Zener capacitor parameters
											'Config'		:	1																						,	#?	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
											'Csingle'		:	1e-6																					,	#?	single capacitor value
											'Rsingle'		:	5e-3																					,	#?	ESR of single capacitor
											'Lsingle'		:	0																						,	#?	ESL of single capacitor
											'nPar'			:	1																						,	#?	number of parallel connections
											'nSer'			:	1																						,	#?	number of series connections
											'Vinit'			:	0																						,	#?	capacitor initial voltage
										},
										'Cp'	:	{																										#	peak detector capacitor parameters
											'Config'		:	1																						,	#?	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
											'Csingle'		:	2.2e-6																					,	#?	single capacitor value
											'Rsingle'		:	5e-3																					,	#?	ESR of single capacitor
											'Lsingle'		:	0																						,	#?	ESL of single capacitor
											'nPar'			:	1																						,	#?	number of parallel connections
											'nSer'			:	1																						,	#?	number of series connections
											'Vinit'			:	0																						,	#?	capacitor initial voltage
										},
										'Rp1'				:	43																						,	#?	current limiter of peak detector current
										'Rp2'				:	4.7e3																					,	#?	load resistor to charge the zener diode
									},
								},
							'nParallel'   					:	1                                       												,   #? 	number of parallel devices
							'Rth_jc'						:	[0.4358,0.07799,0.07803,0.5816]															,	#?	junction-to-case thermal resistance
							'Cth_jc'						:	[0.000848784,0.036761123,0.037126746,0.005037827]										,	#?	junction-to-case thermal capacitance
							'Rth_ca'              			:   [1.3422, 1.4779, 1.0129, 0.701] 														,   #? 	case-to-ambient thermal resistance
							'Cth_ca'              			:   [12.8939,1.6758,0.0755,169.4661]            											,   #? 	case-to-ambient thermal capacitance
							'Tinit'							:	0.0																						,	#?	initial juntion temperature
							'Pinit'							:	0.0																						,	#?	initial power dissipation
							'Coss'					: 	{																									#!	device Coss parameters
								'C'							:	Coss_eff					 															,	#?	device parasitic output capacitance
								'R'							:	0																						,	#?	Coss resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Coss inductance to reduce current slope
								'Coss_er'					:	Crss_er																					,	#?	energy-related Coss
								'Coss_tr'					:	Coss_tr																					,	#?	time-related Coss
								'Vvec'						:	Coss[0]																					,	#? 	device Coss voltage vector
								'Cvec'						:	Coss[1]																					,	#?	device Coss capacity vector
								'Offset'					:	0*25.0e-12																				,	#?	parasitic offset to Coss
                                'Factor'					:	1.0																						,	#?	parasitic tolerance to Coss
								'Qoss'						:	Qoss																					,	#?	equivalent charge of Coss
								'Eoss'						:	Eoss																					,	#?	equivalent energy of Coss
								'Config'					:	5																							#?	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
						},
                        	'Crss'					:	{																									#!	device Crss parameters
                                'C'							:	Crss_eff					 															,	#?	device parasitic reverse transfer capacitance
								'R'							:	0																						,	#?	Crss resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Crss inductance to reduce current slope
								'Crss_er'					:	Crss_er																					,	#?	energy-related Crss
								'Crss_tr'					:	Crss_tr																					,	#?	time-related Crss
								'Vvec'						:	Crss[0]																					,	#?	device Crss voltage vector
                                'Cvec'						:	Crss[1]																					,	#?	device Crss capacity vector
								'Qvec'						:	Qrss																					,	#?	device accumulated Crss charge vector
								'Offset'					:	0																						,	#?	parasitic offset to Crss
								'Factor'					:	1.0																						,	#?	parasitic tolerance to Crss
								'Qrss'						:	Qrss																					,	#?	equivalent charge of Crss
								'Erss'						:	Erss																					,	#?	equivalent energe of Crss
								'Config'					:	5																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
						},
							'Ciss'					:	{																									#!	device Ciss parameters
								'C'							:	Ciss_eff					 															,	#?	device parasitic input capacitance
								'R'							:	0																						,	#?	Ciss resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Ciss inductance to reduce current slope
								'Ciss_er'					:	Ciss_er																					,	#?	energy-related Ciss
								'Ciss_tr'					:	Ciss_tr																					,	#?	time-related Ciss
								'Vvec'						:	Ciss[0]																					,	#?	device Ciss voltage vector
								'Cvec'						:	Ciss[1]																					,	#?	device Ciss capacity vector
								'Offset'					:	0																						,	#?	parasitic offset to Ciss
								'Factor'					:	1.0																						,	#?	parasitic tolerance to Ciss
								'Qiss'						:	Qiss																					,	#?	equivalent charge of Ciss
								'Eiss'						:	Eiss																					,	#?	equivalent energy of Ciss
								'Config'					:	5																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Cds'					:	{																									#!	device Cds parameters
								'C'							:	Cds_eff					 																,	#?	device parasitic Cds capacitance
								'R'							:	0																						,	#?	Cds resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Cds inductance to reduce current slope
								'Cds_er'					:	Cds_er																					,	#?	energy-related Cds
								'Cds_tr'					:	Cds_tr																					,	#?	time-related Cds
								'Vvec'						:	Coss[0]																					,	#?	device Cds voltage vector
								'Cvec'						:	Cds																						,	#?	device Cds capacity vector
								'Offset_ON'					:	0																						,	#?	tuning offset for turn ON
								'Offset_OFF'				:	0																						,	#?	tuning offset for turn OFF
								'Factor_ON'					:	1.0																						,	#?	tuning factor for turn ON
								'Factor_OFF'				:	1.0																						,	#?	tuning factor for turn OFF
								'Config'					:	4																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Cgd'					:	{																									#!	device Cgd parameters
								'C'							:	Cgd_eff							 														,	#?	device parasitic Cgd capacitance
								'R'							:	0																						,	#?	Cgd resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Cgd inductance to reduce current slope
								'Cgd_er'					:	Cgd_er																					,	#?	energy-related Cgd
								'Cgd_tr'					:	Cgd_tr																					,	#?	time-related Cgd
								'Vvec'						:	Crss[0]																					,	#?	device Cgd voltage vector
								'Cvec'						:	Cgd																						,	#?	device Cgd capacity vector
								'Offset_ON'					:	0																						,	#?	tuning offset for turn ON
								'Offset_OFF'				:	0																						,	#?	tuning offset for turn OFF
								'Factor_ON'					:	1.0																						,	#?	tuning factor for turn ON
								'Factor_OFF'				:	1.0																						,	#?	tuning factor for turn OFF
								'Config'					:	4																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Cgs'					:	{																									#!	device Cgs parameters
								'C'							:	Cgs_eff					 																,	#?	device parasitic Cgs capacitance
								'R'							:	0																						,	#?	Cgs resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Cgs inductance to reduce current slope
								'Cgs_er'					:	Cgs_er																					,	#?	energy-related Cgs
								'Cgs_tr'					:	Cgs_tr																					,	#?	time-related Cgs
								'Vvec'						:	Ciss[0]																					,	#?	device Cgs voltage vector
								'Cvec'						:	Cgs																						,	#?	device Cgs capacity vector
								'Offset_ON'					:	0																						,	#?	tuning offset for turn ON
								'Offset_OFF'				:	0																						,	#?	tuning offset for turn OFF
								'Factor_ON'					:	1.0																						,	#?	tuning factor for turn ON
								'Factor_OFF'				:	1.0																						,	#?	tuning factor for turn OFF
								'Config'					:	4																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Eoff'					:	{																									#!	transistor turn-OFF energy losses
									'Ivec'					:	Ioff																					,	#?	turn-OFF energy current vector
                                    'Rgvec'					:	[1.0,2.2,4.7,10,22,47,50]																,	#?	ON path gate resistances vector
                                    'Tjvec'					:	[-55,25,75,150,175]																		,	#?	junction temperature vector
                                    'Vvec'					:	Voff																					,	#?	turn-OFF voltage vector
                                    'Evec'					:	Eoff																					,	#?	turn-OFF energy vectors
                                    'Evec_Temp'				:	Eoff_Temp																				,	#?	turn-OFF energy temp scaling vectors
                                    'CAT'					:	catOFF																					,	#?	octave Eoff energy syntax
                                    'CAT_Temp'				:	catOFF_Temp																				,	#?	octave Eoff energy temp scaling syntax
									'Vgs'					:	0																						,	#?	used OFF path gate-source voltage
									'Vth'					:	4.5																						,	#?	used OFF path threshold voltage
									'Rg'					:	10.0																						#?	used OFF path gate resistance
						},
							'Eon'					:	{																									#!	transistor turn-ON energy losses
									'Ivec'					:	Ion																						,	#?	turn-ON energy current vector
									'Rgvec'					:	[1.0,2.2,4.7,10,22,47,50]																,	#?	ON path gate resistances vector
                                    'Tjvec'					:	[-55,25,75,150,175]																		,	#?	junction temperature vector
                                    'Vvec'					:	Von																						,	#?	turn-ON voltage vector
                                    'Evec'					:	Eon																						,	#?	turn-ON energy vectors
                                    'Evec_Temp'				:	Eon_Temp																				,	#?	turn-ON energy temp scaling vectors
                                    'CAT'					:	catON																					,	#?	octave Eon energy syntax
                                    'CAT_Temp'				:	catON_Temp																				,	#?	octave Eon energy temp scaling syntax
									'Vgs'					:	18																						,	#?	used ON path gate-source voltage
									'Vth'					:	4.5																						,	#?	used ON path threshold voltage
									'Rg'					:	10.0																						#?	used ON path gate resistance
						},
							'Tau_deg'						:	100e-9																					,	#?	deglitch filter for currents and voltages
							'RCsnubber'						:	2																						,	#?	1->enable | 2->disable
						}

#?----------------------------------------------------------------------------------------------------------------------------------------------------------------------

Coss,Qoss,Eoss,Coss_tr,Coss_er		=	paramProcess.MOSFETcaps(switchesCossPath,'AIMDQ75R040M1H','_Coss')
Crss,Qrss,Erss,Crss_tr,Crss_er 		=	paramProcess.MOSFETcaps(switchesCrssPath,'AIMDQ75R040M1H','_Crss')
Ciss,Qiss,Eiss,Ciss_tr,Ciss_er 		=	paramProcess.MOSFETcaps(switchesCissPath,'AIMDQ75R040M1H','_Ciss')
Coss_eff 							=	paramProcess.getCmos(Coss,Coss_tr,Coss_er,Coss[0][0],True)
Ciss_eff 							=	paramProcess.getCmos(Ciss,Ciss_tr,Ciss_er,Ciss[0][0],True)
Crss_eff 							=	paramProcess.getCmos(Crss,Crss_tr,Crss_er,Crss[0][0],True)
Cds 						        =	(np.array(Coss[1]) - np.array(Crss[1])).tolist()
Cgs						        	=	(np.array(Ciss[1]) - np.array(Crss[1])).tolist()
Cgd						        	=	Crss[1]
Cds_tr						        =	(np.array(Coss_tr) - np.array(Crss_tr)).tolist()
Cgs_tr						        =	(np.array(Ciss_tr) - np.array(Crss_tr)).tolist()
Cgd_tr						        =	Crss_tr
Cds_er						        =	(np.array(Coss_er) - np.array(Crss_er)).tolist()
Cgs_er						        =	(np.array(Ciss_er) - np.array(Crss_er)).tolist()
Cgd_er						        =	Crss_er
Cds_eff 							=	paramProcess.getCmos([Coss[0],Cds],Cds_tr,Cds_er,Coss[0][0],True)
Cgs_eff 							=	paramProcess.getCmos([Ciss[0],Cgs],Cgs_tr,Cgs_er,Ciss[0][0],True)
Cgd_eff 							=	Crss_eff
Rvec,Tvec							=	paramProcess.MOSFETrdson(switchesRdsonPath,'AIMDQ75R040M1H','_Rdson')
Nvec,Ivec 							=	paramProcess.MOSFETrdson(switchesIdsonPath,'AIMDQ75R040M1H','_Rdson')
Ioff,catOFF,Eoff					=	paramProcess.MOSFETenergies(switchesEoffPath,'AIMDQ75R040M1H','_Eoff')
Voff,catOFF_Temp,Eoff_Temp			=	paramProcess.MOSFETenergies(switchesEoffPath,'AIMDQ75R040M1H','_Eoff_Temp')
Ion,catON,Eon 						=	paramProcess.MOSFETenergies(switchesEonPath,'AIMDQ75R040M1H','_Eon')
Von,catON_Temp,Eon_Temp				=	paramProcess.MOSFETenergies(switchesEonPath,'AIMDQ75R040M1H','_Eon_Temp')
Vfvec,Ifvec,Rd,Vt					=	paramProcess.DiodeVI_data(bodyDiodeVIPath,'AIMDQ75R040M1H')
Vds_vec,Ids_vec 					=	paramProcess.Forward_Transfer_data(switchesTransferPath,'AIMDQ75R040M1H')

AIMDQ75R040M1H		=	{																																	#*	AIMDQ75R040M1H parameters
							'Config'						:	1																						,	#!	1->electric integrated | 2->electric separate | 3->thermal integrated | 4->thermal separate
							'Transistor'  			: 	{																									#!	transistors parameters
									'Config'				:	2																						,	#?	1->real model | 2->ideal model | 3->behavioral model
									'Thermal'           	:   'Infineon/CoolSiC/AIMDQ75R040M1H'                                  						,   #? 	selected transistor
									'Custom'            	:   ['TCR','1']                 															,   #? 	transistor provided custom variables
									'g_fs'					:	13.0																					,	#?	forward transconductance
									'Rg'					:	52e-3																					,	#?	internal gate resistance
									'Lg'					:	9.52e-9*0																				,	#?	gate pin inductance
									'Rds_on'            	:   Rvec[-1][-1]*1e-3																		,   #? 	transistor ON resistance
									'Rds_off'				:	'inf'																					,	#?	transistor OFF resistance
									'Rvec'					:	(np.array(Rvec)*1e-3).tolist()														,	#?	absolute Rdson vector corresponding to junction temperature
									'Tvec'					:	Tvec 																					,	#?	junction temperature vector for Rdson
									'RTconfig'				:	1																						,	#?	choose which RT vector to be used
									'RdsonScale'			:	1.0																						,	#?	Rdson scaling to account for min, typ and max deviations
									'Nvec'					:	Nvec 																					,	#?	normalized Rdson vector corresponding to current
									'Ivec'					:	Ivec																					,	#?	current vector for normalized Rdson
									'NIconfig'				:	1																						,	#?	choose which NI vector to be used
									'IdsonScale'			:	1.0																						,	#?	Idson resistance scaling to account for min, typ and max deviations
									'Rsrc'					:	47.2e-3*0																				,	#?	kelvin source pin resistance
									'Lsrc'					:	5.57e-9*0																				,	#?	kelvin source pin inductance
									'Ls'					:	4.62e-9*0																				,	#?	package source inductance
                                    'Ld'					:	2.19e-9*0																				,	#?	package drain inductance
									'Rs'					:	0.993e-3*0																				,	#?	package source resistance
									'Rd'					:	46.3e-6*0																				,	#?	package drain inductance
									'Ksrc'					:	0																						,	#?	kelvin source option, 0->no kelvin | 1->kelvin
									'Vblock'            	:   750                                	 													,   #? 	transistor blocking voltage
									'Id'                	:   42.2                                 													,   #? 	transistor drain current
									'Tr'                	:   0                                   													,   #? 	transistor rise time
									'Tf'                	:   0                                       												, 	#? 	transistor fall time
									'Avalanche'		:	{																									#!	transistor avalanche parameters
										'Config'			:	2																						,	#?	1->enable | 2->disable
										'Voltage'			:	750 																					,	#?	avalanche voltage
										'Resistance'		:	1e-3																						#?	avalanche resistance to break voltage state-dependency
									},
									'Transfer'		:	{																									#!	transistor forward transfer parameters
										'Vds'				:	Vds_vec																					,	#?	drain-source voltage vector
										'Vgs'				:	list(np.arange(0.0,22.0+0.8,0.8))													,	#?	gate-source voltage vector
										'Ids'				:	Ids_vec																					,	#?	drain current vector
										'Factor_ON'			:	1.0																						,	#?	scaling factor for Ids at turn ON
										'Factor_OFF'		:	1.0																						,	#?	scaling factor for Ids at turn OFF
										'Factor_Vgs_ON'		:	1.0																						,	#?	scaling factor for Vgs at turn ON
										'Factor_Vgs_OFF'	:	1.0																						,	#?	scaling factor for Vgs at turn OFF
										'Vcoss'				:	0																						,	#?	initial voltage of the Coss
									},
						},
							'BodyDiode'  			:	{																									#!	body diodes paramteters
									'Config'				:	4																						,	#?	1->non-ideal RR | 2->non-ideal | 3->ideal RR | 4->ideal
									'Thermal'           	:   ''                                  													,   #? 	separate body diode
									'Custom'            	:   []					                 													,   #? 	body diode provided custrom variables
									'Rd_on'             	:   Rd[-1]													                              	,  	#? 	body diode ON resistance
									'Rd_off'				:	'inf'																					,	#?	body diode OFF resistance
									'Vf'					:	Vt[-1]																					,	#? 	body diode forward voltage
									'If'                	:   42	                                 													,   #? 	body diode forward current
									'dIr'               	:   1000e6                                 													,   #? 	body diode current slope
									'Lrr'					:	1e-9																					,	#?	body diode reverse recovery inductance
									'Trr'               	:   0	                                  													,   #? 	body diode reverse recovery time
									'Irr'               	:   0                                      													,   #? 	body diode reverse recovery current
									'Qrr'               	:   144e-9			                              											,	#? 	body diode reverse recovery charge
									'Is'                  	:   16.6              																		, 	#? 	body diode reference current
									'Vs'					:	500																						,	#?	body diode reference voltage
                                    'VIcurve'		:	{																									#!	body diode VI characteristics
                                        'Vfvec'				:	Vfvec																					,	#?	forward voltage vector
                                        'Ifvec'				:	Ifvec																					,	#?	forward current vector
										'Rdvec'				:	Rd																						,	#?	dynamic resistance vector
										'Vtvec'				:	Vt																						,	#?	threshold voltage vector
                                        'Temps'				:	[25,175]																				,	#?	temperature vector
                                        'Vfscale'			:	1.359																						#?	Vf scaling to account for min, typ and max deviations
									},
						},
							'GateDriver'			:	{																									#!	gate driver parameters
									'Config'				:	3																						,	#?	1->high-side | 2->low-side | 3->disable
									'Von'					:	18																						,	#?	ON driving voltage
									'Voff'					:	0																						,	#?	OFF driving voltage
									'Ron'					:	5																						,	#?	sourcing output resistance
									'Roff'					:	5																						,	#?	sinking output resistance
									'Lon'					:	0																						,	#?	sourcing output inductance
									'Loff'					:	0																						,	#?	sinking output inductance
									'Cload'					:	0																						,	#?	capacitive load on output
									'Rload'					:	'inf'																					,	#?	resistive load on output
									'Delay'					:	0																						,	#?	input-to-output total deadtime
									'Trise'					:	0																						,	#?	output rising time
									'Tfall'					:	0																						,	#?	output falling time
									'UVLO_Start'			:	7.0																						,	#?	UVLO startup voltage threshold
									'UVLO_Stop'				:	6.5																						,	#?	UVLO shutdown voltage threshold
									'UVLO_Delay'			:	100e-9																					,	#?	delay between UVLO startup and shutdown
									'Init_State'			:	0																						,	#?	initial toggling state, 0->OFF | 1->ON
									'CurrentLimit'	:	{																									#*	current limit of driver stage
										'Config'			:	2																						,	#?	1->enable | 2->disable
										'Ts'				: 	0 																						,	#?	sampling time between inductive & capacitive links
										'tau'				: 	0																						,	#?	first-order delay between inductive & capacitive links
                                    	'Rs'				: 	0																						,	#?	source impedance of inductive link
										'Cs'				:	1e-12																					,	#?	source capacitance of capacitive link
                                        'UpLim'				: 	10																						,	#?	max current limit on capacitive link
                                        'LoLim'				: 	-10																						,	#?	min current limit on capacitive link
                                        'Voffset'			: 	0																							#?	voltage offset between inductive & capacitive links
									},
									'Masking'		:	{																									#*	switching stages masking
										'ON'	:	{																										#	ON path masking
											'Config'		:	2																						,	#?	1->enable | 2->disable
											'HIGH'	:	{																									#!	HIGH mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[0, 0]																						#?	mask output
											},
											'LOW'	:	{																									#!	LOW mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[1, 1]																						#?	mask output
											}
										},
										'OFF'	:	{																										#	OFF path masking
											'Config'		:	2																						,	#?	1->enable | 2->disable
											'HIGH'	:	{																									#!	HIGH mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[0, 0]																						#?	mask output
											},
											'LOW'	:	{																									#!	LOW mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[1, 1]																						#?	mask output
											}
										}
									},
									'Boot'			:	{																									#*	bootstrap/charge pump parameters
										'Config'			:	1																						,	#?	1->bootstrap | 2->charge pump
										'Von'				:	14																						,	#?	boostrap driving voltage
										'Cboot'				:	4.7e-6																					,	#?	bootstrap capacitance
										'Vinit'				:	0																						,	#?	bootstrap capacitance initial voltage
										'Rboot'				:	10																						,	#?	bootstrap resistance
										'Vfboot'			:	0.87																					,	#?	bootstrap diode forward voltage
										'Rdboot'			:	1e-3																					,	#?	bootstrap diode ON-state resistance
										'Ichrg'				:	300e-6																					,	#?	charge pump supply current
										'Idis'				:	5e-6																					,	#?	charge pump loading or leakage current
										'Cpar'				:	0																						,	#?	charge pump parallel cap to break state/source dependency
									    'UVLO_Start'		:	11.6																					,	#?	threshold value to start the charge pump
										'UVLO_Stop'			:	12.4																						#?	threshold value to stop the charge pump
									},
							},
							'GateNetwork'			:	{																									#!	gate drive circuit parameters
									'Config'				:	2																						,	#?	1-> enable | 2->disable
									'ON_Path'		:	{																									#*	sourcing path parameters
										'Rg'				:	10																						,	#?	gate ON path resistance
										'Lg'				:	0																						,	#?	gate ON path inductance
										'Rload'				:	10e3																					,	#?	gate pull down resistance
										'Diode'	:	{																										#	reverse blocking diode parameters
											'Vf'			:	0																						,	#?	forward voltage
											'Rd_on'			:	0																						,	#?	ON-state resistance
										},
									},
									'OFF_Path'		:	{																									#*	sinking path parameters
										'Rg'				:	10																						,	#?	gate OFF path resistance
										'Lg'				:	0																						,	#?	gate OFF path inductance
										'Diode'	:	{																										#	reverse blocking diode parameters
											'Vf'			:	0																						,	#?	forward voltage
											'Rd_on'			:	0																						,	#?	ON-state resistance
										},
									},
									'NegVolt'		:	{																									#*	negative voltage generator parameters
										'Config'			:	2																						,	#?	1-> enable | 2->disable
										'Dz'	:	{																										#	zener diode parameters
											'Vf'			:	0.7																						,	#?	forward voltage
											'Rd_on'			:	1e-3																					,	#?	ON-state resistance
											'Vz'			:	2																						,	#?	Zener breakdown voltage
											'Rz'			:	1e-3																					,	#?	Zener resistance
										},
										'Dp'	:	{																										#	peak detector diode
											'Vf'			:	0.0																						,	#?	forward voltage
											'Rd_on'			:	0.0																						,	#?	ON-state resistance
										},
										'Cz'	:	{																										#	Zener capacitor parameters
											'Config'		:	1																						,	#?	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
											'Csingle'		:	1e-6																					,	#?	single capacitor value
											'Rsingle'		:	5e-3																					,	#?	ESR of single capacitor
											'Lsingle'		:	0																						,	#?	ESL of single capacitor
											'nPar'			:	1																						,	#?	number of parallel connections
											'nSer'			:	1																						,	#?	number of series connections
											'Vinit'			:	0																						,	#?	capacitor initial voltage
										},
										'Cp'	:	{																										#	peak detector capacitor parameters
											'Config'		:	1																						,	#?	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
											'Csingle'		:	2.2e-6																					,	#?	single capacitor value
											'Rsingle'		:	5e-3																					,	#?	ESR of single capacitor
											'Lsingle'		:	0																						,	#?	ESL of single capacitor
											'nPar'			:	1																						,	#?	number of parallel connections
											'nSer'			:	1																						,	#?	number of series connections
											'Vinit'			:	0																						,	#?	capacitor initial voltage
										},
										'Rp1'				:	43																						,	#?	current limiter of peak detector current
										'Rp2'				:	4.7e3																					,	#?	load resistor to charge the zener diode
									},
								},
							'nParallel'   					:	1                                       												,   #? 	number of parallel devices
							'Rth_jc'						:	0.71																					,	#?	junction-to-case thermal resistance
							'Cth_jc'						:	0.00																					,	#?	junction-to-case thermal capacitance
							'Rth_ca'              			:   [1.399,1.017,0.638,0.453,0.564]            												,   #? 	case-to-ambient thermal resistance
							'Cth_ca'              			:   [2.028,16.857,0.757,210.682,0.149]            											,   #? 	case-to-ambient thermal capacitance
							'Tinit'							:	0.0																						,	#?	initial juntion temperature
							'Pinit'							:	0.0																						,	#?	initial power dissipation
							'Coss'					: 	{																									#!	device Coss parameters
								'C'							:	Coss_eff					 															,	#?	device parasitic output capacitance
								'R'							:	0																						,	#?	Coss resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Coss inductance to reduce current slope
								'Coss_er'					:	Crss_er																					,	#?	energy-related Coss
								'Coss_tr'					:	Coss_tr																					,	#?	time-related Coss
								'Vvec'						:	Coss[0]																					,	#? 	device Coss voltage vector
								'Cvec'						:	Coss[1]																					,	#?	device Coss capacity vector
								'Offset'					:	0																						,	#?	parasitic offset to Coss
                                'Factor'					:	1.0																						,	#?	parasitic tolerance to Coss
								'Qoss'						:	Qoss																					,	#?	equivalent charge of Coss
								'Eoss'						:	Eoss																					,	#?	equivalent energy of Coss
								'Config'					:	5																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
						},
                        	'Crss'					:	{																									#!	device Crss parameters
                                'C'							:	Crss_eff					 															,	#?	device parasitic reverse transfer capacitance
								'R'							:	0																						,	#?	Crss resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Crss inductance to reduce current slope
								'Crss_er'					:	Crss_er																					,	#?	energy-related Crss
								'Crss_tr'					:	Crss_tr																					,	#?	time-related Crss
								'Vvec'						:	Crss[0]																					,	#?	device Crss voltage vector
                                'Cvec'						:	Crss[1]																					,	#?	device Crss capacity vector
								'Qvec'						:	Qrss																					,	#?	device accumulated Crss charge vector
								'Offset'					:	0																						,	#?	parasitic offset to Crss
								'Factor'					:	1.0																						,	#?	parasitic tolerance to Crss
								'Qrss'						:	Qrss																					,	#?	equivalent charge of Crss
								'Erss'						:	Erss																					,	#?	equivalent energe of Crss
								'Config'					:	5																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
						},
							'Ciss'					:	{																									#!	device Ciss parameters
								'C'							:	Ciss_eff					 															,	#?	device parasitic input capacitance
								'R'							:	0																						,	#?	Ciss resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Ciss inductance to reduce current slope
								'Ciss_er'					:	Ciss_er																					,	#?	energy-related Ciss
								'Ciss_tr'					:	Ciss_tr																					,	#?	time-related Ciss
								'Vvec'						:	Ciss[0]																					,	#?	device Ciss voltage vector
								'Cvec'						:	Ciss[1]																					,	#?	device Ciss capacity vector
								'Offset'					:	0																						,	#?	parasitic offset to Ciss
								'Factor'					:	1.0																						,	#?	parasitic tolerance to Ciss
								'Qiss'						:	Qiss																					,	#?	equivalent charge of Ciss
								'Eiss'						:	Eiss																					,	#?	equivalent energy of Ciss
								'Config'					:	5																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Cds'					:	{																									#!	device Cds parameters
								'C'							:	Cds_eff					 																,	#?	device parasitic Cds capacitance
								'R'							:	0																						,	#?	Cds resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Cds inductance to reduce current slope
								'Cds_er'					:	Cds_er																					,	#?	energy-related Cds
								'Cds_tr'					:	Cds_tr																					,	#?	time-related Cds
								'Vvec'						:	Coss[0]																					,	#?	device Cds voltage vector
								'Cvec'						:	Cds																						,	#?	device Cds capacity vector
								'Offset_ON'					:	0																						,	#?	tuning offset for turn ON
								'Offset_OFF'				:	0																						,	#?	tuning offset for turn OFF
								'Factor_ON'					:	1.0																						,	#?	tuning factor for turn ON
								'Factor_OFF'				:	1.0																						,	#?	tuning factor for turn OFF
								'Config'					:	4																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Cgd'					:	{																									#!	device Cgd parameters
								'C'							:	Cgd_eff							 														,	#?	device parasitic Cgd capacitance
								'R'							:	0																						,	#?	Cgd resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Cgd inductance to reduce current slope
								'Cgd_er'					:	Cgd_er																					,	#?	energy-related Cgd
								'Cgd_tr'					:	Cgd_tr																					,	#?	time-related Cgd
								'Vvec'						:	Crss[0]																					,	#?	device Cgd voltage vector
								'Cvec'						:	Cgd																						,	#?	device Cgd capacity vector
								'Offset_ON'					:	0																						,	#?	tuning offset for turn ON
								'Offset_OFF'				:	0																						,	#?	tuning offset for turn OFF
								'Factor_ON'					:	1.0																						,	#?	tuning factor for turn ON
								'Factor_OFF'				:	1.0																						,	#?	tuning factor for turn OFF
								'Config'					:	4																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Cgs'					:	{																									#!	device Cgs parameters
								'C'							:	Cgs_eff					 																,	#?	device parasitic Cgs capacitance
								'R'							:	0																						,	#?	Cgs resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Cgs inductance to reduce current slope
								'Cgs_er'					:	Cgs_er																					,	#?	energy-related Cgs
								'Cgs_tr'					:	Cgs_tr																					,	#?	time-related Cgs
								'Vvec'						:	Ciss[0]																					,	#?	device Cgs voltage vector
								'Cvec'						:	Cgs																						,	#?	device Cgs capacity vector
								'Offset_ON'					:	0																						,	#?	tuning offset for turn ON
								'Offset_OFF'				:	0																						,	#?	tuning offset for turn OFF
								'Factor_ON'					:	1.0																						,	#?	tuning factor for turn ON
								'Factor_OFF'				:	1.0																						,	#?	tuning factor for turn OFF
								'Config'					:	4																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Eoff'					:	{																									#!	transistor turn-OFF energy losses
									'Ivec'					:	Ioff																					,	#?	turn-OFF energy current vector
                                    'Rgvec'					:	[1.0,2.2,4.7,10.0,22.0,47.0,100.0]														,	#?	OFF path gate resistances vector
									'Tjvec'					:	[-55,25,75,150,175]																		,	#?	junction temperature vector
                                    'Vvec'					:	Voff																					,	#?	turn-OFF voltage vector
                                    'Evec'					:	Eoff																					,	#?	turn-OFF energy vectors
									'Evec_Temp'				:	Eoff_Temp																				,	#?	turn-OFF energy temp scaling vectors
                                    'CAT'					:	catOFF																					,	#?	octave Eoff energy syntax
									'CAT_Temp'				:	catOFF_Temp																				,	#?	octave Eoff energy temp scaling syntax
									'Vgs'					:	0																						,	#?	used OFF path gate-source voltage
									'Vth'					:	4.3																						,	#?	used OFF path threshold voltage
									'Rg'					:	10.0																						#?	used OFF path gate resistance
						},
							'Eon'					:	{																									#!	transistor turn-ON energy losses
									'Ivec'					:	Ion																						,	#?	turn-ON energy current vector
									'Rgvec'					:	[1.0,2.2,4.7,10.0,22.0,47.0,100.0]														,	#?	ON path gate resistances vector
									'Tjvec'					:	[-55,25,75,150,175]																		,	#?	junction temperature vector
                                    'Vvec'					:	Von																						,	#?	turn-ON voltage vector
                                    'Evec'					:	Eon																						,	#?	turn-ON energy vectors
									'Evec_Temp'				:	Eon_Temp																				,	#?	turn-ON energy temp scaling vectors
                                    'CAT'					:	catON																					,	#?	octave Eon energy syntax
									'CAT_Temp'				:	catON_Temp																				,	#?	octave Eon energy temp scaling syntax
									'Vgs'					:	18																						,	#?	used ON path gate-source voltaged
									'Vth'					:	4.3																						,	#?	used ON path threshold voltage
									'Rg'					:	10.0																						#?	used ON path gate resistance
						},
							'Tau_deg'						:	100e-9																					,	#?	deglitch filter for currents and voltages
							'RCsnubber'						:	2																						,	#?	1->enable | 2->disable
						}

#?----------------------------------------------------------------------------------------------------------------------------------------------------------------------

Coss,Qoss,Eoss,Coss_tr,Coss_er		=	paramProcess.MOSFETcaps(switchesCossPath,'AIMDQ75R040M2H','_Coss')
Crss,Qrss,Erss,Crss_tr,Crss_er 		=	paramProcess.MOSFETcaps(switchesCrssPath,'AIMDQ75R040M2H','_Crss')
Ciss,Qiss,Eiss,Ciss_tr,Ciss_er 		=	paramProcess.MOSFETcaps(switchesCissPath,'AIMDQ75R040M2H','_Ciss')
Coss_eff 							=	paramProcess.getCmos(Coss,Coss_tr,Coss_er,Coss[0][0],True)
Ciss_eff 							=	paramProcess.getCmos(Ciss,Ciss_tr,Ciss_er,Ciss[0][0],True)
Crss_eff 							=	paramProcess.getCmos(Crss,Crss_tr,Crss_er,Crss[0][0],True)
Cds 						        =	(np.array(Coss[1]) - np.array(Crss[1])).tolist()
Cgs						        	=	(np.array(Ciss[1]) - np.array(Crss[1])).tolist()
Cgd						        	=	Crss[1]
Cds_tr						        =	(np.array(Coss_tr) - np.array(Crss_tr)).tolist()
Cgs_tr						        =	(np.array(Ciss_tr) - np.array(Crss_tr)).tolist()
Cgd_tr						        =	Crss_tr
Cds_er						        =	(np.array(Coss_er) - np.array(Crss_er)).tolist()
Cgs_er						        =	(np.array(Ciss_er) - np.array(Crss_er)).tolist()
Cgd_er						        =	Crss_er
Cds_eff 							=	paramProcess.getCmos([Coss[0],Cds],Cds_tr,Cds_er,Coss[0][0],True)
Cgs_eff 							=	paramProcess.getCmos([Ciss[0],Cgs],Cgs_tr,Cgs_er,Ciss[0][0],True)
Cgd_eff 							=	Crss_eff
Rvec,Tvec							=	paramProcess.MOSFETrdson(switchesRdsonPath,'AIMDQ75R040M2H','_Rdson')
Nvec,Ivec 							=	paramProcess.MOSFETrdson(switchesIdsonPath,'AIMDQ75R040M2H','_Rdson')
Ioff,catOFF,Eoff					=	paramProcess.MOSFETenergies(switchesEoffPath,'AIMDQ75R040M2H','_Eoff')
Voff,catOFF_Temp,Eoff_Temp			=	paramProcess.MOSFETenergies(switchesEoffPath,'AIMDQ75R040M2H','_Eoff_Temp')
Ion,catON,Eon 						=	paramProcess.MOSFETenergies(switchesEonPath,'AIMDQ75R040M2H','_Eon')
Von,catON_Temp,Eon_Temp				=	paramProcess.MOSFETenergies(switchesEonPath,'AIMDQ75R040M2H','_Eon_Temp')
Vfvec,Ifvec,Rd,Vt					=	paramProcess.DiodeVI_data(bodyDiodeVIPath,'AIMDQ75R040M2H')
Vds_vec,Ids_vec 					=	paramProcess.Forward_Transfer_data(switchesTransferPath,'AIMDQ75R040M2H')

AIMDQ75R040M2H		=	{																																	#*	AIMDQ75R040M2H parameters
							'Config'						:	1																						,	#!	1->electric integrated | 2->electric separate | 3->thermal integrated | 4->thermal separate
							'Transistor'  			: 	{																									#!	transistors parameters
									'Config'				:	2																						,	#?	1->real model | 2->ideal model | 3->behavioral model
									'Thermal'           	:   ''                                  													,   #? 	selected transistor
									'Custom'            	:   []                 																		,   #? 	transistor provided custom variables
									'g_fs'					:	13.0																					,	#?	forward transconductance
									'Rg'					:	4.1																						,	#?	internal gate resistance
									'Lg'					:	9.52e-9*0																				,	#?	gate pin inductance
									'Rds_on'            	:   Rvec[-1][-1]*1e-3																		,   #? 	transistor ON resistance
									'Rds_off'				:	'inf'																					,	#?	transistor OFF resistance
									'Rvec'					:	(np.array(Rvec)*1e-3).tolist()														,	#?	absolute Rdson vector corresponding to junction temperature
									'Tvec'					:	Tvec 																					,	#?	junction temperature vector for Rdson
									'RTconfig'				:	1																						,	#?	choose which RT vector to be used
									'RdsonScale'			:	1.25																					,	#?	Rdson scaling to account for min, typ and max deviations
									'Nvec'					:	Nvec 																					,	#?	normalized Rdson vector corresponding to current
									'Ivec'					:	Ivec																					,	#?	current vector for normalized Rdson
									'NIconfig'				:	2																						,	#?	choose which NI vector to be used (Vgs=15,18,20)
									'IdsonScale'			:	1.0																						,	#?	Idson resistance scaling to account for min, typ and max deviations
									'Rsrc'					:	47.2e-3*0																				,	#?	kelvin source pin resistance
									'Lsrc'					:	5.57e-9*0																				,	#?	kelvin source pin inductance
									'Ls'					:	4.62e-9*0																				,	#?	package source inductance
                                    'Ld'					:	2.19e-9*0																				,	#?	package drain inductance
									'Rs'					:	993e-6*0																				,	#?	package source resistance
									'Rd'					:	46.3e-6*0																				,	#?	package drain inductance
									'Ksrc'					:	1																						,	#?	kelvin source option, 0->no kelvin | 1->kelvin
									'Vblock'            	:   750                                	 													,   #? 	transistor blocking voltage
									'Id'                	:   45	                                 													,   #? 	transistor drain current
									'Tr'                	:   0                                   													,   #? 	transistor rise time
									'Tf'                	:   0                                       												, 	#? 	transistor fall time
									'Avalanche'		:	{																									#!	transistor avalanche parameters
										'Config'			:	2																						,	#?	1->enable | 2->disable
										'Voltage'			:	750 																					,	#?	avalanche voltage
										'Resistance'		:	1e-3																						#?	avalanche resistance to break voltage state-dependency
									},
									'Transfer'		:	{																									#!	transistor forward transfer parameters
										'Vds'				:	Vds_vec																					,	#?	drain-source voltage vector
										'Vgs'				:	list(np.arange(0.0,21.0,0.35))														,	#?	gate-source voltage vector
										'Ids'				:	Ids_vec																					,	#?	drain current vector
										'Factor_ON'			:	1.0																						,	#?	scaling factor for Ids at turn ON
										'Factor_OFF'		:	1.0																						,	#?	scaling factor for Ids at turn OFF
										'Factor_Vgs_ON'		:	1.0																						,	#?	scaling factor for Vgs at turn ON
										'Factor_Vgs_OFF'	:	1.0																						,	#?	scaling factor for Vgs at turn OFF
										'Vcoss'				:	0																						,	#?	initial voltage of the Coss
									},
						},
							'BodyDiode'  			:	{																									#!	body diodes paramteters
									'Config'				:	4																						,	#?	1->non-ideal RR | 2->non-ideal | 3->ideal RR | 4->ideal
									'Thermal'           	:   ''                                  													,   #? 	separate body diode
									'Custom'            	:   []					                 													,   #? 	body diode provided custrom variables
									'Rd_on'             	:   Rd[-1]													                              	,  	#? 	body diode ON resistance
									'Rd_off'				:	'inf'																					,	#?	body diode OFF resistance
									'Vf'					:	Vt[-1]																					,	#? 	body diode forward voltage
									'If'                	:   45	                                 													,   #? 	body diode forward current
									'dIr'               	:   4000e6                                 													,   #? 	body diode current slope
									'Lrr'					:	1e-9																					,	#?	body diode reverse recovery inductance
									'Trr'               	:   7e-9                                  													,   #? 	body diode reverse recovery time
									'Irr'               	:   0                                      													,   #? 	body diode reverse recovery current
									'Qrr'               	:   67e-9			                              											,	#? 	body diode reverse recovery charge
									'Is'                  	:   21.7              																		, 	#? 	body diode reference current
									'Vs'					:	500																						,	#?	body diode reference voltage
                                    'VIcurve'		:	{																									#!	body diode VI characteristics
                                        'Vfvec'				:	Vfvec																					,	#?	forward voltage vector
                                        'Ifvec'				:	Ifvec																					,	#?	forward current vector
										'Rdvec'				:	Rd																						,	#?	dynamic resistance vector
										'Vtvec'				:	Vt																						,	#?	threshold voltage vector
                                        'Temps'				:	[25,175]																				,	#?	temperature vector
                                        'Vfscale'			:	1.2195																						#?	Vf scaling to account for min, typ and max deviations
									},
						},
							'GateDriver'			:	{																									#!	gate driver parameters
									'Config'				:	3																						,	#?	1->high-side | 2->low-side | 3->disable
									'Von'					:	18																						,	#?	ON driving voltage
									'Voff'					:	0																						,	#?	OFF driving voltage
									'Ron'					:	5																						,	#?	sourcing output resistance
									'Roff'					:	0.55																					,	#?	sinking output resistance
									'Lon'					:	0																						,	#?	sourcing output inductance
									'Loff'					:	0																						,	#?	sinking output inductance
									'Cload'					:	0																						,	#?	capacitive load on output
									'Rload'					:	'inf'																					,	#?	resistive load on output
									'Delay'					:	0																						,	#?	input-to-output total deadtime
									'Trise'					:	0																						,	#?	output rising time
									'Tfall'					:	0																						,	#?	output falling time
									'UVLO_Start'			:	7.0																						,	#?	UVLO startup voltage threshold
									'UVLO_Stop'				:	6.5																						,	#?	UVLO shutdown voltage threshold
									'UVLO_Delay'			:	100e-9																					,	#?	delay between UVLO startup and shutdown
									'Init_State'			:	0																						,	#?	initial toggling state, 0->OFF | 1->ON
									'CurrentLimit'	:	{																									#*	current limit of driver stage
										'Config'			:	2																						,	#?	1->enable | 2->disable
										'Ts'				: 	0 																						,	#?	sampling time between inductive & capacitive links
										'tau'				: 	0																						,	#?	first-order delay between inductive & capacitive links
                                    	'Rs'				: 	0																						,	#?	source impedance of inductive link
										'Cs'				:	1e-12																					,	#?	source capacitance of capacitive link
                                        'UpLim'				: 	10																						,	#?	max current limit on capacitive link
                                        'LoLim'				: 	-10																						,	#?	min current limit on capacitive link
                                        'Voffset'			: 	0																							#?	voltage offset between inductive & capacitive links
									},
									'Masking'		:	{																									#*	switching stages masking
										'ON'	:	{																										#	ON path masking
											'Config'		:	2																						,	#?	1->enable | 2->disable
											'HIGH'	:	{																									#!	HIGH mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[0, 0]																						#?	mask output
											},
											'LOW'	:	{																									#!	LOW mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[1, 1]																						#?	mask output
											}
										},
										'OFF'	:	{																										#	OFF path masking
											'Config'		:	2																						,	#?	1->enable | 2->disable
											'HIGH'	:	{																									#!	HIGH mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[0, 0]																						#?	mask output
											},
											'LOW'	:	{																									#!	LOW mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[1, 1]																						#?	mask output
											}
										}
									},
									'Boot'			:	{																									#*	bootstrap/charge pump parameters
										'Config'			:	1																						,	#?	1->bootstrap | 2->charge pump
										'Von'				:	14																						,	#?	boostrap driving voltage
										'Cboot'				:	4.7e-6																					,	#?	bootstrap capacitance
										'Vinit'				:	0																						,	#?	bootstrap capacitance initial voltage
										'Rboot'				:	10																						,	#?	bootstrap resistance
										'Vfboot'			:	0.87																					,	#?	bootstrap diode forward voltage
										'Rdboot'			:	1e-3																					,	#?	bootstrap diode ON-state resistance
										'Ichrg'				:	300e-6																					,	#?	charge pump supply current
										'Idis'				:	5e-6																					,	#?	charge pump loading or leakage current
										'Cpar'				:	0																						,	#?	charge pump parallel cap to break state/source dependency
									    'UVLO_Start'		:	11.6																					,	#?	threshold value to start the charge pump
										'UVLO_Stop'			:	12.4																						#?	threshold value to stop the charge pump
									},
							},
							'GateNetwork'			:	{																									#!	gate drive circuit parameters
									'Config'				:	2																						,	#?	1-> enable | 2->disable
									'ON_Path'		:	{																									#*	sourcing path parameters
										'Rg'				:	10																						,	#?	gate ON path resistance
										'Lg'				:	0																						,	#?	gate ON path inductance
										'Rload'				:	10e3																					,	#?	gate pull down resistance
										'Diode'	:	{																										#	reverse blocking diode parameters
											'Vf'			:	0																						,	#?	forward voltage
											'Rd_on'			:	0																						,	#?	ON-state resistance
										},
									},
									'OFF_Path'		:	{																									#*	sinking path parameters
										'Rg'				:	1																						,	#?	gate OFF path resistance
										'Lg'				:	0																						,	#?	gate OFF path inductance
										'Diode'	:	{																										#	reverse blocking diode parameters
											'Vf'			:	0																						,	#?	forward voltage
											'Rd_on'			:	0																						,	#?	ON-state resistance
										},
									},
									'NegVolt'		:	{																									#*	negative voltage generator parameters
										'Config'			:	2																						,	#?	1-> enable | 2->disable
										'Dz'	:	{																										#	zener diode parameters
											'Vf'			:	0.7																						,	#?	forward voltage
											'Rd_on'			:	1e-3																					,	#?	ON-state resistance
											'Vz'			:	2																						,	#?	Zener breakdown voltage
											'Rz'			:	1e-3																					,	#?	Zener resistance
										},
										'Dp'	:	{																										#	peak detector diode
											'Vf'			:	0.0																						,	#?	forward voltage
											'Rd_on'			:	0.0																						,	#?	ON-state resistance
										},
										'Cz'	:	{																										#	Zener capacitor parameters
											'Config'		:	1																						,	#?	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
											'Csingle'		:	1e-6																					,	#?	single capacitor value
											'Rsingle'		:	5e-3																					,	#?	ESR of single capacitor
											'Lsingle'		:	0																						,	#?	ESL of single capacitor
											'nPar'			:	1																						,	#?	number of parallel connections
											'nSer'			:	1																						,	#?	number of series connections
											'Vinit'			:	0																						,	#?	capacitor initial voltage
										},
										'Cp'	:	{																										#	peak detector capacitor parameters
											'Config'		:	1																						,	#?	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
											'Csingle'		:	2.2e-6																					,	#?	single capacitor value
											'Rsingle'		:	5e-3																					,	#?	ESR of single capacitor
											'Lsingle'		:	0																						,	#?	ESL of single capacitor
											'nPar'			:	1																						,	#?	number of parallel connections
											'nSer'			:	1																						,	#?	number of series connections
											'Vinit'			:	0																						,	#?	capacitor initial voltage
										},
										'Rp1'				:	43																						,	#?	current limiter of peak detector current
										'Rp2'				:	4.7e3																					,	#?	load resistor to charge the zener diode
									},
								},
							'nParallel'   					:	1                                       												,   #? 	number of parallel devices
							'Rth_jc'						:	0.82																					,	#?	junction-to-case thermal resistance
							'Cth_jc'						:	0.00																					,	#?	junction-to-case thermal capacitance
							'Rth_ca'              			:   [1.0682,1.2039,0.7389,0.427] 															,   #? 	case-to-ambient thermal resistance
							'Cth_ca'              			:   [12.8939,1.6758,0.0755,169.4661]            											,   #? 	case-to-ambient thermal capacitance
							'Tinit'							:	0.0																						,	#?	initial juntion temperature
							'Pinit'							:	0.0																						,	#?	initial power dissipation
							'Coss'					: 	{																									#!	device Coss parameters
								'C'							:	Coss_eff					 															,	#?	device parasitic output capacitance
								'R'							:	0																						,	#?	Coss resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Coss inductance to reduce current slope
								'Coss_er'					:	Crss_er																					,	#?	energy-related Coss
								'Coss_tr'					:	Coss_tr																					,	#?	time-related Coss
								'Vvec'						:	Coss[0]																					,	#? 	device Coss voltage vector
								'Cvec'						:	Coss[1]																					,	#?	device Coss capacity vector
								'Offset'					:	0																						,	#?	parasitic offset to Coss
                                'Factor'					:	1.0																						,	#?	parasitic tolerance to Coss
								'Qoss'						:	Qoss																					,	#?	equivalent charge of Coss
								'Eoss'						:	Eoss																					,	#?	equivalent energy of Coss
								'Config'					:	5																							#?	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
						},
                        	'Crss'					:	{																									#!	device Crss parameters
                                'C'							:	Crss_eff					 															,	#?	device parasitic reverse transfer capacitance
								'R'							:	0																						,	#?	Crss resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Crss inductance to reduce current slope
								'Crss_er'					:	Crss_er																					,	#?	energy-related Crss
								'Crss_tr'					:	Crss_tr																					,	#?	time-related Crss
								'Vvec'						:	Crss[0]																					,	#?	device Crss voltage vector
                                'Cvec'						:	Crss[1]																					,	#?	device Crss capacity vector
								'Qvec'						:	Qrss																					,	#?	device accumulated Crss charge vector
								'Offset'					:	0																						,	#?	parasitic offset to Crss
								'Factor'					:	1.0																						,	#?	parasitic tolerance to Crss
								'Qrss'						:	Qrss																					,	#?	equivalent charge of Crss
								'Erss'						:	Erss																					,	#?	equivalent energe of Crss
								'Config'					:	5																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
						},
							'Ciss'					:	{																									#!	device Ciss parameters
								'C'							:	Ciss_eff					 															,	#?	device parasitic input capacitance
								'R'							:	0																						,	#?	Ciss resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Ciss inductance to reduce current slope
								'Ciss_er'					:	Ciss_er																					,	#?	energy-related Ciss
								'Ciss_tr'					:	Ciss_tr																					,	#?	time-related Ciss
								'Vvec'						:	Ciss[0]																					,	#?	device Ciss voltage vector
								'Cvec'						:	Ciss[1]																					,	#?	device Ciss capacity vector
								'Offset'					:	0																						,	#?	parasitic offset to Ciss
								'Factor'					:	1.0																						,	#?	parasitic tolerance to Ciss
								'Qiss'						:	Qiss																					,	#?	equivalent charge of Ciss
								'Eiss'						:	Eiss																					,	#?	equivalent energy of Ciss
								'Config'					:	5																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Cds'					:	{																									#!	device Cds parameters
								'C'							:	Cds_eff					 																,	#?	device parasitic Cds capacitance
								'R'							:	0																						,	#?	Cds resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Cds inductance to reduce current slope
								'Cds_er'					:	Cds_er																					,	#?	energy-related Cds
								'Cds_tr'					:	Cds_tr																					,	#?	time-related Cds
								'Vvec'						:	Coss[0]																					,	#?	device Cds voltage vector
								'Cvec'						:	Cds																						,	#?	device Cds capacity vector
								'Offset_ON'					:	0																						,	#?	tuning offset for turn ON
								'Offset_OFF'				:	0																						,	#?	tuning offset for turn OFF
								'Factor_ON'					:	1.0																						,	#?	tuning factor for turn ON
								'Factor_OFF'				:	1.0																						,	#?	tuning factor for turn OFF
								'Config'					:	4																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Cgd'					:	{																									#!	device Cgd parameters
								'C'							:	Cgd_eff							 														,	#?	device parasitic Cgd capacitance
								'R'							:	0																						,	#?	Cgd resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Cgd inductance to reduce current slope
								'Cgd_er'					:	Cgd_er																					,	#?	energy-related Cgd
								'Cgd_tr'					:	Cgd_tr																					,	#?	time-related Cgd
								'Vvec'						:	Crss[0]																					,	#?	device Cgd voltage vector
								'Cvec'						:	Cgd																						,	#?	device Cgd capacity vector
								'Offset_ON'					:	0																						,	#?	tuning offset for turn ON
								'Offset_OFF'				:	0																						,	#?	tuning offset for turn OFF
								'Factor_ON'					:	1.0																						,	#?	tuning factor for turn ON
								'Factor_OFF'				:	1.0																						,	#?	tuning factor for turn OFF
								'Config'					:	4																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Cgs'					:	{																									#!	device Cgs parameters
								'C'							:	Cgs_eff					 																,	#?	device parasitic Cgs capacitance
								'R'							:	0																						,	#?	Cgs resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Cgs inductance to reduce current slope
								'Cgs_er'					:	Cgs_er																					,	#?	energy-related Cgs
								'Cgs_tr'					:	Cgs_tr																					,	#?	time-related Cgs
								'Vvec'						:	Ciss[0]																					,	#?	device Cgs voltage vector
								'Cvec'						:	Cgs																						,	#?	device Cgs capacity vector
								'Offset_ON'					:	0																						,	#?	tuning offset for turn ON
								'Offset_OFF'				:	0																						,	#?	tuning offset for turn OFF
								'Factor_ON'					:	1.0																						,	#?	tuning factor for turn ON
								'Factor_OFF'				:	1.0																						,	#?	tuning factor for turn OFF
								'Config'					:	4																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Eoff'					:	{																									#!	transistor turn-OFF energy losses
									'Ivec'					:	Ioff																					,	#?	turn-OFF energy current vector
                                    'Rgvec'					:	[1.0,2.2,4.7,10,22,47,50]																,	#?	OFF path gate resistances vector
                                    'Tjvec'					:	[-55,25,75,150,175]																		,	#?	junction temperature vector
                                    'Vvec'					:	Voff																					,	#?	turn-OFF voltage vector
                                    'Evec'					:	Eoff																					,	#?	turn-OFF energy vectors
                                    'Evec_Temp'				:	Eoff_Temp																				,	#?	turn-OFF energy temp scaling vectors
                                    'CAT'					:	catOFF																					,	#?	octave Eoff energy syntax
                                    'CAT_Temp'				:	catOFF_Temp																				,	#?	octave Eoff energy temp scaling syntax
									'Vgs'					:	0																						,	#?	used OFF path gate-source voltage
									'Vth'					:	4.5																						,	#?	used OFF path threshold voltage
									'Rg'					:	1.0																							#?	used OFF path gate resistance
						},
							'Eon'					:	{																									#!	transistor turn-ON energy losses
									'Ivec'					:	Ion																						,	#?	turn-ON energy current vector
									'Rgvec'					:	[1.0,2.2,4.7,10,22,47,50]																,	#?	ON path gate resistances vector
									'Tjvec'					:	[-55,25,75,150,175]																		,	#?	junction temperature vector
                                    'Vvec'					:	Von																						,	#?	turn-ON voltage vector
                                    'Evec'					:	Eon																						,	#?	turn-ON energy vectors
                                    'Evec_Temp'				:	Eon_Temp																				,	#?	turn-ON energy temp scaling vectors
                                    'CAT'					:	catON																					,	#?	octave Eon energy syntax
									'CAT_Temp'				:	catON_Temp																				,	#?	octave Eon energy temp scaling syntax
									'Vgs'					:	18																						,	#?	used ON path gate-source voltage
									'Vth'					:	4.5																						,	#?	used ON path threshold voltage
									'Rg'					:	10.0																						#?	used ON path gate resistance
						},
							'Tau_deg'						:	100e-9																					,	#?	deglitch filter for currents and voltages
							'RCsnubber'						:	2																						,	#?	1->enable | 2->disable
						}

#?----------------------------------------------------------------------------------------------------------------------------------------------------------------------

Coss,Qoss,Eoss,Coss_tr,Coss_er		=	paramProcess.MOSFETcaps(switchesCossPath,'SCTH35N65G2V','_Coss')
Crss,Qrss,Erss,Crss_tr,Crss_er 		=	paramProcess.MOSFETcaps(switchesCrssPath,'SCTH35N65G2V','_Crss')
Ciss,Qiss,Eiss,Ciss_tr,Ciss_er 		=	paramProcess.MOSFETcaps(switchesCissPath,'SCTH35N65G2V','_Ciss')
Coss_eff 							=	paramProcess.getCmos(Coss,Coss_tr,Coss_er,Coss[0][0],True)
Ciss_eff 							=	paramProcess.getCmos(Ciss,Ciss_tr,Ciss_er,Ciss[0][0],True)
Crss_eff 							=	paramProcess.getCmos(Crss,Crss_tr,Crss_er,Crss[0][0],True)
Cds 						        =	(np.array(Coss[1]) - np.array(Crss[1])).tolist()
Cgs						        	=	(np.array(Ciss[1]) - np.array(Crss[1])).tolist()
Cgd						        	=	Crss[1]
Cds_tr						        =	(np.array(Coss_tr) - np.array(Crss_tr)).tolist()
Cgs_tr						        =	(np.array(Ciss_tr) - np.array(Crss_tr)).tolist()
Cgd_tr						        =	Crss_tr
Cds_er						        =	(np.array(Coss_er) - np.array(Crss_er)).tolist()
Cgs_er						        =	(np.array(Ciss_er) - np.array(Crss_er)).tolist()
Cgd_er						        =	Crss_er
Cds_eff 							=	paramProcess.getCmos([Coss[0],Cds],Cds_tr,Cds_er,Coss[0][0],True)
Cgs_eff 							=	paramProcess.getCmos([Ciss[0],Cgs],Cgs_tr,Cgs_er,Ciss[0][0],True)
Cgd_eff 							=	Crss_eff
Rvec,Tvec							=	paramProcess.MOSFETrdson(switchesRdsonPath,'SCTH35N65G2V','_Rdson')
Nvec,Ivec 							=	paramProcess.MOSFETrdson(switchesIdsonPath,'SCTH35N65G2V','_Rdson')
Ioff,catOFF,Eoff					=	paramProcess.MOSFETenergies(switchesEoffPath,'SCTH35N65G2V','_Eoff')
Voff,catOFF_Temp,Eoff_Temp			=	paramProcess.MOSFETenergies(switchesEoffPath,'SCTH35N65G2V','_Eoff_Temp')
Ion,catON,Eon 						=	paramProcess.MOSFETenergies(switchesEonPath,'SCTH35N65G2V','_Eon')
Von,catON_Temp,Eon_Temp				=	paramProcess.MOSFETenergies(switchesEonPath,'SCTH35N65G2V','_Eon_Temp')
Vfvec,Ifvec,Rd,Vt					=	paramProcess.DiodeVI_data(bodyDiodeVIPath,'SCTH35N65G2V')
#Vds_vec,Ids_vec 					=	paramProcess.Forward_Transfer_data(switchesTransferPath,'SCTH35N65G2V')

SCTH35N65G2V		=	{																																	#*	SCTH35N65G2V parameters
							'Config'						:	1																						,	#!	1->electric integrated | 2->electric separate | 3->thermal integrated | 4->thermal separate
							'Transistor'  			: 	{																									#!	transistors parameters
									'Config'				:	2																						,	#?	1->real model | 2->ideal model | 3->behavioral model
									'Thermal'           	:   ''                                  													,   #? 	selected transistor
									'Custom'            	:   []                 																		,   #? 	transistor provided custom variables
									'g_fs'					:	1e6																						,	#?	forward transconductance
									'Rg'					:	1																						,	#?	internal gate resistance
									'Lg'					:	0																						,	#?	gate pin inductance
									'Rds_on'            	:   Rvec[-1][-1]*1e-3																		,   #? 	transistor ON resistance
									'Rds_off'				:	'inf'																					,	#?	transistor OFF resistance
									'Rvec'					:	(np.array(Rvec)*1e-3).tolist()														,	#?	absolute Rdson vector corresponding to junction temperature
									'Tvec'					:	Tvec 																					,	#?	junction temperature vector for Rdson
									'RTconfig'				:	1																						,	#?	choose which RT vector to be used
									'RdsonScale'			:	1.0																						,	#?	Rdson scaling to account for min, typ and max deviations
									'Nvec'					:	Nvec 																					,	#?	normalized Rdson vector corresponding to current
									'Ivec'					:	Ivec																					,	#?	current vector for normalized Rdson
									'NIconfig'				:	1																						,	#?	choose which NI vector to be used
									'IdsonScale'			:	1.0																						,	#?	Idson resistance scaling to account for min, typ and max deviations
									'Rsrc'					:	0																						,	#?	kelvin source pin resistance
									'Lsrc'					:	0																						,	#?	kelvin source pin inductance
									'Ls'					:	0																						,	#?	package source inductance
                                    'Ld'					:	0																						,	#?	package drain inductance
									'Rs'					:	0																						,	#?	package source resistance
									'Rd'					:	0																						,	#?	package drain inductance
									'Ksrc'					:	1																						,	#?	kelvin source option, 0->no kelvin | 1->kelvin
									'Vblock'            	:   650                                	 													,   #? 	transistor blocking voltage
									'Id'                	:   45                                 														,   #? 	transistor drain current
									'Tr'                	:   30e-9                                  													,   #? 	transistor rise time
									'Tf'                	:   44e-9                                     												, 	#? 	transistor fall time
									'Avalanche'		:	{																									#!	transistor avalanche parameters
										'Config'			:	2																						,	#?	1->enable | 2->disable
										'Voltage'			:	650 																					,	#?	avalanche voltage
										'Resistance'		:	1e-3																						#?	avalanche resistance to break voltage state-dependency
									},
									'Transfer'		:	{																									#!	transistor forward transfer parameters
										'Vds'				:	Vds_vec																					,	#?	drain-source voltage vector
										'Vgs'				:	[0,20]																					,	#?	gate-source voltage vector
										'Ids'				:	Ids_vec																					,	#?	drain current vector
										'Factor_ON'			:	1.0																						,	#?	scaling factor for Ids at turn ON
										'Factor_OFF'		:	1.0																						,	#?	scaling factor for Ids at turn OFF
										'Factor_Vgs_ON'		:	1.0																						,	#?	scaling factor for Vgs at turn ON
										'Factor_Vgs_OFF'	:	1.0																						,	#?	scaling factor for Vgs at turn OFF
										'Vcoss'				:	0																						,	#?	initial voltage of the Coss
									},
						},
							'BodyDiode'  			:	{																									#!	body diodes paramteters
									'Config'				:	4																						,	#?	1->non-ideal RR | 2->non-ideal | 3->ideal RR | 4->ideal
									'Thermal'           	:   ''                                  													,   #? 	separate body diode
									'Custom'            	:   []					                 													,   #? 	body diode provided custrom variables
									'Rd_on'             	:   Rd[-1]													                              	,  	#? 	body diode ON resistance
									'Rd_off'				:	'inf'																					,	#?	body diode OFF resistance
									'Vf'					:	Vt[-1]																					,	#? 	body diode forward voltage
									'If'                	:   45                                 														,   #? 	body diode forward current
									'dIr'               	:   1000e6                                 													,   #? 	body diode current slope
									'Lrr'					:	1e-9																					,	#?	body diode reverse recovery inductance
									'Trr'               	:   18e-9                                  													,   #? 	body diode reverse recovery time
									'Irr'               	:   7                                   													,   #? 	body diode reverse recovery current
									'Qrr'               	:   85e-9	                                  												,	#? 	body diode reverse recovery charge
									'Is'                  	:   20	              																		, 	#? 	body diode reference current
									'Vs'					:	400																						,	#?	body diode reference voltage
                                    'VIcurve'		:	{																									#!	body diode VI characteristics
                                        'Vfvec'				:	Vfvec																					,	#?	forward voltage vector
                                        'Ifvec'				:	Ifvec																					,	#?	forward current vector
										'Rdvec'				:	Rd																						,	#?	dynamic resistance vector
										'Vtvec'				:	Vt																						,	#?	threshold voltage vector
                                        'Temps'				:	[25,175]																				,	#?	temperature vector
                                        'Vfscale'			:	1.0																							#?	Vf scaling to account for min, typ and max deviations
									},
						},
							'GateDriver'			:	{																									#!	gate driver parameters
									'Config'				:	3																						,	#?	1->high-side | 2->low-side | 3->disable
									'Von'					:	12																						,	#?	ON driving voltage
									'Voff'					:	0																						,	#?	OFF driving voltage
									'Ron'					:	5																						,	#?	sourcing output resistance
									'Roff'					:	5																						,	#?	sinking output resistance
									'Lon'					:	0																						,	#?	sourcing output inductance
									'Loff'					:	0																						,	#?	sinking output inductance
									'Cload'					:	0																						,	#?	capacitive load on output
									'Rload'					:	'inf'																					,	#?	resistive load on output
									'Delay'					:	0																						,	#?	input-to-output total deadtime
									'Trise'					:	0																						,	#?	output rising time
									'Tfall'					:	0																						,	#?	output falling time
									'UVLO_Start'			:	7.0																						,	#?	UVLO startup voltage threshold
									'UVLO_Stop'				:	6.5																						,	#?	UVLO shutdown voltage threshold
									'UVLO_Delay'			:	100e-9																					,	#?	delay between UVLO startup and shutdown
									'Init_State'			:	0																						,	#?	initial toggling state, 0->OFF | 1->ON
									'CurrentLimit'	:	{																									#*	current limit of driver stage
										'Config'			:	2																						,	#?	1->enable | 2->disable
										'Ts'				: 	0 																						,	#?	sampling time between inductive & capacitive links
										'tau'				: 	0																						,	#?	first-order delay between inductive & capacitive links
                                    	'Rs'				: 	0																						,	#?	source impedance of inductive link
										'Cs'				:	1e-12																					,	#?	source capacitance of capacitive link
                                        'UpLim'				: 	10																						,	#?	max current limit on capacitive link
                                        'LoLim'				: 	-10																						,	#?	min current limit on capacitive link
                                        'Voffset'			: 	0																							#?	voltage offset between inductive & capacitive links
									},
									'Masking'		:	{																									#*	switching stages masking
										'ON'	:	{																										#	ON path masking
											'Config'		:	2																						,	#?	1->enable | 2->disable
											'HIGH'	:	{																									#!	HIGH mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[0, 0]																						#?	mask output
											},
											'LOW'	:	{																									#!	LOW mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[1, 1]																						#?	mask output
											}
										},
										'OFF'	:	{																										#	OFF path masking
											'Config'		:	2																						,	#?	1->enable | 2->disable
											'HIGH'	:	{																									#!	HIGH mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[0, 0]																						#?	mask output
											},
											'LOW'	:	{																									#!	LOW mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[1, 1]																						#?	mask output
											}
										}
									},
									'Boot'			:	{																									#*	bootstrap/charge pump parameters
										'Config'			:	1																						,	#?	1->bootstrap | 2->charge pump
										'Von'				:	14																						,	#?	boostrap driving voltage
										'Cboot'				:	4.7e-6																					,	#?	bootstrap capacitance
										'Vinit'				:	0																						,	#?	bootstrap capacitance initial voltage
										'Rboot'				:	10																						,	#?	bootstrap resistance
										'Vfboot'			:	0.87																					,	#?	bootstrap diode forward voltage
										'Rdboot'			:	1e-3																					,	#?	bootstrap diode ON-state resistance
										'Ichrg'				:	300e-6																					,	#?	charge pump supply current
										'Idis'				:	5e-6																					,	#?	charge pump loading or leakage current
										'Cpar'				:	0																						,	#?	charge pump parallel cap to break state/source dependency
									    'UVLO_Start'		:	11.6																					,	#?	threshold value to start the charge pump
										'UVLO_Stop'			:	12.4																						#?	threshold value to stop the charge pump
									},
							},
							'GateNetwork'			:	{																									#!	gate drive circuit parameters
									'Config'				:	2																						,	#?	1-> enable | 2->disable
									'ON_Path'		:	{																									#*	sourcing path parameters
										'Rg'				:	5																						,	#?	gate ON path resistance
										'Lg'				:	0																						,	#?	gate ON path inductance
										'Rload'				:	10e3																					,	#?	gate pull down resistance
										'Diode'	:	{																										#	reverse blocking diode parameters
											'Vf'			:	0																						,	#?	forward voltage
											'Rd_on'			:	0																						,	#?	ON-state resistance
										},
									},
									'OFF_Path'		:	{																									#*	sinking path parameters
										'Rg'				:	5																						,	#?	gate OFF path resistance
										'Lg'				:	0																						,	#?	gate OFF path inductance
										'Diode'	:	{																										#	reverse blocking diode parameters
											'Vf'			:	0																						,	#?	forward voltage
											'Rd_on'			:	0																						,	#?	ON-state resistance
										},
									},
									'NegVolt'		:	{																									#*	negative voltage generator parameters
										'Config'			:	2																						,	#?	1-> enable | 2->disable
										'Dz'	:	{																										#	zener diode parameters
											'Vf'			:	0.7																						,	#?	forward voltage
											'Rd_on'			:	1e-3																					,	#?	ON-state resistance
											'Vz'			:	2																						,	#?	Zener breakdown voltage
											'Rz'			:	1e-3																					,	#?	Zener resistance
										},
										'Dp'	:	{																										#	peak detector diode
											'Vf'			:	0.0																						,	#?	forward voltage
											'Rd_on'			:	0.0																						,	#?	ON-state resistance
										},
										'Cz'	:	{																										#	Zener capacitor parameters
											'Config'		:	1																						,	#?	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
											'Csingle'		:	1e-6																					,	#?	single capacitor value
											'Rsingle'		:	5e-3																					,	#?	ESR of single capacitor
											'Lsingle'		:	0																						,	#?	ESL of single capacitor
											'nPar'			:	1																						,	#?	number of parallel connections
											'nSer'			:	1																						,	#?	number of series connections
											'Vinit'			:	0																						,	#?	capacitor initial voltage
										},
										'Cp'	:	{																										#	peak detector capacitor parameters
											'Config'		:	1																						,	#?	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
											'Csingle'		:	2.2e-6																					,	#?	single capacitor value
											'Rsingle'		:	5e-3																					,	#?	ESR of single capacitor
											'Lsingle'		:	0																						,	#?	ESL of single capacitor
											'nPar'			:	1																						,	#?	number of parallel connections
											'nSer'			:	1																						,	#?	number of series connections
											'Vinit'			:	0																						,	#?	capacitor initial voltage
										},
										'Rp1'				:	43																						,	#?	current limiter of peak detector current
										'Rp2'				:	4.7e3																					,	#?	load resistor to charge the zener diode
									},
								},
							'nParallel'   					:	1                                       												,   #? 	number of parallel devices
							'Rth_jc'						:	0.72																					,	#?	junction-to-case thermal resistance
							'Cth_jc'						:	0.00																					,	#?	junction-to-case thermal capacitance
							'Rth_ca'              			:   4.80            																		,   #? 	case-to-ambient thermal resistance
							'Cth_ca'              			:   0.0             																		,   #? 	case-to-ambient thermal capacitance
							'Tinit'							:	0.0																						,	#?	initial juntion temperature
							'Pinit'							:	0.0																						,	#?	initial power dissipation
							'Coss'					: 	{																									#!	device Coss parameters
								'C'							:	Coss_eff					 															,	#?	device parasitic output capacitance
								'R'							:	0																						,	#?	Coss resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Coss inductance to reduce current slope
								'Coss_er'					:	Crss_er																					,	#?	energy-related Coss
								'Coss_tr'					:	Coss_tr																					,	#?	time-related Coss
								'Vvec'						:	Coss[0]																					,	#? 	device Coss voltage vector
								'Cvec'						:	Coss[1]																					,	#?	device Coss capacity vector
								'Offset'					:	0																						,	#?	parasitic offset to Coss
                                'Factor'					:	1.0																						,	#?	parasitic tolerance to Coss
								'Qoss'						:	Qoss																					,	#?	equivalent charge of Coss
								'Eoss'						:	Eoss																					,	#?	equivalent energy of Coss
								'Config'					:	5																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
						},
                        	'Crss'					:	{																									#!	device Crss parameters
                                'C'							:	Crss_eff					 															,	#?	device parasitic reverse transfer capacitance
								'R'							:	0																						,	#?	Crss resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Crss inductance to reduce current slope
								'Crss_er'					:	Crss_er																					,	#?	energy-related Crss
								'Crss_tr'					:	Crss_tr																					,	#?	time-related Crss
								'Vvec'						:	Crss[0]																					,	#?	device Crss voltage vector
                                'Cvec'						:	Crss[1]																					,	#?	device Crss capacity vector
								'Qvec'						:	Qrss																					,	#?	device accumulated Crss charge vector
								'Offset'					:	0																						,	#?	parasitic offset to Crss
								'Factor'					:	1.0																						,	#?	parasitic tolerance to Crss
								'Qrss'						:	Qrss																					,	#?	equivalent charge of Crss
								'Erss'						:	Erss																					,	#?	equivalent energe of Crss
								'Config'					:	5																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
						},
							'Ciss'					:	{																									#!	device Ciss parameters
								'C'							:	Ciss_eff					 															,	#?	device parasitic input capacitance
								'R'							:	0																						,	#?	Ciss resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Ciss inductance to reduce current slope
								'Ciss_er'					:	Ciss_er																					,	#?	energy-related Ciss
								'Ciss_tr'					:	Ciss_tr																					,	#?	time-related Ciss
								'Vvec'						:	Ciss[0]																					,	#?	device Ciss voltage vector
								'Cvec'						:	Ciss[1]																					,	#?	device Ciss capacity vector
								'Offset'					:	0																						,	#?	parasitic offset to Ciss
								'Factor'					:	1.0																						,	#?	parasitic tolerance to Ciss
								'Qiss'						:	Qiss																					,	#?	equivalent charge of Ciss
								'Eiss'						:	Eiss																					,	#?	equivalent energy of Ciss
								'Config'					:	5																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Cds'					:	{																									#!	device Cds parameters
								'C'							:	Cds_eff					 																,	#?	device parasitic Cds capacitance
								'R'							:	0																						,	#?	Cds resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Cds inductance to reduce current slope
								'Cds_er'					:	Cds_er																					,	#?	energy-related Cds
								'Cds_tr'					:	Cds_tr																					,	#?	time-related Cds
								'Vvec'						:	Coss[0]																					,	#?	device Cds voltage vector
								'Cvec'						:	Cds																						,	#?	device Cds capacity vector
								'Offset_ON'					:	0																						,	#?	tuning offset for turn ON
								'Offset_OFF'				:	0																						,	#?	tuning offset for turn OFF
								'Factor_ON'					:	1.0																						,	#?	tuning factor for turn ON
								'Factor_OFF'				:	1.0																						,	#?	tuning factor for turn OFF
								'Config'					:	4																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Cgd'					:	{																									#!	device Cgd parameters
								'C'							:	Cgd_eff							 														,	#?	device parasitic Cgd capacitance
								'R'							:	0																						,	#?	Cgd resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Cgd inductance to reduce current slope
								'Cgd_er'					:	Cgd_er																					,	#?	energy-related Cgd
								'Cgd_tr'					:	Cgd_tr																					,	#?	time-related Cgd
								'Vvec'						:	Crss[0]																					,	#?	device Cgd voltage vector
								'Cvec'						:	Cgd																						,	#?	device Cgd capacity vector
								'Offset_ON'					:	0																						,	#?	tuning offset for turn ON
								'Offset_OFF'				:	0																						,	#?	tuning offset for turn OFF
								'Factor_ON'					:	1.0																						,	#?	tuning factor for turn ON
								'Factor_OFF'				:	1.0																						,	#?	tuning factor for turn OFF
								'Config'					:	4																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Cgs'					:	{																									#!	device Cgs parameters
								'C'							:	Cgs_eff					 																,	#?	device parasitic Cgs capacitance
								'R'							:	0																						,	#?	Cgs resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Cgs inductance to reduce current slope
								'Cgs_er'					:	Cgs_er																					,	#?	energy-related Cgs
								'Cgs_tr'					:	Cgs_tr																					,	#?	time-related Cgs
								'Vvec'						:	Ciss[0]																					,	#?	device Cgs voltage vector
								'Cvec'						:	Cgs																						,	#?	device Cgs capacity vector
								'Offset_ON'					:	0																						,	#?	tuning offset for turn ON
								'Offset_OFF'				:	0																						,	#?	tuning offset for turn OFF
								'Factor_ON'					:	1.0																						,	#?	tuning factor for turn ON
								'Factor_OFF'				:	1.0																						,	#?	tuning factor for turn OFF
								'Config'					:	4																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Eoff'					:	{																									#!	transistor turn-OFF energy losses
									'Ivec'					:	Ioff																					,	#?	turn-OFF energy current vector
									'Rgvec'					:	[0,100]																					,	#?	OFF path gate resistances vector
									'Tjvec'					:	[-55,175]																				,	#?	junction temperature vector
                                    'Vvec'					:	Voff																					,	#?	turn-OFF voltage vector
                                    'Evec'					:	Eoff																					,	#?	turn-OFF energy vectors
									'Evec_Temp'				:	Eoff_Temp																				,	#?	turn-OFF energy temp scaling vectors
                                    'CAT'					:	catOFF																					,	#?	octave Eoff energy syntax
									'CAT_Temp'				:	catOFF_Temp																				,	#?	octave Eoff energy temp scaling syntax
									'Vgs'					:	0																						,	#?	used OFF path gate-source voltage
									'Vth'					:	1.5																						,	#?	used OFF path threshold voltage
									'Rg'					:	0																							#?	used OFF path gate resistance
						},
							'Eon'					:	{																									#!	transistor turn-ON energy losses
									'Ivec'					:	Ion																						,	#?	turn-ON energy current vector
									'Rgvec'					:	[0,100]																					,	#?	ON path gate resistances vector
									'Tjvec'					:	[-55,175]																				,	#?	junction temperature vector
                                    'Vvec'					:	Von																						,	#?	turn-ON voltage vector
                                    'Evec'					:	Eon																						,	#?	turn-ON energy vectors
									'Evec_Temp'				:	Eon_Temp																				,	#?	turn-ON energy temp scaling vectors
                                    'CAT'					:	catON																					,	#?	octave Eon energy syntax
									'CAT_Temp'				:	catON_Temp																				,	#?	octave Eon energy temp scaling syntax
									'Vgs'					:	12																						,	#?	used ON path gate-source voltage
									'Vth'					:	1.5																						,	#?	used ON path threshold voltage
									'Rg'					:	0																							#?	used ON path gate resistance
						},
							'Tau_deg'						:	100e-9																					,	#?	deglitch filter for currents and voltages
							'RCsnubber'						:	2																						,	#?	1->enable | 2->disable
						}

#?----------------------------------------------------------------------------------------------------------------------------------------------------------------------

Coss,Qoss,Eoss,Coss_tr,Coss_er		=	paramProcess.MOSFETcaps(switchesCossPath,'SCT055HU65G3AG','_Coss')
Crss,Qrss,Erss,Crss_tr,Crss_er 		=	paramProcess.MOSFETcaps(switchesCrssPath,'SCT055HU65G3AG','_Crss')
Ciss,Qiss,Eiss,Ciss_tr,Ciss_er 		=	paramProcess.MOSFETcaps(switchesCissPath,'SCT055HU65G3AG','_Ciss')
Coss_eff 							=	paramProcess.getCmos(Coss,Coss_tr,Coss_er,Coss[0][0],True)
Ciss_eff 							=	paramProcess.getCmos(Ciss,Ciss_tr,Ciss_er,Ciss[0][0],True)
Crss_eff 							=	paramProcess.getCmos(Crss,Crss_tr,Crss_er,Crss[0][0],True)
Cds 						        =	(np.array(Coss[1]) - np.array(Crss[1])).tolist()
Cgs						        	=	(np.array(Ciss[1]) - np.array(Crss[1])).tolist()
Cgd						        	=	Crss[1]
Cds_tr						        =	(np.array(Coss_tr) - np.array(Crss_tr)).tolist()
Cgs_tr						        =	(np.array(Ciss_tr) - np.array(Crss_tr)).tolist()
Cgd_tr						        =	Crss_tr
Cds_er						        =	(np.array(Coss_er) - np.array(Crss_er)).tolist()
Cgs_er						        =	(np.array(Ciss_er) - np.array(Crss_er)).tolist()
Cgd_er						        =	Crss_er
Cds_eff 							=	paramProcess.getCmos([Coss[0],Cds],Cds_tr,Cds_er,Coss[0][0],True)
Cgs_eff 							=	paramProcess.getCmos([Ciss[0],Cgs],Cgs_tr,Cgs_er,Ciss[0][0],True)
Cgd_eff 							=	Crss_eff
Rvec,Tvec							=	paramProcess.MOSFETrdson(switchesRdsonPath,'SCT055HU65G3AG','_Rdson')
Nvec,Ivec 							=	paramProcess.MOSFETrdson(switchesIdsonPath,'SCT055HU65G3AG','_Rdson')
Ioff,catOFF,Eoff					=	paramProcess.MOSFETenergies(switchesEoffPath,'SCT055HU65G3AG','_Eoff')
Voff,catOFF_Temp,Eoff_Temp			=	paramProcess.MOSFETenergies(switchesEoffPath,'SCT055HU65G3AG','_Eoff_Temp')
Ion,catON,Eon 						=	paramProcess.MOSFETenergies(switchesEonPath,'SCT055HU65G3AG','_Eon')
Von,catON_Temp,Eon_Temp				=	paramProcess.MOSFETenergies(switchesEonPath,'SCT055HU65G3AG','_Eon_Temp')
Vfvec,Ifvec,Rd,Vt					=	paramProcess.DiodeVI_data(bodyDiodeVIPath,'SCT055HU65G3AG')
Vds_vec,Ids_vec 					=	paramProcess.Forward_Transfer_data(switchesTransferPath,'SCT055HU65G3AG')

SCT055HU65G3AG		=	{																																	#*	SCT055HU65G3AG parameters
							'Config'						:	1																						,	#!	1->electric integrated | 2->electric separate | 3->thermal integrated | 4->thermal separate
							'Transistor'  			: 	{																									#!	transistors parameters
									'Config'				:	2																						,	#?	1->real model | 2->ideal model | 3->behavioral model
									'Thermal'           	:   ''                                  													,   #? 	selected transistor
									'Custom'            	:   []                 																		,   #? 	transistor provided custom variables
									'g_fs'					:	1e6																						,	#?	forward transconductance
									'Rg'					:	1																						,	#?	internal gate resistance
									'Lg'					:	0																						,	#?	gate pin inductance
									'Rds_on'            	:   Rvec[-1][-1]*1e-3																		,   #? 	transistor ON resistance
									'Rds_off'				:	'inf'																					,	#?	transistor OFF resistance
									'Rvec'					:	(np.array(Rvec)*1e-3).tolist()														,	#?	absolute Rdson vector corresponding to junction temperature
									'Tvec'					:	Tvec 																					,	#?	junction temperature vector for Rdson
									'RTconfig'				:	1																						,	#?	choose which RT vector to be used
									'RdsonScale'			:	1.0																						,	#?	Rdson scaling to account for min, typ and max deviations
									'Nvec'					:	Nvec 																					,	#?	normalized Rdson vector corresponding to current
									'Ivec'					:	Ivec																					,	#?	current vector for normalized Rdson
									'NIconfig'				:	1																						,	#?	choose which NI vector to be used
									'IdsonScale'			:	1.0																						,	#?	Idson resistance scaling to account for min, typ and max deviations
									'Rsrc'					:	0																						,	#?	kelvin source pin resistance
									'Lsrc'					:	0																						,	#?	kelvin source pin inductance
									'Ls'					:	0																						,	#?	package source inductance
                                    'Ld'					:	0																						,	#?	package drain inductance
									'Rs'					:	0																						,	#?	package source resistance
									'Rd'					:	0																						,	#?	package drain inductance
									'Ksrc'					:	1																						,	#?	kelvin source option, 0->no kelvin | 1->kelvin
									'Vblock'            	:   650                                	 													,   #? 	transistor blocking voltage
									'Id'                	:   40                                 														,   #? 	transistor drain current
									'Tr'                	:   27e-9                                													,   #? 	transistor rise time
									'Tf'                	:   19.4e-9                                    												, 	#? 	transistor fall time
									'Avalanche'		:	{																									#!	transistor avalanche parameters
										'Config'			:	2																						,	#?	1->enable | 2->disable
										'Voltage'			:	650																						,	#?	avalanche voltage
										'Resistance'		:	1e-3																						#?	avalanche resistance to break voltage state-dependency
									},
									'Transfer'		:	{																									#!	transistor forward transfer parameters
										'Vds'				:	Vds_vec																					,	#?	drain-source voltage vector
										'Vgs'				:	list(np.arange(1.1,21.0+0.5,0.5))																					,	#?	gate-source voltage vector
										'Ids'				:	Ids_vec																					,	#?	drain current vector
										'Factor_ON'			:	1.0																						,	#?	scaling factor for Ids at turn ON
										'Factor_OFF'		:	1.0																						,	#?	scaling factor for Ids at turn OFF
										'Factor_Vgs_ON'		:	1.0																						,	#?	scaling factor for Vgs at turn ON
										'Factor_Vgs_OFF'	:	1.0																						,	#?	scaling factor for Vgs at turn OFF
										'Vcoss'				:	0																						,	#?	initial voltage of the Coss
									},
						},
							'BodyDiode'  			:	{																									#!	body diodes paramteters
									'Config'				:	4																						,	#?	1->non-ideal RR | 2->non-ideal | 3->ideal RR | 4->ideal
									'Thermal'           	:   ''                                  													,   #? 	separate body diode
									'Custom'            	:   []					                 													,   #? 	body diode provided custrom variables
									'Rd_on'             	:   Rd[-1]													                              	,  	#? 	body diode ON resistance
									'Rd_off'				:	'inf'																					,	#?	body diode OFF resistance
									'Vf'					:	Vt[-1]																					,	#? 	body diode forward voltage
									'If'                	:   40                                 														,   #? 	body diode forward current
									'dIr'               	:   1000e6                                 													,   #? 	body diode current slope
									'Lrr'					:	1e-9																					,	#?	body diode reverse recovery inductance
									'Trr'               	:   51e-9                                  													,   #? 	body diode reverse recovery time
									'Irr'               	:   6.3                                   													,   #? 	body diode reverse recovery current
									'Qrr'               	:   71e-9	                                  												,	#? 	body diode reverse recovery charge
									'Is'                  	:   15	              																		, 	#? 	body diode reference current
									'Vs'					:	400																						,	#?	body diode reference voltage
                                    'VIcurve'		:	{																									#!	body diode VI characteristics
                                        'Vfvec'				:	Vfvec																					,	#?	forward voltage vector
                                        'Ifvec'				:	Ifvec																					,	#?	forward current vector
										'Rdvec'				:	Rd																						,	#?	dynamic resistance vector
										'Vtvec'				:	Vt																						,	#?	threshold voltage vector
                                        'Temps'				:	[25,175]																				,	#?	temperature vector
                                        'Vfscale'			:	1.0																							#?	Vf scaling to account for min, typ and max deviations
									},
						},
							'GateDriver'			:	{																									#!	gate driver parameters
									'Config'				:	3																						,	#?	1->high-side | 2->low-side | 3->disable
									'Von'					:	12																						,	#?	ON driving voltage
									'Voff'					:	0																						,	#?	OFF driving voltage
									'Ron'					:	5																						,	#?	sourcing output resistance
									'Roff'					:	5																						,	#?	sinking output resistance
									'Lon'					:	0																						,	#?	sourcing output inductance
									'Loff'					:	0																						,	#?	sinking output inductance
									'Cload'					:	0																						,	#?	capacitive load on output
									'Rload'					:	'inf'																					,	#?	resistive load on output
									'Delay'					:	0																						,	#?	input-to-output total deadtime
									'Trise'					:	0																						,	#?	output rising time
									'Tfall'					:	0																						,	#?	output falling time
									'UVLO_Start'			:	7.0																						,	#?	UVLO startup voltage threshold
									'UVLO_Stop'				:	6.5																						,	#?	UVLO shutdown voltage threshold
									'UVLO_Delay'			:	100e-9																					,	#?	delay between UVLO startup and shutdown
									'Init_State'			:	0																						,	#?	initial toggling state, 0->OFF | 1->ON
									'CurrentLimit'	:	{																									#*	current limit of driver stage
										'Config'			:	2																						,	#?	1->enable | 2->disable
										'Ts'				: 	0 																						,	#?	sampling time between inductive & capacitive links
										'tau'				: 	0																						,	#?	first-order delay between inductive & capacitive links
                                    	'Rs'				: 	0																						,	#?	source impedance of inductive link
										'Cs'				:	1e-12																					,	#?	source capacitance of capacitive link
                                        'UpLim'				: 	10																						,	#?	max current limit on capacitive link
                                        'LoLim'				: 	-10																						,	#?	min current limit on capacitive link
                                        'Voffset'			: 	0																							#?	voltage offset between inductive & capacitive links
									},
									'Masking'		:	{																									#*	switching stages masking
										'ON'	:	{																										#	ON path masking
											'Config'		:	2																						,	#?	1->enable | 2->disable
											'HIGH'	:	{																									#!	HIGH mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[0, 0]																						#?	mask output
											},
											'LOW'	:	{																									#!	LOW mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[1, 1]																						#?	mask output
											}
										},
										'OFF'	:	{																										#	OFF path masking
											'Config'		:	2																						,	#?	1->enable | 2->disable
											'HIGH'	:	{																									#!	HIGH mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[0, 0]																						#?	mask output
											},
											'LOW'	:	{																									#!	LOW mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[1, 1]																						#?	mask output
											}
										}
									},
									'Boot'			:	{																									#*	bootstrap/charge pump parameters
										'Config'			:	1																						,	#?	1->bootstrap | 2->charge pump
										'Von'				:	14																						,	#?	boostrap driving voltage
										'Cboot'				:	4.7e-6																					,	#?	bootstrap capacitance
										'Vinit'				:	0																						,	#?	bootstrap capacitance initial voltage
										'Rboot'				:	10																						,	#?	bootstrap resistance
										'Vfboot'			:	0.87																					,	#?	bootstrap diode forward voltage
										'Rdboot'			:	1e-3																					,	#?	bootstrap diode ON-state resistance
										'Ichrg'				:	300e-6																					,	#?	charge pump supply current
										'Idis'				:	5e-6																					,	#?	charge pump loading or leakage current
										'Cpar'				:	0																						,	#?	charge pump parallel cap to break state/source dependency
									    'UVLO_Start'		:	11.6																					,	#?	threshold value to start the charge pump
										'UVLO_Stop'			:	12.4																						#?	threshold value to stop the charge pump
									},
							},
							'GateNetwork'			:	{																									#!	gate drive circuit parameters
									'Config'				:	2																						,	#?	1-> enable | 2->disable
									'ON_Path'		:	{																									#*	sourcing path parameters
										'Rg'				:	5																						,	#?	gate ON path resistance
										'Lg'				:	0																						,	#?	gate ON path inductance
										'Rload'				:	10e3																					,	#?	gate pull down resistance
										'Diode'	:	{																										#	reverse blocking diode parameters
											'Vf'			:	0																						,	#?	forward voltage
											'Rd_on'			:	0																						,	#?	ON-state resistance
										},
									},
									'OFF_Path'		:	{																									#*	sinking path parameters
										'Rg'				:	5																						,	#?	gate OFF path resistance
										'Lg'				:	0																						,	#?	gate OFF path inductance
										'Diode'	:	{																										#	reverse blocking diode parameters
											'Vf'			:	0																						,	#?	forward voltage
											'Rd_on'			:	0																						,	#?	ON-state resistance
										},
									},
									'NegVolt'		:	{																									#*	negative voltage generator parameters
										'Config'			:	2																						,	#?	1-> enable | 2->disable
										'Dz'	:	{																										#	zener diode parameters
											'Vf'			:	0.7																						,	#?	forward voltage
											'Rd_on'			:	1e-3																					,	#?	ON-state resistance
											'Vz'			:	2																						,	#?	Zener breakdown voltage
											'Rz'			:	1e-3																					,	#?	Zener resistance
										},
										'Dp'	:	{																										#	peak detector diode
											'Vf'			:	0.0																						,	#?	forward voltage
											'Rd_on'			:	0.0																						,	#?	ON-state resistance
										},
										'Cz'	:	{																										#	Zener capacitor parameters
											'Config'		:	1																						,	#?	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
											'Csingle'		:	1e-6																					,	#?	single capacitor value
											'Rsingle'		:	5e-3																					,	#?	ESR of single capacitor
											'Lsingle'		:	0																						,	#?	ESL of single capacitor
											'nPar'			:	1																						,	#?	number of parallel connections
											'nSer'			:	1																						,	#?	number of series connections
											'Vinit'			:	0																						,	#?	capacitor initial voltage
										},
										'Cp'	:	{																										#	peak detector capacitor parameters
											'Config'		:	1																						,	#?	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
											'Csingle'		:	2.2e-6																					,	#?	single capacitor value
											'Rsingle'		:	5e-3																					,	#?	ESR of single capacitor
											'Lsingle'		:	0																						,	#?	ESL of single capacitor
											'nPar'			:	1																						,	#?	number of parallel connections
											'nSer'			:	1																						,	#?	number of series connections
											'Vinit'			:	0																						,	#?	capacitor initial voltage
										},
										'Rp1'				:	43																						,	#?	current limiter of peak detector current
										'Rp2'				:	4.7e3																					,	#?	load resistor to charge the zener diode
									},
								},
							'nParallel'   					:	1                                       												,   #? 	number of parallel devices
							'Rth_jc'						:	0.85																					,	#?	junction-to-case thermal resistance
							'Cth_jc'						:	0.00																					,	#?	junction-to-case thermal capacitance
							'Rth_ca'              			:   4.80            																		,   #? 	case-to-ambient thermal resistance
							'Cth_ca'              			:   0.0             																		,   #? 	case-to-ambient thermal capacitance
							'Tinit'							:	0.0																						,	#?	initial juntion temperature
							'Pinit'							:	0.0																						,	#?	initial power dissipation
							'Coss'					: 	{																									#!	device Coss parameters
								'C'							:	Coss_eff					 															,	#?	device parasitic output capacitance
								'R'							:	0																						,	#?	Coss resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Coss inductance to reduce current slope
								'Coss_er'					:	Crss_er																					,	#?	energy-related Coss
								'Coss_tr'					:	Coss_tr																					,	#?	time-related Coss
								'Vvec'						:	Coss[0]																					,	#? 	device Coss voltage vector
								'Cvec'						:	Coss[1]																					,	#?	device Coss capacity vector
								'Offset'					:	0																						,	#?	parasitic offset to Coss
                                'Factor'					:	1.0																						,	#?	parasitic tolerance to Coss
								'Qoss'						:	Qoss																					,	#?	equivalent charge of Coss
								'Eoss'						:	Eoss																					,	#?	equivalent energy of Coss
								'Config'					:	5																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
						},
                        	'Crss'					:	{																									#!	device Crss parameters
                                'C'							:	Crss_eff					 															,	#?	device parasitic reverse transfer capacitance
								'R'							:	0																						,	#?	Crss resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Crss inductance to reduce current slope
								'Crss_er'					:	Crss_er																					,	#?	energy-related Crss
								'Crss_tr'					:	Crss_tr																					,	#?	time-related Crss
								'Vvec'						:	Crss[0]																					,	#?	device Crss voltage vector
                                'Cvec'						:	Crss[1]																					,	#?	device Crss capacity vector
								'Qvec'						:	Qrss																					,	#?	device accumulated Crss charge vector
								'Offset'					:	0																						,	#?	parasitic offset to Crss
								'Factor'					:	1.0																						,	#?	parasitic tolerance to Crss
								'Qrss'						:	Qrss																					,	#?	equivalent charge of Crss
								'Erss'						:	Erss																					,	#?	equivalent energe of Crss
								'Config'					:	5																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
						},
							'Ciss'					:	{																									#!	device Ciss parameters
								'C'							:	Ciss_eff					 															,	#?	device parasitic input capacitance
								'R'							:	0																						,	#?	Ciss resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Ciss inductance to reduce current slope
								'Ciss_er'					:	Ciss_er																					,	#?	energy-related Ciss
								'Ciss_tr'					:	Ciss_tr																					,	#?	time-related Ciss
								'Vvec'						:	Ciss[0]																					,	#?	device Ciss voltage vector
								'Cvec'						:	Ciss[1]																					,	#?	device Ciss capacity vector
								'Offset'					:	0																						,	#?	parasitic offset to Ciss
								'Factor'					:	1.0																						,	#?	parasitic tolerance to Ciss
								'Qiss'						:	Qiss																					,	#?	equivalent charge of Ciss
								'Eiss'						:	Eiss																					,	#?	equivalent energy of Ciss
								'Config'					:	5																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Cds'					:	{																									#!	device Cds parameters
								'C'							:	Cds_eff					 																,	#?	device parasitic Cds capacitance
								'R'							:	0																						,	#?	Cds resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Cds inductance to reduce current slope
								'Cds_er'					:	Cds_er																					,	#?	energy-related Cds
								'Cds_tr'					:	Cds_tr																					,	#?	time-related Cds
								'Vvec'						:	Coss[0]																					,	#?	device Cds voltage vector
								'Cvec'						:	Cds																						,	#?	device Cds capacity vector
								'Offset_ON'					:	0																						,	#?	tuning offset for turn ON
								'Offset_OFF'				:	0																						,	#?	tuning offset for turn OFF
								'Factor_ON'					:	1.0																						,	#?	tuning factor for turn ON
								'Factor_OFF'				:	1.0																						,	#?	tuning factor for turn OFF
								'Config'					:	4																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Cgd'					:	{																									#!	device Cgd parameters
								'C'							:	Cgd_eff							 														,	#?	device parasitic Cgd capacitance
								'R'							:	0																						,	#?	Cgd resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Cgd inductance to reduce current slope
								'Cgd_er'					:	Cgd_er																					,	#?	energy-related Cgd
								'Cgd_tr'					:	Cgd_tr																					,	#?	time-related Cgd
								'Vvec'						:	Crss[0]																					,	#?	device Cgd voltage vector
								'Cvec'						:	Cgd																						,	#?	device Cgd capacity vector
								'Offset_ON'					:	0																						,	#?	tuning offset for turn ON
								'Offset_OFF'				:	0																						,	#?	tuning offset for turn OFF
								'Factor_ON'					:	1.0																						,	#?	tuning factor for turn ON
								'Factor_OFF'				:	1.0																						,	#?	tuning factor for turn OFF
								'Config'					:	4																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Cgs'					:	{																									#!	device Cgs parameters
								'C'							:	Cgs_eff					 																,	#?	device parasitic Cgs capacitance
								'R'							:	0																						,	#?	Cgs resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Cgs inductance to reduce current slope
								'Cgs_er'					:	Cgs_er																					,	#?	energy-related Cgs
								'Cgs_tr'					:	Cgs_tr																					,	#?	time-related Cgs
								'Vvec'						:	Ciss[0]																					,	#?	device Cgs voltage vector
								'Cvec'						:	Cgs																						,	#?	device Cgs capacity vector
								'Offset_ON'					:	0																						,	#?	tuning offset for turn ON
								'Offset_OFF'				:	0																						,	#?	tuning offset for turn OFF
								'Factor_ON'					:	1.0																						,	#?	tuning factor for turn ON
								'Factor_OFF'				:	1.0																						,	#?	tuning factor for turn OFF
								'Config'					:	4																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Eoff'					:	{																									#!	transistor turn-OFF energy losses
									'Ivec'					:	Ioff																					,	#?	turn-OFF energy current vector
									'Rgvec'					:	[0,100]																					,	#?	OFF path gate resistances vector
									'Tjvec'					:	[-55,175]																				,	#?	junction temperature vector
                                    'Vvec'					:	Voff																					,	#?	turn-OFF voltage vector
                                    'Evec'					:	Eoff																					,	#?	turn-OFF energy vectors
									'Evec_Temp'				:	Eoff_Temp																				,	#?	turn-OFF energy temp scaling vectors
                                    'CAT'					:	catOFF																					,	#?	octave Eoff energy syntax
									'CAT_Temp'				:	catOFF_Temp																				,	#?	octave Eoff energy temp scaling syntax
									'Vgs'					:	0																						,	#?	used OFF path gate-source voltage
									'Vth'					:	1.5																						,	#?	used OFF path threshold voltage
									'Rg'					:	0																							#?	used OFF path gate resistance
						},
							'Eon'					:	{																									#!	transistor turn-ON energy losses
									'Ivec'					:	Ion																						,	#?	turn-ON energy current vector
									'Rgvec'					:	[0,100]																					,	#?	ON path gate resistances vector
									'Tjvec'					:	[-55,175]																				,	#?	junction temperature vector
                                    'Vvec'					:	Von																						,	#?	turn-ON voltage vector
                                    'Evec'					:	Eon																						,	#?	turn-ON energy vectors
									'Evec_Temp'				:	Eon_Temp																				,	#?	turn-ON energy temp scaling vectors
                                    'CAT'					:	catON																					,	#?	octave Eon energy syntax
									'CAT_Temp'				:	catON_Temp																				,	#?	octave Eon energy temp scaling syntax
									'Vgs'					:	12																						,	#?	used ON path gate-source voltage
									'Vth'					:	1.5																						,	#?	used ON path threshold voltage
									'Rg'					:	0																							#?	used ON path gate resistance
						},
							'Tau_deg'						:	100e-9																					,	#?	deglitch filter for currents and voltages
							'RCsnubber'						:	2																						,	#?	1->enable | 2->disable
						}

#! Si Switches models parameters
#?----------------------------------------------------------------------------------------------------------------------------------------------------------------------

Coss,Qoss,Eoss,Coss_tr,Coss_er		=	paramProcess.MOSFETcaps(switchesCossPath,'IAUT300N10S5N015','_Coss')
Crss,Qrss,Erss,Crss_tr,Crss_er 		=	paramProcess.MOSFETcaps(switchesCrssPath,'IAUT300N10S5N015','_Crss')
Ciss,Qiss,Eiss,Ciss_tr,Ciss_er 		=	paramProcess.MOSFETcaps(switchesCissPath,'IAUT300N10S5N015','_Ciss')
Coss_eff 							=	paramProcess.getCmos(Coss,Coss_tr,Coss_er,Coss[0][0],True)
Ciss_eff 							=	paramProcess.getCmos(Ciss,Ciss_tr,Ciss_er,Ciss[0][0],True)
Crss_eff 							=	paramProcess.getCmos(Crss,Crss_tr,Crss_er,Crss[0][0],True)
Cds 						        =	(np.array(Coss[1]) - np.array(Crss[1])).tolist()
Cgs						        	=	(np.array(Ciss[1]) - np.array(Crss[1])).tolist()
Cgd						        	=	Crss[1]
Cds_tr						        =	(np.array(Coss_tr) - np.array(Crss_tr)).tolist()
Cgs_tr						        =	(np.array(Ciss_tr) - np.array(Crss_tr)).tolist()
Cgd_tr						        =	Crss_tr
Cds_er						        =	(np.array(Coss_er) - np.array(Crss_er)).tolist()
Cgs_er						        =	(np.array(Ciss_er) - np.array(Crss_er)).tolist()
Cgd_er						        =	Crss_er
Cds_eff 							=	paramProcess.getCmos([Coss[0],Cds],Cds_tr,Cds_er,Coss[0][0],True)
Cgs_eff 							=	paramProcess.getCmos([Ciss[0],Cgs],Cgs_tr,Cgs_er,Ciss[0][0],True)
Cgd_eff 							=	Crss_eff
Rvec,Tvec							=	paramProcess.MOSFETrdson(switchesRdsonPath,'IAUT300N10S5N015','_Rdson')
Nvec,Ivec 							=	paramProcess.MOSFETrdson(switchesIdsonPath,'IAUT300N10S5N015','_Rdson')
Ioff,catOFF,Eoff					=	paramProcess.MOSFETenergies(switchesEoffPath,'IAUT300N10S5N015','_Eoff')
Voff,catOFF_Temp,Eoff_Temp			=	paramProcess.MOSFETenergies(switchesEoffPath,'IAUT300N10S5N015','_Eoff_Temp')
Ion,catON,Eon 						=	paramProcess.MOSFETenergies(switchesEonPath,'IAUT300N10S5N015','_Eon')
Von,catON_Temp,Eon_Temp				=	paramProcess.MOSFETenergies(switchesEonPath,'IAUT300N10S5N015','_Eon_Temp')
Vfvec,Ifvec,Rd,Vt					=	paramProcess.DiodeVI_data(bodyDiodeVIPath,'IAUT300N10S5N015')
Vds_vec,Ids_vec 					=	paramProcess.Forward_Transfer_data(switchesTransferPath,'IAUT300N10S5N015')

IAUT300N10S5N015	=	{																																	#*	IAUT300N10S5N015 parameters
							'Config'						:	1																						,	#!	1->electric integrated | 2->electric separate | 3->thermal integrated | 4->thermal separate
							'Transistor'  			: 	{																									#!	transistors parameters
									'Config'				:	2																						,	#?	1->real model | 2->ideal model | 3->behavioral model
									'Thermal'           	:   ''                                  													,   #? 	selected transistor
									'Custom'            	:   []						               													,   #? 	transistor provided custom variables
									'g_fs'					:	1e6																						,	#?	forward transconductance
									'Rg'					:	1.5																						,	#?	internal gate resistance
									'Lg'					:	3e-9*0																					,	#?	gate pin inductance
									'Rds_on'            	:   Rvec[-1][-1]*1e-3																		,   #? 	transistor ON resistance
									'Rds_off'				:	'inf'																					,	#?	transistor OFF resistance
									'Rvec'					:	(np.array(Rvec)*1e-3).tolist()														,	#?	absolute Rdson vector corresponding to junction temperature
									'Tvec'					:	Tvec 																					,	#?	junction temperature vector for Rdson
									'RTconfig'				:	1																						,	#?	choose which RT vector to be used
									'RdsonScale'			:	1.0																						,	#?	Rdson scaling to account for min, typ and max deviations
									'Nvec'					:	Nvec 																					,	#?	normalized Rdson vector corresponding to current
									'Ivec'					:	Ivec																					,	#?	current vector for normalized Rdson
									'NIconfig'				:	1																						,	#?	choose which NI vector to be used
									'IdsonScale'			:	1.0																						,	#?	Idson resistance scaling to account for min, typ and max deviations
									'Rsrc'					:	208e-6*0																				,	#?	kelvin source pin resistance
									'Lsrc'					:	1.5e-9*0																				,	#?	kelvin source pin inductance
									'Ls'					:	1.5e-9*0																				,	#?	package source inductance
                                    'Ld'					:	1e-9*0																					,	#?	package drain inductance
									'Rs'					:	208e-6*0																				,	#?	package source resistance
									'Rd'					:	20e-6*0																					,	#?	package drain inductance
									'Ksrc'					:	0																						,	#?	kelvin source option, 0->no kelvin | 1->kelvin
									'Vblock'            	:   100                                	 													,   #? 	transistor blocking voltage
									'Id'                	:   300                                 													,   #? 	transistor drain current
									'Tr'                	:   55e-9                                   												,   #? 	transistor rise time
									'Tf'                	:   118e-9                                       											, 	#? 	transistor fall time
									'Avalanche'		:	{																									#!	transistor avalanche parameters
										'Config'			:	2																						,	#?	1->enable | 2->disable
										'Voltage'			:	100																						,	#?	avalanche voltage
										'Resistance'		:	1e-3																						#?	avalanche resistance to break voltage state-dependency
									},
									'Transfer'		:	{																									#!	transistor forward transfer parameters
										'Vds'				:	Vds_vec																					,	#?	drain-source voltage vector
										'Vgs'				:	list(np.arange(0.0,12.0+0.2,0.2))													,	#?	gate-source voltage vector
										'Ids'				:	Ids_vec																					,	#?	drain current vector
										'Factor_ON'			:	1.0																						,	#?	scaling factor for Ids at turn ON
										'Factor_OFF'		:	1.0																						,	#?	scaling factor for Ids at turn OFF
										'Factor_Vgs_ON'		:	1.0																						,	#?	scaling factor for Vgs at turn ON
										'Factor_Vgs_OFF'	:	1.01																					,	#?	scaling factor for Vgs at turn OFF
										'Vcoss'				:	0																						,	#?	initial voltage of the Coss
									},
						},
							'BodyDiode'  			:	{																									#!	body diodes paramteters
									'Config'				:	4																						,	#?	1->non-ideal RR | 2->non-ideal | 3->ideal RR | 4->ideal
									'Thermal'           	:   ''                                  													,   #? 	separate body diode
									'Custom'            	:   []					                 													,   #? 	body diode provided custrom variables
									'Rd_on'             	:   Rd[-1]																					,  	#? 	body diode ON resistance
									'Rd_off'				:	'inf'																					,	#?	body diode OFF resistance
									'Vf'					:	Vt[-1]																					,	#? 	body diode forward voltage
									'If'                	:   300                                 													,   #? 	body diode forward current
									'dIr'               	:   100e6                                   												,   #? 	body diode current slope
									'Lrr'					:	1e-9																					,	#?	body diode reverse recovery inductance
									'Trr'               	:   90e-9                                  													,   #? 	body diode reverse recovery time
									'Irr'               	:   0                                   													,   #? 	body diode reverse recovery current
									'Qrr'               	:   220e-9                                  												, 	#? 	body diode reverse recovery charge
									'Is'                  	:   50              																		, 	#? 	body diode reference current
									'Vs'					:	50																						,	#?	body diode reference voltage
                                    'VIcurve'		:	{																									#!	body diode VI characteristics
                                        'Vfvec'				:	Vfvec																					,	#?	forward voltage vector
                                        'Ifvec'				:	Ifvec																					,	#?	forward current vector
										'Rdvec'				:	Rd																						,	#?	dynamic resistance vector
										'Vtvec'				:	Vt																						,	#?	threshold voltage vector
                                        'Temps'				:	[25,175]																				,	#?	temperature vector
                                        'Vfscale'			:	1.444																						#?	Vf scaling to account for min, typ and max deviations
									},
						},
							'GateDriver'			:	{																									#!	gate driver parameters
									'Config'				:	3																						,	#?	1->high-side | 2->low-side | 3->disable
									'Von'					:	12																						,	#?	ON driving voltage
									'Voff'					:	0																						,	#?	OFF driving voltage
									'Ron'					:	2.5																						,	#?	sourcing output resistance
									'Roff'					:	1.5																						,	#?	sinking output resistance
									'Lon'					:	0																						,	#?	sourcing output inductance
									'Loff'					:	0																						,	#?	sinking output inductance
									'Cload'					:	0																						,	#?	capacitive load on output
									'Rload'					:	'inf'																					,	#?	resistive load on output
									'Delay'					:	50e-9																					,	#?	input-to-output total deadtime
									'Trise'					:	9e-9																					,	#?	output rising time
									'Tfall'					:	7e-9																					,	#?	output falling time
									'UVLO_Start'			:	7.0																						,	#?	UVLO startup voltage threshold
									'UVLO_Stop'				:	6.5																						,	#?	UVLO shutdown voltage threshold
									'UVLO_Delay'			:	100e-9																					,	#?	delay between UVLO startup and shutdown
									'Init_State'			:	0																						,	#?	initial toggling state, 0->OFF | 1->ON
									'CurrentLimit'	:	{																									#*	current limit of driver stage
										'Config'			:	2																						,	#?	1->enable | 2->disable
										'Ts'				: 	0 																						,	#?	sampling time between inductive & capacitive links
										'tau'				: 	0																						,	#?	first-order delay between inductive & capacitive links
                                    	'Rs'				: 	0																						,	#?	source impedance of inductive link
										'Cs'				:	1e-12																					,	#?	source capacitance of capacitive link
                                        'UpLim'				: 	10																						,	#?	max current limit on capacitive link
                                        'LoLim'				: 	-10																						,	#?	min current limit on capacitive link
                                        'Voffset'			: 	0																							#?	voltage offset between inductive & capacitive links
									},
									'Masking'		:	{																									#*	switching stages masking
										'ON'	:	{																										#	ON path masking
											'Config'		:	2																						,	#?	1->enable | 2->disable
											'HIGH'	:	{																									#!	HIGH mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[0, 0]																						#?	mask output
											},
											'LOW'	:	{																									#!	LOW mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[1, 1]																						#?	mask output
											}
										},
										'OFF'	:	{																										#	OFF path masking
											'Config'		:	2																						,	#?	1->enable | 2->disable
											'HIGH'	:	{																									#!	HIGH mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[0, 0]																						#?	mask output
											},
											'LOW'	:	{																									#!	LOW mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[1, 1]																						#?	mask output
											}
										}
									},
									'Boot'			:	{																									#*	bootstrap/charge pump parameters
										'Config'			:	1																						,	#?	1->bootstrap | 2->charge pump
										'Von'				:	14																						,	#?	boostrap driving voltage
										'Cboot'				:	4.7e-6																					,	#?	bootstrap capacitance
										'Vinit'				:	0																						,	#?	bootstrap capacitance initial voltage
										'Rboot'				:	10																						,	#?	bootstrap resistance
										'Vfboot'			:	0.87																					,	#?	bootstrap diode forward voltage
										'Rdboot'			:	1e-3																					,	#?	bootstrap diode ON-state resistance
										'Ichrg'				:	300e-6																					,	#?	charge pump supply current
										'Idis'				:	5e-6																					,	#?	charge pump loading or leakage current
										'Cpar'				:	0																						,	#?	charge pump parallel cap to break state/source dependency
									    'UVLO_Start'		:	11.6																					,	#?	threshold value to start the charge pump
										'UVLO_Stop'			:	12.4																						#?	threshold value to stop the charge pump
									},
							},
							'GateNetwork'			:	{																									#!	gate drive circuit parameters
									'Config'				:	2																						,	#?	1-> enable | 2->disable
									'ON_Path'		:	{																									#*	sourcing path parameters
										'Rg'				:	3.9																						,	#?	gate ON path resistance
										'Lg'				:	0																						,	#?	gate ON path inductance
										'Rload'				:	10e3																					,	#?	gate pull down resistance
										'Diode'	:	{																										#	reverse blocking diode parameters
											'Vf'			:	0																						,	#?	forward voltage
											'Rd_on'			:	0																						,	#?	ON-state resistance
										},
									},
									'OFF_Path'		:	{																									#*	sinking path parameters
										'Rg'				:	1																						,	#?	gate OFF path resistance
										'Lg'				:	0																						,	#?	gate OFF path inductance
										'Diode'	:	{																										#	reverse blocking diode parameters
											'Vf'			:	0.3																						,	#?	forward voltage
											'Rd_on'			:	1e-3																					,	#?	ON-state resistance
										},
									},
									'NegVolt'		:	{																									#*	negative voltage generator parameters
										'Config'			:	2																						,	#?	1-> enable | 2->disable
										'Dz'	:	{																										#	zener diode parameters
											'Vf'			:	0.7																						,	#?	forward voltage
											'Rd_on'			:	1e-3																					,	#?	ON-state resistance
											'Vz'			:	2																						,	#?	Zener breakdown voltage
											'Rz'			:	1e-3																					,	#?	Zener resistance
										},
										'Dp'	:	{																										#	peak detector diode
											'Vf'			:	0.0																						,	#?	forward voltage
											'Rd_on'			:	0.0																						,	#?	ON-state resistance
										},
										'Cz'	:	{																										#	Zener capacitor parameters
											'Config'		:	1																						,	#?	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
											'Csingle'		:	1e-6																					,	#?	single capacitor value
											'Rsingle'		:	5e-3																					,	#?	ESR of single capacitor
											'Lsingle'		:	0																						,	#?	ESL of single capacitor
											'nPar'			:	1																						,	#?	number of parallel connections
											'nSer'			:	1																						,	#?	number of series connections
											'Vinit'			:	0																						,	#?	capacitor initial voltage
										},
										'Cp'	:	{																										#	peak detector capacitor parameters
											'Config'		:	1																						,	#?	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
											'Csingle'		:	2.2e-6																					,	#?	single capacitor value
											'Rsingle'		:	5e-3																					,	#?	ESR of single capacitor
											'Lsingle'		:	0																						,	#?	ESL of single capacitor
											'nPar'			:	1																						,	#?	number of parallel connections
											'nSer'			:	1																						,	#?	number of series connections
											'Vinit'			:	0																						,	#?	capacitor initial voltage
										},
										'Rp1'				:	43																						,	#?	current limiter of peak detector current
										'Rp2'				:	4.7e3																					,	#?	load resistor to charge the zener diode
									},
								},
							'nParallel'   					:	1                                       												,   #? 	number of parallel devices
							'Rth_jc'						:	[2.202e-4,3e-2,7.642e-2,3.729e-5,2.401e-1,5.318e-2]										,	#?	junction-to-case thermal resistance
							'Cth_jc'						:	[4.541e-2,3.333e-3,1.309e-2,2.682e2,4.164e-1,1.880e1]									,	#?	junction-to-case thermal capacitance
							'Rth_ca'              			:   [0.292,0.258,0.856,0.228,0.8]            												,   #? 	case-to-ambient thermal resistance
							'Cth_ca'              			:   [0.788,0.205,15.91,3.716,0.015]             											,   #? 	case-to-ambient thermal capacitance
							'Tinit'							:	0.0																						,	#?	initial juntion temperature
							'Pinit'							:	0.0																						,	#?	initial power dissipation
							'Coss'					: 	{																									#!	device Coss parameters
								'C'							:	Coss_eff					 															,	#?	device parasitic output capacitance
								'R'							:	0																						,	#?	Coss resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Coss inductance to reduce current slope
								'Coss_er'					:	Crss_er																					,	#?	energy-related Coss
								'Coss_tr'					:	Coss_tr																					,	#?	time-related Coss
								'Vvec'						:	Coss[0]																					,	#? 	device Coss voltage vector
								'Cvec'						:	Coss[1]																					,	#?	device Coss capacity vector
								'Offset'					:	0																						,	#?	parasitic offset to Coss
                                'Factor'					:	0.98																					,	#?	parasitic tolerance to Coss
								'Qoss'						:	Qoss																					,	#?	equivalent charge of Coss
								'Eoss'						:	Eoss																					,	#?	equivalent energy of Coss
								'Config'					:	1																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
						},
                        	'Crss'					:	{																									#!	device Crss parameters
                                'C'							:	Crss_eff					 															,	#?	device parasitic reverse transfer capacitance
								'R'							:	0																						,	#?	Crss resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Crss inductance to reduce current slope
								'Crss_er'					:	Crss_er																					,	#?	energy-related Crss
								'Crss_tr'					:	Crss_tr																					,	#?	time-related Crss
								'Vvec'						:	Crss[0]																					,	#?	device Crss voltage vector
                                'Cvec'						:	Crss[1]																					,	#?	device Crss capacity vector
								'Qvec'						:	Qrss																					,	#?	device accumulated Crss charge vector
								'Offset'					:	0																						,	#?	parasitic offset to Crss
								'Factor'					:	1.0																						,	#?	parasitic tolerance to Crss
								'Qrss'						:	Qrss																					,	#?	equivalent charge of Crss
								'Erss'						:	Erss																					,	#?	equivalent energe of Crss
								'Config'					:	5																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
						},
							'Ciss'					:	{																									#!	device Ciss parameters
								'C'							:	Ciss_eff					 															,	#?	device parasitic input capacitance
								'R'							:	0																						,	#?	Ciss resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Ciss inductance to reduce current slope
								'Ciss_er'					:	Ciss_er																					,	#?	energy-related Ciss
								'Ciss_tr'					:	Ciss_tr																					,	#?	time-related Ciss
								'Vvec'						:	Ciss[0]																					,	#?	device Ciss voltage vector
								'Cvec'						:	Ciss[1]																					,	#?	device Ciss capacity vector
								'Offset'					:	0																						,	#?	parasitic offset to Ciss
								'Factor'					:	1.0																						,	#?	parasitic tolerance to Ciss
								'Qiss'						:	Qiss																					,	#?	equivalent charge of Ciss
								'Eiss'						:	Eiss																					,	#?	equivalent energy of Ciss
								'Config'					:	5																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Cds'					:	{																									#!	device Cds parameters
								'C'							:	Cds_eff					 																,	#?	device parasitic Cds capacitance
								'R'							:	0																						,	#?	Cds resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Cds inductance to reduce current slope
								'Cds_er'					:	Cds_er																					,	#?	energy-related Cds
								'Cds_tr'					:	Cds_tr																					,	#?	time-related Cds
								'Vvec'						:	Coss[0]																					,	#?	device Cds voltage vector
								'Cvec'						:	Cds																						,	#?	device Cds capacity vector
								'Offset_ON'					:	0																						,	#?	tuning offset for turn ON
								'Offset_OFF'				:	0																						,	#?	tuning offset for turn OFF
								'Factor_ON'					:	2.0																						,	#?	tuning factor for turn ON
								'Factor_OFF'				:	1.0																						,	#?	tuning factor for turn OFF
								'Config'					:	4																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Cgd'					:	{																									#!	device Cgd parameters
								'C'							:	Cgd_eff							 														,	#?	device parasitic Cgd capacitance
								'R'							:	0																						,	#?	Cgd resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Cgd inductance to reduce current slope
								'Cgd_er'					:	Cgd_er																					,	#?	energy-related Cgd
								'Cgd_tr'					:	Cgd_tr																					,	#?	time-related Cgd
								'Vvec'						:	Crss[0]																					,	#?	device Cgd voltage vector
								'Cvec'						:	Cgd																						,	#?	device Cgd capacity vector
								'Offset_ON'					:	380e-12																					,	#?	tuning offset for turn ON
								'Offset_OFF'				:	700e-12																					,	#?	tuning offset for turn OFF
								'Factor_ON'					:	1.05																					,	#?	tuning factor for turn ON
								'Factor_OFF'				:	1.0																						,	#?	tuning factor for turn OFF
								'Config'					:	4																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Cgs'					:	{																									#!	device Cgs parameters
								'C'							:	Cgs_eff					 																,	#?	device parasitic Cgs capacitance
								'R'							:	0																						,	#?	Cgs resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Cgs inductance to reduce current slope
								'Cgs_er'					:	Cgs_er																					,	#?	energy-related Cgs
								'Cgs_tr'					:	Cgs_tr																					,	#?	time-related Cgs
								'Vvec'						:	Ciss[0]																					,	#?	device Cgs voltage vector
								'Cvec'						:	Cgs																						,	#?	device Cgs capacity vector
								'Offset_ON'					:	350e-12																					,	#?	tuning offset for turn ON
								'Offset_OFF'				:	0																						,	#?	tuning offset for turn OFF
								'Factor_ON'					:	0.97																					,	#?	tuning factor for turn ON
								'Factor_OFF'				:	0.95																					,	#?	tuning factor for turn OFF
								'Config'					:	4																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Eoff'					:	{																									#!	transistor turn-OFF energy losses
									'Ivec'					:	Ioff																					,	#?	turn-OFF energy current vector
                                    'Rgvec'					:	[0,100]																					,	#?	OFF path gate resistances vector
									'Tjvec'					:	[-55,175]																				,	#?	junction temperature vector
                                    'Vvec'					:	Voff																					,	#?	turn-OFF voltage vector
                                    'Evec'					:	Eoff																					,	#?	turn-OFF energy vectors
									'Evec_Temp'				:	Eoff_Temp																				,	#?	turn-OFF energy temp scaling vectors
                                    'CAT'					:	catOFF																					,	#?	octave Eoff energy syntax
									'CAT_Temp'				:	catOFF_Temp																				,	#?	octave Eoff energy temp scaling syntax
									'Vgs'					:	0																						,	#?	used OFF path gate-source voltage
									'Vth'					:	1.5																						,	#?	used OFF path threshold voltage
									'Rg'					:	1																							#?	used OFF path gate resistance
						},
							'Eon'					:	{																									#!	transistor turn-ON energy losses
									'Ivec'					:	Ion																						,	#?	turn-ON energy current vector
									'Rgvec'					:	[0,100]																					,	#?	ON path gate resistances vector
									'Tjvec'					:	[-55,175]																				,	#?	junction temperature vector
                                    'Vvec'					:	Von																						,	#?	turn-ON voltage vector
                                    'Evec'					:	Eon																						,	#?	turn-ON energy vectors
									'Evec_Temp'				:	Eon_Temp																				,	#?	turn-ON energy temp scaling vectors
                                    'CAT'					:	catON																					,	#?	octave Eon energy syntax
									'CAT_Temp'				:	catON_Temp																				,	#?	octave Eon energy temp scaling syntax
									'Vgs'					:	12																						,	#?	used ON path gate-source voltage
									'Vth'					:	1.5																						,	#?	used ON path threshold voltage
									'Rg'					:	0																							#?	used ON path gate resistance
						},
							'Tau_deg'						:	100e-9																					,	#?	deglitch filter for currents and voltages
							'RCsnubber'						:	2																						,	#?	1->enable | 2->disable
						}

#?----------------------------------------------------------------------------------------------------------------------------------------------------------------------

Coss,Qoss,Eoss,Coss_tr,Coss_er		=	paramProcess.MOSFETcaps(switchesCossPath,'NVBYST001N08X','_Coss')
Crss,Qrss,Erss,Crss_tr,Crss_er 		=	paramProcess.MOSFETcaps(switchesCrssPath,'NVBYST001N08X','_Crss')
Ciss,Qiss,Eiss,Ciss_tr,Ciss_er 		=	paramProcess.MOSFETcaps(switchesCissPath,'NVBYST001N08X','_Ciss')
Coss_eff 							=	paramProcess.getCmos(Coss,Coss_tr,Coss_er,Coss[0][0],True)
Ciss_eff 							=	paramProcess.getCmos(Ciss,Ciss_tr,Ciss_er,Ciss[0][0],True)
Crss_eff 							=	paramProcess.getCmos(Crss,Crss_tr,Crss_er,Crss[0][0],True)
Cds 						        =	(np.array(Coss[1]) - np.array(Crss[1])).tolist()
Cgs						        	=	(np.array(Ciss[1]) - np.array(Crss[1])).tolist()
Cgd						        	=	Crss[1]
Cds_tr						        =	(np.array(Coss_tr) - np.array(Crss_tr)).tolist()
Cgs_tr						        =	(np.array(Ciss_tr) - np.array(Crss_tr)).tolist()
Cgd_tr						        =	Crss_tr
Cds_er						        =	(np.array(Coss_er) - np.array(Crss_er)).tolist()
Cgs_er						        =	(np.array(Ciss_er) - np.array(Crss_er)).tolist()
Cgd_er						        =	Crss_er
Cds_eff 							=	paramProcess.getCmos([Coss[0],Cds],Cds_tr,Cds_er,Coss[0][0],True)
Cgs_eff 							=	paramProcess.getCmos([Ciss[0],Cgs],Cgs_tr,Cgs_er,Ciss[0][0],True)
Cgd_eff 							=	Crss_eff
Rvec,Tvec							=	paramProcess.MOSFETrdson(switchesRdsonPath,'NVBYST001N08X','_Rdson')
Nvec,Ivec 							=	paramProcess.MOSFETrdson(switchesIdsonPath,'NVBYST001N08X','_Rdson')
Ioff,catOFF,Eoff					=	paramProcess.MOSFETenergies(switchesEoffPath,'NVBYST001N08X','_Eoff')
Voff,catOFF_Temp,Eoff_Temp			=	paramProcess.MOSFETenergies(switchesEoffPath,'NVBYST001N08X','_Eoff_Temp')
Ion,catON,Eon 						=	paramProcess.MOSFETenergies(switchesEonPath,'NVBYST001N08X','_Eon')
Von,catON_Temp,Eon_Temp				=	paramProcess.MOSFETenergies(switchesEonPath,'NVBYST001N08X','_Eon_Temp')
Vfvec,Ifvec,Rd,Vt					=	paramProcess.DiodeVI_data(bodyDiodeVIPath,'NVBYST001N08X')

NVBYST001N08X		=	{																																	#*	NVBYST001N08X parameters
							'Config'						:	1																						,	#!	1->electric integrated | 2->electric separate | 3->thermal integrated | 4->thermal separate
							'Transistor'  			: 	{																									#!	transistors parameters
									'Config'				:	2																						,	#?	1->real model | 2->ideal model | 3->behavioral model
									'Thermal'           	:   ''                                  													,   #? 	selected transistor
									'Custom'            	:   []						               													,   #? 	transistor provided custom variables
									'g_fs'					:	1e6																						,	#?	forward transconductance
									'Rg'					:	0.35																					,	#?	internal gate resistance
									'Lg'					:	0																						,	#?	gate pin inductance
									'Rds_on'            	:   Rvec[-1][-1]*1e-3																		,   #? 	transistor ON resistance
									'Rds_off'				:	'inf'																					,	#?	transistor OFF resistance
									'Rvec'					:	(np.array(Rvec)*1e-3).tolist()														,	#?	absolute Rdson vector corresponding to junction temperature
									'Tvec'					:	Tvec 																					,	#?	junction temperature vector for Rdson
									'RTconfig'				:	1																						,	#?	choose which RT vector to be used
									'RdsonScale'			:	1.2143																					,	#?	Rdson scaling to account for min, typ and max deviations
									'Nvec'					:	Nvec 																					,	#?	normalized Rdson vector corresponding to current
									'Ivec'					:	Ivec																					,	#?	current vector for normalized Rdson
									'NIconfig'				:	1																						,	#?	choose which NI vector to be used
									'IdsonScale'			:	1.0																						,	#?	Idson resistance scaling to account for min, typ and max deviations
									'Rsrc'					:	0																						,	#?	kelvin source pin resistance
									'Lsrc'					:	0																						,	#?	kelvin source pin inductance
									'Ls'					:	0																						,	#?	package source inductance
                                    'Ld'					:	0																						,	#?	package drain inductance
									'Rs'					:	0																						,	#?	package source resistance
									'Rd'					:	0																						,	#?	package drain inductance
									'Ksrc'					:	0																						,	#?	kelvin source option, 0->no kelvin | 1->kelvin
									'Vblock'            	:   80                                	 													,   #? 	transistor blocking voltage
									'Id'                	:   467                                 													,   #? 	transistor drain current
									'Tr'                	:   63e-9                                   												,   #? 	transistor rise time
									'Tf'                	:   79e-9                                       											, 	#? 	transistor fall time
									'Avalanche'		:	{																									#!	transistor avalanche parameters
										'Config'			:	2																						,	#?	1->enable | 2->disable
										'Voltage'			:	80																						,	#?	avalanche voltage
										'Resistance'		:	1e-3																						#?	avalanche resistance to break voltage state-dependency
									},
									'Transfer'		:	{																									#!	transistor forward transfer parameters
										'Vds'				:	Vds_vec																					,	#?	drain-source voltage vector
										'Vgs'				:	list(np.arange(0.0,12.0+0.2,0.2))													,	#?	gate-source voltage vector
										'Ids'				:	Ids_vec																					,	#?	drain current vector
										'Factor_ON'			:	1.0																						,	#?	scaling factor for Ids at turn ON
										'Factor_OFF'		:	1.0																						,	#?	scaling factor for Ids at turn OFF
										'Factor_Vgs_ON'		:	1.0																						,	#?	scaling factor for Vgs at turn ON
										'Factor_Vgs_OFF'	:	1.0																						,	#?	scaling factor for Vgs at turn OFF
										'Vcoss'				:	0																						,	#?	initial voltage of the Coss
									},
						},
							'BodyDiode'  			:	{																									#!	body diodes paramteters
									'Config'				:	4																						,	#?	1->non-ideal RR | 2->non-ideal | 3->ideal RR | 4->ideal
									'Thermal'           	:   ''                                  													,   #? 	separate body diode
									'Custom'            	:   []					                 													,   #? 	body diode provided custrom variables
									'Rd_on'             	:   Rd[-1]																					,  	#? 	body diode ON resistance
									'Rd_off'				:	'inf'																					,	#?	body diode OFF resistance
									'Vf'					:	Vt[-1]																					,	#? 	body diode forward voltage
									'If'                	:   467                                 													,   #? 	body diode forward current
									'dIr'               	:   1e9		                                   												,   #? 	body diode current slope
									'Lrr'					:	1e-9																					,	#?	body diode reverse recovery inductance
									'Trr'               	:   48e-9                                  													,   #? 	body diode reverse recovery time
									'Irr'               	:   0                                   													,   #? 	body diode reverse recovery current
									'Qrr'               	:   506e-9                                  												, 	#? 	body diode reverse recovery charge
									'Is'                  	:   80              																		, 	#? 	body diode reference current
									'Vs'					:	64																						,	#?	body diode reference voltage
                                    'VIcurve'		:	{																									#!	body diode VI characteristics
                                        'Vfvec'				:	Vfvec																					,	#?	forward voltage vector
                                        'Ifvec'				:	Ifvec																					,	#?	forward current vector
										'Rdvec'				:	Rd																						,	#?	dynamic resistance vector
										'Vtvec'				:	Vt																						,	#?	threshold voltage vector
                                        'Temps'				:	[-55,25,175]																			,	#?	temperature vector
                                        'Vfscale'			:	1.481																						#?	Vf scaling to account for min, typ and max deviations
									},
						},
							'GateDriver'			:	{																									#!	gate driver parameters
									'Config'				:	3																						,	#?	1->high-side | 2->low-side | 3->disable
									'Von'					:	12																						,	#?	ON driving voltage
									'Voff'					:	0																						,	#?	OFF driving voltage
									'Ron'					:	2.5																						,	#?	sourcing output resistance
									'Roff'					:	1.5																						,	#?	sinking output resistance
									'Lon'					:	0																						,	#?	sourcing output inductance
									'Loff'					:	0																						,	#?	sinking output inductance
									'Cload'					:	0																						,	#?	capacitive load on output
									'Rload'					:	'inf'																					,	#?	resistive load on output
									'Delay'					:	50e-9																					,	#?	input-to-output total deadtime
									'Trise'					:	9e-9																					,	#?	output rising time
									'Tfall'					:	7e-9																					,	#?	output falling time
									'UVLO_Start'			:	7.0																						,	#?	UVLO startup voltage threshold
									'UVLO_Stop'				:	6.5																						,	#?	UVLO shutdown voltage threshold
									'UVLO_Delay'			:	100e-9																					,	#?	delay between UVLO startup and shutdown
									'Init_State'			:	0																						,	#?	initial toggling state, 0->OFF | 1->ON
									'CurrentLimit'	:	{																									#*	current limit of driver stage
										'Config'			:	2																						,	#?	1->enable | 2->disable
										'Ts'				: 	0 																						,	#?	sampling time between inductive & capacitive links
										'tau'				: 	0																						,	#?	first-order delay between inductive & capacitive links
                                    	'Rs'				: 	0																						,	#?	source impedance of inductive link
										'Cs'				:	1e-12																					,	#?	source capacitance of capacitive link
                                        'UpLim'				: 	10																						,	#?	max current limit on capacitive link
                                        'LoLim'				: 	-10																						,	#?	min current limit on capacitive link
                                        'Voffset'			: 	0																							#?	voltage offset between inductive & capacitive links
									},
									'Masking'		:	{																									#*	switching stages masking
										'ON'	:	{																										#	ON path masking
											'Config'		:	2																						,	#?	1->enable | 2->disable
											'HIGH'	:	{																									#!	HIGH mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[0, 0]																						#?	mask output
											},
											'LOW'	:	{																									#!	LOW mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[1, 1]																						#?	mask output
											}
										},
										'OFF'	:	{																										#	OFF path masking
											'Config'		:	2																						,	#?	1->enable | 2->disable
											'HIGH'	:	{																									#!	HIGH mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[0, 0]																						#?	mask output
											},
											'LOW'	:	{																									#!	LOW mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[1, 1]																						#?	mask output
											}
										}
									},
									'Boot'			:	{																									#*	bootstrap/charge pump parameters
										'Config'			:	1																						,	#?	1->bootstrap | 2->charge pump
										'Von'				:	14																						,	#?	boostrap driving voltage
										'Cboot'				:	4.7e-6																					,	#?	bootstrap capacitance
										'Vinit'				:	0																						,	#?	bootstrap capacitance initial voltage
										'Rboot'				:	10																						,	#?	bootstrap resistance
										'Vfboot'			:	0.87																					,	#?	bootstrap diode forward voltage
										'Rdboot'			:	1e-3																					,	#?	bootstrap diode ON-state resistance
										'Ichrg'				:	300e-6																					,	#?	charge pump supply current
										'Idis'				:	5e-6																					,	#?	charge pump loading or leakage current
										'Cpar'				:	0																						,	#?	charge pump parallel cap to break state/source dependency
									    'UVLO_Start'		:	11.6																					,	#?	threshold value to start the charge pump
										'UVLO_Stop'			:	12.4																						#?	threshold value to stop the charge pump
									},
							},
							'GateNetwork'			:	{																									#!	gate drive circuit parameters
									'Config'				:	2																						,	#?	1-> enable | 2->disable
									'ON_Path'		:	{																									#*	sourcing path parameters
										'Rg'				:	3.9																						,	#?	gate ON path resistance
										'Lg'				:	0																						,	#?	gate ON path inductance
										'Rload'				:	10e3																					,	#?	gate pull down resistance
										'Diode'	:	{																										#	reverse blocking diode parameters
											'Vf'			:	0																						,	#?	forward voltage
											'Rd_on'			:	0																						,	#?	ON-state resistance
										},
									},
									'OFF_Path'		:	{																									#*	sinking path parameters
										'Rg'				:	1																						,	#?	gate OFF path resistance
										'Lg'				:	0																						,	#?	gate OFF path inductance
										'Diode'	:	{																										#	reverse blocking diode parameters
											'Vf'			:	0.3																						,	#?	forward voltage
											'Rd_on'			:	1e-3																					,	#?	ON-state resistance
										},
									},
									'NegVolt'		:	{																									#*	negative voltage generator parameters
										'Config'			:	2																						,	#?	1-> enable | 2->disable
										'Dz'	:	{																										#	zener diode parameters
											'Vf'			:	0.7																						,	#?	forward voltage
											'Rd_on'			:	1e-3																					,	#?	ON-state resistance
											'Vz'			:	2																						,	#?	Zener breakdown voltage
											'Rz'			:	1e-3																					,	#?	Zener resistance
										},
										'Dp'	:	{																										#	peak detector diode
											'Vf'			:	0.0																						,	#?	forward voltage
											'Rd_on'			:	0.0																						,	#?	ON-state resistance
										},
										'Cz'	:	{																										#	Zener capacitor parameters
											'Config'		:	1																						,	#?	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
											'Csingle'		:	1e-6																					,	#?	single capacitor value
											'Rsingle'		:	5e-3																					,	#?	ESR of single capacitor
											'Lsingle'		:	0																						,	#?	ESL of single capacitor
											'nPar'			:	1																						,	#?	number of parallel connections
											'nSer'			:	1																						,	#?	number of series connections
											'Vinit'			:	0																						,	#?	capacitor initial voltage
										},
										'Cp'	:	{																										#	peak detector capacitor parameters
											'Config'		:	1																						,	#?	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
											'Csingle'		:	2.2e-6																					,	#?	single capacitor value
											'Rsingle'		:	5e-3																					,	#?	ESR of single capacitor
											'Lsingle'		:	0																						,	#?	ESL of single capacitor
											'nPar'			:	1																						,	#?	number of parallel connections
											'nSer'			:	1																						,	#?	number of series connections
											'Vinit'			:	0																						,	#?	capacitor initial voltage
										},
										'Rp1'				:	43																						,	#?	current limiter of peak detector current
										'Rp2'				:	4.7e3																					,	#?	load resistor to charge the zener diode
									},
								},
							'nParallel'   					:	1                                       												,   #? 	number of parallel devices
							'Rth_jc'						:	[0.29]																					,	#?	junction-to-case thermal resistance
							'Cth_jc'						:	[0]																						,	#?	junction-to-case thermal capacitance
							'Rth_ca'              			:   [3.5]					            													,   #? 	case-to-ambient thermal resistance
							'Cth_ca'              			:   [0]							             												,   #? 	case-to-ambient thermal capacitance
							'Tinit'							:	0.0																						,	#?	initial juntion temperature
							'Pinit'							:	0.0																						,	#?	initial power dissipation
							'Coss'					: 	{																									#!	device Coss parameters
								'C'							:	Coss_eff					 															,	#?	device parasitic output capacitance
								'R'							:	0																						,	#?	Coss resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Coss inductance to reduce current slope
								'Coss_er'					:	Crss_er																					,	#?	energy-related Coss
								'Coss_tr'					:	Coss_tr																					,	#?	time-related Coss
								'Vvec'						:	Coss[0]																					,	#? 	device Coss voltage vector
								'Cvec'						:	Coss[1]																					,	#?	device Coss capacity vector
								'Offset'					:	0																						,	#?	parasitic offset to Coss
                                'Factor'					:	1.0																						,	#?	parasitic tolerance to Coss
								'Qoss'						:	Qoss																					,	#?	equivalent charge of Coss
								'Eoss'						:	Eoss																					,	#?	equivalent energy of Coss
								'Config'					:	1																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
						},
                        	'Crss'					:	{																									#!	device Crss parameters
                                'C'							:	Crss_eff					 															,	#?	device parasitic reverse transfer capacitance
								'R'							:	0																						,	#?	Crss resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Crss inductance to reduce current slope
								'Crss_er'					:	Crss_er																					,	#?	energy-related Crss
								'Crss_tr'					:	Crss_tr																					,	#?	time-related Crss
								'Vvec'						:	Crss[0]																					,	#?	device Crss voltage vector
                                'Cvec'						:	Crss[1]																					,	#?	device Crss capacity vector
								'Qvec'						:	Qrss																					,	#?	device accumulated Crss charge vector
								'Offset'					:	0																						,	#?	parasitic offset to Crss
								'Factor'					:	1.0																						,	#?	parasitic tolerance to Crss
								'Qrss'						:	Qrss																					,	#?	equivalent charge of Crss
								'Erss'						:	Erss																					,	#?	equivalent energe of Crss
								'Config'					:	5																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
						},
							'Ciss'					:	{																									#!	device Ciss parameters
								'C'							:	Ciss_eff					 															,	#?	device parasitic input capacitance
								'R'							:	0																						,	#?	Ciss resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Ciss inductance to reduce current slope
								'Ciss_er'					:	Ciss_er																					,	#?	energy-related Ciss
								'Ciss_tr'					:	Ciss_tr																					,	#?	time-related Ciss
								'Vvec'						:	Ciss[0]																					,	#?	device Ciss voltage vector
								'Cvec'						:	Ciss[1]																					,	#?	device Ciss capacity vector
								'Offset'					:	0																						,	#?	parasitic offset to Ciss
								'Factor'					:	1.0																						,	#?	parasitic tolerance to Ciss
								'Qiss'						:	Qiss																					,	#?	equivalent charge of Ciss
								'Eiss'						:	Eiss																					,	#?	equivalent energy of Ciss
								'Config'					:	5																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Cds'					:	{																									#!	device Cds parameters
								'C'							:	Cds_eff					 																,	#?	device parasitic Cds capacitance
								'R'							:	0																						,	#?	Cds resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Cds inductance to reduce current slope
								'Cds_er'					:	Cds_er																					,	#?	energy-related Cds
								'Cds_tr'					:	Cds_tr																					,	#?	time-related Cds
								'Vvec'						:	Coss[0]																					,	#?	device Cds voltage vector
								'Cvec'						:	Cds																						,	#?	device Cds capacity vector
								'Offset_ON'					:	0																						,	#?	tuning offset for turn ON
								'Offset_OFF'				:	0																						,	#?	tuning offset for turn OFF
								'Factor_ON'					:	2.0																						,	#?	tuning factor for turn ON
								'Factor_OFF'				:	1.0																						,	#?	tuning factor for turn OFF
								'Config'					:	4																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Cgd'					:	{																									#!	device Cgd parameters
								'C'							:	Cgd_eff							 														,	#?	device parasitic Cgd capacitance
								'R'							:	0																						,	#?	Cgd resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Cgd inductance to reduce current slope
								'Cgd_er'					:	Cgd_er																					,	#?	energy-related Cgd
								'Cgd_tr'					:	Cgd_tr																					,	#?	time-related Cgd
								'Vvec'						:	Crss[0]																					,	#?	device Cgd voltage vector
								'Cvec'						:	Cgd																						,	#?	device Cgd capacity vector
								'Offset_ON'					:	0																						,	#?	tuning offset for turn ON
								'Offset_OFF'				:	0																						,	#?	tuning offset for turn OFF
								'Factor_ON'					:	1.0																						,	#?	tuning factor for turn ON
								'Factor_OFF'				:	1.0																						,	#?	tuning factor for turn OFF
								'Config'					:	4																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Cgs'					:	{																									#!	device Cgs parameters
								'C'							:	Cgs_eff					 																,	#?	device parasitic Cgs capacitance
								'R'							:	0																						,	#?	Cgs resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Cgs inductance to reduce current slope
								'Cgs_er'					:	Cgs_er																					,	#?	energy-related Cgs
								'Cgs_tr'					:	Cgs_tr																					,	#?	time-related Cgs
								'Vvec'						:	Ciss[0]																					,	#?	device Cgs voltage vector
								'Cvec'						:	Cgs																						,	#?	device Cgs capacity vector
								'Offset_ON'					:	0																						,	#?	tuning offset for turn ON
								'Offset_OFF'				:	0																						,	#?	tuning offset for turn OFF
								'Factor_ON'					:	1.0																						,	#?	tuning factor for turn ON
								'Factor_OFF'				:	1.0																						,	#?	tuning factor for turn OFF
								'Config'					:	4																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Eoff'					:	{																									#!	transistor turn-OFF energy losses
									'Ivec'					:	Ioff																					,	#?	turn-OFF energy current vector
                                    'Rgvec'					:	[0,100]																					,	#?	OFF path gate resistances vector
									'Tjvec'					:	[-55,175]																				,	#?	junction temperature vector
                                    'Vvec'					:	Voff																					,	#?	turn-OFF voltage vector
                                    'Evec'					:	Eoff																					,	#?	turn-OFF energy vectors
									'Evec_Temp'				:	Eoff_Temp																				,	#?	turn-OFF energy temp scaling vectors
                                    'CAT'					:	catOFF																					,	#?	octave Eoff energy syntax
									'CAT_Temp'				:	catOFF_Temp																				,	#?	octave Eoff energy temp scaling syntax
									'Vgs'					:	0																						,	#?	used OFF path gate-source voltage
									'Vth'					:	1.5																						,	#?	used OFF path threshold voltage
									'Rg'					:	1																							#?	used OFF path gate resistance
						},
							'Eon'					:	{																									#!	transistor turn-ON energy losses
									'Ivec'					:	Ion																						,	#?	turn-ON energy current vector
									'Rgvec'					:	[0,100]																					,	#?	ON path gate resistances vector
									'Tjvec'					:	[-55,175]																				,	#?	junction temperature vector
                                    'Vvec'					:	Von																						,	#?	turn-ON voltage vector
                                    'Evec'					:	Eon																						,	#?	turn-ON energy vectors
									'Evec_Temp'				:	Eon_Temp																				,	#?	turn-ON energy temp scaling vectors
                                    'CAT'					:	catON																					,	#?	octave Eon energy syntax
									'CAT_Temp'				:	catON_Temp																				,	#?	octave Eon energy temp scaling syntax
									'Vgs'					:	12																						,	#?	used ON path gate-source voltage
									'Vth'					:	1.5																						,	#?	used ON path threshold voltage
									'Rg'					:	0																							#?	used ON path gate resistance
						},
							'Tau_deg'						:	100e-9																					,	#?	deglitch filter for currents and voltages
							'RCsnubber'						:	2																						,	#?	1->enable | 2->disable
						}

#?----------------------------------------------------------------------------------------------------------------------------------------------------------------------

Coss,Qoss,Eoss,Coss_tr,Coss_er		=	paramProcess.MOSFETcaps(switchesCossPath,'NVBYST0D8N08X','_Coss')
Crss,Qrss,Erss,Crss_tr,Crss_er 		=	paramProcess.MOSFETcaps(switchesCrssPath,'NVBYST0D8N08X','_Crss')
Ciss,Qiss,Eiss,Ciss_tr,Ciss_er 		=	paramProcess.MOSFETcaps(switchesCissPath,'NVBYST0D8N08X','_Ciss')
Coss_eff 							=	paramProcess.getCmos(Coss,Coss_tr,Coss_er,Coss[0][0],True)
Ciss_eff 							=	paramProcess.getCmos(Ciss,Ciss_tr,Ciss_er,Ciss[0][0],True)
Crss_eff 							=	paramProcess.getCmos(Crss,Crss_tr,Crss_er,Crss[0][0],True)
Cds 						        =	(np.array(Coss[1]) - np.array(Crss[1])).tolist()
Cgs						        	=	(np.array(Ciss[1]) - np.array(Crss[1])).tolist()
Cgd						        	=	Crss[1]
Cds_tr						        =	(np.array(Coss_tr) - np.array(Crss_tr)).tolist()
Cgs_tr						        =	(np.array(Ciss_tr) - np.array(Crss_tr)).tolist()
Cgd_tr						        =	Crss_tr
Cds_er						        =	(np.array(Coss_er) - np.array(Crss_er)).tolist()
Cgs_er						        =	(np.array(Ciss_er) - np.array(Crss_er)).tolist()
Cgd_er						        =	Crss_er
Cds_eff 							=	paramProcess.getCmos([Coss[0],Cds],Cds_tr,Cds_er,Coss[0][0],True)
Cgs_eff 							=	paramProcess.getCmos([Ciss[0],Cgs],Cgs_tr,Cgs_er,Ciss[0][0],True)
Cgd_eff 							=	Crss_eff
Rvec,Tvec							=	paramProcess.MOSFETrdson(switchesRdsonPath,'NVBYST0D8N08X','_Rdson')
Nvec,Ivec 							=	paramProcess.MOSFETrdson(switchesIdsonPath,'NVBYST0D8N08X','_Rdson')
Ioff,catOFF,Eoff					=	paramProcess.MOSFETenergies(switchesEoffPath,'NVBYST0D8N08X','_Eoff')
Voff,catOFF_Temp,Eoff_Temp			=	paramProcess.MOSFETenergies(switchesEoffPath,'NVBYST0D8N08X','_Eoff_Temp')
Ion,catON,Eon 						=	paramProcess.MOSFETenergies(switchesEonPath,'NVBYST0D8N08X','_Eon')
Von,catON_Temp,Eon_Temp				=	paramProcess.MOSFETenergies(switchesEonPath,'NVBYST0D8N08X','_Eon_Temp')
Vfvec,Ifvec,Rd,Vt					=	paramProcess.DiodeVI_data(bodyDiodeVIPath,'NVBYST0D8N08X')

NVBYST0D8N08X		=	{																																	#*	NVBYST0D8N08X parameters
							'Config'						:	1																						,	#!	1->electric integrated | 2->electric separate | 3->thermal integrated | 4->thermal separate
							'Transistor'  			: 	{																									#!	transistors parameters
									'Config'				:	2																						,	#?	1->real model | 2->ideal model | 3->behavioral model
									'Thermal'           	:   ''                                  													,   #? 	selected transistor
									'Custom'            	:   []						               													,   #? 	transistor provided custom variables
									'g_fs'					:	324																						,	#?	forward transconductance
									'Rg'					:	0.40																					,	#?	internal gate resistance
									'Lg'					:	0																						,	#?	gate pin inductance
									'Rds_on'            	:   Rvec[-1][-1]*1e-3																		,   #? 	transistor ON resistance
									'Rds_off'				:	'inf'																					,	#?	transistor OFF resistance
									'Rvec'					:	(np.array(Rvec)*1e-3).tolist()														,	#?	absolute Rdson vector corresponding to junction temperature
									'Tvec'					:	Tvec 																					,	#?	junction temperature vector for Rdson
									'RTconfig'				:	1																						,	#?	choose which RT vector to be used
									'RdsonScale'			:	1.194																					,	#?	Rdson scaling to account for min, typ and max deviations
									'Nvec'					:	Nvec 																					,	#?	normalized Rdson vector corresponding to current
									'Ivec'					:	Ivec																					,	#?	current vector for normalized Rdson
									'NIconfig'				:	1																						,	#?	choose which NI vector to be used
									'IdsonScale'			:	1.0																						,	#?	Idson resistance scaling to account for min, typ and max deviations
									'Rsrc'					:	0																						,	#?	kelvin source pin resistance
									'Lsrc'					:	0																						,	#?	kelvin source pin inductance
									'Ls'					:	0																						,	#?	package source inductance
                                    'Ld'					:	0																						,	#?	package drain inductance
									'Rs'					:	0																						,	#?	package source resistance
									'Rd'					:	0																						,	#?	package drain inductance
									'Ksrc'					:	0																						,	#?	kelvin source option, 0->no kelvin | 1->kelvin
									'Vblock'            	:   80                                	 													,   #? 	transistor blocking voltage
									'Id'                	:   685                                 													,   #? 	transistor drain current
									'Tr'                	:   73e-9                                   												,   #? 	transistor rise time
									'Tf'                	:   99e-9                                       											, 	#? 	transistor fall time
									'Avalanche'		:	{																									#!	transistor avalanche parameters
										'Config'			:	2																						,	#?	1->enable | 2->disable
										'Voltage'			:	80																						,	#?	avalanche voltage
										'Resistance'		:	1e-3																						#?	avalanche resistance to break voltage state-dependency
									},
									'Transfer'		:	{																									#!	transistor forward transfer parameters
										'Vds'				:	Vds_vec																					,	#?	drain-source voltage vector
										'Vgs'				:	list(np.arange(0.0,12.0+0.2,0.2))													,	#?	gate-source voltage vector
										'Ids'				:	Ids_vec																					,	#?	drain current vector
										'Factor_ON'			:	1.0																						,	#?	scaling factor for Ids at turn ON
										'Factor_OFF'		:	1.0																						,	#?	scaling factor for Ids at turn OFF
										'Factor_Vgs_ON'		:	1.0																						,	#?	scaling factor for Vgs at turn ON
										'Factor_Vgs_OFF'	:	1.0																						,	#?	scaling factor for Vgs at turn OFF
										'Vcoss'				:	0																						,	#?	initial voltage of the Coss
									},
						},
							'BodyDiode'  			:	{																									#!	body diodes paramteters
									'Config'				:	4																						,	#?	1->non-ideal RR | 2->non-ideal | 3->ideal RR | 4->ideal
									'Thermal'           	:   ''                                  													,   #? 	separate body diode
									'Custom'            	:   []					                 													,   #? 	body diode provided custrom variables
									'Rd_on'             	:   Rd[-1]																					,  	#? 	body diode ON resistance
									'Rd_off'				:	'inf'																					,	#?	body diode OFF resistance
									'Vf'					:	Vt[-1]																					,	#? 	body diode forward voltage
									'If'                	:   685                                 													,   #? 	body diode forward current
									'dIr'               	:   1000e6                                   												,   #? 	body diode current slope
									'Lrr'					:	1e-9																					,	#?	body diode reverse recovery inductance
									'Trr'               	:   55e-9                                  													,   #? 	body diode reverse recovery time
									'Irr'               	:   0                                   													,   #? 	body diode reverse recovery current
									'Qrr'               	:   609e-9                                  												, 	#? 	body diode reverse recovery charge
									'Is'                  	:   80              																		, 	#? 	body diode reference current
									'Vs'					:	64																						,	#?	body diode reference voltage
                                    'VIcurve'		:	{																									#!	body diode VI characteristics
                                        'Vfvec'				:	Vfvec																					,	#?	forward voltage vector
                                        'Ifvec'				:	Ifvec																					,	#?	forward current vector
										'Rdvec'				:	Rd																						,	#?	dynamic resistance vector
										'Vtvec'				:	Vt																						,	#?	threshold voltage vector
                                        'Temps'				:	[-55,25,175]																			,	#?	temperature vector
                                        'Vfscale'			:	1.519																						#?	Vf scaling to account for min, typ and max deviations
									},
						},
							'GateDriver'			:	{																									#!	gate driver parameters
									'Config'				:	3																						,	#?	1->high-side | 2->low-side | 3->disable
									'Von'					:	12																						,	#?	ON driving voltage
									'Voff'					:	0																						,	#?	OFF driving voltage
									'Ron'					:	2.5																						,	#?	sourcing output resistance
									'Roff'					:	1.5																						,	#?	sinking output resistance
									'Lon'					:	0																						,	#?	sourcing output inductance
									'Loff'					:	0																						,	#?	sinking output inductance
									'Cload'					:	0																						,	#?	capacitive load on output
									'Rload'					:	'inf'																					,	#?	resistive load on output
									'Delay'					:	50e-9																					,	#?	input-to-output total deadtime
									'Trise'					:	9e-9																					,	#?	output rising time
									'Tfall'					:	7e-9																					,	#?	output falling time
									'UVLO_Start'			:	7.0																						,	#?	UVLO startup voltage threshold
									'UVLO_Stop'				:	6.5																						,	#?	UVLO shutdown voltage threshold
									'UVLO_Delay'			:	100e-9																					,	#?	delay between UVLO startup and shutdown
									'Init_State'			:	0																						,	#?	initial toggling state, 0->OFF | 1->ON
									'CurrentLimit'	:	{																									#*	current limit of driver stage
										'Config'			:	2																						,	#?	1->enable | 2->disable
										'Ts'				: 	0 																						,	#?	sampling time between inductive & capacitive links
										'tau'				: 	0																						,	#?	first-order delay between inductive & capacitive links
                                    	'Rs'				: 	0																						,	#?	source impedance of inductive link
										'Cs'				:	1e-12																					,	#?	source capacitance of capacitive link
                                        'UpLim'				: 	10																						,	#?	max current limit on capacitive link
                                        'LoLim'				: 	-10																						,	#?	min current limit on capacitive link
                                        'Voffset'			: 	0																							#?	voltage offset between inductive & capacitive links
									},
									'Masking'		:	{																									#*	switching stages masking
										'ON'	:	{																										#	ON path masking
											'Config'		:	2																						,	#?	1->enable | 2->disable
											'HIGH'	:	{																									#!	HIGH mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[0, 0]																						#?	mask output
											},
											'LOW'	:	{																									#!	LOW mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[1, 1]																						#?	mask output
											}
										},
										'OFF'	:	{																										#	OFF path masking
											'Config'		:	2																						,	#?	1->enable | 2->disable
											'HIGH'	:	{																									#!	HIGH mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[0, 0]																						#?	mask output
											},
											'LOW'	:	{																									#!	LOW mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[1, 1]																						#?	mask output
											}
										}
									},
									'Boot'			:	{																									#*	bootstrap/charge pump parameters
										'Config'			:	1																						,	#?	1->bootstrap | 2->charge pump
										'Von'				:	14																						,	#?	boostrap driving voltage
										'Cboot'				:	4.7e-6																					,	#?	bootstrap capacitance
										'Vinit'				:	0																						,	#?	bootstrap capacitance initial voltage
										'Rboot'				:	10																						,	#?	bootstrap resistance
										'Vfboot'			:	0.87																					,	#?	bootstrap diode forward voltage
										'Rdboot'			:	1e-3																					,	#?	bootstrap diode ON-state resistance
										'Ichrg'				:	300e-6																					,	#?	charge pump supply current
										'Idis'				:	5e-6																					,	#?	charge pump loading or leakage current
										'Cpar'				:	0																						,	#?	charge pump parallel cap to break state/source dependency
									    'UVLO_Start'		:	11.6																					,	#?	threshold value to start the charge pump
										'UVLO_Stop'			:	12.4																						#?	threshold value to stop the charge pump
									},
							},
							'GateNetwork'			:	{																									#!	gate drive circuit parameters
									'Config'				:	2																						,	#?	1-> enable | 2->disable
									'ON_Path'		:	{																									#*	sourcing path parameters
										'Rg'				:	3.9																						,	#?	gate ON path resistance
										'Lg'				:	0																						,	#?	gate ON path inductance
										'Rload'				:	10e3																					,	#?	gate pull down resistance
										'Diode'	:	{																										#	reverse blocking diode parameters
											'Vf'			:	0																						,	#?	forward voltage
											'Rd_on'			:	0																						,	#?	ON-state resistance
										},
									},
									'OFF_Path'		:	{																									#*	sinking path parameters
										'Rg'				:	1																						,	#?	gate OFF path resistance
										'Lg'				:	0																						,	#?	gate OFF path inductance
										'Diode'	:	{																										#	reverse blocking diode parameters
											'Vf'			:	0.3																						,	#?	forward voltage
											'Rd_on'			:	1e-3																					,	#?	ON-state resistance
										},
									},
									'NegVolt'		:	{																									#*	negative voltage generator parameters
										'Config'			:	2																						,	#?	1-> enable | 2->disable
										'Dz'	:	{																										#	zener diode parameters
											'Vf'			:	0.7																						,	#?	forward voltage
											'Rd_on'			:	1e-3																					,	#?	ON-state resistance
											'Vz'			:	2																						,	#?	Zener breakdown voltage
											'Rz'			:	1e-3																					,	#?	Zener resistance
										},
										'Dp'	:	{																										#	peak detector diode
											'Vf'			:	0.0																						,	#?	forward voltage
											'Rd_on'			:	0.0																						,	#?	ON-state resistance
										},
										'Cz'	:	{																										#	Zener capacitor parameters
											'Config'		:	1																						,	#?	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
											'Csingle'		:	1e-6																					,	#?	single capacitor value
											'Rsingle'		:	5e-3																					,	#?	ESR of single capacitor
											'Lsingle'		:	0																						,	#?	ESL of single capacitor
											'nPar'			:	1																						,	#?	number of parallel connections
											'nSer'			:	1																						,	#?	number of series connections
											'Vinit'			:	0																						,	#?	capacitor initial voltage
										},
										'Cp'	:	{																										#	peak detector capacitor parameters
											'Config'		:	1																						,	#?	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
											'Csingle'		:	2.2e-6																					,	#?	single capacitor value
											'Rsingle'		:	5e-3																					,	#?	ESR of single capacitor
											'Lsingle'		:	0																						,	#?	ESL of single capacitor
											'nPar'			:	1																						,	#?	number of parallel connections
											'nSer'			:	1																						,	#?	number of series connections
											'Vinit'			:	0																						,	#?	capacitor initial voltage
										},
										'Rp1'				:	43																						,	#?	current limiter of peak detector current
										'Rp2'				:	4.7e3																					,	#?	load resistor to charge the zener diode
									},
								},
							'nParallel'   					:	1                                       												,   #? 	number of parallel devices
							'Rth_jc'						:	[3.5]																					,	#?	junction-to-case thermal resistance
							'Cth_jc'						:	[0]																						,	#?	junction-to-case thermal capacitance
							'Rth_ca'              			:   [0.19]					            													,   #? 	case-to-ambient thermal resistance
							'Cth_ca'              			:   [0,0]							             											,   #? 	case-to-ambient thermal capacitance
							'Tinit'							:	0.0																						,	#?	initial juntion temperature
							'Pinit'							:	0.0																						,	#?	initial power dissipation
							'Coss'					: 	{																									#!	device Coss parameters
								'C'							:	Coss_eff					 															,	#?	device parasitic output capacitance
								'R'							:	0																						,	#?	Coss resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Coss inductance to reduce current slope
								'Coss_er'					:	Crss_er																					,	#?	energy-related Coss
								'Coss_tr'					:	Coss_tr																					,	#?	time-related Coss
								'Vvec'						:	Coss[0]																					,	#? 	device Coss voltage vector
								'Cvec'						:	Coss[1]																					,	#?	device Coss capacity vector
								'Offset'					:	0																						,	#?	parasitic offset to Coss
                                'Factor'					:	1.0																						,	#?	parasitic tolerance to Coss
								'Qoss'						:	Qoss																					,	#?	equivalent charge of Coss
								'Eoss'						:	Eoss																					,	#?	equivalent energy of Coss
								'Config'					:	1																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
						},
                        	'Crss'					:	{																									#!	device Crss parameters
                                'C'							:	Crss_eff					 															,	#?	device parasitic reverse transfer capacitance
								'R'							:	0																						,	#?	Crss resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Crss inductance to reduce current slope
								'Crss_er'					:	Crss_er																					,	#?	energy-related Crss
								'Crss_tr'					:	Crss_tr																					,	#?	time-related Crss
								'Vvec'						:	Crss[0]																					,	#?	device Crss voltage vector
                                'Cvec'						:	Crss[1]																					,	#?	device Crss capacity vector
								'Qvec'						:	Qrss																					,	#?	device accumulated Crss charge vector
								'Offset'					:	0																						,	#?	parasitic offset to Crss
								'Factor'					:	1.0																						,	#?	parasitic tolerance to Crss
								'Qrss'						:	Qrss																					,	#?	equivalent charge of Crss
								'Erss'						:	Erss																					,	#?	equivalent energe of Crss
								'Config'					:	5																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
						},
							'Ciss'					:	{																									#!	device Ciss parameters
								'C'							:	Ciss_eff					 															,	#?	device parasitic input capacitance
								'R'							:	0																						,	#?	Ciss resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Ciss inductance to reduce current slope
								'Ciss_er'					:	Ciss_er																					,	#?	energy-related Ciss
								'Ciss_tr'					:	Ciss_tr																					,	#?	time-related Ciss
								'Vvec'						:	Ciss[0]																					,	#?	device Ciss voltage vector
								'Cvec'						:	Ciss[1]																					,	#?	device Ciss capacity vector
								'Offset'					:	0																						,	#?	parasitic offset to Ciss
								'Factor'					:	1.0																						,	#?	parasitic tolerance to Ciss
								'Qiss'						:	Qiss																					,	#?	equivalent charge of Ciss
								'Eiss'						:	Eiss																					,	#?	equivalent energy of Ciss
								'Config'					:	5																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Cds'					:	{																									#!	device Cds parameters
								'C'							:	Cds_eff					 																,	#?	device parasitic Cds capacitance
								'R'							:	0																						,	#?	Cds resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Cds inductance to reduce current slope
								'Cds_er'					:	Cds_er																					,	#?	energy-related Cds
								'Cds_tr'					:	Cds_tr																					,	#?	time-related Cds
								'Vvec'						:	Coss[0]																					,	#?	device Cds voltage vector
								'Cvec'						:	Cds																						,	#?	device Cds capacity vector
								'Offset_ON'					:	0																						,	#?	tuning offset for turn ON
								'Offset_OFF'				:	0																						,	#?	tuning offset for turn OFF
								'Factor_ON'					:	2.0																						,	#?	tuning factor for turn ON
								'Factor_OFF'				:	1.0																						,	#?	tuning factor for turn OFF
								'Config'					:	4																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Cgd'					:	{																									#!	device Cgd parameters
								'C'							:	Cgd_eff							 														,	#?	device parasitic Cgd capacitance
								'R'							:	0																						,	#?	Cgd resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Cgd inductance to reduce current slope
								'Cgd_er'					:	Cgd_er																					,	#?	energy-related Cgd
								'Cgd_tr'					:	Cgd_tr																					,	#?	time-related Cgd
								'Vvec'						:	Crss[0]																					,	#?	device Cgd voltage vector
								'Cvec'						:	Cgd																						,	#?	device Cgd capacity vector
								'Offset_ON'					:	0																						,	#?	tuning offset for turn ON
								'Offset_OFF'				:	0																						,	#?	tuning offset for turn OFF
								'Factor_ON'					:	1.0																						,	#?	tuning factor for turn ON
								'Factor_OFF'				:	1.0																						,	#?	tuning factor for turn OFF
								'Config'					:	4																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Cgs'					:	{																									#!	device Cgs parameters
								'C'							:	Cgs_eff					 																,	#?	device parasitic Cgs capacitance
								'R'							:	0																						,	#?	Cgs resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Cgs inductance to reduce current slope
								'Cgs_er'					:	Cgs_er																					,	#?	energy-related Cgs
								'Cgs_tr'					:	Cgs_tr																					,	#?	time-related Cgs
								'Vvec'						:	Ciss[0]																					,	#?	device Cgs voltage vector
								'Cvec'						:	Cgs																						,	#?	device Cgs capacity vector
								'Offset_ON'					:	0																						,	#?	tuning offset for turn ON
								'Offset_OFF'				:	0																						,	#?	tuning offset for turn OFF
								'Factor_ON'					:	1.0																						,	#?	tuning factor for turn ON
								'Factor_OFF'				:	1.0																						,	#?	tuning factor for turn OFF
								'Config'					:	4																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Eoff'					:	{																									#!	transistor turn-OFF energy losses
									'Ivec'					:	Ioff																					,	#?	turn-OFF energy current vector
                                    'Rgvec'					:	[0,100]																					,	#?	OFF path gate resistances vector
									'Tjvec'					:	[-55,175]																				,	#?	junction temperature vector
                                    'Vvec'					:	Voff																					,	#?	turn-OFF voltage vector
                                    'Evec'					:	Eoff																					,	#?	turn-OFF energy vectors
									'Evec_Temp'				:	Eoff_Temp																				,	#?	turn-OFF energy temp scaling vectors
                                    'CAT'					:	catOFF																					,	#?	octave Eoff energy syntax
									'CAT_Temp'				:	catOFF_Temp																				,	#?	octave Eoff energy temp scaling syntax
									'Vgs'					:	-1.3																					,	#?	used OFF path gate-source voltage
									'Vth'					:	3.0																						,	#?	used OFF path threshold voltage
									'Rg'					:	1																							#?	used OFF path gate resistance
						},
							'Eon'					:	{																									#!	transistor turn-ON energy losses
									'Ivec'					:	Ion																						,	#?	turn-ON energy current vector
									'Rgvec'					:	[0,100]																					,	#?	ON path gate resistances vector
									'Tjvec'					:	[-55,175]																				,	#?	junction temperature vector
                                    'Vvec'					:	Von																						,	#?	turn-ON voltage vector
                                    'Evec'					:	Eon																						,	#?	turn-ON energy vectors
									'Evec_Temp'				:	Eon_Temp																				,	#?	turn-ON energy temp scaling vectors
                                    'CAT'					:	catON																					,	#?	octave Eon energy syntax
									'CAT_Temp'				:	catON_Temp																				,	#?	octave Eon energy temp scaling syntax
									'Vgs'					:	11.3																					,	#?	used ON path gate-source voltage
									'Vth'					:	3.0																						,	#?	used ON path threshold voltage
									'Rg'					:	0																							#?	used ON path gate resistance
						},
							'Tau_deg'						:	100e-9																					,	#?	deglitch filter for currents and voltages
							'RCsnubber'						:	2																						,	#?	1->enable | 2->disable
						}

#?----------------------------------------------------------------------------------------------------------------------------------------------------------------------

Coss,Qoss,Eoss,Coss_tr,Coss_er		=	paramProcess.MOSFETcaps(switchesCossPath,'NVMJST3D3N08X','_Coss')
Crss,Qrss,Erss,Crss_tr,Crss_er 		=	paramProcess.MOSFETcaps(switchesCrssPath,'NVMJST3D3N08X','_Crss')
Ciss,Qiss,Eiss,Ciss_tr,Ciss_er 		=	paramProcess.MOSFETcaps(switchesCissPath,'NVMJST3D3N08X','_Ciss')
Coss_eff 							=	paramProcess.getCmos(Coss,Coss_tr,Coss_er,Coss[0][0],True)
Ciss_eff 							=	paramProcess.getCmos(Ciss,Ciss_tr,Ciss_er,Ciss[0][0],True)
Crss_eff 							=	paramProcess.getCmos(Crss,Crss_tr,Crss_er,Crss[0][0],True)
Cds 						        =	(np.array(Coss[1]) - np.array(Crss[1])).tolist()
Cgs						        	=	(np.array(Ciss[1]) - np.array(Crss[1])).tolist()
Cgd						        	=	Crss[1]
Cds_tr						        =	(np.array(Coss_tr) - np.array(Crss_tr)).tolist()
Cgs_tr						        =	(np.array(Ciss_tr) - np.array(Crss_tr)).tolist()
Cgd_tr						        =	Crss_tr
Cds_er						        =	(np.array(Coss_er) - np.array(Crss_er)).tolist()
Cgs_er						        =	(np.array(Ciss_er) - np.array(Crss_er)).tolist()
Cgd_er						        =	Crss_er
Cds_eff 							=	paramProcess.getCmos([Coss[0],Cds],Cds_tr,Cds_er,Coss[0][0],True)
Cgs_eff 							=	paramProcess.getCmos([Ciss[0],Cgs],Cgs_tr,Cgs_er,Ciss[0][0],True)
Cgd_eff 							=	Crss_eff
Rvec,Tvec							=	paramProcess.MOSFETrdson(switchesRdsonPath,'NVMJST3D3N08X','_Rdson')
Nvec,Ivec 							=	paramProcess.MOSFETrdson(switchesIdsonPath,'NVMJST3D3N08X','_Rdson')
Ioff,catOFF,Eoff					=	paramProcess.MOSFETenergies(switchesEoffPath,'NVMJST3D3N08X','_Eoff')
Voff,catOFF_Temp,Eoff_Temp			=	paramProcess.MOSFETenergies(switchesEoffPath,'NVMJST3D3N08X','_Eoff_Temp')
Ion,catON,Eon 						=	paramProcess.MOSFETenergies(switchesEonPath,'NVMJST3D3N08X','_Eon')
Von,catON_Temp,Eon_Temp				=	paramProcess.MOSFETenergies(switchesEonPath,'NVMJST3D3N08X','_Eon_Temp')
Vfvec,Ifvec,Rd,Vt					=	paramProcess.DiodeVI_data(bodyDiodeVIPath,'NVMJST3D3N08X')
Vds_vec,Ids_vec 					=	paramProcess.Forward_Transfer_data(switchesTransferPath,'NVMJST3D3N08X')

NVMJST3D3N08X		=	{																																	#*	NVMJST3D3N08X parameters
							'Config'						:	1																						,	#!	1->electric integrated | 2->electric separate | 3->thermal integrated | 4->thermal separate
							'Transistor'  			: 	{																									#!	transistors parameters
									'Config'				:	2																						,	#?	1->real model | 2->ideal model | 3->behavioral model
									'Thermal'           	:   ''                                  													,   #? 	selected transistor
									'Custom'            	:   []						               													,   #? 	transistor provided custom variables
									'g_fs'					:	1e6																						,	#?	forward transconductance
									'Rg'					:	0.6																						,	#?	internal gate resistance
									'Lg'					:	0																						,	#?	gate pin inductance
									'Rds_on'            	:   Rvec[-1][-1]*1e-3																		,   #? 	transistor ON resistance
									'Rds_off'				:	'inf'																					,	#?	transistor OFF resistance
									'Rvec'					:	(np.array(Rvec)*1e-3).tolist()														,	#?	absolute Rdson vector corresponding to junction temperature
									'Tvec'					:	Tvec 																					,	#?	junction temperature vector for Rdson
									'RTconfig'				:	1																						,	#?	choose which RT vector to be used
									'RdsonScale'			:	1.183																					,	#?	Rdson scaling to account for min, typ and max deviations
									'Nvec'					:	Nvec 																					,	#?	normalized Rdson vector corresponding to current
									'Ivec'					:	Ivec																					,	#?	current vector for normalized Rdson
									'NIconfig'				:	1																						,	#?	choose which NI vector to be used
									'IdsonScale'			:	1.0																						,	#?	Idson resistance scaling to account for min, typ and max deviations
									'Rsrc'					:	0																						,	#?	kelvin source pin resistance
									'Lsrc'					:	0																						,	#?	kelvin source pin inductance
									'Ls'					:	0																						,	#?	package source inductance
                                    'Ld'					:	0																						,	#?	package drain inductance
									'Rs'					:	0																						,	#?	package source resistance
									'Rd'					:	0																						,	#?	package drain inductance
									'Ksrc'					:	0																						,	#?	kelvin source option, 0->no kelvin | 1->kelvin
									'Vblock'            	:   80                               	 													,   #? 	transistor blocking voltage
									'Id'                	:   194                                 													,   #? 	transistor drain current
									'Tr'                	:   31e-9                                   												,   #? 	transistor rise time
									'Tf'                	:   39e-9                                       											, 	#? 	transistor fall time
									'Avalanche'		:	{																									#!	transistor avalanche parameters
										'Config'			:	2																						,	#?	1->enable | 2->disable
										'Voltage'			:	80																						,	#?	avalanche voltage
										'Resistance'		:	1e-3																						#?	avalanche resistance to break voltage state-dependency
									},
									'Transfer'		:	{																									#!	transistor forward transfer parameters
										'Vds'				:	Vds_vec																					,	#?	drain-source voltage vector
										'Vgs'				:	[0,20]																					,	#?	gate-source voltage vector
										'Ids'				:	Ids_vec																					,	#?	drain current vector
										'Factor_ON'			:	1.0																						,	#?	scaling factor for Ids at turn ON
										'Factor_OFF'		:	1.0																						,	#?	scaling factor for Ids at turn OFF
										'Factor_Vgs_ON'		:	1.0																						,	#?	scaling factor for Vgs at turn ON
										'Factor_Vgs_OFF'	:	1.0																						,	#?	scaling factor for Vgs at turn OFF
										'Vcoss'				:	0																						,	#?	initial voltage of the Coss
									},
						},
							'BodyDiode'  			:	{																									#!	body diodes paramteters
									'Config'				:	4																						,	#?	1->non-ideal RR | 2->non-ideal | 3->ideal RR | 4->ideal
									'Thermal'           	:   ''                                  													,   #? 	separate body diode
									'Custom'            	:   []					                 													,   #? 	body diode provided custrom variables
									'Rd_on'             	:   Rd[-1]																					,  	#? 	body diode ON resistance
									'Rd_off'				:	'inf'																					,	#?	body diode OFF resistance
									'Vf'					:	Vt[-1]																					,	#? 	body diode forward voltage
									'If'                	:   194                                 													,   #? 	body diode forward current
									'dIr'               	:   1e9		                                   												,   #? 	body diode current slope
									'Lrr'					:	1e-9																					,	#?	body diode reverse recovery inductance
									'Trr'               	:   22.6e-9                                													,   #? 	body diode reverse recovery time
									'Irr'               	:   0                                   													,   #? 	body diode reverse recovery current
									'Qrr'               	:   151e-9                                  												, 	#? 	body diode reverse recovery charge
									'Is'                  	:   31              																		, 	#? 	body diode reference current
									'Vs'					:	64																						,	#?	body diode reference voltage
                                    'VIcurve'		:	{																									#!	body diode VI characteristics
                                        'Vfvec'				:	Vfvec																					,	#?	forward voltage vector
                                        'Ifvec'				:	Ifvec																					,	#?	forward current vector
										'Rdvec'				:	Rd																						,	#?	dynamic resistance vector
										'Vtvec'				:	Vt																						,	#?	threshold voltage vector
                                        'Temps'				:	[-55,25,175]																			,	#?	temperature vector
                                        'Vfscale'			:	1.445																						#?	Vf scaling to account for min, typ and max deviations
									},
						},
							'GateDriver'			:	{																									#!	gate driver parameters
									'Config'				:	3																						,	#?	1->high-side | 2->low-side | 3->disable
									'Von'					:	11.235																					,	#?	ON driving voltage
									'Voff'					:	-1.509																					,	#?	OFF driving voltage
									'Ron'					:	3.4																						,	#?	sourcing output resistance
									'Roff'					:	1.8																						,	#?	sinking output resistance
									'Lon'					:	0																						,	#?	sourcing output inductance
									'Loff'					:	0																						,	#?	sinking output inductance
									'Cload'					:	0																						,	#?	capacitive load on output
									'Rload'					:	4.7e3																					,	#?	resistive load on output
									'Delay'					:	71e-9																					,	#?	input-to-output total deadtime
									'Trise'					:	30e-9																					,	#?	output rising time
									'Tfall'					:	25e-9																					,	#?	output falling time
									'UVLO_Start'			:	7.0																						,	#?	UVLO startup voltage threshold
									'UVLO_Stop'				:	6.5																						,	#?	UVLO shutdown voltage threshold
									'UVLO_Delay'			:	100e-9																					,	#?	delay between UVLO startup and shutdown
									'Init_State'			:	0																						,	#?	initial toggling state, 0->OFF | 1->ON
									'CurrentLimit'	:	{																									#*	current limit of driver stage
										'Config'			:	2																						,	#?	1->enable | 2->disable
										'Ts'				: 	0 																						,	#?	sampling time between inductive & capacitive links
										'tau'				: 	0																						,	#?	first-order delay between inductive & capacitive links
                                    	'Rs'				: 	0																						,	#?	source impedance of inductive link
										'Cs'				:	1e-12																					,	#?	source capacitance of capacitive link
                                        'UpLim'				: 	10																						,	#?	max current limit on capacitive link
                                        'LoLim'				: 	-10																						,	#?	min current limit on capacitive link
                                        'Voffset'			: 	0																							#?	voltage offset between inductive & capacitive links
									},
									'Masking'		:	{																									#*	switching stages masking
										'ON'	:	{																										#	ON path masking
											'Config'		:	2																						,	#?	1->enable | 2->disable
											'HIGH'	:	{																									#!	HIGH mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[0, 0]																						#?	mask output
											},
											'LOW'	:	{																									#!	LOW mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[1, 1]																						#?	mask output
											}
										},
										'OFF'	:	{																										#	OFF path masking
											'Config'		:	2																						,	#?	1->enable | 2->disable
											'HIGH'	:	{																									#!	HIGH mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[0, 0]																						#?	mask output
											},
											'LOW'	:	{																									#!	LOW mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[1, 1]																						#?	mask output
											}
										}
									},
									'Boot'			:	{																									#*	bootstrap/charge pump parameters
										'Config'			:	1																						,	#?	1->bootstrap | 2->charge pump
										'Von'				:	14																						,	#?	boostrap driving voltage
										'Cboot'				:	4.7e-6																					,	#?	bootstrap capacitance
										'Vinit'				:	0																						,	#?	bootstrap capacitance initial voltage
										'Rboot'				:	3.3																						,	#?	bootstrap resistance
										'Vfboot'			:	0.87																					,	#?	bootstrap diode forward voltage
										'Rdboot'			:	22.4e-3																					,	#?	bootstrap diode ON-state resistance
										'Ichrg'				:	300e-6																					,	#?	charge pump supply current
										'Idis'				:	5e-6																					,	#?	charge pump loading or leakage current
										'Cpar'				:	0																						,	#?	charge pump parallel cap to break state/source dependency
									    'UVLO_Start'		:	11.6																					,	#?	threshold value to start the charge pump
										'UVLO_Stop'			:	12.4																						#?	threshold value to stop the charge pump
									},
							},
							'GateNetwork'			:	{																									#!	gate drive circuit parameters
									'Config'				:	2																						,	#?	1-> enable | 2->disable
									'ON_Path'		:	{																									#*	sourcing path parameters
										'Rg'				:	3.9																						,	#?	gate ON path resistance
										'Lg'				:	0																						,	#?	gate ON path inductance
										'Rload'				:	4.7e3																					,	#?	gate pull down resistance
										'Diode'	:	{																										#	reverse blocking diode parameters
											'Vf'			:	0																						,	#?	forward voltage
											'Rd_on'			:	0																						,	#?	ON-state resistance
										},
									},
									'OFF_Path'		:	{																									#*	sinking path parameters
										'Rg'				:	1																						,	#?	gate OFF path resistance
										'Lg'				:	0																						,	#?	gate OFF path inductance
										'Diode'	:	{																										#	reverse blocking diode parameters
											'Vf'			:	0.38																					,	#?	forward voltage
											'Rd_on'			:	54.29e-3																				,	#?	ON-state resistance
										},
									},
									'NegVolt'		:	{																									#*	negative voltage generator parameters
										'Config'			:	2																						,	#?	1-> enable | 2->disable
										'Dz'	:	{																										#	zener diode parameters
											'Vf'			:	0.9																						,	#?	forward voltage
											'Rd_on'			:	55e-3																					,	#?	ON-state resistance
											'Vz'			:	1.5																						,	#?	Zener breakdown voltage
											'Rz'			:	15																						,	#?	Zener resistance
										},
										'Dp'	:	{																										#	peak detector diode
											'Vf'			:	0.38																					,	#?	forward voltage
											'Rd_on'			:	54.29e-3																				,	#?	ON-state resistance
										},
										'Cz'	:	{																										#	Zener capacitor parameters
											'Config'		:	2																						,	#?	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
											'Csingle'		:	0.8e-6																					,	#?	single capacitor value
											'Rsingle'		:	5e-3																					,	#?	ESR of single capacitor
											'Lsingle'		:	0																						,	#?	ESL of single capacitor
											'nPar'			:	1																						,	#?	number of parallel connections
											'nSer'			:	1																						,	#?	number of series connections
											'Vinit'			:	0																						,	#?	capacitor initial voltage
										},
										'Cp'	:	{																										#	peak detector capacitor parameters
											'Config'		:	2																						,	#?	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
											'Csingle'		:	0.66e-6																					,	#?	single capacitor value
											'Rsingle'		:	5e-3																					,	#?	ESR of single capacitor
											'Lsingle'		:	0																						,	#?	ESL of single capacitor
											'nPar'			:	1																						,	#?	number of parallel connections
											'nSer'			:	1																						,	#?	number of series connections
											'Vinit'			:	0																						,	#?	capacitor initial voltage
										},
										'Rp1'				:	23.32																					,	#?	current limiter of peak detector current
										'Rp2'				:	4.7e3																					,	#?	load resistor to charge the zener diode
									},
								},
							'nParallel'   					:	1                                       												,   #? 	number of parallel devices
							'Rth_jc'						:	[0.58]																					,	#?	junction-to-case thermal resistance
							'Cth_jc'						:	[0]																						,	#?	junction-to-case thermal capacitance
							'Rth_ca'              			:   [0]            																			,   #? 	case-to-ambient thermal resistance
							'Cth_ca'              			:   [0]             																		,   #? 	case-to-ambient thermal capacitance
							'Tinit'							:	0.0																						,	#?	initial juntion temperature
							'Pinit'							:	0.0																						,	#?	initial power dissipation
							'Coss'					: 	{																									#!	device Coss parameters
								'C'							:	Coss_eff					 															,	#?	device parasitic output capacitance
								'R'							:	0																						,	#?	Coss resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Coss inductance to reduce current slope
								'Coss_er'					:	Crss_er																					,	#?	energy-related Coss
								'Coss_tr'					:	Coss_tr																					,	#?	time-related Coss
								'Vvec'						:	Coss[0]																					,	#? 	device Coss voltage vector
								'Cvec'						:	Coss[1]																					,	#?	device Coss capacity vector
								'Offset'					:	0																						,	#?	parasitic offset to Coss
                                'Factor'					:	1.0																						,	#?	parasitic tolerance to Coss
								'Qoss'						:	Qoss																					,	#?	equivalent charge of Coss
								'Eoss'						:	Eoss																					,	#?	equivalent energy of Coss
								'Config'					:	5																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
						},
                        	'Crss'					:	{																									#!	device Crss parameters
                                'C'							:	Crss_eff					 															,	#?	device parasitic reverse transfer capacitance
								'R'							:	0																						,	#?	Crss resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Crss inductance to reduce current slope
								'Crss_er'					:	Crss_er																					,	#?	energy-related Crss
								'Crss_tr'					:	Crss_tr																					,	#?	time-related Crss
								'Vvec'						:	Crss[0]																					,	#?	device Crss voltage vector
                                'Cvec'						:	Crss[1]																					,	#?	device Crss capacity vector
								'Qvec'						:	Qrss																					,	#?	device accumulated Crss charge vector
								'Offset'					:	0																						,	#?	parasitic offset to Crss
								'Factor'					:	1.0																						,	#?	parasitic tolerance to Crss
								'Qrss'						:	Qrss																					,	#?	equivalent charge of Crss
								'Erss'						:	Erss																					,	#?	equivalent energe of Crss
								'Config'					:	5																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
						},
							'Ciss'					:	{																									#!	device Ciss parameters
								'C'							:	Ciss_eff					 															,	#?	device parasitic input capacitance
								'R'							:	0																						,	#?	Ciss resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Ciss inductance to reduce current slope
								'Ciss_er'					:	Ciss_er																					,	#?	energy-related Ciss
								'Ciss_tr'					:	Ciss_tr																					,	#?	time-related Ciss
								'Vvec'						:	Ciss[0]																					,	#?	device Ciss voltage vector
								'Cvec'						:	Ciss[1]																					,	#?	device Ciss capacity vector
								'Offset'					:	0																						,	#?	parasitic offset to Ciss
								'Factor'					:	1.0																						,	#?	parasitic tolerance to Ciss
								'Qiss'						:	Qiss																					,	#?	equivalent charge of Ciss
								'Eiss'						:	Eiss																					,	#?	equivalent energy of Ciss
								'Config'					:	5																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Cds'					:	{																									#!	device Cds parameters
								'C'							:	Cds_eff					 																,	#?	device parasitic Cds capacitance
								'R'							:	0																						,	#?	Cds resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Cds inductance to reduce current slope
								'Cds_er'					:	Cds_er																					,	#?	energy-related Cds
								'Cds_tr'					:	Cds_tr																					,	#?	time-related Cds
								'Vvec'						:	Coss[0]																					,	#?	device Cds voltage vector
								'Cvec'						:	Cds																						,	#?	device Cds capacity vector
								'Offset_ON'					:	0																						,	#?	tuning offset for turn ON
								'Offset_OFF'				:	0																						,	#?	tuning offset for turn OFF
								'Factor_ON'					:	1.0																						,	#?	tuning factor for turn ON
								'Factor_OFF'				:	1.0																						,	#?	tuning factor for turn OFF
								'Config'					:	4																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Cgd'					:	{																									#!	device Cgd parameters
								'C'							:	Cgd_eff							 														,	#?	device parasitic Cgd capacitance
								'R'							:	0																						,	#?	Cgd resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Cgd inductance to reduce current slope
								'Cgd_er'					:	Cgd_er																					,	#?	energy-related Cgd
								'Cgd_tr'					:	Cgd_tr																					,	#?	time-related Cgd
								'Vvec'						:	Crss[0]																					,	#?	device Cgd voltage vector
								'Cvec'						:	Cgd																						,	#?	device Cgd capacity vector
								'Offset_ON'					:	0																						,	#?	tuning offset for turn ON
								'Offset_OFF'				:	0																						,	#?	tuning offset for turn OFF
								'Factor_ON'					:	1.0																						,	#?	tuning factor for turn ON
								'Factor_OFF'				:	1.0																						,	#?	tuning factor for turn OFF
								'Config'					:	4																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Cgs'					:	{																									#!	device Cgs parameters
								'C'							:	Cgs_eff					 																,	#?	device parasitic Cgs capacitance
								'R'							:	0																						,	#?	Cgs resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Cgs inductance to reduce current slope
								'Cgs_er'					:	Cgs_er																					,	#?	energy-related Cgs
								'Cgs_tr'					:	Cgs_tr																					,	#?	time-related Cgs
								'Vvec'						:	Ciss[0]																					,	#?	device Cgs voltage vector
								'Cvec'						:	Cgs																						,	#?	device Cgs capacity vector
								'Offset_ON'					:	0																						,	#?	tuning offset for turn ON
								'Offset_OFF'				:	0																						,	#?	tuning offset for turn OFF
								'Factor_ON'					:	1.0																						,	#?	tuning factor for turn ON
								'Factor_OFF'				:	1.0																						,	#?	tuning factor for turn OFF
								'Config'					:	4																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Eoff'					:	{																									#!	transistor turn-OFF energy losses
									'Ivec'					:	Ioff																					,	#?	turn-OFF energy current vector
                                    'Rgvec'					:	[0,100]																					,	#?	OFF path gate resistances vector
									'Tjvec'					:	[-55,175]																				,	#?	junction temperature vector
                                    'Vvec'					:	Voff																					,	#?	turn-OFF voltage vector
                                    'Evec'					:	Eoff																					,	#?	turn-OFF energy vectors
									'Evec_Temp'				:	Eoff_Temp																				,	#?	turn-OFF energy temp scaling vectors
                                    'CAT'					:	catOFF																					,	#?	octave Eoff energy syntax
									'CAT_Temp'				:	catOFF_Temp																				,	#?	octave Eoff energy temp scaling syntax
									'Vgs'					:	-1.509																					,	#?	used OFF path gate-source voltage
									'Vth'					:	1.5																						,	#?	used OFF path threshold voltage
									'Rg'					:	1																							#?	used OFF path gate resistance
						},
							'Eon'					:	{																									#!	transistor turn-ON energy losses
									'Ivec'					:	Ion																						,	#?	turn-ON energy current vector
									'Rgvec'					:	[0,100]																					,	#?	ON path gate resistances vector
									'Tjvec'					:	[-55,175]																				,	#?	junction temperature vector
                                    'Vvec'					:	Von																						,	#?	turn-ON voltage vector
                                    'Evec'					:	Eon																						,	#?	turn-ON energy vectors
									'Evec_Temp'				:	Eon_Temp																				,	#?	turn-ON energy temp scaling vectors
                                    'CAT'					:	catON																					,	#?	octave Eon energy syntax
									'CAT_Temp'				:	catON_Temp																				,	#?	octave Eon energy temp scaling syntax
									'Vgs'					:	11.235																					,	#?	used ON path gate-source voltage
									'Vth'					:	1.5																						,	#?	used ON path threshold voltage
									'Rg'					:	3.9																							#?	used ON path gate resistance
						},
							'Tau_deg'						:	100e-9																					,	#?	deglitch filter for currents and voltages
							'RCsnubber'						:	2																						,	#?	1->enable | 2->disable
						}

#?----------------------------------------------------------------------------------------------------------------------------------------------------------------------

Coss,Qoss,Eoss,Coss_tr,Coss_er		=	paramProcess.MOSFETcaps(switchesCossPath,'NVBYST0D6N08X','_Coss')
Crss,Qrss,Erss,Crss_tr,Crss_er 		=	paramProcess.MOSFETcaps(switchesCrssPath,'NVBYST0D6N08X','_Crss')
Ciss,Qiss,Eiss,Ciss_tr,Ciss_er 		=	paramProcess.MOSFETcaps(switchesCissPath,'NVBYST0D6N08X','_Ciss')
Coss_eff 							=	paramProcess.getCmos(Coss,Coss_tr,Coss_er,Coss[0][0],True)
Ciss_eff 							=	paramProcess.getCmos(Ciss,Ciss_tr,Ciss_er,Ciss[0][0],True)
Crss_eff 							=	paramProcess.getCmos(Crss,Crss_tr,Crss_er,Crss[0][0],True)
Cds 						        =	(np.array(Coss[1]) - np.array(Crss[1])).tolist()
Cgs						        	=	(np.array(Ciss[1]) - np.array(Crss[1])).tolist()
Cgd						        	=	Crss[1]
Cds_tr						        =	(np.array(Coss_tr) - np.array(Crss_tr)).tolist()
Cgs_tr						        =	(np.array(Ciss_tr) - np.array(Crss_tr)).tolist()
Cgd_tr						        =	Crss_tr
Cds_er						        =	(np.array(Coss_er) - np.array(Crss_er)).tolist()
Cgs_er						        =	(np.array(Ciss_er) - np.array(Crss_er)).tolist()
Cgd_er						        =	Crss_er
Cds_eff 							=	paramProcess.getCmos([Coss[0],Cds],Cds_tr,Cds_er,Coss[0][0],True)
Cgs_eff 							=	paramProcess.getCmos([Ciss[0],Cgs],Cgs_tr,Cgs_er,Ciss[0][0],True)
Cgd_eff 							=	Crss_eff
Rvec,Tvec							=	paramProcess.MOSFETrdson(switchesRdsonPath,'NVBYST0D6N08X','_Rdson')
Nvec,Ivec 							=	paramProcess.MOSFETrdson(switchesIdsonPath,'NVBYST0D6N08X','_Rdson')
Ioff,catOFF,Eoff					=	paramProcess.MOSFETenergies(switchesEoffPath,'NVBYST0D6N08X','_Eoff')
Voff,catOFF_Temp,Eoff_Temp			=	paramProcess.MOSFETenergies(switchesEoffPath,'NVBYST0D6N08X','_Eoff_Temp')
Ion,catON,Eon 						=	paramProcess.MOSFETenergies(switchesEonPath,'NVBYST0D6N08X','_Eon')
Von,catON_Temp,Eon_Temp				=	paramProcess.MOSFETenergies(switchesEonPath,'NVBYST0D6N08X','_Eon_Temp')
Vfvec,Ifvec,Rd,Vt					=	paramProcess.DiodeVI_data(bodyDiodeVIPath,'NVBYST0D6N08X')
Vds_vec,Ids_vec 					=	paramProcess.Forward_Transfer_data(switchesTransferPath,'NVBYST0D6N08X')

NVBYST0D6N08X		=	{																																	#*	NVBYST0D6N08X parameters
							'Config'						:	1																						,	#!	1->electric integrated | 2->electric separate | 3->thermal integrated | 4->thermal separate
							'Transistor'  			: 	{																									#!	transistors parameters
									'Config'				:	2																						,	#?	1->real model | 2->ideal model | 3->behavioral model
									'Thermal'           	:   ''                                  													,   #? 	selected transistor
									'Custom'            	:   []						               													,   #? 	transistor provided custom variables
									'g_fs'					:	200																						,	#?	forward transconductance
									'Rg'					:	1																						,	#?	internal gate resistance
									'Lg'					:	0																						,	#?	gate pin inductance
									'Rds_on'            	:   Rvec[-1][-1]*1e-3																		,   #? 	transistor ON resistance
									'Rds_off'				:	'inf'																					,	#?	transistor OFF resistance
									'Rvec'					:	(np.array(Rvec)*1e-3).tolist()														,	#?	absolute Rdson vector corresponding to junction temperature
									'Tvec'					:	Tvec 																					,	#?	junction temperature vector for Rdson
									'RTconfig'				:	1																						,	#?	choose which RT vector to be used
									'RdsonScale'			:	1.1429																					,	#?	Rdson scaling to account for min, typ and max deviations
									'Nvec'					:	Nvec 																					,	#?	normalized Rdson vector corresponding to current
									'Ivec'					:	Ivec																					,	#?	current vector for normalized Rdson
									'NIconfig'				:	1																						,	#?	choose which NI vector to be used
									'IdsonScale'			:	1.0																						,	#?	Idson resistance scaling to account for min, typ and max deviations
									'Rsrc'					:	0																						,	#?	kelvin source pin resistance
									'Lsrc'					:	0																						,	#?	kelvin source pin inductance
									'Ls'					:	0																						,	#?	package source inductance
                                    'Ld'					:	0																						,	#?	package drain inductance
									'Rs'					:	0																						,	#?	package source resistance
									'Rd'					:	0																						,	#?	package drain inductance
									'Ksrc'					:	0																						,	#?	kelvin source option, 0->no kelvin | 1->kelvin
									'Vblock'            	:   80                               	 													,   #? 	transistor blocking voltage
									'Id'                	:   767                                 													,   #? 	transistor drain current
									'Tr'                	:   115e-9                                   												,   #? 	transistor rise time
									'Tf'                	:   132e-9                                       											, 	#? 	transistor fall time
									'Avalanche'		:	{																									#!	transistor avalanche parameters
										'Config'			:	2																						,	#?	1->enable | 2->disable
										'Voltage'			:	80																						,	#?	avalanche voltage
										'Resistance'		:	1e-3																						#?	avalanche resistance to break voltage state-dependency
									},
									'Transfer'		:	{																									#!	transistor forward transfer parameters
										'Vds'				:	Vds_vec																					,	#?	drain-source voltage vector
										'Vgs'				:	[0,20]																					,	#?	gate-source voltage vector
										'Ids'				:	Ids_vec																					,	#?	drain current vector
										'Factor_ON'			:	1.0																						,	#?	scaling factor for Ids at turn ON
										'Factor_OFF'		:	1.0																						,	#?	scaling factor for Ids at turn OFF
										'Factor_Vgs_ON'		:	1.0																						,	#?	scaling factor for Vgs at turn ON
										'Factor_Vgs_OFF'	:	1.0																						,	#?	scaling factor for Vgs at turn OFF
										'Vcoss'				:	0																						,	#?	initial voltage of the Coss
									},
						},
							'BodyDiode'  			:	{																									#!	body diodes paramteters
									'Config'				:	4																						,	#?	1->non-ideal RR | 2->non-ideal | 3->ideal RR | 4->ideal
									'Thermal'           	:   ''                                  													,   #? 	separate body diode
									'Custom'            	:   []					                 													,   #? 	body diode provided custrom variables
									'Rd_on'             	:   Rd[-1]																					,  	#? 	body diode ON resistance
									'Rd_off'				:	'inf'																					,	#?	body diode OFF resistance
									'Vf'					:	Vt[-1]																					,	#? 	body diode forward voltage
									'If'                	:   767                                 													,   #? 	body diode forward current
									'dIr'               	:   1e9		                                   												,   #? 	body diode current slope
									'Lrr'					:	1e-9																					,	#?	body diode reverse recovery inductance
									'Trr'               	:   63e-9                                													,   #? 	body diode reverse recovery time
									'Irr'               	:   0                                   													,   #? 	body diode reverse recovery current
									'Qrr'               	:   777e-9                                  												, 	#? 	body diode reverse recovery charge
									'Is'                  	:   80              																		, 	#? 	body diode reference current
									'Vs'					:	64																						,	#?	body diode reference voltage
                                    'VIcurve'		:	{																									#!	body diode VI characteristics
                                        'Vfvec'				:	Vfvec																					,	#?	forward voltage vector
                                        'Ifvec'				:	Ifvec																					,	#?	forward current vector
										'Rdvec'				:	Rd																						,	#?	dynamic resistance vector
										'Vtvec'				:	Vt																						,	#?	threshold voltage vector
                                        'Temps'				:	[-55,25,175]																			,	#?	temperature vector
                                        'Vfscale'			:	1.538																						#?	Vf scaling to account for min, typ and max deviations
									},
						},
							'GateDriver'			:	{																									#!	gate driver parameters
									'Config'				:	3																						,	#?	1->high-side | 2->low-side | 3->disable
									'Von'					:	11.3																					,	#?	ON driving voltage
									'Voff'					:	-1.3																					,	#?	OFF driving voltage
									'Ron'					:	3.4																						,	#?	sourcing output resistance
									'Roff'					:	1.8																						,	#?	sinking output resistance
									'Lon'					:	0																						,	#?	sourcing output inductance
									'Loff'					:	0																						,	#?	sinking output inductance
									'Cload'					:	0																						,	#?	capacitive load on output
									'Rload'					:	4.7e3																					,	#?	resistive load on output
									'Delay'					:	71e-9																					,	#?	input-to-output total deadtime
									'Trise'					:	30e-9																					,	#?	output rising time
									'Tfall'					:	25e-9																					,	#?	output falling time
									'UVLO_Start'			:	7.0																						,	#?	UVLO startup voltage threshold
									'UVLO_Stop'				:	6.5																						,	#?	UVLO shutdown voltage threshold
									'UVLO_Delay'			:	100e-9																					,	#?	delay between UVLO startup and shutdown
									'Init_State'			:	0																						,	#?	initial toggling state, 0->OFF | 1->ON
									'CurrentLimit'	:	{																									#*	current limit of driver stage
										'Config'			:	2																						,	#?	1->enable | 2->disable
										'Ts'				: 	0 																						,	#?	sampling time between inductive & capacitive links
										'tau'				: 	0																						,	#?	first-order delay between inductive & capacitive links
                                    	'Rs'				: 	0																						,	#?	source impedance of inductive link
										'Cs'				:	1e-12																					,	#?	source capacitance of capacitive link
                                        'UpLim'				: 	10																						,	#?	max current limit on capacitive link
                                        'LoLim'				: 	-10																						,	#?	min current limit on capacitive link
                                        'Voffset'			: 	0																							#?	voltage offset between inductive & capacitive links
									},
									'Masking'		:	{																									#*	switching stages masking
										'ON'	:	{																										#	ON path masking
											'Config'		:	2																						,	#?	1->enable | 2->disable
											'HIGH'	:	{																									#!	HIGH mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[0, 0]																						#?	mask output
											},
											'LOW'	:	{																									#!	LOW mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[1, 1]																						#?	mask output
											}
										},
										'OFF'	:	{																										#	OFF path masking
											'Config'		:	2																						,	#?	1->enable | 2->disable
											'HIGH'	:	{																									#!	HIGH mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[0, 0]																						#?	mask output
											},
											'LOW'	:	{																									#!	LOW mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[1, 1]																						#?	mask output
											}
										}
									},
									'Boot'			:	{																									#*	bootstrap/charge pump parameters
										'Config'			:	1																						,	#?	1->bootstrap | 2->charge pump
										'Von'				:	14																						,	#?	boostrap driving voltage
										'Cboot'				:	4.7e-6																					,	#?	bootstrap capacitance
										'Vinit'				:	0																						,	#?	bootstrap capacitance initial voltage
										'Rboot'				:	3.3																						,	#?	bootstrap resistance
										'Vfboot'			:	0.87																					,	#?	bootstrap diode forward voltage
										'Rdboot'			:	22.4e-3																					,	#?	bootstrap diode ON-state resistance
										'Ichrg'				:	300e-6																					,	#?	charge pump supply current
										'Idis'				:	5e-6																					,	#?	charge pump loading or leakage current
										'Cpar'				:	0																						,	#?	charge pump parallel cap to break state/source dependency
									    'UVLO_Start'		:	11.6																					,	#?	threshold value to start the charge pump
										'UVLO_Stop'			:	12.4																						#?	threshold value to stop the charge pump
									},
							},
							'GateNetwork'			:	{																									#!	gate drive circuit parameters
									'Config'				:	2																						,	#?	1-> enable | 2->disable
									'ON_Path'		:	{																									#*	sourcing path parameters
										'Rg'				:	3.9																						,	#?	gate ON path resistance
										'Lg'				:	0																						,	#?	gate ON path inductance
										'Rload'				:	4.7e3																					,	#?	gate pull down resistance
										'Diode'	:	{																										#	reverse blocking diode parameters
											'Vf'			:	0																						,	#?	forward voltage
											'Rd_on'			:	0																						,	#?	ON-state resistance
										},
									},
									'OFF_Path'		:	{																									#*	sinking path parameters
										'Rg'				:	1																						,	#?	gate OFF path resistance
										'Lg'				:	0																						,	#?	gate OFF path inductance
										'Diode'	:	{																										#	reverse blocking diode parameters
											'Vf'			:	0.38																					,	#?	forward voltage
											'Rd_on'			:	54.29e-3																				,	#?	ON-state resistance
										},
									},
									'NegVolt'		:	{																									#*	negative voltage generator parameters
										'Config'			:	2																						,	#?	1-> enable | 2->disable
										'Dz'	:	{																										#	zener diode parameters
											'Vf'			:	0.9																						,	#?	forward voltage
											'Rd_on'			:	55e-3																					,	#?	ON-state resistance
											'Vz'			:	1.3																						,	#?	Zener breakdown voltage
											'Rz'			:	15																						,	#?	Zener resistance
										},
										'Dp'	:	{																										#	peak detector diode
											'Vf'			:	0.38																					,	#?	forward voltage
											'Rd_on'			:	54.29e-3																				,	#?	ON-state resistance
										},
										'Cz'	:	{																										#	Zener capacitor parameters
											'Config'		:	2																						,	#?	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
											'Csingle'		:	1.72e-6																					,	#?	single capacitor value
											'Rsingle'		:	5e-3																					,	#?	ESR of single capacitor
											'Lsingle'		:	0																						,	#?	ESL of single capacitor
											'nPar'			:	1																						,	#?	number of parallel connections
											'nSer'			:	1																						,	#?	number of series connections
											'Vinit'			:	0																						,	#?	capacitor initial voltage
										},
										'Cp'	:	{																										#	peak detector capacitor parameters
											'Config'		:	2																						,	#?	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
											'Csingle'		:	1.24e-6																					,	#?	single capacitor value
											'Rsingle'		:	5e-3																					,	#?	ESR of single capacitor
											'Lsingle'		:	0																						,	#?	ESL of single capacitor
											'nPar'			:	1																						,	#?	number of parallel connections
											'nSer'			:	1																						,	#?	number of series connections
											'Vinit'			:	0																						,	#?	capacitor initial voltage
										},
										'Rp1'				:	23.32																						,	#?	current limiter of peak detector current
										'Rp2'				:	4.7e3																					,	#?	load resistor to charge the zener diode
									},
								},
							'nParallel'   					:	1                                       												,   #? 	number of parallel devices
							'Rth_jc'						:	[0.2]																					,	#?	junction-to-case thermal resistance
							'Cth_jc'						:	[0]																						,	#?	junction-to-case thermal capacitance
							'Rth_ca'              			:   [3.5]            																		,   #? 	case-to-ambient thermal resistance
							'Cth_ca'              			:   [0]             																		,   #? 	case-to-ambient thermal capacitance
							'Tinit'							:	0.0																						,	#?	initial juntion temperature
							'Pinit'							:	0.0																						,	#?	initial power dissipation
							'Coss'					: 	{																									#!	device Coss parameters
								'C'							:	Coss_eff					 															,	#?	device parasitic output capacitance
								'R'							:	0																						,	#?	Coss resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Coss inductance to reduce current slope
								'Coss_er'					:	Crss_er																					,	#?	energy-related Coss
								'Coss_tr'					:	Coss_tr																					,	#?	time-related Coss
								'Vvec'						:	Coss[0]																					,	#? 	device Coss voltage vector
								'Cvec'						:	Coss[1]																					,	#?	device Coss capacity vector
								'Offset'					:	0																						,	#?	parasitic offset to Coss
                                'Factor'					:	1.0																						,	#?	parasitic tolerance to Coss
								'Qoss'						:	Qoss																					,	#?	equivalent charge of Coss
								'Eoss'						:	Eoss																					,	#?	equivalent energy of Coss
								'Config'					:	5																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
						},
                        	'Crss'					:	{																									#!	device Crss parameters
                                'C'							:	Crss_eff					 															,	#?	device parasitic reverse transfer capacitance
								'R'							:	0																						,	#?	Crss resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Crss inductance to reduce current slope
								'Crss_er'					:	Crss_er																					,	#?	energy-related Crss
								'Crss_tr'					:	Crss_tr																					,	#?	time-related Crss
								'Vvec'						:	Crss[0]																					,	#?	device Crss voltage vector
                                'Cvec'						:	Crss[1]																					,	#?	device Crss capacity vector
								'Qvec'						:	Qrss																					,	#?	device accumulated Crss charge vector
								'Offset'					:	0																						,	#?	parasitic offset to Crss
								'Factor'					:	1.0																						,	#?	parasitic tolerance to Crss
								'Qrss'						:	Qrss																					,	#?	equivalent charge of Crss
								'Erss'						:	Erss																					,	#?	equivalent energe of Crss
								'Config'					:	5																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
						},
							'Ciss'					:	{																									#!	device Ciss parameters
								'C'							:	Ciss_eff					 															,	#?	device parasitic input capacitance
								'R'							:	0																						,	#?	Ciss resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Ciss inductance to reduce current slope
								'Ciss_er'					:	Ciss_er																					,	#?	energy-related Ciss
								'Ciss_tr'					:	Ciss_tr																					,	#?	time-related Ciss
								'Vvec'						:	Ciss[0]																					,	#?	device Ciss voltage vector
								'Cvec'						:	Ciss[1]																					,	#?	device Ciss capacity vector
								'Offset'					:	0																						,	#?	parasitic offset to Ciss
								'Factor'					:	1.0																						,	#?	parasitic tolerance to Ciss
								'Qiss'						:	Qiss																					,	#?	equivalent charge of Ciss
								'Eiss'						:	Eiss																					,	#?	equivalent energy of Ciss
								'Config'					:	5																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Cds'					:	{																									#!	device Cds parameters
								'C'							:	Cds_eff					 																,	#?	device parasitic Cds capacitance
								'R'							:	0																						,	#?	Cds resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Cds inductance to reduce current slope
								'Cds_er'					:	Cds_er																					,	#?	energy-related Cds
								'Cds_tr'					:	Cds_tr																					,	#?	time-related Cds
								'Vvec'						:	Coss[0]																					,	#?	device Cds voltage vector
								'Cvec'						:	Cds																						,	#?	device Cds capacity vector
								'Offset_ON'					:	0																						,	#?	tuning offset for turn ON
								'Offset_OFF'				:	0																						,	#?	tuning offset for turn OFF
								'Factor_ON'					:	1.0																						,	#?	tuning factor for turn ON
								'Factor_OFF'				:	1.0																						,	#?	tuning factor for turn OFF
								'Config'					:	4																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Cgd'					:	{																									#!	device Cgd parameters
								'C'							:	Cgd_eff							 														,	#?	device parasitic Cgd capacitance
								'R'							:	0																						,	#?	Cgd resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Cgd inductance to reduce current slope
								'Cgd_er'					:	Cgd_er																					,	#?	energy-related Cgd
								'Cgd_tr'					:	Cgd_tr																					,	#?	time-related Cgd
								'Vvec'						:	Crss[0]																					,	#?	device Cgd voltage vector
								'Cvec'						:	Cgd																						,	#?	device Cgd capacity vector
								'Offset_ON'					:	0																						,	#?	tuning offset for turn ON
								'Offset_OFF'				:	0																						,	#?	tuning offset for turn OFF
								'Factor_ON'					:	1.0																						,	#?	tuning factor for turn ON
								'Factor_OFF'				:	1.0																						,	#?	tuning factor for turn OFF
								'Config'					:	4																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Cgs'					:	{																									#!	device Cgs parameters
								'C'							:	Cgs_eff					 																,	#?	device parasitic Cgs capacitance
								'R'							:	0																						,	#?	Cgs resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Cgs inductance to reduce current slope
								'Cgs_er'					:	Cgs_er																					,	#?	energy-related Cgs
								'Cgs_tr'					:	Cgs_tr																					,	#?	time-related Cgs
								'Vvec'						:	Ciss[0]																					,	#?	device Cgs voltage vector
								'Cvec'						:	Cgs																						,	#?	device Cgs capacity vector
								'Offset_ON'					:	0																						,	#?	tuning offset for turn ON
								'Offset_OFF'				:	0																						,	#?	tuning offset for turn OFF
								'Factor_ON'					:	1.0																						,	#?	tuning factor for turn ON
								'Factor_OFF'				:	1.0																						,	#?	tuning factor for turn OFF
								'Config'					:	4																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Eoff'					:	{																									#!	transistor turn-OFF energy losses
									'Ivec'					:	Ioff																					,	#?	turn-OFF energy current vector
                                    'Rgvec'					:	[0,100]																					,	#?	OFF path gate resistances vector
									'Tjvec'					:	[-55,175]																				,	#?	junction temperature vector
                                    'Vvec'					:	Voff																					,	#?	turn-OFF voltage vector
                                    'Evec'					:	Eoff																					,	#?	turn-OFF energy vectors
									'Evec_Temp'				:	Eoff_Temp																				,	#?	turn-OFF energy temp scaling vectors
                                    'CAT'					:	catOFF																					,	#?	octave Eoff energy syntax
									'CAT_Temp'				:	catOFF_Temp																				,	#?	octave Eoff energy temp scaling syntax
									'Vgs'					:	-1.3																					,	#?	used OFF path gate-source voltage
									'Vth'					:	3.0																						,	#?	used OFF path threshold voltage
									'Rg'					:	1																							#?	used OFF path gate resistance
						},
							'Eon'					:	{																									#!	transistor turn-ON energy losses
									'Ivec'					:	Ion																						,	#?	turn-ON energy current vector
									'Rgvec'					:	[0,100]																					,	#?	ON path gate resistances vector
									'Tjvec'					:	[-55,175]																				,	#?	junction temperature vector
                                    'Vvec'					:	Von																						,	#?	turn-ON voltage vector
                                    'Evec'					:	Eon																						,	#?	turn-ON energy vectors
									'Evec_Temp'				:	Eon_Temp																				,	#?	turn-ON energy temp scaling vectors
                                    'CAT'					:	catON																					,	#?	octave Eon energy syntax
									'CAT_Temp'				:	catON_Temp																				,	#?	octave Eon energy temp scaling syntax
									'Vgs'					:	11.3																					,	#?	used ON path gate-source voltage
									'Vth'					:	3.0																						,	#?	used ON path threshold voltage
									'Rg'					:	3.9																							#?	used ON path gate resistance
						},
							'Tau_deg'						:	100e-9																					,	#?	deglitch filter for currents and voltages
							'RCsnubber'						:	2																						,	#?	1->enable | 2->disable
						}

#?----------------------------------------------------------------------------------------------------------------------------------------------------------------------

Coss,Qoss,Eoss,Coss_tr,Coss_er		=	paramProcess.MOSFETcaps(switchesCossPath,'NVMJST004N08X','_Coss')
Crss,Qrss,Erss,Crss_tr,Crss_er 		=	paramProcess.MOSFETcaps(switchesCrssPath,'NVMJST004N08X','_Crss')
Ciss,Qiss,Eiss,Ciss_tr,Ciss_er 		=	paramProcess.MOSFETcaps(switchesCissPath,'NVMJST004N08X','_Ciss')
Coss_eff 							=	paramProcess.getCmos(Coss,Coss_tr,Coss_er,Coss[0][0],True)
Ciss_eff 							=	paramProcess.getCmos(Ciss,Ciss_tr,Ciss_er,Ciss[0][0],True)
Crss_eff 							=	paramProcess.getCmos(Crss,Crss_tr,Crss_er,Crss[0][0],True)
Cds 						        =	(np.array(Coss[1]) - np.array(Crss[1])).tolist()
Cgs						        	=	(np.array(Ciss[1]) - np.array(Crss[1])).tolist()
Cgd						        	=	Crss[1]
Cds_tr						        =	(np.array(Coss_tr) - np.array(Crss_tr)).tolist()
Cgs_tr						        =	(np.array(Ciss_tr) - np.array(Crss_tr)).tolist()
Cgd_tr						        =	Crss_tr
Cds_er						        =	(np.array(Coss_er) - np.array(Crss_er)).tolist()
Cgs_er						        =	(np.array(Ciss_er) - np.array(Crss_er)).tolist()
Cgd_er						        =	Crss_er
Cds_eff 							=	paramProcess.getCmos([Coss[0],Cds],Cds_tr,Cds_er,Coss[0][0],True)
Cgs_eff 							=	paramProcess.getCmos([Ciss[0],Cgs],Cgs_tr,Cgs_er,Ciss[0][0],True)
Cgd_eff 							=	Crss_eff
Rvec,Tvec							=	paramProcess.MOSFETrdson(switchesRdsonPath,'NVMJST004N08X','_Rdson')
Nvec,Ivec 							=	paramProcess.MOSFETrdson(switchesIdsonPath,'NVMJST004N08X','_Rdson')
Ioff,catOFF,Eoff					=	paramProcess.MOSFETenergies(switchesEoffPath,'NVMJST004N08X','_Eoff')
Voff,catOFF_Temp,Eoff_Temp			=	paramProcess.MOSFETenergies(switchesEoffPath,'NVMJST004N08X','_Eoff_Temp')
Ion,catON,Eon 						=	paramProcess.MOSFETenergies(switchesEonPath,'NVMJST004N08X','_Eon')
Von,catON_Temp,Eon_Temp				=	paramProcess.MOSFETenergies(switchesEonPath,'NVMJST004N08X','_Eon_Temp')
Vfvec,Ifvec,Rd,Vt					=	paramProcess.DiodeVI_data(bodyDiodeVIPath,'NVMJST004N08X')
Vds_vec,Ids_vec 					=	paramProcess.Forward_Transfer_data(switchesTransferPath,'NVMJST004N08X')

NVMJST004N08X		=	{																																	#*	NVMJST004N08X parameters
							'Config'						:	1																						,	#!	1->electric integrated | 2->electric separate | 3->thermal integrated | 4->thermal separate
							'Transistor'  			: 	{																									#!	transistors parameters
									'Config'				:	2																						,	#?	1->real model | 2->ideal model | 3->behavioral model
									'Thermal'           	:   ''                                  													,   #? 	selected transistor
									'Custom'            	:   []						               													,   #? 	transistor provided custom variables
									'g_fs'					:	1e6																						,	#?	forward transconductance
									'Rg'					:	1																						,	#?	internal gate resistance
									'Lg'					:	0																						,	#?	gate pin inductance
									'Rds_on'            	:   Rvec[-1][-1]*1e-3																		,   #? 	transistor ON resistance
									'Rds_off'				:	'inf'																					,	#?	transistor OFF resistance
									'Rvec'					:	(np.array(Rvec)*1e-3).tolist()														,	#?	absolute Rdson vector corresponding to junction temperature
									'Tvec'					:	Tvec 																					,	#?	junction temperature vector for Rdson
									'RTconfig'				:	1																						,	#?	choose which RT vector to be used
									'RdsonScale'			:	1.156																					,	#?	Rdson scaling to account for min, typ and max deviations
									'Nvec'					:	Nvec 																					,	#?	normalized Rdson vector corresponding to current
									'Ivec'					:	Ivec																					,	#?	current vector for normalized Rdson
									'NIconfig'				:	1																						,	#?	choose which NI vector to be used
									'IdsonScale'			:	1.0																						,	#?	Idson resistance scaling to account for min, typ and max deviations
									'Rsrc'					:	0																						,	#?	kelvin source pin resistance
									'Lsrc'					:	0																						,	#?	kelvin source pin inductance
									'Ls'					:	0																						,	#?	package source inductance
                                    'Ld'					:	0																						,	#?	package drain inductance
									'Rs'					:	0																						,	#?	package source resistance
									'Rd'					:	0																						,	#?	package drain inductance
									'Ksrc'					:	0																						,	#?	kelvin source option, 0->no kelvin | 1->kelvin
									'Vblock'            	:   80                               	 													,   #? 	transistor blocking voltage
									'Id'                	:   409                                 													,   #? 	transistor drain current
									'Tr'                	:   29e-9                                   												,   #? 	transistor rise time
									'Tf'                	:   37e-9                                       											, 	#? 	transistor fall time
									'Avalanche'		:	{																									#!	transistor avalanche parameters
										'Config'			:	2																						,	#?	1->enable | 2->disable
										'Voltage'			:	80																						,	#?	avalanche voltage
										'Resistance'		:	1e-3																						#?	avalanche resistance to break voltage state-dependency
									},
									'Transfer'		:	{																									#!	transistor forward transfer parameters
										'Vds'				:	Vds_vec																					,	#?	drain-source voltage vector
										'Vgs'				:	[0,20]																					,	#?	gate-source voltage vector
										'Ids'				:	Ids_vec																					,	#?	drain current vector
										'Factor_ON'			:	1.0																						,	#?	scaling factor for Ids at turn ON
										'Factor_OFF'		:	1.0																						,	#?	scaling factor for Ids at turn OFF
										'Factor_Vgs_ON'		:	1.0																						,	#?	scaling factor for Vgs at turn ON
										'Factor_Vgs_OFF'	:	1.0																						,	#?	scaling factor for Vgs at turn OFF
										'Vcoss'				:	0																						,	#?	initial voltage of the Coss
									},
						},
							'BodyDiode'  			:	{																									#!	body diodes paramteters
									'Config'				:	4																						,	#?	1->non-ideal RR | 2->non-ideal | 3->ideal RR | 4->ideal
									'Thermal'           	:   ''                                  													,   #? 	separate body diode
									'Custom'            	:   []					                 													,   #? 	body diode provided custrom variables
									'Rd_on'             	:   Rd[-1]																					,  	#? 	body diode ON resistance
									'Rd_off'				:	'inf'																					,	#?	body diode OFF resistance
									'Vf'					:	Vt[-1]																					,	#? 	body diode forward voltage
									'If'                	:   409                                 													,   #? 	body diode forward current
									'dIr'               	:   1e9		                                   												,   #? 	body diode current slope
									'Lrr'					:	1e-9																					,	#?	body diode reverse recovery inductance
									'Trr'               	:   21e-9                                													,   #? 	body diode reverse recovery time
									'Irr'               	:   0                                   													,   #? 	body diode reverse recovery current
									'Qrr'               	:   138e-9                                  												, 	#? 	body diode reverse recovery charge
									'Is'                  	:   27              																		, 	#? 	body diode reference current
									'Vs'					:	64																						,	#?	body diode reference voltage
                                    'VIcurve'		:	{																									#!	body diode VI characteristics
                                        'Vfvec'				:	Vfvec																					,	#?	forward voltage vector
                                        'Ifvec'				:	Ifvec																					,	#?	forward current vector
										'Rdvec'				:	Rd																						,	#?	dynamic resistance vector
										'Vtvec'				:	Vt																						,	#?	threshold voltage vector
                                        'Temps'				:	[-55,25,175]																			,	#?	temperature vector
                                        'Vfscale'			:	1.463																						#?	Vf scaling to account for min, typ and max deviations
									},
						},
							'GateDriver'			:	{																									#!	gate driver parameters
									'Config'				:	3																						,	#?	1->high-side | 2->low-side | 3->disable
									'Von'					:	12																						,	#?	ON driving voltage
									'Voff'					:	0																						,	#?	OFF driving voltage
									'Ron'					:	5																						,	#?	sourcing output resistance
									'Roff'					:	5																						,	#?	sinking output resistance
									'Lon'					:	0																						,	#?	sourcing output inductance
									'Loff'					:	0																						,	#?	sinking output inductance
									'Cload'					:	0																						,	#?	capacitive load on output
									'Rload'					:	'inf'																					,	#?	resistive load on output
									'Delay'					:	0																						,	#?	input-to-output total deadtime
									'Trise'					:	0																						,	#?	output rising time
									'Tfall'					:	0																						,	#?	output falling time
									'UVLO_Start'			:	7.0																						,	#?	UVLO startup voltage threshold
									'UVLO_Stop'				:	6.5																						,	#?	UVLO shutdown voltage threshold
									'UVLO_Delay'			:	100e-9																					,	#?	delay between UVLO startup and shutdown
									'Init_State'			:	0																						,	#?	initial toggling state, 0->OFF | 1->ON
									'CurrentLimit'	:	{																									#*	current limit of driver stage
										'Config'			:	2																						,	#?	1->enable | 2->disable
										'Ts'				: 	0 																						,	#?	sampling time between inductive & capacitive links
										'tau'				: 	0																						,	#?	first-order delay between inductive & capacitive links
                                    	'Rs'				: 	0																						,	#?	source impedance of inductive link
										'Cs'				:	1e-12																					,	#?	source capacitance of capacitive link
                                        'UpLim'				: 	10																						,	#?	max current limit on capacitive link
                                        'LoLim'				: 	-10																						,	#?	min current limit on capacitive link
                                        'Voffset'			: 	0																							#?	voltage offset between inductive & capacitive links
									},
									'Masking'		:	{																									#*	switching stages masking
										'ON'	:	{																										#	ON path masking
											'Config'		:	2																						,	#?	1->enable | 2->disable
											'HIGH'	:	{																									#!	HIGH mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[0, 0]																						#?	mask output
											},
											'LOW'	:	{																									#!	LOW mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[1, 1]																						#?	mask output
											}
										},
										'OFF'	:	{																										#	OFF path masking
											'Config'		:	2																						,	#?	1->enable | 2->disable
											'HIGH'	:	{																									#!	HIGH mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[0, 0]																						#?	mask output
											},
											'LOW'	:	{																									#!	LOW mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[1, 1]																						#?	mask output
											}
										}
									},
									'Boot'			:	{																									#*	bootstrap/charge pump parameters
										'Config'			:	1																						,	#?	1->bootstrap | 2->charge pump
										'Von'				:	14																						,	#?	boostrap driving voltage
										'Cboot'				:	4.7e-6																					,	#?	bootstrap capacitance
										'Vinit'				:	0																						,	#?	bootstrap capacitance initial voltage
										'Rboot'				:	10																						,	#?	bootstrap resistance
										'Vfboot'			:	0.87																					,	#?	bootstrap diode forward voltage
										'Rdboot'			:	1e-3																					,	#?	bootstrap diode ON-state resistance
										'Ichrg'				:	300e-6																					,	#?	charge pump supply current
										'Idis'				:	5e-6																					,	#?	charge pump loading or leakage current
										'Cpar'				:	0																						,	#?	charge pump parallel cap to break state/source dependency
									    'UVLO_Start'		:	11.6																					,	#?	threshold value to start the charge pump
										'UVLO_Stop'			:	12.4																						#?	threshold value to stop the charge pump
									},
							},
							'GateNetwork'			:	{																									#!	gate drive circuit parameters
									'Config'				:	2																						,	#?	1-> enable | 2->disable
									'ON_Path'		:	{																									#*	sourcing path parameters
										'Rg'				:	5																						,	#?	gate ON path resistance
										'Lg'				:	0																						,	#?	gate ON path inductance
										'Rload'				:	10e3																					,	#?	gate pull down resistance
										'Diode'	:	{																										#	reverse blocking diode parameters
											'Vf'			:	0																						,	#?	forward voltage
											'Rd_on'			:	0																						,	#?	ON-state resistance
										},
									},
									'OFF_Path'		:	{																									#*	sinking path parameters
										'Rg'				:	5																						,	#?	gate OFF path resistance
										'Lg'				:	0																						,	#?	gate OFF path inductance
										'Diode'	:	{																										#	reverse blocking diode parameters
											'Vf'			:	0																						,	#?	forward voltage
											'Rd_on'			:	0																						,	#?	ON-state resistance
										},
									},
									'NegVolt'		:	{																									#*	negative voltage generator parameters
										'Config'			:	2																						,	#?	1-> enable | 2->disable
										'Dz'	:	{																										#	zener diode parameters
											'Vf'			:	0.7																						,	#?	forward voltage
											'Rd_on'			:	1e-3																					,	#?	ON-state resistance
											'Vz'			:	2																						,	#?	Zener breakdown voltage
											'Rz'			:	1e-3																					,	#?	Zener resistance
										},
										'Dp'	:	{																										#	peak detector diode
											'Vf'			:	0.0																						,	#?	forward voltage
											'Rd_on'			:	0.0																						,	#?	ON-state resistance
										},
										'Cz'	:	{																										#	Zener capacitor parameters
											'Config'		:	1																						,	#?	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
											'Csingle'		:	1e-6																					,	#?	single capacitor value
											'Rsingle'		:	5e-3																					,	#?	ESR of single capacitor
											'Lsingle'		:	0																						,	#?	ESL of single capacitor
											'nPar'			:	1																						,	#?	number of parallel connections
											'nSer'			:	1																						,	#?	number of series connections
											'Vinit'			:	0																						,	#?	capacitor initial voltage
										},
										'Cp'	:	{																										#	peak detector capacitor parameters
											'Config'		:	1																						,	#?	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
											'Csingle'		:	2.2e-6																					,	#?	single capacitor value
											'Rsingle'		:	5e-3																					,	#?	ESR of single capacitor
											'Lsingle'		:	0																						,	#?	ESL of single capacitor
											'nPar'			:	1																						,	#?	number of parallel connections
											'nSer'			:	1																						,	#?	number of series connections
											'Vinit'			:	0																						,	#?	capacitor initial voltage
										},
										'Rp1'				:	43																						,	#?	current limiter of peak detector current
										'Rp2'				:	4.7e3																					,	#?	load resistor to charge the zener diode
									},
								},
							'nParallel'   					:	1                                       												,   #? 	number of parallel devices
							'Rth_jc'						:	[0.00352257,0.016627,0.0383147,0.160293,0.427985]										,	#?	junction-to-case thermal resistance
							'Cth_jc'						:	[0.000031294,0.000086371,0.00062568,0.0017269,0.0214]									,	#?	junction-to-case thermal capacitance
							'Rth_ca'              			:   [0]            																			,   #? 	case-to-ambient thermal resistance
							'Cth_ca'              			:   [0]             																		,   #? 	case-to-ambient thermal capacitance
							'Tinit'							:	0.0																						,	#?	initial juntion temperature
							'Pinit'							:	0.0																						,	#?	initial power dissipation
							'Coss'					: 	{																									#!	device Coss parameters
								'C'							:	Coss_eff					 															,	#?	device parasitic output capacitance
								'R'							:	0																						,	#?	Coss resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Coss inductance to reduce current slope
								'Coss_er'					:	Crss_er																					,	#?	energy-related Coss
								'Coss_tr'					:	Coss_tr																					,	#?	time-related Coss
								'Vvec'						:	Coss[0]																					,	#? 	device Coss voltage vector
								'Cvec'						:	Coss[1]																					,	#?	device Coss capacity vector
								'Offset'					:	0																						,	#?	parasitic offset to Coss
                                'Factor'					:	1.0																						,	#?	parasitic tolerance to Coss
								'Qoss'						:	Qoss																					,	#?	equivalent charge of Coss
								'Eoss'						:	Eoss																					,	#?	equivalent energy of Coss
								'Config'					:	5																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
						},
                        	'Crss'					:	{																									#!	device Crss parameters
                                'C'							:	Crss_eff					 															,	#?	device parasitic reverse transfer capacitance
								'R'							:	0																						,	#?	Crss resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Crss inductance to reduce current slope
								'Crss_er'					:	Crss_er																					,	#?	energy-related Crss
								'Crss_tr'					:	Crss_tr																					,	#?	time-related Crss
								'Vvec'						:	Crss[0]																					,	#?	device Crss voltage vector
                                'Cvec'						:	Crss[1]																					,	#?	device Crss capacity vector
								'Qvec'						:	Qrss																					,	#?	device accumulated Crss charge vector
								'Offset'					:	0																						,	#?	parasitic offset to Crss
								'Factor'					:	1.0																						,	#?	parasitic tolerance to Crss
								'Qrss'						:	Qrss																					,	#?	equivalent charge of Crss
								'Erss'						:	Erss																					,	#?	equivalent energe of Crss
								'Config'					:	5																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
						},
							'Ciss'					:	{																									#!	device Ciss parameters
								'C'							:	Ciss_eff					 															,	#?	device parasitic input capacitance
								'R'							:	0																						,	#?	Ciss resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Ciss inductance to reduce current slope
								'Ciss_er'					:	Ciss_er																					,	#?	energy-related Ciss
								'Ciss_tr'					:	Ciss_tr																					,	#?	time-related Ciss
								'Vvec'						:	Ciss[0]																					,	#?	device Ciss voltage vector
								'Cvec'						:	Ciss[1]																					,	#?	device Ciss capacity vector
								'Offset'					:	0																						,	#?	parasitic offset to Ciss
								'Factor'					:	1.0																						,	#?	parasitic tolerance to Ciss
								'Qiss'						:	Qiss																					,	#?	equivalent charge of Ciss
								'Eiss'						:	Eiss																					,	#?	equivalent energy of Ciss
								'Config'					:	5																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Cds'					:	{																									#!	device Cds parameters
								'C'							:	Cds_eff					 																,	#?	device parasitic Cds capacitance
								'R'							:	0																						,	#?	Cds resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Cds inductance to reduce current slope
								'Cds_er'					:	Cds_er																					,	#?	energy-related Cds
								'Cds_tr'					:	Cds_tr																					,	#?	time-related Cds
								'Vvec'						:	Coss[0]																					,	#?	device Cds voltage vector
								'Cvec'						:	Cds																						,	#?	device Cds capacity vector
								'Offset_ON'					:	0																						,	#?	tuning offset for turn ON
								'Offset_OFF'				:	0																						,	#?	tuning offset for turn OFF
								'Factor_ON'					:	1.0																						,	#?	tuning factor for turn ON
								'Factor_OFF'				:	1.0																						,	#?	tuning factor for turn OFF
								'Config'					:	4																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Cgd'					:	{																									#!	device Cgd parameters
								'C'							:	Cgd_eff							 														,	#?	device parasitic Cgd capacitance
								'R'							:	0																						,	#?	Cgd resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Cgd inductance to reduce current slope
								'Cgd_er'					:	Cgd_er																					,	#?	energy-related Cgd
								'Cgd_tr'					:	Cgd_tr																					,	#?	time-related Cgd
								'Vvec'						:	Crss[0]																					,	#?	device Cgd voltage vector
								'Cvec'						:	Cgd																						,	#?	device Cgd capacity vector
								'Offset_ON'					:	0																						,	#?	tuning offset for turn ON
								'Offset_OFF'				:	0																						,	#?	tuning offset for turn OFF
								'Factor_ON'					:	1.0																						,	#?	tuning factor for turn ON
								'Factor_OFF'				:	1.0																						,	#?	tuning factor for turn OFF
								'Config'					:	4																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Cgs'					:	{																									#!	device Cgs parameters
								'C'							:	Cgs_eff					 																,	#?	device parasitic Cgs capacitance
								'R'							:	0																						,	#?	Cgs resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Cgs inductance to reduce current slope
								'Cgs_er'					:	Cgs_er																					,	#?	energy-related Cgs
								'Cgs_tr'					:	Cgs_tr																					,	#?	time-related Cgs
								'Vvec'						:	Ciss[0]																					,	#?	device Cgs voltage vector
								'Cvec'						:	Cgs																						,	#?	device Cgs capacity vector
								'Offset_ON'					:	0																						,	#?	tuning offset for turn ON
								'Offset_OFF'				:	0																						,	#?	tuning offset for turn OFF
								'Factor_ON'					:	1.0																						,	#?	tuning factor for turn ON
								'Factor_OFF'				:	1.0																						,	#?	tuning factor for turn OFF
								'Config'					:	4																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Eoff'					:	{																									#!	transistor turn-OFF energy losses
									'Ivec'					:	Ioff																					,	#?	turn-OFF energy current vector
                                    'Rgvec'					:	[0,100]																					,	#?	OFF path gate resistances vector
									'Tjvec'					:	[-55,175]																				,	#?	junction temperature vector
                                    'Vvec'					:	Voff																					,	#?	turn-OFF voltage vector
                                    'Evec'					:	Eoff																					,	#?	turn-OFF energy vectors
									'Evec_Temp'				:	Eoff_Temp																				,	#?	turn-OFF energy temp scaling vectors
                                    'CAT'					:	catOFF																					,	#?	octave Eoff energy syntax
									'CAT_Temp'				:	catOFF_Temp																				,	#?	octave Eoff energy temp scaling syntax
									'Vgs'					:	0																						,	#?	used OFF path gate-source voltage
									'Vth'					:	1.5																						,	#?	used OFF path threshold voltage
									'Rg'					:	1																							#?	used OFF path gate resistance
						},
							'Eon'					:	{																									#!	transistor turn-ON energy losses
									'Ivec'					:	Ion																						,	#?	turn-ON energy current vector
									'Rgvec'					:	[0,100]																					,	#?	ON path gate resistances vector
									'Tjvec'					:	[-55,175]																				,	#?	junction temperature vector
                                    'Vvec'					:	Von																						,	#?	turn-ON voltage vector
                                    'Evec'					:	Eon																						,	#?	turn-ON energy vectors
									'Evec_Temp'				:	Eon_Temp																				,	#?	turn-ON energy temp scaling vectors
                                    'CAT'					:	catON																					,	#?	octave Eon energy syntax
									'CAT_Temp'				:	catON_Temp																				,	#?	octave Eon energy temp scaling syntax
									'Vgs'					:	12																						,	#?	used ON path gate-source voltage
									'Vth'					:	1.5																						,	#?	used ON path threshold voltage
									'Rg'					:	0																							#?	used ON path gate resistance
						},
							'Tau_deg'						:	100e-9																					,	#?	deglitch filter for currents and voltages
							'RCsnubber'						:	2																						,	#?	1->enable | 2->disable
						}

#?----------------------------------------------------------------------------------------------------------------------------------------------------------------------

Coss,Qoss,Eoss,Coss_tr,Coss_er		=	paramProcess.MOSFETcaps(switchesCossPath,'NVBLS1D5N10MC','_Coss')
Crss,Qrss,Erss,Crss_tr,Crss_er 		=	paramProcess.MOSFETcaps(switchesCrssPath,'NVBLS1D5N10MC','_Crss')
Ciss,Qiss,Eiss,Ciss_tr,Ciss_er 		=	paramProcess.MOSFETcaps(switchesCissPath,'NVBLS1D5N10MC','_Ciss')
Coss_eff 							=	paramProcess.getCmos(Coss,Coss_tr,Coss_er,Coss[0][0],True)
Ciss_eff 							=	paramProcess.getCmos(Ciss,Ciss_tr,Ciss_er,Ciss[0][0],True)
Crss_eff 							=	paramProcess.getCmos(Crss,Crss_tr,Crss_er,Crss[0][0],True)
Cds 						        =	(np.array(Coss[1]) - np.array(Crss[1])).tolist()
Cgs						        	=	(np.array(Ciss[1]) - np.array(Crss[1])).tolist()
Cgd						        	=	Crss[1]
Cds_tr						        =	(np.array(Coss_tr) - np.array(Crss_tr)).tolist()
Cgs_tr						        =	(np.array(Ciss_tr) - np.array(Crss_tr)).tolist()
Cgd_tr						        =	Crss_tr
Cds_er						        =	(np.array(Coss_er) - np.array(Crss_er)).tolist()
Cgs_er						        =	(np.array(Ciss_er) - np.array(Crss_er)).tolist()
Cgd_er						        =	Crss_er
Cds_eff 							=	paramProcess.getCmos([Coss[0],Cds],Cds_tr,Cds_er,Coss[0][0],True)
Cgs_eff 							=	paramProcess.getCmos([Ciss[0],Cgs],Cgs_tr,Cgs_er,Ciss[0][0],True)
Cgd_eff 							=	Crss_eff
Rvec,Tvec							=	paramProcess.MOSFETrdson(switchesRdsonPath,'NVBLS1D5N10MC','_Rdson')
Nvec,Ivec 							=	paramProcess.MOSFETrdson(switchesIdsonPath,'NVBLS1D5N10MC','_Rdson')
Ioff,catOFF,Eoff					=	paramProcess.MOSFETenergies(switchesEoffPath,'NVBLS1D5N10MC','_Eoff')
Voff,catOFF_Temp,Eoff_Temp			=	paramProcess.MOSFETenergies(switchesEoffPath,'NVBLS1D5N10MC','_Eoff_Temp')
Ion,catON,Eon 						=	paramProcess.MOSFETenergies(switchesEonPath,'NVBLS1D5N10MC','_Eon')
Von,catON_Temp,Eon_Temp				=	paramProcess.MOSFETenergies(switchesEonPath,'NVBLS1D5N10MC','_Eon_Temp')
Vfvec,Ifvec,Rd,Vt					=	paramProcess.DiodeVI_data(bodyDiodeVIPath,'NVBLS1D5N10MC')
Vds_vec,Ids_vec 					=	paramProcess.Forward_Transfer_data(switchesTransferPath,'NVBLS1D5N10MC')

NVBLS1D5N10MC		=	{																																	#*	NVBLS1D5N10MC parameters
							'Config'						:	1																						,	#!	1->electric integrated | 2->electric separate | 3->thermal integrated | 4->thermal separate
							'Transistor'  			: 	{																									#!	transistors parameters
									'Config'				:	2																						,	#?	1->real model | 2->ideal model | 3->behavioral model
									'Thermal'           	:   ''                                  													,   #? 	selected transistor
									'Custom'            	:   []						               													,   #? 	transistor provided custom variables
									'g_fs'					:	1e6																						,	#?	forward transconductance
									'Rg'					:	1																						,	#?	internal gate resistance
									'Lg'					:	0																						,	#?	gate pin inductance
									'Rds_on'            	:   Rvec[-1][-1]*1e-3																		,   #? 	transistor ON resistance
									'Rds_off'				:	'inf'																					,	#?	transistor OFF resistance
									'Rvec'					:	(np.array(Rvec)*1e-3).tolist()														,	#?	absolute Rdson vector corresponding to junction temperature
									'Tvec'					:	Tvec 																					,	#?	junction temperature vector for Rdson
									'RTconfig'				:	1																						,	#?	choose which RT vector to be used
									'RdsonScale'			:	1.0																						,	#?	Rdson scaling to account for min, typ and max deviations
									'Nvec'					:	Nvec 																					,	#?	normalized Rdson vector corresponding to current
									'Ivec'					:	Ivec																					,	#?	current vector for normalized Rdson
									'NIconfig'				:	1																						,	#?	choose which NI vector to be used
									'IdsonScale'			:	1.0																						,	#?	Idson resistance scaling to account for min, typ and max deviations
									'Rsrc'					:	0																						,	#?	kelvin source pin resistance
									'Lsrc'					:	0																						,	#?	kelvin source pin inductance
									'Ls'					:	0																						,	#?	package source inductance
                                    'Ld'					:	0																						,	#?	package drain inductance
									'Rs'					:	0																						,	#?	package source resistance
									'Rd'					:	0																						,	#?	package drain inductance
									'Ksrc'					:	0																						,	#?	kelvin source option, 0->no kelvin | 1->kelvin
									'Vblock'            	:   100                                	 													,   #? 	transistor blocking voltage
									'Id'                	:   300                                 													,   #? 	transistor drain current
									'Tr'                	:   0                                   													,   #? 	transistor rise time
									'Tf'                	:   0                                       												, 	#? 	transistor fall time
									'Avalanche'		:	{																									#!	transistor avalanche parameters
										'Config'			:	2																						,	#?	1->enable | 2->disable
										'Voltage'			:	100																						,	#?	avalanche voltage
										'Resistance'		:	1e-3																						#?	avalanche resistance to break voltage state-dependency
									},
									'Transfer'		:	{																									#!	transistor forward transfer parameters
										'Vds'				:	Vds_vec																					,	#?	drain-source voltage vector
										'Vgs'				:	list(np.arange(0.0,12.0+0.4,0.4))													,	#?	gate-source voltage vector
										'Ids'				:	Ids_vec																					,	#?	drain current vector
										'Factor_ON'			:	1.0																						,	#?	scaling factor for Ids at turn ON
										'Factor_OFF'		:	1.0																						,	#?	scaling factor for Ids at turn OFF
										'Factor_Vgs_ON'		:	1.0																						,	#?	scaling factor for Vgs at turn ON
										'Factor_Vgs_OFF'	:	1.0																						,	#?	scaling factor for Vgs at turn OFF
										'Vcoss'				:	0																						,	#?	initial voltage of the Coss
									},
						},
							'BodyDiode'  			:	{																									#!	body diodes paramteters
									'Config'				:	4																						,	#?	1->non-ideal RR | 2->non-ideal | 3->ideal RR | 4->ideal
									'Thermal'           	:   ''                                  													,   #? 	separate body diode
									'Custom'            	:   []					                 													,   #? 	body diode provided custrom variables
									'Rd_on'             	:   Rd[-1]													                              	,  	#? 	body diode ON resistance
									'Rd_off'				:	'inf'																					,	#?	body diode OFF resistance
									'Vf'					:	Vt[-1]																					,	#? 	body diode forward voltage
									'If'                	:   300                                 													,   #? 	body diode forward current
									'dIr'               	:   100e6                                   												,   #? 	body diode current slope
									'Lrr'					:	1e-9																					,	#?	body diode reverse recovery inductance
									'Trr'               	:   110e-9                                  												,   #? 	body diode reverse recovery time
									'Irr'               	:   0                                   													,   #? 	body diode reverse recovery current
									'Qrr'               	:   143e-9                                  											,	#? 	body diode reverse recovery charge
									'Is'                  	:   71              																		, 	#? 	body diode reference current
									'Vs'					:	50																						,	#?	body diode reference voltage
                                    'VIcurve'		:	{																									#!	body diode VI characteristics
                                        'Vfvec'				:	Vfvec																					,	#?	forward voltage vector
                                        'Ifvec'				:	Ifvec																					,	#?	forward current vector
										'Rdvec'				:	Rd																						,	#?	dynamic resistance vector
										'Vtvec'				:	Vt																						,	#?	threshold voltage vector
                                        'Temps'				:	[-55,25,175]																			,	#?	temperature vector
                                        'Vfscale'			:	1.625																						#?	Vf scaling to account for min, typ and max deviations
									},
						},
							'GateDriver'			:	{																									#!	gate driver parameters
									'Config'				:	3																						,	#?	1->high-side | 2->low-side | 3->disable
									'Von'					:	12																						,	#?	ON driving voltage
									'Voff'					:	0																						,	#?	OFF driving voltage
									'Ron'					:	5																						,	#?	sourcing output resistance
									'Roff'					:	5																						,	#?	sinking output resistance
									'Lon'					:	0																						,	#?	sourcing output inductance
									'Loff'					:	0																						,	#?	sinking output inductance
									'Cload'					:	0																						,	#?	capacitive load on output
									'Rload'					:	'inf'																					,	#?	resistive load on output
									'Delay'					:	0																						,	#?	input-to-output total deadtime
									'Trise'					:	0																						,	#?	output rising time
									'Tfall'					:	0																						,	#?	output falling time
									'UVLO_Start'			:	7.0																						,	#?	UVLO startup voltage threshold
									'UVLO_Stop'				:	6.5																						,	#?	UVLO shutdown voltage threshold
									'UVLO_Delay'			:	100e-9																					,	#?	delay between UVLO startup and shutdown
									'Init_State'			:	0																						,	#?	initial toggling state, 0->OFF | 1->ON
									'CurrentLimit'	:	{																									#*	current limit of driver stage
										'Config'			:	2																						,	#?	1->enable | 2->disable
										'Ts'				: 	0 																						,	#?	sampling time between inductive & capacitive links
										'tau'				: 	0																						,	#?	first-order delay between inductive & capacitive links
                                    	'Rs'				: 	0																						,	#?	source impedance of inductive link
										'Cs'				:	1e-12																					,	#?	source capacitance of capacitive link
                                        'UpLim'				: 	10																						,	#?	max current limit on capacitive link
                                        'LoLim'				: 	-10																						,	#?	min current limit on capacitive link
                                        'Voffset'			: 	0																							#?	voltage offset between inductive & capacitive links
									},
									'Masking'		:	{																									#*	switching stages masking
										'ON'	:	{																										#	ON path masking
											'Config'		:	2																						,	#?	1->enable | 2->disable
											'HIGH'	:	{																									#!	HIGH mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[0, 0]																						#?	mask output
											},
											'LOW'	:	{																									#!	LOW mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[1, 1]																						#?	mask output
											}
										},
										'OFF'	:	{																										#	OFF path masking
											'Config'		:	2																						,	#?	1->enable | 2->disable
											'HIGH'	:	{																									#!	HIGH mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[0, 0]																						#?	mask output
											},
											'LOW'	:	{																									#!	LOW mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[1, 1]																						#?	mask output
											}
										}
									},
									'Boot'			:	{																									#*	bootstrap/charge pump parameters
										'Config'			:	1																						,	#?	1->bootstrap | 2->charge pump
										'Von'				:	14																						,	#?	boostrap driving voltage
										'Cboot'				:	4.7e-6																					,	#?	bootstrap capacitance
										'Vinit'				:	0																						,	#?	bootstrap capacitance initial voltage
										'Rboot'				:	10																						,	#?	bootstrap resistance
										'Vfboot'			:	0.87																					,	#?	bootstrap diode forward voltage
										'Rdboot'			:	1e-3																					,	#?	bootstrap diode ON-state resistance
										'Ichrg'				:	300e-6																					,	#?	charge pump supply current
										'Idis'				:	5e-6																					,	#?	charge pump loading or leakage current
										'Cpar'				:	0																						,	#?	charge pump parallel cap to break state/source dependency
									    'UVLO_Start'		:	11.6																					,	#?	threshold value to start the charge pump
										'UVLO_Stop'			:	12.4																						#?	threshold value to stop the charge pump
									},
							},
							'GateNetwork'			:	{																									#!	gate drive circuit parameters
									'Config'				:	2																						,	#?	1-> enable | 2->disable
									'ON_Path'		:	{																									#*	sourcing path parameters
										'Rg'				:	5																						,	#?	gate ON path resistance
										'Lg'				:	0																						,	#?	gate ON path inductance
										'Rload'				:	10e3																					,	#?	gate pull down resistance
										'Diode'	:	{																										#	reverse blocking diode parameters
											'Vf'			:	0																						,	#?	forward voltage
											'Rd_on'			:	0																						,	#?	ON-state resistance
										},
									},
									'OFF_Path'		:	{																									#*	sinking path parameters
										'Rg'				:	5																						,	#?	gate OFF path resistance
										'Lg'				:	0																						,	#?	gate OFF path inductance
										'Diode'	:	{																										#	reverse blocking diode parameters
											'Vf'			:	0																						,	#?	forward voltage
											'Rd_on'			:	0																						,	#?	ON-state resistance
										},
									},
									'NegVolt'		:	{																									#*	negative voltage generator parameters
										'Config'			:	2																						,	#?	1-> enable | 2->disable
										'Dz'	:	{																										#	zener diode parameters
											'Vf'			:	0.7																						,	#?	forward voltage
											'Rd_on'			:	1e-3																					,	#?	ON-state resistance
											'Vz'			:	2																						,	#?	Zener breakdown voltage
											'Rz'			:	1e-3																					,	#?	Zener resistance
										},
										'Dp'	:	{																										#	peak detector diode
											'Vf'			:	0.0																						,	#?	forward voltage
											'Rd_on'			:	0.0																						,	#?	ON-state resistance
										},
										'Cz'	:	{																										#	Zener capacitor parameters
											'Config'		:	1																						,	#?	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
											'Csingle'		:	1e-6																					,	#?	single capacitor value
											'Rsingle'		:	5e-3																					,	#?	ESR of single capacitor
											'Lsingle'		:	0																						,	#?	ESL of single capacitor
											'nPar'			:	1																						,	#?	number of parallel connections
											'nSer'			:	1																						,	#?	number of series connections
											'Vinit'			:	0																						,	#?	capacitor initial voltage
										},
										'Cp'	:	{																										#	peak detector capacitor parameters
											'Config'		:	1																						,	#?	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
											'Csingle'		:	2.2e-6																					,	#?	single capacitor value
											'Rsingle'		:	5e-3																					,	#?	ESR of single capacitor
											'Lsingle'		:	0																						,	#?	ESL of single capacitor
											'nPar'			:	1																						,	#?	number of parallel connections
											'nSer'			:	1																						,	#?	number of series connections
											'Vinit'			:	0																						,	#?	capacitor initial voltage
										},
										'Rp1'				:	43																						,	#?	current limiter of peak detector current
										'Rp2'				:	4.7e3																					,	#?	load resistor to charge the zener diode
									},
								},
							'nParallel'   					:	1                                       												,   #? 	number of parallel devices
							'Rth_jc'						:	0.45																					,	#?	junction-to-case thermal resistance
							'Cth_jc'						:	0.00																					,	#?	junction-to-case thermal capacitance
							'Rth_ca'              			:   [0.292,0.258,0.856,0.228,0.3]            												,   #? 	case-to-ambient thermal resistance
							'Cth_ca'              			:   [0.788,0.205,15.91,3.716,0.015]             											,   #? 	case-to-ambient thermal capacitance
							'Tinit'							:	0.0																						,	#?	initial juntion temperature
							'Pinit'							:	0.0																						,	#?	initial power dissipation
							'Coss'					: 	{																									#!	device Coss parameters
								'C'							:	Coss_eff					 															,	#?	device parasitic output capacitance
								'R'							:	0																						,	#?	Coss resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Coss inductance to reduce current slope
								'Coss_er'					:	Crss_er																					,	#?	energy-related Coss
								'Coss_tr'					:	Coss_tr																					,	#?	time-related Coss
								'Vvec'						:	Coss[0]																					,	#? 	device Coss voltage vector
								'Cvec'						:	Coss[1]																					,	#?	device Coss capacity vector
								'Offset'					:	0																						,	#?	parasitic offset to Coss
                                'Factor'					:	1.0																						,	#?	parasitic tolerance to Coss
								'Qoss'						:	Qoss																					,	#?	equivalent charge of Coss
								'Eoss'						:	Eoss																					,	#?	equivalent energy of Coss
								'Config'					:	5																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
						},
                        	'Crss'					:	{																									#!	device Crss parameters
                                'C'							:	Crss_eff					 															,	#?	device parasitic reverse transfer capacitance
								'R'							:	0																						,	#?	Crss resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Crss inductance to reduce current slope
								'Crss_er'					:	Crss_er																					,	#?	energy-related Crss
								'Crss_tr'					:	Crss_tr																					,	#?	time-related Crss
								'Vvec'						:	Crss[0]																					,	#?	device Crss voltage vector
                                'Cvec'						:	Crss[1]																					,	#?	device Crss capacity vector
								'Qvec'						:	Qrss																					,	#?	device accumulated Crss charge vector
								'Offset'					:	0																						,	#?	parasitic offset to Crss
								'Factor'					:	1.0																						,	#?	parasitic tolerance to Crss
								'Qrss'						:	Qrss																					,	#?	equivalent charge of Crss
								'Erss'						:	Erss																					,	#?	equivalent energe of Crss
								'Config'					:	5																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
						},
							'Ciss'					:	{																									#!	device Ciss parameters
								'C'							:	Ciss_eff					 															,	#?	device parasitic input capacitance
								'R'							:	0																						,	#?	Ciss resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Ciss inductance to reduce current slope
								'Ciss_er'					:	Ciss_er																					,	#?	energy-related Ciss
								'Ciss_tr'					:	Ciss_tr																					,	#?	time-related Ciss
								'Vvec'						:	Ciss[0]																					,	#?	device Ciss voltage vector
								'Cvec'						:	Ciss[1]																					,	#?	device Ciss capacity vector
								'Offset'					:	0																						,	#?	parasitic offset to Ciss
								'Factor'					:	1.0																						,	#?	parasitic tolerance to Ciss
								'Qiss'						:	Qiss																					,	#?	equivalent charge of Ciss
								'Eiss'						:	Eiss																					,	#?	equivalent energy of Ciss
								'Config'					:	5																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Cds'					:	{																									#!	device Cds parameters
								'C'							:	Cds_eff					 																,	#?	device parasitic Cds capacitance
								'R'							:	0																						,	#?	Cds resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Cds inductance to reduce current slope
								'Cds_er'					:	Cds_er																					,	#?	energy-related Cds
								'Cds_tr'					:	Cds_tr																					,	#?	time-related Cds
								'Vvec'						:	Coss[0]																					,	#?	device Cds voltage vector
								'Cvec'						:	Cds																						,	#?	device Cds capacity vector
								'Offset_ON'					:	0																						,	#?	tuning offset for turn ON
								'Offset_OFF'				:	0																						,	#?	tuning offset for turn OFF
								'Factor_ON'					:	1.0																						,	#?	tuning factor for turn ON
								'Factor_OFF'				:	1.0																						,	#?	tuning factor for turn OFF
								'Config'					:	4																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Cgd'					:	{																									#!	device Cgd parameters
								'C'							:	Cgd_eff							 														,	#?	device parasitic Cgd capacitance
								'R'							:	0																						,	#?	Cgd resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Cgd inductance to reduce current slope
								'Cgd_er'					:	Cgd_er																					,	#?	energy-related Cgd
								'Cgd_tr'					:	Cgd_tr																					,	#?	time-related Cgd
								'Vvec'						:	Crss[0]																					,	#?	device Cgd voltage vector
								'Cvec'						:	Cgd																						,	#?	device Cgd capacity vector
								'Offset_ON'					:	0																						,	#?	tuning offset for turn ON
								'Offset_OFF'				:	0																						,	#?	tuning offset for turn OFF
								'Factor_ON'					:	1.0																						,	#?	tuning factor for turn ON
								'Factor_OFF'				:	1.0																						,	#?	tuning factor for turn OFF
								'Config'					:	4																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Cgs'					:	{																									#!	device Cgs parameters
								'C'							:	Cgs_eff					 																,	#?	device parasitic Cgs capacitance
								'R'							:	0																						,	#?	Cgs resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Cgs inductance to reduce current slope
								'Cgs_er'					:	Cgs_er																					,	#?	energy-related Cgs
								'Cgs_tr'					:	Cgs_tr																					,	#?	time-related Cgs
								'Vvec'						:	Ciss[0]																					,	#?	device Cgs voltage vector
								'Cvec'						:	Cgs																						,	#?	device Cgs capacity vector
								'Offset_ON'					:	0																						,	#?	tuning offset for turn ON
								'Offset_OFF'				:	0																						,	#?	tuning offset for turn OFF
								'Factor_ON'					:	1.0																						,	#?	tuning factor for turn ON
								'Factor_OFF'				:	1.0																						,	#?	tuning factor for turn OFF
								'Config'					:	4																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Eoff'					:	{																									#!	transistor turn-OFF energy losses
									'Ivec'					:	Ioff																					,	#?	turn-OFF energy current vector
									'Rgvec'					:	[0,100]																					,	#?	OFF path gate resistances vector
									'Tjvec'					:	[-55,175]																				,	#?	junction temperature vector
                                    'Vvec'					:	Voff																					,	#?	turn-OFF voltage vector
                                    'Evec'					:	Eoff																					,	#?	turn-OFF energy vectors
									'Evec_Temp'				:	Eoff_Temp																				,	#?	turn-OFF energy temp scaling vectors
                                    'CAT'					:	catOFF																					,	#?	octave Eoff energy syntax
									'CAT_Temp'				:	catOFF_Temp																				,	#?	octave Eoff energy temp scaling syntax
									'Vgs'					:	0																						,	#?	used OFF path gate-source voltage
									'Vth'					:	1.5																						,	#?	used OFF path threshold voltage
									'Rg'					:	0																							#?	used OFF path gate resistance
						},
							'Eon'					:	{																									#!	transistor turn-ON energy losses
									'Ivec'					:	Ion																						,	#?	turn-ON energy current vector
									'Rgvec'					:	[0,100]																					,	#?	ON path gate resistances vector
									'Tjvec'					:	[-55,175]																				,	#?	junction temperature vector
                                    'Vvec'					:	Von																						,	#?	turn-ON voltage vector
                                    'Evec'					:	Eon																						,	#?	turn-ON energy vectors
									'Evec_Temp'				:	Eon_Temp																				,	#?	turn-ON energy temp scaling vectors
                                    'CAT'					:	catON																					,	#?	octave Eon energy syntax
									'CAT_Temp'				:	catON_Temp																				,	#?	octave Eon energy temp scaling syntax
									'Vgs'					:	12																						,	#?	used ON path gate-source voltage
									'Vth'					:	1.5																						,	#?	used ON path threshold voltage
									'Rg'					:	0																							#?	used ON path gate resistance
						},
							'Tau_deg'						:	100e-9																					,	#?	deglitch filter for currents and voltages
							'RCsnubber'						:	2																						,	#?	1->enable | 2->disable
						}

#?----------------------------------------------------------------------------------------------------------------------------------------------------------------------

Coss,Qoss,Eoss,Coss_tr,Coss_er		=	paramProcess.MOSFETcaps(switchesCossPath,'NVBLS1D7N10MC','_Coss')
Crss,Qrss,Erss,Crss_tr,Crss_er 		=	paramProcess.MOSFETcaps(switchesCrssPath,'NVBLS1D7N10MC','_Crss')
Ciss,Qiss,Eiss,Ciss_tr,Ciss_er 		=	paramProcess.MOSFETcaps(switchesCissPath,'NVBLS1D7N10MC','_Ciss')
Coss_eff 							=	paramProcess.getCmos(Coss,Coss_tr,Coss_er,Coss[0][0],True)
Ciss_eff 							=	paramProcess.getCmos(Ciss,Ciss_tr,Ciss_er,Ciss[0][0],True)
Crss_eff 							=	paramProcess.getCmos(Crss,Crss_tr,Crss_er,Crss[0][0],True)
Cds 						        =	(np.array(Coss[1]) - np.array(Crss[1])).tolist()
Cgs						        	=	(np.array(Ciss[1]) - np.array(Crss[1])).tolist()
Cgd						        	=	Crss[1]
Cds_tr						        =	(np.array(Coss_tr) - np.array(Crss_tr)).tolist()
Cgs_tr						        =	(np.array(Ciss_tr) - np.array(Crss_tr)).tolist()
Cgd_tr						        =	Crss_tr
Cds_er						        =	(np.array(Coss_er) - np.array(Crss_er)).tolist()
Cgs_er						        =	(np.array(Ciss_er) - np.array(Crss_er)).tolist()
Cgd_er						        =	Crss_er
Cds_eff 							=	paramProcess.getCmos([Coss[0],Cds],Cds_tr,Cds_er,Coss[0][0],True)
Cgs_eff 							=	paramProcess.getCmos([Ciss[0],Cgs],Cgs_tr,Cgs_er,Ciss[0][0],True)
Cgd_eff 							=	Crss_eff
Rvec,Tvec							=	paramProcess.MOSFETrdson(switchesRdsonPath,'NVBLS1D7N10MC','_Rdson')
Nvec,Ivec 							=	paramProcess.MOSFETrdson(switchesIdsonPath,'NVBLS1D7N10MC','_Rdson')
Ioff,catOFF,Eoff					=	paramProcess.MOSFETenergies(switchesEoffPath,'NVBLS1D7N10MC','_Eoff')
Voff,catOFF_Temp,Eoff_Temp			=	paramProcess.MOSFETenergies(switchesEoffPath,'NVBLS1D7N10MC','_Eoff_Temp')
Ion,catON,Eon 						=	paramProcess.MOSFETenergies(switchesEonPath,'NVBLS1D7N10MC','_Eon')
Von,catON_Temp,Eon_Temp				=	paramProcess.MOSFETenergies(switchesEonPath,'NVBLS1D7N10MC','_Eon_Temp')
Vfvec,Ifvec,Rd,Vt					=	paramProcess.DiodeVI_data(bodyDiodeVIPath,'NVBLS1D7N10MC')
Vds_vec,Ids_vec 					=	paramProcess.Forward_Transfer_data(switchesTransferPath,'NVBLS1D7N10MC')

NVBLS1D7N10MC		=	{																																	#*	NVBLS1D7N10MC parameters
							'Config'						:	1																						,	#!	1->electric integrated | 2->electric separate | 3->thermal integrated | 4->thermal separate
							'Transistor'  			: 	{																									#!	transistors parameters
									'Config'				:	2																						,	#?	1->real model | 2->ideal model | 3->behavioral model
									'Thermal'           	:   ''                                  													,   #? 	selected transistor
									'Custom'            	:   []						               													,   #? 	transistor provided custom variables
									'g_fs'					:	1e6																						,	#?	forward transconductance
									'Rg'					:	1																						,	#?	internal gate resistance
									'Lg'					:	0																						,	#?	gate pin inductance
									'Rds_on'            	:   Rvec[-1][-1]*1e-3																		,   #? 	transistor ON resistance
									'Rds_off'				:	'inf'																					,	#?	transistor OFF resistance
									'Rvec'					:	(np.array(Rvec)*1e-3).tolist()														,	#?	absolute Rdson vector corresponding to junction temperature
									'Tvec'					:	Tvec 																					,	#?	junction temperature vector for Rdson
									'RTconfig'				:	1																						,	#?	choose which RT vector to be used
									'RdsonScale'			:	1.0																						,	#?	Rdson scaling to account for min, typ and max deviations
									'Nvec'					:	Nvec 																					,	#?	normalized Rdson vector corresponding to current
									'Ivec'					:	Ivec																					,	#?	current vector for normalized Rdson
									'NIconfig'				:	1																						,	#?	choose which NI vector to be used
									'IdsonScale'			:	1.0																						,	#?	Idson resistance scaling to account for min, typ and max deviations
									'Rsrc'					:	0																						,	#?	kelvin source pin resistance
									'Lsrc'					:	0																						,	#?	kelvin source pin inductance
									'Ls'					:	0																						,	#?	package source inductance
                                    'Ld'					:	0																						,	#?	package drain inductance
									'Rs'					:	0																						,	#?	package source resistance
									'Rd'					:	0																						,	#?	package drain inductance
									'Ksrc'					:	0																						,	#?	kelvin source option, 0->no kelvin | 1->kelvin
									'Vblock'            	:   100                                	 													,   #? 	transistor blocking voltage
									'Id'                	:   300                                 													,   #? 	transistor drain current
									'Tr'                	:   0                                   													,   #? 	transistor rise time
									'Tf'                	:   0                                       												, 	#? 	transistor fall time
									'Avalanche'		:	{																									#!	transistor avalanche parameters
										'Config'			:	2																						,	#?	1->enable | 2->disable
										'Voltage'			:	100																						,	#?	avalanche voltage
										'Resistance'		:	1e-3																						#?	avalanche resistance to break voltage state-dependency
									},
									'Transfer'		:	{																									#!	transistor forward transfer parameters
										'Vds'				:	Vds_vec																					,	#?	drain-source voltage vector
										'Vgs'				:	list(np.arange(0.0,12.0+0.4,0.4))													,	#?	gate-source voltage vector
										'Ids'				:	Ids_vec																					,	#?	drain current vector
										'Factor_ON'			:	1.0																						,	#?	scaling factor for Ids at turn ON
										'Factor_OFF'		:	1.0																						,	#?	scaling factor for Ids at turn OFF
										'Factor_Vgs_ON'		:	1.0																						,	#?	scaling factor for Vgs at turn ON
										'Factor_Vgs_OFF'	:	1.0																						,	#?	scaling factor for Vgs at turn OFF
										'Vcoss'				:	0																						,	#?	initial voltage of the Coss
									},
						},
							'BodyDiode'  			:	{																									#!	body diodes paramteters
									'Config'				:	4																						,	#?	1->non-ideal RR | 2->non-ideal | 3->ideal RR | 4->ideal
									'Thermal'           	:   ''                                  													,   #? 	separate body diode
									'Custom'            	:   []					                 													,   #? 	body diode provided custrom variables
									'Rd_on'             	:   Rd[-1]													                              	,  	#? 	body diode ON resistance
									'Rd_off'				:	'inf'																					,	#?	body diode OFF resistance
									'Vf'					:	Vt[-1]																					,	#? 	body diode forward voltage
									'If'                	:   300                                 													,   #? 	body diode forward current
									'dIr'               	:   100e6                                   												,   #? 	body diode current slope
									'Lrr'					:	1e-9																					,	#?	body diode reverse recovery inductance
									'Trr'               	:   110e-9                                  												,   #? 	body diode reverse recovery time
									'Irr'               	:   0                                   													,   #? 	body diode reverse recovery current
									'Qrr'               	:   143e-9                                  												,	#? 	body diode reverse recovery charge
									'Is'                  	:   62              																		, 	#? 	body diode reference current
									'Vs'					:	50																						,	#?	body diode reference voltage
                                    'VIcurve'		:	{																									#!	body diode VI characteristics
                                        'Vfvec'				:	Vfvec																					,	#?	forward voltage vector
                                        'Ifvec'				:	Ifvec																					,	#?	forward current vector
										'Rdvec'				:	Rd																						,	#?	dynamic resistance vector
										'Vtvec'				:	Vt																						,	#?	threshold voltage vector
                                        'Temps'				:	[-55,25,175]																			,	#?	temperature vector
                                        'Vfscale'			:	1.585																						#?	Vf scaling to account for min, typ and max deviations
									},
						},
							'GateDriver'			:	{																									#!	gate driver parameters
									'Config'				:	3																						,	#?	1->high-side | 2->low-side | 3->disable
									'Von'					:	12																						,	#?	ON driving voltage
									'Voff'					:	0																						,	#?	OFF driving voltage
									'Ron'					:	5																						,	#?	sourcing output resistance
									'Roff'					:	5																						,	#?	sinking output resistance
									'Lon'					:	0																						,	#?	sourcing output inductance
									'Loff'					:	0																						,	#?	sinking output inductance
									'Cload'					:	0																						,	#?	capacitive load on output
									'Rload'					:	'inf'																					,	#?	resistive load on output
									'Delay'					:	0																						,	#?	input-to-output total deadtime
									'Trise'					:	0																						,	#?	output rising time
									'Tfall'					:	0																						,	#?	output falling time
									'UVLO_Start'			:	7.0																						,	#?	UVLO startup voltage threshold
									'UVLO_Stop'				:	6.5																						,	#?	UVLO shutdown voltage threshold
									'UVLO_Delay'			:	100e-9																					,	#?	delay between UVLO startup and shutdown
									'Init_State'			:	0																						,	#?	initial toggling state, 0->OFF | 1->ON
									'CurrentLimit'	:	{																									#*	current limit of driver stage
										'Config'			:	2																						,	#?	1->enable | 2->disable
										'Ts'				: 	0 																						,	#?	sampling time between inductive & capacitive links
										'tau'				: 	0																						,	#?	first-order delay between inductive & capacitive links
                                    	'Rs'				: 	0																						,	#?	source impedance of inductive link
										'Cs'				:	1e-12																					,	#?	source capacitance of capacitive link
                                        'UpLim'				: 	10																						,	#?	max current limit on capacitive link
                                        'LoLim'				: 	-10																						,	#?	min current limit on capacitive link
                                        'Voffset'			: 	0																							#?	voltage offset between inductive & capacitive links
									},
									'Masking'		:	{																									#*	switching stages masking
										'ON'	:	{																										#	ON path masking
											'Config'		:	2																						,	#?	1->enable | 2->disable
											'HIGH'	:	{																									#!	HIGH mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[0, 0]																						#?	mask output
											},
											'LOW'	:	{																									#!	LOW mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[1, 1]																						#?	mask output
											}
										},
										'OFF'	:	{																										#	OFF path masking
											'Config'		:	2																						,	#?	1->enable | 2->disable
											'HIGH'	:	{																									#!	HIGH mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[0, 0]																						#?	mask output
											},
											'LOW'	:	{																									#!	LOW mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[1, 1]																						#?	mask output
											}
										}
									},
									'Boot'			:	{																									#*	bootstrap/charge pump parameters
										'Config'			:	1																						,	#?	1->bootstrap | 2->charge pump
										'Von'				:	14																						,	#?	boostrap driving voltage
										'Cboot'				:	4.7e-6																					,	#?	bootstrap capacitance
										'Vinit'				:	0																						,	#?	bootstrap capacitance initial voltage
										'Rboot'				:	10																						,	#?	bootstrap resistance
										'Vfboot'			:	0.87																					,	#?	bootstrap diode forward voltage
										'Rdboot'			:	1e-3																					,	#?	bootstrap diode ON-state resistance
										'Ichrg'				:	300e-6																					,	#?	charge pump supply current
										'Idis'				:	5e-6																					,	#?	charge pump loading or leakage current
										'Cpar'				:	0																						,	#?	charge pump parallel cap to break state/source dependency
									    'UVLO_Start'		:	11.6																					,	#?	threshold value to start the charge pump
										'UVLO_Stop'			:	12.4																						#?	threshold value to stop the charge pump
									},
							},
							'GateNetwork'			:	{																									#!	gate drive circuit parameters
									'Config'				:	2																						,	#?	1-> enable | 2->disable
									'ON_Path'		:	{																									#*	sourcing path parameters
										'Rg'				:	5																						,	#?	gate ON path resistance
										'Lg'				:	0																						,	#?	gate ON path inductance
										'Rload'				:	10e3																					,	#?	gate pull down resistance
										'Diode'	:	{																										#	reverse blocking diode parameters
											'Vf'			:	0																						,	#?	forward voltage
											'Rd_on'			:	0																						,	#?	ON-state resistance
										},
									},
									'OFF_Path'		:	{																									#*	sinking path parameters
										'Rg'				:	5																						,	#?	gate OFF path resistance
										'Lg'				:	0																						,	#?	gate OFF path inductance
										'Diode'	:	{																										#	reverse blocking diode parameters
											'Vf'			:	0																						,	#?	forward voltage
											'Rd_on'			:	0																						,	#?	ON-state resistance
										},
									},
									'NegVolt'		:	{																									#*	negative voltage generator parameters
										'Config'			:	2																						,	#?	1-> enable | 2->disable
										'Dz'	:	{																										#	zener diode parameters
											'Vf'			:	0.7																						,	#?	forward voltage
											'Rd_on'			:	1e-3																					,	#?	ON-state resistance
											'Vz'			:	2																						,	#?	Zener breakdown voltage
											'Rz'			:	1e-3																					,	#?	Zener resistance
										},
										'Dp'	:	{																										#	peak detector diode
											'Vf'			:	0.0																						,	#?	forward voltage
											'Rd_on'			:	0.0																						,	#?	ON-state resistance
										},
										'Cz'	:	{																										#	Zener capacitor parameters
											'Config'		:	1																						,	#?	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
											'Csingle'		:	1e-6																					,	#?	single capacitor value
											'Rsingle'		:	5e-3																					,	#?	ESR of single capacitor
											'Lsingle'		:	0																						,	#?	ESL of single capacitor
											'nPar'			:	1																						,	#?	number of parallel connections
											'nSer'			:	1																						,	#?	number of series connections
											'Vinit'			:	0																						,	#?	capacitor initial voltage
										},
										'Cp'	:	{																										#	peak detector capacitor parameters
											'Config'		:	1																						,	#?	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
											'Csingle'		:	2.2e-6																					,	#?	single capacitor value
											'Rsingle'		:	5e-3																					,	#?	ESR of single capacitor
											'Lsingle'		:	0																						,	#?	ESL of single capacitor
											'nPar'			:	1																						,	#?	number of parallel connections
											'nSer'			:	1																						,	#?	number of series connections
											'Vinit'			:	0																						,	#?	capacitor initial voltage
										},
										'Rp1'				:	43																						,	#?	current limiter of peak detector current
										'Rp2'				:	4.7e3																					,	#?	load resistor to charge the zener diode
									},
								},
							'nParallel'   					:	1                                       												,   #? 	number of parallel devices
							'Rth_jc'						:	0.49																					,	#?	junction-to-case thermal resistance
							'Cth_jc'						:	0.00																					,	#?	junction-to-case thermal capacitance
							'Rth_ca'              			:   [0.292,0.258,0.856,0.228,0.3]            												,   #? 	case-to-ambient thermal resistance
							'Cth_ca'              			:   [0.788,0.205,15.91,3.716,0.015]             											,   #? 	case-to-ambient thermal capacitance
							'Tinit'							:	0.0																						,	#?	initial juntion temperature
							'Pinit'							:	0.0																						,	#?	initial power dissipation
							'Coss'					: 	{																									#!	device Coss parameters
								'C'							:	Coss_eff					 															,	#?	device parasitic output capacitance
								'R'							:	0																						,	#?	Coss resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Coss inductance to reduce current slope
								'Coss_er'					:	Crss_er																					,	#?	energy-related Coss
								'Coss_tr'					:	Coss_tr																					,	#?	time-related Coss
								'Vvec'						:	Coss[0]																					,	#? 	device Coss voltage vector
								'Cvec'						:	Coss[1]																					,	#?	device Coss capacity vector
								'Offset'					:	0																						,	#?	parasitic offset to Coss
                                'Factor'					:	1.0																						,	#?	parasitic tolerance to Coss
								'Qoss'						:	Qoss																					,	#?	equivalent charge of Coss
								'Eoss'						:	Eoss																					,	#?	equivalent energy of Coss
								'Config'					:	5																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
						},
                        	'Crss'					:	{																									#!	device Crss parameters
                                'C'							:	Crss_eff					 															,	#?	device parasitic reverse transfer capacitance
								'R'							:	0																						,	#?	Crss resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Crss inductance to reduce current slope
								'Crss_er'					:	Crss_er																					,	#?	energy-related Crss
								'Crss_tr'					:	Crss_tr																					,	#?	time-related Crss
								'Vvec'						:	Crss[0]																					,	#?	device Crss voltage vector
                                'Cvec'						:	Crss[1]																					,	#?	device Crss capacity vector
								'Qvec'						:	Qrss																					,	#?	device accumulated Crss charge vector
								'Offset'					:	0																						,	#?	parasitic offset to Crss
								'Factor'					:	1.0																						,	#?	parasitic tolerance to Crss
								'Qrss'						:	Qrss																					,	#?	equivalent charge of Crss
								'Erss'						:	Erss																					,	#?	equivalent energe of Crss
								'Config'					:	5																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
						},
							'Ciss'					:	{																									#!	device Ciss parameters
								'C'							:	Ciss_eff					 															,	#?	device parasitic input capacitance
								'R'							:	0																						,	#?	Ciss resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Ciss inductance to reduce current slope
								'Ciss_er'					:	Ciss_er																					,	#?	energy-related Ciss
								'Ciss_tr'					:	Ciss_tr																					,	#?	time-related Ciss
								'Vvec'						:	Ciss[0]																					,	#?	device Ciss voltage vector
								'Cvec'						:	Ciss[1]																					,	#?	device Ciss capacity vector
								'Offset'					:	0																						,	#?	parasitic offset to Ciss
								'Factor'					:	1.0																						,	#?	parasitic tolerance to Ciss
								'Qiss'						:	Qiss																					,	#?	equivalent charge of Ciss
								'Eiss'						:	Eiss																					,	#?	equivalent energy of Ciss
								'Config'					:	5																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Cds'					:	{																									#!	device Cds parameters
								'C'							:	Cds_eff					 																,	#?	device parasitic Cds capacitance
								'R'							:	0																						,	#?	Cds resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Cds inductance to reduce current slope
								'Cds_er'					:	Cds_er																					,	#?	energy-related Cds
								'Cds_tr'					:	Cds_tr																					,	#?	time-related Cds
								'Vvec'						:	Coss[0]																					,	#?	device Cds voltage vector
								'Cvec'						:	Cds																						,	#?	device Cds capacity vector
								'Offset_ON'					:	0																						,	#?	tuning offset for turn ON
								'Offset_OFF'				:	0																						,	#?	tuning offset for turn OFF
								'Factor_ON'					:	1.0																						,	#?	tuning factor for turn ON
								'Factor_OFF'				:	1.0																						,	#?	tuning factor for turn OFF
								'Config'					:	4																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Cgd'					:	{																									#!	device Cgd parameters
								'C'							:	Cgd_eff							 														,	#?	device parasitic Cgd capacitance
								'R'							:	0																						,	#?	Cgd resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Cgd inductance to reduce current slope
								'Cgd_er'					:	Cgd_er																					,	#?	energy-related Cgd
								'Cgd_tr'					:	Cgd_tr																					,	#?	time-related Cgd
								'Vvec'						:	Crss[0]																					,	#?	device Cgd voltage vector
								'Cvec'						:	Cgd																						,	#?	device Cgd capacity vector
								'Offset_ON'					:	0																						,	#?	tuning offset for turn ON
								'Offset_OFF'				:	0																						,	#?	tuning offset for turn OFF
								'Factor_ON'					:	1.0																						,	#?	tuning factor for turn ON
								'Factor_OFF'				:	1.0																						,	#?	tuning factor for turn OFF
								'Config'					:	4																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Cgs'					:	{																									#!	device Cgs parameters
								'C'							:	Cgs_eff					 																,	#?	device parasitic Cgs capacitance
								'R'							:	0																						,	#?	Cgs resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Cgs inductance to reduce current slope
								'Cgs_er'					:	Cgs_er																					,	#?	energy-related Cgs
								'Cgs_tr'					:	Cgs_tr																					,	#?	time-related Cgs
								'Vvec'						:	Ciss[0]																					,	#?	device Cgs voltage vector
								'Cvec'						:	Cgs																						,	#?	device Cgs capacity vector
								'Offset_ON'					:	0																						,	#?	tuning offset for turn ON
								'Offset_OFF'				:	0																						,	#?	tuning offset for turn OFF
								'Factor_ON'					:	1.0																						,	#?	tuning factor for turn ON
								'Factor_OFF'				:	1.0																						,	#?	tuning factor for turn OFF
								'Config'					:	4																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Eoff'					:	{																									#!	transistor turn-OFF energy losses
									'Ivec'					:	Ioff																					,	#?	turn-OFF energy current vector
									'Rgvec'					:	[0,100]																					,	#?	OFF path gate resistances vector
									'Tjvec'					:	[-55,175]																				,	#?	junction temperature vector
                                    'Vvec'					:	Voff																					,	#?	turn-OFF voltage vector
                                    'Evec'					:	Eoff																					,	#?	turn-OFF energy vectors
									'Evec_Temp'				:	Eoff_Temp																				,	#?	turn-OFF energy temp scaling vectors
                                    'CAT'					:	catOFF																					,	#?	octave Eoff energy syntax
									'CAT_Temp'				:	catOFF_Temp																				,	#?	octave Eoff energy temp scaling syntax
									'Vgs'					:	0																						,	#?	used OFF path gate-source voltage
									'Vth'					:	1.5																						,	#?	used OFF path threshold voltage
									'Rg'					:	0																							#?	used OFF path gate resistance
						},
							'Eon'					:	{																									#!	transistor turn-ON energy losses
									'Ivec'					:	Ion																						,	#?	turn-ON energy current vector
									'Rgvec'					:	[0,100]																					,	#?	ON path gate resistances vector
									'Tjvec'					:	[-55,175]																				,	#?	junction temperature vector
                                    'Vvec'					:	Von																						,	#?	turn-ON voltage vector
                                    'Evec'					:	Eon																						,	#?	turn-ON energy vectors
									'Evec_Temp'				:	Eon_Temp																				,	#?	turn-ON energy temp scaling vectors
                                    'CAT'					:	catON																					,	#?	octave Eon energy syntax
									'CAT_Temp'				:	catON_Temp																				,	#?	octave Eon energy temp scaling syntax
									'Vgs'					:	12																						,	#?	used ON path gate-source voltage
									'Vth'					:	1.5																						,	#?	used ON path threshold voltage
									'Rg'					:	0																							#?	used ON path gate resistance
						},
							'Tau_deg'						:	100e-9																					,	#?	deglitch filter for currents and voltages
							'RCsnubber'						:	2																						,	#?	1->enable | 2->disable
						}

#?----------------------------------------------------------------------------------------------------------------------------------------------------------------------

Coss,Qoss,Eoss,Coss_tr,Coss_er		=	paramProcess.MOSFETcaps(switchesCossPath,'IAUT300N08S5N014','_Coss')
Crss,Qrss,Erss,Crss_tr,Crss_er 		=	paramProcess.MOSFETcaps(switchesCrssPath,'IAUT300N08S5N014','_Crss')
Ciss,Qiss,Eiss,Ciss_tr,Ciss_er 		=	paramProcess.MOSFETcaps(switchesCissPath,'IAUT300N08S5N014','_Ciss')
Coss_eff 							=	paramProcess.getCmos(Coss,Coss_tr,Coss_er,Coss[0][0],True)
Ciss_eff 							=	paramProcess.getCmos(Ciss,Ciss_tr,Ciss_er,Ciss[0][0],True)
Crss_eff 							=	paramProcess.getCmos(Crss,Crss_tr,Crss_er,Crss[0][0],True)
Cds 						        =	(np.array(Coss[1]) - np.array(Crss[1])).tolist()
Cgs						        	=	(np.array(Ciss[1]) - np.array(Crss[1])).tolist()
Cgd						        	=	Crss[1]
Cds_tr						        =	(np.array(Coss_tr) - np.array(Crss_tr)).tolist()
Cgs_tr						        =	(np.array(Ciss_tr) - np.array(Crss_tr)).tolist()
Cgd_tr						        =	Crss_tr
Cds_er						        =	(np.array(Coss_er) - np.array(Crss_er)).tolist()
Cgs_er						        =	(np.array(Ciss_er) - np.array(Crss_er)).tolist()
Cgd_er						        =	Crss_er
Cds_eff 							=	paramProcess.getCmos([Coss[0],Cds],Cds_tr,Cds_er,Coss[0][0],True)
Cgs_eff 							=	paramProcess.getCmos([Ciss[0],Cgs],Cgs_tr,Cgs_er,Ciss[0][0],True)
Cgd_eff 							=	Crss_eff
Rvec,Tvec							=	paramProcess.MOSFETrdson(switchesRdsonPath,'IAUT300N08S5N014','_Rdson')
Nvec,Ivec 							=	paramProcess.MOSFETrdson(switchesIdsonPath,'IAUT300N08S5N014','_Rdson')
Ioff,catOFF,Eoff					=	paramProcess.MOSFETenergies(switchesEoffPath,'IAUT300N08S5N014','_Eoff')
Voff,catOFF_Temp,Eoff_Temp			=	paramProcess.MOSFETenergies(switchesEoffPath,'IAUT300N08S5N014','_Eoff_Temp')
Ion,catON,Eon 						=	paramProcess.MOSFETenergies(switchesEonPath,'IAUT300N08S5N014','_Eon')
Von,catON_Temp,Eon_Temp				=	paramProcess.MOSFETenergies(switchesEonPath,'IAUT300N08S5N014','_Eon_Temp')
Vfvec,Ifvec,Rd,Vt					=	paramProcess.DiodeVI_data(bodyDiodeVIPath,'IAUT300N08S5N014')
Vds_vec,Ids_vec 					=	paramProcess.Forward_Transfer_data(switchesTransferPath,'IAUT300N08S5N014')

IAUT300N08S5N014	=	{																																	#*	IAUT300N08S5N014 parameters
							'Config'						:	1																						,	#!	1->electric integrated | 2->electric separate | 3->thermal integrated | 4->thermal separate
							'Transistor'  			: 	{																									#!	transistors parameters
									'Config'				:	2																						,	#?	1->real model | 2->ideal model | 3->behavioral model
									'Thermal'           	:   ''                                  													,   #? 	selected transistor
									'Custom'            	:   []						               													,   #? 	transistor provided custom variables
									'g_fs'					:	1e6																						,	#?	forward transconductance
									'Rg'					:	1.4																						,	#?	internal gate resistance
									'Lg'					:	3e-9*0																						,	#?	gate pin inductance
									'Rds_on'            	:   Rvec[-1][-1]*1e-3																		,   #? 	transistor ON resistance
									'Rds_off'				:	'inf'																					,	#?	transistor OFF resistance
									'Rvec'					:	(np.array(Rvec)*1e-3).tolist()														,	#?	absolute Rdson vector corresponding to junction temperature
									'Tvec'					:	Tvec 																					,	#?	junction temperature vector for Rdson
									'RTconfig'				:	1																						,	#?	choose which RT vector to be used
									'RdsonScale'			:	1.0																						,	#?	Rdson scaling to account for min, typ and max deviations
									'Nvec'					:	Nvec 																					,	#?	normalized Rdson vector corresponding to current
									'Ivec'					:	Ivec																					,	#?	current vector for normalized Rdson
									'NIconfig'				:	1																						,	#?	choose which NI vector to be used
									'IdsonScale'			:	1.0																						,	#?	Idson resistance scaling to account for min, typ and max deviations
									'Rsrc'					:	189e-6*0																				,	#?	kelvin source pin resistance
									'Lsrc'					:	1.5e-9*0																				,	#?	kelvin source pin inductance
									'Ls'					:	1.5e-9*0																				,	#?	package source inductance
                                    'Ld'					:	1e-9*0																					,	#?	package drain inductance
									'Rs'					:	189e-6*0																				,	#?	package source resistance
									'Rd'					:	20e-6*0																					,	#?	package drain inductance
									'Ksrc'					:	0																						,	#?	kelvin source option, 0->no kelvin | 1->kelvin
									'Vblock'            	:   80                                	 													,   #? 	transistor blocking voltage
									'Id'                	:   300                                 													,   #? 	transistor drain current
									'Tr'                	:   0                                   													,   #? 	transistor rise time
									'Tf'                	:   0                                       												, 	#? 	transistor fall time
									'Avalanche'		:	{																									#!	transistor avalanche parameters
										'Config'			:	2																						,	#?	1->enable | 2->disable
										'Voltage'			:	80																						,	#?	avalanche voltage
										'Resistance'		:	1e-3																						#?	avalanche resistance to break voltage state-dependency
									},
									'Transfer'		:	{																									#!	transistor forward transfer parameters
										'Vds'				:	Vds_vec																					,	#?	drain-source voltage vector
										'Vgs'				:	list(np.arange(0.0,12.0+0.4,0.4))													,	#?	gate-source voltage vector
										'Ids'				:	Ids_vec																					,	#?	drain current vector
										'Factor_ON'			:	1.0																						,	#?	scaling factor for Ids at turn ON
										'Factor_OFF'		:	1.0																						,	#?	scaling factor for Ids at turn OFF
										'Factor_Vgs_ON'		:	1.0																						,	#?	scaling factor for Vgs at turn ON
										'Factor_Vgs_OFF'	:	1.0																						,	#?	scaling factor for Vgs at turn OFF
										'Vcoss'				:	0																						,	#?	initial voltage of the Coss
									},
						},
							'BodyDiode'  			:	{																									#!	body diodes paramteters
									'Config'				:	4																						,	#?	1->non-ideal RR | 2->non-ideal | 3->ideal RR | 4->ideal
									'Thermal'           	:   ''                                  													,   #? 	separate body diode
									'Custom'            	:   []					                 													,   #? 	body diode provided custrom variables
									'Rd_on'             	:   Rd[-1]													                              	,  	#? 	body diode ON resistance
									'Rd_off'				:	'inf'																					,	#?	body diode OFF resistance
									'Vf'					:	Vt[-1]																					,	#? 	body diode forward voltage
									'If'                	:   300                                 													,   #? 	body diode forward current
									'dIr'               	:   100e6                                  													,   #? 	body diode current slope
									'Lrr'					:	1e-9																					,	#?	body diode reverse recovery inductance
									'Trr'               	:   83e-9                                  													,   #? 	body diode reverse recovery time
									'Irr'               	:   0                                   													,   #? 	body diode reverse recovery current
									'Qrr'               	:   156e-9                                  												,	#? 	body diode reverse recovery charge
									'Is'                  	:   50              																		, 	#? 	body diode reference current
									'Vs'					:	40																						,	#?	body diode reference voltage
                                    'VIcurve'		:	{																									#!	body diode VI characteristics
                                        'Vfvec'				:	Vfvec																					,	#?	forward voltage vector
                                        'Ifvec'				:	Ifvec																					,	#?	forward current vector
										'Rdvec'				:	Rd																						,	#?	dynamic resistance vector
										'Vtvec'				:	Vt																						,	#?	threshold voltage vector
                                        'Temps'				:	[25,175]																				,	#?	temperature vector
                                        'Vfscale'			:	1.33																						#?	Vf scaling to account for min, typ and max deviations
									},
						},
							'GateDriver'			:	{																									#!	gate driver parameters
									'Config'				:	3																						,	#?	1->high-side | 2->low-side | 3->disable
									'Von'					:	12																						,	#?	ON driving voltage
									'Voff'					:	0																						,	#?	OFF driving voltage
									'Ron'					:	5																						,	#?	sourcing output resistance
									'Roff'					:	5																						,	#?	sinking output resistance
									'Lon'					:	0																						,	#?	sourcing output inductance
									'Loff'					:	0																						,	#?	sinking output inductance
									'Cload'					:	0																						,	#?	capacitive load on output
									'Rload'					:	'inf'																					,	#?	resistive load on output
									'Delay'					:	0																						,	#?	input-to-output total deadtime
									'Trise'					:	0																						,	#?	output rising time
									'Tfall'					:	0																						,	#?	output falling time
									'UVLO_Start'			:	7.0																						,	#?	UVLO startup voltage threshold
									'UVLO_Stop'				:	6.5																						,	#?	UVLO shutdown voltage threshold
									'UVLO_Delay'			:	100e-9																					,	#?	delay between UVLO startup and shutdown
									'Init_State'			:	0																						,	#?	initial toggling state, 0->OFF | 1->ON
									'CurrentLimit'	:	{																									#*	current limit of driver stage
										'Config'			:	2																						,	#?	1->enable | 2->disable
										'Ts'				: 	0 																						,	#?	sampling time between inductive & capacitive links
										'tau'				: 	0																						,	#?	first-order delay between inductive & capacitive links
                                    	'Rs'				: 	0																						,	#?	source impedance of inductive link
										'Cs'				:	1e-12																					,	#?	source capacitance of capacitive link
                                        'UpLim'				: 	10																						,	#?	max current limit on capacitive link
                                        'LoLim'				: 	-10																						,	#?	min current limit on capacitive link
                                        'Voffset'			: 	0																							#?	voltage offset between inductive & capacitive links
									},
									'Masking'		:	{																									#*	switching stages masking
										'ON'	:	{																										#	ON path masking
											'Config'		:	2																						,	#?	1->enable | 2->disable
											'HIGH'	:	{																									#!	HIGH mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[0, 0]																						#?	mask output
											},
											'LOW'	:	{																									#!	LOW mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[1, 1]																						#?	mask output
											}
										},
										'OFF'	:	{																										#	OFF path masking
											'Config'		:	2																						,	#?	1->enable | 2->disable
											'HIGH'	:	{																									#!	HIGH mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[0, 0]																						#?	mask output
											},
											'LOW'	:	{																									#!	LOW mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[1, 1]																						#?	mask output
											}
										}
									},
									'Boot'			:	{																									#*	bootstrap/charge pump parameters
										'Config'			:	1																						,	#?	1->bootstrap | 2->charge pump
										'Von'				:	14																						,	#?	boostrap driving voltage
										'Cboot'				:	4.7e-6																					,	#?	bootstrap capacitance
										'Vinit'				:	0																						,	#?	bootstrap capacitance initial voltage
										'Rboot'				:	10																						,	#?	bootstrap resistance
										'Vfboot'			:	0.87																					,	#?	bootstrap diode forward voltage
										'Rdboot'			:	1e-3																					,	#?	bootstrap diode ON-state resistance
										'Ichrg'				:	300e-6																					,	#?	charge pump supply current
										'Idis'				:	5e-6																					,	#?	charge pump loading or leakage current
										'Cpar'				:	0																						,	#?	charge pump parallel cap to break state/source dependency
									    'UVLO_Start'		:	11.6																					,	#?	threshold value to start the charge pump
										'UVLO_Stop'			:	12.4																						#?	threshold value to stop the charge pump
									},
							},
							'GateNetwork'			:	{																									#!	gate drive circuit parameters
									'Config'				:	2																						,	#?	1-> enable | 2->disable
									'ON_Path'		:	{																									#*	sourcing path parameters
										'Rg'				:	5																						,	#?	gate ON path resistance
										'Lg'				:	0																						,	#?	gate ON path inductance
										'Rload'				:	10e3																					,	#?	gate pull down resistance
										'Diode'	:	{																										#	reverse blocking diode parameters
											'Vf'			:	0																						,	#?	forward voltage
											'Rd_on'			:	0																						,	#?	ON-state resistance
										},
									},
									'OFF_Path'		:	{																									#*	sinking path parameters
										'Rg'				:	5																						,	#?	gate OFF path resistance
										'Lg'				:	0																						,	#?	gate OFF path inductance
										'Diode'	:	{																										#	reverse blocking diode parameters
											'Vf'			:	0																						,	#?	forward voltage
											'Rd_on'			:	0																						,	#?	ON-state resistance
										},
									},
									'NegVolt'		:	{																									#*	negative voltage generator parameters
										'Config'			:	2																						,	#?	1-> enable | 2->disable
										'Dz'	:	{																										#	zener diode parameters
											'Vf'			:	0.7																						,	#?	forward voltage
											'Rd_on'			:	1e-3																					,	#?	ON-state resistance
											'Vz'			:	2																						,	#?	Zener breakdown voltage
											'Rz'			:	1e-3																					,	#?	Zener resistance
										},
										'Dp'	:	{																										#	peak detector diode
											'Vf'			:	0.0																						,	#?	forward voltage
											'Rd_on'			:	0.0																						,	#?	ON-state resistance
										},
										'Cz'	:	{																										#	Zener capacitor parameters
											'Config'		:	1																						,	#?	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
											'Csingle'		:	1e-6																					,	#?	single capacitor value
											'Rsingle'		:	5e-3																					,	#?	ESR of single capacitor
											'Lsingle'		:	0																						,	#?	ESL of single capacitor
											'nPar'			:	1																						,	#?	number of parallel connections
											'nSer'			:	1																						,	#?	number of series connections
											'Vinit'			:	0																						,	#?	capacitor initial voltage
										},
										'Cp'	:	{																										#	peak detector capacitor parameters
											'Config'		:	1																						,	#?	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
											'Csingle'		:	2.2e-6																					,	#?	single capacitor value
											'Rsingle'		:	5e-3																					,	#?	ESR of single capacitor
											'Lsingle'		:	0																						,	#?	ESL of single capacitor
											'nPar'			:	1																						,	#?	number of parallel connections
											'nSer'			:	1																						,	#?	number of series connections
											'Vinit'			:	0																						,	#?	capacitor initial voltage
										},
										'Rp1'				:	43																						,	#?	current limiter of peak detector current
										'Rp2'				:	4.7e3																					,	#?	load resistor to charge the zener diode
									},
								},
							'nParallel'   					:	1                                       												,   #? 	number of parallel devices
							'Rth_jc'						:	0.5																						,	#?	junction-to-case thermal resistance
							'Cth_jc'						:	0.00																					,	#?	junction-to-case thermal capacitance
							'Rth_ca'              			:   [0.292,0.258,0.856,0.228,0.3]            												,   #? 	case-to-ambient thermal resistance
							'Cth_ca'              			:   [0.788,0.205,15.91,3.716,0.015]             											,   #? 	case-to-ambient thermal capacitance
							'Tinit'							:	0.0																						,	#?	initial juntion temperature
							'Pinit'							:	0.0																						,	#?	initial power dissipation
							'Coss'					: 	{																									#!	device Coss parameters
								'C'							:	Coss_eff					 															,	#?	device parasitic output capacitance
								'R'							:	0																						,	#?	Coss resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Coss inductance to reduce current slope
								'Coss_er'					:	Crss_er																					,	#?	energy-related Coss
								'Coss_tr'					:	Coss_tr																					,	#?	time-related Coss
								'Vvec'						:	Coss[0]																					,	#? 	device Coss voltage vector
								'Cvec'						:	Coss[1]																					,	#?	device Coss capacity vector
								'Offset'					:	0																						,	#?	parasitic offset to Coss
                                'Factor'					:	1.0																						,	#?	parasitic tolerance to Coss
								'Qoss'						:	Qoss																					,	#?	equivalent charge of Coss
								'Eoss'						:	Eoss																					,	#?	equivalent energy of Coss
								'Config'					:	5																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
						},
                        	'Crss'					:	{																									#!	device Crss parameters
                                'C'							:	Crss_eff					 															,	#?	device parasitic reverse transfer capacitance
								'R'							:	0																						,	#?	Crss resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Crss inductance to reduce current slope
								'Crss_er'					:	Crss_er																					,	#?	energy-related Crss
								'Crss_tr'					:	Crss_tr																					,	#?	time-related Crss
								'Vvec'						:	Crss[0]																					,	#?	device Crss voltage vector
                                'Cvec'						:	Crss[1]																					,	#?	device Crss capacity vector
								'Qvec'						:	Qrss																					,	#?	device accumulated Crss charge vector
								'Offset'					:	0																						,	#?	parasitic offset to Crss
								'Factor'					:	1.0																						,	#?	parasitic tolerance to Crss
								'Qrss'						:	Qrss																					,	#?	equivalent charge of Crss
								'Erss'						:	Erss																					,	#?	equivalent energe of Crss
								'Config'					:	5																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
						},
							'Ciss'					:	{																									#!	device Ciss parameters
								'C'							:	Ciss_eff					 															,	#?	device parasitic input capacitance
								'R'							:	0																						,	#?	Ciss resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Ciss inductance to reduce current slope
								'Ciss_er'					:	Ciss_er																					,	#?	energy-related Ciss
								'Ciss_tr'					:	Ciss_tr																					,	#?	time-related Ciss
								'Vvec'						:	Ciss[0]																					,	#?	device Ciss voltage vector
								'Cvec'						:	Ciss[1]																					,	#?	device Ciss capacity vector
								'Offset'					:	0																						,	#?	parasitic offset to Ciss
								'Factor'					:	1.0																						,	#?	parasitic tolerance to Ciss
								'Qiss'						:	Qiss																					,	#?	equivalent charge of Ciss
								'Eiss'						:	Eiss																					,	#?	equivalent energy of Ciss
								'Config'					:	5																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Cds'					:	{																									#!	device Cds parameters
								'C'							:	Cds_eff					 																,	#?	device parasitic Cds capacitance
								'R'							:	0																						,	#?	Cds resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Cds inductance to reduce current slope
								'Cds_er'					:	Cds_er																					,	#?	energy-related Cds
								'Cds_tr'					:	Cds_tr																					,	#?	time-related Cds
								'Vvec'						:	Coss[0]																					,	#?	device Cds voltage vector
								'Cvec'						:	Cds																						,	#?	device Cds capacity vector
								'Offset_ON'					:	0																						,	#?	tuning offset for turn ON
								'Offset_OFF'				:	0																						,	#?	tuning offset for turn OFF
								'Factor_ON'					:	1.0																						,	#?	tuning factor for turn ON
								'Factor_OFF'				:	1.0																						,	#?	tuning factor for turn OFF
								'Config'					:	4																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Cgd'					:	{																									#!	device Cgd parameters
								'C'							:	Cgd_eff							 														,	#?	device parasitic Cgd capacitance
								'R'							:	0																						,	#?	Cgd resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Cgd inductance to reduce current slope
								'Cgd_er'					:	Cgd_er																					,	#?	energy-related Cgd
								'Cgd_tr'					:	Cgd_tr																					,	#?	time-related Cgd
								'Vvec'						:	Crss[0]																					,	#?	device Cgd voltage vector
								'Cvec'						:	Cgd																						,	#?	device Cgd capacity vector
								'Offset_ON'					:	0																						,	#?	tuning offset for turn ON
								'Offset_OFF'				:	0																						,	#?	tuning offset for turn OFF
								'Factor_ON'					:	1.0																						,	#?	tuning factor for turn ON
								'Factor_OFF'				:	1.0																						,	#?	tuning factor for turn OFF
								'Config'					:	4																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Cgs'					:	{																									#!	device Cgs parameters
								'C'							:	Cgs_eff					 																,	#?	device parasitic Cgs capacitance
								'R'							:	0																						,	#?	Cgs resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Cgs inductance to reduce current slope
								'Cgs_er'					:	Cgs_er																					,	#?	energy-related Cgs
								'Cgs_tr'					:	Cgs_tr																					,	#?	time-related Cgs
								'Vvec'						:	Ciss[0]																					,	#?	device Cgs voltage vector
								'Cvec'						:	Cgs																						,	#?	device Cgs capacity vector
								'Offset_ON'					:	0																						,	#?	tuning offset for turn ON
								'Offset_OFF'				:	0																						,	#?	tuning offset for turn OFF
								'Factor_ON'					:	1.0																						,	#?	tuning factor for turn ON
								'Factor_OFF'				:	1.0																						,	#?	tuning factor for turn OFF
								'Config'					:	4																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Eoff'					:	{																									#!	transistor turn-OFF energy losses
									'Ivec'					:	Ioff																					,	#?	turn-OFF energy current vector
									'Rgvec'					:	[0,100]																					,	#?	OFF path gate resistances vector
									'Tjvec'					:	[-55,175]																				,	#?	junction temperature vector
                                    'Vvec'					:	Voff																					,	#?	turn-OFF voltage vector
                                    'Evec'					:	Eoff																					,	#?	turn-OFF energy vectors
									'Evec_Temp'				:	Eoff_Temp																				,	#?	turn-OFF energy temp scaling vectors
                                    'CAT'					:	catOFF																					,	#?	octave Eoff energy syntax
									'CAT_Temp'				:	catOFF_Temp																				,	#?	octave Eoff energy temp scaling syntax
									'Vgs'					:	0																						,	#?	used OFF path gate-source voltage
									'Vth'					:	1.5																						,	#?	used OFF path threshold voltage
									'Rg'					:	0																							#?	used OFF path gate resistance
						},
							'Eon'					:	{																									#!	transistor turn-ON energy losses
									'Ivec'					:	Ion																						,	#?	turn-ON energy current vector
									'Rgvec'					:	[0,100]																					,	#?	ON path gate resistances vector
									'Tjvec'					:	[-55,175]																				,	#?	junction temperature vector
                                    'Vvec'					:	Von																						,	#?	turn-ON voltage vector
                                    'Evec'					:	Eon																						,	#?	turn-ON energy vectors
									'Evec_Temp'				:	Eon_Temp																				,	#?	turn-ON energy temp scaling vectors
                                    'CAT'					:	catON																					,	#?	octave Eon energy syntax
									'CAT_Temp'				:	catON_Temp																				,	#?	octave Eon energy temp scaling syntax
									'Vgs'					:	12																						,	#?	used ON path gate-source voltage
									'Vth'					:	1.5																						,	#?	used ON path threshold voltage
									'Rg'					:	0																							#?	used ON path gate resistance
						},
							'Tau_deg'						:	100e-9																					,	#?	deglitch filter for currents and voltages
							'RCsnubber'						:	2																						,	#?	1->enable | 2->disable
						}

#?----------------------------------------------------------------------------------------------------------------------------------------------------------------------

Coss,Qoss,Eoss,Coss_tr,Coss_er		=	paramProcess.MOSFETcaps(switchesCossPath,'IAUT300N08S5N012','_Coss')
Crss,Qrss,Erss,Crss_tr,Crss_er 		=	paramProcess.MOSFETcaps(switchesCrssPath,'IAUT300N08S5N012','_Crss')
Ciss,Qiss,Eiss,Ciss_tr,Ciss_er 		=	paramProcess.MOSFETcaps(switchesCissPath,'IAUT300N08S5N012','_Ciss')
Coss_eff 							=	paramProcess.getCmos(Coss,Coss_tr,Coss_er,Coss[0][0],True)
Ciss_eff 							=	paramProcess.getCmos(Ciss,Ciss_tr,Ciss_er,Ciss[0][0],True)
Crss_eff 							=	paramProcess.getCmos(Crss,Crss_tr,Crss_er,Crss[0][0],True)
Cds 						        =	(np.array(Coss[1]) - np.array(Crss[1])).tolist()
Cgs						        	=	(np.array(Ciss[1]) - np.array(Crss[1])).tolist()
Cgd						        	=	Crss[1]
Cds_tr						        =	(np.array(Coss_tr) - np.array(Crss_tr)).tolist()
Cgs_tr						        =	(np.array(Ciss_tr) - np.array(Crss_tr)).tolist()
Cgd_tr						        =	Crss_tr
Cds_er						        =	(np.array(Coss_er) - np.array(Crss_er)).tolist()
Cgs_er						        =	(np.array(Ciss_er) - np.array(Crss_er)).tolist()
Cgd_er						        =	Crss_er
Cds_eff 							=	paramProcess.getCmos([Coss[0],Cds],Cds_tr,Cds_er,Coss[0][0],True)
Cgs_eff 							=	paramProcess.getCmos([Ciss[0],Cgs],Cgs_tr,Cgs_er,Ciss[0][0],True)
Cgd_eff 							=	Crss_eff
Rvec,Tvec							=	paramProcess.MOSFETrdson(switchesRdsonPath,'IAUT300N08S5N012','_Rdson')
Nvec,Ivec 							=	paramProcess.MOSFETrdson(switchesIdsonPath,'IAUT300N08S5N012','_Rdson')
Ioff,catOFF,Eoff					=	paramProcess.MOSFETenergies(switchesEoffPath,'IAUT300N08S5N012','_Eoff')
Voff,catOFF_Temp,Eoff_Temp			=	paramProcess.MOSFETenergies(switchesEoffPath,'IAUT300N08S5N012','_Eoff_Temp')
Ion,catON,Eon 						=	paramProcess.MOSFETenergies(switchesEonPath,'IAUT300N08S5N012','_Eon')
Von,catON_Temp,Eon_Temp				=	paramProcess.MOSFETenergies(switchesEonPath,'IAUT300N08S5N012','_Eon_Temp')
Vfvec,Ifvec,Rd,Vt					=	paramProcess.DiodeVI_data(bodyDiodeVIPath,'IAUT300N08S5N012')
Vds_vec,Ids_vec 					=	paramProcess.Forward_Transfer_data(switchesTransferPath,'IAUT300N08S5N012')

IAUT300N08S5N012	=	{																																	#*	IAUT300N08S5N012 parameters
							'Config'						:	1																						,	#!	1->electric integrated | 2->electric separate | 3->thermal integrated | 4->thermal separate
							'Transistor'  			: 	{																									#!	transistors parameters
									'Config'				:	2																						,	#?	1->real model | 2->ideal model | 3->behavioral model
									'Thermal'           	:   ''                                  													,   #? 	selected transistor
									'Custom'            	:   []						               													,   #? 	transistor provided custom variables
									'g_fs'					:	1e6																						,	#?	forward transconductance
									'Rg'					:	1.6																						,	#?	internal gate resistance
									'Lg'					:	3e-9*0																					,	#?	gate pin inductance
									'Rds_on'            	:   Rvec[-1][-1]*1e-3																		,   #? 	transistor ON resistance
									'Rds_off'				:	'inf'																					,	#?	transistor OFF resistance
									'Rvec'					:	(np.array(Rvec)*1e-3).tolist()														,	#?	absolute Rdson vector corresponding to junction temperature
									'Tvec'					:	Tvec 																					,	#?	junction temperature vector for Rdson
									'RTconfig'				:	1																						,	#?	choose which RT vector to be used
									'RdsonScale'			:	1.0																						,	#?	Rdson scaling to account for min, typ and max deviations
									'Nvec'					:	Nvec 																					,	#?	normalized Rdson vector corresponding to current
									'Ivec'					:	Ivec																					,	#?	current vector for normalized Rdson
									'NIconfig'				:	1																						,	#?	choose which NI vector to be used
									'IdsonScale'			:	1.0																						,	#?	Idson resistance scaling to account for min, typ and max deviations
									'Rsrc'					:	208e-6*0																				,	#?	kelvin source pin resistance
									'Lsrc'					:	1.5e-9*0																				,	#?	kelvin source pin inductance
									'Ls'					:	1.5e-9*0																				,	#?	package source inductance
                                    'Ld'					:	1e-9*0																					,	#?	package drain inductance
									'Rs'					:	208e-6*0																				,	#?	package source resistance
									'Rd'					:	20e-6*0																					,	#?	package drain inductance
									'Ksrc'					:	0																						,	#?	kelvin source option, 0->no kelvin | 1->kelvin
									'Vblock'            	:   80                                	 													,   #? 	transistor blocking voltage
									'Id'                	:   300                                 													,   #? 	transistor drain current
									'Tr'                	:   0                                   													,   #? 	transistor rise time
									'Tf'                	:   0                                       												, 	#? 	transistor fall time
									'Avalanche'		:	{																									#!	transistor avalanche parameters
										'Config'			:	2																						,	#?	1->enable | 2->disable
										'Voltage'			:	80																						,	#?	avalanche voltage
										'Resistance'		:	1e-3																						#?	avalanche resistance to break voltage state-dependency
									},
									'Transfer'		:	{																									#!	transistor forward transfer parameters
										'Vds'				:	Vds_vec																					,	#?	drain-source voltage vector
										'Vgs'				:	list(np.arange(0.0,12.0+0.4,0.4))													,	#?	gate-source voltage vector
										'Ids'				:	Ids_vec																					,	#?	drain current vector
										'Factor_ON'			:	1.0																						,	#?	scaling factor for Ids at turn ON
										'Factor_OFF'		:	1.0																						,	#?	scaling factor for Ids at turn OFF
										'Factor_Vgs_ON'		:	1.0																						,	#?	scaling factor for Vgs at turn ON
										'Factor_Vgs_OFF'	:	1.0																						,	#?	scaling factor for Vgs at turn OFF
										'Vcoss'				:	0																						,	#?	initial voltage of the Coss
									},
						},
							'BodyDiode'  			:	{																									#!	body diodes paramteters
									'Config'				:	4																						,	#?	1->non-ideal RR | 2->non-ideal | 3->ideal RR | 4->ideal
									'Thermal'           	:   ''                                  													,   #? 	separate body diode
									'Custom'            	:   []					                 													,   #? 	body diode provided custrom variables
									'Rd_on'             	:   Rd[-1]													                              	,  	#? 	body diode ON resistance
									'Rd_off'				:	'inf'																					,	#?	body diode OFF resistance
									'Vf'					:	Vt[-1]																					,	#? 	body diode forward voltage
									'If'                	:   300                                 													,   #? 	body diode forward current
									'dIr'               	:   100e6                                  													,   #? 	body diode current slope
									'Lrr'					:	1e-9																					,	#?	body diode reverse recovery inductance
									'Trr'               	:   86e-9                                  													,   #? 	body diode reverse recovery time
									'Irr'               	:   0                                   													,   #? 	body diode reverse recovery current
									'Qrr'               	:   177e-9                                  												,	#? 	body diode reverse recovery charge
									'Is'                  	:   50              																		, 	#? 	body diode reference current
									'Vs'					:	40																						,	#?	body diode reference voltage
                                    'VIcurve'		:	{																									#!	body diode VI characteristics
                                        'Vfvec'				:	Vfvec																					,	#?	forward voltage vector
                                        'Ifvec'				:	Ifvec																					,	#?	forward current vector
										'Rdvec'				:	Rd																						,	#?	dynamic resistance vector
										'Vtvec'				:	Vt																						,	#?	threshold voltage vector
                                        'Temps'				:	[25,175]																				,	#?	temperature vector
                                        'Vfscale'			:	1.33																						#?	Vf scaling to account for min, typ and max deviations
									},
						},
							'GateDriver'			:	{																									#!	gate driver parameters
									'Config'				:	3																						,	#?	1->high-side | 2->low-side | 3->disable
									'Von'					:	12																						,	#?	ON driving voltage
									'Voff'					:	0																						,	#?	OFF driving voltage
									'Ron'					:	5																						,	#?	sourcing output resistance
									'Roff'					:	5																						,	#?	sinking output resistance
									'Lon'					:	0																						,	#?	sourcing output inductance
									'Loff'					:	0																						,	#?	sinking output inductance
									'Cload'					:	0																						,	#?	capacitive load on output
									'Rload'					:	'inf'																					,	#?	resistive load on output
									'Delay'					:	0																						,	#?	input-to-output total deadtime
									'Trise'					:	0																						,	#?	output rising time
									'Tfall'					:	0																						,	#?	output falling time
									'UVLO_Start'			:	7.0																						,	#?	UVLO startup voltage threshold
									'UVLO_Stop'				:	6.5																						,	#?	UVLO shutdown voltage threshold
									'UVLO_Delay'			:	100e-9																					,	#?	delay between UVLO startup and shutdown
									'Init_State'			:	0																						,	#?	initial toggling state, 0->OFF | 1->ON
									'CurrentLimit'	:	{																									#*	current limit of driver stage
										'Config'			:	2																						,	#?	1->enable | 2->disable
										'Ts'				: 	0 																						,	#?	sampling time between inductive & capacitive links
										'tau'				: 	0																						,	#?	first-order delay between inductive & capacitive links
                                    	'Rs'				: 	0																						,	#?	source impedance of inductive link
										'Cs'				:	1e-12																					,	#?	source capacitance of capacitive link
                                        'UpLim'				: 	10																						,	#?	max current limit on capacitive link
                                        'LoLim'				: 	-10																						,	#?	min current limit on capacitive link
                                        'Voffset'			: 	0																							#?	voltage offset between inductive & capacitive links
									},
									'Masking'		:	{																									#*	switching stages masking
										'ON'	:	{																										#	ON path masking
											'Config'		:	2																						,	#?	1->enable | 2->disable
											'HIGH'	:	{																									#!	HIGH mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[0, 0]																						#?	mask output
											},
											'LOW'	:	{																									#!	LOW mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[1, 1]																						#?	mask output
											}
										},
										'OFF'	:	{																										#	OFF path masking
											'Config'		:	2																						,	#?	1->enable | 2->disable
											'HIGH'	:	{																									#!	HIGH mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[0, 0]																						#?	mask output
											},
											'LOW'	:	{																									#!	LOW mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[1, 1]																						#?	mask output
											}
										}
									},
									'Boot'			:	{																									#*	bootstrap/charge pump parameters
										'Config'			:	1																						,	#?	1->bootstrap | 2->charge pump
										'Von'				:	14																						,	#?	boostrap driving voltage
										'Cboot'				:	4.7e-6																					,	#?	bootstrap capacitance
										'Vinit'				:	0																						,	#?	bootstrap capacitance initial voltage
										'Rboot'				:	10																						,	#?	bootstrap resistance
										'Vfboot'			:	0.87																					,	#?	bootstrap diode forward voltage
										'Rdboot'			:	1e-3																					,	#?	bootstrap diode ON-state resistance
										'Ichrg'				:	300e-6																					,	#?	charge pump supply current
										'Idis'				:	5e-6																					,	#?	charge pump loading or leakage current
										'Cpar'				:	0																						,	#?	charge pump parallel cap to break state/source dependency
									    'UVLO_Start'		:	11.6																					,	#?	threshold value to start the charge pump
										'UVLO_Stop'			:	12.4																						#?	threshold value to stop the charge pump
									},
							},
							'GateNetwork'			:	{																									#!	gate drive circuit parameters
									'Config'				:	2																						,	#?	1-> enable | 2->disable
									'ON_Path'		:	{																									#*	sourcing path parameters
										'Rg'				:	5																						,	#?	gate ON path resistance
										'Lg'				:	0																						,	#?	gate ON path inductance
										'Rload'				:	10e3																					,	#?	gate pull down resistance
										'Diode'	:	{																										#	reverse blocking diode parameters
											'Vf'			:	0																						,	#?	forward voltage
											'Rd_on'			:	0																						,	#?	ON-state resistance
										},
									},
									'OFF_Path'		:	{																									#*	sinking path parameters
										'Rg'				:	5																						,	#?	gate OFF path resistance
										'Lg'				:	0																						,	#?	gate OFF path inductance
										'Diode'	:	{																										#	reverse blocking diode parameters
											'Vf'			:	0																						,	#?	forward voltage
											'Rd_on'			:	0																						,	#?	ON-state resistance
										},
									},
									'NegVolt'		:	{																									#*	negative voltage generator parameters
										'Config'			:	2																						,	#?	1-> enable | 2->disable
										'Dz'	:	{																										#	zener diode parameters
											'Vf'			:	0.7																						,	#?	forward voltage
											'Rd_on'			:	1e-3																					,	#?	ON-state resistance
											'Vz'			:	2																						,	#?	Zener breakdown voltage
											'Rz'			:	1e-3																					,	#?	Zener resistance
										},
										'Dp'	:	{																										#	peak detector diode
											'Vf'			:	0.0																						,	#?	forward voltage
											'Rd_on'			:	0.0																						,	#?	ON-state resistance
										},
										'Cz'	:	{																										#	Zener capacitor parameters
											'Config'		:	1																						,	#?	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
											'Csingle'		:	1e-6																					,	#?	single capacitor value
											'Rsingle'		:	5e-3																					,	#?	ESR of single capacitor
											'Lsingle'		:	0																						,	#?	ESL of single capacitor
											'nPar'			:	1																						,	#?	number of parallel connections
											'nSer'			:	1																						,	#?	number of series connections
											'Vinit'			:	0																						,	#?	capacitor initial voltage
										},
										'Cp'	:	{																										#	peak detector capacitor parameters
											'Config'		:	1																						,	#?	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
											'Csingle'		:	2.2e-6																					,	#?	single capacitor value
											'Rsingle'		:	5e-3																					,	#?	ESR of single capacitor
											'Lsingle'		:	0																						,	#?	ESL of single capacitor
											'nPar'			:	1																						,	#?	number of parallel connections
											'nSer'			:	1																						,	#?	number of series connections
											'Vinit'			:	0																						,	#?	capacitor initial voltage
										},
										'Rp1'				:	43																						,	#?	current limiter of peak detector current
										'Rp2'				:	4.7e3																					,	#?	load resistor to charge the zener diode
									},
								},
							'nParallel'   					:	1                                       												,   #? 	number of parallel devices
							'Rth_jc'						:	0.4																						,	#?	junction-to-case thermal resistance
							'Cth_jc'						:	0.00																					,	#?	junction-to-case thermal capacitance
							'Rth_ca'              			:   [0.292,0.258,0.856,0.228,0.3]            												,   #? 	case-to-ambient thermal resistance
							'Cth_ca'              			:   [0.788,0.205,15.91,3.716,0.015]             											,   #? 	case-to-ambient thermal capacitance
							'Tinit'							:	0.0																						,	#?	initial juntion temperature
							'Pinit'							:	0.0																						,	#?	initial power dissipation
							'Coss'					: 	{																									#!	device Coss parameters
								'C'							:	Coss_eff					 															,	#?	device parasitic output capacitance
								'R'							:	0																						,	#?	Coss resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Coss inductance to reduce current slope
								'Coss_er'					:	Crss_er																					,	#?	energy-related Coss
								'Coss_tr'					:	Coss_tr																					,	#?	time-related Coss
								'Vvec'						:	Coss[0]																					,	#? 	device Coss voltage vector
								'Cvec'						:	Coss[1]																					,	#?	device Coss capacity vector
								'Offset'					:	0																						,	#?	parasitic offset to Coss
                                'Factor'					:	1.0																						,	#?	parasitic tolerance to Coss
								'Qoss'						:	Qoss																					,	#?	equivalent charge of Coss
								'Eoss'						:	Eoss																					,	#?	equivalent energy of Coss
								'Config'					:	5																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
						},
                        	'Crss'					:	{																									#!	device Crss parameters
                                'C'							:	Crss_eff					 															,	#?	device parasitic reverse transfer capacitance
								'R'							:	0																						,	#?	Crss resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Crss inductance to reduce current slope
								'Crss_er'					:	Crss_er																					,	#?	energy-related Crss
								'Crss_tr'					:	Crss_tr																					,	#?	time-related Crss
								'Vvec'						:	Crss[0]																					,	#?	device Crss voltage vector
                                'Cvec'						:	Crss[1]																					,	#?	device Crss capacity vector
								'Qvec'						:	Qrss																					,	#?	device accumulated Crss charge vector
								'Offset'					:	0																						,	#?	parasitic offset to Crss
								'Factor'					:	1.0																						,	#?	parasitic tolerance to Crss
								'Qrss'						:	Qrss																					,	#?	equivalent charge of Crss
								'Erss'						:	Erss																					,	#?	equivalent energe of Crss
								'Config'					:	5																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
						},
							'Ciss'					:	{																									#!	device Ciss parameters
								'C'							:	Ciss_eff					 															,	#?	device parasitic input capacitance
								'R'							:	0																						,	#?	Ciss resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Ciss inductance to reduce current slope
								'Ciss_er'					:	Ciss_er																					,	#?	energy-related Ciss
								'Ciss_tr'					:	Ciss_tr																					,	#?	time-related Ciss
								'Vvec'						:	Ciss[0]																					,	#?	device Ciss voltage vector
								'Cvec'						:	Ciss[1]																					,	#?	device Ciss capacity vector
								'Offset'					:	0																						,	#?	parasitic offset to Ciss
								'Factor'					:	1.0																						,	#?	parasitic tolerance to Ciss
								'Qiss'						:	Qiss																					,	#?	equivalent charge of Ciss
								'Eiss'						:	Eiss																					,	#?	equivalent energy of Ciss
								'Config'					:	5																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Cds'					:	{																									#!	device Cds parameters
								'C'							:	Cds_eff					 																,	#?	device parasitic Cds capacitance
								'R'							:	0																						,	#?	Cds resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Cds inductance to reduce current slope
								'Cds_er'					:	Cds_er																					,	#?	energy-related Cds
								'Cds_tr'					:	Cds_tr																					,	#?	time-related Cds
								'Vvec'						:	Coss[0]																					,	#?	device Cds voltage vector
								'Cvec'						:	Cds																						,	#?	device Cds capacity vector
								'Offset_ON'					:	0																						,	#?	tuning offset for turn ON
								'Offset_OFF'				:	0																						,	#?	tuning offset for turn OFF
								'Factor_ON'					:	1.0																						,	#?	tuning factor for turn ON
								'Factor_OFF'				:	1.0																						,	#?	tuning factor for turn OFF
								'Config'					:	4																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Cgd'					:	{																									#!	device Cgd parameters
								'C'							:	Cgd_eff							 														,	#?	device parasitic Cgd capacitance
								'R'							:	0																						,	#?	Cgd resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Cgd inductance to reduce current slope
								'Cgd_er'					:	Cgd_er																					,	#?	energy-related Cgd
								'Cgd_tr'					:	Cgd_tr																					,	#?	time-related Cgd
								'Vvec'						:	Crss[0]																					,	#?	device Cgd voltage vector
								'Cvec'						:	Cgd																						,	#?	device Cgd capacity vector
								'Offset_ON'					:	0																						,	#?	tuning offset for turn ON
								'Offset_OFF'				:	0																						,	#?	tuning offset for turn OFF
								'Factor_ON'					:	1.0																						,	#?	tuning factor for turn ON
								'Factor_OFF'				:	1.0																						,	#?	tuning factor for turn OFF
								'Config'					:	4																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Cgs'					:	{																									#!	device Cgs parameters
								'C'							:	Cgs_eff					 																,	#?	device parasitic Cgs capacitance
								'R'							:	0																						,	#?	Cgs resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Cgs inductance to reduce current slope
								'Cgs_er'					:	Cgs_er																					,	#?	energy-related Cgs
								'Cgs_tr'					:	Cgs_tr																					,	#?	time-related Cgs
								'Vvec'						:	Ciss[0]																					,	#?	device Cgs voltage vector
								'Cvec'						:	Cgs																						,	#?	device Cgs capacity vector
								'Offset_ON'					:	0																						,	#?	tuning offset for turn ON
								'Offset_OFF'				:	0																						,	#?	tuning offset for turn OFF
								'Factor_ON'					:	1.0																						,	#?	tuning factor for turn ON
								'Factor_OFF'				:	1.0																						,	#?	tuning factor for turn OFF
								'Config'					:	4																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Eoff'					:	{																									#!	transistor turn-OFF energy losses
									'Ivec'					:	Ioff																					,	#?	turn-OFF energy current vector
									'Rgvec'					:	[0,100]																					,	#?	OFF path gate resistances vector
									'Tjvec'					:	[-55,175]																				,	#?	junction temperature vector
                                    'Vvec'					:	Voff																					,	#?	turn-OFF voltage vector
                                    'Evec'					:	Eoff																					,	#?	turn-OFF energy vectors
									'Evec_Temp'				:	Eoff_Temp																				,	#?	turn-OFF energy temp scaling vectors
                                    'CAT'					:	catOFF																					,	#?	octave Eoff energy syntax
									'CAT_Temp'				:	catOFF_Temp																				,	#?	octave Eoff energy temp scaling syntax
									'Vgs'					:	0																						,	#?	used OFF path gate-source voltage
									'Vth'					:	1.5																						,	#?	used OFF path threshold voltage
									'Rg'					:	0																							#?	used OFF path gate resistance
						},
							'Eon'					:	{																									#!	transistor turn-ON energy losses
									'Ivec'					:	Ion																						,	#?	turn-ON energy current vector
									'Rgvec'					:	[0,100]																					,	#?	ON path gate resistances vector
									'Tjvec'					:	[-55,175]																				,	#?	junction temperature vector
                                    'Vvec'					:	Von																						,	#?	turn-ON voltage vector
                                    'Evec'					:	Eon																						,	#?	turn-ON energy vectors
									'Evec_Temp'				:	Eon_Temp																				,	#?	turn-ON energy temp scaling vectors
                                    'CAT'					:	catON																					,	#?	octave Eon energy syntax
									'CAT_Temp'				:	catON_Temp																				,	#?	octave Eon energy temp scaling syntax
									'Vgs'					:	12																						,	#?	used ON path gate-source voltage
									'Vth'					:	1.5																						,	#?	used ON path threshold voltage
									'Rg'					:	0																							#?	used ON path gate resistance
						},
							'Tau_deg'						:	100e-9																					,	#?	deglitch filter for currents and voltages
							'RCsnubber'						:	2																						,	#?	1->enable | 2->disable
						}

#?----------------------------------------------------------------------------------------------------------------------------------------------------------------------

Coss,Qoss,Eoss,Coss_tr,Coss_er		=	paramProcess.MOSFETcaps(switchesCossPath,'NVBLS1D1N08H','_Coss')
Crss,Qrss,Erss,Crss_tr,Crss_er 		=	paramProcess.MOSFETcaps(switchesCrssPath,'NVBLS1D1N08H','_Crss')
Ciss,Qiss,Eiss,Ciss_tr,Ciss_er 		=	paramProcess.MOSFETcaps(switchesCissPath,'NVBLS1D1N08H','_Ciss')
Coss_eff 							=	paramProcess.getCmos(Coss,Coss_tr,Coss_er,Coss[0][0],True)
Ciss_eff 							=	paramProcess.getCmos(Ciss,Ciss_tr,Ciss_er,Ciss[0][0],True)
Crss_eff 							=	paramProcess.getCmos(Crss,Crss_tr,Crss_er,Crss[0][0],True)
Cds 						        =	(np.array(Coss[1]) - np.array(Crss[1])).tolist()
Cgs						        	=	(np.array(Ciss[1]) - np.array(Crss[1])).tolist()
Cgd						        	=	Crss[1]
Cds_tr						        =	(np.array(Coss_tr) - np.array(Crss_tr)).tolist()
Cgs_tr						        =	(np.array(Ciss_tr) - np.array(Crss_tr)).tolist()
Cgd_tr						        =	Crss_tr
Cds_er						        =	(np.array(Coss_er) - np.array(Crss_er)).tolist()
Cgs_er						        =	(np.array(Ciss_er) - np.array(Crss_er)).tolist()
Cgd_er						        =	Crss_er
Cds_eff 							=	paramProcess.getCmos([Coss[0],Cds],Cds_tr,Cds_er,Coss[0][0],True)
Cgs_eff 							=	paramProcess.getCmos([Ciss[0],Cgs],Cgs_tr,Cgs_er,Ciss[0][0],True)
Cgd_eff 							=	Crss_eff
Rvec,Tvec							=	paramProcess.MOSFETrdson(switchesRdsonPath,'NVBLS1D1N08H','_Rdson')
Nvec,Ivec 							=	paramProcess.MOSFETrdson(switchesIdsonPath,'NVBLS1D1N08H','_Rdson')
Ioff,catOFF,Eoff					=	paramProcess.MOSFETenergies(switchesEoffPath,'NVBLS1D1N08H','_Eoff')
Voff,catOFF_Temp,Eoff_Temp			=	paramProcess.MOSFETenergies(switchesEoffPath,'NVBLS1D1N08H','_Eoff_Temp')
Ion,catON,Eon 						=	paramProcess.MOSFETenergies(switchesEonPath,'NVBLS1D1N08H','_Eon')
Von,catON_Temp,Eon_Temp				=	paramProcess.MOSFETenergies(switchesEonPath,'NVBLS1D1N08H','_Eon_Temp')
Vfvec,Ifvec,Rd,Vt					=	paramProcess.DiodeVI_data(bodyDiodeVIPath,'NVBLS1D1N08H')
Vds_vec,Ids_vec 					=	paramProcess.Forward_Transfer_data(switchesTransferPath,'NVBLS1D1N08H')

NVBLS1D1N08H		=	{																																	#*	NVBLS1D1N08H parameters
							'Config'						:	1																						,	#!	1->electric integrated | 2->electric separate | 3->thermal integrated | 4->thermal separate
							'Transistor'  			: 	{																									#!	transistors parameters
									'Config'				:	2																						,	#?	1->real model | 2->ideal model | 3->behavioral model
									'Thermal'           	:   ''                                  													,   #? 	selected transistor
									'Custom'            	:   []						               													,   #? 	transistor provided custom variables
									'g_fs'					:	1e6																						,	#?	forward transconductance
									'Rg'					:	1																						,	#?	internal gate resistance
									'Lg'					:	0																						,	#?	gate pin inductance
									'Rds_on'            	:   Rvec[-1][-1]*1e-3																		,   #? 	transistor ON resistance
									'Rds_off'				:	'inf'																					,	#?	transistor OFF resistance
									'Rvec'					:	(np.array(Rvec)*1e-3).tolist()														,	#?	absolute Rdson vector corresponding to junction temperature
									'Tvec'					:	Tvec 																					,	#?	junction temperature vector for Rdson
									'RTconfig'				:	1																						,	#?	choose which RT vector to be used
									'RdsonScale'			:	1.0																						,	#?	Rdson scaling to account for min, typ and max deviations
									'Nvec'					:	Nvec 																					,	#?	normalized Rdson vector corresponding to current
									'Ivec'					:	Ivec																					,	#?	current vector for normalized Rdson
									'NIconfig'				:	1																						,	#?	choose which NI vector to be used
									'IdsonScale'			:	1.0																						,	#?	Idson resistance scaling to account for min, typ and max deviations
									'Rsrc'					:	0																						,	#?	kelvin source pin resistance
									'Lsrc'					:	0																						,	#?	kelvin source pin inductance
									'Ls'					:	0																						,	#?	package source inductance
                                    'Ld'					:	0																						,	#?	package drain inductance
									'Rs'					:	0																						,	#?	package source resistance
									'Rd'					:	0																						,	#?	package drain inductance
									'Ksrc'					:	0																						,	#?	kelvin source option, 0->no kelvin | 1->kelvin
									'Vblock'            	:   80                                	 													,   #? 	transistor blocking voltage
									'Id'                	:   351                                 													,   #? 	transistor drain current
									'Tr'                	:   0                                   													,   #? 	transistor rise time
									'Tf'                	:   0                                       												, 	#? 	transistor fall time
									'Avalanche'		:	{																									#!	transistor avalanche parameters
										'Config'			:	2																						,	#?	1->enable | 2->disable
										'Voltage'			:	80																						,	#?	avalanche voltage
										'Resistance'		:	1e-3																						#?	avalanche resistance to break voltage state-dependency
									},
									'Transfer'		:	{																									#!	transistor forward transfer parameters
										'Vds'				:	Vds_vec																					,	#?	drain-source voltage vector
										'Vgs'				:	list(np.arange(0.0,12.0+0.4,0.4))													,	#?	gate-source voltage vector
										'Ids'				:	Ids_vec																					,	#?	drain current vector
										'Factor_ON'			:	1.0																						,	#?	scaling factor for Ids at turn ON
										'Factor_OFF'		:	1.0																						,	#?	scaling factor for Ids at turn OFF
										'Factor_Vgs_ON'		:	1.0																						,	#?	scaling factor for Vgs at turn ON
										'Factor_Vgs_OFF'	:	1.0																						,	#?	scaling factor for Vgs at turn OFF
										'Vcoss'				:	0																						,	#?	initial voltage of the Coss
									},
						},
							'BodyDiode'  			:	{																									#!	body diodes paramteters
									'Config'				:	4																						,	#?	1->non-ideal RR | 2->non-ideal | 3->ideal RR | 4->ideal
									'Thermal'           	:   ''                                  													,   #? 	separate body diode
									'Custom'            	:   []					                 													,   #? 	body diode provided custrom variables
									'Rd_on'             	:   Rd[-1]													                              	,  	#? 	body diode ON resistance
									'Rd_off'				:	'inf'																					,	#?	body diode OFF resistance
									'Vf'					:	Vt[-1]																					,	#? 	body diode forward voltage
									'If'                	:   351                                 													,   #? 	body diode forward current
									'dIr'               	:   100e6                                  													,   #? 	body diode current slope
									'Lrr'					:	1e-9																					,	#?	body diode reverse recovery inductance
									'Trr'               	:   92e-9                                  													,   #? 	body diode reverse recovery time
									'Irr'               	:   0                                   													,   #? 	body diode reverse recovery current
									'Qrr'               	:   234e-9                                  												,	#? 	body diode reverse recovery charge
									'Is'                  	:   50              																		, 	#? 	body diode reference current
									'Vs'					:	64																						,	#?	body diode reference voltage
                                    'VIcurve'		:	{																									#!	body diode VI characteristics
                                        'Vfvec'				:	Vfvec																					,	#?	forward voltage vector
                                        'Ifvec'				:	Ifvec																					,	#?	forward current vector
										'Rdvec'				:	Rd																						,	#?	dynamic resistance vector
										'Vtvec'				:	Vt																						,	#?	threshold voltage vector
                                        'Temps'				:	[-55,25,175]																			,	#?	temperature vector
                                        'Vfscale'			:	1.578																						#?	Vf scaling to account for min, typ and max deviations
									},
						},
							'GateDriver'			:	{																									#!	gate driver parameters
									'Config'				:	3																						,	#?	1->high-side | 2->low-side | 3->disable
									'Von'					:	12																						,	#?	ON driving voltage
									'Voff'					:	0																						,	#?	OFF driving voltage
									'Ron'					:	5																						,	#?	sourcing output resistance
									'Roff'					:	5																						,	#?	sinking output resistance
									'Lon'					:	0																						,	#?	sourcing output inductance
									'Loff'					:	0																						,	#?	sinking output inductance
									'Cload'					:	0																						,	#?	capacitive load on output
									'Rload'					:	'inf'																					,	#?	resistive load on output
									'Delay'					:	0																						,	#?	input-to-output total deadtime
									'Trise'					:	0																						,	#?	output rising time
									'Tfall'					:	0																						,	#?	output falling time
									'UVLO_Start'			:	7.0																						,	#?	UVLO startup voltage threshold
									'UVLO_Stop'				:	6.5																						,	#?	UVLO shutdown voltage threshold
									'UVLO_Delay'			:	100e-9																					,	#?	delay between UVLO startup and shutdown
									'Init_State'			:	0																						,	#?	initial toggling state, 0->OFF | 1->ON
									'CurrentLimit'	:	{																									#*	current limit of driver stage
										'Config'			:	2																						,	#?	1->enable | 2->disable
										'Ts'				: 	0 																						,	#?	sampling time between inductive & capacitive links
										'tau'				: 	0																						,	#?	first-order delay between inductive & capacitive links
                                    	'Rs'				: 	0																						,	#?	source impedance of inductive link
										'Cs'				:	1e-12																					,	#?	source capacitance of capacitive link
                                        'UpLim'				: 	10																						,	#?	max current limit on capacitive link
                                        'LoLim'				: 	-10																						,	#?	min current limit on capacitive link
                                        'Voffset'			: 	0																							#?	voltage offset between inductive & capacitive links
									},
									'Masking'		:	{																									#*	switching stages masking
										'ON'	:	{																										#	ON path masking
											'Config'		:	2																						,	#?	1->enable | 2->disable
											'HIGH'	:	{																									#!	HIGH mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[0, 0]																						#?	mask output
											},
											'LOW'	:	{																									#!	LOW mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[1, 1]																						#?	mask output
											}
										},
										'OFF'	:	{																										#	OFF path masking
											'Config'		:	2																						,	#?	1->enable | 2->disable
											'HIGH'	:	{																									#!	HIGH mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[0, 0]																						#?	mask output
											},
											'LOW'	:	{																									#!	LOW mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[1, 1]																						#?	mask output
											}
										}
									},
									'Boot'			:	{																									#*	bootstrap/charge pump parameters
										'Config'			:	1																						,	#?	1->bootstrap | 2->charge pump
										'Von'				:	14																						,	#?	boostrap driving voltage
										'Cboot'				:	4.7e-6																					,	#?	bootstrap capacitance
										'Vinit'				:	0																						,	#?	bootstrap capacitance initial voltage
										'Rboot'				:	10																						,	#?	bootstrap resistance
										'Vfboot'			:	0.87																					,	#?	bootstrap diode forward voltage
										'Rdboot'			:	1e-3																					,	#?	bootstrap diode ON-state resistance
										'Ichrg'				:	300e-6																					,	#?	charge pump supply current
										'Idis'				:	5e-6																					,	#?	charge pump loading or leakage current
										'Cpar'				:	0																						,	#?	charge pump parallel cap to break state/source dependency
									    'UVLO_Start'		:	11.6																					,	#?	threshold value to start the charge pump
										'UVLO_Stop'			:	12.4																						#?	threshold value to stop the charge pump
									},
							},
							'GateNetwork'			:	{																									#!	gate drive circuit parameters
									'Config'				:	2																						,	#?	1-> enable | 2->disable
									'ON_Path'		:	{																									#*	sourcing path parameters
										'Rg'				:	5																						,	#?	gate ON path resistance
										'Lg'				:	0																						,	#?	gate ON path inductance
										'Rload'				:	10e3																					,	#?	gate pull down resistance
										'Diode'	:	{																										#	reverse blocking diode parameters
											'Vf'			:	0																						,	#?	forward voltage
											'Rd_on'			:	0																						,	#?	ON-state resistance
										},
									},
									'OFF_Path'		:	{																									#*	sinking path parameters
										'Rg'				:	5																						,	#?	gate OFF path resistance
										'Lg'				:	0																						,	#?	gate OFF path inductance
										'Diode'	:	{																										#	reverse blocking diode parameters
											'Vf'			:	0																						,	#?	forward voltage
											'Rd_on'			:	0																						,	#?	ON-state resistance
										},
									},
									'NegVolt'		:	{																									#*	negative voltage generator parameters
										'Config'			:	2																						,	#?	1-> enable | 2->disable
										'Dz'	:	{																										#	zener diode parameters
											'Vf'			:	0.7																						,	#?	forward voltage
											'Rd_on'			:	1e-3																					,	#?	ON-state resistance
											'Vz'			:	2																						,	#?	Zener breakdown voltage
											'Rz'			:	1e-3																					,	#?	Zener resistance
										},
										'Dp'	:	{																										#	peak detector diode
											'Vf'			:	0.0																						,	#?	forward voltage
											'Rd_on'			:	0.0																						,	#?	ON-state resistance
										},
										'Cz'	:	{																										#	Zener capacitor parameters
											'Config'		:	1																						,	#?	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
											'Csingle'		:	1e-6																					,	#?	single capacitor value
											'Rsingle'		:	5e-3																					,	#?	ESR of single capacitor
											'Lsingle'		:	0																						,	#?	ESL of single capacitor
											'nPar'			:	1																						,	#?	number of parallel connections
											'nSer'			:	1																						,	#?	number of series connections
											'Vinit'			:	0																						,	#?	capacitor initial voltage
										},
										'Cp'	:	{																										#	peak detector capacitor parameters
											'Config'		:	1																						,	#?	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
											'Csingle'		:	2.2e-6																					,	#?	single capacitor value
											'Rsingle'		:	5e-3																					,	#?	ESR of single capacitor
											'Lsingle'		:	0																						,	#?	ESL of single capacitor
											'nPar'			:	1																						,	#?	number of parallel connections
											'nSer'			:	1																						,	#?	number of series connections
											'Vinit'			:	0																						,	#?	capacitor initial voltage
										},
										'Rp1'				:	43																						,	#?	current limiter of peak detector current
										'Rp2'				:	4.7e3																					,	#?	load resistor to charge the zener diode
									},
								},
							'nParallel'   					:	1                                       												,   #? 	number of parallel devices
							'Rth_jc'						:	0.48																					,	#?	junction-to-case thermal resistance
							'Cth_jc'						:	0.00																					,	#?	junction-to-case thermal capacitance
							'Rth_ca'              			:   [0.292,0.258,0.856,0.228,0.3]            												,   #? 	case-to-ambient thermal resistance
							'Cth_ca'              			:   [0.788,0.205,15.91,3.716,0.015]             											,   #? 	case-to-ambient thermal capacitance
							'Tinit'							:	0.0																						,	#?	initial juntion temperature
							'Pinit'							:	0.0																						,	#?	initial power dissipation
							'Coss'					: 	{																									#!	device Coss parameters
								'C'							:	Coss_eff					 															,	#?	device parasitic output capacitance
								'R'							:	0																						,	#?	Coss resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Coss inductance to reduce current slope
								'Coss_er'					:	Crss_er																					,	#?	energy-related Coss
								'Coss_tr'					:	Coss_tr																					,	#?	time-related Coss
								'Vvec'						:	Coss[0]																					,	#? 	device Coss voltage vector
								'Cvec'						:	Coss[1]																					,	#?	device Coss capacity vector
								'Offset'					:	0																						,	#?	parasitic offset to Coss
                                'Factor'					:	1.0																						,	#?	parasitic tolerance to Coss
								'Qoss'						:	Qoss																					,	#?	equivalent charge of Coss
								'Eoss'						:	Eoss																					,	#?	equivalent energy of Coss
								'Config'					:	5																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
						},
                        	'Crss'					:	{																									#!	device Crss parameters
                                'C'							:	Crss_eff					 															,	#?	device parasitic reverse transfer capacitance
								'R'							:	0																						,	#?	Crss resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Crss inductance to reduce current slope
								'Crss_er'					:	Crss_er																					,	#?	energy-related Crss
								'Crss_tr'					:	Crss_tr																					,	#?	time-related Crss
								'Vvec'						:	Crss[0]																					,	#?	device Crss voltage vector
                                'Cvec'						:	Crss[1]																					,	#?	device Crss capacity vector
								'Qvec'						:	Qrss																					,	#?	device accumulated Crss charge vector
								'Offset'					:	0																						,	#?	parasitic offset to Crss
								'Factor'					:	1.0																						,	#?	parasitic tolerance to Crss
								'Qrss'						:	Qrss																					,	#?	equivalent charge of Crss
								'Erss'						:	Erss																					,	#?	equivalent energe of Crss
								'Config'					:	5																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
						},
							'Ciss'					:	{																									#!	device Ciss parameters
								'C'							:	Ciss_eff					 															,	#?	device parasitic input capacitance
								'R'							:	0																						,	#?	Ciss resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Ciss inductance to reduce current slope
								'Ciss_er'					:	Ciss_er																					,	#?	energy-related Ciss
								'Ciss_tr'					:	Ciss_tr																					,	#?	time-related Ciss
								'Vvec'						:	Ciss[0]																					,	#?	device Ciss voltage vector
								'Cvec'						:	Ciss[1]																					,	#?	device Ciss capacity vector
								'Offset'					:	0																						,	#?	parasitic offset to Ciss
								'Factor'					:	1.0																						,	#?	parasitic tolerance to Ciss
								'Qiss'						:	Qiss																					,	#?	equivalent charge of Ciss
								'Eiss'						:	Eiss																					,	#?	equivalent energy of Ciss
								'Config'					:	5																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Cds'					:	{																									#!	device Cds parameters
								'C'							:	Cds_eff					 																,	#?	device parasitic Cds capacitance
								'R'							:	0																						,	#?	Cds resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Cds inductance to reduce current slope
								'Cds_er'					:	Cds_er																					,	#?	energy-related Cds
								'Cds_tr'					:	Cds_tr																					,	#?	time-related Cds
								'Vvec'						:	Coss[0]																					,	#?	device Cds voltage vector
								'Cvec'						:	Cds																						,	#?	device Cds capacity vector
								'Offset_ON'					:	0																						,	#?	tuning offset for turn ON
								'Offset_OFF'				:	0																						,	#?	tuning offset for turn OFF
								'Factor_ON'					:	1.0																						,	#?	tuning factor for turn ON
								'Factor_OFF'				:	1.0																						,	#?	tuning factor for turn OFF
								'Config'					:	4																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Cgd'					:	{																									#!	device Cgd parameters
								'C'							:	Cgd_eff							 														,	#?	device parasitic Cgd capacitance
								'R'							:	0																						,	#?	Cgd resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Cgd inductance to reduce current slope
								'Cgd_er'					:	Cgd_er																					,	#?	energy-related Cgd
								'Cgd_tr'					:	Cgd_tr																					,	#?	time-related Cgd
								'Vvec'						:	Crss[0]																					,	#?	device Cgd voltage vector
								'Cvec'						:	Cgd																						,	#?	device Cgd capacity vector
								'Offset_ON'					:	0																						,	#?	tuning offset for turn ON
								'Offset_OFF'				:	0																						,	#?	tuning offset for turn OFF
								'Factor_ON'					:	1.0																						,	#?	tuning factor for turn ON
								'Factor_OFF'				:	1.0																						,	#?	tuning factor for turn OFF
								'Config'					:	4																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Cgs'					:	{																									#!	device Cgs parameters
								'C'							:	Cgs_eff					 																,	#?	device parasitic Cgs capacitance
								'R'							:	0																						,	#?	Cgs resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Cgs inductance to reduce current slope
								'Cgs_er'					:	Cgs_er																					,	#?	energy-related Cgs
								'Cgs_tr'					:	Cgs_tr																					,	#?	time-related Cgs
								'Vvec'						:	Ciss[0]																					,	#?	device Cgs voltage vector
								'Cvec'						:	Cgs																						,	#?	device Cgs capacity vector
								'Offset_ON'					:	0																						,	#?	tuning offset for turn ON
								'Offset_OFF'				:	0																						,	#?	tuning offset for turn OFF
								'Factor_ON'					:	1.0																						,	#?	tuning factor for turn ON
								'Factor_OFF'				:	1.0																						,	#?	tuning factor for turn OFF
								'Config'					:	4																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Eoff'					:	{																									#!	transistor turn-OFF energy losses
									'Ivec'					:	Ioff																					,	#?	turn-OFF energy current vector
									'Rgvec'					:	[0,100]																					,	#?	OFF path gate resistances vector
									'Tjvec'					:	[-55,175]																				,	#?	junction temperature vector
                                    'Vvec'					:	Voff																					,	#?	turn-OFF voltage vector
                                    'Evec'					:	Eoff																					,	#?	turn-OFF energy vectors
									'Evec_Temp'				:	Eoff_Temp																				,	#?	turn-OFF energy temp scaling vectors
                                    'CAT'					:	catOFF																					,	#?	octave Eoff energy syntax
									'CAT_Temp'				:	catOFF_Temp																				,	#?	octave Eoff energy temp scaling syntax
									'Vgs'					:	0																						,	#?	used OFF path gate-source voltage
									'Vth'					:	1.5																						,	#?	used OFF path threshold voltage
									'Rg'					:	0																							#?	used OFF path gate resistance
						},
							'Eon'					:	{																									#!	transistor turn-ON energy losses
									'Ivec'					:	Ion																						,	#?	turn-ON energy current vector
									'Rgvec'					:	[0,100]																					,	#?	ON path gate resistances vector
									'Tjvec'					:	[-55,175]																				,	#?	junction temperature vector
                                    'Vvec'					:	Von																						,	#?	turn-ON voltage vector
                                    'Evec'					:	Eon																						,	#?	turn-ON energy vectors
									'Evec_Temp'				:	Eon_Temp																				,	#?	turn-ON energy temp scaling vectors
                                    'CAT'					:	catON																					,	#?	octave Eon energy syntax
									'CAT_Temp'				:	catON_Temp																				,	#?	octave Eon energy temp scaling syntax
									'Vgs'					:	12																						,	#?	used ON path gate-source voltage
									'Vth'					:	1.5																						,	#?	used ON path threshold voltage
									'Rg'					:	0																							#?	used ON path gate resistance
						},
							'Tau_deg'						:	100e-9																					,	#?	deglitch filter for currents and voltages
							'RCsnubber'						:	2																						,	#?	1->enable | 2->disable
						}

#?----------------------------------------------------------------------------------------------------------------------------------------------------------------------

Coss,Qoss,Eoss,Coss_tr,Coss_er		=	paramProcess.MOSFETcaps(switchesCossPath,'FDBL86361','_Coss')
Crss,Qrss,Erss,Crss_tr,Crss_er 		=	paramProcess.MOSFETcaps(switchesCrssPath,'FDBL86361','_Crss')
Ciss,Qiss,Eiss,Ciss_tr,Ciss_er 		=	paramProcess.MOSFETcaps(switchesCissPath,'FDBL86361','_Ciss')
Coss_eff 							=	paramProcess.getCmos(Coss,Coss_tr,Coss_er,Coss[0][0],True)
Ciss_eff 							=	paramProcess.getCmos(Ciss,Ciss_tr,Ciss_er,Ciss[0][0],True)
Crss_eff 							=	paramProcess.getCmos(Crss,Crss_tr,Crss_er,Crss[0][0],True)
Cds 						        =	(np.array(Coss[1]) - np.array(Crss[1])).tolist()
Cgs						        	=	(np.array(Ciss[1]) - np.array(Crss[1])).tolist()
Cgd						        	=	Crss[1]
Cds_tr						        =	(np.array(Coss_tr) - np.array(Crss_tr)).tolist()
Cgs_tr						        =	(np.array(Ciss_tr) - np.array(Crss_tr)).tolist()
Cgd_tr						        =	Crss_tr
Cds_er						        =	(np.array(Coss_er) - np.array(Crss_er)).tolist()
Cgs_er						        =	(np.array(Ciss_er) - np.array(Crss_er)).tolist()
Cgd_er						        =	Crss_er
Cds_eff 							=	paramProcess.getCmos([Coss[0],Cds],Cds_tr,Cds_er,Coss[0][0],True)
Cgs_eff 							=	paramProcess.getCmos([Ciss[0],Cgs],Cgs_tr,Cgs_er,Ciss[0][0],True)
Cgd_eff 							=	Crss_eff
Rvec,Tvec							=	paramProcess.MOSFETrdson(switchesRdsonPath,'FDBL86361','_Rdson')
Nvec,Ivec 							=	paramProcess.MOSFETrdson(switchesIdsonPath,'FDBL86361','_Rdson')
Ioff,catOFF,Eoff					=	paramProcess.MOSFETenergies(switchesEoffPath,'FDBL86361','_Eoff')
Voff,catOFF_Temp,Eoff_Temp			=	paramProcess.MOSFETenergies(switchesEoffPath,'FDBL86361','_Eoff_Temp')
Ion,catON,Eon 						=	paramProcess.MOSFETenergies(switchesEonPath,'FDBL86361','_Eon')
Von,catON_Temp,Eon_Temp				=	paramProcess.MOSFETenergies(switchesEonPath,'FDBL86361','_Eon_Temp')
Vfvec,Ifvec,Rd,Vt					=	paramProcess.DiodeVI_data(bodyDiodeVIPath,'FDBL86361')
Vds_vec,Ids_vec 					=	paramProcess.Forward_Transfer_data(switchesTransferPath,'FDBL86361')

FDBL86361			=	{																																	#*	FDBL86361 parameters
							'Config'						:	1																						,	#!	1->electric integrated | 2->electric separate | 3->thermal integrated | 4->thermal separate
							'Transistor'  			: 	{																									#!	transistors parameters
									'Config'				:	2																						,	#?	1->real model | 2->ideal model | 3->behavioral model
									'Thermal'           	:   ''                                  													,   #? 	selected transistor
									'Custom'            	:   []						               													,   #? 	transistor provided custom variables
									'g_fs'					:	1e6																						,	#?	forward transconductance
									'Rg'					:	1																						,	#?	internal gate resistance
									'Lg'					:	0																						,	#?	gate pin inductance
									'Rds_on'            	:   Rvec[-1][-1]*1e-3																		,   #? 	transistor ON resistance
									'Rds_off'				:	'inf'																					,	#?	transistor OFF resistance
									'Rvec'					:	(np.array(Rvec)*1e-3).tolist()														,	#?	absolute Rdson vector corresponding to junction temperature
									'Tvec'					:	Tvec 																					,	#?	junction temperature vector for Rdson
									'RTconfig'				:	1																						,	#?	choose which RT vector to be used
									'RdsonScale'			:	1.0																						,	#?	Rdson scaling to account for min, typ and max deviations
									'Nvec'					:	Nvec 																					,	#?	normalized Rdson vector corresponding to current
									'Ivec'					:	Ivec																					,	#?	current vector for normalized Rdson
									'NIconfig'				:	1																						,	#?	choose which NI vector to be used
									'IdsonScale'			:	1.0																						,	#?	Idson resistance scaling to account for min, typ and max deviations
									'Rsrc'					:	0																						,	#?	kelvin source pin resistance
									'Lsrc'					:	0																						,	#?	kelvin source pin inductance
									'Ls'					:	0																						,	#?	package source inductance
                                    'Ld'					:	0																						,	#?	package drain inductance
									'Rs'					:	0																						,	#?	package source resistance
									'Rd'					:	0																						,	#?	package drain inductance
									'Ksrc'					:	0																						,	#?	kelvin source option, 0->no kelvin | 1->kelvin
									'Vblock'            	:   80                                	 													,   #? 	transistor blocking voltage
									'Id'                	:   300                                 													,   #? 	transistor drain current
									'Tr'                	:   0                                   													,   #? 	transistor rise time
									'Tf'                	:   0                                       												, 	#? 	transistor fall time
									'Avalanche'		:	{																									#!	transistor avalanche parameters
										'Config'			:	2																						,	#?	1->enable | 2->disable
										'Voltage'			:	80																						,	#?	avalanche voltage
										'Resistance'		:	1e-3																						#?	avalanche resistance to break voltage state-dependency
									},
									'Transfer'		:	{																									#!	transistor forward transfer parameters
										'Vds'				:	Vds_vec																					,	#?	drain-source voltage vector
										'Vgs'				:	list(np.arange(0.0,12.0+0.4,0.4))													,	#?	gate-source voltage vector
										'Ids'				:	Ids_vec																					,	#?	drain current vector
										'Factor_ON'			:	1.0																						,	#?	scaling factor for Ids at turn ON
										'Factor_OFF'		:	1.0																						,	#?	scaling factor for Ids at turn OFF
										'Factor_Vgs_ON'		:	1.0																						,	#?	scaling factor for Vgs at turn ON
										'Factor_Vgs_OFF'	:	1.0																						,	#?	scaling factor for Vgs at turn OFF
										'Vcoss'				:	0																						,	#?	initial voltage of the Coss
									},
						},
							'BodyDiode'  			:	{																									#!	body diodes paramteters
									'Config'				:	4																						,	#?	1->non-ideal RR | 2->non-ideal | 3->ideal RR | 4->ideal
									'Thermal'           	:   ''                                  													,   #? 	separate body diode
									'Custom'            	:   []					                 													,   #? 	body diode provided custrom variables
									'Rd_on'             	:   Rd[-1]													                              	,  	#? 	body diode ON resistance
									'Rd_off'				:	'inf'																					,	#?	body diode OFF resistance
									'Vf'					:	Vt[-1]																					,	#? 	body diode forward voltage
									'If'                	:   300                                 													,   #? 	body diode forward current
									'dIr'               	:   100e6                                  													,   #? 	body diode current slope
									'Lrr'					:	1e-9																					,	#?	body diode reverse recovery inductance
									'Trr'               	:   136e-9                                 													,   #? 	body diode reverse recovery time
									'Irr'               	:   0                                   													,   #? 	body diode reverse recovery current
									'Qrr'               	:   269e-9                                  												,	#? 	body diode reverse recovery charge
									'Is'                  	:   80              																		, 	#? 	body diode reference current
									'Vs'					:	64																						,	#?	body diode reference voltage
                                    'VIcurve'		:	{																									#!	body diode VI characteristics
                                        'Vfvec'				:	Vfvec																					,	#?	forward voltage vector
                                        'Ifvec'				:	Ifvec																					,	#?	forward current vector
										'Rdvec'				:	Rd																						,	#?	dynamic resistance vector
										'Vtvec'				:	Vt																						,	#?	threshold voltage vector
                                        'Temps'				:	[25,175]																				,	#?	temperature vector
                                        'Vfscale'			:	1.563																						#?	Vf scaling to account for min, typ and max deviations
									},
						},
							'GateDriver'			:	{																									#!	gate driver parameters
									'Config'				:	3																						,	#?	1->high-side | 2->low-side | 3->disable
									'Von'					:	12																						,	#?	ON driving voltage
									'Voff'					:	0																						,	#?	OFF driving voltage
									'Ron'					:	5																						,	#?	sourcing output resistance
									'Roff'					:	5																						,	#?	sinking output resistance
									'Lon'					:	0																						,	#?	sourcing output inductance
									'Loff'					:	0																						,	#?	sinking output inductance
									'Cload'					:	0																						,	#?	capacitive load on output
									'Rload'					:	'inf'																					,	#?	resistive load on output
									'Delay'					:	0																						,	#?	input-to-output total deadtime
									'Trise'					:	0																						,	#?	output rising time
									'Tfall'					:	0																						,	#?	output falling time
									'UVLO_Start'			:	7.0																						,	#?	UVLO startup voltage threshold
									'UVLO_Stop'				:	6.5																						,	#?	UVLO shutdown voltage threshold
									'UVLO_Delay'			:	100e-9																					,	#?	delay between UVLO startup and shutdown
									'Init_State'			:	0																						,	#?	initial toggling state, 0->OFF | 1->ON
									'CurrentLimit'	:	{																									#*	current limit of driver stage
										'Config'			:	2																						,	#?	1->enable | 2->disable
										'Ts'				: 	0 																						,	#?	sampling time between inductive & capacitive links
										'tau'				: 	0																						,	#?	first-order delay between inductive & capacitive links
                                    	'Rs'				: 	0																						,	#?	source impedance of inductive link
										'Cs'				:	1e-12																					,	#?	source capacitance of capacitive link
                                        'UpLim'				: 	10																						,	#?	max current limit on capacitive link
                                        'LoLim'				: 	-10																						,	#?	min current limit on capacitive link
                                        'Voffset'			: 	0																							#?	voltage offset between inductive & capacitive links
									},
									'Masking'		:	{																									#*	switching stages masking
										'ON'	:	{																										#	ON path masking
											'Config'		:	2																						,	#?	1->enable | 2->disable
											'HIGH'	:	{																									#!	HIGH mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[0, 0]																						#?	mask output
											},
											'LOW'	:	{																									#!	LOW mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[1, 1]																						#?	mask output
											}
										},
										'OFF'	:	{																										#	OFF path masking
											'Config'		:	2																						,	#?	1->enable | 2->disable
											'HIGH'	:	{																									#!	HIGH mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[0, 0]																						#?	mask output
											},
											'LOW'	:	{																									#!	LOW mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[1, 1]																						#?	mask output
											}
										}
									},
									'Boot'			:	{																									#*	bootstrap/charge pump parameters
										'Config'			:	1																						,	#?	1->bootstrap | 2->charge pump
										'Von'				:	14																						,	#?	boostrap driving voltage
										'Cboot'				:	4.7e-6																					,	#?	bootstrap capacitance
										'Vinit'				:	0																						,	#?	bootstrap capacitance initial voltage
										'Rboot'				:	10																						,	#?	bootstrap resistance
										'Vfboot'			:	0.87																					,	#?	bootstrap diode forward voltage
										'Rdboot'			:	1e-3																					,	#?	bootstrap diode ON-state resistance
										'Ichrg'				:	300e-6																					,	#?	charge pump supply current
										'Idis'				:	5e-6																					,	#?	charge pump loading or leakage current
										'Cpar'				:	0																						,	#?	charge pump parallel cap to break state/source dependency
									    'UVLO_Start'		:	11.6																					,	#?	threshold value to start the charge pump
										'UVLO_Stop'			:	12.4																						#?	threshold value to stop the charge pump
									},
							},
							'GateNetwork'			:	{																									#!	gate drive circuit parameters
									'Config'				:	2																						,	#?	1-> enable | 2->disable
									'ON_Path'		:	{																									#*	sourcing path parameters
										'Rg'				:	5																						,	#?	gate ON path resistance
										'Lg'				:	0																						,	#?	gate ON path inductance
										'Rload'				:	10e3																					,	#?	gate pull down resistance
										'Diode'	:	{																										#	reverse blocking diode parameters
											'Vf'			:	0																						,	#?	forward voltage
											'Rd_on'			:	0																						,	#?	ON-state resistance
										},
									},
									'OFF_Path'		:	{																									#*	sinking path parameters
										'Rg'				:	5																						,	#?	gate OFF path resistance
										'Lg'				:	0																						,	#?	gate OFF path inductance
										'Diode'	:	{																										#	reverse blocking diode parameters
											'Vf'			:	0																						,	#?	forward voltage
											'Rd_on'			:	0																						,	#?	ON-state resistance
										},
									},
									'NegVolt'		:	{																									#*	negative voltage generator parameters
										'Config'			:	2																						,	#?	1-> enable | 2->disable
										'Dz'	:	{																										#	zener diode parameters
											'Vf'			:	0.7																						,	#?	forward voltage
											'Rd_on'			:	1e-3																					,	#?	ON-state resistance
											'Vz'			:	2																						,	#?	Zener breakdown voltage
											'Rz'			:	1e-3																					,	#?	Zener resistance
										},
										'Dp'	:	{																										#	peak detector diode
											'Vf'			:	0.0																						,	#?	forward voltage
											'Rd_on'			:	0.0																						,	#?	ON-state resistance
										},
										'Cz'	:	{																										#	Zener capacitor parameters
											'Config'		:	1																						,	#?	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
											'Csingle'		:	1e-6																					,	#?	single capacitor value
											'Rsingle'		:	5e-3																					,	#?	ESR of single capacitor
											'Lsingle'		:	0																						,	#?	ESL of single capacitor
											'nPar'			:	1																						,	#?	number of parallel connections
											'nSer'			:	1																						,	#?	number of series connections
											'Vinit'			:	0																						,	#?	capacitor initial voltage
										},
										'Cp'	:	{																										#	peak detector capacitor parameters
											'Config'		:	1																						,	#?	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
											'Csingle'		:	2.2e-6																					,	#?	single capacitor value
											'Rsingle'		:	5e-3																					,	#?	ESR of single capacitor
											'Lsingle'		:	0																						,	#?	ESL of single capacitor
											'nPar'			:	1																						,	#?	number of parallel connections
											'nSer'			:	1																						,	#?	number of series connections
											'Vinit'			:	0																						,	#?	capacitor initial voltage
										},
										'Rp1'				:	43																						,	#?	current limiter of peak detector current
										'Rp2'				:	4.7e3																					,	#?	load resistor to charge the zener diode
									},
								},
							'nParallel'   					:	1                                       												,   #? 	number of parallel devices
							'Rth_jc'						:	0.35																					,	#?	junction-to-case thermal resistance
							'Cth_jc'						:	0.00																					,	#?	junction-to-case thermal capacitance
							'Rth_ca'              			:   [0.292,0.258,0.856,0.228,0.3]            												,   #? 	case-to-ambient thermal resistance
							'Cth_ca'              			:   [0.788,0.205,15.91,3.716,0.015]             											,   #? 	case-to-ambient thermal capacitance
							'Tinit'							:	0.0																						,	#?	initial juntion temperature
							'Pinit'							:	0.0																						,	#?	initial power dissipation
							'Coss'					: 	{																									#!	device Coss parameters
								'C'							:	Coss_eff					 															,	#?	device parasitic output capacitance
								'R'							:	0																						,	#?	Coss resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Coss inductance to reduce current slope
								'Coss_er'					:	Crss_er																					,	#?	energy-related Coss
								'Coss_tr'					:	Coss_tr																					,	#?	time-related Coss
								'Vvec'						:	Coss[0]																					,	#? 	device Coss voltage vector
								'Cvec'						:	Coss[1]																					,	#?	device Coss capacity vector
								'Offset'					:	0																						,	#?	parasitic offset to Coss
                                'Factor'					:	1.0																						,	#?	parasitic tolerance to Coss
								'Qoss'						:	Qoss																					,	#?	equivalent charge of Coss
								'Eoss'						:	Eoss																					,	#?	equivalent energy of Coss
								'Config'					:	5																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
						},
                        	'Crss'					:	{																									#!	device Crss parameters
                                'C'							:	Crss_eff					 															,	#?	device parasitic reverse transfer capacitance
								'R'							:	0																						,	#?	Crss resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Crss inductance to reduce current slope
								'Crss_er'					:	Crss_er																					,	#?	energy-related Crss
								'Crss_tr'					:	Crss_tr																					,	#?	time-related Crss
								'Vvec'						:	Crss[0]																					,	#?	device Crss voltage vector
                                'Cvec'						:	Crss[1]																					,	#?	device Crss capacity vector
								'Qvec'						:	Qrss																					,	#?	device accumulated Crss charge vector
								'Offset'					:	0																						,	#?	parasitic offset to Crss
								'Factor'					:	1.0																						,	#?	parasitic tolerance to Crss
								'Qrss'						:	Qrss																					,	#?	equivalent charge of Crss
								'Erss'						:	Erss																					,	#?	equivalent energe of Crss
								'Config'					:	5																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
						},
							'Ciss'					:	{																									#!	device Ciss parameters
								'C'							:	Ciss_eff					 															,	#?	device parasitic input capacitance
								'R'							:	0																						,	#?	Ciss resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Ciss inductance to reduce current slope
								'Ciss_er'					:	Ciss_er																					,	#?	energy-related Ciss
								'Ciss_tr'					:	Ciss_tr																					,	#?	time-related Ciss
								'Vvec'						:	Ciss[0]																					,	#?	device Ciss voltage vector
								'Cvec'						:	Ciss[1]																					,	#?	device Ciss capacity vector
								'Offset'					:	0																						,	#?	parasitic offset to Ciss
								'Factor'					:	1.0																						,	#?	parasitic tolerance to Ciss
								'Qiss'						:	Qiss																					,	#?	equivalent charge of Ciss
								'Eiss'						:	Eiss																					,	#?	equivalent energy of Ciss
								'Config'					:	5																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Cds'					:	{																									#!	device Cds parameters
								'C'							:	Cds_eff					 																,	#?	device parasitic Cds capacitance
								'R'							:	0																						,	#?	Cds resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Cds inductance to reduce current slope
								'Cds_er'					:	Cds_er																					,	#?	energy-related Cds
								'Cds_tr'					:	Cds_tr																					,	#?	time-related Cds
								'Vvec'						:	Coss[0]																					,	#?	device Cds voltage vector
								'Cvec'						:	Cds																						,	#?	device Cds capacity vector
								'Offset_ON'					:	0																						,	#?	tuning offset for turn ON
								'Offset_OFF'				:	0																						,	#?	tuning offset for turn OFF
								'Factor_ON'					:	1.0																						,	#?	tuning factor for turn ON
								'Factor_OFF'				:	1.0																						,	#?	tuning factor for turn OFF
								'Config'					:	4																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Cgd'					:	{																									#!	device Cgd parameters
								'C'							:	Cgd_eff							 														,	#?	device parasitic Cgd capacitance
								'R'							:	0																						,	#?	Cgd resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Cgd inductance to reduce current slope
								'Cgd_er'					:	Cgd_er																					,	#?	energy-related Cgd
								'Cgd_tr'					:	Cgd_tr																					,	#?	time-related Cgd
								'Vvec'						:	Crss[0]																					,	#?	device Cgd voltage vector
								'Cvec'						:	Cgd																						,	#?	device Cgd capacity vector
								'Offset_ON'					:	0																						,	#?	tuning offset for turn ON
								'Offset_OFF'				:	0																						,	#?	tuning offset for turn OFF
								'Factor_ON'					:	1.0																						,	#?	tuning factor for turn ON
								'Factor_OFF'				:	1.0																						,	#?	tuning factor for turn OFF
								'Config'					:	4																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Cgs'					:	{																									#!	device Cgs parameters
								'C'							:	Cgs_eff					 																,	#?	device parasitic Cgs capacitance
								'R'							:	0																						,	#?	Cgs resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Cgs inductance to reduce current slope
								'Cgs_er'					:	Cgs_er																					,	#?	energy-related Cgs
								'Cgs_tr'					:	Cgs_tr																					,	#?	time-related Cgs
								'Vvec'						:	Ciss[0]																					,	#?	device Cgs voltage vector
								'Cvec'						:	Cgs																						,	#?	device Cgs capacity vector
								'Offset_ON'					:	0																						,	#?	tuning offset for turn ON
								'Offset_OFF'				:	0																						,	#?	tuning offset for turn OFF
								'Factor_ON'					:	1.0																						,	#?	tuning factor for turn ON
								'Factor_OFF'				:	1.0																						,	#?	tuning factor for turn OFF
								'Config'					:	4																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Eoff'					:	{																									#!	transistor turn-OFF energy losses
									'Ivec'					:	Ioff																					,	#?	turn-OFF energy current vector
									'Rgvec'					:	[0,100]																					,	#?	OFF path gate resistances vector
									'Tjvec'					:	[-55,175]																				,	#?	junction temperature vector
                                    'Vvec'					:	Voff																					,	#?	turn-OFF voltage vector
                                    'Evec'					:	Eoff																					,	#?	turn-OFF energy vectors
									'Evec_Temp'				:	Eoff_Temp																				,	#?	turn-OFF energy temp scaling vectors
                                    'CAT'					:	catOFF																					,	#?	octave Eoff energy syntax
									'CAT_Temp'				:	catOFF_Temp																				,	#?	octave Eoff energy temp scaling syntax
									'Vgs'					:	0																						,	#?	used OFF path gate-source voltage
									'Vth'					:	1.5																						,	#?	used OFF path threshold voltage
									'Rg'					:	0																							#?	used OFF path gate resistance
						},
							'Eon'					:	{																									#!	transistor turn-ON energy losses
									'Ivec'					:	Ion																						,	#?	turn-ON energy current vector
									'Rgvec'					:	[0,100]																					,	#?	ON path gate resistances vector
									'Tjvec'					:	[-55,175]																				,	#?	junction temperature vector
                                    'Vvec'					:	Von																						,	#?	turn-ON voltage vector
                                    'Evec'					:	Eon																						,	#?	turn-ON energy vectors
									'Evec_Temp'				:	Eon_Temp																				,	#?	turn-ON energy temp scaling vectors
                                    'CAT'					:	catON																					,	#?	octave Eon energy syntax
									'CAT_Temp'				:	catON_Temp																				,	#?	octave Eon energy temp scaling syntax
									'Vgs'					:	12																						,	#?	used ON path gate-source voltage
									'Vth'					:	1.5																						,	#?	used ON path threshold voltage
									'Rg'					:	0																							#?	used ON path gate resistance
						},
							'Tau_deg'						:	100e-9																					,	#?	deglitch filter for currents and voltages
							'RCsnubber'						:	2																						,	#?	1->enable | 2->disable
						}

#?----------------------------------------------------------------------------------------------------------------------------------------------------------------------

Coss,Qoss,Eoss,Coss_tr,Coss_er		=	paramProcess.MOSFETcaps(switchesCossPath,'NVBLS1D7N08H','_Coss')
Crss,Qrss,Erss,Crss_tr,Crss_er 		=	paramProcess.MOSFETcaps(switchesCrssPath,'NVBLS1D7N08H','_Crss')
Ciss,Qiss,Eiss,Ciss_tr,Ciss_er 		=	paramProcess.MOSFETcaps(switchesCissPath,'NVBLS1D7N08H','_Ciss')
Coss_eff 							=	paramProcess.getCmos(Coss,Coss_tr,Coss_er,Coss[0][0],True)
Ciss_eff 							=	paramProcess.getCmos(Ciss,Ciss_tr,Ciss_er,Ciss[0][0],True)
Crss_eff 							=	paramProcess.getCmos(Crss,Crss_tr,Crss_er,Crss[0][0],True)
Cds 						        =	(np.array(Coss[1]) - np.array(Crss[1])).tolist()
Cgs						        	=	(np.array(Ciss[1]) - np.array(Crss[1])).tolist()
Cgd						        	=	Crss[1]
Cds_tr						        =	(np.array(Coss_tr) - np.array(Crss_tr)).tolist()
Cgs_tr						        =	(np.array(Ciss_tr) - np.array(Crss_tr)).tolist()
Cgd_tr						        =	Crss_tr
Cds_er						        =	(np.array(Coss_er) - np.array(Crss_er)).tolist()
Cgs_er						        =	(np.array(Ciss_er) - np.array(Crss_er)).tolist()
Cgd_er						        =	Crss_er
Cds_eff 							=	paramProcess.getCmos([Coss[0],Cds],Cds_tr,Cds_er,Coss[0][0],True)
Cgs_eff 							=	paramProcess.getCmos([Ciss[0],Cgs],Cgs_tr,Cgs_er,Ciss[0][0],True)
Cgd_eff 							=	Crss_eff
Rvec,Tvec							=	paramProcess.MOSFETrdson(switchesRdsonPath,'NVBLS1D7N08H','_Rdson')
Nvec,Ivec 							=	paramProcess.MOSFETrdson(switchesIdsonPath,'NVBLS1D7N08H','_Rdson')
Ioff,catOFF,Eoff					=	paramProcess.MOSFETenergies(switchesEoffPath,'NVBLS1D7N08H','_Eoff')
Voff,catOFF_Temp,Eoff_Temp			=	paramProcess.MOSFETenergies(switchesEoffPath,'NVBLS1D7N08H','_Eoff_Temp')
Ion,catON,Eon 						=	paramProcess.MOSFETenergies(switchesEonPath,'NVBLS1D7N08H','_Eon')
Von,catON_Temp,Eon_Temp				=	paramProcess.MOSFETenergies(switchesEonPath,'NVBLS1D7N08H','_Eon_Temp')
Vfvec,Ifvec,Rd,Vt					=	paramProcess.DiodeVI_data(bodyDiodeVIPath,'NVBLS1D7N08H')
Vds_vec,Ids_vec 					=	paramProcess.Forward_Transfer_data(switchesTransferPath,'NVBLS1D7N08H')

NVBLS1D7N08H		=	{																																	#*	FDBL86361 parameters
							'Config'						:	1																						,	#!	1->electric integrated | 2->electric separate | 3->thermal integrated | 4->thermal separate
							'Transistor'  			: 	{																									#!	transistors parameters
									'Config'				:	2																						,	#?	1->real model | 2->ideal model | 3->behavioral model
									'Thermal'           	:   ''                                  													,   #? 	selected transistor
									'Custom'            	:   []						               													,   #? 	transistor provided custom variables
									'g_fs'					:	1e6																						,	#?	forward transconductance
									'Rg'					:	1																						,	#?	internal gate resistance
									'Lg'					:	0																						,	#?	gate pin inductance
									'Rds_on'            	:   Rvec[-1][-1]*1e-3																		,   #? 	transistor ON resistance
									'Rds_off'				:	'inf'																					,	#?	transistor OFF resistance
									'Rvec'					:	(np.array(Rvec)*1e-3).tolist()														,	#?	absolute Rdson vector corresponding to junction temperature
									'Tvec'					:	Tvec 																					,	#?	junction temperature vector for Rdson
									'RTconfig'				:	1																						,	#?	choose which RT vector to be used
									'RdsonScale'			:	1.0																						,	#?	Rdson scaling to account for min, typ and max deviations
									'Nvec'					:	Nvec 																					,	#?	normalized Rdson vector corresponding to current
									'Ivec'					:	Ivec																					,	#?	current vector for normalized Rdson
									'NIconfig'				:	1																						,	#?	choose which NI vector to be used
									'IdsonScale'			:	1.0																						,	#?	Idson resistance scaling to account for min, typ and max deviations
									'Rsrc'					:	0																						,	#?	kelvin source pin resistance
									'Lsrc'					:	0																						,	#?	kelvin source pin inductance
									'Ls'					:	0																						,	#?	package source inductance
                                    'Ld'					:	0																						,	#?	package drain inductance
									'Rs'					:	0																						,	#?	package source resistance
									'Rd'					:	0																						,	#?	package drain inductance
									'Ksrc'					:	0																						,	#?	kelvin source option, 0->no kelvin | 1->kelvin
									'Vblock'            	:   80                                	 													,   #? 	transistor blocking voltage
									'Id'                	:   241                                 													,   #? 	transistor drain current
									'Tr'                	:   0                                   													,   #? 	transistor rise time
									'Tf'                	:   0                                       												, 	#? 	transistor fall time
									'Avalanche'		:	{																									#!	transistor avalanche parameters
										'Config'			:	2																						,	#?	1->enable | 2->disable
										'Voltage'			:	80																						,	#?	avalanche voltage
										'Resistance'		:	1e-3																						#?	avalanche resistance to break voltage state-dependency
									},
									'Transfer'		:	{																									#!	transistor forward transfer parameters
										'Vds'				:	Vds_vec																					,	#?	drain-source voltage vector
										'Vgs'				:	list(np.arange(0.0,12.0+0.4,0.4))													,	#?	gate-source voltage vector
										'Ids'				:	Ids_vec																					,	#?	drain current vector
										'Factor_ON'			:	1.0																						,	#?	scaling factor for Ids at turn ON
										'Factor_OFF'		:	1.0																						,	#?	scaling factor for Ids at turn OFF
										'Factor_Vgs_ON'		:	1.0																						,	#?	scaling factor for Vgs at turn ON
										'Factor_Vgs_OFF'	:	1.0																						,	#?	scaling factor for Vgs at turn OFF
										'Vcoss'				:	0																						,	#?	initial voltage of the Coss
									},
						},
							'BodyDiode'  			:	{																									#!	body diodes paramteters
									'Config'				:	4																						,	#?	1->non-ideal RR | 2->non-ideal | 3->ideal RR | 4->ideal
									'Thermal'           	:   ''                                  													,   #? 	separate body diode
									'Custom'            	:   []					                 													,   #? 	body diode provided custrom variables
									'Rd_on'             	:   Rd[-1]													                              	,  	#? 	body diode ON resistance
									'Rd_off'				:	'inf'																					,	#?	body diode OFF resistance
									'Vf'					:	Vt[-1]																					,	#? 	body diode forward voltage
									'If'                	:   241                                 													,   #? 	body diode forward current
									'dIr'               	:   100e6                                  													,   #? 	body diode current slope
									'Lrr'					:	1e-9																					,	#?	body diode reverse recovery inductance
									'Trr'               	:   73e-9                                 													,   #? 	body diode reverse recovery time
									'Irr'               	:   0                                   													,   #? 	body diode reverse recovery current
									'Qrr'               	:   138e-9                                  												,	#? 	body diode reverse recovery charge
									'Is'                  	:   43              																		, 	#? 	body diode reference current
									'Vs'					:	40																						,	#?	body diode reference voltage
                                    'VIcurve'		:	{																									#!	body diode VI characteristics
                                        'Vfvec'				:	Vfvec																					,	#?	forward voltage vector
                                        'Ifvec'				:	Ifvec																					,	#?	forward current vector
										'Rdvec'				:	Rd																						,	#?	dynamic resistance vector
										'Vtvec'				:	Vt																						,	#?	threshold voltage vector
                                        'Temps'				:	[-55,25,175]																			,	#?	temperature vector
                                        'Vfscale'			:	1.5																							#?	Vf scaling to account for min, typ and max deviations
									},
						},
							'GateDriver'			:	{																									#!	gate driver parameters
									'Config'				:	3																						,	#?	1->high-side | 2->low-side | 3->disable
									'Von'					:	12																						,	#?	ON driving voltage
									'Voff'					:	0																						,	#?	OFF driving voltage
									'Ron'					:	5																						,	#?	sourcing output resistance
									'Roff'					:	5																						,	#?	sinking output resistance
									'Lon'					:	0																						,	#?	sourcing output inductance
									'Loff'					:	0																						,	#?	sinking output inductance
									'Cload'					:	0																						,	#?	capacitive load on output
									'Rload'					:	'inf'																					,	#?	resistive load on output
									'Delay'					:	0																						,	#?	input-to-output total deadtime
									'Trise'					:	0																						,	#?	output rising time
									'Tfall'					:	0																						,	#?	output falling time
									'UVLO_Start'			:	7.0																						,	#?	UVLO startup voltage threshold
									'UVLO_Stop'				:	6.5																						,	#?	UVLO shutdown voltage threshold
									'UVLO_Delay'			:	100e-9																					,	#?	delay between UVLO startup and shutdown
									'Init_State'			:	0																						,	#?	initial toggling state, 0->OFF | 1->ON
									'CurrentLimit'	:	{																									#*	current limit of driver stage
										'Config'			:	2																						,	#?	1->enable | 2->disable
										'Ts'				: 	0 																						,	#?	sampling time between inductive & capacitive links
										'tau'				: 	0																						,	#?	first-order delay between inductive & capacitive links
                                    	'Rs'				: 	0																						,	#?	source impedance of inductive link
										'Cs'				:	1e-12																					,	#?	source capacitance of capacitive link
                                        'UpLim'				: 	10																						,	#?	max current limit on capacitive link
                                        'LoLim'				: 	-10																						,	#?	min current limit on capacitive link
                                        'Voffset'			: 	0																							#?	voltage offset between inductive & capacitive links
									},
									'Masking'		:	{																									#*	switching stages masking
										'ON'	:	{																										#	ON path masking
											'Config'		:	2																						,	#?	1->enable | 2->disable
											'HIGH'	:	{																									#!	HIGH mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[0, 0]																						#?	mask output
											},
											'LOW'	:	{																									#!	LOW mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[1, 1]																						#?	mask output
											}
										},
										'OFF'	:	{																										#	OFF path masking
											'Config'		:	2																						,	#?	1->enable | 2->disable
											'HIGH'	:	{																									#!	HIGH mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[0, 0]																						#?	mask output
											},
											'LOW'	:	{																									#!	LOW mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[1, 1]																						#?	mask output
											}
										}
									},
									'Boot'			:	{																									#*	bootstrap/charge pump parameters
										'Config'			:	1																						,	#?	1->bootstrap | 2->charge pump
										'Von'				:	14																						,	#?	boostrap driving voltage
										'Cboot'				:	4.7e-6																					,	#?	bootstrap capacitance
										'Vinit'				:	0																						,	#?	bootstrap capacitance initial voltage
										'Rboot'				:	10																						,	#?	bootstrap resistance
										'Vfboot'			:	0.87																					,	#?	bootstrap diode forward voltage
										'Rdboot'			:	1e-3																					,	#?	bootstrap diode ON-state resistance
										'Ichrg'				:	300e-6																					,	#?	charge pump supply current
										'Idis'				:	5e-6																					,	#?	charge pump loading or leakage current
										'Cpar'				:	0																						,	#?	charge pump parallel cap to break state/source dependency
									    'UVLO_Start'		:	11.6																					,	#?	threshold value to start the charge pump
										'UVLO_Stop'			:	12.4																						#?	threshold value to stop the charge pump
									},
							},
							'GateNetwork'			:	{																									#!	gate drive circuit parameters
									'Config'				:	2																						,	#?	1-> enable | 2->disable
									'ON_Path'		:	{																									#*	sourcing path parameters
										'Rg'				:	5																						,	#?	gate ON path resistance
										'Lg'				:	0																						,	#?	gate ON path inductance
										'Rload'				:	10e3																					,	#?	gate pull down resistance
										'Diode'	:	{																										#	reverse blocking diode parameters
											'Vf'			:	0																						,	#?	forward voltage
											'Rd_on'			:	0																						,	#?	ON-state resistance
										},
									},
									'OFF_Path'		:	{																									#*	sinking path parameters
										'Rg'				:	5																						,	#?	gate OFF path resistance
										'Lg'				:	0																						,	#?	gate OFF path inductance
										'Diode'	:	{																										#	reverse blocking diode parameters
											'Vf'			:	0																						,	#?	forward voltage
											'Rd_on'			:	0																						,	#?	ON-state resistance
										},
									},
									'NegVolt'		:	{																									#*	negative voltage generator parameters
										'Config'			:	2																						,	#?	1-> enable | 2->disable
										'Dz'	:	{																										#	zener diode parameters
											'Vf'			:	0.7																						,	#?	forward voltage
											'Rd_on'			:	1e-3																					,	#?	ON-state resistance
											'Vz'			:	2																						,	#?	Zener breakdown voltage
											'Rz'			:	1e-3																					,	#?	Zener resistance
										},
										'Dp'	:	{																										#	peak detector diode
											'Vf'			:	0.0																						,	#?	forward voltage
											'Rd_on'			:	0.0																						,	#?	ON-state resistance
										},
										'Cz'	:	{																										#	Zener capacitor parameters
											'Config'		:	1																						,	#?	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
											'Csingle'		:	1e-6																					,	#?	single capacitor value
											'Rsingle'		:	5e-3																					,	#?	ESR of single capacitor
											'Lsingle'		:	0																						,	#?	ESL of single capacitor
											'nPar'			:	1																						,	#?	number of parallel connections
											'nSer'			:	1																						,	#?	number of series connections
											'Vinit'			:	0																						,	#?	capacitor initial voltage
										},
										'Cp'	:	{																										#	peak detector capacitor parameters
											'Config'		:	1																						,	#?	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
											'Csingle'		:	2.2e-6																					,	#?	single capacitor value
											'Rsingle'		:	5e-3																					,	#?	ESR of single capacitor
											'Lsingle'		:	0																						,	#?	ESL of single capacitor
											'nPar'			:	1																						,	#?	number of parallel connections
											'nSer'			:	1																						,	#?	number of series connections
											'Vinit'			:	0																						,	#?	capacitor initial voltage
										},
										'Rp1'				:	43																						,	#?	current limiter of peak detector current
										'Rp2'				:	4.7e3																					,	#?	load resistor to charge the zener diode
									},
								},
							'nParallel'   					:	1                                       												,   #? 	number of parallel devices
							'Rth_jc'						:	0.63																					,	#?	junction-to-case thermal resistance
							'Cth_jc'						:	0.00																					,	#?	junction-to-case thermal capacitance
							'Rth_ca'              			:   [0.292,0.258,0.856,0.228,0.3]            												,   #? 	case-to-ambient thermal resistance
							'Cth_ca'              			:   [0.788,0.205,15.91,3.716,0.015]             											,   #? 	case-to-ambient thermal capacitance
							'Tinit'							:	0.0																						,	#?	initial juntion temperature
							'Pinit'							:	0.0																						,	#?	initial power dissipation
							'Coss'					: 	{																									#!	device Coss parameters
								'C'							:	Coss_eff					 															,	#?	device parasitic output capacitance
								'R'							:	0																						,	#?	Coss resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Coss inductance to reduce current slope
								'Coss_er'					:	Crss_er																					,	#?	energy-related Coss
								'Coss_tr'					:	Coss_tr																					,	#?	time-related Coss
								'Vvec'						:	Coss[0]																					,	#? 	device Coss voltage vector
								'Cvec'						:	Coss[1]																					,	#?	device Coss capacity vector
								'Offset'					:	0																						,	#?	parasitic offset to Coss
                                'Factor'					:	1.0																						,	#?	parasitic tolerance to Coss
								'Qoss'						:	Qoss																					,	#?	equivalent charge of Coss
								'Eoss'						:	Eoss																					,	#?	equivalent energy of Coss
								'Config'					:	5																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
						},
                        	'Crss'					:	{																									#!	device Crss parameters
                                'C'							:	Crss_eff					 															,	#?	device parasitic reverse transfer capacitance
								'R'							:	0																						,	#?	Crss resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Crss inductance to reduce current slope
								'Crss_er'					:	Crss_er																					,	#?	energy-related Crss
								'Crss_tr'					:	Crss_tr																					,	#?	time-related Crss
								'Vvec'						:	Crss[0]																					,	#?	device Crss voltage vector
                                'Cvec'						:	Crss[1]																					,	#?	device Crss capacity vector
								'Qvec'						:	Qrss																					,	#?	device accumulated Crss charge vector
								'Offset'					:	0																						,	#?	parasitic offset to Crss
								'Factor'					:	1.0																						,	#?	parasitic tolerance to Crss
								'Qrss'						:	Qrss																					,	#?	equivalent charge of Crss
								'Erss'						:	Erss																					,	#?	equivalent energe of Crss
								'Config'					:	5																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
						},
							'Ciss'					:	{																									#!	device Ciss parameters
								'C'							:	Ciss_eff					 															,	#?	device parasitic input capacitance
								'R'							:	0																						,	#?	Ciss resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Ciss inductance to reduce current slope
								'Ciss_er'					:	Ciss_er																					,	#?	energy-related Ciss
								'Ciss_tr'					:	Ciss_tr																					,	#?	time-related Ciss
								'Vvec'						:	Ciss[0]																					,	#?	device Ciss voltage vector
								'Cvec'						:	Ciss[1]																					,	#?	device Ciss capacity vector
								'Offset'					:	0																						,	#?	parasitic offset to Ciss
								'Factor'					:	1.0																						,	#?	parasitic tolerance to Ciss
								'Qiss'						:	Qiss																					,	#?	equivalent charge of Ciss
								'Eiss'						:	Eiss																					,	#?	equivalent energy of Ciss
								'Config'					:	5																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Cds'					:	{																									#!	device Cds parameters
								'C'							:	Cds_eff					 																,	#?	device parasitic Cds capacitance
								'R'							:	0																						,	#?	Cds resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Cds inductance to reduce current slope
								'Cds_er'					:	Cds_er																					,	#?	energy-related Cds
								'Cds_tr'					:	Cds_tr																					,	#?	time-related Cds
								'Vvec'						:	Coss[0]																					,	#?	device Cds voltage vector
								'Cvec'						:	Cds																						,	#?	device Cds capacity vector
								'Offset_ON'					:	0																						,	#?	tuning offset for turn ON
								'Offset_OFF'				:	0																						,	#?	tuning offset for turn OFF
								'Factor_ON'					:	1.0																						,	#?	tuning factor for turn ON
								'Factor_OFF'				:	1.0																						,	#?	tuning factor for turn OFF
								'Config'					:	4																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Cgd'					:	{																									#!	device Cgd parameters
								'C'							:	Cgd_eff							 														,	#?	device parasitic Cgd capacitance
								'R'							:	0																						,	#?	Cgd resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Cgd inductance to reduce current slope
								'Cgd_er'					:	Cgd_er																					,	#?	energy-related Cgd
								'Cgd_tr'					:	Cgd_tr																					,	#?	time-related Cgd
								'Vvec'						:	Crss[0]																					,	#?	device Cgd voltage vector
								'Cvec'						:	Cgd																						,	#?	device Cgd capacity vector
								'Offset_ON'					:	0																						,	#?	tuning offset for turn ON
								'Offset_OFF'				:	0																						,	#?	tuning offset for turn OFF
								'Factor_ON'					:	1.0																						,	#?	tuning factor for turn ON
								'Factor_OFF'				:	1.0																						,	#?	tuning factor for turn OFF
								'Config'					:	4																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Cgs'					:	{																									#!	device Cgs parameters
								'C'							:	Cgs_eff					 																,	#?	device parasitic Cgs capacitance
								'R'							:	0																						,	#?	Cgs resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Cgs inductance to reduce current slope
								'Cgs_er'					:	Cgs_er																					,	#?	energy-related Cgs
								'Cgs_tr'					:	Cgs_tr																					,	#?	time-related Cgs
								'Vvec'						:	Ciss[0]																					,	#?	device Cgs voltage vector
								'Cvec'						:	Cgs																						,	#?	device Cgs capacity vector
								'Offset_ON'					:	0																						,	#?	tuning offset for turn ON
								'Offset_OFF'				:	0																						,	#?	tuning offset for turn OFF
								'Factor_ON'					:	1.0																						,	#?	tuning factor for turn ON
								'Factor_OFF'				:	1.0																						,	#?	tuning factor for turn OFF
								'Config'					:	4																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Eoff'					:	{																									#!	transistor turn-OFF energy losses
									'Ivec'					:	Ioff																					,	#?	turn-OFF energy current vector
									'Rgvec'					:	[0,100]																					,	#?	OFF path gate resistances vector
									'Tjvec'					:	[-55,175]																				,	#?	junction temperature vector
                                    'Vvec'					:	Voff																					,	#?	turn-OFF voltage vector
                                    'Evec'					:	Eoff																					,	#?	turn-OFF energy vectors
									'Evec_Temp'				:	Eoff_Temp																				,	#?	turn-OFF energy temp scaling vectors
                                    'CAT'					:	catOFF																					,	#?	octave Eoff energy syntax
									'CAT_Temp'				:	catOFF_Temp																				,	#?	octave Eoff energy temp scaling syntax
									'Vgs'					:	0																						,	#?	used OFF path gate-source voltage
									'Vth'					:	1.5																						,	#?	used OFF path threshold voltage
									'Rg'					:	0																							#?	used OFF path gate resistance
						},
							'Eon'					:	{																									#!	transistor turn-ON energy losses
									'Ivec'					:	Ion																						,	#?	turn-ON energy current vector
									'Rgvec'					:	[0,100]																					,	#?	ON path gate resistances vector
									'Tjvec'					:	[-55,175]																				,	#?	junction temperature vector
                                    'Vvec'					:	Von																						,	#?	turn-ON voltage vector
                                    'Evec'					:	Eon																						,	#?	turn-ON energy vectors
									'Evec_Temp'				:	Eon_Temp																				,	#?	turn-ON energy temp scaling vectors
                                    'CAT'					:	catON																					,	#?	octave Eon energy syntax
									'CAT_Temp'				:	catON_Temp																				,	#?	octave Eon energy temp scaling syntax
									'Vgs'					:	12																						,	#?	used ON path gate-source voltage
									'Vth'					:	1.5																						,	#?	used ON path threshold voltage
									'Rg'					:	0																							#?	used ON path gate resistance
						},
							'Tau_deg'						:	100e-9																					,	#?	deglitch filter for currents and voltages
							'RCsnubber'						:	2																						,	#?	1->enable | 2->disable
						}

#?----------------------------------------------------------------------------------------------------------------------------------------------------------------------

Coss,Qoss,Eoss,Coss_tr,Coss_er		=	paramProcess.MOSFETcaps(switchesCossPath,'NVMTS0D6N04CL','_Coss')
Crss,Qrss,Erss,Crss_tr,Crss_er 		=	paramProcess.MOSFETcaps(switchesCrssPath,'NVMTS0D6N04CL','_Crss')
Ciss,Qiss,Eiss,Ciss_tr,Ciss_er 		=	paramProcess.MOSFETcaps(switchesCissPath,'NVMTS0D6N04CL','_Ciss')
Coss_eff 							=	paramProcess.getCmos(Coss,Coss_tr,Coss_er,Coss[0][0],True)
Ciss_eff 							=	paramProcess.getCmos(Ciss,Ciss_tr,Ciss_er,Ciss[0][0],True)
Crss_eff 							=	paramProcess.getCmos(Crss,Crss_tr,Crss_er,Crss[0][0],True)
Cds 						        =	(np.array(Coss[1]) - np.array(Crss[1])).tolist()
Cgs						        	=	(np.array(Ciss[1]) - np.array(Crss[1])).tolist()
Cgd						        	=	Crss[1]
Cds_tr						        =	(np.array(Coss_tr) - np.array(Crss_tr)).tolist()
Cgs_tr						        =	(np.array(Ciss_tr) - np.array(Crss_tr)).tolist()
Cgd_tr						        =	Crss_tr
Cds_er						        =	(np.array(Coss_er) - np.array(Crss_er)).tolist()
Cgs_er						        =	(np.array(Ciss_er) - np.array(Crss_er)).tolist()
Cgd_er						        =	Crss_er
Cds_eff 							=	paramProcess.getCmos([Coss[0],Cds],Cds_tr,Cds_er,Coss[0][0],True)
Cgs_eff 							=	paramProcess.getCmos([Ciss[0],Cgs],Cgs_tr,Cgs_er,Ciss[0][0],True)
Cgd_eff 							=	Crss_eff
Rvec,Tvec							=	paramProcess.MOSFETrdson(switchesRdsonPath,'NVMTS0D6N04CL','_Rdson')
Nvec,Ivec 							=	paramProcess.MOSFETrdson(switchesIdsonPath,'NVMTS0D6N04CL','_Rdson')
Ioff,catOFF,Eoff					=	paramProcess.MOSFETenergies(switchesEoffPath,'NVMTS0D6N04CL','_Eoff')
Voff,catOFF_Temp,Eoff_Temp			=	paramProcess.MOSFETenergies(switchesEoffPath,'NVMTS0D6N04CL','_Eoff_Temp')
Ion,catON,Eon 						=	paramProcess.MOSFETenergies(switchesEonPath,'NVMTS0D6N04CL','_Eon')
Von,catON_Temp,Eon_Temp				=	paramProcess.MOSFETenergies(switchesEonPath,'NVMTS0D6N04CL','_Eon_Temp')
Vfvec,Ifvec,Rd,Vt					=	paramProcess.DiodeVI_data(bodyDiodeVIPath,'NVMTS0D6N04CL')
Vds_vec,Ids_vec 					=	paramProcess.Forward_Transfer_data(switchesTransferPath,'NVMTS0D6N04CL')

NVMTS0D6N04CL		=	{																																	#*	NVMTS0D6N04CL parameters
							'Config'						:	1																						,	#!	1->electric integrated | 2->electric separate | 3->thermal integrated | 4->thermal separate
							'Transistor'  			: 	{																									#!	transistors parameters
									'Config'				:	2																						,	#?	1->real model | 2->ideal model | 3->behavioral model
									'Thermal'           	:   ''                                  													,   #? 	selected transistor
									'Custom'            	:   []						               													,   #? 	transistor provided custom variables
									'g_fs'					:	1e6																						,	#?	forward transconductance
									'Rg'					:	1.077																					,	#?	internal gate resistance
									'Lg'					:	6.23e-9*0																				,	#?	gate pin inductance
									'Rds_on'            	:   Rvec[-1][-1]*1e-3																		,   #? 	transistor ON resistance
									'Rds_off'				:	'inf'																					,	#?	transistor OFF resistance
									'Rvec'					:	(np.array(Rvec)*1e-3).tolist()														,	#?	absolute Rdson vector corresponding to junction temperature
									'Tvec'					:	Tvec 																					,	#?	junction temperature vector for Rdson
									'RTconfig'				:	1																						,	#?	choose which RT vector to be used
									'RdsonScale'			:	1.0																						,	#?	Rdson scaling to account for min, typ and max deviations
									'Nvec'					:	Nvec 																					,	#?	normalized Rdson vector corresponding to current
									'Ivec'					:	Ivec																					,	#?	current vector for normalized Rdson
									'NIconfig'				:	1																						,	#?	choose which NI vector to be used
									'IdsonScale'			:	1.0																						,	#?	Idson resistance scaling to account for min, typ and max deviations
									'Rsrc'					:	54.37e-6*0																				,	#?	kelvin source pin resistance
									'Lsrc'					:	0.99e-9*0																				,	#?	kelvin source pin inductance
									'Ls'					:	0.99e-9*0																				,	#?	package source inductance
                                    'Ld'					:	0.3377e-9*0																				,	#?	package drain inductance
									'Rs'					:	54.37e-6*0																				,	#?	package source resistance
									'Rd'					:	149.74e-9*0																				,	#?	package drain inductance
									'Ksrc'					:	0																						,	#?	kelvin source option, 0->no kelvin | 1->kelvin
									'Vblock'            	:   40                                	 													,   #? 	transistor blocking voltage
									'Id'                	:   533                                 													,   #? 	transistor drain current
									'Tr'                	:   100e-9                                 													,   #? 	transistor rise time
									'Tf'                	:   100e-9                                     												, 	#? 	transistor fall time
									'Avalanche'		:	{																									#!	transistor avalanche parameters
										'Config'			:	2																						,	#?	1->enable | 2->disable
										'Voltage'			:	40																						,	#?	avalanche voltage
										'Resistance'		:	1e-3																						#?	avalanche resistance to break voltage state-dependency
									},
									'Transfer'		:	{																									#!	transistor forward transfer parameters
										'Vds'				:	Vds_vec																					,	#?	drain-source voltage vector
										'Vgs'				:	list(np.arange(0.0,12.0+0.2,0.2))													,	#?	gate-source voltage vector
										'Ids'				:	Ids_vec																					,	#?	drain current vector
										'Factor_ON'			:	1.0																						,	#?	scaling factor for Ids at turn ON
										'Factor_OFF'		:	1.0																						,	#?	scaling factor for Ids at turn OFF
										'Factor_Vgs_ON'		:	1.0																						,	#?	scaling factor for Vgs at turn ON
										'Factor_Vgs_OFF'	:	1.0																						,	#?	scaling factor for Vgs at turn OFF
										'Vcoss'				:	0																						,	#?	initial voltage of the Coss
									},
						},
							'BodyDiode'  			:	{																									#!	body diodes paramteters
									'Config'				:	4																						,	#?	1->non-ideal RR | 2->non-ideal | 3->ideal RR | 4->ideal
									'Thermal'           	:   ''                                  													,   #? 	separate body diode
									'Custom'            	:   []					                 													,   #? 	body diode provided custrom variables
									'Rd_on'             	:   Rd[-1]																					,  	#? 	body diode ON resistance
									'Rd_off'				:	'inf'																					,	#?	body diode OFF resistance
									'Vf'					:	Vt[-1]																					,	#? 	body diode forward voltage
									'If'                	:   300                                 													,   #? 	body diode forward current
									'dIr'               	:   100e6                                  													,   #? 	body diode current slope
									'Lrr'					:	1e-9																					,	#?	body diode reverse recovery inductance
									'Trr'               	:   105e-9                                  												,   #? 	body diode reverse recovery time
									'Irr'               	:   0                                   													,   #? 	body diode reverse recovery current
									'Qrr'               	:   274e-9                                  												, 	#? 	body diode reverse recovery charge
									'Is'                  	:   50              																		, 	#? 	body diode reference current
									'Vs'					:	20																						,	#?	body diode reference voltage
                                    'VIcurve'		:	{																									#!	body diode VI characteristics
                                        'Vfvec'				:	Vfvec																					,	#?	forward voltage vector
                                        'Ifvec'				:	Ifvec																					,	#?	forward current vector
										'Rdvec'				:	Rd																						,	#?	dynamic resistance vector
										'Vtvec'				:	Vt																						,	#?	threshold voltage vector
                                        'Temps'				:	[-55,25,175]																			,	#?	temperature vector
                                        'Vfscale'			:	1.6																							#?	Vf scaling to account for min, typ and max deviations
									},
						},
							'GateDriver'			:	{																									#!	gate driver parameters
									'Config'				:	3																						,	#?	1->high-side | 2->low-side | 3->disable
									'Von'					:	12																						,	#?	ON driving voltage
									'Voff'					:	0																						,	#?	OFF driving voltage
									'Ron'					:	10																						,	#?	sourcing output resistance
									'Roff'					:	12																						,	#?	sinking output resistance
									'Lon'					:	0																						,	#?	sourcing output inductance
									'Loff'					:	0																						,	#?	sinking output inductance
									'Cload'					:	0																						,	#?	capacitive load on output
									'Rload'					:	'inf'																					,	#?	resistive load on output
									'Delay'					:	0																						,	#?	input-to-output total deadtime
									'Trise'					:	0																						,	#?	output rising time
									'Tfall'					:	0																						,	#?	output falling time
									'UVLO_Start'			:	7.0																						,	#?	UVLO startup voltage threshold
									'UVLO_Stop'				:	6.5																						,	#?	UVLO shutdown voltage threshold
									'UVLO_Delay'			:	100e-9																					,	#?	delay between UVLO startup and shutdown
									'Init_State'			:	0																						,	#?	initial toggling state, 0->OFF | 1->ON
									'CurrentLimit'	:	{																									#*	current limit of driver stage
										'Config'			:	2																						,	#?	1->enable | 2->disable
										'Ts'				: 	0 																						,	#?	sampling time between inductive & capacitive links
										'tau'				: 	0																						,	#?	first-order delay between inductive & capacitive links
                                    	'Rs'				: 	0																						,	#?	source impedance of inductive link
										'Cs'				:	1e-12																					,	#?	source capacitance of capacitive link
                                        'UpLim'				: 	40e-6																					,	#?	max current limit on capacitive link
                                        'LoLim'				: 	-10																						,	#?	min current limit on capacitive link
                                        'Voffset'			: 	0																							#?	voltage offset between inductive & capacitive links
									},
									'Masking'		:	{																									#*	switching stages masking
										'ON'	:	{																										#	ON path masking
											'Config'		:	2																						,	#?	1->enable | 2->disable
											'HIGH'	:	{																									#!	HIGH mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[0, 0]																						#?	mask output
											},
											'LOW'	:	{																									#!	LOW mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[1, 1]																						#?	mask output
											}
										},
										'OFF'	:	{																										#	OFF path masking
											'Config'		:	2																						,	#?	1->enable | 2->disable
											'HIGH'	:	{																									#!	HIGH mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[0, 0]																						#?	mask output
											},
											'LOW'	:	{																									#!	LOW mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[1, 1]																						#?	mask output
											}
										}
									},
									'Boot'			:	{																									#*	bootstrap/charge pump parameters
										'Config'			:	1																						,	#?	1->bootstrap | 2->charge pump
										'Von'				:	14																						,	#?	boostrap driving voltage
										'Cboot'				:	4.7e-6																					,	#?	bootstrap capacitance
										'Vinit'				:	0																						,	#?	bootstrap capacitance initial voltage
										'Rboot'				:	10																						,	#?	bootstrap resistance
										'Vfboot'			:	0.87																					,	#?	bootstrap diode forward voltage
										'Rdboot'			:	1e-3																					,	#?	bootstrap diode ON-state resistance
										'Ichrg'				:	300e-6																					,	#?	charge pump supply current
										'Idis'				:	5e-6																					,	#?	charge pump loading or leakage current
										'Cpar'				:	0																						,	#?	charge pump parallel cap to break state/source dependency
									    'UVLO_Start'		:	11.6																					,	#?	threshold value to start the charge pump
										'UVLO_Stop'			:	12.4																						#?	threshold value to stop the charge pump
									},
							},
							'GateNetwork'			:	{																									#!	gate drive circuit parameters
									'Config'				:	2																						,	#?	1-> enable | 2->disable
									'ON_Path'		:	{																									#*	sourcing path parameters
										'Rg'				:	1.95																					,	#?	gate ON path resistance
										'Lg'				:	0																						,	#?	gate ON path inductance
										'Rload'				:	10e3																					,	#?	gate pull down resistance
										'Diode'	:	{																										#	reverse blocking diode parameters
											'Vf'			:	0																						,	#?	forward voltage
											'Rd_on'			:	0																						,	#?	ON-state resistance
										},
									},
									'OFF_Path'		:	{																									#*	sinking path parameters
										'Rg'				:	1.95																					,	#?	gate OFF path resistance
										'Lg'				:	0																						,	#?	gate OFF path inductance
										'Diode'	:	{																										#	reverse blocking diode parameters
											'Vf'			:	0																						,	#?	forward voltage
											'Rd_on'			:	0																						,	#?	ON-state resistance
										},
									},
									'NegVolt'		:	{																									#*	negative voltage generator parameters
										'Config'			:	2																						,	#?	1-> enable | 2->disable
										'Dz'	:	{																										#	zener diode parameters
											'Vf'			:	0.7																						,	#?	forward voltage
											'Rd_on'			:	1e-3																					,	#?	ON-state resistance
											'Vz'			:	2																						,	#?	Zener breakdown voltage
											'Rz'			:	1e-3																					,	#?	Zener resistance
										},
										'Dp'	:	{																										#	peak detector diode
											'Vf'			:	0.0																						,	#?	forward voltage
											'Rd_on'			:	0.0																						,	#?	ON-state resistance
										},
										'Cz'	:	{																										#	Zener capacitor parameters
											'Config'		:	1																						,	#?	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
											'Csingle'		:	1e-6																					,	#?	single capacitor value
											'Rsingle'		:	5e-3																					,	#?	ESR of single capacitor
											'Lsingle'		:	0																						,	#?	ESL of single capacitor
											'nPar'			:	1																						,	#?	number of parallel connections
											'nSer'			:	1																						,	#?	number of series connections
											'Vinit'			:	0																						,	#?	capacitor initial voltage
										},
										'Cp'	:	{																										#	peak detector capacitor parameters
											'Config'		:	1																						,	#?	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
											'Csingle'		:	2.2e-6																					,	#?	single capacitor value
											'Rsingle'		:	5e-3																					,	#?	ESR of single capacitor
											'Lsingle'		:	0																						,	#?	ESL of single capacitor
											'nPar'			:	1																						,	#?	number of parallel connections
											'nSer'			:	1																						,	#?	number of series connections
											'Vinit'			:	0																						,	#?	capacitor initial voltage
										},
										'Rp1'				:	43																						,	#?	current limiter of peak detector current
										'Rp2'				:	4.7e3																					,	#?	load resistor to charge the zener diode
									},
								},
							'nParallel'   					:	2                                       												,   #? 	number of parallel devices
							'Rth_jc'						:	[0.002103,0.00875,0.025951,0.093755,0.642636]											,	#?	junction-to-case thermal resistance
							'Cth_jc'						:	[0.000701,0.001817,0.009225,0.023893,0.0833]											,	#?	junction-to-case thermal capacitance
							'Rth_ca'              			:   [0.830418054,46.83713327,10.8124087,1.682365674,-41.85694941]            				,   #? 	case-to-ambient thermal resistance
							'Cth_ca'              			:   [0.163263676,1.272174175,15.0646712,336.385802,-1.581288262]             				,   #? 	case-to-ambient thermal capacitance
							'Tinit'							:	0.0																						,	#?	initial juntion temperature
							'Pinit'							:	0.0																						,	#?	initial power dissipation
							'Coss'					: 	{																									#!	device Coss parameters
								'C'							:	Coss_eff					 															,	#?	device parasitic output capacitance
								'R'							:	0																						,	#?	Coss resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Coss inductance to reduce current slope
								'Coss_er'					:	Crss_er																					,	#?	energy-related Coss
								'Coss_tr'					:	Coss_tr																					,	#?	time-related Coss
								'Vvec'						:	Coss[0]																					,	#? 	device Coss voltage vector
								'Cvec'						:	Coss[1]																					,	#?	device Coss capacity vector
								'Offset'					:	0																						,	#?	parasitic offset to Coss
                                'Factor'					:	1.0																						,	#?	parasitic tolerance to Coss
								'Qoss'						:	Qoss																					,	#?	equivalent charge of Coss
								'Eoss'						:	Eoss																					,	#?	equivalent energy of Coss
								'Config'					:	5																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
						},
                        	'Crss'					:	{																									#!	device Crss parameters
                                'C'							:	Crss_eff					 															,	#?	device parasitic reverse transfer capacitance
								'R'							:	0																						,	#?	Crss resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Crss inductance to reduce current slope
								'Crss_er'					:	Crss_er																					,	#?	energy-related Crss
								'Crss_tr'					:	Crss_tr																					,	#?	time-related Crss
								'Vvec'						:	Crss[0]																					,	#?	device Crss voltage vector
                                'Cvec'						:	Crss[1]																					,	#?	device Crss capacity vector
								'Qvec'						:	Qrss																					,	#?	device accumulated Crss charge vector
								'Offset'					:	0																						,	#?	parasitic offset to Crss
								'Factor'					:	1.0																						,	#?	parasitic tolerance to Crss
								'Qrss'						:	Qrss																					,	#?	equivalent charge of Crss
								'Erss'						:	Erss																					,	#?	equivalent energe of Crss
								'Config'					:	5																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
						},
							'Ciss'					:	{																									#!	device Ciss parameters
								'C'							:	Ciss_eff					 															,	#?	device parasitic input capacitance
								'R'							:	0																						,	#?	Ciss resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Ciss inductance to reduce current slope
								'Ciss_er'					:	Ciss_er																					,	#?	energy-related Ciss
								'Ciss_tr'					:	Ciss_tr																					,	#?	time-related Ciss
								'Vvec'						:	Ciss[0]																					,	#?	device Ciss voltage vector
								'Cvec'						:	Ciss[1]																					,	#?	device Ciss capacity vector
								'Offset'					:	0																						,	#?	parasitic offset to Ciss
								'Factor'					:	1.0																						,	#?	parasitic tolerance to Ciss
								'Qiss'						:	Qiss																					,	#?	equivalent charge of Ciss
								'Eiss'						:	Eiss																					,	#?	equivalent energy of Ciss
								'Config'					:	5																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Cds'					:	{																									#!	device Cds parameters
								'C'							:	Cds_eff					 																,	#?	device parasitic Cds capacitance
								'R'							:	0																						,	#?	Cds resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Cds inductance to reduce current slope
								'Cds_er'					:	Cds_er																					,	#?	energy-related Cds
								'Cds_tr'					:	Cds_tr																					,	#?	time-related Cds
								'Vvec'						:	Coss[0]																					,	#?	device Cds voltage vector
								'Cvec'						:	Cds																						,	#?	device Cds capacity vector
								'Offset_ON'					:	0																						,	#?	tuning offset for turn ON
								'Offset_OFF'				:	0																						,	#?	tuning offset for turn OFF
								'Factor_ON'					:	1.0																						,	#?	tuning factor for turn ON
								'Factor_OFF'				:	1.0																						,	#?	tuning factor for turn OFF
								'Config'					:	4																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Cgd'					:	{																									#!	device Cgd parameters
								'C'							:	Cgd_eff							 														,	#?	device parasitic Cgd capacitance
								'R'							:	0																						,	#?	Cgd resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Cgd inductance to reduce current slope
								'Cgd_er'					:	Cgd_er																					,	#?	energy-related Cgd
								'Cgd_tr'					:	Cgd_tr																					,	#?	time-related Cgd
								'Vvec'						:	Crss[0]																					,	#?	device Cgd voltage vector
								'Cvec'						:	Cgd																						,	#?	device Cgd capacity vector
								'Offset_ON'					:	0																						,	#?	tuning offset for turn ON
								'Offset_OFF'				:	0																						,	#?	tuning offset for turn OFF
								'Factor_ON'					:	1.0																						,	#?	tuning factor for turn ON
								'Factor_OFF'				:	1.0																						,	#?	tuning factor for turn OFF
								'Config'					:	4																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Cgs'					:	{																									#!	device Cgs parameters
								'C'							:	Cgs_eff					 																,	#?	device parasitic Cgs capacitance
								'R'							:	0																						,	#?	Cgs resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Cgs inductance to reduce current slope
								'Cgs_er'					:	Cgs_er																					,	#?	energy-related Cgs
								'Cgs_tr'					:	Cgs_tr																					,	#?	time-related Cgs
								'Vvec'						:	Ciss[0]																					,	#?	device Cgs voltage vector
								'Cvec'						:	Cgs																						,	#?	device Cgs capacity vector
								'Offset_ON'					:	0																						,	#?	tuning offset for turn ON
								'Offset_OFF'				:	0																						,	#?	tuning offset for turn OFF
								'Factor_ON'					:	1.0																						,	#?	tuning factor for turn ON
								'Factor_OFF'				:	1.0																						,	#?	tuning factor for turn OFF
								'Config'					:	4																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Eoff'					:	{																									#!	transistor turn-OFF energy losses
									'Ivec'					:	Ioff																					,	#?	turn-OFF energy current vector
									'Rgvec'					:	[0,100]																					,	#?	OFF path gate resistances vector
									'Tjvec'					:	[-55,175]																				,	#?	junction temperature vector
                                    'Vvec'					:	Voff																					,	#?	turn-OFF voltage vector
                                    'Evec'					:	Eoff																					,	#?	turn-OFF energy vectors
									'Evec_Temp'				:	Eoff_Temp																				,	#?	turn-OFF energy temp scaling vectors
                                    'CAT'					:	catOFF																					,	#?	octave Eoff energy syntax
									'CAT_Temp'				:	catOFF_Temp																				,	#?	octave Eoff energy temp scaling syntax
									'Vgs'					:	0																						,	#?	used OFF path gate-source voltage
									'Vth'					:	1.5																						,	#?	used OFF path threshold voltage
									'Rg'					:	0																							#?	used OFF path gate resistance
						},
							'Eon'					:	{																									#!	transistor turn-ON energy losses
									'Ivec'					:	Ion																						,	#?	turn-ON energy current vector
									'Rgvec'					:	[0,100]																					,	#?	ON path gate resistances vector
									'Tjvec'					:	[-55,175]																				,	#?	junction temperature vector
                                    'Vvec'					:	Von																						,	#?	turn-ON voltage vector
                                    'Evec'					:	Eon																						,	#?	turn-ON energy vectors
									'Evec_Temp'				:	Eon_Temp																				,	#?	turn-ON energy temp scaling vectors
                                    'CAT'					:	catON																					,	#?	octave Eon energy syntax
									'CAT_Temp'				:	catON_Temp																				,	#?	octave Eon energy temp scaling syntax
									'Vgs'					:	12																						,	#?	used ON path gate-source voltage
									'Vth'					:	1.5																						,	#?	used ON path threshold voltage
									'Rg'					:	0																							#?	used ON path gate resistance
						},
							'Tau_deg'						:	100e-9																					,	#?	deglitch filter for currents and voltages
							'RCsnubber'						:	2																						,	#?	1->enable | 2->disable
						}

#?----------------------------------------------------------------------------------------------------------------------------------------------------------------------

Coss,Qoss,Eoss,Coss_tr,Coss_er		=	paramProcess.MOSFETcaps(switchesCossPath,'NVMTS0D6N04C','_Coss')
Crss,Qrss,Erss,Crss_tr,Crss_er 		=	paramProcess.MOSFETcaps(switchesCrssPath,'NVMTS0D6N04C','_Crss')
Ciss,Qiss,Eiss,Ciss_tr,Ciss_er 		=	paramProcess.MOSFETcaps(switchesCissPath,'NVMTS0D6N04C','_Ciss')
Coss_eff 							=	paramProcess.getCmos(Coss,Coss_tr,Coss_er,Coss[0][0],True)
Ciss_eff 							=	paramProcess.getCmos(Ciss,Ciss_tr,Ciss_er,Ciss[0][0],True)
Crss_eff 							=	paramProcess.getCmos(Crss,Crss_tr,Crss_er,Crss[0][0],True)
Cds 						        =	(np.array(Coss[1]) - np.array(Crss[1])).tolist()
Cgs						        	=	(np.array(Ciss[1]) - np.array(Crss[1])).tolist()
Cgd						        	=	Crss[1]
Cds_tr						        =	(np.array(Coss_tr) - np.array(Crss_tr)).tolist()
Cgs_tr						        =	(np.array(Ciss_tr) - np.array(Crss_tr)).tolist()
Cgd_tr						        =	Crss_tr
Cds_er						        =	(np.array(Coss_er) - np.array(Crss_er)).tolist()
Cgs_er						        =	(np.array(Ciss_er) - np.array(Crss_er)).tolist()
Cgd_er						        =	Crss_er
Cds_eff 							=	paramProcess.getCmos([Coss[0],Cds],Cds_tr,Cds_er,Coss[0][0],True)
Cgs_eff 							=	paramProcess.getCmos([Ciss[0],Cgs],Cgs_tr,Cgs_er,Ciss[0][0],True)
Cgd_eff 							=	Crss_eff
Rvec,Tvec							=	paramProcess.MOSFETrdson(switchesRdsonPath,'NVMTS0D6N04C','_Rdson')
Nvec,Ivec 							=	paramProcess.MOSFETrdson(switchesIdsonPath,'NVMTS0D6N04C','_Rdson')
Ioff,catOFF,Eoff					=	paramProcess.MOSFETenergies(switchesEoffPath,'NVMTS0D6N04C','_Eoff')
Voff,catOFF_Temp,Eoff_Temp			=	paramProcess.MOSFETenergies(switchesEoffPath,'NVMTS0D6N04C','_Eoff_Temp')
Ion,catON,Eon 						=	paramProcess.MOSFETenergies(switchesEonPath,'NVMTS0D6N04C','_Eon')
Von,catON_Temp,Eon_Temp				=	paramProcess.MOSFETenergies(switchesEonPath,'NVMTS0D6N04C','_Eon_Temp')
Vfvec,Ifvec,Rd,Vt					=	paramProcess.DiodeVI_data(bodyDiodeVIPath,'NVMTS0D6N04C')
Vds_vec,Ids_vec 					=	paramProcess.Forward_Transfer_data(switchesTransferPath,'NVMTS0D6N04C')

NVMTS0D6N04C		=	{																																	#*	NVMTS0D6N04C parameters
							'Config'						:	1																						,	#!	1->electric integrated | 2->electric separate | 3->thermal integrated | 4->thermal separate
							'Transistor'  			: 	{																									#!	transistors parameters
									'Config'				:	2																						,	#?	1->real model | 2->ideal model | 3->behavioral model
									'Thermal'           	:   ''                                  													,   #? 	selected transistor
									'Custom'            	:   []						               													,   #? 	transistor provided custom variables
									'g_fs'					:	1e6																						,	#?	forward transconductance
									'Rg'					:	0.6																						,	#?	internal gate resistance
									'Lg'					:	6.2322e-9*0																				,	#?	gate pin inductance
									'Rds_on'            	:   Rvec[-1][-1]*1e-3																		,   #? 	transistor ON resistance
									'Rds_off'				:	'inf'																					,	#?	transistor OFF resistance
									'Rvec'					:	(np.array(Rvec)*1e-3).tolist()														,	#?	absolute Rdson vector corresponding to junction temperature
									'Tvec'					:	Tvec 																					,	#?	junction temperature vector for Rdson
									'RTconfig'				:	1																						,	#?	choose which RT vector to be used
									'RdsonScale'			:	1.0																						,	#?	Rdson scaling to account for min, typ and max deviations
									'Nvec'					:	Nvec 																					,	#?	normalized Rdson vector corresponding to current
									'Ivec'					:	Ivec																					,	#?	current vector for normalized Rdson
									'NIconfig'				:	1																						,	#?	choose which NI vector to be used
									'IdsonScale'			:	1.0																						,	#?	Idson resistance scaling to account for min, typ and max deviations
									'Rsrc'					:	0																						,	#?	kelvin source pin resistance
									'Lsrc'					:	0																						,	#?	kelvin source pin inductance
									'Ls'					:	0.9922e-9*0																				,	#?	package source inductance
                                    'Ld'					:	0.3377e-9*0																				,	#?	package drain inductance
									'Rs'					:	54.3723e-6*0																			,	#?	package source resistance
									'Rd'					:	149.735e-9*0																			,	#?	package drain inductance
									'Ksrc'					:	0																						,	#?	kelvin source option, 0->no kelvin | 1->kelvin
									'Vblock'            	:   40                                	 													,   #? 	transistor blocking voltage
									'Id'                	:   533                                 													,   #? 	transistor drain current
									'Tr'                	:   100e-9                                 													,   #? 	transistor rise time
									'Tf'                	:   100e-9                                     												, 	#? 	transistor fall time
									'Avalanche'		:	{																									#!	transistor avalanche parameters
										'Config'			:	2																						,	#?	1->enable | 2->disable
										'Voltage'			:	40																						,	#?	avalanche voltage
										'Resistance'		:	1e-3																						#?	avalanche resistance to break voltage state-dependency
									},
									'Transfer'		:	{																									#!	transistor forward transfer parameters
										'Vds'				:	Vds_vec																					,	#?	drain-source voltage vector
										'Vgs'				:	list(np.arange(0.0,12.0+0.2,0.2))													,	#?	gate-source voltage vector
										'Ids'				:	Ids_vec																					,	#?	drain current vector
										'Factor_ON'			:	1.0																						,	#?	scaling factor for Ids at turn ON
										'Factor_OFF'		:	1.0																						,	#?	scaling factor for Ids at turn OFF
										'Factor_Vgs_ON'		:	1.0																						,	#?	scaling factor for Vgs at turn ON
										'Factor_Vgs_OFF'	:	1.0																						,	#?	scaling factor for Vgs at turn OFF
										'Vcoss'				:	0																						,	#?	initial voltage of the Coss
									},
						},
							'BodyDiode'  			:	{																									#!	body diodes paramteters
									'Config'				:	4																						,	#?	1->non-ideal RR | 2->non-ideal | 3->ideal RR | 4->ideal
									'Thermal'           	:   ''                                  													,   #? 	separate body diode
									'Custom'            	:   []					                 													,   #? 	body diode provided custrom variables
									'Rd_on'             	:   Rd[-1]																					,  	#? 	body diode ON resistance
									'Rd_off'				:	'inf'																					,	#?	body diode OFF resistance
									'Vf'					:	Vt[-1]																					,	#? 	body diode forward voltage
									'If'                	:   300                                 													,   #? 	body diode forward current
									'dIr'               	:   100e6                                  													,   #? 	body diode current slope
									'Lrr'					:	1e-9																					,	#?	body diode reverse recovery inductance
									'Trr'               	:   105e-9                                  												,   #? 	body diode reverse recovery time
									'Irr'               	:   0                                   													,   #? 	body diode reverse recovery current
									'Qrr'               	:   274e-9                                  												, 	#? 	body diode reverse recovery charge
									'Is'                  	:   50              																		, 	#? 	body diode reference current
									'Vs'					:	20																						,	#?	body diode reference voltage
                                    'VIcurve'		:	{																									#!	body diode VI characteristics
                                        'Vfvec'				:	Vfvec																					,	#?	forward voltage vector
                                        'Ifvec'				:	Ifvec																					,	#?	forward current vector
										'Rdvec'				:	Rd																						,	#?	dynamic resistance vector
										'Vtvec'				:	Vt																						,	#?	threshold voltage vector
                                        'Temps'				:	[-55,25,175]																			,	#?	temperature vector
                                        'Vfscale'			:	1.6																							#?	Vf scaling to account for min, typ and max deviations
									},
						},
							'GateDriver'			:	{																									#!	gate driver parameters
									'Config'				:	3																						,	#?	1->high-side | 2->low-side | 3->disable
									'Von'					:	12																						,	#?	ON driving voltage
									'Voff'					:	0																						,	#?	OFF driving voltage
									'Ron'					:	10																						,	#?	sourcing output resistance
									'Roff'					:	12																						,	#?	sinking output resistance
									'Lon'					:	0																						,	#?	sourcing output inductance
									'Loff'					:	0																						,	#?	sinking output inductance
									'Cload'					:	0																						,	#?	capacitive load on output
									'Rload'					:	'inf'																					,	#?	resistive load on output
									'Delay'					:	0																						,	#?	input-to-output total deadtime
									'Trise'					:	0																						,	#?	output rising time
									'Tfall'					:	0																						,	#?	output falling time
									'UVLO_Start'			:	0																						,	#?	UVLO startup voltage threshold
									'UVLO_Stop'				:	0																						,	#?	UVLO shutdown voltage threshold
									'UVLO_Delay'			:	0																						,	#?	delay between UVLO startup and shutdown
									'Init_State'			:	0																						,	#?	initial toggling state, 0->OFF | 1->ON
									'CurrentLimit'	:	{																									#*	current limit of driver stage
										'Config'			:	2																						,	#?	1->enable | 2->disable
										'Ts'				: 	0 																						,	#?	sampling time between inductive & capacitive links
										'tau'				: 	0																						,	#?	first-order delay between inductive & capacitive links
                                    	'Rs'				: 	0																						,	#?	source impedance of inductive link
										'Cs'				:	1e-12																					,	#?	source capacitance of capacitive link
                                        'UpLim'				: 	40e-6																					,	#?	max current limit on capacitive link
                                        'LoLim'				: 	-10																						,	#?	min current limit on capacitive link
                                        'Voffset'			: 	0																							#?	voltage offset between inductive & capacitive links
									},
									'Masking'		:	{																									#*	switching stages masking
										'ON'	:	{																										#	ON path masking
											'Config'		:	2																						,	#?	1->enable | 2->disable
											'HIGH'	:	{																									#!	HIGH mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[0, 0]																						#?	mask output
											},
											'LOW'	:	{																									#!	LOW mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[1, 1]																						#?	mask output
											}
										},
										'OFF'	:	{																										#	OFF path masking
											'Config'		:	2																						,	#?	1->enable | 2->disable
											'HIGH'	:	{																									#!	HIGH mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[0, 0]																						#?	mask output
											},
											'LOW'	:	{																									#!	LOW mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[1, 1]																						#?	mask output
											}
										}
									},
									'Boot'			:	{																									#*	bootstrap/charge pump parameters
										'Config'			:	1																						,	#?	1->bootstrap | 2->charge pump
										'Von'				:	14																						,	#?	boostrap driving voltage
										'Cboot'				:	4.7e-6																					,	#?	bootstrap capacitance
										'Vinit'				:	0																						,	#?	bootstrap capacitance initial voltage
										'Rboot'				:	10																						,	#?	bootstrap resistance
										'Vfboot'			:	0.87																					,	#?	bootstrap diode forward voltage
										'Rdboot'			:	1e-3																					,	#?	bootstrap diode ON-state resistance
										'Ichrg'				:	300e-6																					,	#?	charge pump supply current
										'Idis'				:	5e-6																					,	#?	charge pump loading or leakage current
										'Cpar'				:	0																						,	#?	charge pump parallel cap to break state/source dependency
									    'UVLO_Start'		:	11.6																					,	#?	threshold value to start the charge pump
										'UVLO_Stop'			:	12.4																						#?	threshold value to stop the charge pump
									},
							},
							'GateNetwork'			:	{																									#!	gate drive circuit parameters
									'Config'				:	2																						,	#?	1-> enable | 2->disable
									'ON_Path'		:	{																									#*	sourcing path parameters
										'Rg'				:	1.95																					,	#?	gate ON path resistance
										'Lg'				:	0																						,	#?	gate ON path inductance
										'Rload'				:	10e3																					,	#?	gate pull down resistance
										'Diode'	:	{																										#	reverse blocking diode parameters
											'Vf'			:	0																						,	#?	forward voltage
											'Rd_on'			:	0																						,	#?	ON-state resistance
										},
									},
									'OFF_Path'		:	{																									#*	sinking path parameters
										'Rg'				:	1.0																						,	#?	gate OFF path resistance
										'Lg'				:	0																						,	#?	gate OFF path inductance
										'Diode'	:	{																										#	reverse blocking diode parameters
											'Vf'			:	0																						,	#?	forward voltage
											'Rd_on'			:	0																						,	#?	ON-state resistance
										},
									},
									'NegVolt'		:	{																									#*	negative voltage generator parameters
										'Config'			:	2																						,	#?	1-> enable | 2->disable
										'Dz'	:	{																										#	zener diode parameters
											'Vf'			:	0.7																						,	#?	forward voltage
											'Rd_on'			:	1e-3																					,	#?	ON-state resistance
											'Vz'			:	2																						,	#?	Zener breakdown voltage
											'Rz'			:	1e-3																					,	#?	Zener resistance
										},
										'Dp'	:	{																										#	peak detector diode
											'Vf'			:	0.0																						,	#?	forward voltage
											'Rd_on'			:	0.0																						,	#?	ON-state resistance
										},
										'Cz'	:	{																										#	Zener capacitor parameters
											'Config'		:	1																						,	#?	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
											'Csingle'		:	1e-6																					,	#?	single capacitor value
											'Rsingle'		:	5e-3																					,	#?	ESR of single capacitor
											'Lsingle'		:	0																						,	#?	ESL of single capacitor
											'nPar'			:	1																						,	#?	number of parallel connections
											'nSer'			:	1																						,	#?	number of series connections
											'Vinit'			:	0																						,	#?	capacitor initial voltage
										},
										'Cp'	:	{																										#	peak detector capacitor parameters
											'Config'		:	1																						,	#?	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
											'Csingle'		:	2.2e-6																					,	#?	single capacitor value
											'Rsingle'		:	5e-3																					,	#?	ESR of single capacitor
											'Lsingle'		:	0																						,	#?	ESL of single capacitor
											'nPar'			:	1																						,	#?	number of parallel connections
											'nSer'			:	1																						,	#?	number of series connections
											'Vinit'			:	0																						,	#?	capacitor initial voltage
										},
										'Rp1'				:	43																						,	#?	current limiter of peak detector current
										'Rp2'				:	4.7e3																					,	#?	load resistor to charge the zener diode
									},
								},
							'nParallel'   					:	2                                       												,   #? 	number of parallel devices
							'Rth_jc'						:	[0.002103,0.00875,0.025951,0.093755,0.642636]											,	#?	junction-to-case thermal resistance
							'Cth_jc'						:	[0.000701,0.001817,0.009225,0.023893,0.0833]											,	#?	junction-to-case thermal capacitance
							'Rth_ca'              			:   [0.830418054,46.83713327,10.8124087,1.682365674,-41.85694941]            				,   #? 	case-to-ambient thermal resistance
							'Cth_ca'              			:   [0.163263676,1.272174175,15.0646712,336.385802,-1.581288262]             				,   #? 	case-to-ambient thermal capacitance
							'Tinit'							:	0.0																						,	#?	initial juntion temperature
							'Pinit'							:	0.0																						,	#?	initial power dissipation
							'Coss'					: 	{																									#!	device Coss parameters
								'C'							:	Coss_eff					 															,	#?	device parasitic output capacitance
								'R'							:	0																						,	#?	Coss resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Coss inductance to reduce current slope
								'Coss_er'					:	Crss_er																					,	#?	energy-related Coss
								'Coss_tr'					:	Coss_tr																					,	#?	time-related Coss
								'Vvec'						:	Coss[0]																					,	#? 	device Coss voltage vector
								'Cvec'						:	Coss[1]																					,	#?	device Coss capacity vector
								'Offset'					:	0																						,	#?	parasitic offset to Coss
                                'Factor'					:	1.0																						,	#?	parasitic tolerance to Coss
								'Qoss'						:	Qoss																					,	#?	equivalent charge of Coss
								'Eoss'						:	Eoss																					,	#?	equivalent energy of Coss
								'Config'					:	5																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
						},
                        	'Crss'					:	{																									#!	device Crss parameters
                                'C'							:	Crss_eff					 															,	#?	device parasitic reverse transfer capacitance
								'R'							:	0																						,	#?	Crss resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Crss inductance to reduce current slope
								'Crss_er'					:	Crss_er																					,	#?	energy-related Crss
								'Crss_tr'					:	Crss_tr																					,	#?	time-related Crss
								'Vvec'						:	Crss[0]																					,	#?	device Crss voltage vector
                                'Cvec'						:	Crss[1]																					,	#?	device Crss capacity vector
								'Qvec'						:	Qrss																					,	#?	device accumulated Crss charge vector
								'Offset'					:	0																						,	#?	parasitic offset to Crss
								'Factor'					:	1.0																						,	#?	parasitic tolerance to Crss
								'Qrss'						:	Qrss																					,	#?	equivalent charge of Crss
								'Erss'						:	Erss																					,	#?	equivalent energe of Crss
								'Config'					:	5																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
						},
							'Ciss'					:	{																									#!	device Ciss parameters
								'C'							:	Ciss_eff					 															,	#?	device parasitic input capacitance
								'R'							:	0																						,	#?	Ciss resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Ciss inductance to reduce current slope
								'Ciss_er'					:	Ciss_er																					,	#?	energy-related Ciss
								'Ciss_tr'					:	Ciss_tr																					,	#?	time-related Ciss
								'Vvec'						:	Ciss[0]																					,	#?	device Ciss voltage vector
								'Cvec'						:	Ciss[1]																					,	#?	device Ciss capacity vector
								'Offset'					:	0																						,	#?	parasitic offset to Ciss
								'Factor'					:	1.0																						,	#?	parasitic tolerance to Ciss
								'Qiss'						:	Qiss																					,	#?	equivalent charge of Ciss
								'Eiss'						:	Eiss																					,	#?	equivalent energy of Ciss
								'Config'					:	5																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Cds'					:	{																									#!	device Cds parameters
								'C'							:	Cds_eff					 																,	#?	device parasitic Cds capacitance
								'R'							:	0																						,	#?	Cds resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Cds inductance to reduce current slope
								'Cds_er'					:	Cds_er																					,	#?	energy-related Cds
								'Cds_tr'					:	Cds_tr																					,	#?	time-related Cds
								'Vvec'						:	Coss[0]																					,	#?	device Cds voltage vector
								'Cvec'						:	Cds																						,	#?	device Cds capacity vector
								'Offset_ON'					:	0																						,	#?	tuning offset for turn ON
								'Offset_OFF'				:	0																						,	#?	tuning offset for turn OFF
								'Factor_ON'					:	1.0																						,	#?	tuning factor for turn ON
								'Factor_OFF'				:	1.0																						,	#?	tuning factor for turn OFF
								'Config'					:	4																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Cgd'					:	{																									#!	device Cgd parameters
								'C'							:	Cgd_eff							 														,	#?	device parasitic Cgd capacitance
								'R'							:	0																						,	#?	Cgd resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Cgd inductance to reduce current slope
								'Cgd_er'					:	Cgd_er																					,	#?	energy-related Cgd
								'Cgd_tr'					:	Cgd_tr																					,	#?	time-related Cgd
								'Vvec'						:	Crss[0]																					,	#?	device Cgd voltage vector
								'Cvec'						:	Cgd																						,	#?	device Cgd capacity vector
								'Offset_ON'					:	0																						,	#?	tuning offset for turn ON
								'Offset_OFF'				:	0																						,	#?	tuning offset for turn OFF
								'Factor_ON'					:	1.0																						,	#?	tuning factor for turn ON
								'Factor_OFF'				:	1.0																						,	#?	tuning factor for turn OFF
								'Config'					:	4																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Cgs'					:	{																									#!	device Cgs parameters
								'C'							:	Cgs_eff					 																,	#?	device parasitic Cgs capacitance
								'R'							:	0																						,	#?	Cgs resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Cgs inductance to reduce current slope
								'Cgs_er'					:	Cgs_er																					,	#?	energy-related Cgs
								'Cgs_tr'					:	Cgs_tr																					,	#?	time-related Cgs
								'Vvec'						:	Ciss[0]																					,	#?	device Cgs voltage vector
								'Cvec'						:	Cgs																						,	#?	device Cgs capacity vector
								'Offset_ON'					:	0																						,	#?	tuning offset for turn ON
								'Offset_OFF'				:	0																						,	#?	tuning offset for turn OFF
								'Factor_ON'					:	1.0																						,	#?	tuning factor for turn ON
								'Factor_OFF'				:	1.0																						,	#?	tuning factor for turn OFF
								'Config'					:	4																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Eoff'					:	{																									#!	transistor turn-OFF energy losses
									'Ivec'					:	Ioff																					,	#?	turn-OFF energy current vector
									'Rgvec'					:	[0,100]																					,	#?	OFF path gate resistances vector
									'Tjvec'					:	[-55,175]																				,	#?	junction temperature vector
                                    'Vvec'					:	Voff																					,	#?	turn-OFF voltage vector
                                    'Evec'					:	Eoff																					,	#?	turn-OFF energy vectors
									'Evec_Temp'				:	Eoff_Temp																				,	#?	turn-OFF energy temp scaling vectors
                                    'CAT'					:	catOFF																					,	#?	octave Eoff energy syntax
									'CAT_Temp'				:	catOFF_Temp																				,	#?	octave Eoff energy temp scaling syntax
									'Vgs'					:	0																						,	#?	used OFF path gate-source voltage
									'Vth'					:	1.5																						,	#?	used OFF path threshold voltage
									'Rg'					:	0																							#?	used OFF path gate resistance
						},
							'Eon'					:	{																									#!	transistor turn-ON energy losses
									'Ivec'					:	Ion																						,	#?	turn-ON energy current vector
									'Rgvec'					:	[0,100]																					,	#?	ON path gate resistances vector
									'Tjvec'					:	[-55,175]																				,	#?	junction temperature vector
                                    'Vvec'					:	Von																						,	#?	turn-ON voltage vector
                                    'Evec'					:	Eon																						,	#?	turn-ON energy vectors
									'Evec_Temp'				:	Eon_Temp																				,	#?	turn-ON energy temp scaling vectors
                                    'CAT'					:	catON																					,	#?	octave Eon energy syntax
									'CAT_Temp'				:	catON_Temp																				,	#?	octave Eon energy temp scaling syntax
									'Vgs'					:	12																						,	#?	used ON path gate-source voltage
									'Vth'					:	1.5																						,	#?	used ON path threshold voltage
									'Rg'					:	0																							#?	used ON path gate resistance
						},
							'Tau_deg'						:	100e-9																					,	#?	deglitch filter for currents and voltages
							'RCsnubber'						:	2																						,	#?	1->enable | 2->disable
						}

#?----------------------------------------------------------------------------------------------------------------------------------------------------------------------

Coss,Qoss,Eoss,Coss_tr,Coss_er		=	paramProcess.MOSFETcaps(switchesCossPath,'NVMFS3D6N10MCL','_Coss')
Crss,Qrss,Erss,Crss_tr,Crss_er 		=	paramProcess.MOSFETcaps(switchesCrssPath,'NVMFS3D6N10MCL','_Crss')
Ciss,Qiss,Eiss,Ciss_tr,Ciss_er 		=	paramProcess.MOSFETcaps(switchesCissPath,'NVMFS3D6N10MCL','_Ciss')
Coss_eff 							=	paramProcess.getCmos(Coss,Coss_tr,Coss_er,Coss[0][0],True)
Ciss_eff 							=	paramProcess.getCmos(Ciss,Ciss_tr,Ciss_er,Ciss[0][0],True)
Crss_eff 							=	paramProcess.getCmos(Crss,Crss_tr,Crss_er,Crss[0][0],True)
Cds 						        =	(np.array(Coss[1]) - np.array(Crss[1])).tolist()
Cgs						        	=	(np.array(Ciss[1]) - np.array(Crss[1])).tolist()
Cgd						        	=	Crss[1]
Cds_tr						        =	(np.array(Coss_tr) - np.array(Crss_tr)).tolist()
Cgs_tr						        =	(np.array(Ciss_tr) - np.array(Crss_tr)).tolist()
Cgd_tr						        =	Crss_tr
Cds_er						        =	(np.array(Coss_er) - np.array(Crss_er)).tolist()
Cgs_er						        =	(np.array(Ciss_er) - np.array(Crss_er)).tolist()
Cgd_er						        =	Crss_er
Cds_eff 							=	paramProcess.getCmos([Coss[0],Cds],Cds_tr,Cds_er,Coss[0][0],True)
Cgs_eff 							=	paramProcess.getCmos([Ciss[0],Cgs],Cgs_tr,Cgs_er,Ciss[0][0],True)
Cgd_eff 							=	Crss_eff
Rvec,Tvec							=	paramProcess.MOSFETrdson(switchesRdsonPath,'NVMFS3D6N10MCL','_Rdson')
Nvec,Ivec 							=	paramProcess.MOSFETrdson(switchesIdsonPath,'NVMFS3D6N10MCL','_Rdson')
Ioff,catOFF,Eoff					=	paramProcess.MOSFETenergies(switchesEoffPath,'NVMFS3D6N10MCL','_Eoff')
Voff,catOFF_Temp,Eoff_Temp			=	paramProcess.MOSFETenergies(switchesEoffPath,'NVMFS3D6N10MCL','_Eoff_Temp')
Ion,catON,Eon 						=	paramProcess.MOSFETenergies(switchesEonPath,'NVMFS3D6N10MCL','_Eon')
Von,catON_Temp,Eon_Temp				=	paramProcess.MOSFETenergies(switchesEonPath,'NVMFS3D6N10MCL','_Eon_Temp')
Vfvec,Ifvec,Rd,Vt					=	paramProcess.DiodeVI_data(bodyDiodeVIPath,'NVMFS3D6N10MCL')
Vds_vec,Ids_vec 					=	paramProcess.Forward_Transfer_data(switchesTransferPath,'NVMFS3D6N10MCL')

NVMFS3D6N10MCL		=	{																																	#*	NVMFS3D6N10MCL parameters
							'Config'						:	1																						,	#!	1->electric integrated | 2->electric separate | 3->thermal integrated | 4->thermal separate
							'Transistor'  			: 	{																									#!	transistors parameters
									'Config'				:	2																						,	#?	1->real model | 2->ideal model | 3->behavioral model
									'Thermal'           	:   ''                                  													,   #? 	selected transistor
									'Custom'            	:   []						               													,   #? 	transistor provided custom variables
									'g_fs'					:	1e6																						,	#?	forward transconductance
									'Rg'					:	1																						,	#?	internal gate resistance
									'Lg'					:	0																						,	#?	gate pin inductance
									'Rds_on'            	:   Rvec[-1][-1]*1e-3																		,   #? 	transistor ON resistance
									'Rds_off'				:	'inf'																					,	#?	transistor OFF resistance
									'Rvec'					:	(np.array(Rvec)*1e-3).tolist()														,	#?	absolute Rdson vector corresponding to junction temperature
									'Tvec'					:	Tvec 																					,	#?	junction temperature vector for Rdson
									'RTconfig'				:	1																						,	#?	choose which RT vector to be used
									'RdsonScale'			:	1.0																						,	#?	Rdson scaling to account for min, typ and max deviations
									'Nvec'					:	Nvec 																					,	#?	normalized Rdson vector corresponding to current
									'Ivec'					:	Ivec																					,	#?	current vector for normalized Rdson
									'NIconfig'				:	1																						,	#?	choose which NI vector to be used
									'IdsonScale'			:	1.0																						,	#?	Idson resistance scaling to account for min, typ and max deviations
									'Rsrc'					:	0																						,	#?	kelvin source pin resistance
									'Lsrc'					:	0																						,	#?	kelvin source pin inductance
									'Ls'					:	0																						,	#?	package source inductance
                                    'Ld'					:	0																						,	#?	package drain inductance
									'Rs'					:	0																						,	#?	package source resistance
									'Rd'					:	0																						,	#?	package drain inductance
									'Ksrc'					:	0																						,	#?	kelvin source option, 0->no kelvin | 1->kelvin
									'Vblock'            	:   100                                	 													,   #? 	transistor blocking voltage
									'Id'                	:   132.0                                 													,   #? 	transistor drain current
									'Tr'                	:   10e-9                                   												,   #? 	transistor rise time
									'Tf'                	:   10e-9                                       											, 	#? 	transistor fall time
									'Avalanche'		:	{																									#!	transistor avalanche parameters
										'Config'			:	2																						,	#?	1->enable | 2->disable
										'Voltage'			:	100																						,	#?	avalanche voltage
										'Resistance'		:	1e-3																						#?	avalanche resistance to break voltage state-dependency
									},
									'Transfer'		:	{																									#!	transistor forward transfer parameters
										'Vds'				:	Vds_vec																					,	#?	drain-source voltage vector
										'Vgs'				:	list(np.arange(0.0,12.0+0.4,0.4))													,	#?	gate-source voltage vector
										'Ids'				:	Ids_vec																					,	#?	drain current vector
										'Factor_ON'			:	1.0																						,	#?	scaling factor for Ids at turn ON
										'Factor_OFF'		:	1.0																						,	#?	scaling factor for Ids at turn OFF
										'Factor_Vgs_ON'		:	1.0																						,	#?	scaling factor for Vgs at turn ON
										'Factor_Vgs_OFF'	:	1.0																						,	#?	scaling factor for Vgs at turn OFF
										'Vcoss'				:	0																						,	#?	initial voltage of the Coss
									},
						},
							'BodyDiode'  			:	{																									#!	body diodes paramteters
									'Config'				:	4																						,	#?	1->non-ideal RR | 2->non-ideal | 3->ideal RR | 4->ideal
									'Thermal'           	:   ''                                  													,   #? 	separate body diode
									'Custom'            	:   []					                 													,   #? 	body diode provided custrom variables
									'Rd_on'             	:   Rd[-1]													                              	,  	#? 	body diode ON resistance
									'Rd_off'				:	'inf'																					,	#?	body diode OFF resistance
									'Vf'					:	Vt[-1]																					,	#? 	body diode forward voltage
									'If'                	:   132.0                                 													,   #? 	body diode forward current
									'dIr'               	:   1000e6                                  												,   #? 	body diode current slope
									'Lrr'					:	1e-9																					,	#?	body diode reverse recovery inductance
									'Trr'               	:   28.0e-9                                  												,   #? 	body diode reverse recovery time
									'Irr'               	:   0                                   													,   #? 	body diode reverse recovery current
									'Qrr'               	:   183e-9                                  												, 	#? 	body diode reverse recovery charge
									'Is'                  	:   24              																		, 	#? 	body diode reference current
									'Vs'					:	50																						,	#?	body diode reference voltage
                                    'VIcurve'		:	{																									#!	body diode VI characteristics
                                        'Vfvec'				:	Vfvec																					,	#?	forward voltage vector
                                        'Ifvec'				:	Ifvec																					,	#?	forward current vector
										'Rdvec'				:	Rd																						,	#?	dynamic resistance vector
										'Vtvec'				:	Vt																						,	#?	threshold voltage vector
                                        'Temps'				:	[25,175]																				,	#?	temperature vector
                                        'Vfscale'			:	1.566																						#?	Vf scaling to account for min, typ and max deviations
									},
						},
							'GateDriver'			:	{																									#!	gate driver parameters
									'Config'				:	3																						,	#?	1->high-side | 2->low-side | 3->disable
									'Von'					:	12																						,	#?	ON driving voltage
									'Voff'					:	0																						,	#?	OFF driving voltage
									'Ron'					:	2.5																						,	#?	sourcing output resistance
									'Roff'					:	1.5																						,	#?	sinking output resistance
									'Lon'					:	0																						,	#?	sourcing output inductance
									'Loff'					:	0																						,	#?	sinking output inductance
									'Cload'					:	0																						,	#?	capacitive load on output
									'Rload'					:	'inf'																					,	#?	resistive load on output
									'Delay'					:	50e-9																					,	#?	input-to-output total deadtime
									'Trise'					:	9e-9																					,	#?	output rising time
									'Tfall'					:	7e-9																					,	#?	output falling time
									'UVLO_Start'			:	7.0																						,	#?	UVLO startup voltage threshold
									'UVLO_Stop'				:	6.5																						,	#?	UVLO shutdown voltage threshold
									'UVLO_Delay'			:	100e-9																					,	#?	delay between UVLO startup and shutdown
									'Init_State'			:	0																						,	#?	initial toggling state, 0->OFF | 1->ON
									'CurrentLimit'	:	{																									#*	current limit of driver stage
										'Config'			:	2																						,	#?	1->enable | 2->disable
										'Ts'				: 	0 																						,	#?	sampling time between inductive & capacitive links
										'tau'				: 	0																						,	#?	first-order delay between inductive & capacitive links
                                    	'Rs'				: 	0																						,	#?	source impedance of inductive link
										'Cs'				:	1e-12																					,	#?	source capacitance of capacitive link
                                        'UpLim'				: 	10																						,	#?	max current limit on capacitive link
                                        'LoLim'				: 	-10																						,	#?	min current limit on capacitive link
                                        'Voffset'			: 	0																							#?	voltage offset between inductive & capacitive links
									},
									'Masking'		:	{																									#*	switching stages masking
										'ON'	:	{																										#	ON path masking
											'Config'		:	2																						,	#?	1->enable | 2->disable
											'HIGH'	:	{																									#!	HIGH mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[0, 0]																						#?	mask output
											},
											'LOW'	:	{																									#!	LOW mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[1, 1]																						#?	mask output
											}
										},
										'OFF'	:	{																										#	OFF path masking
											'Config'		:	2																						,	#?	1->enable | 2->disable
											'HIGH'	:	{																									#!	HIGH mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[0, 0]																						#?	mask output
											},
											'LOW'	:	{																									#!	LOW mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[1, 1]																						#?	mask output
											}
										}
									},
									'Boot'			:	{																									#*	bootstrap/charge pump parameters
										'Config'			:	1																						,	#?	1->bootstrap | 2->charge pump
										'Von'				:	14																						,	#?	boostrap driving voltage
										'Cboot'				:	4.7e-6																					,	#?	bootstrap capacitance
										'Vinit'				:	0																						,	#?	bootstrap capacitance initial voltage
										'Rboot'				:	10																						,	#?	bootstrap resistance
										'Vfboot'			:	0.87																					,	#?	bootstrap diode forward voltage
										'Rdboot'			:	1e-3																					,	#?	bootstrap diode ON-state resistance
										'Ichrg'				:	300e-6																					,	#?	charge pump supply current
										'Idis'				:	5e-6																					,	#?	charge pump loading or leakage current
										'Cpar'				:	0																						,	#?	charge pump parallel cap to break state/source dependency
									    'UVLO_Start'		:	11.6																					,	#?	threshold value to start the charge pump
										'UVLO_Stop'			:	12.4																						#?	threshold value to stop the charge pump
									},
							},
							'GateNetwork'			:	{																									#!	gate drive circuit parameters
									'Config'				:	2																						,	#?	1-> enable | 2->disable
									'ON_Path'		:	{																									#*	sourcing path parameters
										'Rg'				:	1																						,	#?	gate ON path resistance
										'Lg'				:	0																						,	#?	gate ON path inductance
										'Rload'				:	10e3																					,	#?	gate pull down resistance
										'Diode'	:	{																										#	reverse blocking diode parameters
											'Vf'			:	0																						,	#?	forward voltage
											'Rd_on'			:	0																						,	#?	ON-state resistance
										},
									},
									'OFF_Path'		:	{																									#*	sinking path parameters
										'Rg'				:	1																						,	#?	gate OFF path resistance
										'Lg'				:	0																						,	#?	gate OFF path inductance
										'Diode'	:	{																										#	reverse blocking diode parameters
											'Vf'			:	0																						,	#?	forward voltage
											'Rd_on'			:	0																						,	#?	ON-state resistance
										},
									},
									'NegVolt'		:	{																									#*	negative voltage generator parameters
										'Config'			:	2																						,	#?	1-> enable | 2->disable
										'Dz'	:	{																										#	zener diode parameters
											'Vf'			:	0.7																						,	#?	forward voltage
											'Rd_on'			:	1e-3																					,	#?	ON-state resistance
											'Vz'			:	2																						,	#?	Zener breakdown voltage
											'Rz'			:	1e-3																					,	#?	Zener resistance
										},
										'Dp'	:	{																										#	peak detector diode
											'Vf'			:	0.0																						,	#?	forward voltage
											'Rd_on'			:	0.0																						,	#?	ON-state resistance
										},
										'Cz'	:	{																										#	Zener capacitor parameters
											'Config'		:	1																						,	#?	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
											'Csingle'		:	1e-6																					,	#?	single capacitor value
											'Rsingle'		:	5e-3																					,	#?	ESR of single capacitor
											'Lsingle'		:	0																						,	#?	ESL of single capacitor
											'nPar'			:	1																						,	#?	number of parallel connections
											'nSer'			:	1																						,	#?	number of series connections
											'Vinit'			:	0																						,	#?	capacitor initial voltage
										},
										'Cp'	:	{																										#	peak detector capacitor parameters
											'Config'		:	1																						,	#?	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
											'Csingle'		:	2.2e-6																					,	#?	single capacitor value
											'Rsingle'		:	5e-3																					,	#?	ESR of single capacitor
											'Lsingle'		:	0																						,	#?	ESL of single capacitor
											'nPar'			:	1																						,	#?	number of parallel connections
											'nSer'			:	1																						,	#?	number of series connections
											'Vinit'			:	0																						,	#?	capacitor initial voltage
										},
										'Rp1'				:	43																						,	#?	current limiter of peak detector current
										'Rp2'				:	4.7e3																					,	#?	load resistor to charge the zener diode
									},
								},
							'nParallel'   					:	1                                       												,   #? 	number of parallel devices
							'Rth_jc'						:	[0.015264,0.131852,0.687605,0.265279]													,	#?	junction-to-case thermal resistance
							'Cth_jc'						:	[0.001045,0.000791,0.009862,0.091526]													,	#?	junction-to-case thermal capacitance
							'Rth_ca'              			:   [15.21677265,3.550500602,7.988490088,1.96139986,2.312302281]            				,   #? 	case-to-ambient thermal resistance
							'Cth_ca'              			:   [1.734533318,1.345923536,18.43461362,242.1156251,0.159741955]             				,   #? 	case-to-ambient thermal capacitance
							'Tinit'							:	0.0																						,	#?	initial juntion temperature
							'Pinit'							:	0.0																						,	#?	initial power dissipation
							'Coss'					: 	{																									#!	device Coss parameters
								'C'							:	Coss_eff					 															,	#?	device parasitic output capacitance
								'R'							:	0																						,	#?	Coss resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Coss inductance to reduce current slope
								'Coss_er'					:	Crss_er																					,	#?	energy-related Coss
								'Coss_tr'					:	Coss_tr																					,	#?	time-related Coss
								'Vvec'						:	Coss[0]																					,	#? 	device Coss voltage vector
								'Cvec'						:	Coss[1]																					,	#?	device Coss capacity vector
								'Offset'					:	0																						,	#?	parasitic offset to Coss
                                'Factor'					:	1.0																						,	#?	parasitic tolerance to Coss
								'Qoss'						:	Qoss																					,	#?	equivalent charge of Coss
								'Eoss'						:	Eoss																					,	#?	equivalent energy of Coss
								'Config'					:	5																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
						},
                        	'Crss'					:	{																									#!	device Crss parameters
                                'C'							:	Crss_eff					 															,	#?	device parasitic reverse transfer capacitance
								'R'							:	0																						,	#?	Crss resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Crss inductance to reduce current slope
								'Crss_er'					:	Crss_er																					,	#?	energy-related Crss
								'Crss_tr'					:	Crss_tr																					,	#?	time-related Crss
								'Vvec'						:	Crss[0]																					,	#?	device Crss voltage vector
                                'Cvec'						:	Crss[1]																					,	#?	device Crss capacity vector
								'Qvec'						:	Qrss																					,	#?	device accumulated Crss charge vector
								'Offset'					:	0																						,	#?	parasitic offset to Crss
								'Factor'					:	1.0																						,	#?	parasitic tolerance to Crss
								'Qrss'						:	Qrss																					,	#?	equivalent charge of Crss
								'Erss'						:	Erss																					,	#?	equivalent energe of Crss
								'Config'					:	5																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
						},
							'Ciss'					:	{																									#!	device Ciss parameters
								'C'							:	Ciss_eff					 															,	#?	device parasitic input capacitance
								'R'							:	0																						,	#?	Ciss resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Ciss inductance to reduce current slope
								'Ciss_er'					:	Ciss_er																					,	#?	energy-related Ciss
								'Ciss_tr'					:	Ciss_tr																					,	#?	time-related Ciss
								'Vvec'						:	Ciss[0]																					,	#?	device Ciss voltage vector
								'Cvec'						:	Ciss[1]																					,	#?	device Ciss capacity vector
								'Offset'					:	0																						,	#?	parasitic offset to Ciss
								'Factor'					:	1.0																						,	#?	parasitic tolerance to Ciss
								'Qiss'						:	Qiss																					,	#?	equivalent charge of Ciss
								'Eiss'						:	Eiss																					,	#?	equivalent energy of Ciss
								'Config'					:	5																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Cds'					:	{																									#!	device Cds parameters
								'C'							:	Cds_eff					 																,	#?	device parasitic Cds capacitance
								'R'							:	0																						,	#?	Cds resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Cds inductance to reduce current slope
								'Cds_er'					:	Cds_er																					,	#?	energy-related Cds
								'Cds_tr'					:	Cds_tr																					,	#?	time-related Cds
								'Vvec'						:	Coss[0]																					,	#?	device Cds voltage vector
								'Cvec'						:	Cds																						,	#?	device Cds capacity vector
								'Offset_ON'					:	0																						,	#?	tuning offset for turn ON
								'Offset_OFF'				:	0																						,	#?	tuning offset for turn OFF
								'Factor_ON'					:	1.0																						,	#?	tuning factor for turn ON
								'Factor_OFF'				:	1.0																						,	#?	tuning factor for turn OFF
								'Config'					:	4																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Cgd'					:	{																									#!	device Cgd parameters
								'C'							:	Cgd_eff							 														,	#?	device parasitic Cgd capacitance
								'R'							:	0																						,	#?	Cgd resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Cgd inductance to reduce current slope
								'Cgd_er'					:	Cgd_er																					,	#?	energy-related Cgd
								'Cgd_tr'					:	Cgd_tr																					,	#?	time-related Cgd
								'Vvec'						:	Crss[0]																					,	#?	device Cgd voltage vector
								'Cvec'						:	Cgd																						,	#?	device Cgd capacity vector
								'Offset_ON'					:	0																						,	#?	tuning offset for turn ON
								'Offset_OFF'				:	0																						,	#?	tuning offset for turn OFF
								'Factor_ON'					:	1.0																						,	#?	tuning factor for turn ON
								'Factor_OFF'				:	1.0																						,	#?	tuning factor for turn OFF
								'Config'					:	4																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Cgs'					:	{																									#!	device Cgs parameters
								'C'							:	Cgs_eff					 																,	#?	device parasitic Cgs capacitance
								'R'							:	0																						,	#?	Cgs resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Cgs inductance to reduce current slope
								'Cgs_er'					:	Cgs_er																					,	#?	energy-related Cgs
								'Cgs_tr'					:	Cgs_tr																					,	#?	time-related Cgs
								'Vvec'						:	Ciss[0]																					,	#?	device Cgs voltage vector
								'Cvec'						:	Cgs																						,	#?	device Cgs capacity vector
								'Offset_ON'					:	0																						,	#?	tuning offset for turn ON
								'Offset_OFF'				:	0																						,	#?	tuning offset for turn OFF
								'Factor_ON'					:	1.0																						,	#?	tuning factor for turn ON
								'Factor_OFF'				:	1.0																						,	#?	tuning factor for turn OFF
								'Config'					:	4																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Eoff'					:	{																									#!	transistor turn-OFF energy losses
									'Ivec'					:	Ioff																					,	#?	turn-OFF energy current vector
									'Rgvec'					:	[0,100]																					,	#?	OFF path gate resistances vector
									'Tjvec'					:	[-55,175]																				,	#?	junction temperature vector
                                    'Vvec'					:	Voff																					,	#?	turn-OFF voltage vector
                                    'Evec'					:	Eoff																					,	#?	turn-OFF energy vectors
									'Evec_Temp'				:	Eoff_Temp																				,	#?	turn-OFF energy temp scaling vectors
                                    'CAT'					:	catOFF																					,	#?	octave Eoff energy syntax
									'CAT_Temp'				:	catOFF_Temp																				,	#?	octave Eoff energy temp scaling syntax
									'Vgs'					:	0																						,	#?	used OFF path gate-source voltage
									'Vth'					:	1.5																						,	#?	used OFF path threshold voltage
									'Rg'					:	1																							#?	used OFF path gate resistance
						},
							'Eon'					:	{																									#!	transistor turn-ON energy losses
									'Ivec'					:	Ion																						,	#?	turn-ON energy current vector
									'Rgvec'					:	[0,100]																					,	#?	ON path gate resistances vector
									'Tjvec'					:	[-55,175]																				,	#?	junction temperature vector
                                    'Vvec'					:	Von																						,	#?	turn-ON voltage vector
                                    'Evec'					:	Eon																						,	#?	turn-ON energy vectors
									'Evec_Temp'				:	Eon_Temp																				,	#?	turn-ON energy temp scaling vectors
                                    'CAT'					:	catON																					,	#?	octave Eon energy syntax
									'CAT_Temp'				:	catON_Temp																				,	#?	octave Eon energy temp scaling syntax
									'Vgs'					:	13																						,	#?	used ON path gate-source voltage
									'Vth'					:	1.5																						,	#?	used ON path threshold voltage
									'Rg'					:	1																							#?	used ON path gate resistance
						},
							'Tau_deg'						:	100e-9																					,	#?	deglitch filter for currents and voltages
							'RCsnubber'						:	2																						,	#?	1->enable | 2->disable
						}

#?----------------------------------------------------------------------------------------------------------------------------------------------------------------------

Coss,Qoss,Eoss,Coss_tr,Coss_er		=	paramProcess.MOSFETcaps(switchesCossPath,'SQJQ186ER','_Coss')
Crss,Qrss,Erss,Crss_tr,Crss_er 		=	paramProcess.MOSFETcaps(switchesCrssPath,'SQJQ186ER','_Crss')
Ciss,Qiss,Eiss,Ciss_tr,Ciss_er 		=	paramProcess.MOSFETcaps(switchesCissPath,'SQJQ186ER','_Ciss')
Coss_eff 							=	paramProcess.getCmos(Coss,Coss_tr,Coss_er,Coss[0][0],True)
Ciss_eff 							=	paramProcess.getCmos(Ciss,Ciss_tr,Ciss_er,Ciss[0][0],True)
Crss_eff 							=	paramProcess.getCmos(Crss,Crss_tr,Crss_er,Crss[0][0],True)
Cds 						        =	(np.array(Coss[1]) - np.array(Crss[1])).tolist()
Cgs						        	=	(np.array(Ciss[1]) - np.array(Crss[1])).tolist()
Cgd						        	=	Crss[1]
Cds_tr						        =	(np.array(Coss_tr) - np.array(Crss_tr)).tolist()
Cgs_tr						        =	(np.array(Ciss_tr) - np.array(Crss_tr)).tolist()
Cgd_tr						        =	Crss_tr
Cds_er						        =	(np.array(Coss_er) - np.array(Crss_er)).tolist()
Cgs_er						        =	(np.array(Ciss_er) - np.array(Crss_er)).tolist()
Cgd_er						        =	Crss_er
Cds_eff 							=	paramProcess.getCmos([Coss[0],Cds],Cds_tr,Cds_er,Coss[0][0],True)
Cgs_eff 							=	paramProcess.getCmos([Ciss[0],Cgs],Cgs_tr,Cgs_er,Ciss[0][0],True)
Cgd_eff 							=	Crss_eff
Rvec,Tvec							=	paramProcess.MOSFETrdson(switchesRdsonPath,'SQJQ186ER','_Rdson')
Nvec,Ivec 							=	paramProcess.MOSFETrdson(switchesIdsonPath,'SQJQ186ER','_Rdson')
Ioff,catOFF,Eoff					=	paramProcess.MOSFETenergies(switchesEoffPath,'SQJQ186ER','_Eoff')
Voff,catOFF_Temp,Eoff_Temp			=	paramProcess.MOSFETenergies(switchesEoffPath,'SQJQ186ER','_Eoff_Temp')
Ion,catON,Eon 						=	paramProcess.MOSFETenergies(switchesEonPath,'SQJQ186ER','_Eon')
Von,catON_Temp,Eon_Temp				=	paramProcess.MOSFETenergies(switchesEonPath,'SQJQ186ER','_Eon_Temp')
Vfvec,Ifvec,Rd,Vt					=	paramProcess.DiodeVI_data(bodyDiodeVIPath,'SQJQ186ER')
#Vds_vec,Ids_vec 					=	paramProcess.Forward_Transfer_data(switchesTransferPath,'SQJQ186ER')

SQJQ186ER_1			=	{																																	#*	SQJQ186ER parameters
							'Config'						:	1																						,	#!	1->electric integrated | 2->electric separate | 3->thermal integrated | 4->thermal separate
							'Transistor'  			: 	{																									#!	transistors parameters
									'Config'				:	2																						,	#?	1->real model | 2->ideal model | 3->behavioral model
									'Thermal'           	:   ''                                  													,   #? 	selected transistor
									'Custom'            	:   []						               													,   #? 	transistor provided custom variables
									'g_fs'					:	1e6																						,	#?	forward transconductance
									'Rg'					:	1																						,	#?	internal gate resistance
									'Lg'					:	0																						,	#?	gate pin inductance
									'Rds_on'            	:   Rvec[-1][-1]*1e-3																		,   #? 	transistor ON resistance
									'Rds_off'				:	'inf'																					,	#?	transistor OFF resistance
									'Rvec'					:	(np.array(Rvec)*1e-3).tolist()														,	#?	absolute Rdson vector corresponding to junction temperature
									'Tvec'					:	Tvec 																					,	#?	junction temperature vector for Rdson
									'RTconfig'				:	1																						,	#?	choose which RT vector to be used, 1->typ | 2->max
									'RdsonScale'			:	1.0																						,	#?	Rdson scaling to account for min, typ and max deviations
									'Nvec'					:	Nvec 																					,	#?	normalized Rdson vector corresponding to current
									'Ivec'					:	Ivec																					,	#?	current vector for normalized Rdson
									'NIconfig'				:	1																						,	#?	choose which NI vector to be used
									'IdsonScale'			:	1.0																						,	#?	Idson resistance scaling to account for min, typ and max deviations
									'Rsrc'					:	0																						,	#?	kelvin source pin resistance
									'Lsrc'					:	0																						,	#?	kelvin source pin inductance
									'Ls'					:	0																						,	#?	package source inductance
                                    'Ld'					:	0																						,	#?	package drain inductance
									'Rs'					:	0																						,	#?	package source resistance
									'Rd'					:	0																						,	#?	package drain inductance
									'Ksrc'					:	0																						,	#?	kelvin source option, 0->no kelvin | 1->kelvin
									'Vblock'            	:   80                                	 													,   #? 	transistor blocking voltage
									'Id'                	:   329.0                                 													,   #? 	transistor drain current
									'Tr'                	:   0                                   													,   #? 	transistor rise time
									'Tf'                	:   0                                       												, 	#? 	transistor fall time
									'Avalanche'		:	{																									#!	transistor avalanche parameters
										'Config'			:	2																						,	#?	1->enable | 2->disable
										'Voltage'			:	80																						,	#?	avalanche voltage
										'Resistance'		:	1e-3																						#?	avalanche resistance to break voltage state-dependency
									},
									'Transfer'		:	{																									#!	transistor forward transfer parameters
										'Vds'				:	Vds_vec																					,	#?	drain-source voltage vector
										'Vgs'				:	[0,10]																					,	#?	gate-source voltage vector
										'Ids'				:	Ids_vec																					,	#?	drain current vector
										'Factor_ON'			:	1.0																						,	#?	scaling factor for Ids at turn ON
										'Factor_OFF'		:	1.0																						,	#?	scaling factor for Ids at turn OFF
										'Factor_Vgs_ON'		:	1.0																						,	#?	scaling factor for Vgs at turn ON
										'Factor_Vgs_OFF'	:	1.0																						,	#?	scaling factor for Vgs at turn OFF
										'Vcoss'				:	0																						,	#?	initial voltage of the Coss
									},
						},
							'BodyDiode'  			:	{																									#!	body diodes paramteters
									'Config'				:	4																						,	#?	1->non-ideal RR | 2->non-ideal | 3->ideal RR | 4->ideal
									'Thermal'           	:   ''                                  													,   #? 	separate body diode
									'Custom'            	:   []					                 													,   #? 	body diode provided custrom variables
									'Rd_on'             	:   Rd[-1]													                              	,  	#? 	body diode ON resistance
									'Rd_off'				:	'inf'																					,	#?	body diode OFF resistance
									'Vf'					:	Vt[-1]																					,	#? 	body diode forward voltage
									'If'                	:   329.0                                 													,   #? 	body diode forward current
									'dIr'               	:   100e6                                  													,   #? 	body diode current slope
									'Lrr'					:	1e-9																					,	#?	body diode reverse recovery inductance
									'Trr'               	:   126e-9                                  												,   #? 	body diode reverse recovery time
									'Irr'               	:   0                                   													,   #? 	body diode reverse recovery current
									'Qrr'               	:   210e-9                                  												,	#? 	body diode reverse recovery charge
									'Is'                  	:   40              																		, 	#? 	body diode reference current
									'Vs'					:	64																						,	#?	body diode reference voltage
                                    'VIcurve'		:	{																									#!	body diode VI characteristics
                                        'Vfvec'				:	Vfvec																					,	#?	forward voltage vector
                                        'Ifvec'				:	Ifvec																					,	#?	forward current vector
										'Rdvec'				:	Rd																						,	#?	dynamic resistance vector
										'Vtvec'				:	Vt																						,	#?	threshold voltage vector
                                        'Temps'				:	[25,150]																				,	#?	temperature vector
                                        'Vfscale'			:	1.375																						#?	Vf scaling to account for min, typ and max deviations
									},
						},
							'GateDriver'			:	{																									#!	gate driver parameters
									'Config'				:	3																						,	#?	1->high-side | 2->low-side | 3->disable
									'Von'					:	12																						,	#?	ON driving voltage
									'Voff'					:	-2																						,	#?	OFF driving voltage
									'Ron'					:	2.5																						,	#?	sourcing output resistance
									'Roff'					:	1.5																						,	#?	sinking output resistance
									'Lon'					:	0																						,	#?	sourcing output inductance
									'Loff'					:	0																						,	#?	sinking output inductance
									'Cload'					:	0																						,	#?	capacitive load on output
									'Rload'					:	'inf'																					,	#?	resistive load on output
									'Delay'					:	50e-9																					,	#?	input-to-output total deadtime
									'Trise'					:	9e-9																					,	#?	output rising time
									'Tfall'					:	7e-9																					,	#?	output falling time
									'UVLO_Start'			:	7.0																						,	#?	UVLO startup voltage threshold
									'UVLO_Stop'				:	6.5																						,	#?	UVLO shutdown voltage threshold
									'UVLO_Delay'			:	100e-9																					,	#?	delay between UVLO startup and shutdown
									'Init_State'			:	0																						,	#?	initial toggling state, 0->OFF | 1->ON
									'CurrentLimit'	:	{																									#*	current limit of driver stage
										'Config'			:	2																						,	#?	1->enable | 2->disable
										'Ts'				: 	0 																						,	#?	sampling time between inductive & capacitive links
										'tau'				: 	0																						,	#?	first-order delay between inductive & capacitive links
                                    	'Rs'				: 	0																						,	#?	source impedance of inductive link
										'Cs'				:	1e-12																					,	#?	source capacitance of capacitive link
                                        'UpLim'				: 	10																						,	#?	max current limit on capacitive link
                                        'LoLim'				: 	-10																						,	#?	min current limit on capacitive link
                                        'Voffset'			: 	0																							#?	voltage offset between inductive & capacitive links
									},
									'Masking'		:	{																									#*	switching stages masking
										'ON'	:	{																										#	ON path masking
											'Config'		:	2																						,	#?	1->enable | 2->disable
											'HIGH'	:	{																									#!	HIGH mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[0, 0]																						#?	mask output
											},
											'LOW'	:	{																									#!	LOW mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[1, 1]																						#?	mask output
											}
										},
										'OFF'	:	{																										#	OFF path masking
											'Config'		:	2																						,	#?	1->enable | 2->disable
											'HIGH'	:	{																									#!	HIGH mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[0, 0]																						#?	mask output
											},
											'LOW'	:	{																									#!	LOW mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[1, 1]																						#?	mask output
											}
										}
									},
									'Boot'			:	{																									#*	bootstrap/charge pump parameters
										'Config'			:	1																						,	#?	1->bootstrap | 2->charge pump
										'Von'				:	14																						,	#?	boostrap driving voltage
										'Cboot'				:	4.7e-6																					,	#?	bootstrap capacitance
										'Vinit'				:	0																						,	#?	bootstrap capacitance initial voltage
										'Rboot'				:	10																						,	#?	bootstrap resistance
										'Vfboot'			:	0.87																					,	#?	bootstrap diode forward voltage
										'Rdboot'			:	1e-3																					,	#?	bootstrap diode ON-state resistance
										'Ichrg'				:	300e-6																					,	#?	charge pump supply current
										'Idis'				:	5e-6																					,	#?	charge pump loading or leakage current
										'Cpar'				:	0																						,	#?	charge pump parallel cap to break state/source dependency
									    'UVLO_Start'		:	11.6																					,	#?	threshold value to start the charge pump
										'UVLO_Stop'			:	12.4																						#?	threshold value to stop the charge pump
									},
							},
							'GateNetwork'			:	{																									#!	gate drive circuit parameters
									'Config'				:	2																						,	#?	1-> enable | 2->disable
									'ON_Path'		:	{																									#*	sourcing path parameters
										'Rg'				:	0.5																						,	#?	gate ON path resistance
										'Lg'				:	0																						,	#?	gate ON path inductance
										'Rload'				:	10e3																					,	#?	gate pull down resistance
										'Diode'	:	{																										#	reverse blocking diode parameters
											'Vf'			:	0																						,	#?	forward voltage
											'Rd_on'			:	0																						,	#?	ON-state resistance
										},
									},
									'OFF_Path'		:	{																									#*	sinking path parameters
										'Rg'				:	0.5																						,	#?	gate OFF path resistance
										'Lg'				:	0																						,	#?	gate OFF path inductance
										'Diode'	:	{																										#	reverse blocking diode parameters
											'Vf'			:	0																						,	#?	forward voltage
											'Rd_on'			:	0																						,	#?	ON-state resistance
										},
									},
									'NegVolt'		:	{																									#*	negative voltage generator parameters
										'Config'			:	2																						,	#?	1-> enable | 2->disable
										'Dz'	:	{																										#	zener diode parameters
											'Vf'			:	0.7																						,	#?	forward voltage
											'Rd_on'			:	1e-3																					,	#?	ON-state resistance
											'Vz'			:	2																						,	#?	Zener breakdown voltage
											'Rz'			:	1e-3																					,	#?	Zener resistance
										},
										'Dp'	:	{																										#	peak detector diode
											'Vf'			:	0.0																						,	#?	forward voltage
											'Rd_on'			:	0.0																						,	#?	ON-state resistance
										},
										'Cz'	:	{																										#	Zener capacitor parameters
											'Config'		:	1																						,	#?	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
											'Csingle'		:	1e-6																					,	#?	single capacitor value
											'Rsingle'		:	5e-3																					,	#?	ESR of single capacitor
											'Lsingle'		:	0																						,	#?	ESL of single capacitor
											'nPar'			:	1																						,	#?	number of parallel connections
											'nSer'			:	1																						,	#?	number of series connections
											'Vinit'			:	0																						,	#?	capacitor initial voltage
										},
										'Cp'	:	{																										#	peak detector capacitor parameters
											'Config'		:	1																						,	#?	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
											'Csingle'		:	2.2e-6																					,	#?	single capacitor value
											'Rsingle'		:	5e-3																					,	#?	ESR of single capacitor
											'Lsingle'		:	0																						,	#?	ESL of single capacitor
											'nPar'			:	1																						,	#?	number of parallel connections
											'nSer'			:	1																						,	#?	number of series connections
											'Vinit'			:	0																						,	#?	capacitor initial voltage
										},
										'Rp1'				:	43																						,	#?	current limiter of peak detector current
										'Rp2'				:	4.7e3																					,	#?	load resistor to charge the zener diode
									},
								},
							'nParallel'   					:	2                                       												,   #? 	number of parallel devices
							'Rth_jc'						:	0.25																					,	#?	junction-to-case thermal resistance
							'Cth_jc'						:	0.00																					,	#?	junction-to-case thermal capacitance
							'Rth_ca'              			:   [0.803,2.119,0.791,0.225,0.962]            												,   #? 	case-to-ambient thermal resistance
							'Cth_ca'              			:   [2.441,0.281,12.082,140.360,40.968]             										,   #? 	case-to-ambient thermal capacitance
							'Tinit'							:	0.0																						,	#?	initial juntion temperature
							'Pinit'							:	0.0																						,	#?	initial power dissipation
							'Coss'					: 	{																									#!	device Coss parameters
								'C'							:	Coss_eff					 															,	#?	device parasitic output capacitance
								'R'							:	0																						,	#?	Coss resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Coss inductance to reduce current slope
								'Coss_er'					:	Crss_er																					,	#?	energy-related Coss
								'Coss_tr'					:	Coss_tr																					,	#?	time-related Coss
								'Vvec'						:	Coss[0]																					,	#? 	device Coss voltage vector
								'Cvec'						:	Coss[1]																					,	#?	device Coss capacity vector
								'Offset'					:	0																						,	#?	parasitic offset to Coss
                                'Factor'					:	1.0																						,	#?	parasitic tolerance to Coss
								'Qoss'						:	Qoss																					,	#?	equivalent charge of Coss
								'Eoss'						:	Eoss																					,	#?	equivalent energy of Coss
								'Config'					:	5																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
						},
                        	'Crss'					:	{																									#!	device Crss parameters
                                'C'							:	Crss_eff					 															,	#?	device parasitic reverse transfer capacitance
								'R'							:	0																						,	#?	Crss resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Crss inductance to reduce current slope
								'Crss_er'					:	Crss_er																					,	#?	energy-related Crss
								'Crss_tr'					:	Crss_tr																					,	#?	time-related Crss
								'Vvec'						:	Crss[0]																					,	#?	device Crss voltage vector
                                'Cvec'						:	Crss[1]																					,	#?	device Crss capacity vector
								'Qvec'						:	Qrss																					,	#?	device accumulated Crss charge vector
								'Offset'					:	0																						,	#?	parasitic offset to Crss
								'Factor'					:	1.0																						,	#?	parasitic tolerance to Crss
								'Qrss'						:	Qrss																					,	#?	equivalent charge of Crss
								'Erss'						:	Erss																					,	#?	equivalent energe of Crss
								'Config'					:	5																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
						},
							'Ciss'					:	{																									#!	device Ciss parameters
								'C'							:	Ciss_eff					 															,	#?	device parasitic input capacitance
								'R'							:	0																						,	#?	Ciss resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Ciss inductance to reduce current slope
								'Ciss_er'					:	Ciss_er																					,	#?	energy-related Ciss
								'Ciss_tr'					:	Ciss_tr																					,	#?	time-related Ciss
								'Vvec'						:	Ciss[0]																					,	#?	device Ciss voltage vector
								'Cvec'						:	Ciss[1]																					,	#?	device Ciss capacity vector
								'Offset'					:	0																						,	#?	parasitic offset to Ciss
								'Factor'					:	1.0																						,	#?	parasitic tolerance to Ciss
								'Qiss'						:	Qiss																					,	#?	equivalent charge of Ciss
								'Eiss'						:	Eiss																					,	#?	equivalent energy of Ciss
								'Config'					:	5																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Cds'					:	{																									#!	device Cds parameters
								'C'							:	Cds_eff					 																,	#?	device parasitic Cds capacitance
								'R'							:	0																						,	#?	Cds resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Cds inductance to reduce current slope
								'Cds_er'					:	Cds_er																					,	#?	energy-related Cds
								'Cds_tr'					:	Cds_tr																					,	#?	time-related Cds
								'Vvec'						:	Coss[0]																					,	#?	device Cds voltage vector
								'Cvec'						:	Cds																						,	#?	device Cds capacity vector
								'Offset_ON'					:	0																						,	#?	tuning offset for turn ON
								'Offset_OFF'				:	0																						,	#?	tuning offset for turn OFF
								'Factor_ON'					:	1.0																						,	#?	tuning factor for turn ON
								'Factor_OFF'				:	1.0																						,	#?	tuning factor for turn OFF
								'Config'					:	4																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Cgd'					:	{																									#!	device Cgd parameters
								'C'							:	Cgd_eff							 														,	#?	device parasitic Cgd capacitance
								'R'							:	0																						,	#?	Cgd resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Cgd inductance to reduce current slope
								'Cgd_er'					:	Cgd_er																					,	#?	energy-related Cgd
								'Cgd_tr'					:	Cgd_tr																					,	#?	time-related Cgd
								'Vvec'						:	Crss[0]																					,	#?	device Cgd voltage vector
								'Cvec'						:	Cgd																						,	#?	device Cgd capacity vector
								'Offset_ON'					:	0																						,	#?	tuning offset for turn ON
								'Offset_OFF'				:	0																						,	#?	tuning offset for turn OFF
								'Factor_ON'					:	1.0																						,	#?	tuning factor for turn ON
								'Factor_OFF'				:	1.0																						,	#?	tuning factor for turn OFF
								'Config'					:	4																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Cgs'					:	{																									#!	device Cgs parameters
								'C'							:	Cgs_eff					 																,	#?	device parasitic Cgs capacitance
								'R'							:	0																						,	#?	Cgs resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Cgs inductance to reduce current slope
								'Cgs_er'					:	Cgs_er																					,	#?	energy-related Cgs
								'Cgs_tr'					:	Cgs_tr																					,	#?	time-related Cgs
								'Vvec'						:	Ciss[0]																					,	#?	device Cgs voltage vector
								'Cvec'						:	Cgs																						,	#?	device Cgs capacity vector
								'Offset_ON'					:	0																						,	#?	tuning offset for turn ON
								'Offset_OFF'				:	0																						,	#?	tuning offset for turn OFF
								'Factor_ON'					:	1.0																						,	#?	tuning factor for turn ON
								'Factor_OFF'				:	1.0																						,	#?	tuning factor for turn OFF
								'Config'					:	4																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Eoff'					:	{																									#!	transistor turn-OFF energy losses
									'Ivec'					:	Ioff																					,	#?	turn-OFF energy current vector
									'Rgvec'					:	[0,100]																					,	#?	OFF path gate resistances vector
									'Tjvec'					:	[-55,175]																				,	#?	junction temperature vector
                                    'Vvec'					:	Voff																					,	#?	turn-OFF voltage vector
                                    'Evec'					:	Eoff																					,	#?	turn-OFF energy vectors
									'Evec_Temp'				:	Eoff_Temp																				,	#?	turn-OFF energy temp scaling vectors
                                    'CAT'					:	catOFF																					,	#?	octave Eoff energy syntax
									'CAT_Temp'				:	catOFF_Temp																				,	#?	octave Eoff energy temp scaling syntax
									'Vgs'					:	0																						,	#?	used OFF path gate-source voltage
									'Vth'					:	1.5																						,	#?	used OFF path threshold voltage
									'Rg'					:	0																							#?	used OFF path gate resistance
						},
							'Eon'					:	{																									#!	transistor turn-ON energy losses
									'Ivec'					:	Ion																						,	#?	turn-ON energy current vector
									'Rgvec'					:	[0,100]																					,	#?	ON path gate resistances vector
									'Tjvec'					:	[-55,175]																				,	#?	junction temperature vector
                                    'Vvec'					:	Von																						,	#?	turn-ON voltage vector
                                    'Evec'					:	Eon																						,	#?	turn-ON energy vectors
									'Evec_Temp'				:	Eon_Temp																				,	#?	turn-ON energy temp scaling vectors
                                    'CAT'					:	catON																					,	#?	octave Eon energy syntax
									'CAT_Temp'				:	catON_Temp																				,	#?	octave Eon energy temp scaling syntax
									'Vgs'					:	12																						,	#?	used ON path gate-source voltage
									'Vth'					:	1.5																						,	#?	used ON path threshold voltage
									'Rg'					:	0																							#?	used ON path gate resistance
						},
							'Tau_deg'						:	100e-9																					,	#?	deglitch filter for currents and voltages
							'RCsnubber'						:	2																						,	#?	1->enable | 2->disable
						}
SQJQ186ER_2 			=	copy.deepcopy(SQJQ186ER_1)
SQJQ186ER_2['Transistor']['Rg']						=	2
SQJQ186ER_2['GateDriver']['Voff']					=	0
SQJQ186ER_2['GateNetwork']['ON_Path']['Rg']			=	1
SQJQ186ER_2['GateNetwork']['OFF_Path']['Rg']		=	1
SQJQ186ER_2['Rth_ca']								=	[1.558,1.022,1.820,0.621]
SQJQ186ER_2['Cth_ca']								=	[5.024,0.342,28.706,114.962]
SQJQ186ER_2['nParallel']							=	1

#?----------------------------------------------------------------------------------------------------------------------------------------------------------------------

Coss,Qoss,Eoss,Coss_tr,Coss_er		=	paramProcess.MOSFETcaps(switchesCossPath,'SQJQ144AER','_Coss')
Crss,Qrss,Erss,Crss_tr,Crss_er 		=	paramProcess.MOSFETcaps(switchesCrssPath,'SQJQ144AER','_Crss')
Ciss,Qiss,Eiss,Ciss_tr,Ciss_er 		=	paramProcess.MOSFETcaps(switchesCissPath,'SQJQ144AER','_Ciss')
Coss_eff 							=	paramProcess.getCmos(Coss,Coss_tr,Coss_er,Coss[0][0],True)
Ciss_eff 							=	paramProcess.getCmos(Ciss,Ciss_tr,Ciss_er,Ciss[0][0],True)
Crss_eff 							=	paramProcess.getCmos(Crss,Crss_tr,Crss_er,Crss[0][0],True)
Cds 						        =	(np.array(Coss[1]) - np.array(Crss[1])).tolist()
Cgs						        	=	(np.array(Ciss[1]) - np.array(Crss[1])).tolist()
Cgd						        	=	Crss[1]
Cds_tr						        =	(np.array(Coss_tr) - np.array(Crss_tr)).tolist()
Cgs_tr						        =	(np.array(Ciss_tr) - np.array(Crss_tr)).tolist()
Cgd_tr						        =	Crss_tr
Cds_er						        =	(np.array(Coss_er) - np.array(Crss_er)).tolist()
Cgs_er						        =	(np.array(Ciss_er) - np.array(Crss_er)).tolist()
Cgd_er						        =	Crss_er
Cds_eff 							=	paramProcess.getCmos([Coss[0],Cds],Cds_tr,Cds_er,Coss[0][0],True)
Cgs_eff 							=	paramProcess.getCmos([Ciss[0],Cgs],Cgs_tr,Cgs_er,Ciss[0][0],True)
Cgd_eff 							=	Crss_eff
Rvec,Tvec							=	paramProcess.MOSFETrdson(switchesRdsonPath,'SQJQ144AER','_Rdson')
Nvec,Ivec 							=	paramProcess.MOSFETrdson(switchesIdsonPath,'SQJQ144AER','_Rdson')
Ioff,catOFF,Eoff					=	paramProcess.MOSFETenergies(switchesEoffPath,'SQJQ144AER','_Eoff')
Voff,catOFF_Temp,Eoff_Temp			=	paramProcess.MOSFETenergies(switchesEoffPath,'SQJQ144AER','_Eoff_Temp')
Ion,catON,Eon 						=	paramProcess.MOSFETenergies(switchesEonPath,'SQJQ144AER','_Eon')
Von,catON_Temp,Eon_Temp				=	paramProcess.MOSFETenergies(switchesEonPath,'SQJQ144AER','_Eon_Temp')
Vfvec,Ifvec,Rd,Vt					=	paramProcess.DiodeVI_data(bodyDiodeVIPath,'SQJQ144AER')
#Vds_vec,Ids_vec 					=	paramProcess.Forward_Transfer_data(switchesTransferPath,'SQJQ144AER')

SQJQ144AER			=	{																																	#*	SQJQ144AER parameters
							'Config'						:	1																						,	#!	1->electric integrated | 2->electric separate | 3->thermal integrated | 4->thermal separate
							'Transistor'  			: 	{																									#!	transistors parameters
									'Config'				:	2																						,	#?	1->real model | 2->ideal model | 3->behavioral model
									'Thermal'           	:   ''                                  													,   #? 	selected transistor
									'Custom'            	:   []						               													,   #? 	transistor provided custom variables
									'g_fs'					:	1e6																						,	#?	forward transconductance
									'Rg'					:	1																						,	#?	internal gate resistance
									'Lg'					:	0																						,	#?	gate pin inductance
									'Rds_on'            	:   Rvec[-1][-1]*1e-3																		,   #? 	transistor ON resistance
									'Rds_off'				:	'inf'																					,	#?	transistor OFF resistance
									'Rvec'					:	(np.array(Rvec)*1e-3).tolist()														,	#?	absolute Rdson vector corresponding to junction temperature
									'Tvec'					:	Tvec 																					,	#?	junction temperature vector for Rdson
									'RTconfig'				:	1																						,	#?	choose which RT vector to be used, 1->typ | 2->max
									'RdsonScale'			:	1.0																						,	#?	Rdson scaling to account for min, typ and max deviations
									'Nvec'					:	Nvec 																					,	#?	normalized Rdson vector corresponding to current
									'Ivec'					:	Ivec																					,	#?	current vector for normalized Rdson
									'NIconfig'				:	1																						,	#?	choose which NI vector to be used
									'IdsonScale'			:	1.0																						,	#?	Idson resistance scaling to account for min, typ and max deviations
									'Rsrc'					:	0																						,	#?	kelvin source pin resistance
									'Lsrc'					:	0																						,	#?	kelvin source pin inductance
									'Ls'					:	0																						,	#?	package source inductance
                                    'Ld'					:	0																						,	#?	package drain inductance
									'Rs'					:	0																						,	#?	package source resistance
									'Rd'					:	0																						,	#?	package drain inductance
									'Ksrc'					:	0																						,	#?	kelvin source option, 0->no kelvin | 1->kelvin
									'Vblock'            	:   40                                	 													,   #? 	transistor blocking voltage
									'Id'                	:   575                                 													,   #? 	transistor drain current
									'Tr'                	:   0                                   													,   #? 	transistor rise time
									'Tf'                	:   0                                       												, 	#? 	transistor fall time
									'Avalanche'		:	{																									#!	transistor avalanche parameters
										'Config'			:	2																						,	#?	1->enable | 2->disable
										'Voltage'			:	40																						,	#?	avalanche voltage
										'Resistance'		:	1e-3																						#?	avalanche resistance to break voltage state-dependency
									},
									'Transfer'		:	{																									#!	transistor forward transfer parameters
										'Vds'				:	Vds_vec																					,	#?	drain-source voltage vector
										'Vgs'				:	[0,20]																					,	#?	gate-source voltage vector
										'Ids'				:	Ids_vec																					,	#?	drain current vector
										'Factor_ON'			:	1.0																						,	#?	scaling factor for Ids at turn ON
										'Factor_OFF'		:	1.0																						,	#?	scaling factor for Ids at turn OFF
										'Factor_Vgs_ON'		:	1.0																						,	#?	scaling factor for Vgs at turn ON
										'Factor_Vgs_OFF'	:	1.0																						,	#?	scaling factor for Vgs at turn OFF
										'Vcoss'				:	0																						,	#?	initial voltage of the Coss
									},
						},
							'BodyDiode'  			:	{																									#!	body diodes paramteters
									'Config'				:	4																						,	#?	1->non-ideal RR | 2->non-ideal | 3->ideal RR | 4->ideal
									'Thermal'           	:   ''                                  													,   #? 	separate body diode
									'Custom'            	:   []					                 													,   #? 	body diode provided custrom variables
									'Rd_on'             	:   Rd[-1]													                              	,  	#? 	body diode ON resistance
									'Rd_off'				:	'inf'																					,	#?	body diode OFF resistance
									'Vf'					:	Vt[-1]																					,	#? 	body diode forward voltage
									'If'                	:   545                                 													,   #? 	body diode forward current
									'dIr'               	:   100e6	                                  												,   #? 	body diode current slope
									'Lrr'					:	1e-9																					,	#?	body diode reverse recovery inductance
									'Trr'               	:   66.0e-9                                  												,   #? 	body diode reverse recovery time
									'Irr'               	:   0                                   													,   #? 	body diode reverse recovery current
									'Qrr'               	:   94e-9	                                  												,	#? 	body diode reverse recovery charge
									'Is'                  	:   15              																		, 	#? 	body diode reference current
									'Vs'					:	32																						,	#?	body diode reference voltage
                                    'VIcurve'		:	{																									#!	body diode VI characteristics
                                        'Vfvec'				:	Vfvec																					,	#?	forward voltage vector
                                        'Ifvec'				:	Ifvec																					,	#?	forward current vector
										'Rdvec'				:	Rd																						,	#?	dynamic resistance vector
										'Vtvec'				:	Vt																						,	#?	threshold voltage vector
                                        'Temps'				:	[25,150]																				,	#?	temperature vector
                                        'Vfscale'			:	1.375																						#?	Vf scaling to account for min, typ and max deviations
									},
						},
							'GateDriver'			:	{																									#!	gate driver parameters
									'Config'				:	3																						,	#?	1->high-side | 2->low-side | 3->disable
									'Von'					:	12																						,	#?	ON driving voltage
									'Voff'					:	0																						,	#?	OFF driving voltage
									'Ron'					:	5																						,	#?	sourcing output resistance
									'Roff'					:	5																						,	#?	sinking output resistance
									'Lon'					:	0																						,	#?	sourcing output inductance
									'Loff'					:	0																						,	#?	sinking output inductance
									'Cload'					:	0																						,	#?	capacitive load on output
									'Rload'					:	'inf'																					,	#?	resistive load on output
									'Delay'					:	0																						,	#?	input-to-output total deadtime
									'Trise'					:	0																						,	#?	output rising time
									'Tfall'					:	0																						,	#?	output falling time
									'UVLO_Start'			:	7.0																						,	#?	UVLO startup voltage threshold
									'UVLO_Stop'				:	6.5																						,	#?	UVLO shutdown voltage threshold
									'UVLO_Delay'			:	100e-9																					,	#?	delay between UVLO startup and shutdown
									'Init_State'			:	0																						,	#?	initial toggling state, 0->OFF | 1->ON
									'CurrentLimit'	:	{																									#*	current limit of driver stage
										'Config'			:	2																						,	#?	1->enable | 2->disable
										'Ts'				: 	0 																						,	#?	sampling time between inductive & capacitive links
										'tau'				: 	0																						,	#?	first-order delay between inductive & capacitive links
                                    	'Rs'				: 	0																						,	#?	source impedance of inductive link
										'Cs'				:	1e-12																					,	#?	source capacitance of capacitive link
                                        'UpLim'				: 	10																						,	#?	max current limit on capacitive link
                                        'LoLim'				: 	-10																						,	#?	min current limit on capacitive link
                                        'Voffset'			: 	0																							#?	voltage offset between inductive & capacitive links
									},
									'Masking'		:	{																									#*	switching stages masking
										'ON'	:	{																										#	ON path masking
											'Config'		:	2																						,	#?	1->enable | 2->disable
											'HIGH'	:	{																									#!	HIGH mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[0, 0]																						#?	mask output
											},
											'LOW'	:	{																									#!	LOW mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[1, 1]																						#?	mask output
											}
										},
										'OFF'	:	{																										#	OFF path masking
											'Config'		:	2																						,	#?	1->enable | 2->disable
											'HIGH'	:	{																									#!	HIGH mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[0, 0]																						#?	mask output
											},
											'LOW'	:	{																									#!	LOW mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[1, 1]																						#?	mask output
											}
										}
									},
									'Boot'			:	{																									#*	bootstrap/charge pump parameters
										'Config'			:	1																						,	#?	1->bootstrap | 2->charge pump
										'Von'				:	14																						,	#?	boostrap driving voltage
										'Cboot'				:	4.7e-6																					,	#?	bootstrap capacitance
										'Vinit'				:	0																						,	#?	bootstrap capacitance initial voltage
										'Rboot'				:	10																						,	#?	bootstrap resistance
										'Vfboot'			:	0.87																					,	#?	bootstrap diode forward voltage
										'Rdboot'			:	1e-3																					,	#?	bootstrap diode ON-state resistance
										'Ichrg'				:	300e-6																					,	#?	charge pump supply current
										'Idis'				:	5e-6																					,	#?	charge pump loading or leakage current
										'Cpar'				:	0																						,	#?	charge pump parallel cap to break state/source dependency
									    'UVLO_Start'		:	11.6																					,	#?	threshold value to start the charge pump
										'UVLO_Stop'			:	12.4																						#?	threshold value to stop the charge pump
									},
							},
							'GateNetwork'			:	{																									#!	gate drive circuit parameters
									'Config'				:	2																						,	#?	1-> enable | 2->disable
									'ON_Path'		:	{																									#*	sourcing path parameters
										'Rg'				:	5																						,	#?	gate ON path resistance
										'Lg'				:	0																						,	#?	gate ON path inductance
										'Rload'				:	10e3																					,	#?	gate pull down resistance
										'Diode'	:	{																										#	reverse blocking diode parameters
											'Vf'			:	0																						,	#?	forward voltage
											'Rd_on'			:	0																						,	#?	ON-state resistance
										},
									},
									'OFF_Path'		:	{																									#*	sinking path parameters
										'Rg'				:	5																						,	#?	gate OFF path resistance
										'Lg'				:	0																						,	#?	gate OFF path inductance
										'Diode'	:	{																										#	reverse blocking diode parameters
											'Vf'			:	0																						,	#?	forward voltage
											'Rd_on'			:	0																						,	#?	ON-state resistance
										},
									},
									'NegVolt'		:	{																									#*	negative voltage generator parameters
										'Config'			:	2																						,	#?	1-> enable | 2->disable
										'Dz'	:	{																										#	zener diode parameters
											'Vf'			:	0.7																						,	#?	forward voltage
											'Rd_on'			:	1e-3																					,	#?	ON-state resistance
											'Vz'			:	2																						,	#?	Zener breakdown voltage
											'Rz'			:	1e-3																					,	#?	Zener resistance
										},
										'Dp'	:	{																										#	peak detector diode
											'Vf'			:	0.0																						,	#?	forward voltage
											'Rd_on'			:	0.0																						,	#?	ON-state resistance
										},
										'Cz'	:	{																										#	Zener capacitor parameters
											'Config'		:	1																						,	#?	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
											'Csingle'		:	1e-6																					,	#?	single capacitor value
											'Rsingle'		:	5e-3																					,	#?	ESR of single capacitor
											'Lsingle'		:	0																						,	#?	ESL of single capacitor
											'nPar'			:	1																						,	#?	number of parallel connections
											'nSer'			:	1																						,	#?	number of series connections
											'Vinit'			:	0																						,	#?	capacitor initial voltage
										},
										'Cp'	:	{																										#	peak detector capacitor parameters
											'Config'		:	1																						,	#?	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
											'Csingle'		:	2.2e-6																					,	#?	single capacitor value
											'Rsingle'		:	5e-3																					,	#?	ESR of single capacitor
											'Lsingle'		:	0																						,	#?	ESL of single capacitor
											'nPar'			:	1																						,	#?	number of parallel connections
											'nSer'			:	1																						,	#?	number of series connections
											'Vinit'			:	0																						,	#?	capacitor initial voltage
										},
										'Rp1'				:	43																						,	#?	current limiter of peak detector current
										'Rp2'				:	4.7e3																					,	#?	load resistor to charge the zener diode
									},
								},
							'nParallel'   					:	2                                       												,   #? 	number of parallel devices
							'Rth_jc'						:	0.25																					,	#?	junction-to-case thermal resistance
							'Cth_jc'						:	0.00																					,	#?	junction-to-case thermal capacitance
							'Rth_ca'              			:   [2.251,4.171,1.986,2.052,5.029]            												,   #? 	case-to-ambient thermal resistance
							'Cth_ca'              			:   [1.877,0.351,18.314,133.837,43.720]             										,   #? 	case-to-ambient thermal capacitance
							'Tinit'							:	0.0																						,	#?	initial juntion temperature
							'Pinit'							:	0.0																						,	#?	initial power dissipation
							'Coss'					: 	{																									#!	device Coss parameters
								'C'							:	Coss_eff					 															,	#?	device parasitic output capacitance
								'R'							:	0																						,	#?	Coss resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Coss inductance to reduce current slope
								'Coss_er'					:	Crss_er																					,	#?	energy-related Coss
								'Coss_tr'					:	Coss_tr																					,	#?	time-related Coss
								'Vvec'						:	Coss[0]																					,	#? 	device Coss voltage vector
								'Cvec'						:	Coss[1]																					,	#?	device Coss capacity vector
								'Offset'					:	0																						,	#?	parasitic offset to Coss
                                'Factor'					:	1.0																						,	#?	parasitic tolerance to Coss
								'Qoss'						:	Qoss																					,	#?	equivalent charge of Coss
								'Eoss'						:	Eoss																					,	#?	equivalent energy of Coss
								'Config'					:	5																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
						},
                        	'Crss'					:	{																									#!	device Crss parameters
                                'C'							:	Crss_eff					 															,	#?	device parasitic reverse transfer capacitance
								'R'							:	0																						,	#?	Crss resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Crss inductance to reduce current slope
								'Crss_er'					:	Crss_er																					,	#?	energy-related Crss
								'Crss_tr'					:	Crss_tr																					,	#?	time-related Crss
								'Vvec'						:	Crss[0]																					,	#?	device Crss voltage vector
                                'Cvec'						:	Crss[1]																					,	#?	device Crss capacity vector
								'Qvec'						:	Qrss																					,	#?	device accumulated Crss charge vector
								'Offset'					:	0																						,	#?	parasitic offset to Crss
								'Factor'					:	1.0																						,	#?	parasitic tolerance to Crss
								'Qrss'						:	Qrss																					,	#?	equivalent charge of Crss
								'Erss'						:	Erss																					,	#?	equivalent energe of Crss
								'Config'					:	5																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
						},
							'Ciss'					:	{																									#!	device Ciss parameters
								'C'							:	Ciss_eff					 															,	#?	device parasitic input capacitance
								'R'							:	0																						,	#?	Ciss resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Ciss inductance to reduce current slope
								'Ciss_er'					:	Ciss_er																					,	#?	energy-related Ciss
								'Ciss_tr'					:	Ciss_tr																					,	#?	time-related Ciss
								'Vvec'						:	Ciss[0]																					,	#?	device Ciss voltage vector
								'Cvec'						:	Ciss[1]																					,	#?	device Ciss capacity vector
								'Offset'					:	0																						,	#?	parasitic offset to Ciss
								'Factor'					:	1.0																						,	#?	parasitic tolerance to Ciss
								'Qiss'						:	Qiss																					,	#?	equivalent charge of Ciss
								'Eiss'						:	Eiss																					,	#?	equivalent energy of Ciss
								'Config'					:	5																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Cds'					:	{																									#!	device Cds parameters
								'C'							:	Cds_eff					 																,	#?	device parasitic Cds capacitance
								'R'							:	0																						,	#?	Cds resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Cds inductance to reduce current slope
								'Cds_er'					:	Cds_er																					,	#?	energy-related Cds
								'Cds_tr'					:	Cds_tr																					,	#?	time-related Cds
								'Vvec'						:	Coss[0]																					,	#?	device Cds voltage vector
								'Cvec'						:	Cds																						,	#?	device Cds capacity vector
								'Offset_ON'					:	0																						,	#?	tuning offset for turn ON
								'Offset_OFF'				:	0																						,	#?	tuning offset for turn OFF
								'Factor_ON'					:	1.0																						,	#?	tuning factor for turn ON
								'Factor_OFF'				:	1.0																						,	#?	tuning factor for turn OFF
								'Config'					:	4																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Cgd'					:	{																									#!	device Cgd parameters
								'C'							:	Cgd_eff							 														,	#?	device parasitic Cgd capacitance
								'R'							:	0																						,	#?	Cgd resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Cgd inductance to reduce current slope
								'Cgd_er'					:	Cgd_er																					,	#?	energy-related Cgd
								'Cgd_tr'					:	Cgd_tr																					,	#?	time-related Cgd
								'Vvec'						:	Crss[0]																					,	#?	device Cgd voltage vector
								'Cvec'						:	Cgd																						,	#?	device Cgd capacity vector
								'Offset_ON'					:	0																						,	#?	tuning offset for turn ON
								'Offset_OFF'				:	0																						,	#?	tuning offset for turn OFF
								'Factor_ON'					:	1.0																						,	#?	tuning factor for turn ON
								'Factor_OFF'				:	1.0																						,	#?	tuning factor for turn OFF
								'Config'					:	4																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Cgs'					:	{																									#!	device Cgs parameters
								'C'							:	Cgs_eff					 																,	#?	device parasitic Cgs capacitance
								'R'							:	0																						,	#?	Cgs resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Cgs inductance to reduce current slope
								'Cgs_er'					:	Cgs_er																					,	#?	energy-related Cgs
								'Cgs_tr'					:	Cgs_tr																					,	#?	time-related Cgs
								'Vvec'						:	Ciss[0]																					,	#?	device Cgs voltage vector
								'Cvec'						:	Cgs																						,	#?	device Cgs capacity vector
								'Offset_ON'					:	0																						,	#?	tuning offset for turn ON
								'Offset_OFF'				:	0																						,	#?	tuning offset for turn OFF
								'Factor_ON'					:	1.0																						,	#?	tuning factor for turn ON
								'Factor_OFF'				:	1.0																						,	#?	tuning factor for turn OFF
								'Config'					:	4																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Eoff'					:	{																									#!	transistor turn-OFF energy losses
									'Ivec'					:	Ioff																					,	#?	turn-OFF energy current vector
									'Rgvec'					:	[0,100]																					,	#?	OFF path gate resistances vector
									'Tjvec'					:	[-55,175]																				,	#?	junction temperature vector
                                    'Vvec'					:	Voff																					,	#?	turn-OFF voltage vector
                                    'Evec'					:	Eoff																					,	#?	turn-OFF energy vectors
									'Evec_Temp'				:	Eoff_Temp																				,	#?	turn-OFF energy temp scaling vectors
                                    'CAT'					:	catOFF																					,	#?	octave Eoff energy syntax
									'CAT_Temp'				:	catOFF_Temp																				,	#?	octave Eoff energy temp scaling syntax
									'Vgs'					:	0																						,	#?	used OFF path gate-source voltage
									'Vth'					:	1.5																						,	#?	used OFF path threshold voltage
									'Rg'					:	0																							#?	used OFF path gate resistance
						},
							'Eon'					:	{																									#!	transistor turn-ON energy losses
									'Ivec'					:	Ion																						,	#?	turn-ON energy current vector
									'Rgvec'					:	[0,100]																					,	#?	ON path gate resistances vector
									'Tjvec'					:	[-55,175]																				,	#?	junction temperature vector
                                    'Vvec'					:	Von																						,	#?	turn-ON voltage vector
                                    'Evec'					:	Eon																						,	#?	turn-ON energy vectors
									'Evec_Temp'				:	Eon_Temp																				,	#?	turn-ON energy temp scaling vectors
                                    'CAT'					:	catON																					,	#?	octave Eon energy syntax
									'CAT_Temp'				:	catON_Temp																				,	#?	octave Eon energy temp scaling syntax
									'Vgs'					:	12																						,	#?	used ON path gate-source voltage
									'Vth'					:	1.5																						,	#?	used ON path threshold voltage
									'Rg'					:	0																							#?	used ON path gate resistance
						},
							'Tau_deg'						:	100e-9																					,	#?	deglitch filter for currents and voltages
							'RCsnubber'						:	2																						,	#?	1->enable | 2->disable
						}

#?----------------------------------------------------------------------------------------------------------------------------------------------------------------------

Coss,Qoss,Eoss,Coss_tr,Coss_er		=	paramProcess.MOSFETcaps(switchesCossPath,'NVMJST0D7N04XM','_Coss')
Crss,Qrss,Erss,Crss_tr,Crss_er 		=	paramProcess.MOSFETcaps(switchesCrssPath,'NVMJST0D7N04XM','_Crss')
Ciss,Qiss,Eiss,Ciss_tr,Ciss_er 		=	paramProcess.MOSFETcaps(switchesCissPath,'NVMJST0D7N04XM','_Ciss')
Coss_eff 							=	paramProcess.getCmos(Coss,Coss_tr,Coss_er,Coss[0][0],True)
Ciss_eff 							=	paramProcess.getCmos(Ciss,Ciss_tr,Ciss_er,Ciss[0][0],True)
Crss_eff 							=	paramProcess.getCmos(Crss,Crss_tr,Crss_er,Crss[0][0],True)
Cds 						        =	(np.array(Coss[1]) - np.array(Crss[1])).tolist()
Cgs						        	=	(np.array(Ciss[1]) - np.array(Crss[1])).tolist()
Cgd						        	=	Crss[1]
Cds_tr						        =	(np.array(Coss_tr) - np.array(Crss_tr)).tolist()
Cgs_tr						        =	(np.array(Ciss_tr) - np.array(Crss_tr)).tolist()
Cgd_tr						        =	Crss_tr
Cds_er						        =	(np.array(Coss_er) - np.array(Crss_er)).tolist()
Cgs_er						        =	(np.array(Ciss_er) - np.array(Crss_er)).tolist()
Cgd_er						        =	Crss_er
Cds_eff 							=	paramProcess.getCmos([Coss[0],Cds],Cds_tr,Cds_er,Coss[0][0],True)
Cgs_eff 							=	paramProcess.getCmos([Ciss[0],Cgs],Cgs_tr,Cgs_er,Ciss[0][0],True)
Cgd_eff 							=	Crss_eff
Rvec,Tvec							=	paramProcess.MOSFETrdson(switchesRdsonPath,'NVMJST0D7N04XM','_Rdson')
Nvec,Ivec 							=	paramProcess.MOSFETrdson(switchesIdsonPath,'NVMJST0D7N04XM','_Rdson')
Ioff,catOFF,Eoff					=	paramProcess.MOSFETenergies(switchesEoffPath,'NVMJST0D7N04XM','_Eoff')
Voff,catOFF_Temp,Eoff_Temp			=	paramProcess.MOSFETenergies(switchesEoffPath,'NVMJST0D7N04XM','_Eoff_Temp')
Ion,catON,Eon 						=	paramProcess.MOSFETenergies(switchesEonPath,'NVMJST0D7N04XM','_Eon')
Von,catON_Temp,Eon_Temp				=	paramProcess.MOSFETenergies(switchesEonPath,'NVMJST0D7N04XM','_Eon_Temp')
Vfvec,Ifvec,Rd,Vt					=	paramProcess.DiodeVI_data(bodyDiodeVIPath,'NVMJST0D7N04XM')
Vds_vec,Ids_vec 					=	paramProcess.Forward_Transfer_data(switchesTransferPath,'NVMJST0D7N04XM')

NVMJST0D7N04XM		=	{																																	#*	NVMJST0D7N04XM parameters
							'Config'						:	1																						,	#!	1->electric integrated | 2->electric separate | 3->thermal integrated | 4->thermal separate
							'Transistor'  			: 	{																									#!	transistors parameters
									'Config'				:	2																						,	#?	1->real model | 2->ideal model | 3->behavioral model
									'Thermal'           	:   ''                                  													,   #? 	selected transistor
									'Custom'            	:   []						               													,   #? 	transistor provided custom variables
									'g_fs'					:	1e6																						,	#?	forward transconductance
									'Rg'					:	1																						,	#?	internal gate resistance
									'Lg'					:	0																						,	#?	gate pin inductance
									'Rds_on'            	:   Rvec[-1][-1]*1e-3																		,   #? 	transistor ON resistance
									'Rds_off'				:	'inf'																					,	#?	transistor OFF resistance
									'Rvec'					:	(np.array(Rvec)*1e-3).tolist()														,	#?	absolute Rdson vector corresponding to junction temperature
									'Tvec'					:	Tvec 																					,	#?	junction temperature vector for Rdson
									'RTconfig'				:	1																						,	#?	choose which RT vector to be used, 1->typ | 2->max
									'RdsonScale'			:	1.164																					,	#?	Rdson scaling to account for min, typ and max deviations
									'Nvec'					:	Nvec 																					,	#?	normalized Rdson vector corresponding to current
									'Ivec'					:	Ivec																					,	#?	current vector for normalized Rdson
									'NIconfig'				:	1																						,	#?	choose which NI vector to be used
									'IdsonScale'			:	1.0																						,	#?	Idson resistance scaling to account for min, typ and max deviations
									'Rsrc'					:	0																						,	#?	kelvin source pin resistance
									'Lsrc'					:	0																						,	#?	kelvin source pin inductance
									'Ls'					:	0																						,	#?	package source inductance
                                    'Ld'					:	0																						,	#?	package drain inductance
									'Rs'					:	0																						,	#?	package source resistance
									'Rd'					:	0																						,	#?	package drain inductance
									'Ksrc'					:	0																						,	#?	kelvin source option, 0->no kelvin | 1->kelvin
									'Vblock'            	:   40                                	 													,   #? 	transistor blocking voltage
									'Id'                	:   553                                 													,   #? 	transistor drain current
									'Tr'                	:   0                                   													,   #? 	transistor rise time
									'Tf'                	:   0                                       												, 	#? 	transistor fall time
									'Avalanche'		:	{																									#!	transistor avalanche parameters
										'Config'			:	2																						,	#?	1->enable | 2->disable
										'Voltage'			:	40																						,	#?	avalanche voltage
										'Resistance'		:	1e-3																						#?	avalanche resistance to break voltage state-dependency
									},
									'Transfer'		:	{																									#!	transistor forward transfer parameters
										'Vds'				:	Vds_vec																					,	#?	drain-source voltage vector
										'Vgs'				:	list(np.arange(0.0,12.0+0.2,0.2))													,	#?	gate-source voltage vector
										'Ids'				:	Ids_vec																					,	#?	drain current vector
										'Factor_ON'			:	1.0																						,	#?	scaling factor for Ids at turn ON
										'Factor_OFF'		:	1.0																						,	#?	scaling factor for Ids at turn OFF
										'Factor_Vgs_ON'		:	1.0																						,	#?	scaling factor for Vgs at turn ON
										'Factor_Vgs_OFF'	:	1.0																						,	#?	scaling factor for Vgs at turn OFF
										'Vcoss'				:	0																						,	#?	initial voltage of the Coss
									},
						},
							'BodyDiode'  			:	{																									#!	body diodes paramteters
									'Config'				:	4																						,	#?	1->non-ideal RR | 2->non-ideal | 3->ideal RR | 4->ideal
									'Thermal'           	:   ''                                  													,   #? 	separate body diode
									'Custom'            	:   []					                 													,   #? 	body diode provided custrom variables
									'Rd_on'             	:   Rd[-1]													                             	,  	#? 	body diode ON resistance
									'Rd_off'				:	'inf'																					,	#?	body diode OFF resistance
									'Vf'					:	Vt[-1]																					,	#? 	body diode forward voltage
									'If'                	:   553                                 													,   #? 	body diode forward current
									'dIr'               	:   100e6	                                  												,   #? 	body diode current slope
									'Lrr'					:	1e-9																					,	#?	body diode reverse recovery inductance
									'Trr'               	:   69.0e-9                                  												,   #? 	body diode reverse recovery time
									'Irr'               	:   0                                   													,   #? 	body diode reverse recovery current
									'Qrr'               	:   132e-9	                                  												,	#? 	body diode reverse recovery charge
									'Is'                  	:   17.8              																		, 	#? 	body diode reference current
									'Vs'					:	32																						,	#?	body diode reference voltage
                                    'VIcurve'		:	{																									#!	body diode VI characteristics
                                        'Vfvec'				:	Vfvec																					,	#?	forward voltage vector
                                        'Ifvec'				:	Ifvec																					,	#?	forward current vector
										'Rdvec'				:	Rd																						,	#?	dynamic resistance vector
										'Vtvec'				:	Vt																						,	#?	threshold voltage vector
                                        'Temps'				:	[-55,25,175]																			,	#?	temperature vector
                                        'Vfscale'			:	1.00																						#?	Vf scaling to account for min, typ and max deviations
									},
						},
							'GateDriver'			:	{																									#!	gate driver parameters
									'Config'				:	3																						,	#?	1->high-side | 2->low-side | 3->disable
									'Von'					:	12																						,	#?	ON driving voltage
									'Voff'					:	0																						,	#?	OFF driving voltage
									'Ron'					:	5																						,	#?	sourcing output resistance
									'Roff'					:	5																						,	#?	sinking output resistance
									'Lon'					:	0																						,	#?	sourcing output inductance
									'Loff'					:	0																						,	#?	sinking output inductance
									'Cload'					:	0																						,	#?	capacitive load on output
									'Rload'					:	'inf'																					,	#?	resistive load on output
									'Delay'					:	0																						,	#?	input-to-output total deadtime
									'Trise'					:	0																						,	#?	output rising time
									'Tfall'					:	0																						,	#?	output falling time
									'UVLO_Start'			:	7.0																						,	#?	UVLO startup voltage threshold
									'UVLO_Stop'				:	6.5																						,	#?	UVLO shutdown voltage threshold
									'UVLO_Delay'			:	100e-9																					,	#?	delay between UVLO startup and shutdown
									'Init_State'			:	0																						,	#?	initial toggling state, 0->OFF | 1->ON
									'CurrentLimit'	:	{																									#*	current limit of driver stage
										'Config'			:	2																						,	#?	1->enable | 2->disable
										'Ts'				: 	0 																						,	#?	sampling time between inductive & capacitive links
										'tau'				: 	0																						,	#?	first-order delay between inductive & capacitive links
                                    	'Rs'				: 	0																						,	#?	source impedance of inductive link
										'Cs'				:	1e-12																					,	#?	source capacitance of capacitive link
                                        'UpLim'				: 	10																						,	#?	max current limit on capacitive link
                                        'LoLim'				: 	-10																						,	#?	min current limit on capacitive link
                                        'Voffset'			: 	0																							#?	voltage offset between inductive & capacitive links
									},
									'Masking'		:	{																									#*	switching stages masking
										'ON'	:	{																										#	ON path masking
											'Config'		:	2																						,	#?	1->enable | 2->disable
											'HIGH'	:	{																									#!	HIGH mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[0, 0]																						#?	mask output
											},
											'LOW'	:	{																									#!	LOW mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[1, 1]																						#?	mask output
											}
										},
										'OFF'	:	{																										#	OFF path masking
											'Config'		:	2																						,	#?	1->enable | 2->disable
											'HIGH'	:	{																									#!	HIGH mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[0, 0]																						#?	mask output
											},
											'LOW'	:	{																									#!	LOW mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[1, 1]																						#?	mask output
											}
										}
									},
									'Boot'			:	{																									#*	bootstrap/charge pump parameters
										'Config'			:	1																						,	#?	1->bootstrap | 2->charge pump
										'Von'				:	14																						,	#?	boostrap driving voltage
										'Cboot'				:	4.7e-6																					,	#?	bootstrap capacitance
										'Vinit'				:	0																						,	#?	bootstrap capacitance initial voltage
										'Rboot'				:	10																						,	#?	bootstrap resistance
										'Vfboot'			:	0.87																					,	#?	bootstrap diode forward voltage
										'Rdboot'			:	1e-3																					,	#?	bootstrap diode ON-state resistance
										'Ichrg'				:	300e-6																					,	#?	charge pump supply current
										'Idis'				:	5e-6																					,	#?	charge pump loading or leakage current
										'Cpar'				:	0																						,	#?	charge pump parallel cap to break state/source dependency
									    'UVLO_Start'		:	11.6																					,	#?	threshold value to start the charge pump
										'UVLO_Stop'			:	12.4																						#?	threshold value to stop the charge pump
									},
							},
							'GateNetwork'			:	{																									#!	gate drive circuit parameters
									'Config'				:	2																						,	#?	1-> enable | 2->disable
									'ON_Path'		:	{																									#*	sourcing path parameters
										'Rg'				:	5																						,	#?	gate ON path resistance
										'Lg'				:	0																						,	#?	gate ON path inductance
										'Rload'				:	10e3																					,	#?	gate pull down resistance
										'Diode'	:	{																										#	reverse blocking diode parameters
											'Vf'			:	0																						,	#?	forward voltage
											'Rd_on'			:	0																						,	#?	ON-state resistance
										},
									},
									'OFF_Path'		:	{																									#*	sinking path parameters
										'Rg'				:	5																						,	#?	gate OFF path resistance
										'Lg'				:	0																						,	#?	gate OFF path inductance
										'Diode'	:	{																										#	reverse blocking diode parameters
											'Vf'			:	0																						,	#?	forward voltage
											'Rd_on'			:	0																						,	#?	ON-state resistance
										},
									},
									'NegVolt'		:	{																									#*	negative voltage generator parameters
										'Config'			:	2																						,	#?	1-> enable | 2->disable
										'Dz'	:	{																										#	zener diode parameters
											'Vf'			:	0.7																						,	#?	forward voltage
											'Rd_on'			:	1e-3																					,	#?	ON-state resistance
											'Vz'			:	2																						,	#?	Zener breakdown voltage
											'Rz'			:	1e-3																					,	#?	Zener resistance
										},
										'Dp'	:	{																										#	peak detector diode
											'Vf'			:	0.0																						,	#?	forward voltage
											'Rd_on'			:	0.0																						,	#?	ON-state resistance
										},
										'Cz'	:	{																										#	Zener capacitor parameters
											'Config'		:	1																						,	#?	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
											'Csingle'		:	1e-6																					,	#?	single capacitor value
											'Rsingle'		:	5e-3																					,	#?	ESR of single capacitor
											'Lsingle'		:	0																						,	#?	ESL of single capacitor
											'nPar'			:	1																						,	#?	number of parallel connections
											'nSer'			:	1																						,	#?	number of series connections
											'Vinit'			:	0																						,	#?	capacitor initial voltage
										},
										'Cp'	:	{																										#	peak detector capacitor parameters
											'Config'		:	1																						,	#?	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
											'Csingle'		:	2.2e-6																					,	#?	single capacitor value
											'Rsingle'		:	5e-3																					,	#?	ESR of single capacitor
											'Lsingle'		:	0																						,	#?	ESL of single capacitor
											'nPar'			:	1																						,	#?	number of parallel connections
											'nSer'			:	1																						,	#?	number of series connections
											'Vinit'			:	0																						,	#?	capacitor initial voltage
										},
										'Rp1'				:	43																						,	#?	current limiter of peak detector current
										'Rp2'				:	4.7e3																					,	#?	load resistor to charge the zener diode
									},
								},
							'nParallel'   					:	2                                       												,   #? 	number of parallel devices
							'Rth_jc'						:	[0.00129071,0.0068152,0.0254695,0.0909854,0.241406]										,	#?	junction-to-case thermal resistance
							'Cth_jc'						:	[2.78E-05,7.68E-05,0.00083487,0.0023042,0.0214]											,	#?	junction-to-case thermal capacitance
							'Rth_ca'              			:   0.0            																			,   #? 	case-to-ambient thermal resistance
							'Cth_ca'              			:   0.0             																		,   #? 	case-to-ambient thermal capacitance
							'Tinit'							:	0.0																						,	#?	initial juntion temperature
							'Pinit'							:	0.0																						,	#?	initial power dissipation
							'Coss'					: 	{																									#!	device Coss parameters
								'C'							:	Coss_eff					 															,	#?	device parasitic output capacitance
								'R'							:	0																						,	#?	Coss resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Coss inductance to reduce current slope
								'Coss_er'					:	Crss_er																					,	#?	energy-related Coss
								'Coss_tr'					:	Coss_tr																					,	#?	time-related Coss
								'Vvec'						:	Coss[0]																					,	#? 	device Coss voltage vector
								'Cvec'						:	Coss[1]																					,	#?	device Coss capacity vector
								'Offset'					:	0																						,	#?	parasitic offset to Coss
                                'Factor'					:	1.0																						,	#?	parasitic tolerance to Coss
								'Qoss'						:	Qoss																					,	#?	equivalent charge of Coss
								'Eoss'						:	Eoss																					,	#?	equivalent energy of Coss
								'Config'					:	5																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
						},
                        	'Crss'					:	{																									#!	device Crss parameters
                                'C'							:	Crss_eff					 															,	#?	device parasitic reverse transfer capacitance
								'R'							:	0																						,	#?	Crss resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Crss inductance to reduce current slope
								'Crss_er'					:	Crss_er																					,	#?	energy-related Crss
								'Crss_tr'					:	Crss_tr																					,	#?	time-related Crss
								'Vvec'						:	Crss[0]																					,	#?	device Crss voltage vector
                                'Cvec'						:	Crss[1]																					,	#?	device Crss capacity vector
								'Qvec'						:	Qrss																					,	#?	device accumulated Crss charge vector
								'Offset'					:	0																						,	#?	parasitic offset to Crss
								'Factor'					:	1.0																						,	#?	parasitic tolerance to Crss
								'Qrss'						:	Qrss																					,	#?	equivalent charge of Crss
								'Erss'						:	Erss																					,	#?	equivalent energe of Crss
								'Config'					:	5																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
						},
							'Ciss'					:	{																									#!	device Ciss parameters
								'C'							:	Ciss_eff					 															,	#?	device parasitic input capacitance
								'R'							:	0																						,	#?	Ciss resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Ciss inductance to reduce current slope
								'Ciss_er'					:	Ciss_er																					,	#?	energy-related Ciss
								'Ciss_tr'					:	Ciss_tr																					,	#?	time-related Ciss
								'Vvec'						:	Ciss[0]																					,	#?	device Ciss voltage vector
								'Cvec'						:	Ciss[1]																					,	#?	device Ciss capacity vector
								'Offset'					:	0																						,	#?	parasitic offset to Ciss
								'Factor'					:	1.0																						,	#?	parasitic tolerance to Ciss
								'Qiss'						:	Qiss																					,	#?	equivalent charge of Ciss
								'Eiss'						:	Eiss																					,	#?	equivalent energy of Ciss
								'Config'					:	5																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Cds'					:	{																									#!	device Cds parameters
								'C'							:	Cds_eff					 																,	#?	device parasitic Cds capacitance
								'R'							:	0																						,	#?	Cds resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Cds inductance to reduce current slope
								'Cds_er'					:	Cds_er																					,	#?	energy-related Cds
								'Cds_tr'					:	Cds_tr																					,	#?	time-related Cds
								'Vvec'						:	Coss[0]																					,	#?	device Cds voltage vector
								'Cvec'						:	Cds																						,	#?	device Cds capacity vector
								'Offset_ON'					:	0																						,	#?	tuning offset for turn ON
								'Offset_OFF'				:	0																						,	#?	tuning offset for turn OFF
								'Factor_ON'					:	1.0																						,	#?	tuning factor for turn ON
								'Factor_OFF'				:	1.0																						,	#?	tuning factor for turn OFF
								'Config'					:	4																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Cgd'					:	{																									#!	device Cgd parameters
								'C'							:	Cgd_eff							 														,	#?	device parasitic Cgd capacitance
								'R'							:	0																						,	#?	Cgd resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Cgd inductance to reduce current slope
								'Cgd_er'					:	Cgd_er																					,	#?	energy-related Cgd
								'Cgd_tr'					:	Cgd_tr																					,	#?	time-related Cgd
								'Vvec'						:	Crss[0]																					,	#?	device Cgd voltage vector
								'Cvec'						:	Cgd																						,	#?	device Cgd capacity vector
								'Offset_ON'					:	0																						,	#?	tuning offset for turn ON
								'Offset_OFF'				:	0																						,	#?	tuning offset for turn OFF
								'Factor_ON'					:	1.0																						,	#?	tuning factor for turn ON
								'Factor_OFF'				:	1.0																						,	#?	tuning factor for turn OFF
								'Config'					:	4																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Cgs'					:	{																									#!	device Cgs parameters
								'C'							:	Cgs_eff					 																,	#?	device parasitic Cgs capacitance
								'R'							:	0																						,	#?	Cgs resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Cgs inductance to reduce current slope
								'Cgs_er'					:	Cgs_er																					,	#?	energy-related Cgs
								'Cgs_tr'					:	Cgs_tr																					,	#?	time-related Cgs
								'Vvec'						:	Ciss[0]																					,	#?	device Cgs voltage vector
								'Cvec'						:	Cgs																						,	#?	device Cgs capacity vector
								'Offset_ON'					:	0																						,	#?	tuning offset for turn ON
								'Offset_OFF'				:	0																						,	#?	tuning offset for turn OFF
								'Factor_ON'					:	1.0																						,	#?	tuning factor for turn ON
								'Factor_OFF'				:	1.0																						,	#?	tuning factor for turn OFF
								'Config'					:	4																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Eoff'					:	{																									#!	transistor turn-OFF energy losses
									'Ivec'					:	Ioff																					,	#?	turn-OFF energy current vector
									'Rgvec'					:	[0,100]																					,	#?	OFF path gate resistances vector
									'Tjvec'					:	[-55,175]																				,	#?	junction temperature vector
                                    'Vvec'					:	Voff																					,	#?	turn-OFF voltage vector
                                    'Evec'					:	Eoff																					,	#?	turn-OFF energy vectors
									'Evec_Temp'				:	Eoff_Temp																				,	#?	turn-OFF energy temp scaling vectors
                                    'CAT'					:	catOFF																					,	#?	octave Eoff energy syntax
									'CAT_Temp'				:	catOFF_Temp																				,	#?	octave Eoff energy temp scaling syntax
									'Vgs'					:	0																						,	#?	used OFF path gate-source voltage
									'Vth'					:	1.5																						,	#?	used OFF path threshold voltage
									'Rg'					:	0																							#?	used OFF path gate resistance
						},
							'Eon'					:	{																									#!	transistor turn-ON energy losses
									'Ivec'					:	Ion																						,	#?	turn-ON energy current vector
									'Rgvec'					:	[0,100]																					,	#?	ON path gate resistances vector
									'Tjvec'					:	[-55,175]																				,	#?	junction temperature vector
                                    'Vvec'					:	Von																						,	#?	turn-ON voltage vector
                                    'Evec'					:	Eon																						,	#?	turn-ON energy vectors
									'Evec_Temp'				:	Eon_Temp																				,	#?	turn-ON energy temp scaling vectors
                                    'CAT'					:	catON																					,	#?	octave Eon energy syntax
									'CAT_Temp'				:	catON_Temp																				,	#?	octave Eon energy temp scaling syntax
									'Vgs'					:	12																						,	#?	used ON path gate-source voltage
									'Vth'					:	1.5																						,	#?	used ON path threshold voltage
									'Rg'					:	0																							#?	used ON path gate resistance
						},
							'Tau_deg'						:	100e-9																					,	#?	deglitch filter for currents and voltages
							'RCsnubber'						:	2																						,	#?	1->enable | 2->disable
						}

#?----------------------------------------------------------------------------------------------------------------------------------------------------------------------

Coss,Qoss,Eoss,Coss_tr,Coss_er		=	paramProcess.MOSFETcaps(switchesCossPath,'NVMJST0D5N04XM','_Coss')
Crss,Qrss,Erss,Crss_tr,Crss_er 		=	paramProcess.MOSFETcaps(switchesCrssPath,'NVMJST0D5N04XM','_Crss')
Ciss,Qiss,Eiss,Ciss_tr,Ciss_er 		=	paramProcess.MOSFETcaps(switchesCissPath,'NVMJST0D5N04XM','_Ciss')
Coss_eff 							=	paramProcess.getCmos(Coss,Coss_tr,Coss_er,Coss[0][0],True)
Ciss_eff 							=	paramProcess.getCmos(Ciss,Ciss_tr,Ciss_er,Ciss[0][0],True)
Crss_eff 							=	paramProcess.getCmos(Crss,Crss_tr,Crss_er,Crss[0][0],True)
Cds 						        =	(np.array(Coss[1]) - np.array(Crss[1])).tolist()
Cgs						        	=	(np.array(Ciss[1]) - np.array(Crss[1])).tolist()
Cgd						        	=	Crss[1]
Cds_tr						        =	(np.array(Coss_tr) - np.array(Crss_tr)).tolist()
Cgs_tr						        =	(np.array(Ciss_tr) - np.array(Crss_tr)).tolist()
Cgd_tr						        =	Crss_tr
Cds_er						        =	(np.array(Coss_er) - np.array(Crss_er)).tolist()
Cgs_er						        =	(np.array(Ciss_er) - np.array(Crss_er)).tolist()
Cgd_er						        =	Crss_er
Cds_eff 							=	paramProcess.getCmos([Coss[0],Cds],Cds_tr,Cds_er,Coss[0][0],True)
Cgs_eff 							=	paramProcess.getCmos([Ciss[0],Cgs],Cgs_tr,Cgs_er,Ciss[0][0],True)
Cgd_eff 							=	Crss_eff
Rvec,Tvec							=	paramProcess.MOSFETrdson(switchesRdsonPath,'NVMJST0D5N04XM','_Rdson')
Nvec,Ivec 							=	paramProcess.MOSFETrdson(switchesIdsonPath,'NVMJST0D5N04XM','_Rdson')
Ioff,catOFF,Eoff					=	paramProcess.MOSFETenergies(switchesEoffPath,'NVMJST0D5N04XM','_Eoff')
Voff,catOFF_Temp,Eoff_Temp			=	paramProcess.MOSFETenergies(switchesEoffPath,'NVMJST0D5N04XM','_Eoff_Temp')
Ion,catON,Eon 						=	paramProcess.MOSFETenergies(switchesEonPath,'NVMJST0D5N04XM','_Eon')
Von,catON_Temp,Eon_Temp				=	paramProcess.MOSFETenergies(switchesEonPath,'NVMJST0D5N04XM','_Eon_Temp')
Vfvec,Ifvec,Rd,Vt					=	paramProcess.DiodeVI_data(bodyDiodeVIPath,'NVMJST0D5N04XM')
#Vds_vec,Ids_vec 					=	paramProcess.Forward_Transfer_data(switchesTransferPath,'NVMJST0D5N04XM')

NVMJST0D5N04XM		=	{																																	#*	NVMJST0D5N04XM parameters
							'Config'						:	1																						,	#!	1->electric integrated | 2->electric separate | 3->thermal integrated | 4->thermal separate
							'Transistor'  			: 	{																									#!	transistors parameters
									'Config'				:	2																						,	#?	1->real model | 2->ideal model | 3->behavioral model
									'Thermal'           	:   ''                                  													,   #? 	selected transistor
									'Custom'            	:   []						               													,   #? 	transistor provided custom variables
									'g_fs'					:	1e6																						,	#?	forward transconductance
									'Rg'					:	1																						,	#?	internal gate resistance
									'Lg'					:	0																						,	#?	gate pin inductance
									'Rds_on'            	:   Rvec[-1][-1]*1e-3																		,   #? 	transistor ON resistance
									'Rds_off'				:	'inf'																					,	#?	transistor OFF resistance
									'Rvec'					:	(np.array(Rvec)*1e-3).tolist()														,	#?	absolute Rdson vector corresponding to junction temperature
									'Tvec'					:	Tvec 																					,	#?	junction temperature vector for Rdson
									'RTconfig'				:	1																						,	#?	choose which RT vector to be used, 1->typ | 2->max
									'RdsonScale'			:	1.174																					,	#?	Rdson scaling to account for min, typ and max deviations
									'Nvec'					:	Nvec 																					,	#?	normalized Rdson vector corresponding to current
									'Ivec'					:	Ivec																					,	#?	current vector for normalized Rdson
									'NIconfig'				:	1																						,	#?	choose which NI vector to be used
									'IdsonScale'			:	1.0																						,	#?	Idson resistance scaling to account for min, typ and max deviations
									'Rsrc'					:	0																						,	#?	kelvin source pin resistance
									'Lsrc'					:	0																						,	#?	kelvin source pin inductance
									'Ls'					:	0																						,	#?	package source inductance
                                    'Ld'					:	0																						,	#?	package drain inductance
									'Rs'					:	0																						,	#?	package source resistance
									'Rd'					:	0																						,	#?	package drain inductance
									'Ksrc'					:	0																						,	#?	kelvin source option, 0->no kelvin | 1->kelvin
									'Vblock'            	:   40                                	 													,   #? 	transistor blocking voltage
									'Id'                	:   906                                 													,   #? 	transistor drain current
									'Tr'                	:   0                                   													,   #? 	transistor rise time
									'Tf'                	:   0                                       												, 	#? 	transistor fall time
									'Avalanche'		:	{																									#!	transistor avalanche parameters
										'Config'			:	2																						,	#?	1->enable | 2->disable
										'Voltage'			:	40																						,	#?	avalanche voltage
										'Resistance'		:	1e-3																						#?	avalanche resistance to break voltage state-dependency
									},
									'Transfer'		:	{																									#!	transistor forward transfer parameters
										'Vds'				:	Vds_vec																					,	#?	drain-source voltage vector
										'Vgs'				:	[0,20]																					,	#?	gate-source voltage vector
										'Ids'				:	Ids_vec																					,	#?	drain current vector
										'Factor_ON'			:	1.0																						,	#?	scaling factor for Ids at turn ON
										'Factor_OFF'		:	1.0																						,	#?	scaling factor for Ids at turn OFF
										'Factor_Vgs_ON'		:	1.0																						,	#?	scaling factor for Vgs at turn ON
										'Factor_Vgs_OFF'	:	1.0																						,	#?	scaling factor for Vgs at turn OFF
										'Vcoss'				:	0																						,	#?	initial voltage of the Coss
									},
						},
							'BodyDiode'  			:	{																									#!	body diodes paramteters
									'Config'				:	4																						,	#?	1->non-ideal RR | 2->non-ideal | 3->ideal RR | 4->ideal
									'Thermal'           	:   ''                                  													,   #? 	separate body diode
									'Custom'            	:   []					                 													,   #? 	body diode provided custrom variables
									'Rd_on'             	:   Rd[-1]													                             	,  	#? 	body diode ON resistance
									'Rd_off'				:	'inf'																					,	#?	body diode OFF resistance
									'Vf'					:	Vt[-1]																					,	#? 	body diode forward voltage
									'If'                	:   906                                 													,   #? 	body diode forward current
									'dIr'               	:   100e6	                                  												,   #? 	body diode current slope
									'Lrr'					:	1e-9																					,	#?	body diode reverse recovery inductance
									'Trr'               	:  	93.0e-9                                  												,   #? 	body diode reverse recovery time
									'Irr'               	:   0                                   													,   #? 	body diode reverse recovery current
									'Qrr'               	:   282e-9	                                  												,	#? 	body diode reverse recovery charge
									'Is'                  	:   31.2              																		, 	#? 	body diode reference current
									'Vs'					:	32																						,	#?	body diode reference voltage
                                    'VIcurve'		:	{																									#!	body diode VI characteristics
                                        'Vfvec'				:	Vfvec																					,	#?	forward voltage vector
                                        'Ifvec'				:	Ifvec																					,	#?	forward current vector
										'Rdvec'				:	Rd																						,	#?	dynamic resistance vector
										'Vtvec'				:	Vt																						,	#?	threshold voltage vector
                                        'Temps'				:	[-55,25,175]																			,	#?	temperature vector
                                        'Vfscale'			:	1.00																						#?	Vf scaling to account for min, typ and max deviations
									},
						},
							'GateDriver'			:	{																									#!	gate driver parameters
									'Config'				:	3																						,	#?	1->high-side | 2->low-side | 3->disable
									'Von'					:	12																						,	#?	ON driving voltage
									'Voff'					:	0																						,	#?	OFF driving voltage
									'Ron'					:	5																						,	#?	sourcing output resistance
									'Roff'					:	5																						,	#?	sinking output resistance
									'Lon'					:	0																						,	#?	sourcing output inductance
									'Loff'					:	0																						,	#?	sinking output inductance
									'Cload'					:	0																						,	#?	capacitive load on output
									'Rload'					:	'inf'																					,	#?	resistive load on output
									'Delay'					:	0																						,	#?	input-to-output total deadtime
									'Trise'					:	0																						,	#?	output rising time
									'Tfall'					:	0																						,	#?	output falling time
									'UVLO_Start'			:	7.0																						,	#?	UVLO startup voltage threshold
									'UVLO_Stop'				:	6.5																						,	#?	UVLO shutdown voltage threshold
									'UVLO_Delay'			:	100e-9																					,	#?	delay between UVLO startup and shutdown
									'Init_State'			:	0																						,	#?	initial toggling state, 0->OFF | 1->ON
									'CurrentLimit'	:	{																									#*	current limit of driver stage
										'Config'			:	2																						,	#?	1->enable | 2->disable
										'Ts'				: 	0 																						,	#?	sampling time between inductive & capacitive links
										'tau'				: 	0																						,	#?	first-order delay between inductive & capacitive links
                                    	'Rs'				: 	0																						,	#?	source impedance of inductive link
										'Cs'				:	1e-12																					,	#?	source capacitance of capacitive link
                                        'UpLim'				: 	10																						,	#?	max current limit on capacitive link
                                        'LoLim'				: 	-10																						,	#?	min current limit on capacitive link
                                        'Voffset'			: 	0																							#?	voltage offset between inductive & capacitive links
									},
									'Masking'		:	{																									#*	switching stages masking
										'ON'	:	{																										#	ON path masking
											'Config'		:	2																						,	#?	1->enable | 2->disable
											'HIGH'	:	{																									#!	HIGH mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[0, 0]																						#?	mask output
											},
											'LOW'	:	{																									#!	LOW mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[1, 1]																						#?	mask output
											}
										},
										'OFF'	:	{																										#	OFF path masking
											'Config'		:	2																						,	#?	1->enable | 2->disable
											'HIGH'	:	{																									#!	HIGH mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[0, 0]																						#?	mask output
											},
											'LOW'	:	{																									#!	LOW mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[1, 1]																						#?	mask output
											}
										}
									},
									'Boot'			:	{																									#*	bootstrap/charge pump parameters
										'Config'			:	1																						,	#?	1->bootstrap | 2->charge pump
										'Von'				:	14																						,	#?	boostrap driving voltage
										'Cboot'				:	4.7e-6																					,	#?	bootstrap capacitance
										'Vinit'				:	0																						,	#?	bootstrap capacitance initial voltage
										'Rboot'				:	10																						,	#?	bootstrap resistance
										'Vfboot'			:	0.87																					,	#?	bootstrap diode forward voltage
										'Rdboot'			:	1e-3																					,	#?	bootstrap diode ON-state resistance
										'Ichrg'				:	300e-6																					,	#?	charge pump supply current
										'Idis'				:	5e-6																					,	#?	charge pump loading or leakage current
										'Cpar'				:	0																						,	#?	charge pump parallel cap to break state/source dependency
									    'UVLO_Start'		:	11.6																					,	#?	threshold value to start the charge pump
										'UVLO_Stop'			:	12.4																						#?	threshold value to stop the charge pump
									},
							},
							'GateNetwork'			:	{																									#!	gate drive circuit parameters
									'Config'				:	2																						,	#?	1-> enable | 2->disable
									'ON_Path'		:	{																									#*	sourcing path parameters
										'Rg'				:	5																						,	#?	gate ON path resistance
										'Lg'				:	0																						,	#?	gate ON path inductance
										'Rload'				:	10e3																					,	#?	gate pull down resistance
										'Diode'	:	{																										#	reverse blocking diode parameters
											'Vf'			:	0																						,	#?	forward voltage
											'Rd_on'			:	0																						,	#?	ON-state resistance
										},
									},
									'OFF_Path'		:	{																									#*	sinking path parameters
										'Rg'				:	5																						,	#?	gate OFF path resistance
										'Lg'				:	0																						,	#?	gate OFF path inductance
										'Diode'	:	{																										#	reverse blocking diode parameters
											'Vf'			:	0																						,	#?	forward voltage
											'Rd_on'			:	0																						,	#?	ON-state resistance
										},
									},
									'NegVolt'		:	{																									#*	negative voltage generator parameters
										'Config'			:	2																						,	#?	1-> enable | 2->disable
										'Dz'	:	{																										#	zener diode parameters
											'Vf'			:	0.7																						,	#?	forward voltage
											'Rd_on'			:	1e-3																					,	#?	ON-state resistance
											'Vz'			:	2																						,	#?	Zener breakdown voltage
											'Rz'			:	1e-3																					,	#?	Zener resistance
										},
										'Dp'	:	{																										#	peak detector diode
											'Vf'			:	0.0																						,	#?	forward voltage
											'Rd_on'			:	0.0																						,	#?	ON-state resistance
										},
										'Cz'	:	{																										#	Zener capacitor parameters
											'Config'		:	1																						,	#?	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
											'Csingle'		:	1e-6																					,	#?	single capacitor value
											'Rsingle'		:	5e-3																					,	#?	ESR of single capacitor
											'Lsingle'		:	0																						,	#?	ESL of single capacitor
											'nPar'			:	1																						,	#?	number of parallel connections
											'nSer'			:	1																						,	#?	number of series connections
											'Vinit'			:	0																						,	#?	capacitor initial voltage
										},
										'Cp'	:	{																										#	peak detector capacitor parameters
											'Config'		:	1																						,	#?	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
											'Csingle'		:	2.2e-6																					,	#?	single capacitor value
											'Rsingle'		:	5e-3																					,	#?	ESR of single capacitor
											'Lsingle'		:	0																						,	#?	ESL of single capacitor
											'nPar'			:	1																						,	#?	number of parallel connections
											'nSer'			:	1																						,	#?	number of series connections
											'Vinit'			:	0																						,	#?	capacitor initial voltage
										},
										'Rp1'				:	43																						,	#?	current limiter of peak detector current
										'Rp2'				:	4.7e3																					,	#?	load resistor to charge the zener diode
									},
								},
							'nParallel'   					:	2                                       												,   #? 	number of parallel devices
							'Rth_jc'						:	[0.00067201,0.00355133,0.0168122,0.0515319,0.141005]									,	#?	junction-to-case thermal resistance
							'Cth_jc'						:	[4.76E-05,0.00013147,0.0014285,0.0039428,0.0214]										,	#?	junction-to-case thermal capacitance
							'Rth_ca'              			:   0.0            																			,   #? 	case-to-ambient thermal resistance
							'Cth_ca'              			:   0.0             																		,   #? 	case-to-ambient thermal capacitance
							'Tinit'							:	0.0																						,	#?	initial juntion temperature
							'Pinit'							:	0.0																						,	#?	initial power dissipation
							'Coss'					: 	{																									#!	device Coss parameters
								'C'							:	Coss_eff					 															,	#?	device parasitic output capacitance
								'R'							:	0																						,	#?	Coss resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Coss inductance to reduce current slope
								'Coss_er'					:	Crss_er																					,	#?	energy-related Coss
								'Coss_tr'					:	Coss_tr																					,	#?	time-related Coss
								'Vvec'						:	Coss[0]																					,	#? 	device Coss voltage vector
								'Cvec'						:	Coss[1]																					,	#?	device Coss capacity vector
								'Offset'					:	0																						,	#?	parasitic offset to Coss
                                'Factor'					:	1.0																						,	#?	parasitic tolerance to Coss
								'Qoss'						:	Qoss																					,	#?	equivalent charge of Coss
								'Eoss'						:	Eoss																					,	#?	equivalent energy of Coss
								'Config'					:	5																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
						},
                        	'Crss'					:	{																									#!	device Crss parameters
                                'C'							:	Crss_eff					 															,	#?	device parasitic reverse transfer capacitance
								'R'							:	0																						,	#?	Crss resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Crss inductance to reduce current slope
								'Crss_er'					:	Crss_er																					,	#?	energy-related Crss
								'Crss_tr'					:	Crss_tr																					,	#?	time-related Crss
								'Vvec'						:	Crss[0]																					,	#?	device Crss voltage vector
                                'Cvec'						:	Crss[1]																					,	#?	device Crss capacity vector
								'Qvec'						:	Qrss																					,	#?	device accumulated Crss charge vector
								'Offset'					:	0																						,	#?	parasitic offset to Crss
								'Factor'					:	1.0																						,	#?	parasitic tolerance to Crss
								'Qrss'						:	Qrss																					,	#?	equivalent charge of Crss
								'Erss'						:	Erss																					,	#?	equivalent energe of Crss
								'Config'					:	5																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
						},
							'Ciss'					:	{																									#!	device Ciss parameters
								'C'							:	Ciss_eff					 															,	#?	device parasitic input capacitance
								'R'							:	0																						,	#?	Ciss resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Ciss inductance to reduce current slope
								'Ciss_er'					:	Ciss_er																					,	#?	energy-related Ciss
								'Ciss_tr'					:	Ciss_tr																					,	#?	time-related Ciss
								'Vvec'						:	Ciss[0]																					,	#?	device Ciss voltage vector
								'Cvec'						:	Ciss[1]																					,	#?	device Ciss capacity vector
								'Offset'					:	0																						,	#?	parasitic offset to Ciss
								'Factor'					:	1.0																						,	#?	parasitic tolerance to Ciss
								'Qiss'						:	Qiss																					,	#?	equivalent charge of Ciss
								'Eiss'						:	Eiss																					,	#?	equivalent energy of Ciss
								'Config'					:	5																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Cds'					:	{																									#!	device Cds parameters
								'C'							:	Cds_eff					 																,	#?	device parasitic Cds capacitance
								'R'							:	0																						,	#?	Cds resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Cds inductance to reduce current slope
								'Cds_er'					:	Cds_er																					,	#?	energy-related Cds
								'Cds_tr'					:	Cds_tr																					,	#?	time-related Cds
								'Vvec'						:	Coss[0]																					,	#?	device Cds voltage vector
								'Cvec'						:	Cds																						,	#?	device Cds capacity vector
								'Offset_ON'					:	0																						,	#?	tuning offset for turn ON
								'Offset_OFF'				:	0																						,	#?	tuning offset for turn OFF
								'Factor_ON'					:	1.0																						,	#?	tuning factor for turn ON
								'Factor_OFF'				:	1.0																						,	#?	tuning factor for turn OFF
								'Config'					:	4																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Cgd'					:	{																									#!	device Cgd parameters
								'C'							:	Cgd_eff							 														,	#?	device parasitic Cgd capacitance
								'R'							:	0																						,	#?	Cgd resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Cgd inductance to reduce current slope
								'Cgd_er'					:	Cgd_er																					,	#?	energy-related Cgd
								'Cgd_tr'					:	Cgd_tr																					,	#?	time-related Cgd
								'Vvec'						:	Crss[0]																					,	#?	device Cgd voltage vector
								'Cvec'						:	Cgd																						,	#?	device Cgd capacity vector
								'Offset_ON'					:	0																						,	#?	tuning offset for turn ON
								'Offset_OFF'				:	0																						,	#?	tuning offset for turn OFF
								'Factor_ON'					:	1.0																						,	#?	tuning factor for turn ON
								'Factor_OFF'				:	1.0																						,	#?	tuning factor for turn OFF
								'Config'					:	4																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Cgs'					:	{																									#!	device Cgs parameters
								'C'							:	Cgs_eff					 																,	#?	device parasitic Cgs capacitance
								'R'							:	0																						,	#?	Cgs resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Cgs inductance to reduce current slope
								'Cgs_er'					:	Cgs_er																					,	#?	energy-related Cgs
								'Cgs_tr'					:	Cgs_tr																					,	#?	time-related Cgs
								'Vvec'						:	Ciss[0]																					,	#?	device Cgs voltage vector
								'Cvec'						:	Cgs																						,	#?	device Cgs capacity vector
								'Offset_ON'					:	0																						,	#?	tuning offset for turn ON
								'Offset_OFF'				:	0																						,	#?	tuning offset for turn OFF
								'Factor_ON'					:	1.0																						,	#?	tuning factor for turn ON
								'Factor_OFF'				:	1.0																						,	#?	tuning factor for turn OFF
								'Config'					:	4																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Eoff'					:	{																									#!	transistor turn-OFF energy losses
									'Ivec'					:	Ioff																					,	#?	turn-OFF energy current vector
									'Rgvec'					:	[0,100]																					,	#?	OFF path gate resistances vector
									'Tjvec'					:	[-55,175]																				,	#?	junction temperature vector
                                    'Vvec'					:	Voff																					,	#?	turn-OFF voltage vector
                                    'Evec'					:	Eoff																					,	#?	turn-OFF energy vectors
									'Evec_Temp'				:	Eoff_Temp																				,	#?	turn-OFF energy temp scaling vectors
                                    'CAT'					:	catOFF																					,	#?	octave Eoff energy syntax
									'CAT_Temp'				:	catOFF_Temp																				,	#?	octave Eoff energy temp scaling syntax
									'Vgs'					:	0																						,	#?	used OFF path gate-source voltage
									'Vth'					:	1.5																						,	#?	used OFF path threshold voltage
									'Rg'					:	0																							#?	used OFF path gate resistance
						},
							'Eon'					:	{																									#!	transistor turn-ON energy losses
									'Ivec'					:	Ion																						,	#?	turn-ON energy current vector
									'Rgvec'					:	[0,100]																					,	#?	ON path gate resistances vector
									'Tjvec'					:	[-55,175]																				,	#?	junction temperature vector
                                    'Vvec'					:	Von																						,	#?	turn-ON voltage vector
                                    'Evec'					:	Eon																						,	#?	turn-ON energy vectors
									'Evec_Temp'				:	Eon_Temp																				,	#?	turn-ON energy temp scaling vectors
                                    'CAT'					:	catON																					,	#?	octave Eon energy syntax
									'CAT_Temp'				:	catON_Temp																				,	#?	octave Eon energy temp scaling syntax
									'Vgs'					:	12																						,	#?	used ON path gate-source voltage
									'Vth'					:	1.5																						,	#?	used ON path threshold voltage
									'Rg'					:	0																							#?	used ON path gate resistance
						},
							'Tau_deg'						:	100e-9																					,	#?	deglitch filter for currents and voltages
							'RCsnubber'						:	2																						,	#?	1->enable | 2->disable
						}

#?----------------------------------------------------------------------------------------------------------------------------------------------------------------------

Coss,Qoss,Eoss,Coss_tr,Coss_er		=	paramProcess.MOSFETcaps(switchesCossPath,'PMT200EPE','_Coss')
Crss,Qrss,Erss,Crss_tr,Crss_er 		=	paramProcess.MOSFETcaps(switchesCrssPath,'PMT200EPE','_Crss')
Ciss,Qiss,Eiss,Ciss_tr,Ciss_er 		=	paramProcess.MOSFETcaps(switchesCissPath,'PMT200EPE','_Ciss')
Coss_eff 							=	paramProcess.getCmos(Coss,Coss_tr,Coss_er,Coss[0][0],True)
Ciss_eff 							=	paramProcess.getCmos(Ciss,Ciss_tr,Ciss_er,Ciss[0][0],True)
Crss_eff 							=	paramProcess.getCmos(Crss,Crss_tr,Crss_er,Crss[0][0],True)
Cds 						        =	(np.array(Coss[1]) - np.array(Crss[1])).tolist()
Cgs						        	=	(np.array(Ciss[1]) - np.array(Crss[1])).tolist()
Cgd						        	=	Crss[1]
Cds_tr						        =	(np.array(Coss_tr) - np.array(Crss_tr)).tolist()
Cgs_tr						        =	(np.array(Ciss_tr) - np.array(Crss_tr)).tolist()
Cgd_tr						        =	Crss_tr
Cds_er						        =	(np.array(Coss_er) - np.array(Crss_er)).tolist()
Cgs_er						        =	(np.array(Ciss_er) - np.array(Crss_er)).tolist()
Cgd_er						        =	Crss_er
Cds_eff 							=	paramProcess.getCmos([Coss[0],Cds],Cds_tr,Cds_er,Coss[0][0],True)
Cgs_eff 							=	paramProcess.getCmos([Ciss[0],Cgs],Cgs_tr,Cgs_er,Ciss[0][0],True)
Cgd_eff 							=	Crss_eff
Rvec,Tvec							=	paramProcess.MOSFETrdson(switchesRdsonPath,'PMT200EPE','_Rdson')
Nvec,Ivec 							=	paramProcess.MOSFETrdson(switchesIdsonPath,'PMT200EPE','_Rdson')
Ioff,catOFF,Eoff					=	paramProcess.MOSFETenergies(switchesEoffPath,'PMT200EPE','_Eoff')
Voff,catOFF_Temp,Eoff_Temp			=	paramProcess.MOSFETenergies(switchesEoffPath,'PMT200EPE','_Eoff_Temp')
Ion,catON,Eon 						=	paramProcess.MOSFETenergies(switchesEonPath,'PMT200EPE','_Eon')
Von,catON_Temp,Eon_Temp				=	paramProcess.MOSFETenergies(switchesEonPath,'PMT200EPE','_Eon_Temp')
Vfvec,Ifvec,Rd,Vt					=	paramProcess.DiodeVI_data(bodyDiodeVIPath,'PMT200EPE')
Vds_vec,Ids_vec 					=	paramProcess.Forward_Transfer_data(switchesTransferPath,'PMT200EPE')

PMT200EPE			=	{																																	#*	PMT200EPE parameters
							'Config'						:	1																						,	#!	1->electric integrated | 2->electric separate | 3->thermal integrated | 4->thermal separate
							'Transistor'  			: 	{																									#!	transistors parameters
									'Config'				:	2																						,	#?	1->real model | 2->ideal model | 3->behavioral model
									'Thermal'           	:   ''                                  													,   #? 	selected transistor
									'Custom'            	:   []						               													,   #? 	transistor provided custom variables
									'g_fs'					:	1e6																						,	#?	forward transconductance
									'Rg'					:	12																						,	#?	internal gate resistance
									'Lg'					:	1.66871834767356e-9*0																	,	#?	gate pin inductance
									'Rds_on'            	:   Rvec[-1][-1]*1e-3																		,   #? 	transistor ON resistance
									'Rds_off'				:	'inf'																					,	#?	transistor OFF resistance
									'Rvec'					:	(np.array(Rvec)*1e-3).tolist()														,	#?	absolute Rdson vector corresponding to junction temperature
									'Tvec'					:	Tvec 																					,	#?	junction temperature vector for Rdson
									'RTconfig'				:	1																						,	#?	choose which RT vector to be used, 1->typ | 2->max
									'RdsonScale'			:	1.5																						,	#?	Rdson scaling to account for min, typ and max deviations
									'Nvec'					:	Nvec 																					,	#?	normalized Rdson vector corresponding to current
									'Ivec'					:	Ivec																					,	#?	current vector for normalized Rdson
									'NIconfig'				:	1																						,	#?	choose which NI vector to be used
									'IdsonScale'			:	1.0																						,	#?	Idson resistance scaling to account for min, typ and max deviations
									'Rsrc'					:	0.1e-3*0																				,	#?	kelvin source pin resistance
									'Lsrc'					:	1.8672843065499e-9*0																	,	#?	kelvin source pin inductance
									'Ls'					:	1.8672843065499e-9*0																	,	#?	package source inductance
                                    'Ld'					:	0.1e-9*0																				,	#?	package drain inductance
									'Rs'					:	0.1e-3*0																				,	#?	package source resistance
									'Rd'					:	101.606060976995e-3*0																	,	#?	package drain inductance
									'Ksrc'					:	0																						,	#?	kelvin source option, 0->no kelvin | 1->kelvin
									'Vblock'            	:   40                                	 													,   #? 	transistor blocking voltage
									'Id'                	:   2.4                                 													,   #? 	transistor drain current
									'Tr'                	:   14e-9                                  													,   #? 	transistor rise time
									'Tf'                	:   44e-9                                      												, 	#? 	transistor fall time
									'Avalanche'		:	{																									#!	transistor avalanche parameters
										'Config'			:	2																						,	#?	1->enable | 2->disable
										'Voltage'			:	70																						,	#?	avalanche voltage
										'Resistance'		:	1e-3																						#?	avalanche resistance to break voltage state-dependency
									},
									'Transfer'		:	{																									#!	transistor forward transfer parameters
										'Vds'				:	Vds_vec																					,	#?	drain-source voltage vector
										'Vgs'				:	list(np.linspace(-12,0,int((12/0.3)+1)))												,	#?	gate-source voltage vector
										'Ids'				:	Ids_vec																					,	#?	drain current vector
										'Factor_ON'			:	1.0																						,	#?	scaling factor for Ids at turn ON
										'Factor_OFF'		:	1.0																						,	#?	scaling factor for Ids at turn OFF
										'Factor_Vgs_ON'		:	1.0																						,	#?	scaling factor for Vgs at turn ON
										'Factor_Vgs_OFF'	:	1.0																						,	#?	scaling factor for Vgs at turn OFF
										'Vcoss'				:	0																						,	#?	initial voltage of the Coss
									},
						},
							'BodyDiode'  			:	{																									#!	body diodes paramteters
									'Config'				:	4																						,	#?	1->non-ideal RR | 2->non-ideal | 3->ideal RR | 4->ideal
									'Thermal'           	:   ''                                  													,   #? 	separate body diode
									'Custom'            	:   []					                 													,   #? 	body diode provided custrom variables
									'Rd_on'             	:   Rd[-1]																					,  	#? 	body diode ON resistance
									'Rd_off'				:	'inf'																					,	#?	body diode OFF resistance
									'Vf'					:	Vt[-1]																					,	#? 	body diode forward voltage
									'If'                	:   1.8                                 													,   #? 	body diode forward current
									'dIr'               	:   100e6	                                  												,   #? 	body diode current slope
									'Lrr'					:	1e-9																					,	#?	body diode reverse recovery inductance
									'Trr'               	:   1e-9	                                  												,   #? 	body diode reverse recovery time
									'Irr'               	:   0                                   													,   #? 	body diode reverse recovery current
									'Qrr'               	:   1e-9	                                  												, 	#? 	body diode reverse recovery charge
									'Is'                  	:   1              																		   	, 	#? 	body diode reference current
									'Vs'					:	0																						,	#?	body diode reference voltage
                                    'VIcurve'		:	{																									#!	body diode VI characteristics
                                        'Vfvec'				:	Vfvec																					,	#?	forward voltage vector
                                        'Ifvec'				:	Ifvec																					,	#?	forward current vector
										'Rdvec'				:	Rd																						,	#?	dynamic resistance vector
										'Vtvec'				:	Vt																						,	#?	threshold voltage vector
                                        'Temps'				:	[25,150]																				,	#?	temperature vector
                                        'Vfscale'			:	1.5																							#?	Vf scaling to account for min, typ and max deviations
									},
						},
							'GateDriver'			:	{																									#!	gate driver parameters
									'Config'				:	3																						,	#?	1->high-side | 2->low-side | 3->disable
									'Von'					:	12																						,	#?	ON driving voltage
									'Voff'					:	0																						,	#?	OFF driving voltage
									'Ron'					:	5																						,	#?	sourcing output resistance
									'Roff'					:	5																						,	#?	sinking output resistance
									'Lon'					:	0																						,	#?	sourcing output inductance
									'Loff'					:	0																						,	#?	sinking output inductance
									'Cload'					:	0																						,	#?	capacitive load on output
									'Rload'					:	'inf'																					,	#?	resistive load on output
									'Delay'					:	0																						,	#?	input-to-output total deadtime
									'Trise'					:	0																						,	#?	output rising time
									'Tfall'					:	0																						,	#?	output falling time
									'UVLO_Start'			:	7.0																						,	#?	UVLO startup voltage threshold
									'UVLO_Stop'				:	6.5																						,	#?	UVLO shutdown voltage threshold
									'UVLO_Delay'			:	100e-9																					,	#?	delay between UVLO startup and shutdown
									'Init_State'			:	0																						,	#?	initial toggling state, 0->OFF | 1->ON
									'CurrentLimit'	:	{																									#*	current limit of driver stage
										'Config'			:	2																						,	#?	1->enable | 2->disable
										'Ts'				: 	0 																						,	#?	sampling time between inductive & capacitive links
										'tau'				: 	0																						,	#?	first-order delay between inductive & capacitive links
                                    	'Rs'				: 	0																						,	#?	source impedance of inductive link
										'Cs'				:	1e-12																					,	#?	source capacitance of capacitive link
                                        'UpLim'				: 	10																						,	#?	max current limit on capacitive link
                                        'LoLim'				: 	-10																						,	#?	min current limit on capacitive link
                                        'Voffset'			: 	0																							#?	voltage offset between inductive & capacitive links
									},
									'Masking'		:	{																									#*	switching stages masking
										'ON'	:	{																										#	ON path masking
											'Config'		:	2																						,	#?	1->enable | 2->disable
											'HIGH'	:	{																									#!	HIGH mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[0, 0]																						#?	mask output
											},
											'LOW'	:	{																									#!	LOW mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[1, 1]																						#?	mask output
											}
										},
										'OFF'	:	{																										#	OFF path masking
											'Config'		:	2																						,	#?	1->enable | 2->disable
											'HIGH'	:	{																									#!	HIGH mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[0, 0]																						#?	mask output
											},
											'LOW'	:	{																									#!	LOW mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[1, 1]																						#?	mask output
											}
										}
									},
									'Boot'			:	{																									#*	bootstrap/charge pump parameters
										'Config'			:	1																						,	#?	1->bootstrap | 2->charge pump
										'Von'				:	14																						,	#?	boostrap driving voltage
										'Cboot'				:	4.7e-6																					,	#?	bootstrap capacitance
										'Vinit'				:	0																						,	#?	bootstrap capacitance initial voltage
										'Rboot'				:	10																						,	#?	bootstrap resistance
										'Vfboot'			:	0.87																					,	#?	bootstrap diode forward voltage
										'Rdboot'			:	1e-3																					,	#?	bootstrap diode ON-state resistance
										'Ichrg'				:	300e-6																					,	#?	charge pump supply current
										'Idis'				:	5e-6																					,	#?	charge pump loading or leakage current
										'Cpar'				:	0																						,	#?	charge pump parallel cap to break state/source dependency
									    'UVLO_Start'		:	11.6																					,	#?	threshold value to start the charge pump
										'UVLO_Stop'			:	12.4																						#?	threshold value to stop the charge pump
									},
							},
							'GateNetwork'			:	{																									#!	gate drive circuit parameters
									'Config'				:	2																						,	#?	1-> enable | 2->disable
									'ON_Path'		:	{																									#*	sourcing path parameters
										'Rg'				:	5																						,	#?	gate ON path resistance
										'Lg'				:	0																						,	#?	gate ON path inductance
										'Rload'				:	10e3																					,	#?	gate pull down resistance
										'Diode'	:	{																										#	reverse blocking diode parameters
											'Vf'			:	0																						,	#?	forward voltage
											'Rd_on'			:	0																						,	#?	ON-state resistance
										},
									},
									'OFF_Path'		:	{																									#*	sinking path parameters
										'Rg'				:	5																						,	#?	gate OFF path resistance
										'Lg'				:	0																						,	#?	gate OFF path inductance
										'Diode'	:	{																										#	reverse blocking diode parameters
											'Vf'			:	0																						,	#?	forward voltage
											'Rd_on'			:	0																						,	#?	ON-state resistance
										},
									},
									'NegVolt'		:	{																									#*	negative voltage generator parameters
										'Config'			:	2																						,	#?	1-> enable | 2->disable
										'Dz'	:	{																										#	zener diode parameters
											'Vf'			:	0.7																						,	#?	forward voltage
											'Rd_on'			:	1e-3																					,	#?	ON-state resistance
											'Vz'			:	2																						,	#?	Zener breakdown voltage
											'Rz'			:	1e-3																					,	#?	Zener resistance
										},
										'Dp'	:	{																										#	peak detector diode
											'Vf'			:	0.0																						,	#?	forward voltage
											'Rd_on'			:	0.0																						,	#?	ON-state resistance
										},
										'Cz'	:	{																										#	Zener capacitor parameters
											'Config'		:	1																						,	#?	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
											'Csingle'		:	1e-6																					,	#?	single capacitor value
											'Rsingle'		:	5e-3																					,	#?	ESR of single capacitor
											'Lsingle'		:	0																						,	#?	ESL of single capacitor
											'nPar'			:	1																						,	#?	number of parallel connections
											'nSer'			:	1																						,	#?	number of series connections
											'Vinit'			:	0																						,	#?	capacitor initial voltage
										},
										'Cp'	:	{																										#	peak detector capacitor parameters
											'Config'		:	1																						,	#?	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
											'Csingle'		:	2.2e-6																					,	#?	single capacitor value
											'Rsingle'		:	5e-3																					,	#?	ESR of single capacitor
											'Lsingle'		:	0																						,	#?	ESL of single capacitor
											'nPar'			:	1																						,	#?	number of parallel connections
											'nSer'			:	1																						,	#?	number of series connections
											'Vinit'			:	0																						,	#?	capacitor initial voltage
										},
										'Rp1'				:	43																						,	#?	current limiter of peak detector current
										'Rp2'				:	4.7e3																					,	#?	load resistor to charge the zener diode
									},
								},
							'nParallel'   					:	1                                       												,   #? 	number of parallel devices
							'Rth_jc'						:	15.0																					,	#?	junction-to-case thermal resistance
							'Cth_jc'						:	0.00																					,	#?	junction-to-case thermal capacitance
							'Rth_ca'              			:   15.0            																		,   #? 	case-to-ambient thermal resistance
							'Cth_ca'              			:   0.0             																		,   #? 	case-to-ambient thermal capacitance
							'Tinit'							:	0.0																						,	#?	initial juntion temperature
							'Pinit'							:	0.0																						,	#?	initial power dissipation
							'Coss'					: 	{																									#!	device Coss parameters
								'C'							:	Coss_eff					 															,	#?	device parasitic output capacitance
								'R'							:	0																						,	#?	Coss resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Coss inductance to reduce current slope
								'Coss_er'					:	Crss_er																					,	#?	energy-related Coss
								'Coss_tr'					:	Coss_tr																					,	#?	time-related Coss
								'Vvec'						:	Coss[0]																					,	#? 	device Coss voltage vector
								'Cvec'						:	Coss[1]																					,	#?	device Coss capacity vector
								'Offset'					:	0																						,	#?	parasitic offset to Coss
                                'Factor'					:	1.0																						,	#?	parasitic tolerance to Coss
								'Qoss'						:	Qoss																					,	#?	equivalent charge of Coss
								'Eoss'						:	Eoss																					,	#?	equivalent energy of Coss
								'Config'					:	5																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
						},
                        	'Crss'					:	{																									#!	device Crss parameters
                                'C'							:	Crss_eff					 															,	#?	device parasitic reverse transfer capacitance
								'R'							:	0																						,	#?	Crss resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Crss inductance to reduce current slope
								'Crss_er'					:	Crss_er																					,	#?	energy-related Crss
								'Crss_tr'					:	Crss_tr																					,	#?	time-related Crss
								'Vvec'						:	Crss[0]																					,	#?	device Crss voltage vector
                                'Cvec'						:	Crss[1]																					,	#?	device Crss capacity vector
								'Qvec'						:	Qrss																					,	#?	device accumulated Crss charge vector
								'Offset'					:	0																						,	#?	parasitic offset to Crss
								'Factor'					:	1.0																						,	#?	parasitic tolerance to Crss
								'Qrss'						:	Qrss																					,	#?	equivalent charge of Crss
								'Erss'						:	Erss																					,	#?	equivalent energe of Crss
								'Config'					:	5																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
						},
							'Ciss'					:	{																									#!	device Ciss parameters
								'C'							:	Ciss_eff					 															,	#?	device parasitic input capacitance
								'R'							:	0																						,	#?	Ciss resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Ciss inductance to reduce current slope
								'Ciss_er'					:	Ciss_er																					,	#?	energy-related Ciss
								'Ciss_tr'					:	Ciss_tr																					,	#?	time-related Ciss
								'Vvec'						:	Ciss[0]																					,	#?	device Ciss voltage vector
								'Cvec'						:	Ciss[1]																					,	#?	device Ciss capacity vector
								'Offset'					:	0																						,	#?	parasitic offset to Ciss
								'Factor'					:	1.0																						,	#?	parasitic tolerance to Ciss
								'Qiss'						:	Qiss																					,	#?	equivalent charge of Ciss
								'Eiss'						:	Eiss																					,	#?	equivalent energy of Ciss
								'Config'					:	5																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Cds'					:	{																									#!	device Cds parameters
								'C'							:	Cds_eff					 																,	#?	device parasitic Cds capacitance
								'R'							:	0																						,	#?	Cds resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Cds inductance to reduce current slope
								'Cds_er'					:	Cds_er																					,	#?	energy-related Cds
								'Cds_tr'					:	Cds_tr																					,	#?	time-related Cds
								'Vvec'						:	Coss[0]																					,	#?	device Cds voltage vector
								'Cvec'						:	Cds																						,	#?	device Cds capacity vector
								'Offset_ON'					:	0																						,	#?	tuning offset for turn ON
								'Offset_OFF'				:	0																						,	#?	tuning offset for turn OFF
								'Factor_ON'					:	1.0																						,	#?	tuning factor for turn ON
								'Factor_OFF'				:	1.0																						,	#?	tuning factor for turn OFF
								'Config'					:	4																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Cgd'					:	{																									#!	device Cgd parameters
								'C'							:	Cgd_eff							 														,	#?	device parasitic Cgd capacitance
								'R'							:	0																						,	#?	Cgd resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Cgd inductance to reduce current slope
								'Cgd_er'					:	Cgd_er																					,	#?	energy-related Cgd
								'Cgd_tr'					:	Cgd_tr																					,	#?	time-related Cgd
								'Vvec'						:	Crss[0]																					,	#?	device Cgd voltage vector
								'Cvec'						:	Cgd																						,	#?	device Cgd capacity vector
								'Offset_ON'					:	0																						,	#?	tuning offset for turn ON
								'Offset_OFF'				:	0																						,	#?	tuning offset for turn OFF
								'Factor_ON'					:	1.0																						,	#?	tuning factor for turn ON
								'Factor_OFF'				:	1.0																						,	#?	tuning factor for turn OFF
								'Config'					:	4																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Cgs'					:	{																									#!	device Cgs parameters
								'C'							:	Cgs_eff					 																,	#?	device parasitic Cgs capacitance
								'R'							:	0																						,	#?	Cgs resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Cgs inductance to reduce current slope
								'Cgs_er'					:	Cgs_er																					,	#?	energy-related Cgs
								'Cgs_tr'					:	Cgs_tr																					,	#?	time-related Cgs
								'Vvec'						:	Ciss[0]																					,	#?	device Cgs voltage vector
								'Cvec'						:	Cgs																						,	#?	device Cgs capacity vector
								'Offset_ON'					:	0																						,	#?	tuning offset for turn ON
								'Offset_OFF'				:	0																						,	#?	tuning offset for turn OFF
								'Factor_ON'					:	1.0																						,	#?	tuning factor for turn ON
								'Factor_OFF'				:	1.0																						,	#?	tuning factor for turn OFF
								'Config'					:	4																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Eoff'					:	{																									#!	transistor turn-OFF energy losses
									'Ivec'					:	Ioff																					,	#?	turn-OFF energy current vector
									'Rgvec'					:	[0,100]																					,	#?	OFF path gate resistances vector
									'Tjvec'					:	[-55,175]																				,	#?	junction temperature vector
                                    'Vvec'					:	Voff																					,	#?	turn-OFF voltage vector
                                    'Evec'					:	Eoff																					,	#?	turn-OFF energy vectors
									'Evec_Temp'				:	Eoff_Temp																				,	#?	turn-OFF energy temp scaling vectors
                                    'CAT'					:	catOFF																					,	#?	octave Eoff energy syntax
									'CAT_Temp'				:	catOFF_Temp																				,	#?	octave Eoff energy temp scaling syntax
									'Vgs'					:	0																						,	#?	used OFF path gate-source voltage
									'Vth'					:	1.5																						,	#?	used OFF path threshold voltage
									'Rg'					:	0																							#?	used OFF path gate resistance
						},
							'Eon'					:	{																									#!	transistor turn-ON energy losses
									'Ivec'					:	Ion																						,	#?	turn-ON energy current vector
									'Rgvec'					:	[0,100]																					,	#?	ON path gate resistances vector
									'Tjvec'					:	[-55,175]																				,	#?	junction temperature vector
                                    'Vvec'					:	Von																						,	#?	turn-ON voltage vector
                                    'Evec'					:	Eon																						,	#?	turn-ON energy vectors
									'Evec_Temp'				:	Eon_Temp																				,	#?	turn-ON energy temp scaling vectors
                                    'CAT'					:	catON																					,	#?	octave Eon energy syntax
									'CAT_Temp'				:	catON_Temp																				,	#?	octave Eon energy temp scaling syntax
									'Vgs'					:	12																						,	#?	used ON path gate-source voltage
									'Vth'					:	1.5																						,	#?	used ON path threshold voltage
									'Rg'					:	0																							#?	used ON path gate resistance
						},
							'Tau_deg'						:	100e-9																					,	#?	deglitch filter for currents and voltages
							'RCsnubber'						:	2																						,	#?	1->enable | 2->disable
						}

#?----------------------------------------------------------------------------------------------------------------------------------------------------------------------

Coss,Qoss,Eoss,Coss_tr,Coss_er		=	paramProcess.MOSFETcaps(switchesCossPath,'BUK9Y6R540H','_Coss')
Crss,Qrss,Erss,Crss_tr,Crss_er 		=	paramProcess.MOSFETcaps(switchesCrssPath,'BUK9Y6R540H','_Crss')
Ciss,Qiss,Eiss,Ciss_tr,Ciss_er 		=	paramProcess.MOSFETcaps(switchesCissPath,'BUK9Y6R540H','_Ciss')
Coss_eff 							=	paramProcess.getCmos(Coss,Coss_tr,Coss_er,Coss[0][0],True)
Ciss_eff 							=	paramProcess.getCmos(Ciss,Ciss_tr,Ciss_er,Ciss[0][0],True)
Crss_eff 							=	paramProcess.getCmos(Crss,Crss_tr,Crss_er,Crss[0][0],True)
Cds 						        =	(np.array(Coss[1]) - np.array(Crss[1])).tolist()
Cgs						        	=	(np.array(Ciss[1]) - np.array(Crss[1])).tolist()
Cgd						        	=	Crss[1]
Cds_tr						        =	(np.array(Coss_tr) - np.array(Crss_tr)).tolist()
Cgs_tr						        =	(np.array(Ciss_tr) - np.array(Crss_tr)).tolist()
Cgd_tr						        =	Crss_tr
Cds_er						        =	(np.array(Coss_er) - np.array(Crss_er)).tolist()
Cgs_er						        =	(np.array(Ciss_er) - np.array(Crss_er)).tolist()
Cgd_er						        =	Crss_er
Cds_eff 							=	paramProcess.getCmos([Coss[0],Cds],Cds_tr,Cds_er,Coss[0][0],True)
Cgs_eff 							=	paramProcess.getCmos([Ciss[0],Cgs],Cgs_tr,Cgs_er,Ciss[0][0],True)
Cgd_eff 							=	Crss_eff
Rvec,Tvec							=	paramProcess.MOSFETrdson(switchesRdsonPath,'BUK9Y6R540H','_Rdson')
Nvec,Ivec 							=	paramProcess.MOSFETrdson(switchesIdsonPath,'BUK9Y6R540H','_Rdson')
Ioff,catOFF,Eoff					=	paramProcess.MOSFETenergies(switchesEoffPath,'BUK9Y6R540H','_Eoff')
Voff,catOFF_Temp,Eoff_Temp			=	paramProcess.MOSFETenergies(switchesEoffPath,'BUK9Y6R540H','_Eoff_Temp')
Ion,catON,Eon 						=	paramProcess.MOSFETenergies(switchesEonPath,'BUK9Y6R540H','_Eon')
Von,catON_Temp,Eon_Temp				=	paramProcess.MOSFETenergies(switchesEonPath,'BUK9Y6R540H','_Eon_Temp')
Vfvec,Ifvec,Rd,Vt					=	paramProcess.DiodeVI_data(bodyDiodeVIPath,'BUK9Y6R540H')
Vds_vec,Ids_vec 					=	paramProcess.Forward_Transfer_data(switchesTransferPath,'BUK9Y6R540H')

BUK9Y6R540H			=	{																																	#*	BUK9Y6R540H parameters
							'Config'						:	1																						,	#!	1->electric integrated | 2->electric separate | 3->thermal integrated | 4->thermal separate
							'Transistor'  			: 	{																									#!	transistors parameters
									'Config'				:	2																						,	#?	1->real model | 2->ideal model | 3->behavioral model
									'Thermal'           	:   ''                                  													,   #? 	selected transistor
									'Custom'            	:   []						               													,   #? 	transistor provided custom variables
									'g_fs'					:	1e6																						,	#?	forward transconductance
									'Rg'					:	670.9e-3																				,	#?	internal gate resistance
									'Lg'					:	1.509e-9*0																				,	#?	gate pin inductance
									'Rds_on'            	:   Rvec[-1][-1]*1e-3																		,   #? 	transistor ON resistance
									'Rds_off'				:	'inf'																					,	#?	transistor OFF resistance
									'Rvec'					:	(np.array(Rvec)*1e-3).tolist()														,	#?	absolute Rdson vector corresponding to junction temperature
									'Tvec'					:	Tvec 																					,	#?	junction temperature vector for Rdson
									'RTconfig'				:	1																						,	#?	choose which RT vector to be used, 1->typ | 2->max
									'RdsonScale'			:	1.607																					,	#?	Rdson scaling to account for min, typ and max deviations
									'Nvec'					:	Nvec 																					,	#?	normalized Rdson vector corresponding to current
									'Ivec'					:	Ivec																					,	#?	current vector for normalized Rdson
									'NIconfig'				:	1																						,	#?	choose which NI vector to be used (Vgs=4.5,10)
									'IdsonScale'			:	1.0																						,	#?	Idson resistance scaling to account for min, typ and max deviations
									'Rsrc'					:	0																						,	#?	kelvin source pin resistance
									'Lsrc'					:	0																						,	#?	kelvin source pin inductance
									'Ls'					:	530e-12*0																				,	#?	package source inductance
                                    'Ld'					:	10e-12*0																				,	#?	package drain inductance
									'Rs'					:	1e-6*0																					,	#?	package source resistance
									'Rd'					:	4.836e-3*0																				,	#?	package drain inductance
									'Ksrc'					:	0																						,	#?	kelvin source option, 0->no kelvin | 1->kelvin
									'Vblock'            	:   40                                	 													,   #? 	transistor blocking voltage
									'Id'                	:   70	                                 													,   #? 	transistor drain current
									'Tr'                	:   22e-9                                  													,   #? 	transistor rise time
									'Tf'                	:   17e-9                                      												, 	#? 	transistor fall time
									'Avalanche'		:	{																									#!	transistor avalanche parameters
										'Config'			:	2																						,	#?	1->enable | 2->disable
										'Voltage'			:	70																						,	#?	avalanche voltage
										'Resistance'		:	1e-3																						#?	avalanche resistance to break voltage state-dependency
									},
									'Transfer'		:	{																									#!	transistor forward transfer parameters
										'Vds'				:	Vds_vec																					,	#?	drain-source voltage vector
										'Vgs'				:	list(np.arange(0.0,12.0+0.2,0.2))													,	#?	gate-source voltage vector
										'Ids'				:	Ids_vec																					,	#?	drain current vector
										'Factor_ON'			:	1.0																						,	#?	scaling factor for Ids at turn ON
										'Factor_OFF'		:	1.0																						,	#?	scaling factor for Ids at turn OFF
										'Factor_Vgs_ON'		:	1.0																						,	#?	scaling factor for Vgs at turn ON
										'Factor_Vgs_OFF'	:	1.0																						,	#?	scaling factor for Vgs at turn OFF
										'Vcoss'				:	0																						,	#?	initial voltage of the Coss
									},
						},
							'BodyDiode'  			:	{																									#!	body diodes paramteters
									'Config'				:	4																						,	#?	1->non-ideal RR | 2->non-ideal | 3->ideal RR | 4->ideal
									'Thermal'           	:   ''                                  													,   #? 	separate body diode
									'Custom'            	:   []					                 													,   #? 	body diode provided custrom variables
									'Rd_on'             	:   Rd[-1]																					,  	#? 	body diode ON resistance
									'Rd_off'				:	'inf'																					,	#?	body diode OFF resistance
									'Vf'					:	Vt[-1]																					,	#? 	body diode forward voltage
									'If'                	:   70	                                 													,   #? 	body diode forward current
									'dIr'               	:   100e6	                                  												,   #? 	body diode current slope
									'Lrr'					:	1e-9																					,	#?	body diode reverse recovery inductance
									'Trr'               	:   19e-9	                                  												,   #? 	body diode reverse recovery time
									'Irr'               	:   0                                   													,   #? 	body diode reverse recovery current
									'Qrr'               	:   9.9e-9	                                  												, 	#? 	body diode reverse recovery charge
									'Is'                  	:   20              																		, 	#? 	body diode reference current
									'Vs'					:	20																						,	#?	body diode reference voltage
                                    'VIcurve'		:	{																									#!	body diode VI characteristics
                                        'Vfvec'				:	Vfvec																					,	#?	forward voltage vector
                                        'Ifvec'				:	Ifvec																					,	#?	forward current vector
										'Rdvec'				:	Rd																						,	#?	dynamic resistance vector
										'Vtvec'				:	Vt																						,	#?	threshold voltage vector
                                        'Temps'				:	[25,175]																				,	#?	temperature vector
                                        'Vfscale'			:	1.205																						#?	Vf scaling to account for min, typ and max deviations
									},
						},
							'GateDriver'			:	{																									#!	gate driver parameters
									'Config'				:	3																						,	#?	1->high-side | 2->low-side | 3->disable
									'Von'					:	12																						,	#?	ON driving voltage
									'Voff'					:	0																						,	#?	OFF driving voltage
									'Ron'					:	5																						,	#?	sourcing output resistance
									'Roff'					:	5																						,	#?	sinking output resistance
									'Lon'					:	0																						,	#?	sourcing output inductance
									'Loff'					:	0																						,	#?	sinking output inductance
									'Cload'					:	0																						,	#?	capacitive load on output
									'Rload'					:	'inf'																					,	#?	resistive load on output
									'Delay'					:	0																						,	#?	input-to-output total deadtime
									'Trise'					:	0																						,	#?	output rising time
									'Tfall'					:	0																						,	#?	output falling time
									'UVLO_Start'			:	7.0																						,	#?	UVLO startup voltage threshold
									'UVLO_Stop'				:	6.5																						,	#?	UVLO shutdown voltage threshold
									'UVLO_Delay'			:	100e-9																					,	#?	delay between UVLO startup and shutdown
									'Init_State'			:	0																						,	#?	initial toggling state, 0->OFF | 1->ON
									'CurrentLimit'	:	{																									#*	current limit of driver stage
										'Config'			:	2																						,	#?	1->enable | 2->disable
										'Ts'				: 	0 																						,	#?	sampling time between inductive & capacitive links
										'tau'				: 	0																						,	#?	first-order delay between inductive & capacitive links
                                    	'Rs'				: 	0																						,	#?	source impedance of inductive link
										'Cs'				:	1e-12																					,	#?	source capacitance of capacitive link
                                        'UpLim'				: 	10																						,	#?	max current limit on capacitive link
                                        'LoLim'				: 	-10																						,	#?	min current limit on capacitive link
                                        'Voffset'			: 	0																							#?	voltage offset between inductive & capacitive links
									},
									'Masking'		:	{																									#*	switching stages masking
										'ON'	:	{																										#	ON path masking
											'Config'		:	2																						,	#?	1->enable | 2->disable
											'HIGH'	:	{																									#!	HIGH mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[0, 0]																						#?	mask output
											},
											'LOW'	:	{																									#!	LOW mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[1, 1]																						#?	mask output
											}
										},
										'OFF'	:	{																										#	OFF path masking
											'Config'		:	2																						,	#?	1->enable | 2->disable
											'HIGH'	:	{																									#!	HIGH mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[0, 0]																						#?	mask output
											},
											'LOW'	:	{																									#!	LOW mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[1, 1]																						#?	mask output
											}
										}
									},
									'Boot'			:	{																									#*	bootstrap/charge pump parameters
										'Config'			:	1																						,	#?	1->bootstrap | 2->charge pump
										'Von'				:	14																						,	#?	boostrap driving voltage
										'Cboot'				:	4.7e-6																					,	#?	bootstrap capacitance
										'Vinit'				:	0																						,	#?	bootstrap capacitance initial voltage
										'Rboot'				:	10																						,	#?	bootstrap resistance
										'Vfboot'			:	0.87																					,	#?	bootstrap diode forward voltage
										'Rdboot'			:	1e-3																					,	#?	bootstrap diode ON-state resistance
										'Ichrg'				:	300e-6																					,	#?	charge pump supply current
										'Idis'				:	5e-6																					,	#?	charge pump loading or leakage current
										'Cpar'				:	0																						,	#?	charge pump parallel cap to break state/source dependency
									    'UVLO_Start'		:	11.6																					,	#?	threshold value to start the charge pump
										'UVLO_Stop'			:	12.4																						#?	threshold value to stop the charge pump
									},
							},
							'GateNetwork'			:	{																									#!	gate drive circuit parameters
									'Config'				:	2																						,	#?	1-> enable | 2->disable
									'ON_Path'		:	{																									#*	sourcing path parameters
										'Rg'				:	5																						,	#?	gate ON path resistance
										'Lg'				:	0																						,	#?	gate ON path inductance
										'Rload'				:	10e3																					,	#?	gate pull down resistance
										'Diode'	:	{																										#	reverse blocking diode parameters
											'Vf'			:	0																						,	#?	forward voltage
											'Rd_on'			:	0																						,	#?	ON-state resistance
										},
									},
									'OFF_Path'		:	{																									#*	sinking path parameters
										'Rg'				:	5																						,	#?	gate OFF path resistance
										'Lg'				:	0																						,	#?	gate OFF path inductance
										'Diode'	:	{																										#	reverse blocking diode parameters
											'Vf'			:	0																						,	#?	forward voltage
											'Rd_on'			:	0																						,	#?	ON-state resistance
										},
									},
									'NegVolt'		:	{																									#*	negative voltage generator parameters
										'Config'			:	2																						,	#?	1-> enable | 2->disable
										'Dz'	:	{																										#	zener diode parameters
											'Vf'			:	0.7																						,	#?	forward voltage
											'Rd_on'			:	1e-3																					,	#?	ON-state resistance
											'Vz'			:	2																						,	#?	Zener breakdown voltage
											'Rz'			:	1e-3																					,	#?	Zener resistance
										},
										'Dp'	:	{																										#	peak detector diode
											'Vf'			:	0.0																						,	#?	forward voltage
											'Rd_on'			:	0.0																						,	#?	ON-state resistance
										},
										'Cz'	:	{																										#	Zener capacitor parameters
											'Config'		:	1																						,	#?	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
											'Csingle'		:	1e-6																					,	#?	single capacitor value
											'Rsingle'		:	5e-3																					,	#?	ESR of single capacitor
											'Lsingle'		:	0																						,	#?	ESL of single capacitor
											'nPar'			:	1																						,	#?	number of parallel connections
											'nSer'			:	1																						,	#?	number of series connections
											'Vinit'			:	0																						,	#?	capacitor initial voltage
										},
										'Cp'	:	{																										#	peak detector capacitor parameters
											'Config'		:	1																						,	#?	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
											'Csingle'		:	2.2e-6																					,	#?	single capacitor value
											'Rsingle'		:	5e-3																					,	#?	ESR of single capacitor
											'Lsingle'		:	0																						,	#?	ESL of single capacitor
											'nPar'			:	1																						,	#?	number of parallel connections
											'nSer'			:	1																						,	#?	number of series connections
											'Vinit'			:	0																						,	#?	capacitor initial voltage
										},
										'Rp1'				:	43																						,	#?	current limiter of peak detector current
										'Rp2'				:	4.7e3																					,	#?	load resistor to charge the zener diode
									},
								},
							'nParallel'   					:	1                                       												,   #? 	number of parallel devices
							'Rth_jc'						:	2.35																					,	#?	junction-to-case thermal resistance
							'Cth_jc'						:	0.00																					,	#?	junction-to-case thermal capacitance
							'Rth_ca'              			:   2.35            																		,   #? 	case-to-ambient thermal resistance
							'Cth_ca'              			:   0.0             																		,   #? 	case-to-ambient thermal capacitance
							'Tinit'							:	0.0																						,	#?	initial juntion temperature
							'Pinit'							:	0.0																						,	#?	initial power dissipation
							'Coss'					: 	{																									#!	device Coss parameters
								'C'							:	Coss_eff					 															,	#?	device parasitic output capacitance
								'R'							:	0																						,	#?	Coss resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Coss inductance to reduce current slope
								'Coss_er'					:	Crss_er																					,	#?	energy-related Coss
								'Coss_tr'					:	Coss_tr																					,	#?	time-related Coss
								'Vvec'						:	Coss[0]																					,	#? 	device Coss voltage vector
								'Cvec'						:	Coss[1]																					,	#?	device Coss capacity vector
								'Offset'					:	0																						,	#?	parasitic offset to Coss
                                'Factor'					:	1.0																						,	#?	parasitic tolerance to Coss
								'Qoss'						:	Qoss																					,	#?	equivalent charge of Coss
								'Eoss'						:	Eoss																					,	#?	equivalent energy of Coss
								'Config'					:	5																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
						},
                        	'Crss'					:	{																									#!	device Crss parameters
                                'C'							:	Crss_eff					 															,	#?	device parasitic reverse transfer capacitance
								'R'							:	0																						,	#?	Crss resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Crss inductance to reduce current slope
								'Crss_er'					:	Crss_er																					,	#?	energy-related Crss
								'Crss_tr'					:	Crss_tr																					,	#?	time-related Crss
								'Vvec'						:	Crss[0]																					,	#?	device Crss voltage vector
                                'Cvec'						:	Crss[1]																					,	#?	device Crss capacity vector
								'Qvec'						:	Qrss																					,	#?	device accumulated Crss charge vector
								'Offset'					:	0																						,	#?	parasitic offset to Crss
								'Factor'					:	1.0																						,	#?	parasitic tolerance to Crss
								'Qrss'						:	Qrss																					,	#?	equivalent charge of Crss
								'Erss'						:	Erss																					,	#?	equivalent energe of Crss
								'Config'					:	5																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
						},
							'Ciss'					:	{																									#!	device Ciss parameters
								'C'							:	Ciss_eff					 															,	#?	device parasitic input capacitance
								'R'							:	0																						,	#?	Ciss resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Ciss inductance to reduce current slope
								'Ciss_er'					:	Ciss_er																					,	#?	energy-related Ciss
								'Ciss_tr'					:	Ciss_tr																					,	#?	time-related Ciss
								'Vvec'						:	Ciss[0]																					,	#?	device Ciss voltage vector
								'Cvec'						:	Ciss[1]																					,	#?	device Ciss capacity vector
								'Offset'					:	0																						,	#?	parasitic offset to Ciss
								'Factor'					:	1.0																						,	#?	parasitic tolerance to Ciss
								'Qiss'						:	Qiss																					,	#?	equivalent charge of Ciss
								'Eiss'						:	Eiss																					,	#?	equivalent energy of Ciss
								'Config'					:	5																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Cds'					:	{																									#!	device Cds parameters
								'C'							:	Cds_eff					 																,	#?	device parasitic Cds capacitance
								'R'							:	0																						,	#?	Cds resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Cds inductance to reduce current slope
								'Cds_er'					:	Cds_er																					,	#?	energy-related Cds
								'Cds_tr'					:	Cds_tr																					,	#?	time-related Cds
								'Vvec'						:	Coss[0]																					,	#?	device Cds voltage vector
								'Cvec'						:	Cds																						,	#?	device Cds capacity vector
								'Offset_ON'					:	0																						,	#?	tuning offset for turn ON
								'Offset_OFF'				:	0																						,	#?	tuning offset for turn OFF
								'Factor_ON'					:	1.0																						,	#?	tuning factor for turn ON
								'Factor_OFF'				:	1.0																						,	#?	tuning factor for turn OFF
								'Config'					:	4																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Cgd'					:	{																									#!	device Cgd parameters
								'C'							:	Cgd_eff							 														,	#?	device parasitic Cgd capacitance
								'R'							:	0																						,	#?	Cgd resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Cgd inductance to reduce current slope
								'Cgd_er'					:	Cgd_er																					,	#?	energy-related Cgd
								'Cgd_tr'					:	Cgd_tr																					,	#?	time-related Cgd
								'Vvec'						:	Crss[0]																					,	#?	device Cgd voltage vector
								'Cvec'						:	Cgd																						,	#?	device Cgd capacity vector
								'Offset_ON'					:	0																						,	#?	tuning offset for turn ON
								'Offset_OFF'				:	0																						,	#?	tuning offset for turn OFF
								'Factor_ON'					:	1.0																						,	#?	tuning factor for turn ON
								'Factor_OFF'				:	1.0																						,	#?	tuning factor for turn OFF
								'Config'					:	4																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Cgs'					:	{																									#!	device Cgs parameters
								'C'							:	Cgs_eff					 																,	#?	device parasitic Cgs capacitance
								'R'							:	0																						,	#?	Cgs resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Cgs inductance to reduce current slope
								'Cgs_er'					:	Cgs_er																					,	#?	energy-related Cgs
								'Cgs_tr'					:	Cgs_tr																					,	#?	time-related Cgs
								'Vvec'						:	Ciss[0]																					,	#?	device Cgs voltage vector
								'Cvec'						:	Cgs																						,	#?	device Cgs capacity vector
								'Offset_ON'					:	0																						,	#?	tuning offset for turn ON
								'Offset_OFF'				:	0																						,	#?	tuning offset for turn OFF
								'Factor_ON'					:	1.0																						,	#?	tuning factor for turn ON
								'Factor_OFF'				:	1.0																						,	#?	tuning factor for turn OFF
								'Config'					:	4																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Eoff'					:	{																									#!	transistor turn-OFF energy losses
									'Ivec'					:	Ioff																					,	#?	turn-OFF energy current vector
									'Rgvec'					:	[0,100]																					,	#?	OFF path gate resistances vector
									'Tjvec'					:	[-55,175]																				,	#?	junction temperature vector
                                    'Vvec'					:	Voff																					,	#?	turn-OFF voltage vector
                                    'Evec'					:	Eoff																					,	#?	turn-OFF energy vectors
									'Evec_Temp'				:	Eoff_Temp																				,	#?	turn-OFF energy temp scaling vectors
                                    'CAT'					:	catOFF																					,	#?	octave Eoff energy syntax
									'CAT_Temp'				:	catOFF_Temp																				,	#?	octave Eoff energy temp scaling syntax
									'Vgs'					:	0																						,	#?	used OFF path gate-source voltage
									'Vth'					:	1.5																						,	#?	used OFF path threshold voltage
									'Rg'					:	0																							#?	used OFF path gate resistance
						},
							'Eon'					:	{																									#!	transistor turn-ON energy losses
									'Ivec'					:	Ion																						,	#?	turn-ON energy current vector
									'Rgvec'					:	[0,100]																					,	#?	ON path gate resistances vector
									'Tjvec'					:	[-55,175]																				,	#?	junction temperature vector
                                    'Vvec'					:	Von																						,	#?	turn-ON voltage vector
                                    'Evec'					:	Eon																						,	#?	turn-ON energy vectors
									'Evec_Temp'				:	Eon_Temp																				,	#?	turn-ON energy temp scaling vectors
                                    'CAT'					:	catON																					,	#?	octave Eon energy syntax
									'CAT_Temp'				:	catON_Temp																				,	#?	octave Eon energy temp scaling syntax
									'Vgs'					:	12																						,	#?	used ON path gate-source voltage
									'Vth'					:	1.5																						,	#?	used ON path threshold voltage
									'Rg'					:	0																							#?	used ON path gate resistance
						},
							'Tau_deg'						:	100e-9																					,	#?	deglitch filter for currents and voltages
							'RCsnubber'						:	2																						,	#?	1->enable | 2->disable
						}

#?----------------------------------------------------------------------------------------------------------------------------------------------------------------------

Coss,Qoss,Eoss,Coss_tr,Coss_er		=	paramProcess.MOSFETcaps(switchesCossPath,'BUK6D3040E','_Coss')
Crss,Qrss,Erss,Crss_tr,Crss_er 		=	paramProcess.MOSFETcaps(switchesCrssPath,'BUK6D3040E','_Crss')
Ciss,Qiss,Eiss,Ciss_tr,Ciss_er 		=	paramProcess.MOSFETcaps(switchesCissPath,'BUK6D3040E','_Ciss')
Coss_eff 							=	paramProcess.getCmos(Coss,Coss_tr,Coss_er,Coss[0][0],True)
Ciss_eff 							=	paramProcess.getCmos(Ciss,Ciss_tr,Ciss_er,Ciss[0][0],True)
Crss_eff 							=	paramProcess.getCmos(Crss,Crss_tr,Crss_er,Crss[0][0],True)
Cds 						        =	(np.array(Coss[1]) - np.array(Crss[1])).tolist()
Cgs						        	=	(np.array(Ciss[1]) - np.array(Crss[1])).tolist()
Cgd						        	=	Crss[1]
Cds_tr						        =	(np.array(Coss_tr) - np.array(Crss_tr)).tolist()
Cgs_tr						        =	(np.array(Ciss_tr) - np.array(Crss_tr)).tolist()
Cgd_tr						        =	Crss_tr
Cds_er						        =	(np.array(Coss_er) - np.array(Crss_er)).tolist()
Cgs_er						        =	(np.array(Ciss_er) - np.array(Crss_er)).tolist()
Cgd_er						        =	Crss_er
Cds_eff 							=	paramProcess.getCmos([Coss[0],Cds],Cds_tr,Cds_er,Coss[0][0],True)
Cgs_eff 							=	paramProcess.getCmos([Ciss[0],Cgs],Cgs_tr,Cgs_er,Ciss[0][0],True)
Cgd_eff 							=	Crss_eff
Rvec,Tvec							=	paramProcess.MOSFETrdson(switchesRdsonPath,'BUK6D3040E','_Rdson')
Nvec,Ivec 							=	paramProcess.MOSFETrdson(switchesIdsonPath,'BUK6D3040E','_Rdson')
Ioff,catOFF,Eoff					=	paramProcess.MOSFETenergies(switchesEoffPath,'BUK6D3040E','_Eoff')
Voff,catOFF_Temp,Eoff_Temp			=	paramProcess.MOSFETenergies(switchesEoffPath,'BUK6D3040E','_Eoff_Temp')
Ion,catON,Eon 						=	paramProcess.MOSFETenergies(switchesEonPath,'BUK6D3040E','_Eon')
Von,catON_Temp,Eon_Temp				=	paramProcess.MOSFETenergies(switchesEonPath,'BUK6D3040E','_Eon_Temp')
Vfvec,Ifvec,Rd,Vt					=	paramProcess.DiodeVI_data(bodyDiodeVIPath,'BUK6D3040E')
Vds_vec,Ids_vec 					=	paramProcess.Forward_Transfer_data(switchesTransferPath,'BUK6D3040E')

BUK6D3040E			=	{																																	#*	BUK6D3040E parameters
							'Config'						:	1																						,	#!	1->electric integrated | 2->electric separate | 3->thermal integrated | 4->thermal separate
							'Transistor'  			: 	{																									#!	transistors parameters
									'Config'				:	2																						,	#?	1->real model | 2->ideal model | 3->behavioral model
									'Thermal'           	:   ''                                  													,   #? 	selected transistor
									'Custom'            	:   []						               													,   #? 	transistor provided custom variables
									'g_fs'					:	1e6																						,	#?	forward transconductance
									'Rg'					:	2.0																						,	#?	internal gate resistance
									'Lg'					:	0																						,	#?	gate pin inductance
									'Rds_on'            	:   Rvec[-1][-1]*1e-3																		,   #? 	transistor ON resistance
									'Rds_off'				:	'inf'																					,	#?	transistor OFF resistance
									'Rvec'					:	(np.array(Rvec)*1e-3).tolist()														,	#?	absolute Rdson vector corresponding to junction temperature
									'Tvec'					:	Tvec 																					,	#?	junction temperature vector for Rdson
									'RTconfig'				:	1																						,	#?	choose which RT vector to be used, 1->typ | 2->max
									'RdsonScale'			:	1.3043																					,	#?	Rdson scaling to account for min, typ and max deviations
									'Nvec'					:	Nvec 																					,	#?	normalized Rdson vector corresponding to current
									'Ivec'					:	Ivec																					,	#?	current vector for normalized Rdson
									'NIconfig'				:	1																						,	#?	choose which NI vector to be used (Vgs=4.5,10)
									'IdsonScale'			:	1.0																						,	#?	Idson resistance scaling to account for min, typ and max deviations
									'Rsrc'					:	0																						,	#?	kelvin source pin resistance
									'Lsrc'					:	0																						,	#?	kelvin source pin inductance
									'Ls'					:	0																						,	#?	package source inductance
                                    'Ld'					:	0																						,	#?	package drain inductance
									'Rs'					:	0																						,	#?	package source resistance
									'Rd'					:	0																						,	#?	package drain inductance
									'Ksrc'					:	0																						,	#?	kelvin source option, 0->no kelvin | 1->kelvin
									'Vblock'            	:   40                                	 													,   #? 	transistor blocking voltage
									'Id'                	:   18	                                 													,   #? 	transistor drain current
									'Tr'                	:   1e-9                                  													,   #? 	transistor rise time
									'Tf'                	:   1e-9                                      												, 	#? 	transistor fall time
									'Avalanche'		:	{																									#!	transistor avalanche parameters
										'Config'			:	2																						,	#?	1->enable | 2->disable
										'Voltage'			:	40																						,	#?	avalanche voltage
										'Resistance'		:	1e-3																						#?	avalanche resistance to break voltage state-dependency
									},
									'Transfer'		:	{																									#!	transistor forward transfer parameters
										'Vds'				:	Vds_vec																					,	#?	drain-source voltage vector
										'Vgs'				:	list(np.arange(0.0,12.0+0.2,0.2))													,	#?	gate-source voltage vector
										'Ids'				:	Ids_vec																					,	#?	drain current vector
										'Factor_ON'			:	1.0																						,	#?	scaling factor for Ids at turn ON
										'Factor_OFF'		:	1.0																						,	#?	scaling factor for Ids at turn OFF
										'Factor_Vgs_ON'		:	1.0																						,	#?	scaling factor for Vgs at turn ON
										'Factor_Vgs_OFF'	:	1.0																						,	#?	scaling factor for Vgs at turn OFF
										'Vcoss'				:	0																						,	#?	initial voltage of the Coss
									},
						},
							'BodyDiode'  			:	{																									#!	body diodes paramteters
									'Config'				:	4																						,	#?	1->non-ideal RR | 2->non-ideal | 3->ideal RR | 4->ideal
									'Thermal'           	:   ''                                  													,   #? 	separate body diode
									'Custom'            	:   []					                 													,   #? 	body diode provided custrom variables
									'Rd_on'             	:   Rd[-1]																					,  	#? 	body diode ON resistance
									'Rd_off'				:	'inf'																					,	#?	body diode OFF resistance
									'Vf'					:	Vt[-1]																					,	#? 	body diode forward voltage
									'If'                	:   18	                                 													,   #? 	body diode forward current
									'dIr'               	:   100e6	                                  												,   #? 	body diode current slope
									'Lrr'					:	1e-9																					,	#?	body diode reverse recovery inductance
									'Trr'               	:   11e-9	                                  												,   #? 	body diode reverse recovery time
									'Irr'               	:   0                                   													,   #? 	body diode reverse recovery current
									'Qrr'               	:   4.0e-9	                                  												, 	#? 	body diode reverse recovery charge
									'Is'                  	:   1.6              																		, 	#? 	body diode reference current
									'Vs'					:	20																						,	#?	body diode reference voltage
                                    'VIcurve'		:	{																									#!	body diode VI characteristics
                                        'Vfvec'				:	Vfvec																					,	#?	forward voltage vector
                                        'Ifvec'				:	Ifvec																					,	#?	forward current vector
										'Rdvec'				:	Rd																						,	#?	dynamic resistance vector
										'Vtvec'				:	Vt																						,	#?	threshold voltage vector
                                        'Temps'				:	[-55,0,25,75,175]																				,	#?	temperature vector
                                        'Vfscale'			:	1.50																						#?	Vf scaling to account for min, typ and max deviations
									},
						},
							'GateDriver'			:	{																									#!	gate driver parameters
									'Config'				:	3																						,	#?	1->high-side | 2->low-side | 3->disable
									'Von'					:	6																						,	#?	ON driving voltage
									'Voff'					:	0																						,	#?	OFF driving voltage
									'Ron'					:	10																						,	#?	sourcing output resistance
									'Roff'					:	10																						,	#?	sinking output resistance
									'Lon'					:	0																						,	#?	sourcing output inductance
									'Loff'					:	0																						,	#?	sinking output inductance
									'Cload'					:	0																						,	#?	capacitive load on output
									'Rload'					:	'inf'																					,	#?	resistive load on output
									'Delay'					:	0																						,	#?	input-to-output total deadtime
									'Trise'					:	0																						,	#?	output rising time
									'Tfall'					:	0																						,	#?	output falling time
									'UVLO_Start'			:	2																						,	#?	UVLO startup voltage threshold
									'UVLO_Stop'				:	1																						,	#?	UVLO shutdown voltage threshold
									'UVLO_Delay'			:	100e-9																					,	#?	delay between UVLO startup and shutdown
									'Init_State'			:	0																						,	#?	initial toggling state, 0->OFF | 1->ON
									'CurrentLimit'	:	{																									#*	current limit of driver stage
										'Config'			:	2																						,	#?	1->enable | 2->disable
										'Ts'				: 	0 																						,	#?	sampling time between inductive & capacitive links
										'tau'				: 	0																						,	#?	first-order delay between inductive & capacitive links
                                    	'Rs'				: 	0																						,	#?	source impedance of inductive link
										'Cs'				:	1e-12																					,	#?	source capacitance of capacitive link
                                        'UpLim'				: 	10																						,	#?	max current limit on capacitive link
                                        'LoLim'				: 	-10																						,	#?	min current limit on capacitive link
                                        'Voffset'			: 	0																							#?	voltage offset between inductive & capacitive links
									},
									'Masking'		:	{																									#*	switching stages masking
										'ON'	:	{																										#	ON path masking
											'Config'		:	2																						,	#?	1->enable | 2->disable
											'HIGH'	:	{																									#!	HIGH mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[0, 0]																						#?	mask output
											},
											'LOW'	:	{																									#!	LOW mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[1, 1]																						#?	mask output
											}
										},
										'OFF'	:	{																										#	OFF path masking
											'Config'		:	2																						,	#?	1->enable | 2->disable
											'HIGH'	:	{																									#!	HIGH mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[0, 0]																						#?	mask output
											},
											'LOW'	:	{																									#!	LOW mask configuration
												'TimeVec'	:	[0, 1]																					,	#?	activation time vector
												'OutVec'	:	[1, 1]																						#?	mask output
											}
										}
									},
									'Boot'			:	{																									#*	bootstrap/charge pump parameters
										'Config'			:	2																						,	#?	1->bootstrap | 2->charge pump
										'Von'				:	0																						,	#?	boostrap driving voltage
										'Cboot'				:	0																						,	#?	bootstrap capacitance
										'Vinit'				:	0																						,	#?	bootstrap capacitance initial voltage
										'Rboot'				:	0																						,	#?	bootstrap resistance
										'Vfboot'			:	0																						,	#?	bootstrap diode forward voltage
										'Rdboot'			:	0																						,	#?	bootstrap diode ON-state resistance
										'Ichrg'				:	0																						,	#?	charge pump supply current
										'Idis'				:	0																						,	#?	charge pump loading or leakage current
										'Cpar'				:	0																						,	#?	charge pump parallel cap to break state/source dependency
									    'UVLO_Start'		:	0																						,	#?	threshold value to start the charge pump
										'UVLO_Stop'			:	0																								#?	threshold value to stop the charge pump
									},
							},
							'GateNetwork'			:	{																									#!	gate drive circuit parameters
									'Config'				:	2																						,	#?	1-> enable | 2->disable
									'ON_Path'		:	{																									#*	sourcing path parameters
										'Rg'				:	10																						,	#?	gate ON path resistance
										'Lg'				:	0																						,	#?	gate ON path inductance
										'Rload'				:	10e3																					,	#?	gate pull down resistance
										'Diode'	:	{																										#	reverse blocking diode parameters
											'Vf'			:	0																						,	#?	forward voltage
											'Rd_on'			:	0																						,	#?	ON-state resistance
										},
									},
									'OFF_Path'		:	{																									#*	sinking path parameters
										'Rg'				:	10																						,	#?	gate OFF path resistance
										'Lg'				:	0																						,	#?	gate OFF path inductance
										'Diode'	:	{																										#	reverse blocking diode parameters
											'Vf'			:	0																						,	#?	forward voltage
											'Rd_on'			:	0																						,	#?	ON-state resistance
										},
									},
									'NegVolt'		:	{																									#*	negative voltage generator parameters
										'Config'			:	2																						,	#?	1-> enable | 2->disable
										'Dz'	:	{																										#	zener diode parameters
											'Vf'			:	0																						,	#?	forward voltage
											'Rd_on'			:	0																						,	#?	ON-state resistance
											'Vz'			:	0																						,	#?	Zener breakdown voltage
											'Rz'			:	0																						,	#?	Zener resistance
										},
										'Dp'	:	{																										#	peak detector diode
											'Vf'			:	0.0																						,	#?	forward voltage
											'Rd_on'			:	0.0																						,	#?	ON-state resistance
										},
										'Cz'	:	{																										#	Zener capacitor parameters
											'Config'		:	5																						,	#?	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
											'Csingle'		:	0																						,	#?	single capacitor value
											'Rsingle'		:	0																						,	#?	ESR of single capacitor
											'Lsingle'		:	0																						,	#?	ESL of single capacitor
											'nPar'			:	1																						,	#?	number of parallel connections
											'nSer'			:	1																						,	#?	number of series connections
											'Vinit'			:	0																						,	#?	capacitor initial voltage
										},
										'Cp'	:	{																										#	peak detector capacitor parameters
											'Config'		:	5																						,	#?	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
											'Csingle'		:	0																						,	#?	single capacitor value
											'Rsingle'		:	0																						,	#?	ESR of single capacitor
											'Lsingle'		:	0																						,	#?	ESL of single capacitor
											'nPar'			:	1																						,	#?	number of parallel connections
											'nSer'			:	1																						,	#?	number of series connections
											'Vinit'			:	0																						,	#?	capacitor initial voltage
										},
										'Rp1'				:	0																						,	#?	current limiter of peak detector current
										'Rp2'				:	0																						,	#?	load resistor to charge the zener diode
									},
								},
							'nParallel'   					:	1                                       												,   #? 	number of parallel devices
							'Rth_jc'						:	8.0																						,	#?	junction-to-case thermal resistance
							'Cth_jc'						:	0.00																					,	#?	junction-to-case thermal capacitance
							'Rth_ca'              			:   68.0            																		,   #? 	case-to-ambient thermal resistance
							'Cth_ca'              			:   0.0             																		,   #? 	case-to-ambient thermal capacitance
							'Tinit'							:	0.0																						,	#?	initial juntion temperature
							'Pinit'							:	0.0																						,	#?	initial power dissipation
							'Coss'					: 	{																									#!	device Coss parameters
								'C'							:	Coss_eff					 															,	#?	device parasitic output capacitance
								'R'							:	0																						,	#?	Coss resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Coss inductance to reduce current slope
								'Coss_er'					:	Crss_er																					,	#?	energy-related Coss
								'Coss_tr'					:	Coss_tr																					,	#?	time-related Coss
								'Vvec'						:	Coss[0]																					,	#? 	device Coss voltage vector
								'Cvec'						:	Coss[1]																					,	#?	device Coss capacity vector
								'Offset'					:	0																						,	#?	parasitic offset to Coss
                                'Factor'					:	1.0																						,	#?	parasitic tolerance to Coss
								'Qoss'						:	Qoss																					,	#?	equivalent charge of Coss
								'Eoss'						:	Eoss																					,	#?	equivalent energy of Coss
								'Config'					:	5																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
						},
                        	'Crss'					:	{																									#!	device Crss parameters
                                'C'							:	Crss_eff					 															,	#?	device parasitic reverse transfer capacitance
								'R'							:	0																						,	#?	Crss resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Crss inductance to reduce current slope
								'Crss_er'					:	Crss_er																					,	#?	energy-related Crss
								'Crss_tr'					:	Crss_tr																					,	#?	time-related Crss
								'Vvec'						:	Crss[0]																					,	#?	device Crss voltage vector
                                'Cvec'						:	Crss[1]																					,	#?	device Crss capacity vector
								'Qvec'						:	Qrss																					,	#?	device accumulated Crss charge vector
								'Offset'					:	0																						,	#?	parasitic offset to Crss
								'Factor'					:	1.0																						,	#?	parasitic tolerance to Crss
								'Qrss'						:	Qrss																					,	#?	equivalent charge of Crss
								'Erss'						:	Erss																					,	#?	equivalent energe of Crss
								'Config'					:	5																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
						},
							'Ciss'					:	{																									#!	device Ciss parameters
								'C'							:	Ciss_eff					 															,	#?	device parasitic input capacitance
								'R'							:	0																						,	#?	Ciss resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Ciss inductance to reduce current slope
								'Ciss_er'					:	Ciss_er																					,	#?	energy-related Ciss
								'Ciss_tr'					:	Ciss_tr																					,	#?	time-related Ciss
								'Vvec'						:	Ciss[0]																					,	#?	device Ciss voltage vector
								'Cvec'						:	Ciss[1]																					,	#?	device Ciss capacity vector
								'Offset'					:	0																						,	#?	parasitic offset to Ciss
								'Factor'					:	1.0																						,	#?	parasitic tolerance to Ciss
								'Qiss'						:	Qiss																					,	#?	equivalent charge of Ciss
								'Eiss'						:	Eiss																					,	#?	equivalent energy of Ciss
								'Config'					:	5																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Cds'					:	{																									#!	device Cds parameters
								'C'							:	Cds_eff					 																,	#?	device parasitic Cds capacitance
								'R'							:	0																						,	#?	Cds resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Cds inductance to reduce current slope
								'Cds_er'					:	Cds_er																					,	#?	energy-related Cds
								'Cds_tr'					:	Cds_tr																					,	#?	time-related Cds
								'Vvec'						:	Coss[0]																					,	#?	device Cds voltage vector
								'Cvec'						:	Cds																						,	#?	device Cds capacity vector
								'Offset_ON'					:	0																						,	#?	tuning offset for turn ON
								'Offset_OFF'				:	0																						,	#?	tuning offset for turn OFF
								'Factor_ON'					:	1.0																						,	#?	tuning factor for turn ON
								'Factor_OFF'				:	1.0																						,	#?	tuning factor for turn OFF
								'Config'					:	4																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Cgd'					:	{																									#!	device Cgd parameters
								'C'							:	Cgd_eff							 														,	#?	device parasitic Cgd capacitance
								'R'							:	0																						,	#?	Cgd resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Cgd inductance to reduce current slope
								'Cgd_er'					:	Cgd_er																					,	#?	energy-related Cgd
								'Cgd_tr'					:	Cgd_tr																					,	#?	time-related Cgd
								'Vvec'						:	Crss[0]																					,	#?	device Cgd voltage vector
								'Cvec'						:	Cgd																						,	#?	device Cgd capacity vector
								'Offset_ON'					:	0																						,	#?	tuning offset for turn ON
								'Offset_OFF'				:	0																						,	#?	tuning offset for turn OFF
								'Factor_ON'					:	1.0																						,	#?	tuning factor for turn ON
								'Factor_OFF'				:	1.0																						,	#?	tuning factor for turn OFF
								'Config'					:	4																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Cgs'					:	{																									#!	device Cgs parameters
								'C'							:	Cgs_eff					 																,	#?	device parasitic Cgs capacitance
								'R'							:	0																						,	#?	Cgs resistance to emulate limited dV/dt
								'L'							:	0																						,	#?	Cgs inductance to reduce current slope
								'Cgs_er'					:	Cgs_er																					,	#?	energy-related Cgs
								'Cgs_tr'					:	Cgs_tr																					,	#?	time-related Cgs
								'Vvec'						:	Ciss[0]																					,	#?	device Cgs voltage vector
								'Cvec'						:	Cgs																						,	#?	device Cgs capacity vector
								'Offset_ON'					:	0																						,	#?	tuning offset for turn ON
								'Offset_OFF'				:	0																						,	#?	tuning offset for turn OFF
								'Factor_ON'					:	1.0																						,	#?	tuning factor for turn ON
								'Factor_OFF'				:	1.0																						,	#?	tuning factor for turn OFF
								'Config'					:	4																							#? 	1->capacitor only | 2->include ESR | 3->include ESR & ESL | 4->variable capacitor | 5->pass | 6->short
							},
							'Eoff'					:	{																									#!	transistor turn-OFF energy losses
									'Ivec'					:	Ioff																					,	#?	turn-OFF energy current vector
									'Rgvec'					:	[0,100]																					,	#?	OFF path gate resistances vector
									'Tjvec'					:	[-55,175]																				,	#?	junction temperature vector
                                    'Vvec'					:	Voff																					,	#?	turn-OFF voltage vector
                                    'Evec'					:	Eoff																					,	#?	turn-OFF energy vectors
									'Evec_Temp'				:	Eoff_Temp																				,	#?	turn-OFF energy temp scaling vectors
                                    'CAT'					:	catOFF																					,	#?	octave Eoff energy syntax
									'CAT_Temp'				:	catOFF_Temp																				,	#?	octave Eoff energy temp scaling syntax
									'Vgs'					:	0																						,	#?	used OFF path gate-source voltage
									'Vth'					:	1.5																						,	#?	used OFF path threshold voltage
									'Rg'					:	10																							#?	used OFF path gate resistance
						},
							'Eon'					:	{																									#!	transistor turn-ON energy losses
									'Ivec'					:	Ion																						,	#?	turn-ON energy current vector
									'Rgvec'					:	[0,100]																					,	#?	ON path gate resistances vector
									'Tjvec'					:	[-55,175]																				,	#?	junction temperature vector
                                    'Vvec'					:	Von																						,	#?	turn-ON voltage vector
                                    'Evec'					:	Eon																						,	#?	turn-ON energy vectors
									'Evec_Temp'				:	Eon_Temp																				,	#?	turn-ON energy temp scaling vectors
                                    'CAT'					:	catON																					,	#?	octave Eon energy syntax
									'CAT_Temp'				:	catON_Temp																				,	#?	octave Eon energy temp scaling syntax
									'Vgs'					:	6																						,	#?	used ON path gate-source voltage
									'Vth'					:	1.5																						,	#?	used ON path threshold voltage
									'Rg'					:	10																							#?	used ON path gate resistance
						},
							'Tau_deg'						:	100e-9																					,	#?	deglitch filter for currents and voltages
							'RCsnubber'						:	2																						,	#?	1->enable | 2->disable
						}

#?----------------------------------------------------------------------------------------------------------------------------------------------------------------------

#!	assemble all switches to be transferred to the PLECS model
#?----------------------------------------------------------------------------------------------------------------------------------------------------------------------

LVswitchVars 			= 	{
								'IAUT300N10S5N015' 		: 	IAUT300N10S5N015 		,
                                'NVBYST001N08X' 		: 	NVBYST001N08X 			,
                                'NVBYST0D8N08X' 		: 	NVBYST0D8N08X 			,
                                'NVBYST0D6N08X'			:	NVBYST0D6N08X			,
								'NVBLS1D5N10MC' 		: 	NVBLS1D5N10MC 			,
								'NVBLS1D7N10MC' 		: 	NVBLS1D7N10MC 			,
								'IAUT300N08S5N014' 		: 	IAUT300N08S5N014 		,
								'IAUT300N08S5N012' 		: 	IAUT300N08S5N012 		,
								'NVBLS1D1N08H' 			: 	NVBLS1D1N08H 			,
								'FDBL86361' 			: 	FDBL86361 				,
								'NVBLS1D7N08H'			:	NVBLS1D7N08H			,
                                'SQJQ186ER_1'			:	SQJQ186ER_1
							}

HVswitchVars 			= 	{
								'GS66508T'				:	GS66508T				,
                                'AIMDQ75R060M1H'		:	AIMDQ75R060M1H			,
								'AIMDQ75R060M2H'		:	AIMDQ75R060M2H			,
                                'AIMDQ75R040M1H'		:	AIMDQ75R040M1H			,
                                'AIMDQ75R040M2H'		:	AIMDQ75R040M2H			,
                                'SCT055HU65G3AG'		:	SCT055HU65G3AG			,
								'SCTH35N65G2V'			:	SCTH35N65G2V
							}

shortCircuitSwitchVars	= 	{
								'NVMTS0D6N04CL' 		: 	NVMTS0D6N04CL 			,
                                'NVMTS0D6N04C'			:	NVMTS0D6N04C			,
                                'SQJQ144AER'			:	SQJQ144AER				,
                                'NVMJST0D7N04XM'		:	NVMJST0D7N04XM			,
                                'NVMJST0D5N04XM'		:	NVMJST0D5N04XM
							}

FreewheelingSwitchVars	=	{
								'NVMFS3D6N10MCL'		:	NVMFS3D6N10MCL			,
                                'SQJQ186ER_2'			:	SQJQ186ER_2				,
                                'NVMJST3D3N08X'			:	NVMJST3D3N08X			,
                                'NVMJST004N08X'			:	NVMJST004N08X
							}

AuxiliarySwitchVars		=	{
								'PMT200EPE'				:	PMT200EPE				,
								'BUK9Y6R540H'			:	BUK9Y6R540H				,
								'BUK6D3040E'			:	BUK6D3040E
							}

AllSwitches 			=	{
								'IAUT300N10S5N015' 		: 	IAUT300N10S5N015 		,
                                'NVBYST001N08X' 		: 	NVBYST001N08X 			,
                                'NVBYST0D8N08X'			:	NVBYST0D8N08X			,
                                'NVBYST0D6N08X'			:	NVBYST0D6N08X			,
								'NVBLS1D5N10MC' 		: 	NVBLS1D5N10MC 			,
								'NVBLS1D7N10MC' 		: 	NVBLS1D7N10MC 			,
								'IAUT300N08S5N014' 		: 	IAUT300N08S5N014 		,
								'IAUT300N08S5N012' 		: 	IAUT300N08S5N012 		,
								'NVBLS1D1N08H' 			: 	NVBLS1D1N08H 			,
								'FDBL86361' 			: 	FDBL86361 				,
								'NVBLS1D7N08H'			:	NVBLS1D7N08H			,
								'SQJQ186ER_1'			:	SQJQ186ER_1				,
								'SQJQ186ER_2'			:	SQJQ186ER_2				,
                                'GS66508T'				:	GS66508T				,
                                'AIMDQ75R060M1H'		:	AIMDQ75R060M1H			,
                                'AIMDQ75R060M2H'		:	AIMDQ75R060M2H			,
                                'AIMDQ75R040M1H'		:	AIMDQ75R040M1H			,
                                'AIMDQ75R040M2H'		:	AIMDQ75R040M2H			,
                                'SCT055HU65G3AG'		:	SCT055HU65G3AG			,
								'SCTH35N65G2V'			:	SCTH35N65G2V			,
                                'NVMTS0D6N04CL' 		: 	NVMTS0D6N04CL 			,
                                'NVMTS0D6N04C'			:	NVMTS0D6N04C			,
                                'SQJQ144AER'			:	SQJQ144AER				,
                                'NVMFS3D6N10MCL'		:	NVMFS3D6N10MCL			,
                                'PMT200EPE'				:	PMT200EPE				,
                                'BUK9Y6R540H'			:	BUK9Y6R540H				,
								'BUK6D3040E'			:	BUK6D3040E				,
                                'NVMJST3D3N08X'			:	NVMJST3D3N08X			,
                                'NVMJST004N08X'			:	NVMJST004N08X			,
                                'NVMJST0D7N04XM'		:	NVMJST0D7N04XM			,
                                'NVMJST0D5N04XM'		:	NVMJST0D5N04XM
							}
#?----------------------------------------------------------------------------------------------------------------------------------------------------------------------