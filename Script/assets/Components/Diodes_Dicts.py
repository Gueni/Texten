
#?----------------------------------------------------------------------------------------------------------------------------------------------------------------------
#?									 ____  _           _        ____                                _
#?									|  _ \(_) ___   __| | ___  |  _ \ __ _ _ __ __ _ _ __ ___   ___| |_ ___ _ __ ___
#?									| | | | |/ _ \ / _` |/ _ \ | |_) / _` | '__/ _` | '_ ` _ \ / _ \ __/ _ \ '__/ __|
#?									| |_| | | (_) | (_| |  __/ |  __/ (_| | | | (_| | | | | | |  __/ ||  __/ |  \__ \
#?									|____/|_|\___/ \__,_|\___| |_|   \__,_|_|  \__,_|_| |_| |_|\___|\__\___|_|  |___/
#?
#?----------------------------------------------------------------------------------------------------------------------------------------------------------------------
#!----------------------------------------------------------------------------------------------------------------------------------------------------------------------
#!   This Script works as a Netlists dictionary for the plecs spice diode models.
#!   Do not modify the values in this file.
#!----------------------------------------------------------------------------------------------------------------------------------------------------------------------
#?----------------------------------------------------------------------------------------------------------------------------------------------------------------------
import  Lib.Param_Process           as        PM
#?----------------------------------------------------------------------------------------------------------------------------------------------------------------------

# #!  call the Params-Processing class and point to the location of csv and netlist data
paramProcess			=	PM.ParamProcess()
DiodeVIPath 			=	'Script/Data/Diodes_VI/'
diodesNetlistPath		=	'Script/Data/Netlists/Diodes/'

#! 	Diode netlist parameters

# GaN Switches
#?----------------------------------------------------------------------------------------------------------------------------------------------------------------------

Vfvec,Ifvec,Rd,Vt 					=	paramProcess.DiodeVI_data(DiodeVIPath,'NRVB230LSFT1G')
netlistpath							=	paramProcess.Netlist_path(diodesNetlistPath, 'NRVB230LSFT1G')

NRVB230LSFT1G		=	{																																		#*	NRVB230LSFT1G parameters
							'Name'				:	'NRVB230LSFT1G'																							,	#?	.subckt name
							'File'				:	netlistpath																								,	#?	Netlist file path
							'Config'			:	4																										,	#?	1->non-ideal RR | 2->non-ideal | 3->ideal RR | 4->ideal | 5-> Spice diode
							'Thermal'           :   ''                                  																	,   #? 	separate body diode
							'Custom'            :   []					                 																	,   #? 	diode provided custrom variables
							'Rd_on'             :   Rd[0]													                              					,  	#? 	diode ON resistance
							'Rd_off'			:	'inf'																									,	#?	diode OFF resistance
							'Vf'                :   Vt[0]                                 																	,   #? 	diode forward voltage
							'If'                :   2	                                 																	,   #? 	diode forward current
							'dIr'               :   0                                 																		,   #? 	diode current slope
							'Lrr'				:	1e-9																									,	#?	diode reverse recovery inductance
							'Trr'               :   0	                                  																	,   #? 	diode reverse recovery time
							'Irr'               :   0                                      																	,   #? 	diode reverse recovery current
							'Qrr'               :   0			                              																,	#? 	diode reverse recovery charge
							'Is'                :   0              																		   					,	#? 	diode reference current
							'Vs'				:	0																										,	#?	diode reference voltage
                            'VIcurve'			:	{																											#!	diode VI characteristics
                                'Vfvec'				:	Vfvec																								,	#?	forward voltage vector
                                'Ifvec'				:	Ifvec																								,	#?	forward current vector
								'Rdvec'				:	Rd																									,	#?	dynamic resistance vector
								'Vtvec'				:	Vt																									,	#?	threshold voltage vector
                                'Temps'				:	[-55,25,100,125]																					,	#?	temperature vector
                                'Vfscale'			:	1																										#?	Vf scaling to account for min, typ and max deviations
						},
							'Tau_deg'			:	1e-9																										#?	deglitch filter for currents and voltages
						}
#?----------------------------------------------------------------------------------------------------------------------------------------------------------------------

Vfvec,Ifvec,Rd,Vt 					=	paramProcess.DiodeVI_data(DiodeVIPath,'DRB068MM100')
netlistpath							=	paramProcess.Netlist_path(diodesNetlistPath, 'DRB068MM100')

