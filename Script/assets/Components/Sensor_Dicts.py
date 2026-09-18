
#?----------------------------------------------------------------------------------------------------------------------------------------------------------------------
#?						 ____                                  ____                                _
#?						/ ___|  ___ _ __  ___  ___  _ __ ___  |  _ \ __ _ _ __ __ _ _ __ ___   ___| |_ ___ _ __ ___
#?						\___ \ / _ \ '_ \/ __|/ _ \| '__/ __| | |_) / _` | '__/ _` | '_ ` _ \ / _ \ __/ _ \ '__/ __|
#?						 ___) |  __/ | | \__ \ (_) | |  \__ \ |  __/ (_| | | | (_| | | | | | |  __/ ||  __/ |  \__ \
#?						|____/ \___|_| |_|___/\___/|_|  |___/ |_|   \__,_|_|  \__,_|_| |_| |_|\___|\__\___|_|  |___/
#?
#?----------------------------------------------------------------------------------------------------------------------------------------------------------------------
#!----------------------------------------------------------------------------------------------------------------------------------------------------------------------
#!   This Script works as a Parameter dictionary for the plecs sensor models.
#!   Do not modify the values in this file.
#!----------------------------------------------------------------------------------------------------------------------------------------------------------------------
#?----------------------------------------------------------------------------------------------------------------------------------------------------------------------
import 	assets.Dependencies 		as 		  dp
import  Lib.Data_Process            as        PP
#?----------------------------------------------------------------------------------------------------------------------------------------------------------------------

#! Call the Post-Processing class and point to the location of csv data
postProcessing 		=	PP.Processing()
sensorsPath			=	'Script/Data/Sensors_Errors/'
opampImpedancePath	=   'Script/Data/OpAmp_Impedance/'

#! random number generator range
randMin				=	-1e6
randMax				=	 1e6

#! Voltage Sensors models parameters
#?----------------------------------------------------------------------------------------------------------------------------------------------------------------------

randError	=	dp.random.SystemRandom().randint(randMin, randMax)
randNoise	=	dp.random.SystemRandom().randint(randMin, randMax)
sensor 		= 	sensorsPath + 'Si8932D_Error'
error		=	postProcessing.extractArrays(sensor)
#impedance  =   paramProcess.outputImpedanceMatching(opampImpedancePath, 'Ideal')

