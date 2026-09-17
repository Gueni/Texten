
#?-------------------------------------------------------------------------------------------------------------------------------------------------------------
#?                             __  __    _    ____     ____    _    _     ____ _   _ _        _  _____ ___ ___  _   _
#?                            |  \/  |  / \  |  _ \   / ___|  / \  | |   / ___| | | | |      / \|_   _|_ _/ _ \| \ | |
#?                            | |\/| | / _ \ | |_) | | |     / _ \ | |  | |   | | | | |     / _ \ | |  | | | | |  \| |
#?                            | |  | |/ ___ \|  __/  | |___ / ___ \| |__| |___| |_| | |___ / ___ \| |  | | |_| | |\  |
#?                            |_|  |_/_/   \_\_|      \____/_/   \_\_____\____|\___/|_____/_/   \_\_| |___\___/|_| \_|
#?
#?-------------------------------------------------------------------------------------------------------------------------------------------------------------
from    abc     import  ABC , abstractmethod
import  numpy   as      np
#?-------------------------------------------------------------------------------------------------------------------------------------------------------------

class MapStrategy(ABC):
    """
    _summary_

    *Args:
        ABC (_type_)    : _description_
    """
    @abstractmethod
    def generate(self, config):
        """
        _summary_

        *Args:
            config (_type_) : _description_
        """
        pass

class Map():
    def __init__(self):
        """
        Initialize the Map class

        """
        self.sweepMatrix    = []
        self.Map            = ''
        self.Iterations     = 1

    def GenerateNormalMap(self, matrix):
        """
        Generate parameter combinations starting from a given index.

        *Args   :
            matrix  (list)          : Parameter matrix (X1-X10 lists)
            index   (list)          : Starting index(es)
            pattern (bool, optional): True for Cartesian product,False for simple listing. Defaults to True.

        !Returns:
            tuple                   : (parameter combinations subset, number of combinations)

        """

        #?------------------------------------------------------
        #? NORMAL MODE LOGIC : Sequential sweep
        #?------------------------------------------------------
        # Extract simple values from parameter matrix
        matrix_vals = self.extract_matrix_values(matrix)

        # Pad each parameter list to max length by repeating last value
        max_len     = max(len(v) if v != [0] else 1 for v in matrix_vals)
        padded      = []
        for v in matrix_vals:
            if v == [0] :   padded.append([0]*max_len)
            else        :   padded.append(v + [v[-1]]*(max_len - len(v)))

        # Transpose to iteration-wise rows
        Map         = np.array(padded).T.tolist()
        return Map, len(Map)

    def GeneratePermuteMap(self, matrix):
        """
        Generate parameter combinations starting from a given index.

        *Args   :
            matrix  (list)          : Parameter matrix (X1-X10 lists)
            index   (list)          : Starting index(es)
            pattern (bool, optional): True for Cartesian product,False for simple listing. Defaults to True.

        !Returns:
            tuple                   : (parameter combinations subset, number of combinations)

        """
        #?------------------------------------------------------
        #? PERMUTATION MODE : Cartesian product
        #?------------------------------------------------------

        # Extract simple values from parameter matrix
        matrix_vals     = self.extract_matrix_values(matrix)

        # Get dimensions of each parameter list
        lens            =   [len(v) if v != [0] else 1 for v in matrix_vals]

        # Total combinations = product of all dimensions
        total           =   np.prod(lens)
        if total == 0   :   return np.zeros((0, 10)), 0

        # Initialize parameter map: rows = combinations, columns = X1-X10
        map_data        = np.zeros((total, 10))
        step            = total  # Start with total combinations

        # Generate Cartesian product efficiently using numpy operations
        for col in range(10):
            if matrix_vals[col] == [0]:

                # Unused parameter: fill column with zeros
                step            //= 1  # Dimension is 1
                map_data[:, col]  = 0
            else:
                # Active parameter: generate repeating pattern
                # and update step size for this dimension
                dim               = lens[col]
                step            //= dim

                # Calculate repetition factor for this parameter's values
                repeat            = total // (step * dim)

                # Fill column with repeating pattern of values
                map_data[:, col]  = np.tile(np.repeat(matrix_vals[col], step), repeat)

        # Extract subset starting from the given index
        #start   = index[-1] if index else 0
        #subset  = map_data[start:] if start < len(map_data) else []

        return map_data, len(map_data)

    def extract_matrix_values(self, Xs):
        """
        Extract simple values from parameter lists for normal and permute mode.

        *Args   :
            Xs (list)       : List of parameter lists for X1-X10

        !Returns:
            list            : Simplified list of parameter values (removes nested structure)

        ?Example:
            Input           : [[[10], [20]], [[100]], [[0]], ...]
            Output          : [[10, 20], [100], [0], ...]
        """
        return [[sub[0] if isinstance(sub, list) and sub else sub for sub in var] if var not in [[[0]], [0]] else [0] for var in Xs]

    def returnResults(self):
        """
        _summary_

        !Returns:
            _type_  : _description_
        """
        return self.sweepMatrix, self.Map, self.Iterations