DRB068MM100			=	{																																		#*	DRB068MM100 parameters
							'Name'				:	'DRB068MM100'																							,	#?	.subckt name
							'File'				:	netlistpath																								,	#?	Netlist file path
							'Config'			:	4																										,	#?	1->non-ideal RR | 2->non-ideal | 3->ideal RR | 4->ideal | 5-> Spice diode
							'Thermal'           :   ''                                  																	,   #? 	separate body diode
							'Custom'            :   []					                 																	,   #? 	diode provided custrom variables
							'Rd_on'             :   Rd[0]													                              					,  	#? 	diode ON resistance
							'Rd_off'			:	'inf'																									,	#?	diode OFF resistance
							'Vf'                :   Vt[0]                                 																	,   #? 	diode forward voltage
							'If'                :   2	                                 																	,   #? 	diode forward current
							'dIr'               :   0                                 																		,   #? 	diode current slope
							'Lrr'				:	1e-9																									,	#?	diode reverse recovery inductance
							'Trr'               :   8.15e-9	                                  																,   #? 	diode reverse recovery time
							'Irr'               :   0.01                                    																,   #? 	diode reverse recovery current
							'Qrr'               :   0			                              																,	#? 	diode reverse recovery charge
							'Is'                :   0              																		   					,	#? 	diode reference current
							'Vs'				:	0																										,	#?	diode reference voltage
                            'VIcurve'			:	{																											#!	diode VI characteristics
                                'Vfvec'				:	Vfvec																								,	#?	forward voltage vector
                                'Ifvec'				:	Ifvec																								,	#?	forward current vector
								'Rdvec'				:	Rd																									,	#?	dynamic resistance vector
								'Vtvec'				:	Vt																									,	#?	threshold voltage vector
                                'Temps'				:	[-25,25,75,125,175]																					,	#?	temperature vector
                                'Vfscale'			:	1																										#?	Vf scaling to account for min, typ and max deviations
						},
							'Tau_deg'			:	1e-9																										#?	deglitch filter for currents and voltages
						}
#?----------------------------------------------------------------------------------------------------------------------------------------------------------------------

Vfvec,Ifvec,Rd,Vt 					=	paramProcess.DiodeVI_data(DiodeVIPath,'BZT52C2V0_Diotec')
netlistpath							=	paramProcess.Netlist_path(diodesNetlistPath, 'BZT52C2V0')

BZT52C2V0_Diotec_DF	=	{																																		#*	BZT52C2V0 parameters
							'Name'				:	'BZT52C2V0'																								,	#?	.subckt name
							'File'				:	netlistpath																								,	#?	Netlist file path
							'Config'			:	4																										,	#?	1->non-ideal RR | 2->non-ideal | 3->ideal RR | 4->ideal | 5-> Spice diode
                            'Thermal'           :   ''                                  																	,   #? 	separate body diode
							'Custom'            :   []					                 																	,   #? 	diode provided custrom variables
							'Rd_on'             :   Rd[0]													                              					,  	#? 	diode ON resistance
							'Rd_off'			:	'inf'																									,	#?	diode OFF resistance
							'Vf'                :   Vt[0]                                 																	,   #? 	diode forward voltage
							'If'                :   50e-3   	                              																,   #? 	diode forward current
							'dIr'               :   0                                 																		,   #? 	diode current slope
							'Lrr'				:	1e-9																									,	#?	diode reverse recovery inductance
							'Trr'               :   0	                                  																	,   #? 	diode reverse recovery time
							'Irr'               :   0                                      																	,   #? 	diode reverse recovery current
							'Qrr'               :   0			                              																,	#? 	diode reverse recovery charge
							'Is'                :   0              																		   					,	#? 	diode reference current
							'Vs'				:	0																										,	#?	diode reference voltage
                            'VIcurve'			:	{																											#!	diode VI characteristics
                                'Vfvec'				:	Vfvec																								,	#?	forward voltage vector
                                'Ifvec'				:	Ifvec																								,	#?	forward current vector
								'Rdvec'				:	Rd																									,	#?	dynamic resistance vector
								'Vtvec'				:	Vt																									,	#?	threshold voltage vector
                                'Temps'				:	[25]																								,	#?	temperature vector
                                'Vfscale'			:	1																										#?	Vf scaling to account for min, typ and max deviations
						},
							'Tau_deg'			:	1e-9																										#?	deglitch filter for currents and voltages
						}

