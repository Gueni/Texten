
#?-------------------------------------------------------------------------------------------------------------------------------------------------------------
#?                                                                ____            ____  _       _
#?                                                               |  _ \ _   _    |  _ \| | ___ | |_
#?                                                               | |_) | | | |   | |_) | |/ _ \| __|
#?                                                               |  __/| |_| |   |  __/| | (_) | |_
#?                                                               |_|    \__, |___|_|   |_|\___/ \__|
#?                                                                      |___/_____|
#?-------------------------------------------------------------------------------------------------------------------------------------------------------------
import assets.Dependencies as dp
#?-------------------------------------------------------------------------------------------------------------------------------------------------------------
class HTML_REPORT:
    def __init__(self,ResultsPath='',utc=''):
        """
        Initialize the HTML_REPORT class with various attributes and load configuration data from a JSON file.
        """
        self.ResultsPath                =   ResultsPath                                                                                                                 #? Path to store results
        self.utc                        =   utc                                                                                                                         #? UTC timestamp string
        self.title                      =   f"{dp.scriptname}_Report_{self.utc}_{str(dp.socket.gethostname())}"                                                        #? HTML page title template

        self.tab_val_list               =   []                                                                                                                          #? List for table values
        self.iter_param_key             =   []                                                                                                                          #? List of iteration parameter keys
        self.iter_param_val             =   []                                                                                                                          #? List of iteration parameter values
        self.iter_param_unt             =   []                                                                                                                          #? List of iteration parameter units

        self.constants_list             =   []                                                                                                                          #? List of constant names
        self.constants_vals             =   []                                                                                                                          #? List of constant values
        self.constants_units            =   []                                                                                                                          #? List of constant units

    #?-------------------------------------------------------------------------------------------------------------------------------------------------------------
    #? TABLES
    #?-------------------------------------------------------------------------------------------------------------------------------------------------------------

    def mdlvar_params_table(self,i):
        """
            Generate plotly table figure for modelvar dictionary containing sub-dictionaries
            and simulation parameters for the current iteration.The layout also include a dropdown menu
            which helps select , interactively,which sub-dictionary to display. Defualt is all data.

            Parameters  : i     (int)       : Number of the current iteration.
            Return      : fig   (object)    : Plotly figure : table.
        """
        dropdown_level      =   3
        dropdown_buttons    =   []
        data_dict           =   self.tab_val_list[i]

        def brackets_notation(d, parent_keys=None):
            """Flatten a nested dictionary using bracket notation"""
            if parent_keys is None:
                parent_keys = []

            items = []
            for k, v in d.items():
                current_keys = parent_keys + [k]
                if isinstance(v, dict):
                    items.extend(brackets_notation(v, current_keys))
                else:
                    # Create bracket notation: ["key1"]["key2"]["key3"]
                    bracket_path = ''.join([f'["{key}"]' for key in current_keys])
                    items.append((bracket_path, v))
            return items

        def get_paths_at_level(d, current_level=1, target_level=1, current_path=None):
            """Get dictionary paths at specified level"""
            if current_path is None: current_path = []
            paths   = []

            # If we've reached the target level, return current path as an option
            if current_level == target_level:
                if current_path:  # Only add if we have a path
                    path_str = "->".join(current_path)
                    paths.append(("->".join(current_path), current_path.copy()))
            else:
                # If we haven't reached target level yet, continue traversing
                for key, value in d.items():
                    if isinstance(value, dict):
                        new_path = current_path + [key]
                        paths.extend(get_paths_at_level(value, current_level + 1, target_level, new_path))

            # Always include "all" option at any level
            if current_level == 1: paths.insert(0, ("all", []))

            return paths

        def get_subdict_by_path(d, path_keys):
            """Get sub-dictionary by path keys"""
            if not path_keys: return d
            current = d
            for key in path_keys:
                if isinstance(current, dict) and key in current: current = current[key]
                else: return {}
            return current if isinstance(current, dict) else {path_keys[-1]: current}

        available_paths         = get_paths_at_level(data_dict, target_level=dropdown_level)
        flattened_items         = brackets_notation(data_dict)
        parameters              = [item[0] for item in flattened_items]
        values                  = [str(item[1]) for item in flattened_items]
        table                   = dp.plotly.graph_objects.Table(      header  =   dict(
                                                                    values      =   ['PARAMETERS', 'VALUE']                    ,
                                                                    fill_color  =   dp.headerColor                           ,
                                                                    align       =   'center'
                                                            ),
                                                    cells   =   dict(
                                                                    values      =   [parameters, values]                       ,
                                                                    align       =   ['left', 'left']
                                                            ),
                                                    domain  =   dict(x=[0, 1], y=[0, 0.9])  # Table occupies bottom 90%

                                        )

        for path_label, path_keys in available_paths:
            if path_label == "all": # Show all parameters
                flattened_items = brackets_notation(data_dict)
                params          = [item[0] for item in flattened_items]
                vals            = [str(item[1]) for item in flattened_items]
            else:   # Get specific sub-dictionary at the chosen level
                sub_dict        = get_subdict_by_path(data_dict, path_keys)
                if isinstance(sub_dict, dict) and sub_dict:
                    flattened_items = brackets_notation(sub_dict, path_keys)
                    params          = [item[0] for item in flattened_items]
                    vals            = [str(item[1]) for item in flattened_items]
                else:   # If it's not a dict or empty, show it as a single parameter
                    if path_keys:
                        bracket_path    = ''.join([f'["{key}"]' for key in path_keys])
                        params          = [bracket_path]
                        vals            = [str(sub_dict)]
                    else:
                        params          = []
                        vals            = []

            args=[{"cells": {
                                    "values": [params, vals]  ,
                                    "align"       :   ['left', 'left']                           ,
                                    "line_color"  :   'darkslategray'
                                    }}]
            dropdown_buttons.append(dict(label=path_label,method="update",args=args))


        fig = dp.plotly.graph_objects.Figure(data=[table])

        # Layout with clear section separation
        fig.update_layout(
            height          =   500,
            margin          =   dict(t=10, l=20, r=20, b=10),
            plot_bgcolor    =   'white',
            paper_bgcolor   =   'white',
            updatemenus     =   [dict(
                                        buttons     =   dropdown_buttons,
                                        direction   =   "down",
                                        showactive  =   True,
                                        x           =   0.0,
                                        xanchor     =   "left",
                                        y           =   0.95,
                                        yanchor     =   "middle",
                                        bgcolor     =   "white",
                                        bordercolor =   "#2E86AB",
                                        borderwidth =   1,
                                        font        =   dict(size=12),
                                        active      =   0
                                    )
                                ]
        )

        return fig

    def operational_params_table(self,csv_file):
        """
            Reads in a CSV file containing data and creates a table of constants by taking the mean values of certain columns.
            The columns to use are defined in a constant dictionaries list. The resulting table is displayed using Plotly,
            a Python visualization library, and returned.

            Parameters  :   csv_file (str)      : The path to a CSV file containing the data to use for calculating the constants.
            Return      :   fig   (object)      : A Plotly figure object representing the constant table.
        """

        # Read in the CSV file and create a DataFrame
        df                      =   dp.pd.read_csv(csv_file)

        # Loop through the constant dictionaries and calculate the mean values for each column
        # Append the constant names, values, and units to separate lists
        for _ , val in dp.constant_dict.items():
            column_values = df.iloc[:, val[1]]
            column_values = column_values.to_numpy()
            column_values = column_values[-50:]
            self.constants_list.append(val[0])
            self.constants_vals.append(dp.np.mean(column_values).round(2))
            self.constants_units.append(val[2])

        # Create a Plotly table to display the constants
        # Use alternating row colors for better readability and set header color
        # set table layout and title
        constants_tab           =   dp.plotly.graph_objects.Table(    header  =   dict(
                                                                values      =   ['PARAMETER','VALUE','UNIT']                                      ,
                                                                fill_color  =   dp.headerColor                                                  ,
                                                                font_size   =   12                                                                ,
                                                                align       =   'center'
                                                            ),

                                                    cells   =   dict(
                                                                values      =   [self.constants_list,self.constants_vals,self.constants_units]    ,
                                                                align       =   ['left', 'center']
                                                            )
                                        )

        # Create a subplot to hold the table
        fig = dp.plotly.graph_objects.Figure(data=[constants_tab])

        # Layout with clear section separation
        fig.update_layout(
            height          =   450 ,
                        margin          =   dict(t=30, l=20, r=20, b=30)
        )

        return fig

    def focused_params_table(self,i=0):
        """
            Generate plotly table figure for the focusedparameters dictionary for the current iteration.

            Parameters  : i     (int)       : Number of the current iteration.
            Return      : fig   (object)    : Plotly figure : table.
        """
        #* Focused parameters values table-------------------------------------
        # Create a Plotly table to display the focused parameters
        updated_vals_table       =   dp.plotly.graph_objects.Table(    header  =   dict(
                                                                values      =   ['FOCUSED PARAMETERS', 'VALUE','UNIT']                      ,
                                                                fill_color  =   dp.headerColor                                     ,
                                                                align       =   'center'
                                                            ),

                                                    cells   =   dict(   values      =  [self.iter_param_key[i], self.iter_param_val[i] ,self.iter_param_unt[i]],
                                                                align       =   ['left', 'left'] ,
                                                            )
                                        )

        fig = dp.plotly.graph_objects.Figure(data=[updated_vals_table])

        # Layout with clear section separation
        fig.update_layout(
            height=200,
            margin          =   dict(t=30, l=20, r=20, b=20)
        )
        return fig

    #?-------------------------------------------------------------------------------------------------------------------------------------------------------------
    #? PLOTS
    #?-------------------------------------------------------------------------------------------------------------------------------------------------------------

    def multiplot(self,csv_file):
        """
        Generate a plot of voltage and current data from a Plecs simulation output file.
        This function reads voltage and current data from a CSV file generated by a Plecs simulation.
        The data is assumed to be organized in columns, with the first column containing the time values.
        The function generates a plot with two y-axes, one for the current data and one for the voltage data.
        The plot includes a menu that allows the user to toggle the display of the current and voltage data.

        Args:
            csv_file (str): The path to the CSV file containing the data.

        Returns:
            A plotly.graph_objs._figure.Figure object representing the plot.

        Raises:
            FileNotFoundError: If the specified CSV file does not exist.
        """

        # Genarate dataframe from csv file.
        # Retrieve data index dictionaries from plecs_mapping module.
        # Get keys from previously defined dictionaries (to be used as labels)
        dff                     = dp.pd.read_csv(csv_file)
        Voltages_labels_dict    = dp.pmap_multi['Peak_Voltages']
        Currents_labels_dict    = dp.pmap_multi['Peak_Currents']
        PWM_labels_dict         = dp.pwm_dict
        voltage_keys            = list(Voltages_labels_dict.keys())
        Current_keys            = list(Currents_labels_dict.keys())
        PWM_keys                = list(PWM_labels_dict.keys())
        fig                     = dp.make_subplots(specs=[[{"secondary_y": True}]])

        # Create and add Traces for th Current Plots.
        for each in Current_keys:fig.add_trace(dp.plotly.graph_objects.Scatter(x= dff.iloc[:,0],y= dff.iloc[:,Currents_labels_dict.get(each)],name= each,mode= "lines",line= dict(shape = 'linear', dash = 'dot')),secondary_y=False)

        # Create and add Traces for th Voltage Plots.
        for each in voltage_keys:fig.add_trace(dp.plotly.graph_objects.Scatter(x= dff.iloc[:,0],y= dff.iloc[:,Voltages_labels_dict.get(each)],name= each,mode= "lines",line= dict(shape = 'linear')),secondary_y=True)

        # Create and add Traces for th PWM Plots.
        for each in PWM_keys:fig.add_trace(dp.plotly.graph_objects.Scatter(x= dff.iloc[:,0],y= dff.iloc[:,PWM_labels_dict.get(each)],name= each,mode= "lines+markers",line= dict(shape = 'linear', dash = 'dashdot')),secondary_y=True)

        # Define button for showing all plots.
        button_all          = dict(
                                    label   = 'CURRENTS & VOLTAGES & PWM'                                             ,
                                    method  = 'update'                                          ,
                                    args    = [{'visible'   :   [True for i in range(len(list(Currents_labels_dict.values())))]+ \
                                                                [True for j in range(len(list(Voltages_labels_dict.values())))]+ \
                                                                [True for j in range(len(list(Voltages_labels_dict.values())))],
                                                'title'     : 'CURRENTS & VOLTAGES & PWM'                             ,
                                                'showlegend': True
                                                }
                                            ],
                                    )
        # Define button for showing Current plots.
        button_curr          = dict(
                                    label   = 'CURRENTS'                                             ,
                                    method  = 'update'                                          ,
                                    args    = [{'visible'   :   [True for i in range(len(list(Currents_labels_dict.values())))]+ \
                                                                [False for j in range(len(list(Voltages_labels_dict.values())))]+ \
                                                                [False for j in range(len(list(Voltages_labels_dict.values())))],
                                                'title'     : 'CURRENTS'                             ,
                                                'showlegend': True
                                                }
                                            ],
                                    )
        # Define button for showing all plots.
        button_volt          = dict(
                                    label   = 'VOLTAGES'                                             ,
                                    method  = 'update'                                          ,
                                    args    = [{'visible'   :   [False for i in range(len(list(Currents_labels_dict.values())))]+ \
                                                                [True for j in range(len(list(Voltages_labels_dict.values())))]+ \
                                                                [False for j in range(len(list(Voltages_labels_dict.values())))],
                                                'title'     : 'VOLTAGES'                             ,
                                                'showlegend': True
                                                }
                                            ],
                                    )
        # Define button for showing PWM plots.
        button_pwm          = dict(
                                    label   = 'PWM SIGNALS'                                             ,
                                    method  = 'update'                                          ,
                                    args    = [{'visible'   :   [False for i in range(len(list(Currents_labels_dict.values())))]+ \
                                                                [False for j in range(len(list(Voltages_labels_dict.values())))]+ \
                                                                [True for j in range(len(list(Voltages_labels_dict.values())))],
                                                'title'     : 'PWM SIGNALS'                             ,
                                                'showlegend': True
                                                }
                                            ],
                                    )
        # Define button for showing PWM and voltages plots.
        button_pwm_volt          = dict(
                                    label   = 'PWM & VOLTAGES'                                             ,
                                    method  = 'update'                                          ,
                                    args    = [{'visible'   :   [False for i in range(len(list(Currents_labels_dict.values())))]+ \
                                                                [True for j in range(len(list(Voltages_labels_dict.values())))]+ \
                                                                [True for j in range(len(list(Voltages_labels_dict.values())))],
                                                'title'     : 'PWM SIGNALS & VOLTAGES'                             ,
                                                'showlegend': True
                                                }
                                            ],
                                    )
        # Define button for showing PWM and currentsplots.
        button_pwm_curr          = dict(
                                    label   = 'PWM & CURRENTS'                                             ,
                                    method  = 'update'                                          ,
                                    args    = [{'visible'   :   [True for i in range(len(list(Currents_labels_dict.values())))]+ \
                                                                [False for j in range(len(list(Voltages_labels_dict.values())))]+ \
                                                                [True for j in range(len(list(Voltages_labels_dict.values())))],
                                                'title'     : 'PWM SIGNALS & CURRENTS'                             ,
                                                'showlegend': True
                                                }
                                            ],
                                    )

        # Initialize and Define layout arguments for overall plots.Set titles, axis labels, colors, and background color.
        # Add the update menu with buttons to the layout.Set the initial visibility of all traces to True.
        fig.update_layout(
            height          =   500,
            margin          =   dict(t=20, l=20, r=20, b=20),
            updatemenus     =   [dp.plotly.graph_objects.layout.Updatemenu(active  = 0,buttons = [button_all,button_curr,button_volt,button_pwm,button_pwm_volt,button_pwm_curr],direction = 'up',x= 0,xanchor = 'left',y= -0.1,yanchor = 'top')],
            xaxis           =   dict(title='Time [ s ]')                            ,
            yaxis           =   dict(side= "left",title= "Current [ A ]",titlefont= dict(color="#1f77b4"),tickfont= dict(color="#1f77b4")),
            yaxis2          =   dict(side="right",title="Voltage [ V ]",titlefont=dict(color="#1f77b4"),tickfont=dict(color="#1f77b4")),
            plot_bgcolor    =   '#f8fafd'
            )

        return fig

    def plot_scopes(self,fName,odict,xticks=None,yticks=None,xaxis_range=None,yaxis_range=None,Legend=True,height = None):
        """
            Generates a list of subplots for the data in a CSV file, based on the specifications in the input dictionaries.

            Parameters
            ----------
            fName : str
                The path of the CSV file to read.
            odict : dict
                A dictionary of dictionaries specifying the data to plot in each subplot. The keys are the names of the subplots,
                and the values are dictionaries with the following keys:
                - 0: a list of strings, representing the names of the columns in the CSV file to plot on the y-axis.
                - 1: a list of strings, representing the names of the traces to plot in each column.
                - 2: a list of integers, representing the indices of the columns in the CSV file to plot.
                - 3: a list of strings, representing the titles of the y-axes for each column.
            splt_titles : list of str
                A list of strings representing the titles of the subplots.
            xticks : float or None, optional
                The tick interval for the x-axis. If None, the default tick interval is used.
            yticks : float or None, optional
                The tick interval for the y-axis. If None, the default tick interval is used.
            xaxis_range : list of float or None, optional
                The range of values to display on the x-axis. If None, the default range is used.
            yaxis_range : list of float or None, optional
                The range of values to display on the y-axis. If None, the default range is used.
            Legend          :       bool.
                                If True activates the legend in the figure, default is True.

            Returns
            -------
            list of plotly.graph_objs._figure.Figure
                A list of subplots, each represented as a Plotly Figure object.

            Raises
            ------
            FileNotFoundError
                If the specified CSV file does not exist.
        """

        # Initialize an empty list to hold the figures
        # Read the CSV file into a Pandas DataFrame
        figure_list     = []
        df              = dp.pd.read_csv(fName)

        # Loop through the input dictionary and create a subplot for each key
        # Set the titles, axis labels, and other properties of the subplot
        for key, _ in odict.items():
                titles      = [odict[key][x][1][0] for x in range(len(odict[key]))]
                fig         = dp.make_subplots(rows=len(odict[key]), cols=1,subplot_titles=titles,shared_xaxes=True,vertical_spacing=0.08)

                # Loop through the columns specified in the input dictionary and add traces to the subplot
                for j in range(len(odict[key])):
                    for i in range(len(odict[key][j][0])):
                        X,Y     =   df.iloc[:,0],df.iloc[:,odict[key][j][2][i]]

                        # Handle the case where all Y values are the same
                        # If all Y values are the same, only plot the first and last values
                        if len(set(Y)) == 1:
                            new_df = dp.pd.DataFrame({'X': [X.iloc[0], X.iloc[-1]], 'Y': [Y.iloc[0], Y.iloc[-1]]})
                            fig.add_trace(dp.plotly.graph_objects.Scatter(x=new_df['X'], y=new_df['Y'], name=odict[key][j][0][i]), row=j+1, col=1)

                        # Otherwise, plot all the Y values
                        else:
                            fig.add_trace(dp.plotly.graph_objects.Scatter(x=X, y=Y, name=odict[key][j][0][i]), row=j+1, col=1)

                    # Set the y-axis title and other properties for each subplot
                    fig['layout'][f'yaxis{j+1}']['title']= odict[key][j][3][i]

                # Set the x-axis title and other properties for the entire figure
                # Update the x-axis and y-axis ranges and tick intervals if specified
                fig['layout'][f'xaxis{j+1}']['title']= 'Time [s]'
                fig.update_xaxes(range=xaxis_range, dtick=xticks)
                fig.update_yaxes(range=yaxis_range, dtick=yticks)

                # If Legend is True, show the legend for the figure
                if Legend   ==  True:

                    # Special handling for DCDC_D configuration to always show legend
                    if dp.JSON['model'] == 'DCDC_D':
                        fig.update_layout(title={'text' : str(key) },showlegend = True)

                    # For other configurations, show legend only if there are multiple traces
                    else:
                        # Check if there are multiple traces in the subplot
                        # If there are multiple traces, show the legend else hide it
                        if len(odict[key])>1:
                            fig.update_layout(title={'text' : str(key) },showlegend = True)

                        else:
                            fig.update_layout(
                                            showlegend      =   False           ,
                                            plot_bgcolor    =   '#f8fafd'     ,
                                            yaxis2          =   dict(anchor='free',position=0,side='left')
                                            )
                else:

                    # If Legend is False, hide the legend for the figure
                    fig.update_layout(showlegend = False)

                # Set hover mode to "x unified" for better interactivity
                # Remove hover template to use default hover behavior
                # Add the figure to the list of figures
                fig.update_traces(hovertemplate=None)
                fig.update_layout(hovermode="x unified")
                if height is not None:  fig.update_layout(height=height)
                figure_list.append(fig)

        # Return the list of figures
        return figure_list

    def plot_std(self,csv_file):
        """
        Create Plotly figures from CSV standalone data with Time as x-axis and signals as y-axis (with header).

        Parameters  :   csv_file (str)  : Path to the CSV file
        Returns     :   list     (list) : List of Plotly figure objects
        """
        # Read CSV file and Get signal names (all columns except first)
        df                           = dp.pd.read_csv(csv_file)
        time_col   ,signal_names     = df.columns[0] ,df.columns[1:]
        figures                      = []
        units                        = [dp.unit_map[dp.pattern.search(" ".join(s.split()[-2:])).group().lower()] if dp.pattern.search(" ".join(s.split()[-2:])) else "[-]" for s in signal_names]

        # Create individual figure for each signal
        for i, (signal_name, unit) in enumerate(zip(signal_names, units)):
            fig = dp.plotly.graph_objects.Figure()
            fig.add_trace(dp.plotly.graph_objects.Scatter(x=df[time_col],y=df[signal_name],mode='lines',showlegend=False,line=dict(color='blue')))
            fig.update_layout(title=dp.re.sub(r'[^a-zA-Z0-9]', '_', signal_name) ,xaxis_title=time_col,yaxis_title=f"{unit}",template="plotly_white")
            figures.append(fig)

        return figures

    def fft_bar_plot(self,current_fft_csv="", voltage_fft_csv="", iteration=0,standalone_fft_map_path ="",headers=""):
        """
        Generate a bar plot of FFT magnitudes for current and voltage signals.

        Parameters  :
                            current_fft_csv      :         String
                                                            Path to the CSV file containing current data.
                            voltage_fft_csv      :         String
                                                            Path to the CSV file containing voltage data.
                            iteration            :         int
                                                            Iteration index.
            Returns        :  figure_list          :         list
                                                            List of plotly figures.
        """

        figure_list                   = []

        if dp.JSON['FFT'] and dp.standalone_exist and standalone_fft_map_path:

            df          = dp.pd.read_csv(standalone_fft_map_path, header=None,index_col=None)
            df.columns  = headers

            for col in headers:
                fig = dp.plotly.graph_objects.Figure()
                y_vals  = df[col].iloc[iteration * len(dp.harmonics): (iteration + 1) * len(dp.harmonics)]

                fig.add_trace(dp.plotly.graph_objects.Bar(
                                                            x           = dp.harmonics,
                                                            y           = y_vals.values,
                                                            name        = f'{col}',
                                                        ))
                fig.update_layout(
                                    title           =   f'FFT Magnitudes - {col}'                                   ,
                                    xaxis_title     =   'Harmonic Orders'                                           ,
                                    xaxis           =   dict (tickvals = dp.harmonics ,ticktext = dp.harmonics)     ,
                                    yaxis           =   dict(
                                                            side        = "left"                                    ,
                                                            title       = "Magnitude"                               ,
                                                            titlefont   = dict(color="#1f77b4")                   ,
                                                            tickfont    = dict(color="#1f77b4"))                  ,
                                    plot_bgcolor    =   '#f8fafd'                                                 ,
                                    barmode         =   'overlay'
                                )

                figure_list.append(fig)

        else :
            # Load current and voltage FFT headers from JSON.
            # Read current and voltage FFT CSV data into pandas DataFrames without headers or index columns.
            # Initialize an empty list to store generated Plotly figures.
            Current_headers               = dp.json.load(open((dp.os.getcwd()).replace("\\","/") + "/Script/assets/Headers/FFT_Current.json" , 'r'))
            Voltage_headers               = dp.json.load(open((dp.os.getcwd()).replace("\\","/") + "/Script/assets/Headers/FFT_Voltage.json" , 'r'))
            dfcurr                        = dp.pd.read_csv(current_fft_csv, header=None,index_col=None)
            dfvolt                        = dp.pd.read_csv(voltage_fft_csv, header=None,index_col=None)

            # Loop through each entry in dp.plt_title_list to create subplots.
            for i in range(len(dp.plt_title_list)):

                # Create a Plotly subplot with a secondary y-axis for combined current and voltage plotting.
                fig                   = dp.make_subplots(rows=1, cols=1,specs=[[{"secondary_y": True}]])

                # Determine the indices of current columns to plot from Current_headers based on plt_title_list structure.
                # Determine the indices of voltage columns to plot from Voltage_headers based on plt_title_list structure.
                current_idx_list      = [Current_headers.index(dp.plt_title_list[i][1] + " FFT")] if len(dp.plt_title_list[i])<5 else [ Current_headers.index(dp.plt_title_list[i][1] + " FFT") , Current_headers.index(dp.plt_title_list[i][2] + " FFT")  ]
                voltage_idx_list      = [Voltage_headers.index(dp.plt_title_list[i][2] + " FFT")] if len(dp.plt_title_list[i])<5 else [ Voltage_headers.index(dp.plt_title_list[i][3] + " FFT") , Voltage_headers.index(dp.plt_title_list[i][4] + " FFT")  ]

                # Extract the titles for current traces from plt_title_list.
                # Extract the titles for voltage traces from plt_title_list.
                current_titles        = [dp.plt_title_list[i][1]] if len(dp.plt_title_list[i])<5 else [dp.plt_title_list[i][1] , dp.plt_title_list[i][2]  ]
                voltage_titles        = [dp.plt_title_list[i][2]] if len(dp.plt_title_list[i])<5 else [dp.plt_title_list[i][3] , dp.plt_title_list[i][4]  ]

                # If FFT plotting is enabled in the JSON settings, add bar traces for current and voltage.
                # Current traces are plotted on the primary y-axis, and voltage traces on the secondary y-axis.
                # The data for each trace is sliced according to the current iteration and harmonics length.
                # If FFT plotting is disabled, return an empty list immediately.
                for c, name in enumerate(current_titles):fig.add_trace(dp.plotly.graph_objects.Bar(x=dp.harmonics, y=dfcurr.iloc[iteration * len(dp.harmonics): (iteration + 1) * len(dp.harmonics), current_idx_list[c]], name=name), row=1, col=1,secondary_y=False)
                for j, name in enumerate(voltage_titles):fig.add_trace(dp.plotly.graph_objects.Bar(x=dp.harmonics, y=dfvolt.iloc[iteration * len(dp.harmonics): (iteration + 1) * len(dp.harmonics), voltage_idx_list[j]], name=name), row=1, col=1,secondary_y=True)

                # Update the layout of the FFT figure with a title, axis labels, tick settings, and background color.
                # The primary y-axis shows current magnitudes and the secondary y-axis shows voltage magnitudes.
                # Bar traces are overlaid for comparison, and the configured figure is appended to figure_list.
                fig.update_layout(
                                    title           =   f'FFT Magnitudes - {dp.plt_title_list[i][0]}'               ,
                                    xaxis_title     =   'Harmonic Orders'                                           ,
                                    xaxis           =   dict (tickvals = dp.harmonics ,ticktext = dp.harmonics)     ,
                                    yaxis           =   dict(
                                                            side        = "left"                                    ,
                                                            title       = "Current Magnitude"                       ,
                                                            titlefont   = dict(color="#1f77b4")                     ,
                                                            tickfont    = dict(color="#1f77b4"))                    ,
                                    yaxis2          =   dict(
                                                            side        = "right"                                   ,
                                                            title       = "Voltage Magnitude"                       ,
                                                            titlefont   = dict(color="#1f77b4")                     ,
                                                            tickfont    = dict(color="#1f77b4"))                    ,
                                    plot_bgcolor    =   '#f8fafd'                                                   ,
                                    barmode         =   'overlay'
                                )
                figure_list.append(fig)

        return figure_list

    def barchart3D(self,x_vals, y_vals, z_vals, title, z_title, x_title, y_title, opacity=1):
        """
            Emulate the creation of a 3D bar chart in plotly using mesh3D.

            Parameters      :   x_vals  (array-like)    : array of X values.
                                y_vals  (array-like)    : array of Y values.
                                z_vals  (array-like)    : array of Z values.
                                title   (String)        : title of the plot.
                                z_title (String)        : z axis title.
                                x_title (String)        : x axis title.
                                y_title (String)        : y axis title.
                                opacity (float)         : cuboid opacity. default to 1.
            Return          :   fig     (object)        : plotly figure.
        """
        fig, ann                = dp.plotly.graph_objects.Figure(), []
        x_vals                  = dp.np.array(x_vals, dtype=int)
        y_vals, z_vals          = map(lambda arr: dp.np.array(arr, dtype=float),(y_vals, z_vals))
        x_unique ,y_unique      = dp.np.unique(x_vals) , dp.np.unique(y_vals)

        # Base spacing between unique points
        dx_base = dp.np.min(dp.np.diff(x_unique)) if len(x_unique) > 1 else 1.0
        dy_base = dp.np.min(dp.np.diff(y_unique)) if len(y_unique) > 1 else 1.0

        # Scale width inversely with the number of unique bars ==> if you have 20 bars, bars will be thinner than if you have 2
        nx, ny = len(x_unique), len(y_unique)
        scale_factor = 0.6 / dp.np.sqrt(max(nx, ny))

        # prevent being too thin
        dx = dx_base * (0.8 * scale_factor + 0.2)
        dy = dy_base * (0.8 * scale_factor + 0.2)

        # Keep small minimums to avoid division errors
        dx, dy = max(dx, 1e-6), max(dy, 1e-6)

        for i, z_max in enumerate(z_vals):
            x_cnt, y_cnt    = x_vals[i], y_vals[i]
            x_min, x_max    = x_cnt - dx/2, x_cnt + dx/2
            y_min, y_max    = y_cnt - dy/2, y_cnt + dy/2
            x               = [x_min, x_min, x_max, x_max, x_min, x_min, x_max, x_max]
            y               = [y_min, y_max, y_max, y_min, y_min, y_max, y_max, y_min]
            z               = [0, 0, 0, 0, z_max, z_max, z_max, z_max]

            # Visible bar
            fig.add_trace(dp.plotly.graph_objects.Mesh3d(x=x, y=y, z=z,alphahull=0,color="royalblue",showscale=False,opacity=opacity,hoverinfo='none'))

            # Transparent hover plane
            fig.add_trace(dp.plotly.graph_objects.Mesh3d(
                x=[x_min, x_max, x_max, x_min],
                y=[y_min, y_min, y_max, y_max],
                z=[z_max, z_max, z_max, z_max],
                color='rgba(0,0,0,0)',
                opacity=0.0,
                hovertemplate=(f"<b>{x_title}</b>: {x_cnt:.2f}<br>"f"<b>{y_title}</b>: {y_cnt:.2f}<br>"f"<b>{z_title}</b>: {z_max:.2f}<extra></extra>"),
                hoverlabel=dict(bgcolor='rgba(30,30,30,0.8)',font_color='white',bordercolor='white'),showlegend=False
                ))

        fig.update_layout(
            title=dict(text=title, x=0.5, xanchor='center', yanchor='top'),
            scene=dict(
                xaxis=dict(title=x_title,tickmode='array',tickvals=x_vals,ticktext=[str(int(v)) for v in x_vals],
                title_font=dict(size=10),tickfont=dict(size=10),autorange='reversed'),
                yaxis=dict(title=y_title,title_font=dict(size=10),tickfont=dict(size=10),autorange='reversed'),
                zaxis=dict(title=z_title,title_font=dict(size=10),tickfont=dict(size=10)),
                annotations=ann
                ),
            hoverlabel=dict(bgcolor='rgba(50,50,50,0.8)',font_color='white',bordercolor='white')
        )

        return fig

    #?-------------------------------------------------------------------------------------------------------------------------------------------------------------
    #? REPORTS
    #?-------------------------------------------------------------------------------------------------------------------------------------------------------------

    def iter_reports(self, report_type, **kwargs):
        """
        Unified method for generating iteration reports (signals, FFT, or standalone).

        Parameters:
            report_type (str): Type of report - 'signal', 'fft', or 'standalone'

            For 'signal' report_type:

                path (str)          : Path to directory containing CSV files
                label_dict (dict)   : Dictionary with column names as keys and indexes as values
                html_path (str)     : Path where HTML file should be saved
                Y_axis_label (str)  : Label for Y-axis
                type (str)          : Sets the type to current or voltage
                auto_open (bool)    : If True, opens HTML automatically

            For 'fft' report_type:

                FFT_file (str)      : FFT json header file
                title (str)         : Title to be included in the report
                csv_path (str)      : Path to the CSV file containing data
                html_path (str)     : Path to save the generated HTML report
                type (str)          : Sets the type to current or voltage
                auto_open (bool)    : If True, opens HTML automatically

            For 'standalone' report_type:

                csv_files (list)    : List of CSV standalone files
                html_path (str)     : Path where HTML file should be saved
                auto_open (bool)    : If True, opens HTML automatically
        """

        include_plotlyjs        = 'cdn'
        plot_items              = ''
        html_content            = self.prep_html_template(Time_series=False,Standalone=False)

        #?--------------------------------------------------------------------
        #? SIGNAL REPORTS
        #?--------------------------------------------------------------------

        if report_type == 'signal':

            path            = kwargs.get('path')
            label_dict      = kwargs.get('label_dict', {})
            html_path       = kwargs.get('html_path')
            Y_axis_label    = kwargs.get('Y_axis_label')
            report_subtype  = kwargs.get('type')
            auto_open       = kwargs.get('auto_open', False)
            labels_dict     = dict(label_dict)
            dict_keys       = list(labels_dict.keys())
            csv_files       = [f for f in dp.os.listdir(path) if f.endswith('.csv') and not f.endswith('_MAP.csv') and not f.endswith('_Standalone.csv')]

            if len(csv_files) >= 1:

                csv_files   = dp.natsort.natsorted(csv_files)
                dfs         = [dp.pd.read_csv(dp.os.path.join(path, f)) for f in csv_files]
                fig_list    = []

                for each in dict_keys:

                    fig = dp.make_subplots()
                    for C, df in enumerate(dfs, 1):
                        fig.add_trace(
                            dp.plotly.graph_objects.Scatter(
                                            x       =   df.iloc[:, 0]                           ,
                                            y       =   df.iloc[:, labels_dict.get(each)]       ,
                                            # name    =   str("Iter :" + str(C) + " | ") + each   ,
                                            name    =   str("Iter : " + str(C))                 ,
                                            mode    =   "lines"                                 ,
                                            line    =   dict(shape='linear')
                                        )
                                    )
                        fig.update_layout(
                                            showlegend      =   True                                                                                                    ,
                                            title           =   each                                                                                                    ,
                                            xaxis           =   dict(title='Time [ s ]')                                                                                ,
                                            yaxis           =   dict(side="left", title=Y_axis_label,titlefont=dict(color="#1f77b4"),tickfont=dict(color="#1f77b4")),
                                            plot_bgcolor    = '#f8fafd'
                                        )
                    fig_list.append(fig)

                # If 'iterSplit' is enabled in the JSON settings, a separate HTML report is generated for each key.
                if dp.iterSplit:
                    for i in range(len(dict_keys)):
                        plot_items      =  fig_list[i].to_html(full_html=False, include_plotlyjs=include_plotlyjs)
                        html_content    = self.prep_html_template(Time_series=False,Standalone=False) # Get FRESH HTML template for each file
                        html_content    = html_content.replace("{{PLOT_ITEMS}}", plot_items)
                        with open(html_path + "_" + dict_keys[i] + ".html", 'w', encoding='utf-8') as file: file.write(html_content)
                        file.close()

                # If 'iterSplit' is disabled in the JSON settings, a single consolidated HTML report is generated.
                #! for developer only
                else :
                    for fig_i in fig_list:
                        plot_items      +=  fig_i.to_html(full_html=False, include_plotlyjs=include_plotlyjs)
                    html_content = html_content.replace("{{PLOT_ITEMS}}", plot_items)
                    with open(html_path + "_" + str(report_subtype) + ".html", 'w', encoding='utf-8') as file: file.write(html_content)
                    file.close()

        #?--------------------------------------------------------------------
        #? FFT REPORTS
        #?--------------------------------------------------------------------

        elif report_type == 'fft':

            FFT_file        = kwargs.get('FFT_file')
            title           = kwargs.get('title', '')
            csv_path        = kwargs.get('csv_path')
            html_path       = kwargs.get('html_path')
            report_subtype  = kwargs.get('type')
            auto_open       = kwargs.get('auto_open', False)

            if dp.JSON["model"] :
                headers_path    = (dp.os.getcwd()).replace("\\", "/") + f"/Script/assets/Headers/{FFT_file}"
                headers         = dp.json.load(open(headers_path, 'r'))

            else :
                headers = dp.std_headers[1:]

            df              = dp.pd.read_csv(csv_path, header=None, index_col=None)
            num_iterations  = df.shape[0] // len(dp.harmonics)
            figure_list     = []

            # Generate figures for each column
            for column in range(df.shape[1]):

                fig = dp.plotly.graph_objects.Figure()

                for iteration in range(num_iterations):
                    start_idx       = iteration * len(dp.harmonics)
                    end_idx         = (iteration + 1) * len(dp.harmonics)
                    iteration_data  = df.iloc[start_idx:end_idx, column]

                    fig.add_trace(
                                    dp.plotly.graph_objects.Bar(
                                        x       =   dp.harmonics                                            ,
                                        y       =   iteration_data                                          ,
                                        # name    =   f'{headers[column]} {title} : Iteration {iteration + 1}'
                                        name    =   f'Iter : {iteration + 1}'
                                    )
                                )

                fig.update_layout(
                                    title       =   f'FFT Magnitudes - {headers[column]}'                   ,
                                    showlegend  =   True                                                    ,
                                    xaxis_title =   'Harmonic Orders'                                       ,
                                    yaxis_title =   'Magnitude'                                             ,
                                    xaxis       =   dict(tickvals=dp.harmonics, ticktext=dp.harmonics)      ,
                                    barmode     =   'stack'
                                )

                figure_list.append(fig)

                # If 'iterSplit' is enabled, create a separate HTML report for each FFT column.
                if dp.iterSplit:
                    # Get FRESH plot_items and html_content for EACH file
                    plot_items      = fig.to_html(full_html=False, include_plotlyjs=include_plotlyjs)
                    html_content    = self.prep_html_template(Time_series=False,Standalone=False)
                    html_content    = html_content.replace("{{PLOT_ITEMS}}", plot_items)
                    if dp.JSON["model"]:
                        file_path       = html_path + "_" + str(headers[column]) + ".html"
                    else :
                        file_path       = html_path + "_Standalone_" + str(headers[column]) + "_FFT.html"

                    with open(file_path, 'w', encoding='utf-8') as file: file.write(html_content)

            # If 'iterSplit' is disabled in the JSON settings, a single consolidated HTML report is generated.
            #! for developer only
            if not dp.iterSplit:
                plot_items      = ''
                for fig_i in figure_list:
                    plot_items += fig_i.to_html(full_html=False, include_plotlyjs=include_plotlyjs)
                html_content    = self.prep_html_template(Time_series=False,Standalone=False)
                html_content    = html_content.replace("{{PLOT_ITEMS}}", plot_items)
                file_path       = html_path + "_" + report_subtype + ".html"
                with open(file_path, 'w', encoding='utf-8') as file: file.write(html_content)

        #?--------------------------------------------------------------------
        #? STANDALONE  SIGNAL REPORTS
        #?--------------------------------------------------------------------

        elif report_type == 'standalone':

            csv_files   = kwargs.get('csv_files')
            html_path   = kwargs.get('html_path')
            auto_open   = kwargs.get('auto_open', False)

            if len(csv_files) >= 1:
                dfs     = [dp.pd.read_csv(f) for f in csv_files]

                if dfs:
                    all_columns     = dfs[0].columns.tolist()
                    # Skip the first column (assuming it's time/x-axis)
                    plot_columns    = all_columns[1:] if len(all_columns) > 1 else all_columns
                    plot_columns    = [dp.re.sub(r'[^a-zA-Z0-9]', '_', each) for each in plot_columns]
                    fig_list        = []

                    for each in plot_columns:
                        fig         = dp.make_subplots()
                        C=1
                        for df in dfs:
                            # Clean column names
                            df.columns = [dp.re.sub(r'[^a-zA-Z0-9]', '_', col) for col in df.columns]
                            signal_units = [dp.unit_map[dp.pattern.search(" ".join(s.split()[-2:])).group().lower()] if dp.pattern.search(" ".join(s.split()[-2:])) else "[-]" for s in df.columns.values]
                            # Find which column index 'each' corresponds to in the current dataframe
                            col_idx      = df.columns.get_loc(each) if each in df.columns else 1
                            fig.add_trace(
                                    dp.plotly.graph_objects.Scatter(
                                                    x       =   df.iloc[:, 0]                           ,
                                                    y       =   df[each]                                ,
                                                    # name    =   str("Iter :" + str(C) + " | ") + each   ,
                                                    name    =   str("Iter :" + str(C))                  ,
                                                    mode    =   "lines"                                 ,
                                                    line    =   dict(shape='linear')
                                                )
                                        )

                            fig.update_layout(
                                                showlegend  =   True                                                                                                            ,
                                                title       =   each                                                                                                            ,
                                                xaxis       =   dict(title='Time [s]')                                                                                          ,
                                                yaxis       =   dict(side="left", title=signal_units[col_idx],titlefont=dict(color="#1f77b4"),tickfont=dict(color="#1f77b4"))   ,
                                                plot_bgcolor=   '#f8fafd'
                                            )
                            C += 1
                        fig_list.append(fig)

                    # If 'iterSplit' is enabled in the JSON settings, a separate HTML report is generated for each key.
                    if dp.iterSplit:
                        for i in range(len(plot_columns)):

                            plot_items      =  fig_list[i].to_html(full_html=False, include_plotlyjs=include_plotlyjs)
                            html_content    = self.prep_html_template(Time_series=False,Standalone=False)
                            html_content    = html_content.replace("{{PLOT_ITEMS}}", plot_items)
                            with open(html_path + "_Standalone_" + plot_columns[i] + ".html", 'w', encoding='utf-8') as file: file.write(html_content)
                            file.close()

                    # If 'iterSplit' is disabled in the JSON settings, a single consolidated HTML report is generated.
                    #! for developer only
                    if not dp.iterSplit:
                        for fig_i in fig_list:
                            plot_items      +=  fig_i.to_html(full_html=False, include_plotlyjs=include_plotlyjs)
                        html_content = html_content.replace("{{PLOT_ITEMS}}", plot_items)
                        with open(html_path + "_Standalone_Iterations.html", 'w', encoding='utf-8') as file: file.write(html_content)
                        file.close()

        # If auto_open is enabled, the generated HTML report is automatically opened in the default web browser.
        if auto_open: dp.webbrowser.open(dp.pathlib.Path(html_path).absolute().as_uri())

    def format_fixed_title(self,fixed_dict, sweepNames=[]):
        """
        Format the fixed title in the same way as dropdown case

        Args:
            fixed_dict (dict)   : dictionary of the fixed Xlists.
            sweepNames (list)   : list of sweep names. Defaults to [].

        Returns:
            Str :   title of the fixed variables for that plot.
        """
        Title = "<br>".join(" | ".join(f"{sweepNames[int(''.join(filter(str.isdigit, k)))-1]} = {v}" for k, v in list(fixed_dict.items())[j:j+2]) for j in range(0, len(fixed_dict), 2))
        return Title

    def write_html_report(self,html_file, plots):
        """
        Export interactive Plotly figures to a styled HTML report with logo, metadata, and optional multi-figure layout.

        Args:
            html_file   (str) : path to the current html file.
            plots       (list): list of the current plots.
        """
        plot_items        =   ''
        html_content      =   self.prep_html_template(Time_series = False)
        plot_items        +=  '<div class="plot-container">\n'

        for i, fig in enumerate(plots):

                # Set figure height for consistency
                fig.update_layout(height=720, margin=dict(t=50, b=50, l=50, r=50))
                fig_html    = dp.plotly.io.to_html(fig, include_plotlyjs='cdn', full_html=False, div_id=f"plot-{i}")
                plot_items += f'<div class="plot-item">{fig_html}</div>\n'

        # Replace plot items
        plot_items  += '</div>\n'
        html_content = html_content.replace("{{PLOT_ITEMS}}", plot_items)

        # Write the populated HTML
        with open(html_file, 'w', encoding='utf-8') as file: file.write(html_content)
        file.close()

    def WCA_graphs(self,signal_matrices,fft_matrices,filelog):
        """
            Generate Iteration scatter plots one HTML per signal
                Each HTML   :
                                one figure per category (AVG, RMS, ...)
                                one FFT figure  : x=harmonic, y=magnitude,all iterations overlaid as separate bar
        Args:
            signal_matrices (dict)  : signal matrices dict
            fft_matrices    (dict)  : fft matrices dict
            filelog         (obj)   : pylog object
        """

        #?------------------------------------------------
        #? Build per_signal dict from signal matrices {base_signal_name: {category: {x, y}}}
        #?------------------------------------------------
        per_signal = {}

        for csv_key, (matrix, headers) in signal_matrices.items():
            if matrix is None or matrix.shape[0] == 0   :   continue

            # Derive category label from csv_key
            category = csv_key.replace('Standalone_', '') if dp.standalone_exist else csv_key
            n_iters  = matrix.shape[0]

            for col_idx, header in enumerate(headers):
                # Extract base signal name
                # standalone: 'I_L1_AVG'.rsplit('_',1)[0] -> 'I_L1'
                # normal    : header IS the base name already
                base_name = header.rsplit('_', 1)[0] if dp.standalone_exist else header

                if base_name not in per_signal  : per_signal[base_name] = {}
                per_signal[base_name][category] = {'x': list(range(1,n_iters+1)),'y': matrix[:, col_idx].tolist()}

        #?------------------------------------------------
        #? Build per_signal_fft dict from FFT matrices {base_signal_name: [{'x': harmonics, 'y': magnitudes, 'name': iter_label}]}
        #?------------------------------------------------
        per_signal_fft = {}

        if dp.JSON['FFT'] and fft_matrices:
            n_harmonics     = len(dp.harmonics)
            harmonic_orders = list(range(n_harmonics))

            for csv_key, (matrix, headers) in fft_matrices.items():
                if matrix is None or matrix.shape[0] == 0   :   continue
                n_combos                                    =   matrix.shape[0] // n_harmonics

                for col_idx, header in enumerate(headers):
                    base_name                           =   header.rsplit('_', 1)[0] if dp.standalone_exist else header
                    if base_name not in per_signal_fft  :   per_signal_fft[base_name] = []

                    # One trace per iteration rows are interleaved as   :   combo_0_harm_0, combo_0_harm_1, ..., combo_1_harm_0, ...
                    for combo_idx in range(n_combos):
                        row_start                       =   combo_idx * n_harmonics
                        row_end                         =   row_start + n_harmonics
                        if row_end > matrix.shape[0]    :   break
                        magnitudes                      =   matrix[row_start:row_end, col_idx].tolist()
                        per_signal_fft[base_name].append({'x'   : harmonic_orders,'y'   : magnitudes,'name': f"Iter {combo_idx+1}"})

        #?------------------------------------------------
        #? Write one HTML per signal figures in order: signal categories then FFT
        #?------------------------------------------------
        all_signal_names = set(per_signal.keys()) | set(per_signal_fft.keys())

        for base_name in all_signal_names:
            signal_plots = []

            # One figure per category (AVG, RMS, MAX ...) x=iteration y=value
            if base_name in per_signal:
                for category, data in per_signal[base_name].items():
                    fig = dp.plotly.graph_objects.Figure()
                    fig.add_trace(dp.plotly.graph_objects.Scatter(
                                                                    x       = data['x']                ,
                                                                    y       = data['y']                ,
                                                                    mode    = 'markers'                ,
                                                                    name    = base_name                ,
                                                                    marker  = dict(size=8)
                                                                )
                                  )

                    fig.update_layout(
                                        title       = dict(text=f"{base_name} : {category}", x=0.5) ,
                                        xaxis_title = 'Iteration'                                   ,
                                        yaxis_title = base_name                                     ,
                                        height      = 500                                           ,
                                        margin      = dict(t=80)
                                    )

                    signal_plots.append(fig)

            # One FFT figure : x=harmonic order, y=magnitude, one trace per iteration
            if base_name in per_signal_fft:
                fig = dp.plotly.graph_objects.Figure()

                for trace in per_signal_fft[base_name]:

                    fig.add_trace(dp.plotly.graph_objects.Bar(
                                                                x    = trace['x']                                   ,
                                                                y    = trace['y']                                   ,
                                                                name = trace['name']
                                                            )
                                  )

                fig.update_layout(
                                    title           =   dict(text=f"{base_name} : FFT", x=0.5)                      ,
                                    xaxis_title     =   'Harmonic Order'                                            ,
                                    xaxis           =   dict (tickvals = dp.harmonics ,ticktext = dp.harmonics)     ,
                                    yaxis           =   dict(
                                                            side        = "left"                                    ,
                                                            title       = "Magnitude"                               ,
                                                            titlefont   = dict(color="#1f77b4")                   ,
                                                            tickfont    = dict(color="#1f77b4"))                  ,
                                    plot_bgcolor    =   '#f8fafd'                                                 ,
                                    barmode         =   'overlay'
                                )
                signal_plots.append(fig)

            if signal_plots:
                html_path = dp.os.path.normpath(dp.os.path.join(f"{filelog.resultfolder}/HTML_GRAPHS/",f"HTML_GRAPH_{dp.re.sub(r'[^a-zA-Z0-9]', '_', base_name)}_{self.utc}.html")).replace('\\', '/')
                self.write_html_report(html_path, signal_plots)

    def graphs_scopes(self, filelog, Xs, MAPS_dir):
        """
        Generate 2D or 3D simulation plots (including FFT) from matrix and JSON data
        and export them as interactive HTML reports. Supports both single-variable
        2D plots and multi-variable 3D surfaces.

        Args  :
                fileLog         (object)    : fileLog class object.
        """

        #?--------------------------------------------------
        #? Load all data
        #?--------------------------------------------------
        self.get_headers(MAPS_dir)
        signal_matrices, fft_matrices   = self.load_matrices(MAPS_dir)

        if not signal_matrices and not fft_matrices :   return

        #?--------------------------------------------------
        #? Generate Graphs in WCA case
        #?--------------------------------------------------
        if dp.mode_sim.upper() == 'WCA' :

            self.WCA_graphs(signal_matrices,fft_matrices,filelog)

        #?--------------------------------------------------
        #? Generate Graphs for other cases
        #?--------------------------------------------------
        else   :
            #?--------------------------------------------------
            #? Get sweep configuration from JSON
            #?--------------------------------------------------
            sweep_vars      = self.get_sweep_vars(Xs)
            sweep_keys      = list(sweep_vars.keys())
            sweep_names     = dp.JSON["sweepNames"]

            #?--------------------------------------------------
            #? Determine if 2D or 3D
            #?--------------------------------------------------
            active_sweeps   = [k for k, v in sweep_vars.items() if len(v) > 1]
            is_2d           = len(active_sweeps) < 2
            var1, var2      = dp.JSON["Var1"], dp.JSON["Var2"]

            #?--------------------------------------------------
            #? Get X and Y indices
            #?--------------------------------------------------
            if is_2d:
                x_key       = active_sweeps[0]
                fixed_keys  = [k for k in sweep_keys if k != x_key]
                x_idx       = sweep_keys.index(x_key)
                y_idx       = None
            else:
                x_key,y_key = var1, var2
                fixed_keys  = [k for k in sweep_keys if k not in [x_key, y_key]]
                x_idx       = sweep_keys.index(x_key) if x_key in sweep_keys else -1
                y_idx       = sweep_keys.index(y_key) if y_key in sweep_keys else -1

            #?--------------------------------------------------
            #? Build sweep combinations
            #?--------------------------------------------------
            is_permute      = dp.JSON["permute"]
            if is_permute:
                all_combos  = list(dp.itertools.product(*sweep_vars.values()))
            else:
                values_list = list(sweep_vars.values())
                max_len     = max(len(v) for v in values_list) if values_list else 0
                all_combos  = []

                for i in range(max_len):
                    combo   = tuple(v[i] if i < len(v) else v[-1] for v in values_list)
                    all_combos.append(combo)


            #?--------------------------------------------------
            #? Process signal matrices
            #?--------------------------------------------------
            for matrix_name, (matrix, headers) in signal_matrices.items():
                if matrix is None or matrix.shape[1] == 0   :   continue

                for col_idx, component in enumerate(headers):
                    component_plots = []
                    fixed_groups    = {}

                    for combo_idx, combo in enumerate(all_combos):
                        if combo_idx >= matrix.shape[0] :   break

                        fixed_tuple = tuple(combo[sweep_keys.index(k)] for k in fixed_keys) if fixed_keys else ()

                        if fixed_tuple not in fixed_groups:
                            fixed_groups[fixed_tuple]   =   {'x': [], 'z': []}
                            if not is_2d                :   fixed_groups[fixed_tuple]['y'] = []

                        if is_2d:
                            fixed_groups[fixed_tuple]['x'].append(combo[x_idx])
                            fixed_groups[fixed_tuple]['z'].append(matrix[combo_idx, col_idx])
                        else:
                            fixed_groups[fixed_tuple]['x'].append(combo[x_idx])
                            fixed_groups[fixed_tuple]['y'].append(combo[y_idx])
                            fixed_groups[fixed_tuple]['z'].append(matrix[combo_idx, col_idx])

                    for fixed_tuple, data in fixed_groups.items():
                        if not data['z']:continue

                        fixed_dict = {}
                        if fixed_keys and fixed_tuple:
                            for i, k in enumerate(fixed_keys):
                                if i < len(fixed_tuple):    fixed_dict[k] = fixed_tuple[i]

                        fixed_title = self.format_fixed_title(fixed_dict, sweep_names) if fixed_dict else ""
                        title       = f"{component}<br>{fixed_title}" if fixed_title else component
                        if is_2d:
                            fig = self.create_2d_plot(data, component, title, x_key, sweep_names)
                        else:
                            fig = self.create_3d_plot(data, component, title, x_key, y_key, sweep_names, is_permute)
                        if fig:
                            component_plots.append(fig)

                    if component_plots:
                        safe_name = dp.re.sub(r'[^a-zA-Z0-9]', '_', component)
                        html_path = dp.os.path.normpath(dp.os.path.join(f"{filelog.resultfolder}/HTML_GRAPHS/", f"HTML_GRAPH_{safe_name}_{self.utc}.html")).replace('\\', '/')
                        self.write_html_report(html_path, component_plots)

            #?------------------------------------------------
            #? Process FFT matrices if enabled
            #?------------------------------------------------
            if dp.JSON['FFT'] and fft_matrices:

                fft_combos = list(map(tuple, dp.np.repeat(all_combos, len(dp.harmonics), axis=0)))

                for matrix_name, (matrix, headers) in fft_matrices.items():
                    if matrix is None or matrix.shape[1] == 0   :   continue

                    for col_idx, component in enumerate(headers):
                        component_plots = []

                        #?-------------------------------------------------------------
                        #? 2D FFT
                        #?-------------------------------------------------------------
                        if is_2d:
                            #?-------------------------------------------
                            #? 2D Case  : x=harmonic, y=magnitude
                            #? One figure per fixed sweep combination
                            #?-------------------------------------------
                            fixed_groups = {}

                            for combo_idx, combo in enumerate(fft_combos):
                                if combo_idx >= matrix.shape[0] :   break

                                harmonic_idx    = combo_idx % len(dp.harmonics)
                                harmonic_order  = harmonic_idx + 1
                                fixed_tuple     = tuple(combo[sweep_keys.index(k)] for k in fixed_keys) if fixed_keys else ()

                                if fixed_tuple not in fixed_groups  :   fixed_groups[fixed_tuple] = {'x': [], 'z': []}

                                fixed_groups[fixed_tuple]['x'].append(harmonic_order)
                                fixed_groups[fixed_tuple]['z'].append(matrix[combo_idx, col_idx])

                            # Build 2D bar charts
                            for fixed_tuple, data in fixed_groups.items():
                                if not data['z']    :   continue

                                fixed_dict = {}
                                if fixed_keys and fixed_tuple:
                                    for i, k in enumerate(fixed_keys):
                                        if i < len(fixed_tuple) :   fixed_dict[k] = fixed_tuple[i]

                                fixed_title = self.format_fixed_title(fixed_dict, sweep_names) if fixed_dict else ""
                                fig         = dp.plotly.graph_objects.Figure()

                                fig.add_trace(dp.plotly.graph_objects.Bar(x = data['x'], y = data['z'], name = component))
                                fig.update_layout(
                                                    title       = dict(text=f"{component}<br>{fixed_title}" if fixed_title else component, x=0.5)   ,
                                                    xaxis_title = 'Harmonic Order'                                                                  ,
                                                    yaxis_title = 'Magnitude'                                                                       ,
                                                    height      = 500                                                                               ,
                                                    margin      = dict(t=80)
                                                )
                                component_plots.append(fig)

                        #?-------------------------------------------------------------
                        #? 3D FFT
                        #?-------------------------------------------------------------
                        else:
                            # Set 1         : var1 varies (x=harmonic, y=var1, z=magnitude)
                            # Grouped by    : fixed vars + var2
                            var1_groups = {}

                            # Set 2         : var2 varies (x=harmonic, y=var2, z=magnitude)
                            # Grouped by    : fixed vars + var1
                            var2_groups = {}

                            for combo_idx, combo in enumerate(fft_combos):
                                if combo_idx >= matrix.shape[0]:break

                                harmonic_idx    = combo_idx % len(dp.harmonics)
                                harmonic_order  = harmonic_idx + 1
                                fixed_tuple     = tuple(combo[sweep_keys.index(k)] for k in fixed_keys) if fixed_keys else ()

                                #*-------------------------------------------
                                #* Set 1        : var1 as y-axis
                                #* x = harmonic, y = var1, z = magnitude
                                #* Grouped by   : fixed vars + var2
                                #*-------------------------------------------
                                if not is_2d and x_idx != -1:
                                    # Group key = (var2_value, fixed_tuple)
                                    group_key   = (combo[y_idx],) + fixed_tuple

                                    if group_key not in var1_groups:
                                        var1_groups[group_key] = {'x': [], 'y': [], 'z': []}

                                    var1_groups[group_key]['x'].append(harmonic_order)
                                    var1_groups[group_key]['y'].append(combo[x_idx])                # var1 is the y-axis
                                    var1_groups[group_key]['z'].append(matrix[combo_idx, col_idx])

                                #*-------------------------------------------
                                #* Set 2        : var2 as y-axis
                                #* x = harmonic, y = var2, z = magnitude
                                #* Grouped by   : fixed vars + var1
                                #*-------------------------------------------
                                if not is_2d and y_idx != -1:
                                    # Group key = (var1_value, fixed_tuple)
                                    group_key   = (combo[x_idx],) + fixed_tuple

                                    if group_key not in var2_groups:
                                        var2_groups[group_key] = {'x': [], 'y': [], 'z': []}

                                    var2_groups[group_key]['x'].append(harmonic_order)
                                    var2_groups[group_key]['y'].append(combo[y_idx])                # var2 is the y-axis
                                    var2_groups[group_key]['z'].append(matrix[combo_idx, col_idx])

                            #?-------------------------------------------
                            #? Build Set 1: var1 figures (x=harmonic, y=var1, z=magnitude)
                            #?-------------------------------------------
                            if not is_2d and x_idx != -1:
                                for group_key, data in var1_groups.items():
                                    if not data['z']:continue

                                    var2_value = group_key[0]
                                    rest_tuple = group_key[1:]

                                    # Fixed dictionary: var2 is fixed, plus any other fixed sweeps
                                    fixed_dict = {y_key: var2_value} if y_key else {}
                                    if fixed_keys and rest_tuple:
                                        for i, k in enumerate(fixed_keys):
                                            if i < len(rest_tuple):fixed_dict[k] = rest_tuple[i]

                                    fixed_title = self.format_fixed_title(fixed_dict, sweep_names) if fixed_dict else ""

                                    fig = self.barchart3D(
                                                            x_vals  = data['x']                                                                     ,
                                                            y_vals  = data['y']                                                                     ,
                                                            z_vals  = data['z']                                                                     ,
                                                            title   = f"{component}<br>{fixed_title}" if fixed_title else component                 ,
                                                            z_title = 'Magnitude'                                                                   ,
                                                            x_title = 'Harmonic Order'                                                              ,
                                                            y_title = sweep_names[int(dp.re.search(r'\d+', x_key).group())-1] if x_key else 'Var1'  ,
                                                            opacity = 0.9
                                                        )
                                    if fig  :   component_plots.append(fig)

                            #?-------------------------------------------
                            #? Build Set 2: var2 figures (x=harmonic, y=var2, z=magnitude)
                            #?-------------------------------------------
                            if not is_2d and y_idx != -1:
                                for group_key, data in var2_groups.items():
                                    if not data['z']:
                                        continue

                                    var1_value = group_key[0]
                                    rest_tuple = group_key[1:]

                                    # Fixed dictionary: var1 is fixed, plus any other fixed sweeps
                                    fixed_dict = {x_key: var1_value} if x_key else {}
                                    if fixed_keys and rest_tuple:
                                        for i, k in enumerate(fixed_keys):
                                            if i < len(rest_tuple):fixed_dict[k] = rest_tuple[i]

                                    fixed_title = self.format_fixed_title(fixed_dict, sweep_names) if fixed_dict else ""

                                    fig = self.barchart3D(
                                                            x_vals  = data['x']                                                                     ,
                                                            y_vals  = data['y']                                                                     ,
                                                            z_vals  = data['z']                                                                     ,
                                                            title   = f"{component}<br>{fixed_title}" if fixed_title else component                 ,
                                                            z_title = 'Magnitude'                                                                   ,
                                                            x_title = 'Harmonic Order'                                                              ,
                                                            y_title = sweep_names[int(dp.re.search(r'\d+', y_key).group())-1] if y_key else 'Var2'  ,
                                                            opacity = 0.9
                                                        )
                                    if fig  :   component_plots.append(fig)

                        #?-------------------------------------------
                        #? Write report
                        #?-------------------------------------------
                        if component_plots:
                            html_path = dp.os.path.normpath(dp.os.path.join(f"{filelog.resultfolder}/HTML_GRAPHS/",f"HTML_GRAPH_{dp.re.sub(r'[^a-zA-Z0-9]', '_', component)}_{self.utc}.html")).replace('\\', '/')
                            self.write_html_report(html_path, component_plots)

    def get_sweep_vars(self,Xs):
        """
        Extract sweep variables from sweepvars list Xs.

        Args:
            Xs (List)   : List of parameters sweep

        Returns:
                dict    : parameters values sweep dictionary
        """

        sweep_vars  = {}

        for i , x_values in enumerate(Xs,1):
            if x_values and x_values != [0] :   sweep_vars[f"X{i}"] = x_values

        return sweep_vars

    def create_2d_plot(self, data, component, title, x_key, sweep_names):
        """
        Create 2D plots.

        Args:
            data        (_type_)    : _description_
            component   (_type_)    : _description_
            title       (_type_)    : _description_
            x_key       (_type_)    : _description_
            sweep_names (_type_)    : _description_

        Returns:
            _type_: _description_
        """
        fig         = dp.plotly.graph_objects.Figure()
        sorted_idx  = dp.np.argsort(data['x'])

        fig.add_trace(dp.plotly.graph_objects.Scatter(
                                                        x       =   dp.np.array(data['x'])[sorted_idx]  ,
                                                        y       =   dp.np.array(data['z'])[sorted_idx]  ,
                                                        mode    =   'lines'                             ,
                                                        name    =   component
                                                    ))
        fig.update_layout(
                            title       =   dict(text=title, x=0.5)                                 ,
                            xaxis_title =   sweep_names[int(dp.re.search(r'\d+', x_key).group())-1] ,
                            yaxis_title =   component                                               ,
                            height      =   600                                                     ,
                            margin      =   dict(t=80)
                            )
        return fig

    def create_3d_plot(self, data, component, title, x_key, y_key, sweep_names, is_permute):
        """
        Create 3D plots.
        For permute=True    : Use Surface plot (gridded data)
        For permute=False   : Use Scatter3d plot (sequential data, not enough for surface)

        Args:
            data        (_type_)    : _description_
            component   (_type_)    : _description_
            title       (_type_)    : _description_
            x_key       (_type_)    : _description_
            y_key       (_type_)    : _description_
            sweep_names (_type_)    : _description_
            is_permute  (bool)      : _description_

        Returns:
            _type_: _description_
        """
        x_vals  = dp.np.array(data['x'])
        y_vals  = dp.np.array(data['y'])
        z_vals  = dp.np.array(data['z'])
        x_title = sweep_names[int(dp.re.search(r'\d+', x_key).group())-1]
        y_title = sweep_names[int(dp.re.search(r'\d+', y_key).group())-1]

        if is_permute:

            x_unique    = dp.np.unique(x_vals)
            y_unique    = dp.np.unique(y_vals)
            X, Y        = dp.np.meshgrid(x_unique, y_unique)
            Z           = dp.np.full_like(X, dp.np.nan, dtype=float)

            # Build index maps for safe indexing
            x_map       = {v: i for i, v in enumerate(x_unique)}
            y_map       = {v: i for i, v in enumerate(y_unique)}

            for x, y, z in zip(x_vals, y_vals, z_vals):
                if x in x_map and y in y_map    :   Z[y_map[y], x_map[x]] = z

            fig = dp.plotly.graph_objects.Figure(data  = [dp.plotly.graph_objects.Surface(
                                                                                            x           =   X           ,
                                                                                            y           =   Y           ,
                                                                                            z           =   Z           ,
                                                                                            colorscale  =   'Viridis')
                                                          ])

        else:

            fig = dp.plotly.graph_objects.Figure(data=[dp.plotly.graph_objects.Scatter3d(
                                                                                            x       =   x_vals                          ,
                                                                                            y       =   y_vals                          ,
                                                                                            z       =   z_vals                          ,
                                                                                            mode    =   'markers'                       ,
                                                                                            marker  =   dict(size=5, color='royalblue') ,
                                                                                            line    =   dict(color='royalblue', width=2)
                                                                                        )])

        fig.update_layout(
                            title   =   dict(text=title, x=0.5)                             ,
                            scene   =   dict(
                                                xaxis_title =   x_title                     ,
                                                yaxis_title =   y_title                     ,
                                                zaxis_title =   component                   ,
                                                xaxis       =   dict(autorange='reversed')  ,
                                                yaxis       =   dict(autorange='reversed')
                                            )                                               ,
                            height  =   700                                                 ,
                            margin  =   dict(t=80)
                        )

        return fig

    def build_ordered_keys(self, map_types, sens_map_types, base_signal_names, prefix='', mat_name_headers=None):
        """
        Single source of truth for CSV file order AND header order.

        Args:
            map_types         (set)  : available map type stems
            sens_map_types    (set)  : available sensitivity map type stems
            base_signal_names (list) : signal names — standalone mode only
            prefix            (str)  : 'Standalone_' for standalone, '' for normal
            mat_name_headers  (dict) : normal mode only — ordered {mat_name: [headers]}

        Returns :   list of (csv_key, header_name) tuples in exact file-load order
        """
        entries = []

        #?------------------------------------------------
        #? Standalone mode
        #?------------------------------------------------
        if prefix == 'Standalone_':

            signal_order = ['AVG', 'FIRST', 'LAST', 'MAX', 'MIN', 'P2P', 'RMS']

            for sig_type in signal_order:
                if sig_type in map_types:
                    for sig_name in base_signal_names   :   entries.append((f"Standalone_{sig_type}", f"{sig_name}_{sig_type}"))

                if sig_type in sens_map_types:
                    for sig_name in base_signal_names   :   entries.append((f"Standalone_{sig_type}_Sens", f"{sig_name}_{sig_type}_Sens"))

            if dp.JSON['FFT']:
                if 'FFT' in map_types:
                    for sig_name in base_signal_names   :   entries.append(('Standalone_FFT', f"{sig_name}_FFT"))

                if 'FFT' in sens_map_types:
                    for sig_name in base_signal_names   :   entries.append(('Standalone_FFT_Sens', f"{sig_name}_FFT_Sens"))

        #?------------------------------------------------
        #? Normal mode
        #?------------------------------------------------
        else:
            for mat_name, headers in mat_name_headers.items():

                if mat_name in map_types:
                    for h in headers    :   entries.append((mat_name, h))

                if f"{mat_name}_Sens" in map_types:
                    for h in headers    :   entries.append((f"{mat_name}_Sens", f"{h}_Sens"))

            # FFT entries at the end
            if dp.JSON['FFT'] and mat_name_headers:
                for fft_name in ['FFT_Current', 'FFT_Voltage']:
                    if fft_name in map_types and fft_name in mat_name_headers:
                        for h in mat_name_headers[fft_name] :   entries.append((fft_name, h))

                if 'FFT_Sens' in map_types and 'FFT_Sens' in mat_name_headers:
                    for h in mat_name_headers['FFT_Sens']   :   entries.append(('FFT_Sens', h))

        return entries

    def get_headers(self, csv_maps_dir):
        """
        Build signal and FFT header lists and store self.entries as the single
        source of truth for file-to-header mapping used by load_matrices.

        Args:
            csv_maps_dir        (str)    : path to CSV_MAPS directory

        Returns:
            signal_headers (list) : ordered list of signal header strings
            fft_headers    (list) : ordered list of FFT header strings
        """

        # Get all map files and derive mat_order from natsort — this IS the load order
        signal_headers,fft_headers  = [],[]
        map_files                   = dp.natsort.natsorted([f for f in dp.os.listdir(csv_maps_dir) if f.endswith('_Map.csv')])
        mat_order                   = [f.replace('_Map.csv', '') for f in map_files]
        map_types,sens_map_types    = set(),set()

        #?------------------------------------------------
        #? Standalone mode
        #?------------------------------------------------
        if dp.standalone_exist:

            for name in mat_order:
                clean                       =   name.replace('Standalone_', '')
                if clean.endswith('_Sens')  :   sens_map_types.add(clean.replace('_Sens', ''))
                else                        :   map_types.add(clean)

            # Get base signal names
            base_signal_names               =   [dp.re.sub(r'[^a-zA-Z0-9]', '_', n) for n in dp.std_headers[1:]]
            self.entries                    =   self.build_ordered_keys(map_types, sens_map_types, base_signal_names, prefix='Standalone_')

        #?------------------------------------------------
        #? Normal mode
        #?------------------------------------------------
        else:

            for name in mat_order:
                if name.endswith('_Sens')   :   sens_map_types.add(name.replace('_Sens', ''))
                else                        :   map_types.add(name)

            # Load headers from JSON files in natsort file order
            header_path                     =   (dp.os.getcwd()).replace("\\", "/") + "/Script/assets/Headers/"
            mat_name_headers                =   {}

            for name in mat_order:
                json_path   = dp.os.path.join(header_path, f"{name}.json")

                if dp.os.path.exists(json_path):
                    with open(json_path, 'r') as f:
                        headers                 = dp.json.load(f)
                        mat_name_headers[name]  = headers if isinstance(headers, list) else [headers]

            # Add sensitivity FFT headers if they exist
            if dp.JSON['FFT'] and dp.JSON["perturbation"] != 0 :
                sens_fft_path       = dp.os.path.join(header_path, "FFT_Sens.json")

                if dp.os.path.exists(sens_fft_path):
                    with open(sens_fft_path, 'r') as f:
                        headers                         = dp.json.load(f)
                        mat_name_headers['FFT_Sens']    = headers if isinstance(headers, list) else [headers]

            self.entries    = self.build_ordered_keys(map_types, sens_map_types, base_signal_names=[],prefix='',mat_name_headers=mat_name_headers)

        # Derive final header lists from self.entries
        signal_headers      = [h for (key, h) in self.entries if 'FFT' not in key]
        fft_headers         = [h for (key, h) in self.entries if 'FFT'     in key]

        return signal_headers, fft_headers

    def load_matrices(self, csv_maps_dir):
        """
        Load CSV map files and organize by type using self.entries as the
        single source of truth for file-to-header mapping.

        Args:
            csv_maps_dir   (str)  : path to CSV_MAPS directory

        Returns:
            signal_matrices : dict of {csv_key: (matrix, headers_list)}
            fft_matrices    : dict of {csv_key: (matrix, headers_list)}
        """

        signal_matrices,fft_matrices = {},{}

        for csv_key, group in dp.itertools.groupby(self.entries, key=lambda x: x[0]):

            headers     = [h for (_, h) in group]
            matrix      = dp.pd.read_csv(dp.os.path.join(csv_maps_dir, f"{csv_key}_Map.csv"), header=None).values.astype(float)

            if 'FFT' in csv_key :   fft_matrices[csv_key]       = (matrix, headers)
            else                :   signal_matrices[csv_key]    = (matrix, headers)

        return signal_matrices, fft_matrices

    #?-------------------------------------------------------------------------------------------------------------------------------------------------------------
    #? MAIN
    #?-------------------------------------------------------------------------------------------------------------------------------------------------------------

    def prep_html_template(self,Time_series = True,Standalone=False):
        """
            Load and prepare the html template to be used depending on the Time_series argument.
            By default the template to be used is the time series one.

            Parameters :
                            Time_series  (bool)   : select the desired html template file.
            Return     :
                            html_content (string) : string of modified html source code.
        """
        def minify_css(css):
            # Remove comments, whitespace, etc.
            css = dp.re.sub(r'/\*.*?\*/', '', css, flags=dp.re.DOTALL)
            css = dp.re.sub(r'\s+', ' ', css)
            css = dp.re.sub(r';\s*', ';', css)
            css = dp.re.sub(r':\s*', ':', css)
            css = dp.re.sub(r'\s*\{\s*', '{', css)
            css = dp.re.sub(r'\s*\}\s*', '}', css)
            return css.strip()

        if Standalone:
            # load the standalone html template file content
            with open(dp.html_template_standalone , 'r' , encoding='utf_8') as file : html_content = file.read()

        if Time_series:
            # load the time series html file template.
            with open(dp.html_template, 'r', encoding='utf-8') as file: html_content = file.read()

        elif Time_series==False and Standalone==False :
            # load the iterations html file template.
            with open(dp.html_template_iter, 'r', encoding='utf-8') as file: html_content = file.read()

        # the CSS styling sheet content gets ported in both cases.
        with open(dp.stylesheet, 'r')  as f : css = minify_css(f.read())
        html_content                        = dp.re.sub(r'<style>.*?</style>'  , f'<style>{css}</style>' , html_content, flags=dp.re.DOTALL)

        with open(dp.BMW_Base64_Logo, 'r', encoding='utf-8') as logo_file: logo_base64 = logo_file.read().strip()

        # Replace the variables
        html_content = html_content.replace("{{TITLE}}"         , self.title)
        html_content = html_content.replace("{{SCRIPT_NAME}}"   , dp.scriptname)
        html_content = html_content.replace("{{DATE_TIME}}"     , dp.date)
        html_content = html_content.replace("{{SIMULATION_ID}}" , self.utc)
        html_content = html_content.replace("{{LOGO_BASE64}}"   , logo_base64)

        file.close()
        return html_content

    def append_to_html(self,csv_filename,figure, filename,auto_open, i=1,include_plotlyjs='cdn',standalone = False):
        """
            Appends figures to an existing html file.

            Parameters        :     csv_filename        (String)    The path to a CSV file containing the data to use for calculating the data.
                                    figure              (Object)    Plotly lib graph objects class object.
                                    filename            (String)    Path of the html file.
                                    auto_open           (bool)      Determines whether the file should open automatically. Defaults to False.
                                    include_plotlyjs    (String)    Defaults to 'cdn'. check to html  : https://plotly.com/python-api-reference/generated/plotly.graph_objects.Figure.html#plotly.graph_objects.Figure.to_html
                                    standalone          (bool)      if Ture use standalone html filling , else append normally.
        """
        #?----------------------------------------------------------------
        #? Non-Standalone
        #?----------------------------------------------------------------
        if not standalone:
            multiplot       = self.multiplot(csv_filename)
            param_table     = self.mdlvar_params_table(i)
            focused_table   = self.focused_params_table(i)

            if dp.JSON["figureName"] and dp.JSON["figureComment"]:

                self.FigureNames                =   [dp.plt_title_list[i][0] for i in range(len(dp.plt_title_list))]
                self.CtrlFigureNames            =   list(dp.pmap_plt_ctrl.keys())

                if dp.JSON["FFT"] :
                    self.fftFigureNames         =   [f'FFT {dp.plt_title_list[i][0]}' for i in range(len(dp.plt_title_list))]
                    N                           =   2
                    self.FigTitles              =   (dp.interleaved(self.FigureNames, self.fftFigureNames)) + self.CtrlFigureNames
                else :
                    N                           =   1
                    self.FigTitles              =   self.FigureNames + self.CtrlFigureNames

                self.Comments                   =   [" " for _ in range((N*len(dp.plt_title_list))+ len(self.CtrlFigureNames))]

            html_content              = self.prep_html_template(Time_series = True,Standalone=False)
            table_items               = ''
            focused_table_items       = ''
            multiplot_item            = ''
            plot_items                = ''
            constant_items            = ''
            table_items              += param_table.to_html(full_html=False, include_plotlyjs=include_plotlyjs)
            focused_table_items      += focused_table.to_html(full_html=False, include_plotlyjs=include_plotlyjs)
            multiplot_item           += multiplot.to_html(full_html=False, include_plotlyjs=include_plotlyjs)

            if dp.JSON["figureName"] and dp.JSON["figureComment"]:
                for b in range(len(dp.JSON["figureName"])): self.Comments[self.FigTitles.index(dp.JSON["figureName"][b])] =  dp.JSON["figureComment"][b]

            for i in range(len(figure)):
                plot_items      += figure[i].to_html(full_html=False, include_plotlyjs=include_plotlyjs)

                if dp.JSON["figureName"] and dp.JSON["figureComment"]:
                    if not self.Comments[i] == " " :
                        plot_items += f'<input type="text" class="comment-box" style="font-size:9pt;height:50px;width:1500px;" value="{self.comments[i]}" readonly="readonly">'

            # Generate a table of constants from the CSV file and write its HTML representation to the report.
            # Clear the stored constants lists to reset for the next use.
            constant_tables      = self.operational_params_table(csv_filename)
            constant_items      +=  constant_tables.to_html(full_html=False, include_plotlyjs=include_plotlyjs)
            self.constants_list.clear()
            self.constants_vals.clear()
            self.constants_units.clear()

            # If figure names and comments are used, clear all related lists to reset the state for future reports.
            if dp.JSON["figureName"] and dp.JSON["figureComment"]:
                self.FigTitles.clear()
                self.FigureNames.clear()
                if dp.JSON["FFT"] : self.fftFigureNames.clear()
                self.Comments.clear()

            # Replace plot items
            html_content        = html_content.replace("{{TABLE_ITEMS}}", table_items)
            html_content        = html_content.replace("{{FOCUSED_ITEMS}}", focused_table_items)
            html_content        = html_content.replace("{{NOTE_TEXT}}", dp.JSON['simNote'])
            html_content        = html_content.replace("{{multiplot_ITEMS}}", multiplot_item)
            html_content        = html_content.replace("{{PLOT_ITEMS}}", plot_items)
            html_content        = html_content.replace("{{constants_ITEMS_TABLE}}", constant_items)

        #?----------------------------------------------------------------
        #? Standalone
        #?----------------------------------------------------------------
        else :

            focused_table       = self.focused_params_table(i)
            html_content        = self.prep_html_template(Time_series = False,Standalone=True)
            plot_items          = ''
            focused_table_items = ''
            focused_table_items += focused_table.to_html(full_html=False, include_plotlyjs=include_plotlyjs)

            for i in range(len(figure)):
                plot_items      += figure[i].to_html(full_html=False, include_plotlyjs=include_plotlyjs)

            html_content        = html_content.replace("{{FOCUSED_ITEMS}}", focused_table_items)
            html_content        = html_content.replace("{{NOTE_TEXT}}", dp.JSON['simNote'])
            html_content        = html_content.replace("{{PLOT_ITEMS}}", plot_items)

        #?----------------------------------------------------------------
        #? Write the populated HTML
        #?----------------------------------------------------------------
        with open(filename, 'w', encoding='utf-8') as file: file.write(html_content)
        file.close()

        #?----------------------------------------------------------------
        #? If auto_open is True, automatically open the generated HTML file in the default web browser.
        #?----------------------------------------------------------------
        if auto_open: dp.webbrowser.open(dp.pathlib.Path(filename).absolute().as_uri())

    def auto_plot(self,simutil,fileLog,misc,open=False,iterReport=False):
        """
        Generates an HTML report containing multiple plots.

        Args:
            misc (object)               : Miscellaneous object containing utility functions.
            Open (bool, optional)       : If True, open the generated HTML report automatically. Defaults to False.
            iterReport (bool, optional) : If True, generate iterations HTML report. Defaults to False.
        """

        #?----------------------------------------------------------------
        #? Initialize Variables
        #?----------------------------------------------------------------
        misc.tic()
        ResDir                  =   (dp.os.getcwd()).replace("\\","/") + "/Script/" + "D".upper() + "ata/Res/"+dp.scriptname+ "_"+self.utc+dp.suffix +"/CSV_TIME_SERIES"
        MAPS_dir                =   (dp.os.getcwd()).replace("\\","/") + "/Script/" + "D".upper() + "ata/Res/"+dp.scriptname+ "_"+self.utc+dp.suffix +"/CSV_MAPS"
        FFT_curr_path           =   MAPS_dir+"/FFT_Current_Map.csv"
        FFT_volt_path           =   MAPS_dir+"/FFT_Voltage_Map.csv"
        file_list               =   fileLog.natsort_files(ResDir)
        legend                  =   True if dp.JSON['model'] == 'DCDC_D' else False
        c  ,d                   =   0,0
        standalone_csv_files    =   fileLog.natsort_files(ResDir,standalone=True)

        #?----------------------------------------------------------------
        #? generate configured time series and iteration  html reports
        #?----------------------------------------------------------------
        if dp.JSON['model'] :
            if iterReport :
                # Signal reports for currents
                self.iter_reports(
                                'signal'                                                                                ,
                                path            =   ResDir                                                              ,
                                label_dict      =   dp.pmap_multi['Peak_Currents']                                      ,
                                html_path       =   fileLog.resultfolder + "/HTML_REPORTS/" + "HTML_Report_" + self.utc ,
                                Y_axis_label    =   "[ A ]"                                                             ,
                                type            =   "Currents"                                                          ,
                                auto_open       =   open
                                )

                # Signal reports for voltages
                self.iter_reports(
                                'signal'                                                                                ,
                                path            =   ResDir                                                              ,
                                label_dict      =   dp.pmap_multi['Peak_Voltages']                                      ,
                                html_path       =   fileLog.resultfolder + "/HTML_REPORTS/" + "HTML_Report_" + self.utc ,
                                Y_axis_label    =   "[ V ]"                                                             ,
                                type            =   "Voltages"                                                          ,
                                auto_open       =   open
                                )

                # if FFT reports is enabled
                if dp.JSON['FFT']:

                    # FFT reports for currents
                    self.iter_reports(
                                'fft'                                                                                   ,
                                FFT_file        =   "FFT_Current.json"                                                  ,
                                title           =   " "                                                                 ,
                                csv_path        =   FFT_curr_path                                                       ,
                                html_path       =   fileLog.resultfolder + "/HTML_REPORTS/" + "HTML_Report_" + self.utc ,
                                type            =   "Currents_FFT"                                                      ,
                                auto_open       =   open
                                )

                    # FFT reports for voltages
                    self.iter_reports(
                                'fft'                                                                                   ,
                                FFT_file        =   "FFT_Voltage.json"                                                  ,
                                title           =   " "                                                                 ,
                                csv_path        =   FFT_volt_path                                                       ,
                                html_path       =   fileLog.resultfolder + "/HTML_REPORTS/" + "HTML_Report_" + self.utc ,
                                type            =   "Voltages_FFT"                                                      ,
                                auto_open       =   open
                                )

            # loop through each CSV file, generate plots, and append to HTML report
            for x  in range(len(file_list)):

                figures_list            =   self.plot_scopes(file_list[x],dp.pmap_plt,Legend=legend)

                if dp.JSON['FFT'] :
                    FFT_figs                =   self.fft_bar_plot(FFT_curr_path,FFT_volt_path,x)
                    figures_list            =   dp.interleaved(figures_list,FFT_figs)

                # drop extra columns from the CSV file if DCDC_S or DCDC_D
                # and generate control figures and extend to the main figure list
                if dp.JSON['model'] == 'DCDC_S' or 'DCDC_D':
                    simutil.postProcessing.drop_Extra_Cols(file_list[x],sum(dp.Y_list[0:3]),sum(dp.Y_list[0:4]))
                    figures_list.extend(self.plot_scopes(file_list[x],dp.pmap_plt_ctrl,Legend=True,height=1080))

                # increment counter and append plots to HTML report
                c   +=  1
                self.append_to_html(
                                        csv_filename    =   file_list[x]                                                                                    ,
                                        figure          =   figures_list                                                                                    ,
                                        filename        =   fileLog.resultfolder + "/HTML_REPORTS" + "/HTML_REPORT_" + self.utc + "_" + str(c) + ".html"    ,
                                        auto_open       =   open                                                                                            ,
                                        i               =   c-1
                                        )
                # clear lists for next iteration
                self.constants_list.clear()
                self.constants_vals.clear()
                self.constants_units.clear()
                figures_list.clear()

        #?----------------------------------------------------------------
        #? generate standalone time series and iteration  html reports
        #?----------------------------------------------------------------
        if standalone_csv_files:

            for x  in range(len(standalone_csv_files)):

                std_figures_list    =   self.plot_std(standalone_csv_files[x])
                if dp.JSON['FFT']   :
                    FFT_std_figs        =   self.fft_bar_plot(
                                                                iteration               =   x                                   ,
                                                                standalone_fft_map_path =   MAPS_dir+"/Standalone_FFT_Map.csv"  ,
                                                                headers                 =   dp.std_headers[1:]
                                                            )
                    std_figures_list    =   dp.interleaved(std_figures_list,FFT_std_figs)
                d                   +=  1
                self.append_to_html(
                                        csv_filename    =   standalone_csv_files[x]                                                                                 ,
                                        figure          =   std_figures_list                                                                                        ,
                                        filename        =   fileLog.resultfolder + "/HTML_REPORTS" + "/HTML_REPORT_" + self.utc + "_Standalone_" + str(d) + ".html" ,
                                        auto_open       =   open                                                                                                    ,
                                        i               =   d-1                                                                                                     ,
                                        standalone      =   True
                                    )

            if iterReport:
                # Standalone iteration report
                self.iter_reports(
                                    'standalone'                                                                            ,
                                    csv_files       =   standalone_csv_files                                                ,
                                    html_path       =   fileLog.resultfolder + "/HTML_REPORTS/" + "HTML_Report_" + self.utc ,
                                    auto_open       =   open
                                )

                # if FFT reports is enabled
                if dp.JSON['FFT']:

                    # Standalone FFT reports
                    self.iter_reports(
                                'fft'                                                                                   ,
                                csv_path        =   MAPS_dir+"/Standalone_FFT_Map.csv"                                  ,
                                html_path       =   fileLog.resultfolder + "/HTML_REPORTS/" + "HTML_Report_" + self.utc ,
                                type            =   "FFT"   ,
                                auto_open       =   open
                                )

        #?----------------------------------------------------------------
        #? Generate 2D or 3D html report for signals and FFT
        #?----------------------------------------------------------------
        if iterReport   :
            self.graphs_scopes(
                                filelog     =   fileLog             ,
                                Xs          =   simutil.sweepMatrix ,
                                MAPS_dir    =   MAPS_dir
                               )

        #?----------------------------------------------------------------
        #? log the completion of HTML report generation and clear file list
        #?----------------------------------------------------------------
        fileLog.line_separator()
        fileLog.log('{} = {}'.format("Generating HTML Report".ljust(fileLog.PADDING_WIDTH  , ' '),f"{str(misc.toc())} seconds.\n"))
        file_list.clear()
#?-------------------------------------------------------------------------------------------------------------------------------------------------------------