class NormalMap(MapStrategy, Map):
    """
    _summary_

    *Args:
        MapStrategy (_type_)    : _description_
        Map         (_type_)    : _description_
    """
    def generate(self, config):
        """
        _summary_

        *Args   :
            config (_type_) : _description_

        !Returns:
            _type_          : _description_
        """
        self.sweepMatrix            = config["sweepMatrix"]
        self.Map, self.Iterations   = self.GenerateNormalMap(config["sweepMatrix"])
        return self.returnResults()

class PermuteMap(MapStrategy, Map):
    """
    _summary_

    *Args:
        MapStrategy (_type_)    : _description_
        Map         (_type_)    : _description_
    """
    def generate(self, config):
        """
        _summary_

        *Args   :
            config (_type_)     : _description_

        !Returns:
            _type_              : _description_
        """
        self.sweepMatrix            = config["sweepMatrix"]
        self.Map, self.Iterations   = self.GeneratePermuteMap(config["sweepMatrix"])
        return self.returnResults()

class WcaMap(MapStrategy, Map):
    """
    _summary_

    *Args:
        MapStrategy (_type_)    : _description_
        Map         (_type_)    : _description_
    """
    def generate(self, config):
        """
        _summary_

        *Args   :
            config (_type_)     : _description_

        !Returns:
            _type_              : _description_
        """
        self.sweepMatrix    = config["sweepMatrix"]

        # Build full WCA map
        active              = self.get_active_wca_params(self.sweepMatrix)
        self.wca_iterations = 2 ** len(active)
        self.Iterations     = self.wca_iterations + 1
        self.Map            = []

        for iter_num in range(self.Iterations):
            if iter_num == self.Iterations - 1  :   self.Map.append([[sub[0] for sub in var] if var not in [[[0]], [0]] else [0]for var in self.sweepMatrix]) # Nominal values
            else                                :   self.Map.append(self.calculate_wca_values(iter_num, self.sweepMatrix))

        # Flatten for 2D representation
        #self.Map          = [sum((list(p) if isinstance(p, list) else [p] for p in row), [])for row in self.Map]

        return self.returnResults()

    def calculate_wca_values(self, iteration, Xs):
        """
        Calculate WCA values for all parameters in a given iteration.

        *Args   :
            iteration   (int)   : Current WCA iteration number
            Xs          (list)  : List of parameter lists for X1-X10

        !Returns:
            (list)              : 3D list of calculated WCA values for all parameters

        """
        results = []

        # Process each parameter X1 through X10
        for i, var in enumerate(Xs):
            # Handle unused parameters
            if var == [[0]] or var == [0]:
                results.append([0])
                continue

            # Calculate WCA values for this parameter's sublists
            wca_vals = []

            for sub in var:
                # Single value sublist (no tolerance)
                if len(sub) == 1    :   wca_vals.append(sub[0])

                # WCA format: [nominal, tolerance, min, max] or [nominal, tolerance]
                elif len(sub) in (2, 4):
                    nom, tol = sub[0], sub[1]

                    # Default bounds if not provided
                    if len(sub) == 4    :   mn, mx =  sub[2]    , sub[3]
                    else                :   mn, mx = -np.inf , np.inf

                    # Determine tolerance type: True for absolute, False for relative
                    tol_type    = tol <= 1

                    # Apply tolerance function.
                    x           = self.funtol(tol_type, iteration, i, nom, tol)

                    # Clamp value within min/max bounds
                    wca_vals.append(min(max(x, mn), mx))

                # Unknown format, use first element
                else:   wca_vals.append(sub[0])

            results.append(wca_vals)

        return results

    def funtol(self, Abs_rel, iteration, index, nom, tol):
        """
        Calculate tolerance-adjusted value for WCA analysis.

        *Args   :
            Abs_rel     (bool)  : True for absolute tolerance (tol <= 1), False for relative
            iteration   (int)   : Current WCA iteration number
            index       (int)   : Parameter index for binary encoding
            nom         (float) : Nominal value
            tol         (float) : Tolerance value

        !Returns:
            (float)             : Tolerance-adjusted value

        ?Logic  :
            - If binary_index(iteration, index) == 1    :   Apply upper tolerance
            - If binary_index(iteration, index) == 0    :   Apply lower tolerance
            - For absolute tolerance (tol <= 1)         :   Upper: nom * tol, Lower: nom / tol
            - For relative tolerance (tol > 1)          :   Upper: nom * (1 + tol), Lower: nom * (1 - tol)
        """
        active = self.get_active_wca_params(self.sweepMatrix)

        # Check the bit for this parameter in current iteration
        if not self.binary_index(iteration, index, active):
            # Bit is 0: apply upper tolerance (increase value)
            return nom * (1 + tol) if Abs_rel else nom * tol
        # Bit is 1: apply lower tolerance (decrease value)
        return  nom * (1 - tol)  if Abs_rel else nom / tol

    def get_active_wca_params(self, Xs):
        """
        Identify which parameters X lists are used.

        *Args   :
            Xs  (list)      : List of parameter lists for X1-X10

        !Returns:
            (list)          : Indices of parameters that have WCA format (4 or 2 elements per sublist)

        """
        return [i for i, var in enumerate(Xs) if var not in [[[0]], [0]] and len(var) > 0 and isinstance(var[0], list) and len(var[0]) in (2, 4)]

    def binary_index(self, iteration, index, active):
        """
        Generate binary indexing for each iteration.

        *Args   :
            iteration   (int)   : current iteration
            index       (int)   : input list index 0-9
            active      (list)  : list of active input list variables X1-10

        !Returns:
            binary indexing (000,001...)
        """
        # index is global parameter index 0..9
        # active is list of active WCA parameter indices
        active_index    = active.index(index)
        n_active        = len(active)

        # Reverse bit significance
        bit_position    = n_active - 1 - active_index

        return (iteration >> bit_position) & 1