Vfvec,Ifvec,Rd,Vt 					=	paramProcess.DiodeVI_data(DiodeVIPath,'BZT52C2V0_Diotec')
netlistpath							=	paramProcess.Netlist_path(diodesNetlistPath, 'BZT52C2V0')

BZT52C2V0_Diotec_DR	=	{																																		#*	BZT52C2V0 parameters
							'Name'				:	'BZT52C2V0'																								,	#?	.subckt name
							'File'				:	netlistpath																								,	#?	Netlist file path
							'Config'			:	4																										,	#?	1->non-ideal RR | 2->non-ideal | 3->ideal RR | 4->ideal | 5-> Spice diode
                            'Thermal'           :   ''                                  																	,   #? 	separate body diode
							'Custom'            :   []					                 																	,   #? 	diode provided custrom variables
							'Rd_on'             :   Rd[0]													                              					,  	#? 	diode ON resistance
							'Rd_off'			:	'inf'																									,	#?	diode OFF resistance
							'Vf'                :   Vt[0]                                 																	,   #? 	diode forward voltage
							'If'                :   50e-3   	                              																,   #? 	diode forward current
							'dIr'               :   0                                 																		,   #? 	diode current slope
							'Lrr'				:	1e-9																									,	#?	diode reverse recovery inductance
							'Trr'               :   0	                                  																	,   #? 	diode reverse recovery time
							'Irr'               :   0                                      																	,   #? 	diode reverse recovery current
							'Qrr'               :   0			                              																,	#? 	diode reverse recovery charge
							'Is'                :   0              																		   					,	#? 	diode reference current
							'Vs'				:	0																										,	#?	diode reference voltage
                            'VIcurve'			:	{																											#!	diode VI characteristics
                                'Vfvec'				:	Vfvec																								,	#?	forward voltage vector
                                'Ifvec'				:	Ifvec																								,	#?	forward current vector
								'Rdvec'				:	Rd																									,	#?	dynamic resistance vector
								'Vtvec'				:	Vt																									,	#?	threshold voltage vector
                                'Temps'				:	[25]																								,	#?	temperature vector
                                'Vfscale'			:	1																										#?	Vf scaling to account for min, typ and max deviations
						},
							'Tau_deg'			:	1e-9																										#?	deglitch filter for currents and voltages
						}
#?----------------------------------------------------------------------------------------------------------------------------------------------------------------------

Vfvec,Ifvec,Rd,Vt 					=	paramProcess.DiodeVI_data(DiodeVIPath,'BZT52C3V0_Diotec')
netlistpath							=	paramProcess.Netlist_path(diodesNetlistPath, 'BZT52C3V0')

BZT52C3V0_Diotec_DF	=	{																																		#*	BZT52C3V0 parameters
							'Name'				:	'DI_BZT52C3V0'																							,	#?	.subckt name
							'File'				:	netlistpath																								,	#?	Netlist file path
							'Config'			:	4																										,	#?	1->non-ideal RR | 2->non-ideal | 3->ideal RR | 4->ideal | 5-> Spice diode
                            'Thermal'           :   ''                                  																	,   #? 	separate body diode
							'Custom'            :   []					                 																	,   #? 	diode provided custrom variables
							'Rd_on'             :   Rd[0]													                              					,  	#? 	diode ON resistance
							'Rd_off'			:	'inf'																									,	#?	diode OFF resistance
							'Vf'                :   Vt[0]        	                        																,   #? 	diode forward voltage
							'If'                :   50e-3	  	    	                         															,   #? 	diode forward current
							'dIr'               :   0                                 																		,   #? 	diode current slope
							'Lrr'				:	1e-9																									,	#?	diode reverse recovery inductance
							'Trr'               :   0	                                  																	,   #? 	diode reverse recovery time
							'Irr'               :   0                                      																	,   #? 	diode reverse recovery current
							'Qrr'               :   0			                              																,	#? 	diode reverse recovery charge
							'Is'                :   0              																		   					,	#? 	diode reference current
							'Vs'				:	0																										,	#?	diode reference voltage
                            'VIcurve'			:	{																											#!	diode VI characteristics
                                'Vfvec'				:	Vfvec																								,	#?	forward voltage vector
                                'Ifvec'				:	Ifvec																								,	#?	forward current vector
								'Rdvec'				:	Rd																									,	#?	dynamic resistance vector
								'Vtvec'				:	Vt																									,	#?	threshold voltage vector
                                'Temps'				:	[25]																								,	#?	temperature vector
                                'Vfscale'			:	1																										#?	Vf scaling to account for min, typ and max deviations
						},
							'Tau_deg'			:	1e-9																										#?	deglitch filter for currents and voltages
						}
