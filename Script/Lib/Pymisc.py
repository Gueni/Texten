
#?-------------------------------------------------------------------------------------------------------------------------------------------------------------
#?                                                __  __ _              _ _
#?                                               |  \/  (_)___  ___ ___| | | __ _ _ __   ___  ___  _   _ ___
#?                                               | |\/| | / __|/ __/ _ \ | |/ _` | '_ \ / _ \/ _ \| | | / __|
#?                                               | |  | | \__ \ (_|  __/ | | (_| | | | |  __/ (_) | |_| \__ \
#?                                               |_|  |_|_|___/\___\___|_|_|\__,_|_| |_|\___|\___/ \__,_|___/
#?
#?-------------------------------------------------------------------------------------------------------------------------------------------------------------
import time
#?-------------------------------------------------------------------------------------------------------------------------------------------------------------
class Misc :
    def __init__(self):

        self.TicToc     =   self.TicTocGenerator()          # create an instance of the TicToc generator

    def TicTocGenerator(self):
        """
        Generator that returns time differences

        !Returns:
            float: returns the time difference
        """

        # initialize time variables
        # and yield the time difference
        ti = 0
        tf = time.time()
        while True:
            ti = tf
            tf = time.time()
            yield tf-ti

    def toc(self,tempBool=True):
        """
            Records a time in TicToc, marks the end of a time interval

        *Args   :
            tempBool (bool, optional)   : token used to mark the end. Defaults to True.

        !Returns:
            float                       : time difference returned by generator.
        """

        # return the time difference yielded by generator instance TicToC
        # if tempBool is True else do not return anything
        tempTimeInterval    =   next(self.TicToc)
        if tempBool         :   return tempTimeInterval

    def tic(self):
        """
        Records a time in TicToc, marks the beginning of a time interval
        """

        # call toc with False to mark the beginning of a time interval`
        # without returning the time difference`
        self.toc(False)

    def update_dict_value(self,d, key_path, multiplier):
        """
        Updates the value in a nested dictionary at the specified key path by applying a multiplier.

        *Args:
            d           (dict)  : The dictionary to update.
            key_path    (str)   : The key path represented as a bracketed string (e.g., "['a']['b']['c']").
            multiplier  (float) : The multiplier to apply to the value at the specified key path.

        """

        # Update the value in the nested dictionary at the specified key path
        # by multiplying it with the given multiplier
        # e.g., for key_path "['a']['b']['c']", it accesses d['a']['b']['c']
        # and updates its value to d['a']['b']['c'] * multiplier
        # if the key path exists in the dictionary
        keys = key_path.strip("[]").replace("']['", "/").replace("'", "").split("/")
        temp = d
        for key in keys[:-1]:
            temp = temp.get(key, {})
        last_key = keys[-1]
        if last_key in temp:
            temp[last_key] = temp[last_key] + temp[last_key] * multiplier

#?-------------------------------------------------------------------------------------------------------------------------------------------------------------