class SensitivityMap(MapStrategy, Map):
    """
    _summary_

    *Args:
        MapStrategy     (_type_)    : _description_
        Map             (_type_)    : _description_
    """
    def generate(self, config):
        """
        _summary_

        *Args   :
            config (_type_) : _description_

        !Returns:
            _type_          : _description_
        """
        self.sweepMatrix            = self.apply_perturbation(config["sweepMatrix"], config["perturbation"], config["nvars"])
        self.Map, self.Iterations   = self.GenerateNormalMap(config["sweepMatrix"])
        return self.returnResults()

    def apply_perturbation(self, Xs, perturbation_value, nvars=None):
        """
        Generate sensitivity Xlists for sensitivity sweep.

        *Args  :
            perturbation_value  (float) : perturbation value
            nvars               (int)   : number of used parameters (required only for Case 1)
            Xs                  (list)  : sweep variables from X1 to X10

        !Returns:
            Xs                          : list of lists
        """

        #? --------------------------------------------------
        #? CASE 1: All zeros
        #? --------------------------------------------------

        if (not nvars == None) and all(var == [0] for var in Xs[:10]):
            if nvars is None    :   raise ValueError("nvars must be provided when all Xlists are zero")

            # Diagonal perturbation matrix
            result_matrix       = np.zeros((nvars, nvars))
            np.fill_diagonal(result_matrix, perturbation_value)

            # Final matrix: nominal first
            final_matrix        = np.hstack((np.zeros((nvars, 1)), result_matrix))
            # Write back
            for idx, row in zip(list(range(nvars)), final_matrix) : Xs[idx] = row.tolist()

        elif nvars is None :

            #? --------------------------------------------------
            #? CASE 2: Nominal values provided
            #? --------------------------------------------------
            active_indices      = [i for i, var in enumerate(Xs) if var not in [[[0]], [0]] and len(var) == 1]
            nvars               = len(active_indices)

            # Extract nominal values at operating point k
            nominal_values = [Xs[i][0] for i in active_indices]

            # Initialize sensitivity matrix (n_vars × n_vars)
            result_matrix  = np.zeros((nvars, nvars))

            # Fill each row with nominal values
            for i in range(nvars) : result_matrix[i, :] = nominal_values[i]

            # Apply perturbation on diagonal (one variable at a time)
            for i in range(nvars):

                result_matrix[i, i] = nominal_values[i] * (1 + perturbation_value / 100)

            nominal_matrix  = np.array([[Xs[i][0]] for i in active_indices])
            final_matrix    = np.hstack((nominal_matrix,result_matrix))

            # Write computed rows back into X1..X10 structure
            for idx, row in zip(active_indices, final_matrix): Xs[idx] = row.tolist()

        return Xs