#?----------------------------------------------------------------------------------------------------------------------------------------------------------------------
Vfvec,Ifvec,Rd,Vt 					=	paramProcess.DiodeVI_data(DiodeVIPath,'BZT52C3V0_Diotec')
netlistpath							=	paramProcess.Netlist_path(diodesNetlistPath, 'BZT52C3V0')

BZT52C3V0_Diotec_DR	=	{																																		#*	BZT52C3V0 parameters
							'Name'				:	'DI_BZT52C3V0'																							,	#?	.subckt name
							'File'				:	netlistpath																								,	#?	Netlist file path
							'Config'			:	4																										,	#?	1->non-ideal RR | 2->non-ideal | 3->ideal RR | 4->ideal | 5-> Spice diode
                            'Thermal'           :   ''                                  																	,   #? 	separate body diode
							'Custom'            :   []					                 																	,   #? 	diode provided custrom variables
							'Rd_on'             :   Rd[0]													                              					,  	#? 	diode ON resistance
							'Rd_off'			:	'inf'																									,	#?	diode OFF resistance
							'Vf'                :   Vt[0]        	                        																,   #? 	diode forward voltage
							'If'                :   50e-3	  	    	                         															,   #? 	diode forward current
							'dIr'               :   0                                 																		,   #? 	diode current slope
							'Lrr'				:	1e-9																									,	#?	diode reverse recovery inductance
							'Trr'               :   0	                                  																	,   #? 	diode reverse recovery time
							'Irr'               :   0                                      																	,   #? 	diode reverse recovery current
							'Qrr'               :   0			                              																,	#? 	diode reverse recovery charge
							'Is'                :   0              																		   					,	#? 	diode reference current
							'Vs'				:	0																										,	#?	diode reference voltage
                            'VIcurve'			:	{																											#!	diode VI characteristics
                                'Vfvec'				:	Vfvec																								,	#?	forward voltage vector
                                'Ifvec'				:	Ifvec																								,	#?	forward current vector
								'Rdvec'				:	Rd																									,	#?	dynamic resistance vector
								'Vtvec'				:	Vt																									,	#?	threshold voltage vector
                                'Temps'				:	[25]																								,	#?	temperature vector
                                'Vfscale'			:	1																										#?	Vf scaling to account for min, typ and max deviations
						},
							'Tau_deg'			:	1e-9																										#?	deglitch filter for currents and voltages
						}
#?----------------------------------------------------------------------------------------------------------------------------------------------------------------------

Vfvec,Ifvec,Rd,Vt 					=	paramProcess.DiodeVI_data(DiodeVIPath,'BZT52C2V0_DiodesInc')
netlistpath							=	paramProcess.Netlist_path(diodesNetlistPath, 'BZT52C2V0')

BZT52C2V0_DiodesInc_DF	=	{																																	#*	BZT52C2V0 parameters
							'Name'				:	'BZT52C2V0'																								,	#?	.subckt name
							'File'				:	netlistpath																								,	#?	Netlist file path
							'Config'			:	4																										,	#?	1->non-ideal RR | 2->non-ideal | 3->ideal RR | 4->ideal | 5-> Spice diode
                            'Thermal'           :   ''                                  																	,   #? 	separate body diode
							'Custom'            :   []					                 																	,   #? 	diode provided custrom variables
							'Rd_on'             :   Rd[0]													                              					,  	#? 	diode ON resistance
							'Rd_off'			:	'inf'																									,	#?	diode OFF resistance
							'Vf'                :   Vt[0]                                 																	,   #? 	diode forward voltage
							'If'                :   10e-3   	                              																,   #? 	diode forward current
							'dIr'               :   0                                 																		,   #? 	diode current slope
							'Lrr'				:	1e-9																									,	#?	diode reverse recovery inductance
							'Trr'               :   0	                                  																	,   #? 	diode reverse recovery time
							'Irr'               :   0                                      																	,   #? 	diode reverse recovery current
							'Qrr'               :   0			                              																,	#? 	diode reverse recovery charge
							'Is'                :   0              																		   					,	#? 	diode reference current
							'Vs'				:	0																										,	#?	diode reference voltage
                            'VIcurve'			:	{																											#!	diode VI characteristics
                                'Vfvec'				:	Vfvec																								,	#?	forward voltage vector
                                'Ifvec'				:	Ifvec																								,	#?	forward current vector
								'Rdvec'				:	Rd																									,	#?	dynamic resistance vector
								'Vtvec'				:	Vt																									,	#?	threshold voltage vector
                                'Temps'				:	[25]																								,	#?	temperature vector
                                'Vfscale'			:	1																										#?	Vf scaling to account for min, typ and max deviations
						},
							'Tau_deg'			:	1e-9																										#?	deglitch filter for currents and voltages
						}