SI8932D				=	{																																	#*	generic SI8932D voltage sensor model
							'Config'				: 2																									,	#?	1->physical model | 2->small-signal model | 3->ideal model | 4->disable
							'Channel'				: 1																									,	#?	0->odd-odd or even-even | 1->even-odd or odd-even
							'Phase'					: 0																									,	#?	point in time of sampling trigger
                            'Zo'       :   {                                                                                                                #!  complex output impedance model
                                'Config'			:	3																								,	#? 	1->network 1 | 2->network 2 | 3->disable
                                'Network1'	:	{																											#*  parameters of network 1
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
							'BuffOpAmp'				:   {																									#!	buffer amplifier parameters
                                							'OpAmp'				: dp.copy.deepcopy(dp.OpAmps_Dicts.Ideal)								,	#?	opamp model parameters
															'Rf'				: 10e3																	,	#?	opamp feedback resistance
                                							'Av'				: 1																		,	#?	amplifier gain
														},
							'Divider'				:	{																									#!	voltage divider parameters
															'R1'				: 160e3*5																,	#?	HV resistance
															'R2'				: 3.79e3																,	#?	LV resistance
															'Cf'				: 820e-12+4.7e-9															#?	filter capacitance
														},
                            'Model' 				:	{																									#*	frequency behavior model as 3-stage Sallen-Key filter
									'OpAmp'										: dp.copy.deepcopy(dp.OpAmps_Dicts.Ideal)								,	#?	opamp model parameters
									'FirstStage'			:	{																							#!	first filter parameters
																'R1'			: 23.446																,	#?	first resistor
																'C1'			: 10e-9																	,	#?	first capacitor
																'R2'			: 23.446																,	#?	second resistor
																'C2'			: 20e-9																	,	#?	second capacitor
																'R3'			: 1e3																	,	#?	feedback gain resistance
																'Gain'			: 1.0																	,	#?	feedback gain
															},
									'SecondStage'			:	{																							#!	second filter parameters
																'R1'			: 0.0																	,	#?	first resistor
																'R2'			: 0.0																	,	#?	first capacitor
																'C1'			: 0.0																	,	#?	second resistor
																'C2'			: 0.0																	,	#?	second capacitor
																'R3'			: 1e3																	,	#?	feedback gain resistance
																'Gain'			: 1.0																	,	#?	feedback gain
															},
									'ThirdStage'			:	{																							#!	third filter parameters
																'R1'			: 0.0																	,	#?	first resistor
																'R2'			: 0.0																	,	#?	first capacitor
																'C1'			: 0.0																	,	#?	second resistor
																'C2'			: 0.0																	,	#?	second capacitor
																'R3'			: 1e3																	,	#?	feedback gain resistance
																'Gain'			: 1.0																	,	#?	feedback gain
															},
							},
							'LP_Filter'				:	{																									#!	external low-pass filter
															'R'					: 0																		,	#?	filter resistance
															'C'					: 0																			#?	filter capacitance
														},
							'Misc'					:	{																									#!	miscellaneous parameters
															'Vadc'				: 3.0																	,	#?	full-scale ADC voltage
															'Gain'				: 3.79/(3.79 + 160*5)													,	#?	measurement gain
															'Voffset'			: 0.0																	,	#?	measurement offset
															'Delay'		:	{																				#!	sensor delay paramteres
																'Config'		: 1																		,	#?	1->transport delay | 2->pade delay
                                                                'Order'			: 2																		,	#?	pade delay degree
                                                                'Td'			: 1e-6*0																,	#?	delay duration
															},
														},
							'Error'					:	{																									#*	error parameters
									'Vvec'										: error[0]																,	#?	voltage vector referred to ADC range
                                    'Polarity'									: 1																		,	#?	1->positive | 2->negative | 3->random
									'Seed'										: randError																,   #?	random polarity seed
									'SampleTime'								: 10e-6																	,	#?	random polarity sample time
									'Digital'	:	{																										#!	digital error parameters
															'Config'			: 2																		,	#?	1->enable | 2->disable
															'ErrVec'			: ((dp.np.array(error[1:5])).T).tolist()								,	#?	digital error vectors
															'ErrType'			: 1																			#?	1->uncalibrated rms error | 2->uncalibrated max error | 3->calibrated rms error | 4->calibrated max error
													},
                                    'Analog'	:	{																										#!	analog error parameters
															'Config'			: 2																		,	#?	1->enable | 2->disable
															'ErrVec'			: ((dp.np.array(error[5:9])).T).tolist()								,	#?	analog error vectors
															'ErrType'			: 1																			#?	1->uncalibrated rms error | 2->uncalibrated max error | 3->calibrated rms error | 4->calibrated max error
													},
														},
                            'Noise'					:	{																									#*	white noise parameters
									'Digital'	:	{																										#!	digital noise parameters
															'Config'			: 2																		,	#?	1->enable | 2->disable
                                                            'Sigma'				: 0.05																	,	#?	standard deveiation of the normally distributed noise
                                                            'Mean'				: 0																		,	#?	DC offset of the normally distributed noise
															'Seed'				: randNoise																,   #?	random noise seed
															'SampleTime'		: 100e-6																	#?	random noise sample time
													},
                                    'Analog'	:	{																										#!	analog noise parameters
															'Config'			: 2																		,	#?	1->enable | 2->disable
                                                            'Sigma'				: 0.05																	,	#?	standard deveiation of the normally distributed noise
                                                            'Mean'				: 0																		,	#?	DC offset of the normally distributed noise
															'Seed'				: randNoise																,   #?	random noise seed
															'SampleTime'		: 100e-6																	#?	random noise sample time
													},
														},
                            'CurrentLimit'			:	{																									#*	current limit
															'Config'			: 2																		,	#?	1->enable | 2->disable
															'Ts'				: 0 																	,	#?	sampling time between inductive & capacitive links
															'tau'				: 1e-9																	,	#?	first-order delay between inductive & capacitive links
                                                            'Rs'				: 0																		,	#?	source impedance of inductive link
															'Cs'				: 0																		,	#?	source capacitance of capacitive link
                                                            'UpLim'				: 5e-3																	,	#?	max current limit on capacitive link
                                                            'LoLim'				: -5e-3																	,	#?	min current limit on capacitive link
                                                            'Voffset'			: 0																			#?	voltage offset between inductive & capacitive links
							}
						}

#?----------------------------------------------------------------------------------------------------------------------------------------------------------------------

randError	=	dp.random.SystemRandom().randint(randMin, randMax)
randNoise	=	dp.random.SystemRandom().randint(randMin, randMax)
sensor 		= 	sensorsPath + 'BuffDivider_1_Error'
error		=	postProcessing.extractArrays(sensor)
#impedance  =   paramProcess.outputImpedanceMatching(opampImpedancePath, 'Ideal')

BuffDivider_1		=	{																																	#*	voltage divider model
							'Config'											: 2																		,	#?	1->physical model | 2->small-signal model | 3->ideal model | 4->disable
							'Channel'											: 1																		,	#?	0->odd-odd or even-even | 1->even-odd or odd-even
							'Phase'												: 0																		,	#?	point in time of sampling trigger
							'R1'												: 18e3																	,	#?	HV resistance
							'R2'												: 2e3																	,	#?	LV resistance
							'Cf'												: 0.0																	,	#?	filter capacitance
                            'Zo'       :   {                                                                                                                #!  complex output impedance model
                                'Config'			:	3																								,	#? 	1->network 1 | 2->network 2 | 3->disable
                                'Network1'	:	{																											#*  parameters of network 1
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
							'BuffOpAmp'				:   {																									#!	buffer amplifier parameters
                                							'OpAmp'				: dp.copy.deepcopy(dp.OpAmps_Dicts.TLV316)								,	#?	opamp model parameters
															'Rf'				: 10e3																	,	#?	opamp feedback resistance
                                							'Av'				: 1																		,	#?	amplifier gain
														},
							'LP_Filter'				:	{																									#!	external low-pass filter
															'R'					: 0																		,	#?	filter resistance
															'C'					: 0																			#?	filter capacitance
														},
							'Error'					:	{																									#*	error parameters
									'Vvec'										: error[0]																,	#?	voltage vector referred to ADC range
                                    'Polarity'									: 1																		,	#?	1->positive | 2->negative | 3->random
									'Seed'										: randError																,   #?	random polarity seed
									'SampleTime'								: 10e-6																	,	#?	random polarity sample time
									'Digital'	:	{																										#!	digital error parameters
															'Config'			: 2																		,	#?	1->enable | 2->disable
															'ErrVec'			: ((dp.np.array(error[1:5])).T).tolist()								,	#?	digital error vectors
															'ErrType'			: 1																			#?	1->uncalibrated rms error | 2->uncalibrated max error | 3->calibrated rms error | 4->calibrated max error
													},
                                    'Analog'	:	{																										#!	analog error parameters
															'Config'			: 2																		,	#?	1->enable | 2->disable
															'ErrVec'			: ((dp.np.array(error[5:9])).T).tolist()								,	#?	analog error vectors
															'ErrType'			: 1																			#?	1->uncalibrated rms error | 2->uncalibrated max error | 3->calibrated rms error | 4->calibrated max error
													},
														},
							'Noise'					:	{																									#*	white noise parameters
									'Digital'	:	{																										#!	digital noise parameters
															'Config'			: 2																		,	#?	1->enable | 2->disable
                                                            'Sigma'				: 0.05																	,	#?	standard deveiation of the normally distributed noise
                                                            'Mean'				: 0																		,	#?	DC offset of the normally distributed noise
															'Seed'				: randNoise																,   #?	random noise seed
															'SampleTime'		: 100e-6																	#?	random noise sample time
													},
                                    'Analog'	:	{																										#!	analog noise parameters
															'Config'			: 2																		,	#?	1->enable | 2->disable
                                                            'Sigma'				: 0.05																	,	#?	standard deveiation of the normally distributed noise
                                                            'Mean'				: 0																		,	#?	DC offset of the normally distributed noise
															'Seed'				: randNoise																,   #?	random noise seed
															'SampleTime'		: 100e-6																	#?	random noise sample time
													},
														},
                            'CurrentLimit'			:	{																									#*	current limit
															'Config'			: 2																		,	#?	1->enable | 2->disable
															'Ts'				: 0 																	,	#?	sampling time between inductive & capacitive links
															'tau'				: 1e-9																	,	#?	first-order delay between inductive & capacitive links
                                                            'Rs'				: 0																		,	#?	source impedance of inductive link
															'Cs'				: 0																		,	#?	source capacitance of capacitive link
                                                            'UpLim'				: 1.5e-3																,	#?	max current limit on capacitive link
                                                            'LoLim'				: -1.5e-3																,	#?	min current limit on capacitive link
                                                            'Voffset'			: 0																			#?	voltage offset between inductive & capacitive links
														},
							'Misc'					:	{																									#!	miscellaneous parameters
															'Vadc'				: 3.0																	,	#?	full-scale ADC voltage
															'Gain'				: 2/(2 + 18)															,	#?	measurement gain
															'Voffset'			: 0.0																	,	#?	measurement offset
															'Delay'		:	{																				#!	sensor delay paramteres
																'Config'		: 2																		,	#?	1->transport delay | 2->pade delay
                                                                'Order'			: 2																		,	#?	pade delay degree
                                                                'Td'			: 500e-9																,	#?	delay duration
															},
														}
						}

#?----------------------------------------------------------------------------------------------------------------------------------------------------------------------

randError	=	dp.random.SystemRandom().randint(randMin, randMax)
randNoise	=	dp.random.SystemRandom().randint(randMin, randMax)
sensor 		= 	sensorsPath + 'BuffDivider_2_Error'
error		=	postProcessing.extractArrays(sensor)
#impedance  =   paramProcess.outputImpedanceMatching(opampImpedancePath, 'Ideal')

BuffDivider_2		=	{																																	#*	voltage divider model
							'Config'											: 2																		,	#?	1->physical model | 2->small-signal model | 3->ideal model | 4->disable
							'Channel'											: 1																		,	#?	0->odd-odd or even-even | 1->even-odd or odd-even
							'Phase'												: 0																		,	#?	point in time of sampling trigger
							'R1'												: 9e3																	,	#?	HV resistance
							'R2'												: 1e3																	,	#?	LV resistance
							'Cf'												: 100e-12																,	#?	filter capacitance
                            'Zo'       :   {                                                                                                                #!  complex output impedance model
                                'Config'			:	3																								,	#? 	1->network 1 | 2->network 2 | 3->disable
                                'Network1'	:	{																											#*  parameters of network 1
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
							'BuffOpAmp'				:   {																									#!	buffer amplifier parameters
                                							'OpAmp'				: dp.copy.deepcopy(dp.OpAmps_Dicts.TLV316)								,	#?	opamp model parameters
															'Rf'				: 10e3																	,	#?	opamp feedback resistance
                                							'Av'				: 1																		,	#?	amplifier gain
														},
							'LP_Filter'				:	{																									#!	external low-pass filter
															'R'					: 200																	,	#?	filter resistance
															'C'					: 330e-12																	#?	filter capacitance
														},
							'Error'					:	{																									#*	error parameters
									'Vvec'										: error[0]																,	#?	voltage vector referred to ADC range
                                    'Polarity'									: 1																		,	#?	1->positive | 2->negative | 3->random
									'Seed'										: randError																,   #?	random polarity seed
									'SampleTime'								: 10e-6																	,	#?	random polarity sample time
									'Digital'	:	{																										#!	digital error parameters
															'Config'			: 2																		,	#?	1->enable | 2->disable
															'ErrVec'			: ((dp.np.array(error[1:5])).T).tolist()								,	#?	digital error vectors
															'ErrType'			: 1																			#?	1->uncalibrated rms error | 2->uncalibrated max error | 3->calibrated rms error | 4->calibrated max error
													},
                                    'Analog'	:	{																										#!	analog error parameters
															'Config'			: 2																		,	#?	1->enable | 2->disable
															'ErrVec'			: ((dp.np.array(error[5:9])).T).tolist()								,	#?	analog error vectors
															'ErrType'			: 1																			#?	1->uncalibrated rms error | 2->uncalibrated max error | 3->calibrated rms error | 4->calibrated max error
													},
														},
							'Noise'					:	{																									#*	white noise parameters
									'Digital'	:	{																										#!	digital noise parameters
															'Config'			: 2																		,	#?	1->enable | 2->disable
                                                            'Sigma'				: 0.05																	,	#?	standard deveiation of the normally distributed noise
                                                            'Mean'				: 0																		,	#?	DC offset of the normally distributed noise
															'Seed'				: randNoise																,   #?	random noise seed
															'SampleTime'		: 100e-6																	#?	random noise sample time
													},
                                    'Analog'	:	{																										#!	analog noise parameters
															'Config'			: 2																		,	#?	1->enable | 2->disable
                                                            'Sigma'				: 0.05																	,	#?	standard deveiation of the normally distributed noise
                                                            'Mean'				: 0																		,	#?	DC offset of the normally distributed noise
															'Seed'				: randNoise																,   #?	random noise seed
															'SampleTime'		: 100e-6																	#?	random noise sample time
													},
														},
                            'CurrentLimit'			:	{																									#*	current limit
															'Config'			: 2																		,	#?	1->enable | 2->disable
															'Ts'				: 0 																	,	#?	sampling time between inductive & capacitive links
															'tau'				: 0																		,	#?	first-order delay between inductive & capacitive links
                                                            'Rs'				: 0																		,	#?	source impedance of inductive link
															'Cs'				: 0																		,	#?	source capacitance of capacitive link
                                                            'UpLim'				: 1.5e-3																,	#?	max current limit on capacitive link
                                                            'LoLim'				: -1.5e-3																,	#?	min current limit on capacitive link
                                                            'Voffset'			: 0																			#?	voltage offset between inductive & capacitive links
														},
							'Misc'					:	{																									#!	miscellaneous parameters
															'Vadc'				: 3.0																	,	#?	full-scale ADC voltage
															'Gain'				: 1/(1 + 9)																,	#?	measurement gain
															'Voffset'			: 0.0																	,	#?	measurement offset
															'Delay'		:	{																				#!	sensor delay paramteres
																'Config'		: 2																		,	#?	1->transport delay | 2->pade delay
                                                                'Order'			: 2																		,	#?	pade delay degree
                                                                'Td'			: 1e-6																	,	#?	delay duration
															},
														}
						}

#?----------------------------------------------------------------------------------------------------------------------------------------------------------------------

randError	=	dp.random.SystemRandom().randint(randMin, randMax)
randNoise	=	dp.random.SystemRandom().randint(randMin, randMax)
sensor 		= 	sensorsPath + 'BuffDivider_3_Error'
error		=	postProcessing.extractArrays(sensor)
#impedance  =   paramProcess.outputImpedanceMatching(opampImpedancePath, 'Ideal')

BuffDivider_3		=	{																																	#*	voltage divider model
							'Config'											: 2																		,	#?	1->physical model | 2->small-signal model | 3->ideal model | 4->disable
							'Channel'											: 1																		,	#?	0->odd-odd or even-even | 1->even-odd or odd-even
							'Phase'												: 0																		,	#?	point in time of sampling trigger
							'R1'												: 56e3																	,	#?	HV resistance
							'R2'												: 4.7e3																	,	#?	LV resistance
							'Cf'												: 100e-12																,	#?	filter capacitance
                            'Zo'       :   {                                                                                                                #!  complex output impedance model
                                'Config'			:	3																								,	#? 	1->network 1 | 2->network 2 | 3->disable
                                'Network1'	:	{																											#*  parameters of network 1
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
							'BuffOpAmp'				:   {																									#!	buffer amplifier parameters
                                							'OpAmp'				: dp.copy.deepcopy(dp.OpAmps_Dicts.TLV316)								,	#?	opamp model parameters
															'Rf'				: 10e3																	,	#?	opamp feedback resistance
                                							'Av'				: 1																		,	#?	amplifier gain
														},
							'LP_Filter'				:	{																									#!	external low-pass filter
															'R'					: 0																		,	#?	filter resistance
															'C'					: 0																			#?	filter capacitance
														},
							'Error'					:	{																									#*	error parameters
									'Vvec'										: error[0]																,	#?	voltage vector referred to ADC range
                                    'Polarity'									: 1																		,	#?	1->positive | 2->negative | 3->random
									'Seed'										: randError																,   #?	random polarity seed
									'SampleTime'								: 10e-6																	,	#?	random polarity sample time
									'Digital'	:	{																										#!	digital error parameters
															'Config'			: 2																		,	#?	1->enable | 2->disable
															'ErrVec'			: ((dp.np.array(error[1:5])).T).tolist()								,	#?	digital error vectors
															'ErrType'			: 1																			#?	1->uncalibrated rms error | 2->uncalibrated max error | 3->calibrated rms error | 4->calibrated max error
													},
                                    'Analog'	:	{																										#!	analog error parameters
															'Config'			: 2																		,	#?	1->enable | 2->disable
															'ErrVec'			: ((dp.np.array(error[5:9])).T).tolist()								,	#?	analog error vectors
															'ErrType'			: 1																			#?	1->uncalibrated rms error | 2->uncalibrated max error | 3->calibrated rms error | 4->calibrated max error
													},
														},
							'Noise'					:	{																									#*	white noise parameters
									'Digital'	:	{																										#!	digital noise parameters
															'Config'			: 2																		,	#?	1->enable | 2->disable
                                                            'Sigma'				: 0.05																	,	#?	standard deveiation of the normally distributed noise
                                                            'Mean'				: 0																		,	#?	DC offset of the normally distributed noise
															'Seed'				: randNoise																,   #?	random noise seed
															'SampleTime'		: 100e-6																	#?	random noise sample time
													},
                                    'Analog'	:	{																										#!	analog noise parameters
															'Config'			: 2																		,	#?	1->enable | 2->disable
                                                            'Sigma'				: 0.05																	,	#?	standard deveiation of the normally distributed noise
                                                            'Mean'				: 0																		,	#?	DC offset of the normally distributed noise
															'Seed'				: randNoise																,   #?	random noise seed
															'SampleTime'		: 100e-6																	#?	random noise sample time
													},
														},
                            'CurrentLimit'			:	{																									#*	current limit
															'Config'			: 2																		,	#?	1->enable | 2->disable
															'Ts'				: 0 																	,	#?	sampling time between inductive & capacitive links
															'tau'				: 1e-9																	,	#?	first-order delay between inductive & capacitive links
                                                            'Rs'				: 0																		,	#?	source impedance of inductive link
															'Cs'				: 0																		,	#?	source capacitance of capacitive link
                                                            'UpLim'				: 1.5e-3																,	#?	max current limit on capacitive link
                                                            'LoLim'				: -1.5e-3																,	#?	min current limit on capacitive link
                                                            'Voffset'			: 0																			#?	voltage offset between inductive & capacitive links
														},
							'Misc'					:	{																									#!	miscellaneous parameters
															'Vadc'				: 3.0																	,	#?	full-scale ADC voltage
															'Gain'				: 4.7/(4.7 + 56)														,	#?	measurement gain
															'Voffset'			: 0.0																	,	#?	measurement offset
															'Delay'		:	{																				#!	sensor delay paramteres
																'Config'		: 1																		,	#?	1->transport delay | 2->pade delay
                                                                'Order'			: 2																		,	#?	pade delay degree
                                                                'Td'			: 100e-9*0																,	#?	delay duration
															},
														}
						}

#?----------------------------------------------------------------------------------------------------------------------------------------------------------------------

randError	=	dp.random.SystemRandom().randint(randMin, randMax)
randNoise	=	dp.random.SystemRandom().randint(randMin, randMax)
sensor 		= 	sensorsPath + 'BuffDivider_4_Error'
error		=	postProcessing.extractArrays(sensor)
#impedance  =   paramProcess.outputImpedanceMatching(opampImpedancePath, 'Ideal')

BuffDivider_4		=	{																																	#*	voltage divider model
							'Config'											: 2																		,	#?	1->physical model | 2->small-signal model | 3->ideal model | 4->disable
							'Channel'											: 1																		,	#?	0->odd-odd or even-even | 1->even-odd or odd-even
							'Phase'												: 0																		,	#?	point in time of sampling trigger
							'R1'												: 141e3																	,	#?	HV resistance
							'R2'												: 3.0e3																	,	#?	LV resistance
							'Cf'												: 100e-12																,	#?	filter capacitance
                            'Zo'       :   {                                                                                                                #!  complex output impedance model
                                'Config'			:	3																								,	#? 	1->network 1 | 2->network 2 | 3->disable
                                'Network1'	:	{																											#*  parameters of network 1
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
							'BuffOpAmp'				:   {																									#!	buffer amplifier parameters
                                							'OpAmp'				: dp.copy.deepcopy(dp.OpAmps_Dicts.TLV906)								,	#?	opamp model parameters
															'Rf'				: 10e3																	,	#?	opamp feedback resistance
                                							'Av'				: 1																		,	#?	amplifier gain
														},
							'LP_Filter'				:	{																									#!	external low-pass filter
															'R'					: 0																		,	#?	filter resistance
															'C'					: 0																			#?	filter capacitance
														},
							'Error'					:	{																									#*	error parameters
									'Vvec'										: error[0]																,	#?	voltage vector referred to ADC range
                                    'Polarity'									: 1																		,	#?	1->positive | 2->negative | 3->random
									'Seed'										: randError																,   #?	random polarity seed
									'SampleTime'								: 10e-6																	,	#?	random polarity sample time
									'Digital'	:	{																										#!	digital error parameters
															'Config'			: 2																		,	#?	1->enable | 2->disable
															'ErrVec'			: ((dp.np.array(error[1:5])).T).tolist()								,	#?	digital error vectors
															'ErrType'			: 1																			#?	1->uncalibrated rms error | 2->uncalibrated max error | 3->calibrated rms error | 4->calibrated max error
													},
                                    'Analog'	:	{																										#!	analog error parameters
															'Config'			: 2																		,	#?	1->enable | 2->disable
															'ErrVec'			: ((dp.np.array(error[5:9])).T).tolist()								,	#?	analog error vectors
															'ErrType'			: 1																			#?	1->uncalibrated rms error | 2->uncalibrated max error | 3->calibrated rms error | 4->calibrated max error
													},
														},
							'Noise'					:	{																									#*	white noise parameters
									'Digital'	:	{																										#!	digital noise parameters
															'Config'			: 2																		,	#?	1->enable | 2->disable
                                                            'Sigma'				: 0.05																	,	#?	standard deveiation of the normally distributed noise
                                                            'Mean'				: 0																		,	#?	DC offset of the normally distributed noise
															'Seed'				: randNoise																,   #?	random noise seed
															'SampleTime'		: 100e-6																	#?	random noise sample time
													},
                                    'Analog'	:	{																										#!	analog noise parameters
															'Config'			: 2																		,	#?	1->enable | 2->disable
                                                            'Sigma'				: 0.05																	,	#?	standard deveiation of the normally distributed noise
                                                            'Mean'				: 0																		,	#?	DC offset of the normally distributed noise
															'Seed'				: randNoise																,   #?	random noise seed
															'SampleTime'		: 100e-6																	#?	random noise sample time
													},
														},
                            'CurrentLimit'			:	{																									#*	current limit
															'Config'			: 2																		,	#?	1->enable | 2->disable
															'Ts'				: 0 																	,	#?	sampling time between inductive & capacitive links
															'tau'				: 1e-9																	,	#?	first-order delay between inductive & capacitive links
                                                            'Rs'				: 0																		,	#?	source impedance of inductive link
															'Cs'				: 0																		,	#?	source capacitance of capacitive link
                                                            'UpLim'				: 1.5e-3																,	#?	max current limit on capacitive link
                                                            'LoLim'				: -1.5e-3																,	#?	min current limit on capacitive link
                                                            'Voffset'			: 0																			#?	voltage offset between inductive & capacitive links
														},
							'Misc'					:	{																									#!	miscellaneous parameters
															'Vadc'				: 3.0																	,	#?	full-scale ADC voltage
															'Gain'				: 3.0/(3.0 + 141)														,	#?	measurement gain
															'Voffset'			: 0.0																	,	#?	measurement offset
															'Delay'		:	{																				#!	sensor delay paramteres
																'Config'		: 1																		,	#?	1->transport delay | 2->pade delay
                                                                'Order'			: 2																		,	#?	pade delay degree
                                                                'Td'			: 100e-9*0																,	#?	delay duration
															},
														}
						}

#! Current Sensors models parameters
#?----------------------------------------------------------------------------------------------------------------------------------------------------------------------

randError	=	dp.random.SystemRandom().randint(randMin, randMax)
randNoise	=	dp.random.SystemRandom().randint(randMin, randMax)
sensor 		= 	sensorsPath + 'INA240A2_Error'
error		=	postProcessing.extractArrays(sensor)
#impedance  =   paramProcess.outputImpedanceMatching(opampImpedancePath, 'INA240A2')

INA240A2			=	{																																	#*	generic INA240A2 current sensor model
							'Config'				: 2																									,	#?	1->physical model | 2->small-signal model | 3->ideal model | 4->disable
							'Channel'				: 1																									,	#?	0->odd-odd or even-even | 1->even-odd or odd-even
							'Phase'					: 0																									,	#?	point in time of sampling trigger
							'R'						: 100e-6																							,	#?	shunt or internal sensor resistance
                            'L'						: 600e-12*0																							,	#?	shunt or internal parasitic resistance
                            'Rth'					: [4.260,6.212,6.000,5.222,13.956]																	,	#?	sensor themral resistance vector
                            'Cth'					: [1.504,0.350,15.102,127.085,40.961]																,	#?	sensor themral capacitance vector
                            'Zo'       :   {                                                                                                                #!  complex output impedance model
                                'Config'			:	3																								,	#? 	1->network 1 | 2->network 2 | 3->disable
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
                                'Network2'	:	{																											#*  parameters of network 2
									'Rs'                :   2.97835145e-05                                                                              ,   #?  serial resistance
                                	'Ls'                :   0                                                                                           ,   #?  serial inductance
                                	'Rp1'               :   0                                                                                           ,   #?  parallel resistance 1
                                	'Lp1'               :   4.10979565e-06                                                                              ,   #?  parallel inductance
                                	'Rp2'               :   1.01481641e+01                                                                              ,   #?  parallel resistance 2
                                	'Cp1'               :   2.00298132e-06                                                                              ,   #?  parallel capacitance
								},
                            },
							'DiffOpAmp'				:   {																									#!	differential amplifier parameters
                                							'OpAmp'				: dp.copy.deepcopy(dp.OpAmps_Dicts.Ideal)								,	#?	opamp model parameters
															'Rf'				: 10e3																	,	#?	opamp feedback resistance
                                							'R1'				: 10e3																	,	#?	opamp input resistance
														},
                            'Model' 				:	{																									#*	frequency behavior model as 3-stage Sallen-Key filter
									'OpAmp'										: dp.copy.deepcopy(dp.OpAmps_Dicts.Ideal)								,	#?	opamp model parameters
									'FirstStage'			:	{																							#!	first filter parameters
																'R1'			: 100.0																	,	#?	first resistor
																'C1'			: 4.2e-9																,	#?	first capacitor
																'R2'			: 0.0																	,	#?	second resistor
																'C2'			: 0.0																	,	#?	second capacitor
																'R3'			: 1e3																	,	#?	feedback gain resistance
																'Gain'			: 50																	,	#?	feedback gain
															},
									'SecondStage'			:	{																							#!	second filter parameters
																'R1'			: 0.0																	,	#?	first resistor
																'R2'			: 0.0																	,	#?	first capacitor
																'C1'			: 0.0																	,	#?	second resistor
																'C2'			: 0.0																	,	#?	second capacitor
																'R3'			: 1e3																	,	#?	feedback gain resistance
																'Gain'			: 1.0																	,	#?	feedback gain
															},
									'ThirdStage'			:	{																							#!	third filter parameters
																'R1'			: 0.0																	,	#?	first resistor
																'R2'			: 0.0																	,	#?	first capacitor
																'C1'			: 0.0																	,	#?	second resistor
																'C2'			: 0.0																	,	#?	second capacitor
																'R3'			: 1e3																	,	#?	feedback gain resistance
																'Gain'			: 1.0																	,	#?	feedback gain
															},
							},
							'LP_Filter'				:	{																									#!	external low-pass filter
															'R'					: 0																		,	#?	filter resistance
															'C'					: 1e-9																		#?	filter capacitance
														},
							'Misc'					:	{																									#!	miscellaneous parameters
															'Vadc'				: 3.0																	,	#?	full-scale ADC voltage
															'Gain'				: 100e-6*50																,	#?	measurement gain
															'Voffset'			: 1.5																	,	#?	measurement offset
															'Delay'		:	{																				#!	sensor delay paramteres
																'Config'		: 1																		,	#?	1->transport delay | 2->pade delay
                                                                'Order'			: 2																		,	#?	pade delay degree
                                                                'Td'			: 511e-9*0																,	#?	delay duration
															},
														},
							'Error'					:	{																									#*	error parameters
									'Vvec'										: error[0]																,	#?	voltage vector referred to ADC range
                                    'Polarity'									: 1																		,	#?	1->positive | 2->negative | 3->random
									'Seed'										: randError																,   #?	random polarity seed
									'SampleTime'								: 10e-6																	,	#?	random polarity sample time
									'Digital'	:	{																										#!	digital error parameters
															'Config'			: 2																		,	#?	1->enable | 2->disable
															'ErrVec'			: ((dp.np.array(error[1:5])).T).tolist()								,	#?	digital error vectors
															'ErrType'			: 1																			#?	1->uncalibrated rms error | 2->uncalibrated max error | 3->calibrated rms error | 4->calibrated max error
													},
                                    'Analog'	:	{																										#!	analog error parameters
															'Config'			: 2																		,	#?	1->enable | 2->disable
															'ErrVec'			: ((dp.np.array(error[5:9])).T).tolist()								,	#?	analog error vectors
															'ErrType'			: 1																			#?	1->uncalibrated rms error | 2->uncalibrated max error | 3->calibrated rms error | 4->calibrated max error
													},
														},
							'Noise'					:	{																									#*	white noise parameters
									'Digital'	:	{																										#!	digital noise parameters
															'Config'			: 2																		,	#?	1->enable | 2->disable
                                                            'Sigma'				: 0.05																	,	#?	standard deveiation of the normally distributed noise
                                                            'Mean'				: 0																		,	#?	DC offset of the normally distributed noise
															'Seed'				: randNoise																,   #?	random noise seed
															'SampleTime'		: 100e-6																	#?	random noise sample time
													},
                                    'Analog'	:	{																										#!	analog noise parameters
															'Config'			: 2																		,	#?	1->enable | 2->disable
                                                            'Sigma'				: 0.05																	,	#?	standard deveiation of the normally distributed noise
                                                            'Mean'				: 0																		,	#?	DC offset of the normally distributed noise
															'Seed'				: randNoise																,   #?	random noise seed
															'SampleTime'		: 100e-6																	#?	random noise sample time
													},
														},
							'CurrentLimit'			:	{																									#*	current limit
															'Config'			: 2																		,	#?	1->enable | 2->disable
															'Ts'				: 0 																	,	#?	sampling time between inductive & capacitive links
															'tau'				: 0																		,	#?	first-order delay between inductive & capacitive links
                                                            'Rs'				: 0																		,	#?	source impedance of inductive link
															'Cs'				: 0																		,	#?	source capacitance of capacitive link
                                                            'UpLim'				: 1.5e-3																,	#?	max current limit on capacitive link
                                                            'LoLim'				: -1.5e-3																,	#?	min current limit on capacitive link
                                                            'Voffset'			: 1.5																		#?	voltage offset between inductive & capacitive links
														}
						}

#?----------------------------------------------------------------------------------------------------------------------------------------------------------------------

randError	=	dp.random.SystemRandom().randint(randMin, randMax)
randNoise	=	dp.random.SystemRandom().randint(randMin, randMax)
sensor 		= 	sensorsPath + 'INA240A1_Error'
error		=	postProcessing.extractArrays(sensor)
#impedance  =   paramProcess.outputImpedanceMatching(opampImpedancePath, 'INA240A1')

INA240A1			=	{																																	#*	generic INA240A1 current sensor model
							'Config'				: 2																									,	#?	1->physical model | 2->small-signal model | 3->ideal model | 4->disable
							'Channel'				: 1																									,	#?	0->odd-odd or even-even | 1->even-odd or odd-even
							'Phase'					: 0																									,	#?	point in time of sampling trigger
							'R'						: 300e-6																							,	#?	shunt or inline sensor resistance
                            'L'						: 600e-12*0																							,	#?	shunt or internal parasitic resistance
                            'Rth'					: [4.260,6.212,6.000,5.222,13.956]																	,	#?	sensor themral resistance vector
                            'Cth'					: [1.504,0.350,15.102,127.085,40.961]																,	#?	sensor themral capacitance vector
                            'Zo'       :   {                                                                                                                #!  complex output impedance model
                                'Config'			:	3																								,	#? 	1->network 1 | 2->network 2 | 3->disable
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
                                'Network2'	:	{																											#*  parameters of network 2
									'Rs'                :   2.97835145e-05                                                                              ,   #?  serial resistance
                                	'Ls'                :   0                                                                                           ,   #?  serial inductance
                                	'Rp1'               :   0                                                                                           ,   #?  parallel resistance 1
                                	'Lp1'               :   4.10979565e-06                                                                              ,   #?  parallel inductance
                                	'Rp2'               :   1.01481641e+01                                                                              ,   #?  parallel resistance 2
                                	'Cp1'               :   2.00298132e-06                                                                              ,   #?  parallel capacitance
								},
                            },
							'DiffOpAmp'				:   {																									#!	differential amplifier parameters
                                							'OpAmp'				: dp.copy.deepcopy(dp.OpAmps_Dicts.Ideal)								,	#?	opamp model parameters
															'Rf'				: 10e3																	,	#?	opamp feedback resistance
                                							'R1'				: 10e3																	,	#?	opamp input resistance
														},
                            'Model' 				:	{																									#*	frequency behavior model as 3-stage Sallen-Key filter
									'OpAmp'										: dp.copy.deepcopy(dp.OpAmps_Dicts.Ideal)								,	#?	opamp model parameters
									'FirstStage'			:	{																							#!	first filter parameters
																'R1'			: 100.0																	,	#?	first resistor
																'C1'			: 4.2e-9																,	#?	first capacitor
																'R2'			: 0.0																	,	#?	second resistor
																'C2'			: 0.0																	,	#?	second capacitor
																'R3'			: 1e3																	,	#?	feedback gain resistance
																'Gain'			: 20																	,	#?	feedback gain
															},
									'SecondStage'			:	{																							#!	second filter parameters
																'R1'			: 0.0																	,	#?	first resistor
																'R2'			: 0.0																	,	#?	first capacitor
																'C1'			: 0.0																	,	#?	second resistor
																'C2'			: 0.0																	,	#?	second capacitor
																'R3'			: 1e3																	,	#?	feedback gain resistance
																'Gain'			: 1.0																	,	#?	feedback gain
															},
									'ThirdStage'			:	{																							#!	third filter parameters
																'R1'			: 0.0																	,	#?	first resistor
																'R2'			: 0.0																	,	#?	first capacitor
																'C1'			: 0.0																	,	#?	second resistor
																'C2'			: 0.0																	,	#?	second capacitor
																'R3'			: 1e3																	,	#?	feedback gain resistance
																'Gain'			: 1.0																	,	#?	feedback gain
															},
							},
							'LP_Filter'				:	{																									#!	external low-pass filter
															'R'					: 0																		,	#?	filter resistance
															'C'					: 1e-9																		#?	filter capacitance
														},
							'Misc'					:	{																									#!	miscellaneous parameters
															'Vadc'				: 3.0																	,	#?	full-scale ADC voltage
															'Gain'				: 300e-6*20																,	#?	measurement gain
															'Voffset'			: 1.5																	,	#?	measurement offset
															'Delay'		:	{																				#!	sensor delay paramteres
																'Config'		: 2																		,	#?	1->transport delay | 2->pade delay
                                                                'Order'			: 2																		,	#?	pade delay degree
                                                                'Td'			: 511e-9																,	#?	delay duration
															},
														},
							'Error'					:	{																									#*	error parameters
									'Vvec'										: error[0]																,	#?	voltage vector referred to ADC range
                                    'Polarity'									: 1																		,	#?	1->positive | 2->negative | 3->random
									'Seed'										: randError																,   #?	random polarity seed
									'SampleTime'								: 10e-6																	,	#?	random polarity sample time
									'Digital'	:	{																										#!	digital error parameters
															'Config'			: 2																		,	#?	1->enable | 2->disable
															'ErrVec'			: ((dp.np.array(error[1:5])).T).tolist()								,	#?	digital error vectors
															'ErrType'			: 1																			#?	1->uncalibrated rms error | 2->uncalibrated max error | 3->calibrated rms error | 4->calibrated max error
													},
                                    'Analog'	:	{																										#!	analog error parameters
															'Config'			: 2																		,	#?	1->enable | 2->disable
															'ErrVec'			: ((dp.np.array(error[5:9])).T).tolist()								,	#?	analog error vectors
															'ErrType'			: 1																			#?	1->uncalibrated rms error | 2->uncalibrated max error | 3->calibrated rms error | 4->calibrated max error
													},
														},
							'Noise'					:	{																									#*	white noise parameters
									'Digital'	:	{																										#!	digital noise parameters
															'Config'			: 2																		,	#?	1->enable | 2->disable
                                                            'Sigma'				: 0.05																	,	#?	standard deveiation of the normally distributed noise
                                                            'Mean'				: 0																		,	#?	DC offset of the normally distributed noise
															'Seed'				: randNoise																,   #?	random noise seed
															'SampleTime'		: 100e-6																	#?	random noise sample time
													},
                                    'Analog'	:	{																										#!	analog noise parameters
															'Config'			: 2																		,	#?	1->enable | 2->disable
                                                            'Sigma'				: 0.05																	,	#?	standard deveiation of the normally distributed noise
                                                            'Mean'				: 0																		,	#?	DC offset of the normally distributed noise
															'Seed'				: randNoise																,   #?	random noise seed
															'SampleTime'		: 100e-6																	#?	random noise sample time
													},
														},
                            'CurrentLimit'			:	{																									#*	current limit
															'Config'			: 2																		,	#?	1->enable | 2->disable
															'Ts'				: 0 																	,	#?	sampling time between inductive & capacitive links
															'tau'				: 0																		,	#?	first-order delay between inductive & capacitive links
                                                            'Rs'				: 0																		,	#?	source impedance of inductive link
															'Cs'				: 0																		,	#?	source capacitance of capacitive link
                                                            'UpLim'				: 1.5e-3																,	#?	max current limit on capacitive link
                                                            'LoLim'				: -1.5e-3																,	#?	min current limit on capacitive link
                                                            'Voffset'			: 1.5																		#?	voltage offset between inductive & capacitive links
														}
						}

#?----------------------------------------------------------------------------------------------------------------------------------------------------------------------

randError	=	dp.random.SystemRandom().randint(randMin, randMax)
randNoise	=	dp.random.SystemRandom().randint(randMin, randMax)
sensor 		= 	sensorsPath + 'AD8411A_Error'
error		=	postProcessing.extractArrays(sensor)
#impedance  =   paramProcess.outputImpedanceMatching(opampImpedancePath, 'AD8411A')

AD8411A			=	{																																		#*	generic AD8411A current sensor model
							'Config'				: 2																									,	#?	1->physical model | 2->small-signal model | 3->ideal model | 4->disable
							'Channel'				: 1																									,	#?	0->odd-odd or even-even | 1->even-odd or odd-even
							'Phase'					: 0																									,	#?	point in time of sampling trigger
							'R'						: 100e-6																							,	#?	shunt or internal sensor resistance
                            'L'						: 600e-12*0																							,	#?	shunt or internal parasitic resistance
                            'Rth'					: [4.260,6.212,6.000,5.222,13.956]																	,	#?	sensor themral resistance vector
                            'Cth'					: [1.504,0.350,15.102,127.085,40.961]																,	#?	sensor themral capacitance vector
                            'Zo'       :   {                                                                                                                #!  complex output impedance model
                                'Config'			:	3																								,	#? 	1->network 1 | 2->network 2 | 3->disable
                                'Network1'	:	{																											#*  parameters of network 1
									'R1'                :   0                                                                                           ,   #?  first resistance
                                    'RL1'               :   0                                                                                           ,   #?  series resistance of first inductor
                                    'L1'                :   0                                                                                           ,   #?  first inductance
                                    'R2'                :   0                                                                                           ,   #?  second resistance
                                    'RL2'               :   0                                                                                           ,   #?  series resistance of second inductor
                                    'L2'                :   0                                                                                           ,   #?  first inductance
                                    'R3'                :   0                                                                                           ,   #?  third resistance
                                    'R4'                :   0.2                                                                                         ,   #?  fourth resistance
                                    'C1'                :   0                                                                                           ,   #?  first capacitance
								},
                                'Network2'  :   {                                                                                                           #*  parameters of network 2
                                    'Rs'                :   0.2                                                                                         ,   #?  serial resistance
                                    'Ls'                :   0                                                                                           ,   #?  serial inductance
                                    'Rp1'               :   0                                                                                           ,   #?  parallel resistance 1
                                    'Lp1'               :   0                                                                                           ,   #?  parallel inductance
                                    'Rp2'               :   0                                                                                           ,   #?  parallel resistance 2
                                    'Cp1'               :   0                                                                                           ,   #?  parallel capacitance
                                    },
                            },
							'DiffOpAmp'				:   {																									#!	differential amplifier parameters
                                							'OpAmp'				: dp.copy.deepcopy(dp.OpAmps_Dicts.Ideal)								,	#?	opamp model parameters
															'Rf'				: 10e3																	,	#?	opamp feedback resistance
                                							'R1'				: 10e3																	,	#?	opamp input resistance
														},
                            'Model' 				:	{																									#*	frequency behavior model as 3-stage Sallen-Key filter
									'OpAmp'										: dp.copy.deepcopy(dp.OpAmps_Dicts.Ideal)								,	#?	opamp model parameters
									'FirstStage'			:	{																							#!	first filter parameters
																'R1'			: 0.0																	,	#?	first resistor
																'C1'			: 0.0																	,	#?	first capacitor
																'R2'			: 0.0																	,	#?	second resistor
																'C2'			: 0.0																	,	#?	second capacitor
																'R3'			: 1e3																	,	#?	feedback gain resistance
																'Gain'			: 50																	,	#?	feedback gain
															},
									'SecondStage'			:	{																							#!	second filter parameters
																'R1'			: 0.0																	,	#?	first resistor
																'R2'			: 0.0																	,	#?	first capacitor
																'C1'			: 0.0																	,	#?	second resistor
																'C2'			: 0.0																	,	#?	second capacitor
																'R3'			: 1e3																	,	#?	feedback gain resistance
																'Gain'			: 1.0																	,	#?	feedback gain
															},
									'ThirdStage'			:	{																							#!	third filter parameters
																'R1'			: 0.0																	,	#?	first resistor
																'R2'			: 0.0																	,	#?	first capacitor
																'C1'			: 0.0																	,	#?	second resistor
																'C2'			: 0.0																	,	#?	second capacitor
																'R3'			: 1e3																	,	#?	feedback gain resistance
																'Gain'			: 1.0																	,	#?	feedback gain
															},
							},
							'LP_Filter'				:	{																									#!	external low-pass filter
															'R'					: 0																		,	#?	filter resistance
															'C'					: 0																			#?	filter capacitance
														},
							'Misc'					:	{																									#!	miscellaneous parameters
															'Vadc'				: 3.0																	,	#?	full-scale ADC voltage
															'Gain'				: 100e-6*50																,	#?	measurement gain
															'Voffset'			: 1.5																	,	#?	measurement offset
															'Delay'		:	{																				#!	sensor delay paramteres
																'Config'		: 1																		,	#?	1->transport delay | 2->pade delay
                                                                'Order'			: 2																		,	#?	pade delay degree
                                                                'Td'			: 0																		,	#?	delay duration
															},
														},
							'Error'					:	{																									#*	error parameters
									'Vvec'										: error[0]																,	#?	voltage vector referred to ADC range
                                    'Polarity'									: 1																		,	#?	1->positive | 2->negative | 3->random
									'Seed'										: randError																,   #?	random polarity seed
									'SampleTime'								: 10e-6																	,	#?	random polarity sample time
									'Digital'	:	{																										#!	digital error parameters
															'Config'			: 2																		,	#?	1->enable | 2->disable
															'ErrVec'			: ((dp.np.array(error[1:5])).T).tolist()								,	#?	digital error vectors
															'ErrType'			: 1																			#?	1->uncalibrated rms error | 2->uncalibrated max error | 3->calibrated rms error | 4->calibrated max error
													},
                                    'Analog'	:	{																										#!	analog error parameters
															'Config'			: 2																		,	#?	1->enable | 2->disable
															'ErrVec'			: ((dp.np.array(error[5:9])).T).tolist()								,	#?	analog error vectors
															'ErrType'			: 1																			#?	1->uncalibrated rms error | 2->uncalibrated max error | 3->calibrated rms error | 4->calibrated max error
													},
														},
							'Noise'					:	{																									#*	white noise parameters
									'Digital'	:	{																										#!	digital noise parameters
															'Config'			: 2																		,	#?	1->enable | 2->disable
                                                            'Sigma'				: 0.05																	,	#?	standard deveiation of the normally distributed noise
                                                            'Mean'				: 0																		,	#?	DC offset of the normally distributed noise
															'Seed'				: randNoise																,   #?	random noise seed
															'SampleTime'		: 100e-6																	#?	random noise sample time
													},
                                    'Analog'	:	{																										#!	analog noise parameters
															'Config'			: 2																		,	#?	1->enable | 2->disable
                                                            'Sigma'				: 0.05																	,	#?	standard deveiation of the normally distributed noise
                                                            'Mean'				: 0																		,	#?	DC offset of the normally distributed noise
															'Seed'				: randNoise																,   #?	random noise seed
															'SampleTime'		: 100e-6																	#?	random noise sample time
													},
														},
							'CurrentLimit'			:	{																									#*	current limit
															'Config'			: 2																		,	#?	1->enable | 2->disable
															'Ts'				: 0 																	,	#?	sampling time between inductive & capacitive links
															'tau'				: 0																		,	#?	first-order delay between inductive & capacitive links
                                                            'Rs'				: 0																		,	#?	source impedance of inductive link
															'Cs'				: 0																		,	#?	source capacitance of capacitive link
                                                            'UpLim'				: 47e-3																	,	#?	max current limit on capacitive link
                                                            'LoLim'				: -47e-3																,	#?	min current limit on capacitive link
                                                            'Voffset'			: 1.5																		#?	voltage offset between inductive & capacitive links
														}
						}

#?----------------------------------------------------------------------------------------------------------------------------------------------------------------------

randError	=	dp.random.SystemRandom().randint(randMin, randMax)
randNoise	=	dp.random.SystemRandom().randint(randMin, randMax)
sensor 		= 	sensorsPath + 'INA296A3_Error'
error		=	postProcessing.extractArrays(sensor)
#impedance  =   paramProcess.outputImpedanceMatching(opampImpedancePath, 'INA296A3')

INA296A3			=	{																																	#*	generic INA296A3 current sensor model
							'Config'				: 2																									,	#?	1->physical model | 2->small-signal model | 3->ideal model | 4->disable
							'Channel'				: 1																									,	#?	0->odd-odd or even-even | 1->even-odd or odd-even
							'Phase'					: 0																									,	#?	point in time of sampling trigger
							'R'						: 100e-6																							,	#?	shunt or internal sensor resistance
                            'L'						: 600e-12*0																							,	#?	shunt or internal parasitic resistance
                            'Rth'					: [4.260,6.212,6.000,5.222,13.956]																	,	#?	sensor themral resistance vector
                            'Cth'					: [1.504,0.350,15.102,127.085,40.961]																,	#?	sensor themral capacitance vector
                            'Zo'       :   {                                                                                                                #!  complex output impedance model
                                'Config'			:	3																								,	#? 	1->network 1 | 2->network 2 | 3->disable
                                'Network1'	:	{																											#*  parameters of network 1
									'R1'                :   0                                                                                           ,   #?  first resistance
                                    'RL1'               :   0                                                                                           ,   #?  series resistance of first inductor
                                    'L1'                :   0                                                                                           ,   #?  first inductance
                                    'R2'                :   0                                                                                           ,   #?  second resistance
                                    'RL2'               :   0                                                                                           ,   #?  series resistance of second inductor
                                    'L2'                :   0                                                                                           ,   #?  first inductance
                                    'R3'                :   0                                                                                           ,   #?  third resistance
                                    'R4'                :   0                                                                                         	,   #?  fourth resistance
                                    'C1'                :   0                                                                                           ,   #?  first capacitance
								},
                                'Network2'	:	{                                																			#*  parameters of network 2
									'Rs'                :   8.46268943e-02                                                                              ,   #?  serial resistance
                                	'Ls'                :   2.34000736e-10                                                                              ,   #?  serial inductance
                                	'Rp1'               :   0                                                                                           ,   #?  parallel resistance 1
                                	'Lp1'               :   5.91712414e-06                                                                              ,   #?  parallel inductance
                                	'Rp2'               :   1.55096330e+02                                                                              ,   #?  parallel resistance 2
                                	'Cp1'               :   9.11206136e-10                                                                              ,   #?  parallel capacitance
								},
                            },
							'DiffOpAmp'				:   {																									#!	differential amplifier parameters
                                							'OpAmp'				: dp.copy.deepcopy(dp.OpAmps_Dicts.Ideal)								,	#?	opamp model parameters
															'Rf'				: 10e3																	,	#?	opamp feedback resistance
                                							'R1'				: 10e3																	,	#?	opamp input resistance
														},
                            'Model' 				:	{																									#*	frequency behavior model as 3-stage Sallen-Key filter
									'OpAmp'										: dp.copy.deepcopy(dp.OpAmps_Dicts.Ideal)								,	#?	opamp model parameters
									'FirstStage'			:	{																							#!	first filter parameters
																'R1'			: 1																		,	#?	first resistor
																'C1'			: 0																		,	#?	first capacitor
																'R2'			: 0.0																	,	#?	second resistor
																'C2'			: 0.0																	,	#?	second capacitor
																'R3'			: 1e3																	,	#?	feedback gain resistance
																'Gain'			: 50																	,	#?	feedback gain
															},
									'SecondStage'			:	{																							#!	second filter parameters
																'R1'			: 0.0																	,	#?	first resistor
																'R2'			: 0.0																	,	#?	first capacitor
																'C1'			: 0.0																	,	#?	second resistor
																'C2'			: 0.0																	,	#?	second capacitor
																'R3'			: 1e3																	,	#?	feedback gain resistance
																'Gain'			: 1.0																	,	#?	feedback gain
															},
									'ThirdStage'			:	{																							#!	third filter parameters
																'R1'			: 0.0																	,	#?	first resistor
																'R2'			: 0.0																	,	#?	first capacitor
																'C1'			: 0.0																	,	#?	second resistor
																'C2'			: 0.0																	,	#?	second capacitor
																'R3'			: 1e3																	,	#?	feedback gain resistance
																'Gain'			: 1.0																	,	#?	feedback gain
															},
							},
							'LP_Filter'				:	{																									#!	external low-pass filter
															'R'					: 0																		,	#?	filter resistance
															'C'					: 0																			#?	filter capacitance
														},
							'Misc'					:	{																									#!	miscellaneous parameters
															'Vadc'				: 3.0																	,	#?	full-scale ADC voltage
															'Gain'				: 100e-6*50																,	#?	measurement gain
															'Voffset'			: 1.5																	,	#?	measurement offset
															'Delay'		:	{																				#!	sensor delay paramteres
																'Config'		: 1																		,	#?	1->transport delay | 2->pade delay
                                                                'Order'			: 2																		,	#?	pade delay degree
                                                                'Td'			: 0																		,	#?	delay duration
															},
														},
							'Error'					:	{																									#*	error parameters
									'Vvec'										: error[0]																,	#?	voltage vector referred to ADC range
                                    'Polarity'									: 1																		,	#?	1->positive | 2->negative | 3->random
									'Seed'										: randError																,   #?	random polarity seed
									'SampleTime'								: 10e-6																	,	#?	random polarity sample time
									'Digital'	:	{																										#!	digital error parameters
															'Config'			: 2																		,	#?	1->enable | 2->disable
															'ErrVec'			: ((dp.np.array(error[1:5])).T).tolist()								,	#?	digital error vectors
															'ErrType'			: 1																			#?	1->uncalibrated rms error | 2->uncalibrated max error | 3->calibrated rms error | 4->calibrated max error
													},
                                    'Analog'	:	{																										#!	analog error parameters
															'Config'			: 2																		,	#?	1->enable | 2->disable
															'ErrVec'			: ((dp.np.array(error[5:9])).T).tolist()								,	#?	analog error vectors
															'ErrType'			: 1																			#?	1->uncalibrated rms error | 2->uncalibrated max error | 3->calibrated rms error | 4->calibrated max error
													},
														},
							'Noise'					:	{																									#*	white noise parameters
									'Digital'	:	{																										#!	digital noise parameters
															'Config'			: 2																		,	#?	1->enable | 2->disable
                                                            'Sigma'				: 0.05																	,	#?	standard deveiation of the normally distributed noise
                                                            'Mean'				: 0																		,	#?	DC offset of the normally distributed noise
															'Seed'				: randNoise																,   #?	random noise seed
															'SampleTime'		: 100e-6																	#?	random noise sample time
													},
                                    'Analog'	:	{																										#!	analog noise parameters
															'Config'			: 2																		,	#?	1->enable | 2->disable
                                                            'Sigma'				: 0.05																	,	#?	standard deveiation of the normally distributed noise
                                                            'Mean'				: 0																		,	#?	DC offset of the normally distributed noise
															'Seed'				: randNoise																,   #?	random noise seed
															'SampleTime'		: 100e-6																	#?	random noise sample time
													},
														},
							'CurrentLimit'			:	{																									#*	current limit
															'Config'			: 2																		,	#?	1->enable | 2->disable
															'Ts'				: 0 																	,	#?	sampling time between inductive & capacitive links
															'tau'				: 0																		,	#?	first-order delay between inductive & capacitive links
                                                            'Rs'				: 0																		,	#?	source impedance of inductive link
															'Cs'				: 0																		,	#?	source capacitance of capacitive link
                                                            'UpLim'				: 8e-3																	,	#?	max current limit on capacitive link
                                                            'LoLim'				: -8e-3																	,	#?	min current limit on capacitive link
                                                            'Voffset'			: 1.5																		#?	voltage offset between inductive & capacitive links
														}
						}

#?----------------------------------------------------------------------------------------------------------------------------------------------------------------------

randError	=	dp.random.SystemRandom().randint(randMin, randMax)
randNoise	=	dp.random.SystemRandom().randint(randMin, randMax)
sensor 		= 	sensorsPath + 'ACS773_Error'
error		=	postProcessing.extractArrays(sensor)
#impedance  =   paramProcess.outputImpedanceMatching(opampImpedancePath, 'Ideal')

ACS773				=	{																																	#*	generic ACS773 current sensor model
							'Config'				: 2																									,	#?	1->physical model | 2->small-signal model | 3->ideal model | 4->disable
							'Channel'				: 1																									,	#?	0->odd-odd or even-even | 1->even-odd or odd-even
							'Phase'					: 0																									,	#?	point in time of sampling trigger
							'R'						: 100e-6																							,	#?	shunt or internal sensor resistance
                            'L'						: 600e-12*0																							,	#?	shunt or internal parasitic resistance
                            'Zo'       :   {                                                                                                                #!  complex output impedance model
                                'Config'			:	3																								,	#? 	1->network 1 | 2->network 2 | 3->disable
                                'Network1'	:	{																											#*  parameters of network 1
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
							'DiffOpAmp'				:   {																									#!	differential amplifier parameters
                                							'OpAmp'				: dp.copy.deepcopy(dp.OpAmps_Dicts.Ideal)								,	#?	opamp model parameters
															'Rf'				: 10e3																	,	#?	opamp feedback resistance
                                							'R1'				: 10e3																	,	#?	opamp input resistance
														},
                            'Model' 				:	{																									#*	frequency behavior model as 3-stage Sallen-Key filter
									'OpAmp'										: dp.copy.deepcopy(dp.OpAmps_Dicts.Ideal)								,	#?	opamp model parameters
									'FirstStage'			:	{																							#!	first filter parameters
																'R1'			: 75.0																	,	#?	first resistor
																'C1'			: 20e-9																	,	#?	first capacitor
																'R2'			: 212.0																	,	#?	second resistor
																'C2'			: 1.0e-9																,	#?	second capacitor
																'R3'			: 1e3																	,	#?	feedback gain resistance
																'Gain'			: 66.0																	,	#?	feedback gain
															},
									'SecondStage'			:	{																							#!	second filter parameters
																'R1'			: 40.0																	,	#?	first resistor
																'R2'			: 0.0																	,	#?	first capacitor
																'C1'			: 10e-9																	,	#?	second resistor
																'C2'			: 0.0																	,	#?	second capacitor
																'R3'			: 1e3																	,	#?	feedback gain resistance
																'Gain'			: 1.0																	,	#?	feedback gain
															},
									'ThirdStage'			:	{																							#!	third filter parameters
																'R1'			: 0.0																	,	#?	first resistor
																'R2'			: 0.0																	,	#?	first capacitor
																'C1'			: 0.0																	,	#?	second resistor
																'C2'			: 0.0																	,	#?	second capacitor
																'R3'			: 1e3																	,	#?	feedback gain resistance
																'Gain'			: 1.0																	,	#?	feedback gain
															},
							},
							'LP_Filter'				:	{																									#!	external low-pass filter
															'R'					: 2e3																	,	#?	filter resistance
															'C'					: 1e-9																		#?	filter capacitance
														},
							'Misc'					:	{																									#!	miscellaneous parameters
															'Vadc'				: 3.0																	,	#?	full-scale ADC voltage
															'Gain'				: 100e-6*66																,	#?	measurement gain
															'Voffset'			: 1.5																	,	#?	measurement offset
															'Delay'		:	{																				#!	sensor delay paramteres
																'Config'		: 2																		,	#?	1->transport delay | 2->pade delay
                                                                'Order'			: 2																		,	#?	pade delay degree
                                                                'Td'			: 2.5e-6																,	#?	delay duration
															},
														},
							'Error'					:	{																									#*	error parameters
									'Vvec'										: error[0]																,	#?	voltage vector referred to ADC range
                                    'Polarity'									: 1																		,	#?	1->positive | 2->negative | 3->random
									'Seed'										: randError																,   #?	random polarity seed
									'SampleTime'								: 10e-6																	,	#?	random polarity sample time
									'Digital'	:	{																										#!	digital error parameters
															'Config'			: 2																		,	#?	1->enable | 2->disable
															'ErrVec'			: ((dp.np.array(error[1:5])).T).tolist()								,	#?	digital error vectors
															'ErrType'			: 1																			#?	1->uncalibrated rms error | 2->uncalibrated max error | 3->calibrated rms error | 4->calibrated max error
													},
                                    'Analog'	:	{																										#!	analog error parameters
															'Config'			: 2																		,	#?	1->enable | 2->disable
															'ErrVec'			: ((dp.np.array(error[5:9])).T).tolist()								,	#?	analog error vectors
															'ErrType'			: 1																			#?	1->uncalibrated rms error | 2->uncalibrated max error | 3->calibrated rms error | 4->calibrated max error
													},
														},
							'Noise'					:	{																									#*	white noise parameters
									'Digital'	:	{																										#!	digital noise parameters
															'Config'			: 2																		,	#?	1->enable | 2->disable
                                                            'Sigma'				: 0.05																	,	#?	standard deveiation of the normally distributed noise
                                                            'Mean'				: 0																		,	#?	DC offset of the normally distributed noise
															'Seed'				: randNoise																,   #?	random noise seed
															'SampleTime'		: 100e-6																	#?	random noise sample time
													},
                                    'Analog'	:	{																										#!	analog noise parameters
															'Config'			: 2																		,	#?	1->enable | 2->disable
                                                            'Sigma'				: 0.05																	,	#?	standard deveiation of the normally distributed noise
                                                            'Mean'				: 0																		,	#?	DC offset of the normally distributed noise
															'Seed'				: randNoise																,   #?	random noise seed
															'SampleTime'		: 100e-6																	#?	random noise sample time
													},
														},
                            'CurrentLimit'			:	{																									#*	current limit
															'Config'			: 2																		,	#?	1->enable | 2->disable
															'Ts'				: 0 																	,	#?	sampling time between inductive & capacitive links
															'tau'				: 0																		,	#?	first-order delay between inductive & capacitive links
                                                            'Rs'				: 0																		,	#?	source impedance of inductive link
															'Cs'				: 0																		,	#?	source capacitance of capacitive link
                                                            'UpLim'				: 1.5e-3																,	#?	max current limit on capacitive link
                                                            'LoLim'				: -1.5e-3																,	#?	min current limit on capacitive link
                                                            'Voffset'			: 1.5																		#?	voltage offset between inductive & capacitive links
														}
						}

#?----------------------------------------------------------------------------------------------------------------------------------------------------------------------

randError	=	dp.random.SystemRandom().randint(randMin, randMax)
randNoise	=	dp.random.SystemRandom().randint(randMin, randMax)
sensor 		= 	sensorsPath + 'ASC724_Error'
error		=	postProcessing.extractArrays(sensor)
#impedance  =   paramProcess.outputImpedanceMatching(opampImpedancePath, 'Ideal')

ACS724				=	{																																	#*	generic ACS724 current sensor model
							'Config'				: 2																									,	#?	1->physical model | 2->small-signal model | 3->ideal model | 4->disable
							'Channel'				: 1																									,	#?	0->odd-odd or even-even | 1->even-odd or odd-even
							'Phase'					: 0																									,	#?	point in time of sampling trigger
							'R'						: 264e-6																							,	#?	shunt or internal sensor resistance
                            'L'						: 600e-12*0																							,	#?	shunt or internal parasitic resistance
                            'Zo'       :   {                                                                                                                #!  complex output impedance model
                                'Config'			:	3																								,	#? 	1->network 1 | 2->network 2 | 3->disable
                                'Network1'	:	{																											#*  parameters of network 1
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
							'DiffOpAmp'				:   {																									#!	differential amplifier parameters
                                							'OpAmp'				: dp.copy.deepcopy(dp.OpAmps_Dicts.Ideal)								,	#?	opamp model parameters
															'Rf'				: 10e3																	,	#?	opamp feedback resistance
                                							'R1'				: 10e3																	,	#?	opamp input resistance
														},
                            'Model' 				:	{																									#*	frequency behavior model as 3-stage Sallen-Key filter
									'OpAmp'										: dp.copy.deepcopy(dp.OpAmps_Dicts.Ideal)								,	#?	opamp model parameters
									'FirstStage'			:	{																							#!	first filter parameters
																'R1'			: 28.35e3																,	#?	first resistor
																'C1'			: 10e-9																	,	#?	first capacitor
																'R2'			: 10.0																	,	#?	second resistor
																'C2'			: 40.1e-12																,	#?	second capacitor
																'R3'			: 1e3																	,	#?	feedback gain resistance
																'Gain'			: 250																	,	#?	feedback gain
															},
									'SecondStage'			:	{																							#!	second filter parameters
																'R1'			: 72.3																	,	#?	first resistor
																'R2'			: 0.0																	,	#?	first capacitor
																'C1'			: 10e-9																	,	#?	second resistor
																'C2'			: 0.0																	,	#?	second capacitor
																'R3'			: 1e3																	,	#?	feedback gain resistance
																'Gain'			: 1.0																	,	#?	feedback gain
															},
									'ThirdStage'			:	{																							#!	third filter parameters
																'R1'			: 0.0																	,	#?	first resistor
																'R2'			: 0.0																	,	#?	first capacitor
																'C1'			: 0.0																	,	#?	second resistor
																'C2'			: 0.0																	,	#?	second capacitor
																'R3'			: 1e3																	,	#?	feedback gain resistance
																'Gain'			: 1.0																	,	#?	feedback gain
															},
							},
							'LP_Filter'				:	{																									#!	external low-pass filter
															'R'					: 0																		,	#?	filter resistance
															'C'					: 0																			#?	filter capacitance
														},
							'Misc'					:	{																									#!	miscellaneous parameters
															'Vadc'				: 3.0																	,	#?	full-scale ADC voltage
															'Gain'				: 264e-6*250															,	#?	measurement gain
															'Voffset'			: 1.5																	,	#?	measurement offset
															'Delay'		:	{																				#!	sensor delay paramteres
																'Config'		: 1																		,	#?	1->transport delay | 2->pade delay
                                                                'Order'			: 2																		,	#?	pade delay degree
                                                                'Td'			: 4e-6*0																,	#?	delay duration
															},
														},
							'Error'					:	{																									#*	error parameters
									'Vvec'										: error[0]																,	#?	voltage vector referred to ADC range
                                    'Polarity'									: 1																		,	#?	1->positive | 2->negative | 3->random
									'Seed'										: randError																,   #?	random polarity seed
									'SampleTime'								: 10e-6																	,	#?	random polarity sample time
									'Digital'	:	{																										#!	digital error parameters
															'Config'			: 2																		,	#?	1->enable | 2->disable
															'ErrVec'			: ((dp.np.array(error[1:5])).T).tolist()								,	#?	digital error vectors
															'ErrType'			: 1																			#?	1->uncalibrated rms error | 2->uncalibrated max error | 3->calibrated rms error | 4->calibrated max error
													},
                                    'Analog'	:	{																										#!	analog error parameters
															'Config'			: 2																		,	#?	1->enable | 2->disable
															'ErrVec'			: ((dp.np.array(error[5:9])).T).tolist()								,	#?	analog error vectors
															'ErrType'			: 1																			#?	1->uncalibrated rms error | 2->uncalibrated max error | 3->calibrated rms error | 4->calibrated max error
													},
														},
							'Noise'					:	{																									#*	white noise parameters
									'Digital'	:	{																										#!	digital noise parameters
															'Config'			: 2																		,	#?	1->enable | 2->disable
                                                            'Sigma'				: 0.05																	,	#?	standard deveiation of the normally distributed noise
                                                            'Mean'				: 0																		,	#?	DC offset of the normally distributed noise
															'Seed'				: randNoise																,   #?	random noise seed
															'SampleTime'		: 100e-6																	#?	random noise sample time
													},
                                    'Analog'	:	{																										#!	analog noise parameters
															'Config'			: 2																		,	#?	1->enable | 2->disable
                                                            'Sigma'				: 0.05																	,	#?	standard deveiation of the normally distributed noise
                                                            'Mean'				: 0																		,	#?	DC offset of the normally distributed noise
															'Seed'				: randNoise																,   #?	random noise seed
															'SampleTime'		: 100e-6																	#?	random noise sample time
													},
														},
							'CurrentLimit'			:	{																									#*	current limit
															'Config'			: 2																		,	#?	1->enable | 2->disable
															'Ts'				: 0 																	,	#?	sampling time between inductive & capacitive links
															'tau'				: 1e-9																	,	#?	first-order delay between inductive & capacitive links
                                                            'Rs'				: 0																		,	#?	source impedance of inductive link
															'Cs'				: 0																		,	#?	source capacitance of capacitive link
                                                            'UpLim'				: 1.6e-3																,	#?	max current limit on capacitive link
                                                            'LoLim'				: -1.6e-3																,	#?	min current limit on capacitive link
                                                            'Voffset'			: 1.5																		#?	voltage offset between inductive & capacitive links
														}
						}

#?----------------------------------------------------------------------------------------------------------------------------------------------------------------------

randError	=	dp.random.SystemRandom().randint(randMin, randMax)
randNoise	=	dp.random.SystemRandom().randint(randMin, randMax)
sensor 		= 	sensorsPath + 'DS_P100076_Error'
error		=	postProcessing.extractArrays(sensor)

DS_P100076			=	{																																	#*	DS_P100076 current transformer parameters
							'Config'				:	1																								,	#?	1->physical model | 2->small-signal model | 3->ideal model | 4->disable
                            'Channel'				:   1																								,	#?	0->odd-odd or even-even | 1->even-odd or odd-even
							'Trafo'					:	dp.copy.deepcopy(dp.Mags_Dicts.DS_P100076_Trafo)												,	#?	current transformer parameters
                            'Rt'					:	11																								,	#?	burden or terminating resistance
                            'Ct'					:	0																								,	#?	terminating capacitance
							'Vf'        			:	0.375			    																			,   #?	rectifier diode forward voltage
							'Rd'       				:	22e-3		        																			,   #?	rectifier diode ON-state resistance
							'Rf'					:	100																								,	#?	RC filter resistance
							'Cf'					: 	100e-12																							,	#?	RC filter capacitance
                            'Phase'					: 	0																								,	#?	point in time of sampling trigger
							'Cf_factor'				:	100																								,	#?	RC filter capacitance factor
							'DiodeLoss'				:	[0.1, 0.1, 0.1, 0.1]	 																		,	#?	estimated switching loss of the CT diodes
							'LP_Filter'				:	{																									#!	external low-pass filter
															'R'					: 0																		,	#?	filter resistance
															'C'					: 0																			#?	filter capacitance
														},
                            'Misc'					:	{																									#!	miscellaneous parameters
															'Vadc'				: 3.0																	,	#?	full-scale ADC voltage
															'Gain'				: 11/100																,	#?	measurement gain
															'Voffset'			: 0																		,	#?	measurement offset
															'Delay'		:	{																				#!	sensor delay paramteres
																'Config'		: 2																		,	#?	1->transport delay | 2->pade delay
                                                                'Order'			: 2																		,	#?	pade delay degree
                                                                'Td'			: 0																		,	#?	delay duration
															},
														},
                            'Error'					:	{																									#*	error parameters
									'Vvec'										: error[0]																,	#?	voltage vector referred to ADC range
                                    'Polarity'									: 1																		,	#?	1->positive | 2->negative | 3->random
									'Seed'										: randError																,   #?	random polarity seed
									'SampleTime'								: 10e-6																	,	#?	random polarity sample time
									'Digital'	:	{																										#!	digital error parameters
															'Config'			: 2																		,	#?	1->enable | 2->disable
															'ErrVec'			: ((dp.np.array(error[1:5])).T).tolist()								,	#?	digital error vectors
															'ErrType'			: 1																			#?	1->uncalibrated rms error | 2->uncalibrated max error | 3->calibrated rms error | 4->calibrated max error
													},
                                    'Analog'	:	{																										#!	analog error parameters
															'Config'			: 2																		,	#?	1->enable | 2->disable
															'ErrVec'			: ((dp.np.array(error[5:9])).T).tolist()								,	#?	analog error vectors
															'ErrType'			: 1																			#?	1->uncalibrated rms error | 2->uncalibrated max error | 3->calibrated rms error | 4->calibrated max error
													},
														},
							'Noise'					:	{																									#*	white noise parameters
									'Digital'	:	{																										#!	digital noise parameters
															'Config'			: 2																		,	#?	1->enable | 2->disable
                                                            'Sigma'				: 0.05																	,	#?	standard deveiation of the normally distributed noise
                                                            'Mean'				: 0																		,	#?	DC offset of the normally distributed noise
															'Seed'				: randNoise																,   #?	random noise seed
															'SampleTime'		: 100e-6																	#?	random noise sample time
													},
                                    'Analog'	:	{																										#!	analog noise parameters
															'Config'			: 2																		,	#?	1->enable | 2->disable
                                                            'Sigma'				: 0.05																	,	#?	standard deveiation of the normally distributed noise
                                                            'Mean'				: 0																		,	#?	DC offset of the normally distributed noise
															'Seed'				: randNoise																,   #?	random noise seed
															'SampleTime'		: 100e-6																	#?	random noise sample time
													},
														},
						}

#?----------------------------------------------------------------------------------------------------------------------------------------------------------------------

#!	assemble all sensors to be transferred to the PLECS model
#?----------------------------------------------------------------------------------------------------------------------------------------------------------------------

AllSensors 			= 	{
							'SI8932D' 				: 	SI8932D 			,
							'BuffDivider_1' 		: 	BuffDivider_1 		,
							'BuffDivider_2' 		: 	BuffDivider_2 		,
                            'BuffDivider_3' 		: 	BuffDivider_3 		,
                            'BuffDivider_4' 		: 	BuffDivider_4 		,
							'INA240A2' 				: 	INA240A2 			,
                            'INA240A1'				:	INA240A1			,
                            'AD8411A'				:	AD8411A				,
                            'INA296A3'				:	INA296A3			,
							'ACS773' 				: 	ACS773 				,
							'ACS724' 				: 	ACS724 				,
							'DS_P100076' 			: 	DS_P100076
						}
#?----------------------------------------------------------------------------------------------------------------------------------------------------------------------