class MonteCarloMap(MapStrategy, Map):
    """
    _summary_

    *Args:
        MapStrategy (_type_)    : _description_
        Map         (_type_)    : _description_
    """
    def generate(self, config):
        """
        _summary_

        *Args   :
            config (_type_)     : _description_

        !Returns:
            _type_              : _description_
        """
        self.apply_rand_tol(config["sweepMatrix"], config["points"], config["Tols"], config["seed"])
        self.Map, self.Iterations = self.GenerateNormalMap(config["sweepMatrix"])
        return self.returnResults()

    def apply_rand_tol(self,Xs, points, Tols,seed=None):
        """
            Generate randomised tolerance sweep lists for Monte Carlo analysis.

        *Args:
            Xs      (list)  :   Sweep variable lists X1-X10.
            points  (int)   :   number of random points in interval -tol:+tol
            tols    (list)  :   Relative tolerances, one per active variable.
            seed    (int)   :   Integer seed passed to numpy.random.default_rng.
                                'None' → a random seed is drawn from the system RNG and printed.
                                or pass the printed seed back in to reproduce an identical run.

        !Returns:
            Xs      (list)  :   Modified X-lists.
        """
        rng         = np.random.default_rng(seed)

        # Check if all X lists are zero
        all_zero    = all(var in [[[0]], [0], [0.0]] for var in Xs[:10])

        #?---------------------------------------------------------
        if all_zero:
            n_active       =   len(Tols)
            active_indices =   list(range(n_active))
            nominal_values =   [0.0] * n_active
        else:
            active_indices =   [i for i, var in enumerate(Xs[:10]) if var not in [[[0]], [0], [0.0]] and len(var) == 1]
            n_active       =   len(active_indices)
            nominal_values =   [Xs[i][0] for i in active_indices]
        #?---------------------------------------------------------

        generated_columns  =   []

        for idx in range(n_active):

            tol            =   Tols[idx]                                        # current tolerance
            randMin        =  -tol                                              # random minimum limit
            randMax        =   tol                                              # random maximum limit
            nominal        =   nominal_values[idx]                              # nominal values array (0.0 or actual)
            random_values  =   rng.uniform(randMin,randMax,size=points)

            if all_zero    :   values =  random_values.tolist()
            else           :   values =  [nominal * (1 + rv) for rv in random_values]

            generated_columns.append(values)

        #?---------------------------------------------------------
        #? Update Xs with generated values
        #?---------------------------------------------------------
        for i, col_idx in enumerate(active_indices) :   Xs[col_idx] = generated_columns[i]

        return Xs

class MapContext:
    """
    _summary_

    """
    def __init__(self, map_strategy):
        """
        _summary_

        *Args:
            map_strategy (_type_)   : _description_
        """
        self.maps           = {
                                "NORMAL"        : NormalMap(),
                                "PERMUTE"       : PermuteMap(),
                                "WCA"           : WcaMap(),
                                "MONTECARLO"    : MonteCarloMap(),
                                "SENSITIVITY"   : SensitivityMap()
                            }
        self.map_strategy   = self.maps[map_strategy]

    def set_map_strategy(self, map_strategy):
        """
        _summary_

        *Args:
            map_strategy (_type_)   : _description_
        """
        self.map_strategy = self.maps[map_strategy]

    def generate_map(self, config):
        """
        _summary_

        *Args   :
            config (_type_) : _description_

        !Returns:
            _type_          : _description_
        """
        return self.map_strategy.generate(config)
#?-------------------------------------------------------------------------------------------------------------------------------------------------------------