#?----------------------------------------------------------------------------------------------------------------------------------------------------------------------

Vfvec,Ifvec,Rd,Vt 					=	paramProcess.DiodeVI_data(DiodeVIPath,'BZT52C2V0_DiodesInc')
netlistpath							=	paramProcess.Netlist_path(diodesNetlistPath, 'BZT52C2V0')

BZT52C2V0_DiodesInc_DR	=	{																																	#*	BZT52C2V0 parameters
							'Name'				:	'BZT52C2V0'																								,	#?	.subckt name
							'File'				:	netlistpath																								,	#?	Netlist file path
							'Config'			:	4																										,	#?	1->non-ideal RR | 2->non-ideal | 3->ideal RR | 4->ideal | 5-> Spice diode
                            'Thermal'           :   ''                                  																	,   #? 	separate body diode
							'Custom'            :   []					                 																	,   #? 	diode provided custrom variables
							'Rd_on'             :   Rd[0]													                              					,  	#? 	diode ON resistance
							'Rd_off'			:	'inf'																									,	#?	diode OFF resistance
							'Vf'                :   Vt[0]                                 																	,   #? 	diode forward voltage
							'If'                :   10e-3   	                              																,   #? 	diode forward current
							'dIr'               :   0                                 																		,   #? 	diode current slope
							'Lrr'				:	1e-9																									,	#?	diode reverse recovery inductance
							'Trr'               :   0	                                  																	,   #? 	diode reverse recovery time
							'Irr'               :   0                                      																	,   #? 	diode reverse recovery current
							'Qrr'               :   0			                              																,	#? 	diode reverse recovery charge
							'Is'                :   0              																		   					,	#? 	diode reference current
							'Vs'				:	0																										,	#?	diode reference voltage
                            'VIcurve'			:	{																											#!	diode VI characteristics
                                'Vfvec'				:	Vfvec																								,	#?	forward voltage vector
                                'Ifvec'				:	Ifvec																								,	#?	forward current vector
								'Rdvec'				:	Rd																									,	#?	dynamic resistance vector
								'Vtvec'				:	Vt																									,	#?	threshold voltage vector
                                'Temps'				:	[25]																								,	#?	temperature vector
                                'Vfscale'			:	1																										#?	Vf scaling to account for min, typ and max deviations
						},
							'Tau_deg'			:	100e-9																										#?	deglitch filter for currents and voltages
						}
#?----------------------------------------------------------------------------------------------------------------------------------------------------------------------

Vfvec,Ifvec,Rd,Vt 					=	paramProcess.DiodeVI_data(DiodeVIPath,'BZT52C3V0_DiodesInc')
netlistpath							=	paramProcess.Netlist_path(diodesNetlistPath, 'BZT52C3V0')

BZT52C3V0_DiodesInc_DF	=	{																																	#*	BZT52C2V0 parameters
							'Name'				:	'DI_BZT52C3V0'																							,	#?	.subckt name
							'File'				:	netlistpath																								,	#?	Netlist file path
							'Config'			:	4																										,	#?	1->non-ideal RR | 2->non-ideal | 3->ideal RR | 4->ideal | 5-> Spice diode
                            'Thermal'           :   ''                                  																	,   #? 	separate body diode
							'Custom'            :   []					                 																	,   #? 	diode provided custrom variables
							'Rd_on'             :   Rd[0]													                              					,  	#? 	diode ON resistance
							'Rd_off'			:	'inf'																									,	#?	diode OFF resistance
							'Vf'                :   Vt[0]                                 																	,   #? 	diode forward voltage
							'If'                :   10e-3   	                              																,   #? 	diode forward current
							'dIr'               :   0                                 																		,   #? 	diode current slope
							'Lrr'				:	1e-9																									,	#?	diode reverse recovery inductance
							'Trr'               :   0	                                  																	,   #? 	diode reverse recovery time
							'Irr'               :   0                                      																	,   #? 	diode reverse recovery current
							'Qrr'               :   0			                              																,	#? 	diode reverse recovery charge
							'Is'                :   0              																		   					,	#? 	diode reference current
							'Vs'				:	0																										,	#?	diode reference voltage
                            'VIcurve'			:	{																											#!	diode VI characteristics
                                'Vfvec'				:	Vfvec																								,	#?	forward voltage vector
                                'Ifvec'				:	Ifvec																								,	#?	forward current vector
								'Rdvec'				:	Rd																									,	#?	dynamic resistance vector
								'Vtvec'				:	Vt																									,	#?	threshold voltage vector
                                'Temps'				:	[25,125]																								,	#?	temperature vector
                                'Vfscale'			:	1																										#?	Vf scaling to account for min, typ and max deviations
						},
							'Tau_deg'			:	1e-9																										#?	deglitch filter for currents and voltages
						}

