
#?----------------------------------------------------------------------------------------------------------------------------------------------------------------------
#?						 _____              _ _         ____                 _       ____                                _
#?						|  ___|__ _ __ _ __(_) |_ ___  | __ )  ___  __ _  __| |___  |  _ \ __ _ _ __ __ _ _ __ ___   ___| |_ ___ _ __ ___
#?						| |_ / _ \ '__| '__| | __/ _ \ |  _ \ / _ \/ _` |/ _` / __| | |_) / _` | '__/ _` | '_ ` _ \ / _ \ __/ _ \ '__/ __|
#?						|  _|  __/ |  | |  | | ||  __/ | |_) |  __/ (_| | (_| \__ \ |  __/ (_| | | | (_| | | | | | |  __/ ||  __/ |  \__ \
#?						|_|  \___|_|  |_|  |_|\__\___| |____/ \___|\__,_|\__,_|___/ |_|   \__,_|_|  \__,_|_| |_| |_|\___|\__\___|_|  |___/
#?
#?----------------------------------------------------------------------------------------------------------------------------------------------------------------------
#!----------------------------------------------------------------------------------------------------------------------------------------------------------------------
#!   This Script works as a Parameter dictionary for the plecs ferrite beads models.
#!   Do not modify the values in this file.
#!----------------------------------------------------------------------------------------------------------------------------------------------------------------------
#?----------------------------------------------------------------------------------------------------------------------------------------------------------------------
import  Lib.Param_Process	as	PM
#?----------------------------------------------------------------------------------------------------------------------------------------------------------------------

#! Call the Post-Processing class and point to the location of csv data
paramProcess				=	PM.ParamProcess()
beadsNetlistPath   			=	'Script/Data/Netlists/Ferrite_Beads/'

#! Ferrite beads models parameters
#?----------------------------------------------------------------------------------------------------------------------------------------------------------------------

Netlistpath		    =	paramProcess.Netlist_path(beadsNetlistPath, 'BLM21PG220SH1')

BLM21PG220SH1 		=	{																																	#!	BLM21PG220SH1 ferrite bead parameters
							'Config'    				:	1					            															,   #?	1->model 1 | 2->model 2 | 3->spice netlist
							'Model_1'	:	{																												#*	model 1 parameters
                                'R1'					:	20.23					            														,	#?	first resistance value
								'L1'					:	3.864e-8					            													,	#?	first inductance value
								'C1'					:	8.193e-13					            													,	#?	first capacitance value
								'R2'					:	9.170					            														,	#?	second resistance value
								'L2'					:	1.188e-7					            													,	#?	second inductance value
								'R3'					:	1.773e+5					            													,	#?	third resistance value
								'L3'					:	7.514e-10					            													,	#?	third inductance value
								'R4'					:	3.000e-3					            													,	#?	fourth resistance value
							},
                            'Model_2'	:	{																												#*	model 2 parameters
								'R1'					:	0						            														,	#?	first resistance value
								'L1'					:	0							            													,	#?	first inductance value
								'C1'					:	0							            													,	#?	first capacitance value
								'R2'					:	0						            														,	#?	second resistance value
								'L2'					:	0							            													,	#?	second inductance value
								'R3'					:	0							            													,	#?	third resistance value
								'L3'					:	0							            													,	#?	third inductance value
								'R4'					:	0							            													,	#?	fourth resistance value
							},
                            'Netlist'       :   {                                                                                                           #!  SPICE netlist parameters
									'File'              :   Netlistpath                                                                                 ,   #?  netlist file directory location
									'Type'              :   1                                                                                           ,   #?  description type, 1->.subckt | 2->.model
									'Name'              :   'BLM21PG220SH1'                                                                             	#?  spice model name as it appears in the netlist file
							},
					}

#?----------------------------------------------------------------------------------------------------------------------------------------------------------------------

Netlistpath		    =	paramProcess.Netlist_path(beadsNetlistPath, 'BLM31PG601SH1')