#?----------------------------------------------------------------------------------------------------------------------------------------------------------------------

Vfvec,Ifvec,Rd,Vt 					=	paramProcess.DiodeVI_data(DiodeVIPath,'BZT52C3V0_DiodesInc')
netlistpath							=	paramProcess.Netlist_path(diodesNetlistPath, 'BZT52C3V0')

BZT52C3V0_DiodesInc_DR	=	{																																	#*	BZT52C2V0 parameters
							'Name'				:	'DI_BZT52C3V0'																							,	#?	.subckt name
							'File'				:	netlistpath																								,	#?	Netlist file path
							'Config'			:	4																										,	#?	1->non-ideal RR | 2->non-ideal | 3->ideal RR | 4->ideal | 5-> Spice diode
                            'Thermal'           :   ''                                  																	,   #? 	separate body diode
							'Custom'            :   []					                 																	,   #? 	diode provided custrom variables
							'Rd_on'             :   Rd[0]													                              					,  	#? 	diode ON resistance
							'Rd_off'			:	'inf'																									,	#?	diode OFF resistance
							'Vf'                :   Vt[0]                                 																	,   #? 	diode forward voltage
							'If'                :   10e-3   	                              																,   #? 	diode forward current
							'dIr'               :   0                                 																		,   #? 	diode current slope
							'Lrr'				:	1e-9																									,	#?	diode reverse recovery inductance
							'Trr'               :   0	                                  																	,   #? 	diode reverse recovery time
							'Irr'               :   0                                      																	,   #? 	diode reverse recovery current
							'Qrr'               :   0			                              																,	#? 	diode reverse recovery charge
							'Is'                :   0              																		   					,	#? 	diode reference current
							'Vs'				:	0																										,	#?	diode reference voltage
                            'VIcurve'			:	{																											#!	diode VI characteristics
                                'Vfvec'				:	Vfvec																								,	#?	forward voltage vector
                                'Ifvec'				:	Ifvec																								,	#?	forward current vector
								'Rdvec'				:	Rd																									,	#?	dynamic resistance vector
								'Vtvec'				:	Vt																									,	#?	threshold voltage vector
                                'Temps'				:	[25,125]																								,	#?	temperature vector
                                'Vfscale'			:	1																										#?	Vf scaling to account for min, typ and max deviations
						},
							'Tau_deg'			:	1e-9																										#?	deglitch filter for currents and voltages
						}

#?----------------------------------------------------------------------------------------------------------------------------------------------------------------------

#!	assemble all diodes to be transferred to the PLECS model
#?----------------------------------------------------------------------------------------------------------------------------------------------------------------------

AllDiodes 			=	{
								'NRVB230LSFT1G' 			: 	NRVB230LSFT1G,
                                'DRB068MM100'				: 	DRB068MM100,
                                'BZT52C2V0_Diotec_DF' 		:	BZT52C2V0_Diotec_DF,
                                'BZT52C2V0_Diotec_DR' 		:	BZT52C2V0_Diotec_DR,
                                'BZT52C3V0_Diotec_DF'		:	BZT52C3V0_Diotec_DF,
                                'BZT52C3V0_Diotec_DR'		:	BZT52C3V0_Diotec_DR,
                                'BZT52C2V0_DiodesInc_DF'	:	BZT52C2V0_DiodesInc_DF,
                                'BZT52C2V0_DiodesInc_DR'	:	BZT52C2V0_DiodesInc_DR,
                                'BZT52C3V0_DiodesInc_DF'	:	BZT52C3V0_DiodesInc_DF,
                                'BZT52C3V0_DiodesInc_DR'	:	BZT52C3V0_DiodesInc_DR
						}
#?----------------------------------------------------------------------------------------------------------------------------------------------------------------------