BLM31PG601SH1 		=	{																																	#!	BLM31PG601SH1 ferrite bead parameters
							'Config'    				:	1					            															,   #?	1->model 1 | 2->model 2 | 3->spice netlist
							'Model_1'	:	{																												#*	model 1 parameters
                                'R1'					:	178.4					            														,	#?	first resistance value
								'L1'					:	2.592e-6						            												,	#?	first inductance value
								'C1'					:	1.357e-12						            												,	#?	first capacitance value
								'R2'					:	451.3					            														,	#?	second resistance value
								'L2'					:	9.665e-7						            												,	#?	second inductance value
								'R3'					:	28.53						            													,	#?	third resistance value
								'L3'					:	5.435e-7						            												,	#?	third inductance value
								'R4'					:	6.000e-2						            												,	#?	fourth resistance value
							},
                            'Model_2'	:	{																												#*	model 2 parameters
								'R1'					:	0						            														,	#?	first resistance value
								'L1'					:	0							            													,	#?	first inductance value
								'C1'					:	0							            													,	#?	first capacitance value
								'R2'					:	0						            														,	#?	second resistance value
								'L2'					:	0							            													,	#?	second inductance value
								'R3'					:	0							            													,	#?	third resistance value
								'L3'					:	0							            													,	#?	third inductance value
								'R4'					:	0							            													,	#?	fourth resistance value
							},
                            'Netlist'       :   {                                                                                                           #!  SPICE netlist parameters
									'File'              :   Netlistpath                                                                                 ,   #?  netlist file directory location
									'Type'              :   1                                                                                           ,   #?  description type, 1->.subckt | 2->.model
									'Name'              :   'BLM31PG601SH1'                                                                             	#?  spice model name as it appears in the netlist file
							},
					}

#?----------------------------------------------------------------------------------------------------------------------------------------------------------------------

Netlistpath		    =	paramProcess.Netlist_path(beadsNetlistPath, 'KPZ1608SHR221ATD25')

KPZ1608SHR221ATD25 		=	{																																#!	KPZ1608SHR221ATD25 ferrite bead parameters
							'Config'    				:	1					            															,   #?	1->model 1 | 2->model 2 | 3->spice netlist
							'Model_1'	:	{																												#*	model 1 parameters
                                'R1'					:	2.6e2					            														,	#?	first resistance value
								'L1'					:	1.04e-6						            													,	#?	first inductance value
								'C1'					:	5.8e-13						            													,	#?	first capacitance value
								'R2'					:	0					            															,	#?	second resistance value
								'L2'					:	0						            														,	#?	second inductance value
								'R3'					:	0						            														,	#?	third resistance value
								'L3'					:	0						            														,	#?	third inductance value
								'R4'					:	3.9e-2						            													,	#?	fourth resistance value
							},
                            'Model_2'	:	{																												#*	model 2 parameters
								'R1'					:	0						            														,	#?	first resistance value
								'L1'					:	0							            													,	#?	first inductance value
								'C1'					:	0							            													,	#?	first capacitance value
								'R2'					:	0						            														,	#?	second resistance value
								'L2'					:	0							            													,	#?	second inductance value
								'R3'					:	0							            													,	#?	third resistance value
								'L3'					:	0							            													,	#?	third inductance value
								'R4'					:	0							            													,	#?	fourth resistance value
							},
                            'Netlist'       :   {                                                                                                           #!  SPICE netlist parameters
									'File'              :   Netlistpath                                                                                 ,   #?  netlist file directory location
									'Type'              :   1                                                                                           ,   #?  description type, 1->.subckt | 2->.model
									'Name'              :   'KPZ1608SHR221ATD25_p'                                                                          #?  spice model name as it appears in the netlist file
							},
					}

#?----------------------------------------------------------------------------------------------------------------------------------------------------------------------

#!	assemble all beads to be transferred to the PLECS model
#?----------------------------------------------------------------------------------------------------------------------------------------------------------------------

AllFerriteBeads	=	{
						'BLM21PG220SH1'			:	BLM21PG220SH1			,
						'BLM31PG601SH1'			:	BLM31PG601SH1			,
                        'KPZ1608SHR221ATD25'	:	KPZ1608SHR221ATD25		,
					}
#?----------------------------------------------------------------------------------------------------------------------------------------------------------------------
